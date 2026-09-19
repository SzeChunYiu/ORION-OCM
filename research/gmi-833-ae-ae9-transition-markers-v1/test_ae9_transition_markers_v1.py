#!/usr/bin/env python3
"""Tests for the GMI #833 AE9 transition-marker package.

Runnable standalone with ``-v``.  Every assertion is a ``unittest.TestCase``
method, never the bare ``assert`` statement, so that nothing is stripped when
the suite runs under ``python3 -I -O -B``.
"""

import ast
import hashlib
import itertools
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ae9_transition_markers_v1 as routeA
import independent_marker_oracle_v1 as routeB

RECEIPT_PATH = os.path.join(HERE, "RESULT_V1.json")
ROUTE_A_FILE = os.path.join(HERE, "ae9_transition_markers_v1.py")
ROUTE_B_FILE = os.path.join(HERE, "independent_marker_oracle_v1.py")
TEST_FILE = os.path.abspath(__file__)


def load_receipt():
    with open(RECEIPT_PATH, "r") as handle:
        return json.load(handle)


class TestSourceDiscipline(unittest.TestCase):

    def test_no_bare_assert_anywhere_in_the_package(self):
        for path in (ROUTE_A_FILE, ROUTE_B_FILE, TEST_FILE):
            with open(path, "r") as handle:
                tree = ast.parse(handle.read(), filename=path)
            bare = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
            self.assertEqual(
                bare, [], "bare assert statement in " + os.path.basename(path))

    def test_no_float_literal_in_any_module(self):
        for path in (ROUTE_A_FILE, ROUTE_B_FILE, TEST_FILE):
            with open(path, "r") as handle:
                tree = ast.parse(handle.read(), filename=path)
            floats = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(
                        node.value, float):
                    floats.append(node.value)
            self.assertEqual(
                floats, [], "float literal in " + os.path.basename(path))

    def test_route_b_does_not_import_route_a(self):
        with open(ROUTE_B_FILE, "r") as handle:
            tree = ast.parse(handle.read(), filename=ROUTE_B_FILE)
        banned = "ae9_transition_markers_v1"
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(banned, alias.name)
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(banned, node.module or "")

    def test_route_b_names_no_route_a_symbol(self):
        with open(ROUTE_B_FILE, "r") as handle:
            text = handle.read()
        code_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            code_lines.append(line)
        body = "\n".join(code_lines)
        tree = ast.parse(body)
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings.add(doc)
        executable = body
        for doc in docstrings:
            executable = executable.replace(doc, "")
        self.assertNotIn("ae9_transition_markers_v1", executable)


class TestRegisterCustody(unittest.TestCase):

    def test_register_self_digest_recomputes(self):
        with open(os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")) as handle:
            reg = json.load(handle)
        canonical = dict(
            (k, v) for k, v in reg.items()
            if k not in ("self_digest_sha256", "self_digest_note"))
        digest = hashlib.sha256(json.dumps(
            canonical, sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        self.assertEqual(digest, reg["self_digest_sha256"])

    def test_executor_refuses_to_emit_on_a_tampered_register(self):
        """Exercise the refusal path, not just the hash arithmetic."""
        import shutil
        import tempfile
        workdir = tempfile.mkdtemp(prefix="ae9-tamper-")
        try:
            for name in ("ae9_transition_markers_v1.py",
                         "independent_marker_oracle_v1.py"):
                shutil.copy(os.path.join(HERE, name),
                            os.path.join(workdir, name))
            with open(os.path.join(HERE,
                                   "PROSPECTIVE_REGISTER_V1.json")) as handle:
                reg = json.load(handle)
            reg["registered_constants"] = dict(reg["registered_constants"])
            reg["registered_constants"]["exact_match_k"] = 3
            with open(os.path.join(workdir,
                                   "PROSPECTIVE_REGISTER_V1.json"), "w") as h:
                h.write(json.dumps(reg, sort_keys=True, indent=2) + "\n")
            proc = subprocess.Popen(
                [sys.executable, "-I", "-B",
                 os.path.join(workdir, "ae9_transition_markers_v1.py")],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir)
            out, err = proc.communicate()
            self.assertNotEqual(proc.returncode, 0,
                                "executor emitted on a tampered register")
            self.assertEqual(out, b"", "executor wrote a receipt anyway")
            self.assertIn(b"register", err.lower())
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def test_untampered_register_digest_recomputes(self):
        with open(os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")) as handle:
            reg = json.load(handle)
        canonical = dict(
            (k, v) for k, v in reg.items()
            if k not in ("self_digest_sha256", "self_digest_note"))
        digest = hashlib.sha256(json.dumps(
            canonical, sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        self.assertEqual(digest, reg["self_digest_sha256"])


class TestReceiptShape(unittest.TestCase):

    def setUp(self):
        self.receipt = load_receipt()

    def test_required_keys_present(self):
        for key in ("schema", "issue", "issue_comment_id", "package",
                    "source_main", "freeze_commit", "claim_ceiling", "verdict",
                    "checks", "results", "bounds", "hostiles", "null",
                    "prospective_predictions", "forbidden_promotions"):
            self.assertIn(key, self.receipt)

    def test_verdict_and_checks(self):
        self.assertEqual(self.receipt["verdict"], "GREEN")
        self.assertEqual(self.receipt["issue"], 833)
        self.assertEqual(self.receipt["issue_comment_id"], 5692689542)
        for name in sorted(self.receipt["checks"]):
            self.assertTrue(self.receipt["checks"][name], name)

    def test_forbidden_promotions_all_asserted_absent(self):
        names = [f["name"] for f in self.receipt["forbidden_promotions"]]
        self.assertIn("NEURAL_RESULT_FROM_NON_NEURAL_ROSTER", names)
        self.assertIn("TRANSITION_MARKER_PREDICTS_CAPABILITY_ONSET", names)
        for entry in self.receipt["forbidden_promotions"]:
            self.assertTrue(entry["asserted_absent"], entry["name"])

    def test_four_measurement_rows_are_left_open(self):
        self.assertEqual(len(self.receipt["rows_left_open"]), 4)
        for row in self.receipt["rows_left_open"]:
            self.assertTrue(len(row["instrument_required"]) > 40)

    def test_receipt_is_byte_identical_in_both_modes(self):
        with open(RECEIPT_PATH, "rb") as handle:
            stored = handle.read()
        for flags in (["-I", "-B"], ["-I", "-O", "-B"]):
            out = subprocess.check_output(
                [sys.executable] + flags + [ROUTE_A_FILE], cwd=HERE)
            self.assertEqual(out, stored, "mode " + " ".join(flags))


class TestArchitectureIndependence(unittest.TestCase):

    def setUp(self):
        self.receipt = load_receipt()
        self.row = self.receipt["results"]["architecture_independence"]

    def test_two_learners_same_partition_equal_markers(self):
        gf2 = None
        for _key, vals in routeA.AFFINE_FORMS:
            if tuple(vals) == routeA.T_XOR12:
                gf2 = tuple(vals)
        greedy = routeB.greedy_decision_list(
            routeB.T_XOR12, routeB.POOL, routeB.TREE_DEPTH)
        self.assertEqual(routeA.canonical_labels(gf2),
                         routeA.canonical_labels(greedy))
        tmask = routeA.as_mask(routeA.T_XOR12)
        self.assertEqual(routeA.marker_vector(routeA.canonical_labels(gf2), tmask),
                         routeA.marker_vector(
                             routeA.canonical_labels(greedy), tmask))
        self.assertTrue(self.row["same_partition_two_learners"][
            "markers_exactly_equal"])

    def test_injective_reencoding_moves_codes_and_fixes_markers(self):
        tmask = routeA.as_mask(routeA.T_XOR12)
        base = routeA.marker_vector(
            routeA.canonical_labels(routeA.T_XOR12), tmask)
        for shift in (3, 5, 11, 101):
            recoded = tuple("z%d" % (shift * z + shift) for z in routeA.T_XOR12)
            self.assertNotEqual(
                tuple(str(z) for z in routeA.T_XOR12), recoded)
            self.assertEqual(
                routeA.marker_vector(routeA.canonical_labels(recoded), tmask),
                base)
        self.assertTrue(self.row["injective_reencoding"][
            "code_set_actually_changed"])
        self.assertTrue(self.row["injective_reencoding"][
            "every_marker_unchanged"])

    def test_distinct_partitions_move_at_least_one_marker(self):
        self.assertTrue(self.row["distinct_partitions_move_a_marker"][
            "every_pair_moves_REFINEMENT"])
        for pair in self.row["distinct_partitions_move_a_marker"]["pairs"]:
            self.assertTrue(
                Fraction(pair["normalized_partition_distance"]) > 0)


class TestRowThree(unittest.TestCase):

    def setUp(self):
        self.row = load_receipt()["results"]["row3_smooth_versus_qualitative"]

    def test_smooth_arm_exact_numbers(self):
        self.assertEqual(self.row["smooth"]["accuracy"],
                         ["1/2", "17/32", "9/16", "19/32", "5/8", "21/32",
                          "11/16", "23/32", "3/4"])
        self.assertEqual(set(self.row["smooth"]["per_step_increments"]),
                         set(["1/32"]))
        self.assertTrue(self.row["smooth"]["structural_profile_constant"])
        self.assertEqual(self.row["smooth"]["structural_tuple"], [16, 24, 2])

    def test_jump_arm_exact_numbers(self):
        self.assertEqual(self.row["jump"]["accuracy"][:5], ["1/2"] * 5)
        self.assertEqual(self.row["jump"]["accuracy"][5], "11/14")
        self.assertEqual(self.row["jump"]["m_star_structural"], 5)
        self.assertEqual(self.row["jump"]["m_star_accuracy"], 5)
        self.assertTrue(self.row["jump"]["same_step"])
        self.assertEqual(self.row["jump"]["readout_arity_by_m"][4], ["NONE"])
        self.assertIn("2", self.row["jump"]["readout_arity_by_m"][5])
        self.assertEqual(self.row["jump"]["jump_magnitude_heldout"], "2/7")


class TestRowFour(unittest.TestCase):

    def setUp(self):
        self.row = load_receipt()["results"]["row4_emergence_reaudit"]

    def test_underlying_is_exactly_linear(self):
        self.assertEqual(self.row["underlying_increment_spread"], "0")
        self.assertEqual(set(self.row["underlying_increments"]), set(["1/32"]))

    def test_transform_has_a_strict_knee(self):
        self.assertTrue(self.row["transformed_increments_strictly_increasing"])
        incs = [Fraction(x) for x in self.row["transformed_increments"]]
        for i in range(len(incs) - 1):
            self.assertTrue(incs[i] < incs[i + 1])
        self.assertTrue(Fraction(self.row["knee_ratio_last_over_first"]) > 1)

    def test_knee_does_not_raise_the_genuine_transition_alarm(self):
        self.assertTrue(self.row[
            "classifier_on_transformed_curve_raises_no_alarm"])

    def test_classifier_recall_and_no_alarm(self):
        val = self.row["classifier_validation"]
        self.assertEqual(val["recall"], 3)
        self.assertEqual(val["planted_positives"], 3)
        self.assertTrue(val["no_alarm_on_clean_smooth_trajectory"])
        for key in sorted(val["confusion_over_roster"]):
            planted = key.split("__")[0]
            row = val["confusion_over_roster"][key]
            self.assertEqual(row[planted], 1)
            self.assertEqual(sum(row.values()), 1)

    def test_witness_classes(self):
        self.assertEqual(self.row["witness_classes"], {
            "TRAJ_SMOOTH": "THRESHOLDED_METRIC_ARTIFACT",
            "TRAJ_JUMP": "PHASE_LIKE_REORGANIZATION",
            "TRAJ_GROK": "GROKKING_DELAYED_GENERALIZATION"})


class TestBounds(unittest.TestCase):

    def setUp(self):
        self.bounds = load_receipt()["bounds"]

    def test_bound_status_is_emitted_not_refused(self):
        for b in self.bounds:
            self.assertIn(b["status"],
                          ("FALSIFIABLE_BOUND", "UNFALSIFIED_BOUND"))
            self.assertEqual(b["status"] == "FALSIFIABLE_BOUND",
                             "violated_by" in b)
            self.assertEqual(b["used_to_close_a_row"],
                             b["status"] == "FALSIFIABLE_BOUND")

    def test_five_bounds_with_consistent_vacuity_records(self):
        self.assertEqual(len(self.bounds), 5)
        for b in self.bounds:
            lo = Fraction(b["range_lo"])
            hi = Fraction(b["range_hi"])
            val = Fraction(b["bound_value"])
            expected = (val >= hi) if b["kind"] == "upper" else (val <= lo)
            self.assertEqual(expected, b["vacuous"], b["id"])
            self.assertFalse(b["vacuous"], b["id"])
            self.assertTrue(len(b["range_derivation"]) > 60, b["id"])

    def test_every_bound_has_a_violating_witness_that_violates(self):
        for b in self.bounds:
            self.assertIn("violated_by", b)
            witness = Fraction(b["violated_by"]["value"])
            val = Fraction(b["bound_value"])
            if b["kind"] == "upper":
                self.assertTrue(witness > val, b["id"])
            else:
                self.assertTrue(witness < val, b["id"])
            self.assertTrue(
                len(b["violated_by"]["relaxed_class"]) > 10, b["id"])

    def test_attainment_is_recorded_separately(self):
        for b in self.bounds:
            self.assertIn("attained_by", b)
            self.assertNotEqual(b["attained_by"], b["violated_by"])


class TestHostiles(unittest.TestCase):

    def setUp(self):
        self.hostiles = load_receipt()["hostiles"]

    def test_all_five_registered_hostiles_present(self):
        names = sorted(h["name"] for h in self.hostiles)
        self.assertEqual(names, ["H_ARITY_CAP", "H_INVARIANCE_INFLATE",
                                 "H_PARTITION_RELABEL", "H_THRESHOLD_K",
                                 "H_TRAIN_LEAK"])

    def test_potency_then_detection_or_silence(self):
        for h in self.hostiles:
            self.assertTrue(h["potency"], h["name"] + " could not move it")
            if h["inverted"]:
                self.assertTrue(h["silence"], h["name"])
                self.assertEqual(h["true_value"], h["perturbed_value"])
            else:
                self.assertTrue(h["detected"], h["name"])
                self.assertNotEqual(h["true_value"], h["perturbed_value"])

    def test_inverted_hostile_is_the_relabelling_one(self):
        inverted = [h["name"] for h in self.hostiles if h["inverted"]]
        self.assertEqual(inverted, ["H_PARTITION_RELABEL"])


class TestNull(unittest.TestCase):

    def setUp(self):
        self.null = load_receipt()["null"]

    def test_registered_trial_count(self):
        self.assertEqual(self.null["trials"], 200)
        self.assertEqual(sum(self.null["class_counts"].values()), 200)

    def test_witness_beats_the_largest_false_alarm(self):
        self.assertTrue(Fraction(self.null["planted_witness_magnitude"])
                        > Fraction(self.null["largest_false_alarm_magnitude"]))
        self.assertTrue(self.null["witness_exceeds_largest_false_alarm"])

    def test_labelled_confusion_counts_over_the_null(self):
        c = self.null["confusion_over_null"]
        self.assertEqual(c["true_positive"] + c["false_negative"],
                         self.null["affine_draws"])
        self.assertEqual(c["true_positive"] + c["false_positive"],
                         self.null["alarms"])
        self.assertEqual(sum([c["true_positive"], c["false_negative"],
                              c["false_positive"], c["true_negative"]]),
                         self.null["trials"])

    def test_no_alarm_on_known_clean_witness(self):
        self.assertEqual(self.null["known_clean_witnesses_flagged"], [])

    def test_every_firing_trial_is_diagnosed(self):
        self.assertEqual(len(self.null["firing_trials"]), self.null["alarms"])
        for trial in self.null["firing_trials"]:
            self.assertIn("target_is_affine", trial)
            self.assertTrue(Fraction(trial["magnitude"]) > 0)
        affine = [t for t in self.null["firing_trials"] if t["target_is_affine"]]
        self.assertEqual(len(affine), self.null["alarms_on_affine_draws"])


class TestPredictions(unittest.TestCase):

    def test_a_refuted_prediction_cannot_suppress_the_receipt(self):
        receipt = load_receipt()
        self.assertNotIn("all_predictions_confirmed", receipt["checks"])
        summary = receipt["prospective_prediction_summary"]
        self.assertEqual(summary["registered"], summary["reported"])
        self.assertEqual(summary["confirmed"] + summary["refuted"],
                         summary["reported"])

    def test_every_registered_prediction_is_reported(self):
        receipt = load_receipt()
        with open(os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")) as handle:
            reg = json.load(handle)
        registered = sorted(p["id"] for p in reg["prospective_predictions"])
        reported = sorted(p["id"] for p in receipt["prospective_predictions"])
        self.assertEqual(registered, reported)
        for p in receipt["prospective_predictions"]:
            self.assertIn(p["verdict"], ("CONFIRMED", "REFUTED"))
            self.assertTrue(len(p["values"]) > 0, p["id"])


class TestRouteAgreement(unittest.TestCase):

    def test_spanning_counts_agree(self):
        for m in routeA.SAMPLE_RANGE:
            self.assertEqual(routeA.spanning_count(routeA.POOL, m),
                             routeB.spanning_count(routeB.POOL, m))

    def test_markers_agree_on_named_partitions(self):
        pairs = (
            (routeA.POINTS, routeA.T_XOR12),
            (routeA.D_X4, routeA.T_XOR12),
            (routeA.T_XOR12, routeA.T_XOR12),
            (routeA.T_PARITY4, routeA.T_PARITY4),
            (routeA.D_X4, routeA.T_PARITY4),
        )
        for codes, target in pairs:
            a = routeA.marker_vector(
                routeA.canonical_labels(codes), routeA.as_mask(target))
            b = routeB.marker_vector(
                routeB.partition_of(list(codes)), tuple(target))
            self.assertEqual(a, b)

    def test_trajectory_quantities_agree(self):
        specs = {"TRAJ_SMOOTH": routeA.SPEC_SMOOTH,
                 "TRAJ_JUMP": routeA.SPEC_JUMP,
                 "TRAJ_GROK": routeA.SPEC_GROK}
        for name in sorted(specs):
            a = routeA.closed_form_trajectory(specs[name])
            b = routeB.trajectory_report(name)
            self.assertEqual([str(x) for x in a["acc_overall"]],
                             [str(x) for x in b["acc_overall"]], name)
            self.assertEqual([str(x) for x in a["acc_heldout"]],
                             [str(x) for x in b["acc_heldout"]], name)
            self.assertEqual([str(x) for x in a["acc_train"]],
                             [str(x) for x in b["acc_train"]], name)
            self.assertEqual(a["determined_count"], b["determined_count"], name)

    def test_receipt_records_agreement(self):
        self.assertTrue(load_receipt()["checks"]["routes_agree"])


class TestMarkerDefinitions(unittest.TestCase):

    def test_markers_are_functions_of_the_partition_only(self):
        tmask = routeA.as_mask(routeA.T_XOR12)
        codes_a = routeA.T_XOR12
        codes_b = tuple(1 - z for z in routeA.T_XOR12)
        self.assertNotEqual(codes_a, codes_b)
        self.assertEqual(
            routeA.marker_vector(routeA.canonical_labels(codes_a), tmask),
            routeA.marker_vector(routeA.canonical_labels(codes_b), tmask))

    def test_mirkin_distance_is_zero_only_on_equal_partitions(self):
        parts = [routeA.canonical_labels(c) for c in
                 (routeA.POINTS, routeA.D_X4, routeA.T_XOR12,
                  routeA.T_PARITY4)]
        for p, q in itertools.combinations(parts, 2):
            self.assertTrue(routeA.mirkin_distance(p, q) > 0)
        for p in parts:
            self.assertEqual(routeA.mirkin_distance(p, p), Fraction(0))

    def test_usable_is_bounded_by_the_budget_on_parity(self):
        tmask = routeA.as_mask(routeA.T_PARITY4)
        for codes in (routeA.POINTS, routeA.D_X4, routeA.T_PARITY4,
                      routeA.T_XOR12):
            self.assertEqual(
                routeA.usable(routeA.canonical_labels(codes), tmask),
                Fraction(1, 2))
        self.assertEqual(
            routeA.usable(routeA.canonical_labels(routeA.T_PARITY4), tmask,
                          routeA.FULL_MASKS), Fraction(1))


if __name__ == "__main__":
    unittest.main()
