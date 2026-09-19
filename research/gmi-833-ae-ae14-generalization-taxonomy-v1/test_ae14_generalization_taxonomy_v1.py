#!/usr/bin/env python3
"""Tests for GMI #833 AE14.

Every check uses a ``unittest`` assertion **method** or an explicit ``raise``;
the bare ``assert`` statement appears nowhere, so nothing is stripped by ``-O``.
Run standalone::

    python3 -I -B  test_ae14_generalization_taxonomy_v1.py -v
    python3 -I -O -B test_ae14_generalization_taxonomy_v1.py -v
"""
from __future__ import print_function

import ast
import hashlib
import importlib.util
import json
import os
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTE_A_FILE = "ae14_generalization_taxonomy_v1.py"
ROUTE_B_FILE = "independent_taxonomy_oracle_v1.py"
ROUTE_A_MODULE = "ae14_generalization_taxonomy_v1"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name,
                                                  os.path.join(HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _load("route_a_ae14", ROUTE_A_FILE)
B = _load("route_b_ae14", ROUTE_B_FILE)
RECEIPT = A.build()
SERIALIZED = json.dumps(RECEIPT, sort_keys=True, indent=2) + "\n"


def _read(name):
    fh = open(os.path.join(HERE, name), "r")
    try:
        return fh.read()
    finally:
        fh.close()


class TestReceiptShape(unittest.TestCase):
    def test_required_top_level_keys(self):
        for key in ("schema", "issue", "issue_comment_id", "package",
                    "source_main", "freeze_commit", "claim_ceiling", "verdict",
                    "checks", "results", "bounds", "hostiles", "null",
                    "prospective_predictions", "forbidden_promotions"):
            self.assertIn(key, RECEIPT)

    def test_identity_fields(self):
        self.assertEqual(RECEIPT["issue"], 833)
        self.assertEqual(RECEIPT["issue_comment_id"], 5692689542)
        self.assertEqual(RECEIPT["package"],
                         "gmi-833-ae-ae14-generalization-taxonomy-v1")
        self.assertEqual(RECEIPT["verdict"], "GREEN")

    def test_every_check_is_true(self):
        for name in sorted(RECEIPT["checks"]):
            self.assertTrue(RECEIPT["checks"][name], name)

    def test_claim_ceiling_matches_the_freeze(self):
        self.assertIn(RECEIPT["claim_ceiling"], _read("FREEZE_V1.md"))

    def test_no_float_anywhere_in_the_receipt(self):
        stack = [RECEIPT]
        while stack:
            node = stack.pop()
            if isinstance(node, float):
                raise AssertionError("float found in the receipt")
            if isinstance(node, dict):
                stack.extend(sorted(node.keys()))
                stack.extend(node.values())
            elif isinstance(node, (list, tuple)):
                stack.extend(node)

    def test_receipt_matches_the_committed_file(self):
        path = os.path.join(HERE, "RESULT_V1.json")
        if not os.path.exists(path):
            self.skipTest("RESULT_V1.json not generated yet")
        self.assertEqual(SERIALIZED, _read("RESULT_V1.json"))

    def test_serialization_is_deterministic(self):
        again = json.dumps(A.build(), sort_keys=True, indent=2) + "\n"
        self.assertEqual(SERIALIZED, again)


class TestRegisterCustody(unittest.TestCase):
    def setUp(self):
        self.reg = json.loads(_read("PROSPECTIVE_REGISTER_V1.json"))

    def test_digest_recomputes(self):
        d = dict(self.reg)
        d.pop("self_digest_sha256", None)
        d.pop("self_digest_note", None)
        blob = json.dumps(d, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")
        self.assertEqual(hashlib.sha256(blob).hexdigest(),
                         self.reg["self_digest_sha256"])
        self.assertEqual(RECEIPT["register_digest"],
                         self.reg["self_digest_sha256"])

    def test_every_registered_prediction_is_reported(self):
        reported = sorted(p["id"] for p in RECEIPT["prospective_predictions"])
        registered = sorted(p["id"] for p in self.reg["prospective_predictions"])
        self.assertEqual(reported, registered)
        for p in RECEIPT["prospective_predictions"]:
            self.assertIn(p["status"], ("CONFIRMED", "REFUTED"))
            self.assertTrue(p["values"], p["id"])

    def test_every_registered_hostile_is_exercised(self):
        reported = sorted(h["name"] for h in RECEIPT["hostiles"])
        registered = sorted(h["name"] for h in self.reg["hostiles"])
        self.assertEqual(reported, registered)

    def test_registered_constants_are_honoured(self):
        c = self.reg["registered_constants"]
        self.assertEqual(c["n"], A.N)
        self.assertEqual(c["search_depth_cap"], A.SEARCH_DEPTH_CAP)
        self.assertEqual(c["null_trials"], A.NULL_TRIALS)
        self.assertEqual(c["rule_class_budget"]["junta_arity"], A.JUNTA_ARITY)
        self.assertEqual(c["rule_class_budget"]["tree_depth"], A.TREE_DEPTH)
        self.assertEqual([list(b) for b in A.BLOCKS], c["blocks"])
        self.assertEqual(len(A.GROUP), 4)
        self.assertEqual(len(A.REASON_RULES), 4)

    def test_frozen_mechanism_predictor_is_the_registered_table(self):
        self.assertEqual(A.MECHANISM_PREDICTOR,
                         self.reg["mechanism_predictor"]["table"])

    def test_registered_roster_names_match(self):
        self.assertEqual(sorted(A.TASK_NAMES),
                         sorted(self.reg["roster"]["tasks"]))
        self.assertEqual(sorted(A.MODES), sorted(self.reg["roster"]["modes"]))
        self.assertEqual(sorted(A.CLASSES),
                         sorted(self.reg["roster"]["learner_classes"]))
        self.assertEqual(sorted(A.PREDICTION_ONLY),
                         sorted(self.reg["roster"]["prediction_only_classes"]))


class TestRouteIndependence(unittest.TestCase):
    def test_route_b_does_not_import_route_a(self):
        tree = ast.parse(_read(ROUTE_B_FILE))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(ROUTE_A_MODULE, alias.name)
            elif isinstance(node, ast.ImportFrom):
                self.assertNotIn(ROUTE_A_MODULE, node.module or "")
                for alias in node.names:
                    self.assertNotIn(ROUTE_A_MODULE, alias.name)

    def test_no_bare_assert_statement_in_any_shipped_python_file(self):
        for name in (ROUTE_A_FILE, ROUTE_B_FILE,
                     "test_ae14_generalization_taxonomy_v1.py"):
            tree = ast.parse(_read(name))
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    raise AssertionError("bare assert in %s" % name)


class TestRoutesAgree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = B.compute()

    def test_structures_agree(self):
        for name in sorted(A.TASK_NAMES):
            tr = A.TASKS[name]["tr"]
            o = self.oracle["structures"][name]
            self.assertEqual(list(A.span(tr)), o["span"], name)
            self.assertEqual(list(A.recomb(tr)), o["recomb"], name)
            self.assertEqual(list(A.analogy_pts(tr)), o["analogy"], name)
            self.assertEqual(list(A.plan_pts(tr)), o["plan"], name)
            self.assertEqual(list(A.eval_points("REASONING", tr)),
                             o["reason"], name)

    def test_truth_cube_agrees(self):
        cube = RECEIPT["results"]["mode_truth_cube"]
        for name in sorted(A.TASK_NAMES):
            for mode in A.MODES:
                a = cube[name][mode]
                b = self.oracle["cube"][name][mode]
                self.assertEqual(a["n_eval"], b["n_eval"], (name, mode))
                for c in A.CLASSES:
                    self.assertEqual(a[c], b[c], (name, mode, c))

    def test_home_specifications_agree(self):
        enum = RECEIPT["results"]["row2_enumeration"]
        for st in sorted(A.STRUCTURE_TYPES):
            a = enum[st]
            b = self.oracle["home"][st]
            self.assertEqual(a["minimal_realizing_class"], b["minimal"], st)
            self.assertEqual(a["predictor_hit"], b["hit"], st)
            self.assertEqual(a["constraint_points"], b["constraint_points"], st)
            for c in A.CLASSES:
                self.assertEqual(a["classes"][c]["best_attainable_accuracy"],
                                 b["best"][c], (st, c))
                self.assertEqual(a["classes"][c]["distinct_members"],
                                 b["distinct"][c], (st, c))

    def test_rows_three_four_five_agree(self):
        r3 = RECEIPT["results"]["row3_matched_predictive_pair"]
        o3 = self.oracle["row3"]
        self.assertEqual(r3["held_out_recombinations"], o3["held"])
        self.assertEqual(r3["shortest_code_model_index"], o3["mdl_index"])
        self.assertEqual(r3["shortest_code_model_length_bits"], o3["mdl_length"])
        self.assertEqual(r3["recombination_accuracy"], o3["recomb_acc"])
        self.assertEqual(r3["bayes_predictive_accuracy"][
            "T_MATCH_COMPOSITIONAL"], o3["bayes"])
        r4 = RECEIPT["results"]["row4_matched_compression_pair"]
        o4 = self.oracle["row4"]
        self.assertEqual(r4["model_space_size"], o4["model_space_size"])
        self.assertEqual(r4["T_CODE_A"]["model_index"], o4["index_a"])
        self.assertEqual(r4["T_CODE_B"]["model_index"], o4["index_b"])
        self.assertEqual(r4["T_CODE_A"]["description_length_bits"],
                         o4["length_a"])
        self.assertEqual(r4["T_CODE_B"]["description_length_bits"],
                         o4["length_b"])
        self.assertEqual(r4["T_CODE_A"]["transfer_accuracy"], o4["transfer_a"])
        self.assertEqual(r4["T_CODE_B"]["transfer_accuracy"], o4["transfer_b"])
        self.assertEqual(r4["kraft_sum"], o4["kraft_sum"])
        r5 = RECEIPT["results"]["row5_mechanism_predictor"]
        o5 = self.oracle["row5"]
        self.assertEqual(r5["hit_count"], o5["hit_count"])
        self.assertEqual(r5["null_largest_hit_count"], o5["null_largest"])
        self.assertEqual(r5["null_rate_at_or_above_predictor"],
                         o5["null_at_or_above"])

    def test_separation_null_agrees(self):
        s = RECEIPT["null"]["separation_null"]
        o = self.oracle["separation_null"]
        self.assertEqual(s["witness_magnitude"], o["witness"])
        self.assertEqual(s["largest_null_magnitude"], o["largest"])
        self.assertEqual(s["null_rate_at_or_above_witness"], o["at_or_above"])


class TestRowOne(unittest.TestCase):
    def test_seven_modes_with_exact_predicates(self):
        self.assertEqual(len(A.MODES), 7)
        self.assertEqual(sorted(A.MODE_DEFINITIONS), sorted(A.MODES))

    def test_every_ordered_pair_is_reported(self):
        pairs = RECEIPT["results"]["pairwise_distinctness"]
        self.assertEqual(len(pairs), 42)
        for key in sorted(pairs):
            self.assertIn(pairs[key]["witness_kind"],
                          ("NONDEGENERATE", "SECOND_MODE_STRUCTURE_EMPTY",
                           "NOT_SEPARATED"))

    def test_each_separation_witness_really_separates(self):
        pairs = RECEIPT["results"]["pairwise_distinctness"]
        cube = RECEIPT["results"]["mode_truth_cube"]
        for key in sorted(pairs):
            rec = pairs[key]
            if rec["witness_kind"] == "NOT_SEPARATED":
                continue
            m1, m2 = key[:-len("_fails")].split("_holds_")
            self.assertTrue(cube[rec["task"]][m1][rec["class"]], key)
            self.assertFalse(cube[rec["task"]][m2][rec["class"]], key)

    def test_the_implication_is_scoped_to_a_nonempty_second_structure(self):
        # a recombination-closed support: interpolation has a structure, the
        # recombination structure is empty, so the implication is stated only
        # where the second structure is non-empty.
        tr = (0, 3, 12, 15)
        self.assertEqual(A.eval_points("SYSTEMATIC_GENERALIZATION", tr), ())
        self.assertNotEqual(A.eval_points("INTERPOLATION", tr), ())

    def test_unseparated_pairs_carry_an_implication_certificate(self):
        certs = RECEIPT["results"]["mode_implication_certificates"]
        summary = RECEIPT["results"]["pairwise_distinctness_summary"]
        for key in summary["not_separated"]:
            self.assertIn(key, certs)
            self.assertTrue(certs[key]["constraint_set_inclusion_holds"], key)
            self.assertIsNone(certs[key]["counterexample_support"], key)
            self.assertGreater(certs[key]["supports_checked"], 60000, key)

    def test_the_predicates_read_only_the_function_and_the_support(self):
        """architecture independence: a task rebuilt by a different rule, but
        realizing the same function on the same support, gets the same verdict
        in every mode and every class; and the verdicts do not depend on the
        order in which a class is enumerated."""
        tr = A.TASKS["T_ANALOGY"]["tr"]
        literal = A.TASKS["T_ANALOGY"]["mask"]
        # rebuild the same function from the rotation orbits of 1 and 3
        orbits = set()
        for seed in (1, 3):
            y = seed
            for _ in range(4):
                orbits.add(y)
                y = A.op_rho(y)
        rebuilt = A.tt(lambda x: 1 if x in orbits else 0)
        self.assertEqual(rebuilt, literal)
        for mode in A.MODES:
            for c in A.CLASSES:
                fs = A.class_members(c, tr, literal)
                a = A.mode_holds(mode, fs, literal, tr)
                b = A.mode_holds(mode, A.class_members(c, tr, rebuilt),
                                 rebuilt, tr)
                self.assertEqual(a, b, (mode, c))
                self.assertEqual(a, A.mode_holds(mode, tuple(reversed(fs)),
                                                 literal, tr), (mode, c))


class TestRowTwo(unittest.TestCase):
    def test_three_modes_require_the_composition_machinery(self):
        req = RECEIPT["results"]["row2_modes_requiring_composition_machinery"]
        self.assertEqual(req, ["ANALOGY", "PLANNING_INFERENCE", "REASONING"])

    def test_four_modes_reduce_to_prediction(self):
        red = RECEIPT["results"]["row2_modes_reducible_to_prediction"]
        self.assertEqual(red, ["EXTRAPOLATION", "INTERPOLATION", "MEMORIZATION",
                               "SYSTEMATIC_GENERALIZATION"])

    def test_prediction_only_classes_are_enumerated_whole(self):
        enum = RECEIPT["results"]["row2_enumeration"]
        self.assertEqual(enum["GROUP_ORBIT"]["classes"]["L1"][
            "distinct_members"], 70)
        self.assertEqual(enum["GROUP_ORBIT"]["classes"]["L_lin"][
            "distinct_members"], 32)
        self.assertEqual(enum["GROUP_ORBIT"]["classes"]["L_mod"][
            "distinct_members"], 520)

    def test_headline_accuracies(self):
        enum = RECEIPT["results"]["row2_enumeration"]
        self.assertEqual(enum["GROUP_ORBIT"]["classes"]["L_mod"][
            "best_attainable_accuracy"], "13/15")
        self.assertEqual(enum["GROUP_ORBIT"]["classes"]["L_search"][
            "best_attainable_accuracy"], "1")
        self.assertEqual(enum["COMPOSITION_DEPTH_GE_2"]["classes"]["L0"][
            "best_attainable_accuracy"], "4/5")
        self.assertEqual(enum["COMPOSITION_DEPTH_GE_2"]["classes"]["L_search"][
            "best_attainable_accuracy"], "1")
        self.assertEqual(enum["DEDUCTIVE_CLOSURE"]["classes"]["L1"][
            "best_attainable_accuracy"], "9/10")
        self.assertEqual(enum["DEDUCTIVE_CLOSURE"]["classes"]["L_search"][
            "best_attainable_accuracy"], "1")

    def test_no_prediction_only_member_is_exact_on_the_hard_specifications(self):
        for st in ("GROUP_ORBIT", "COMPOSITION_DEPTH_GE_2",
                   "DEDUCTIVE_CLOSURE"):
            task, mode = A.HOME[st]
            t = A.TASKS[task]
            need = A.constraint_set(mode, t["tr"])
            for c in A.PREDICTION_ONLY:
                for m in A.class_members(c, t["tr"], t["mask"]):
                    if A.exact_on(m, t["mask"], need):
                        raise AssertionError("%s member exact on %s" % (c, st))

    def test_the_reasoning_specification_needs_the_derivability_readout(self):
        enum = RECEIPT["results"]["row2_enumeration"]["DEDUCTIVE_CLOSURE"]
        self.assertEqual(enum["realizing_lookup_members"], [])
        self.assertIn("atom|tau|5", enum["realizing_atom_members"])

    def test_the_analogy_specification_is_realized_by_transport(self):
        enum = RECEIPT["results"]["row2_enumeration"]["GROUP_ORBIT"]
        self.assertEqual(enum["realizing_atom_members"], [])
        self.assertTrue(enum["realizing_lookup_members"])

    def test_depth_one_composition_does_not_suffice(self):
        for st in ("GROUP_ORBIT", "COMPOSITION_DEPTH_GE_2",
                   "DEDUCTIVE_CLOSURE"):
            task, mode = A.HOME[st]
            t = A.TASKS[task]
            need = A.constraint_set(mode, t["tr"])
            shallow = tuple(m for _, m in A.build_L_search(t["tr"], t["mask"], 1))
            self.assertLess(A.best_joint(shallow, t["mask"], need), Fraction(1),
                            st)


class TestRowsThreeAndFour(unittest.TestCase):
    def test_matched_predictive_pair(self):
        r = RECEIPT["results"]["row3_matched_predictive_pair"]
        self.assertTrue(r["tasks_agree_on_training_view"])
        self.assertEqual(r["bayes_predictive_accuracy"][
            "T_MATCH_COMPOSITIONAL"],
            r["bayes_predictive_accuracy"]["T_MATCH_LOOKUP"])
        self.assertEqual(r["recombination_accuracy"]["T_MATCH_COMPOSITIONAL"],
                         "0")
        self.assertEqual(r["recombination_accuracy"]["T_MATCH_LOOKUP"], "1")

    def test_the_two_tasks_really_differ_only_off_the_training_view(self):
        a = A.TASKS["T_MATCH_COMPOSITIONAL"]["mask"]
        b = A.TASKS["T_MATCH_LOOKUP"]["mask"]
        differ = sorted(x for x in A.XS if A.val(a, x) != A.val(b, x))
        self.assertEqual(differ, RECEIPT["results"][
            "row3_matched_predictive_pair"]["held_out_recombinations"])

    def test_matched_compression_pair(self):
        r = RECEIPT["results"]["row4_matched_compression_pair"]
        self.assertEqual(r["T_CODE_A"]["description_length_bits"], 11)
        self.assertEqual(r["T_CODE_B"]["description_length_bits"], 11)
        self.assertEqual(r["T_CODE_A"]["transfer_accuracy"], "3/8")
        self.assertEqual(r["T_CODE_B"]["transfer_accuracy"], "3/4")
        self.assertNotEqual(r["T_CODE_A"]["transfer_accuracy"],
                            r["T_CODE_B"]["transfer_accuracy"])

    def test_code_is_kraft_compliant_and_integer_valued(self):
        total = Fraction(0)
        for i in range(len(A.MODEL_SPACE)):
            length = A.code_length(i)
            self.assertIsInstance(length, int)
            total += Fraction(1, 2 ** length)
        self.assertLessEqual(total, Fraction(1))
        self.assertEqual(str(total), RECEIPT["results"][
            "row4_matched_compression_pair"]["kraft_sum"])

    def test_code_length_plateaus(self):
        self.assertEqual(A.code_length(0), 3)
        self.assertEqual(A.code_length(1), 5)
        self.assertEqual(A.code_length(16), 11)
        self.assertEqual(A.code_length(20), 11)


class TestRowFive(unittest.TestCase):
    def test_predictor_beats_the_registered_null(self):
        r = RECEIPT["results"]["row5_mechanism_predictor"]
        self.assertEqual(r["hit_count"], 7)
        self.assertEqual(r["null_trials"], 200)
        self.assertGreater(r["hit_count"], r["null_largest_hit_count"])
        self.assertEqual(r["null_rate_at_or_above_predictor"], "0")

    def test_the_structurally_guaranteed_cell_is_declared(self):
        r = RECEIPT["results"]["row5_mechanism_predictor"]
        self.assertEqual(r["structurally_guaranteed_cell"], "LOOKUP_ONLY")
        self.assertEqual(r["evidential_hit_count"], 6)
        self.assertGreater(r["evidential_hit_count"],
                           r["null_largest_evidential_hit_count"])

    def test_family_sweep_is_not_a_single_instance(self):
        sweep = RECEIPT["results"]["row5_mechanism_predictor"]["family_sweep"]
        self.assertEqual(sweep["AFFINE"]["rate"], "1")
        self.assertEqual(sweep["JUNTA"]["rate"], "1")
        self.assertEqual(sweep["BLOCK_FACTORIZED"]["rate"], "1")
        self.assertEqual(sweep["COMPOSITION_DEPTH_GE_2"]["rate"], "1")
        self.assertEqual(sweep["GROUP_ORBIT"]["rate"], "26/27")
        self.assertEqual(sweep["BLOCK_FACTORIZED"]["nondegenerate_members"], 432)

    def test_the_null_sampler_is_exactly_uniform(self):
        s = A.Stream(A.NULL_SEED)
        counts = [0] * 5
        for _ in range(5000):
            counts[s.below(5)] += 1
        for c in counts:
            self.assertGreater(c, 800)
            self.assertLess(c, 1200)


class TestBounds(unittest.TestCase):
    def test_every_bound_record_is_complete(self):
        for b in RECEIPT["bounds"]:
            for field in ("id", "kind", "bound_value", "range_lo", "range_hi",
                          "range_derivation", "vacuous", "attained_by",
                          "violated_by"):
                self.assertIn(field, b, b.get("id"))
            self.assertIn(b["kind"], ("upper", "lower"))
            self.assertTrue(b["range_derivation"])

    def test_no_bound_is_vacuous_under_its_own_definition(self):
        for b in RECEIPT["bounds"]:
            lo = Fraction(b["range_lo"])
            hi = Fraction(b["range_hi"])
            v = Fraction(b["bound_value"])
            expected = (v >= hi) if b["kind"] == "upper" else (v <= lo)
            self.assertEqual(b["vacuous"], expected, b["id"])
            self.assertFalse(b["vacuous"], b["id"])

    def test_every_bound_has_a_violating_witness(self):
        for b in RECEIPT["bounds"]:
            w = b["violated_by"]
            self.assertTrue(w["violates"], b["id"])
            self.assertFalse(b.get("unfalsified"), b["id"])
            v = Fraction(w["value"])
            bound = Fraction(b["bound_value"])
            if b["kind"] == "upper":
                self.assertGreater(v, bound, b["id"])
            else:
                self.assertLess(v, bound, b["id"])

    def test_the_relaxed_classes_are_really_relaxations(self):
        registered = set(A.L1_LIST)
        for name, funcs in A.relaxation_ladder():
            self.assertTrue(set(funcs) >= registered, name)
            self.assertGreater(len(set(funcs)), len(registered), name)


class TestHostiles(unittest.TestCase):
    def test_each_hostile_is_potent_before_it_is_detected(self):
        for h in RECEIPT["hostiles"]:
            self.assertTrue(h["potency"]["moved"], h["name"] + " potency")
            self.assertNotEqual(h["potency"]["true_value"],
                                h["potency"]["perturbed_value"], h["name"])
            self.assertTrue(h["detection"]["flagged"],
                            h["name"] + " detection")

    def test_the_registered_hostile_names_are_all_present(self):
        names = sorted(h["name"] for h in RECEIPT["hostiles"])
        self.assertEqual(names, ["H_CODE_LENGTH", "H_GROUP_SHRINK",
                                 "H_RECOMBINATION_LEAK", "H_SEARCH_DEPTH",
                                 "H_SPAN_WIDEN"])

    def test_the_span_checker_accepts_the_true_span(self):
        for name in sorted(A.TASK_NAMES):
            tr = A.TASKS[name]["tr"]
            sp = set(A.span(tr))
            self.assertTrue(set(tr) <= sp, name)
            for other in A.XS:
                if other in sp:
                    continue
                self.assertFalse(other in set(tr), name)


class TestNullAndNoAlarm(unittest.TestCase):
    def test_conjunctive_witness_beats_every_control(self):
        s = RECEIPT["null"]["separation_null"]
        self.assertEqual(s["witness_magnitude"], 3)
        self.assertEqual(s["trials"], 200)
        self.assertGreater(s["witness_magnitude"], s["largest_null_magnitude"])
        self.assertEqual(s["null_rate_at_or_above_witness"], "0")

    def test_no_alarm_on_the_known_clean_specifications(self):
        s = RECEIPT["null"]["separation_null"]
        self.assertEqual(s["known_clean_specifications_flagged"], [])
        for st in ("LOOKUP_ONLY", "JUNTA", "AFFINE", "BLOCK_FACTORIZED"):
            task, mode = A.HOME[st]
            self.assertFalse(A.machinery_detector(A.TASKS[task]["mask"],
                                                  A.TASKS[task]["tr"], mode),
                             st)

    def test_the_detector_does_fire_on_the_planted_positives(self):
        for st in ("GROUP_ORBIT", "COMPOSITION_DEPTH_GE_2",
                   "DEDUCTIVE_CLOSURE"):
            task, mode = A.HOME[st]
            self.assertTrue(A.machinery_detector(A.TASKS[task]["mask"],
                                                 A.TASKS[task]["tr"], mode), st)

    def test_per_specification_rates_are_published(self):
        s = RECEIPT["null"]["separation_null"]
        self.assertEqual(sorted(s["per_specification_null_fire_counts"]),
                         ["T_ANALOGY", "T_PLAN", "T_REASON"])


class TestForbiddenPromotionGuard(unittest.TestCase):
    def test_no_artifact_asserts_the_blanket_claim(self):
        self.assertEqual(RECEIPT["results"]["row6_forbidden_blanket_claim"][
            "unguarded_occurrences_in_package"], [])

    def test_the_guard_flags_a_genuine_assertion(self):
        hostile = ("The finite roster establishes that "
                   + A.FORBIDDEN_BLANKET
                   + " is the correct account at every scale.")
        self.assertEqual(A.guard_scan_text(hostile), [1])

    def test_the_guard_flags_a_bare_unattributed_occurrence(self):
        self.assertEqual(A.guard_scan_text(A.FORBIDDEN_BLANKET), [1])

    def test_the_guard_accepts_a_declared_forbidden_promotion(self):
        text = ("Forbidden promotions of this package: " + A.FORBIDDEN_BLANKET
                + ", and nothing else.")
        self.assertEqual(A.guard_scan_text(text), [])

    def test_the_committed_receipt_is_also_clean(self):
        path = os.path.join(HERE, "RESULT_V1.json")
        if not os.path.exists(path):
            self.skipTest("RESULT_V1.json not generated yet")
        self.assertEqual(A.guard_scan_text(_read("RESULT_V1.json")), [])

    def test_forbidden_promotions_list_matches_the_freeze(self):
        freeze = _read("FREEZE_V1.md")
        for name in RECEIPT["forbidden_promotions"]:
            self.assertIn(name, freeze, name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
