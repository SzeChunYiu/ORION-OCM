#!/usr/bin/env python3
"""Exact finite Pareto-front density on semantic/resource morphologies."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
SOURCE_MAIN = "883d13e852fa3904d202b5cae1aee474e0a12dfb"
FREEZE_COMMIT = "8fd7f1118402d580b947bba5eced1fa1b7f4e10a"
SOURCE_ISSUE = 994
SOURCE_PR = 996
PARENT_ISSUE = 833
CLAIM_CEILING = "GMI_833_FINITE_PARETO_DENSITY_AT_REGISTERED_G0_SCOPE"
REGISTERED_BUDGETS = ((1, 1), (2, 1), (1, 2), (2, 2))
REGISTERED_WORDS = ((), (0,), (1,))
REGISTERED_STEP_CAP = 6
FORBIDDEN_PROMOTIONS = (
    "UNIVERSAL_PARETO_DENSITY",
    "OBJECTIVE_OR_ECOLOGY_NEUTRAL_DENSITY",
    "UNIQUE_SCALAR_WINNER",
    "SCALABLE_LARGE_BUDGET_SAMPLING",
    "MILLION_SCALE_GENERATION",
    "HUNDRED_MILLION_SCALE_GENERATION",
    "ALL_SEARCH_LAW_REACHABILITY_MEASURED",
    "CLUSTERING_PERFORMED",
    "KNOWN_FAMILY_RECOVERY",
    "UNKNOWN_CLUSTER_VALIDATED",
    "CLUSTERING_STABILITY_VALIDATED",
    "UNBOUNDED_RESULT",
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
    "gmi833_f3_candidate_parent",
    HERE.parent / "gmi-833-finite-candidate-space-v1" / "finite_candidate_space_v1.py",
)
O = _load_module("gmi833_f3_frontier_oracle", HERE / "independent_frontier_oracle_v1.py")

Observation = tuple[str, tuple[int, ...]]
ObservationTable = tuple[Observation, ...]
ResourceVector = tuple[int, int]
BehaviorVector = tuple[int, int, int]


def validate_observations(value: object) -> ObservationTable:
    if type(value) is not tuple or len(value) != len(REGISTERED_WORDS):
        raise ValueError("observations must be the complete registered table")
    allowed = {"HALTED", "BLOCKED_INPUT", "STEP_LIMIT"}
    for row in value:
        if type(row) is not tuple or len(row) != 2:
            raise ValueError("observation rows must be pairs")
        status, output = row
        if status not in allowed or type(output) is not tuple:
            raise ValueError("malformed protected observation")
        if any(type(token) is not int or token < 0 for token in output):
            raise ValueError("protected outputs must contain exact natural numbers")
    return value


def validate_resources(value: object) -> ResourceVector:
    if type(value) is not tuple or len(value) != 2:
        raise ValueError("resources must be a two-coordinate tuple")
    if any(type(item) is not int or item <= 0 for item in value):
        raise ValueError("resource coordinates must be positive exact integers")
    return value


def behavioral_objectives(observations: ObservationTable) -> BehaviorVector:
    observations = validate_observations(observations)
    termination = sum(status == "HALTED" for status, _ in observations)
    copy = sum(observations[index][1] == REGISTERED_WORDS[index] for index in (1, 2))
    productive = sum(bool(output) for _, output in observations)
    return (termination, copy, productive)


@dataclass(frozen=True)
class MorphologyPoint:
    observations: ObservationTable
    resources: ResourceVector

    def __post_init__(self) -> None:
        validate_observations(self.observations)
        validate_resources(self.resources)

    @property
    def behavior(self) -> BehaviorVector:
        return behavioral_objectives(self.observations)

    def oriented_vector(self) -> tuple[int, int, int, int, int]:
        # The oracle maximizes all coordinates, hence negated raw costs.
        return self.behavior + (-self.resources[0], -self.resources[1])

    def canonical_key(self) -> tuple[ObservationTable, ResourceVector]:
        return (self.observations, self.resources)


def registered_interface():
    return F.ObservationInterface(REGISTERED_WORDS, REGISTERED_STEP_CAP)


def point_from_program(program) -> MorphologyPoint:
    F.validate_program(program)
    return MorphologyPoint(F.semantic_key(program, registered_interface()), program.resource_vector())


def validate_point_set(points: object) -> tuple[MorphologyPoint, ...]:
    if type(points) is not tuple or not points:
        raise ValueError("Pareto analysis requires a nonempty tuple")
    if any(not isinstance(point, MorphologyPoint) for point in points):
        raise ValueError("Pareto input contains a non-morphology point")
    keys = [point.canonical_key() for point in points]
    if len(keys) != len(set(keys)):
        raise ValueError("Pareto morphology set must be duplicate-free")
    return points


def distinct_morphologies(programs: Iterable[object]) -> tuple[MorphologyPoint, ...]:
    rows: dict[tuple[ObservationTable, ResourceVector], MorphologyPoint] = {}
    count = 0
    for program in programs:
        point = point_from_program(program)
        rows[point.canonical_key()] = point
        count += 1
    if count == 0:
        raise ValueError("morphology quotient requires at least one presentation")
    result = tuple(sorted(rows.values(), key=lambda point: point.canonical_key()))
    return validate_point_set(result)


def dominates(left: MorphologyPoint, right: MorphologyPoint) -> bool:
    if not isinstance(left, MorphologyPoint) or not isinstance(right, MorphologyPoint):
        raise ValueError("dominance requires two morphology points")
    weak_behavior = all(a >= b for a, b in zip(left.behavior, right.behavior))
    weak_resource = all(a <= b for a, b in zip(left.resources, right.resources))
    strict = left.behavior != right.behavior or left.resources != right.resources
    return weak_behavior and weak_resource and strict


def pareto_front(points: tuple[MorphologyPoint, ...]) -> tuple[MorphologyPoint, ...]:
    points = validate_point_set(points)
    result = tuple(
        point for point in points
        if not any(dominates(rival, point) for rival in points if rival != point)
    )
    if not result:
        raise AssertionError("a nonempty finite strict order must have a maximal point")
    return result


def exact_density(points: tuple[MorphologyPoint, ...]) -> Fraction:
    points = validate_point_set(points)
    return Fraction(len(pareto_front(points)), len(points))


def fraction_text(value: Fraction) -> str:
    if type(value) is not Fraction:
        raise ValueError("fraction_text requires an exact Fraction")
    return f"{value.numerator}/{value.denominator}"


def _point_json(point: MorphologyPoint) -> dict[str, object]:
    semantic_payload = json.dumps(
        [[status, list(output)] for status, output in point.observations],
        separators=(",", ":"),
    ).encode()
    return {
        "behavior": list(point.behavior),
        "resources": list(point.resources),
        "semantic_table_sha256": sha256(semantic_payload).hexdigest(),
    }


def frontier_certificate(points: tuple[MorphologyPoint, ...]) -> dict[str, object]:
    points = validate_point_set(points)
    front = pareto_front(points)
    front_set = set(front)
    irreflexive_checks = 0
    transitive_checks = 0
    antichain_checks = 0
    cover_checks = 0
    for left in points:
        irreflexive_checks += 1
        if dominates(left, left):
            raise AssertionError("strict dominance became reflexive")
        for middle in points:
            if left in front_set and middle in front_set and left != middle:
                antichain_checks += 1
                if dominates(left, middle) or dominates(middle, left):
                    raise AssertionError("frontier is not an antichain")
            for right in points:
                transitive_checks += 1
                if dominates(left, middle) and dominates(middle, right) and not dominates(left, right):
                    raise AssertionError("dominance is not transitive")
    for point in points:
        cover_checks += 1
        if point not in front_set and not any(dominates(maximal, point) for maximal in front):
            raise AssertionError("nonfront point has no maximal dominator")

    oriented = tuple(point.oriented_vector() for point in points)
    if len(oriented) != len(set(oriented)):
        # Distinct semantic tables may intentionally have the same registered
        # objective vector. The independent oracle therefore operates on the
        # unique objective/resource carrier, then is lifted back to points.
        objective_carrier = tuple(sorted(set(oriented)))
    else:
        objective_carrier = oriented
    oracle_vectors = set(objective_carrier[index] for index in O.maximal_indices(objective_carrier))
    primary_vectors = {point.oriented_vector() for point in front}
    if oracle_vectors != primary_vectors:
        raise AssertionError("independent frontier oracle disagrees")

    return {
        "morphology_count": len(points),
        "objective_resource_vector_count": len(objective_carrier),
        "frontier_morphology_count": len(front),
        "frontier_objective_resource_vector_count": len(primary_vectors),
        "density": fraction_text(Fraction(len(front), len(points))),
        "frontier": [_point_json(point) for point in front],
        "irreflexive_checks": irreflexive_checks,
        "transitive_checks": transitive_checks,
        "antichain_ordered_checks": antichain_checks,
        "maximal_cover_checks": cover_checks,
        "independent_oracle_exact_match": True,
    }


def duplicate_injection_census() -> dict[str, object]:
    strong = MorphologyPoint(
        (("HALTED", ()), ("HALTED", (0,)), ("HALTED", (1,))),
        (1, 1),
    )
    weak = MorphologyPoint(
        (("STEP_LIMIT", ()), ("STEP_LIMIT", ()), ("STEP_LIMIT", ())),
        (2, 2),
    )
    if not dominates(strong, weak):
        raise AssertionError("registered duplicate hostile lost dominance")
    quotient = (strong, weak)
    quotient_density = exact_density(quotient)

    def presentation_density(rows: tuple[MorphologyPoint, ...]) -> Fraction:
        unique = tuple(sorted(set(rows), key=lambda point: point.canonical_key()))
        front = set(pareto_front(unique))
        return Fraction(sum(point in front for point in rows), len(rows))

    baseline = presentation_density((strong, weak))
    duplicate_front = presentation_density((strong, strong, weak))
    duplicate_dominated = presentation_density((strong, weak, weak))
    if (baseline, duplicate_front, duplicate_dominated) != (
        Fraction(1, 2), Fraction(2, 3), Fraction(1, 3)
    ):
        raise AssertionError("duplicate-injection hostile drifted")
    for rows in ((strong, weak), (strong, strong, weak), (strong, weak, weak)):
        unique = tuple(sorted(set(rows), key=lambda point: point.canonical_key()))
        if exact_density(unique) != quotient_density:
            raise AssertionError("quotient density changed under duplicate injection")
    return {
        "quotient_density": fraction_text(quotient_density),
        "presentation_density_baseline": fraction_text(baseline),
        "presentation_density_after_front_duplicate": fraction_text(duplicate_front),
        "presentation_density_after_dominated_duplicate": fraction_text(duplicate_dominated),
        "quotient_invariance_checks": 3,
        "presentation_estimator_representation_sensitive": True,
    }


def remint_census() -> dict[str, object]:
    programs = F.enumerate_candidates(F.StructuralBudget(2, 2))
    baseline = {program.canonical_code(): point_from_program(program) for program in programs}
    tokens = ("p0", "p1", "p2", "p3", "p4")
    checks = 0
    for permuted in permutations(tokens):
        mapping = dict(zip(F.SEMANTIC_OPS, permuted))
        for program in programs:
            decoded = F.decode_reminted(F.remint_program(program, mapping), mapping)
            if point_from_program(decoded) != baseline[program.canonical_code()]:
                raise AssertionError("certified surface remint changed a morphology point")
            checks += 1
    return {
        "certified_surface_remint_count": 120,
        "registered_presentation_count": len(programs),
        "morphology_point_invariance_checks": checks,
        "frontier_and_density_invariant_by_factorization": True,
    }


def registered_census() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    total_transitive = 0
    for code_cells, register_cells in REGISTERED_BUDGETS:
        programs = F.enumerate_candidates(F.StructuralBudget(code_cells, register_cells))
        points = distinct_morphologies(programs)
        certificate = frontier_certificate(points)
        total_transitive += int(certificate["transitive_checks"])
        front = set(pareto_front(points))
        presentation_front = sum(point_from_program(program) in front for program in programs)
        rows.append({
            "budget": [code_cells, register_cells],
            "presentation_count": len(programs),
            **certificate,
            "presentation_front_count": presentation_front,
            "presentation_weighted_density_not_registered": fraction_text(
                Fraction(presentation_front, len(programs))
            ),
        })
    return {
        "budget_rows": rows,
        "total_transitive_checks": total_transitive,
        "duplicate_injection": duplicate_injection_census(),
        "remint": remint_census(),
    }


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / ".git").is_file():
            return candidate
    raise RuntimeError("repository root not found")


def git_blob_sha(data: bytes) -> str:
    return sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows: list[dict[str, object]] = []
    for name, relative, expected_blob, claim_field, expected_claim in PARENT_PINS:
        path = root / relative
        try:
            data = path.read_bytes()
            payload = json.loads(data)
            actual_blob = git_blob_sha(data)
            claim_ok = payload.get(claim_field) == expected_claim
        except (OSError, json.JSONDecodeError):
            actual_blob = None
            claim_ok = False
        rows.append({
            "name": name,
            "path": relative,
            "expected_blob": expected_blob,
            "actual_blob": actual_blob,
            "blob_ok": actual_blob == expected_blob,
            "claim_ok": claim_ok,
        })
    return {"all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows), "rows": rows}


def validate_scientific_ledger() -> dict[str, object]:
    payload = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text(encoding="utf-8"))
    claims = payload.get("claims", [])
    gaps = payload.get("open_gaps", [])
    required = {"id", "statement", "scope", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    if payload.get("schema") != "GMI_833_FINITE_PARETO_DENSITY_SCIENTIFIC_LEDGER_V1":
        raise ValueError("scientific ledger schema drifted")
    if len(claims) != 3 or any(set(row) != required for row in claims):
        raise ValueError("scientific claim ledger is incomplete")
    if len(gaps) < 8 or any(row.get("status") != "OPEN" for row in gaps):
        raise ValueError("open-gap ledger is incomplete")
    return {"claim_ledgers": 3, "open_gaps": len(gaps), "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"}


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_FINITE_PARETO_DENSITY_V1.json").read_text(encoding="utf-8"))
    replacements = reconciliation.get("replacements", [])
    expected_old = "- [ ] Measure Pareto-front density."
    manifest_ok = (
        manifest.get("schema") == "GMI_833_FINITE_PARETO_DENSITY_MANIFEST_V1"
        and manifest.get("issue") == SOURCE_ISSUE
        and manifest.get("source_pr") == SOURCE_PR
        and manifest.get("parent_issue") == PARENT_ISSUE
        and manifest.get("source_main") == SOURCE_MAIN
        and manifest.get("freeze_commit") == FREEZE_COMMIT
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("target_rows") == 1
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
    )
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == PARENT_ISSUE
        and reconciliation.get("source_issue") == SOURCE_ISSUE
        and reconciliation.get("source_pr") == SOURCE_PR
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and len(replacements) == 1
        and replacements[0].get("anchor") == "# F. Intelligence-space generator"
        and replacements[0].get("old") == expected_old
        and replacements[0].get("new", "").startswith("- [x] Measure Pareto-front density.")
        and f"PR #{SOURCE_PR}" in replacements[0].get("new", "")
    )
    if not manifest_ok or not reconciliation_ok:
        raise ValueError("manifest/reconciliation package contract drifted")
    return {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 1, "source_pr": SOURCE_PR}


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or audit_parents()
    try:
        census = registered_census()
        ledger = validate_scientific_ledger()
        package = validate_package_contracts()
        rows = census["budget_rows"]
        checks = {
            "parents_exactly_pinned": bool(parent_audit.get("all_ok")),
            "all_four_complete_budget_censuses": len(rows) == 4,
            "all_frontiers_nonempty": all(row["frontier_morphology_count"] > 0 for row in rows),
            "all_densities_exact_reduced_rationals": all(Fraction(row["density"]) > 0 for row in rows),
            "independent_frontier_oracle_exact": all(row["independent_oracle_exact_match"] for row in rows),
            "strict_order_and_frontier_certificates": all(
                row["irreflexive_checks"] == row["morphology_count"]
                and row["maximal_cover_checks"] == row["morphology_count"]
                for row in rows
            ),
            "duplicate_injection_hostile_detected": census["duplicate_injection"]["presentation_estimator_representation_sensitive"] is True,
            "quotient_density_duplicate_invariant": census["duplicate_injection"]["quotient_invariance_checks"] == 3,
            "all_surface_remints_invariant": census["remint"]["morphology_point_invariance_checks"] == 69_120,
            "scientific_ledger_complete": ledger["claim_ledgers"] == 3,
            "larger_scope_gaps_remain_open": ledger["open_gaps"] >= 8,
            "package_contract_exact": package["manifest_ok"] and package["reconciliation_ok"],
        }
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError, AssertionError) as exc:
        return {
            "schema": "GMI833FiniteParetoDensityResultV1",
            "issue": SOURCE_ISSUE,
            "parent_issue": PARENT_ISSUE,
            "source_pr": SOURCE_PR,
            "claim_ceiling": CLAIM_CEILING,
            "verdict": "RED",
            "error": str(exc),
            "parent_audit": parent_audit,
            "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        }
    return {
        "schema": "GMI833FiniteParetoDensityResultV1",
        "issue": SOURCE_ISSUE,
        "parent_issue": PARENT_ISSUE,
        "source_pr": SOURCE_PR,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "grammar": "G0-fin-v1",
        "registered_interface": {"input_words": [[], [0], [1]], "step_cap": REGISTERED_STEP_CAP},
        "registered_objectives": {
            "maximize": ["termination_count", "copy_count", "productive_count"],
            "minimize": ["code_cells", "register_cells"],
            "scalarization": None,
            "evaluation_prior_disclosed": True,
        },
        "claim_ceiling": CLAIM_CEILING,
        "checks": checks,
        "census": census,
        "ledger": ledger,
        "package": package,
        "parent_audit": parent_audit,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def main() -> int:
    receipt = build_receipt()
    print(canonical_json(receipt), end="")
    return 0 if receipt.get("verdict") == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
