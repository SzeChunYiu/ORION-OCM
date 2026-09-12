#!/usr/bin/env python3
"""One protected K5 B-H V5 task with quality/admissibility enforcement and fail-closed provenance."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE=os.path.join(ROOT,"GMI_K5_BH_PHASE_FREEZE_V1.json"); SCORE=os.path.join(ROOT,"GMI_K5_BH_SCORING_FREEZE_V1.json")
CORR2=os.path.join(ROOT,"GMI_K5_BH_DESIGN_CORRIGENDUM_V2.json"); CORR3=os.path.join(ROOT,"GMI_K5_BH_CONTINUAL_CORRIGENDUM_V3.json")
ADM=os.path.join(ROOT,"GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json"); EXEC=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V5.json")
BEACON=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V5.json"); RES=os.path.join(ROOT,"microscopes","results","k5_bh_v5")
def jh(p): raw=open(p).read(); return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def git_sha():
    try:return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    except Exception:return "UNKNOWN"

def contracts():
    phase,ph=jh(PHASE); score,sc=jh(SCORE); c2,c2h=jh(CORR2); c3,c3h=jh(CORR3); adm,ah=jh(ADM); ex,exh=jh(EXEC); b,bh=jh(BEACON)
    if adm.get("status")!="FROZEN_BEFORE_K5_PUBLIC_BEACON_AND_ANY_PROTECTED_K5_RESULT": raise RuntimeError("bad admissibility addendum")
    if ex.get("status")!="FROZEN_BEFORE_K5_V5_BEACON_AND_PROTECTED_EXECUTION": raise RuntimeError("bad V5 execution freeze status")
    if b.get("schema")!="GMIK5BHPublicBeaconV5" or b.get("status")!="ACQUIRED_NO_REROLL" or not b.get("no_reroll") or not b.get("sha256_signature_consistency_verified"): raise RuntimeError("invalid K5 V5 public beacon")
    return phase,score,c2,c3,adm,ex,b,{"phase":ph,"score":sc,"corr2":c2h,"corr3":c3h,"admissibility":ah,"execution":exh,"beacon":bh}

def task_plan(ex):
    return [{"lane":lane,"parameter":spec["parameter"],"value":value,"replicate":rep}
            for lane in sorted(ex["final_task_plan"]) for value in ex["final_task_plan"][lane]["values"] for rep in range(int(ex["replicates_per_value"]))]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--task-index",type=int,required=True); ap.add_argument("--job-id",default="local"); ap.add_argument("--host",default="unknown"); a=ap.parse_args()
    os.makedirs(RES,exist_ok=True); t0=time.time(); rec={"schema":"GMIK5BHTaskReceiptV5","task_index":a.task_index,"slurm_job_id":a.job_id,"host":a.host}
    try:
        phase,score,c2,c3,adm,ex,b,hs=contracts(); p=task_plan(ex)
        rec.update({"git_commit_sha":git_sha(),"freeze_hashes":hs,"public_beacon_round":b.get("target_round"),"public_beacon_randomness":b.get("randomness"),"python_version":sys.version.split()[0],"platform":platform.platform(),"n_tasks_in_plan":len(p),"resource_request":{"cpus":1}})
        if len(p)!=int(ex["expected_tasks"]): raise RuntimeError(f"task-plan cardinality {len(p)} != frozen {ex['expected_tasks']}")
        if not 0<=a.task_index<len(p): raise IndexError(f"task index {a.task_index} outside 0..{len(p)-1}")
        unit=p[a.task_index]; rec.update(unit)
        key={**unit,"phase":hs["phase"],"score":hs["score"],"corr2":hs["corr2"],"corr3":hs["corr3"],"admissibility":hs["admissibility"],"execution":hs["execution"]}
        th=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(",",":")).encode()).hexdigest(); rec["task_hash"]=th
        rec["seed"]=int(hashlib.sha256(("GMI-K5-BH-V5"+th+b["randomness"]).encode()).hexdigest()[:16],16)%(2**32)
        rec["seed_derivation"]="int(SHA256('GMI-K5-BH-V5'||task_hash||drand_randomness)[:16],16) mod 2^32"
        from gmi_k5_bh_experiments import run
        raw=run(unit["lane"],rec["seed"],unit["value"])
        if not isinstance(raw,dict) or not all(k in raw for k in ("predicted_winner","observed_winner","prediction_margin","observables","admissible")): raise RuntimeError("experiment returned incomplete result")
        if not isinstance(raw["admissible"],list): raise RuntimeError("admissible must be a list")
        if raw["observed_winner"]!="NONE" and raw["observed_winner"] not in raw["admissible"]: raise RuntimeError("observed winner lies outside runner admissible set")
        pred_ok=raw["predicted_winner"] in raw["admissible"]
        rec["raw_result"]=raw; rec["status"]="OK"; rec["predicted_admissible"]=pred_ok
        rec["task_verdict"]="PREDICTED_INADMISSIBLE" if not pred_ok else ("AGREE" if raw["predicted_winner"]==raw["observed_winner"] else "DISAGREE")
    except Exception:
        rec["status"]="FAILED"; rec["task_verdict"]="TASK_FAILED"; rec["traceback"]=traceback.format_exc()
    finally:
        ru=resource.getrusage(resource.RUSAGE_SELF); rec["wall_seconds"]=round(time.time()-t0,3); rec["cpu_seconds"]=round(ru.ru_utime+ru.ru_stime,3); rec["peak_rss_kb"]=ru.ru_maxrss; rec["exit_code"]=0 if rec.get("status")=="OK" else 1
        path=os.path.join(RES,f"K5BHV5_{a.host}_{a.job_id}_{a.task_index:05d}.json"); json.dump(rec,open(path,"w"),indent=1,sort_keys=True,default=str)
        print(json.dumps({k:rec.get(k) for k in ("task_index","lane","parameter","value","replicate","task_verdict","status","public_beacon_round","wall_seconds")},sort_keys=True))
    sys.exit(rec["exit_code"])
if __name__=="__main__": main()
