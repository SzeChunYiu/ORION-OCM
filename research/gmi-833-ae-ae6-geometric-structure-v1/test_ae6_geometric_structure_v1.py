#!/usr/bin/env python3
"""GMI #833 AE6 tests: two-route agreement, hostile potency then detection,
bound vacuity records, the null, and the prospective predictions.

Runnable as `python3 -I -B test_ae6_geometric_structure_v1.py -v` and
`python3 -I -O -B test_ae6_geometric_structure_v1.py -v`.  Stdlib only.

No bare `assert` statement appears in this file: under `-O` the statement is
stripped and the test would pass vacuously.  Every check is a unittest
assertion method or an explicit `raise AssertionError`.

Every hostile is asserted in two stages, in order:
  (1) POTENCY   -- the perturbation actually moves the quantity it targets;
  (2) DETECTION -- the checker flags the perturbed object.
A hostile that fails stage (1) is a package defect, so stage (1) is a hard
assertion and never a skip.
"""
import ast
import json
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ae6_geometric_structure_v1 as A            # noqa: E402
import independent_geometry_oracle_v1 as O        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = A.build_result()
R = RES["results"]
ORACLE = O.oracle()


class TestVerdict(unittest.TestCase):
    def test_green(self):
        self.assertEqual(RES["verdict"], "GREEN")
        for name, ok in sorted(RES["checks"].items()):
            self.assertTrue(ok, "check failed: " + name)

    def test_required_receipt_keys(self):
        for key in ("schema", "issue", "issue_comment_id", "package",
                    "source_main", "freeze_commit", "claim_ceiling",
                    "verdict", "checks", "results", "bounds", "hostiles",
                    "null", "prospective_predictions",
                    "forbidden_promotions"):
            self.assertIn(key, RES)
        self.assertEqual(RES["issue"], 833)
        self.assertEqual(RES["issue_comment_id"], 5692689542)

    def test_no_float_anywhere_in_receipt(self):
        def walk(node, path):
            if isinstance(node, float):
                self.fail("float found in receipt at " + path)
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, path + "/" + str(k))
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, path + "/" + str(i))
        walk(RES, "")

    def test_receipt_matches_the_shipped_file(self):
        with open(os.path.join(HERE, "RESULT_V1.json"),
                  encoding="utf-8") as fh:
            shipped = fh.read()
        rebuilt = json.dumps(RES, sort_keys=True, indent=2) + "\n"
        self.assertEqual(shipped, rebuilt)

    def test_deterministic_across_rebuilds(self):
        again = A.build_result()
        self.assertEqual(json.dumps(again, sort_keys=True, indent=2),
                         json.dumps(RES, sort_keys=True, indent=2))

    def test_register_digest_is_recomputed_and_enforced(self):
        reg, digest = A.load_register()
        self.assertEqual(digest, reg["self_digest_sha256"])
        self.assertEqual(RES["register_digest"], digest)


class TestRouteIndependence(unittest.TestCase):
    def test_distinct_modules(self):
        self.assertNotEqual(A.__file__, O.__file__)

    def test_oracle_has_no_executable_import_of_route_a(self):
        with open(O.__file__, encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
        banned = "ae6_geometric_structure_v1"
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if banned in alias.name:
                        self.fail("oracle imports route A: " + alias.name)
            if isinstance(node, ast.ImportFrom):
                if node.module and banned in node.module:
                    self.fail("oracle imports route A: " + str(node.module))

    def test_oracle_uses_a_different_dimension_algorithm(self):
        with open(A.__file__, encoding="utf-8") as fh:
            srcA = fh.read()
        with open(O.__file__, encoding="utf-8") as fh:
            srcB = fh.read()
        self.assertIn("def gf2_rank", srcA)
        self.assertNotIn("def gf2_rank", srcB)
        self.assertIn("def affine_closure", srcB)
        self.assertNotIn("def affine_closure", srcA)


class TestTwoRouteAgreement(unittest.TestCase):
    def test_scope_constants(self):
        self.assertEqual(ORACLE["geometric_cycle_ranks"],
                         R["registered_scope"]["geometric_cycle_ranks"])
        self.assertEqual(ORACLE["subgroup_lattice_size"],
                         R["registered_scope"]["subgroup_lattice_size"])
        self.assertEqual(
            ORACLE["algorithmic_circuit"]["accepting_set"],
            R["registered_scope"]["algorithmic_circuit"]["accepting_set"])

    def test_every_roster_source_classifies_identically(self):
        for name in sorted(R["structure_classes"]):
            a = R["structure_classes"][name]
            b = ORACLE["structure_classes"][name]
            for key in ("affine_dimension", "support_size",
                        "maximal_coset_dimensions", "block_support_sizes",
                        "is_block_product", "graph", "membership"):
                self.assertEqual(a[key], b[key], name + "." + key)

    def test_union_census_agrees(self):
        for key in ("supports_with_dimension_at_least_1", "members",
                    "non_members", "non_member_size_histogram",
                    "non_member_stabilizer_orders"):
            self.assertEqual(R["union_predicate_census"][key],
                             ORACLE["union_predicate_census"][key], key)

    def test_sparse_containment_agrees(self):
        self.assertEqual(R["sparse_containment_certificate"],
                         ORACLE["sparse_containment_certificate"])

    def test_row2_agrees(self):
        cert = R["row2_nonmanifold_learnable"]["non_manifold_certificates"]
        self.assertEqual(cert["degree_sequence"], ORACLE["row2"][
            "degree_sequence"])
        self.assertEqual(cert["maximal_coset_dimensions"],
                         ORACLE["row2"]["maximal_coset_dimensions"])
        self.assertEqual(
            R["row2_nonmanifold_learnable"]["learned_exactly"]["accuracy"],
            ORACLE["row2"]["M_local_2_accuracy"])

    def test_row3_agrees(self):
        a = R["row3_low_dimension_is_useless"]
        b = ORACLE["row3"]
        self.assertEqual(a["literal_witness"]["affine_dimension"],
                         b["literal_affine_dimension"])
        self.assertEqual(
            a["literal_witness"]["coordinates_determining_the_target"],
            b["literal_coordinates_carrying_the_target"])
        self.assertEqual(
            a["impossibility"]["dimension_1_exhaustive"][
                "cases_satisfying_the_full_conjunction"],
            b["dimension_1_cases_satisfying_the_full_conjunction"])
        for ka, kb in (("block1_factor_dimension",
                        "composite_block1_factor_dimension"),
                       ("block2_factor_dimension",
                        "composite_block2_factor_dimension"),
                       ("interventional_effect_block1",
                        "composite_interventional_effect"),
                       ("best_accuracy_reading_block1_only",
                        "composite_accuracy_block1"),
                       ("best_accuracy_reading_block2_only",
                        "composite_accuracy_block2")):
            self.assertEqual(a["composite_witness"][ka], b[kb], ka)

    def test_derivations_agree(self):
        pairs = (
            ("derivation_locality", "derivation_locality"),
            ("derivation_symmetry", "derivation_symmetry"),
            ("derivation_compositionality", "derivation_compositionality"))
        for ka, kb in pairs:
            a = R[ka]
            b = ORACLE[kb]
            self.assertEqual(a["integer_cost"], b["integer_cost"], ka)
            self.assertEqual(a["positive"]["named_class_accuracy"],
                             b["positive_named"], ka)
            self.assertEqual(a["positive"]["comparator_accuracy"],
                             b["positive_comparator"], ka)
            self.assertEqual(a["matched_failure"]["named_class_accuracy"],
                             b["failure_named"], ka)
            self.assertEqual(a["matched_failure"]["accuracy_drop"],
                             b["failure_drop"], ka)

    def test_description_code_agrees(self):
        self.assertEqual(R["description_code"]["costs"],
                         ORACLE["description_code"]["costs"])
        self.assertEqual(R["description_code"]["kraft_sum"],
                         ORACLE["description_code"]["kraft_sum"])
        self.assertEqual(R["description_code"]["relaxed_code_kraft_sum"],
                         ORACLE["description_code"]["relaxed_code_kraft_sum"])
        self.assertEqual(
            R["description_code"]["registered_description_count"],
            ORACLE["description_code"]["registered_description_count"])

    def test_null_agrees(self):
        self.assertEqual(RES["null"]["random_worlds_flagged"],
                         ORACLE["null"]["random_worlds_flagged"])
        self.assertEqual(RES["null"]["largest_null_magnitude"],
                         ORACLE["null"]["largest_null_magnitude"])
        self.assertEqual(RES["null"]["planted_positive_flagged"],
                         ORACLE["null"]["planted_positive_flagged"])
        self.assertEqual(RES["null"]["planted_positive_magnitude"],
                         ORACLE["null"]["planted_positive_magnitude"])


class TestHierarchy(unittest.TestCase):
    def test_strictness_table_is_complete_and_resolved(self):
        table = R["strictness_table"]
        self.assertEqual(len(table), 30)
        for row in table:
            if row["separated"]:
                self.assertIsNotNone(row["witness"])
                mem = R["structure_classes"][row["witness"]]["membership"]
                self.assertTrue(mem[row["in_class"]])
                self.assertFalse(mem[row["not_in_class"]])
            else:
                self.assertIsNone(row["witness"])
                self.assertTrue(bool(row["reason"]))

    def test_separated_count(self):
        self.assertEqual(R["strictness_summary"]["separated_with_witness"], 23)
        self.assertEqual(R["strictness_summary"]["not_separated"], 7)

    def test_union_predicate_is_near_universal(self):
        c = R["union_predicate_census"]
        self.assertEqual(c["supports_with_dimension_at_least_1"], 65519)
        self.assertEqual(c["members"], 65503)
        self.assertEqual(c["non_members"], 16)
        self.assertEqual(c["non_member_size_histogram"], {"15": 16})
        self.assertTrue(c["every_non_member_has_nontrivial_stabilizer"])
        self.assertNotIn(1, c["non_member_stabilizer_orders"])

    def test_geometric_cycle_ranks_come_from_the_definition(self):
        self.assertEqual(R["registered_scope"]["geometric_cycle_ranks"],
                         [0, 1, 5, 17])


class TestRow2(unittest.TestCase):
    def test_three_independent_non_manifold_certificates(self):
        cert = R["row2_nonmanifold_learnable"]["non_manifold_certificates"]
        self.assertFalse(cert["degree_sequence_is_constant"])
        self.assertTrue(cert["maximal_coset_dimensions_are_heterogeneous"])
        self.assertTrue(cert["pieces_have_distinct_dimensions"])
        self.assertTrue(cert["pieces_intersect"])

    def test_learned_to_exact_accuracy_one(self):
        le = R["row2_nonmanifold_learnable"]["learned_exactly"]
        self.assertEqual(le["accuracy"], "1")
        self.assertEqual(le["class"], "M_local[2]")
        self.assertEqual(le["cost_bits"], 13)


class TestRow3(unittest.TestCase):
    def test_literal_gloss_is_met_exactly(self):
        lit = R["row3_low_dimension_is_useless"]["literal_witness"]
        self.assertEqual(lit["affine_dimension"], 1)
        self.assertEqual(lit["mutual_information_bits"], "0")
        self.assertEqual(lit["interventional_effect"], "0")
        self.assertTrue(lit["register_gloss_satisfied"])

    def test_the_added_conjunct_is_impossible(self):
        imp = R["row3_low_dimension_is_useless"]["impossibility"]
        self.assertEqual(imp["dimension_1_exhaustive"][
            "cases_satisfying_the_full_conjunction"], 0)
        self.assertEqual(imp["dimension_1_exhaustive"]["cases_checked"], 480)
        self.assertEqual(imp["zero_information_forces_constant_target"][
            "violations"], 0)
        self.assertEqual(imp["zero_information_forces_constant_target"][
            "cases_checked"], 34112)

    def test_composite_witness_is_useless_both_ways(self):
        comp = R["row3_low_dimension_is_useless"]["composite_witness"]
        self.assertEqual(comp["block1_factor_dimension"], 1)
        self.assertEqual(comp["block2_factor_dimension"], 2)
        self.assertTrue(comp["block2_is_full_dimension_in_its_block"])
        self.assertEqual(comp["mutual_information_block1_bits"], "0")
        self.assertEqual(comp["interventional_effect_block1"], "0")
        self.assertEqual(comp["best_accuracy_reading_block1_only"], "1/2")
        self.assertEqual(comp["best_accuracy_reading_block2_only"], "1")
        self.assertEqual(comp["interventional_effect_of_coordinate_2"], "1")

    def test_relaxed_companion_breaks_both_bounds(self):
        rel = R["row3_low_dimension_is_useless"]["relaxed_companion"]
        self.assertEqual(rel["mutual_information_block1_bits"], "1")
        self.assertEqual(rel["interventional_effect_block1"], "1")


class TestDerivations(unittest.TestCase):
    def test_locality(self):
        d = R["derivation_locality"]
        self.assertEqual(d["status"], "DERIVED")
        self.assertTrue(d["positive"]["condition_holds"])
        self.assertEqual(d["positive"]["named_class_accuracy"], "1")
        self.assertEqual(d["positive"]["comparator_accuracy"], "7/8")
        self.assertFalse(d["matched_failure"]["condition_holds"])
        self.assertEqual(d["matched_failure"]["named_class_accuracy"], "15/16")
        self.assertEqual(d["matched_failure"]["comparator_accuracy"], "1")
        self.assertTrue(d["matched_failure"]["named_class_strictly_worse"])
        self.assertEqual(d["matched_failure"]["accuracy_drop"], "1/16")

    def test_symmetry(self):
        d = R["derivation_symmetry"]
        self.assertEqual(d["status"], "DERIVED")
        self.assertTrue(d["positive"]["condition_holds"])
        self.assertEqual(d["positive"]["named_class_accuracy"], "1")
        self.assertEqual(d["positive"]["comparator_accuracy"], "13/16")
        self.assertEqual(d["integer_cost"], 12)
        self.assertEqual(d["unshared_cost"], 23)
        self.assertEqual(d["cost_reduction_bits"], 11)
        self.assertEqual(d["orbit_count_reduction"], 11)
        self.assertTrue(d["cost_reduction_equals_orbit_reduction"])
        self.assertFalse(d["matched_failure"]["condition_holds"])
        self.assertEqual(d["matched_failure"]["named_class_accuracy"], "11/16")
        self.assertEqual(d["matched_failure"]["comparator_accuracy"], "1")
        self.assertEqual(d["matched_failure"]["accuracy_drop"], "5/16")

    def test_compositionality(self):
        d = R["derivation_compositionality"]
        self.assertEqual(d["status"], "DERIVED")
        self.assertTrue(d["positive"]["condition_holds"])
        self.assertEqual(d["positive"]["named_class_accuracy"], "1")
        self.assertEqual(d["positive"]["comparator_accuracy"], "5/8")
        self.assertEqual(d["integer_cost"], 14)
        self.assertFalse(d["matched_failure"]["condition_holds"])
        self.assertEqual(d["matched_failure"]["named_class_accuracy"], "7/8")
        self.assertEqual(d["matched_failure"]["failure_comparator_accuracy"],
                         "1")
        self.assertTrue(d["matched_failure"]["named_class_strictly_worse"])
        self.assertEqual(d["matched_failure"]["accuracy_drop"], "1/8")

    def test_monolithic_comparator_cannot_expose_the_modular_failure(self):
        d = R["derivation_compositionality"]
        self.assertFalse(d["matched_failure"][
            "monolithic_comparator_can_expose_the_failure"])
        cont = d["monolithic_comparator_containment"]
        self.assertTrue(cont["all_contained_in_M_modular"])
        self.assertTrue(cont["containment_is_sharp_at_one_more_term"])
        self.assertEqual(cont["monolithic_max_terms_at_that_budget"], 1)

    def test_no_derivation_is_an_unfalsified_condition(self):
        for key in ("derivation_locality", "derivation_symmetry",
                    "derivation_compositionality"):
            self.assertNotEqual(R[key]["status"], "UNFALSIFIED_CONDITION")
            self.assertTrue(R[key]["condition_falsified_on_roster"])


class TestBounds(unittest.TestCase):
    def test_every_bound_carries_the_full_vacuity_record(self):
        self.assertEqual(len(RES["bounds"]), 10)
        for b in RES["bounds"]:
            for field in ("kind", "bound_value", "range_lo", "range_hi",
                          "range_derivation", "vacuous", "attained_by",
                          "violated_by", "status"):
                self.assertIn(field, b, b["name"])
            self.assertIn(b["kind"], ("upper", "lower"))
            self.assertTrue(len(b["range_derivation"]) > 40, b["name"])
            self.assertIsNotNone(b["violated_by"], b["name"])
            self.assertEqual(b["status"], "FALSIFIABLE", b["name"])

    def test_no_bound_is_vacuous_and_the_flag_is_computed(self):
        for b in RES["bounds"]:
            lo = F(b["range_lo"])
            hi = F(b["range_hi"])
            val = F(b["bound_value"])
            expected = val >= hi if b["kind"] == "upper" else val <= lo
            self.assertEqual(b["vacuous"], expected, b["name"])
            self.assertFalse(b["vacuous"], b["name"])
            self.assertTrue(lo <= val <= hi, b["name"])

    def test_range_is_not_taken_from_the_roster(self):
        for b in RES["bounds"]:
            text = b["range_derivation"].lower()
            self.assertIn("definition", text, b["name"])
            for bad in ("largest observed", "smallest observed",
                        "observed extremes", "observed maximum",
                        "observed minimum", "observed range"):
                self.assertNotIn(bad, text, b["name"])

    def test_kraft_bound_is_real(self):
        code = R["description_code"]
        self.assertTrue(code["kraft_sum_is_at_most_1"])
        self.assertTrue(code["relaxed_code_violates_kraft"])
        self.assertTrue(F(code["kraft_sum"]) <= 1)
        self.assertTrue(F(code["relaxed_code_kraft_sum"]) > 1)


class TestHostiles(unittest.TestCase):
    def test_five_registered_hostiles_present(self):
        names = sorted(h["name"] for h in RES["hostiles"])
        self.assertEqual(names, ["H_BLOCK_LEAK", "H_BUDGET_INFLATE",
                                 "H_CYCLE_RANK", "H_DIM_INFLATE",
                                 "H_ORBIT_MERGE"])

    def test_potency_then_detection(self):
        for h in RES["hostiles"]:
            # stage 1: potency. A hostile that cannot move its quantity is a
            # package defect.
            if h["true_value"] == h["perturbed_value"]:
                raise AssertionError(
                    "hostile %s is impotent: true %r equals perturbed %r"
                    % (h["name"], h["true_value"], h["perturbed_value"]))
            self.assertTrue(h["potency"], h["name"])
            # stage 2: detection, asserted only after potency.
            self.assertTrue(h["detected"], h["name"])
            self.assertFalse(h["inverted"], h["name"])

    def test_specific_hostile_movements(self):
        h = dict((x["name"], x) for x in RES["hostiles"])
        self.assertEqual(h["H_DIM_INFLATE"]["true_value"], 4)
        self.assertEqual(h["H_DIM_INFLATE"]["perturbed_value"], 2)
        self.assertFalse(h["H_ORBIT_MERGE"]["true_value"])
        self.assertTrue(h["H_ORBIT_MERGE"]["perturbed_value"])
        self.assertEqual(h["H_BLOCK_LEAK"]["true_value"], "3/4")
        self.assertEqual(h["H_BLOCK_LEAK"]["perturbed_value"], "1")
        self.assertEqual(h["H_BUDGET_INFLATE"]["true_value"], "5/8")
        self.assertEqual(h["H_BUDGET_INFLATE"]["perturbed_value"], "1")
        self.assertEqual(h["H_CYCLE_RANK"]["true_value"], 1)
        self.assertEqual(h["H_CYCLE_RANK"]["perturbed_value"], 2)


class TestNull(unittest.TestCase):
    def test_trials_and_planted_positive(self):
        n = RES["null"]
        self.assertEqual(n["trials"], 200)
        self.assertTrue(n["planted_positive_flagged"])
        self.assertEqual(n["planted_positive_magnitude"], "1/2")

    def test_no_alarm_on_clean_registered_witnesses(self):
        n = RES["null"]
        self.assertTrue(n["no_alarm_case_holds"])
        self.assertTrue(len(n["no_alarm_cases"]) >= 2)
        for c in n["no_alarm_cases"]:
            self.assertFalse(c["detector_fires"], c["witness"])

    def test_firing_rate_is_reported_exactly_and_every_firing_is_genuine(self):
        n = RES["null"]
        self.assertEqual(len(n["random_worlds_flagged_detail"]),
                         n["random_worlds_flagged"])
        self.assertTrue(n["firing_trials_are_genuine_instances"])
        for f in n["random_worlds_flagged_detail"]:
            self.assertEqual(f["mutual_information_block1_bits"], "0")
            self.assertEqual(f["interventional_effect_block1"], "0")
            self.assertEqual(f["best_accuracy_reading_block2_only"], "1")

    def test_magnitude_ceiling_is_definitional(self):
        n = RES["null"]
        self.assertEqual(n["magnitude_definitional_maximum"], "1/2")
        self.assertTrue(n["witness_attains_definitional_maximum"])
        self.assertTrue(F(n["largest_null_magnitude"]) <= F(1, 2))
        # the strictly-exceeds comparison is reported, not claimed
        self.assertIn("witness_exceeds_largest_null_magnitude", n)


class TestProspective(unittest.TestCase):
    def test_every_registered_prediction_is_reported(self):
        reg, _ = A.load_register()
        ids = sorted(p["id"] for p in RES["prospective_predictions"])
        self.assertEqual(
            ids, sorted(p["id"] for p in reg["prospective_predictions"]))
        for p in RES["prospective_predictions"]:
            self.assertIn(p["verdict"], ("CONFIRMED", "REFUTED"))

    def test_p3_is_reported_refuted_with_its_exact_values(self):
        p3 = [p for p in RES["prospective_predictions"]
              if p["id"] == "AE6-P3"][0]
        self.assertEqual(p3["verdict"], "REFUTED")
        self.assertEqual(p3["refuted_conjunct"],
                         "a_full_dimension_coordinate_determines_the_target")
        self.assertTrue(p3["conjuncts"]["affine_dimension_is_1"])
        self.assertTrue(p3["conjuncts"]["mutual_information_is_0_bits"])
        self.assertTrue(p3["conjuncts"]["interventional_effect_is_0"])
        self.assertFalse(p3["conjuncts"][
            "a_full_dimension_coordinate_determines_the_target"])
        self.assertEqual(p3["exact_values"]["coordinates_determining_the_"
                                            "target"], [])

    def test_other_predictions_confirmed(self):
        want = {"AE6-P1": "CONFIRMED", "AE6-P2": "CONFIRMED",
                "AE6-P4": "CONFIRMED", "AE6-P5": "CONFIRMED"}
        got = dict((p["id"], p["verdict"])
                   for p in RES["prospective_predictions"]
                   if p["id"] in want)
        self.assertEqual(got, want)


class TestScope(unittest.TestCase):
    def test_forbidden_promotions_are_carried(self):
        self.assertIn("MANIFOLD_HYPOTHESIS_UNIVERSAL",
                      RES["forbidden_promotions"])
        self.assertIn("LOW_DIMENSION_IMPLIES_LEARNABILITY",
                      RES["forbidden_promotions"])
        self.assertIn("GEOMETRIC_STRUCTURE_IMPLIES_TASK_RELEVANCE",
                      RES["forbidden_promotions"])
        self.assertIn("SYMMETRY_ALWAYS_JUSTIFIES_PARAMETER_SHARING",
                      RES["forbidden_promotions"])

    def test_the_prospective_real_dataset_row_is_left_open(self):
        rows = RES["rows_left_open"]
        self.assertEqual(len(rows), 1)
        self.assertTrue(len(rows[0]["instrument_required"]) > 120)
        self.assertEqual(RES["rows_closed"], 6)

    def test_derivation_worlds_are_declared_separate_from_the_roster(self):
        scope = R["registered_scope"]
        self.assertEqual(len(scope["structure_roster"]), 8)
        for w in scope["derivation_worlds"]:
            if w == "D_LOCAL_POS":
                continue
            self.assertNotIn(w, scope["structure_roster"])
        self.assertIn("derivation_worlds_note", scope)


class TestNoBareAssertInShippedPython(unittest.TestCase):
    def test_no_assert_statement_in_any_shipped_module(self):
        for fname in ("ae6_geometric_structure_v1.py",
                      "independent_geometry_oracle_v1.py",
                      "test_ae6_geometric_structure_v1.py"):
            with open(os.path.join(HERE, fname), encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    self.fail("bare assert statement in " + fname
                              + " at line " + str(node.lineno))


if __name__ == "__main__":
    unittest.main(verbosity=2)
