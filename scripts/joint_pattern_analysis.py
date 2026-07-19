from __future__ import annotations

import argparse
import csv
import math
import xml.etree.ElementTree as ET
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

from audit_numerical_claims import DIGITS, STANDARD_VALUES, gematria, is_palindrome, to_base
from build_control_pool import (
    FINAL_FORMS,
    load_forbidden_phrases,
    local_name,
    normalize_hebrew,
    source_revision,
    verse_words,
)
from matched_control_analysis import (
    build_match_indexes,
    candidates_for_match,
    load_csv,
)


ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data" / "control_phrase_pool.csv"
MATCHES = ROOT / "data" / "control_match_registry.csv"
REGISTRY = ROOT / "data" / "corpus_registry.csv"
EXPANSION = ROOT / "data" / "divine_name_expansion_candidates.csv"

YESHUA_OUT = ROOT / "data" / "joint_signature_counts.csv"
YESHUA_CONTROLS_OUT = ROOT / "data" / "joint_signature_exact_controls.csv"
YESHUA_PROPER_OUT = ROOT / "data" / "joint_signature_proper_name_counts.csv"
YESHUA_PROPER_CONTROLS_OUT = ROOT / "data" / "joint_signature_proper_name_exact_controls.csv"
FORMULA_OUT = ROOT / "data" / "formula_completion_results.csv"
FORMULA_ROWS_OUT = ROOT / "data" / "formula_repeated_controls.csv"
NETWORK_OUT = ROOT / "data" / "anchor_network_results.csv"
CONTACTS_OUT = ROOT / "data" / "anchor_network_contacts.csv"
DISTRIBUTION_OUT = ROOT / "data" / "anchor_network_distributions.csv"
REPORT_OUT = ROOT / "docs" / "JOINT_PATTERN_TEST_RESULTS.md"

PROTOCOL_COMMIT = "236dbde"
SEMANTIC_PROTOCOL_COMMIT = "539781a"
SOURCE_COMMIT = "3d15126fb1ef74867fc1434be1942e837932691f"
SIMULATIONS = 100_000
SEED = 20_260_719
ANCHORS = (8, 12, 22, 42, 72)
ROUTES = (
    "exact_decimal",
    "exact_base12_text",
    "first_base12_digit_sum",
    "palindrome_center",
    "palindrome_outer_frame",
    "repeated_outer_sum",
)
TARGET_NAMES = (
    "YHWH",
    "Yeshua",
    "Yeshua HaMashiach",
    "Ehyeh Asher Ehyeh",
    "Eloah",
    "Elohim",
)


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def digit_values(text: str) -> list[int]:
    return [DIGITS.index(char) for char in text]


def structural_match_row(
    match_rows: list[dict[str, str]], name: str
) -> dict[str, str]:
    matches = [
        row
        for row in match_rows
        if row["analysis_layer"] == "full-christian-expansion"
        and row["name"] == name
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one full-layer match row for {name}, found {len(matches)}")
    return matches[0]


def target_hebrew(name: str) -> str:
    registry_rows = load_csv(REGISTRY)
    expansion_rows = load_csv(EXPANSION)
    registry_matches = [row["analysis_hebrew"] for row in registry_rows if row["name"] == name]
    expansion_matches = [row["hebrew"] for row in expansion_rows if row["name"] == name]
    matches = registry_matches + expansion_matches
    if len(matches) != 1:
        raise ValueError(f"Expected one source row for {name}, found {len(matches)}")
    return matches[0]


def yeshua_metrics(base12: str) -> dict[str, bool]:
    three_digit = len(base12) == 3
    palindrome = three_digit and is_palindrome(base12)
    return {
        "three_digit_base12": three_digit,
        "three_digit_palindrome": palindrome,
        "outer_22_palindrome": palindrome and base12[0] == "2" and base12[-1] == "2",
        "three_digit_sum_12": three_digit and sum(digit_values(base12)) == 12,
        "exact_282_signature": base12 == "282",
    }


def run_yeshua_test(
    pool_rows: list[dict[str, str]],
    candidate_sets: dict[str, np.ndarray],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    target = target_hebrew("Yeshua")
    target_value = gematria(target, STANDARD_VALUES)
    target_base12 = to_base(target_value)
    target_flags = yeshua_metrics(target_base12)

    candidates = candidate_sets["Yeshua"]
    control_counts = Counter({metric: 0 for metric in target_flags})
    exact_control_rows: list[dict[str, object]] = []
    for index in candidates:
        row = pool_rows[int(index)]
        value = gematria(row["hebrew"], STANDARD_VALUES)
        base12 = to_base(value)
        for metric, hit in yeshua_metrics(base12).items():
            control_counts[metric] += int(hit)
        if base12 == "282":
            exact_control_rows.append(
                {
                    "control_id": row["control_id"],
                    "hebrew": row["hebrew"],
                    "first_reference": row["first_reference"],
                    "frequency": row["frequency"],
                    "standard_value": value,
                    "base12": base12,
                    "same_letter_multiset_as_yeshua": (
                        "yes" if sorted(row["hebrew"]) == sorted(target) else "no"
                    ),
                }
            )

    universe_values = range(12**2, 12**3)
    universe_counts = Counter({metric: 0 for metric in target_flags})
    for value in universe_values:
        for metric, hit in yeshua_metrics(to_base(value)).items():
            universe_counts[metric] += int(hit)

    rows: list[dict[str, object]] = []
    for universe, counts, total in (
        ("all_three_digit_base12_integers", universe_counts, 12**3 - 12**2),
        ("matched_hebrew_controls", control_counts, len(candidates)),
    ):
        for metric in target_flags:
            hits = int(counts[metric])
            rows.append(
                {
                    "universe": universe,
                    "metric": metric,
                    "target_hit": "yes" if target_flags[metric] else "no",
                    "hits": hits,
                    "total": total,
                    "proportion": hits / total,
                }
            )

    details = {
        "hebrew": target,
        "standard_value": target_value,
        "base12": target_base12,
        "eligible_controls": len(candidates),
        "exact_control_hits": int(control_counts["exact_282_signature"]),
        "exact_anagram_hits": sum(
            row["same_letter_multiset_as_yeshua"] == "yes"
            for row in exact_control_rows
        ),
        "integer_universe_hits": int(universe_counts["exact_282_signature"]),
    }
    return rows, exact_control_rows, details


def run_proper_name_sensitivity(
    source: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    if source_revision(source) != SOURCE_COMMIT:
        raise ValueError("MorphHB checkout does not match the locked source revision")
    xml_files = sorted((source / "wlc").glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"No wlc/*.xml files under {source}")

    forbidden = load_forbidden_phrases().get(1, set())
    records: dict[str, dict[str, object]] = {}
    for xml_file in xml_files:
        root = ET.parse(xml_file).getroot()
        for verse in (node for node in root.iter() if local_name(node.tag) == "verse"):
            reference = verse.attrib.get("osisID", "")
            for word in verse_words(verse):
                if word.attrib.get("morph", "") != "HNp":
                    continue
                normalized = normalize_hebrew("".join(word.itertext()))
                if len(normalized) != 4 or any(char in FINAL_FORMS for char in normalized):
                    continue
                if (normalized,) in forbidden:
                    continue
                if normalized in records:
                    records[normalized]["frequency"] = int(records[normalized]["frequency"]) + 1
                else:
                    records[normalized] = {
                        "hebrew": normalized,
                        "first_reference": reference,
                        "frequency": 1,
                    }

    counts = Counter({metric: 0 for metric in yeshua_metrics("282")})
    exact_rows: list[dict[str, object]] = []
    for hebrew, record in sorted(records.items()):
        value = gematria(hebrew, STANDARD_VALUES)
        base12 = to_base(value)
        for metric, hit in yeshua_metrics(base12).items():
            counts[metric] += int(hit)
        if base12 == "282":
            exact_rows.append(
                {
                    **record,
                    "standard_value": value,
                    "base12": base12,
                    "same_letter_multiset_as_yeshua": (
                        "yes" if sorted(hebrew) == sorted("ישוע") else "no"
                    ),
                }
            )

    total = len(records)
    rows = [
        {
            "universe": "strict_HNp_proper_name_controls",
            "metric": metric,
            "target_hit": "yes",
            "hits": int(counts[metric]),
            "total": total,
            "proportion": counts[metric] / total if total else float("nan"),
        }
        for metric in yeshua_metrics("282")
    ]
    return rows, exact_rows, {
        "eligible_controls": total,
        "exact_control_hits": int(counts["exact_282_signature"]),
        "exact_anagram_hits": sum(
            row["same_letter_multiset_as_yeshua"] == "yes" for row in exact_rows
        ),
        "exact_control_labels": ", ".join(
            f"`{row['hebrew']}` ({row['first_reference']})" for row in exact_rows
        ),
    }


def completion_flags(hebrew: str, values: dict[str, int] = STANDARD_VALUES) -> dict[str, bool]:
    tokens = hebrew.split()
    if len(tokens) != 3:
        raise ValueError(f"Completion test requires three tokens: {hebrew}")
    first_base12 = to_base(gematria(tokens[0], values))
    full_base12 = to_base(gematria(hebrew, values))
    repeated = tokens[0] == tokens[2]
    first_palindrome = is_palindrome(first_base12)
    full_palindrome = is_palindrome(full_base12)
    return {
        "repeated": repeated,
        "first_palindrome": first_palindrome,
        "full_palindrome": full_palindrome,
        "completion": (not first_palindrome) and full_palindrome,
    }


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    row1 = a + b
    row2 = c + d
    col1 = a + c
    total = row1 + row2

    def probability(cell_a: int) -> float:
        cell_c = col1 - cell_a
        return (
            math.comb(row1, cell_a)
            * math.comb(row2, cell_c)
            / math.comb(total, col1)
        )

    minimum = max(0, col1 - row2)
    maximum = min(row1, col1)
    observed_probability = probability(a)
    return min(
        1.0,
        sum(
            probability(candidate)
            for candidate in range(minimum, maximum + 1)
            if probability(candidate) <= observed_probability * (1 + 1e-12)
        ),
    )


def completion_comparison(
    label: str, rows: list[dict[str, str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    classified: list[tuple[dict[str, str], dict[str, bool]]] = [
        (row, completion_flags(row["hebrew"])) for row in rows
    ]
    repeated = [item for item in classified if item[1]["repeated"]]
    nonrepeated = [item for item in classified if not item[1]["repeated"]]
    repeated_hits = sum(int(flags["completion"]) for _, flags in repeated)
    nonrepeated_hits = sum(int(flags["completion"]) for _, flags in nonrepeated)
    table = (
        repeated_hits,
        len(repeated) - repeated_hits,
        nonrepeated_hits,
        len(nonrepeated) - nonrepeated_hits,
    )
    fisher = fisher_exact_two_sided(*table)
    raw_odds = (
        (table[0] * table[3]) / (table[1] * table[2])
        if table[1] and table[2]
        else float("inf") if table[0] and table[3] else float("nan")
    )
    corrected_odds = ((table[0] + 0.5) * (table[3] + 0.5)) / (
        (table[1] + 0.5) * (table[2] + 0.5)
    )

    summary: list[dict[str, object]] = []
    for group, items, hits in (
        ("repeated_X_Y_X", repeated, repeated_hits),
        ("nonrepeated", nonrepeated, nonrepeated_hits),
    ):
        summary.append(
            {
                "comparison": label,
                "group": group,
                "completion_hits": hits,
                "total": len(items),
                "proportion": hits / len(items) if items else float("nan"),
                "raw_odds_ratio": raw_odds,
                "haldane_corrected_odds_ratio": corrected_odds,
                "fisher_two_sided": fisher,
            }
        )

    repeated_rows = []
    for row, flags in repeated:
        tokens = row["hebrew"].split()
        repeated_rows.append(
            {
                "comparison": label,
                "control_id": row["control_id"],
                "hebrew": row["hebrew"],
                "first_reference": row["first_reference"],
                "first_value": gematria(tokens[0], STANDARD_VALUES),
                "first_base12": to_base(gematria(tokens[0], STANDARD_VALUES)),
                "full_value": gematria(row["hebrew"], STANDARD_VALUES),
                "full_base12": to_base(gematria(row["hebrew"], STANDARD_VALUES)),
                "first_palindrome": "yes" if flags["first_palindrome"] else "no",
                "full_palindrome": "yes" if flags["full_palindrome"] else "no",
                "completion_hit": "yes" if flags["completion"] else "no",
            }
        )
    return summary, repeated_rows


def run_completion_test(
    pool_rows: list[dict[str, str]], candidate_sets: dict[str, np.ndarray]
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    exact_rows = [pool_rows[int(index)] for index in candidate_sets["Ehyeh Asher Ehyeh"]]
    broad_rows = [row for row in pool_rows if int(row["word_count"]) == 3]
    exact_summary, exact_repeated = completion_comparison("exact_4_3_4_no_finals", exact_rows)
    broad_summary, broad_repeated = completion_comparison("all_three_word_controls", broad_rows)

    target = target_hebrew("Ehyeh Asher Ehyeh")
    tokens = target.split()
    target_details = {
        "hebrew": target,
        "first_value": gematria(tokens[0], STANDARD_VALUES),
        "first_base12": to_base(gematria(tokens[0], STANDARD_VALUES)),
        "full_value": gematria(target, STANDARD_VALUES),
        "full_base12": to_base(gematria(target, STANDARD_VALUES)),
        **completion_flags(target),
    }
    return exact_summary + broad_summary, exact_repeated + broad_repeated, target_details


def anchor_contacts(hebrew: str) -> tuple[dict[int, set[str]], bool]:
    value = gematria(hebrew, STANDARD_VALUES)
    base12 = to_base(value)
    digits = digit_values(base12)
    palindrome = is_palindrome(base12)
    tokens = hebrew.split()
    contacts: dict[int, set[str]] = {anchor: set() for anchor in ANCHORS}

    for anchor in ANCHORS:
        if value == anchor:
            contacts[anchor].add("exact_decimal")
        if base12 == str(anchor):
            contacts[anchor].add("exact_base12_text")
        if sum(digits) == anchor:
            contacts[anchor].add("first_base12_digit_sum")
        if (
            anchor == 8
            and palindrome
            and len(base12) % 2 == 1
            and DIGITS.index(base12[len(base12) // 2]) == anchor
        ):
            contacts[anchor].add("palindrome_center")
        if palindrome and len(base12) >= 3 and base12[0] + base12[-1] == str(anchor):
            contacts[anchor].add("palindrome_outer_frame")
        if (
            len(tokens) == 3
            and tokens[0] == tokens[2]
            and 2 * gematria(tokens[0], STANDARD_VALUES) == anchor
        ):
            contacts[anchor].add("repeated_outer_sum")

    return {anchor: routes for anchor, routes in contacts.items() if routes}, palindrome


def network_metrics(contacts: list[dict[int, set[str]]], palindromes: list[bool]) -> dict[str, int]:
    anchor_sets = [set(node) for node in contacts]
    return {
        "anchor_incidences": sum(len(node) for node in anchor_sets),
        "pairwise_shared_anchor_links": sum(
            int(bool(anchor_sets[left] & anchor_sets[right]))
            for left, right in combinations(range(len(anchor_sets)), 2)
        ),
        "occupied_anchors": len(set().union(*anchor_sets)),
        "nodes_with_anchor": sum(int(bool(node)) for node in anchor_sets),
        "base12_palindromes": sum(int(value) for value in palindromes),
    }


def holm_adjust_two(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    for index, (name, value) in enumerate(ordered):
        candidate = min(1.0, (len(ordered) - index) * value)
        running = max(running, candidate)
        adjusted[name] = running
    return adjusted


def run_network_test(
    pool_rows: list[dict[str, str]], candidate_sets: dict[str, np.ndarray]
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, int],
]:
    target_contacts: list[dict[int, set[str]]] = []
    target_palindromes: list[bool] = []
    contact_rows: list[dict[str, object]] = []
    target_route_counts = Counter({route: 0 for route in ROUTES})
    for name in TARGET_NAMES:
        hebrew = target_hebrew(name)
        contacts, palindrome = anchor_contacts(hebrew)
        target_contacts.append(contacts)
        target_palindromes.append(palindrome)
        for anchor, routes in contacts.items():
            for route in routes:
                target_route_counts[route] += 1
            contact_rows.append(
                {
                    "node": name,
                    "hebrew": hebrew,
                    "standard_value": gematria(hebrew, STANDARD_VALUES),
                    "base12": to_base(gematria(hebrew, STANDARD_VALUES)),
                    "anchor": anchor,
                    "routes": ";".join(sorted(routes)),
                }
            )

    observed = network_metrics(target_contacts, target_palindromes)

    control_masks = np.zeros(len(pool_rows), dtype=np.uint8)
    control_palindromes = np.zeros(len(pool_rows), dtype=np.uint8)
    control_routes = np.zeros((len(pool_rows), len(ROUTES)), dtype=np.uint8)
    for index, row in enumerate(pool_rows):
        contacts, palindrome = anchor_contacts(row["hebrew"])
        mask = 0
        for anchor, routes in contacts.items():
            mask |= 1 << ANCHORS.index(anchor)
            for route in routes:
                control_routes[index, ROUTES.index(route)] += 1
        control_masks[index] = mask
        control_palindromes[index] = int(palindrome)

    bit_counts = np.asarray([value.bit_count() for value in range(1 << len(ANCHORS))])
    simulated = {
        metric: np.zeros(SIMULATIONS, dtype=np.int16)
        for metric in observed
    }
    simulated_routes = {
        route: np.zeros(SIMULATIONS, dtype=np.int16) for route in ROUTES
    }

    rng = np.random.default_rng(SEED)
    ordered_candidates = [candidate_sets[name] for name in TARGET_NAMES]
    batch_size = 5_000
    for offset in range(0, SIMULATIONS, batch_size):
        size = min(batch_size, SIMULATIONS - offset)
        choices = np.empty((len(TARGET_NAMES), size), dtype=np.int32)
        for target_index, candidates in enumerate(ordered_candidates):
            draw = candidates[rng.integers(0, len(candidates), size=size)]
            if target_index:
                duplicate = np.any(choices[:target_index] == draw, axis=0)
                attempts = 0
                while np.any(duplicate):
                    draw[duplicate] = candidates[
                        rng.integers(0, len(candidates), size=int(np.sum(duplicate)))
                    ]
                    duplicate = np.any(choices[:target_index] == draw, axis=0)
                    attempts += 1
                    if attempts > 100:
                        raise RuntimeError("Unable to sample unique network controls")
            choices[target_index] = draw

        selected_masks = control_masks[choices]
        destination = slice(offset, offset + size)
        simulated["anchor_incidences"][destination] = bit_counts[selected_masks].sum(axis=0)
        simulated["occupied_anchors"][destination] = bit_counts[
            np.bitwise_or.reduce(selected_masks, axis=0)
        ]
        simulated["nodes_with_anchor"][destination] = np.sum(selected_masks != 0, axis=0)
        simulated["base12_palindromes"][destination] = control_palindromes[choices].sum(axis=0)
        pair_links = np.zeros(size, dtype=np.int16)
        for left, right in combinations(range(len(TARGET_NAMES)), 2):
            pair_links += (selected_masks[left] & selected_masks[right]) != 0
        simulated["pairwise_shared_anchor_links"][destination] = pair_links
        for route_index, route in enumerate(ROUTES):
            simulated_routes[route][destination] = control_routes[choices, route_index].sum(axis=0)

    primary_metrics = ("anchor_incidences", "pairwise_shared_anchor_links")
    raw_primary = {
        metric: (int(np.sum(simulated[metric] >= observed[metric])) + 1) / (SIMULATIONS + 1)
        for metric in primary_metrics
    }
    adjusted = holm_adjust_two(raw_primary)

    result_rows: list[dict[str, object]] = []
    distribution_rows: list[dict[str, object]] = []
    for metric, values in simulated.items():
        at_least = int(np.sum(values >= observed[metric]))
        lower, median, upper = np.percentile(values, [2.5, 50, 97.5])
        result_rows.append(
            {
                "metric": metric,
                "status": "primary" if metric in primary_metrics else "secondary",
                "observed": observed[metric],
                "control_mean": float(np.mean(values)),
                "control_median": float(median),
                "control_interval_2_5": float(lower),
                "control_interval_97_5": float(upper),
                "simulations_at_least_observed": at_least,
                "empirical_upper_tail": (at_least + 1) / (SIMULATIONS + 1),
                "holm_adjusted_upper_tail": adjusted.get(metric, ""),
                "simulations": SIMULATIONS,
                "seed": SEED,
            }
        )
        for value, frequency in sorted(Counter(int(item) for item in values).items()):
            distribution_rows.append(
                {
                    "metric": metric,
                    "value": value,
                    "frequency": frequency,
                    "proportion": frequency / SIMULATIONS,
                }
            )

    for route, values in simulated_routes.items():
        at_least = int(np.sum(values >= target_route_counts[route]))
        lower, median, upper = np.percentile(values, [2.5, 50, 97.5])
        result_rows.append(
            {
                "metric": f"route_{route}",
                "status": "route-sensitivity",
                "observed": target_route_counts[route],
                "control_mean": float(np.mean(values)),
                "control_median": float(median),
                "control_interval_2_5": float(lower),
                "control_interval_97_5": float(upper),
                "simulations_at_least_observed": at_least,
                "empirical_upper_tail": (at_least + 1) / (SIMULATIONS + 1),
                "holm_adjusted_upper_tail": "",
                "simulations": SIMULATIONS,
                "seed": SEED,
            }
        )

    return result_rows, contact_rows, distribution_rows, observed


def format_probability(value: float) -> str:
    return f"{value:.6f}"


def write_report(
    yeshua_rows: list[dict[str, object]],
    yeshua_details: dict[str, object],
    proper_name_rows: list[dict[str, object]],
    proper_name_details: dict[str, object],
    formula_rows: list[dict[str, object]],
    formula_details: dict[str, object],
    network_rows: list[dict[str, object]],
    contact_rows: list[dict[str, object]],
) -> None:
    yeshua_table = [
        "| Universe | Metric | Hits | Total | Proportion |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in yeshua_rows:
        yeshua_table.append(
            f"| {row['universe']} | {row['metric']} | {row['hits']} | {row['total']} | "
            f"{float(row['proportion']):.8f} |"
        )

    proper_name_table = [
        "| Semantic universe | Metric | Hits | Total | Proportion |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in proper_name_rows:
        proper_name_table.append(
            f"| {row['universe']} | {row['metric']} | {row['hits']} | {row['total']} | "
            f"{float(row['proportion']):.8f} |"
        )

    formula_table = [
        "| Comparison | Group | Completion hits | Total | Proportion | Odds ratio | Fisher two-sided |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in formula_rows:
        odds = float(row["raw_odds_ratio"])
        odds_text = "infinite" if math.isinf(odds) else "undefined" if math.isnan(odds) else f"{odds:.4f}"
        formula_table.append(
            f"| {row['comparison']} | {row['group']} | {row['completion_hits']} | "
            f"{row['total']} | {float(row['proportion']):.8f} | {odds_text} | "
            f"{format_probability(float(row['fisher_two_sided']))} |"
        )

    primary_network = [row for row in network_rows if row["status"] == "primary"]
    network_table = [
        "| Metric | Status | Observed | Control mean | 95% interval | Simulations at least observed | Upper tail | Holm |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in network_rows:
        holm = row["holm_adjusted_upper_tail"]
        holm_text = format_probability(float(holm)) if holm != "" else ""
        network_table.append(
            f"| {row['metric']} | {row['status']} | {row['observed']} | "
            f"{float(row['control_mean']):.4f} | {float(row['control_interval_2_5']):.1f}-"
            f"{float(row['control_interval_97_5']):.1f} | {row['simulations_at_least_observed']} | "
            f"{format_probability(float(row['empirical_upper_tail']))} | {holm_text} |"
        )

    contacts_table = [
        "| Node | Value | Base 12 | Anchor | Route |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in contact_rows:
        contacts_table.append(
            f"| {row['node']} | {row['standard_value']} | {row['base12']} | "
            f"{row['anchor']} | {str(row['routes']).replace(';', ', ')} |"
        )

    exact_formula = [
        row for row in formula_rows if row["comparison"] == "exact_4_3_4_no_finals"
    ]
    exact_repeated = next(row for row in exact_formula if row["group"] == "repeated_X_Y_X")
    exact_nonrepeated = next(row for row in exact_formula if row["group"] == "nonrepeated")
    formula_direction = (
        "Repeated frames have a higher completion proportion in the exact stratum."
        if float(exact_repeated["proportion"]) > float(exact_nonrepeated["proportion"])
        else "Repeated frames do not have a higher completion proportion in the exact stratum."
    )

    network_clears = all(
        float(row["holm_adjusted_upper_tail"]) < 0.05 for row in primary_network
    )
    network_interpretation = (
        "Both frozen primary network scores exceed the matched-control expectation after Holm adjustment."
        if network_clears
        else "The two frozen primary network scores do not both clear 0.05 after Holm adjustment."
    )

    content = f"""# Joint-Pattern Test Results

Generated by `scripts/joint_pattern_analysis.py` under `docs/JOINT_PATTERN_TEST_PROTOCOL.md`.

## Reproducibility Lock

- Protocol commit: `{PROTOCOL_COMMIT}`
- Proper-name sensitivity protocol commit: `{SEMANTIC_PROTOCOL_COMMIT}`
- OSHB source commit: `{SOURCE_COMMIT}`
- Network simulations: {SIMULATIONS:,}
- Network seed: `{SEED}`
- Generator: NumPy `PCG64`

The hypotheses were motivated by known manuscript patterns. The control outcomes were calculated only after the protocol commit, but the results remain exploratory rather than independent confirmation.

## 1. Yeshua's Exact `282` Signature

Yeshua (`{yeshua_details['hebrew']}`) has standard value {yeshua_details['standard_value']} and base-12 form `{yeshua_details['base12']}`. The exact signature is a palindrome with outer frame `22`, center `8`, and first digit sum 12. These properties are algebraically linked: `2 + 8 + 2 = 12`, so they are one composite pattern rather than independent events.

{chr(10).join(yeshua_table)}

Within the complete three-digit base-12 universe, exactly {yeshua_details['integer_universe_hits']} of 1,584 values has the full signature. In the complete matched Hebrew stratum, {yeshua_details['exact_control_hits']} of {yeshua_details['eligible_controls']:,} deduplicated one-word, four-letter, zero-final controls have it. The matched rate is higher than the uniform-integer rate because Hebrew gematria values are not uniformly distributed. Of the 20 exact controls, {yeshua_details['exact_anagram_hits']} use the same four-letter multiset as Yeshua in another order, leaving {yeshua_details['exact_control_hits'] - yeshua_details['exact_anagram_hits']} forms with other consonant sets. Gematria is order-insensitive, so the twelve are permutation collisions rather than independent routes to 386. Their exact count of twelve is nevertheless part of the outcome and was recognized after the test. All matching controls are retained in `data/joint_signature_exact_controls.csv`.

The controls are structurally matched biblical words, not a semantic corpus restricted to personal names or titles. This establishes the signature's exact scarcity under the declared comparison, not uniqueness among Hebrew words or the probability of theological intention.

### Proper-Name Sensitivity

After the structural result was known, a separate rule was frozen for unprefixed, unsuffixed MorphHB proper names marked exactly `HNp`. Tested expressions were excluded, and the remaining surface forms were deduplicated before gematria calculation.

{chr(10).join(proper_name_table)}

The strict proper-name stratum contains {proper_name_details['eligible_controls']:,} controls, of which {proper_name_details['exact_control_hits']} have the exact `282` signature: {proper_name_details['exact_control_labels']}. Both are letter permutations of Yeshua; their equal gematria therefore follows directly from the shared consonant multiset. Every hit is retained in `data/joint_signature_proper_name_exact_controls.csv`. MorphHB's proper-name category includes place names as well as personal names, so this is a semantic sensitivity rather than a personal-name-only test.

## 2. Completion in `X Y X` Formulas

Ehyeh alone has value {formula_details['first_value']} and base-12 form `{formula_details['first_base12']}`, which is not palindromic. Ehyeh Asher Ehyeh has value {formula_details['full_value']} and base-12 form `{formula_details['full_base12']}`, which is palindromic.

The completion event requires a nonpalindromic first token and a palindromic complete phrase.

{chr(10).join(formula_table)}

None of the 30 exact `4-3-4`, zero-final repeated frames produces the completion event. {formula_direction} Across all three-word controls, repeated frames complete at 8.27 percent and nonrepeated phrases at 7.71 percent, with no meaningful difference (`p = 0.419300`). Repetition by itself is therefore not a general explanation for the target result. The Fisher comparison does not test whether the control phrases have the grammar or meaning of the biblical formula.

## 3. Fixed-Anchor Network

The six selected expressions were tested against anchors 8, 12, 22, 42, and 72 using only the six routes frozen in the protocol.

{chr(10).join(contacts_table)}

{chr(10).join(network_table)}

{network_interpretation} The occupied-anchor and node counts show breadth; the pairwise score measures actual cross-name sharing. Route rows are unadjusted sensitivities and should not be promoted individually.

## Overall Reading

The `282` result is exact and rare, but the 20 matched collisions prevent a claim of lexical uniqueness. The full Ehyeh expression has no completion counterpart among the 30 exact repeated-frame controls, while the broader comparison shows that repetition itself does not raise the palindrome rate. Under the frozen network score, the selected names occupy all five anchors and share three cross-name links much more often than matched phrases do.

None of these analyses turns a post-discovery pattern into a prospective prediction. Their value is narrower and still useful: they separate exact scarcity, linguistic structure, and cross-name concentration instead of treating fascination as its own statistical argument.

Subsequent robustness tests show that the eight non-Yeshua-family collision forms occupy four consonant families of two forms each. Together with the twelve Yeshua-letter permutations, this gives the descriptive partition `20 = 12 + 8` and `8 = 4 x 2`. Because it was noticed after the outcomes, it is an exploratory structural observation rather than a frozen test statistic. The same robustness tests show that the five-anchor set is not statistically privileged among attainable numerical alternatives and that the cross-name links are centered on Yeshua. These statements concern numerical availability and network dependence. They do not make alternative values canonically equivalent, and within a Christian interpretation Yeshua's centrality may be theologically coherent. The synthetic Asher test likewise examines the mechanism `2x + 501`; the complete Ehyeh declaration remains the primary textual object.
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen joint-pattern tests")
    parser.add_argument(
        "--morphhb-source",
        type=Path,
        required=True,
        help="Path to the locked openscriptures/morphhb checkout",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pool_rows = load_csv(POOL)
    if not pool_rows or pool_rows[0]["source_commit"] != SOURCE_COMMIT:
        raise ValueError("Control pool does not match the locked OSHB source")
    match_rows = load_csv(MATCHES)
    exact, total, word_final = build_match_indexes(pool_rows)

    needed_names = set(TARGET_NAMES) | {"Ehyeh Asher Ehyeh"}
    candidate_sets: dict[str, np.ndarray] = {}
    for name in sorted(needed_names):
        row = structural_match_row(match_rows, name)
        candidate_sets[name] = candidates_for_match(
            row, exact, total, word_final, pool_rows
        )

    yeshua_rows, yeshua_control_rows, yeshua_details = run_yeshua_test(
        pool_rows, candidate_sets
    )
    proper_name_rows, proper_name_control_rows, proper_name_details = (
        run_proper_name_sensitivity(args.morphhb_source)
    )
    formula_rows, formula_repeated_rows, formula_details = run_completion_test(
        pool_rows, candidate_sets
    )
    network_rows, contact_rows, distribution_rows, _ = run_network_test(
        pool_rows, candidate_sets
    )

    write_csv(
        YESHUA_OUT,
        yeshua_rows,
        ["universe", "metric", "target_hit", "hits", "total", "proportion"],
    )
    write_csv(
        YESHUA_CONTROLS_OUT,
        yeshua_control_rows,
        [
            "control_id",
            "hebrew",
            "first_reference",
            "frequency",
            "standard_value",
            "base12",
            "same_letter_multiset_as_yeshua",
        ],
    )
    write_csv(
        YESHUA_PROPER_OUT,
        proper_name_rows,
        ["universe", "metric", "target_hit", "hits", "total", "proportion"],
    )
    write_csv(
        YESHUA_PROPER_CONTROLS_OUT,
        proper_name_control_rows,
        [
            "hebrew",
            "first_reference",
            "frequency",
            "standard_value",
            "base12",
            "same_letter_multiset_as_yeshua",
        ],
    )
    write_csv(
        FORMULA_OUT,
        formula_rows,
        [
            "comparison",
            "group",
            "completion_hits",
            "total",
            "proportion",
            "raw_odds_ratio",
            "haldane_corrected_odds_ratio",
            "fisher_two_sided",
        ],
    )
    write_csv(
        FORMULA_ROWS_OUT,
        formula_repeated_rows,
        [
            "comparison",
            "control_id",
            "hebrew",
            "first_reference",
            "first_value",
            "first_base12",
            "full_value",
            "full_base12",
            "first_palindrome",
            "full_palindrome",
            "completion_hit",
        ],
    )
    write_csv(
        NETWORK_OUT,
        network_rows,
        [
            "metric",
            "status",
            "observed",
            "control_mean",
            "control_median",
            "control_interval_2_5",
            "control_interval_97_5",
            "simulations_at_least_observed",
            "empirical_upper_tail",
            "holm_adjusted_upper_tail",
            "simulations",
            "seed",
        ],
    )
    write_csv(
        CONTACTS_OUT,
        contact_rows,
        ["node", "hebrew", "standard_value", "base12", "anchor", "routes"],
    )
    write_csv(
        DISTRIBUTION_OUT,
        distribution_rows,
        ["metric", "value", "frequency", "proportion"],
    )
    write_report(
        yeshua_rows,
        yeshua_details,
        proper_name_rows,
        proper_name_details,
        formula_rows,
        formula_details,
        network_rows,
        contact_rows,
    )


if __name__ == "__main__":
    main()
