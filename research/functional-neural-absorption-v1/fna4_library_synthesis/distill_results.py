"""Distil FNA4_RESULTS.json from the preserved run-3 receipts (and the P6 revival
sweep receipts when present). Pure JSON analysis -- no harness imports, so the
numbers are exactly what the runs recorded. Not a scored artifact: outputs are
projections of receipts, never inputs to anything.
"""
import json
import gzip
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R3 = HERE / "receipts" / "FNA4_RUN3_RECEIPTS.json.gz"
R2 = HERE / "receipts" / "FNA4_SWEEP_R2_RECEIPTS.json"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fam_of(tid):
    return tid.split("-")[1]


d = json.loads(gzip.open(R3, "rt").read())
out = {"schema": "ocm.fna.fna4.results.v1",
       "source_receipts": {"run3": "receipts/FNA4_RUN3_RECEIPTS.json.gz "
                                   "(raw json sha256 "
                                   "06a72a5e87d33c6681332a9a06477a06b5b5962768a33e172638023dfe628d5b)",
                           "run3_raw_sha256": "06a72a5e87d33c6681332a9a06477a06b5b5962768a33e172638023dfe628d5b",
                           "run3_gz_sha256": sha(R3)},
       "defect_runs": ["defect_runs/FNA4_DEFECT_RUN1_RECEIPTS.json.gz",
                       "defect_runs/FNA4_DEFECT_RUN2_PARTIAL.json.gz"],
       "harness": d["phases"]["harness"]}

m = d["phases"]["main"]
by = {a["arm"]: a for a in m["arms"]}
out["main"] = {"arms": {}, "oracle_teleport_LABELLED_UPPER_BOUND":
               m["oracle_teleport_LABELLED_UPPER_BOUND"]}
for a in m["arms"]:
    fam = {}
    for r in a["test_receipts"]:
        f = fam_of(r["task_id"])
        s = fam.setdefault(f, {"work": 0, "hits": 0, "n": 0, "solved": 0})
        s["work"] += r["work"]["total_units"]; s["hits"] += r["macro_hits"]
        s["n"] += 1; s["solved"] += 1 if r["solved"] else 0
    out["main"]["arms"][a["arm"]] = {
        "acquisition_work": a["acquisition_work"],
        "acquisition_work_marginal_units": a["acquisition_work_marginal_units"],
        "acq_experience_chains": a["acq_experience_chains"],
        "test_work_total": a["test_work_total"],
        "test_solved": a["test_solved"], "macro_hits_fresh": a["macro_hits_fresh"],
        "misfires_test": a["misfires_test"],
        "library_size": len(a["library"]),
        "library_families": [tuple(s[0] for s in mm["skeleton"]) for mm in a["library"]],
        "per_family": fam,
        "totals": m["arm_totals"][a["arm"]]}

no = out["main"]["arms"]["NO_LIBRARY"]
out["main"]["per_task_delta_vs_no_library"] = {
    arm: {f: round((v["work"] - no["per_family"][f]["work"]) / no["per_family"][f]["n"])
          for f, v in a["per_family"].items()}
    for arm, a in out["main"]["arms"].items()}
# critical F2 share (F3 folded into non-F2): d_F2*x = d_nonF2*(1-x)
out["main"]["critical_f2_share"] = {"convention": "x solves d_F2*x = d_nonF2*(1-x); "
                                    "balanced = non-F2 stream is half F1, half F3; "
                                    "f1_only = non-F2 stream is all F1 (worst case)"}
for arm in ("STITCH", "STITCH_NOGOOD_CEGIS", "CHUNK", "AU_PAIR", "EGGRAPH"):
    dd = out["main"]["per_task_delta_vs_no_library"][arm]
    row = {}
    for tag, d_non in (("balanced", (dd["F1"] + dd["F3"]) / 2.0), ("f1_only", dd["F1"])):
        den = d_non - dd["F2"]
        row[tag] = round(d_non / den, 4) if den > 0 else \
            ("no_share_pays" if dd["F2"] > 0 else None)
    out["main"]["critical_f2_share"][arm] = row

out["ablation"] = {k: v for k, v in d["phases"]["ablation"].items()
                   if not isinstance(v, list)}
out["revocation"] = {k: v for k, v in d["phases"]["revocation"].items()
                     if not isinstance(v, list)}
sw = d["phases"]["repeat_rate_sweep"]
out["repeat_rate_sweep_frozen_axis"] = sw
p0 = sw["points"][0]
out["repeat_rate_sweep_frozen_axis"]["r0_economics"] = {
    "saving_on_24_task_stream": p0["no_library_total"] -
    (p0["stitch_with_library_total"] - p0["stitch_acquisition"]),
    "break_even_tasks_marginal": round(p0["stitch_acquisition_marginal"] /
        ((p0["no_library_total"] - (p0["stitch_with_library_total"] -
          p0["stitch_acquisition"])) / 24), 1)}
out["determinism"] = d["phases"]["determinism"]
c = by["STITCH_NOGOOD_CEGIS"]
out["cegis"] = {"refinements": sum(len(r.get("cegis_refinements", []))
                                   for r in c["test_receipts"]),
                "misfires_combined_vs_stitch": [c["misfires_test"],
                                                by["STITCH"]["misfires_test"]]}
out["nogood_granularity_pair"] = {
    a: {"test_work_total": by[a]["test_work_total"],
        "marginal": m["arm_totals"][a]["marginal"],
        "misfires": by[a]["misfires_test"]}
    for a in ("NOGOOD_ONLY_per_op", "NOGOOD_ONLY_per_batch")}

if R2.exists():
    d2 = json.loads(R2.read_text())
    out["p6_revival_sweep"] = {
        "declared_in": "FNA4_FREEZE_ADDENDUM_V3.json",
        "receipts": "receipts/FNA4_SWEEP_R2_RECEIPTS.json",
        "raw_sha256": sha(R2),
        "exhibited_chains": d2["exhibited_chains"],
        "acquisition_work_full": d2["acquisition_work_full"],
        "stitch_learner_units": d2["stitch_learner_units"],
        "points": d2["points"]}

dest = HERE / "FNA4_RESULTS.json"
dest.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
print("wrote", dest, dest.stat().st_size, "bytes")
print("critical_f2_share:", out["main"]["critical_f2_share"])
print("r0 economics:", out["repeat_rate_sweep_frozen_axis"]["r0_economics"])
if "p6_revival_sweep" in out:
    for p in out["p6_revival_sweep"]["points"]:
        print("r2-sweep:", {k: p[k] for k in p if k != "library"})
