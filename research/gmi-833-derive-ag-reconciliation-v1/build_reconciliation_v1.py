# -*- coding: utf-8 -*-
"""Build and audit the AG/AH comment reconciliation for the derive-ag tranche.

Three things happen here and all three are checked, not assumed:

  1. every `old` line is taken from a LIVE fetch of the comment body made
     immediately before the file is written, and is proved to occur exactly once
     inside its own `###` section as well as exactly once in the whole body;
  2. every `old` line is additionally compared against the pinned
     `AGAH_ROWS_V1.json` custody snapshot, so a row edited by another lane since
     the pin would be caught rather than silently reconciled;
  3. the RA-1 citation admissibility auditor built by the earlier AG lane is
     REUSED, not reimplemented, to refuse any citation whose row meaning appears
     in the cited receipt's own forbidden set.

    python3 -I -B build_reconciliation_v1.py <live_ag.txt> <live_ah.txt>
"""

import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MAP = os.path.join(REPO, "research", "gmi-833-agah-map-v1")
SOURCE_MAIN = "50f833cc4bc3cadcefd44eca14fa58f73f815587"


def load_auditor():
    spec = importlib.util.spec_from_file_location(
        "gmi_ra1", os.path.join(MAP, "citation_audit_v1.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RA1 = load_auditor()


def cite(pkg, fields):
    path = "research/%s/RESULT_V1.json" % pkg
    full = os.path.join(REPO, path)
    doc = json.load(open(full))
    out = {}
    for f in fields:
        cur = doc
        for seg in f.split("."):
            cur = cur[int(seg)] if isinstance(cur, list) else cur[seg]
        out[f] = json.dumps(cur, sort_keys=True)
    return {"package": pkg, "receipt_path": path, "blob_sha": RA1.blob_sha(full),
            "fields": out}


ENTRIES = [
    {"row_index": 14, "comment_id": 5693520829, "bucket": "EXACT-FORMAL",
     "status": "EARNED",
     "row_meaning_token": "PRESENTATION_EQUIVALENCE_STRENGTHS_DEFINED_AND_ORDERED",
     "evidence": (
         "`gmi-833-ag3-presentation-equivalence-v1` AG3L-1…AG3L-5: over a registered "
         "universe of 2,548 presentations and 1,621,802 comparable pairs the four named "
         "strengths relate 1,762 / 29,470 / 297,166 / 297,358 pairs and are **not a "
         "chain** — definitional/term equivalence and compiler equivalence at overhead 1 "
         "are incomparable, certified by a separating pair in each direction, so the "
         "generated sublattice has 5 elements with one new meet; k* = 2 is the least "
         "overhead at which term equivalence sits inside compiler equivalence, the ladder "
         "saturates at k = 2 so the parent's 5t factor is not strict here and that "
         "strictness claim is withdrawn; the compiler clause read alone relates 367,372 "
         "pairs presenting different objects, so the level published in the order is that "
         "clause intersected with model equivalence — the freeze contains two clauses that "
         "cannot both hold, its section 1 governs, and its section 6 instruction to "
         "withdraw rather than repair was deliberately not followed, the whole decision "
         "recorded in the receipt as frozen-clause conflict AG3-FC-1 with the measured "
         "evidence and a two-state counterexample; fixed overhead is a tolerance rather "
         "than an equivalence with an explicit non-transitive triple at k = 1, and the one named "
         "strength with no merged witness — definitional/term equivalence — is constructed "
         "here and placed at its exact level; 2 routes 0 disagreements, 6 hostiles "
         "detected, 0/200 on both nulls."),
     "citations": [
         ("gmi-833-ag3-presentation-equivalence-v1",
          ["status", "universe_size", "comparable_pairs", "k_star_l2_inside_l3",
           "generated_sublattice_size", "l3_raw_clause_cross_object_pairs",
           "level_related_pairs"]),
         ("gmi-833-aj5-g0-lowering-v1", ["status", "dynamic_time_bound"]),
         ("gmi-833-g0-grammar-bias-v1", ["claim_ceiling"]),
     ]},
    {"row_index": 19, "comment_id": 5693520829, "bucket": "NEW-SCIENCE",
     "status": "EARNED",
     "row_meaning_token": ("AG4_EXACT_TRANSLATIONS_AMONG_THE_APPLICABLE_FINITE_"
                           "SPECIALIZATIONS_CONSTRUCTED"),
     "evidence": (
         "`gmi-833-ag4-formalism-translations-v1` AG4T-1…AG4T-4: all 30 directed "
         "translations among the six families are adjudicated over 8,032 registered "
         "objects — 16 TOTAL over the source's whole range, 14 PARTIAL with an exact "
         "domain (274/1,024, 542/1,412, 478/1,348 and 3,728/4,160), 0 EMPTY — giving 4 "
         "mutually total pairs, 8 total in one direction only and 3 partial in both; every "
         "partial verdict carries a named obstruction from a vocabulary of 8 fixed before "
         "any run plus a witness proved untranslatable by exhaustive search over the whole "
         "target range, while the two differences that are not barriers are measured as "
         "fibres instead (324 kernels over 102 supports, largest fibre 90; translations out "
         "of the category family total but non-canonical with fibre sizes 1, 4, 6, 13); the "
         "anti-flattening control cuts the same universe to 516 objects and makes all 15 "
         "pairs mutually total, which is what a universe designed to succeed looks like; 2 "
         "routes 0 disagreements, 6 hostiles detected, 0/200 null."),
     "citations": [
         ("gmi-833-ag4-formalism-translations-v1",
          ["status", "registered_objects_total", "directed_verdict_histogram",
           "pair_verdict_histogram", "mutually_total_pairs", "obstruction_histogram"]),
         ("gmi-833-aj1-operational-process-base-v1", ["claim_ceiling"]),
         ("gmi-833-aj5-g0-lowering-v1", ["status"]),
     ]},
    {"row_index": 41, "comment_id": 5693520829, "bucket": "NEW-SCIENCE",
     "status": "EARNED_BY_COUNTEREXAMPLE",
     "row_meaning_token": "AG7_CANDIDATE_BOUNDARIES_TESTED",
     "evidence": (
         "`gmi-833-emergence-conditions-v1` EC-1…EM-7: all six named boundaries are tested "
         "as extensional predicates on the observable trace — 0 of the trace groups split, "
         "so no predicate reads the program — over an exhaustive enumeration of 813,615 "
         "programs of a substrate whose 15 operations contain no behaviour word; "
         "metareasoning and endogenous experiment choice, the two with no coverage anywhere "
         "in the merged corpus, are FORCED in 132/132 and 1,648/1,648 conforming programs "
         "with 0 predicate-free blind covers, adaptation likewise in 882/882 and routing "
         "in 154/154 — and all four survive the requirement-entails-predicate control at "
         "0 of 4 entailed, the one extra requirement clause among them (experiment choice) "
         "measured inert at 1,648 conforming programs either way, against 5 of the 13 "
         "frozen requirements that do entail their own predicate — "
         "history-sensitive development is forced only by a requirement clause that when "
         "stripped flips it to DOES_NOT_EMERGE at margin −1, reusable-operator acquisition "
         "is DOES_NOT_EMERGE at margin −2, and capability-frontier expansion is "
         "NOT_EXPRESSIBLE with 0 of 882 conforming programs growing their coverage even "
         "against a probe set larger than the family; EMERGES_BY_PRICE occurs 0 times "
         "across all thirteen families, both accountings and the whole observation-price "
         "sweep, so the flat-pricing control has nothing to act on and is published as "
         "vacuous rather than counted; 2 routes 0 disagreements, 5 hostiles detected, "
         "0/200 on both nulls."),
     "citations": [
         ("gmi-833-emergence-conditions-v1",
          ["status", "emerges_by_price", "ec3_exercised", "verdict_histogram",
           "not_expressible"]),
         ("gmi-833-aj8-intelligence-boundary-v1", ["claim_ceiling"]),
     ]},
    {"row_index": 62, "comment_id": 5693590252, "bucket": "NEW-SCIENCE",
     "status": "EARNED_BY_COUNTEREXAMPLE",
     "row_meaning_token": ("AH3_ATOM_SUPPORTED_EMERGENCE_TESTED_WITHOUT_PRIMITIVE_MACROS"),
     "evidence": (
         "`gmi-833-emergence-conditions-v1` EC-1…EM-7: all seven named mechanisms are "
         "tested as extensional predicates on the observable trace, with 0 trace groups "
         "split so none of them can be satisfied by naming an operation, over an exhaustive "
         "enumeration of 813,615 programs; the base substrate supports memory, routing, "
         "symbolic rewriting and learning laws — routing FORCED in all 154 conforming "
         "programs, symbolic rewriting expressible but 1 unit dearer than avoiding it — and "
         "does not support search, probabilistic state or self-modification, each "
         "NOT_EXPRESSIBLE with a named obstruction proved by the enumeration (0 conforming "
         "programs for probabilistic state and self-modification, 0 of 14,478 exhibiting "
         "search), of which two are recovered on the declared one-operation extensions at "
         "35 and 311 conforming programs, both FORCED, and the third becomes expressible at "
         "cost 7 once the instance is three symbols long; 2 routes 0 disagreements, 5 "
         "hostiles detected, 0/200 on both nulls."),
     "citations": [
         ("gmi-833-emergence-conditions-v1",
          ["status", "not_expressible", "verdict_histogram", "emerges_by_price"]),
         ("gmi-833-aj6-aj8-development-value-intelligence-v1", ["claim_ceiling"]),
     ]},
]

NOT_CLOSED = [
    {"comment_id": 5693520829, "row_index": 1, "bucket": "NEW-SCIENCE",
     "reason": ("AG0 residual. This tranche's three freezes each state that no neighbouring "
                "row is earned, so none of them may reach it. The row needs a system whose "
                "EXTERNAL description uses a grammar while its MECHANISM contains no grammar "
                "object, together with a no-reification detector validated in both "
                "directions. gmi-833-emergence-conditions-v1's substrate is a candidate "
                "carrier for that construction but its freeze forbids claiming the row, so "
                "it is left open rather than reached by a package that promised not to. "
                "Next tranche: gmi-833-ag0-no-internal-grammar-v1.")},
]


def section_of(body, anchor):
    lines = body.split("\n")
    if anchor not in lines:
        return None
    i = lines.index(anchor)
    j = len(lines)
    for k in range(i + 1, len(lines)):
        if lines[k].startswith("### "):
            j = k
            break
    return "\n".join(lines[i:j])


def main(argv):
    live = {5693520829: io.open(argv[0], encoding="utf-8").read(),
            5693590252: io.open(argv[1], encoding="utf-8").read()}
    pinned = json.load(open(os.path.join(MAP, "AGAH_ROWS_V1.json")))

    reps, checks = [], []
    for e in ENTRIES:
        pin = pinned[e["row_index"]]
        body = live[e["comment_id"]]
        sec = section_of(body, pin["anchor"])
        old = pin["row"]
        chk = {"row_index": e["row_index"], "anchor": pin["anchor"],
               "anchor_present_live": sec is not None,
               "occurrences_in_body": body.count(old),
               "occurrences_in_section": sec.count(old) if sec else 0,
               "live_matches_pinned_custody_snapshot": old in body,
               "still_unchecked_live": ("- [x] " + old[len("- [ ] "):]) not in body}
        checks.append(chk)
        reps.append({
            "comment_id": e["comment_id"], "row_index": e["row_index"],
            "anchor": pin["anchor"], "old": old,
            "new": "- [x] " + old[len("- [ ] "):] + " — ✅ " + e["evidence"],
            "bucket": e["bucket"], "status": e["status"],
            "row_meaning_token": e["row_meaning_token"],
            "citations": [cite(p, f) for p, f in e["citations"]]})

    table = {"replacements": reps}
    violations = RA1.audit(table, pinned, REPO)

    ok = (all(c["anchor_present_live"] and c["occurrences_in_body"] == 1 and
              c["occurrences_in_section"] == 1 and
              c["live_matches_pinned_custody_snapshot"] and c["still_unchecked_live"]
              for c in checks)
          and all(v == 0 for v in violations.values()))

    audit = {"schema": "GMI_833_RECONCILIATION_AUDIT_V1", "issue": 833,
             "source_main": SOURCE_MAIN,
             "live_fetch_checks": checks,
             "ra1_violations": violations,
             "ra1_note": ("RA-1 is the committed auditor of gmi-833-agah-map-v1, imported "
                          "rather than reimplemented. It refuses a citation whose row "
                          "meaning appears in the cited receipt's own forbidden set."),
             "status": "GREEN" if ok else "RED"}
    with open(os.path.join(HERE, "RECONCILIATION_AUDIT_V1.json"), "w") as fh:
        json.dump(audit, fh, indent=1, sort_keys=True)
        fh.write("\n")

    doc = {"schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1", "issue": 833,
           "source_main": SOURCE_MAIN,
           "packages": ["gmi-833-ag3-presentation-equivalence-v1",
                        "gmi-833-emergence-conditions-v1",
                        "gmi-833-ag4-formalism-translations-v1"],
           "audited_by": ("gmi-833-derive-ag-reconciliation-v1: every `old` taken from a "
                          "live comment fetch and proved to occur exactly once inside its "
                          "own section, cross-checked against the pinned custody snapshot, "
                          "and every citation run through the committed RA-1 auditor"),
           "do_not_edit_note": ("The orchestrator performs every issue write. This file is "
                                "a proposal; no comment and no issue body was edited by the "
                                "lane that produced it."),
           "replacements": reps, "not_closed": NOT_CLOSED}
    with open(os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json"), "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps({"status": audit["status"], "replacements": len(reps),
                      "not_closed": len(NOT_CLOSED), "ra1_violations": violations,
                      "live_checks": checks}, sort_keys=True, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
