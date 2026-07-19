from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from audit_numerical_claims import to_base


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"

MASTER_RESULTS = DATA_DIR / "master_results.csv"
EXPANSION_RESULTS = DATA_DIR / "divine_name_expansion_results.csv"
HOSTS_OUTPUT = DATA_DIR / "frame_relation_hosts.csv"
DIFFERENCES_OUTPUT = DATA_DIR / "frame_family_differences.csv"
YHWH_SCAN_OUTPUT = DATA_DIR / "yhwh_frame_center_scan.csv"
REPEATED_FRAME_SCAN_OUTPUT = DATA_DIR / "repeated_frame_center_scan.csv"
REPORT_OUTPUT = DOCS_DIR / "FRAME_RELATION_RESULTS.md"

DIGITS = "0123456789AB"
BASIS_ORDER = {"standard": 0, "mispar-gadol": 1}

DIFFERENCE_ANCHORS = {
    8: "eight",
    12: "twelve",
    22: "Hebrew alphabet / YHWH base-12 signature",
    26: "YHWH",
    31: "El",
    37: "Genesis-factor candidate",
    42: "forty-two",
    52: "BEN / doubled YHWH",
    72: "seventy-two",
    73: "Chokmah / wisdom candidate",
    91: "YHWH + Adonai / Amen",
    137: "fine-structure candidate",
    153: "fish / triangular-17 candidate",
    314: "Shaddai / pi digits",
    345: "El Shaddai / 3-4-5",
    358: "Mashiach / Nachash",
    386: "Yeshua",
    655: "Tanakh chapter prefix candidate",
}


@dataclass(frozen=True)
class RawExpression:
    record_id: str
    source_table: str
    name: str
    hebrew: str
    layer: str
    object_class: str
    attestation_status: str
    representative_source: str
    source_url: str
    standard: int
    mispar_gadol: int


@dataclass(frozen=True)
class Expression:
    key: str
    name: str
    hebrew: str
    layers: tuple[str, ...]
    object_classes: tuple[str, ...]
    attestation_statuses: tuple[str, ...]
    representative_sources: tuple[str, ...]
    source_urls: tuple[str, ...]
    source_records: tuple[str, ...]
    source_tables: tuple[str, ...]
    standard: int
    mispar_gadol: int


@dataclass(frozen=True)
class HostRow:
    expression_key: str
    name: str
    hebrew: str
    layers: str
    object_classes: str
    attestation_statuses: str
    representative_sources: str
    source_records: str
    basis: str
    value: int
    base12: str
    center_digit: str
    center_value: int
    outer_frame: str
    outer_frame_value: int
    base10_digital_root: int
    base12_digit_sum: int
    self_center_match: str
    named_frame_match: str
    framed_expressions: str


@dataclass(frozen=True)
class DisplayedHost:
    expression_key: str
    name: str
    hebrew: str
    base12: str
    value: int
    center_digit: str
    center_value: int
    outer_frame: str
    bases: tuple[str, ...]
    layers: str


@dataclass(frozen=True)
class DifferenceRow:
    outer_frame: str
    framed_expressions: str
    left_name: str
    left_base12: str
    left_center: str
    left_bases: str
    right_name: str
    right_base12: str
    right_center: str
    right_bases: str
    shared_uniform_bases: str
    comparison_type: str
    decimal_difference: int
    base12_difference: str
    anchor_hit: str
    anchor_note: str


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def expression_key(name: str, hebrew: str) -> str:
    return f"{name.casefold()}|{normalize_space(hebrew)}"


def decimal_root(value: int) -> int:
    return 0 if value == 0 else 1 + (value - 1) % 9


def digit_value(digit: str) -> int:
    return DIGITS.index(digit)


def join_unique(values: list[str] | tuple[str, ...]) -> str:
    return "; ".join(sorted({value for value in values if value}))


def read_master() -> list[RawExpression]:
    rows: list[RawExpression] = []
    with MASTER_RESULTS.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            standard = int(row["computed_standard"])
            mispar = int(row["computed_mispar_gadol"])
            if to_base(standard) != row["base12_standard"]:
                raise ValueError(f"Stored standard base-12 value changed for {row['name']}")
            if to_base(mispar) != row["base12_mispar_gadol"]:
                raise ValueError(f"Stored Mispar Gadol base-12 value changed for {row['name']}")
            rows.append(
                RawExpression(
                    record_id=f"manuscript:{row['index']}",
                    source_table="manuscript",
                    name=row["name"],
                    hebrew=normalize_space(row["hebrew"]),
                    layer=row["corpus_layer"],
                    object_class=row["object_class"],
                    attestation_status=row["attestation_status"],
                    representative_source=row["representative_source"],
                    source_url=row["source_url"],
                    standard=standard,
                    mispar_gadol=mispar,
                )
            )
    return rows


def read_expansion() -> list[RawExpression]:
    rows: list[RawExpression] = []
    with EXPANSION_RESULTS.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            standard = int(row["standard_gematria"])
            mispar = int(row["mispar_gadol"])
            if to_base(standard) != row["base12_standard"]:
                raise ValueError(f"Stored expansion standard base-12 value changed for {row['name']}")
            if to_base(mispar) != row["base12_mispar_gadol"]:
                raise ValueError(f"Stored expansion Mispar Gadol base-12 value changed for {row['name']}")
            rows.append(
                RawExpression(
                    record_id=f"expansion:{row['candidate_id']}",
                    source_table="expansion",
                    name=row["name"],
                    hebrew=normalize_space(row["hebrew"]),
                    layer=row["layer"],
                    object_class=row["object_class"],
                    attestation_status=row["attestation_status"],
                    representative_source=row["representative_source"],
                    source_url=row["source_url"],
                    standard=standard,
                    mispar_gadol=mispar,
                )
            )
    return rows


def collapse_expressions(rows: list[RawExpression]) -> list[Expression]:
    grouped: dict[str, list[RawExpression]] = {}
    for row in rows:
        grouped.setdefault(expression_key(row.name, row.hebrew), []).append(row)

    expressions: list[Expression] = []
    for key, members in grouped.items():
        values = {(member.standard, member.mispar_gadol) for member in members}
        if len(values) != 1:
            raise ValueError(f"Duplicate expression has inconsistent values: {key}")
        preferred = next(
            (member for member in members if member.source_table == "manuscript"),
            members[0],
        )
        standard, mispar = values.pop()
        expressions.append(
            Expression(
                key=key,
                name=preferred.name,
                hebrew=preferred.hebrew,
                layers=tuple(sorted({member.layer for member in members})),
                object_classes=tuple(sorted({member.object_class for member in members})),
                attestation_statuses=tuple(
                    sorted({member.attestation_status for member in members})
                ),
                representative_sources=tuple(
                    sorted({member.representative_source for member in members})
                ),
                source_urls=tuple(sorted({member.source_url for member in members})),
                source_records=tuple(sorted(member.record_id for member in members)),
                source_tables=tuple(sorted({member.source_table for member in members})),
                standard=standard,
                mispar_gadol=mispar,
            )
        )
    return sorted(expressions, key=lambda row: (row.name.casefold(), row.hebrew))


def value_for(expression: Expression, basis: str) -> int:
    return expression.standard if basis == "standard" else expression.mispar_gadol


def build_hosts(expressions: list[Expression]) -> list[HostRow]:
    value_index: dict[tuple[str, str], list[Expression]] = {}
    for expression in expressions:
        for basis in BASIS_ORDER:
            base12 = to_base(value_for(expression, basis))
            value_index.setdefault((basis, base12), []).append(expression)

    hosts: list[HostRow] = []
    for expression in expressions:
        for basis in BASIS_ORDER:
            value = value_for(expression, basis)
            base12 = to_base(value)
            if len(base12) < 3 or len(base12) % 2 == 0 or base12 != base12[::-1]:
                continue
            midpoint = len(base12) // 2
            center = base12[midpoint]
            frame = base12[:midpoint] + base12[midpoint + 1 :]
            matches = [
                match
                for match in value_index.get((basis, frame), [])
                if match.key != expression.key
            ]
            hosts.append(
                HostRow(
                    expression_key=expression.key,
                    name=expression.name,
                    hebrew=expression.hebrew,
                    layers=join_unique(expression.layers),
                    object_classes=join_unique(expression.object_classes),
                    attestation_statuses=join_unique(expression.attestation_statuses),
                    representative_sources=join_unique(expression.representative_sources),
                    source_records=join_unique(expression.source_records),
                    basis=basis,
                    value=value,
                    base12=base12,
                    center_digit=center,
                    center_value=digit_value(center),
                    outer_frame=frame,
                    outer_frame_value=int(frame, 12),
                    base10_digital_root=decimal_root(value),
                    base12_digit_sum=sum(digit_value(digit) for digit in base12),
                    self_center_match="yes" if digit_value(center) == decimal_root(value) else "no",
                    named_frame_match="yes" if matches else "no",
                    framed_expressions=join_unique([match.name for match in matches]),
                )
            )
    return sorted(
        hosts,
        key=lambda row: (
            row.outer_frame,
            row.base12,
            BASIS_ORDER[row.basis],
            row.name.casefold(),
        ),
    )


def displayed_hosts(hosts: list[HostRow]) -> list[DisplayedHost]:
    grouped: dict[tuple[str, str, str], list[HostRow]] = {}
    for host in hosts:
        if host.named_frame_match == "yes":
            grouped.setdefault(
                (host.expression_key, host.base12, host.outer_frame), []
            ).append(host)

    displayed: list[DisplayedHost] = []
    for (_, _, _), members in grouped.items():
        first = members[0]
        displayed.append(
            DisplayedHost(
                expression_key=first.expression_key,
                name=first.name,
                hebrew=first.hebrew,
                base12=first.base12,
                value=first.value,
                center_digit=first.center_digit,
                center_value=first.center_value,
                outer_frame=first.outer_frame,
                bases=tuple(sorted({row.basis for row in members}, key=BASIS_ORDER.get)),
                layers=first.layers,
            )
        )
    return sorted(displayed, key=lambda row: (row.outer_frame, row.value, row.name.casefold()))


def frame_expression_names(
    expressions: list[Expression], frame: str, bases: set[str] | None = None
) -> str:
    names: list[str] = []
    for expression in expressions:
        matching_bases = [
            basis
            for basis in BASIS_ORDER
            if to_base(value_for(expression, basis)) == frame
            and (bases is None or basis in bases)
        ]
        if matching_bases:
            names.append(f"{expression.name} [{'/'.join(matching_bases)}]")
    return join_unique(names)


def build_differences(
    expressions: list[Expression], displayed: list[DisplayedHost]
) -> list[DifferenceRow]:
    by_frame: dict[str, list[DisplayedHost]] = {}
    for host in displayed:
        by_frame.setdefault(host.outer_frame, []).append(host)

    rows: list[DifferenceRow] = []
    for frame, members in by_frame.items():
        if len(members) < 2:
            continue
        framed_names = frame_expression_names(expressions, frame)
        for left, right in combinations(sorted(members, key=lambda row: row.value), 2):
            if left.expression_key == right.expression_key:
                continue
            shared = sorted(set(left.bases) & set(right.bases), key=BASIS_ORDER.get)
            difference = abs(right.value - left.value)
            anchor_note = DIFFERENCE_ANCHORS.get(difference, "")
            rows.append(
                DifferenceRow(
                    outer_frame=frame,
                    framed_expressions=framed_names,
                    left_name=left.name,
                    left_base12=left.base12,
                    left_center=left.center_digit,
                    left_bases="; ".join(left.bases),
                    right_name=right.name,
                    right_base12=right.base12,
                    right_center=right.center_digit,
                    right_bases="; ".join(right.bases),
                    shared_uniform_bases="; ".join(shared),
                    comparison_type="same-basis" if shared else "mixed-basis-only",
                    decimal_difference=difference,
                    base12_difference=to_base(difference),
                    anchor_hit="yes" if anchor_note else "no",
                    anchor_note=anchor_note,
                )
            )
    return sorted(
        rows,
        key=lambda row: (
            row.outer_frame,
            row.decimal_difference,
            row.left_name.casefold(),
            row.right_name.casefold(),
        ),
    )


def build_yhwh_scan() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for center_value in range(12):
        center = DIGITS[center_value]
        base12 = f"2{center}2"
        value = int(base12, 12)
        root = decimal_root(value)
        digit_sum = 4 + center_value
        center_match = center_value == root
        sum_match = digit_sum == 12
        rows.append(
            {
                "center_digit": center,
                "center_value": center_value,
                "base12": base12,
                "decimal_value": value,
                "base10_digital_root": root,
                "base12_digit_sum": digit_sum,
                "center_equals_decimal_root": "yes" if center_match else "no",
                "base12_digit_sum_equals_12": "yes" if sum_match else "no",
                "both_conditions": "yes" if center_match and sum_match else "no",
            }
        )
    return rows


def matching_expression_names(
    expressions: list[Expression], basis: str, base12: str
) -> str:
    return join_unique(
        [
            expression.name
            for expression in expressions
            if to_base(value_for(expression, basis)) == base12
        ]
    )


def build_repeated_frame_scan(
    expressions: list[Expression],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for outer_value in range(1, 12):
        outer = DIGITS[outer_value]
        frame = f"{outer}{outer}"
        for center_value in range(12):
            center = DIGITS[center_value]
            base12 = f"{outer}{center}{outer}"
            value = int(base12, 12)
            root = decimal_root(value)
            digit_sum = 2 * outer_value + center_value
            center_match = center_value == root
            sum_match = digit_sum == 12
            rows.append(
                {
                    "outer_digit": outer,
                    "outer_value": outer_value,
                    "center_digit": center,
                    "center_value": center_value,
                    "base12": base12,
                    "decimal_value": value,
                    "base10_digital_root": root,
                    "base12_digit_sum": digit_sum,
                    "center_equals_decimal_root": "yes" if center_match else "no",
                    "base12_digit_sum_equals_12": "yes" if sum_match else "no",
                    "both_conditions": "yes" if center_match and sum_match else "no",
                    "standard_expressions": matching_expression_names(
                        expressions, "standard", base12
                    ),
                    "mispar_gadol_expressions": matching_expression_names(
                        expressions, "mispar-gadol", base12
                    ),
                    "outer_frame_base12": frame,
                    "standard_frame_expressions": matching_expression_names(
                        expressions, "standard", frame
                    ),
                    "mispar_gadol_frame_expressions": matching_expression_names(
                        expressions, "mispar-gadol", frame
                    ),
                }
            )
    return rows


def write_csv(path: Path, rows: list[object] | list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty output: {path}")
    if isinstance(rows[0], dict):
        fieldnames = list(rows[0].keys())
        records = rows
    else:
        fieldnames = list(rows[0].__dataclass_fields__)
        records = [
            {field: getattr(row, field) for field in fieldnames}
            for row in rows
        ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def md(value: str) -> str:
    return value.replace("|", "\\|")


def scope_membership(expression: Expression, scope: str) -> bool:
    if scope == "primary manuscript":
        return "manuscript" in expression.source_tables and "primary-biblical" in expression.layers
    if scope == "all manuscript":
        return "manuscript" in expression.source_tables
    if scope == "biblical expansion":
        return "primary-biblical-expansion" in expression.layers
    if scope == "Christian expansion":
        return "christian-comparative-expansion" in expression.layers
    if scope == "later expansion":
        return "later-traditional-expansion" in expression.layers
    if scope == "deduplicated union":
        return True
    raise ValueError(f"Unknown scope: {scope}")


def count_named_hosts_within_scope(
    expressions: list[Expression], hosts: list[HostRow], keys: set[str]
) -> int:
    expression_lookup = {expression.key: expression for expression in expressions}
    value_index: dict[tuple[str, str], set[str]] = {}
    for key in keys:
        expression = expression_lookup[key]
        for basis in BASIS_ORDER:
            value_index.setdefault(
                (basis, to_base(value_for(expression, basis))), set()
            ).add(key)

    count = 0
    for host in hosts:
        if host.expression_key not in keys:
            continue
        matches = value_index.get((host.basis, host.outer_frame), set()) - {
            host.expression_key
        }
        if matches:
            count += 1
    return count


def write_report(
    raw_rows: list[RawExpression],
    expressions: list[Expression],
    hosts: list[HostRow],
    displayed: list[DisplayedHost],
    differences: list[DifferenceRow],
    yhwh_scan: list[dict[str, object]],
    repeated_frame_scan: list[dict[str, object]],
) -> None:
    named_hosts = [row for row in hosts if row.named_frame_match == "yes"]
    yeshua_frame = [row for row in displayed if row.outer_frame == "22"]
    anchor_differences = [row for row in differences if row.anchor_hit == "yes"]
    both_yhwh = [row for row in yhwh_scan if row["both_conditions"] == "yes"]
    repeated_solutions = [
        row for row in repeated_frame_scan if row["both_conditions"] == "yes"
    ]

    lines = [
        "# Named-Frame Relation Audit Results",
        "",
        "This report is generated by `scripts/frame_relation_analysis.py` under the frozen rules in `docs/FRAME_RELATION_TEST_PROTOCOL.md`. The motivating `22_12`--`282_12` relation was known before the protocol, so every result remains exploratory.",
        "",
        "## Corpus Accounting",
        "",
        f"The input contains {len(raw_rows)} source rows: {sum(row.source_table == 'manuscript' for row in raw_rows)} manuscript rows and {sum(row.source_table == 'expansion' for row in raw_rows)} expansion rows. Exact name-and-form deduplication leaves {len(expressions)} expressions, so this input contains {len(raw_rows) - len(expressions)} exact cross-table duplicate(s). Source-record identities remain visible in `data/frame_relation_hosts.csv`.",
        "",
        "| Scope | Expressions | Eligible odd palindromes | Named-frame relations |",
        "| --- | ---: | ---: | ---: |",
    ]

    scopes = [
        "primary manuscript",
        "all manuscript",
        "biblical expansion",
        "Christian expansion",
        "later expansion",
        "deduplicated union",
    ]
    for scope in scopes:
        keys = {
            expression.key
            for expression in expressions
            if scope_membership(expression, scope)
        }
        scope_hosts = [row for row in hosts if row.expression_key in keys]
        scope_named_count = count_named_hosts_within_scope(expressions, hosts, keys)
        lines.append(
            f"| {scope} | {len(keys)} | {len(scope_hosts)} | {scope_named_count} |"
        )

    lines.extend(
        [
            "",
            "Counts are value-layer counts: an expression can contribute once under standard gematria and once under Mispar Gadol when both layers satisfy the rule. In each scope, both the host and the expression supplying its frame must belong to that scope.",
            "",
            "## Exact Named-Frame Relations",
            "",
            "| Host | Layer | Value | Base 12 | Center | Outer frame | Framed expression(s) | Decimal root | Center = root |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
        ]
    )
    for row in named_hosts:
        lines.append(
            f"| {md(row.name)} | {row.basis} | {row.value} | `{row.base12}` | `{row.center_digit}` | `{row.outer_frame}` | {md(row.framed_expressions)} | {row.base10_digital_root} | {row.self_center_match} |"
        )

    lines.extend(
        [
            "",
            "## Frame Families",
            "",
        ]
    )
    by_frame: dict[str, list[DisplayedHost]] = {}
    for host in displayed:
        by_frame.setdefault(host.outer_frame, []).append(host)
    for frame, members in sorted(by_frame.items()):
        framed = frame_expression_names(expressions, frame)
        lines.append(f"### Frame `{frame}`: {framed}")
        lines.append("")
        lines.append("| Host | Display | Center | Available basis layer(s) | Corpus layer(s) |")
        lines.append("| --- | ---: | ---: | --- | --- |")
        for member in sorted(members, key=lambda row: (row.value, row.name.casefold())):
            lines.append(
                f"| {md(member.name)} | `{member.base12}` | `{member.center_digit}` | {'; '.join(member.bases)} | {md(member.layers)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Pairwise Frame-Family Differences",
            "",
            "| Frame | Left | Right | Basis relation | Difference | Base 12 | Frozen-anchor hit |",
            "| ---: | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in differences:
        anchor = row.anchor_note if row.anchor_hit == "yes" else ""
        lines.append(
            f"| `{row.outer_frame}` | {md(row.left_name)} `{row.left_base12}` | {md(row.right_name)} `{row.right_base12}` | {row.comparison_type} | {row.decimal_difference} | `{row.base12_difference}` | {md(anchor)} |"
        )

    lines.extend(
        [
            "",
            "## Complete `2d2_12` Enumeration",
            "",
            "| Center | Base 12 | Decimal | Decimal root | Base-12 digit sum | Center = root | Sum = 12 | Both |",
            "| ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in yhwh_scan:
        lines.append(
            f"| `{row['center_digit']}` | `{row['base12']}` | {row['decimal_value']} | {row['base10_digital_root']} | {row['base12_digit_sum']} | {row['center_equals_decimal_root']} | {row['base12_digit_sum_equals_12']} | {row['both_conditions']} |"
        )

    lines.extend(
        [
            "",
            "## Complete Repeated-Frame Enumeration",
            "",
            "The outcome-aware extension in `docs/REPEATED_FRAME_CENTER_PROTOCOL.md` enumerates all 132 three-digit palindromes `ada_12` with a nonzero repeated outer digit. Exactly the following members have both a center equal to their decimal digital root and a base-12 digit sum of 12:",
            "",
            "| Base 12 | Decimal | Center/root | Outer frame | Admitted expression(s) | Named frame expression(s) |",
            "| ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in repeated_solutions:
        admitted = join_unique(
            [
                f"{row['standard_expressions']} [standard]"
                if row["standard_expressions"]
                else "",
                f"{row['mispar_gadol_expressions']} [mispar-gadol]"
                if row["mispar_gadol_expressions"]
                else "",
            ]
        )
        frames = join_unique(
            [
                f"{row['standard_frame_expressions']} [standard]"
                if row["standard_frame_expressions"]
                else "",
                f"{row['mispar_gadol_frame_expressions']} [mispar-gadol]"
                if row["mispar_gadol_frame_expressions"]
                else "",
            ]
        )
        lines.append(
            f"| `{row['base12']}` | {row['decimal_value']} | `{row['center_digit']}` | `{row['outer_frame_base12']}` | {md(admitted)} | {md(frames)} |"
        )

    lines.extend(
        [
            "",
            "### Why There Are Only Two",
            "",
            "Write a repeated-frame palindrome as `ada_12`, with numerical outer digit $a$ and center $d$. Its decimal value is",
            "",
            "$$N=145a+12d.$$",
            "",
            "The digit-sum condition gives $2a+d=12$, so $d=12-2a$. A positive decimal digital root equal to $d$ also requires $N\\equiv d\\pmod 9$. Since $N\\equiv a+3d\\pmod 9$, this becomes $a+2d\\equiv0\\pmod 9$. Substituting the digit-sum condition leaves $a\\equiv2\\pmod 3$. Within the valid digit range, only $a=2$ and $a=5$ remain, giving $d=8$ and $d=2$ respectively.",
            "",
            "The enumeration and the congruence therefore agree: the complete solution set is `282_12` and `525_12`.",
        ]
    )

    lines.extend(
        [
            "",
            "## Main Numerical Findings",
            "",
            f"- The complete union contains {len(hosts)} eligible odd-palindrome value layers, of which {len(named_hosts)} reproduce another admitted expression as an exact outer frame.",
            f"- The visible `22` family contains {len(yeshua_frame)} deduplicated host expressions: " + "; ".join(f"{row.name} `{row.base12}`" for row in yeshua_frame) + ".",
            f"- The finite YHWH-frame enumeration has {len(both_yhwh)} member satisfying both the self-center and digit-sum-12 conditions: " + "; ".join(f"`{row['base12']}` = {row['decimal_value']}" for row in both_yhwh) + ".",
            f"- Across all {len(repeated_frame_scan)} repeated-frame palindromes `ada_12`, exactly {len(repeated_solutions)} satisfy both conditions: " + "; ".join(f"`{row['base12']}` = {row['decimal_value']}" for row in repeated_solutions) + ". Both are occupied by admitted Yeshua expressions and both outer frames are complete admitted divine values.",
            f"- The frame families produce {len(differences)} pairwise displayed differences, of which {len(anchor_differences)} meet the frozen reference set.",
        ]
    )
    for row in anchor_differences:
        lines.append(
            f"- Frozen-anchor difference: {row.right_name} `{row.right_base12}` and {row.left_name} `{row.left_base12}` differ by {row.decimal_difference} (`{row.base12_difference}_12`), the existing {row.anchor_note} reference. This comparison is {row.comparison_type}."
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The audit shows whether the Yeshua observation belongs to a larger numeral-frame architecture. A shared frame is exact, and a complete center enumeration can establish uniqueness within its finite family. Neither result supplies a probability of theological intention.",
            "",
            "The same-basis relations are the cleanest comparisons. Mixed-basis-only family pairings remain visible because the manuscript treats both standard and Mispar Gadol results as declared layers, but they should not be described as though they came from one uniform calculation rule.",
            "",
            "Reader-facing integration is tracked in `docs/REVISION_QUEUE.md`. This report remains the technical source for the exact families, source layers, and failure cases.",
        ]
    )

    REPORT_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(
    expressions: list[Expression],
    hosts: list[HostRow],
    yhwh_scan: list[dict[str, object]],
    repeated_frame_scan: list[dict[str, object]],
) -> None:
    by_name = {expression.name: expression for expression in expressions}
    expected = {
        "YHWH": (26, "22"),
        "Shaddai": (314, "222"),
        "Yeshua": (386, "282"),
    }
    for name, (value, base12) in expected.items():
        expression = by_name[name]
        if expression.standard != value or to_base(expression.standard) != base12:
            raise ValueError(f"Known frame input changed for {name}")

    yeshua_hits = [
        row
        for row in hosts
        if row.name == "Yeshua"
        and row.basis == "standard"
        and row.outer_frame == "22"
        and row.framed_expressions == "YHWH"
    ]
    if len(yeshua_hits) != 1:
        raise ValueError("Known Yeshua--YHWH frame relation was not reproduced exactly")

    both = [row for row in yhwh_scan if row["both_conditions"] == "yes"]
    if len(both) != 1 or both[0]["center_digit"] != "8":
        raise ValueError("YHWH-frame center enumeration did not uniquely select 8")

    repeated_solutions = {
        row["base12"]
        for row in repeated_frame_scan
        if row["both_conditions"] == "yes"
    }
    if repeated_solutions != {"282", "525"}:
        raise ValueError(
            f"Repeated-frame solution set changed: {sorted(repeated_solutions)}"
        )


def main() -> None:
    raw_rows = read_master() + read_expansion()
    expressions = collapse_expressions(raw_rows)
    hosts = build_hosts(expressions)
    displayed = displayed_hosts(hosts)
    differences = build_differences(expressions, displayed)
    yhwh_scan = build_yhwh_scan()
    repeated_frame_scan = build_repeated_frame_scan(expressions)
    validate(expressions, hosts, yhwh_scan, repeated_frame_scan)
    write_csv(HOSTS_OUTPUT, hosts)
    write_csv(DIFFERENCES_OUTPUT, differences)
    write_csv(YHWH_SCAN_OUTPUT, yhwh_scan)
    write_csv(REPEATED_FRAME_SCAN_OUTPUT, repeated_frame_scan)
    write_report(
        raw_rows,
        expressions,
        hosts,
        displayed,
        differences,
        yhwh_scan,
        repeated_frame_scan,
    )
    print(
        f"Wrote {len(hosts)} eligible host layers, "
        f"{sum(row.named_frame_match == 'yes' for row in hosts)} named-frame relations, "
        f"and {len(differences)} frame-family differences."
    )


if __name__ == "__main__":
    main()
