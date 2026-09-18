#!/usr/bin/env python3
"""Tests for the #833 Section K capability predictor.

Runs under `python3 -I -B` and `python3 -I -O -B`. No `assert` statement is used
for validation anywhere in the package, so -O cannot silently disable a check.
"""

from __future__ import annotations

import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import capability_predictor_v1 as A  # noqa: E402
import oracle_route_b_v1 as B  # noqa: E402


def to_fraction(numerator):
    if numerator == B.UNSATISFIED:
        return A.UNSATISFIED
    return Fraction(numerator, B.DENOM)


class RouteIndependence(unittest.TestCase):
    def test_route_b_does_not_import_route_a(self):
        source = (HERE / "oracle_route_b_v1.py").read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                self.assertNotIn("capability_predictor_v1", stripped)
        self.assertNotIn("capability_predictor_v1", B.__dict__.keys())
        self.assertIsNone(getattr(B, "capability_predictor_v1", None))

    def test_route_a_does_not_import_route_b(self):
        source = (HERE / "capability_predictor_v1.py").read_text(encoding="utf-8")
        self.assertNotIn("oracle_route_b_v1", source)

    def test_universes_agree(self):
        self.assertEqual(A.N, B.N)
        for index in range(A.N):
            rec_a = A.UNIVERSE[index]
            rec_b = B.UNIVERSE[index]
            self.assertEqual(rec_a[A.F_A], rec_b["a"])
            self.assertEqual(rec_a[A.F_K], rec_b["k"])
            self.assertEqual(rec_a[A.F_RHO], rec_b["rho"])
            self.assertEqual(rec_a[A.F_DEV], rec_b["dev"])
            self.assertEqual(rec_a[A.F_OBS], rec_b["obs"])
            self.assertEqual(A.SEARCH_RANK[index], rec_b["rank"])
        for contract in A.CONTRACTS:
            for index in range(A.N):
                self.assertEqual(A.CAP[contract][index],
                                 Fraction(B.SCORE_NUM[contract][index], B.DENOM))


class GridAgreement(unittest.TestCase):
    """KP-1A/KP-1B/KP-2B verified twice, by two materially independent routes."""

    @classmethod
    def setUpClass(cls):
        cls.compared = 0
        cls.disagreements = []
        u_by_id = dict((entry[0], entry) for entry in A.U_VALUES)
        for entry in A.main_grid():
            (k_index, r_value, d_value, b_value, h_value,
             u_id, u_kind, u_mask, alpha, contract, tau) = entry
            emission, cuts, masks, ceilings, survivors, res, qtau = A.evaluate(entry)
            flags = A.mode_flags("REGISTERED", survivors, ceilings, tau, qtau)
            live = A.assigned_mode(flags)
            mode_a = live[0] if len(live) == 1 else "AMBIGUOUS"
            tau_num = int(tau * B.DENOM)
            out = B.classify(k_index, contract, r_value, h_value, d_value, b_value,
                             u_id, tau_num)
            ident_b = tuple(to_fraction(v) for v in out["identified"])
            cls.compared += 1
            if (emission.disposition != out["disposition"]
                    or emission.identified_set != ident_b
                    or mode_a != out["mode"]):
                if len(cls.disagreements) < 5:
                    cls.disagreements.append((entry, emission.disposition,
                                              out["disposition"], mode_a, out["mode"]))
            _ = u_by_id

    def test_grid_fully_compared(self):
        self.assertEqual(self.compared, 51840)

    def test_routes_agree_everywhere(self):
        self.assertEqual(self.disagreements, [])


class Receipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = A.build_receipt()

    def test_verdict_green(self):
        failed = sorted(k for k, v in self.receipt["checks"].items() if not v)
        self.assertEqual(failed, [])
        self.assertEqual(self.receipt["verdict"], "GREEN")

    def test_no_floats_anywhere(self):
        def scan(node, path):
            if isinstance(node, float):
                raise ValueError("float found at %s" % (path,))
            if isinstance(node, dict):
                for key, value in node.items():
                    scan(value, path + "/" + str(key))
            elif isinstance(node, (list, tuple)):
                for position, value in enumerate(node):
                    scan(value, path + "/" + str(position))
        scan(A.canonicalize(self.receipt), "")

    def test_kp1a_totality(self):
        census = self.receipt["main_census"]
        self.assertEqual(census["exceptions"], 0)
        self.assertEqual(sum(census["dispositions"].values()), census["grid_size"])
        self.assertEqual(sum(census["emit_sites"].values()), census["grid_size"])

    def test_kp1b_soundness(self):
        self.assertEqual(self.receipt["main_census"]["soundness_violations"], 0)

    def test_kp1c_forced_abstention(self):
        census = self.receipt["main_census"]
        self.assertEqual(census["forced_abstention_witnesses"],
                         census["dispositions"]["CANNOT_IDENTIFY"])
        self.assertIsNotNone(census["forced_abstention_example"])

    def test_kp1d_boundary_counterexample(self):
        item = self.receipt["kp1d_boundary_counterexample"]
        self.assertIsNotNone(item)
        self.assertTrue(item["sound_over_consistent_worlds"])
        self.assertFalse(item["equals_actual_system_capability"])

    def test_kp2a_monotone(self):
        self.assertEqual(
            self.receipt["main_census"]["ladder_monotonicity_violations"], 0)

    def test_kp2b_partition(self):
        census = self.receipt["main_census"]
        self.assertEqual(census["taxonomy_overlaps"], 0)
        self.assertEqual(census["taxonomy_gaps"], 0)
        self.assertEqual(sum(census["mode_counts"].values()), census["grid_size"])

    def test_kp2b_every_mode_nonempty_or_reported(self):
        census = self.receipt["main_census"]
        self.assertEqual(census["modes_empty"], [])
        self.assertEqual(census["mode_counts"]["FM_CANNOT_CHECK"], 0)
        self.assertEqual(self.receipt["semantics_subcensus"]["cannot_check"], 144)

    def test_kp2c_unique_binding_cut(self):
        self.assertEqual(self.receipt["main_census"]["kp2c_violations"], 0)

    def test_kp2d_order_boundary(self):
        orders = self.receipt["order_census"]
        self.assertEqual(orders["orders"], 120)
        self.assertEqual(orders["inputs"], 8640)
        self.assertEqual(orders["order_sensitive_inputs"]
                         + orders["order_invariant_inputs"], orders["inputs"])
        self.assertIsNotNone(orders["order_sensitivity_example"])
        self.assertIsNotNone(orders["sharp_unique_lever_counterexample"])
        self.assertEqual(len(orders["sharp_unique_lever_counterexample"]
                             ["individually_binding_cuts"]), 1)

    def test_kp3a_total_attachment(self):
        funnel = self.receipt["emit_funnel"]
        self.assertEqual(funnel["bare_return_lines"], [])
        self.assertEqual(funnel["carrier_construction_functions"], ["emit"])
        self.assertTrue(funnel["funnel_ok"])

    def test_kp3b_budget(self):
        census = self.receipt["main_census"]
        self.assertEqual(census["confidence_budget_mismatches"], 0)
        self.assertEqual(census["feasible_sets_carrying_coverage"], 0)
        product = self.receipt["hostiles"]["H6_independence_product"]
        self.assertTrue(product["product_strictly_larger"])
        self.assertEqual(product["union_bound"], "913/1000")

    def test_kp3c_exact_coverage(self):
        census = self.receipt["main_census"]
        self.assertEqual(census["coverage_fraction"], "1")
        self.assertEqual(census["coverage_hits"], census["coverage_pairs"])
        self.assertGreater(census["coverage_pairs"], 0)

    def test_kp4_null_beaten(self):
        null = self.receipt["null_control"]
        self.assertEqual(null["predictor_soundness_violations"], 0)
        self.assertGreater(null["null_soundness_violations"], 0)
        self.assertTrue(null["predictor_strictly_beats_null"])

    def test_all_hostiles_detected(self):
        for name, payload in sorted(self.receipt["hostiles"].items()):
            self.assertTrue(payload.get("detected"), name)

    def test_parent_pins(self):
        parents = self.receipt["parent_audit"]
        self.assertTrue(parents["all_blobs_ok"])
        self.assertTrue(parents["all_claims_ok"])
        self.assertTrue(parents["mutation_hostile_detected"])

    def test_claim_ceiling_and_forbidden_promotions(self):
        self.assertEqual(self.receipt["claim_ceiling"], A.CLAIM_CEILING)
        for token in ("HELD_OUT_PREDICTOR_VALIDATION",
                      "EMPIRICAL_CALIBRATION_ERROR_MEASURED",
                      "OOD_FAILURE_MEASURED",
                      "REAL_SYSTEM_CAPABILITY_VALIDATION",
                      "QUALITATIVE_FAILURE_PREDICTED_BEFORE_EVALUATION"):
            self.assertIn(token, self.receipt["forbidden_promotions"])

    def test_receipt_matches_committed_result(self):
        committed = HERE / "RESULT_V1.json"
        if not committed.is_file():
            self.skipTest("RESULT_V1.json not yet materialised")
        self.assertEqual(A.canonical_json(self.receipt),
                         committed.read_text(encoding="utf-8"))


class RouteBReceipt(unittest.TestCase):
    def test_route_b_aggregates_match_route_a(self):
        receipt_a = A.build_receipt()["main_census"]
        receipt_b = B.census()
        self.assertEqual(receipt_a["grid_size"], receipt_b["grid_size"])
        self.assertEqual(receipt_a["dispositions"], receipt_b["dispositions"])
        self.assertEqual(receipt_a["mode_counts"], receipt_b["mode_counts"])
        self.assertEqual(receipt_a["soundness_violations"],
                         receipt_b["soundness_violations"])
        self.assertEqual(receipt_a["coverage_pairs"], receipt_b["coverage_pairs"])
        self.assertEqual(receipt_a["coverage_hits"], receipt_b["coverage_hits"])
        self.assertEqual(receipt_a["coverage_fraction"], receipt_b["coverage_fraction"])
        self.assertEqual(B.semantics_census(),
                         {"cases": 144, "cannot_check": 144})


class EmitContract(unittest.TestCase):
    def test_bare_value_refused(self):
        with self.assertRaises(ValueError):
            A.emit("SITE_IDENTIFIED", "IDENTIFIED", None, value=Fraction(1, 2),
                   identified_set=(Fraction(1, 2),))

    def test_feasible_set_cannot_carry_coverage(self):
        with self.assertRaises(ValueError):
            A.TypedUncertainty("FEASIBLE_SET", None, Fraction(1, 2), "FEASIBLE",
                               dict(A.BETA), 1)

    def test_confidence_budget_must_equal_union_bound(self):
        with self.assertRaises(ValueError):
            A.TypedUncertainty("CONFIDENCE_SET", Fraction(1, 20), Fraction(19, 20),
                               "FEASIBLE", dict(A.BETA), 1)
        good = A.TypedUncertainty("CONFIDENCE_SET", Fraction(1, 20),
                                  Fraction(913, 1000), "FEASIBLE", dict(A.BETA), 1)
        self.assertEqual(good.coverage_lower, Fraction(913, 1000))

    def test_float_budget_refused(self):
        with self.assertRaises(ValueError):
            A.TypedUncertainty("CONFIDENCE_SET", 0.05, Fraction(913, 1000),
                               "FEASIBLE", dict(A.BETA), 1)

    def test_unregistered_constructor_refused(self):
        with self.assertRaises(ValueError):
            A.TypedUncertainty("PREDICTIVE_LAW", None, None, "FEASIBLE",
                               dict(A.BETA), 1)

    def test_point_for_multi_valued_image_refused(self):
        unc = A.build_uncertainty("FEASIBLE_SET", None, "FEASIBLE", 2)
        with self.assertRaises(ValueError):
            A.emit("SITE_IDENTIFIED", "IDENTIFIED", unc, value=Fraction(1, 2),
                   identified_set=(Fraction(1, 2), Fraction(1, 3)))

    def test_funnel_checker_flags_planted_hostile(self):
        clean = A.audit_emit_funnel(
            (HERE / "capability_predictor_v1.py").read_text(encoding="utf-8"))
        hostile = A.audit_emit_funnel(A.HOSTILE_DROP_UNCERTAINTY)
        self.assertTrue(clean["funnel_ok"])
        self.assertFalse(hostile["funnel_ok"])
        self.assertNotEqual(hostile["bare_return_lines"], [])


class ScopeFreeze(unittest.TestCase):
    def test_frozen_grid_sizes(self):
        self.assertEqual(len(A.K_M_VALUES), 8)
        self.assertEqual(len(A.R_VALUES), 6)
        self.assertEqual(len(A.D_VALUES), 3)
        self.assertEqual(len(A.B_VALUES), 5)
        self.assertEqual(len(A.H_VALUES), 3)
        self.assertEqual(len(A.U_VALUES), 3)
        self.assertEqual(len(A.CONTRACTS), 2)
        self.assertEqual(len(A.TAU_VALUES), 4)
        self.assertEqual(A.N, 32)
        self.assertEqual(A.RHO_DIM, 14)
        self.assertEqual(A.BETA_SUM, Fraction(37, 1000))

    def test_resource_is_not_a_candidacy_cut(self):
        """The KP-1B design decision, checked structurally and behaviourally."""
        source = (HERE / "capability_predictor_v1.py").read_text(encoding="utf-8")
        start = source.index("def survivor_mask(")
        end = source.index("def predict(")
        self.assertNotIn("RES_MASKS", source[start:end])
        for entry in A.main_grid():
            (k_index, r_value, d_value, b_value, h_value,
             u_id, u_kind, u_mask, alpha, contract, tau) = entry
            survivors = A.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
            if survivors == 0:
                continue
            if survivors & ~A.RES_MASKS[r_value]:
                emission = A.predict(k_index, contract, r_value, h_value, d_value,
                                     b_value, u_kind, u_mask, alpha, "REGISTERED")
                self.assertIn(A.UNSATISFIED, emission.identified_set)
                return
        self.fail("no grid input retains a resource-inadmissible survivor")

    def test_unsatisfied_never_meets_a_threshold(self):
        for tau in A.TAU_VALUES:
            self.assertFalse(A.meets(A.UNSATISFIED, tau))
        self.assertNotEqual(A.UNSATISFIED, Fraction(0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
