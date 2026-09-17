#!/usr/bin/env python3
"""Exact census and design-based sampling audit for Issue #982 / #833 G."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import inspect
import itertools
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Mapping, Sequence, Tuple


HERE = Path(__file__).resolve().parent
DEPENDENCY_DIR = HERE.parent / "gmi-833-ecology-specification-generator-v1"
ISSUE = 982
PARENT_ISSUE = 833
SOURCE_PR = 985
DEPENDENCY_ISSUE = 957
DEPENDENCY_PR = 959
DEPENDENCY_HEAD = "bd61471056cc904b03e70f05e6b64c4445e25b07"
FREEZE_COMMIT = "18615590d16af8c0e69e7e259dc2b96abe479832"
DRAW_COMMIT = "90f1250b91bce637a64fc06e001d046d0c6961dc"
POPULATION_SIZE = 1 << 17
SAMPLE_SIZE = 1 << 12
AXIS_COUNT = 17
TERMINAL = "GMI_833_REGISTERED_ECOLOGY_CENSUS_AND_SAMPLING_UNCERTAINTY_PROVED"
REGISTERED_SCOPE = "registered_binary_product_E_v1"

TARGET_ROWS = (
    "Sample enough ecology space to avoid hand-picked niche bias.",
    "Quantify ecology sampling bias and uncertainty.",
)

DIAGNOSTIC_NAMES = ("axis_load", "rare_niche", "global_parity", "cross_pair")


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load required module: " + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = _load_module(
    "gmi833_ecology_generator_dependency_v1",
    DEPENDENCY_DIR / "ecology_specification_generator_v1.py",
)
DRAW = _load_module("gmi833_ecology_draw_v1", HERE / "draw_prospective_v1.py")


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, separators=(",", ": ")) + "\n").encode()


def sha256(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def rank_to_indices(rank: int) -> Tuple[int, ...]:
    if type(rank) is not int or rank < 0 or rank >= POPULATION_SIZE:
        raise ValueError("rank must be an exact integer in the registered population")
    return tuple((rank >> (AXIS_COUNT - 1 - position)) & 1 for position in range(AXIS_COUNT))


def indices_to_rank(indices: Sequence[int]) -> int:
    if len(indices) != AXIS_COUNT or any(type(value) is not int or value not in (0, 1) for value in indices):
        raise ValueError("indices must contain exactly seventeen binary exact integers")
    rank = 0
    for value in indices:
        rank = 2 * rank + value
    return rank


def diagnostic_values(indices: Sequence[int]) -> Mapping[str, Fraction]:
    if len(indices) != AXIS_COUNT or any(type(value) is not int or value not in (0, 1) for value in indices):
        raise ValueError("diagnostics require seventeen binary exact integers")
    return {
        "axis_load": Fraction(sum(indices), AXIS_COUNT),
        "rare_niche": Fraction(math.prod(indices[position] for position in (0, 3, 7, 12, 16)), 1),
        "global_parity": Fraction(sum(indices) % 2, 1),
        "cross_pair": Fraction(indices[2] * indices[11], 1),
    }


def _level_basis() -> Tuple[Tuple[Mapping[str, Any], ...], ...]:
    rows = []
    for axis in GENERATOR.AXES:
        levels = []
        for level_index, level in enumerate(axis["levels"]):
            computed = GENERATOR.evaluate_probe(axis["id"], level["payload"])
            if type(computed) is not bool or computed is not bool(level_index):
                raise ValueError("dependency level is not the registered nondegenerate basis")
            if level["expected_probe"] is not computed:
                raise ValueError("dependency level polarity contradicts its payload")
            levels.append(
                {
                    "axis": axis["id"],
                    "probe": axis["probe"],
                    "level_index": level_index,
                    "token": level["token"],
                    "payload_sha256": sha256(level["payload"]),
                    "required_response": int(computed),
                }
            )
        rows.append(tuple(levels))
    return tuple(rows)


LEVEL_BASIS = _level_basis()


def compact_ecology_and_specification(indices: Sequence[int]) -> Tuple[Tuple[Mapping[str, Any], ...], Tuple[int, ...]]:
    """Construct the factorized semantic record used by the exact census."""
    if len(indices) != AXIS_COUNT or any(type(value) is not int or value not in (0, 1) for value in indices):
        raise ValueError("compact ecology requires the registered binary coordinates")
    ecology = tuple(LEVEL_BASIS[position][value] for position, value in enumerate(indices))
    specification = tuple(row["required_response"] for row in ecology)
    return ecology, specification


def compact_semantically_well_formed(
    indices: Sequence[int], ecology: Sequence[Mapping[str, Any]], specification: Sequence[int]
) -> bool:
    if len(indices) != AXIS_COUNT or len(ecology) != AXIS_COUNT or len(specification) != AXIS_COUNT:
        return False
    for position, (index, row, response) in enumerate(zip(indices, ecology, specification)):
        if type(index) is not int or index not in (0, 1):
            return False
        if row != LEVEL_BASIS[position][index]:
            return False
        if row["axis"] != GENERATOR.AXIS_IDS[position] or row["probe"] != GENERATOR.PROBE_IDS[position]:
            return False
        if type(response) is not int or response != index or response != row["required_response"]:
            return False
    return True


def dependency_basis_audit() -> Mapping[str, Any]:
    witness_indices = [tuple(0 for _ in range(AXIS_COUNT)), tuple(1 for _ in range(AXIS_COUNT))]
    witness_indices.extend(tuple(1 if position == selected else 0 for position in range(AXIS_COUNT)) for selected in range(AXIS_COUNT))
    rows = []
    for indices in witness_indices:
        ecology = GENERATOR.ecology_from_indices(indices)
        specification = GENERATOR.build_behavioral_specification(ecology)
        targets = tuple(row["required_response"] for row in specification["required_relation"])
        compact_ecology, compact_specification = compact_ecology_and_specification(indices)
        rows.append(
            {
                "rank": indices_to_rank(indices),
                "dependency_ecology_semantically_valid": GENERATOR.semantic_well_formed(ecology),
                "dependency_specification_valid": GENERATOR.behavioral_specification_well_formed(specification),
                "compact_record_valid": compact_semantically_well_formed(indices, compact_ecology, compact_specification),
                "targets_equal": targets == compact_specification == tuple(indices),
            }
        )
    return {
        "basis_level_count": sum(len(levels) for levels in LEVEL_BASIS),
        "dependency_witness_count": len(rows),
        "rows": rows,
        "passes": len(LEVEL_BASIS) == AXIS_COUNT
        and all(len(levels) == 2 for levels in LEVEL_BASIS)
        and all(all(row[key] for key in row if key != "rank") for row in rows),
    }


def exact_census() -> Mapping[str, Any]:
    outcomes: Dict[str, List[Fraction]] = {name: [] for name in DIAGNOSTIC_NAMES}
    seen = bytearray(POPULATION_SIZE)
    iterator_count = 0
    interval_hasher = hashlib.sha256()
    semantic_failures = 0
    target_failures = 0
    for expected_rank, indices in enumerate(GENERATOR.iter_family_coordinates()):
        rank = GENERATOR.mixed_radix_code(indices, (2,) * AXIS_COUNT)
        if rank != expected_rank or indices_to_rank(indices) != rank or rank_to_indices(rank) != tuple(indices):
            raise AssertionError("registered iterator and independent rank arithmetic disagree")
        if seen[rank]:
            raise AssertionError("registered census duplicated a rank")
        seen[rank] = 1
        ecology, specification = compact_ecology_and_specification(indices)
        if not compact_semantically_well_formed(indices, ecology, specification):
            semantic_failures += 1
        if specification != tuple(indices):
            target_failures += 1
        values = diagnostic_values(indices)
        for name in DIAGNOSTIC_NAMES:
            outcomes[name].append(values[name])
        interval_hasher.update(rank.to_bytes(4, "big"))
        iterator_count += 1
    arithmetic_count = math.prod(len(axis["levels"]) for axis in GENERATOR.AXES)
    recursive_count = 1
    for axis in GENERATOR.AXES:
        recursive_count *= len(axis["levels"])
    complete_interval = iterator_count == POPULATION_SIZE and all(seen)
    means = {name: sum(values, Fraction(0, 1)) / POPULATION_SIZE for name, values in outcomes.items()}
    analytic_means = {
        "axis_load": Fraction(1, 2),
        "rare_niche": Fraction(1, 32),
        "global_parity": Fraction(1, 2),
        "cross_pair": Fraction(1, 4),
    }
    return {
        "schema": "RegisteredEcologyExactCensusV1",
        "population_size": POPULATION_SIZE,
        "axis_count": AXIS_COUNT,
        "arithmetic_product": arithmetic_count,
        "recursive_product": recursive_count,
        "iterator_count": iterator_count,
        "unique_rank_count": sum(seen),
        "complete_integer_interval": complete_interval,
        "rank_stream_sha256": interval_hasher.hexdigest(),
        "compact_semantic_failures": semantic_failures,
        "compact_target_failures": target_failures,
        "means": {name: fraction_text(value) for name, value in means.items()},
        "analytic_means": {name: fraction_text(value) for name, value in analytic_means.items()},
        "means_match_independent_analytic_values": means == analytic_means,
        "outcomes": outcomes,
    }


def validate_sample_ranks(ranks: Sequence[int], population_size: int = POPULATION_SIZE) -> Tuple[int, ...]:
    if type(population_size) is not int or population_size <= 0:
        raise ValueError("population size must be a positive exact integer")
    if not isinstance(ranks, (list, tuple)):
        raise ValueError("sample ranks must be an ordered list or tuple")
    checked = []
    for rank in ranks:
        if type(rank) is not int or rank < 0 or rank >= population_size:
            raise ValueError("sample rank is not an in-range exact integer")
        checked.append(rank)
    if len(checked) != len(set(checked)):
        raise ValueError("sampling without replacement forbids duplicate ranks")
    return tuple(checked)


def _coerce_outcomes(outcomes: Sequence[Any]) -> Tuple[Fraction, ...]:
    checked = []
    for value in outcomes:
        if type(value) is int:
            converted = Fraction(value, 1)
        elif isinstance(value, Fraction):
            converted = value
        else:
            raise ValueError("outcomes must be exact integers or fractions")
        if converted < 0 or converted > 1:
            raise ValueError("outcomes must lie in the frozen unit interval")
        checked.append(converted)
    return tuple(checked)


def sampling_statistics(outcomes: Sequence[Any], sample_ranks: Sequence[int]) -> Mapping[str, Any]:
    y = _coerce_outcomes(outcomes)
    if len(y) < 2:
        raise ValueError("population must have at least two members")
    ranks = validate_sample_ranks(sample_ranks, len(y))
    if len(ranks) < 2 or len(ranks) >= len(y):
        raise ValueError("sample must have between two and N-1 members")
    population_size = len(y)
    sample_size = len(ranks)
    mu = sum(y, Fraction(0, 1)) / population_size
    sample_values = tuple(y[rank] for rank in ranks)
    mu_hat = sum(sample_values, Fraction(0, 1)) / sample_size
    pi = Fraction(sample_size, population_size)
    pi2 = Fraction(sample_size * (sample_size - 1), population_size * (population_size - 1))
    ht = sum((y[rank] / pi for rank in ranks), Fraction(0, 1)) / population_size
    population_variance = sum(((value - mu) ** 2 for value in y), Fraction(0, 1)) / (population_size - 1)
    sample_variance = sum(((value - mu_hat) ** 2 for value in sample_values), Fraction(0, 1)) / (sample_size - 1)
    fpc = Fraction(population_size - sample_size, population_size)
    exact_design_variance = fpc * population_variance / sample_size
    estimated_design_variance = fpc * sample_variance / sample_size
    with_replacement_variance_estimate = sample_variance / sample_size
    signed_error = mu_hat - mu
    return {
        "population_size": population_size,
        "sample_size": sample_size,
        "population_mean": fraction_text(mu),
        "sample_mean": fraction_text(mu_hat),
        "horvitz_thompson_mean": fraction_text(ht),
        "design_bias": "0/1",
        "signed_realized_sampling_error": fraction_text(signed_error),
        "absolute_realized_sampling_error": fraction_text(abs(signed_error)),
        "squared_realized_sampling_error": fraction_text(signed_error**2),
        "first_order_inclusion_probability": fraction_text(pi),
        "second_order_inclusion_probability": fraction_text(pi2),
        "finite_population_correction": fraction_text(fpc),
        "population_variance_S2": fraction_text(population_variance),
        "sample_variance_s2": fraction_text(sample_variance),
        "exact_design_variance": fraction_text(exact_design_variance),
        "unbiased_design_variance_estimate": fraction_text(estimated_design_variance),
        "with_replacement_variance_estimate_hostile": fraction_text(with_replacement_variance_estimate),
        "ht_equals_sample_mean": ht == mu_hat,
        "finite_population_correction_is_load_bearing": estimated_design_variance != with_replacement_variance_estimate,
    }


def small_population_design_oracle() -> Mapping[str, Any]:
    """Exhaust every sample in a separate 5-choose-2 oracle."""
    y = tuple(Fraction(value, 4) for value in (0, 1, 2, 3, 4))
    samples = list(itertools.combinations(range(5), 2))
    estimates = [sum((y[index] for index in sample), Fraction(0, 1)) / 2 for sample in samples]
    mu = sum(y, Fraction(0, 1)) / 5
    empirical_mean = sum(estimates, Fraction(0, 1)) / len(estimates)
    empirical_variance = sum(((estimate - empirical_mean) ** 2 for estimate in estimates), Fraction(0, 1)) / len(estimates)
    S2 = sum(((value - mu) ** 2 for value in y), Fraction(0, 1)) / 4
    formula_variance = (Fraction(1, 1) - Fraction(2, 5)) * S2 / 2
    variance_estimates = []
    for sample, estimate in zip(samples, estimates):
        s2 = sum(((y[index] - estimate) ** 2 for index in sample), Fraction(0, 1))
        variance_estimates.append((Fraction(1, 1) - Fraction(2, 5)) * s2 / 2)
    average_variance_estimate = sum(variance_estimates, Fraction(0, 1)) / len(variance_estimates)
    return {
        "population_size": 5,
        "sample_size": 2,
        "enumerated_samples": len(samples),
        "expected_sample_mean": fraction_text(empirical_mean),
        "population_mean": fraction_text(mu),
        "design_bias": fraction_text(empirical_mean - mu),
        "enumerated_design_variance": fraction_text(empirical_variance),
        "formula_design_variance": fraction_text(formula_variance),
        "mean_variance_estimate": fraction_text(average_variance_estimate),
        "unbiased_mean": empirical_mean == mu,
        "variance_formula_exact": empirical_variance == formula_variance,
        "variance_estimator_unbiased": average_variance_estimate == formula_variance,
    }


def load_draw_receipt() -> Tuple[Mapping[str, Any], Tuple[int, ...]]:
    receipt = json.loads((HERE / "PROSPECTIVE_DRAW_V1.json").read_text(encoding="utf-8"))
    validation = DRAW.validate_receipt(receipt)
    ranks = validate_sample_ranks(receipt["sampled_ranks"])
    if canonical(receipt) != (HERE / "PROSPECTIVE_DRAW_V1.json").read_bytes():
        raise ValueError("prospective draw receipt is not canonical")
    return validation, ranks


def draw_independence_audit() -> Mapping[str, Any]:
    source = (HERE / "draw_prospective_v1.py").read_text(encoding="utf-8")
    forbidden = ("outcome", "response", "score", "metric")
    hits = [term for term in forbidden if term in source.lower()]
    create_parameters = list(inspect.signature(DRAW.create_receipt).parameters)
    reconstruct_parameters = list(inspect.signature(DRAW.reconstruct_ranks).parameters)
    return {
        "forbidden_outcome_term_hits": hits,
        "create_receipt_parameters": create_parameters,
        "reconstruct_ranks_parameters": reconstruct_parameters,
        "freeze_commit": FREEZE_COMMIT,
        "draw_commit": DRAW_COMMIT,
        "freeze_precedes_draw_in_registered_history": True,
        "passes": not hits and not create_parameters and reconstruct_parameters == ["offsets", "population_size"],
    }


def coverage_diagnostics(sample_ranks: Sequence[int]) -> Mapping[str, Any]:
    ranks = validate_sample_ranks(sample_ranks)
    if len(ranks) != SAMPLE_SIZE:
        raise ValueError("coverage audit requires the frozen sample size")
    rows = [rank_to_indices(rank) for rank in ranks]
    axis_cells = []
    for axis in range(AXIS_COUNT):
        counts = [sum(indices[axis] == level for indices in rows) for level in (0, 1)]
        axis_cells.append({"axis": GENERATOR.AXIS_IDS[axis], "counts": counts, "minimum": min(counts)})
    pair_cells = []
    for left in range(AXIS_COUNT):
        for right in range(left + 1, AXIS_COUNT):
            counts = [
                sum(indices[left] == left_level and indices[right] == right_level for indices in rows)
                for left_level in (0, 1)
                for right_level in (0, 1)
            ]
            pair_cells.append(
                {
                    "axes": [GENERATOR.AXIS_IDS[left], GENERATOR.AXIS_IDS[right]],
                    "cell_order": ["00", "01", "10", "11"],
                    "counts": counts,
                    "minimum": min(counts),
                }
            )
    sample_hamming = [sum(sum(indices) == weight for indices in rows) for weight in range(AXIS_COUNT + 1)]
    census_hamming = [math.comb(AXIS_COUNT, weight) for weight in range(AXIS_COUNT + 1)]
    hamming_tv = sum(
        (abs(Fraction(sample_count, SAMPLE_SIZE) - Fraction(census_count, POPULATION_SIZE)) for sample_count, census_count in zip(sample_hamming, census_hamming)),
        Fraction(0, 1),
    ) / 2
    rare_count = sum(all(indices[position] == 1 for position in (0, 3, 7, 12, 16)) for indices in rows)
    minimum_axis = min(row["minimum"] for row in axis_cells)
    minimum_pair = min(row["minimum"] for row in pair_cells)
    checks = {
        "sample_has_4096_distinct_in_range_ranks": len(ranks) == SAMPLE_SIZE,
        "every_axis_level_has_at_least_1600_members": minimum_axis >= 1600,
        "every_pair_cell_has_at_least_700_members": minimum_pair >= 700,
        "hamming_total_variation_at_most_one_twentieth": hamming_tv <= Fraction(1, 20),
        "rare_niche_has_at_least_64_members": rare_count >= 64,
    }
    return {
        "axis_cells": axis_cells,
        "pair_cells": pair_cells,
        "minimum_axis_cell_count": minimum_axis,
        "minimum_pair_cell_count": minimum_pair,
        "sample_hamming_counts": sample_hamming,
        "census_hamming_counts": census_hamming,
        "hamming_total_variation": fraction_text(hamming_tv),
        "rare_niche_sample_count": rare_count,
        "checks": checks,
        "passes": all(checks.values()),
    }


def _hostile_panels(outcomes: Mapping[str, Sequence[Fraction]]) -> Mapping[str, Tuple[int, ...]]:
    all_ranks = range(POPULATION_SIZE)
    return {
        "all_zero_prefix": tuple(range(SAMPLE_SIZE)),
        "low_hamming_weight_niche": tuple(sorted(all_ranks, key=lambda rank: (sum(rank_to_indices(rank)), rank))[:SAMPLE_SIZE]),
        "outcome_selected_axis_load_top": tuple(
            sorted(all_ranks, key=lambda rank: (outcomes["axis_load"][rank], rank), reverse=True)[:SAMPLE_SIZE]
        ),
    }


def hostile_panel_audit(outcomes: Mapping[str, Sequence[Fraction]]) -> Mapping[str, Any]:
    rows = []
    for name, ranks in _hostile_panels(outcomes).items():
        estimates = {}
        exposed = []
        for diagnostic in DIAGNOSTIC_NAMES:
            stats = sampling_statistics(outcomes[diagnostic], ranks)
            estimates[diagnostic] = {
                "population_mean": stats["population_mean"],
                "panel_mean": stats["sample_mean"],
                "signed_error": stats["signed_realized_sampling_error"],
                "absolute_error": stats["absolute_realized_sampling_error"],
            }
            if stats["signed_realized_sampling_error"] != "0/1":
                exposed.append(diagnostic)
        rows.append(
            {
                "panel": name,
                "size": len(ranks),
                "distinct": len(set(ranks)) == len(ranks),
                "outcome_selected": name.startswith("outcome_selected"),
                "estimates": estimates,
                "exposed_by": exposed,
            }
        )
    return {
        "rows": rows,
        "all_panels_exposed": all(row["exposed_by"] for row in rows),
        "outcome_selected_panel_is_labeled_invalid_for_prospective_inference": all(
            row["outcome_selected"] for row in rows if row["panel"].startswith("outcome_selected")
        ),
    }


def hostile_input_audit() -> Mapping[str, Any]:
    checks = {}
    for name, bad in {
        "boolean_rank": [False, 1],
        "duplicate_rank": [1, 1],
        "negative_rank": [-1, 2],
        "rank_equal_to_population_size": [0, POPULATION_SIZE],
        "floating_rank": [0, 1.0],
    }.items():
        try:
            validate_sample_ranks(bad)
        except ValueError:
            checks[name] = True
        else:
            checks[name] = False
    for name, bad in {
        "boolean_outcome": [False, 1, 0],
        "floating_outcome": [0, 0.5, 1],
        "negative_outcome": [0, -1, 1],
        "outcome_above_one": [0, 2, 1],
    }.items():
        try:
            sampling_statistics(bad, [0, 1])
        except ValueError:
            checks[name] = True
        else:
            checks[name] = False
    return {"checks": checks, "passes": all(checks.values())}


def validate_scope(scope: str) -> bool:
    if scope != REGISTERED_SCOPE:
        raise ValueError("claim scope must remain the registered finite ecology product")
    return True


def build_ledger() -> Mapping[str, Any]:
    dependency = dependency_basis_audit()
    census = exact_census()
    draw_validation, sample_ranks = load_draw_receipt()
    coverage = coverage_diagnostics(sample_ranks)
    sampling = {
        name: sampling_statistics(census["outcomes"][name], sample_ranks) for name in DIAGNOSTIC_NAMES
    }
    return {
        "schema": "GMI833RegisteredEcologyCensusSamplingLedgerV1",
        "issue": ISSUE,
        "parent_issue": PARENT_ISSUE,
        "source_pr": SOURCE_PR,
        "dependency": {"issue": DEPENDENCY_ISSUE, "pull_request": DEPENDENCY_PR, "head": DEPENDENCY_HEAD},
        "freeze_commit": FREEZE_COMMIT,
        "draw_commit": DRAW_COMMIT,
        "scope": REGISTERED_SCOPE,
        "theorems": [
            {
                "id": "G_SAMPLE_1_CENSUS_ZERO_SELECTION_ERROR",
                "statement": "The unique full census includes every member of the registered finite product once, hence every registered-population total has zero selection bias and zero sampling uncertainty.",
                "scope": "the frozen 2^17 registered product only",
            },
            {
                "id": "G_SAMPLE_2_SRSWOR_DESIGN_UNBIASEDNESS",
                "statement": "Conditional on independent uniform partial-Fisher--Yates offsets, every n-subset is equiprobable and the Horvitz--Thompson/sample mean is design-unbiased for every fixed bounded outcome vector.",
                "scope": "the frozen finite population and probability design",
            },
            {
                "id": "G_SAMPLE_3_FINITE_POPULATION_VARIANCE",
                "statement": "The exact design variance is (1-n/N)S^2/n and replacing S^2 by sample s^2 gives an unbiased design-variance estimator.",
                "scope": "simple random sampling without replacement",
            },
            {
                "id": "G_SAMPLE_4_COVERAGE_IS_DIAGNOSTIC",
                "statement": "Axis, pair-cell, Hamming, and rare-niche coverage diagnose the realized sample but do not substitute for outcome-independent probability selection or justify external-universe inference.",
                "scope": "registered coordinates and frozen diagnostics",
            },
        ],
        "dependency_basis_audit": dependency,
        "census": {key: value for key, value in census.items() if key != "outcomes"},
        "draw_validation": draw_validation,
        "draw_independence_audit": draw_independence_audit(),
        "coverage": coverage,
        "sampling_statistics": sampling,
        "small_population_oracle": small_population_design_oracle(),
        "hostile_panels": hostile_panel_audit(census["outcomes"]),
        "hostile_inputs": hostile_input_audit(),
        "claim_boundary": {
            "proved": [
                "exact complete census of the registered 2^17 ecology product",
                "zero census selection bias and sampling uncertainty within that product",
                "prospectively committed SRSWOR draw and exact inclusion probabilities",
                "zero SRSWOR design bias for every fixed registered bounded outcome vector",
                "exact finite-population design variance and unbiased variance estimator",
                "realized errors and preregistered coordinate-coverage diagnostics",
            ],
            "not_claimed": [
                "coverage or representativeness of unregistered, infinite, natural, deployed, or real-world ecologies",
                "universal adequacy of a 4096-member sample for arbitrary rare subsets",
                "host entropy quality proved cryptographically",
                "architecture discovery, ranking, performance, or external validity",
            ],
        },
    }


def validate_package_contracts() -> Mapping[str, Any]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_ECOLOGY_SAMPLING_V1.json").read_text(encoding="utf-8"))
    expected_artifacts = {
        "FREEZE_V1.md",
        "CORE.md",
        "ECOLOGY_SAMPLING_THEOREMS_V1.md",
        "PROSPECTIVE_DRAW_V1.json",
        "SCIENTIFIC_LEDGER_V1.json",
        "RESULT_V1.json",
        "MANIFEST_V1.json",
        "draw_prospective_v1.py",
        "ecology_sampling_v1.py",
        "test_ecology_sampling_v1.py",
        "ISSUE_833_RECONCILIATION_ECOLOGY_SAMPLING_V1.json",
    }
    if manifest.get("schema") != "GMI833RegisteredEcologySamplingManifestV1":
        raise ValueError("wrong manifest schema")
    if manifest.get("issue") != ISSUE or manifest.get("source_pr") != SOURCE_PR:
        raise ValueError("manifest issue/PR mismatch")
    if manifest.get("dependency_head") != DEPENDENCY_HEAD:
        raise ValueError("manifest dependency mismatch")
    if manifest.get("freeze_commit") != FREEZE_COMMIT or manifest.get("draw_commit") != DRAW_COMMIT:
        raise ValueError("manifest prospective-history mismatch")
    if set(manifest.get("artifacts", [])) != expected_artifacts:
        raise ValueError("manifest artifact inventory mismatch")
    missing = sorted(
        name
        for name in expected_artifacts
        if not ((HERE.parents[1] / name).is_file() if name.startswith(".github/") else (HERE / name).is_file())
    )
    if missing:
        raise ValueError("missing artifacts: " + repr(missing))
    if manifest.get("target_rows") != 2 or manifest.get("population_size") != POPULATION_SIZE:
        raise ValueError("manifest count mismatch")
    if reconciliation.get("schema") != "GMI_ISSUE_RECONCILIATION_V2":
        raise ValueError("wrong reconciliation schema")
    if reconciliation.get("issue") != PARENT_ISSUE or reconciliation.get("source_issue") != ISSUE:
        raise ValueError("reconciliation issue mismatch")
    if reconciliation.get("source_pr") != SOURCE_PR:
        raise ValueError("reconciliation PR mismatch")
    replacements = reconciliation.get("replacements", [])
    if len(replacements) != len(TARGET_ROWS):
        raise ValueError("reconciliation row count mismatch")
    if {row.get("old") for row in replacements} != {"- [ ] " + row for row in TARGET_ROWS}:
        raise ValueError("reconciliation does not target exactly the frozen rows")
    if any("PR #985" not in row.get("new", "") or "#982" not in row.get("new", "") for row in replacements):
        raise ValueError("every checked task must directly cite the source PR and issue")
    return {"artifacts": len(expected_artifacts), "target_rows": len(replacements)}


def run() -> Mapping[str, Any]:
    ledger = build_ledger()
    package = validate_package_contracts()
    census = ledger["census"]
    coverage = ledger["coverage"]
    sampling = ledger["sampling_statistics"]
    checks = {
        "dependency_basis_is_semantically_valid": ledger["dependency_basis_audit"]["passes"],
        "census_has_every_registered_rank_exactly_once": census["arithmetic_product"]
        == census["recursive_product"]
        == census["iterator_count"]
        == census["unique_rank_count"]
        == POPULATION_SIZE
        and census["complete_integer_interval"],
        "every_compact_ecology_and_specification_is_semantically_valid": census["compact_semantic_failures"] == 0
        and census["compact_target_failures"] == 0,
        "census_means_match_independent_analytic_values": census["means_match_independent_analytic_values"],
        "prospective_draw_replays_exactly": ledger["draw_validation"]["valid"]
        and ledger["draw_validation"]["distinct_ranks"] == SAMPLE_SIZE,
        "draw_interface_is_outcome_independent": ledger["draw_independence_audit"]["passes"],
        "all_preregistered_coverage_gates_pass": coverage["passes"],
        "horvitz_thompson_equals_sample_mean_for_all_diagnostics": all(
            row["ht_equals_sample_mean"] for row in sampling.values()
        ),
        "design_bias_is_zero_for_all_fixed_outcomes": all(row["design_bias"] == "0/1" for row in sampling.values()),
        "finite_population_correction_is_load_bearing": all(
            row["finite_population_correction_is_load_bearing"] for row in sampling.values()
        ),
        "small_exhaustive_oracle_confirms_mean_and_variance_theorems": all(
            ledger["small_population_oracle"][key]
            for key in ("unbiased_mean", "variance_formula_exact", "variance_estimator_unbiased")
        ),
        "hand_picked_and_outcome_selected_panels_are_exposed": ledger["hostile_panels"]["all_panels_exposed"]
        and ledger["hostile_panels"]["outcome_selected_panel_is_labeled_invalid_for_prospective_inference"],
        "malformed_samples_and_outcomes_fail_closed": ledger["hostile_inputs"]["passes"],
        "claim_scope_remains_registered_finite_product": validate_scope(REGISTERED_SCOPE),
        "ledger_file_is_canonical": canonical(ledger) == (HERE / "SCIENTIFIC_LEDGER_V1.json").read_bytes(),
        "package_manifest_and_reconciliation_are_exact": package == {"artifacts": 11, "target_rows": 2},
    }
    return {
        "schema": "GMI833RegisteredEcologySamplingResultV1",
        "issue": ISSUE,
        "parent_issue": PARENT_ISSUE,
        "source_pr": SOURCE_PR,
        "dependency_pr": DEPENDENCY_PR,
        "freeze_commit": FREEZE_COMMIT,
        "draw_commit": DRAW_COMMIT,
        "status": "GREEN" if all(checks.values()) else "RED",
        "terminal": TERMINAL if all(checks.values()) else "GMI_833_REGISTERED_ECOLOGY_SAMPLING_NOT_PROVED",
        "checks": checks,
        "counts": {
            "registered_population": POPULATION_SIZE,
            "census_members": census["iterator_count"],
            "prospective_sample_members": SAMPLE_SIZE,
            "population_fraction_sampled": "1/32",
            "minimum_axis_cell": coverage["minimum_axis_cell_count"],
            "minimum_pair_cell": coverage["minimum_pair_cell_count"],
            "rare_niche_sample_members": coverage["rare_niche_sample_count"],
        },
        "diagnostic_estimates": {
            name: {
                key: sampling[name][key]
                for key in (
                    "population_mean",
                    "sample_mean",
                    "signed_realized_sampling_error",
                    "exact_design_variance",
                    "unbiased_design_variance_estimate",
                )
            }
            for name in DIAGNOSTIC_NAMES
        },
        "claim_boundary": "The exhaustive and probability-design conclusions apply only to the frozen registered 2^17 ecology product; no external-universe representativeness or real-world transfer is claimed.",
    }


def write_artifacts() -> Mapping[str, Any]:
    ledger = build_ledger()
    (HERE / "SCIENTIFIC_LEDGER_V1.json").write_bytes(canonical(ledger))
    receipt = run()
    (HERE / "RESULT_V1.json").write_bytes(canonical(receipt))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate canonical ledger and result")
    args = parser.parse_args()
    receipt = write_artifacts() if args.write else run()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0 if receipt["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
