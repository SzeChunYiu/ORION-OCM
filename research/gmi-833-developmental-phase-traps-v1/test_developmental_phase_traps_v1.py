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
SPEC = importlib.util.spec_from_file_location(
    "developmental_phase_traps_v1", HERE / "developmental_phase_traps_v1.py"
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class DevelopmentalPhaseTrapTests(unittest.TestCase):
    def test_prerequisite_and_strongest_parents_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 5)
        self.assertEqual(audit["rows"][0]["name"], "developmental_potential_909")

    def test_parent_byte_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            for _, path, _, _, _ in M.PARENT_PINS:
                target = temporary / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / path, target)
            victim = temporary / M.PARENT_PINS[0][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(temporary)["all_ok"])

    def test_exact_contract_rejects_bool_and_float(self):
        for value in (True, False, 0.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                M.exact(value)

    def test_phase_schedule_returns_shortest_ray_thresholds(self):
        result = M.phase_schedule(
            ("root", "a", "b", "goal"),
            "root",
            (
                ("root", "a", (2, 0)),
                ("root", "b", (0, 2)),
                ("a", "goal", (0, 2)),
                ("b", "goal", (1, 0)),
                ("root", "goal", (3, 3)),
            ),
            {"root": 0, "a": 1, "b": 1, "goal": 5},
            (1, 1),
        )
        self.assertEqual(result["thresholds"]["goal"], 2)
        self.assertEqual(result["threshold_witness_costs"]["goal"], (Fraction(1), Fraction(2)))
        self.assertIn((Fraction(1), Fraction(2)), result["pareto_path_costs"]["goal"])

    def test_phase_argmax_is_complete_and_preserves_ties(self):
        result = M.phase_schedule(
            ("root", "a", "b"),
            "root",
            (("root", "a", (1,)), ("root", "b", (2,))),
            {"root": 0, "a": 3, "b": 3},
            (1,),
        )
        self.assertEqual([event["threshold"] for event in result["events"]], [0, 1, 2])
        self.assertEqual(result["events"][-1]["argmax"], ("a", "b"))
        self.assertTrue(result["events"][-1]["argmax_changed"])

    def test_phase_changes_only_at_exact_entry_thresholds(self):
        result = M.phase_schedule(
            ("root", "a", "b"),
            "root",
            (("root", "a", (1,)), ("root", "b", (3,))),
            {"root": 0, "a": 2, "b": 4},
            (2,),
        )
        self.assertEqual(tuple(event["threshold"] for event in result["events"]), (0, Fraction(1, 2), Fraction(3, 2)))
        self.assertEqual(tuple(event["argmax"] for event in result["events"]), (("root",), ("a",), ("b",)))

    def test_zero_ray_coordinate_makes_positive_cost_unreachable(self):
        result = M.phase_schedule(
            ("root", "blocked"),
            "root",
            (("root", "blocked", (1, 0)),),
            {"root": 0, "blocked": 10},
            (0, 1),
        )
        self.assertIsNone(result["thresholds"]["blocked"])
        self.assertEqual(result["events"][0]["argmax"], ("root",))

    def test_dominated_path_does_not_set_threshold(self):
        result = M.phase_schedule(
            ("root", "mid", "goal"),
            "root",
            (
                ("root", "goal", (4, 4)),
                ("root", "mid", (1, 1)),
                ("mid", "goal", (1, 1)),
            ),
            {"root": 0, "mid": 1, "goal": 2},
            (1, 1),
        )
        self.assertEqual(result["pareto_path_costs"]["goal"], ((Fraction(2), Fraction(2)),))
        self.assertEqual(result["thresholds"]["goal"], 2)

    def test_phase_graph_validation_fails_closed(self):
        with self.assertRaises(ValueError):
            M.phase_schedule(("x",), "missing", (), {"x": 0}, (1,))
        with self.assertRaises(ValueError):
            M.phase_schedule(("x",), "x", (), {"x": 0, "extra": 1}, (1,))
        with self.assertRaises(ValueError):
            M.phase_schedule(("x",), "x", (("x", "outside", (1,)),), {"x": 0}, (1,))
        with self.assertRaises(ValueError):
            M.phase_schedule(("x",), "x", (), {"x": 0}, (0,))

    def test_two_form_hysteresis_interior_and_exteriors(self):
        self.assertEqual(
            M.two_form_hysteresis(0, 1)["selections"],
            {"A": ("A",), "B": ("B",)},
        )
        self.assertEqual(set(M.two_form_hysteresis(-2, 1)["selections"].values()), {("B",)})
        self.assertEqual(set(M.two_form_hysteresis(2, 1)["selections"].values()), {("A",)})

    def test_hysteresis_boundary_ties_are_not_collapsed(self):
        self.assertEqual(
            M.two_form_hysteresis(-1, 1)["selections"],
            {"A": ("A", "B"), "B": ("B",)},
        )
        self.assertEqual(
            M.two_form_hysteresis(1, 1)["selections"],
            {"A": ("A",), "B": ("A", "B")},
        )

    def test_negative_switching_cost_fails_closed(self):
        with self.assertRaises(ValueError):
            M.symmetric_switching(-1)
        switching = M.symmetric_switching(1)
        switching[("A", "B")] = Fraction(-1)
        with self.assertRaises(ValueError):
            M.switching_selection(("A", "B"), {"A": 0, "B": 0}, switching, "A")

    def test_origin_additive_and_reset_erase_history(self):
        result = M.origin_additive_erasure(
            ("A", "B", "C"),
            {"A": 0, "B": 1, "C": 2},
            {"A": 0, "B": 1, "C": 2},
            {"A": 2, "B": 0, "C": 1},
        )
        self.assertTrue(result["history_erased"])
        self.assertEqual(len(set(result["selections"].values())), 1)
        reset = M.reset_erasure(
            ("A", "B"), {"A": 0, "B": 0}, M.symmetric_switching(1), "A"
        )
        self.assertEqual(reset, {"A": ("A",), "B": ("A",)})

    def test_deterministic_escape_iff_budget_feasible_path_exists(self):
        states = ("start", "local", "target")
        closed = (("start", "local", (1,)), ("local", "start", (0,)))
        trapped = M.deterministic_escape(states, "start", {"target"}, closed, (2,))
        escaped = M.deterministic_escape(
            states, "start", {"target"}, closed + (("local", "target", (1,)),), (2,)
        )
        self.assertTrue(trapped["is_local_trap"])
        self.assertFalse(trapped["escape_exists"])
        self.assertEqual(escaped["witness_path"], ("start", "local", "target"))
        self.assertEqual(escaped["witness_cost"], (Fraction(2),))

    def test_deterministic_escape_rejects_unknown_target_and_negative_budget(self):
        with self.assertRaises(ValueError):
            M.deterministic_escape(("s",), "s", {"outside"}, (), (0,))
        with self.assertRaises(ValueError):
            M.deterministic_escape(("s",), "s", {"s"}, (), (-1,))

    @staticmethod
    def _mass_fixture():
        states = ("source", "target", "other")
        kernel = {
            "source": {"source": 0, "target": Fraction(1, 2), "other": Fraction(1, 2)},
            "target": {"source": 0, "target": 0, "other": 1},
            "other": {"source": 0, "target": 0, "other": 1},
        }
        initial = {"source": 1, "target": 0, "other": 0}
        return states, kernel, initial

    def test_endpoint_and_cumulative_first_hit_mass_are_exact_and_distinct(self):
        states, kernel, initial = self._mass_fixture()
        result = M.markov_reachability(states, kernel, initial, {"target"}, 2)
        self.assertEqual(result["endpoint_mass"], (0, Fraction(1, 2), 0))
        self.assertEqual(result["new_first_hit_mass"], (0, Fraction(1, 2), 0))
        self.assertEqual(result["cumulative_first_hit_mass"], (0, Fraction(1, 2), Fraction(1, 2)))
        self.assertTrue(result["normalization_holds"])
        self.assertTrue(result["first_hit_accounting_holds"])
        self.assertTrue(result["cumulative_monotonicity_holds"])

    def test_dynamic_programme_equals_independent_path_enumeration(self):
        states, kernel, initial = self._mass_fixture()
        dynamic = M.markov_reachability(states, kernel, initial, {"target"}, 3)
        oracle = M.path_enumeration_oracle(states, kernel, initial, {"target"}, 3)
        self.assertEqual(dynamic["endpoint_mass"], oracle["endpoint_mass"])
        self.assertEqual(dynamic["cumulative_first_hit_mass"], oracle["cumulative_first_hit_mass"])

    def test_stochastic_escape_positive_mass_iff_positive_path_exists(self):
        states = ("s", "t")
        initial = {"s": 1, "t": 0}
        closed = {"s": {"s": 1, "t": 0}, "t": {"s": 0, "t": 1}}
        opened = {
            "s": {"s": Fraction(3, 4), "t": Fraction(1, 4)},
            "t": {"s": 0, "t": 1},
        }
        closed_result = M.stochastic_escape(states, closed, initial, {"t"}, 2)
        open_result = M.stochastic_escape(states, opened, initial, {"t"}, 2)
        self.assertTrue(closed_result["iff_holds"])
        self.assertFalse(closed_result["positive_escape_mass"])
        self.assertTrue(open_result["iff_holds"])
        self.assertTrue(open_result["positive_escape_mass"])
        self.assertEqual(open_result["dynamic"]["cumulative_first_hit_mass"][-1], Fraction(7, 16))

    def test_zero_probability_edge_is_not_a_positive_path(self):
        result = M.stochastic_escape(
            ("s", "t"),
            {"s": {"s": 1, "t": 0}, "t": {"s": 0, "t": 1}},
            {"s": 1, "t": 0},
            {"t"},
            5,
        )
        self.assertFalse(result["enumeration"]["positive_target_path_exists"])
        self.assertEqual(result["dynamic"]["cumulative_first_hit_mass"][-1], 0)

    def test_markov_contract_fails_closed(self):
        states = ("s", "t")
        good_initial = {"s": 1, "t": 0}
        good_kernel = {"s": {"s": 1, "t": 0}, "t": {"s": 0, "t": 1}}
        malformed = (
            {"s": {"s": Fraction(1, 2), "t": 0}, "t": {"s": 0, "t": 1}},
            {"s": {"s": 2, "t": -1}, "t": {"s": 0, "t": 1}},
            {"s": {"s": 0.5, "t": 0.5}, "t": {"s": 0, "t": 1}},
        )
        for kernel in malformed:
            with self.subTest(kernel=kernel), self.assertRaises(ValueError):
                M.markov_reachability(states, kernel, good_initial, {"t"}, 1)
        with self.assertRaises(ValueError):
            M.markov_reachability(states, good_kernel, good_initial, {"outside"}, 1)
        with self.assertRaises(ValueError):
            M.markov_reachability(states, good_kernel, good_initial, {"t"}, -1)
        with self.assertRaises(ValueError):
            M.markov_reachability(states, good_kernel, {"s": Fraction(1, 2), "t": 0}, {"t"}, 1)

    def test_bounded_census_counts(self):
        self.assertEqual(
            M.exhaustive_census(),
            {
                "phase_worlds": 5184,
                "phase_threshold_events": 11097,
                "hysteresis_cases": 21,
                "deterministic_escape_cases": 1792,
                "stochastic_dp_enumeration_cases": 18144,
            },
        )

    def test_scientific_ledger_closes_locally_with_review_open(self):
        self.assertEqual(
            M.validate_ledgers(),
            {"claim_ledgers": 5, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        )

    def test_manifest_and_reconciliation_are_narrow_and_direct(self):
        self.assertEqual(
            M.validate_package_contracts(),
            {
                "manifest_ok": True,
                "reconciliation_ok": True,
                "reconciliation_rows": 4,
                "source_pr": 924,
                "prerequisite_pr": 909,
            },
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt(M.audit_parents())
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        canonical = M.canonical_json(receipt)
        self.assertEqual(canonical, (HERE / "RESULT_V1.json").read_text())
        self.assertEqual(json.loads(canonical), json.loads((HERE / "RESULT_V1.json").read_text()))

    def test_claim_boundary_keeps_all_forbidden_promotions_red(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertEqual(tuple(receipt["forbidden_promotions"]), M.FORBIDDEN_PROMOTIONS)
        self.assertIn("UNIVERSAL_HYSTERESIS", receipt["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main()
