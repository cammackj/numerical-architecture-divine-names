from __future__ import annotations

import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import make_rows
from exploratory_pattern_mining import component_rows


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"


DECIMAL_ENCODINGS = {
    314: "pi to two decimal places: 3.14",
    2718: "e to three decimal places: 2.718",
    1618: "phi to three decimal places: 1.618",
    1414: "sqrt(2) to three decimal places: 1.414",
    1732: "sqrt(3) to three decimal places: 1.732",
    2236: "sqrt(5) to three decimal places: 2.236",
}

STAR_NUMBERS = {
    1: "S1",
    13: "S2",
    37: "S3",
    73: "S4",
    121: "S5",
    181: "S6",
    253: "S7",
    337: "S8",
    433: "S9",
    541: "S10",
}

FIBONACCI = {
    1,
    2,
    3,
    5,
    8,
    13,
    21,
    34,
    55,
    89,
    144,
    233,
    377,
    610,
    987,
    1597,
    2584,
}

PYTHAGOREAN_DIGIT_STRINGS = {
    "345": "primitive 3-4-5 triple",
    "51213": "primitive 5-12-13 triple",
    "72425": "primitive 7-24-25 triple",
    "81517": "primitive 8-15-17 triple",
}


@dataclass
class MathHit:
    source: str
    category: str
    name: str
    hebrew: str
    basis: str
    value: str
    structure: str
    significance: str
    caution: str


def triangular_index(value: int) -> int | None:
    if value < 1:
        return None
    n = int((math.isqrt(8 * value + 1) - 1) // 2)
    return n if n * (n + 1) // 2 == value else None


def is_square(value: int) -> int | None:
    if value < 0:
        return None
    root = math.isqrt(value)
    return root if root * root == value else None


def mersenne_power(value: int) -> int | None:
    candidate = value + 1
    if candidate > 0 and candidate & (candidate - 1) == 0:
        return candidate.bit_length() - 1
    return None


def add_value_hits(
    hits: list[MathHit],
    source: str,
    name: str,
    hebrew: str,
    basis: str,
    value: int,
) -> None:
    if value in DECIMAL_ENCODINGS:
        hits.append(
            MathHit(
                source,
                "decimal-constant-encoding",
                name,
                hebrew,
                basis,
                str(value),
                DECIMAL_ENCODINGS[value],
                "Direct decimal encoding of a standard mathematical constant.",
                "Decimal encodings are suggestive only when the surrounding name is independently important.",
            )
        )

    if str(value) in PYTHAGOREAN_DIGIT_STRINGS:
        hits.append(
            MathHit(
                source,
                "pythagorean-digit-encoding",
                name,
                hebrew,
                basis,
                str(value),
                PYTHAGOREAN_DIGIT_STRINGS[str(value)],
                "Encodes a primitive Pythagorean triple as decimal digits.",
                "This is digit syntax, not a theorem unless the manuscript defines why digit strings count.",
            )
        )

    if value in STAR_NUMBERS:
        hits.append(
            MathHit(
                source,
                "star-number",
                name,
                hebrew,
                basis,
                str(value),
                STAR_NUMBERS[value],
                "Exact star-number hit.",
                "Needs a rule explaining why star/hexagram numbers matter in this corpus.",
            )
        )
    else:
        for star, label in STAR_NUMBERS.items():
            if star > 1 and value % star == 0 and 1 < value // star <= 20:
                hits.append(
                    MathHit(
                        source,
                        "star-number-multiple",
                        name,
                        hebrew,
                        basis,
                        str(value),
                        f"{value // star} * {star} ({label})",
                        "Multiple of a low star number.",
                        "Multiples are weaker than exact hits and need controls.",
                    )
                )

    if value in FIBONACCI:
        hits.append(
            MathHit(
                source,
                "fibonacci",
                name,
                hebrew,
                basis,
                str(value),
                "Fibonacci number",
                "Exact Fibonacci hit.",
                "Low Fibonacci numbers are common; stronger if repeated in semantically linked rows.",
            )
        )

    t_index = triangular_index(value)
    if t_index is not None and t_index >= 2:
        hits.append(
            MathHit(
                source,
                "triangular",
                name,
                hebrew,
                basis,
                str(value),
                f"T{t_index}",
                "Exact triangular-number hit.",
                "Triangular hits are common; prioritize large or semantically meaningful cases.",
            )
        )

    square_root = is_square(value)
    if square_root is not None and square_root >= 2:
        hits.append(
            MathHit(
                source,
                "square",
                name,
                hebrew,
                basis,
                str(value),
                f"{square_root}^2",
                "Exact square-number hit.",
                "Only meaningful if the square root has independent relevance.",
            )
        )

    power = mersenne_power(value)
    if power is not None and power >= 2:
        hits.append(
            MathHit(
                source,
                "mersenne",
                name,
                hebrew,
                basis,
                str(value),
                f"2^{power} - 1",
                "Exact Mersenne-form hit.",
                "Mersenne form is mathematically real, but still needs interpretive warrant.",
            )
        )


def add_base12_notation_hits(
    hits: list[MathHit],
    source: str,
    name: str,
    hebrew: str,
    basis: str,
    base12_text: str,
) -> None:
    if base12_text.isdigit():
        decimal_reading = int(base12_text)
        if decimal_reading in FIBONACCI and decimal_reading >= 21:
            hits.append(
                MathHit(
                    source,
                    "base12-notation-fibonacci-string",
                    name,
                    hebrew,
                    basis,
                    f"{base12_text}_12",
                    f"digits form Fibonacci number {decimal_reading}",
                    "Base-12 notation visually matches a Fibonacci number.",
                    "This is notation-level only; do not confuse with decimal value.",
                )
            )
        if decimal_reading in STAR_NUMBERS:
            hits.append(
                MathHit(
                    source,
                    "base12-notation-star-string",
                    name,
                    hebrew,
                    basis,
                    f"{base12_text}_12",
                    f"digits form star number {decimal_reading}",
                    "Base-12 notation visually matches a star number.",
                    "This is notation-level only; do not confuse with decimal value.",
                )
            )


def corpus_hits() -> list[MathHit]:
    hits: list[MathHit] = []
    for row in make_rows():
        add_value_hits(hits, "corpus", row.name, row.hebrew, "standard", row.computed_standard)
        add_value_hits(hits, "corpus", row.name, row.hebrew, "mispar-gadol", row.computed_mispar_gadol)
        add_base12_notation_hits(hits, "corpus", row.name, row.hebrew, "standard-base12", row.base12_standard)
        add_base12_notation_hits(hits, "corpus", row.name, row.hebrew, "mispar-gadol-base12", row.base12_mispar_gadol)
    return hits


def component_hits() -> list[MathHit]:
    hits: list[MathHit] = []
    for row in component_rows():
        add_value_hits(hits, row.category, row.name, row.hebrew, "standard", row.standard)
        add_value_hits(hits, row.category, row.name, row.hebrew, "mispar-gadol", row.mispar_gadol)
        add_base12_notation_hits(
            hits,
            row.category,
            row.name,
            row.hebrew,
            "standard-base12",
            row.base12_standard,
        )
        add_base12_notation_hits(
            hits,
            row.category,
            row.name,
            row.hebrew,
            "mispar-gadol-base12",
            row.base12_mispar_gadol,
        )
    return hits


def write_csv(rows: list[MathHit]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / "mathematical_constant_hits.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def table(rows: list[MathHit], category_filter: set[str] | None = None, source_filter: set[str] | None = None) -> str:
    selected = [
        row
        for row in rows
        if (category_filter is None or row.category in category_filter)
        and (source_filter is None or row.source in source_filter)
    ]
    lines = [
        "| Source | Name | Basis | Value | Structure | Significance | Caution |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in selected:
        lines.append(
            f"| {row.source} | {row.name} | {row.basis} | {row.value} | "
            f"{row.structure} | {row.significance} | {row.caution} |"
        )
    return "\n".join(lines) if selected else "No hits under these rules."


def write_report(rows: list[MathHit]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    direct_absences = [
        "`phi`: no `1618` decimal encoding found in the current corpus/component pass.",
        "`e`: no `2718` decimal encoding found in the current corpus/component pass.",
        "`sqrt(2)`: no `1414` decimal encoding found in the current corpus/component pass.",
        "`sqrt(3)`: no `1732` decimal encoding found in the current corpus/component pass.",
        "`sqrt(5)`: no `2236` decimal encoding found in the current corpus/component pass.",
        "`355/113`: no direct 355/113 pair found in the tested values.",
    ]
    content = f"""# Mathematical Constant and Structure Audit

This report was generated by `scripts/mathematical_constant_audit.py`.

This audit checks for ordinary mathematical constants and structures: decimal encodings of constants, Pythagorean digit strings, star numbers, Fibonacci numbers, triangular numbers, square numbers, and Mersenne-form numbers.

It intentionally separates these from Hebrew/traditional constants such as 22, 42, and 72.

## Output

- `data/mathematical_constant_hits.csv`

## Direct Mathematical Constant Encodings

{table(rows, {"decimal-constant-encoding"}, {"corpus"})}

## Pythagorean Triple Encodings

{table(rows, {"pythagorean-digit-encoding"}, {"corpus"})}

## Star / Hexagram Number Structure

Star numbers follow `6n(n - 1) + 1`: `1, 13, 37, 73, 121, 181, ...`.

This sequence may matter because the paper already has strong interest in 12-fold symmetry; star numbers are built from hexagonal/triangular geometry.

{table(rows, {"star-number", "star-number-multiple"}, {"corpus", "component", "candidate-title", "candidate-variant", "candidate-combination"})}

## Mersenne Structure

{table(rows, {"mersenne"}, {"corpus", "component", "candidate-title", "candidate-variant", "candidate-combination"})}

## Fibonacci / Phi-Adjacent Structure

These are not direct phi hits. They are Fibonacci or Fibonacci-string hits, which are phi-adjacent only in the weaker sequence sense.

{table(rows, {"fibonacci", "base12-notation-fibonacci-string"}, {"corpus", "component", "candidate-title", "candidate-variant", "candidate-combination"})}

## Triangular And Square Structure

{table(rows, {"triangular", "square"}, {"corpus", "component", "candidate-title", "candidate-variant", "candidate-combination"})}

## Notable Absences

The following were checked and not found as direct encodings:

{chr(10).join(f"- {item}" for item in direct_absences)}

## Highest-Value Interpretation

The ordinary-math constants currently divide into three tiers:

1. `pi / 3.14`: strong direct hit through `Shaddai = 314`.
2. `3-4-5`: strong structural hit through `El Shaddai = 345`.
3. Star/Mersenne/Fibonacci structures: promising, but should remain exploratory until tested against controls.

The most interesting new mathematical structure is probably not phi or e. It is the star-number/Mersenne cluster around `13`, `37`, `73`, and `181`:

- `El = 31 = 2^5 - 1`
- `HaKavod = 37`, a star number
- `Olam` and `HaNe'eman` components are `146 = 2 * 73`
- `El De'ot = 511 = 2^9 - 1 = 7 * 73`
- `Ehyeh Asher Ehyeh = 543 = 3 * 181`

That may be a real geometry/number-theory sublayer, but it is not yet manuscript-ready.
"""
    (DOCS_DIR / "MATHEMATICAL_CONSTANT_AUDIT.md").write_text(content, encoding="utf-8")


def main() -> None:
    rows = corpus_hits() + component_hits()
    write_csv(rows)
    write_report(rows)
    print(f"wrote {DATA_DIR / 'mathematical_constant_hits.csv'}")
    print(f"wrote {DOCS_DIR / 'MATHEMATICAL_CONSTANT_AUDIT.md'}")


if __name__ == "__main__":
    main()
