#!/usr/bin/env python3
"""GMI #833 AE15 tests: two-route agreement, hostile potency then detection,
bound falsifiability, the null in both directions, and byte determinism.

Runnable as `python3 -I -B test_ae15_world_model_necessity_v1.py -v` and
`python3 -I -O -B test_ae15_world_model_necessity_v1.py -v`.  Stdlib only.

No bare `assert` statement appears anywhere in this file: `-O` strips those,
which would turn a check into a vacuous pass.  Every check is a
unittest.TestCase assertion method or an explicit raise.

Every hostile is asserted in two stages and in this order:
  (1) POTENCY  -- the perturbation actually moves the quantity it targets;
  (2) DETECTION -- the checker flags the perturbed object.
For the one INVERTED hostile the register names (H_LATENT_RELABEL), stage (2)
asserts the checker's SILENCE instead.
"""
import ast
import hashlib
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ae15_world_model_necessity_v1 as A        # noqa: E402
import independent_world_model_oracle_v1 as O    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = A.build()
R = RES["results"]
RO, MN, SW, SWA = A.build_worlds()
OR = O.oracle_roster()


def a_reactive_map(W, pi):
    return dict((W.onames[o], W.anames[pi[o]]) for o in range(W.nO))


class TestVerdict(unittest.TestCase):
    def test_green(self):
        self.assertEqual(RES["verdict"], "GREEN")
        for name in sorted(RES["checks"]):
            self.assertTrue(RES["checks"][name], "check failed: " + name)

    def test_top_level_keys(self):
        for k in ("schema", "issue", "issue_comment_id", "package",
                  "source_main", "freeze_commit", "claim_ceiling", "verdict",
                  "checks", "results", "bounds", "hostiles", "null",
                  "prospective_predictions", "forbidden_promotions"):
            self.assertIn(k, RES)
        self.assertEqual(RES["issue"], 833)
        self.assertEqual(RES["issue_comment_id"], 5692689542)

    def test_no_float_anywhere_in_receipt(self):
        def walk(o):
            if isinstance(o, float):
                self.fail("float found in receipt")
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(RES)

    def test_deterministic(self):
        self.assertEqual(json.dumps(A.build(), sort_keys=True, indent=2),
                         json.dumps(RES, sort_keys=True, indent=2))

    def test_receipt_file_matches_if_present(self):
        p = os.path.join(HERE, "RESULT_V1.json")
        if not os.path.exists(p):
            self.skipTest("RESULT_V1.json not yet written")
        fh = open(p)
        try:
            text = fh.read()
        finally:
            fh.close()
        self.assertEqual(text,
                         json.dumps(RES, indent=2, sort_keys=True) + "\n")

    def test_register_digest(self):
        p = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
        fh = open(p)
        try:
            reg = json.loads(fh.read())
        finally:
            fh.close()
        core = dict(reg)
        core.pop("self_digest_sha256")
        core.pop("self_digest_note")
        got = hashlib.sha256(json.dumps(
            core, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(got, reg["self_digest_sha256"])
        self.assertEqual(got, RES["register_digest"])

    def test_registered_scope_respected(self):
        for W in (RO, MN, SW):
            self.assertLessEqual(W.nS, 4)
            self.assertLessEqual(W.nO, 3)
            self.assertLessEqual(W.nA, 3)
            self.assertEqual(W.horizon, 3)
            self.assertEqual(W.gamma, F(1, 2))


class TestRouteIndependence(unittest.TestCase):
    def test_distinct_modules(self):
        self.assertNotEqual(A.__file__, O.__file__)
        self.assertIn("ae15_world_model_necessity_v1", A.__file__)
        self.assertIn("independent_world_model_oracle_v1", O.__file__)

    def test_oracle_has_no_executable_import_of_route_a(self):
        fh = open(O.__file__)
        try:
            tree = ast.parse(fh.read())
        finally:
            fh.close()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn("ae15_world_model_necessity",
                                     alias.name)
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn("ae15_world_model_necessity",
                                 node.module or "")

    def test_no_bare_assert_in_shipped_python(self):
        for name in ("ae15_world_model_necessity_v1.py",
                     "independent_world_model_oracle_v1.py",
                     "test_ae15_world_model_necessity_v1.py"):
            fh = open(os.path.join(HERE, name))
            try:
                tree = ast.parse(fh.read())
            finally:
                fh.close()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    self.fail("bare assert in " + name)


class TestTwoRouteAgreement(unittest.TestCase):
    def test_optimal_values_agree(self):
        pairs = [(RO, OR["K_REACTIVE_OPT"]), (MN, OR["K_MODEL_NEEDED"]),
                 (SW, OR["K_SWAP"]), (SWA, OR["K_SWAP_R_ALT"])]
        for wa, wb in pairs:
            self.assertEqual(A.opt_value(wa), O.oracle_opt_value(wb), wa.name)
        for g in (1, 2, 3, 4):
            self.assertEqual(A.opt_value(A.phase_world(MN, g)),
                             O.oracle_opt_value(O.w_phase(g)), "phase %d" % g)

    def test_reactive_class_agrees_and_is_exhaustive(self):
        pairs = [(RO, OR["K_REACTIVE_OPT"]), (MN, OR["K_MODEL_NEEDED"]),
                 (SW, OR["K_SWAP"]), (SWA, OR["K_SWAP_R_ALT"])]
        for wa, wb in pairs:
            va, pia = A.best_memoryless(wa)
            vb, pib = O.oracle_best_reactive(wb)
            self.assertEqual(va, vb, wa.name)
            self.assertEqual(a_reactive_map(wa, pia), pib, wa.name)
            self.assertEqual(len(A.all_memoryless(wa)), wa.nA ** wa.nO)
            self.assertEqual(len(O.oracle_all_reactive(wb)),
                             len(wb["A"]) ** len(wb["O"]))

    def test_cached_class_agrees(self):
        for wa, wb in [(RO, OR["K_REACTIVE_OPT"]), (MN, OR["K_MODEL_NEEDED"]),
                       (SW, OR["K_SWAP"]), (SWA, OR["K_SWAP_R_ALT"])]:
            va, _t = A.best_cached_skill(wa)
            vb, _u = O.oracle_best_cached(wb)
            self.assertEqual(va, vb, wa.name)

    def test_value_representation_agrees(self):
        for wa, wb in [(RO, OR["K_REACTIVE_OPT"]), (MN, OR["K_MODEL_NEEDED"]),
                       (SW, OR["K_SWAP"]), (SWA, OR["K_SWAP_R_ALT"])]:
            va = A.best_value_representation(wa)[0]
            vb = O.oracle_best_value_representation(wb)[0]
            self.assertEqual(va, vb, wa.name)
            _ga, ba = A.lookahead_action_groups(wa)
            _gb, bb = O.oracle_lookahead_groups(wb)
            self.assertEqual(ba, bb, wa.name)

    def test_one_step_memory_class_agrees(self):
        va = A.best_one_step_memory(MN)[0]
        vb = O.oracle_best_one_step_memory(OR["K_MODEL_NEEDED"])[0]
        self.assertEqual(va, vb)

    def test_phase_boundary_agrees(self):
        for row in R["phase_boundary"]["rows"]:
            ob = O.oracle_phase(row["G"])
            self.assertEqual(F(row["V_mb"]), ob["V_mb"])
            self.assertEqual(F(row["V_mf"]), ob["V_mf"])
            self.assertEqual(F(row["c_star"]), ob["c_star"])

    def test_probe_agrees(self):
        ob = O.oracle_probe()
        for cls in sorted(ob):
            self.assertEqual(F(R["reward_swap_probe"][cls]["shortfall"]),
                             ob[cls]["shortfall"], cls)
            self.assertEqual(
                R["reward_swap_probe"][cls]["reoptimizes_under_probe"],
                ob[cls]["reoptimizes"], cls)

    def test_scm_profiles_agree(self):
        ident = R["identifiability"]
        self.assertEqual(ident["observable_profile_A"],
                         O.oracle_profile(O.SCM_A))
        self.assertEqual(ident["observable_profile_B"],
                         O.oracle_profile(O.SCM_B))
        for c in ("x0", "x1"):
            self.assertEqual(ident["interventional_profile_A"]["do_X=%s" % c],
                             O.oracle_do(O.SCM_A, c))
            self.assertEqual(ident["interventional_profile_B"]["do_X=%s" % c],
                             O.oracle_do(O.SCM_B, c))
        self.assertEqual(ident["recovery_map"],
                         O.oracle_recovery_map(O.SCM_ID))


class TestRow1Interfaces(unittest.TestCase):
    def test_five_classes_pairwise_distinct(self):
        i = R["interfaces"]
        self.assertEqual(sorted(i["classes"]), sorted(A.CLASSES))
        self.assertEqual(len(i["classes"]), 5)
        vecs = i["vectors"]
        for a in i["classes"]:
            for b in i["classes"]:
                if a < b:
                    self.assertNotEqual(vecs[a], vecs[b], a + " vs " + b)
        self.assertTrue(i["every_unordered_pair_separated"])

    def test_every_ordered_pair_is_filled(self):
        i = R["interfaces"]
        self.assertEqual(i["ordered_pairs_total"], 20)
        self.assertEqual(i["ordered_pairs_strict"]
                         + i["ordered_pairs_dominated"], 20)
        seen = set()
        for e in i["pairwise_distinctness"]:
            self.assertIsNotNone(e["separating_coordinate"])
            self.assertIn(e["separating_coordinate"], i["coordinates"])
            seen.add((e["from"], e["to"]))
        self.assertEqual(len(seen), 20)

    def test_probe_separates_the_explicit_model_alone(self):
        s = R["reward_swap_probe_summary"]
        self.assertEqual(s["reoptimizing_classes"],
                         ["EXPLICIT_GENERATIVE_MODEL"])
        for cls in ("REACTIVE_POLICY", "CACHED_SKILL",
                    "VALUE_REPRESENTATION"):
            self.assertEqual(F(R["reward_swap_probe"][cls]["shortfall"]),
                             F(3, 4), cls)
        self.assertTrue(R["reward_swap_probe"]["PREDICTIVE_STATE"][
            "predictive_state_invariant_under_reward_swap"])


class TestRow2ReactiveOptimal(unittest.TestCase):
    def test_gap_is_exactly_zero(self):
        t = R["reactive_optimal_task"]
        self.assertEqual(F(t["gap"]), F(0))
        self.assertEqual(F(t["model_based_optimum"]), F(3, 4))
        self.assertEqual(F(t["best_reactive_value"]), F(3, 4))
        self.assertTrue(t["observation_map_is_identity"])

    def test_verified_by_exhaustive_reactive_enumeration_in_route_b(self):
        wb = OR["K_REACTIVE_OPT"]
        pols = O.oracle_all_reactive(wb)
        self.assertEqual(len(pols), len(wb["A"]) ** len(wb["O"]))
        best = max(O.oracle_eval(wb, lambda t, h, o, _p=p: _p[o])
                   for p in pols)
        self.assertEqual(best, O.oracle_opt_value(wb))
        self.assertEqual(best, F(3, 4))

    def test_task_is_not_myopically_trivial(self):
        t = R["reactive_optimal_task"]
        self.assertTrue(t["myopically_greedy_action_at_s0_is_not_optimal"])
        self.assertEqual(F(t["value_of_myopically_greedy_reactive_policy"]),
                         F(7, 16))


class TestRow3ModelNecessity(unittest.TestCase):
    def test_every_member_of_each_class_is_strictly_suboptimal(self):
        t = R["model_needed_task"]
        self.assertEqual(F(t["model_based_optimum"]), F(1, 2))
        for cls in ("REACTIVE_POLICY", "CACHED_SKILL",
                    "VALUE_REPRESENTATION"):
            self.assertEqual(F(t["best_value_by_class"][cls]), F(1, 4), cls)
            self.assertEqual(F(t["gap_by_class"][cls]), F(1, 4), cls)
            self.assertLess(F(t["best_value_by_class"][cls]),
                            F(t["model_based_optimum"]), cls)
        self.assertTrue(t["all_strictly_suboptimal"])

    def test_each_finite_class_was_enumerated_exhaustively(self):
        sizes = R["model_needed_task"]["class_sizes_enumerated"]
        self.assertEqual(sizes["REACTIVE_POLICY"], 27)
        self.assertEqual(sizes["CACHED_SKILL"], 27)
        self.assertEqual(len(A.all_memoryless(MN)), 27)
        self.assertEqual(len(A.cached_members(MN)), 27)
        for pi in A.all_memoryless(MN):
            self.assertLessEqual(A.eval_memoryless(MN, pi), F(1, 4))
        for tab in A.cached_members(MN):
            v = A.eval_cached_table(MN, tab)
            self.assertLessEqual(v, F(1, 4))

    def test_value_representation_bound_is_semantics_independent(self):
        t = R["model_needed_task"]
        self.assertTrue(
            t["value_representation_suboptimal_for_any_memoryless_lookahead"])
        self.assertEqual(F(t["value_representation_upper_bound_is_memoryless_best"]),
                         F(1, 4))
        self.assertLess(
            t["value_representation_structural_upper_bound_on_realizable_maps"],
            27)

    def test_aliasing_is_present_and_load_bearing(self):
        t = R["model_needed_task"]
        self.assertEqual(t["aliased_states"], ["s0", "s1"])
        self.assertEqual(MN.Z[MN.snames.index("s0")],
                         MN.Z[MN.snames.index("s1")])
        acts = t["optimal_history_dependent_actions"]
        self.assertEqual(acts["oa"], "a0")
        self.assertEqual(acts["oa|a0|oa"], "a1")
        self.assertEqual(acts["oa|a0|ob"], "a2")


class TestRow4PhaseBoundary(unittest.TestCase):
    def test_exact_threshold_and_closed_form(self):
        rows = R["phase_boundary"]["rows"]
        self.assertEqual([r["c_star"] for r in rows],
                         ["1/4", "1/2", "3/4", "1"])
        for r in rows:
            self.assertTrue(r["closed_form_matches"], "G=%d" % r["G"])
            self.assertEqual(F(r["c_star"]), F(r["G"], 4))

    def test_strictly_increasing(self):
        rows = R["phase_boundary"]["rows"]
        for i in range(len(rows) - 1):
            self.assertLess(F(rows[i]["c_star"]), F(rows[i + 1]["c_star"]))
        self.assertTrue(R["phase_boundary"]["strictly_increasing_in_G"])

    def test_flip_is_strict_on_both_sides(self):
        for r in R["phase_boundary"]["rows"]:
            self.assertEqual(r["chosen_below"], "EXPLICIT_GENERATIVE_MODEL")
            self.assertNotEqual(r["chosen_above"],
                                "EXPLICIT_GENERATIVE_MODEL")
            self.assertGreater(F(r["margin_below"]), F(0))
            self.assertEqual(F(r["margin_at"]), F(0))
            self.assertLess(F(r["margin_above"]), F(0))


class TestRow5Identifiability(unittest.TestCase):
    def test_non_identifiability_pair(self):
        i = R["identifiability"]
        self.assertEqual(i["observable_profile_A"], i["observable_profile_B"])
        self.assertTrue(i["observational_and_predictive_joints_identical"])
        self.assertTrue(i["latent_factorizations_differ"])
        self.assertEqual(i["latent_cardinalities"], [2, 4])
        self.assertNotEqual(i["SCM_LATENT_A"]["edges"],
                            i["SCM_LATENT_B"]["edges"])

    def test_pair_is_interventionally_distinguishable(self):
        i = R["identifiability"]
        self.assertNotEqual(i["interventional_profile_A"],
                            i["interventional_profile_B"])
        self.assertEqual(i["interventional_profile_A"]["do_X=x1"],
                         {"y0": "1/2", "y1": "1/2"})
        self.assertEqual(i["interventional_profile_B"]["do_X=x1"],
                         {"y1": "1"})

    def test_identifiable_latent_recovered_up_to_relabelling(self):
        i = R["identifiability"]
        self.assertTrue(i["latent_recovered_exactly"])
        self.assertEqual(i["relabelling_permutations_checked"], 6)
        for rec in i["relabelling_recovery"]:
            self.assertTrue(rec["observable_profile_unchanged"])
            self.assertTrue(rec["recovered_exactly"])
        self.assertTrue(i["recovered_up_to_relabelling"])


class TestRow6ForbiddenPromotion(unittest.TestCase):
    def test_every_scanned_file_exists(self):
        for name in A.SCANNED_FILES:
            self.assertTrue(os.path.exists(os.path.join(HERE, name)),
                            "missing scanned artifact: " + name)

    def test_no_artifact_asserts_a_forbidden_promotion(self):
        c = R["forbidden_promotion_closure"]
        self.assertEqual(c["assertions_found"], [])
        self.assertTrue(c["no_artifact_asserts_a_forbidden_promotion"])
        self.assertEqual(c["evidence_result_id"], "AE15-5")
        self.assertIn("LATENTS_ARE_HUMAN_INTERPRETABLE",
                      RES["forbidden_promotions"])

    def test_the_json_scanner_is_validated_in_both_directions(self):
        planted = {"summary": "our latents are LATENTS_ARE_HUMAN_INTERPRETABLE"}
        self.assertNotEqual(A._json_offenders(planted, "probe.json", []), [])
        declared = {"forbidden_promotions":
                    ["LATENTS_ARE_HUMAN_INTERPRETABLE"]}
        self.assertEqual(A._json_offenders(declared, "probe.json", []), [])
        guarded = {"note": ("LATENTS_ARE_HUMAN_INTERPRETABLE is a forbidden "
                            "promotion and is refused")}
        self.assertEqual(A._json_offenders(guarded, "probe.json", []), [])

    def test_the_scanner_actually_catches_an_assertion(self):
        """Validate the detector in the positive direction: a line that does
        assert the string, with no declaration guard, must be caught."""
        bad = A._text_offenders(
            "Our recovered latents are LATENTS_ARE_HUMAN_INTERPRETABLE.\n",
            "probe.md")
        self.assertNotEqual(bad, [])
        good = A._text_offenders(
            "## Forbidden promotions\n\n`LATENTS_ARE_HUMAN_INTERPRETABLE`\n",
            "probe.md")
        self.assertEqual(good, [])


class TestBounds(unittest.TestCase):
    def test_every_bound_has_a_full_vacuity_record(self):
        self.assertEqual(len(RES["bounds"]), 3)
        for b in RES["bounds"]:
            for k in ("kind", "bound_value", "range_lo", "range_hi",
                      "range_derivation", "vacuous", "attained_by",
                      "violated_by"):
                self.assertIn(k, b, b["id"])
            self.assertIn(b["kind"], ("upper", "lower"))
            lo, hi, bv = F(b["range_lo"]), F(b["range_hi"]), F(b["bound_value"])
            if b["kind"] == "upper":
                self.assertEqual(b["vacuous"], bv >= hi, b["id"])
            else:
                self.assertEqual(b["vacuous"], bv <= lo, b["id"])
            self.assertFalse(b["vacuous"], b["id"])
            self.assertEqual(b["status"], "FALSIFIABLE_BOUND", b["id"])
            self.assertTrue(b["violated_by"]["breaks_bound"], b["id"])
            self.assertNotEqual(b["violated_by"]["relaxed_class"], "")

    def test_violators_really_break_their_bounds(self):
        by = dict((b["id"], b) for b in RES["bounds"])
        b1 = by["AE15-B1"]
        self.assertGreater(F(b1["violated_by"]["value"]),
                           F(b1["bound_value"]))
        b2 = by["AE15-B2"]
        self.assertEqual(F(b2["violated_by"]["value"]), F(1, 2))
        self.assertGreater(F(b2["violated_by"]["value"]),
                           F(b2["bound_value"]))
        b3 = by["AE15-B3"]
        self.assertLess(F(b3["violated_by"]["value"]), F(b3["bound_value"]))

    def test_relaxed_discount_violator_recomputed_by_route_b(self):
        for row in [r for r in RES["bounds"][0]["violated_by"]["rows"]]:
            W = O.w_phase(row["G"])
            W = dict(W)
            W["gamma"] = F(1)
            vmb = O.oracle_opt_value(W)
            vmf = max(O.oracle_best_reactive(W)[0], O.oracle_best_cached(W)[0])
            self.assertEqual(F(row["V_mb"]), vmb, "G=%d" % row["G"])
            self.assertEqual(F(row["V_mf"]), vmf, "G=%d" % row["G"])


class TestHostiles(unittest.TestCase):
    def by_name(self, n):
        for h in RES["hostiles"]:
            if h["name"] == n:
                return h
        raise AssertionError("no hostile " + n)

    def test_all_five_registered_hostiles_present(self):
        names = sorted(h["name"] for h in RES["hostiles"])
        self.assertEqual(names, ["H_ALIAS_BREAK", "H_COST_SHIFT",
                                 "H_HORIZON", "H_LATENT_RELABEL",
                                 "H_MEMORY_LEAK"])

    def test_memory_leak_potency_then_detection(self):
        h = self.by_name("H_MEMORY_LEAK")
        self.assertNotEqual(F(h["perturbed_quantity"]),
                            F(h["true_quantity"]))          # potency
        self.assertEqual(F(h["perturbed_quantity"]), F(1, 2))
        self.assertTrue(h["potent"])
        self.assertTrue(h["detected"])                       # detection
        self.assertEqual(A.best_one_step_memory(MN)[0], A.opt_value(MN))

    def test_alias_break_potency_then_detection(self):
        h = self.by_name("H_ALIAS_BREAK")
        self.assertNotEqual(F(h["perturbed_quantity"]),
                            F(h["true_quantity"]))          # potency
        self.assertEqual(F(h["perturbed_quantity"]), F(0))
        self.assertTrue(h["potent"])
        self.assertTrue(h["detected"])                       # detection

    def test_horizon_potency_then_detection(self):
        h = self.by_name("H_HORIZON")
        moved = [r for r in h["witness"]
                 if r["V_mb_registered"] != r["V_mb_perturbed"]]
        self.assertNotEqual(moved, [])                       # potency
        self.assertTrue(h["potent"])
        self.assertTrue(h["detected"])                       # detection

    def test_cost_shift_potency_then_detection(self):
        h = self.by_name("H_COST_SHIFT")
        for row in h["witness"]:
            self.assertNotEqual(row["chosen_at_registered_probe_cost"],
                                row["chosen_at_perturbed_probe_cost"])
        self.assertTrue(h["potent"])                         # potency
        self.assertTrue(h["detected"])                       # detection

    def test_latent_relabel_is_inverted_and_the_checker_stays_silent(self):
        h = self.by_name("H_LATENT_RELABEL")
        self.assertTrue(h["inverted"])
        self.assertTrue(h["object_changed"])                 # the object moved
        self.assertFalse(h["checker_flagged"])               # silence
        self.assertTrue(h["detected"])
        a, b, _i = A.build_scms()
        rel = b.relabel({"v0": "w3", "v1": "w2", "v2": "w1", "v3": "w0"})
        self.assertNotEqual(b.stored(), rel.stored())
        self.assertFalse(A.behaviour_differs(b, rel))
        self.assertTrue(A.behaviour_differs(a, _i))


class TestNull(unittest.TestCase):
    def test_detector_fires_on_the_planted_positive(self):
        n = RES["null"]
        self.assertTrue(n["detector_fires_on_witness"])
        self.assertEqual(F(n["planted_positive_magnitude"]), F(1, 4))

    def test_no_alarm_on_the_known_clean_registered_witnesses(self):
        n = RES["null"]
        self.assertEqual(n["known_clean_witnesses_flagged"], [])
        self.assertTrue(n["no_alarm_on_clean"])
        for W in (RO, SW):
            g, _a, _b = A.necessity_gap(W)
            self.assertEqual(g, F(0), W.name)

    def test_primary_null_is_beaten_threshold_free(self):
        p = RES["null"]["primary"]
        self.assertEqual(p["trials"], 200)
        self.assertGreater(F(RES["null"]["planted_positive_magnitude"]),
                           F(p["largest_null_magnitude"]))
        self.assertTrue(p["witness_exceeds_largest_null_magnitude"])

    def test_structure_matched_control_is_reported_honestly(self):
        s = RES["null"]["structure_matched"]
        self.assertEqual(s["trials"], 200)
        # this control does NOT beat the witness, and says so
        self.assertFalse(s["witness_exceeds_largest_null_magnitude"])
        conf = s["conflict_vs_gap_confusion"]
        # the structural predicate is necessary ...
        self.assertEqual(conf["no_conflict_and_gap_positive"], 0)
        self.assertEqual(F(s["largest_null_magnitude_without_a_conflict"]),
                         F(0))
        # ... and NOT sufficient, which is reported rather than hidden
        self.assertGreater(conf["conflict_and_gap_zero"], 0)
        self.assertFalse(s["conflict_predicts_a_positive_gap_exactly"])


class TestProspectivePredictions(unittest.TestCase):
    def test_every_registered_prediction_is_reported(self):
        p = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
        fh = open(p)
        try:
            reg = json.loads(fh.read())
        finally:
            fh.close()
        ids = sorted(x["id"] for x in reg["prospective_predictions"])
        got = sorted(x["id"] for x in RES["prospective_predictions"])
        self.assertEqual(ids, got)
        for rec in RES["prospective_predictions"]:
            self.assertIn(rec["status"], ("CONFIRMED", "REFUTED"))
            self.assertNotEqual(rec["values"], {})
        claims = dict((x["id"], x["claim"])
                      for x in reg["prospective_predictions"])
        for rec in RES["prospective_predictions"]:
            self.assertEqual(rec["claim"], claims[rec["id"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
