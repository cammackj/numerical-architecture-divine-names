from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import make_rows
from exploratory_pattern_mining import corpus_constant_hits, shared_values
from mathematical_constant_audit import corpus_hits as ordinary_math_hits
from strict_cluster_reclassification import make_strict_rows


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"


THEMATIC_DOMAIN_HINTS = {
    "El": "identity/root name",
    "Eloah": "identity/root name",
    "Elohim": "identity/creation",
    "YHWH": "identity/covenant",
    "Adonai": "lordship/kingship",
    "Shaddai": "power/provision",
    "Ehyeh Asher Ehyeh": "self-existence/formula",
    "El Elyon": "transcendence/kingship",
    "El Olam": "eternity/stability",
    "El Roi": "seeing/providence",
    "El Gibbor": "might/agency",
    "El Yeshuati": "salvation",
    "Shekhinah": "presence/indwelling",
    "HaMakom": "presence/place",
    "HaRachaman": "mercy",
    "HaKadosh Baruch Hu": "holiness/blessing",
    "Ribbono Shel Olam": "sovereignty/cosmos",
    "Yeshua": "salvation/agency bridge",
    "Immanuel": "presence/incarnation",
    "Mashiach": "messianic agency",
    "Sar Shalom": "peace/rule",
    "Adon": "lordship/root title",
    "Elohei HaShamayim": "heaven/cosmic order",
    "Elohei HaAretz": "earth/cosmic order",
    "El Shaddai": "power/provision",
    "El Kana": "jealousy/covenant",
    "El De’ot": "knowledge/wisdom",
    "El Berit": "covenant",
    "El HaNe’eman": "faithfulness/stability",
    "El HaGadol": "greatness",
    "El HaNorah": "awe/judgment",
    "El HaKavod": "glory",
    "El HaShamayim": "heaven/cosmic order",
    "El HaAretz": "earth/cosmic order",
    "Elohei Avraham": "patriarchal covenant",
    "Elohei Yitzchak": "patriarchal covenant",
    "Elohei Yaakov": "patriarchal covenant",
    "The 42-Letter Name": "formula/canonical structure",
    "The 72Letter Name": "formula/canonical reference structure",
    "AB": "Name expansion",
    "SAG": "Name expansion",
    "MAH": "Name expansion",
    "BEN": "Name expansion",
}


@dataclass
class MasterRow:
    index: int
    name: str
    hebrew: str
    inherited_hebrew: str
    form_status: str
    corpus_layer: str
    object_class: str
    attestation_status: str
    representative_source: str
    source_url: str
    source_form: str
    recommended_action: str
    scope: str
    thematic_or_structural_domain: str
    standard_gematria: int
    claimed_standard: str
    standard_match: str
    mispar_gadol: int
    claimed_mispar_gadol: str
    mispar_gadol_match: str
    base12_standard: str
    base12_mispar_gadol: str
    claimed_base12: str
    base12_claim_basis: str
    base12_match: str
    decimal_collapse_standard: int
    decimal_collapse_mispar_gadol: int
    base12_collapse_standard: int
    base12_collapse_mispar_gadol: int
    base10_palindrome_layers: str
    base12_palindrome_layers: str
    strict_8_layers: str
    strict_12_layers: str
    strict_layers: str
    canonical_or_structural_signatures: str
    notable_constant_hits: str
    ordinary_math_hits: str
    shared_value_links: str
    current_paper_cluster: str
    audit_flags: str
    taxonomy_flags: str
    review_status: str
    revision_note: str


def clean_join(values: list[str]) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        value = value.strip()
        if value and value not in seen:
            out.append(value)
            seen.add(value)
    return "; ".join(out)


def palindrome_layers(row) -> tuple[str, str]:
    base10: list[str] = []
    base12: list[str] = []
    if row.standard_base10_palindrome == "yes":
        base10.append(f"standard={row.computed_standard}")
    if row.mispar_base10_palindrome == "yes":
        base10.append(f"mispar-gadol={row.computed_mispar_gadol}")
    if row.standard_base12_palindrome == "yes":
        base12.append(f"standard={row.base12_standard}_12")
    if row.mispar_base12_palindrome == "yes":
        base12.append(f"mispar-gadol={row.base12_mispar_gadol}_12")
    return clean_join(base10), clean_join(base12)


def form_status(corpus_layer: str, recommended_action: str) -> str:
    if recommended_action.startswith("correct"):
        return "source-corrected"
    return corpus_layer


def make_hit_summary(hits: list[object], exact_only: bool = False) -> dict[str, str]:
    grouped: dict[str, list[str]] = {}
    for hit in hits:
        hit_type = getattr(hit, "hit_type", "")
        if exact_only and hit_type == "multiple":
            continue
        basis = getattr(hit, "basis")
        value = getattr(hit, "value")
        note = getattr(hit, "note", "")
        category = getattr(hit, "category", hit_type)
        structure = getattr(hit, "structure", note)
        summary = f"{basis}={value} ({category}: {structure})"
        grouped.setdefault(getattr(hit, "name"), []).append(summary)
    return {name: clean_join(items) for name, items in grouped.items()}


def make_shared_links() -> dict[str, str]:
    links: dict[str, list[str]] = {}
    for item in shared_values():
        if not item.note:
            continue
        names = [name.strip() for name in item.names.split(";")]
        for name in names:
            others = [other for other in names if other != name]
            if others:
                if item.basis.startswith("base12"):
                    value_text = f"{item.base12}_12 ({item.value}_10)"
                else:
                    value_text = str(item.value)
                links.setdefault(name, []).append(
                    f"{item.basis}={value_text} with {', '.join(others)} ({item.note})"
                )
    return {name: clean_join(items) for name, items in links.items()}


def canonical_base12_hits(row) -> list[str]:
    hits: list[str] = []
    base12_signatures = {
        "72": "canonical seventy-two signature",
        "282": "Yeshua bridge string",
        "393": "Ehyeh Asher Ehyeh formula palindrome",
        "515": "El Olam Mispar Gadol palindrome",
        "7A7": "HaKadosh Baruch Hu Mispar Gadol palindrome",
        "313": "Elohei HaShamayim standard palindrome",
        "44": "BEN standard palindrome",
    }
    for basis, value in [
        ("standard-base12", row.base12_standard),
        ("mispar-gadol-base12", row.base12_mispar_gadol),
    ]:
        if value in base12_signatures:
            hits.append(f"{basis}={value}_12 ({base12_signatures[value]})")
    return hits


def review_status(row, strict_row) -> str:
    audit_flags = row.review_flags
    taxonomy_flags = strict_row.comparison_flags
    if row.scope != "literal-heading":
        return "special-object-review"
    if "mismatch" in audit_flags or "calculation-review" in taxonomy_flags:
        return "calculation-review"
    if "paper-claims" in taxonomy_flags or "not-claimed" in taxonomy_flags:
        return "classification-review"
    if not strict_row.strict_domains:
        return "neutral-or-thematic"
    return "stable-computed"


def revision_note(row, strict_row, shared_links: str) -> str:
    notes = [strict_row.review_action]
    special_notes = {
        "Elohim": "Add hidden standard/base-12 result: 86_10 = 72_12.",
        "Yeshua": "Treat 282_12 as a major bridge: 8 inside a 2...2 frame, with the exact digit sum 2 + 8 + 2 = 12.",
        "Shekhinah": "Current form is 385 -> 7; keep 12-domain only as thematic unless HaShekhinah is added as a separate exact 12-sum variant.",
        "HaKadosh Baruch Hu": "Resolve full-form vs no-article form before final prose.",
        "Sar Shalom": "Possible 12 * 73 star-number multiple remains exploratory.",
        "El De’ot": "Current displayed form is 511; final-tsadi logic does not apply to the ending tav.",
    }
    if row.name in special_notes:
        notes.append(special_notes[row.name])
    if shared_links:
        notes.append(f"Shared link: {shared_links}")
    return clean_join(notes)


def make_master_rows() -> list[MasterRow]:
    rows = make_rows()
    strict = {row.index: row for row in make_strict_rows()}
    notable_hits = make_hit_summary(corpus_constant_hits(), exact_only=True)
    math_hits = make_hit_summary(ordinary_math_hits())
    shared_links = make_shared_links()
    master_rows: list[MasterRow] = []

    for row in rows:
        strict_row = strict[row.index]
        base10_pal, base12_pal = palindrome_layers(row)
        canonical_constants = clean_join(
            [strict_row.strict_constants, *canonical_base12_hits(row)]
        )
        strict_layers = clean_join(
            [
                strict_row.strict_8_layers,
                strict_row.strict_12_layers,
                strict_row.strict_base10_palindrome_layers,
                strict_row.strict_base12_palindrome_layers,
                canonical_constants,
            ]
        )
        links = shared_links.get(row.name, "")
        master_rows.append(
            MasterRow(
                index=row.index,
                name=row.name,
                hebrew=row.hebrew,
                inherited_hebrew=row.inherited_hebrew,
                form_status=form_status(row.corpus_layer, row.recommended_action),
                corpus_layer=row.corpus_layer,
                object_class=row.object_class,
                attestation_status=row.attestation_status,
                representative_source=row.representative_source,
                source_url=row.source_url,
                source_form=row.source_form,
                recommended_action=row.recommended_action,
                scope=row.scope,
                thematic_or_structural_domain=THEMATIC_DOMAIN_HINTS.get(row.name, "TBD"),
                standard_gematria=row.computed_standard,
                claimed_standard=row.claimed_standard,
                standard_match=row.standard_match,
                mispar_gadol=row.computed_mispar_gadol,
                claimed_mispar_gadol=row.claimed_mispar_gadol,
                mispar_gadol_match=row.mispar_gadol_match,
                base12_standard=f"{row.base12_standard}_12",
                base12_mispar_gadol=f"{row.base12_mispar_gadol}_12",
                claimed_base12=f"{row.claimed_base12}_12" if row.claimed_base12 else "",
                base12_claim_basis=row.base12_claim_basis,
                base12_match=row.base12_match,
                decimal_collapse_standard=row.collapse_standard,
                decimal_collapse_mispar_gadol=row.collapse_mispar_gadol,
                base12_collapse_standard=row.collapse_base12_standard,
                base12_collapse_mispar_gadol=row.collapse_base12_mispar_gadol,
                base10_palindrome_layers=base10_pal,
                base12_palindrome_layers=base12_pal,
                strict_8_layers=strict_row.strict_8_layers,
                strict_12_layers=strict_row.strict_12_layers,
                strict_layers=strict_layers,
                canonical_or_structural_signatures=canonical_constants,
                notable_constant_hits=notable_hits.get(row.name, ""),
                ordinary_math_hits=math_hits.get(row.name, ""),
                shared_value_links=links,
                current_paper_cluster=row.claimed_cluster,
                audit_flags=row.review_flags,
                taxonomy_flags=strict_row.comparison_flags,
                review_status=review_status(row, strict_row),
                revision_note=revision_note(row, strict_row, links),
            )
        )
    return master_rows


def write_csv(rows: list[MasterRow]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / "master_results_table.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def md_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown_table(rows: list[MasterRow]) -> str:
    headers = [
        "#",
        "Name",
        "Form",
        "Std/MG",
        "B12 Std/MG",
        "Strict Layers",
        "Status",
        "Revision Note",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.index),
                    md_escape(row.name),
                    md_escape(row.form_status),
                    f"{row.standard_gematria}/{row.mispar_gadol}",
                    f"{row.base12_standard}/{row.base12_mispar_gadol}",
                    md_escape(row.strict_layers or "(none)"),
                    md_escape(row.review_status),
                    md_escape(row.revision_note),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def status_counts(rows: list[MasterRow]) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.review_status] = counts.get(row.review_status, 0) + 1
    return "\n".join(f"- `{status}`: {count}" for status, count in sorted(counts.items()))


def write_report(rows: list[MasterRow]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    with (DATA_DIR / "corpus_registry.csv").open(encoding="utf-8-sig", newline="") as handle:
        registry_rows = list(csv.DictReader(handle))
    literal_rows = [row for row in rows if row.scope == "literal-heading"]
    special_rows = [row for row in rows if row.scope != "literal-heading"]
    priority_rows = [
        row
        for row in rows
        if row.review_status
        in {"calculation-review", "classification-review", "special-object-review"}
    ]
    high_value_names = {
        "Elohim",
        "YHWH",
        "Shaddai",
        "Ehyeh Asher Ehyeh",
        "El Olam",
        "Yeshua",
        "El Shaddai",
        "El HaNe’eman",
    }
    high_value_rows = [row for row in rows if row.name in high_value_names]

    content = f"""# Master Results Table

This document was generated by `scripts/build_master_results_table.py`.

It is the manuscript-facing table for the rewrite. The source registry supplies admitted forms, while the frozen inherited-claims registry supplies provenance comparisons only. This merged table adds strict layers, inherited paper claims, review status, notable reference values, ordinary mathematical hits, shared-value links, and revision notes.

## Output

- `data/master_results_table.csv`

## Scope Summary

- Inherited audit objects: {len(registry_rows)}
- Source-admitted calculated entries: {len(rows)}
- Excluded objects without an admitted numerical form: {len(registry_rows) - len(rows)}
- Literal heading rows: {len(literal_rows)}
- Special formula or constructed-reference rows: {len(special_rows)}

## Review Status Counts

{status_counts(rows)}

## How To Use This Table

- Use `standard_gematria`, `mispar_gadol`, and the base-12 columns as the calculation authority during the first rewrite pass.
- Use `review_status` to decide which rows need correction before interpretation.
- Use `strict_layers` for the new taxonomy.
- Use `thematic_or_structural_domain` only as a working domain hint, not as a final claim.
- Keep `ordinary_math_hits` exploratory unless the manuscript explicitly argues why that mathematical structure belongs in the model.

## Priority Rewrite Rows

These rows should be handled before prose polish.

{markdown_table(priority_rows)}

## High-Value Stable Or Bridge Rows

These rows either survive strongly or deserve elevated treatment after the calculation pass.

{markdown_table(high_value_rows)}
"""
    (DOCS_DIR / "MASTER_RESULTS_TABLE.md").write_text(content, encoding="utf-8")


def main() -> None:
    rows = make_master_rows()
    write_csv(rows)
    write_report(rows)
    print(f"wrote {DATA_DIR / 'master_results_table.csv'}")
    print(f"wrote {DOCS_DIR / 'MASTER_RESULTS_TABLE.md'}")


if __name__ == "__main__":
    main()
