#!/usr/bin/env python3
"""AE5 tests: two-route agreement, hostile potency and detection, nulls."""
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ae5_causal_state_audit_v1 as A        # noqa: E402
import independent_process_oracle_v1 as O    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = A.build_result()
R = RES["results"]


class TestVerdict(unittest.TestCase):
    def test_green(self):
        for name in sorted(RES["checks"]):
            self.assertTrue(RES["checks"][name], "check failed: " + name)
        self.assertEqual(RES["verdict"], "GREEN")
        self.assertEqual(RES["rows_closed"], 5)
        self.assertEqual(RES["issue_comment_id"], 5692689542)

    def test_row_five_is_declared_elsewhere(self):
        self.assertIn("morphology-sweep", RES["row_closed_elsewhere"])

    def test_no_float_anywhere(self):
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

    def test_sources_never_use_floats_or_logs(self):
        for fn in ("ae5_causal_state_audit_v1.py",
                   "independent_process_oracle_v1.py"):
            with open(os.path.join(HERE, fn)) as fh:
                src = fh.read()
            for bad in ("float(", "math.log", "import math", "0.5"):
                self.assertNotIn(bad, src, fn + " uses " + bad)

    def test_deterministic(self):
        self.assertEqual(
            json.dumps(A.build_result(), sort_keys=True),
            json.dumps(RES, sort_keys=True),
        )


class TestTwoRoutes(unittest.TestCase):
    def test_joints_agree_on_the_whole_family(self):
        n = 0
        for proc in A.FAMILY:
            self.assertEqual(A.joint(proc), O.joint(proc))
            n += 1
        self.assertEqual(n, 2187)

    def test_quantities_agree(self):
        for proc in A.FAMILY[::7]:
            jt = A.joint(proc)
            ms = A.dyadic_state_masses(jt)
            self.assertEqual(
                ms, O.state_masses(jt, A.PREFIX_LEN, A.HORIZON)
            )
            if A.is_dyadic_distribution(ms):
                self.assertEqual(A.entropy_exact(ms), O.entropy(ms))
            self.assertEqual(
                A.hankel_rank(jt, A.SPLIT), O.hankel_rank(jt, A.SPLIT)
            )
            self.assertEqual(A.description_length(proc), O.description_length(proc))
            self.assertEqual(
                A.predictive_state_cardinality(jt),
                len(O.epsilon_machine_states(jt)),
            )
            if A.excess_entropy_is_exact(jt):
                self.assertEqual(
                    A.excess_entropy(jt, A.SPLIT), O.excess_entropy(jt, A.SPLIT)
                )

    def test_dyadic_exponent_agrees(self):
        for a in range(0, 12):
            p = F(1, 1 << a)
            self.assertEqual(A.dyadic_exponent(p), O.dyadic_exp(p))
        self.assertIsNone(A.dyadic_exponent(F(3, 4)))
        self.assertIsNone(O.dyadic_exp(F(3, 4)))


class TestNamedResults(unittest.TestCase):
    def test_ae5_1_horizon_scope(self):
        s = R["AE5_1_horizon_scope"]
        self.assertTrue(s["refinement_is_monotone_on_every_member"])
        self.assertIsNotNone(s["horizon_1_counterexample"])
        seq = s["horizon_1_counterexample"]["classes_by_horizon"]
        self.assertLess(seq[0], seq[-1])
        proc = tuple(
            "F" if v == "F" else int(v)
            for v in s["horizon_1_counterexample"]["proc"]
        )
        jt = O.joint(proc)
        self.assertLess(len(O.classes(jt, 1, 1)), len(O.classes(jt, 1, 2)))

    def test_ae5_2_complexity_and_excess_entropy(self):
        s = R["AE5_2_statistical_complexity_and_excess_entropy"]
        self.assertEqual(s["tree_processes_enumerated"], 2187)
        self.assertEqual(
            s["family_size"] + s["excluded_for_non_dyadic_state_masses"], 2187
        )
        self.assertTrue(s["E_le_C_mu_holds_on_all"])
        self.assertEqual(
            s["E_le_C_mu_holds_on"],
            s["members_with_exactly_computable_excess_entropy"],
        )
        self.assertTrue(s["every_member_is_dyadic"])
        self.assertIsNotNone(s["strict_crypticity_witness"])
        w = s["strict_crypticity_witness"]
        self.assertGreater(F(w["crypticity"]), 0)
        self.assertEqual(F(w["C_mu"]) - F(w["E"]), F(w["crypticity"]))
        proc = tuple("F" if v == "F" else int(v) for v in w["proc"])
        jt = O.joint(proc)
        self.assertEqual(
            O.entropy(O.state_masses(jt, A.PREFIX_LEN, A.HORIZON)), F(w["C_mu"])
        )
        self.assertEqual(O.excess_entropy(jt, A.SPLIT), F(w["E"]))
        nu = s["non_uniform_state_mass_witness"]
        self.assertIsNotNone(nu)
        self.assertGreater(len(set(nu["state_masses"])), 1)

    def test_ae5_3_parent_ownership(self):
        s = R["AE5_3_parent_ownership_audit"]
        self.assertEqual(s["verdict_counts"].get("PARENT_SUFFICIENT"), 4)
        self.assertEqual(s["verdict_counts"].get("RESIDUAL"), 1)
        self.assertFalse(s["novelty_claimed_for_gmi_state_complexity"])
        self.assertTrue(s["parent_sufficient_is_a_success_terminal"])
        for row in s["rows"]:
            self.assertGreater(len(row["parent"]), 20)

    def test_ae5_4_disagreement(self):
        s = R["AE5_4_four_quantity_disagreement"]
        self.assertEqual(s["ordered_pairs"], 12)
        self.assertGreaterEqual(s["ordered_pairs_disagreeing"], 11)
        self.assertTrue(s["every_unordered_pair_is_non_equivalent"])
        self.assertTrue(s["rank_le_state_count_verified_on_every_member"])
        self.assertGreater(s["ordered_pairs_with_a_strict_order_reversal"], 0)
        for key in sorted(s["matrix"]):
            ent = s["matrix"][key]
            if ent["equal_value_disagreement"] is None:
                self.assertIn(key, s["determined_directions"])
        # re-verify one equal-value disagreement through the oracle
        ent = s["matrix"]["S_vs_DL"]["equal_value_disagreement"]
        self.assertIsNotNone(ent)
        pa = tuple("F" if v == "F" else int(v) for v in ent["proc_a"])
        pb = tuple("F" if v == "F" else int(v) for v in ent["proc_b"])
        self.assertEqual(
            len(O.epsilon_machine_states(O.joint(pa))),
            len(O.epsilon_machine_states(O.joint(pb))),
        )
        self.assertNotEqual(
            O.description_length(pa), O.description_length(pb)
        )

    def test_ae5_6_gap_preservation(self):
        s = R["AE5_6_finite_horizon_gap_preservation"]
        self.assertTrue(s["claim_is_finite_horizon_only"])
        self.assertGreaterEqual(
            len(s["infinite_horizon_assumptions_that_would_be_required_open"]), 5
        )
        self.assertEqual(s["gap_alarms_on_this_receipt"], 0)
        self.assertEqual(s["gap_alarm_paths"], [])
        self.assertTrue(s["horizon_truncation_loses_information"])
        w = s["truncation_witness"]
        self.assertLess(w["classes_at_horizon_1"], w["classes_at_horizon_2"])
        proc = tuple("F" if v == "F" else int(v) for v in w["proc"])
        jt = O.joint(proc)
        self.assertEqual(len(O.classes(jt, 1, 1)), w["classes_at_horizon_1"])
        self.assertEqual(len(O.classes(jt, 1, 2)), w["classes_at_horizon_2"])
        self.assertIn("INFINITE_HORIZON_EQUIVALENCE_PROVED",
                      RES["forbidden_promotions"])
        planted = {"a": {"infinite_horizon_equivalence": True}}
        self.assertEqual(len(A.gap_preservation_guard(planted)), 1)
        self.assertEqual(
            A.gap_preservation_guard({"infinite_horizon_assumptions": []}), []
        )


class TestHostilesAndNull(unittest.TestCase):
    def test_hostiles(self):
        ids = set()
        for h in RES["hostiles"]:
            ids.add(h["id"])
            self.assertTrue(h["perturbation_moved_its_quantity"], h["id"])
            self.assertTrue(h["detected"], h["id"])
        self.assertEqual(len(ids), 5)

    def test_non_dyadic_entropy_raises_in_both_routes(self):
        self.assertRaises(ValueError, A.entropy_exact, [F(1, 3), F(2, 3)])
        self.assertRaises(ValueError, O.entropy, [F(1, 3), F(2, 3)])

    def test_null(self):
        n = RES["null"]
        self.assertEqual(n["shuffle_trials"], 200)
        self.assertEqual(n["shuffle_trials_matching"], 0)
        self.assertEqual(n["true_family_alarms"], 0)


class TestArtifacts(unittest.TestCase):
    def test_parent_pins(self):
        aud = RES["parent_audit"]
        self.assertTrue(aud["all_ok"])
        self.assertEqual(len(aud["rows"]), 5)
        for row in aud["rows"]:
            self.assertTrue(row["blob_ok"], row["path"])
            self.assertTrue(row["claim_ok"], row["path"])

    def test_reconciliation_spec(self):
        path = os.path.join(
            HERE, "ISSUE_833_RECONCILIATION_AE5_CAUSAL_STATE_AUDIT_V1.json"
        )
        with open(path) as fh:
            spec = json.load(fh)
        self.assertEqual(spec["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(spec["issue"], 833)
        self.assertEqual(spec["issue_comment_id"], 5692689542)
        self.assertEqual(spec["claim_ceiling"], RES["claim_ceiling"])
        self.assertEqual(len(spec["replacements"]), 5)
        self.assertEqual(len(spec["not_closed"]), 1)
        seen = set()
        for rep in spec["replacements"]:
            self.assertTrue(rep["old"].startswith("- [ ] "))
            self.assertTrue(rep["new"].startswith("- [x] "))
            self.assertTrue(rep["new"][6:].startswith(rep["old"][6:]))
            self.assertNotIn(rep["old"], seen)
            seen.add(rep["old"])
            self.assertEqual(
                rep["anchor"],
                "### AE5 — Predictive-state / causal-state unification audit",
            )
        self.assertNotIn(spec["not_closed"][0]["old"], seen)
        self.assertIn("morphology-sweep", spec["not_closed"][0]["reason"])

    def test_manifest(self):
        with open(os.path.join(HERE, "MANIFEST_V1.json")) as fh:
            m = json.load(fh)
        self.assertEqual(m["claim_ceiling"], RES["claim_ceiling"])
        self.assertEqual(m["source_main"], RES["source_main"])
        self.assertEqual(m["freeze_commit"], RES["freeze_commit"])
        self.assertEqual(m["rows_closed"], 5)
        self.assertEqual(len(m["parent_pins"]), 5)

    def test_receipt_matches_committed(self):
        with open(os.path.join(HERE, "RESULT_V1.json")) as fh:
            committed = json.load(fh)
        self.assertEqual(
            json.dumps(committed, sort_keys=True), json.dumps(RES, sort_keys=True)
        )


if __name__ == "__main__":
    unittest.main()
