from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "master_results_table.csv"
REGISTRY = ROOT / "data" / "corpus_registry.csv"
OUT = ROOT / "tex" / "sections" / "04_full_derivations.tex"


STATUS_NOTES = {
    "stable-computed": "This row is usable as a stable computed result under the current audit.",
    "classification-review": (
        "The arithmetic is usable, but the row should be classified by multiple layers rather "
        "than by a single cluster label."
    ),
    "calculation-review": (
        "The corrected arithmetic is shown here. Any earlier prose that conflicts with this "
        "derivation should be revised before the row is used as final evidence."
    ),
    "neutral-or-thematic": (
        "No strict 8, strict 12, palindrome, or canonical signature layer appears under the "
        "current rules. Interpretive use should therefore be thematic or comparative."
    ),
    "special-object-review": (
        "This is a formula or constructed object rather than an ordinary literal-heading row. It "
        "should be handled separately from the main name count."
    ),
}


def read_rows() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_registry() -> list[dict[str, str]]:
    with REGISTRY.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def b12(value: str) -> str:
    return value.removesuffix("_12")


def humanize(text: str) -> str:
    replacements = [
        (r"base12-mispar-gadol-collapse-(\d+)", r"Mispar Gadol base-12 notation-collapse to \1"),
        (r"base12-standard-collapse-(\d+)", r"standard base-12 notation-collapse to \1"),
        (r"mispar-gadol-collapse-(\d+)", r"Mispar Gadol decimal collapse to \1"),
        (r"standard-collapse-(\d+)", r"standard decimal collapse to \1"),
        (r"mispar-gadol-base10-palindrome", "Mispar Gadol base-10 palindrome"),
        (r"standard-base10-palindrome", "standard base-10 palindrome"),
        (r"mispar-gadol-base12-palindrome:([0-9AB]+)", r"Mispar Gadol base-12 palindrome \1_12"),
        (r"standard-base12-palindrome:([0-9AB]+)", r"standard base-12 palindrome \1_12"),
        (
            r"mispar-gadol-base12-signature-([0-9AB]+):([^;]+)",
            r"Mispar Gadol base-12 signature \1_12 (\2)",
        ),
        (
            r"standard-base12-signature-([0-9AB]+):([^;]+)",
            r"standard base-12 signature \1_12 (\2)",
        ),
        (r"mispar-gadol-constant-([0-9]+):([^;]+)", r"Mispar Gadol reference value \1 (\2)"),
        (r"standard-constant-([0-9]+):([^;]+)", r"standard reference value \1 (\2)"),
        (r"base12-mispar-gadol=", "Mispar Gadol base-12 = "),
        (r"base12-standard=", "standard base-12 = "),
        (r"mispar-gadol-base12=", "Mispar Gadol base-12 = "),
        (r"standard-base12=", "standard base-12 = "),
        (r"mispar-gadol=", "Mispar Gadol = "),
        (r"standard=", "standard = "),
        (r"base12-notation-fibonacci-string", "base-12 notation Fibonacci string"),
        (r"base12-string", "base-12 string"),
        (r"decimal-constant-encoding", "decimal digit-string encoding"),
        (r"canonical-constant-not-heading", "canonical-reference-not-heading"),
        (r"macro-constant/canonical structure", "formula/canonical reference structure"),
        (r"paper-constant/basemultiple-not-major-constant", "paper reference/basemultiple, not a mathematical constant"),
        (r"pythagorean-digit-encoding", "Pythagorean digit encoding"),
        (r"star-number-multiple", "star-number multiple"),
        (r"\btriangular\b", "triangular number"),
        (r"\bmersenne\b", "Mersenne form"),
        (r"->", "to"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text


def tex_escape(text: str) -> str:
    if not text:
        return ""
    text = humanize(text)
    text = text.replace("`", "")
    subscript_placeholders: list[str] = []

    def subscript_repl(match: re.Match[str]) -> str:
        subscript_placeholders.append(f"{match.group(1)}\\textsubscript{{{match.group(2)}}}")
        return f"@@SUBSCRIPT{len(subscript_placeholders) - 1}@@"

    text = re.sub(r"\b([0-9AB]+)_(10|12)\b", subscript_repl, text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    for index, value in enumerate(subscript_placeholders):
        text = text.replace(f"@@SUBSCRIPT{index}@@", value)
    return text


def tex_list(items: list[str]) -> str:
    if not items:
        return "None."
    lines = ["\\begin{itemize}"]
    for item in items:
        lines.append(f"\\item {tex_escape(item)}")
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def split_layers(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def collapse_items(row: dict[str, str]) -> list[str]:
    return [
        f"standard decimal collapse: {row['standard_gematria']} -> {row['decimal_collapse_standard']}",
        f"Mispar Gadol decimal collapse: {row['mispar_gadol']} -> {row['decimal_collapse_mispar_gadol']}",
        (
            f"standard base-12 notation-collapse: {row['base12_standard']} -> "
            f"{row['base12_collapse_standard']}"
        ),
        (
            f"Mispar Gadol base-12 notation-collapse: {row['base12_mispar_gadol']} -> "
            f"{row['base12_collapse_mispar_gadol']}"
        ),
    ]


def cluster_items(row: dict[str, str]) -> list[str]:
    items: list[str] = []
    if row["strict_8_layers"]:
        items.append(f"8-collapse layer: {row['strict_8_layers']}")
    if row["strict_12_layers"]:
        items.append(f"threshold-12 terminal layer: {row['strict_12_layers']}")
    if row["base10_palindrome_layers"]:
        items.append(f"Base10 palindrome layer: {row['base10_palindrome_layers']}")
    if row["base12_palindrome_layers"]:
        items.append(f"Base12 palindrome layer: {row['base12_palindrome_layers']}")
    if row["canonical_or_structural_signatures"]:
        items.append(f"Reference/signature layer: {row['canonical_or_structural_signatures']}")
    if not items:
        items.append("No strict numerical layer under current rules.")
    items.append(f"Review status: {row['review_status']}")
    return items


def optional_paragraph(title: str, value: str) -> str:
    if not value:
        return ""
    items = split_layers(value)
    body = tex_list(items) if len(items) > 1 else tex_escape(value)
    return f"\\paragraph{{{title}}}\n{body}\n"


def row_section(row: dict[str, str]) -> str:
    name = tex_escape(row["name"])
    hebrew = row["hebrew"]
    status_note = STATUS_NOTES.get(row["review_status"], "")
    parts = [
        f"\\subsection{{{name} ({hebrew})}}",
        "\\paragraph{Row Status}",
        tex_list(
            [
                f"form status: {row['form_status']}",
                f"corpus layer: {row['corpus_layer']}",
                f"object class: {row['object_class']}",
                f"attestation: {row['attestation_status']}",
                f"scope: {row['scope']}",
                f"review status: {row['review_status']}",
                f"working thematic domain: {row['thematic_or_structural_domain']}",
            ]
        ),
    ]

    parts.extend(
        [
            "\\paragraph{Source and Form Provenance}",
            f"Admitted form: {hebrew}.",
            f"Representative source: {tex_escape(row['representative_source'])}.",
        ]
    )
    if row["source_url"]:
        parts.append(f"\\url{{{row['source_url']}}}")
    if row["inherited_hebrew"] != row["hebrew"]:
        parts.append(
            "Inherited display: "
            f"{row['inherited_hebrew']}. The calculation below uses the admitted form above."
        )

    parts.extend(
        [
            "\\paragraph{Standard Gematria}",
            f"Total = {row['standard_gematria']}",
            f"Digit-collapse: {row['standard_gematria']} -> {row['decimal_collapse_standard']}",
            "\\paragraph{Mispar Gadol}",
        ]
    )

    if row["standard_gematria"] == row["mispar_gadol"]:
        parts.extend(
            [
                "No final-letter expansion changes the displayed form.",
                "",
                f"Total remains {row['mispar_gadol']}",
                "",
            ]
        )
    else:
        parts.extend(
            [
                "Final-letter expansion is applied only to displayed final forms.",
                "",
                f"Total becomes {row['mispar_gadol']}",
                "",
            ]
        )

    parts.extend(
        [
            f"Digit-collapse: {row['mispar_gadol']} -> {row['decimal_collapse_mispar_gadol']}",
            "\\paragraph{Base12 Conversion}",
            (
                f"Mispar Gadol total: {row['mispar_gadol']} -> "
                f"{b12(row['base12_mispar_gadol'])}\\textsubscript{{12}}"
            ),
            (
                f"Standard total: {row['standard_gematria']} -> "
                f"{b12(row['base12_standard'])}\\textsubscript{{12}}"
            ),
            "\\paragraph{Digit-Collapse Summary}",
            tex_list(collapse_items(row)),
            "\\paragraph{Palindromes}",
            tex_list(
                [
                    *(["base-10: " + row["base10_palindrome_layers"]] if row["base10_palindrome_layers"] else []),
                    *(["base-12: " + row["base12_palindrome_layers"]] if row["base12_palindrome_layers"] else []),
                ]
            ),
            "\\paragraph{Reference and Signature Resonance}",
            tex_list(
                [
                    *(split_layers(row["canonical_or_structural_signatures"])),
                    *(split_layers(row["notable_constant_hits"])),
                ]
            ),
        ]
    )

    ordinary = optional_paragraph("Exploratory Mathematical Notes", row["ordinary_math_hits"])
    if ordinary:
        parts.append(ordinary.rstrip())
    shared = optional_paragraph("Shared-Value Links", row["shared_value_links"])
    if shared:
        parts.append(shared.rstrip())

    parts.extend(
        [
            "\\paragraph{Cluster Assignment}",
            tex_list(cluster_items(row)),
            "\\paragraph{Structural Interpretation}",
            tex_escape(status_note),
            "",
            tex_list(split_layers(row["revision_note"])) if row["revision_note"] else "",
        ]
    )
    return "\n".join(parts)


def excluded_section(row: dict[str, str]) -> str:
    name = tex_escape(row["name"])
    inherited = row["displayed_hebrew"]
    source = tex_escape(row["representative_source"])
    parts = [
        f"\\subsection{{{name} ({inherited})}}",
        "\\paragraph{Row Status}",
        tex_list(
            [
                f"corpus layer: {row['corpus_layer']}",
                f"object class: {row['object_class']}",
                f"attestation: {row['attestation_status']}",
                f"recommended action: {row['recommended_action']}",
            ]
        ),
        "\\paragraph{Source-Critical Disposition}",
        (
            "The source registry admits no Hebrew form for numerical analysis. "
            "The inherited display is retained here only as provenance, and no gematria, "
            "collapse, palindrome, or signature result is assigned to it."
        ),
    ]
    if source:
        parts.append(f"Representative review source: {source}.")
    if row["source_url"]:
        parts.append(f"\\url{{{row['source_url']}}}")
    return "\n".join(parts)


def build_section(rows: list[dict[str, str]], registry: list[dict[str, str]]) -> str:
    intro = r"""\section{Inherited Derivations and Source Audit}

This section preserves the inherited 43-object audit boundary while taking every numerical input from the source registry's admitted Hebrew form. The frozen inherited-claims table is used only for provenance comparisons. Standard gematria, Mispar Gadol, base-12 conversion, truncated digit sums, palindrome behavior, reference-value resonances, and thematic interpretation are kept distinct.

An inherited row for which the registry admits no analyzable form remains visible as an exclusion but receives no calculation. Rows marked as calculation-review or special-object-review remain because they belong to the inherited corpus, but their interpretive claims should be finalized only after the relevant form or formula question is resolved.
"""
    rows_by_index = {int(row["index"]): row for row in rows}
    sections: list[str] = []
    for registry_row in registry:
        index = int(registry_row["index"])
        if index in rows_by_index:
            sections.append(row_section(rows_by_index[index]))
        else:
            sections.append(excluded_section(registry_row))
    return intro + "\n\n" + "\n\n".join(sections) + "\n"


def main() -> None:
    rows = read_rows()
    registry = read_registry()
    OUT.write_text(build_section(rows, registry), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
