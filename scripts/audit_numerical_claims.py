from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "corpus_registry.csv"
INHERITED_CLAIMS = ROOT / "data" / "inherited_claims_registry.csv"
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"


STANDARD_VALUES = {
    "א": 1,
    "ב": 2,
    "ג": 3,
    "ד": 4,
    "ה": 5,
    "ו": 6,
    "ז": 7,
    "ח": 8,
    "ט": 9,
    "י": 10,
    "כ": 20,
    "ך": 20,
    "ל": 30,
    "מ": 40,
    "ם": 40,
    "נ": 50,
    "ן": 50,
    "ס": 60,
    "ע": 70,
    "פ": 80,
    "ף": 80,
    "צ": 90,
    "ץ": 90,
    "ק": 100,
    "ר": 200,
    "ש": 300,
    "ת": 400,
}

MISPAR_GADOL_VALUES = {
    **STANDARD_VALUES,
    "ך": 500,
    "ם": 600,
    "ן": 700,
    "ף": 800,
    "ץ": 900,
}

DIGITS = "0123456789AB"


@dataclass
class AuditRow:
    index: int
    name: str
    hebrew: str
    inherited_hebrew: str
    corpus_layer: str
    object_class: str
    attestation_status: str
    representative_source: str
    source_url: str
    source_form: str
    recommended_action: str
    scope: str
    hebrew_letters: str
    computed_standard: int
    claimed_standard: str
    standard_match: str
    computed_mispar_gadol: int
    claimed_mispar_gadol: str
    mispar_gadol_match: str
    base12_standard: str
    base12_mispar_gadol: str
    base12_claim_basis: str
    claimed_base12: str
    base12_match: str
    collapse_standard: int
    collapse_mispar_gadol: int
    collapse_base12_standard: int
    collapse_base12_mispar_gadol: int
    standard_base10_palindrome: str
    mispar_base10_palindrome: str
    standard_base12_palindrome: str
    mispar_base12_palindrome: str
    claimed_cluster: str
    computed_domains: str
    review_flags: str


def to_base(value: int, base: int = 12) -> str:
    if value == 0:
        return "0"
    out: list[str] = []
    current = value
    while current:
        current, remainder = divmod(current, base)
        out.append(DIGITS[remainder])
    return "".join(reversed(out))


def digit_sum_decimal(value: int) -> int:
    return sum(int(ch) for ch in str(abs(value)))


def collapse_decimal(value: int, stop: int = 12) -> int:
    current = abs(value)
    while current > stop:
        current = digit_sum_decimal(current)
    return current


def collapse_base12_text(base12_text: str, stop: int = 12) -> int:
    total = sum(DIGITS.index(ch) for ch in base12_text)
    return collapse_decimal(total, stop=stop)


def is_palindrome(text: str) -> bool:
    return len(text) > 1 and text == text[::-1]


def hebrew_letters(text: str) -> str:
    return "".join(ch for ch in text if ch in STANDARD_VALUES)


def gematria(text: str, values: dict[str, int]) -> int:
    return sum(values[ch] for ch in hebrew_letters(text))


def parse_int(text: str) -> int | None:
    return int(text) if text and text.isdigit() else None


def compare_claim(computed: int, claimed: int | None, scope: str) -> str:
    if claimed is None:
        return ""
    if scope != "literal-heading":
        return "not compared"
    return "yes" if computed == claimed else "no"


def compare_text(computed: str, claimed: str, scope: str) -> str:
    if not claimed:
        return ""
    if scope != "literal-heading":
        return "not compared"
    return "yes" if computed == claimed else "no"


def row_scope(name: str, object_class: str) -> str:
    if name.startswith("The 42-Letter Name"):
        return "formula-not-in-heading"
    if name.startswith("The 72"):
        return "canonical-constant-not-heading"
    if object_class == "kabbalistic-expansion-label":
        return "expansion-label-not-name"
    return "literal-heading"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def computed_domains(
    standard: int,
    mispar: int,
    base12_standard: str,
    base12_mispar: str,
) -> list[str]:
    domains: list[str] = []
    for label, value in [("standard", standard), ("mispar", mispar)]:
        collapse = collapse_decimal(value)
        if collapse in {8, 12}:
            domains.append(f"{label}-collapse-{collapse}")
        if is_palindrome(str(value)):
            domains.append(f"{label}-base10-palindrome")
        if value in {22, 42, 72, 314, 345}:
            domains.append(f"{label}-constant-{value}")
    for label, value in [("standard-base12", base12_standard), ("mispar-base12", base12_mispar)]:
        collapse = collapse_base12_text(value)
        if collapse in {8, 12}:
            domains.append(f"{label}-collapse-{collapse}")
        if is_palindrome(value):
            domains.append(f"{label}-palindrome")
    return domains


def flags_for_row(row: AuditRow) -> list[str]:
    flags: list[str] = []
    if row.standard_match == "no":
        flags.append("standard-claim-mismatch")
    if row.mispar_gadol_match == "no":
        flags.append("mispar-gadol-claim-mismatch")
    if row.base12_match == "no":
        flags.append("base12-claim-mismatch")
    if row.scope != "literal-heading":
        flags.append(row.scope)
    cluster = row.claimed_cluster.lower()
    domains = row.computed_domains.lower()
    if "12-collapse" in cluster and "collapse-12" not in domains:
        flags.append("claimed-12-collapse-without-computed-12")
    if "8-collapse" in cluster and "collapse-8" not in domains:
        flags.append("claimed-8-collapse-without-computed-8")
    return flags


def make_rows() -> list[AuditRow]:
    registry = read_csv(REGISTRY)
    inherited_by_index = {
        int(row["index"]): row for row in read_csv(INHERITED_CLAIMS)
    }
    rows: list[AuditRow] = []
    for registry_row in registry:
        index = int(registry_row["index"])
        inherited = inherited_by_index[index]
        name = registry_row["name"]
        hebrew = registry_row["analysis_hebrew"].strip()
        if not hebrew:
            continue
        scope = row_scope(name, registry_row["object_class"])
        letters = hebrew_letters(hebrew)
        standard = gematria(hebrew, STANDARD_VALUES)
        mispar = gematria(hebrew, MISPAR_GADOL_VALUES)
        base12_standard = to_base(standard)
        base12_mispar = to_base(mispar)
        c_standard = parse_int(inherited["claimed_standard"])
        c_mispar = parse_int(inherited["claimed_mispar_gadol"])
        c_base12 = inherited["claimed_base12"]
        base12_claim_basis = inherited["base12_claim_basis"] or "mispar-gadol"
        if base12_claim_basis == "standard":
            base12_for_claim = base12_standard
        else:
            base12_for_claim = base12_mispar
        domains = computed_domains(standard, mispar, base12_standard, base12_mispar)
        row = AuditRow(
            index=index,
            name=name,
            hebrew=hebrew,
            inherited_hebrew=registry_row["displayed_hebrew"],
            corpus_layer=registry_row["corpus_layer"],
            object_class=registry_row["object_class"],
            attestation_status=registry_row["attestation_status"],
            representative_source=registry_row["representative_source"],
            source_url=registry_row["source_url"],
            source_form=registry_row["source_form"],
            recommended_action=registry_row["recommended_action"],
            scope=scope,
            hebrew_letters=letters,
            computed_standard=standard,
            claimed_standard="" if c_standard is None else str(c_standard),
            standard_match=compare_claim(standard, c_standard, scope),
            computed_mispar_gadol=mispar,
            claimed_mispar_gadol="" if c_mispar is None else str(c_mispar),
            mispar_gadol_match=compare_claim(mispar, c_mispar, scope),
            base12_standard=base12_standard,
            base12_mispar_gadol=base12_mispar,
            base12_claim_basis=base12_claim_basis,
            claimed_base12=c_base12,
            base12_match=compare_text(base12_for_claim, c_base12, scope),
            collapse_standard=collapse_decimal(standard),
            collapse_mispar_gadol=collapse_decimal(mispar),
            collapse_base12_standard=collapse_base12_text(base12_standard),
            collapse_base12_mispar_gadol=collapse_base12_text(base12_mispar),
            standard_base10_palindrome="yes" if is_palindrome(str(standard)) else "no",
            mispar_base10_palindrome="yes" if is_palindrome(str(mispar)) else "no",
            standard_base12_palindrome="yes" if is_palindrome(base12_standard) else "no",
            mispar_base12_palindrome="yes" if is_palindrome(base12_mispar) else "no",
            claimed_cluster=inherited["claimed_cluster"],
            computed_domains="; ".join(domains),
            review_flags="",
        )
        row.review_flags = "; ".join(flags_for_row(row))
        rows.append(row)
    return rows


def write_csv(rows: list[AuditRow]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / "master_results.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_flags_csv(rows: list[AuditRow]) -> None:
    out = DATA_DIR / "audit_flags.csv"
    flagged = [row for row in rows if row.review_flags]
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in flagged:
            writer.writerow(asdict(row))


def markdown_table(rows: list[AuditRow]) -> str:
    headers = [
        "#",
        "Name",
        "Scope",
        "Std",
        "MG",
        "B12 used",
        "Basis",
        "Collapses",
        "Palindromes",
        "Flags",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        b12_used = row.base12_standard if row.base12_claim_basis == "standard" else row.base12_mispar_gadol
        b12_collapse = (
            row.collapse_base12_standard
            if row.base12_claim_basis == "standard"
            else row.collapse_base12_mispar_gadol
        )
        collapse = f"{row.collapse_standard}/{row.collapse_mispar_gadol}/{b12_collapse}"
        pals = []
        if row.standard_base10_palindrome == "yes":
            pals.append("std10")
        if row.mispar_base10_palindrome == "yes":
            pals.append("mg10")
        if row.standard_base12_palindrome == "yes":
            pals.append("std12")
        if row.mispar_base12_palindrome == "yes":
            pals.append("mg12")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.index),
                    row.name,
                    row.scope,
                    str(row.computed_standard),
                    str(row.computed_mispar_gadol),
                    b12_used,
                    row.base12_claim_basis,
                    collapse,
                    ", ".join(pals) if pals else "-",
                    row.review_flags or "-",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def value_for(text: str, values: dict[str, int]) -> int:
    return gematria(text, values)


def write_findings(rows: list[AuditRow]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    flagged = [row for row in rows if row.review_flags]
    mismatches = [
        row
        for row in rows
        if "claim-mismatch" in row.review_flags
    ]
    strict_12 = [row for row in rows if "collapse-12" in row.computed_domains]
    strict_8 = [row for row in rows if "collapse-8" in row.computed_domains]

    scroll_decimal = int("6556", 12)
    scroll_base12_collapse = collapse_base12_text("6556")
    scroll_decimal_collapse = collapse_decimal(scroll_decimal)
    shekhinah = value_for("שכינה", STANDARD_VALUES)
    hashekhinah = value_for("השכינה", STANDARD_VALUES)

    content = f"""# Numerical Audit Findings

This audit was generated by `scripts/audit_numerical_claims.py`.

The audit is intentionally mechanical. It does not decide theological meaning; it separates calculations from claims in the transferred text. Numerical inputs come from `data/corpus_registry.csv`; inherited forms and claims are frozen separately in `data/inherited_claims_registry.csv` for provenance comparison.

## Outputs

- `data/master_results.csv` - all source-admitted entries and computed values.
- `data/audit_flags.csv` - rows with review flags.
- `data/inherited_claims_registry.csv` - the frozen pre-correction forms and claims.

## Summary

- Source-admitted calculated entries: {len(rows)}
- Inherited audit objects: 43
- Excluded objects with no admitted numerical form: {43 - len(rows)}
- Entries with review flags: {len(flagged)}
- Entries with direct claim/computation mismatches: {len(mismatches)}
- Entries touching a computed 8-collapse domain: {len(strict_8)}
- Entries touching a computed 12-collapse domain: {len(strict_12)}

The derivation section preserves all 43 inherited objects. Three constructed or false-match rows have no admitted analysis form and therefore receive a source-critical disposition rather than a numerical derivation.

Base-12 comparisons use the basis recorded in the frozen inherited-claims table. Formula and expansion labels are retained as special objects and are not counted as literal divine names.

## Important Clarifications

### Scroll Construction

For the notation-level base-12 digit collapse:

`6556_12 -> 6 + 5 + 5 + 6 = 22 -> 2 + 2 = {scroll_base12_collapse}`

So the base-12 notation does not collapse to 12; it collapses to 4 after passing through 22.

However, the decimal value of `6556_12` is `{scroll_decimal}`, and its decimal digit-collapse is:

`{scroll_decimal} -> 1 + 1 + 1 + 5 + 4 = {scroll_decimal_collapse}`

This means the construction may carry both signatures:

- base-12 palindrome and notation-collapse to 4 through 22
- decimal-value collapse to 12 after conversion from base-12

That should be handled explicitly in the paper rather than collapsed into a single claim.

### Shekhinah

For `שכינה`, the computed standard value is `{shekhinah}` and its collapse is `{collapse_decimal(shekhinah)}`.

For the possible variant `השכינה` (`HaShekhinah`), the computed standard value is `{hashekhinah}` and its collapse is `{collapse_decimal(hashekhinah)}`.

So the current spelling does not strictly collapse to 12, but the `HaShekhinah` form does produce a 12-collapse. This is a strong candidate for reconstructing the intended reasoning.

## Preliminary Observations

These are not final edits, but they are the most useful leads from the mechanical audit:

- The inherited `Adonai` claim applies Mispar Gadol to `נ`, but in `אדני` the nun is not final because the word ends with `י`.
- The inherited `El Elyon` claim double-counts `El`: the component line gives `עליון = 197`, which is actually the total for `אל עליון`; the displayed total then adds `אל = 31` again.
- The inherited `HaKadosh Baruch Hu` claim undercounts the standard value by 5; the admitted heading computes to 655, not 650.
- The inherited `El De'ot` claim applies a final-tsadi rule, but the heading `דעות` ends with tav (`ת`), not final tsadi (`ץ`).
- Source corrections to the `El Ha...` and `Elohei...` titles now flow directly into every generated table and derivation.
- `The 42-Letter Name` and `The 72Letter Name` are marked as special because the heading is a label, not necessarily the full formula being valued.

## Flag Types

- `standard-claim-mismatch` - inherited standard gematria differs from the admitted-form computation.
- `mispar-gadol-claim-mismatch` - inherited Mispar Gadol differs from the admitted-form computation.
- `base12-claim-mismatch` - the inherited base-12 form differs from the admitted-form conversion on its recorded basis.
- `claimed-12-collapse-without-computed-12` - cluster text says 12-collapse but no computed layer hits 12.
- `claimed-8-collapse-without-computed-8` - cluster text says 8-collapse but no computed layer hits 8.
- `formula-not-in-heading` / `canonical-constant-not-heading` / `expansion-label-not-name` - the heading is a special label, not an ordinary literal divine name.

## Rows Needing Review

{markdown_table(flagged)}

## Full Mechanical Table

Collapse column order is `standard / Mispar Gadol / base-12 used for the claim`.

{markdown_table(rows)}
"""
    (DOCS_DIR / "AUDIT_FINDINGS.md").write_text(content, encoding="utf-8")


def main() -> None:
    rows = make_rows()
    write_csv(rows)
    write_flags_csv(rows)
    write_findings(rows)
    print(f"wrote {DATA_DIR / 'master_results.csv'}")
    print(f"wrote {DATA_DIR / 'audit_flags.csv'}")
    print(f"wrote {DOCS_DIR / 'AUDIT_FINDINGS.md'}")


if __name__ == "__main__":
    main()
