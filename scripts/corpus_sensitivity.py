from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import (
    MISPAR_GADOL_VALUES,
    STANDARD_VALUES,
    collapse_base12_text,
    collapse_decimal,
    gematria,
    is_palindrome,
    to_base,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "corpus_registry.csv"
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass
class CorrectedValue:
    index: int
    name: str
    corpus_layer: str
    displayed_hebrew: str
    analysis_hebrew: str
    form_changed: str
    standard_gematria: int
    mispar_gadol: int
    base12_standard: str
    base12_mispar_gadol: str
    decimal_collapse_standard: int
    decimal_collapse_mispar_gadol: int
    base12_collapse_standard: int
    base12_collapse_mispar_gadol: int
    base10_palindrome_any: str
    base12_palindrome_any: str


@dataclass
class SensitivitySummary:
    corpus_slice: str
    row_count: int
    strict_8_count: int
    strict_12_count: int
    base10_palindrome_count: int
    base12_palindrome_count: int
    standard_base12_palindrome_count: int
    standard_base12_palindrome_rank: int
    standard_leading_bases: str
    mispar_base12_palindrome_count: int
    mispar_base12_palindrome_rank: int
    mispar_leading_bases: str


def load_registry() -> list[dict[str, str]]:
    with REGISTRY.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def make_values(rows: list[dict[str, str]]) -> list[CorrectedValue]:
    values: list[CorrectedValue] = []
    for row in rows:
        hebrew = row["analysis_hebrew"].strip()
        if not hebrew:
            continue
        standard = gematria(hebrew, STANDARD_VALUES)
        mispar = gematria(hebrew, MISPAR_GADOL_VALUES)
        base12_standard = to_base(standard)
        base12_mispar = to_base(mispar)
        values.append(
            CorrectedValue(
                index=int(row["index"]),
                name=row["name"],
                corpus_layer=row["corpus_layer"],
                displayed_hebrew=row["displayed_hebrew"],
                analysis_hebrew=hebrew,
                form_changed="yes" if hebrew != row["displayed_hebrew"] else "no",
                standard_gematria=standard,
                mispar_gadol=mispar,
                base12_standard=base12_standard,
                base12_mispar_gadol=base12_mispar,
                decimal_collapse_standard=collapse_decimal(standard),
                decimal_collapse_mispar_gadol=collapse_decimal(mispar),
                base12_collapse_standard=collapse_base12_text(base12_standard),
                base12_collapse_mispar_gadol=collapse_base12_text(base12_mispar),
                base10_palindrome_any=(
                    "yes" if is_palindrome(str(standard)) or is_palindrome(str(mispar)) else "no"
                ),
                base12_palindrome_any=(
                    "yes" if is_palindrome(base12_standard) or is_palindrome(base12_mispar) else "no"
                ),
            )
        )
    return values


def to_any_base(value: int, base: int) -> str:
    if value == 0:
        return "0"
    out: list[str] = []
    current = value
    while current:
        current, remainder = divmod(current, base)
        out.append(DIGITS[remainder])
    return "".join(reversed(out))


def palindrome_counts(rows: list[CorrectedValue], field: str) -> dict[int, int]:
    counts: dict[int, int] = {}
    for base in range(2, 21):
        count = 0
        for row in rows:
            representation = to_any_base(getattr(row, field), base)
            if is_palindrome(representation):
                count += 1
        counts[base] = count
    return counts


def competition_rank(counts: dict[int, int], base: int) -> int:
    target = counts[base]
    return 1 + sum(1 for count in counts.values() if count > target)


def leading_bases(counts: dict[int, int]) -> str:
    high = max(counts.values())
    return "; ".join(str(base) for base, count in counts.items() if count == high)


def summarize(name: str, rows: list[CorrectedValue]) -> SensitivitySummary:
    strict_8 = 0
    strict_12 = 0
    for row in rows:
        endpoints = {
            row.decimal_collapse_standard,
            row.decimal_collapse_mispar_gadol,
            row.base12_collapse_standard,
            row.base12_collapse_mispar_gadol,
        }
        strict_8 += 8 in endpoints
        strict_12 += 12 in endpoints

    standard_counts = palindrome_counts(rows, "standard_gematria")
    mispar_counts = palindrome_counts(rows, "mispar_gadol")
    return SensitivitySummary(
        corpus_slice=name,
        row_count=len(rows),
        strict_8_count=strict_8,
        strict_12_count=strict_12,
        base10_palindrome_count=sum(row.base10_palindrome_any == "yes" for row in rows),
        base12_palindrome_count=sum(row.base12_palindrome_any == "yes" for row in rows),
        standard_base12_palindrome_count=standard_counts[12],
        standard_base12_palindrome_rank=competition_rank(standard_counts, 12),
        standard_leading_bases=leading_bases(standard_counts),
        mispar_base12_palindrome_count=mispar_counts[12],
        mispar_base12_palindrome_rank=competition_rank(mispar_counts, 12),
        mispar_leading_bases=leading_bases(mispar_counts),
    )


def write_csv(path: Path, rows: list[object]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def changed_forms_table(values: list[CorrectedValue]) -> str:
    changed = [row for row in values if row.form_changed == "yes"]
    lines = [
        "| Name | Displayed | Source-controlled | Standard | Mispar Gadol | Base 12 (std./MG) |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in changed:
        lines.append(
            f"| {row.name} | `{row.displayed_hebrew}` | `{row.analysis_hebrew}` | "
            f"{row.standard_gematria} | {row.mispar_gadol} | "
            f"`{row.base12_standard}` / `{row.base12_mispar_gadol}` |"
        )
    return "\n".join(lines)


def summary_table(rows: list[SensitivitySummary]) -> str:
    lines = [
        "| Slice | N | Strict 8 | Strict 12 | Base-10 pal. | Base-12 pal. (any) | Base 12 std. count/rank | Base 12 MG count/rank |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.corpus_slice} | {row.row_count} | {row.strict_8_count} | "
            f"{row.strict_12_count} | {row.base10_palindrome_count} | "
            f"{row.base12_palindrome_count} | {row.standard_base12_palindrome_count} / "
            f"rank {row.standard_base12_palindrome_rank} | {row.mispar_base12_palindrome_count} / "
            f"rank {row.mispar_base12_palindrome_rank} |"
        )
    return "\n".join(lines)


def write_report(values: list[CorrectedValue], summaries: list[SensitivitySummary]) -> None:
    primary = next(row for row in summaries if row.corpus_slice == "primary-biblical")
    christian = next(
        row for row in summaries
        if row.corpus_slice == "primary-plus-messianic-comparative"
    )
    all_names = next(row for row in summaries if row.corpus_slice == "all-name-layers")
    content = f"""# Source-Controlled Corpus Sensitivity

This report is generated by `scripts/corpus_sensitivity.py` from `data/corpus_registry.csv`. It does not reuse the inherited row totals after a source form changes.

## Results

{summary_table(summaries)}

The source-controlled primary biblical corpus contains {primary.row_count} rows. Within that Hebrew-Bible-only slice, base 12 produces {primary.standard_base12_palindrome_count} standard-value palindromes (rank {primary.standard_base12_palindrome_rank} among bases 2-20) and {primary.mispar_base12_palindrome_count} Mispar Gadol palindromes (rank {primary.mispar_base12_palindrome_rank}). The leading standard-value base(s) are {primary.standard_leading_bases}; the leading Mispar Gadol base(s) are {primary.mispar_leading_bases}.

That is not a corpus-independent ranking. When the Christian messianic layer is joined to the primary biblical rows, base 12 has {christian.standard_base12_palindrome_count} standard-value palindromes (rank {christian.standard_base12_palindrome_rank}) and {christian.mispar_base12_palindrome_count} Mispar Gadol palindromes (rank {christian.mispar_base12_palindrome_rank}, tied between bases {christian.mispar_leading_bases.replace("; ", " and ")}). Across all declared name layers, base 12 has {all_names.mispar_base12_palindrome_count} Mispar Gadol palindromes and ranks {all_names.mispar_base12_palindrome_rank}, with base {all_names.mispar_leading_bases} as the leader. The source correction therefore changes some specified slice rankings, but it does not justify an unqualified claim that base 12's overall ranking has fallen.

The base-12 case is nontrivial: its primary palindromes are concentrated in `YHWH`, `Adonai`, `Shaddai`, `Ehyeh Asher Ehyeh`, and, through Mispar Gadol, `El Olam`; `Yeshua` adds `282_12` in the Christian messianic layer. The defensible claim is that the ranking depends on the declared corpus and value system, while the named structural cluster persists across those choices and requires matched controls.

## Corrected Forms

{changed_forms_table(values)}

The changed-form table also includes later, comparative, and expansion layers so that every inherited spelling change remains visible. Rows with false syntactic matches have no `analysis_hebrew` value and are not recalculated.

## Layer Policy

- `primary-biblical` is the repository-locked primary analysis set; it derives from an inherited, previously inspected list.
- `primary-plus-later-traditional` tests whether rabbinic and liturgical names alter the result.
- `primary-plus-messianic-comparative` admits Yeshua and messianic titles under the manuscript's Christian theological framework. The label records that they are not an independently selected Hebrew-Bible divine-name sample; it does not deny or downgrade Yeshua's divine status in Christian theology.
- `all-name-layers` combines those three declared name layers but still excludes foreign-deity, constructed, formula-label, and expansion-label rows.

These are sensitivity slices, not independent samples. No p-value is claimed.
"""
    (DOCS_DIR / "CORPUS_SENSITIVITY.md").write_text(content, encoding="utf-8")


def main() -> None:
    registry = load_registry()
    values = make_values(registry)
    by_layer: dict[str, list[CorrectedValue]] = {}
    for row in values:
        by_layer.setdefault(row.corpus_layer, []).append(row)

    primary = by_layer["primary-biblical"]
    later = by_layer["later-traditional"]
    messianic = by_layer["messianic-comparative"]
    summaries = [
        summarize("primary-biblical", primary),
        summarize("primary-plus-later-traditional", primary + later),
        summarize("primary-plus-messianic-comparative", primary + messianic),
        summarize("all-name-layers", primary + later + messianic),
    ]

    write_csv(DATA_DIR / "corpus_corrected_values.csv", values)
    write_csv(DATA_DIR / "corpus_sensitivity_summary.csv", summaries)
    write_report(values, summaries)
    print(f"registry rows: {len(registry)}")
    print(f"recalculated rows: {len(values)}")
    print(f"primary biblical rows: {len(primary)}")
    print(f"wrote {DATA_DIR / 'corpus_corrected_values.csv'}")
    print(f"wrote {DATA_DIR / 'corpus_sensitivity_summary.csv'}")
    print(f"wrote {DOCS_DIR / 'CORPUS_SENSITIVITY.md'}")


if __name__ == "__main__":
    main()
