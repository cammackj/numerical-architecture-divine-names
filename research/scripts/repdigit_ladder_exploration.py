from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_numerical_claims import (  # noqa: E402
    MISPAR_GADOL_VALUES,
    STANDARD_VALUES,
    gematria,
    to_base,
)


RESEARCH_ROOT = PROJECT_ROOT / "research"
DATA_DIR = RESEARCH_ROOT / "data"
REPORT_OUT = RESEARCH_ROOT / "REPDIGIT_LADDER_EXPLORATION.md"
LADDER_OUT = DATA_DIR / "repdigit_ladder.csv"
RELATION_OUT = DATA_DIR / "repdigit_additive_relations.csv"
ENUMERATION_OUT = DATA_DIR / "repdigit_subset_enumeration.csv"
MASTER_REGISTRY = PROJECT_ROOT / "data" / "master_results.csv"
EXPANSION_REGISTRY = PROJECT_ROOT / "data" / "divine_name_expansion_results.csv"
PSALM_WINDOWS = DATA_DIR / "psalm_first_verse_two_word_windows.csv"

DIGITS = "0123456789AB"
CORE_RUNGS = frozenset({1, 2, 3, 4, 5, 7})
EXTENDED_RUNGS = frozenset({1, 2, 3, 4, 5, 7, 9, 11})


@dataclass(frozen=True)
class Node:
    rung: int
    name: str
    hebrew: str
    category: str
    evidence: str
    note: str


@dataclass(frozen=True)
class LadderRow:
    rung: int
    decimal_value: int
    base12_repdigit: str
    occupied_core: str
    occupied_extended: str
    occupants: str
    evidence_notes: str


@dataclass(frozen=True)
class RelationRow:
    scope: str
    left_rung: int
    middle_rung: int
    result_rung: int
    decimal_equation: str
    base12_equation: str
    left_occupants: str
    middle_occupants: str
    result_occupants: str


NODES = (
    Node(1, "Echad", "אחד", "formula-component", "exact-biblical-component", "The one/echad term in YHWH Echad."),
    Node(2, "YHWH", "יהוה", "divine-name", "exact-biblical", "Primary divine-name row."),
    Node(3, "YHWH Echad", "יהוה אחד", "identity-formula", "exact-biblical", "Complete Shema identity formula."),
    Node(4, "Elohei", "אלוהי", "construct-component", "exact-biblical-component", "Construct form used in attested Elohei titles."),
    Node(4, "BEN", "בן", "kabbalistic-label", "later-traditional", "Standard value only; the manuscript's BEN row has a different Mispar Gadol value."),
    Node(5, "Adonai", "אדני", "divine-title", "exact-biblical", "Primary divine-title row."),
    Node(7, "Adonai YHWH", "אדני יהוה", "divine-address", "exact-biblical", "Attested complete divine address."),
    Node(7, "Amen lexical form", "אמן", "lexical-title-extraction", "translation-sensitive", "The exact translated Revelation title bears an article and is not this value."),
    Node(9, "Malakh YHWH", "מלאך יהוה", "divine-agent-title", "exact-biblical-form", "Admission as divine designation depends on a Christian divine-agent reading."),
    Node(11, "Ben HaElohim defective", "בן האלהים", "translated-christian-title", "translation-sensitive", "The palindrome depends on a defective historical spelling."),
)


def occupants_by_rung() -> dict[int, list[Node]]:
    grouped: dict[int, list[Node]] = defaultdict(list)
    for node in NODES:
        value = gematria(node.hebrew, STANDARD_VALUES)
        expected = 13 * node.rung
        representation = to_base(value)
        expected_repdigit = DIGITS[node.rung] * 2
        if value != expected or representation != expected_repdigit:
            raise ValueError(
                f"Node validation failed for {node.name}: {value}={representation}, "
                f"expected {expected}={expected_repdigit}"
            )
        grouped[node.rung].append(node)
    return grouped


def additive_triples(rungs: frozenset[int]) -> list[tuple[int, int, int]]:
    values = sorted(rungs)
    return [
        (left, right, left + right)
        for index, left in enumerate(values)
        for right in values[index + 1 :]
        if left + right in rungs
    ]


def ladder_rows(grouped: dict[int, list[Node]]) -> list[LadderRow]:
    rows: list[LadderRow] = []
    for rung in range(1, 12):
        nodes = grouped.get(rung, [])
        rows.append(
            LadderRow(
                rung=rung,
                decimal_value=13 * rung,
                base12_repdigit=DIGITS[rung] * 2,
                occupied_core="yes" if rung in CORE_RUNGS else "no",
                occupied_extended="yes" if rung in EXTENDED_RUNGS else "no",
                occupants="; ".join(node.name for node in nodes),
                evidence_notes="; ".join(
                    f"{node.name}: {node.evidence} ({node.note})" for node in nodes
                ),
            )
        )
    return rows


def relation_rows(grouped: dict[int, list[Node]]) -> list[RelationRow]:
    rows: list[RelationRow] = []
    for scope, rungs in (("core", CORE_RUNGS), ("extended", EXTENDED_RUNGS)):
        for left, right, result in additive_triples(rungs):
            rows.append(
                RelationRow(
                    scope=scope,
                    left_rung=left,
                    middle_rung=right,
                    result_rung=result,
                    decimal_equation=f"{13 * left} + {13 * right} = {13 * result}",
                    base12_equation=f"{DIGITS[left] * 2} + {DIGITS[right] * 2} = {DIGITS[result] * 2}",
                    left_occupants="; ".join(node.name for node in grouped[left]),
                    middle_occupants="; ".join(node.name for node in grouped[right]),
                    result_occupants="; ".join(node.name for node in grouped[result]),
                )
            )
    return rows


def enumerate_subsets() -> tuple[list[dict[str, object]], dict[int, dict[str, object]]]:
    rows: list[dict[str, object]] = []
    summaries: dict[int, dict[str, object]] = {}
    for size, observed in ((6, CORE_RUNGS), (8, EXTENDED_RUNGS)):
        frequencies: Counter[int] = Counter()
        maximum = 0
        maximum_sets: list[tuple[int, ...]] = []
        for subset in combinations(range(1, 12), size):
            count = len(additive_triples(frozenset(subset)))
            frequencies[count] += 1
            if count > maximum:
                maximum = count
                maximum_sets = [subset]
            elif count == maximum:
                maximum_sets.append(subset)
        observed_count = len(additive_triples(observed))
        total = sum(frequencies.values())
        at_least = sum(frequency for count, frequency in frequencies.items() if count >= observed_count)
        summaries[size] = {
            "observed_count": observed_count,
            "maximum": maximum,
            "maximum_sets": maximum_sets,
            "at_least": at_least,
            "total": total,
            "proportion": at_least / total,
        }
        for count, frequency in sorted(frequencies.items()):
            rows.append(
                {
                    "subset_size": size,
                    "additive_relation_count": count,
                    "frequency": frequency,
                    "proportion": frequency / total,
                    "observed_relation_count": observed_count,
                }
            )
    return rows, summaries


def verify_empty_sixth_rung() -> None:
    registry_specs = (
        (MASTER_REGISTRY, "computed_standard", "computed_mispar_gadol"),
        (EXPANSION_REGISTRY, "standard_gematria", "mispar_gadol"),
    )
    registry_hits: list[str] = []
    for path, standard_field, mispar_field in registry_specs:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row[standard_field] == "78" or row[mispar_field] == "78":
                    registry_hits.append(f"{path.name}: {row['name']}")
    if registry_hits:
        raise ValueError(
            "The admitted registry now contains a 66_12 occupant: "
            + "; ".join(registry_hits)
        )

    phrase = "יהוה בכל"
    standard = gematria(phrase, STANDARD_VALUES)
    mispar = gematria(phrase, MISPAR_GADOL_VALUES)
    if standard != 78 or mispar != 78 or to_base(standard) != "66":
        raise ValueError("Psalm 111:1 gap-boundary calculation changed")

    with PSALM_WINDOWS.open(encoding="utf-8-sig", newline="") as handle:
        matches = [
            row
            for row in csv.DictReader(handle)
            if row["standard_value"] == "78" or row["mispar_gadol_value"] == "78"
        ]
    if (
        len(matches) != 1
        or matches[0]["reference"] != "Ps.111.1"
        or matches[0]["phrase"] != phrase
    ):
        raise ValueError("The declared Psalm-opening 66_12 boundary is no longer exact")


def write_dataclass_csv(path: Path, rows: list[object]) -> None:
    dictionaries = [asdict(row) for row in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dictionaries[0].keys()))
        writer.writeheader()
        writer.writerows(dictionaries)


def write_dict_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def ladder_table(rows: list[LadderRow]) -> str:
    lines = [
        "| Rung | Decimal | Base 12 | Core | Extended | Occupants |",
        "| ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.rung} | {row.decimal_value} | `{row.base12_repdigit}` | "
            f"{row.occupied_core} | {row.occupied_extended} | {row.occupants or '-'} |"
        )
    return "\n".join(lines)


def relation_table(rows: list[RelationRow], scope: str) -> str:
    selected = [row for row in rows if row.scope == scope]
    lines = [
        "| Rungs | Decimal equation | Base-12 equation | Named nodes |",
        "| --- | --- | --- | --- |",
    ]
    for row in selected:
        lines.append(
            f"| {row.left_rung} + {row.middle_rung} = {row.result_rung} | "
            f"`{row.decimal_equation}` | `{row.base12_equation}` | "
            f"{row.left_occupants} + {row.middle_occupants} -> {row.result_occupants} |"
        )
    return "\n".join(lines)


def write_report(
    ladder: list[LadderRow],
    relations: list[RelationRow],
    summaries: dict[int, dict[str, object]],
) -> None:
    core = summaries[6]
    extended = summaries[8]
    core_max_sets = ", ".join("{" + ", ".join(map(str, item)) + "}" for item in core["maximum_sets"])
    content = f"""# Base-12 Repdigit Ladder Exploration

## Status

Post-publication exploratory analysis integrated into manuscript version
`1.1.0`. The archived `v1.0.0` remains unchanged.

## Mathematical Identity

Every two-digit repeated-digit numeral in base 12 satisfies:

`dd_12 = 12d + d = 13d`

The two-digit divine-name palindromes are therefore members of one exact
11-rung ladder rather than unrelated conversions.

## Observed Ladder

{ladder_table(ladder)}

The core six rungs are `1, 2, 3, 4, 5, 7`. They use exact biblical names,
formulas, or components, but they are not six independent lexical names:
`Echad` and `Elohei` are components, and `YHWH Echad` and `Adonai YHWH` contain
already counted names. The extended set adds the Christian divine-agent
reading at rung 9 and a translation-sensitive defective title at rung 11.

The missing sixth rung is explicit: `66_12 = 78_10`, but neither the corrected
manuscript registry nor the 82-row expansion registry contains an admitted
name, title, formula, or component at value 78 under either value system. The
Psalm-opening scan contains one mechanical two-word window at that value,
`יהוה בכל` in Psalm 111:1, but it cuts the ordinary phrase "YHWH, with all
[my heart]" before its completion. It is retained as a boundary check rather
than promoted into a divine title. Rungs 8 and 10 are also unoccupied.

## Additive Closure

Because the ladder is linear in 13, addition of occupied rungs becomes
carry-free addition of repeated base-12 digits whenever the result remains
below 12.

### Core relations

{relation_table(relations, "core")}

### Extended relations

{relation_table(relations, "extended")}

## Finite Subset Comparison

Among all `C(11, 6) = {core['total']}` six-rung subsets of `1..11`, the core set
has {core['observed_count']} distinct-addend closure relations. This is the
maximum possible. Only {core['at_least']} subsets attain that maximum:
{core_max_sets}. The descriptive finite proportion is
`{core['at_least']}/{core['total']} = {core['proportion']:.6f}`.

The eight-rung extended set has {extended['observed_count']} relations. Among
all `C(11, 8) = {extended['total']}` subsets, {extended['at_least']} have at
least that many, for a descriptive proportion of
`{extended['proportion']:.6f}`. Its closure is therefore less exceptional than
the core six-rung set.

## Interpretation Boundary

This is a genuine algebraic organization, not six separate base-conversion
coincidences. It also has a strong selection caveat: the ladder was recognized
because these rows were already known to be two-digit base-12 palindromes, and
the core set mixes complete names with components and nested formulas. The
finite subset proportions describe the occupied rung pattern; they are not
sampling probabilities for independently selected divine names.

The strongest defensible result is structural: the source-secure biblical
nodes occupy the maximally additively closed six-rung subset `{{1,2,3,4,5,7}}`
of the 11 possible two-digit base-12 repdigits.
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def main() -> None:
    grouped = occupants_by_rung()
    verify_empty_sixth_rung()
    ladder = ladder_rows(grouped)
    relations = relation_rows(grouped)
    enumeration, summaries = enumerate_subsets()
    write_dataclass_csv(LADDER_OUT, ladder)
    write_dataclass_csv(RELATION_OUT, relations)
    write_dict_csv(ENUMERATION_OUT, enumeration)
    write_report(ladder, relations, summaries)
    print(f"wrote {REPORT_OUT}")
    print(f"wrote {LADDER_OUT}")
    print(f"wrote {RELATION_OUT}")
    print(f"wrote {ENUMERATION_OUT}")


if __name__ == "__main__":
    main()
