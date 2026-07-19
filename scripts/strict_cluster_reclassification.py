from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import make_rows


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
TAXONOMY = ROOT / "tex" / "sections" / "05_structural_taxonomy.tex"

MAJOR_CONSTANTS = {
    42: "42",
    72: "72",
    314: "pi/Shaddai",
    345: "345",
    655: "Tanakh chapter prefix",
}
BASE12_SIGNATURES = {
    "22": "YHWH/base-12 alphabet signature",
}


@dataclass
class StrictRow:
    index: int
    name: str
    hebrew: str
    scope: str
    standard: int
    mispar_gadol: int
    base12_standard: str
    base12_mispar_gadol: str
    strict_8_layers: str
    strict_12_layers: str
    strict_base10_palindrome_layers: str
    strict_base12_palindrome_layers: str
    strict_constants: str
    strict_domains: str
    paper_claims: str
    claimed_cluster: str
    comparison_flags: str
    review_action: str


def yes(value: str) -> bool:
    return value == "yes"


def layer_join(values: list[str]) -> str:
    return "; ".join(values)


def strict_8_layers(row) -> list[str]:
    layers: list[str] = []
    if row.collapse_standard == 8:
        layers.append("standard-collapse-8")
    if row.collapse_mispar_gadol == 8:
        layers.append("mispar-gadol-collapse-8")
    if row.collapse_base12_standard == 8:
        layers.append("base12-standard-collapse-8")
    if row.collapse_base12_mispar_gadol == 8:
        layers.append("base12-mispar-gadol-collapse-8")
    return layers


def strict_12_layers(row) -> list[str]:
    layers: list[str] = []
    if row.collapse_standard == 12:
        layers.append("standard-collapse-12")
    if row.collapse_mispar_gadol == 12:
        layers.append("mispar-gadol-collapse-12")
    if row.collapse_base12_standard == 12:
        layers.append("base12-standard-collapse-12")
    if row.collapse_base12_mispar_gadol == 12:
        layers.append("base12-mispar-gadol-collapse-12")
    return layers


def strict_base10_palindrome_layers(row) -> list[str]:
    layers: list[str] = []
    if yes(row.standard_base10_palindrome):
        layers.append("standard-base10-palindrome")
    if yes(row.mispar_base10_palindrome):
        layers.append("mispar-gadol-base10-palindrome")
    return layers


def strict_base12_palindrome_layers(row) -> list[str]:
    layers: list[str] = []
    if yes(row.standard_base12_palindrome):
        layers.append(f"standard-base12-palindrome:{row.base12_standard}")
    if yes(row.mispar_base12_palindrome):
        layers.append(f"mispar-gadol-base12-palindrome:{row.base12_mispar_gadol}")
    return layers


def strict_constants(row) -> list[str]:
    layers: list[str] = []
    for label, value in [("standard", row.computed_standard), ("mispar-gadol", row.computed_mispar_gadol)]:
        if value in MAJOR_CONSTANTS:
            layers.append(f"{label}-constant-{value}:{MAJOR_CONSTANTS[value]}")
    for label, value in [("standard", row.base12_standard), ("mispar-gadol", row.base12_mispar_gadol)]:
        if value in BASE12_SIGNATURES:
            layers.append(f"{label}-base12-signature-{value}:{BASE12_SIGNATURES[value]}")
    return layers


def paper_claims(row) -> list[str]:
    text = row.claimed_cluster.lower()
    claims: list[str] = []
    if "8-collapse" in text or "8cluster" in text or "8-cluster" in text:
        claims.append("paper-8")
    if "12-collapse" in text or "12cluster" in text or "12-cluster" in text:
        claims.append("paper-12")
    if "base10 palindrome" in text or "base-10 palindrome" in text:
        claims.append("paper-base10-palindrome")
    if "base12 palindrome" in text or "base-12 palindrome" in text:
        claims.append("paper-base12-palindrome")
    if "constant" in text or "basemultiple" in text or "base-multiple" in text:
        claims.append("paper-constant-or-basemultiple")
    if "thematic" in text or "canonically assigned" in text:
        claims.append("paper-thematic-domain")
    if "neutral" in text:
        claims.append("paper-neutral")
    return claims


def strict_domains(
    eights: list[str],
    twelves: list[str],
    base10: list[str],
    base12: list[str],
    constants: list[str],
) -> list[str]:
    domains: list[str] = []
    if eights:
        domains.append("strict-8")
    if twelves:
        domains.append("strict-12")
    if base10:
        domains.append("base10-palindrome")
    if base12:
        domains.append("base12-palindrome")
    if constants:
        domains.append("major-constant")
    return domains


def comparison_flags(
    row,
    eights: list[str],
    twelves: list[str],
    base10: list[str],
    base12: list[str],
    constants: list[str],
    paper: list[str],
    domains: list[str],
) -> list[str]:
    flags: list[str] = []
    if "paper-8" in paper and not eights:
        flags.append("paper-claims-8-without-strict-8")
    if eights and "paper-8" not in paper:
        flags.append("strict-8-not-claimed")
    if "paper-12" in paper and not twelves:
        flags.append("paper-claims-12-without-strict-12")
    if twelves and "paper-12" not in paper:
        flags.append("strict-12-not-claimed")
    if "paper-base10-palindrome" in paper and not base10:
        flags.append("paper-claims-base10-without-strict-base10")
    if base10 and "paper-base10-palindrome" not in paper:
        flags.append("strict-base10-not-claimed")
    if "paper-base12-palindrome" in paper and not base12:
        flags.append("paper-claims-base12-without-strict-base12")
    if base12 and "paper-base12-palindrome" not in paper:
        flags.append("strict-base12-not-claimed")
    if "paper-constant-or-basemultiple" in paper and not constants:
        flags.append("paper-constant/basemultiple-not-major-constant")
    if constants and "paper-constant-or-basemultiple" not in paper:
        flags.append("major-constant-not-claimed")
    if "paper-neutral" in paper and domains:
        flags.append("paper-neutral-but-strict-signature")
    if row.review_flags:
        flags.append("calculation-review")
    if row.scope != "literal-heading":
        flags.append(row.scope)
    return flags


def review_action(row, flags: list[str], domains: list[str]) -> str:
    actions = {
        "Yeshua": "Cross-classify: terminal decimal 8, exact base-12 digit sum 12, and base-12 palindrome; elevate the `282_12` bridge.",
        "Shekhinah": "Relabel current spelling as thematic/domain only, or introduce `HaShekhinah` as a separate exact first-step 12-sum variant.",
        "HaKadosh Baruch Hu": "Fix article/form mix; full form gives 655 standard and 1135 -> 7A7_12 Mispar Gadol.",
        "El HaGadol": "Remove 8-collapse claim unless a different attested form is intentionally selected.",
        "El De’ot": "Do not use final-tsadi logic for the displayed heading; any 12 result requires a different attested form.",
        "Adonai": "Correct Mispar Gadol handling; base-12 palindrome survives as 55_12.",
        "El Elyon": "Correct standard total/double-count issue; strict standard 8-collapse survives.",
        "El Olam": "Treat as cross-layer: Mispar Gadol terminal 8, exact base-12 digit sum 12, and base-10 and base-12 palindrome layers.",
        "Ehyeh Asher Ehyeh": "Add the exact decimal first-step sum 5 + 4 + 3 = 12.",
        "Elohei HaShamayim": "Use the corrected construct spelling: the inherited 313_12 palindrome disappears; the admitted form retains a base-12 12-collapse and a Mispar Gadol decimal palindrome.",
        "El HaAretz": "Treat as cross-cluster: strict 12 plus base-12 8 signatures.",
    }
    if row.name in actions:
        return actions[row.name]
    if "paper-claims-8-without-strict-8" in flags or "paper-claims-12-without-strict-12" in flags:
        return "Correct or relabel the claimed collapse category."
    if "strict-8-not-claimed" in flags or "strict-12-not-claimed" in flags:
        return "Consider cross-classification or explain why this strict layer is excluded."
    if "calculation-review" in flags:
        return "Resolve arithmetic/rule mismatch before final classification."
    if domains:
        return "Strict classification agrees broadly; preserve with clearer layer labels."
    return "Leave neutral unless thematic grounds are explicitly argued."


def make_strict_rows() -> list[StrictRow]:
    rows: list[StrictRow] = []
    for row in make_rows():
        eights = strict_8_layers(row)
        twelves = strict_12_layers(row)
        base10 = strict_base10_palindrome_layers(row)
        base12 = strict_base12_palindrome_layers(row)
        constants = strict_constants(row)
        domains = strict_domains(eights, twelves, base10, base12, constants)
        paper = paper_claims(row)
        flags = comparison_flags(row, eights, twelves, base10, base12, constants, paper, domains)
        rows.append(
            StrictRow(
                index=row.index,
                name=row.name,
                hebrew=row.hebrew,
                scope=row.scope,
                standard=row.computed_standard,
                mispar_gadol=row.computed_mispar_gadol,
                base12_standard=row.base12_standard,
                base12_mispar_gadol=row.base12_mispar_gadol,
                strict_8_layers=layer_join(eights),
                strict_12_layers=layer_join(twelves),
                strict_base10_palindrome_layers=layer_join(base10),
                strict_base12_palindrome_layers=layer_join(base12),
                strict_constants=layer_join(constants),
                strict_domains=layer_join(domains),
                paper_claims=layer_join(paper),
                claimed_cluster=row.claimed_cluster,
                comparison_flags=layer_join(flags),
                review_action=review_action(row, flags, domains),
            )
        )
    return rows


def write_csv(rows: list[StrictRow]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / "strict_clusters.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def clean_item(text: str) -> str:
    text = re.sub(r"\\textsubscript\{12\}", "_12", text)
    text = text.replace(r"\&", "&")
    text = text.strip()
    text = re.split(r"\s*(?:→|=)\s*", text, maxsplit=1)[0].strip()
    aliases = {
        "42-Letter Name": "The 42-Letter Name",
        "72Letter Name": "The 72Letter Name",
    }
    return aliases.get(text, text)


def taxonomy_items_between(source: str, start_marker: str, end_marker: str) -> set[str]:
    start = source.find(start_marker)
    if start < 0:
        return set()
    end = source.find(end_marker, start)
    if end < 0:
        end = len(source)
    block = source[start:end]
    return {clean_item(item) for item in re.findall(r"\\item\s+([^\n]+)", block)}


def taxonomy_members() -> dict[str, set[str]]:
    source = TAXONOMY.read_text(encoding="utf-8")
    return {
        "strict-8": taxonomy_items_between(source, "Members of the 8Cluster", "Structural Characteristics"),
        "strict-12": taxonomy_items_between(source, "Members of the 12Cluster", "Structural Characteristics"),
        "base10-palindrome": taxonomy_items_between(
            source,
            "Members of the Base10 Palindrome Cluster",
            "Structural Characteristics",
        ),
        "base12-palindrome": taxonomy_items_between(
            source,
            "Members of the Base12 Palindrome Cluster",
            "Structural Characteristics",
        ),
        "major-constant": taxonomy_items_between(
            source,
            r"\subsection{The Constant-Resonance Cluster",
            "Structural Characteristics",
        ),
    }


def row_set(rows: list[StrictRow], domain: str) -> set[str]:
    return {row.name for row in rows if domain in row.strict_domains and row.scope == "literal-heading"}


def markdown_table(rows: list[StrictRow], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        values = {
            "Name": row.name,
            "Hebrew": row.hebrew,
            "Std": str(row.standard),
            "MG": str(row.mispar_gadol),
            "B12": f"{row.base12_standard}/{row.base12_mispar_gadol}",
            "Strict Domains": row.strict_domains or "-",
            "Strict 8": row.strict_8_layers or "-",
            "Strict 12": row.strict_12_layers or "-",
            "Palindromes": "; ".join(
                part
                for part in [row.strict_base10_palindrome_layers, row.strict_base12_palindrome_layers]
                if part
            )
            or "-",
            "Paper Claims": row.paper_claims or "-",
            "Flags": row.comparison_flags or "-",
            "Action": row.review_action,
        }
        lines.append("| " + " | ".join(values[column] for column in columns) + " |")
    return "\n".join(lines)


def taxonomy_comparison_table(rows: list[StrictRow]) -> str:
    taxonomy = taxonomy_members()
    domain_labels = {
        "strict-8": "8-collapse",
        "strict-12": "12-collapse",
        "base10-palindrome": "Base-10 palindrome",
        "base12-palindrome": "Base-12 palindrome",
        "major-constant": "Major constant",
    }
    all_row_names = {row.name for row in rows}
    lines = [
        "| Domain | Strict Literal Rows | Listed In Taxonomy | Missing From Taxonomy | Extra/Special In Taxonomy |",
        "| --- | --- | --- | --- | --- |",
    ]
    for domain, label in domain_labels.items():
        strict = row_set(rows, domain)
        listed = taxonomy.get(domain, set())
        listed_in_rows = {name for name in listed if name in all_row_names}
        extra = listed - all_row_names
        missing = strict - listed
        extra_or_special = extra | (listed_in_rows - strict)
        lines.append(
            "| "
            + " | ".join(
                [
                    label,
                    str(len(strict)),
                    str(len(listed)),
                    ", ".join(sorted(missing)) or "-",
                    ", ".join(sorted(extra_or_special)) or "-",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def write_report(rows: list[StrictRow]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    literal = [row for row in rows if row.scope == "literal-heading"]
    strict_8 = [row for row in literal if row.strict_8_layers]
    strict_12 = [row for row in literal if row.strict_12_layers]
    base10 = [row for row in literal if row.strict_base10_palindrome_layers]
    base12 = [row for row in literal if row.strict_base12_palindrome_layers]
    constants = [row for row in literal if row.strict_constants]
    no_strict = [row for row in literal if not row.strict_domains]
    high_priority = [
        row
        for row in rows
        if any(
            flag in row.comparison_flags
            for flag in [
                "paper-claims-8-without-strict-8",
                "paper-claims-12-without-strict-12",
                "paper-neutral-but-strict-signature",
                "calculation-review",
                "strict-12-not-claimed",
            ]
        )
        or row.name in {"Yeshua", "Shekhinah", "HaKadosh Baruch Hu"}
    ]

    content = f"""# Strict Cluster Reclassification

This report was generated by `scripts/strict_cluster_reclassification.py`.

The purpose is to separate strict computed categories from thematic or interpretive assignments. A strict row is not automatically more theologically important; it is simply easier to defend mathematically.

## Outputs

- `data/strict_clusters.csv` - one row per derivation entry with strict layers and comparison flags.

## Category Rules

- `strict-8`: any standard, Mispar Gadol, base-12-standard, or base-12-Mispar layer digit-collapses to 8.
- `strict-12`: any standard, Mispar Gadol, base-12-standard, or base-12-Mispar layer digit-collapses to 12.
- `base10-palindrome`: standard or Mispar Gadol value is a base-10 palindrome.
- `base12-palindrome`: standard or Mispar Gadol base-12 representation is a palindrome.
- `major-constant`: strict hit on the paper's main constants/signatures: 42, 72, 314, 345, 655, or `22_12`.

## Summary

- Total derivation entries: {len(rows)}
- Literal-heading rows: {len(literal)}
- Special label/formula rows: {len(rows) - len(literal)}
- Literal rows with strict 8 layer: {len(strict_8)}
- Literal rows with strict 12 layer: {len(strict_12)}
- Literal rows with base-10 palindrome layer: {len(base10)}
- Literal rows with base-12 palindrome layer: {len(base12)}
- Literal rows with major constant/signature layer: {len(constants)}
- Literal rows with no strict marker under these rules: {len(no_strict)}

## Main Findings

### The Taxonomy Survives, But It Needs Layer Labels

The broad architecture is still there. The problem is that the current prose often uses one cluster label where the math shows multiple layers. The cleanup should stop treating `8-collapse`, `12-collapse`, `base-12 palindrome`, `constant`, and `thematic domain` as interchangeable.

### Yeshua Should Become A Cross-Cluster Centerpiece

`Yeshua / ישוע` is not merely a 12-cluster example. Strictly, it has:

- standard and Mispar Gadol decimal collapse to 8
- base-12 notation collapse to 12
- base-12 palindrome `282_12`

That makes it one of the cleanest bridges in the whole corpus: agency/value 8 inside the `2 ... 2` YHWH-frame structure.

### Shekhinah Must Be Reframed

The current spelling `שכינה` has no strict 8, strict 12, base-10 palindrome, base-12 palindrome, or major constant marker under this audit. It can still belong to the presence/completion domain thematically, but it should not be called a strict 12-collapse unless the paper intentionally introduces `HaShekhinah / השכינה` as a separate form.

### Some Strong Rows Are Under-Classified

`Ehyeh Asher Ehyeh`, `El Olam`, and `El HaNe'eman` have strict 12 layers but are not listed in the current 12-collapse taxonomy. `Yeshua` and `Elohei HaShamayim` have strict base-12 palindrome layers but are not listed in the current base-12 palindrome taxonomy.

### Some Current Members Need Correction Or Special Labels

`El HaGadol` is currently claimed as 8-collapse but has no strict 8 layer from the displayed heading. `Ana B'Koach` and the `22-scroll constant` appear in the taxonomy but are not current derivation rows, so they need either their own derivation rows or a separate "macro/special object" table.

## Taxonomy Section Comparison

{taxonomy_comparison_table(rows)}

## High-Priority Review Rows

{markdown_table(high_priority, ["Name", "Hebrew", "Std", "MG", "B12", "Strict Domains", "Paper Claims", "Flags", "Action"])}

## Strict 8 Rows

{markdown_table(strict_8, ["Name", "Hebrew", "Strict 8", "Paper Claims", "Action"])}

## Strict 12 Rows

{markdown_table(strict_12, ["Name", "Hebrew", "Strict 12", "Paper Claims", "Action"])}

## Base-12 Palindrome Rows

{markdown_table(base12, ["Name", "Hebrew", "B12", "Palindromes", "Paper Claims", "Action"])}

## Rows With No Strict Marker

These may still be meaningful, but their paper role should be thematic, neutral, source-critical, or reserved for a different form.

{markdown_table(no_strict, ["Name", "Hebrew", "Std", "MG", "B12", "Paper Claims", "Action"])}

## Recommended Rewrite Rule

Every derivation should separate three statements:

1. strict computed layers;
2. cross-cluster/thematic interpretation;
3. whether the chosen Hebrew form is primary, variant, abbreviation, formula label, or constructed reference object.

That will let the paper preserve its strongest insights without forcing every meaningful association to masquerade as a digit-collapse claim.
"""
    (DOCS_DIR / "STRICT_CLUSTER_RECLASSIFICATION.md").write_text(content, encoding="utf-8")


def main() -> None:
    rows = make_strict_rows()
    write_csv(rows)
    write_report(rows)
    print(f"wrote {DATA_DIR / 'strict_clusters.csv'}")
    print(f"wrote {DOCS_DIR / 'STRICT_CLUSTER_RECLASSIFICATION.md'}")


if __name__ == "__main__":
    main()
