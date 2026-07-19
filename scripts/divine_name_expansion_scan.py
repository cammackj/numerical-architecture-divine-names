from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import (
    MISPAR_GADOL_VALUES,
    STANDARD_VALUES,
    gematria,
    is_palindrome,
    to_base,
)
from corpus_sensitivity import competition_rank, palindrome_counts


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "data" / "divine_name_expansion_candidates.csv"
CURRENT_VALUES = ROOT / "data" / "corpus_corrected_values.csv"
RESULTS = ROOT / "data" / "divine_name_expansion_results.csv"
REPORT = ROOT / "docs" / "DIVINE_NAME_EXPANSION_SCAN.md"


@dataclass
class ExpansionResult:
    candidate_id: int
    name: str
    hebrew: str
    layer: str
    object_class: str
    attestation_status: str
    representative_source: str
    source_url: str
    broad_biblical_scan: str
    standard_gematria: int
    mispar_gadol: int
    base12_standard: str
    base12_mispar_gadol: str
    standard_base12_palindrome: str
    mispar_base12_palindrome: str
    base12_palindrome_any: str
    notes: str


@dataclass
class ValuePair:
    standard_gematria: int
    mispar_gadol: int


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def calculate(rows: list[dict[str, str]]) -> list[ExpansionResult]:
    results: list[ExpansionResult] = []
    for row in rows:
        standard = gematria(row["hebrew"], STANDARD_VALUES)
        mispar = gematria(row["hebrew"], MISPAR_GADOL_VALUES)
        base12_standard = to_base(standard)
        base12_mispar = to_base(mispar)
        standard_palindrome = is_palindrome(base12_standard)
        mispar_palindrome = is_palindrome(base12_mispar)
        results.append(
            ExpansionResult(
                candidate_id=int(row["candidate_id"]),
                name=row["name"],
                hebrew=row["hebrew"],
                layer=row["layer"],
                object_class=row["object_class"],
                attestation_status=row["attestation_status"],
                representative_source=row["representative_source"],
                source_url=row["source_url"],
                broad_biblical_scan=row["broad_biblical_scan"],
                standard_gematria=standard,
                mispar_gadol=mispar,
                base12_standard=base12_standard,
                base12_mispar_gadol=base12_mispar,
                standard_base12_palindrome="yes" if standard_palindrome else "no",
                mispar_base12_palindrome="yes" if mispar_palindrome else "no",
                base12_palindrome_any="yes" if standard_palindrome or mispar_palindrome else "no",
                notes=row["notes"],
            )
        )
    return results


def write_results(rows: list[ExpansionResult]) -> None:
    with RESULTS.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def source_cell(row: ExpansionResult) -> str:
    if row.source_url:
        return f"[{row.representative_source}]({row.source_url})"
    return row.representative_source or "Source lock pending"


def hit_table(rows: list[ExpansionResult]) -> str:
    lines = [
        "| Name | Hebrew | Layer | Status | Standard | Base 12 | Mispar Gadol | Base 12 | Source |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        standard = (
            f"**`{row.base12_standard}`**"
            if row.standard_base12_palindrome == "yes"
            else f"`{row.base12_standard}`"
        )
        mispar = (
            f"**`{row.base12_mispar_gadol}`**"
            if row.mispar_base12_palindrome == "yes"
            else f"`{row.base12_mispar_gadol}`"
        )
        lines.append(
            f"| {row.name} | `{row.hebrew}` | {row.layer} | {row.attestation_status} | "
            f"{row.standard_gematria} | {standard} | {row.mispar_gadol} | {mispar} | "
            f"{source_cell(row)} |"
        )
    return "\n".join(lines)


def expanded_biblical_ranking(
    rows: list[ExpansionResult],
) -> tuple[int, dict[int, int], dict[int, int]]:
    current = [
        ValuePair(int(row["standard_gematria"]), int(row["mispar_gadol"]))
        for row in load_csv(CURRENT_VALUES)
        if row["corpus_layer"] == "primary-biblical"
    ]
    additions = [
        ValuePair(row.standard_gematria, row.mispar_gadol)
        for row in rows
        if row.broad_biblical_scan == "yes"
    ]
    combined = current + additions
    standard_counts = palindrome_counts(combined, "standard_gematria")
    mispar_counts = palindrome_counts(combined, "mispar_gadol")

    return len(combined), standard_counts, mispar_counts


def leading_bases(counts: dict[int, int]) -> str:
    maximum = max(counts.values())
    return ", ".join(str(base) for base, count in counts.items() if count == maximum)


def nearest_other_bases(counts: dict[int, int]) -> tuple[str, int]:
    maximum = max(count for base, count in counts.items() if base != 12)
    bases = ", ".join(
        str(base) for base, count in counts.items() if base != 12 and count == maximum
    )
    return bases, maximum


def validate_results(rows: list[ExpansionResult]) -> None:
    ids = [row.candidate_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate candidate_id in expansion registry")
    if any(row.broad_biblical_scan == "yes" and row.layer != "primary-biblical-expansion" for row in rows):
        raise ValueError("Only biblical expansion rows may enter the broad biblical scan")

    expected_hits = {4, 5, 10, 16, 18, 22, 24, 25, 28, 57, 61, 62, 64, 66, 68, 69, 70, 74, 77, 81}
    actual_hits = {row.candidate_id for row in rows if row.base12_palindrome_any == "yes"}
    if actual_hits != expected_hits:
        raise ValueError(f"Expansion hit set changed: {sorted(actual_hits)}")

    expected_values = {
        4: (91, "77", 91, "77"),
        5: (39, "33", 39, "33"),
        10: (1039, "727", 3059, "192B"),
        16: (410, "2A2", 410, "2A2"),
        18: (592, "414", 592, "414"),
        22: (594, "416", 1244, "878"),
        24: (1087, "767", 1087, "767"),
        25: (631, "447", 1111, "787"),
        28: (664, "474", 1144, "7B4"),
        57: (117, "99", 597, "419"),
        61: (749, "525", 749, "525"),
    }
    by_id = {row.candidate_id: row for row in rows}
    for candidate_id, expected in expected_values.items():
        row = by_id[candidate_id]
        actual = (
            row.standard_gematria,
            row.base12_standard,
            row.mispar_gadol,
            row.base12_mispar_gadol,
        )
        if actual != expected:
            raise ValueError(f"Candidate {candidate_id} changed: {actual} != {expected}")


def write_report(rows: list[ExpansionResult]) -> None:
    hits = [row for row in rows if row.base12_palindrome_any == "yes"]
    biblical = [row for row in rows if row.layer == "primary-biblical-expansion"]
    christian = [row for row in rows if row.layer == "christian-comparative-expansion"]
    later = [row for row in rows if row.layer == "later-traditional-expansion"]
    biblical_hits = [row for row in biblical if row.base12_palindrome_any == "yes"]
    christian_hits = [row for row in christian if row.base12_palindrome_any == "yes"]
    later_hits = [row for row in later if row.base12_palindrome_any == "yes"]
    total, standard_counts, mispar_counts = expanded_biblical_ranking(rows)
    std_other_bases, std_other_count = nearest_other_bases(standard_counts)
    mg_other_bases, mg_other_count = nearest_other_bases(mispar_counts)

    content = f"""# Divine-Name Expansion Scan

This is a supplemental discovery scan. It does not silently add rows to the manuscript's frozen 24-row primary corpus. The registry preserves every candidate tested in this pass, including non-hits in `data/divine_name_expansion_results.csv`; it was assembled during exploration and is not an independently assembled primary sample.

## Scope

- {len(rows)} total candidate forms;
- {len(biblical)} source-declared biblical names, titles, metaphors, and identity formulas;
- {len(christian)} Christian-comparative or Hebrew-translation forms;
- {len(later)} later rabbinic, liturgical, or Kabbalistic forms.

The scan finds {len(hits)} candidates with a base-12 palindrome on at least one value layer: {len(biblical_hits)} biblical, {len(christian_hits)} Christian-comparative, and {len(later_hits)} later-traditional.

## Positive Results

{hit_table(hits)}

Bold base-12 digit strings are palindromes. A row can be palindromic under standard gematria, Mispar Gadol, or both.

## Broad Biblical Sensitivity

The broad comparison adds **all {len(biblical)} recorded biblical candidates**, not only the {len(biblical_hits)} positive rows, to the existing 24-row primary corpus. In that {total}-row exploratory set:

- base 12 produces {standard_counts[12]} standard-value palindromes and ranks {competition_rank(standard_counts, 12)} alone; the nearest other base is {std_other_bases} with {std_other_count};
- base 12 produces {mispar_counts[12]} Mispar Gadol palindromes and ranks {competition_rank(mispar_counts, 12)} alone; the nearest other base(s) are {mg_other_bases} with {mg_other_count}.

This is a descriptive sensitivity result, not a significance test. The expanded rows include nested expressions, metaphors, identity formulas, and symbolic altar or city names, so they are not independent observations.

## Admission Assessment

The strongest new biblical name or title candidates are:

- `Adonai YHWH / אדני יהוה = 91 = 77_12`;
- `El Elyon Qoneh Shamayim VaAretz / אל עליון קנה שמים וארץ = 1039 = 727_12`;
- `Qadosh / קדוש = 410 = 2A2_12`;
- `Kedosh Yaakov / קדוש יעקב = 592 = 414_12`;
- `Shomer Yisrael / שומר ישראל = 1087 = 767_12`;
- `Melekh Yisrael / מלך ישראל`, whose Mispar Gadol value is `1111 = 787_12`.

Two source-secure formula-level results should be reported separately rather than inflated into lexical-name counts:

- `YHWH Echad / יהוה אחד = 39 = 33_12` in the Shema;
- `YHWH Tzevaot Hu Melekh HaKavod / יהוה צבאות הוא מלך הכבוד = 664 = 474_12` in Psalm 24:10.

`Eben Yisrael / אבן ישראל` gives a Mispar Gadol palindrome `1244 = 878_12`, but its syntax and status as a divine epithet require philological review.

## Christian and Later Layers

`Yeshua HaMashiach / ישוע המשיח = 749 = 525_12` is the strongest Christian Hebrew title recovered for the current corpus because its spelling is conventional and the palindrome does not depend on final-letter expansion. The author reports having identified this palindrome before the present scan, although the combined title is absent from both the saved Word manuscript and the initial LaTeX transfer; it should therefore be treated as a restored prior observation, not claimed as a new discovery. `Malakh YHWH / מלאך יהוה = 117 = 99_12` is source-secure Hebrew, but admitting it as a divine designation depends on a Christian divine-agent reading.

Several translated Christian titles are orthography-sensitive. The defective spellings `אדנינו`, `האלהים`, and `הרעה` produce palindromes that disappear in common plene forms `אדונינו`, `האלוהים`, and `הרועה`. Bare `Amen / אמן = 91 = 77_12` is also palindromic, but Revelation 3:14 has the article-bearing Hebrew translation `HaAmen / האמן`, which is not. Those results must remain translation-specific or lexical-extraction observations rather than headline evidence.

The later layer adds `Melekh HaOlam / מלך העולם = 241 = 181_12`, `Avinu Shebashamayim / אבינו שבשמים = 761 = 535_12`, and the Aramaic `Qudsha Berikh Hu / קודשא בריך הוא`, whose Mispar Gadol value reproduces `1135 = 7A7_12`. The latter is numerically identical to the existing Hebrew `HaKadosh Baruch Hu` result and should be treated as a cross-language equivalence rather than an independent count.

## Next Decision

The frozen primary corpus should remain unchanged until the manuscript adopts a completeness rule for biblical epithets. Once that rule is fixed, this registry can supply a prospective expansion corpus without reselecting rows by outcome.
"""
    REPORT.write_text(content, encoding="utf-8")


def main() -> None:
    rows = calculate(load_csv(CANDIDATES))
    validate_results(rows)
    write_results(rows)
    write_report(rows)
    print(f"candidates: {len(rows)}")
    print(f"base-12 palindrome candidates: {sum(row.base12_palindrome_any == 'yes' for row in rows)}")
    print(f"wrote {RESULTS}")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
