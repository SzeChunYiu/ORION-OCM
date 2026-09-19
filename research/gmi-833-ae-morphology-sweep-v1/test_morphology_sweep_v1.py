#!/usr/bin/env python3
"""AE morphology sweep tests: two-route agreement, hostile potency, detection."""
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import morphology_sweep_v1 as A            # noqa: E402
import independent_sweep_oracle_v1 as O    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = A.build_result()
R = RES["results"]


class TestVerdict(unittest.TestCase):
    def test_green(self):
        for name in sorted(RES["checks"]):
            self.assertTrue(RES["checks"][name], "check failed: " + name)
        self.assertEqual(RES["verdict"], "GREEN")

    def test_no_float_anywhere_in_receipt(self):
        def walk(o):
            if isinstance(o, float):
                self.fail("float in receipt")
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, (list, tuple)):
                for v in o:
                    walk(v)
        walk(RES)

    def test_source_never_uses_floats_or_logs(self):
        for fn in ("morphology_sweep_v1.py", "independent_sweep_oracle_v1.py"):
            with open(os.path.join(HERE, fn)) as fh:
                src = fh.read()
            for bad in ("float(", "math.log", "import math", "/ 2.0", "0.5"):
                self.assertNotIn(bad, src, fn + " uses " + bad)

    def test_deterministic(self):
        self.assertEqual(
            json.dumps(A.build_result(), sort_keys=True),
            json.dumps(RES, sort_keys=True),
        )

    def test_rows_closed(self):
        self.assertEqual(RES["rows_closed"], 4)
        self.assertEqual(RES["issue_comment_id"], 5692689542)


class TestTwoRoutes(unittest.TestCase):
    def test_profiles_agree_on_the_whole_census(self):
        n = 0
        for table in A.all_deterministic_tables():
            a = A.profile_route_a(A.deterministic_world(table, "t"))
            b = O.deterministic_profile(table)
            self.assertEqual(a, b, "route disagreement on " + str(table))
            n += 1
        self.assertEqual(n, 256)

    def test_selection_agrees_on_the_whole_census(self):
        for table in A.all_deterministic_tables():
            prof = O.deterministic_profile(table)
            a = A.selection_key(prof, A.TAU, A.PRICE_A)
            b = O.selection(prof, A.TAU, A.PRICE_A)
            self.assertEqual(a, b)
            a2 = A.selection_key(prof, A.TAU, A.PRICE_B)
            b2 = O.selection(prof, A.TAU, A.PRICE_B)
            self.assertEqual(a2, b2)

    def test_causal_fixtures_agree(self):
        obs_l, obs_r, do_l, do_r = A.causal_fixtures()
        pairs = (
            (obs_l, O.world_L(False)),
            (obs_r, O.world_R(False)),
            (do_l, O.world_L(True)),
            (do_r, O.world_R(True)),
        )
        for wa, (px, py1) in pairs:
            self.assertEqual(wa.px, px)
            self.assertEqual(wa.py1, py1)
            self.assertEqual(A.profile_route_a(wa), O.profile(px, py1))

    def test_oracle_confirms_markov_equivalence(self):
        self.assertEqual(O.joint(*O.world_L(False)), O.joint(*O.world_R(False)))
        self.assertNotEqual(O.joint(*O.world_L(True)), O.joint(*O.world_R(True)))


class TestNamedResults(unittest.TestCase):
    def test_sweep1_raw_information_fails(self):
        c = R["SWEEP_1_raw_information"]["census"]
        self.assertEqual(c["worlds_used"], 256)
        self.assertGreater(c["conflicting_pairs"], 0)
        self.assertFalse(c["functionally_determines_selection"])
        w = R["SWEEP_1_raw_information"]["witness_pair"]
        ta, tb = tuple(w["table_a"]), tuple(w["table_b"])
        self.assertEqual(
            A.raw_information_invariant(ta), A.raw_information_invariant(tb)
        )
        sa = O.selection(O.deterministic_profile(ta), A.TAU, A.PRICE_A)
        sb = O.selection(O.deterministic_profile(tb), A.TAU, A.PRICE_A)
        self.assertNotEqual(sa, sb)

    def test_sweep2_usable_scalar_fails(self):
        c = R["SWEEP_2_usable_information_scalar"]["census"]
        self.assertGreater(c["conflicting_pairs"], 0)
        w = R["SWEEP_2_usable_information_scalar"]["witness_pair"]
        ta, tb = tuple(w["table_a"]), tuple(w["table_b"])
        pa, pb = O.deterministic_profile(ta), O.deterministic_profile(tb)
        ua = pa[O.ORDER.index("m2_arity2_junta")] - pa[O.ORDER.index("m0_constant")]
        ub = pb[O.ORDER.index("m2_arity2_junta")] - pb[O.ORDER.index("m0_constant")]
        self.assertEqual(ua, ub)
        self.assertEqual(str(ua), w["usable_r0"])
        self.assertNotEqual(
            O.selection(pa, A.TAU, A.PRICE_A), O.selection(pb, A.TAU, A.PRICE_A)
        )

    def test_sweep3_profile_predicts_and_is_non_vacuous(self):
        s = R["SWEEP_3_resource_conditioned_vector"]
        self.assertEqual(s["census"]["conflicting_pairs"], 0)
        self.assertTrue(s["census"]["functionally_determines_selection"])
        nv = s["non_vacuity"]
        self.assertTrue(nv["strictly_finer_than_raw_information"])
        self.assertTrue(nv["strictly_finer_than_usable_scalar"])
        a, b = nv["strictly_coarser_than_world_witness"]
        self.assertNotEqual(a, b)
        self.assertEqual(
            O.deterministic_profile(tuple(a)), O.deterministic_profile(tuple(b))
        )
        self.assertGreater(len(s["minimal_sufficient_subvectors"]), 0)
        for sub in s["minimal_sufficient_subvectors"]:
            idx = [O.ORDER.index(m) for m in sub]
            buckets = {}
            for table in A.all_deterministic_tables():
                prof = O.deterministic_profile(table)
                key = tuple(prof[i] for i in idx)
                sel = O.selection(prof, A.TAU, A.PRICE_A)
                if key in buckets:
                    self.assertEqual(buckets[key], sel)
                buckets[key] = sel

    def test_sweep4_locality_boundary(self):
        s = R["SWEEP_4_locality_phase_boundary"]
        self.assertEqual(s["locality_exploitable_order_parity"], 3)
        self.assertEqual(s["locality_exploitable_order_and"], 2)
        self.assertEqual(s["profile_parity"]["m2_arity2_junta"], "1/2")
        self.assertEqual(s["profile_parity"]["m4_gf2_affine"], "1")
        self.assertEqual(s["profile_and"]["m2_arity2_junta"], "1")
        self.assertEqual(s["profile_and"]["m4_gf2_affine"], "3/4")
        self.assertEqual(s["selection_parity_at_tau_star"], ["m4_gf2_affine"])
        self.assertEqual(s["selection_and_at_tau_star"], ["m2_arity2_junta"])
        self.assertTrue(s["local_class_inactive_for_parity_above_boundary"])
        self.assertEqual(s["displacement_boundary_tau"], "1/2")
        # phase map endpoints are exact rationals and the map is a partition
        for pm in (s["phase_map_parity"], s["phase_map_and"]):
            prev = F(0)
            for ph in pm:
                lo, hi = F(ph["tau_interval"][0]), F(ph["tau_interval"][1])
                self.assertEqual(lo, prev)
                self.assertGreater(hi, lo)
                prev = hi
            self.assertEqual(prev, F(1))

    def test_sweep5_causal_intervention(self):
        s = R["SWEEP_5_causal_intervention"]
        self.assertTrue(s["observational_joints_identical"])
        self.assertFalse(s["interventional_joints_identical"])
        self.assertEqual(s["observational_selection_L"], s["observational_selection_R"])
        self.assertNotEqual(
            s["interventional_selection_L"], s["interventional_selection_R"]
        )
        self.assertEqual(s["interventional_selection_L"], ["SELECTED", ["m1_arity1_junta"]])
        self.assertEqual(s["interventional_selection_R"], ["NO_VIABLE_MORPHOLOGY", []])
        self.assertEqual(s["profile_do_R"]["m1_arity1_junta"], "1/2")
        self.assertEqual(s["profile_do_L"]["m1_arity1_junta"], "3/4")

    def test_sweep6_ae5_scalars_all_fail(self):
        s = R["SWEEP_6_ae5_scalar_family"]["scalars"]
        self.assertEqual(len(s), 4)
        for name in sorted(s):
            self.assertGreater(
                s[name]["conflicting_pairs"], 0, name + " unexpectedly predicts"
            )
            self.assertGreater(s[name]["worlds_used"], 0)


class TestHostiles(unittest.TestCase):
    def test_every_hostile_is_potent_and_detected(self):
        ids = set()
        for h in RES["hostiles"]:
            ids.add(h["id"])
            self.assertTrue(
                h["perturbation_moved_its_quantity"],
                h["id"] + " could not move the quantity it perturbs",
            )
            self.assertTrue(h["detected"], h["id"] + " not detected")
        self.assertEqual(len(ids), 5)

    def test_zero_price_guard_raises(self):
        prof = A.profile_route_a(A.locality_fixtures()[0])
        self.assertRaises(ValueError, A.select, prof, A.TAU, (1, 0, 1))
        self.assertRaises(ValueError, O.selection, prof, A.TAU, (0, 1, 1))

    def test_observational_only_hostile_really_is_wrong(self):
        obs_l, obs_r, do_l, do_r = A.causal_fixtures()
        obs_sel = (
            O.selection(O.profile(obs_l.px, obs_l.py1), A.TAU, A.PRICE_A),
            O.selection(O.profile(obs_r.px, obs_r.py1), A.TAU, A.PRICE_A),
        )
        do_sel = (
            O.selection(O.profile(do_l.px, do_l.py1), A.TAU, A.PRICE_A),
            O.selection(O.profile(do_r.px, do_r.py1), A.TAU, A.PRICE_A),
        )
        self.assertEqual(obs_sel[0], obs_sel[1])
        self.assertNotEqual(do_sel[0], do_sel[1])
        self.assertNotEqual(obs_sel, do_sel)


class TestNull(unittest.TestCase):
    def test_shuffle_null_never_reaches_zero(self):
        n = RES["null"]
        self.assertEqual(n["shuffle_trials"], 200)
        self.assertEqual(n["shuffle_trials_with_zero_conflicts"], 0)
        self.assertGreater(n["shuffle_min_conflicts"], 0)

    def test_no_alarm_on_the_true_result(self):
        self.assertEqual(RES["null"]["true_profile_conflicts"], 0)

    def test_price_null(self):
        n = RES["null"]
        self.assertEqual(n["random_price_trials"], 200)
        self.assertEqual(n["sel1_pareto_violations"], 0)
        self.assertEqual(
            n["random_prices_where_raw_information_still_fails"],
            n["random_price_trials"],
        )


class TestParentsAndReconciliation(unittest.TestCase):
    def test_parent_pins(self):
        aud = RES["parent_audit"]
        self.assertTrue(aud["all_ok"])
        self.assertEqual(len(aud["rows"]), 7)
        for row in aud["rows"]:
            self.assertTrue(row["blob_ok"], row["path"])
            self.assertTrue(row["claim_ok"], row["path"])

    def test_reconciliation_spec(self):
        path = os.path.join(
            HERE, "ISSUE_833_RECONCILIATION_AE_MORPHOLOGY_SWEEP_V1.json"
        )
        with open(path) as fh:
            spec = json.load(fh)
        self.assertEqual(spec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(spec["issue"], 833)
        self.assertEqual(spec["issue_comment_id"], 5692689542)
        self.assertEqual(spec["claim_ceiling"], RES["claim_ceiling"])
        self.assertEqual(len(spec["replacements"]), 4)
        anchors = set()
        seen = set()
        for rep in spec["replacements"]:
            self.assertTrue(rep["old"].startswith("- [ ] "))
            self.assertTrue(rep["new"].startswith("- [x] "))
            self.assertTrue(rep["new"][6:].startswith(rep["old"][6:]))
            self.assertNotIn(rep["old"], seen)
            seen.add(rep["old"])
            self.assertTrue(rep["anchor"].startswith("### AE"))
            anchors.add(rep["anchor"])
        self.assertEqual(len(anchors), 4)

    def test_manifest(self):
        with open(os.path.join(HERE, "MANIFEST_V1.json")) as fh:
            m = json.load(fh)
        self.assertEqual(m["claim_ceiling"], RES["claim_ceiling"])
        self.assertEqual(m["source_main"], RES["source_main"])
        self.assertEqual(m["freeze_commit"], RES["freeze_commit"])
        self.assertEqual(
            sorted(m["forbidden_promotions"]), sorted(RES["forbidden_promotions"])
        )
        self.assertEqual(len(m["parent_pins"]), 7)

    def test_receipt_matches_committed_result(self):
        with open(os.path.join(HERE, "RESULT_V1.json")) as fh:
            committed = json.load(fh)
        self.assertEqual(
            json.dumps(committed, sort_keys=True), json.dumps(RES, sort_keys=True)
        )


if __name__ == "__main__":
    unittest.main()
