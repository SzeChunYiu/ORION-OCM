#!/usr/bin/env python3
"""Exact finite collapse rates and syntax-free morphology metrics for #833-F."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from hashlib import sha1
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import sys
from typing import Callable, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
SOURCE_MAIN = "b30237c229b2c3fd4016de19c5fa9c155c0a7484"
FREEZE_COMMIT = "866a2bb1d7b2f304977e3c7a2f6fa377a0d8dc0a"
SOURCE_ISSUE = 983
SOURCE_PR = 984
PARENT_ISSUE = 833
CLAIM_CEILING = "GMI_833_FINITE_COLLAPSE_AND_SEMANTIC_RESOURCE_DEVELOPMENTAL_METRICS_AT_REGISTERED_SCOPE"
REGISTERED_BUDGETS = ((1, 1), (2, 1), (1, 2), (2, 2))
REGISTERED_INTERFACE_WORDS = ((), (0,), (1,))
REGISTERED_STEP_CAP = 6
MAX_RESOURCE = (2, 2)
MAX_HISTORY_LENGTH = 4
BASE_WEIGHTS = None  # assigned after MetricWeights is declared
PERTURBED_WEIGHTS = None
WEIGHT_EPSILON = Fraction(1, 100)
UNIFORM_PERTURBATION_BOUND = Fraction(9, 100)
NOVELTY_THRESHOLD = Fraction(11, 2)
FORBIDDEN_PROMOTIONS = (
    "UNBOUNDED_PROGRAM_EQUIVALENCE_DECIDED",
    "UNIVERSAL_SEMANTIC_QUOTIENT",
    "ARCHITECTURE_FREE_IN_ABSOLUTE_SENSE",
    "UNIQUE_OR_UNBIASED_GRAMMAR",
    "SCALABLE_LARGE_BUDGET_SAMPLING",
    "MILLION_SCALE_GENERATION",
    "HUNDRED_MILLION_SCALE_GENERATION",
    "ALL_SEARCH_LAW_REACHABILITY_MEASURED",
    "PARETO_FRONT_DENSITY_MEASURED",
    "CLUSTERING_STABILITY_VALIDATED",
    "KNOWN_FAMILY_RECOVERY",
    "UNKNOWN_CLUSTER_VALIDATED",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    (
        "finite_candidate_space",
        "research/gmi-833-finite-candidate-space-v1/RESULT_V1.json",
        "4086d6bea440d626e48d92eb35d39267a010589e",
        "claim_ceiling",
        "GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_REGISTERED_SCOPE",
    ),
    (
        "grammar_remint_boundary",
        "research/gmi-833-g0-grammar-bias-v1/RESULT_V1.json",
        "e903033615946a71f2f0859cda42e5b902e0d693",
        "claim_ceiling",
        "GMI_FINITE_GRAMMAR_BIAS_AND_REMINT_BOUNDARY_AT_REGISTERED_G0_SCOPE",
    ),
    (
        "robustness_controls",
        "research/gmi-833-robustness-controls-v1/RESULT_V1.json",
        "c3ff199c343b6905dabe8e3aefdc5958a2c8a06a",
        "claim_ceiling",
        "GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE",
    ),
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


F = _load_module(
    "gmi833_f2_finite_candidate_parent",
    HERE.parent / "gmi-833-finite-candidate-space-v1" / "finite_candidate_space_v1.py",
)


Observation = tuple[str, tuple[int, ...]]
ObservationTable = tuple[Observation, ...]
ResourceVector = tuple[int, int]


def _exact_positive_int(value: object, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive exact integer")
    return value


def validate_observations(observations: object) -> ObservationTable:
    if type(observations) is not tuple or len(observations) != len(REGISTERED_INTERFACE_WORDS):
        raise ValueError("observations must be the complete registered-interface tuple")
    allowed = {"HALTED", "BLOCKED_INPUT", "STEP_LIMIT"}
    for row in observations:
        if type(row) is not tuple or len(row) != 2 or row[0] not in allowed or type(row[1]) is not tuple:
            raise ValueError("malformed protected observation")
        if any(type(value) is not int or value < 0 for value in row[1]):
            raise ValueError("protected output must contain exact natural numbers")
    return observations


def validate_resources(resources: object) -> ResourceVector:
    if type(resources) is not tuple or len(resources) != 2:
        raise ValueError("resources must be an exact two-coordinate tuple")
    if any(type(value) is not int or value <= 0 for value in resources):
        raise ValueError("resource coordinates must be positive exact integers")
    if any(resources[index] > MAX_RESOURCE[index] for index in range(2)):
        raise ValueError("resource vector exceeds the registered metric domain")
    return resources


@dataclass(frozen=True)
class Milestone:
    observations: ObservationTable
    resources: ResourceVector

    def __post_init__(self) -> None:
        validate_observations(self.observations)
        validate_resources(self.resources)


@lru_cache(maxsize=1)
def registered_interface():
    return F.ObservationInterface(REGISTERED_INTERFACE_WORDS, REGISTERED_STEP_CAP)


def all_halt_program(resources: ResourceVector):
    code_cells, register_cells = validate_resources(resources)
    return F.CandidateProgram(register_cells, tuple(F.Instruction("HALT") for _ in range(code_cells)))


@lru_cache(maxsize=None)
def program_milestone(program) -> Milestone:
    F.validate_program(program)
    resources = program.resource_vector()
    validate_resources(resources)
    return Milestone(F.semantic_key(program, registered_interface()), resources)


@lru_cache(maxsize=1)
def seed_milestone() -> Milestone:
    return program_milestone(all_halt_program((1, 1)))


def validate_history(history: object, final: Milestone) -> tuple[Milestone, ...]:
    if type(history) is not tuple or not history or len(history) > MAX_HISTORY_LENGTH:
        raise ValueError("development history must be a nonempty tuple of at most four milestones")
    if any(not isinstance(row, Milestone) for row in history):
        raise ValueError("development history contains a non-milestone")
    if history[0] != seed_milestone():
        raise ValueError("development history must start at the registered seed")
    if history[-1] != final:
        raise ValueError("development history must end at the record's final morphology")
    for left, right in zip(history, history[1:]):
        same_semantics = left.observations == right.observations
        same_resources = left.resources == right.resources
        resource_add = (
            same_semantics
            and sum(right.resources[index] - left.resources[index] for index in range(2)) == 1
            and all(right.resources[index] >= left.resources[index] for index in range(2))
        )
        semantic_adoption = same_resources and not same_semantics
        if not (resource_add or semantic_adoption):
            raise ValueError("history step violates the registered development law")
    return history


@dataclass(frozen=True)
class MorphologyRecord:
    observations: ObservationTable
    resources: ResourceVector
    history: tuple[Milestone, ...]

    def __post_init__(self) -> None:
        validate_observations(self.observations)
        validate_resources(self.resources)
        validate_history(self.history, Milestone(self.observations, self.resources))


@lru_cache(maxsize=None)
def canonical_history(program) -> tuple[Milestone, ...]:
    F.validate_program(program)
    target_resources = validate_resources(program.resource_vector())
    target = program_milestone(program)
    history = [seed_milestone()]
    current = (1, 1)
    while current[0] < target_resources[0]:
        current = (current[0] + 1, current[1])
        history.append(program_milestone(all_halt_program(current)))
    while current[1] < target_resources[1]:
        current = (current[0], current[1] + 1)
        history.append(program_milestone(all_halt_program(current)))
    if history[-1] != target:
        history.append(target)
    result = tuple(history)
    validate_history(result, target)
    return result


@lru_cache(maxsize=None)
def morphology_record(program) -> MorphologyRecord:
    target = program_milestone(program)
    return MorphologyRecord(target.observations, target.resources, canonical_history(program))


@dataclass(frozen=True)
class MetricWeights:
    semantic: Fraction
    resource: Fraction
    developmental: Fraction

    def __post_init__(self) -> None:
        for label, value in (
            ("semantic", self.semantic),
            ("resource", self.resource),
            ("developmental", self.developmental),
        ):
            if type(value) is not Fraction or value <= 0:
                raise ValueError(f"{label} weight must be a strictly positive exact Fraction")

    def as_tuple(self) -> tuple[Fraction, Fraction, Fraction]:
        return (self.semantic, self.resource, self.developmental)


BASE_WEIGHTS = MetricWeights(Fraction(5), Fraction(3), Fraction(2))
PERTURBED_WEIGHTS = MetricWeights(Fraction(501, 100), Fraction(299, 100), Fraction(201, 100))


def semantic_component(left: ObservationTable, right: ObservationTable) -> int:
    validate_observations(left)
    validate_observations(right)
    return sum(a != b for a, b in zip(left, right))


def resource_component(left: ResourceVector, right: ResourceVector) -> int:
    validate_resources(left)
    validate_resources(right)
    return sum(abs(a - b) for a, b in zip(left, right))


def developmental_component(left: tuple[Milestone, ...], right: tuple[Milestone, ...]) -> int:
    if type(left) is not tuple or type(right) is not tuple or not left or not right:
        raise ValueError("developmental distance requires nonempty milestone tuples")
    if len(left) > MAX_HISTORY_LENGTH or len(right) > MAX_HISTORY_LENGTH:
        raise ValueError("developmental history exceeds the registered bound")
    if any(not isinstance(row, Milestone) for row in left + right):
        raise ValueError("developmental distance received a malformed history")
    previous = list(range(len(right) + 1))
    for i, left_row in enumerate(left, 1):
        current = [i]
        for j, right_row in enumerate(right, 1):
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + int(left_row != right_row),
                )
            )
        previous = current
    return previous[-1]


def morphology_distance(
    left: MorphologyRecord,
    right: MorphologyRecord,
    weights: MetricWeights = BASE_WEIGHTS,
) -> Fraction:
    if not isinstance(left, MorphologyRecord) or not isinstance(right, MorphologyRecord):
        raise ValueError("morphology distance requires two validated records")
    if not isinstance(weights, MetricWeights):
        raise ValueError("weights must be MetricWeights")
    return (
        weights.semantic * semantic_component(left.observations, right.observations)
        + weights.resource * resource_component(left.resources, right.resources)
        + weights.developmental * developmental_component(left.history, right.history)
    )


def novelty_score(
    record: MorphologyRecord,
    archive: tuple[MorphologyRecord, ...],
    weights: MetricWeights = BASE_WEIGHTS,
) -> Fraction:
    if not isinstance(record, MorphologyRecord):
        raise ValueError("novelty query must be a MorphologyRecord")
    if type(archive) is not tuple or not archive or any(not isinstance(row, MorphologyRecord) for row in archive):
        raise ValueError("novelty archive must be a nonempty tuple of morphology records")
    if len(set(archive)) != len(archive):
        raise ValueError("novelty archive must not contain duplicate morphologies")
    return min(morphology_distance(record, reference, weights) for reference in archive)


def fraction_pair(value: Fraction) -> tuple[int, int]:
    if type(value) is not Fraction:
        raise ValueError("fraction_pair requires an exact Fraction")
    return (value.numerator, value.denominator)


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def collapse_statistics(programs: Sequence[object]) -> dict[str, object]:
    candidates = tuple(programs)
    if not candidates:
        raise ValueError("collapse measurement requires a nonempty candidate sequence")
    for program in candidates:
        F.validate_program(program)
    codes = [program.canonical_code() for program in candidates]
    if len(codes) != len(set(codes)):
        raise ValueError("collapse measurement requires syntactically duplicate-free presentations")
    quotient = F.semantic_quotient(candidates, registered_interface())
    multiplicities = tuple(int(row["multiplicity"]) for row in quotient)
    presentation_count = len(candidates)
    class_count = len(multiplicities)
    collapsed = presentation_count - class_count
    equivalent_pairs = sum(value * (value - 1) // 2 for value in multiplicities)
    total_pairs = presentation_count * (presentation_count - 1) // 2
    histogram = Counter(multiplicities)
    singleton_count = histogram.get(1, 0)
    return {
        "presentation_count": presentation_count,
        "semantic_class_count": class_count,
        "collapsed_presentation_count": collapsed,
        "collapse_fraction": fraction_pair(Fraction(collapsed, presentation_count)),
        "equivalent_unordered_pair_count": equivalent_pairs,
        "total_unordered_pair_count": total_pairs,
        "pair_collision_fraction": fraction_pair(
            Fraction(equivalent_pairs, total_pairs) if total_pairs else Fraction(0)
        ),
        "singleton_class_count": singleton_count,
        "singleton_presentation_fraction": fraction_pair(Fraction(singleton_count, presentation_count)),
        "multiplicity_histogram": tuple(sorted(histogram.items())),
    }


def _record_sort_key(record: MorphologyRecord) -> str:
    def milestone_json(row: Milestone) -> list[object]:
        return [
            [[status, list(output)] for status, output in row.observations],
            list(row.resources),
        ]

    payload = {
        "observations": [[status, list(output)] for status, output in record.observations],
        "resources": list(record.resources),
        "history": [milestone_json(row) for row in record.history],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


@lru_cache(maxsize=1)
def registered_programs():
    return F.enumerate_candidates(F.StructuralBudget(2, 2))


@lru_cache(maxsize=1)
def registered_records() -> tuple[MorphologyRecord, ...]:
    return tuple(morphology_record(program) for program in registered_programs())


@lru_cache(maxsize=1)
def distinct_registered_records() -> tuple[MorphologyRecord, ...]:
    return tuple(sorted(set(registered_records()), key=_record_sort_key))


@lru_cache(maxsize=1)
def registered_archive() -> tuple[MorphologyRecord, ...]:
    programs = F.enumerate_candidates(F.StructuralBudget(1, 1))
    return tuple(sorted({morphology_record(program) for program in programs}, key=_record_sort_key))


def _metric_axioms(values: tuple[object, ...], distance: Callable[[object, object], Fraction | int]) -> dict[str, int | bool]:
    matrix = [[distance(left, right) for right in values] for left in values]
    nonnegative_checks = 0
    symmetry_checks = 0
    identity_checks = 0
    triangle_checks = 0
    for i, left in enumerate(values):
        for j, right in enumerate(values):
            value = matrix[i][j]
            nonnegative_checks += 1
            if value < 0:
                raise ValueError("metric component became negative")
            symmetry_checks += 1
            if value != matrix[j][i]:
                raise ValueError("metric component lost symmetry")
            identity_checks += 1
            if (value == 0) != (left == right):
                raise ValueError("metric component lost identity of indiscernibles")
            for k in range(len(values)):
                triangle_checks += 1
                if matrix[i][k] > value + matrix[j][k]:
                    raise ValueError("metric component violated triangle inequality")
    return {
        "domain_size": len(values),
        "nonnegative_checks": nonnegative_checks,
        "symmetry_checks": symmetry_checks,
        "identity_checks": identity_checks,
        "triangle_checks": triangle_checks,
        "all_metric_axioms_hold": True,
    }


@lru_cache(maxsize=1)
def metric_axiom_census() -> dict[str, object]:
    records = distinct_registered_records()
    semantics = tuple(sorted({record.observations for record in records}))
    resources = tuple(sorted({record.resources for record in records}))
    histories = tuple(sorted({record.history for record in records}, key=repr))
    return {
        "semantic_factor": _metric_axioms(semantics, semantic_component),
        "resource_factor": _metric_axioms(resources, resource_component),
        "developmental_factor": _metric_axioms(histories, developmental_component),
        "weighted_product": _metric_axioms(
            records, lambda left, right: morphology_distance(left, right, BASE_WEIGHTS)
        ),
    }


@lru_cache(maxsize=1)
def novelty_census() -> dict[str, object]:
    records = distinct_registered_records()
    archive = registered_archive()
    scores = {record: novelty_score(record, archive) for record in records}
    zero_exact_checks = 0
    for record in records:
        zero_exact_checks += 1
        if (scores[record] == 0) != (record in archive):
            raise ValueError("novelty zero set differs from the archive")
    lipschitz_checks = 0
    for left in records:
        for right in records:
            lipschitz_checks += 1
            if abs(scores[left] - scores[right]) > morphology_distance(left, right):
                raise ValueError("archive novelty violated 1-Lipschitzness")

    programs = registered_programs()
    program_records = tuple(morphology_record(program) for program in programs)
    zero_distance_distinct_presentations = 0
    groups: dict[MorphologyRecord, int] = Counter(program_records)
    for size in groups.values():
        zero_distance_distinct_presentations += size * (size - 1) // 2
    if zero_distance_distinct_presentations <= 0:
        raise ValueError("registered census lacks a syntax-independence witness")

    same_final = next(record for record in records if record.resources == (2, 2))
    seed = seed_milestone()
    register_first = program_milestone(all_halt_program((1, 2)))
    fully_resourced_halt = program_milestone(all_halt_program((2, 2)))
    alternative_history = (seed, register_first, fully_resourced_halt)
    if fully_resourced_halt != Milestone(same_final.observations, same_final.resources):
        alternative_history = alternative_history + (Milestone(same_final.observations, same_final.resources),)
    alternative = MorphologyRecord(same_final.observations, same_final.resources, alternative_history)
    developmental_witness = morphology_distance(same_final, alternative)
    if developmental_witness <= 0:
        raise ValueError("development-history change did not affect morphology distance")

    return {
        "archive_morphology_count": len(archive),
        "distinct_registered_morphology_count": len(records),
        "novelty_zero_exact_checks": zero_exact_checks,
        "novelty_lipschitz_checks": lipschitz_checks,
        "zero_distance_distinct_syntax_pair_count": zero_distance_distinct_presentations,
        "development_only_witness_distance": fraction_text(developmental_witness),
        "novelty_score_histogram": {
            fraction_text(score): count
            for score, count in sorted(Counter(scores.values()).items())
        },
    }


@lru_cache(maxsize=1)
def remint_census() -> dict[str, object]:
    programs = registered_programs()
    baseline = tuple(morphology_record(program) for program in programs)
    token_bank = ("u0", "u1", "u2", "u3", "u4")
    checks = 0
    for permuted in permutations(token_bank):
        remint = dict(zip(F.SEMANTIC_OPS, permuted))
        for program, expected in zip(programs, baseline):
            decoded = F.decode_reminted(F.remint_program(program, remint), remint)
            if morphology_record(decoded) != expected:
                raise ValueError("certified grammar remint changed a morphology record")
            checks += 1

    hostile_original = F.CandidateProgram(1, (F.Instruction("INC", 0, 0),))
    honest = dict(zip(F.SEMANTIC_OPS, token_bank))
    dishonest = dict(honest)
    dishonest["INC"], dishonest["READ"] = dishonest["READ"], dishonest["INC"]
    hostile_changed = F.decode_reminted(F.remint_program(hostile_original, honest), dishonest)
    hostile_distance = morphology_distance(morphology_record(hostile_original), morphology_record(hostile_changed))
    if hostile_distance <= 0:
        raise ValueError("semantics-changing pseudo-remint escaped the metric")
    return {
        "certified_surface_remint_count": 120,
        "registered_presentation_count": len(programs),
        "morphology_record_invariance_checks": checks,
        "implied_ordered_distance_invariance_checks": 120 * len(programs) ** 2,
        "semantics_changing_hostile_detected": True,
        "hostile_morphology_distance": fraction_text(hostile_distance),
    }


@lru_cache(maxsize=1)
def perturbation_census() -> dict[str, object]:
    for base, changed in zip(BASE_WEIGHTS.as_tuple(), PERTURBED_WEIGHTS.as_tuple()):
        if abs(base - changed) > WEIGHT_EPSILON:
            raise ValueError("registered perturbation exceeds its coordinate bound")
    analytic_bound = WEIGHT_EPSILON * Fraction(3 + 2 + 4)
    if analytic_bound != UNIFORM_PERTURBATION_BOUND:
        raise ValueError("analytic perturbation bound drifted")

    records = distinct_registered_records()
    pair_checks = 0
    observed_pair_max = Fraction(0)
    for i, left in enumerate(records):
        for right in records[i + 1 :]:
            change = abs(
                morphology_distance(left, right, BASE_WEIGHTS)
                - morphology_distance(left, right, PERTURBED_WEIGHTS)
            )
            pair_checks += 1
            observed_pair_max = max(observed_pair_max, change)
            if change > analytic_bound:
                raise ValueError("registered pair exceeded the metric perturbation bound")

    archive = registered_archive()
    candidates = registered_records()
    base_scores = tuple(novelty_score(record, archive, BASE_WEIGHTS) for record in candidates)
    changed_scores = tuple(novelty_score(record, archive, PERTURBED_WEIGHTS) for record in candidates)
    score_checks = 0
    observed_score_max = Fraction(0)
    threshold_checks = 0
    for base, changed in zip(base_scores, changed_scores):
        delta = abs(base - changed)
        score_checks += 1
        observed_score_max = max(observed_score_max, delta)
        if delta > analytic_bound:
            raise ValueError("registered novelty score exceeded the perturbation bound")
        threshold_checks += 1
        if (base >= NOVELTY_THRESHOLD) != (changed >= NOVELTY_THRESHOLD):
            raise ValueError("registered novelty threshold classification changed")
        if abs(base - NOVELTY_THRESHOLD) <= analytic_bound:
            raise ValueError("threshold stability lacks a strict analytic margin")

    strict_order_checks = 0
    strict_gaps: list[Fraction] = []
    for i, left in enumerate(base_scores):
        for j in range(i + 1, len(base_scores)):
            right = base_scores[j]
            if left == right:
                continue
            strict_order_checks += 1
            strict_gaps.append(abs(left - right))
            changed_left, changed_right = changed_scores[i], changed_scores[j]
            if (left < right) != (changed_left < changed_right):
                raise ValueError("a strict registered novelty ordering changed")

    minimum_strict_gap = min(strict_gaps)
    minimum_threshold_margin = min(abs(score - NOVELTY_THRESHOLD) for score in base_scores)
    if minimum_strict_gap <= 2 * analytic_bound:
        raise ValueError("strict novelty orders lack the registered two-sided perturbation margin")
    if minimum_threshold_margin <= analytic_bound:
        raise ValueError("threshold labels lack the registered perturbation margin")

    return {
        "base_weights": [fraction_text(value) for value in BASE_WEIGHTS.as_tuple()],
        "perturbed_weights": [fraction_text(value) for value in PERTURBED_WEIGHTS.as_tuple()],
        "coordinate_epsilon": fraction_text(WEIGHT_EPSILON),
        "analytic_uniform_bound": fraction_text(analytic_bound),
        "distinct_morphology_pair_checks": pair_checks,
        "observed_max_pair_change": fraction_text(observed_pair_max),
        "candidate_novelty_bound_checks": score_checks,
        "observed_max_novelty_change": fraction_text(observed_score_max),
        "strict_novelty_order_checks": strict_order_checks,
        "minimum_base_strict_novelty_gap": fraction_text(minimum_strict_gap),
        "required_two_sided_order_margin": fraction_text(2 * analytic_bound),
        "threshold": fraction_text(NOVELTY_THRESHOLD),
        "minimum_base_threshold_margin": fraction_text(minimum_threshold_margin),
        "threshold_classification_checks": threshold_checks,
        "all_registered_stability_checks": True,
    }


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    while current.parent != current:
        if (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows: list[dict[str, object]] = []
    for name, relative, expected_blob, field, expected_claim in PARENT_PINS:
        path = root / relative
        if not path.is_file():
            rows.append({"name": name, "path": relative, "actual_blob": None, "blob_ok": False, "claim_ok": False})
            continue
        data = path.read_bytes()
        actual_blob = git_blob_sha(data)
        try:
            claim_ok = json.loads(data).get(field) == expected_claim
        except (UnicodeDecodeError, json.JSONDecodeError):
            claim_ok = False
        rows.append(
            {
                "name": name,
                "path": relative,
                "actual_blob": actual_blob,
                "blob_ok": actual_blob == expected_blob,
                "claim_ok": claim_ok,
            }
        )
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def _load_oracle():
    return _load_module("gmi833_f2_independent_collapse_oracle", HERE / "independent_collapse_oracle_v1.py")


@lru_cache(maxsize=1)
def collapse_census() -> dict[str, object]:
    oracle = _load_oracle()
    rows: list[dict[str, object]] = []
    direct_pair_checks = 0
    for code_cells, register_cells in REGISTERED_BUDGETS:
        candidates = F.enumerate_candidates(F.StructuralBudget(code_cells, register_cells))
        primary = collapse_statistics(candidates)
        keys = tuple(F.semantic_key(program, registered_interface()) for program in candidates)
        independent = oracle.direct_collapse_statistics(keys)
        if primary != independent:
            raise ValueError("primary collapse measurement disagrees with independent direct oracle")
        if sum(size * count for size, count in primary["multiplicity_histogram"]) != len(candidates):
            raise ValueError("collapse histogram does not reconstruct the census")
        direct_pair_checks += primary["total_unordered_pair_count"]
        rows.append(
            {
                "budget": [code_cells, register_cells],
                "presentation_count": primary["presentation_count"],
                "semantic_class_count": primary["semantic_class_count"],
                "collapsed_presentation_count": primary["collapsed_presentation_count"],
                "collapse_fraction": fraction_text(Fraction(*primary["collapse_fraction"])),
                "equivalent_unordered_pair_count": primary["equivalent_unordered_pair_count"],
                "total_unordered_pair_count": primary["total_unordered_pair_count"],
                "pair_collision_fraction": fraction_text(Fraction(*primary["pair_collision_fraction"])),
                "singleton_class_count": primary["singleton_class_count"],
                "singleton_presentation_fraction": fraction_text(
                    Fraction(*primary["singleton_presentation_fraction"])
                ),
                "multiplicity_histogram": {
                    str(size): count for size, count in primary["multiplicity_histogram"]
                },
                "independent_oracle_exact_match": True,
            }
        )
    return {
        "registered_interface": {
            "input_words": [list(word) for word in REGISTERED_INTERFACE_WORDS],
            "step_cap": REGISTERED_STEP_CAP,
        },
        "budget_rows": rows,
        "independent_direct_pair_comparisons": direct_pair_checks,
    }


def validate_scientific_ledger() -> dict[str, object]:
    ledger = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text(encoding="utf-8"))
    required = {
        "id",
        "statement",
        "scope",
        "assumptions",
        "dependencies",
        "falsifiers",
        "strongest_parent",
        "counterexample_methods",
        "limits",
    }
    claims = ledger.get("claims", [])
    gaps = ledger.get("open_gaps", [])
    if len(claims) != 5 or any(set(row) != required for row in claims):
        raise ValueError("scientific claim ledger schema/count drifted")
    if tuple(row["id"] for row in claims) != (
        "COLLAPSE-1",
        "MORPH-METRIC-1",
        "NOVELTY-1",
        "REMINT-1",
        "PERTURB-1",
    ):
        raise ValueError("scientific claim ledger IDs drifted")
    if any(not row["assumptions"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific claim ledger contains an empty discipline field")
    if len(gaps) < 7 or any(row.get("status") != "OPEN" for row in gaps):
        raise ValueError("larger-scope gaps must remain explicitly open")
    return {"claim_ledgers": 5, "open_gaps": len(gaps), "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"}


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
    reconciliation = json.loads(
        (HERE / "ISSUE_833_RECONCILIATION_FINITE_MORPHOLOGY_METRICS_V1.json").read_text(encoding="utf-8")
    )
    expected_old = (
        "- [ ] Measure duplicate/equivalence collapse rate.",
        "- [ ] Develop novelty metrics that are not mere syntactic distance.",
        "- [ ] Develop semantic/resource/developmental morphology distance.",
    )
    replacements = reconciliation.get("replacements", [])
    manifest_ok = (
        manifest.get("schema") == "GMI_833_FINITE_MORPHOLOGY_METRICS_MANIFEST_V1"
        and manifest.get("issue") == SOURCE_ISSUE
        and manifest.get("source_pr") == SOURCE_PR
        and manifest.get("parent_issue") == PARENT_ISSUE
        and manifest.get("source_main") == SOURCE_MAIN
        and manifest.get("freeze_commit") == FREEZE_COMMIT
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("target_rows") == 3
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
    )
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == PARENT_ISSUE
        and reconciliation.get("source_issue") == SOURCE_ISSUE
        and reconciliation.get("source_pr") == SOURCE_PR
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and tuple(row.get("old") for row in replacements) == expected_old
        and all(row.get("anchor") == "# F. Intelligence-space generator" for row in replacements)
        and all(row.get("new", "").startswith("- [x] ") and "PR #984 / #983" in row.get("new", "") for row in replacements)
    )
    if not manifest_ok or not reconciliation_ok:
        raise ValueError("manifest/reconciliation package contract drifted")
    return {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 3, "source_pr": SOURCE_PR}


def build_receipt(parent_audit: Mapping[str, object] | None = None) -> dict[str, object]:
    parent_audit = dict(parent_audit or audit_parents())
    collapse = collapse_census()
    axioms = metric_axiom_census()
    novelty = novelty_census()
    remints = remint_census()
    perturbation = perturbation_census()
    ledger = validate_scientific_ledger()
    package = validate_package_contracts()
    checks = {
        "parent_artifacts_exactly_pinned": bool(parent_audit.get("all_ok")),
        "collapse_oracle_exact_match": all(row["independent_oracle_exact_match"] for row in collapse["budget_rows"]),
        "metric_axioms_exhaustive": all(row["all_metric_axioms_hold"] for row in axioms.values()),
        "novelty_not_syntax_and_lipschitz": novelty["zero_distance_distinct_syntax_pair_count"] > 0
        and novelty["novelty_lipschitz_checks"] > 0,
        "all_surface_remints_invariant": remints["morphology_record_invariance_checks"] == 69_120,
        "semantics_changing_remint_detected": remints["semantics_changing_hostile_detected"],
        "bounded_metric_perturbation_stable": perturbation["all_registered_stability_checks"],
        "scientific_ledger_valid": ledger["claim_ledgers"] == 5,
        "package_contracts_valid": package["reconciliation_rows"] == 3,
        "larger_scope_claims_forbidden": "CLUSTERING_STABILITY_VALIDATED" in FORBIDDEN_PROMOTIONS,
    }
    return {
        "schema": "GMI_833_FINITE_MORPHOLOGY_METRICS_RESULT_V1",
        "issue": SOURCE_ISSUE,
        "source_pr": SOURCE_PR,
        "parent_issue": PARENT_ISSUE,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "checks": checks,
        "collapse_census": collapse,
        "metric_axiom_census": axioms,
        "novelty_census": novelty,
        "remint_census": remints,
        "perturbation_census": perturbation,
        "parent_audit": parent_audit,
        "scientific_ledger": ledger,
        "package_contracts": package,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
    }


def canonical_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, indent=2) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    receipt = canonical_json(build_receipt())
    if arguments == ("--write-result",):
        (HERE / "RESULT_V1.json").write_text(receipt, encoding="utf-8")
    elif not arguments:
        sys.stdout.write(receipt)
    else:
        raise SystemExit("usage: finite_morphology_metrics_v1.py [--write-result]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
