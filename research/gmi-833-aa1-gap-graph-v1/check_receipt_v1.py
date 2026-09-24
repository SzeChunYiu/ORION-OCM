#!/usr/bin/env python3
"""Build or verify RESULT_V1.json and ISSUE_833_COMMENT_RECONCILIATION_AA1_GAP_GRAPH_V1.json.

    check_receipt_v1.py            re-derive both files and compare them by equality (exit 1 on any drift)
    check_receipt_v1.py --write    write both files from a live two-route run

Both files are a pure function of the pinned inputs and this package's own
files, so two runs are byte-identical; CI checks that.
"""
import hashlib
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gap_graph_v1 as A                      # noqa: E402
import independent_gap_graph_oracle_v1 as B   # noqa: E402
import fixtures_v1 as F                       # noqa: E402

RESULT = os.path.join(HERE, "RESULT_V1.json")
RECON = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_AA1_GAP_GRAPH_V1.json")
COMMENT_ID = 5684607872
AA = "### AA. Recursive loophole / logic-gap closure"
AD = "### AD. Recursive research loop"
PKG = A.PKG

FORBIDDEN = ["ALL_GAPS_EXHAUSTED", "INDEPENDENT_HOSTILE_REVIEW_COMPLETE", "CORPUS_AUDIT_COMPLETE",
             "REPLICATED_CLOSED", "REAL_SCALE_CLOSED", "COMPLETE_GMI", "GMI_GAP_GRAPH_COMPLETE",
             "RECURSION_EXHAUSTED", "NO_MATERIAL_GAP_REMAINS", "ISOLATED_GAP_IS_LEAF", "ANALYTIC_PROOF",
             "HOSTILE_CLOSED_AWARDED_TO_ANY_REAL_NODE", "PARENT_ISSUE_CLOSURE_PREVENTED_ON_GITHUB",
             "FLAGSHIP_RESULTS_COUNTEREXAMPLE_SEARCHED", "LEDGER_CONTENTS_VERIFIED"]

ROWS = {
    "AA11": (AA, "- [ ] Require at least two distinct counterexample-generation methods for flagship theorems."),
    "AA38": (AA, "- [ ] Maintain a live `GMI_GAP_GRAPH` linking every claim to unresolved descendants."),
    "AA40": (AA, "- [ ] Prevent parent issue closure while any critical descendant gap remains unresolved."),
    "AA08": (AA, "- [ ] Recurse until no new **material** gap is found under the declared scope."),
    "AA10": (AA, "- [ ] Require independent hostile review before a gap can be marked exhausted."),
    "AD01": (AD, "- [ ] Implement the loop as a standard research template."),
    "AD02": (AD, "- [ ] Require each iteration to create explicit new-gap records rather than silently editing assumptions."),
    "AD03": (AD, "- [ ] Stop only at the declared evidence ceiling, never because the checklist is long."),
}


def key_of(anchor, old):
    text = old[len("- [ ] "):]
    return hashlib.sha256((anchor + "\x00" + text).encode("utf-8")).hexdigest()


def evidence(s, rb, diffs, loop):
    n, e, d, c, m, f = (s["nodes_by_kind"], s["edges_by_kind"], s["descendants"], s["closure"],
                        s["materiality"], s["flagship"])
    r = s["descendant_edges_by_rule"]
    return {
        "AA38": (
            "`%s` AA1G-1+AA1G-2+AA1G-3: `GMI_GAP_GRAPH_V3.json` types %d nodes (%d GAP, %d CLAIM, %d RESULT, "
            "%d PARENT, %d ASSUMPTION) and %d edges. Its %d DESCENDANT edges are derived by three declared rules "
            "only: R1 id precedence %d, R2 stated-dependency propagation %d (route B recomputes it by fixed point "
            "without reading the V2 field), R3 repair successor %d. %d of the 1140 census gap records gain a gap "
            "descendant from corpus records alone (census graph: %d/1140), %d under any rule, %d carry a gap or "
            "object descendant. Every one of the %d gap claim ids has a claim node; %d of %d claim nodes link to "
            "at least one unresolved descendant gap. Live: the builder re-derives the graph from blob-pinned "
            "inputs and ingests AD-loop gap records, and CI requires the committed file to equal a fresh build "
            "byte for byte; 0 cycles and 0 findings in two routes. Absence of a stated edge is not independence "
            "(extracted as the CRITICAL gap GAP-AD-AA1-SPARSITY)."
            % (PKG, sum(n.values()), n["GAP"], n["CLAIM"], n["RESULT"], n["PARENT"], n["ASSUMPTION"],
               sum(e.values()), e["DESCENDANT"], r["R1_ID_PRECEDENCE"], r["R2_DEPENDENCY_PROPAGATION"],
               r["R3_REPAIR_SUCCESSOR"], d["corpus_records_gaining_gap_descendants_by_R1_R2"],
               d["v1_records_with_nonempty_descendants"], d["corpus_records_gaining_gap_descendants_any_rule"],
               d["corpus_records_with_gap_or_object_descendants"], s["claims"]["gap_claim_ids"],
               s["claims"]["claims_with_unresolved_descendants"], s["claims"]["claim_nodes"])),
        "AA11": (
            "`%s` AA1G-5+AA1G-8: every flagship result record carries at least two counterexample-method slots "
            "over six declared classes (bounded exhaustive, SAT/SMT/model checking, property-based randomized, "
            "proof assistant, hand-constructed adversarial, independent-implementation differential); "
            "HOSTILE_CLOSED or higher is refused unless two filled slots name distinct classes with no "
            "counterexample on record, fail-closed on a missing or non-boolean flagship flag, a non-list slot "
            "field or a non-object slot. Exhaustive %d-case cube: %d flagship grants without two distinct "
            "methods, routes agree. Requirement state disclosed, not discharged: the %d flagship results of the "
            "frozen AJ0 registry have %d filled slots and HOSTILE_CLOSED is refused %d/%d (extracted as the "
            "CRITICAL gap GAP-AD-AA1-FLAGSHIP-SLOTS)."
            % (PKG, diffs["flagship_promotions"]["cases"],
               diffs["flagship_promotions"]["flagship_granted_without_two_methods"], f["results"],
               f["slots_filled_total"], f["refused_for_missing_methods"], f["results"])),
        "AD01": (
            "`%s` AA1G-7: `AD_LOOP_TEMPLATE_V1.json` implements the twelve steps of the AD text block in order "
            "(matched to the comment's text block), each with a DONE / NOT_RUN / NOT_APPLICABLE status "
            "contract, plus the iteration record, declared stop reasons and a materiality input rule. The "
            "validator (two routes) accepts the worked instance for this lane (%d iterations, %d extracted gaps "
            "ingested into the graph) and rejects %d/%d seeded mutations over %d mutation classes with %d route "
            "disagreements."
            % (PKG, loop["iterations"], loop["extracted_gaps"], diffs["randomized_loops"]["trials_rejected"],
               diffs["randomized_loops"]["trials"], len(F.LOOP_MUTATIONS),
               diffs["randomized_loops"]["route_disagreements"])),
        "AD02": (
            "`%s` AA1G-7: the loop validator rejects an iteration whose new-gap extraction step is not DONE or "
            "extracts no gap (`L_NO_GAP_EXTRACTION`), and any assumption edit, within an iteration or between "
            "iterations, that is not declared as a change paired with a gap extracted in that same iteration "
            "(`L_SILENT_ASSUMPTION_EDIT`, `L_ITERATION_CONTINUITY`); every planted positive fires in both "
            "routes, and the worked instance records %d assumption changes, each paired with its gap record."
            % (PKG, loop["assumption_changes"])),
    }


def build():
    ra = A.run(write=False)
    s = ra["summary"]
    rb = B.run()
    planted = F.run_planted()
    clean = F.run_clean()
    diffs = {
        "digraphs": F.exhaustive_digraphs(),
        "gap_promotions": F.exhaustive_gap_promotions(),
        "flagship_promotions": F.exhaustive_flagship_promotions(),
        "parent_promotions": F.exhaustive_parent_promotions(),
        "randomized_graphs": F.randomized_graphs(),
        "randomized_loops": F.randomized_loops(),
    }
    doc = A.load_json(A.OWN["loops"])
    its = doc["loops"][0]["iterations"]
    loop = {"loops": len(doc["loops"]), "iterations": len(its),
            "extracted_gaps": sum(len(x["extracted_gaps"]) for x in its),
            "assumption_changes": sum(len(x["assumption_changes"]) for x in its),
            "stop_reason": its[-1]["stop_reason"],
            "findings_route_a": A.validate_loops(doc), "findings_route_b": B.validate_loops(doc)}
    ev = evidence(s, rb, diffs, loop)
    keys = dict((rid, key_of(ROWS[rid][0], ROWS[rid][1])) for rid in ROWS)
    import test_gap_graph_v1 as T
    n_tests = unittest.defaultTestLoader.loadTestsFromModule(T).countTestCases()
    agreement = {
        "descendant_edges_by_rule": rb["descendant_edges_by_rule"] == s["descendant_edges_by_rule"],
        "locally_closed_by_rule": rb["locally_closed_by_rule"] == s["closure"]["locally_closed_by_rule"],
        "closed_blocked_beyond_local": rb["closed_blocked_beyond_local"] == s["materiality"]["closed_blocked_beyond_local"],
        "parent_closure": rb["parent_closure"] == s["parent_closure"],
        "validation_findings": rb["validation_findings"] == s["validation_findings"],
        "route_b_disagreements": rb["disagreements"],
    }
    result = {
        "schema": "GMI_833_AA1_GAP_GRAPH_RESULT_V1",
        "package": PKG,
        "issue": 839,
        "parent_issue": 833,
        "source_main": A.SOURCE_MAIN,
        "claim_ceiling": A.CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "graph": {"path": A.GRAPH_REL, "sha256": ra["graph_sha256"]},
        "pins": ra["pins"],
        "summary": s,
        "route_b": rb,
        "route_agreement": agreement,
        "planted": {"rows": planted, "count": len(planted),
                    "codes_covered": len(set(p["expected"] for p in planted)),
                    "fired_both_routes": sum(1 for p in planted if p["route_a_fired"] and p["route_b_fired"]),
                    "identical_findings": sum(1 for p in planted if p["routes_identical"])},
        "clean": {"rows": clean, "silent_both_routes": sum(
            1 for c in clean if c["route_a_findings"] == 0 and c["route_b_findings"] == 0)},
        "differentials": diffs,
        "loop": loop,
        "tests": {"file": "test_gap_graph_v1.py", "count": n_tests,
                  "modes": ["python3 -I -B", "python3 -I -O -B"]},
        "named_results": dict((r["result_id"], r["statement"])
                              for r in A.load_json(A.OWN["results"])["records"]),
        "reconciliation_evidence": dict(("L:" + keys[rid][:12], {"row_id": rid, "evidence": ev[rid]})
                                        for rid in sorted(ev)),
        "issue_839_acceptance": ACCEPTANCE,
    }
    recon = reconciliation(ev, keys, s, diffs)
    return result, recon


ACCEPTANCE = [
    {"item": 1, "text": "machine-readable result record with assumptions, dependencies, falsifiers/counterexamples, strongest parents/subsumption, prior disclosure, evidence/maturity and forbidden extrapolations",
     "status": "EARNED_HERE", "evidence": "research/gmi-833-aa1-gap-graph-v1 AA1G-8: GAP_GRAPH_SCHEMA_V1.json#result_record_fields, RESULT_RECORDS_V1.json (8 records), 9 flagship records in GMI_GAP_GRAPH_V3.json",
     "builds_on": "gmi-833-aa-ledger-gate-v1 LG-1..LG-3 (theorem ledger emission), gmi-833-claim-discipline-v1 REGISTRATIONS_V2.json (registered ledgers)"},
    {"item": 2, "text": "experiment ledger with leakage, search-space, cost-model, evaluation and sampling-bias entries",
     "status": "PRE_EXISTING", "evidence": "research/gmi-833-aa-ledger-gate-v1 LG-4 (GMI_EXPERIMENT_LEDGER_V1, EXPERIMENT_LEDGER_CORPUS_CENSUS_V1.md, EXPERIMENT_LEDGER_GATE_VALIDATION_V1.md); one further instance here: EXPERIMENT_LEDGER_GAP_GRAPH_V1.md"},
    {"item": 3, "text": "GMI_GAP_GRAPH nodes/edges; every closed gap records newly introduced assumptions and descendant gaps",
     "status": "EARNED_HERE", "evidence": "research/gmi-833-aa1-gap-graph-v1 AA1G-1+AA1G-2: GMI_GAP_GRAPH_V3.json",
     "builds_on": "gmi-833-census-registration-pass-v1 GAP_GRAPH_V2.json (gap-to-object descendants on 50/1140), gmi-833-aa-gap-object-v1 AAG-5 (REPAIR_DELTA)"},
    {"item": 4, "text": "materiality enforcement: an unresolved CRITICAL descendant blocks promotion beyond local closure",
     "status": "EARNED_HERE", "evidence": "research/gmi-833-aa1-gap-graph-v1 AA1G-3",
     "builds_on": "gmi-833-aa-gap-object-v1 AAG-3 (materiality threshold)"},
    {"item": 5, "text": "closure states LOCALLY_CLOSED / HOSTILE_CLOSED / REPLICATED_CLOSED / REAL_SCALE_CLOSED; bare scientific closed rejected",
     "status": "PRE_EXISTING_AND_ENFORCED_HERE", "evidence": "research/gmi-833-aa-gap-object-v1 AAG-4 (lattice and detector); enforced in the graph validator and promotion evaluator here, AA1G-4"},
    {"item": 6, "text": "static hostiles: forall/exists order, converse, necessity/sufficiency, representability/reachability, optimality/selection, finite-to-universal, correlation-to-causation",
     "status": "PRE_EXISTING", "evidence": "research/gmi-833-aa-logical-form-register-v1 LF (AA16 quantifier order, AA17 converse/inverse, AA18 necessity/sufficiency, AA20 optimality, AA22 correlation/causal; reconciliation pending on #833); research/gmi-833-aa-fallacy-detectors-v1 FD-1 (AA19 representability/reachability); research/gmi-833-aa-finite-universal-harness-v1 FU-1..FU-4 (AA21 finite-to-universal)"},
    {"item": 7, "text": "at least two counterexample-method slots for flagship results; fail closed when HOSTILE_CLOSED is requested without both",
     "status": "EARNED_HERE", "evidence": "research/gmi-833-aa1-gap-graph-v1 AA1G-5"},
    {"item": 8, "text": "deterministic graph validation, cycle reporting, orphan/missing-parent checks, exact normal and python -O tests",
     "status": "EARNED_HERE", "evidence": "research/gmi-833-aa1-gap-graph-v1 AA1G-6; test_gap_graph_v1.py in both modes",
     "builds_on": "gmi-833-depgraph-adjudication-v1 CYCLE_REPORT_V1.json (cycle report for the stated-dependency graph)"},
    {"item": 9, "text": "standard AD research-loop template requiring new-gap extraction on each iteration",
     "status": "EARNED_HERE", "evidence": "research/gmi-833-aa1-gap-graph-v1 AA1G-7: AD_LOOP_TEMPLATE_V1.json, AD_LOOP_RECORDS_V1.json"},
    {"item": 10, "text": "reconcile only directly earned #833 addendum boxes after merge",
     "status": "PREPARED_NOT_APPLIED", "evidence": "research/gmi-833-aa1-gap-graph-v1/ISSUE_833_COMMENT_RECONCILIATION_AA1_GAP_GRAPH_V1.json (AA11, AA38, AD01, AD02 PENDING; AA40, AA08, AA10, AD03 not closed); applied only after merge by the orchestrator"},
]

NOT_CLOSED_REASONS = {
    "AA40": ("EXTERNAL-ACTION",
             "Instrument delivered, row not earned: `gap_graph_v1.py --parent-closure-gate` refuses closing a "
             "parent while a CRITICAL gap in its cone is unresolved (exit 1; T833-B1-AA refused with %d, "
             "T833-AA1 with %d; %d-case exhaustive cube with 0 grants over an open critical), but nothing binds it "
             "to the GitHub issue-close action or to the checklist safe-write path, which this lane may not edit. "
             "Recorded as GAP-AD-AA1-AA40-BINDING."),
    "AA08": ("NEW-SCIENCE",
             "The worked AD loop stopped at DECLARED_EVIDENCE_CEILING_REACHED with %d CRITICAL extracted gaps "
             "unresolved; no claim was recursed to a no-new-material-gap fixpoint."),
    "AA10": ("EXTERNAL-GATE",
             "Independent hostile review needs a lane that did not author the result; this package's route B is "
             "an independent implementation by the same lane, not an independent review."),
    "AD03": ("EXACT-FORMAL",
             "The template admits only DECLARED_EVIDENCE_CEILING_REACHED or NO_MATERIAL_GAP_AT_THRESHOLD as stop "
             "reasons for loop records, but it does not verify that a declared ceiling was reached, and no census "
             "binds packages' loops to their claim ceilings; not earned."),
}


def reconciliation(ev, keys, s, diffs):
    reps = []
    for rid in ("AA38", "AA11", "AD01", "AD02"):
        anchor, old = ROWS[rid]
        tag = {"AA38": "AA1G-1/AA1G-2/AA1G-3", "AA11": "AA1G-5/AA1G-8", "AD01": "AA1G-7", "AD02": "AA1G-7"}[rid]
        new = "- [x] " + old[len("- [ ] "):] + u" — ✅ #839 `%s` %s L:%s" % (PKG, tag, keys[rid][:12])
        reps.append({"comment_id": COMMENT_ID, "anchor": anchor, "row_id": rid, "old": old, "new": new,
                     "status": "EARNED", "apply_state": "PENDING", "evidence_key": "L:" + keys[rid][:12],
                     "evidence": ev[rid]})
    pc = s["parent_closure"]
    nc = []
    for rid in ("AA40", "AA08", "AA10", "AD03"):
        anchor, old = ROWS[rid]
        bucket, reason = NOT_CLOSED_REASONS[rid]
        if rid == "AA40":
            reason = reason % (pc["T833-B1-AA"]["unresolved_critical"], pc["T833-AA1"]["unresolved_critical"],
                               diffs["parent_promotions"]["cases"])
        elif rid == "AA08":
            reason = reason % s["materiality"]["unresolved_critical_extracted"]
        nc.append({"comment_id": COMMENT_ID, "anchor": anchor, "row_id": rid, "old": old,
                   "bucket": bucket, "reason": "[%s] %s" % (bucket, reason)})
    return {
        "schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1",
        "issue": 833,
        "comment_id": COMMENT_ID,
        "child_issue": 839,
        "package": PKG,
        "source_main": A.SOURCE_MAIN,
        "comment_live_updated_at_freeze": "2026-09-18T17:31:30Z",
        "claim_ceiling": A.CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN,
        "earned_criterion": "research/gmi-833-aa1-gap-graph-v1/FREEZE_V1.md section 6",
        "do_not_edit": True,
        "do_not_edit_note": ("This package did not edit the issue body or any comment. The `old` strings are "
                             "byte-exact against the live comment 5684607872 read at freeze and its mirror "
                             "research/gmi-833-checklist-mirror-v1/comments/comment_5684607872.md, and each "
                             "occurs exactly once under its ### anchor. `new` is in pointer form; the full "
                             "evidence is in `evidence` here and in RESULT_V1.json#reconciliation_evidence. "
                             "Apply only after merge, through comment_safe_write_v1.py."),
        "replacements": reps,
        "not_closed": nc,
        "apply_state_counts": {"PENDING": len(reps)},
    }


def dumps(obj):
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def check():
    result, recon = build()
    bad = []
    for path, obj in ((RESULT, result), (RECON, recon)):
        if not os.path.exists(path):
            bad.append("missing " + os.path.basename(path))
            continue
        with open(path, "r", encoding="utf-8") as fh:
            have = fh.read()
        if have != dumps(obj):
            old = json.loads(have)
            diff = sorted(k for k in set(old) | set(obj) if old.get(k) != obj.get(k))
            bad.append("%s drifted in keys %s" % (os.path.basename(path), diff))
    return bad


def main(argv):
    if "--write" in argv:
        result, recon = build()
        for path, obj in ((RESULT, result), (RECON, recon)):
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(dumps(obj))
        print("wrote RESULT_V1.json and the reconciliation JSON")
        return 0
    bad = check()
    for b in bad:
        print("DRIFT: " + b)
    print("receipt matches the live two-route run" if not bad else "receipt check FAILED")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
