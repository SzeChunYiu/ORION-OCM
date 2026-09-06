"""Development controls for the FLT Proof Gap Atlas contract."""
from __future__ import annotations

import copy
import unittest

from contracts import (
    CannotCheck,
    dependency_distance,
    identity,
    pareto_frontier,
    theorem_liveness,
    validate_challenge,
    validate_outcome,
    validate_route,
    validate_universe,
)


H = "a" * 64
H2 = "b" * 64
H3 = "c" * 64
H4 = "d" * 64


def universe():
    return {
        "environment": {
            "source": {
                "repository": "anthropics/fermats-last-theorem",
                "commit": "aa2d8b34692b16c70f699536de0d8e75b9a3e9ef",
            },
            "lean_toolchain": "leanprover/lean4:v4.33.1",
            "mathlib_ref": "v4.33.0",
            "mathlib_commit": "db584cd6d46c92f209a44c0f1c829460d327499d",
            "checkers": ["lean-kernel", "leanprover-comparator", "nanoda"],
        },
        "library": {
            "declaration_inventory_sha256": H,
            "declaration_count": 29511,
        },
        "operators": ["exact", "apply", "refine", "rw", "simp", "constructor"],
        "budget": {
            "search_nodes": 10000,
            "generated_bytes": 1000000,
            "checker_milliseconds": 60000,
        },
        "normalization": {
            "version": "route-normalization-v1",
            "features": [
                "dependency-set",
                "landmark-theorems",
                "intermediate-lemmas",
                "proof-dag-topology",
                "operator-sequence",
            ],
        },
    }


def challenge():
    u = universe()
    return {
        "universe_sha256": identity(u),
        "target": {
            "id": "AbsoluteValue.foo",
            "statement_sha256": H2,
            "theorem_module": "Theorems.Thm_AbsoluteValue_foo",
            "solution_module": "P2M.Sol.S_AbsoluteValue_foo",
        },
        "gap_class": "G1",
        "hidden_nodes": ["AbsoluteValue.foo"],
        "solver_view": {
            "statement_sha256": H2,
            "visible_declarations_sha256": H3,
            "network_access": False,
            "solution_bytes_present": False,
            "theorem_wrapper_present": False,
            "forbidden_modules": [
                "Theorems.Thm_AbsoluteValue_foo",
                "P2M.Sol.S_AbsoluteValue_foo",
            ],
        },
        "budget": copy.deepcopy(u["budget"]),
        "operators_sha256": identity(u["operators"]),
        "normalization_version": "route-normalization-v1",
    }


def solved_outcome():
    c = challenge()
    return {
        "challenge_sha256": identity(c),
        "status": "SOLVED",
        "resource_usage": {
            "search_nodes": 900,
            "generated_bytes": 20000,
            "checker_milliseconds": 4000,
        },
        "checker_evidence": {
            "checker_id": "lean-kernel",
            "statement_sha256": H2,
            "proof_sha256": H3,
            "dependencies_sha256": H4,
            "environment_sha256": H,
            "accepted": True,
        },
    }


def route(route_id="r1", deps=None, proof=H3, metrics=None):
    if deps is None:
        deps = ["A", "B"]
    if metrics is None:
        metrics = {"dependencies": len(deps), "proof_size": 100, "checker_cost": 10}
    c = challenge()
    return {
        "route_id": route_id,
        "challenge_sha256": identity(c),
        "dependencies": deps,
        "proof_sha256": proof,
        "checker_evidence": {
            "checker_id": "lean-kernel",
            "statement_sha256": H2,
            "proof_sha256": proof,
            "dependencies_sha256": identity(sorted(deps)),
            "accepted": True,
        },
        "metrics": metrics,
        "novelty_class": "alternate-dependency-family",
        "normalization_family": "family-1",
    }


class ContractTests(unittest.TestCase):
    def test_frozen_universe(self):
        receipt = validate_universe(universe())
        self.assertEqual(receipt["status"], "FROZEN_UNIVERSE_VALID")
        self.assertEqual(receipt["operator_count"], 6)

    def test_rejects_nonfinite_or_invalid_budget(self):
        u = universe()
        u["budget"]["search_nodes"] = -1
        with self.assertRaises(CannotCheck):
            validate_universe(u)

    def test_hermetic_challenge(self):
        self.assertEqual(
            validate_challenge(challenge(), universe())["status"],
            "HERMETIC_CHALLENGE_VALID",
        )

    def test_rejects_solution_leak(self):
        c = challenge()
        c["solver_view"]["solution_bytes_present"] = True
        with self.assertRaises(CannotCheck):
            validate_challenge(c, universe())

    def test_rejects_wrapper_leak(self):
        c = challenge()
        c["solver_view"]["theorem_wrapper_present"] = True
        with self.assertRaises(CannotCheck):
            validate_challenge(c, universe())

    def test_rejects_missing_forbidden_solution(self):
        c = challenge()
        c["solver_view"]["forbidden_modules"].remove(c["target"]["solution_module"])
        with self.assertRaises(CannotCheck):
            validate_challenge(c, universe())

    def test_rejects_changed_universe(self):
        c = challenge()
        u = universe()
        u["operators"].append("aesop")
        with self.assertRaises(CannotCheck):
            validate_challenge(c, u)

    def test_checked_solved_outcome(self):
        result = validate_outcome(solved_outcome(), challenge(), universe())
        self.assertTrue(result["solved"])
        self.assertFalse(result["scientific_claim_authorized"])

    def test_negative_terminal_never_becomes_success(self):
        o = solved_outcome()
        o["status"] = "NOT_FOUND_WITHIN_REGISTERED_BUDGET"
        o["checker_evidence"] = None
        result = validate_outcome(o, challenge(), universe())
        self.assertFalse(result["solved"])

    def test_cannot_check_requires_reason(self):
        o = solved_outcome()
        o["status"] = "CANNOT_CHECK_CONSUMPTION"
        o["checker_evidence"] = None
        with self.assertRaises(CannotCheck):
            validate_outcome(o, challenge(), universe())
        o["reason"] = "registered consumption evidence unavailable"
        self.assertFalse(validate_outcome(o, challenge(), universe())["solved"])

    def test_forbids_all_flt_proofs_terminal(self):
        o = solved_outcome()
        o["status"] = "ALL_FLT_PROOFS_FOUND"
        o["checker_evidence"] = None
        with self.assertRaises(CannotCheck):
            validate_outcome(o, challenge(), universe())

    def test_exhaustive_terminal_requires_certificate(self):
        o = solved_outcome()
        o["status"] = "ALL_NORMALIZED_ROUTES_WITHIN_BOUND_FOUND"
        o["checker_evidence"] = None
        o["search_exhaustive"] = True
        with self.assertRaises(CannotCheck):
            validate_outcome(o, challenge(), universe())
        o["completeness_certificate_sha256"] = H4
        self.assertEqual(
            validate_outcome(o, challenge(), universe())["terminal"],
            "ALL_NORMALIZED_ROUTES_WITHIN_BOUND_FOUND",
        )

    def test_budget_overrun_cannot_validate(self):
        o = solved_outcome()
        o["resource_usage"]["search_nodes"] = 10001
        with self.assertRaises(CannotCheck):
            validate_outcome(o, challenge(), universe())

    def test_route_binds_exact_dependencies(self):
        self.assertEqual(
            validate_route(route(), challenge(), universe())["dependency_count"], 2
        )
        bad = route()
        bad["checker_evidence"]["dependencies_sha256"] = H4
        with self.assertRaises(CannotCheck):
            validate_route(bad, challenge(), universe())

    def test_alternate_route_survives_revocation(self):
        r1 = route("r1", ["A", "B"], "1" * 64)
        r2 = route("r2", ["C"], "2" * 64)
        self.assertEqual(theorem_liveness([r1, r2], ["A"])["status"], "LIVE")
        self.assertEqual(
            theorem_liveness([r1, r2], ["A", "C"])["status"], "DEAD"
        )

    def test_dependency_distance_is_exact_and_not_novelty_claim(self):
        d = dependency_distance(
            route("r1", ["A", "B"]),
            route("r2", ["B", "C"], "2" * 64),
        )
        self.assertEqual(d["dependency_distance"], "2/3")
        self.assertEqual(d["dependency_overlap"], "1/3")
        self.assertEqual(d["semantic_novelty"], "NOT_ESTABLISHED")

    def test_pareto_frontier(self):
        routes = [
            route("a", ["A"], "1" * 64, {"dependencies": 1, "proof_size": 100, "checker_cost": 10}),
            route("b", ["B"], "2" * 64, {"dependencies": 2, "proof_size": 120, "checker_cost": 12}),
            route("c", ["C"], "3" * 64, {"dependencies": 1, "proof_size": 90, "checker_cost": 20}),
        ]
        self.assertEqual(
            pareto_frontier(routes, ["dependencies", "proof_size", "checker_cost"]),
            ("a", "c"),
        )


if __name__ == "__main__":
    unittest.main()
