from __future__ import annotations

import csv
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

from audit_numerical_claims import DIGITS, STANDARD_VALUES, gematria, is_palindrome, to_base
from joint_pattern_analysis import (
    ANCHORS,
    ROUTES,
    SEED,
    SIMULATIONS,
    SOURCE_COMMIT,
    TARGET_NAMES,
    completion_flags,
    structural_match_row,
    target_hebrew,
)
from matched_control_analysis import (
    build_match_indexes,
    candidates_for_match,
    load_csv,
)


ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data" / "control_phrase_pool.csv"
MATCHES = ROOT / "data" / "control_match_registry.csv"
BASELINE_RESULTS = ROOT / "data" / "anchor_network_results.csv"
ROBUSTNESS_OUT = ROOT / "data" / "network_robustness_results.csv"
PLACEBO_OUT = ROOT / "data" / "network_placebo_anchor_sets.csv"
FAMILY_SUMMARY_OUT = ROOT / "data" / "yeshua_consonant_family_results.csv"
FAMILY_EXACT_OUT = ROOT / "data" / "yeshua_consonant_exact_families.csv"
ASHER_SUMMARY_OUT = ROOT / "data" / "asher_formula_results.csv"
ASHER_ATTESTED_OUT = ROOT / "data" / "asher_formula_attested_controls.csv"
ASHER_SYNTHETIC_OUT = ROOT / "data" / "asher_formula_synthetic_hits.csv"
REPORT_OUT = ROOT / "docs" / "ROBUSTNESS_TEST_RESULTS.md"

PROTOCOL_COMMIT = "3f595c5"
PRIMARY_METRICS = ("anchor_incidences", "pairwise_shared_anchor_links")
ALL_METRICS = (
    "anchor_incidences",
    "pairwise_shared_anchor_links",
    "occupied_anchors",
    "nodes_with_anchor",
    "base12_palindromes",
)
BIT_COUNTS = np.asarray([value.bit_count() for value in range(1 << len(ANCHORS))])


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def numeric_text(text: str) -> int | None:
    return int(text) if text and all(char.isdigit() for char in text) else None


def route_output_values(hebrew: str) -> dict[str, set[int]]:
    value = gematria(hebrew, STANDARD_VALUES)
    base12 = to_base(value)
    digit_values = [DIGITS.index(char) for char in base12]
    palindrome = is_palindrome(base12)
    tokens = hebrew.split()
    outputs = {route: set() for route in ROUTES}

    outputs["exact_decimal"].add(value)
    if (parsed := numeric_text(base12)) is not None:
        outputs["exact_base12_text"].add(parsed)
    outputs["first_base12_digit_sum"].add(sum(digit_values))
    if palindrome and len(base12) % 2 == 1:
        outputs["palindrome_center"].add(DIGITS.index(base12[len(base12) // 2]))
    if palindrome and len(base12) >= 3:
        if (parsed := numeric_text(base12[0] + base12[-1])) is not None:
            outputs["palindrome_outer_frame"].add(parsed)
    if len(tokens) == 3 and tokens[0] == tokens[2]:
        outputs["repeated_outer_sum"].add(2 * gematria(tokens[0], STANDARD_VALUES))
    return outputs


def route_masks_for_anchors(hebrew: str, anchors: tuple[int, ...]) -> np.ndarray:
    masks = np.zeros(len(ROUTES), dtype=np.uint8)
    outputs = route_output_values(hebrew)
    anchor_index = {anchor: index for index, anchor in enumerate(anchors)}
    for route_index, route in enumerate(ROUTES):
        for value in outputs[route]:
            if value in anchor_index:
                masks[route_index] |= 1 << anchor_index[value]
    return masks


def union_route_masks(route_masks: np.ndarray, omit_route: int | None = None) -> np.ndarray:
    if omit_route is None:
        return np.bitwise_or.reduce(route_masks, axis=-1)
    retained = [index for index in range(len(ROUTES)) if index != omit_route]
    return np.bitwise_or.reduce(route_masks[..., retained], axis=-1)


def observed_metrics(masks: np.ndarray, palindromes: np.ndarray) -> dict[str, int]:
    return {
        "anchor_incidences": int(BIT_COUNTS[masks].sum()),
        "pairwise_shared_anchor_links": sum(
            int(bool(int(masks[left]) & int(masks[right])))
            for left, right in combinations(range(len(masks)), 2)
        ),
        "occupied_anchors": int(BIT_COUNTS[np.bitwise_or.reduce(masks)]),
        "nodes_with_anchor": int(np.sum(masks != 0)),
        "base12_palindromes": int(np.sum(palindromes)),
    }


def simulated_metrics(masks: np.ndarray, palindromes: np.ndarray) -> dict[str, np.ndarray]:
    pair_links = np.zeros(masks.shape[1], dtype=np.int16)
    for left, right in combinations(range(masks.shape[0]), 2):
        pair_links += (masks[left] & masks[right]) != 0
    return {
        "anchor_incidences": BIT_COUNTS[masks].sum(axis=0).astype(np.int16),
        "pairwise_shared_anchor_links": pair_links,
        "occupied_anchors": BIT_COUNTS[np.bitwise_or.reduce(masks, axis=0)].astype(np.int16),
        "nodes_with_anchor": np.sum(masks != 0, axis=0).astype(np.int16),
        "base12_palindromes": np.sum(palindromes, axis=0).astype(np.int16),
    }


def generate_choices(candidate_sets: list[np.ndarray]) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    choices = np.empty((len(candidate_sets), SIMULATIONS), dtype=np.int32)
    batch_size = 5_000
    for offset in range(0, SIMULATIONS, batch_size):
        size = min(batch_size, SIMULATIONS - offset)
        batch = np.empty((len(candidate_sets), size), dtype=np.int32)
        for target_index, candidates in enumerate(candidate_sets):
            draw = candidates[rng.integers(0, len(candidates), size=size)]
            if target_index:
                duplicate = np.any(batch[:target_index] == draw, axis=0)
                attempts = 0
                while np.any(duplicate):
                    draw[duplicate] = candidates[
                        rng.integers(0, len(candidates), size=int(np.sum(duplicate)))
                    ]
                    duplicate = np.any(batch[:target_index] == draw, axis=0)
                    attempts += 1
                    if attempts > 100:
                        raise RuntimeError("Unable to sample unique robustness controls")
            batch[target_index] = draw
        choices[:, offset : offset + size] = batch
    return choices


def holm_adjust(rows: list[dict[str, object]]) -> None:
    primary = [row for row in rows if row["metric"] in PRIMARY_METRICS]
    ordered = sorted(primary, key=lambda row: float(row["empirical_upper_tail"]))
    running = 0.0
    count = len(ordered)
    for index, row in enumerate(ordered):
        candidate = min(1.0, (count - index) * float(row["empirical_upper_tail"]))
        running = max(running, candidate)
        row["holm_adjusted_upper_tail"] = running


def result_rows_for_scenario(
    scenario_type: str,
    omitted: str,
    target_masks: np.ndarray,
    target_palindromes: np.ndarray,
    control_masks: np.ndarray,
    control_palindromes: np.ndarray,
    include_secondary: bool,
) -> list[dict[str, object]]:
    observed = observed_metrics(target_masks, target_palindromes)
    simulated = simulated_metrics(control_masks, control_palindromes)
    metrics = ALL_METRICS if include_secondary else PRIMARY_METRICS
    rows = []
    for metric in metrics:
        values = simulated[metric]
        at_least = int(np.sum(values >= observed[metric]))
        lower, median, upper = np.percentile(values, [2.5, 50, 97.5])
        rows.append(
            {
                "scenario_type": scenario_type,
                "omitted": omitted,
                "metric": metric,
                "status": "robustness-primary" if metric in PRIMARY_METRICS else "secondary",
                "observed": observed[metric],
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
    return rows


def validate_baseline(rows: list[dict[str, object]]) -> None:
    committed = {
        row["metric"]: row for row in load_csv(BASELINE_RESULTS) if row["status"] == "primary"
    }
    generated = {row["metric"]: row for row in rows if row["metric"] in PRIMARY_METRICS}
    for metric in PRIMARY_METRICS:
        if int(generated[metric]["observed"]) != int(committed[metric]["observed"]):
            raise ValueError(f"Baseline observed metric changed for {metric}")
        if int(generated[metric]["simulations_at_least_observed"]) != int(
            committed[metric]["simulations_at_least_observed"]
        ):
            raise ValueError(f"Baseline simulation sequence changed for {metric}")
        if not np.isclose(
            float(generated[metric]["control_mean"]),
            float(committed[metric]["control_mean"]),
        ):
            raise ValueError(f"Baseline control mean changed for {metric}")


def run_robustness_networks(
    pool_rows: list[dict[str, str]], candidate_sets: dict[str, np.ndarray]
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    pool_routes = np.zeros((len(pool_rows), len(ROUTES)), dtype=np.uint8)
    pool_palindromes = np.zeros(len(pool_rows), dtype=np.uint8)
    for index, row in enumerate(pool_rows):
        pool_routes[index] = route_masks_for_anchors(row["hebrew"], ANCHORS)
        pool_palindromes[index] = int(
            is_palindrome(to_base(gematria(row["hebrew"], STANDARD_VALUES)))
        )

    target_routes = np.asarray(
        [route_masks_for_anchors(target_hebrew(name), ANCHORS) for name in TARGET_NAMES],
        dtype=np.uint8,
    )
    target_palindromes = np.asarray(
        [
            int(is_palindrome(to_base(gematria(target_hebrew(name), STANDARD_VALUES))))
            for name in TARGET_NAMES
        ],
        dtype=np.uint8,
    )

    choices = generate_choices([candidate_sets[name] for name in TARGET_NAMES])
    selected_routes = pool_routes[choices]
    selected_palindromes = pool_palindromes[choices]
    baseline_target_masks = union_route_masks(target_routes)
    baseline_control_masks = union_route_masks(selected_routes)

    all_rows = result_rows_for_scenario(
        "baseline",
        "none",
        baseline_target_masks,
        target_palindromes,
        baseline_control_masks,
        selected_palindromes,
        True,
    )
    validate_baseline(all_rows)

    node_rows: list[dict[str, object]] = []
    for omitted_index, name in enumerate(TARGET_NAMES):
        retained = [index for index in range(len(TARGET_NAMES)) if index != omitted_index]
        node_rows.extend(
            result_rows_for_scenario(
                "leave_one_node_out",
                name,
                baseline_target_masks[retained],
                target_palindromes[retained],
                baseline_control_masks[retained],
                selected_palindromes[retained],
                True,
            )
        )
    holm_adjust(node_rows)
    all_rows.extend(node_rows)

    anchor_rows: list[dict[str, object]] = []
    for anchor_index, anchor in enumerate(ANCHORS):
        keep_mask = np.uint8(((1 << len(ANCHORS)) - 1) ^ (1 << anchor_index))
        anchor_rows.extend(
            result_rows_for_scenario(
                "leave_one_anchor_out",
                str(anchor),
                baseline_target_masks & keep_mask,
                target_palindromes,
                baseline_control_masks & keep_mask,
                selected_palindromes,
                False,
            )
        )
    holm_adjust(anchor_rows)
    all_rows.extend(anchor_rows)

    route_rows: list[dict[str, object]] = []
    for route_index, route in enumerate(ROUTES):
        route_rows.extend(
            result_rows_for_scenario(
                "leave_one_route_out",
                route,
                union_route_masks(target_routes, route_index),
                target_palindromes,
                union_route_masks(selected_routes, route_index),
                selected_palindromes,
                False,
            )
        )
    holm_adjust(route_rows)
    all_rows.extend(route_rows)

    placebo_rows, placebo_details = run_placebo_anchors()
    return all_rows, placebo_rows, placebo_details


def contacts_for_anchor_set(outputs: dict[str, set[int]], anchors: set[int]) -> set[int]:
    return set().union(*(values & anchors for values in outputs.values()))


def run_placebo_anchors() -> tuple[list[dict[str, object]], dict[str, object]]:
    target_outputs = {
        name: route_output_values(target_hebrew(name)) for name in TARGET_NAMES
    }
    attainable = set().union(
        *(set().union(*outputs.values()) for outputs in target_outputs.values())
    )
    one_digit = sorted(value for value in attainable if 2 <= value <= 9)
    two_digit = sorted(value for value in attainable if 10 <= value <= 99)
    theological = set(ANCHORS)

    rows: list[dict[str, object]] = []
    for single in one_digit:
        for four in combinations(two_digit, 4):
            anchors = {single, *four}
            contacts = [contacts_for_anchor_set(target_outputs[name], anchors) for name in TARGET_NAMES]
            masks = np.asarray(
                [
                    sum(1 << index for index, anchor in enumerate(sorted(anchors)) if anchor in node)
                    for node in contacts
                ],
                dtype=np.uint8,
            )
            metrics = observed_metrics(masks, np.zeros(len(TARGET_NAMES), dtype=np.uint8))
            rows.append(
                {
                    "anchors": ";".join(map(str, sorted(anchors))),
                    "one_digit_anchor": single,
                    "two_digit_anchors": ";".join(map(str, four)),
                    "anchor_incidences": metrics["anchor_incidences"],
                    "pairwise_shared_anchor_links": metrics["pairwise_shared_anchor_links"],
                    "occupied_anchors": metrics["occupied_anchors"],
                    "nodes_with_anchor": metrics["nodes_with_anchor"],
                    "theological_anchor_set": "yes" if anchors == theological else "no",
                }
            )

    target = next(row for row in rows if row["theological_anchor_set"] == "yes")
    incidence_hits = sum(
        int(int(row["anchor_incidences"]) >= int(target["anchor_incidences"])) for row in rows
    )
    link_hits = sum(
        int(
            int(row["pairwise_shared_anchor_links"])
            >= int(target["pairwise_shared_anchor_links"])
        )
        for row in rows
    )
    joint_hits = sum(
        int(
            int(row["anchor_incidences"]) >= int(target["anchor_incidences"])
            and int(row["pairwise_shared_anchor_links"])
            >= int(target["pairwise_shared_anchor_links"])
        )
        for row in rows
    )
    details = {
        "one_digit_pool": one_digit,
        "two_digit_pool": two_digit,
        "sets": len(rows),
        "target_incidences": int(target["anchor_incidences"]),
        "target_links": int(target["pairwise_shared_anchor_links"]),
        "incidence_hits": incidence_hits,
        "link_hits": link_hits,
        "joint_hits": joint_hits,
        "max_incidences": max(int(row["anchor_incidences"]) for row in rows),
        "max_links": max(int(row["pairwise_shared_anchor_links"]) for row in rows),
    }
    return rows, details


def run_yeshua_family_adjustment(
    pool_rows: list[dict[str, str]], yeshua_candidates: np.ndarray
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    families: dict[str, list[dict[str, str]]] = defaultdict(list)
    for index in yeshua_candidates:
        row = pool_rows[int(index)]
        families["".join(sorted(row["hebrew"]))].append(row)

    target_key = "".join(sorted(target_hebrew("Yeshua")))
    exact_rows: list[dict[str, object]] = []
    exact_family_keys: set[str] = set()
    exact_form_count = 0
    for key, forms in sorted(families.items()):
        values = {gematria(row["hebrew"], STANDARD_VALUES) for row in forms}
        if len(values) != 1:
            raise ValueError(f"Consonant family has inconsistent gematria: {key}")
        value = values.pop()
        if to_base(value) != "282":
            continue
        exact_family_keys.add(key)
        exact_form_count += len(forms)
        exact_rows.append(
            {
                "family_key": key,
                "is_yeshua_family": "yes" if key == target_key else "no",
                "standard_value": value,
                "base12": "282",
                "form_count": len(forms),
                "token_frequency": sum(int(row["frequency"]) for row in forms),
                "forms": ";".join(row["hebrew"] for row in forms),
                "first_references": ";".join(row["first_reference"] for row in forms),
            }
        )

    summary = [
        {
            "level": "surface_forms",
            "exact_282": exact_form_count,
            "total": len(yeshua_candidates),
            "proportion": exact_form_count / len(yeshua_candidates),
            "notes": "Complete structurally matched control forms",
        },
        {
            "level": "consonant_families",
            "exact_282": len(exact_family_keys),
            "total": len(families),
            "proportion": len(exact_family_keys) / len(families),
            "notes": "Each sorted consonant multiset counted once",
        },
        {
            "level": "families_excluding_yeshua_multiset",
            "exact_282": len(exact_family_keys - {target_key}),
            "total": len(families) - int(target_key in families),
            "proportion": len(exact_family_keys - {target_key})
            / (len(families) - int(target_key in families)),
            "notes": "All permutations of Yeshua's consonants removed",
        },
    ]
    non_target_keys = exact_family_keys - {target_key}
    details = {
        "families": len(families),
        "exact_families": len(exact_family_keys),
        "target_family_forms": len(families.get(target_key, [])),
        "non_target_exact_forms": sum(len(families[key]) for key in non_target_keys),
        "non_target_exact_families": len(non_target_keys),
        "non_target_family_sizes": sorted(len(families[key]) for key in non_target_keys),
        "non_target_token_frequency": sum(
            int(row["frequency"])
            for key in non_target_keys
            for row in families[key]
        ),
    }
    return summary, exact_rows, details


def completion_record(hebrew: str) -> dict[str, object]:
    tokens = hebrew.split()
    first_value = gematria(tokens[0], STANDARD_VALUES)
    full_value = gematria(hebrew, STANDARD_VALUES)
    flags = completion_flags(hebrew)
    return {
        "first_value": first_value,
        "first_base12": to_base(first_value),
        "full_value": full_value,
        "full_base12": to_base(full_value),
        "completion_hit": flags["completion"],
    }


def run_asher_controls(
    pool_rows: list[dict[str, str]], ehyeh_candidates: np.ndarray
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
]:
    attested_rows: list[dict[str, object]] = []
    for row in pool_rows:
        if int(row["word_count"]) != 3:
            continue
        tokens = row["hebrew"].split()
        if tokens[0] != tokens[2] or tokens[1] != "אשר":
            continue
        calculation = completion_record(row["hebrew"])
        attested_rows.append(
            {
                "control_id": row["control_id"],
                "hebrew": row["hebrew"],
                "first_reference": row["first_reference"],
                "word_lengths": row["word_lengths"],
                "final_form_count": row["final_form_count"],
                "exact_target_structure": (
                    "yes"
                    if row["word_lengths"] == "4-3-4" and row["final_form_count"] == "0"
                    else "no"
                ),
                **{
                    key: "yes" if value is True else "no" if value is False else value
                    for key, value in calculation.items()
                },
            }
        )

    synthetic_rows: list[dict[str, object]] = []
    family_events: dict[str, bool] = {}
    value_events: dict[int, bool] = {}
    form_hits = 0
    for index in ehyeh_candidates:
        row = pool_rows[int(index)]
        outer = row["hebrew"]
        formula = f"{outer} אשר {outer}"
        calculation = completion_record(formula)
        family_key = "".join(sorted(outer))
        hit = bool(calculation["completion_hit"])
        form_hits += int(hit)
        family_events[family_key] = hit
        value_events[int(calculation["first_value"])] = hit
        if hit:
            synthetic_rows.append(
                {
                    "control_id": row["control_id"],
                    "outer_hebrew": outer,
                    "first_reference": row["first_reference"],
                    "consonant_family": family_key,
                    **{
                        key: "yes" if value is True else "no" if value is False else value
                        for key, value in calculation.items()
                    },
                }
            )

    exact_attested = [row for row in attested_rows if row["exact_target_structure"] == "yes"]
    summary = []
    for comparison, rows in (
        ("attested_exact_4_3_4_no_finals", exact_attested),
        ("attested_all_X_Asher_X", attested_rows),
    ):
        hits = sum(row["completion_hit"] == "yes" for row in rows)
        summary.append(
            {
                "comparison": comparison,
                "level": "surface_forms",
                "completion_hits": hits,
                "total": len(rows),
                "proportion": hits / len(rows) if rows else "",
            }
        )
    for level, events in (
        ("surface_forms", {str(index): row for index, row in enumerate(ehyeh_candidates)}),
        ("consonant_families", family_events),
        ("distinct_outer_values", value_events),
    ):
        if level == "surface_forms":
            hits = form_hits
            total = len(ehyeh_candidates)
        else:
            hits = sum(int(hit) for hit in events.values())
            total = len(events)
        summary.append(
            {
                "comparison": "synthetic_X_Asher_X",
                "level": level,
                "completion_hits": hits,
                "total": total,
                "proportion": hits / total,
            }
        )

    target = completion_record(target_hebrew("Ehyeh Asher Ehyeh"))
    exact_target_rows = [
        row for row in synthetic_rows if row["full_base12"] == target["full_base12"]
    ]
    details = {
        "target_first_value": target["first_value"],
        "target_first_base12": target["first_base12"],
        "target_full_value": target["full_value"],
        "target_full_base12": target["full_base12"],
        "attested_total": len(attested_rows),
        "attested_exact": len(exact_attested),
        "synthetic_exact_target_forms": len(exact_target_rows),
        "synthetic_exact_target_families": len(
            {str(row["consonant_family"]) for row in exact_target_rows}
        ),
        "synthetic_exact_target_values": len(
            {int(row["first_value"]) for row in exact_target_rows}
        ),
    }
    return summary, attested_rows, synthetic_rows, details


def format_probability(value: object) -> str:
    return f"{float(value):.6f}"


def write_report(
    robustness_rows: list[dict[str, object]],
    placebo_details: dict[str, object],
    family_summary: list[dict[str, object]],
    family_details: dict[str, object],
    asher_summary: list[dict[str, object]],
    asher_details: dict[str, object],
) -> None:
    scenario_table = [
        "| Scenario | Omitted | Incidences | Incidence tail | Holm | Shared links | Link tail | Holm |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scenario_type in (
        "leave_one_node_out",
        "leave_one_anchor_out",
        "leave_one_route_out",
    ):
        omissions = []
        for row in robustness_rows:
            if row["scenario_type"] == scenario_type and row["omitted"] not in omissions:
                omissions.append(str(row["omitted"]))
        for omitted in omissions:
            rows = [
                row
                for row in robustness_rows
                if row["scenario_type"] == scenario_type and row["omitted"] == omitted
            ]
            incidence = next(row for row in rows if row["metric"] == "anchor_incidences")
            links = next(
                row for row in rows if row["metric"] == "pairwise_shared_anchor_links"
            )
            scenario_table.append(
                f"| {scenario_type} | {omitted} | {incidence['observed']} | "
                f"{format_probability(incidence['empirical_upper_tail'])} | "
                f"{format_probability(incidence['holm_adjusted_upper_tail'])} | "
                f"{links['observed']} | {format_probability(links['empirical_upper_tail'])} | "
                f"{format_probability(links['holm_adjusted_upper_tail'])} |"
            )

    yeshua_rows = [
        row
        for row in robustness_rows
        if row["scenario_type"] == "leave_one_node_out" and row["omitted"] == "Yeshua"
    ]
    yeshua_incidence = next(row for row in yeshua_rows if row["metric"] == "anchor_incidences")
    yeshua_links = next(
        row for row in yeshua_rows if row["metric"] == "pairwise_shared_anchor_links"
    )

    family_table = [
        "| Level | Exact 282 | Total | Proportion |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in family_summary:
        family_table.append(
            f"| {row['level']} | {row['exact_282']} | {row['total']} | "
            f"{float(row['proportion']):.8f} |"
        )

    asher_table = [
        "| Comparison | Level | Completion hits | Total | Proportion |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in asher_summary:
        proportion = row["proportion"]
        proportion_text = "not estimable" if proportion == "" else f"{float(proportion):.8f}"
        asher_table.append(
            f"| {row['comparison']} | {row['level']} | {row['completion_hits']} | "
            f"{row['total']} | {proportion_text} |"
        )

    node_primary = [
        row
        for row in robustness_rows
        if row["scenario_type"] == "leave_one_node_out" and row["metric"] in PRIMARY_METRICS
    ]
    anchor_primary = [
        row
        for row in robustness_rows
        if row["scenario_type"] == "leave_one_anchor_out" and row["metric"] in PRIMARY_METRICS
    ]
    route_primary = [
        row
        for row in robustness_rows
        if row["scenario_type"] == "leave_one_route_out" and row["metric"] in PRIMARY_METRICS
    ]

    def adjusted_survivors(rows: list[dict[str, object]]) -> int:
        return sum(float(row["holm_adjusted_upper_tail"]) < 0.05 for row in rows)

    content = f"""# Network and Formula Robustness Results

Generated by `scripts/network_robustness_analysis.py` under `docs/ROBUSTNESS_TEST_PROTOCOL.md`.

## Reproducibility Lock

- Robustness protocol commit: `{PROTOCOL_COMMIT}`
- Matched network simulations: {SIMULATIONS:,}
- Matched network seed: `{SEED}`
- Generator: NumPy `PCG64`

The script first reproduced the committed six-node baseline exactly before calculating any omission result.

## 1. Network Omission Results

{chr(10).join(scenario_table)}

Removing Yeshua leaves {yeshua_incidence['observed']} anchor incidences and a single shared-anchor link. Their raw upper tails are {format_probability(yeshua_incidence['empirical_upper_tail'])} and {format_probability(yeshua_links['empirical_upper_tail'])}; their twelve-test Holm values are {format_probability(yeshua_incidence['holm_adjusted_upper_tail'])} and {format_probability(yeshua_links['holm_adjusted_upper_tail'])}.

Across the declared primary omission tests, {adjusted_survivors(node_primary)} of 12 node-omission metrics, {adjusted_survivors(anchor_primary)} of 10 anchor-omission metrics, and {adjusted_survivors(route_primary)} of 12 route-omission metrics remain below 0.05 after within-family Holm adjustment. This count describes distributed robustness; it is not a new prospective significance claim.

The incidence concentration survives every node, anchor, and route omission after correction. Shared-link concentration survives every node omission except Yeshua's, survives every anchor omission, and survives only one route omission after the twelve-test correction. The network therefore retains broad anchor contact without Yeshua, but its cross-name connectivity is materially centered on Yeshua and is more sensitive to how contact routes are defined.

That centrality has two distinct readings. Statistically, the link score is not distributed evenly across the six nodes and should not be described as independent of Yeshua. Within a Christian interpretation, a network whose connections converge on Yeshua may instead be theologically coherent. The stress test identifies the center of the numerical network; it does not decide the meaning of that center.

## 2. Consonant-Family Adjustment

{chr(10).join(family_table)}

The structural control stratum contains {family_details['families']:,} distinct consonant families. The {family_details['target_family_forms'] + family_details['non_target_exact_forms']} exact `282` controls partition into {family_details['target_family_forms']} permutations of Yeshua's four consonants and {family_details['non_target_exact_forms']} external forms. Those {family_details['non_target_exact_forms']} external forms occupy {family_details['non_target_exact_families']} consonant families, with family sizes `{family_details['non_target_family_sizes']}`. The outcome therefore has the exact descriptive structure `{family_details['target_family_forms'] + family_details['non_target_exact_forms']} = {family_details['target_family_forms']} + {family_details['non_target_exact_forms']}` and `{family_details['non_target_exact_forms']} = {family_details['non_target_exact_families']} x 2`.

The partition was recognized after the control outcome and was not a frozen test statistic. It is reported as an exploratory structural observation, not assigned a prospective probability. Because Yeshua itself was excluded from the control pool, the count of twelve means twelve other permutations; reinserting the target gives thirteen attested forms in that consonant family. The eight external forms have a total locked-corpus token frequency of {family_details['non_target_token_frequency']}; its correspondence with the traditional value of *chai* is still more frequency-dependent and is not promoted in the reader-facing argument.

The two strict proper-name collisions found earlier both belong to the Yeshua consonant family, so they do not create independent family-level routes to 386.

## 3. Attainable-Anchor Placebos

The target names generate attainable one-digit anchors `{', '.join(map(str, placebo_details['one_digit_pool']))}` and two-digit anchors `{', '.join(map(str, placebo_details['two_digit_pool']))}` under the six frozen routes. Combining one single-digit and four two-digit values produces {placebo_details['sets']:,} exact placebo sets.

The theological set has {placebo_details['target_incidences']} incidences and {placebo_details['target_links']} shared links. Among the attainable placebo sets, {placebo_details['incidence_hits']} equal or exceed its incidence count, {placebo_details['link_hits']} equal or exceed its shared-link count, and {placebo_details['joint_hits']} equal or exceed both simultaneously. The corresponding exact proportions are {placebo_details['incidence_hits'] / placebo_details['sets']:.6f}, {placebo_details['link_hits'] / placebo_details['sets']:.6f}, and {placebo_details['joint_hits'] / placebo_details['sets']:.6f}. Some attainable sets reach {placebo_details['max_incidences']} incidences and {placebo_details['max_links']} shared links, exceeding the theological set on both metrics.

This is the direct correction for freedom to notice a favorable five-anchor set among values already exposed by the selected names and routes. Under that numerical correction, `{{8, 12, 22, 42, 72}}` is not statistically privileged: nearly one quarter of the attainable sets score at least as highly on both declared metrics. The placebo sets treat attainable values as semantically interchangeable, so this result does not test whether the selected values possess independent canonical associations or theological significance.

## 4. Asher-Specific Formula Test

Ehyeh has value {asher_details['target_first_value']} and base-12 form `{asher_details['target_first_base12']}`. Ehyeh Asher Ehyeh has value {asher_details['target_full_value']} and base-12 form `{asher_details['target_full_base12']}`.

{chr(10).join(asher_table)}

The attested rows test actual biblical `X Asher X` sequences remaining in the locked control pool. The synthetic rows hold Asher fixed while varying only the structurally matched outer expression. Surface, consonant-family, and distinct-value levels prevent repeated spellings or gematria-equivalent forms from inflating the arithmetic comparison.

No attested control has the exact target structure, so the attested comparison cannot directly estimate rarity for Ehyeh Asher Ehyeh. In the synthetic template, {asher_details['synthetic_exact_target_forms']} surface forms across {asher_details['synthetic_exact_target_families']} consonant families reproduce the exact `393` output; all do so through the single outer value 21. At the broader palindrome-completion level, roughly one in fifteen distinct outer values succeeds. The result is not automatic, and its value-level mechanism is not arithmetically unique to Ehyeh. The synthetic forms test `2x + 501`; they are not competing attested divine declarations. The complete scriptural expression remains the primary interpretive object.

## Overall Reading

The robustness audit separates four conclusions. First, the selected names remain unusually rich in anchor contacts under matched controls, even when Yeshua is removed. Second, the actual cross-name links are centered on Yeshua. That is statistical dependence, while its theological interpretation remains open; within Christianity, the same centrality may strengthen the architecture's coherence. Third, the five anchors are not unusual as a numerical set once alternative attainable values are admitted, but the placebo does not compare canonical meanings. Fourth, the full Ehyeh expression is an exact completion whose arithmetic mechanism can also produce palindromes for other outer values; those synthetic forms do not replace the complete declaration as the textual object.

All results remain post-discovery stress tests. They can strengthen or weaken the descriptive architecture, but they do not transform it into prospective evidence of intention.
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def main() -> None:
    pool_rows = load_csv(POOL)
    if not pool_rows or pool_rows[0]["source_commit"] != SOURCE_COMMIT:
        raise ValueError("Control pool does not match the locked MorphHB source")
    match_rows = load_csv(MATCHES)
    exact, total, word_final = build_match_indexes(pool_rows)

    needed = set(TARGET_NAMES) | {"Ehyeh"}
    candidate_sets: dict[str, np.ndarray] = {}
    for name in sorted(needed):
        if name == "Ehyeh":
            eligible = [
                item
                for item in match_rows
                if item["analysis_layer"] == "expanded-biblical-all"
                and item["name"] == name
            ]
            if len(eligible) != 1:
                raise ValueError(f"Expected one expanded-biblical match row for {name}")
            row = eligible[0]
        else:
            row = structural_match_row(match_rows, name)
        candidate_sets[name] = candidates_for_match(
            row, exact, total, word_final, pool_rows
        )

    robustness_rows, placebo_rows, placebo_details = run_robustness_networks(
        pool_rows, candidate_sets
    )
    family_summary, exact_families, family_details = run_yeshua_family_adjustment(
        pool_rows, candidate_sets["Yeshua"]
    )
    asher_summary, asher_attested, asher_synthetic, asher_details = run_asher_controls(
        pool_rows, candidate_sets["Ehyeh"]
    )

    write_csv(
        ROBUSTNESS_OUT,
        robustness_rows,
        [
            "scenario_type",
            "omitted",
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
        PLACEBO_OUT,
        placebo_rows,
        [
            "anchors",
            "one_digit_anchor",
            "two_digit_anchors",
            "anchor_incidences",
            "pairwise_shared_anchor_links",
            "occupied_anchors",
            "nodes_with_anchor",
            "theological_anchor_set",
        ],
    )
    write_csv(
        FAMILY_SUMMARY_OUT,
        family_summary,
        ["level", "exact_282", "total", "proportion", "notes"],
    )
    write_csv(
        FAMILY_EXACT_OUT,
        exact_families,
        [
            "family_key",
            "is_yeshua_family",
            "standard_value",
            "base12",
            "form_count",
            "token_frequency",
            "forms",
            "first_references",
        ],
    )
    write_csv(
        ASHER_SUMMARY_OUT,
        asher_summary,
        ["comparison", "level", "completion_hits", "total", "proportion"],
    )
    write_csv(
        ASHER_ATTESTED_OUT,
        asher_attested,
        [
            "control_id",
            "hebrew",
            "first_reference",
            "word_lengths",
            "final_form_count",
            "exact_target_structure",
            "first_value",
            "first_base12",
            "full_value",
            "full_base12",
            "completion_hit",
        ],
    )
    write_csv(
        ASHER_SYNTHETIC_OUT,
        asher_synthetic,
        [
            "control_id",
            "outer_hebrew",
            "first_reference",
            "consonant_family",
            "first_value",
            "first_base12",
            "full_value",
            "full_base12",
            "completion_hit",
        ],
    )
    write_report(
        robustness_rows,
        placebo_details,
        family_summary,
        family_details,
        asher_summary,
        asher_details,
    )


if __name__ == "__main__":
    main()
