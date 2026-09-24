#!/usr/bin/env python3
"""Tests for gmi-833-aa1-gap-graph-v1 (issue #839).

Runnable as `python3 -I -B test_gap_graph_v1.py` and `python3 -I -O -B ...`.
Every assertion is a unittest assertion, so `-O` does not remove any check; a
test asserts that `assert` is not relied upon anywhere in the routes.

Planted positives must FIRE in both routes, clean cases must stay SILENT in both
routes, and the two routes must return identical finding lists.
"""
import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gap_graph_v1 as A                      # noqa: E402
import independent_gap_graph_oracle_v1 as B   # noqa: E402
import fixtures_v1 as F                       # noqa: E402

I = A.load_inputs()
GRAPH = A.build(I)
TEXT = A.dumps_graph(GRAPH)
SUMMARY = A.summarize(GRAPH, I)
SCHEMA, OGS, TEMPLATE = I["schema"], I["ogs"], I["template"]
PKG_DIR = HERE
REPO = A.REPO


def committed_graph():
    with open(os.path.join(PKG_DIR, "GMI_GAP_GRAPH_V3.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


class TestPinsAndDeterminism(unittest.TestCase):
    def test_every_input_matches_its_freeze_pin(self):
        rep = A.pin_report()
        self.assertEqual(sorted(rep), sorted(A.INPUTS))
        for k, v in rep.items():
            self.assertTrue(v["match"], "%s drifted: %s != %s" % (k, v["live"], v["pinned"]))

    def test_two_builds_are_byte_identical(self):
        self.assertEqual(A.dumps_graph(A.build(A.load_inputs())), TEXT)

    def test_committed_graph_is_the_build(self):
        with open(os.path.join(PKG_DIR, "GMI_GAP_GRAPH_V3.json"), "r", encoding="utf-8") as fh:
            self.assertEqual(fh.read(), TEXT)

    def test_serialization_round_trips(self):
        self.assertEqual(json.loads(TEXT), json.loads(json.dumps(GRAPH)))

    def test_routes_do_not_rely_on_assert(self):
        for fn in ("gap_graph_v1.py", "independent_gap_graph_oracle_v1.py", "fixtures_v1.py"):
            with open(os.path.join(PKG_DIR, fn), "r", encoding="utf-8") as fh:
                src = fh.read()
            self.assertNotIn("\n    assert ", src, fn)
            self.assertNotIn("\nassert ", src, fn)

    def test_route_b_imports_nothing_from_route_a(self):
        with open(os.path.join(PKG_DIR, "independent_gap_graph_oracle_v1.py"), "r", encoding="utf-8") as fh:
            src = fh.read()
        for banned in ("import gap_graph_v1", "from gap_graph_v1", "gap_object_v1", "fixtures_v1"):
            self.assertNotIn(banned, src)


class TestRealGraph(unittest.TestCase):
    """AA1G-1, AA1G-2, AA1G-3 on the pinned universe (exact equality)."""

    def test_nodes_and_edges(self):
        self.assertEqual(SUMMARY["nodes_by_kind"],
                         {"ASSUMPTION": 2, "CLAIM": 1174, "GAP": 1146, "PARENT": 2, "RESULT": 17})
        self.assertEqual(SUMMARY["edges_by_kind"],
                         {"DEPENDS_ON": 113, "DESCENDANT": 198, "GAP_ON": 1146, "INTRODUCES": 154,
                          "PARENT_OF": 1146})
        self.assertEqual(SUMMARY["descendant_edges_by_rule"],
                         {"R1_ID_PRECEDENCE": 46, "R2_DEPENDENCY_PROPAGATION": 16, "R3_REPAIR_SUCCESSOR": 136})

    def test_gap_identity_is_never_collapsed(self):
        g = SUMMARY["gap_records"]
        self.assertEqual((g["corpus"], g["corpus_distinct_ids"], g["ids_shared_by_several_records"],
                          g["records_under_shared_ids"], g["extracted_ad_loop"]), (1140, 1126, 10, 24, 6))
        ids = [n["id"] for n in GRAPH["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_records_gain_descendants(self):
        d = SUMMARY["descendants"]
        self.assertEqual(d["v1_records_with_nonempty_descendants"], 0)
        self.assertEqual(d["v2_records_with_nonempty_object_descendants"], 50)
        self.assertEqual(d["corpus_records_gaining_gap_descendants_by_R1_R2"], 41)
        self.assertEqual(d["corpus_records_gaining_gap_descendants_any_rule"], 169)
        self.assertEqual(d["corpus_records_with_gap_or_object_descendants"], 207)
        self.assertEqual(d["unmapped_descendant_register_keys"], 0)

    def test_every_descendant_edge_is_derived_by_a_declared_rule(self):
        rules = set(SCHEMA["descendant_rules"])
        for e in GRAPH["edges"]:
            if e[0] == "DESCENDANT":
                self.assertIn(e[3], rules)

    def test_closed_gaps_record_assumptions_and_descendants(self):
        c = SUMMARY["closure"]
        self.assertEqual(c["locally_closed"], 154)
        self.assertEqual(c["locally_closed_by_rule"],
                         {"B1_VERBATIM_REDECLARATION": 108, "B3_POINTER_TO_SAME_CONTENT": 46})
        self.assertEqual(c["closed_with_nonempty_new_assumptions"], 154)
        self.assertEqual(c["closed_with_nonempty_new_gaps"], 136)
        self.assertEqual(c["adjudicated_duplicate_not_closed"], 0)
        self.assertEqual(c["higher_grades_awarded"], 0)
        ctx = A.Context(GRAPH, SCHEMA, OGS)
        for n in GRAPH["nodes"]:
            if n["kind"] == "GAP" and n["closure_state"] != "OPEN":
                rd = n["repair_delta"]
                self.assertTrue(rd["new_assumptions"])
                self.assertEqual(rd["new_gaps"], sorted(ctx.succ("DESCENDANT", n["id"])))
                self.assertEqual(rd["closure_grade_awarded"], n["closure_state"])
                self.assertEqual(n["adjudication"]["reason"], n["adjudication"]["rederived_reason"])

    def test_materiality_blocks_promotion(self):
        m = SUMMARY["materiality"]
        self.assertEqual((m["unresolved_critical_corpus"], m["unresolved_critical_extracted"]), (290, 5))
        self.assertEqual((m["closed_blocked_beyond_local"], m["closed_blocked_by_corpus_rules_only"],
                          m["closed_not_blocked"]), (136, 6, 18))
        ctx = A.Context(GRAPH, SCHEMA, OGS)
        granted_hostile = 0
        for n in GRAPH["nodes"]:
            if n["kind"] == "GAP" and n["closure_state"] == "LOCALLY_CLOSED":
                local = A.evaluate_promotion(GRAPH, n["id"], "LOCALLY_CLOSED", SCHEMA, OGS, ctx=ctx)
                self.assertTrue(local["granted"], n["id"])
                hostile = A.evaluate_promotion(GRAPH, n["id"], "HOSTILE_CLOSED", SCHEMA, OGS, ctx=ctx)
                self.assertFalse(hostile["granted"])
                blocked = bool(ctx.blocking_descendants(n["id"]))
                self.assertEqual("CRITICAL_DESCENDANT_BLOCKS_PROMOTION" in hostile["reasons"], blocked)
                granted_hostile += int(hostile["granted"])
        self.assertEqual(granted_hostile, 0)

    def test_parent_closure_refused(self):
        self.assertEqual(SUMMARY["parent_closure"],
                         {"T833-AA1": {"closure_permitted": False, "unresolved_critical": 5},
                          "T833-B1-AA": {"closure_permitted": False, "unresolved_critical": 292}})

    def test_parent_closure_gate_cli_exits_nonzero(self):
        for key in ("T833-B1-AA", "T833-AA1"):
            p = subprocess.run([sys.executable, "-I", "-B", os.path.join(PKG_DIR, "gap_graph_v1.py"),
                                "--parent-closure-gate", key], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(p.returncode, 1, key)

    def test_claims_linked_to_unresolved_descendants(self):
        c = SUMMARY["claims"]
        self.assertEqual((c["claim_nodes"], c["gap_claim_ids"], c["claims_with_unresolved_descendants"],
                          c["claims_without_unresolved_descendants"]), (1174, 1094, 1082, 92))
        present = set(n["key"] for n in GRAPH["nodes"] if n["kind"] == "CLAIM")
        for n in GRAPH["nodes"]:
            if n["kind"] == "GAP":
                self.assertIn(n["claim_id"], present)

    def test_no_cycles_and_no_findings(self):
        self.assertEqual(SUMMARY["cycles"], {"DEPENDS_ON": {"cycles": [], "self_loops": []},
                                             "DESCENDANT": {"cycles": [], "self_loops": []}})
        self.assertEqual(SUMMARY["validation_findings"], [])
        self.assertEqual(SUMMARY["loop_findings"], [])
        self.assertEqual(SUMMARY["record_findings"], {})

    def test_extracted_gaps_are_ingested_under_their_parent(self):
        ex = [n for n in GRAPH["nodes"] if n["kind"] == "GAP" and n["origin"] == "AD_LOOP"]
        self.assertEqual(len(ex), 6)
        self.assertTrue(all(n["parent_result"] == "T833-AA1" for n in ex))
        r3 = {}
        for e in GRAPH["edges"]:
            if e[3] == "R3_REPAIR_SUCCESSOR":
                r3[e[2]] = r3.get(e[2], 0) + 1
        self.assertEqual(r3, {"GAP:GAP-AD-AA1-B1-CONTEXT#1": 90, "GAP:GAP-AD-AA1-B3-POINTER#1": 46})


class TestTwoRoutes(unittest.TestCase):
    def test_route_b_reproduces_every_headline(self):
        b = B.run()
        self.assertEqual(b["disagreements"], [])
        self.assertEqual(b["descendant_edges_by_rule"], SUMMARY["descendant_edges_by_rule"])
        self.assertEqual(b["depends_on_edges"], SUMMARY["edges_by_kind"]["DEPENDS_ON"])
        self.assertEqual(b["corpus_records_gaining_gap_descendants_by_R1_R2"],
                         SUMMARY["descendants"]["corpus_records_gaining_gap_descendants_by_R1_R2"])
        self.assertEqual(b["locally_closed"], SUMMARY["closure"]["locally_closed"])
        self.assertEqual(b["locally_closed_by_rule"], SUMMARY["closure"]["locally_closed_by_rule"])
        self.assertEqual(b["closed_blocked_beyond_local"], SUMMARY["materiality"]["closed_blocked_beyond_local"])
        self.assertEqual(b["unresolved_critical_corpus"], SUMMARY["materiality"]["unresolved_critical_corpus"])
        self.assertEqual(b["parent_closure"], SUMMARY["parent_closure"])
        self.assertEqual(b["flagship_hostile_closed_refused"], 9)
        self.assertEqual(b["flagship_refused_for_missing_methods"], 9)
        self.assertEqual(b["claims_with_unresolved_descendants"],
                         SUMMARY["claims"]["claims_with_unresolved_descendants"])
        self.assertEqual((b["own_records"], b["own_records_valid"]), (8, 8))
        self.assertEqual(b["validation_findings"], [])
        self.assertEqual(b["loop_findings"], [])

    def test_both_validators_clean_on_committed_graph(self):
        g = committed_graph()
        self.assertEqual(A.validate(g), [])
        self.assertEqual(B.validate(g), [])


class TestPlantedPositives(unittest.TestCase):
    """HAND_CONSTRUCTED_ADVERSARIAL: one planted positive per code; each must fire."""

    def test_clean_baseline_is_silent(self):
        g = F.clean()
        self.assertEqual(A.validate(g), [])
        self.assertEqual(B.validate(g), [])

    def test_every_planted_positive_fires_in_both_routes(self):
        for name, build, code in F.PLANTED:
            with self.subTest(name=name):
                g = build()
                fa, fb = A.validate(g), B.validate(g)
                self.assertIn(code, F.codes(fa), "route A missed %s" % name)
                self.assertIn(code, F.codes(fb), "route B missed %s" % name)
                self.assertEqual(fa, fb, name)
                self.assertGreater(len(fa), 0)

    def test_every_finding_code_has_a_planted_positive(self):
        self.assertEqual(sorted(set(c for _n, _b, c in F.PLANTED)), sorted(SCHEMA["finding_codes"]))

    def test_cycle_is_reported_with_all_members_not_collapsed(self):
        g = [r for r in F.PLANTED if r[0] == "descendant_cycle"][0][1]()
        cyc = [f for f in A.validate(g) if f[0] == "CYCLE"]
        self.assertEqual(cyc, [["CYCLE", "DESCENDANT:GAP:g1#1|GAP:g2#1"]])
        ids = [n["id"] for n in g["nodes"]]
        self.assertIn("GAP:g1#1", ids)
        self.assertIn("GAP:g2#1", ids)


class TestCleanNoAlarm(unittest.TestCase):
    def test_clean_cases_are_silent_in_both_routes(self):
        for name, build in F.CLEAN:
            with self.subTest(name=name):
                g = build()
                self.assertEqual(A.validate(g), [], name)
                self.assertEqual(B.validate(g), [], name)

    def test_qualified_grade_names_are_not_bare(self):
        for grade in A.GRADES:
            self.assertFalse(B.is_bare_closed(grade))
            self.assertEqual(A.GO.bare_closed_hits(grade), [])
        for bare in ("closed", "Closed", "CLOSED", "closed.", "HOSTILE-closed"):
            self.assertTrue(B.is_bare_closed(bare), bare)
            self.assertTrue(A.GO.bare_closed_hits(bare), bare)


class TestPromotionEvaluator(unittest.TestCase):
    def setUp(self):
        self.g = F.clean()

    def ab(self, nid, grade, forbidden=None):
        ra = A.evaluate_promotion(self.g, nid, grade, SCHEMA, OGS, forbidden)
        rb = B.promote(self.g, nid, grade, forbidden)
        self.assertEqual(ra, rb)
        return ra

    def test_bare_and_unknown_requests_refused(self):
        self.assertEqual(self.ab("GAP:g1#1", "closed")["reasons"], ["BARE_CLOSED"])
        self.assertEqual(self.ab("GAP:g1#1", "Closed")["reasons"], ["BARE_CLOSED"])
        self.assertEqual(self.ab("GAP:g1#1", "DONE")["reasons"], ["UNKNOWN_CLOSURE_STATE"])

    def test_local_closure_is_not_blocked_by_a_critical_descendant(self):
        self.assertTrue(self.ab("GAP:g1#1", "LOCALLY_CLOSED")["granted"])

    def test_critical_descendant_blocks_hostile(self):
        n = F.node(self.g, "GAP:g1#1")
        n["closure_evidence"] = F.ev("local_checks_pass", "independent_route", "hostiles_detected")
        n["repair_delta"]["closure_grade_awarded"] = "HOSTILE_CLOSED"
        self.assertEqual(self.ab("GAP:g1#1", "HOSTILE_CLOSED")["reasons"], ["CRITICAL_DESCENDANT_BLOCKS_PROMOTION"])

    def test_forbidden_grades_refused_by_default(self):
        n = F.node(self.g, "RESULT:R2")
        n["closure_evidence"] = F.ev(*F.FLAGS)
        self.assertIn("FORBIDDEN_GRADE_AWARDED", self.ab("RESULT:R2", "REPLICATED_CLOSED")["reasons"])
        self.assertIn("FORBIDDEN_GRADE_AWARDED", self.ab("RESULT:R2", "REAL_SCALE_CLOSED")["reasons"])

    def test_flagship_two_distinct_methods_granted(self):
        self.assertTrue(self.ab("RESULT:R1", "HOSTILE_CLOSED")["granted"])

    def test_flagship_fail_closed_variants(self):
        rec = F.node(self.g, "RESULT:R1")["record"]
        variants = [
            ("one_method", lambda r: r.__setitem__("counterexample_methods",
                                                   [F.slot(1, "BOUNDED_EXHAUSTIVE_ENUMERATION"), F.slot(2)])),
            ("flag_missing_one_method", lambda r: (r.pop("is_flagship"), r.__setitem__(
                "counterexample_methods", [F.slot(1, "PROOF_ASSISTANT"), F.slot(2)]))),
            ("flag_not_bool", lambda r: (r.__setitem__("is_flagship", "no"), r.__setitem__(
                "counterexample_methods", [F.slot(1)]))),
            ("slots_not_list", lambda r: r.__setitem__("counterexample_methods", None)),
            ("slot_not_object", lambda r: r.__setitem__("counterexample_methods",
                                                        ["BOUNDED_EXHAUSTIVE_ENUMERATION", "PROOF_ASSISTANT"])),
            ("undeclared_class", lambda r: r.__setitem__("counterexample_methods",
                                                         [F.slot(1, "BOUNDED_EXHAUSTIVE_ENUMERATION"),
                                                          F.slot(2, "GUESSING")])),
        ]
        for name, mut in variants:
            with self.subTest(name=name):
                self.g = F.clean()
                rec = F.node(self.g, "RESULT:R1")["record"]
                mut(rec)
                r = self.ab("RESULT:R1", "HOSTILE_CLOSED")
                self.assertFalse(r["granted"], name)
                self.assertIn("FLAGSHIP_METHODS_MISSING", r["reasons"])

    def test_non_flagship_needs_no_methods(self):
        n = F.node(self.g, "RESULT:R2")
        n["closure_evidence"] = F.ev("local_checks_pass", "independent_route", "hostiles_detected")
        self.assertTrue(self.ab("RESULT:R2", "HOSTILE_CLOSED")["granted"])

    def test_real_flagship_results_refused(self):
        ctx = A.Context(GRAPH, SCHEMA, OGS)
        fl = [n for n in GRAPH["nodes"] if n["kind"] == "RESULT" and n["record"]["is_flagship"] is True]
        self.assertEqual(len(fl), 9)
        for n in fl:
            r = A.evaluate_promotion(GRAPH, n["id"], "HOSTILE_CLOSED", SCHEMA, OGS, ctx=ctx)
            self.assertFalse(r["granted"])
            self.assertIn("FLAGSHIP_METHODS_MISSING", r["reasons"])
            self.assertEqual(len(n["record"]["counterexample_methods"]), 2)
        f = SUMMARY["flagship"]
        self.assertEqual((f["results"], f["hostile_closed_refused"], f["refused_for_missing_methods"],
                          f["slots_filled_total"]), (9, 9, 9, 0))

    def test_parent_gate_opens_when_critical_resolved(self):
        self.assertFalse(A.parent_closure_gate(self.g, "P", SCHEMA, OGS)["closure_permitted"])
        self.assertFalse(B.parent_gate(self.g, "P")["closure_permitted"])
        g2 = F.CLEAN[1][1]()
        self.assertTrue(A.parent_closure_gate(g2, "P", SCHEMA, OGS)["closure_permitted"])
        self.assertTrue(B.parent_gate(g2, "P")["closure_permitted"])
        self.assertFalse(A.parent_closure_gate(self.g, "NOPE", SCHEMA, OGS)["closure_permitted"])


class TestExhaustiveDifferential(unittest.TestCase):
    """BOUNDED_EXHAUSTIVE_ENUMERATION against both routes."""

    def test_all_small_digraphs(self):
        s = F.exhaustive_digraphs()
        self.assertEqual(s, {"graphs": 4608, "with_cycle": 3865, "with_self_loop": 448,
                             "route_disagreements": 0, "oracle_disagreements": 0})

    def test_gap_promotion_cube(self):
        s = F.exhaustive_gap_promotions()
        self.assertEqual(s["cases"], 13824)
        self.assertEqual(s["route_disagreements"], 0)
        self.assertEqual((s["granted"], s["blocked_by_critical"]), (280, 576))

    def test_flagship_cube(self):
        s = F.exhaustive_flagship_promotions()
        self.assertEqual(s["cases"], 1000)
        self.assertEqual(s["route_disagreements"], 0)
        self.assertEqual(s["flagship_granted_without_two_methods"], 0)
        self.assertEqual(s["granted_hostile_or_higher"], 93)

    def test_parent_cube(self):
        s = F.exhaustive_parent_promotions()
        self.assertEqual((s["cases"], s["route_disagreements"], s["granted_with_open_critical"], s["granted"]),
                         (3072, 0, 0, 330))


class TestRandomizedDifferential(unittest.TestCase):
    """PROPERTY_BASED_RANDOMIZED against both routes."""

    def test_random_graphs(self):
        s = F.randomized_graphs()
        self.assertEqual(s["route_disagreements"], 0)
        self.assertEqual(s["trials"], 300)
        self.assertGreater(s["trials_without_findings"], 0)
        self.assertGreater(s["trials_with_findings"], 0)
        self.assertEqual(s["codes_exercised"], sorted(SCHEMA["finding_codes"]))

    def test_random_loop_mutations(self):
        s = F.randomized_loops()
        self.assertEqual((s["trials"], s["route_disagreements"], s["trials_rejected"]), (200, 0, 200))
        self.assertEqual(s["mutations_never_rejected"], [])


class TestADLoop(unittest.TestCase):
    def setUp(self):
        self.doc = A.load_json(A.OWN["loops"])

    def both(self, doc):
        fa, fb = A.validate_loops(doc, TEMPLATE, OGS), B.validate_loops(doc)
        self.assertEqual(fa, fb)
        return F.codes(fa)

    def test_template_has_the_twelve_steps_in_order(self):
        self.assertEqual([s["name"] for s in TEMPLATE["steps"]],
                         ["claim", "formalize", "parent-search", "derive", "counterexample-search",
                          "repair/downgrade", "architecture-prior audit", "independent implementation",
                          "frozen prediction", "replication", "real-scale test", "new-gap extraction"])
        text = TEMPLATE["source_text"]
        for s in TEMPLATE["steps"]:
            self.assertIn(s["name"], text)

    def test_template_matches_the_issue_text_block(self):
        path = os.path.join(REPO, "research", "gmi-833-checklist-mirror-v1", "comments", "comment_5684607872.md")
        with open(path, "r", encoding="utf-8") as fh:
            mirror = fh.read()
        block = mirror.split("```text\n", 1)[1].split("```", 1)[0]
        self.assertEqual(" ".join(block.split()), TEMPLATE["source_text"])

    def test_real_loop_is_clean(self):
        self.assertEqual(self.both(self.doc), [])
        it = self.doc["loops"][0]["iterations"]
        self.assertEqual(len(it), 2)
        self.assertEqual(sum(len(x["extracted_gaps"]) for x in it), 6)
        self.assertEqual(sum(len(x["assumption_changes"]) for x in it), 5)

    def planted(self, name, fn, code):
        d = copy.deepcopy(self.doc)
        fn(d)
        got = self.both(d)
        self.assertIn(code, got, name)

    def test_iteration_without_extracted_gaps_rejected(self):
        self.planted("empty", lambda d: d["loops"][0]["iterations"][0].__setitem__("extracted_gaps", []),
                     "L_NO_GAP_EXTRACTION")

        def not_run(d):
            d["loops"][0]["iterations"][1]["steps"][11] = {
                "step": "S12_NEW_GAP_EXTRACTION", "status": "NOT_RUN", "reason": "later"}
        self.planted("s12_not_run", not_run, "L_NO_GAP_EXTRACTION")

    def test_silent_assumption_edit_rejected(self):
        def add(d):
            d["loops"][0]["iterations"][1]["assumptions_after"].append("A-SILENT: quietly edited")
        self.planted("silent_add", add, "L_SILENT_ASSUMPTION_EDIT")

        def drop_change(d):
            d["loops"][0]["iterations"][0]["assumption_changes"].pop()
        self.planted("undeclared_change", drop_change, "L_SILENT_ASSUMPTION_EDIT")

        def ref_elsewhere(d):
            d["loops"][0]["iterations"][1]["assumption_changes"][0]["gap_ref"] = "GAP-AD-AA1-SPARSITY"
        self.planted("change_paired_with_gap_from_another_iteration", ref_elsewhere, "L_SILENT_ASSUMPTION_EDIT")

    def test_between_iteration_edit_rejected(self):
        def edit(d):
            d["loops"][0]["iterations"][1]["assumptions_before"][0] = "A0-UNIVERSE: something else"
        self.planted("continuity", edit, "L_ITERATION_CONTINUITY")

    def test_other_loop_codes(self):
        it0 = lambda d: d["loops"][0]["iterations"][0]  # noqa: E731
        it1 = lambda d: d["loops"][0]["iterations"][1]  # noqa: E731
        self.planted("order", lambda d: it0(d)["steps"].reverse(), "L_STEP_MISSING_OR_ORDER")
        self.planted("status", lambda d: it0(d)["steps"][0].__setitem__("evidence", ""), "L_STEP_STATUS")
        self.planted("gap_field", lambda d: it0(d)["extracted_gaps"][0].__setitem__("premise", " "),
                     "L_GAP_RECORD_INVALID")
        self.planted("inputs", lambda d: it0(d)["extracted_gaps"][0]["materiality_inputs"].__setitem__("blast", -1),
                     "L_MATERIALITY_INPUTS")
        self.planted("dup", lambda d: it1(d)["extracted_gaps"].append(copy.deepcopy(it0(d)["extracted_gaps"][0])),
                     "L_DUPLICATE_GAP_ID")
        self.planted("stop_reason", lambda d: it1(d).__setitem__("stop_reason", "CHECKLIST_TOO_LONG"),
                     "L_STOP_REASON")
        self.planted("stop_unjustified", lambda d: it1(d).__setitem__("stop_reason", "NO_MATERIAL_GAP_AT_THRESHOLD"),
                     "L_STOP_UNJUSTIFIED")
        self.planted("schema", lambda d: d["loops"][0].pop("iterations"), "L_SCHEMA")

    def test_terminal_iteration_with_only_immaterial_gaps_may_stop(self):
        d = copy.deepcopy(self.doc)
        last = d["loops"][0]["iterations"][1]
        for g in last["extracted_gaps"]:
            g["materiality_inputs"] = {"severity": "INFO", "evidence_mode": "HOSTILE_CHECKED",
                                       "scope": "LOCAL", "blast": 0}
            g["severity"] = "INFO"
        last["stop_reason"] = "NO_MATERIAL_GAP_AT_THRESHOLD"
        self.assertEqual(self.both(d), [])

    def test_validate_loop_cli(self):
        p = subprocess.run([sys.executable, "-I", "-B", os.path.join(PKG_DIR, "gap_graph_v1.py"), "--validate-loop",
                            os.path.join(PKG_DIR, "AD_LOOP_RECORDS_V1.json")],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(p.returncode, 0)


class TestResultRecords(unittest.TestCase):
    def test_all_records_in_graph_valid_in_both_routes(self):
        recs = [n["record"] for n in GRAPH["nodes"] if n["kind"] == "RESULT"]
        self.assertEqual(len(recs), 17)
        for r in recs:
            self.assertEqual(A.validate_result_record(r, SCHEMA), [], r["result_id"])
            self.assertTrue(B.record_ok(r), r["result_id"])

    def test_flagship_records_copied_with_pointers(self):
        f = SUMMARY["flagship"]
        self.assertEqual(f["unregistered_fields"], dict((k, 0) for k in SCHEMA["result_record_list_fields"]))
        self.assertEqual((f["evidence_level_unregistered"], f["freeze_pointer_registered"]), (9, 8))
        for n in GRAPH["nodes"]:
            if n["kind"] == "RESULT" and n["record"]["is_flagship"]:
                prov = n["record"]["provenance"]
                for k in ("assumptions", "falsifiers", "strongest_parents", "dependencies",
                          "forbidden_extrapolations"):
                    self.assertIn(k, prov)

    def test_own_records_have_two_distinct_methods(self):
        self.assertEqual(SUMMARY["own_results"], {"records": 8, "with_two_distinct_filled_methods": 8})

    def test_planted_invalid_records_rejected(self):
        base = A.load_json(A.OWN["results"])["records"][0]
        muts = [("missing_field", lambda r: r.pop("prior_disclosure")),
                ("empty_list", lambda r: r.__setitem__("falsifiers", [])),
                ("blank_string_in_list", lambda r: r.__setitem__("assumptions", ["ok", " "])),
                ("bad_scope", lambda r: r.__setitem__("scope", "GALACTIC")),
                ("flagship_scope_not_flagged", lambda r: r.__setitem__("scope", "FLAGSHIP")),
                ("bad_timing", lambda r: r["prior_disclosure"].__setitem__("outcome_timing", "LATER")),
                ("bare_state", lambda r: r.__setitem__("closure_state", "closed")),
                ("slot_gap", lambda r: r["counterexample_methods"][0].__setitem__("slot", 5)),
                ("evidence_missing", lambda r: r["evidence"].pop("maturity_level")),
                ("closure_evidence_extra", lambda r: r["closure_evidence"].__setitem__("vibes", True))]
        for name, mut in muts:
            with self.subTest(name=name):
                r = copy.deepcopy(base)
                mut(r)
                self.assertNotEqual(A.validate_result_record(r, SCHEMA), [], name)
                self.assertFalse(B.record_ok(r), name)


class TestReceiptAndReconciliation(unittest.TestCase):
    def test_receipt_has_no_float_and_holds_the_ceiling(self):
        with open(os.path.join(PKG_DIR, "RESULT_V1.json"), "r", encoding="utf-8") as fh:
            rec = json.load(fh)

        def walk(x):
            self.assertNotIsInstance(x, float)
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(rec)
        self.assertEqual(rec["claim_ceiling"], A.CLAIM_CEILING)
        for f in ("ALL_GAPS_EXHAUSTED", "INDEPENDENT_HOSTILE_REVIEW_COMPLETE", "CORPUS_AUDIT_COMPLETE",
                  "REPLICATED_CLOSED", "REAL_SCALE_CLOSED", "COMPLETE_GMI"):
            self.assertIn(f, rec["forbidden_promotions"])

    def test_receipt_matches_live_run(self):
        import check_receipt_v1 as C
        self.assertEqual(C.check(), [])

    def test_reconciliation_claims_only_earned_rows(self):
        with open(os.path.join(PKG_DIR, "ISSUE_833_COMMENT_RECONCILIATION_AA1_GAP_GRAPH_V1.json"),
                  "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        self.assertEqual(rec["schema"], "GMI_ISSUE_COMMENT_RECONCILIATION_V1")
        self.assertEqual((rec["issue"], rec["comment_id"]), (833, 5684607872))
        earned = sorted(r["row_id"] for r in rec["replacements"])
        self.assertEqual(earned, ["AA11", "AA38", "AD01", "AD02"])
        self.assertIn("AA40", [r["row_id"] for r in rec["not_closed"]])
        path = os.path.join(REPO, "research", "gmi-833-checklist-mirror-v1", "comments", "comment_5684607872.md")
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        for r in rec["replacements"] + rec["not_closed"]:
            anchor = [i for i, ln in enumerate(lines) if ln.strip() == r["anchor"]]
            self.assertEqual(len(anchor), 1, r["anchor"])
            lo = anchor[0] + 1
            hi = next((j for j in range(lo, len(lines)) if lines[j].startswith("#")), len(lines))
            self.assertEqual(sum(1 for j in range(lo, hi) if lines[j] == r["old"]), 1, r["old"])
        for r in rec["replacements"]:
            self.assertEqual(r["comment_id"], 5684607872)
            self.assertTrue(r["new"].startswith("- [x] " + r["old"][len("- [ ] "):]))
            text = r["old"][len("- [ ] "):]
            key = hashlib.sha256((r["anchor"] + "\x00" + text).encode("utf-8")).hexdigest()
            self.assertTrue(r["new"].endswith("L:" + key[:12]))
            self.assertEqual(r["status"], "EARNED")
            self.assertEqual(r["apply_state"], "PENDING")


class TestCustody(unittest.TestCase):
    def git(self, *args):
        p = subprocess.run(["git"] + list(args), cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            return None
        return p.stdout.decode("utf-8")

    def test_freeze_committed_first_and_unchanged(self):
        if self.git("rev-parse", "--is-inside-work-tree") is None:
            self.skipTest("not a git work tree; the workflow's custody step enforces this")
        log = self.git("log", "--reverse", "--format=%H", "--", "research/gmi-833-aa1-gap-graph-v1/")
        self.assertTrue(log and log.split())
        first = log.split()[0]
        files = [f for f in self.git("show", "--name-only", "--format=", first, "--",
                                     "research/gmi-833-aa1-gap-graph-v1/").split("\n") if f.strip()]
        self.assertIn("research/gmi-833-aa1-gap-graph-v1/FREEZE_V1.md", files)
        if len(files) > 1:
            self.assertIn("FREEZE_V1.md", " ".join(files))  # squash publication: freeze in the publishing commit
        frozen = self.git("show", first + ":research/gmi-833-aa1-gap-graph-v1/FREEZE_V1.md")
        with open(os.path.join(PKG_DIR, "FREEZE_V1.md"), "r", encoding="utf-8") as fh:
            self.assertEqual(fh.read(), frozen)


if __name__ == "__main__":
    unittest.main(verbosity=1)
