# -*- coding: utf-8 -*-
"""AJ9 hostiles, controls and the no-alarm case for the holdout blind-source audit.

No gate depends on a bare `assert`; the file behaves identically under `-O`.

    python3 -I -O -B  test_aj9_holdout_source_audit_v1.py
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import aj9_holdout_source_audit_v1 as A   # noqa: E402

FINDINGS = []
HOSTILES = []
VOCAB = A.build_vocabulary()


def hostile(name, detected, control_clean, detail):
    HOSTILES.append({"hostile": name, "detected": bool(detected),
                     "control_clean": bool(control_clean), "detail": detail})
    if not detected:
        FINDINGS.append("HOSTILE_NOT_DETECTED:" + name)
    if not control_clean:
        FINDINGS.append("CONTROL_NOT_CLEAN:" + name)


def real_blind_source():
    p = os.path.join(A.RESEARCH, "gmi-833-aj9b-k01-blind-recovery-v1", "blind_search_v1.py")
    return open(p, "rb").read().decode("utf-8", "replace")


BASE = real_blind_source()


def plant(line):
    v, _r, _e = A.scan_text("blind_search_v1.py", BASE + "\n" + line + "\n", VOCAB)
    clean_v, _cr, _ce = A.scan_text("blind_search_v1.py", BASE, VOCAB)
    return len(v), len(clean_v)


def h_plant(name, line):
    got, clean = plant(line)
    hostile(name, got > 0, clean == 0, {"planted_violations": got, "clean_violations": clean})


def h_boundary_regex_word_only():
    """The defect the planted-positive test caught: `\\b` does not separate on `_`."""
    line = "def attention_macro(x): return x"
    weak = len(re.findall(r"\battention\b", line))
    strong = len(re.findall(r"(?<![a-z0-9])attention(?![a-z0-9])", line))
    got, clean = plant(line)
    hostile("boundary_regex_word_only", weak == 0 and strong == 1 and got > 0, clean == 0,
            {"word_boundary_hits": weak, "alphabetic_boundary_hits": strong,
             "auditor_violations": got})


def h_exemption_too_wide():
    """A scanner that treats every line as a declaration sees nothing."""
    saved = A.declaration_spans
    try:
        A.declaration_spans = lambda name, text: set(range(1, len(text.split("\n")) + 2))
        v, _r, _e = A.scan_text("blind_search_v1.py", BASE + "\nTARGET_FAMILY = 'K01'\n", VOCAB)
        wide = len(v)
    finally:
        A.declaration_spans = saved
    v2, _r2, _e2 = A.scan_text("blind_search_v1.py", BASE + "\nTARGET_FAMILY = 'K01'\n", VOCAB)
    hostile("exemption_too_wide", wide == 0 and len(v2) > 0, len(v2) > 0,
            {"with_wide_exemption": wide, "with_real_exemption": len(v2)})


def h_blind_file_rule_too_narrow():
    narrow = [n for n in ("blind_search_v1.py", "SEARCH_CONFIG_V1.json",
                          "BLIND_OUTCOME_V1.json") if n.startswith("blind_")]
    full = [n for n in ("blind_search_v1.py", "SEARCH_CONFIG_V1.json",
                        "BLIND_OUTCOME_V1.json") if A.is_blind(n)]
    hostile("blind_file_rule_too_narrow", len(narrow) < len(full), len(full) == 3,
            {"narrow_rule_matches": len(narrow), "registered_rule_matches": len(full)})


def h_vocabulary_not_derived():
    hand = {"family_ids": ["K01"], "paper_names": [], "multiword_names": [],
            "name_tokens": [], "fingerprint_clauses": [], "exclusion_clauses": [],
            "observation_clauses": [], "parent_anchors": []}
    missed = 0
    for _name, line in (("a", "MODE = 'neural/feed-forward'"),
                        ("b", "# after " + VOCAB["parent_anchors"][0]),
                        ("c", "# require " + VOCAB["fingerprint_clauses"][0][:60])):
        v, _r, _e = A.scan_text("blind_x.py", line + "\n", hand)
        if not v:
            missed += 1
    full = 0
    for _name, line in (("a", "MODE = 'neural/feed-forward'"),
                        ("b", "# after " + VOCAB["parent_anchors"][0]),
                        ("c", "# require " + VOCAB["fingerprint_clauses"][0][:60])):
        v, _r, _e = A.scan_text("blind_x.py", line + "\n", VOCAB)
        if v:
            full += 1
    hostile("vocabulary_not_derived", missed > 0, full == 3,
            {"hand_vocabulary_misses": missed, "derived_vocabulary_detects": full})


def h_posthoc_treated_as_blind():
    p = os.path.join(A.RESEARCH, "gmi-833-aj9b-k01-blind-recovery-v1",
                     "posthoc_adjudicate_v1.py")
    text = open(p, "rb").read().decode("utf-8", "replace")
    v, _r, _e = A.scan_text("posthoc_adjudicate_v1.py", text, VOCAB)
    vb, _rb, _eb = A.scan_text("blind_search_v1.py", BASE, VOCAB)
    hostile("posthoc_treated_as_blind", len(v) > 0, len(vb) == 0,
            {"posthoc_family_hits": len(v), "blind_violations": len(vb)})


def h_benchmark_blob_drift():
    saved = A.BENCHMARK_BLOB
    try:
        A.BENCHMARK_BLOB = "0" * 40
        v = A.build_vocabulary()
        drift = not v["blob_matches_pin"]
    finally:
        A.BENCHMARK_BLOB = saved
    hostile("benchmark_blob_drift", drift, A.build_vocabulary()["blob_matches_pin"],
            {"drift_detected": drift})


def no_alarm():
    res = A.audit(VOCAB)
    generic_only = True
    for _pkg, e in res["per_holdout"].items():
        for r in e["review"]:
            if r["class"] != "NAME_TOKEN" or r["pattern"] not in A.GENERIC_TOKENS:
                generic_only = False
    exempt_in_declaration = True
    for _pkg, e in res["per_holdout"].items():
        for x in e["exemptions"]:
            low = x["text"].lower()
            if not any(k in low for k in ("forbidden", "hidden", "no_family_score",
                                          "benchmark_blob_required")):
                exempt_in_declaration = False
    quiet = {"violations": res["violations"],
             "review_hits_all_generic": generic_only,
             "exemptions_all_inside_declarations": exempt_in_declaration,
             "control_scan_found_family_vocabulary":
                 res["control_family_hits_in_posthoc"] > 0}
    bad = [k for k, v in quiet.items() if (v is not True and v != 0)]
    if bad:
        FINDINGS.append("NO_ALARM_VIOLATED:" + ",".join(bad))
    return quiet


def main():
    h_plant("plant_family_id", "TARGET_FAMILY = 'K01'")
    h_plant("plant_paper_name", "MODE = 'neural/feed-forward'")
    h_plant("plant_fingerprint_clause", "# require " + VOCAB["fingerprint_clauses"][0][:60])
    h_plant("plant_parent_anchor", "# after " + VOCAB["parent_anchors"][0])
    h_plant("plant_benchmark_reference",
            "cfg = open('%s')" % A.BENCHMARK_FILE)
    h_plant("plant_cost_bonus", "COST_BONUS = {'K03': -2, 'K04': -1}")
    h_plant("plant_exclusion_clause", "# avoid " + VOCAB["exclusion_clauses"][0][:40])
    for fn in (h_boundary_regex_word_only, h_exemption_too_wide,
               h_blind_file_rule_too_narrow, h_vocabulary_not_derived,
               h_posthoc_treated_as_blind, h_benchmark_blob_drift):
        fn()
    quiet = no_alarm()
    recall = A.planted_positives(VOCAB)
    missed = [p["class"] for p in recall if not p["detected"]]
    if missed:
        FINDINGS.append("PLANTED_POSITIVE_MISSED:" + ",".join(missed))
    out = {"schema": "GMI833AJ9HoldoutSourceAuditTestReceiptV1",
           "hostiles": HOSTILES,
           "hostiles_declared": len(HOSTILES),
           "hostiles_detected": sum(1 for h in HOSTILES if h["detected"]),
           "controls_clean": sum(1 for h in HOSTILES if h["control_clean"]),
           "planted_positive_recall": recall,
           "planted_positives_detected": sum(1 for p in recall if p["detected"]),
           "no_alarm": quiet,
           "findings": FINDINGS,
           "status": "GREEN" if not FINDINGS else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(out, indent=2, sort_keys=True, separators=(",", ": ")) + "\n")
    print(json.dumps({"status": out["status"], "hostiles_declared": out["hostiles_declared"],
                      "hostiles_detected": out["hostiles_detected"],
                      "controls_clean": out["controls_clean"],
                      "planted_positives_detected": out["planted_positives_detected"],
                      "findings": FINDINGS}, indent=2, sort_keys=True))
    return 0 if not FINDINGS else 1


if __name__ == "__main__":
    sys.exit(main())
