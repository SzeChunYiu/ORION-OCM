#!/usr/bin/env python3
"""Tests for gmi-833-census-registration-pass-v1.

Run:  python3 -I -B test_registration_pass_v1.py
      python3 -I -O -B test_registration_pass_v1.py
Covers: freeze-first custody, frozen-parent pins, register-key uniqueness,
predictions P1-P6 of FREEZE_V1.md, sentinel semantics, pointer verifier
(no-alarm + detection), hostiles H1-H8, the null, two-route set equality,
decidability counts, and the no-float rule over the receipt.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import registration_pass_v1 as A                 # noqa: E402
import independent_registration_oracle_v1 as B   # noqa: E402

PINS = {
    "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json": "709159c53c6284366aaf1f05380f5fada8d81a98",
    "research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json": "61006b756721c748f8dcc797c755abd25cc42956",
    "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json": "0cfca31894960e24c1c12bb7bf05f9e13e63f4aa",
    "research/gmi-833-maturity-rescore-v3-w4-v1/SCORES_V3_DELTA.json": "d8f6d02ecb61b83c20a10c5fe0fab67fbcfd5493",
    "research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json": "66c3b7e4ef91e096f0ece2720af4645bebe75238",
    "research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json": "41174e0557ac4fa721412e1afc06c72163c34f94",
    "research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json": "9050c2e01e44347aa2b19710286890be1a5eb21d",
}

_CACHE = {}


def route_a():
    if "a" not in _CACHE:
        _CACHE["inp"] = A.Inputs()
        _CACHE["a"] = A.build(_CACHE["inp"], write=False)
    return _CACHE["inp"], _CACHE["a"]


def route_b():
    if "b" not in _CACHE:
        _CACHE["b"] = B.derive()
    return _CACHE["b"]


def git(*args):
    p = subprocess.run(["git"] + list(args), cwd=str(REPO), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def walk_no_float(obj, path="receipt"):
    if isinstance(obj, float):
        raise AssertionError("float at %s" % path)
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk_no_float(v, path + "." + str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            walk_no_float(v, path + "[%d]" % i)


class TestCustody(unittest.TestCase):
    def test_freeze_is_first(self):
        rc, out = git("log", "--reverse", "--format=%H", "--", "research/gmi-833-census-registration-pass-v1/")
        if rc != 0 or not out.strip():
            self.skipTest("no git history available")
        first = out.split()[0]
        rc, files = git("show", "--name-only", "--format=", first, "--", "research/gmi-833-census-registration-pass-v1/")
        names = [f for f in files.splitlines() if f.strip()]
        self.assertTrue(any(f.endswith("FREEZE_V1.md") for f in names), names)
        if len(names) == 1:
            self.assertTrue(names[0].endswith("FREEZE_V1.md"))

    def test_frozen_parents_unchanged(self):
        for path, blob in PINS.items():
            rc, out = git("rev-parse", "HEAD:" + path)
            if rc != 0:
                self.skipTest("git unavailable for %s" % path)
            self.assertEqual(out.strip(), blob, path)

    def test_census_frozen_sha(self):
        inp, _ = route_a()
        self.assertEqual(inp.census["frozen_source_sha"], A.CENSUS_FROZEN_SHA)


class TestIdentity(unittest.TestCase):
    def test_register_keys_unique_and_object_id_not_a_key(self):
        inp, _ = route_a()
        self.assertEqual(len(inp.by_key), len(inp.objects))
        self.assertGreater(sum(1 for v in inp.by_id.values() if len(v) > 1), 0)

    def test_P1_every_legacy_row_bound_or_refused_never_both(self):
        inp, out = route_a()
        legacy = [r["result_id"] for r in inp.scores if A.LEGACY_RE.match(r["result_id"])]
        refused = set(r["result_id"] for r in out["refusals"] if r["kind"] == "SCORED_ROW")
        for rid in legacy:
            self.assertTrue((rid in out["bound"]) != (rid in refused), rid)
        self.assertEqual(len(out["bound"]), 173)
        self.assertEqual(out["result"]["binding"]["by_rule"], {"B1_RESULT_ID_SUFFIX_EXACT": 145, "B2_THEOREM_NAME_ID_EXACT": 28})
        self.assertEqual(len(refused), 0)

    def test_P2_no_package_level_row_binds(self):
        inp, out = route_a()
        for rid in out["bound"]:
            self.assertFalse(rid.startswith(A.PACKAGE_LEVEL_PREFIXES), rid)
        self.assertEqual(out["result"]["binding"]["package_level_rows"], 25)
        self.assertEqual(out["result"]["binding"]["package_level_rows_with_census_objects"], 0)

    def test_bound_object_is_in_row_citation_paths(self):
        _, out = route_a()
        self.assertEqual(out["result"]["binding"]["source_path_in_citation_paths"], 173)

    def test_one_object_per_row_and_one_row_per_object(self):
        _, out = route_a()
        keys = [k for _, k in out["bound"].values()]
        self.assertEqual(len(keys), len(set(keys)))

    def test_P4_loose_prefix_variant_measured(self):
        inp, out = route_a()
        self.assertEqual(out["result"]["binding"]["loose_prefix_variant_extra_bindings"], 0)

    def test_similarity_plants_refused(self):
        _, out = route_a()
        h3 = [h for h in out["result"]["hostiles"] if h["id"] == "H3"][0]
        self.assertTrue(h3["detected"])
        self.assertEqual(h3["perturbed"], 0)

    def test_v3_delta_applied_to_w4c_only(self):
        inp, out = route_a()
        self.assertEqual(out["result"]["binding"]["v3_delta_applied"], ["GMI833_V2_LEGACY_074_W4-C"])
        key = out["bound"]["GMI833_V2_LEGACY_074_W4-C"][1]
        r = out["records"][key]
        self.assertEqual((r["maturity_level"], r["evidence_level"]), ("M2", "EV2"))
        self.assertEqual(tuple(r["binding"]["v3_delta"]["superseded_v2"]), ("M4", "EV3"))
        self.assertEqual(len(r["provenance"]["maturity_level"]), 2)


class TestPopulation(unittest.TestCase):
    def test_P5_counts(self):
        _, out = route_a()
        pop = out["result"]["population"]
        self.assertEqual(pop["maturity_level"]["after_populated"], 172)
        self.assertEqual(pop["evidence_level"]["after_populated"], 170)
        self.assertEqual(pop["maturity_level"]["after_bound_but_scored_unknown"], 1)
        self.assertEqual(pop["evidence_level"]["after_bound_but_scored_unknown"], 3)
        self.assertLessEqual(pop["maturity_level"]["after_populated"] + pop["maturity_level"]["after_bound_but_scored_unknown"], 197)
        for f in A.LIST_FIELDS:
            self.assertLessEqual(pop[f]["after_populated"], 235 + out["result"]["population"]["strongest_parents_entries_from_edges"])
            self.assertEqual(pop[f]["before_populated"], 0)
            self.assertEqual(pop[f]["after_empty_list"], 0)
        self.assertEqual(pop["assumptions"]["after_populated"], 173)
        self.assertEqual(pop["strongest_parents"]["after_populated"], 179)
        self.assertEqual(pop["claim_dependencies"]["after_populated"], 30)
        self.assertEqual(pop["claim_dependencies"]["edges"], 113)

    def test_sentinel_semantics(self):
        inp, out = route_a()
        for r in out["records"].values():
            for f in A.LIST_FIELDS:
                v = r[f]
                self.assertTrue(v == A.UNREGISTERED or (isinstance(v, list) and len(v) > 0), (r["register_key"], f))
                if isinstance(v, list):
                    self.assertEqual(len(r["provenance"][f]), len(v))
            for f in ("maturity_level", "evidence_level"):
                if r[f] != A.UNKNOWN:
                    self.assertTrue(r["provenance"].get(f))
            self.assertEqual(len(r["provenance"].get("claim_dependencies", [])), len(r["claim_dependencies"]))

    def test_unpopulated_objects_carry_nothing(self):
        inp, out = route_a()
        self.assertEqual(out["result"]["population"]["objects"] - out["result"]["population"]["populated_records"],
                         len(inp.objects) - len(out["records"]))
        self.assertGreater(len(inp.objects) - len(out["records"]), 22000)


class TestEdgesAndGaps(unittest.TestCase):
    def test_edge_resolution_counts(self):
        _, out = route_a()
        e = out["result"]["edges"]
        self.assertEqual(e["resolved"], 153)
        self.assertEqual(e["refused"], 12)
        self.assertEqual(e["duplicate_records_skipped"], 3)
        self.assertEqual(e["refused_by_reason"], {"AMBIGUOUS_CHILD_IDENTITY": 6, "NO_OBJECT_AT_CITATION": 6})

    def test_P3_partition_reproduces_AAG3(self):
        _, out = route_a()
        g = out["result"]["gap_graph"]
        self.assertEqual(g["grade_counts"], {"IMMATERIAL": 0, "MINOR": 0, "MATERIAL": 847, "CRITICAL": 293})
        self.assertEqual(g["monotonicity"]["violations"], 0)
        self.assertEqual(g["materiality_v1_distinct"], 1)
        self.assertEqual(g["materiality_v2_distinct"], 2)

    def test_P6_descendants(self):
        _, out = route_a()
        g = out["result"]["gap_graph"]
        self.assertEqual(g["gaps"], 1140)
        self.assertEqual(g["gaps_with_nonempty_descendants"], 50)
        self.assertEqual(g["gaps_isolated"], 1090)
        self.assertLessEqual(g["gaps_with_nonempty_descendants"], out["result"]["population"]["claim_dependencies"]["distinct_parent_ids"])
        self.assertGreaterEqual(g["descendant_keys_total"], g["descendant_keys_total_direct"])

    def test_descendant_verifier_no_alarm_and_detects_plant(self):
        _, out = route_a()
        self.assertEqual(out["result"]["descendant_verification"]["findings"], 0)
        h8 = [h for h in out["result"]["hostiles"] if h["id"] == "H8"][0]
        self.assertTrue(h8["detected"])


class TestVerifierAndHostiles(unittest.TestCase):
    def test_pointer_verifier_no_alarm_on_real_register(self):
        _, out = route_a()
        self.assertEqual(out["result"]["pointer_verification"]["findings"], 0)
        self.assertGreater(out["result"]["pointer_verification"]["pointers_checked"], 1000)

    def test_all_hostiles_detected_and_moved(self):
        _, out = route_a()
        ids = [h["id"] for h in out["result"]["hostiles"]]
        self.assertEqual(ids, ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"])
        for h in out["result"]["hostiles"]:
            self.assertTrue(h["detected"], h["id"])
            self.assertNotEqual(h["baseline"], h["perturbed"], h["id"])

    def test_null_beaten(self):
        _, out = route_a()
        nl = out["result"]["null"]
        self.assertTrue(nl["true_beats_every_draw"])
        self.assertEqual(nl["draws_at_or_above_true"], 0)
        self.assertEqual(nl["true_bound_rows"], 173)
        self.assertEqual(nl["suffix_null"]["bound_max"], 0)
        Fraction(nl["permuted_mean"])  # parses as an exact rational


class TestTwoRoutes(unittest.TestCase):
    def test_bound_sets_identical(self):
        _, out = route_a()
        b = route_b()
        self.assertEqual(dict((rid, k) for rid, (_, k) in out["bound"].items()), b["bound"])
        self.assertEqual(dict((rid, r) for rid, (r, _) in out["bound"].items()), b["rules"])
        self.assertEqual(out["result"]["binding"]["v3_delta_applied"], b["delta_applied"])
        self.assertEqual(sorted(p["result_id"] for p in out["package_level"] if p.get("source") != "SCORES_V3_DELTA"), b["package_level_rows"])

    def test_levels_identical(self):
        _, out = route_a()
        b = route_b()
        a_levels = dict((k, [r["maturity_level"], r["evidence_level"]]) for k, r in out["records"].items() if r["provenance"].get("maturity_level"))
        self.assertEqual(a_levels, b["levels"])

    def test_ledgers_identical(self):
        _, out = route_a()
        b = route_b()
        for f in A.LIST_FIELDS:
            a_keys = sorted(k for k, r in out["records"].items() if r[f] != A.UNREGISTERED and r["binding"].get("registration"))
            self.assertEqual(a_keys, b["ledger_keys"][f], f)
        for kf, content in b["ledger_content"].items():
            k, f = kf.split("|")
            a_val = out["records"][k][f]
            if f == "strongest_parents":
                a_val = [v for v in a_val if not v.endswith("(CORPUS_CLAIM)") and not v.endswith("(CORPUS_CLAIM_BY_NAME)")]
            self.assertEqual(list(a_val), content, kf)

    def test_edges_identical(self):
        _, out = route_a()
        b = route_b()
        self.assertEqual(sorted(out["dep_edges"]), [tuple(x) for x in b["dep_edges"]])
        a_byname = sorted((k, p) for k, r in out["records"].items() for p in r["dependency_parents_by_name"])
        self.assertEqual(a_byname, [tuple(x) for x in b["byname_edges"]])
        a_sp = sorted((k, v) for k, r in out["records"].items() if isinstance(r["strongest_parents"], list)
                      for v in r["strongest_parents"] if v.endswith("(CORPUS_CLAIM)") or v.endswith("(CORPUS_CLAIM_BY_NAME)"))
        self.assertEqual(a_sp, [tuple(x) for x in b["sp_edges"]])
        self.assertEqual(sorted((r["layer"], r["index"], r["reason"]) for r in out["refusals"] if r["kind"] == "DEPENDENCY_EDGE"),
                         [tuple(x) for x in b["refused_edges"]])

    def test_descendants_and_grades_identical(self):
        _, out = route_a()
        b = route_b()
        self.assertEqual(dict((g["id"], g["descendants"]) for g in out["gaps"]), b["descendants"])
        self.assertEqual(dict((g["id"], g["descendants_direct"]) for g in out["gaps"]), b["descendants_direct"])
        self.assertEqual(dict((g["id"], g["materiality"]) for g in out["gaps"]), b["grade_of"])
        self.assertEqual(dict((k, v) for k, v in out["result"]["gap_graph"]["grade_counts"].items() if v), b["grade_counts"])

    def test_populated_record_set_identical(self):
        _, out = route_a()
        b = route_b()
        self.assertEqual(len(out["records"]), b["populated_records"])

    def test_decidability_inputs_identical(self):
        _, out = route_a()
        b = route_b()
        s = out["decidability"]["summary"]
        self.assertEqual(s["binding_field_populated"], b["decidability"]["assumptions_populated"])
        self.assertEqual(s["binding_fraction"], b["decidability"]["binding_fraction"])
        aa24 = [r for r in out["decidability"]["rows"] if r["row_id"] == "AA24"][0]
        self.assertEqual(aa24["evaluable_objects_after"], b["decidability"]["stat_or_empirical_registered"])
        aa33 = [r for r in out["decidability"]["rows"] if r["row_id"] == "AA33"][0]
        self.assertEqual(aa33["evaluable_objects_after"], b["decidability"]["statistical_registered"])
        self.assertEqual(aa33["registered_statistical_families"], b["decidability"]["registered_statistical_families"])


class TestDecidability(unittest.TestCase):
    def test_counts(self):
        _, out = route_a()
        s = out["decidability"]["summary"]
        self.assertEqual(s["rows"], 22)
        self.assertEqual(s["already_decided"], 4)
        self.assertEqual(s["gained_registered_discriminator"], 5)
        self.assertEqual(s["still_no_registered_discriminator"], 13)
        self.assertEqual(s["binding_field"], "assumptions")
        self.assertEqual(s["binding_field_populated"], 173)
        verdicts = dict((r["row_id"], r["verdict"]) for r in out["decidability"]["rows"])
        for rid in ("AA24", "AA25", "AA26", "AA27", "AA33"):
            self.assertEqual(verdicts[rid], "REGISTERED_DISCRIMINATOR", rid)
        for rid in ("AA19", "AA21", "AA31", "AA37"):
            self.assertEqual(verdicts[rid], "ALREADY_DECIDED", rid)
        self.assertEqual(sum(1 for v in verdicts.values() if v == "NO_REGISTERED_DISCRIMINATOR"), 13)

    def test_every_evaluable_object_has_a_registered_ledger(self):
        _, out = route_a()
        for r in out["decidability"]["rows"]:
            if r["verdict"] == "REGISTERED_DISCRIMINATOR":
                self.assertLessEqual(r["evaluable_objects_after"], 173, r["row_id"])
                self.assertEqual(r["evaluable_objects_before"], 0)


class TestExactness(unittest.TestCase):
    def test_no_float_anywhere_in_receipt(self):
        _, out = route_a()
        walk_no_float(out["result"])
        walk_no_float(out["decidability"])
        walk_no_float(route_b())


if __name__ == "__main__":
    unittest.main(verbosity=2)
