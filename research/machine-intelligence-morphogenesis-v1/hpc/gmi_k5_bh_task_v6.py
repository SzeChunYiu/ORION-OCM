#!/usr/bin/env python3
"""One protected K5 B-H V6 task with quality enforcement and independently verified beacon provenance."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE=os.path.join(ROOT,"GMI_K5_BH_PHASE_FREEZE_V1.json");SCORE=os.path.join(ROOT,"GMI_K5_BH_SCORING_FREEZE_V1.json");CORR2=os.path.join(ROOT,"GMI_K5_BH_DESIGN_CORRIGENDUM_V2.json");CORR3=os.path.join(ROOT,"GMI_K5_BH_CONTINUAL_CORRIGENDUM_V3.json");ADM=os.path.join(ROOT,"GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json");EXEC=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V6.json");BEACON=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V6.json");RES=os.path.join(ROOT,"microscopes","results","k5_bh_v6")
def jh(p):raw=open(p).read();return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def git_sha():
    try:return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    except Exception:return "UNKNOWN"
def contracts():
    phase,ph=jh(PHASE);score,sc=jh(SCORE);c2,c2h=jh(CORR2);c3,c3h=jh(CORR3);adm,ah=jh(ADM);ex,eh=jh(EXEC);b,bh=jh(BEACON)
    if adm.get("status")!="FROZEN_BEFORE_K5_PUBLIC_BEACON_AND_ANY_PROTECTED_K5_RESULT":raise RuntimeError("bad admissibility addendum")
    if ex.get("status")!="FROZEN_BEFORE_K5_V6_BEACON_AND_PROTECTED_EXECUTION":raise RuntimeError("bad K5 V6 execution freeze")
    from hpc.gmi_beacon_verify import verify_beacon
    verified=verify_beacon(repo_root=ROOT,freeze_path=EXEC,beacon=b,expected_schema="GMIK5BHPublicBeaconV6")
    return ex,verified,{"phase":ph,"score":sc,"corr2":c2h,"corr3":c3h,"admissibility":ah,"execution":eh,"beacon":bh}
def plan(ex):return [{"lane":l,"parameter":s["parameter"],"value":v,"replicate":r} for l in sorted(ex["final_task_plan"]) for v in ex["final_task_plan"][l]["values"] for r in range(int(ex["replicates_per_value"]))]
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--task-index",type=int,required=True);ap.add_argument("--job-id",default="local");ap.add_argument("--host",default="unknown");a=ap.parse_args();os.makedirs(RES,exist_ok=True);t0=time.time();rec={"schema":"GMIK5BHTaskReceiptV6","task_index":a.task_index,"slurm_job_id":a.job_id,"host":a.host}
    try:
        ex,verified,hs=contracts();p=plan(ex);rec.update({"git_commit_sha":git_sha(),"freeze_hashes":hs,"public_beacon_round":verified["target_round"],"public_beacon_randomness":verified["randomness"],"beacon_verification":verified,"python_version":sys.version.split()[0],"platform":platform.platform(),"n_tasks_in_plan":len(p),"resource_request":{"cpus":1}})
        if len(p)!=int(ex["expected_tasks"]):raise RuntimeError("task-plan cardinality mismatch")
        if not 0<=a.task_index<len(p):raise IndexError(a.task_index)
        unit=p[a.task_index];rec.update(unit);key={**unit,"phase":hs["phase"],"score":hs["score"],"corr2":hs["corr2"],"corr3":hs["corr3"],"admissibility":hs["admissibility"],"execution":hs["execution"]};th=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(",",":")).encode()).hexdigest();rec["task_hash"]=th;rec["seed"]=int(hashlib.sha256(("GMI-K5-BH-V6"+th+verified["randomness"]).encode()).hexdigest()[:16],16)%(2**32);rec["seed_derivation"]="int(SHA256('GMI-K5-BH-V6'||task_hash||verified_unique_drand_randomness)[:16],16) mod 2^32"
        from gmi_k5_bh_experiments import run
        raw=run(unit["lane"],rec["seed"],unit["value"])
        if not isinstance(raw,dict) or not all(k in raw for k in ("predicted_winner","observed_winner","prediction_margin","observables","admissible")):raise RuntimeError("incomplete result")
        if not isinstance(raw["admissible"],list):raise RuntimeError("admissible not list")
        if raw["observed_winner"]!="NONE" and raw["observed_winner"] not in raw["admissible"]:raise RuntimeError("observed winner outside admissible")
        ok=raw["predicted_winner"] in raw["admissible"];rec["raw_result"]=raw;rec["status"]="OK";rec["predicted_admissible"]=ok;rec["task_verdict"]="PREDICTED_INADMISSIBLE" if not ok else ("AGREE" if raw["predicted_winner"]==raw["observed_winner"] else "DISAGREE")
    except Exception:
        rec["status"]="FAILED";rec["task_verdict"]="TASK_FAILED";rec["traceback"]=traceback.format_exc()
    finally:
        ru=resource.getrusage(resource.RUSAGE_SELF);rec["wall_seconds"]=round(time.time()-t0,3);rec["cpu_seconds"]=round(ru.ru_utime+ru.ru_stime,3);rec["peak_rss_kb"]=ru.ru_maxrss;rec["exit_code"]=0 if rec.get("status")=="OK" else 1;path=os.path.join(RES,f"K5BHV6_{a.host}_{a.job_id}_{a.task_index:05d}.json");json.dump(rec,open(path,"w"),indent=1,sort_keys=True,default=str);print(json.dumps({k:rec.get(k) for k in ("task_index","lane","value","replicate","task_verdict","status","public_beacon_round")},sort_keys=True))
    sys.exit(rec["exit_code"])
if __name__=="__main__":main()
