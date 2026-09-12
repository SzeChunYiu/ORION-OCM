#!/usr/bin/env python3
"""One protected DG-10-corrected K4 V4 array task with fail-closed provenance."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, resource, subprocess, sys, time, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")
SUCCESSOR_FREEZE = os.path.join(ROOT, "GMI_K4_MEASURED_RESOURCE_SUCCESSOR_FREEZE_V4.json")
BEACON = os.path.join(ROOT, "GMI_K4_PUBLIC_BEACON_V4.json")
RES = os.path.join(ROOT, "microscopes", "results", "k4_v4")


def jhash(path):
    raw = open(path).read(); return json.loads(raw), hashlib.sha256(raw.encode()).hexdigest()

def load_contracts():
    freeze, fsha = jhash(FREEZE); freeze.pop("name_key", None)
    succ, ssha = jhash(SUCCESSOR_FREEZE); beacon, bsha = jhash(BEACON)
    if succ.get("status") != "FROZEN_BEFORE_V4_PUBLIC_BEACON_AND_ANY_V4_SEARCH_RESULT": raise RuntimeError("bad V4 successor freeze status")
    if beacon.get("schema") != "GMIK4PublicBeaconV4" or beacon.get("status") != "ACQUIRED_NO_REROLL" or not beacon.get("no_reroll") or not beacon.get("sha256_signature_consistency_verified"):
        raise RuntimeError("invalid V4 public beacon")
    return freeze, fsha, ssha, beacon, bsha

def git_sha():
    try: return subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    except Exception: return "UNKNOWN"

def plan(fr):
    return [{"family":f,"grammar":g,"cell":c} for f in sorted(fr["families"]) for g in sorted(fr["grammars"]) for c in ("w1","w2","w4","w8")]


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--task-index",type=int,required=True); ap.add_argument("--job-id",default="local")
    ap.add_argument("--host",default="unknown"); ap.add_argument("--budget",type=int,default=1_000_000); a=ap.parse_args()
    os.makedirs(RES,exist_ok=True); t0=time.time(); rec={"schema":"GMIK4TaskReceiptV5","task_index":a.task_index,"slurm_job_id":a.job_id,"host":a.host}
    try:
        freeze,fsha,ssha,beacon,bsha=load_contracts(); p=plan(freeze)
        rec.update({"git_commit_sha":git_sha(),"freeze_artifact_sha256":fsha,"successor_freeze_sha256":ssha,
                    "public_beacon_sha256":bsha,"public_beacon_round":beacon.get("target_round"),
                    "public_beacon_randomness":beacon.get("randomness"),"python_version":sys.version.split()[0],"platform":platform.platform(),
                    "resource_request":{"cpus":1,"budget_scored_candidates":a.budget},"n_tasks_in_plan":len(p)})
        if not 0<=a.task_index<len(p): raise IndexError(f"task index {a.task_index} outside plan of {len(p)}")
        unit=p[a.task_index]; rec.update(unit)
        th=hashlib.sha256(json.dumps({**unit,"prediction_freeze":fsha,"successor_freeze":ssha},sort_keys=True).encode()).hexdigest(); rec["task_hash"]=th
        rec["seed"]=int(hashlib.sha256(("GMI-K4-V4"+th+beacon["randomness"]).encode()).hexdigest()[:16],16)%(2**32)
        rec["seed_derivation"]="int(SHA256('GMI-K4-V4'||task_hash||drand_randomness)[:16],16) mod 2^32"
        from gmi_k4_search_v4 import run_cell
        out=run_cell(unit["family"],unit["grammar"],unit["cell"],freeze=freeze,seed=rec["seed"],budget=a.budget)
        rec["raw_result"]=out; rec["verdict"]=out["verdict"]; rec["status"]="OK"
    except Exception:
        rec["status"]="FAILED"; rec["traceback"]=traceback.format_exc(); rec["verdict"]="TASK_FAILED"
    finally:
        ru=resource.getrusage(resource.RUSAGE_SELF); rec["wall_seconds"]=round(time.time()-t0,3); rec["cpu_seconds"]=round(ru.ru_utime+ru.ru_stime,3); rec["peak_rss_kb"]=ru.ru_maxrss
        rec["exit_code"]=0 if rec.get("status")=="OK" else 1
        path=os.path.join(RES,f"K4V4_{a.host}_{a.job_id}_{a.task_index:05d}.json"); json.dump(rec,open(path,"w"),indent=1,sort_keys=True,default=str)
        print(json.dumps({k:rec.get(k) for k in ("task_index","family","grammar","cell","verdict","status","public_beacon_round","wall_seconds","cpu_seconds")}))
    sys.exit(rec["exit_code"])

if __name__=="__main__": main()
