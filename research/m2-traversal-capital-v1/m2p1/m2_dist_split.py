#!/usr/bin/env python3
"""Split an arm comparison by arrangement distance -- the registered-grammar P3 test.

The ecology rows carry arrangement_distance_to_train (1 or 2). Joining each arm's
per-target rows to that field gives B_arm(d) for d in {1,2} from ONE run, on the
REGISTERED solver, with the MDL (hierarchically chunked) library. If CONTINUED_MDL beats
RESET at d=2, the developmental benefit survives on novel ARRANGEMENTS of known parts in
the registered substrate -- the claim the hostile review said was untested and the
feasibility map said was unreachable with flat length-2 libraries.
"""
import argparse, json, statistics
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--ecology", required=True); ap.add_argument("--run-dir", required=True)
ap.add_argument("--label", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
eco = json.loads(Path(a.ecology).read_text())
dist = {r["normal_form_digest"]: r.get("arrangement_distance_to_train") for r in eco["streams"]["protected"]}
dev = json.loads((Path(a.run_dir) / "dev_state.json").read_text())
out = {"label": a.label, "mdl_admission": dev.get("mdl_admission"), "mdl_terminal": dev.get("mdl_terminal"),
       "mdl_fragments": dev.get("mdl_fragments"), "freq_admission": dev.get("admission"), "by_distance": {}}
arms = {}
for f in sorted(Path(a.run_dir).glob("arm_*.json")):
    d = json.loads(f.read_text())
    first = {}
    for r in d["rows"]:
        if r["verified"] and r["target"] not in first:
            first[r["target"]] = r["B_slots"]
    # unsolved targets: charge the top budget (censoring made explicit)
    top = max(d["ladder"])
    arms[d["arm"]] = {t: first.get(t, top) for t in dist}
for dd in (1, 2):
    tg = [t for t, v in dist.items() if v == dd]
    if not tg:
        continue
    row = {"n": len(tg)}
    for an, m in arms.items():
        row[an] = round(statistics.fmean(m[t] for t in tg), 1)
    if "RESET" in row and "CONTINUED_MDL" in row:
        row["MDL_reduction_vs_RESET"] = round(1 - row["CONTINUED_MDL"] / row["RESET"], 4)
        row["MDL_strictly_better"] = sum(1 for t in tg if arms["CONTINUED_MDL"][t] < arms["RESET"][t])
    out["by_distance"][str(dd)] = row
Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
print(json.dumps({k: v for k, v in out.items() if k != "mdl_fragments"}, indent=1))
