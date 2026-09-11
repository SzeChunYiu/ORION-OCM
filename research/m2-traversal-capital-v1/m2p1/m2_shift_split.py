#!/usr/bin/env python3
"""Per-segment (A / B / A') arm totals for the shifted ecology."""
import argparse, json, statistics
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--ecology", required=True); ap.add_argument("--run-dir", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
eco = json.loads(Path(a.ecology).read_text())
seg = {r["normal_form_digest"]: r["segment"] for r in eco["streams"]["protected"]}
out = {"by_segment": {}}
arms = {}
for f in sorted(Path(a.run_dir).glob("arm_*.json")):
    d = json.loads(f.read_text()); top = max(d["ladder"]); first = {}
    for r in d["rows"]:
        if r["verified"] and r["target"] not in first: first[r["target"]] = r["B_slots"]
    arms[d["arm"]] = {t: first.get(t, top) for t in seg}
for s in ("A", "B", "A_prime"):
    tg = [t for t, v in seg.items() if v == s]
    row = {"n": len(tg)}
    for an, m in arms.items(): row[an] = round(statistics.fmean(m[t] for t in tg), 1)
    out["by_segment"][s] = row
out["lifetime"] = {an: round(statistics.fmean(m.values()), 1) for an, m in arms.items()}
Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True)); print(json.dumps(out, indent=1))
