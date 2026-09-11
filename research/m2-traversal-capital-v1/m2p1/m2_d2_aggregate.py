#!/usr/bin/env python3
"""Pool the pure-d=2 replication seeds: MDL library and integrated arm vs RESET."""
import json, glob, statistics
from pathlib import Path
rows = []
for f in sorted(glob.glob("DIST_SPLIT_D2.json") + glob.glob("DIST_SPLIT_R4*.json")):
    d = json.loads(Path(f).read_text()); r = d["by_distance"].get("2")
    if not r: continue
    rows.append({"seed": Path(f).stem.replace("DIST_SPLIT_", ""), "n": r["n"], "RESET": r["RESET"],
                 "MDL": r.get("CONTINUED_MDL"), "OCM": r.get("CONTINUED_OCM"), "SHUF": r.get("SHUFFLED_HISTORY"),
                 "mdl_red": r.get("MDL_reduction_vs_RESET"), "better": r.get("MDL_strictly_better"),
                 "ocm_red": round(1 - r["CONTINUED_OCM"] / r["RESET"], 4) if r.get("CONTINUED_OCM") else None})
mdl = [r["mdl_red"] for r in rows if r["mdl_red"] is not None]; ocm = [r["ocm_red"] for r in rows if r["ocm_red"] is not None]
out = {"schema": "OCM_M2_D2_AGGREGATE_V1", "seeds": len(rows), "rows": rows,
       "mdl_reduction_mean": round(statistics.fmean(mdl), 4) if mdl else None,
       "mdl_reduction_min": round(min(mdl), 4) if mdl else None, "mdl_positive_seeds": sum(1 for x in mdl if x > 0),
       "ocm_reduction_mean": round(statistics.fmean(ocm), 4) if ocm else None, "ocm_positive_seeds": sum(1 for x in ocm if x > 0),
       "shuffled_worse_every_seed": all(r["SHUF"] > r["RESET"] for r in rows if r["SHUF"])}
Path("D2_AGGREGATE.json").write_text(json.dumps(out, indent=1, sort_keys=True))
for r in rows: print("%-6s n=%-3s RESET=%-9s MDL=%-9s OCM=%-9s SHUF=%-9s mdl_red=%s ocm_red=%s better=%s" % (
    r["seed"], r["n"], r["RESET"], r["MDL"], r["OCM"], r["SHUF"], r["mdl_red"], r["ocm_red"], r["better"]))
print("\nseeds=%d mdl mean=%s min=%s positive=%d | ocm mean=%s positive=%d | shuffled worse every seed=%s" % (
    out["seeds"], out["mdl_reduction_mean"], out["mdl_reduction_min"], out["mdl_positive_seeds"], out["ocm_reduction_mean"], out["ocm_positive_seeds"], out["shuffled_worse_every_seed"]))
