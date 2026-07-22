from __future__ import annotations

import csv
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_numerical_claims import to_base  # noqa: E402


RESEARCH_ROOT = PROJECT_ROOT / "research"
DATA_DIR = RESEARCH_ROOT / "data"
REPORT_OUT = RESEARCH_ROOT / "CHAPTER_CLOSURE_EXPLORATION.md"
SCAN_OUT = DATA_DIR / "chapter_closure_finite_scan.csv"
CONTACT_OUT = DATA_DIR / "chapter_closure_registry_contacts.csv"
DIGITS = "0123456789AB"
TANAKH_CHAPTERS = 929


@dataclass(frozen=True)
class ClosureRow:
    source_decimal: int
    source_base12: str
    source_decimal_palindrome: str
    source_prime: str
    closure_base12: str
    closure_decimal: int
    closure_outer_digit_sum: int
    closure_inner_digit_sum: int
    closure_notation_digit_sum: int
    closure_decimal_first_digit_sum: int
    full_conjunction: str


@dataclass(frozen=True)
class RegistryContact:
    source: str
    name: str
    layer: str
    route: str
    decimal_value: int
    base12_value: str


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    return all(value % divisor for divisor in range(3, math.isqrt(value) + 1, 2))


def one_digit_right_closure(base12: str) -> str | None:
    if len(base12) != 3 or base12[1] != base12[2]:
        return None
    return base12 + base12[0]


def notation_digit_sum(base12: str) -> int:
    return sum(DIGITS.index(digit) for digit in base12)


def decimal_first_digit_sum(value: int) -> int:
    return sum(int(digit) for digit in str(value))


def make_row(value: int) -> ClosureRow | None:
    source_base12 = to_base(value)
    closure_base12 = one_digit_right_closure(source_base12)
    if closure_base12 is None:
        return None

    closure_decimal = int(closure_base12, 12)
    source_palindrome = str(value) == str(value)[::-1]
    source_prime = is_prime(value)
    closure_notation_sum = notation_digit_sum(closure_base12)
    closure_outer_sum = notation_digit_sum(
        closure_base12[0] + closure_base12[-1]
    )
    closure_inner_sum = notation_digit_sum(closure_base12[1:3])
    closure_decimal_sum = decimal_first_digit_sum(closure_decimal)
    full_conjunction = (
        source_palindrome
        and source_prime
        and closure_notation_sum == 22
        and closure_decimal_sum == 12
    )

    return ClosureRow(
        source_decimal=value,
        source_base12=source_base12,
        source_decimal_palindrome="yes" if source_palindrome else "no",
        source_prime="yes" if source_prime else "no",
        closure_base12=closure_base12,
        closure_decimal=closure_decimal,
        closure_outer_digit_sum=closure_outer_sum,
        closure_inner_digit_sum=closure_inner_sum,
        closure_notation_digit_sum=closure_notation_sum,
        closure_decimal_first_digit_sum=closure_decimal_sum,
        full_conjunction="yes" if full_conjunction else "no",
    )


def write_csv(path: Path, rows: list[ClosureRow] | list[RegistryContact]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dictionaries = [asdict(row) for row in rows]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dictionaries[0].keys()))
        writer.writeheader()
        writer.writerows(dictionaries)


def registry_contacts() -> list[RegistryContact]:
    contacts: list[RegistryContact] = []
    targets_decimal = {65, 556, 655, 786, 929}
    targets_base12 = {"55", "556", "655"}
    sources = (
        (
            "master_results.csv",
            PROJECT_ROOT / "data" / "master_results.csv",
            "corpus_layer",
            "computed_standard",
            "computed_mispar_gadol",
            "base12_standard",
            "base12_mispar_gadol",
        ),
        (
            "divine_name_expansion_results.csv",
            PROJECT_ROOT / "data" / "divine_name_expansion_results.csv",
            "layer",
            "standard_gematria",
            "mispar_gadol",
            "base12_standard",
            "base12_mispar_gadol",
        ),
    )

    for (
        source_name,
        path,
        layer_field,
        standard_field,
        mispar_field,
        base12_standard_field,
        base12_mispar_field,
    ) in sources:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                for route, decimal_field, base12_field in (
                    ("standard", standard_field, base12_standard_field),
                    ("mispar-gadol", mispar_field, base12_mispar_field),
                ):
                    decimal_value = int(row[decimal_field])
                    base12_value = row[base12_field]
                    if (
                        decimal_value not in targets_decimal
                        and base12_value not in targets_base12
                    ):
                        continue
                    contacts.append(
                        RegistryContact(
                            source=source_name,
                            name=row["name"],
                            layer=row[layer_field],
                            route=route,
                            decimal_value=decimal_value,
                            base12_value=base12_value,
                        )
                    )
    return contacts


def palindrome_source_table(rows: list[ClosureRow]) -> str:
    lines = [
        "| Decimal source | Base 12 | Prime? | Closure | Closure value | "
        "Outer sum | Inner sum | Notation sum | Decimal sum |",
        "| ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        if row.source_decimal_palindrome != "yes":
            continue
        lines.append(
            f"| {row.source_decimal} | `{row.source_base12}` | "
            f"{row.source_prime} | `{row.closure_base12}` | "
            f"{row.closure_decimal} | {row.closure_outer_digit_sum} | "
            f"{row.closure_inner_digit_sum} | "
            f"{row.closure_notation_digit_sum} | "
            f"{row.closure_decimal_first_digit_sum} |"
        )
    return "\n".join(lines)


def write_report(rows: list[ClosureRow]) -> None:
    target = next(row for row in rows if row.source_decimal == TANAKH_CHAPTERS)
    full_hits = [row for row in rows if row.full_conjunction == "yes"]
    decimal_palindromes = sum(
        row.source_decimal_palindrome == "yes" for row in rows
    )
    primes = sum(row.source_prime == "yes" for row in rows)
    palindromic_primes = sum(
        row.source_decimal_palindrome == "yes" and row.source_prime == "yes"
        for row in rows
    )
    notation_22 = sum(row.closure_notation_digit_sum == 22 for row in rows)
    outer_12 = sum(row.closure_outer_digit_sum == 12 for row in rows)
    outer_12_and_notation_22 = sum(
        row.closure_outer_digit_sum == 12
        and row.closure_notation_digit_sum == 22
        for row in rows
    )
    decimal_12 = sum(
        row.closure_decimal_first_digit_sum == 12 for row in rows
    )
    both_sums = sum(
        row.closure_notation_digit_sum == 22
        and row.closure_decimal_first_digit_sum == 12
        for row in rows
    )

    content = f"""# Chapter-Total Palindromic Closure Exploration

## Status

Post-publication exploratory analysis integrated into manuscript version
1.2.0. This report records the author's forward/reverse-overlap observation
and supplies the complete finite check behind the reader-facing discussion.
Earlier numbered releases remain unchanged.

## Exact Observation

The received Tanakh chapter total gives:

`929_10 = 655_12`

The one-digit right palindromic closure is:

`655_12 -> 6556_12 = 11154_10`

The completed string contains the source numeral forward in its first three
positions and backward in its last three positions:

`655 | 6`

`6 | 556`

The two readings overlap on the central `55`. More generally, every eligible
three-digit source has the form `ABB`; its closure is `ABBA`, which contains
`ABB` followed by the overlapping reversal `BBA`. The overlap is therefore an
exact description of the target, but it is not independent of the palindrome
construction.

The target also has the exact frame decomposition:

`outer digits: 6 + 6 = 12`;

`inner digits: 5 + 5 = 10`;

`complete notation: 12 + 10 = 22`.

The central string is not only a pair summing to 10: `55_12` is the complete
base-12 value of Adonai.

## Finite Comparison

The exhaustive universe is every three-digit base-12 integer from `100_12`
through `BBB_12`, or {12**3 - 12**2:,} values. A one-digit right extension can
make `XYZ` palindromic only when `Y = Z`, after which the unique appended digit
is `X`. Exactly {len(rows)} values satisfy this condition, a proportion of
`{len(rows)}/{12**3 - 12**2} = {len(rows) / (12**3 - 12**2):.8f}`.

Within those {len(rows)} eligible sources:

- {decimal_palindromes} are also palindromes in ordinary decimal notation;
- {primes} are prime;
- {palindromic_primes} are both decimal palindromes and prime;
- {outer_12} closures have outer digits summing to 12;
- {notation_22} closures have base-12 notation digits summing to 22;
- {outer_12_and_notation_22} closure has both an outer sum of 12 and a complete
  notation sum of 22;
- {decimal_12} converted closure values have a first decimal digit sum of 12;
- {both_sums} closure satisfies both exact sum conditions;
- {len(full_hits)} source satisfies the complete conjunction of decimal
  palindrome, primality, notation sum 22, and converted-value sum 12.

The decimal-palindromic sources provide the clearest compact comparison:

{palindrome_source_table(rows)}

The sole full-conjunction row is therefore:

`{target.source_decimal}_10 = {target.source_base12}_12 -> {target.closure_base12}_12 = {target.closure_decimal}_10`

with:

`6 + 5 + 5 + 6 = 22 -> 4`

with outer/inner partition:

`(6 + 6) + (5 + 5) = 12 + 10 = 22`

and:

`1 + 1 + 1 + 5 + 4 = 12`.

This is a finite descriptive uniqueness result, not a confirmatory probability.
The conjunction and its comparison universe were articulated after the target
was known.

## Registered Name And Title Contacts

The displayed string `655` has a separate registered contact:

- `HaKadosh Baruch Hu / הקדוש ברוך הוא = 655_10` under standard gematria;
- its Aramaic counterpart `Qudsha Berikh Hu / קודשא בריך הוא` also equals
  `655_10` in the expansion registry;
- the chapter total is `655_12 = 929_10`, so this is an exact digit-string
  correspondence across different bases, not equality of the underlying
  values;
- the central `55_12` is the complete base-12 value of
  `Adonai / אדני = 65_10`;
- the reversed suffix `556_12 = 786_10` has no match among registered standard
  or Mispar Gadol name/title values, and neither decimal 556 nor 929 has such a
  registered match.

The Hebrew and Aramaic forms at decimal 655 express the same later-traditional
title family and should not be counted as two independent confirmations.
The complete registry query is preserved in
`research/data/chapter_closure_registry_contacts.csv`.

## Abba / Father Aside

The generic four-position pattern of the closure is `A-B-B-A`. The same Latin
and Greek transliteration, *Abba*, represents the Aramaic address for
"father," used by Jesus in Mark 14:36 and repeated in Romans 8:15 and
Galatians 4:6. The underlying Semitic spelling is `אבא`, a three-letter
`A-B-A` palindrome rather than a four-letter Hebrew or Aramaic `A-B-B-A`
spelling.

Its standard gematria is:

`אבא = 1 + 2 + 1 = 4`.

The closure therefore supports the following exact but cross-representational
sequence:

`6556_12` has abstract form `A-B-B-A`;

`6 + 5 + 5 + 6 = 22_10 -> 4_10`;

the project tracks a declared 22-scroll/book arrangement of the Tanakh;

`YHWH = 26_10 = 22_12 -> 2 + 2 = 4_10`;

`Abba / אבא = 4_10`.

These statements use 22 in different mathematical roles: a count of declared
canonical units, a decimal intermediate in the closure's notation sum, and the
base-12 representation of YHWH. They do not need to be numerically identical
to form the observed pattern. The structural recurrence is that the
chapter-based construction passes through 22, the tracked Tanakh convention
contains 22 scroll/book units, and YHWH visibly takes the form `22_12`; both
the construction and YHWH then reach 4 under their displayed digit-collapse
paths, while *Abba* has gematria 4.

The letter labels are arbitrary. The same palindrome can be described as
`X-Y-Y-X`, `1-2-2-1`, or by any other pair of symbols. Choosing `A-B-B-A`
because it happens to spell *Abba* in transliteration is therefore post-hoc
wordplay, not an invariant mathematical property and not independent evidence
for the larger architecture. The meaning of *Abba* and its gematria of 4 are
exact, but their attachment to `6556_12` depends on the chosen variable names.
This observation is retained only as an interesting interpretive aside.

Textual anchors:

- Mark 14:36: https://www.biblegateway.com/passage/?search=Mark%2014%3A36
- Romans 8:15: https://www.biblegateway.com/passage/?search=Romans%208%3A15
- Galatians 4:6: https://www.biblegateway.com/passage/?search=Galatians%204%3A6

## Interpretation Boundary

The strongest new result is not merely that `6556` can be read in both
directions; every palindrome permits that. It is that the received decimal
palindromic prime 929 lands on the eligible base-12 form `655`, and its unique
one-digit closure is the sole member of the complete three-digit universe that
also produces both the 22 notation sum and the 12 converted-value sum.

The chapter system is received and late-medieval, while the closure remains a
defined post-conversion operation. The finite result makes the construction
more precisely describable; it does not make the closure an ancient textual
division or establish deliberate encoding. The project-specific 22-unit
arrangement must likewise remain explicit rather than being described as the
only Jewish enumeration.
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def main() -> None:
    rows = [
        row
        for value in range(12**2, 12**3)
        if (row := make_row(value)) is not None
    ]
    contacts = registry_contacts()
    write_csv(SCAN_OUT, rows)
    write_csv(CONTACT_OUT, contacts)
    write_report(rows)
    print(f"wrote {REPORT_OUT}")
    print(f"wrote {SCAN_OUT}")
    print(f"wrote {CONTACT_OUT}")


if __name__ == "__main__":
    main()
