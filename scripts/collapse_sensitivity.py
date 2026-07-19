from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from audit_numerical_claims import (
    DIGITS,
    collapse_base12_text,
    collapse_decimal,
    digit_sum_decimal,
    to_base,
)
from corpus_sensitivity import load_registry, make_values


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
SUMMARY_OUT = DATA_DIR / "collapse_sensitivity_summary.csv"
DETAIL_OUT = DATA_DIR / "collapse_sensitivity_details.csv"
REPORT_OUT = DOCS_DIR / "COLLAPSE_SENSITIVITY.md"


@dataclass
class ThresholdRow:
    stopping_threshold: int
    primary_rows: int
    truncated_endpoint_8_rows: int
    truncated_endpoint_12_rows: int


@dataclass
class DetailRow:
    index: int
    name: str
    decimal_first_sum_standard: int
    decimal_first_sum_mispar_gadol: int
    base12_first_sum_standard: int
    base12_first_sum_mispar_gadol: int
    truncated_12_endpoint_standard: int
    truncated_12_endpoint_mispar_gadol: int
    truncated_12_endpoint_base12_standard: int
    truncated_12_endpoint_base12_mispar_gadol: int
    decimal_root_standard: int
    decimal_root_mispar_gadol: int
    base12_root_standard: int
    base12_root_mispar_gadol: int
    exact_first_sum_8: str
    exact_first_sum_12: str
    truncated_endpoint_8: str
    truncated_endpoint_12: str
    basis_consistent_root_8: str


def base12_digit_sum(text: str) -> int:
    return sum(DIGITS.index(char) for char in text)


def decimal_digital_root(value: int) -> int:
    current = abs(value)
    while current >= 10:
        current = digit_sum_decimal(current)
    return current


def base12_digital_root(text: str) -> int:
    current = base12_digit_sum(text)
    while current >= 12:
        current = base12_digit_sum(to_base(current))
    return current


def first_sums(row) -> tuple[int, int, int, int]:
    return (
        digit_sum_decimal(row.standard_gematria),
        digit_sum_decimal(row.mispar_gadol),
        base12_digit_sum(row.base12_standard),
        base12_digit_sum(row.base12_mispar_gadol),
    )


def truncated_endpoints(row, stop: int) -> tuple[int, int, int, int]:
    return (
        collapse_decimal(row.standard_gematria, stop),
        collapse_decimal(row.mispar_gadol, stop),
        collapse_base12_text(row.base12_standard, stop),
        collapse_base12_text(row.base12_mispar_gadol, stop),
    )


def basis_consistent_roots(row) -> tuple[int, int, int, int]:
    return (
        decimal_digital_root(row.standard_gematria),
        decimal_digital_root(row.mispar_gadol),
        base12_digital_root(row.base12_standard),
        base12_digital_root(row.base12_mispar_gadol),
    )


def make_threshold_rows(rows: list[object]) -> list[ThresholdRow]:
    output: list[ThresholdRow] = []
    for stop in range(9, 16):
        endpoints = [set(truncated_endpoints(row, stop)) for row in rows]
        output.append(
            ThresholdRow(
                stopping_threshold=stop,
                primary_rows=len(rows),
                truncated_endpoint_8_rows=sum(8 in values for values in endpoints),
                truncated_endpoint_12_rows=sum(12 in values for values in endpoints),
            )
        )
    return output


def make_detail_rows(rows: list[object]) -> list[DetailRow]:
    output: list[DetailRow] = []
    for row in rows:
        sums = first_sums(row)
        endpoints = truncated_endpoints(row, 12)
        roots = basis_consistent_roots(row)
        output.append(
            DetailRow(
                index=row.index,
                name=row.name,
                decimal_first_sum_standard=sums[0],
                decimal_first_sum_mispar_gadol=sums[1],
                base12_first_sum_standard=sums[2],
                base12_first_sum_mispar_gadol=sums[3],
                truncated_12_endpoint_standard=endpoints[0],
                truncated_12_endpoint_mispar_gadol=endpoints[1],
                truncated_12_endpoint_base12_standard=endpoints[2],
                truncated_12_endpoint_base12_mispar_gadol=endpoints[3],
                decimal_root_standard=roots[0],
                decimal_root_mispar_gadol=roots[1],
                base12_root_standard=roots[2],
                base12_root_mispar_gadol=roots[3],
                exact_first_sum_8="yes" if 8 in sums else "no",
                exact_first_sum_12="yes" if 12 in sums else "no",
                truncated_endpoint_8="yes" if 8 in endpoints else "no",
                truncated_endpoint_12="yes" if 12 in endpoints else "no",
                basis_consistent_root_8="yes" if 8 in roots else "no",
            )
        )
    return output


def write_csv(path: Path, rows: list[object]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def threshold_table(rows: list[ThresholdRow]) -> str:
    lines = [
        "| Stopping threshold | Endpoint 8 rows | Endpoint 12 rows |",
        "| ---: | ---: | ---: |",
    ]
    lines.extend(
        f"| {row.stopping_threshold} | {row.truncated_endpoint_8_rows} | {row.truncated_endpoint_12_rows} |"
        for row in rows
    )
    return "\n".join(lines)


def name_list(rows: list[DetailRow], field: str) -> str:
    return "; ".join(row.name for row in rows if getattr(row, field) == "yes")


def write_report(thresholds: list[ThresholdRow], details: list[DetailRow]) -> None:
    first_8 = [row for row in details if row.exact_first_sum_8 == "yes"]
    first_12 = [row for row in details if row.exact_first_sum_12 == "yes"]
    truncated_8 = [row for row in details if row.truncated_endpoint_8 == "yes"]
    truncated_12 = [row for row in details if row.truncated_endpoint_12 == "yes"]
    root_8 = [row for row in details if row.basis_consistent_root_8 == "yes"]

    content = f"""# Collapse Sensitivity

Generated by `scripts/collapse_sensitivity.py` from the 24 source-controlled primary rows in `data/corpus_registry.csv`.

## Operator Under Test

The manuscript's current operator repeatedly sums decimal digits until the result is no greater than a declared stopping threshold. For a base-12 notation, it first sums the displayed base-12 digit values and then applies the same decimal truncated sum. This is a custom truncated digit sum, not a conventional digital root.

## Stopping-Threshold Sensitivity

{threshold_table(thresholds)}

The 8 endpoint is stable at {len(truncated_8)} rows throughout thresholds 9 through 15. The 12 endpoint is absent at thresholds 9 through 11 and appears at {len(truncated_12)} rows as soon as the process is allowed to stop at 12. It therefore should not be described as an independently emerging attractor.

## Exact First-Step Sums

The threshold result does not erase the underlying equalities. All {len(first_12)} rows classified at endpoint 12 reach 12 on the first digit-sum step; none arrives there only after a longer iteration. The stable description is therefore an **exact first-step 12-sum layer**, while "terminal 12-collapse" is rule-dependent.

- Exact first-step 8 rows ({len(first_8)}): {name_list(details, 'exact_first_sum_8')}
- Exact first-step 12 rows ({len(first_12)}): {name_list(details, 'exact_first_sum_12')}

## Basis-Consistent Digital Roots

Conventional one-digit reduction continues until a single digit remains in the relevant basis. Under that rule, 12 cannot be a terminal value. Across the four declared standard/Mispar and decimal/base-12 paths, {len(root_8)} primary rows touch a one-digit root of 8:

{name_list(details, 'basis_consistent_root_8')}

This differs from the {len(truncated_8)}-row endpoint-8 set under the manuscript's mixed truncated rule. Neither rule should silently replace the other; they answer different questions.

## Manuscript Consequence

- Retain every exact equation such as `5 + 4 + 3 = 12` and `2 + 8 + 2 = 12`.
- Rename the strict 12 endpoint as the **exact 12-sum layer** where the first-step equality is what matters.
- Describe the current repeated operation as a truncated digit sum with stopping threshold 12.
- Do not call 12 a conventional digital-root attractor.
- Keep the 8 endpoint result, while reporting that its membership changes from 10 to 11 rows under basis-consistent roots.

## Files

- `data/collapse_sensitivity_summary.csv`
- `data/collapse_sensitivity_details.csv`
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def main() -> None:
    rows = [
        row
        for row in make_values(load_registry())
        if row.corpus_layer == "primary-biblical"
    ]
    thresholds = make_threshold_rows(rows)
    details = make_detail_rows(rows)
    write_csv(SUMMARY_OUT, thresholds)
    write_csv(DETAIL_OUT, details)
    write_report(thresholds, details)
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {DETAIL_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
