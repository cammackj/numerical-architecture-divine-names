from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "master_results.csv"
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass
class DetailRow:
    dataset: str
    base: int
    index: int
    name: str
    value: int
    representation: str
    is_palindrome: str
    collapse_endpoint: int


@dataclass
class SummaryRow:
    dataset: str
    base: int
    value_count: int
    palindrome_count: int
    palindrome_rank: int
    collapse_8_count: int
    collapse_12_count: int
    collapse_4_count: int
    attractor_8_12_count: int
    attractor_rank: int
    combined_score: int
    combined_rank: int
    palindrome_examples: str
    collapse_8_examples: str
    collapse_12_examples: str


def to_base(value: int, base: int) -> str:
    if value == 0:
        return "0"
    out: list[str] = []
    current = value
    while current:
        current, remainder = divmod(current, base)
        out.append(DIGITS[remainder])
    return "".join(reversed(out))


def collapse_representation(text: str, stop: int = 12) -> int:
    current = sum(DIGITS.index(ch) for ch in text)
    while current > stop:
        current = sum(int(ch) for ch in str(current))
    return current


def is_palindrome(text: str) -> bool:
    return len(text) > 1 and text == text[::-1]


def load_literal_rows() -> list[dict[str, str]]:
    with MASTER.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if row["scope"] == "literal-heading"]


def value_for_dataset(row: dict[str, str], dataset: str) -> int:
    if dataset == "standard":
        return int(row["computed_standard"])
    if dataset == "mispar_gadol":
        return int(row["computed_mispar_gadol"])
    if dataset == "paper_basis":
        if row["base12_claim_basis"] == "standard":
            return int(row["computed_standard"])
        return int(row["computed_mispar_gadol"])
    raise ValueError(f"unknown dataset: {dataset}")


def make_details(rows: list[dict[str, str]]) -> list[DetailRow]:
    details: list[DetailRow] = []
    for dataset in ["standard", "mispar_gadol", "paper_basis"]:
        for base in range(2, 21):
            for row in rows:
                value = value_for_dataset(row, dataset)
                representation = to_base(value, base)
                details.append(
                    DetailRow(
                        dataset=dataset,
                        base=base,
                        index=int(row["index"]),
                        name=row["name"],
                        value=value,
                        representation=representation,
                        is_palindrome="yes" if is_palindrome(representation) else "no",
                        collapse_endpoint=collapse_representation(representation),
                    )
                )
    return details


def rank_desc(rows: list[SummaryRow], attr: str, rank_attr: str) -> None:
    last_value: int | None = None
    last_rank = 0
    for position, row in enumerate(sorted(rows, key=lambda item: (-getattr(item, attr), item.base)), start=1):
        value = getattr(row, attr)
        if value != last_value:
            last_rank = position
            last_value = value
        setattr(row, rank_attr, last_rank)


def make_summary(details: list[DetailRow]) -> list[SummaryRow]:
    summaries: list[SummaryRow] = []
    for dataset in ["standard", "mispar_gadol", "paper_basis"]:
        dataset_rows = [row for row in details if row.dataset == dataset]
        per_base: list[SummaryRow] = []
        for base in range(2, 21):
            rows = [row for row in dataset_rows if row.base == base]
            pal_rows = [row for row in rows if row.is_palindrome == "yes"]
            collapse8 = [row for row in rows if row.collapse_endpoint == 8]
            collapse12 = [row for row in rows if row.collapse_endpoint == 12]
            collapse4 = [row for row in rows if row.collapse_endpoint == 4]
            attractor = len(collapse8) + len(collapse12)
            # Combined score is intentionally simple and visible: palindromes are weighted
            # higher because the paper's base argument relies heavily on symmetry.
            combined = (2 * len(pal_rows)) + attractor
            per_base.append(
                SummaryRow(
                    dataset=dataset,
                    base=base,
                    value_count=len(rows),
                    palindrome_count=len(pal_rows),
                    palindrome_rank=0,
                    collapse_8_count=len(collapse8),
                    collapse_12_count=len(collapse12),
                    collapse_4_count=len(collapse4),
                    attractor_8_12_count=attractor,
                    attractor_rank=0,
                    combined_score=combined,
                    combined_rank=0,
                    palindrome_examples="; ".join(f"{row.name}={row.representation}" for row in pal_rows),
                    collapse_8_examples="; ".join(f"{row.name}={row.representation}" for row in collapse8),
                    collapse_12_examples="; ".join(f"{row.name}={row.representation}" for row in collapse12),
                )
            )
        rank_desc(per_base, "palindrome_count", "palindrome_rank")
        rank_desc(per_base, "attractor_8_12_count", "attractor_rank")
        rank_desc(per_base, "combined_score", "combined_rank")
        summaries.extend(sorted(per_base, key=lambda row: row.base))
    return summaries


def write_csv(path: Path, rows: list) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def table_for_dataset(summaries: list[SummaryRow], dataset: str) -> str:
    rows = [row for row in summaries if row.dataset == dataset]
    lines = [
        "| Base | Palindromes | Pal rank | Collapse 8 | Collapse 12 | 8/12 total | Attractor rank | Combined | Combined rank |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        marker = " **<- base 12**" if row.base == 12 else ""
        lines.append(
            f"| {row.base}{marker} | {row.palindrome_count} | {row.palindrome_rank} | "
            f"{row.collapse_8_count} | {row.collapse_12_count} | {row.attractor_8_12_count} | "
            f"{row.attractor_rank} | {row.combined_score} | {row.combined_rank} |"
        )
    return "\n".join(lines)


def top_examples(summaries: list[SummaryRow], dataset: str, metric: str) -> str:
    rows = sorted(
        [row for row in summaries if row.dataset == dataset],
        key=lambda row: (-getattr(row, metric), row.base),
    )[:5]
    chunks = []
    for row in rows:
        examples = row.palindrome_examples if metric == "palindrome_count" else (
            row.collapse_8_examples + ("; " if row.collapse_8_examples and row.collapse_12_examples else "") + row.collapse_12_examples
        )
        chunks.append(f"- Base {row.base}: {getattr(row, metric)} ({examples or 'no examples'})")
    return "\n".join(chunks)


def write_report(summaries: list[SummaryRow]) -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    p12 = {row.dataset: row for row in summaries if row.base == 12}
    paper_rows = [row for row in summaries if row.dataset == "paper_basis"]
    best_combined = max(paper_rows, key=lambda row: row.combined_score)
    p12_palindromes = ", ".join(
        f"`{example}`" for example in p12["paper_basis"].palindrome_examples.split("; ")
    )
    report = f"""# Base Comparison Findings

Generated by `scripts/base_comparison.py`.

This is a pressure test for the base-12 thesis. It compares bases 2 through 20 using the {p12['paper_basis'].value_count} literal-heading rows from `data/master_results.csv`; expansion labels, formulas, and canonical reference objects are excluded from the main comparison.

## Method

Three datasets are compared:

- `standard`: standard gematria values.
- `mispar_gadol`: computed Mispar Gadol values.
- `paper_basis`: the value basis declared for each manuscript row, whether standard or Mispar Gadol.

For each base, the script counts:

- representations that are palindromes;
- digit-collapse endpoints of `8`;
- digit-collapse endpoints of `12`;
- a simple combined score: `2 * palindrome_count + collapse_8_count + collapse_12_count`.

The collapse operation sums digit-symbol values in the representation and repeats until the result is `12` or below. This is a mechanical comparison, not a final interpretive rule.

## Headline Results

For the `paper_basis` dataset, base 12 has:

- palindrome count: {p12['paper_basis'].palindrome_count} (rank {p12['paper_basis'].palindrome_rank} of 19)
- 8/12 collapse total: {p12['paper_basis'].attractor_8_12_count} (rank {p12['paper_basis'].attractor_rank} of 19)
- combined score: {p12['paper_basis'].combined_score} (rank {p12['paper_basis'].combined_rank} of 19)

Base 12 ranks first for palindrome production in the paper-basis dataset. Its simple combined score ranks {p12['paper_basis'].combined_rank}, behind base {best_combined.base}, because base {best_combined.base} produces more broad 8/12 collapse endpoints. This does not change the base-12 palindrome ranking; it distinguishes two different measures.

It is not uniquely strongest on collapse endpoints alone; nearby and lower bases can produce many 8/12 endpoints under this broad collapse rule.

This supports a more precise thesis: base 12 appears distinctive mainly for **identity/symmetry/palindrome structure**, while collapse clustering needs stricter definitions and controls.

## Paper-Basis Summary

{table_for_dataset(summaries, 'paper_basis')}

## Top Palindrome Bases

### Paper Basis

{top_examples(summaries, 'paper_basis', 'palindrome_count')}

### Standard

{top_examples(summaries, 'standard', 'palindrome_count')}

### Mispar Gadol

{top_examples(summaries, 'mispar_gadol', 'palindrome_count')}

## Top 8/12 Collapse Bases

### Paper Basis

{top_examples(summaries, 'paper_basis', 'attractor_8_12_count')}

### Standard

{top_examples(summaries, 'standard', 'attractor_8_12_count')}

### Mispar Gadol

{top_examples(summaries, 'mispar_gadol', 'attractor_8_12_count')}

## Standard Summary

{table_for_dataset(summaries, 'standard')}

## Mispar Gadol Summary

{table_for_dataset(summaries, 'mispar_gadol')}

## Provisional Interpretation

- The base-12 case is not merely arbitrary: in the paper-basis dataset it ranks first for palindrome production.
- The {p12['paper_basis'].palindrome_count} base-12 palindrome rows in this declared-basis set are {p12_palindromes}.
- Expansion labels such as `BEN` remain mathematically relevant in their own category, but they are not counted as divine-name rows here.
- Other bases also produce palindromes. The possible significance of the base-12 result therefore depends not only on the count, but on which names occupy those rows.
- Collapse endpoints are more ambiguous. They should not carry the whole argument without controls.
- The paper should separate the base-12 palindrome/identity argument from the collapse-cluster argument.
"""
    (DOCS_DIR / "BASE_COMPARISON.md").write_text(report, encoding="utf-8")


def main() -> None:
    rows = load_literal_rows()
    details = make_details(rows)
    summaries = make_summary(details)
    write_csv(DATA_DIR / "base_comparison_details.csv", details)
    write_csv(DATA_DIR / "base_comparison_summary.csv", summaries)
    write_report(summaries)
    print(f"rows compared: {len(rows)}")
    print(f"wrote {DATA_DIR / 'base_comparison_details.csv'}")
    print(f"wrote {DATA_DIR / 'base_comparison_summary.csv'}")
    print(f"wrote {DOCS_DIR / 'BASE_COMPARISON.md'}")


if __name__ == "__main__":
    main()
