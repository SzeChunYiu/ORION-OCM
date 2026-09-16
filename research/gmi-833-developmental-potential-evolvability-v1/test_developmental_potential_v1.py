#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("developmental_potential_v1", HERE / "developmental_potential_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class DevelopmentalPotentialTests(unittest.TestCase):
    def test_parent_artifacts_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 7)

    def test_parent_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for _, path, _, _, _ in M.PARENT_PINS:
                target = tmp / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / path, target)
            victim = tmp / M.PARENT_PINS[4][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_exact_numeric_contract_rejects_float_and_bool(self):
        for value in (0.5, True, False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                M.exact(value)

    def test_current_capability_potential_and_headroom_are_distinct(self):
        result = M.developmental_potential(
            ("now", "mid", "future"), "now", {"now": 1, "mid": 2, "future": 5},
            (("now", "mid", (1, 0)), ("mid", "future", (1, 1))), (2, 1),
        )
        self.assertEqual(result["current_capability"], 1)
        self.assertEqual(result["developmental_potential"], 5)
        self.assertEqual(result["headroom"], 4)
        self.assertEqual(result["reachable_states"], ("now", "mid", "future"))

    def test_potential_is_nondecreasing_under_budget_expansion(self):
        args = (
            ("x", "y", "z"), "x", {"x": 1, "y": 3, "z": 7},
            (("x", "y", (1, 0)), ("y", "z", (0, 2))),
        )
        low = M.developmental_potential(*args, (1, 0))
        high = M.developmental_potential(*args, (1, 2))
        self.assertEqual((low["developmental_potential"], high["developmental_potential"]), (3, 7))

    def test_current_score_does_not_identify_headroom(self):
        high_now = M.developmental_potential(("x",), "x", {"x": 5}, (), (0,))
        low_now = M.developmental_potential(("x", "y"), "x", {"x": 1, "y": 5}, (("x", "y", (1,)),), (1,))
        self.assertEqual(high_now["headroom"], 0)
        self.assertEqual(low_now["headroom"], 4)

    def test_vector_reachability_retains_nondominated_path_costs(self):
        reachable = M.reachable_with_costs(
            ("x", "y"), "x",
            (("x", "y", (2, 0)), ("x", "y", (0, 2)), ("y", "x", (0, 0))),
            (2, 2),
        )
        self.assertEqual(set(reachable["y"]), {(Fraction(2), Fraction(0)), (Fraction(0), Fraction(2))})
        self.assertEqual(reachable["x"], ((Fraction(0), Fraction(0)),))

    def test_graph_contract_fails_closed(self):
        with self.assertRaises(ValueError):
            M.developmental_potential(("x",), "missing", {"x": 1}, (), (0,))
        with self.assertRaises(ValueError):
            M.developmental_potential(("x",), "x", {"x": 1, "extra": 2}, (), (0,))
        with self.assertRaises(ValueError):
            M.reachable_with_costs(("x",), "x", (("x", "outside", (1,)),), (1,))
        with self.assertRaises(ValueError):
            M.reachable_with_costs(("x",), "x", (("x", "x", (-1,)),), (1,))
        with self.assertRaises(ValueError):
            M.reachable_with_costs(("x",), "x", (("x", "x", (1, 0)),), (1,))

    def test_useful_descendant_mass_is_exact(self):
        kernel = {"a": Fraction(1, 4), "b": Fraction(1, 2), "c": Fraction(1, 4)}
        self.assertEqual(M.useful_descendant_mass(kernel, {"a", "c"}), Fraction(1, 2))

    def test_kernel_contract_fails_closed(self):
        for kernel in ({}, {"a": Fraction(1, 2)}, {"a": 2, "b": -1}, {"a": 0.5, "b": 0.5}):
            with self.subTest(kernel=kernel), self.assertRaises(ValueError):
                M.validate_kernel(kernel)
        with self.assertRaises(ValueError):
            M.useful_descendant_mass({"a": 1}, {"outside"})

    def test_iid_first_hit_and_zero_mass_terminal(self):
        self.assertEqual(M.iid_first_hit(Fraction(1, 4)), {"status": "FINITE_EXPECTATION", "expected_proposals": 4})
        self.assertEqual(M.iid_first_hit(0), {"status": M.ZERO_MASS, "expected_proposals": None})
        with self.assertRaises(ValueError):
            M.iid_first_hit(Fraction(5, 4))

    def test_priced_burden_uses_registered_vector_prices(self):
        self.assertEqual(M.priced_burden((2, 3), (Fraction(1, 2), 2)), 7)
        with self.assertRaises(ValueError):
            M.priced_burden((1,), (0,))
        with self.assertRaises(ValueError):
            M.priced_burden((1, 2), (1,))
        with self.assertRaises(ValueError):
            M.priced_burden((1,), (-1,))

    def test_history_improvement_charges_overhead(self):
        result = M.history_discovery_comparison(
            {"u": Fraction(1, 4), "n": Fraction(3, 4)},
            {"u": Fraction(1, 2), "n": Fraction(1, 2)},
            {"u"}, set(), (2,), (1,), (1,),
        )
        self.assertEqual(result["baseline_expected_priced_burden"], 8)
        self.assertEqual(result["history_expected_priced_burden"], 5)
        self.assertEqual(result["verdict"], "HISTORY_STRICTLY_IMPROVES")
        self.assertTrue(result["positive_mass_iff_holds"])

    def test_history_benefit_can_be_neutralized_or_reversed(self):
        baseline = {"u": Fraction(1, 4), "n": Fraction(3, 4)}
        history = {"u": Fraction(1, 2), "n": Fraction(1, 2)}
        tie = M.history_discovery_comparison(baseline, history, {"u"}, set(), (2,), (4,), (1,))
        costly = M.history_discovery_comparison(baseline, history, {"u"}, set(), (2,), (5,), (1,))
        self.assertEqual(tie["verdict"], "TIE")
        self.assertEqual(costly["verdict"], "HISTORY_HARMS")

    def test_zero_mass_history_cases_remain_typed(self):
        zero = {"u": 0, "n": 1}
        positive = {"u": Fraction(1, 2), "n": Fraction(1, 2)}
        self.assertEqual(
            M.history_discovery_comparison(zero, positive, {"u"}, set(), (1,), (0,), (1,))["verdict"],
            "HISTORY_STRICTLY_IMPROVES",
        )
        self.assertEqual(
            M.history_discovery_comparison(positive, zero, {"u"}, set(), (1,), (0,), (1,))["verdict"],
            "HISTORY_HARMS",
        )
        self.assertEqual(
            M.history_discovery_comparison(zero, zero, {"u"}, set(), (1,), (0,), (1,))["verdict"],
            "BOTH_UNREACHABLE",
        )

    def test_policy_assay_rejects_stored_target_and_unmatched_carrier(self):
        kernel = {"u": Fraction(1, 2), "n": Fraction(1, 2)}
        with self.assertRaises(ValueError):
            M.history_discovery_comparison(kernel, kernel, {"u"}, {"u"}, (1,), (0,), (1,))
        with self.assertRaises(ValueError):
            M.history_discovery_comparison(kernel, {"u": 1}, {"u"}, set(), (1,), (0,), (1,))
        with self.assertRaises(ValueError):
            M.history_discovery_comparison(kernel, kernel, {"u"}, set(), (0,), (0,), (1,))

    def test_solution_only_intervention_is_not_policy_capital(self):
        kernel = {"u": Fraction(1, 4), "n": Fraction(3, 4)}
        result = M.classify_capital({"u"}, {"u"}, kernel, kernel, (1,), (0,), (1,))
        self.assertTrue(result["solution_capital"])
        self.assertFalse(result["search_policy_capital"])
        self.assertEqual(result["policy_assay_status"], "SOLUTION_ONLY_UNCHANGED_POLICY")

    def test_stored_target_plus_changed_policy_is_not_identifiable(self):
        result = M.classify_capital(
            {"u"}, {"u"},
            {"u": Fraction(1, 4), "n": Fraction(3, 4)},
            {"u": Fraction(1, 2), "n": Fraction(1, 2)},
            (1,), (0,), (1,),
        )
        self.assertTrue(result["solution_capital"])
        self.assertIsNone(result["search_policy_capital"])
        self.assertEqual(result["policy_assay_status"], "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION")

    def test_policy_only_intervention_is_not_solution_reuse(self):
        result = M.classify_capital(
            {"u"}, set(),
            {"u": Fraction(1, 4), "n": Fraction(3, 4)},
            {"u": Fraction(1, 2), "n": Fraction(1, 2)},
            (2,), (1,), (1,),
        )
        self.assertFalse(result["solution_capital"])
        self.assertTrue(result["search_policy_capital"])
        self.assertEqual(result["policy_assay_status"], "HISTORY_STRICTLY_IMPROVES")

    def test_unchanged_proposal_law_cannot_be_policy_capital(self):
        kernel = {"u": Fraction(1, 2), "n": Fraction(1, 2)}
        result = M.classify_capital({"u"}, set(), kernel, kernel, (1,), (0,), (1,))
        self.assertFalse(result["solution_capital"])
        self.assertFalse(result["search_policy_capital"])
        self.assertEqual(result["policy_assay_status"], "TIE")

    def test_bounded_census_counts(self):
        self.assertEqual(
            M.exhaustive_census(),
            {
                "budgeted_potential_cases": 1512,
                "useful_mass_first_hit_cases": 105,
                "history_discovery_cases": 300,
                "capital_separation_cases": 24,
            },
        )

    def test_scientific_ledger_is_complete_but_review_stays_open(self):
        self.assertEqual(
            M.validate_ledgers(),
            {"claim_ledgers": 5, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        )

    def test_manifest_and_reconciliation_are_exactly_scoped_to_pr(self):
        self.assertEqual(
            M.validate_package_contracts(),
            {
                "manifest_ok": True,
                "reconciliation_ok": True,
                "reconciliation_rows": 4,
                "source_pr": 909,
            },
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt(M.audit_parents())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(M.canonical_json(receipt), (HERE / "RESULT_V1.json").read_text())
        self.assertEqual(json.loads(M.canonical_json(receipt)), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_preserves_empirical_and_open_ended_negatives(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("EMPIRICAL_K2_ESTABLISHED", receipt["forbidden_promotions"])
        self.assertIn("UNIVERSAL_OPEN_ENDED_EVOLVABILITY", receipt["forbidden_promotions"])
        self.assertIn("HISTORY_ALWAYS_HELPS", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
