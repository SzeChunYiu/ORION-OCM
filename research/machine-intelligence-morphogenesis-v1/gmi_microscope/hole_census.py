"""RV-377-027 hole census at the exact layer: read every executed Stage D'/E' receipt, tabulate the admissible set of registered
rows per (ecology, criterion), list the HOLES (no admissible row) and the single-occupant regions, and attach the occupant
property the theory predicts for each hole from the target's algebra (property first, occupant second; RV-377-024 method).
Writes microscopes/results/STAGE_DE_HOLE_CENSUS_V1.json and a markdown table."""
from __future__ import annotations

import glob
import json
import os

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
CLASS = {"S4": "gradient (dense numeric)", "S2": "exact program search", "S2a": "approximate program search", "S5": "exemplar memory",
         "S5k": "kNN memory (DEFECTIVE implementation, RV-021)", "S5h": "generalizing kNN memory", "S6": "algebraic (XOR-linear) identification", "S3": "particles (stochastic search)"}
# the property the theory predicts an occupant must have, by target algebra / split (declared here, before any new row)
PREDICTED_PROPERTY = {
    "parity": "closure under the target algebra (XOR-linear identification); admissible only where the seen inputs span GF(2)^4",
    "smooth": "a real-valued output with per-input generalization: either a parametric map with bounded per-event update (gradient), a program from a grammar containing an approximation of the target (search), or local averaging over seen neighbours (kNN)",
    "binding": "an exact key->value store (memory); any generalizing form is dominated on cost",
}


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(RES, "STAGE_DE_SMOOTH_*.json"))):
        d = json.load(open(path))
        if "capability_by_cell" not in d: continue
        eco = d["ecology"]; theta = eco["theta"]; crit = eco.get("capability_criterion", "all")
        caps = d["capability_by_cell"]
        by_row = {}
        for k, v in caps.items():
            r, col, size = k.split("|"); by_row.setdefault(r, {}).setdefault(int(size), set()).add(v)
        adm = {}; best = {}
        for r, sizes in by_row.items():
            top = max(sizes); vals = sizes[top]
            best[r] = max(vals); adm[r] = min(vals) >= theta
        target = d.get("target_coeffs"); kind = "parity" if target is None and "PARITY" in os.path.basename(path) else ("smooth" if target else "unknown")
        rows.append({"receipt": os.path.basename(path), "run_tag": d.get("run_tag"), "kind": kind, "target_coeffs": target, "train": eco.get("train"), "criterion": crit, "H": eco.get("H"), "label_noise": eco.get("label_noise"),
                     "best_capability_by_row": best, "admissible_rows": sorted(r for r in adm if adm[r]), "hole": not any(adm.values()),
                     "frontier_empty_everywhere": all(v == [] for v in d["frontier_H_r"].values()), "predicted_occupant_property": PREDICTED_PROPERTY.get(kind)})
    holes = [r for r in rows if r["hole"]]
    singles = [r for r in rows if len(r["admissible_rows"]) == 1]
    out = {"schema": "StageDEHoleCensusV1", "issue": 377, "revival_record": "RV-377-027", "n_receipts": len(rows), "rows": rows,
           "holes": [{"receipt": r["receipt"], "kind": r["kind"], "train": r["train"], "criterion": r["criterion"], "predicted_occupant_property": r["predicted_occupant_property"]} for r in holes],
           "single_occupant_regions": [{"receipt": r["receipt"], "occupant": r["admissible_rows"][0], "class": CLASS.get(r["admissible_rows"][0])} for r in singles],
           "row_classes": CLASS}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, "STAGE_DE_HOLE_CENSUS_V1.json"), "w"), indent=1, sort_keys=True, default=str)
    L = ["# Hole census v1 (RV-377-027) — admissible registered rows per executed ecology\n", "| receipt | kind | criterion | events | noise | train | admissible rows | hole |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['receipt']} | {r['kind']} {r['target_coeffs'] or ''} | {r['criterion']} | {r['H']} | {'yes' if r['label_noise'] else ''} | {r['train']} | {', '.join(r['admissible_rows']) or '—'} | {'HOLE' if r['hole'] else ''} |")
    L.append("\nPredicted occupant property per hole kind (declared before any occupant row): " + json.dumps(PREDICTED_PROPERTY, indent=0))
    open(os.path.join(RES, "STAGE_DE_HOLE_CENSUS_V1.md"), "w").write("\n".join(L) + "\n")
    return out


if __name__ == "__main__":
    o = main()
    for r in o["rows"]:
        print(f"{r['receipt']:48s} {r['kind']:7s} {r['criterion']:6s} adm={r['admissible_rows']} hole={r['hole']}")
    print("holes:", [h["receipt"] for h in o["holes"]])
    print("single-occupant:", [(s["receipt"], s["occupant"]) for s in o["single_occupant_regions"]])
