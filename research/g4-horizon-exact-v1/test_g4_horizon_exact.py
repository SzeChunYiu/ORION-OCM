"""Exact G4.2/G4.3 horizon toy. No ML, no donor engines, no scalarized claims."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import horizon_exact as H  # noqa: E402


class CostAndParetoTests(unittest.TestCase):
    def test_coordinates_stay_raw(self):
        vector = H.cost(rent=3, build=8)
        self.assertEqual(len(vector), len(H.COORDINATES))
        self.assertEqual(H.as_dict(vector)["rent"], 3)
        self.assertEqual(H.as_dict(vector)["hit"], 0)

    def test_incomparable_vectors_have_price_witnesses(self):
        rent = H.cost(rent=12)
        buy = H.cost(build=8, hit=3)
        prices = H.price_halfspaces(rent, buy)
        self.assertTrue(prices["pareto_incomparable"])
        self.assertEqual(prices["price_witness_prefer_a"], {"build": 1})
        self.assertEqual(prices["price_witness_prefer_b"], {"rent": 1})


class HorizonAndHeffTests(unittest.TestCase):
    def test_always_rent_has_zero_reuse(self):
        out = H.simulate((0, 0, 0, 0), H.always_rent)
        self.assertEqual(out.h_eff, 0)
        self.assertEqual(out.vector, H.cost(rent=12))

    def test_always_buy_heff_is_horizon_minus_one_on_constant(self):
        seq = (0,) * 8
        out = H.simulate(seq, H.always_buy)
        self.assertEqual(out.h_eff, 7)
        self.assertEqual(out.vector, H.cost(build=H.BUILD, hit=7 * H.HIT))

    def test_reset_every_one_kills_reuse(self):
        out = H.simulate((0,) * 6, H.always_buy, H.Lifecycle(reset_every=1))
        self.assertEqual(out.h_eff, 0)
        self.assertEqual(out.resets, 6)
        self.assertEqual(out.vector, H.cost(build=6 * H.BUILD, invalidation=6))

    def test_drift_reduces_heff_relative_to_stable(self):
        seq = (0, 1, 0, 1, 0, 1, 0, 1)
        stable = H.simulate(seq, H.always_buy)
        drifted = H.simulate(seq, H.always_buy, H.Lifecycle(drift_every=2))
        self.assertGreater(stable.h_eff, drifted.h_eff)
        self.assertGreater(drifted.drifts, 0)
        self.assertGreater(drifted.vector[H.COORDINATES.index("invalidation")], 0)

    def test_revision_of_item_zero_invalidates_only_that_entry(self):
        seq = (0, 1, 0, 1, 0, 1)
        out = H.simulate(seq, H.always_buy, H.Lifecycle(revision_every=2, revision_item=0))
        self.assertEqual(out.revisions, 3)
        self.assertGreater(out.vector[H.COORDINATES.index("invalidation")], 0)
        self.assertLess(out.h_eff, H.simulate(seq, H.always_buy).h_eff)

    def test_checkpoint_charges_write_read_replay_without_killing_reuse(self):
        seq = (0,) * 8
        out = H.simulate(seq, H.always_buy, H.Lifecycle(checkpoint_every=4))
        self.assertEqual(out.h_eff, 7)
        self.assertEqual(out.checkpoints, 2)
        self.assertEqual(out.vector[H.COORDINATES.index("checkpoint_write")], 2)
        self.assertEqual(out.vector[H.COORDINATES.index("checkpoint_read")], 2)
        self.assertEqual(out.vector[H.COORDINATES.index("replay")], 2)

    def test_reuse_density_controls_heff(self):
        rows = {row["unique"]: row for row in H.density_sweep()}
        self.assertEqual(rows[1]["h_eff_always_buy"], 5)
        self.assertEqual(rows[3]["h_eff_always_buy"], 3)
        self.assertGreater(rows[1]["h_eff_always_buy"], rows[3]["h_eff_always_buy"])

    def test_unlimited_buy_is_order_invariant(self):
        order = H.order_sweep()
        self.assertTrue(order["unlimited"]["order_invariant_h_eff"])
        self.assertTrue(order["unlimited"]["order_invariant_vector"])
        self.assertFalse(order["capacity_2_lru"]["order_invariant_h_eff"])


class ParentTests(unittest.TestCase):
    def test_analytic_threshold_matches_break_even(self):
        self.assertFalse(H.analytic_should_buy(4))
        self.assertTrue(H.analytic_should_buy(5))
        short = H.simulate((0,) * 4, H.analytic_threshold)
        long = H.simulate((0,) * 5, H.analytic_threshold)
        self.assertEqual(short.h_eff, 0)
        self.assertEqual(long.h_eff, 4)
        self.assertEqual(short.vector, H.cost(rent=12))
        self.assertEqual(long.vector, H.cost(build=H.BUILD, hit=4 * H.HIT))

    def test_analytic_is_on_exact_dp_pareto(self):
        for seq in H.frozen_sequences().values():
            residual = H.residual_after_exact_parents(seq)
            self.assertTrue(residual["analytic_on_dp_pareto"], seq)
            self.assertEqual(residual["selector_residual_after_analytic"], 0)

    def test_ski_rental_stays_inside_classic_summed_bound(self):
        ski = H.ski_rental_ratio_rows()
        self.assertLessEqual(ski["worst_summed_unit_ratio"], 2.0)
        h3 = next(row for row in ski["rows"] if row["horizon"] == 3)
        self.assertEqual(h3["online"]["build"], H.BUILD)
        self.assertEqual(h3["online"]["rent"], 2 * H.RENT)

    def test_belady_does_not_lose_to_lru_on_hits(self):
        seq = (0, 1, 2, 0, 1, 2, 0, 1)
        rows = H.cache_admission_rows(seq, capacity=2)
        self.assertGreaterEqual(rows["belady_opt"]["h_eff"], rows["lru"]["h_eff"])
        self.assertTrue(rows["belady_weakly_dominates_lru"] or rows["belady_opt"]["h_eff"] >= rows["lru"]["h_eff"])

    def test_common_action_stops_without_probe(self):
        stopping = H.stopping_study()
        self.assertEqual(stopping["common_action"]["gamma"], ["go"])
        self.assertTrue(stopping["common_action"]["early_exit_saves_probe"])
        self.assertIsNone(stopping["common_action"]["dp_policy_budget_1"])
        self.assertEqual(stopping["split_action"]["gamma"], [])
        self.assertEqual(stopping["split_action"]["dp_policy_budget_1"], "probe")
        self.assertEqual(stopping["split_action"]["policy"]["vector"]["probe"], H.PROBE)

    def test_rent_vs_buy_mid_horizon_is_price_regime(self):
        mixed = H.frozen_sequences()["unique_then_repeat"]
        prices = H.compare_parents(mixed)["rent_vs_buy_prices"]
        self.assertTrue(prices["pareto_incomparable"])


class ReportTests(unittest.TestCase):
    def test_report_terminals_and_boxes(self):
        report = H.build_report()
        for terminal in (
            "EXACT_META_POLICY_SUFFICIENT",
            "EXACT_EARLY_EXIT_VALUE_SUPPORTED",
            "PRICE_REGIME_ONLY",
            "LEARNED_ROUTER_NOT_NEEDED",
            "PARENT_SUFFICIENT",
            "CANNOT_CHECK_UNMERGED_PR154_SEMANTIC_LIFETIME",
            "CANNOT_CHECK_PRODUCTION_OCM_LIFETIME",
        ):
            self.assertIn(terminal, report["terminals"])
        self.assertEqual(report["g4_boxes"]["G4.4_learned_routing"], "NOT_UNLOCKED")
        self.assertEqual(report["g4_boxes"]["G4.2"]["sweep_reuse_density"], "CHECKED_TOY")
        self.assertEqual(report["g4_boxes"]["G4.2"]["sweep_drift"], "CHECKED_TOY")
        self.assertEqual(report["pr154_disposition"]["head"], H.PR154_HEAD)

    def test_summary_json_roundtrip(self):
        report, path = H.write_report(HERE / "SUMMARY.json")
        loaded = json.loads(path.read_text())
        self.assertEqual(loaded["terminals"], report["terminals"])
        self.assertEqual(loaded["schema"], "ocm.g4-horizon-exact.v1")


if __name__ == "__main__":
    unittest.main()
