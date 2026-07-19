from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import (
    MISPAR_GADOL_VALUES,
    STANDARD_VALUES,
    collapse_base12_text,
    collapse_decimal,
    gematria,
    hebrew_letters,
    is_palindrome,
    make_rows,
    to_base,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"

FINAL_TO_MEDIAL = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}
MEDIAL_TO_FINAL = {value: key for key, value in FINAL_TO_MEDIAL.items()}
ABBREVIATION_MARKERS = set("\"'`״׳")
HEBREW_WORD_RE = re.compile(r"[א-ת]+")
CONSTANTS = {
    3: "AB",
    22: "YHWH-base12-signature",
    26: "YHWH-standard",
    42: "forty-two",
    45: "MAH",
    52: "BEN-standard",
    63: "SAG",
    72: "seventy-two",
    314: "Shaddai",
    345: "El-Shaddai/Moses",
    386: "Yeshua",
    655: "Tanakh-chapter-base12-prefix",
}


@dataclass(frozen=True)
class Candidate:
    label: str
    hebrew: str
    note: str


@dataclass
class VariantRow:
    source_index: int
    source_name: str
    source_hebrew: str
    source_scope: str
    variant_label: str
    hebrew_variant: str
    note: str
    standard: int
    mispar_gadol: int
    base12_standard: str
    base12_mispar_gadol: str
    collapse_standard: int
    collapse_mispar_gadol: int
    collapse_base12_standard: int
    collapse_base12_mispar_gadol: int
    standard_base12_palindrome: str
    mispar_base12_palindrome: str
    final_letter_notes: str
    interesting_hits: str
    gained_against_original: str
    lost_against_original: str


def has_abbreviation_marker(text: str) -> bool:
    return any(ch in ABBREVIATION_MARKERS for ch in text)


def split_words(text: str) -> list[str]:
    return [word for word in re.split(r"\s+", text.strip()) if word]


def join_words(words: list[str]) -> str:
    return " ".join(words)


def normalize_final_letters(text: str) -> str:
    if has_abbreviation_marker(text):
        return text
    chars = list(text)
    for match in HEBREW_WORD_RE.finditer(text):
        start, end = match.span()
        for index in range(start, end):
            ch = chars[index]
            is_last = index == end - 1
            if is_last and ch in MEDIAL_TO_FINAL:
                chars[index] = MEDIAL_TO_FINAL[ch]
            elif not is_last and ch in FINAL_TO_MEDIAL:
                chars[index] = FINAL_TO_MEDIAL[ch]
    return "".join(chars)


def final_letter_notes(text: str) -> list[str]:
    if has_abbreviation_marker(text):
        return ["abbreviation-or-name-marker:final-normalization-skipped"]
    notes: list[str] = []
    for match in HEBREW_WORD_RE.finditer(text):
        word = match.group(0)
        start, end = match.span()
        for index, ch in enumerate(word):
            absolute = start + index
            is_last = absolute == end - 1
            if ch in FINAL_TO_MEDIAL and not is_last:
                notes.append(f"final-form-inside-word:{word}")
            elif ch in MEDIAL_TO_FINAL and is_last:
                notes.append(f"word-final-medial-form:{word}:{ch}->{MEDIAL_TO_FINAL[ch]}")
    return notes


def add_candidate(
    candidates: list[Candidate],
    seen: set[str],
    label: str,
    hebrew: str,
    note: str,
) -> None:
    normalized = re.sub(r"\s+", " ", hebrew.strip())
    if not normalized or normalized in seen or not hebrew_letters(normalized):
        return
    candidates.append(Candidate(label, normalized, note))
    seen.add(normalized)


def generated_candidates(row) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[str] = set()
    original = row.hebrew
    add_candidate(candidates, seen, "original", original, "paper heading")

    if row.scope != "literal-heading":
        return candidates

    if original == "שכינה":
        add_candidate(
            candidates,
            seen,
            "hashekhinah_specific",
            "השכינה",
            "specific candidate for the intended Shekhinah 12-collapse claim",
        )

    normalized_finals = normalize_final_letters(original)
    if normalized_finals != original:
        add_candidate(
            candidates,
            seen,
            "final_normalized",
            normalized_finals,
            "mechanical contextual normalization of Hebrew final-letter forms",
        )

    words = split_words(original)
    if not words:
        return candidates

    first = words[0]
    if first.startswith("ה") and len(first) > 1:
        add_candidate(
            candidates,
            seen,
            "remove_ha_first_word",
            join_words([first[1:], *words[1:]]),
            "mechanical removal of definite article from first word",
        )
    elif first != "אל":
        add_candidate(
            candidates,
            seen,
            "add_ha_first_word",
            join_words([f"ה{first}", *words[1:]]),
            "mechanical addition of definite article to first word",
        )

    if first == "אל" and len(words) > 1:
        second = words[1]
        add_candidate(
            candidates,
            seen,
            "remove_initial_el",
            join_words(words[1:]),
            "mechanical removal of initial El",
        )
        if second.startswith("ה") and len(second) > 1:
            add_candidate(
                candidates,
                seen,
                "remove_ha_after_el",
                join_words([first, second[1:], *words[2:]]),
                "mechanical removal of definite article after El",
            )
        else:
            add_candidate(
                candidates,
                seen,
                "add_ha_after_el",
                join_words([first, f"ה{second}", *words[2:]]),
                "mechanical addition of definite article after El",
            )

    if first != "אל" and len(words) == 1:
        add_candidate(
            candidates,
            seen,
            "add_initial_el",
            f"אל {original}",
            "mechanical addition of initial El before a single-word title",
        )

    if first == "אלוהי" and len(words) > 1:
        add_candidate(
            candidates,
            seen,
            "construct_defective_אלהי",
            join_words(["אלהי", *words[1:]]),
            "spelling-sensitive construct variant; requires philological review",
        )
        add_candidate(
            candidates,
            seen,
            "absolute_elohim_אלהים",
            join_words(["אלהים", *words[1:]]),
            "absolute-form control variant; not a presumed correction",
        )

    return candidates


def signature_markers(
    standard: int,
    mispar: int,
    base12_standard: str,
    base12_mispar: str,
) -> set[str]:
    markers: set[str] = set()
    for basis, value, base12_text in [
        ("std", standard, base12_standard),
        ("mg", mispar, base12_mispar),
    ]:
        collapse = collapse_decimal(value)
        base12_collapse = collapse_base12_text(base12_text)
        if collapse in {8, 12}:
            markers.add(f"{basis}-collapse-{collapse}")
        if base12_collapse in {8, 12}:
            markers.add(f"{basis}-base12-collapse-{base12_collapse}")
        if is_palindrome(str(value)):
            markers.add(f"{basis}-base10-palindrome")
        if is_palindrome(base12_text):
            markers.add(f"{basis}-base12-palindrome")
        if value in CONSTANTS:
            markers.add(f"{basis}-constant-{value}:{CONSTANTS[value]}")
        if base12_text == "22":
            markers.add(f"{basis}-base12-22:YHWH-frame")
        if len(base12_text) >= 3 and base12_text[0] == "2" and base12_text[-1] == "2":
            markers.add(f"{basis}-outer-2-frame:{base12_text}")
        if base12_text == "282":
            markers.add(f"{basis}-yeshua-bridge-282")
    return markers


def variant_row(row, candidate: Candidate) -> VariantRow:
    standard = gematria(candidate.hebrew, STANDARD_VALUES)
    mispar = gematria(candidate.hebrew, MISPAR_GADOL_VALUES)
    base12_standard = to_base(standard)
    base12_mispar = to_base(mispar)
    original_markers = signature_markers(
        row.computed_standard,
        row.computed_mispar_gadol,
        row.base12_standard,
        row.base12_mispar_gadol,
    )
    variant_markers = signature_markers(standard, mispar, base12_standard, base12_mispar)
    gained = sorted(variant_markers - original_markers)
    lost = sorted(original_markers - variant_markers)
    return VariantRow(
        source_index=row.index,
        source_name=row.name,
        source_hebrew=row.hebrew,
        source_scope=row.scope,
        variant_label=candidate.label,
        hebrew_variant=candidate.hebrew,
        note=candidate.note,
        standard=standard,
        mispar_gadol=mispar,
        base12_standard=base12_standard,
        base12_mispar_gadol=base12_mispar,
        collapse_standard=collapse_decimal(standard),
        collapse_mispar_gadol=collapse_decimal(mispar),
        collapse_base12_standard=collapse_base12_text(base12_standard),
        collapse_base12_mispar_gadol=collapse_base12_text(base12_mispar),
        standard_base12_palindrome="yes" if is_palindrome(base12_standard) else "no",
        mispar_base12_palindrome="yes" if is_palindrome(base12_mispar) else "no",
        final_letter_notes="; ".join(final_letter_notes(candidate.hebrew)),
        interesting_hits="; ".join(sorted(variant_markers)),
        gained_against_original="; ".join(gained),
        lost_against_original="; ".join(lost),
    )


def make_variant_rows() -> list[VariantRow]:
    rows = make_rows()
    variants: list[VariantRow] = []
    for row in rows:
        for candidate in generated_candidates(row):
            variants.append(variant_row(row, candidate))
    return variants


def write_csv(rows: list[VariantRow]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / "variant_audit.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def markdown_table(rows: list[VariantRow], limit: int | None = None) -> str:
    selected = rows[:limit] if limit else rows
    headers = [
        "Source",
        "Variant",
        "Hebrew",
        "Std",
        "MG",
        "B12 Std/MG",
        "Collapses",
        "Gained",
        "Lost",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in selected:
        collapse = (
            f"{row.collapse_standard}/{row.collapse_mispar_gadol}/"
            f"{row.collapse_base12_standard}/{row.collapse_base12_mispar_gadol}"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{row.source_index}. {row.source_name}",
                    row.variant_label,
                    row.hebrew_variant,
                    str(row.standard),
                    str(row.mispar_gadol),
                    f"{row.base12_standard}/{row.base12_mispar_gadol}",
                    collapse,
                    row.gained_against_original or "-",
                    row.lost_against_original or "-",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def review_note(row: VariantRow) -> str:
    key = (row.source_name, row.variant_label)
    notes = {
        ("Yeshua", "original"): "Primary bridge: `282_12`, decimal 8, base-12 collapse 12.",
        ("Yeshua", "add_ha_first_word"): "Control: adding `Ha` destroys the `282_12` bridge.",
        ("Yeshua", "add_initial_el"): "Control: adding `El` gives decimal 12 but loses the `282_12` frame.",
        ("Shekhinah", "original"): "No strict 12-collapse; keep as thematic/domain unless form changes.",
        ("Shekhinah", "hashekhinah_specific"): "Plausible strict decimal 12-collapse source.",
        ("HaKadosh Baruch Hu", "original"): "Full form preserves `655` standard and `7A7_12` Mispar Gadol.",
        ("HaKadosh Baruch Hu", "remove_ha_first_word"): "Explains current `650` claim but loses the full-form `7A7_12` result.",
        ("Shaddai", "original"): "`314 = 222_12`; strong 8/identity pattern.",
        ("Shaddai", "add_initial_el"): "Becomes `El Shaddai = 345`; meaningful shift to 12-domain.",
        ("El Shaddai", "original"): "`345` result should be treated as its own primary form.",
        ("El Shaddai", "remove_initial_el"): "Returns to Shaddai `314/222_12`; useful paired comparison.",
        ("El De’ot", "original"): "Heading does not support final-tsadi logic; current value is neutral.",
        ("El De’ot", "remove_initial_el"): "Bare `De'ot` gives decimal 12, but this is only a control.",
        ("El De’ot", "add_ha_after_el"): "`El HaDe'ot` gives decimal 12, but requires attestation review.",
    }
    return notes.get(key, "")


def review_table(rows: list[VariantRow]) -> str:
    headers = [
        "Source",
        "Variant",
        "Hebrew",
        "Std",
        "MG",
        "B12 Std/MG",
        "Collapses",
        "Review Note",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        collapse = (
            f"{row.collapse_standard}/{row.collapse_mispar_gadol}/"
            f"{row.collapse_base12_standard}/{row.collapse_base12_mispar_gadol}"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{row.source_index}. {row.source_name}",
                    row.variant_label,
                    row.hebrew_variant,
                    str(row.standard),
                    str(row.mispar_gadol),
                    f"{row.base12_standard}/{row.base12_mispar_gadol}",
                    collapse,
                    review_note(row) or "-",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def selected_review_rows(rows: list[VariantRow]) -> list[VariantRow]:
    selections = [
        ("Yeshua", "original"),
        ("Yeshua", "add_ha_first_word"),
        ("Yeshua", "add_initial_el"),
        ("Shekhinah", "original"),
        ("Shekhinah", "hashekhinah_specific"),
        ("HaKadosh Baruch Hu", "original"),
        ("HaKadosh Baruch Hu", "remove_ha_first_word"),
        ("Shaddai", "original"),
        ("Shaddai", "add_initial_el"),
        ("El Shaddai", "original"),
        ("El Shaddai", "remove_initial_el"),
        ("El De’ot", "original"),
        ("El De’ot", "remove_initial_el"),
        ("El De’ot", "add_ha_after_el"),
    ]
    lookup = {(row.source_name, row.variant_label): row for row in rows}
    return [lookup[key] for key in selections if key in lookup]


def write_report(rows: list[VariantRow]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    originals = [row for row in rows if row.variant_label == "original"]
    generated = [row for row in rows if row.variant_label != "original"]
    variants_with_gains = [row for row in generated if row.gained_against_original]
    final_notes = [row for row in originals if row.final_letter_notes]
    final_anomalies = [
        row
        for row in final_notes
        if "abbreviation-or-name-marker" not in row.final_letter_notes
    ]
    review_rows = selected_review_rows(rows)
    yeshua = next(
        row
        for row in originals
        if row.source_name == "Yeshua"
    )
    shekhinah_variant = next(
        row
        for row in rows
        if row.source_name == "Shekhinah" and row.variant_label == "hashekhinah_specific"
    )

    content = f"""# Spelling and Form Variant Audit

This audit was generated by `scripts/variant_audit.py`.

The audit is mechanical. It is meant to show where results depend on spelling, article choice, construct form, or final-letter treatment. A generated variant is a candidate for review, not a correction.

## Outputs

- `data/variant_audit.csv` - original rows plus generated form variants.

## Summary

- Source rows: {len(originals)}
- Generated variant rows: {len(generated)}
- Generated variants that gain at least one structural marker: {len(variants_with_gains)}
- Original non-abbreviation headings with final-letter-form anomalies: {len(final_anomalies)}
- Abbreviation/name-marker rows skipped by final-letter normalizer: {len(final_notes) - len(final_anomalies)}

Collapse column order in the tables is:

`standard / Mispar Gadol / base-12 standard digit-collapse / base-12 Mispar Gadol digit-collapse`

## Main Findings

### Yeshua Remains a Strong Result

The original heading already gives the result that matters:

`Yeshua / ישוע = {yeshua.standard}_10 = {yeshua.base12_standard}_12`

This is not a variant-dependent result. It has:

- decimal collapse to `{yeshua.collapse_standard}`
- base-12 notation collapse to `{yeshua.collapse_base12_standard}`
- base-12 palindrome: `{yeshua.base12_standard}`
- outer `2 ... 2` frame with central `8`

This supports the revision-queue idea that `282_12` should be treated as a major bridge pattern: `8` inside the `22_12` YHWH frame.

### HaShekhinah Explains the 12-Collapse Candidate

The original heading `שכינה` computes to `385`, collapse `7`.

The generated specific candidate `השכינה` computes to:

`השכינה = {shekhinah_variant.standard}_10 = {shekhinah_variant.base12_standard}_12`

That gives a strict decimal collapse to `{shekhinah_variant.collapse_standard}`.

This does not prove the paper should change the heading, but it does show a plausible source for the intended 12-domain assignment. The paper should distinguish:

- `Shekhinah / שכינה`: thematic or presence-domain assignment, not strict collapse
- `HaShekhinah / השכינה`: strict decimal 12-collapse candidate

### HaKadosh Baruch Hu Likely Mixes Two Forms

The original heading `הקדוש ברוך הוא` computes to:

`655_10 = 467_12` by standard gematria

and:

`1135_10 = 7A7_12` by Mispar Gadol

The paper's current standard value of `650` is exactly the value of the no-article variant:

`קדוש ברוך הוא = 650_10`

So the likely issue is not random arithmetic noise. The paper appears to combine the standard value from `קדוש ברוך הוא` with the Mispar Gadol/base-12 result from `הקדוש ברוך הוא`. This should be corrected explicitly by choosing one primary form or presenting both forms as separate rows.

### Shaddai / El Shaddai Is a Real Pair, Not a Cleanup Error

The variant audit also confirms a meaningful relationship between `שדי` and `אל שדי`:

- `שדי = 314_10 = 222_12`, decimal collapse `8`
- `אל שדי = 345_10 = 249_12`, decimal collapse `12`

This is an example where adding `El` is not merely a mechanical variant. It shifts the name from the Shaddai `8`/`222_12` identity pattern into the `345`/`12` pattern associated with `El Shaddai`.

### Article and `El` Variants Are Fragile

Adding or removing `Ha` and `El` often changes collapse and palindrome status. This means article-bearing forms should be justified as chosen forms, not treated as interchangeable spellings.

The strongest lesson is methodological: the paper should state whether each Hebrew form is canonical, liturgical, construct, absolute, or a deliberately tested variant.

### Final-Letter Rules Need Targeted Review

The mechanical final-letter check mostly confirms that the headings themselves are internally well formed. The biggest existing problems are therefore not usually in the Hebrew heading, but in the prose calculations applying Mispar Gadol to a non-final letter or to a different word than the heading displays.

Rows already identified by the numerical audit remain the priority:

- `Adonai`: the paper appears to apply Mispar Gadol to `נ`, but `נ` is not final in `אדני`.
- `El De'ot`: the paper appears to apply a final-tsadi rule where the heading ends in tav.
- `Elohei Yitzchak`: same possible final-tsadi issue if the prose treats `צ` as final when the heading ends in `ק`.
- `HaKadosh Baruch Hu`: the heading's final letters are fine, but the prose seems to combine two article variants and may include a stray final-tsadi calculation.

## High-Priority Review Rows

{review_table(review_rows)}

## Full Variant Table

The full mechanical list is in `data/variant_audit.csv`. Many generated rows are useful only as controls, not as candidates for the paper.

## Original Rows With Final-Letter Notes

{markdown_table(final_notes, limit=40) if final_notes else "No original headings were flagged by the mechanical final-letter-form check."}

No original non-abbreviation heading was flagged as malformed by the mechanical final-letter-form check. The rows above are abbreviation/name-marker cases where automatic normalization is intentionally skipped.

## Working Rule For The Paper

The cleanup should not silently substitute variants. Instead, each name should get one of these labels:

- `primary form`: the form actually analyzed in the corpus
- `attested/liturgical variant`: a form worth including as a secondary result
- `mechanical control`: a generated comparison used only to test fragility
- `thematic assignment`: a domain assignment not based on strict collapse

This protects the strongest results while making the weaker or form-sensitive claims much easier to defend.
"""
    (DOCS_DIR / "VARIANT_AUDIT.md").write_text(content, encoding="utf-8")


def main() -> None:
    rows = make_variant_rows()
    write_csv(rows)
    write_report(rows)
    print(f"wrote {DATA_DIR / 'variant_audit.csv'}")
    print(f"wrote {DOCS_DIR / 'VARIANT_AUDIT.md'}")


if __name__ == "__main__":
    main()
