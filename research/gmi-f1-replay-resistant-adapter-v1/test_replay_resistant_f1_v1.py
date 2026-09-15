import importlib.util
import itertools
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("rrf1_adapter", HERE / "replay_resistant_f1_v1.py")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

Campaign = MOD.Campaign
ComparisonContract = MOD.ComparisonContract
DerivedAffineContract = MOD.DerivedAffineContract
affine_interval = MOD.affine_interval


def contract(cid="c", version=1, tau_parent=F(1, 2), tau_twin=F(1, 4)):
    return ComparisonContract(cid, "planning_horizon", version, f"system-{version}", "parent", "twin", tau_parent, tau_twin)


def feed(campaign, row_id, value, n, prefix):
    for i in range(n):
        origin = f"{prefix}-o-{i}"
        token = f"{prefix}-t-{i}"
        campaign.reserve(row_id, origin, token)
        campaign.observe(row_id, origin, token, value)


class ContractTests(unittest.TestCase):
    def test_contract_is_frozen_and_validated(self):
        c = contract()
        with self.assertRaises(Exception):
            c.tau_parent = F(0)
        with self.assertRaises(ValueError):
            contract(tau_twin=F(5, 4))
        with self.assertRaises(ValueError):
            ComparisonContract("", "x", 1, "s", "p", "t", F(0), F(0))

    def test_rows_allocate_monotonically_across_adaptive_registration(self):
        camp = Campaign(F(1, 20))
        p1, t1 = camp.register_comparison(contract("first", 1))
        camp.reserve(p1, "o", "t")
        camp.observe(p1, "o", "t", F(0))
        p2, t2 = camp.register_comparison(contract("second", 1))
        self.assertEqual([camp.row_stats(x)["row_index"] for x in (p1, t1, p2, t2)], [1, 2, 3, 4])
        self.assertEqual(camp.row_stats(p2)["visits"], 0)

    def test_duplicate_comparison_version_rejected(self):
        camp = Campaign(F(1, 20))
        camp.register_comparison(contract())
        with self.assertRaises(ValueError):
            camp.register_comparison(contract())


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.camp = Campaign(F(1, 20))
        self.p, self.t = self.camp.register_comparison(contract())

    def test_observe_before_reserve_is_rejected(self):
        with self.assertRaises(ValueError):
            self.camp.observe(self.p, "origin", "token", F(0))
        self.assertEqual(self.camp.row_stats(self.p)["visits"], 0)

    def test_token_replay_adds_no_evidence(self):
        self.camp.reserve(self.p, "origin", "token")
        self.camp.observe(self.p, "origin", "token", F(1))
        with self.assertRaises(ValueError):
            self.camp.observe(self.p, "origin", "token", F(1))
        self.assertEqual(self.camp.row_stats(self.p)["visits"], 1)
        self.assertEqual(self.camp.row_stats(self.p)["acquisition_charges"], 1)

    def test_token_cannot_be_reserved_twice(self):
        self.camp.reserve(self.p, "origin-a", "token")
        with self.assertRaises(ValueError):
            self.camp.reserve(self.t, "origin-b", "token")
        self.assertEqual(self.camp.row_stats(self.t)["acquisition_charges"], 0)

    def test_origin_is_globally_single_use(self):
        self.camp.reserve(self.p, "origin", "token-a")
        with self.assertRaises(ValueError):
            self.camp.reserve(self.t, "origin", "token-b")
        self.assertEqual(self.camp.row_stats(self.t)["acquisition_charges"], 0)

    def test_wrong_origin_does_not_consume_reservation(self):
        self.camp.reserve(self.p, "origin", "token")
        with self.assertRaises(ValueError):
            self.camp.observe(self.p, "wrong", "token", F(0))
        self.assertEqual(self.camp.row_stats(self.p)["pending"], 1)
        self.camp.observe(self.p, "origin", "token", F(0))
        self.assertEqual(self.camp.row_stats(self.p)["visits"], 1)

    def test_malformed_retires_and_preserves_charge(self):
        self.camp.reserve(self.p, "origin", "token")
        self.assertEqual(self.camp.observe(self.p, "origin", "token", F(2)), "RETIRED_MALFORMED")
        stats = self.camp.row_stats(self.p)
        self.assertTrue(stats["retired"])
        self.assertEqual(stats["visits"], 0)
        self.assertEqual(stats["acquisition_charges"], 1)
        with self.assertRaises(RuntimeError):
            self.camp.reserve(self.p, "new-origin", "new-token")

    def test_non_exact_outcome_is_malformed(self):
        self.camp.reserve(self.p, "origin", "token")
        self.assertEqual(self.camp.observe(self.p, "origin", "token", 0.0), "RETIRED_MALFORMED")
        self.assertEqual(self.camp.row_stats(self.p)["visits"], 0)

    def test_missing_retires_and_preserves_charge(self):
        self.camp.reserve(self.t, "origin", "token")
        self.assertEqual(self.camp.mark_missing(self.t, "origin", "token"), "RETIRED_MISSING")
        stats = self.camp.row_stats(self.t)
        self.assertTrue(stats["retired"])
        self.assertEqual(stats["visits"], 0)
        self.assertEqual(stats["acquisition_charges"], 1)

    def test_retirement_keeps_all_reserved_charges(self):
        self.camp.reserve(self.p, "o1", "t1")
        self.camp.reserve(self.p, "o2", "t2")
        self.camp.mark_missing(self.p, "o1", "t1")
        stats = self.camp.row_stats(self.p)
        self.assertEqual(stats["acquisition_charges"], 2)
        self.assertEqual(stats["pending"], 0)

    def test_declared_metadata_does_not_claim_freshness(self):
        for i in range(4):
            o, tok = f"claimed-origin-{i}", f"tok-{i}"
            self.camp.reserve(self.p, o, tok)
            self.camp.observe(self.p, o, tok, F(1))
        self.assertEqual(self.camp.row_stats(self.p)["visits"], 4)


class StatisticalBridgeTests(unittest.TestCase):
    def test_zero_visits_maps_to_full_paired_difference_interval(self):
        camp = Campaign(F(1, 20))
        p, _ = camp.register_comparison(contract())
        self.assertEqual(camp.row_interval(p), (F(-1), F(1)))

    def test_affine_map_matches_parent_interval_exactly(self):
        camp = Campaign(F(1, 20))
        p, _ = camp.register_comparison(contract())
        feed(camp, p, F(1, 2), 17, "half")
        stats = camp.row_stats(p)
        ly, uy = MOD.ARC6.interval_from_sum(stats["mapped_sum"], camp.alpha, stats["row_index"], stats["visits"])
        self.assertEqual(camp.row_interval(p), (2 * ly - 1, 2 * uy - 1))

    def test_registered_full_control_is_supported(self):
        camp = Campaign(F(1, 20))
        p, t = camp.register_comparison(contract())
        feed(camp, p, F(1), 1024, "pos")
        feed(camp, t, F(0), 1024, "twin")
        self.assertEqual(camp.decision("c", 1), "SUPPORTED")

    def test_small_prefix_abstains(self):
        camp = Campaign(F(1, 20))
        p, t = camp.register_comparison(contract())
        feed(camp, p, F(1), 64, "pos")
        feed(camp, t, F(0), 64, "twin")
        self.assertEqual(camp.decision("c", 1), "CANNOT_IDENTIFY")

    def test_parent_nonseparation_terminal(self):
        camp = Campaign(F(1, 20))
        p, t = camp.register_comparison(contract(tau_parent=F(3, 4), tau_twin=F(1)))
        feed(camp, p, F(0), 4096, "pos")
        feed(camp, t, F(0), 4096, "twin")
        self.assertEqual(camp.decision("c", 1), "PARENT_NOT_SEPARATED")

    def test_twin_noncollapse_terminal(self):
        camp = Campaign(F(1, 20))
        p, t = camp.register_comparison(contract(tau_parent=F(0), tau_twin=F(1, 4)))
        feed(camp, p, F(1), 4096, "pos")
        feed(camp, t, F(1), 4096, "twin")
        self.assertEqual(camp.decision("c", 1), "TWIN_NOT_COLLAPSED")

    def test_retired_row_forces_abstention(self):
        camp = Campaign(F(1, 20))
        p, _ = camp.register_comparison(contract())
        camp.reserve(p, "o", "t")
        camp.mark_missing(p, "o", "t")
        self.assertEqual(camp.decision("c", 1), "CANNOT_IDENTIFY_RETIRED")


class CompositionTests(unittest.TestCase):
    def test_affine_interval_matches_every_corner(self):
        families = [
            ((F(2), (F(-1), F(3))), (F(-3), (F(1, 2), F(2))), (F(1, 4), (F(-2), F(5)))),
            ((F(-1), (F(-3, 2), F(7, 3))), (F(5, 2), (F(0), F(4, 3)))),
        ]
        for terms in families:
            lo, hi = affine_interval(terms, F(2, 7))
            values = []
            for corner in itertools.product(*[(interval[0], interval[1]) for _w, interval in terms]):
                values.append(F(2, 7) + sum((w * x for (w, _interval), x in zip(terms, corner)), F(0)))
            self.assertEqual((lo, hi), (min(values), max(values)))

    def test_derived_must_be_frozen_before_acquisition(self):
        camp = Campaign(F(1, 20))
        p, t = camp.register_comparison(contract())
        camp.reserve(p, "o", "tok")
        with self.assertRaises(ValueError):
            camp.register_derived(DerivedAffineContract("late", ((p, F(1)), (t, F(-1)))))

    def test_derived_contrast_contains_truth(self):
        camp = Campaign(F(1, 20))
        p, t = camp.register_comparison(contract())
        camp.register_derived(DerivedAffineContract("contrast", ((p, F(1)), (t, F(-1)))))
        feed(camp, p, F(1), 1024, "pos")
        feed(camp, t, F(0), 1024, "twin")
        lo, hi = camp.derived_interval("contrast")
        self.assertLessEqual(lo, F(1))
        self.assertGreaterEqual(hi, F(1))

    def test_retired_input_invalidates_derived_interval(self):
        camp = Campaign(F(1, 20))
        p, t = camp.register_comparison(contract())
        camp.register_derived(DerivedAffineContract("contrast", ((p, F(1)), (t, F(-1)))))
        camp.reserve(p, "o", "tok")
        camp.mark_missing(p, "o", "tok")
        with self.assertRaises(RuntimeError):
            camp.derived_interval("contrast")

    def test_two_95_percent_marginals_need_not_have_95_percent_joint_coverage(self):
        universe = set(range(20))
        cover_a = universe - {0}
        cover_b = universe - {1}
        self.assertEqual(F(len(cover_a), 20), F(19, 20))
        self.assertEqual(F(len(cover_b), 20), F(19, 20))
        self.assertEqual(F(len(cover_a & cover_b), 20), F(9, 10))


class DevelopmentTests(unittest.TestCase):
    def test_new_developmental_version_inherits_no_visits(self):
        camp = Campaign(F(1, 20))
        p1, _ = camp.register_comparison(contract("c", 1))
        feed(camp, p1, F(1), 8, "old")
        p2, t2 = camp.register_comparison(contract("c", 2))
        self.assertEqual((camp.row_stats(p2)["visits"], camp.row_stats(t2)["visits"]), (0, 0))
        self.assertGreater(camp.row_stats(p2)["row_index"], camp.row_stats(p1)["row_index"])

    def test_old_token_cannot_be_reused_by_new_version(self):
        camp = Campaign(F(1, 20))
        p1, _ = camp.register_comparison(contract("c", 1))
        camp.reserve(p1, "old-origin", "old-token")
        camp.observe(p1, "old-origin", "old-token", F(1))
        p2, _ = camp.register_comparison(contract("c", 2))
        with self.assertRaises(ValueError):
            camp.reserve(p2, "new-origin", "old-token")


class ReceiptTests(unittest.TestCase):
    def test_receipt_is_deterministic_and_has_frozen_terminals(self):
        a = MOD.build_receipt()
        b = MOD.build_receipt()
        self.assertEqual(a, b)
        self.assertEqual(a["full_control"]["decision"], "SUPPORTED")
        self.assertEqual(a["small_prefix_control"]["decision"], "CANNOT_IDENTIFY")
        self.assertTrue(a["full_control"]["contrast_contains_one"])
        self.assertTrue(a["provenance_controls"]["replay_blocked"])
        self.assertEqual(a["marginal_joint_counterexample"]["joint_coverage_with_disjoint_failures"], "9/10")


if __name__ == "__main__":
    unittest.main()
