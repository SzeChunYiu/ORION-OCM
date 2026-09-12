#!/usr/bin/env python3
"""K5 B-H revival V8 task runner (RV-377-170 / RV-377-171).

Runs the UNCHANGED gmi_k5_bh_experiments core on the task plan in GMI_K5_BH_REVIVAL_PLAN_V8.json.
Tier is DEVELOPMENT unless --tier protected is given, in which case GMI_K5_BH_EXECUTION_FREEZE_V8.json and
GMI_K5_BH_PUBLIC_BEACON_V8.json must exist and verify through hpc.gmi_beacon_verify. Development receipts are
written under microscopes/results/k5_bh_v8_dev/ and are never protected evidence.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:sys.path.insert(0,ROOT)
PLAN=os.path.join(ROOT,"GMI_K5_BH_REVIVAL_PLAN_V8.json");PHASE=os.path.join(ROOT,"GMI_K5_BH_PHASE_FREEZE_V1.json");SCORE=os.path.join(ROOT,"GMI_K5_BH_SCORING_FREEZE_V1.json");ADM=os.path.join(ROOT,"GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json");EXEC=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V8.json");BEACON=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V8.json")
def jh(p):raw=open(p).read();return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def git_sha():
    try:return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    except Exception:return "UNKNOWN"
def plan(pl,ph):
    out=[]
    for lane in sorted(pl["lanes"]):
        s=pl["lanes"][lane]
        for c in s["cells"]:
            for r in range(int(pl["replicates_per_value"])):out.append({"lane":lane,"parameter":s["parameter"],"value":c["value"],"replicate":r,"kind":"cell","plan":ph})
        pr=s.get("probe")
        if pr:
            for r in range(int(pl["replicates_per_value"])):out.append({"lane":lane,"parameter":s["parameter"],"value":pr["value"],"replicate":r,"kind":"probe","plan":ph})
    return out
def contracts(tier):
    pl,ph=jh(PLAN);phase,phh=jh(PHASE);score,sc=jh(SCORE);adm,ah=jh(ADM)
    if pl.get("schema")!="GMIK5BHRevivalPlanV8" or pl.get("status")!="FROZEN_BEFORE_ANY_V8_EXECUTION":raise RuntimeError("bad V8 plan")
    if adm.get("status")!="FROZEN_BEFORE_K5_PUBLIC_BEACON_AND_ANY_PROTECTED_K5_RESULT":raise RuntimeError("bad admissibility addendum")
    hs={"plan":ph,"phase":phh,"score":sc,"admissibility":ah};verified=None
    if tier=="protected":
        ex,eh=jh(EXEC);b,bh=jh(BEACON)
        if ex.get("status")!="FROZEN_BEFORE_K5_V8_BEACON_AND_PROTECTED_EXECUTION":raise RuntimeError("bad K5 V8 execution freeze")
        if ex.get("plan_sha256")!=ph:raise RuntimeError("execution freeze does not pin this plan")
        from hpc.gmi_beacon_verify import verify_beacon
        verified=verify_beacon(repo_root=ROOT,freeze_path=EXEC,beacon=b,expected_schema="GMIK5BHPublicBeaconV8");hs.update({"execution":eh,"beacon":bh})
    return pl,ph,hs,verified
def task_seed(tier,th,hs,verified):
    if tier=="protected":return int(hashlib.sha256(("GMI-K5-BH-V8"+th+verified["randomness"]).encode()).hexdigest()[:16],16)%(2**32)
    return int(hashlib.sha256(("GMI-K5-BH-V8-DEV"+th+hs["plan"]).encode()).hexdigest()[:16],16)%(2**32)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--task-index",type=int,required=True);ap.add_argument("--job-id",default="local");ap.add_argument("--host",default="unknown");ap.add_argument("--tier",choices=["development","protected"],default="development");a=ap.parse_args()
    res=os.path.join(ROOT,"microscopes","results","k5_bh_v8" if a.tier=="protected" else "k5_bh_v8_dev");os.makedirs(res,exist_ok=True);t0=time.time()
    rec={"schema":"GMIK5BHTaskReceiptV8","tier":a.tier.upper(),"protected":a.tier=="protected","task_index":a.task_index,"slurm_job_id":a.job_id,"host":a.host}
    try:
        pl,ph,hs,verified=contracts(a.tier);p=plan(pl,ph);rec.update({"git_commit_sha":git_sha(),"freeze_hashes":hs,"python_version":sys.version.split()[0],"platform":platform.platform(),"n_tasks_in_plan":len(p),"resource_request":{"cpus":1}})
        if verified:rec.update({"public_beacon_round":verified["target_round"],"public_beacon_randomness":verified["randomness"],"beacon_verification":verified})
        if len(p)!=int(pl["expected_tasks"]):raise RuntimeError("task-plan cardinality mismatch")
        if not 0<=a.task_index<len(p):raise IndexError(a.task_index)
        unit=p[a.task_index];rec.update(unit);th=hashlib.sha256(json.dumps(unit,sort_keys=True,separators=(",",":")).encode()).hexdigest();rec["task_hash"]=th;rec["seed"]=task_seed(a.tier,th,hs,verified)
        lane=pl["lanes"][unit["lane"]];spec=lane["probe"] if unit["kind"]=="probe" else next(c for c in lane["cells"] if c["value"]==unit["value"]);rec["v8_predicted_winner"]=spec["predicted_winner"]
        from gmi_k5_bh_experiments import run
        raw=run(unit["lane"],rec["seed"],unit["value"])
        if not isinstance(raw,dict) or not all(k in raw for k in ("predicted_winner","observed_winner","prediction_margin","observables","admissible")):raise RuntimeError("incomplete result")
        if not isinstance(raw["admissible"],list):raise RuntimeError("admissible not list")
        if raw["observed_winner"]!="NONE" and raw["observed_winner"] not in raw["admissible"]:raise RuntimeError("observed winner outside admissible")
        pw=spec["predicted_winner"];o=raw["observables"]
        if unit["lane"]=="C_FEATURE_LEARNING":obj={"FIXED_FEATURE":o["fixed_objective"],"TRAINABLE_FEATURE":o["trainable_objective"]}
        else:obj={"DIRECT":o["direct_development_cost"],"MODEL":o["model_development_plus_planning_cost"]}
        if pw=="NONE":ok=True;agree=raw["observed_winner"]=="NONE";margin=0.0
        else:ok=pw in raw["admissible"];agree=ok and raw["observed_winner"]==pw;alt=[v for k,v in obj.items() if k!=pw];margin=min(alt)-obj[pw]
        rec["raw_result"]=raw;rec["status"]="OK";rec["v8_predicted_admissible"]=ok;rec["v8_prediction_margin"]=margin;rec["task_verdict"]="PREDICTED_INADMISSIBLE" if not ok else ("AGREE" if agree else "DISAGREE")
    except Exception:
        rec["status"]="FAILED";rec["task_verdict"]="TASK_FAILED";rec["traceback"]=traceback.format_exc()
    finally:
        ru=resource.getrusage(resource.RUSAGE_SELF);rec["wall_seconds"]=round(time.time()-t0,3);rec["cpu_seconds"]=round(ru.ru_utime+ru.ru_stime,3);rec["peak_rss_kb"]=ru.ru_maxrss;rec["exit_code"]=0 if rec.get("status")=="OK" else 1
        path=os.path.join(res,f"K5BHV8{'' if a.tier=='protected' else 'DEV'}_{a.host}_{a.job_id}_{a.task_index:05d}.json");json.dump(rec,open(path,"w"),indent=1,sort_keys=True,default=str)
    sys.exit(rec["exit_code"])
if __name__=="__main__":main()
