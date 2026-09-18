#!/usr/bin/env python3
"""Tests for gmi-833-aa-gap-object-v1.

Every hostile uses assert_moved(): the perturbation must change the exact
quantity it targets AND the checker must flag it. A hostile that cannot move
its quantity is a defect, not a pass.

Runnable as `python3 -I -B test_gap_object_v1.py` and `python3 -I -O -B ...`.
Assertions are unittest assertions, so -O does not disable them.
"""
import copy
import json
import os
import random
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gap_object_v1 as A            # noqa: E402
import independent_oracle_v1 as B    # noqa: E402

SCHEMA = A.load_schema()
DOC = A.load_gaps()
RECORDS = DOC["gaps"]


def write_tmp(obj):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as fh:
        json.dump(obj, fh)
    return path


class Moved(unittest.TestCase):
    def assert_moved(self, name, baseline, perturbed, flagged):
        """A hostile is only valid if the quantity it perturbs actually moved."""
        self.assertNotEqual(baseline, perturbed,
                            "HOSTILE %s did not move its quantity (%r) - the hostile is "
                            "structurally invisible to the checker" % (name, baseline))
        self.assertTrue(flagged, "HOSTILE %s moved its quantity but was not flagged" % name)


class TestAAG1SchemaRealization(Moved):
    def test_nine_named_fields_bound_injectively(self):
        f = SCHEMA["open_gap_fields"]
        self.assertEqual(len(f), 9)
        self.assertEqual(len(set(x["key"] for x in f)), 9)
        self.assertEqual(len(set(x["aa01_name"] for x in f)), 9)
        self.assertEqual(
            [x["aa01_name"] for x in f],
            ["claim", "premise", "inference", "unresolved assumption",
             "possible counterexample", "severity", "owner", "parent result",
             "evidence needed"])

    def test_route_a_conformance(self):
        r = A.validate_open_gap(RECORDS, SCHEMA)
        self.assertEqual(r["records"], 1140)
        self.assertEqual(r["conforming"], 1140)
        self.assertEqual(r["empty_cell_events"], 0)
        self.assertEqual(r["missing_field_events"], 0)
        self.assertEqual(r["distinct_claim_id"], 1094)
        self.assertEqual(r["verdict"], "PASS")

    def test_two_routes_agree(self):
        a = A.run()
        b = B.run()
        self.assertEqual(a["AAG-1"]["records"], b["records"])
        self.assertEqual(a["AAG-1"]["conforming"], b["conforming"])
        self.assertEqual(a["AAG-1"]["distinct_claim_id"], b["distinct_claim_id"])
        self.assertEqual(a["AAG-2"]["degenerate_columns"], b["degenerate_columns"])
        self.assertEqual(a["AAG-3"]["applied"]["grade_counts"], b["grade_counts"])
        self.assertEqual(a["AAG-3"]["applied"]["kind_counts"], b["kind_counts"])
        self.assertEqual(a["AAG-4"]["violations"], b["closure_chain"]["violations"])
        self.assertEqual(a["AA38_not_earned"]["records_with_nonempty_descendants"],
                         b["records_with_nonempty_descendants"])
        # exact rational impurity must agree numerator/denominator after reduction
        for k, av in a["AAG-2"]["columns"].items():
            bv = b["columns"][k]
            from fractions import Fraction
            self.assertEqual(Fraction(av["impurity_num"], av["impurity_den"]),
                             Fraction(bv["impurity_num"], bv["impurity_den"]), k)

    def test_hostile_H1_dropped_field(self):
        base = A.validate_open_gap(RECORDS, SCHEMA)["conforming"]
        bad = copy.deepcopy(RECORDS)
        del bad[7]["premise"]
        r = A.validate_open_gap(bad, SCHEMA)
        self.assert_moved("H1 dropped-field", base, r["conforming"], r["verdict"] == "FAIL")
        self.assertEqual(r["missing_field_events"], 1)

    def test_hostile_H2_blanked_value(self):
        base = A.validate_open_gap(RECORDS, SCHEMA)["empty_cell_events"]
        bad = copy.deepcopy(RECORDS)
        bad[11]["evidence_needed"] = "   "
        r = A.validate_open_gap(bad, SCHEMA)
        self.assert_moved("H2 blanked-value", base, r["empty_cell_events"], r["verdict"] == "FAIL")

    def test_hostile_H3_duplicate_json_key_seen_only_by_route_B(self):
        """json.load collapses duplicate keys; the byte-level route must not."""
        rec = copy.deepcopy(RECORDS[0])
        body = ", ".join('"%s": %s' % (k, json.dumps(v)) for k, v in rec.items())
        body += ', "severity": ""'          # duplicate key with an empty value
        raw = '{"schema": "GMI_GAP_GRAPH_V1", "gaps": [{%s}]}' % body
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            fh.write(raw)
        try:
            b = B.run(gaps_path=path)
            self.assert_moved("H3 duplicate-key", 0, b["duplicate_key_records"],
                              b["conforming"] == 0)
            with open(path) as fh:
                collapsed = json.load(fh)["gaps"]
            a = A.validate_open_gap(collapsed, SCHEMA)
            # route A is structurally blind to the duplicate itself; it only sees
            # the collapsed last value. Recorded, not hidden.
            self.assertEqual(a["missing_field_events"], 0)
        finally:
            os.unlink(path)

    def test_null_randomized_records_do_not_conform(self):
        rng = random.Random(8331140)
        keys = [f["key"] for f in SCHEMA["open_gap_fields"]]
        passed = 0
        for _ in range(200):
            rec = {}
            for k in keys:
                roll = rng.randrange(3)
                if roll == 0:
                    continue                       # missing
                if roll == 1:
                    rec[k] = ""                    # empty
                else:
                    rec[k + "_" + str(rng.randrange(9))] = "x"   # renamed
            r = A.validate_open_gap([rec], SCHEMA)
            if r["verdict"] == "PASS":
                passed += 1
        self.assertEqual(passed, 0, "null must be beaten: %d/200 random records conformed" % passed)
        # no-alarm case: the true records must pass the same checker
        self.assertEqual(A.validate_open_gap(RECORDS, SCHEMA)["verdict"], "PASS")


class TestAAG2Degeneracy(unittest.TestCase):
    def test_incumbent_grading_columns_are_exactly_degenerate(self):
        cols = A.column_report(RECORDS, ["severity", "materiality", "status",
                                         "owner_role", "parent_result", "descendants"])
        for k, v in cols.items():
            self.assertEqual((v["impurity_num"], v["impurity_den"]), (0, 1), k)
            self.assertEqual(v["distinct"], 1, k)

    def test_informative_columns_are_not_degenerate(self):
        cols = A.column_report(RECORDS, ["claim_id", "possible_counterexample"])
        for k, v in cols.items():
            self.assertNotEqual(v["impurity_num"], 0, k)


class TestAAG3Materiality(Moved):
    def test_monotone_over_whole_finite_domain(self):
        r = A.monotonicity_violations(SCHEMA)
        self.assertEqual(r["domain_points"], 256)
        self.assertEqual(r["comparisons"], 768)
        self.assertEqual(r["violations"], 0)

    def test_applied_partition_is_non_degenerate(self):
        r = A.grade_real_gaps(RECORDS, SCHEMA)
        self.assertEqual(r["graded"], 1140)
        self.assertEqual(r["grade_counts"]["MATERIAL"], 847)
        self.assertEqual(r["grade_counts"]["CRITICAL"], 293)
        self.assertEqual(r["unknown_kind"], 0)
        self.assertTrue(r["non_degenerate"])
        # the incumbent column could not have produced this partition
        self.assertEqual(len(set(x["materiality"] for x in RECORDS)), 1)

    def test_hostile_H4_flipped_severity_moves_grades(self):
        base = A.grade_real_gaps(RECORDS, SCHEMA)["grade_counts"]["CRITICAL"]
        bad = copy.deepcopy(RECORDS)
        flipped = 0
        for r in bad:
            if r["id"].split("-")[1] == "FIN2UNIV" and flipped < 5:
                r["severity"] = "MINOR"
                flipped += 1
        got = A.grade_real_gaps(bad, SCHEMA)["grade_counts"]["CRITICAL"]
        self.assert_moved("H4 flipped-severity", base, got, got == base - 5)

    def test_hostile_H5_non_monotone_grade_table_is_caught(self):
        def bad_grade(idx):
            if idx == 7:
                return "IMMATERIAL"          # dip: breaks monotonicity
            return A.materiality_grade(idx, SCHEMA)
        base = A.monotonicity_violations(SCHEMA)["violations"]
        got = A.monotonicity_violations(SCHEMA, grade_fn=bad_grade)["violations"]
        self.assert_moved("H5 non-monotone-table", base, got, got > 0)

    def test_threshold_is_a_declared_function_not_a_judgement(self):
        t = SCHEMA["recursion_threshold"]
        self.assertEqual(t["index"], 6)
        self.assertEqual(t["grade"], "MATERIAL")
        self.assertEqual(A.materiality_grade(6, SCHEMA), "MATERIAL")
        self.assertEqual(A.materiality_grade(5, SCHEMA), "MINOR")


class TestAAG4ClosureGrades(Moved):
    def test_four_grades_declared(self):
        names = [g["grade"] for g in SCHEMA["closure_grades"]]
        self.assertEqual(names, ["LOCALLY_CLOSED", "HOSTILE_CLOSED",
                                 "REPLICATED_CLOSED", "REAL_SCALE_CLOSED"])

    def test_chain_is_total_over_all_evidence_points(self):
        r = A.closure_chain_violations(SCHEMA)
        self.assertEqual(r["evidence_points"], 32)
        self.assertEqual(r["violations"], 0)

    def test_hostile_H6_broken_lattice_is_caught(self):
        base = A.closure_chain_violations(SCHEMA)["violations"]
        bad = copy.deepcopy(SCHEMA)
        bad["closure_grades"][1]["requires"] = ["hostiles_detected"]
        got = A.closure_chain_violations(bad)["violations"]
        self.assert_moved("H6 broken-lattice", base, got, got > 0)

    def test_hostile_H7_bare_closed_detector_recall_and_no_alarm(self):
        planted = "\n".join([
            "The gap is closed.",
            "We consider this CLOSED at real scale.",
            "status: closed",
        ])
        clean = "\n".join([
            "The gap is LOCALLY_CLOSED.",
            "Promoted to HOSTILE_CLOSED after the sweep.",
            "REPLICATED_CLOSED and REAL_SCALE_CLOSED are not awarded.",
            "The enclosure and the closure of the set are unrelated words.",
        ])
        hits_planted = A.bare_closed_hits(planted)
        hits_clean = A.bare_closed_hits(clean)
        self.assert_moved("H7 bare-closed", len(hits_clean), len(hits_planted),
                          len(hits_planted) == 3)
        self.assertEqual(len(hits_clean), 0,
                         "no-alarm case failed: %r" % (hits_clean,))


class TestAAG5RepairDelta(Moved):
    def test_emitter_total_over_the_frozen_universe(self):
        r = A.repair_delta_totality(RECORDS, SCHEMA)
        self.assertEqual(r["attempted"], 1140)
        self.assertEqual(r["emitted"], 1140)
        self.assertEqual(r["verdict"], "PASS")

    def test_emitted_record_carries_every_mandatory_field(self):
        rec = A.emit_repair_delta(RECORDS[0], "worked repair", ["A1"], ["G1"],
                                  "LOCALLY_CLOSED", SCHEMA)
        for f in SCHEMA["repair_delta_fields"]:
            self.assertIn(f["key"], rec)
        self.assertTrue(rec["interrogation_answered"])
        self.assertEqual(rec["new_gaps"], ["G1"])

    def test_hostile_H8_unlabelled_closure_grade_rejected(self):
        base = A.repair_delta_totality(RECORDS, SCHEMA)["emitted"]
        bad = copy.deepcopy(RECORDS)
        for r in bad[:4]:
            r["id"] = ""
        got = A.repair_delta_totality(bad, SCHEMA)
        self.assert_moved("H8 empty-id", base, got["emitted"], got["verdict"] == "FAIL")
        with self.assertRaises(ValueError):
            A.emit_repair_delta(RECORDS[0], "r", [], [], "closed", SCHEMA)


class TestAA38NotEarned(unittest.TestCase):
    def test_descendant_linkage_is_absent_and_disclosed(self):
        self.assertEqual(len([r for r in RECORDS if r.get("descendants")]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
