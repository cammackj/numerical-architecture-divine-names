from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from audit_numerical_claims import (
    MISPAR_GADOL_VALUES,
    STANDARD_VALUES,
    collapse_base12_text,
    collapse_decimal,
    gematria,
    is_palindrome,
    to_base,
)
from corpus_sensitivity import competition_rank, to_any_base


ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data" / "control_phrase_pool.csv"
MATCHES = ROOT / "data" / "control_match_registry.csv"
SUMMARY_OUT = ROOT / "data" / "control_simulation_summary.csv"
BASE_OUT = ROOT / "data" / "control_base_results.csv"
SECONDARY_OUT = ROOT / "data" / "control_secondary_results.csv"
DISTRIBUTION_OUT = ROOT / "data" / "control_simulation_distributions.csv"
REPORT_OUT = ROOT / "docs" / "MATCHED_CONTROL_RESULTS.md"

PROTOCOL_COMMIT = "b7724fda228eb09489ab13c062c0d4d33fe3c876"
POOL_COMMIT = "bbbfec43d21af68f2a960eb24a42ee874b985269"
SOURCE_COMMIT = "3d15126fb1ef74867fc1434be1942e837932691f"
SIMULATIONS = 100_000
SEED = 20_260_718
BASES = tuple(range(2, 21))
BASE12_INDEX = BASES.index(12)
LAYER_ORDER = (
    "primary-biblical",
    "expanded-biblical-all",
    "restored-christian-inclusive",
    "full-christian-expansion",
)


@dataclass
class ControlValue:
    standard: int
    mispar_gadol: int
    standard_flags: tuple[int, ...]
    mispar_flags: tuple[int, ...]
    any_base12: int
    strict_8: int
    strict_12: int


@dataclass
class SummaryRow:
    analysis_layer: str
    analysis_status: str
    target_rows: int
    value_system: str
    observed_base12_palindromes: int
    observed_base12_rank: int
    observed_base12_sole_leader: str
    simulations_rank_as_good_or_better: int
    empirical_rank_lower_tail: float
    control_mean: float
    control_median: float
    control_interval_2_5: float
    control_interval_97_5: float
    simulations_at_least_observed: int
    empirical_upper_tail: float
    holm_adjusted_upper_tail: float
    simulations: int
    seed: int


@dataclass
class BaseResultRow:
    analysis_layer: str
    analysis_status: str
    value_system: str
    base: int
    observed_palindromes: int
    observed_rank: int
    control_mean: float
    control_median: float
    control_interval_2_5: float
    control_interval_97_5: float
    simulations_at_least_observed: int
    empirical_upper_tail: float


@dataclass
class SecondaryRow:
    analysis_layer: str
    analysis_status: str
    metric: str
    observed_count: int
    control_mean: float
    control_median: float
    control_interval_2_5: float
    control_interval_97_5: float
    simulations_at_least_observed: int
    empirical_upper_tail: float


@dataclass
class DistributionRow:
    analysis_layer: str
    value_system: str
    metric: str
    value: int
    frequency: int
    proportion: float


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def palindrome_flags(value: int) -> tuple[int, ...]:
    return tuple(int(is_palindrome(to_any_base(value, base))) for base in BASES)


def calculate_value(hebrew: str) -> ControlValue:
    standard = gematria(hebrew, STANDARD_VALUES)
    mispar = gematria(hebrew, MISPAR_GADOL_VALUES)
    standard_flags = palindrome_flags(standard)
    mispar_flags = palindrome_flags(mispar)
    endpoints = {
        collapse_decimal(standard),
        collapse_decimal(mispar),
        collapse_base12_text(to_base(standard)),
        collapse_base12_text(to_base(mispar)),
    }
    return ControlValue(
        standard=standard,
        mispar_gadol=mispar,
        standard_flags=standard_flags,
        mispar_flags=mispar_flags,
        any_base12=int(standard_flags[BASE12_INDEX] or mispar_flags[BASE12_INDEX]),
        strict_8=int(8 in endpoints),
        strict_12=int(12 in endpoints),
    )


def load_control_arrays() -> tuple[list[dict[str, str]], dict[str, np.ndarray]]:
    rows = load_csv(POOL)
    if not rows or rows[0]["source_commit"] != SOURCE_COMMIT:
        raise ValueError("Control pool does not match the locked OSHB source")

    count = len(rows)
    std_flags = np.zeros((count, len(BASES)), dtype=np.uint8)
    mg_flags = np.zeros((count, len(BASES)), dtype=np.uint8)
    any_base12 = np.zeros(count, dtype=np.uint8)
    strict_8 = np.zeros(count, dtype=np.uint8)
    strict_12 = np.zeros(count, dtype=np.uint8)

    value_cache: dict[str, ControlValue] = {}
    for index, row in enumerate(rows):
        value = value_cache.get(row["hebrew"])
        if value is None:
            value = calculate_value(row["hebrew"])
            value_cache[row["hebrew"]] = value
        std_flags[index] = value.standard_flags
        mg_flags[index] = value.mispar_flags
        any_base12[index] = value.any_base12
        strict_8[index] = value.strict_8
        strict_12[index] = value.strict_12

    return rows, {
        "standard": std_flags,
        "mispar_gadol": mg_flags,
        "any_base12": any_base12,
        "strict_8": strict_8,
        "strict_12": strict_12,
    }


def parse_lengths(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("-"))


def build_match_indexes(
    pool_rows: list[dict[str, str]],
) -> tuple[
    dict[tuple[int, tuple[int, ...], int], np.ndarray],
    dict[tuple[int, int, int], np.ndarray],
    dict[tuple[int, int], np.ndarray],
]:
    exact: dict[tuple[int, tuple[int, ...], int], list[int]] = defaultdict(list)
    total: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    word_final: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(pool_rows):
        words = int(row["word_count"])
        lengths = parse_lengths(row["word_lengths"])
        letters = int(row["total_letters"])
        finals = int(row["final_form_count"])
        exact[(words, lengths, finals)].append(index)
        total[(words, letters, finals)].append(index)
        word_final[(words, finals)].append(index)

    return (
        {key: np.asarray(values, dtype=np.int32) for key, values in exact.items()},
        {key: np.asarray(values, dtype=np.int32) for key, values in total.items()},
        {key: np.asarray(values, dtype=np.int32) for key, values in word_final.items()},
    )


def candidates_for_match(
    row: dict[str, str],
    exact: dict[tuple[int, tuple[int, ...], int], np.ndarray],
    total: dict[tuple[int, int, int], np.ndarray],
    word_final: dict[tuple[int, int], np.ndarray],
    pool_rows: list[dict[str, str]],
) -> np.ndarray:
    words = int(row["word_count"])
    lengths = parse_lengths(row["word_lengths"])
    letters = int(row["total_letters"])
    finals = int(row["final_form_count"])
    level = row["match_level"]
    if level == "exact-word-vector":
        candidates = exact[(words, lengths, finals)]
    elif level == "fallback-exact-total":
        candidates = total[(words, letters, finals)]
    elif level in {"fallback-total-within-1", "fallback-total-within-2"}:
        distance = 1 if level.endswith("1") else 2
        base = word_final[(words, finals)]
        candidates = np.asarray(
            [
                index for index in base
                if abs(int(pool_rows[int(index)]["total_letters"]) - letters) <= distance
            ],
            dtype=np.int32,
        )
    else:
        raise ValueError(f"Unknown match level: {level}")

    expected = int(row["eligible_control_count"])
    if len(candidates) != expected:
        raise ValueError(
            f"Match count changed for {row['target_id']}: {len(candidates)} != {expected}"
        )
    return candidates


def observed_metrics(rows: list[dict[str, str]]) -> dict[str, object]:
    values = [calculate_value(row["hebrew"]) for row in rows]
    standard_counts = np.asarray(
        [sum(value.standard_flags[index] for value in values) for index in range(len(BASES))],
        dtype=np.int16,
    )
    mispar_counts = np.asarray(
        [sum(value.mispar_flags[index] for value in values) for index in range(len(BASES))],
        dtype=np.int16,
    )
    return {
        "standard": standard_counts,
        "mispar_gadol": mispar_counts,
        "any_base12": sum(value.any_base12 for value in values),
        "strict_8": sum(value.strict_8 for value in values),
        "strict_12": sum(value.strict_12 for value in values),
    }


def sample_layer(
    candidate_sets: list[np.ndarray],
    arrays: dict[str, np.ndarray],
    rng: np.random.Generator,
    batch_size: int = 2_000,
) -> dict[str, np.ndarray]:
    standard_counts = np.zeros((SIMULATIONS, len(BASES)), dtype=np.int16)
    mispar_counts = np.zeros((SIMULATIONS, len(BASES)), dtype=np.int16)
    any_counts = np.zeros(SIMULATIONS, dtype=np.int16)
    strict_8_counts = np.zeros(SIMULATIONS, dtype=np.int16)
    strict_12_counts = np.zeros(SIMULATIONS, dtype=np.int16)

    for offset in range(0, SIMULATIONS, batch_size):
        size = min(batch_size, SIMULATIONS - offset)
        choices = np.empty((len(candidate_sets), size), dtype=np.int32)
        for target_index, candidates in enumerate(candidate_sets):
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
                        raise RuntimeError("Unable to sample unique controls within a corpus")
            choices[target_index] = draw

        destination = slice(offset, offset + size)
        standard_counts[destination] = arrays["standard"][choices].sum(axis=0)
        mispar_counts[destination] = arrays["mispar_gadol"][choices].sum(axis=0)
        any_counts[destination] = arrays["any_base12"][choices].sum(axis=0)
        strict_8_counts[destination] = arrays["strict_8"][choices].sum(axis=0)
        strict_12_counts[destination] = arrays["strict_12"][choices].sum(axis=0)

    return {
        "standard": standard_counts,
        "mispar_gadol": mispar_counts,
        "any_base12": any_counts,
        "strict_8": strict_8_counts,
        "strict_12": strict_12_counts,
    }


def analysis_status(layer: str) -> str:
    return "primary-locked" if layer == "primary-biblical" else "exploratory-sensitivity"


def empirical_tail(values: np.ndarray, observed: int) -> tuple[int, float]:
    count = int(np.sum(values >= observed))
    return count, (count + 1) / (SIMULATIONS + 1)


def interval(values: np.ndarray) -> tuple[float, float, float]:
    lower, median, upper = np.percentile(values, [2.5, 50, 97.5])
    return float(lower), float(median), float(upper)


def holm_adjust_two(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    for index, (name, value) in enumerate(ordered):
        candidate = min(1.0, (len(ordered) - index) * value)
        running = max(running, candidate)
        adjusted[name] = running
    return adjusted


def make_distribution_rows(
    layer: str, value_system: str, metric: str, values: np.ndarray
) -> list[DistributionRow]:
    counts = Counter(int(value) for value in values)
    return [
        DistributionRow(
            analysis_layer=layer,
            value_system=value_system,
            metric=metric,
            value=value,
            frequency=frequency,
            proportion=frequency / SIMULATIONS,
        )
        for value, frequency in sorted(counts.items())
    ]


def analyze_layer(
    layer: str,
    match_rows: list[dict[str, str]],
    candidate_sets: list[np.ndarray],
    arrays: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> tuple[
    list[SummaryRow],
    list[BaseResultRow],
    list[SecondaryRow],
    list[DistributionRow],
]:
    observed = observed_metrics(match_rows)
    simulated = sample_layer(candidate_sets, arrays, rng)
    status = analysis_status(layer)

    primary_p: dict[str, float] = {}
    primary_counts: dict[str, int] = {}
    for value_system in ("standard", "mispar_gadol"):
        observed_count = int(observed[value_system][BASE12_INDEX])
        at_least, p_value = empirical_tail(
            simulated[value_system][:, BASE12_INDEX], observed_count
        )
        primary_p[value_system] = p_value
        primary_counts[value_system] = at_least
    adjusted = holm_adjust_two(primary_p)

    summaries: list[SummaryRow] = []
    base_results: list[BaseResultRow] = []
    distributions: list[DistributionRow] = []
    for value_system in ("standard", "mispar_gadol"):
        observed_counts = observed[value_system]
        control_counts = simulated[value_system]
        rank = competition_rank(
            {base: int(observed_counts[index]) for index, base in enumerate(BASES)}, 12
        )
        sole_leader = (
            observed_counts[BASE12_INDEX] == np.max(observed_counts)
            and int(np.sum(observed_counts == np.max(observed_counts))) == 1
        )
        ranks = 1 + np.sum(
            control_counts > control_counts[:, [BASE12_INDEX]], axis=1
        )
        rank_at_least = int(np.sum(ranks <= rank))
        rank_tail = (rank_at_least + 1) / (SIMULATIONS + 1)
        lower, median, upper = interval(control_counts[:, BASE12_INDEX])
        summaries.append(
            SummaryRow(
                analysis_layer=layer,
                analysis_status=status,
                target_rows=len(match_rows),
                value_system=value_system,
                observed_base12_palindromes=int(observed_counts[BASE12_INDEX]),
                observed_base12_rank=rank,
                observed_base12_sole_leader="yes" if sole_leader else "no",
                simulations_rank_as_good_or_better=rank_at_least,
                empirical_rank_lower_tail=rank_tail,
                control_mean=float(np.mean(control_counts[:, BASE12_INDEX])),
                control_median=median,
                control_interval_2_5=lower,
                control_interval_97_5=upper,
                simulations_at_least_observed=primary_counts[value_system],
                empirical_upper_tail=primary_p[value_system],
                holm_adjusted_upper_tail=adjusted[value_system],
                simulations=SIMULATIONS,
                seed=SEED,
            )
        )
        for index, base in enumerate(BASES):
            base_values = control_counts[:, index]
            at_least, p_value = empirical_tail(base_values, int(observed_counts[index]))
            base_lower, base_median, base_upper = interval(base_values)
            observed_rank = competition_rank(
                {candidate: int(observed_counts[i]) for i, candidate in enumerate(BASES)},
                base,
            )
            base_results.append(
                BaseResultRow(
                    analysis_layer=layer,
                    analysis_status=status,
                    value_system=value_system,
                    base=base,
                    observed_palindromes=int(observed_counts[index]),
                    observed_rank=observed_rank,
                    control_mean=float(np.mean(base_values)),
                    control_median=base_median,
                    control_interval_2_5=base_lower,
                    control_interval_97_5=base_upper,
                    simulations_at_least_observed=at_least,
                    empirical_upper_tail=p_value,
                )
            )
        distributions.extend(
            make_distribution_rows(
                layer, value_system, "base12_palindrome_count", control_counts[:, BASE12_INDEX]
            )
        )
        distributions.extend(
            make_distribution_rows(layer, value_system, "base12_competition_rank", ranks)
        )

    secondary: list[SecondaryRow] = []
    for metric in ("any_base12", "strict_8", "strict_12"):
        observed_count = int(observed[metric])
        values = simulated[metric]
        at_least, p_value = empirical_tail(values, observed_count)
        lower, median, upper = interval(values)
        secondary.append(
            SecondaryRow(
                analysis_layer=layer,
                analysis_status=status,
                metric=metric,
                observed_count=observed_count,
                control_mean=float(np.mean(values)),
                control_median=median,
                control_interval_2_5=lower,
                control_interval_97_5=upper,
                simulations_at_least_observed=at_least,
                empirical_upper_tail=p_value,
            )
        )
        distributions.extend(make_distribution_rows(layer, "combined", metric, values))

    return summaries, base_results, secondary, distributions


def write_dataclass_csv(path: Path, rows: list[object]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def format_probability(value: float) -> str:
    return f"{value:.6f}"


def write_report(
    summaries: list[SummaryRow],
    base_results: list[BaseResultRow],
    secondary: list[SecondaryRow],
) -> None:
    summary_lines = [
        "| Layer | Status | N | Values | Observed B12 | Rank | Rank tail | Control mean | 95% interval | Count tail | Holm |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in summaries:
        summary_lines.append(
            f"| {row.analysis_layer} | {row.analysis_status} | {row.target_rows} | "
            f"{row.value_system} | {row.observed_base12_palindromes} | {row.observed_base12_rank} | "
            f"{format_probability(row.empirical_rank_lower_tail)} | {row.control_mean:.3f} | "
            f"{row.control_interval_2_5:.1f}-{row.control_interval_97_5:.1f} | "
            f"{format_probability(row.empirical_upper_tail)} | "
            f"{format_probability(row.holm_adjusted_upper_tail)} |"
        )

    primary = [row for row in summaries if row.analysis_layer == "primary-biblical"]
    standard = next(row for row in primary if row.value_system == "standard")
    mispar = next(row for row in primary if row.value_system == "mispar_gadol")
    primary_interpretation = (
        "Both co-primary base-12 counts exceed the matched-control expectation after "
        "the prespecified Holm adjustment."
        if standard.holm_adjusted_upper_tail < 0.05
        and mispar.holm_adjusted_upper_tail < 0.05
        else "The co-primary results do not both clear the prespecified 0.05 threshold after Holm adjustment; the base-12 concentration remains descriptive under this control design."
    )

    primary_bases = [
        row for row in base_results
        if row.analysis_layer == "primary-biblical" and row.base == 12
    ]
    base_sentences = " ".join(
        f"Under {row.value_system}, base 12 has {row.observed_palindromes} palindromes "
        f"(rank {row.observed_rank}), versus a matched-control mean of {row.control_mean:.3f}."
        for row in primary_bases
    )

    primary_all_bases = [
        row for row in base_results if row.analysis_layer == "primary-biblical"
    ]
    primary_base_lines = [
        "| Base | Standard observed | Standard mean | Standard tail | MG observed | MG mean | MG tail |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for base in BASES:
        std_row = next(
            row for row in primary_all_bases
            if row.value_system == "standard" and row.base == base
        )
        mg_row = next(
            row for row in primary_all_bases
            if row.value_system == "mispar_gadol" and row.base == base
        )
        primary_base_lines.append(
            f"| {base} | {std_row.observed_palindromes} | {std_row.control_mean:.3f} | "
            f"{format_probability(std_row.empirical_upper_tail)} | {mg_row.observed_palindromes} | "
            f"{mg_row.control_mean:.3f} | {format_probability(mg_row.empirical_upper_tail)} |"
        )

    base3_standard = next(
        row for row in primary_all_bases
        if row.value_system == "standard" and row.base == 3
    )
    base3_mispar = next(
        row for row in primary_all_bases
        if row.value_system == "mispar_gadol" and row.base == 3
    )
    competing_base_interpretation = (
        f"On an expression-row count, base 3 is the observed primary-corpus leader under both value systems, with "
        f"{base3_standard.observed_palindromes} palindromes under standard gematria "
        f"(unadjusted upper tail {format_probability(base3_standard.empirical_upper_tail)}) "
        f"and {base3_mispar.observed_palindromes} under Mispar Gadol "
        f"(unadjusted upper tail {format_probability(base3_mispar.empirical_upper_tail)}). "
        "The expression-row base-12 result must therefore be discussed as one structured concentration, not as the only unusual base. "
        "A companion finite sensitivity in `docs/DISTINCT_VALUE_BASE_RANKING.md` counts each exact numerical value once; under that metric, base 12 shares first place in the primary corpus under both value systems."
    )

    def sensitivity_sentence(layer: str, label: str) -> str:
        rows = [row for row in summaries if row.analysis_layer == layer]
        std_row = next(row for row in rows if row.value_system == "standard")
        mg_row = next(row for row in rows if row.value_system == "mispar_gadol")
        return (
            f"{label} has {std_row.observed_base12_palindromes} standard and "
            f"{mg_row.observed_base12_palindromes} Mispar Gadol base-12 palindromes; "
            f"its Holm-adjusted exploratory tails are "
            f"{format_probability(std_row.holm_adjusted_upper_tail)} and "
            f"{format_probability(mg_row.holm_adjusted_upper_tail)}."
        )

    sensitivity_interpretation = " ".join(
        [
            sensitivity_sentence(
                "expanded-biblical-all", "The complete expanded biblical layer"
            ),
            sensitivity_sentence(
                "restored-christian-inclusive",
                "The restored Christian-inclusive layer containing Yeshua HaMashiach",
            ),
            sensitivity_sentence(
                "full-christian-expansion", "The full Christian candidate layer"
            ),
        ]
    )

    secondary_lines = [
        "| Layer | Metric | Observed | Control mean | 95% interval | Upper tail |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]
    for row in secondary:
        secondary_lines.append(
            f"| {row.analysis_layer} | {row.metric} | {row.observed_count} | "
            f"{row.control_mean:.3f} | {row.control_interval_2_5:.1f}-{row.control_interval_97_5:.1f} | "
            f"{format_probability(row.empirical_upper_tail)} |"
        )

    content = f"""# Matched Hebrew Control Results

Generated by `scripts/matched_control_analysis.py` under the frozen protocol in `docs/CONTROL_TEST_PROTOCOL.md`.

## Reproducibility Lock

- Protocol commit: `{PROTOCOL_COMMIT}`
- Blinded control-pool commit: `{POOL_COMMIT}`
- OSHB source commit: `{SOURCE_COMMIT}`
- Simulations per layer: {SIMULATIONS:,}
- Seed: `{SEED}`
- Generator: NumPy `PCG64`

The control pool was committed before this numerical script existed. Every simulation samples unique control phrases within a corpus and preserves each target row's predeclared structural match set.

## Primary and Sensitivity Results

{chr(10).join(summary_lines)}

The `primary-biblical` rows form the repository-locked primary analysis set. The set and protocol were frozen before control outcomes, but the names, base-12 hypothesis, and operations arose from earlier inspection of the inherited manuscript; the analysis is therefore conditional on that prior selection rather than fully confirmatory. All expanded and Christian-inclusive rows are exploratory sensitivity analyses because their membership was specified after pattern discovery. `restored-christian-inclusive` includes `Yeshua HaMashiach / ישוע המשיח`; `expanded-biblical-all` and `full-christian-expansion` retain their complete candidate sets, including non-hits.

## Primary Interpretation

{primary_interpretation} {base_sentences}

{competing_base_interpretation}

`Rank tail` is the proportion of matched simulations in which base 12 ranks at least as highly as observed. It is descriptive and is not one of the two co-primary tests.

## All Bases in the Primary Corpus

{chr(10).join(primary_base_lines)}

These base-specific tails are unadjusted secondary results. They are shown to prevent base-12-only reporting and should not be interpreted as 19 independent primary tests.

## Additional Discoveries

{sensitivity_interpretation}

Those results retain all declared candidates and non-hits, but they remain exploratory because the layers were defined after discovery and contain overlapping expressions. They justify continued investigation and manuscript discussion, not independent confirmation.

Empirical probabilities answer a narrow question: how often a structurally matched set of Hebrew Bible phrases equals or exceeds the observed count. They do not establish design, antiquity, theological intent, or independence among nested expressions.

## Secondary Outcomes

{chr(10).join(secondary_lines)}

`any_base12` counts a row palindromic under either standard gematria or Mispar Gadol. `strict_8` and `strict_12` use the previously defined decimal and base-12 digit-collapse paths and count a row when any declared path reaches the endpoint.

## Files

- `data/control_simulation_summary.csv`: co-primary base-12 results and adjusted probabilities;
- `data/control_base_results.csv`: all bases 2-20, not only base 12;
- `data/control_secondary_results.csv`: combined palindrome and collapse outcomes;
- `data/control_simulation_distributions.csv`: complete count and rank frequency tables.

## Limitations

- Controls are structurally matched Hebrew Bible phrase types, not a semantic corpus of divine titles.
- Uniform sampling is over unique normalized phrase types, not token frequency.
- Expanded candidate lists contain nested and non-independent formulas.
- The Christian layers compare Hebrew Christian titles with Hebrew Bible phrase controls and therefore remain exploratory and comparative.
- This study tests the locked operations only; it does not license additional post hoc transformations.

## Protocol Deviations

None.
"""
    REPORT_OUT.write_text(content, encoding="utf-8")


def main() -> None:
    pool_rows, arrays = load_control_arrays()
    match_rows = load_csv(MATCHES)
    if [layer for layer in LAYER_ORDER if layer not in {row["analysis_layer"] for row in match_rows}]:
        raise ValueError("A declared analysis layer is missing from the match registry")

    exact, total, word_final = build_match_indexes(pool_rows)
    seed_sequence = np.random.SeedSequence(SEED)
    layer_seeds = seed_sequence.spawn(len(LAYER_ORDER))

    all_summaries: list[SummaryRow] = []
    all_bases: list[BaseResultRow] = []
    all_secondary: list[SecondaryRow] = []
    all_distributions: list[DistributionRow] = []

    for layer, layer_seed in zip(LAYER_ORDER, layer_seeds, strict=True):
        layer_rows = [row for row in match_rows if row["analysis_layer"] == layer]
        candidate_sets = [
            candidates_for_match(row, exact, total, word_final, pool_rows)
            for row in layer_rows
        ]
        summaries, bases, secondary, distributions = analyze_layer(
            layer,
            layer_rows,
            candidate_sets,
            arrays,
            np.random.default_rng(layer_seed),
        )
        all_summaries.extend(summaries)
        all_bases.extend(bases)
        all_secondary.extend(secondary)
        all_distributions.extend(distributions)
        print(f"completed {layer}: {len(layer_rows)} rows")

    write_dataclass_csv(SUMMARY_OUT, all_summaries)
    write_dataclass_csv(BASE_OUT, all_bases)
    write_dataclass_csv(SECONDARY_OUT, all_secondary)
    write_dataclass_csv(DISTRIBUTION_OUT, all_distributions)
    write_report(all_summaries, all_bases, all_secondary)
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {BASE_OUT}")
    print(f"wrote {SECONDARY_OUT}")
    print(f"wrote {DISTRIBUTION_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
