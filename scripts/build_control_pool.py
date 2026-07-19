from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import STANDARD_VALUES


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "corpus_registry.csv"
EXPANSION = ROOT / "data" / "divine_name_expansion_candidates.csv"
POOL_OUT = ROOT / "data" / "control_phrase_pool.csv"
MATCH_OUT = ROOT / "data" / "control_match_registry.csv"
SOURCE_LOCK_OUT = ROOT / "data" / "control_source_lock.csv"
REPORT_OUT = ROOT / "docs" / "CONTROL_POOL_AUDIT.md"

SOURCE_REPOSITORY = "https://github.com/openscriptures/morphhb"
SOURCE_COMMIT = "3d15126fb1ef74867fc1434be1942e837932691f"
PROTOCOL_COMMIT = "b7724fda228eb09489ab13c062c0d4d33fe3c876"
MINIMUM_STRATUM_SIZE = 50
FINAL_FORMS = set("ךםןףץ")


@dataclass(frozen=True)
class Target:
    analysis_layer: str
    target_id: str
    name: str
    hebrew: str
    source_dataset: str
    source_row_id: str
    word_count: int
    word_lengths: tuple[int, ...]
    total_letters: int
    final_form_count: int


@dataclass
class PhraseRecord:
    words: tuple[str, ...]
    first_reference: str
    first_book_file: str
    frequency: int = 1


@dataclass
class PoolRow:
    control_id: str
    hebrew: str
    word_count: int
    word_lengths: str
    total_letters: int
    final_form_count: int
    first_reference: str
    first_book_file: str
    frequency: int
    source_commit: str


@dataclass
class MatchRow:
    analysis_layer: str
    target_id: str
    name: str
    hebrew: str
    source_dataset: str
    source_row_id: str
    word_count: int
    word_lengths: str
    total_letters: int
    final_form_count: int
    match_level: str
    eligible_control_count: int
    minimum_stratum_size: int


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_hebrew(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if char in STANDARD_VALUES)


def phrase_words(text: str) -> tuple[str, ...]:
    return tuple(
        normalized
        for raw in text.split()
        if (normalized := normalize_hebrew(raw))
    )


def structural_fields(words: tuple[str, ...]) -> tuple[int, tuple[int, ...], int, int]:
    lengths = tuple(len(word) for word in words)
    return (
        len(words),
        lengths,
        sum(lengths),
        sum(char in FINAL_FORMS for word in words for char in word),
    )


def make_target(
    layer: str,
    target_id: str,
    name: str,
    hebrew: str,
    source_dataset: str,
    source_row_id: str,
) -> Target:
    words = phrase_words(hebrew)
    if not words:
        raise ValueError(f"Target has no Hebrew letters: {target_id}")
    word_count, lengths, total, finals = structural_fields(words)
    return Target(
        analysis_layer=layer,
        target_id=target_id,
        name=name,
        hebrew=" ".join(words),
        source_dataset=source_dataset,
        source_row_id=source_row_id,
        word_count=word_count,
        word_lengths=lengths,
        total_letters=total,
        final_form_count=finals,
    )


def load_targets() -> list[Target]:
    registry = load_csv(REGISTRY)
    expansion = load_csv(EXPANSION)
    primary = [row for row in registry if row["corpus_layer"] == "primary-biblical"]
    messianic = [row for row in registry if row["corpus_layer"] == "messianic-comparative"]
    broad = [row for row in expansion if row["broad_biblical_scan"] == "yes"]
    christian = [
        row for row in expansion
        if row["layer"] == "christian-comparative-expansion"
    ]
    yeshua_hamashiach = next(row for row in expansion if row["candidate_id"] == "61")

    targets: list[Target] = []

    def add_registry(layer: str, rows: list[dict[str, str]]) -> None:
        for row in rows:
            targets.append(
                make_target(
                    layer,
                    f"{layer}:registry:{row['index']}",
                    row["name"],
                    row["analysis_hebrew"],
                    "corpus_registry.csv",
                    row["index"],
                )
            )

    def add_expansion(layer: str, rows: list[dict[str, str]]) -> None:
        for row in rows:
            targets.append(
                make_target(
                    layer,
                    f"{layer}:expansion:{row['candidate_id']}",
                    row["name"],
                    row["hebrew"],
                    "divine_name_expansion_candidates.csv",
                    row["candidate_id"],
                )
            )

    add_registry("primary-biblical", primary)

    add_registry("expanded-biblical-all", primary)
    add_expansion("expanded-biblical-all", broad)

    add_registry("restored-christian-inclusive", primary + messianic)
    add_expansion("restored-christian-inclusive", [yeshua_hamashiach])

    add_registry("full-christian-expansion", primary + messianic)
    add_expansion("full-christian-expansion", christian)

    return targets


def load_forbidden_phrases() -> dict[int, set[tuple[str, ...]]]:
    forbidden: dict[int, set[tuple[str, ...]]] = defaultdict(set)
    for row in load_csv(REGISTRY):
        for field in ("displayed_hebrew", "analysis_hebrew", "source_form"):
            words = phrase_words(row[field])
            if words:
                forbidden[len(words)].add(words)
    for row in load_csv(EXPANSION):
        words = phrase_words(row["hebrew"])
        if words:
            forbidden[len(words)].add(words)
    return forbidden


def contains_forbidden(
    words: tuple[str, ...], forbidden: dict[int, set[tuple[str, ...]]]
) -> bool:
    for length, phrases in forbidden.items():
        if length > len(words):
            continue
        for start in range(len(words) - length + 1):
            if words[start : start + length] in phrases:
                return True
    return False


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def verse_words(element: ET.Element) -> list[ET.Element]:
    words: list[ET.Element] = []

    def walk(node: ET.Element) -> None:
        if local_name(node.tag) == "note":
            return
        if local_name(node.tag) == "w":
            words.append(node)
            return
        for child in node:
            walk(child)

    walk(element)
    return words


def source_revision(source: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def source_tree_hash(xml_files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in xml_files:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def extract_pool(
    source: Path, targets: list[Target]
) -> tuple[list[PoolRow], Counter[str], str]:
    revision = source_revision(source)
    if revision != SOURCE_COMMIT:
        raise ValueError(f"OSHB source revision {revision} != locked {SOURCE_COMMIT}")

    wlc = source / "wlc"
    xml_files = sorted(wlc.glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"No wlc/*.xml files under {source}")

    max_words = max(target.word_count for target in targets)
    calipers: dict[tuple[int, int], set[int]] = defaultdict(set)
    for target in targets:
        calipers[(target.word_count, target.final_form_count)].add(target.total_letters)
    forbidden = load_forbidden_phrases()
    records: dict[tuple[str, ...], PhraseRecord] = {}
    counts: Counter[str] = Counter()

    for xml_file in xml_files:
        root = ET.parse(xml_file).getroot()
        for verse in (node for node in root.iter() if local_name(node.tag) == "verse"):
            reference = verse.attrib.get("osisID", "")
            tokens: list[tuple[str, bool]] = []
            for word in verse_words(verse):
                normalized = normalize_hebrew("".join(word.itertext()))
                morph = word.attrib.get("morph", "")
                tokens.append((normalized, bool(normalized) and morph.startswith("H")))

            for length in range(1, min(max_words, len(tokens)) + 1):
                for start in range(len(tokens) - length + 1):
                    counts["windows_considered"] += 1
                    window = tokens[start : start + length]
                    if not all(is_hebrew for _, is_hebrew in window):
                        counts["non_hebrew_or_unparsed"] += 1
                        continue
                    words = tuple(word for word, _ in window)
                    if contains_forbidden(words, forbidden):
                        counts["forbidden_expression"] += 1
                        continue
                    word_count, _, total, finals = structural_fields(words)
                    target_totals = calipers.get((word_count, finals), set())
                    if not any(abs(total - target_total) <= 2 for target_total in target_totals):
                        counts["outside_structural_caliper"] += 1
                        continue

                    counts["eligible_occurrences"] += 1
                    if words in records:
                        records[words].frequency += 1
                    else:
                        records[words] = PhraseRecord(
                            words=words,
                            first_reference=reference,
                            first_book_file=xml_file.name,
                        )

    sorted_records = sorted(
        records.values(),
        key=lambda row: (len(row.words), structural_fields(row.words)[2], row.words),
    )
    pool: list[PoolRow] = []
    for index, record in enumerate(sorted_records, start=1):
        word_count, lengths, total, finals = structural_fields(record.words)
        pool.append(
            PoolRow(
                control_id=f"C{index:07d}",
                hebrew=" ".join(record.words),
                word_count=word_count,
                word_lengths="-".join(map(str, lengths)),
                total_letters=total,
                final_form_count=finals,
                first_reference=record.first_reference,
                first_book_file=record.first_book_file,
                frequency=record.frequency,
                source_commit=SOURCE_COMMIT,
            )
        )
    counts["unique_control_phrases"] = len(pool)
    counts["xml_files"] = len(xml_files)
    return pool, counts, source_tree_hash(xml_files)


def match_candidates(target: Target, pool: list[PoolRow]) -> tuple[str, list[PoolRow]]:
    exact = [
        row for row in pool
        if row.word_count == target.word_count
        and row.word_lengths == "-".join(map(str, target.word_lengths))
        and row.final_form_count == target.final_form_count
    ]
    if len(exact) >= MINIMUM_STRATUM_SIZE:
        return "exact-word-vector", exact

    exact_total = [
        row for row in pool
        if row.word_count == target.word_count
        and row.total_letters == target.total_letters
        and row.final_form_count == target.final_form_count
    ]
    if len(exact_total) >= MINIMUM_STRATUM_SIZE:
        return "fallback-exact-total", exact_total

    within_one = [
        row for row in pool
        if row.word_count == target.word_count
        and abs(row.total_letters - target.total_letters) <= 1
        and row.final_form_count == target.final_form_count
    ]
    if len(within_one) >= MINIMUM_STRATUM_SIZE:
        return "fallback-total-within-1", within_one

    within_two = [
        row for row in pool
        if row.word_count == target.word_count
        and abs(row.total_letters - target.total_letters) <= 2
        and row.final_form_count == target.final_form_count
    ]
    return "fallback-total-within-2", within_two


def make_match_rows(targets: list[Target], pool: list[PoolRow]) -> list[MatchRow]:
    rows: list[MatchRow] = []
    for target in targets:
        level, candidates = match_candidates(target, pool)
        if not candidates:
            raise ValueError(f"No controls for {target.target_id}")
        rows.append(
            MatchRow(
                analysis_layer=target.analysis_layer,
                target_id=target.target_id,
                name=target.name,
                hebrew=target.hebrew,
                source_dataset=target.source_dataset,
                source_row_id=target.source_row_id,
                word_count=target.word_count,
                word_lengths="-".join(map(str, target.word_lengths)),
                total_letters=target.total_letters,
                final_form_count=target.final_form_count,
                match_level=level,
                eligible_control_count=len(candidates),
                minimum_stratum_size=MINIMUM_STRATUM_SIZE,
            )
        )
    return rows


def write_dataclass_csv(path: Path, rows: list[object]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_source_lock(tree_hash: str) -> None:
    fields = ["source_repository", "source_commit", "wlc_tree_sha256", "protocol_commit"]
    with SOURCE_LOCK_OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "source_repository": SOURCE_REPOSITORY,
                "source_commit": SOURCE_COMMIT,
                "wlc_tree_sha256": tree_hash,
                "protocol_commit": PROTOCOL_COMMIT,
            }
        )


def write_report(pool: list[PoolRow], matches: list[MatchRow], counts: Counter[str]) -> None:
    by_words = Counter(row.word_count for row in pool)
    by_layer = Counter(row.analysis_layer for row in matches)
    by_level = Counter(row.match_level for row in matches)
    sparse = [row for row in matches if row.eligible_control_count < MINIMUM_STRATUM_SIZE]

    word_rows = "\n".join(
        f"| {words} | {by_words[words]} |" for words in sorted(by_words)
    )
    layer_rows = "\n".join(
        f"| {layer} | {by_layer[layer]} |" for layer in sorted(by_layer)
    )
    level_rows = "\n".join(
        f"| {level} | {by_level[level]} |" for level in sorted(by_level)
    )
    sparse_rows = (
        "\n".join(
            f"| {row.analysis_layer} | {row.name} | `{row.hebrew}` | "
            f"{row.match_level} | {row.eligible_control_count} |"
            for row in sparse
        )
        if sparse
        else "| None | - | - | - | - |"
    )

    content = f"""# Structural Control-Pool Audit

This report is generated by `scripts/build_control_pool.py`. It contains no gematria values, base conversions, palindrome outcomes, or collapse outcomes.

## Source Lock

- Protocol commit: `{PROTOCOL_COMMIT}`
- OSHB repository: [{SOURCE_REPOSITORY}]({SOURCE_REPOSITORY})
- OSHB commit: `{SOURCE_COMMIT}`
- WLC XML files: {counts['xml_files']}

The exact WLC tree hash is recorded in `data/control_source_lock.csv`.

## Extraction

- Contiguous in-verse windows considered: {counts['windows_considered']}
- Excluded as non-Hebrew or unparsed: {counts['non_hebrew_or_unparsed']}
- Excluded for containing a forbidden test expression: {counts['forbidden_expression']}
- Excluded outside every declared structural caliper: {counts['outside_structural_caliper']}
- Structurally eligible occurrences: {counts['eligible_occurrences']}
- Unique normalized control phrases retained: {counts['unique_control_phrases']}

| Words | Unique controls |
| ---: | ---: |
{word_rows}

## Target Layers

| Analysis layer | Target rows |
| --- | ---: |
{layer_rows}

## Match Levels

| Match level | Target rows |
| --- | ---: |
{level_rows}

The complete row-level availability table is `data/control_match_registry.csv`.

## Sparse Strata

| Layer | Target | Hebrew | Match level | Eligible controls |
| --- | --- | --- | --- | ---: |
{sparse_rows}

No numerical outcomes were calculated during this stage. The pool is ready to be committed before the simulation script is created or run.
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the blinded structural control pool")
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the locked openscriptures/morphhb checkout",
    )
    args = parser.parse_args()

    targets = load_targets()
    pool, counts, tree_hash = extract_pool(args.source.resolve(), targets)
    matches = make_match_rows(targets, pool)
    write_dataclass_csv(POOL_OUT, pool)
    write_dataclass_csv(MATCH_OUT, matches)
    write_source_lock(tree_hash)
    write_report(pool, matches, counts)

    print(f"targets: {len(targets)}")
    print(f"control phrases: {len(pool)}")
    print(f"wrote {POOL_OUT}")
    print(f"wrote {MATCH_OUT}")
    print(f"wrote {SOURCE_LOCK_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
