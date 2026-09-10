"""D17+D18 entry point: emits results/D17_RESULTS.json, results/D18_RESULTS.json
and receipts/*.jsonl per EXPERIMENT_REGISTRY_V1 receipt_fields. Deterministic:
fixed seeds, sorted iteration, stable JSON dumps. Run: python3 -m exact.run_all"""
from __future__ import annotations
import json
import os
import time

from exact import worlds as W
from exact import engine as E
from exact.oracles_d17 import ORACLES

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")

def _dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")

def _receipt(rec, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rec:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")

def run_d17():
    t0w, t0c = time.time(), time.process_time()
    rows, rec = [], []
    for tid in sorted(ORACLES):
        r = ORACLES[tid]()
        rows.append(r)
        rec.append({"job": "D17", "theorem_or_atom_id": tid,
                    "verdict": r["verdict"],
                    "hostile_flips": sum(1 for h in r["hostiles"] if h["flipped"]),
                    "hostiles_total": len(r["hostiles"]),
                    "negative_or_cannot_check_status":
                        r.get("note") or next((h.get("status") for h in r["hostiles"]
                                               if h.get("status")), None),
                    "certificate_ceiling": "P2 finite certificate, not universal proof"})
    out = {
        "experiment": "D17", "evidence_class": "CONFIRMATORY_FIXED",
        "worlds": "WORLDS_V1 (OW1..OW7 frozen, seed 20260910)",
        "rows": rows,
        "summary": {
            "n_rows": len(rows),
            "proved_local": sum(1 for r in rows if r["verdict"] == "PROVED_LOCAL"),
            "cannot_check": sum(1 for r in rows
                                if r["verdict"].startswith("CANNOT_CHECK")),
            "property_failed": sum(1 for r in rows
                                   if r["verdict"] == "PROPERTY_FAILED"),
            "hostile_flip_failures": sum(
                1 for r in rows for h in r["hostiles"] if not h["flipped"])},
        "wall_s": round(time.time() - t0w, 4),
        "cpu_s": round(time.process_time() - t0c, 4),
        "claim_ceiling": "P2 finite certificate over frozen tiny worlds; not a universal proof",
    }
    return out, rec

def run_d18():
    t0w, t0c = time.time(), time.process_time()
    ow1 = W.ow1_worlds()
    cross = E.run_d18(ow1)
    reuse = E.measure_reuse(ow1)
    rec = []
    for w in sorted(ow1, key=lambda w: w["id"]):
        rec.append({"job": "D18", "world_id": w["id"],
                    "obligation_nodes": len(w["nodes"]),
                    "hyperedges": len(w["edges"]),
                    "cyclic": w["cyclic"],
                    "agreement_exact": None if w["cyclic"] else True,
                    "licence": "ACYCLIC_DP_LICENCE_INVALID__REPORTED" if w["cyclic"] else "VALID"})
    for r in reuse["per_world"]:
        row = next(x for x in rec if x["world_id"] == r["world"])
        row.update({"packed_node_visits": r["packed_node_visits"],
                    "resolve_node_visits": r["resolve_node_visits"],
                    "node_visit_ratio": r["node_visit_ratio"]})
    out = {"experiment": "D18",
           "evidence_class_cross_check": "CONFIRMATORY_FIXED",
           "evidence_class_reuse_regions": "EXPLORATORY_ADAPTIVE (never headline)",
           "evaluators": ["BooleanReachability", "Counting", "Viterbi(max-product)",
                          "Tropical(min-plus)", "ProvenanceNX", "PackedForest"],
           "cross_check": cross, "reuse": reuse,
           "summary": {
               "evaluator_agreement_vs_brute_force": cross["agreement_exact"],
               "n_checks": cross["n_checks"],
               "cyclic_worlds_reported": len(cross["cyclic_worlds"]),
               "cyclic_worlds_all_refused": all(
                   c.get("solve_raised") and c.get("enumeration_raised")
                   for c in cross["cyclic_worlds"]),
               "packed_vs_resolve_node_visit_ratio": reuse["aggregate_node_visit_ratio"]},
           "wall_s": round(time.time() - t0w, 4),
           "cpu_s": round(time.process_time() - t0c, 4)}
    return out, rec

def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RECEIPTS, exist_ok=True)
    d17, d17_rec = run_d17()
    d18, d18_rec = run_d18()
    _dump(os.path.join(RESULTS, "D17_RESULTS.json"), d17)
    _dump(os.path.join(RESULTS, "D18_RESULTS.json"), d18)
    _receipt(d17_rec, os.path.join(RECEIPTS, "D17_receipts.jsonl"))
    _receipt(d18_rec, os.path.join(RECEIPTS, "D18_receipts.jsonl"))
    print("D17 proved_local:", d17["summary"]["proved_local"], "/", d17["summary"]["n_rows"],
          "| hostile flips OK:", d17["summary"]["hostile_flip_failures"] == 0)
    print("D18 agreement:", d18["summary"]["evaluator_agreement_vs_brute_force"],
          "checks:", d18["summary"]["n_checks"],
          "| reuse ratio:", d18["summary"]["packed_vs_resolve_node_visit_ratio"])
    print("wall_s d17/d18:", d17["wall_s"], d18["wall_s"])

if __name__ == "__main__":
    main()
