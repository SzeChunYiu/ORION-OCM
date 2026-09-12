#!/usr/bin/env python3
"""Development-only LUNARC sizing/import probe for protected null-aware K4 V5."""
from __future__ import annotations
import hashlib,json,os,platform,resource,subprocess,sys,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE=os.path.join(ROOT,"GMI_K4_LOFO_FREEZE_V1.json");SUCCESSOR=os.path.join(ROOT,"GMI_K4_NULL_AWARE_SUCCESSOR_FREEZE_V5.json");OUT=os.path.join(ROOT,"LUNARC_ENV_PROBE_V1.json")
PILOT_BUDGET=20_000;PROTECTED_BUDGET=1_000_000
def sh(cmd):
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=30);return {"returncode":p.returncode,"stdout":p.stdout.strip(),"stderr":p.stderr.strip()}
    except Exception as e:return {"returncode":-1,"stdout":"","stderr":repr(e)}
def jh(p):raw=open(p).read();return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def main():
    full,fsha=jh(FREEZE);fr=dict(full);fr.pop("name_key",None);succ,ssha=jh(SUCCESSOR)
    if succ.get("status")!="FROZEN_BEFORE_V5_PUBLIC_BEACON_AND_ANY_V5_SEARCH_RESULT":raise SystemExit("bad V5 successor freeze")
    partitions=sh(["sinfo","-h","-o","%P|%a|%l|%c|%m|%G"]);assoc=sh(["sacctmgr","-n","-P","show","assoc",f"user={os.environ.get('USER','')}","format=Account,Partition,QOS"]);slurm=sh(["sinfo","--version"])
    fam=sorted(fr["families"])[0];gram=sorted(fr["grammars"])[0];seed=0x4B345035
    from gmi_k4_search_v5 import run_cell
    t=time.perf_counter();r=run_cell(fam,gram,"w1",freeze=fr,seed=seed,budget=PILOT_BUDGET);wall=time.perf_counter()-t;ru=resource.getrusage(resource.RUSAGE_SELF);projected=wall*(PROTECTED_BUDGET/PILOT_BUDGET)
    rec={"schema":"LUNARCEnvProbeV6","status":"DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED","scientific_use":"SIZING_AND_IMPORT_SMOKE_ONLY__EXCLUDED_FROM_PROTECTED_K4_V5","host":platform.node(),"platform":platform.platform(),"python":sys.version,"cwd":os.getcwd(),"freeze_sha256":fsha,"successor_freeze_sha256":ssha,"slurm_version":slurm,"partitions":partitions,"associations":assoc,
         "pilot":{"family":fam,"grammar":gram,"cell":"w1","development_seed":seed,"budget":PILOT_BUDGET,"protected_budget":PROTECTED_BUDGET,"development_verdict_not_evidence":r.get("verdict"),"development_null_not_evidence":(r.get("null_frontier") or {}).get("best_admissible_null"),"wall_seconds":wall,"projected_protected_wall_seconds":projected,"peak_rss_kb":ru.ru_maxrss,"search_digest":r.get("search_digest"),"null_search_digest":r.get("null_search_digest")},
         "sizing_rule_frozen_here":{"time_safety_factor_on_projected_full_run":3.0,"minimum_wall_seconds":600,"memory_safety_factor":4.0,"minimum_memory_mib":512,"note":"Walltime=max(minimum, measured_20k_time*(1e6/20k)*3). Development verdict and null audit are never protected evidence."}}
    json.dump(rec,open(OUT,"w"),indent=1,sort_keys=True);print(json.dumps({"wrote":OUT,"status":rec["status"],"pilot_wall_seconds":wall,"projected_protected_wall_seconds":projected,"partition_probe_rc":partitions["returncode"],"assoc_probe_rc":assoc["returncode"]}))
if __name__=="__main__":main()
