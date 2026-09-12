#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,platform,resource,subprocess,sys,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));EXEC=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V7.json");OUT=os.path.join(ROOT,"LUNARC_K5_BH_ENV_PROBE_V7.json")
def sh(cmd):
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=30);return {"returncode":p.returncode,"stdout":p.stdout.strip(),"stderr":p.stderr.strip()}
    except Exception as e:return {"returncode":-1,"stdout":"","stderr":repr(e)}
def h(p):return hashlib.sha256(open(p,"rb").read()).hexdigest()
def main():
    ex=json.load(open(EXEC))
    if ex.get("status")!="FROZEN_BEFORE_K5_V7_BEACON_AND_PROTECTED_EXECUTION":raise SystemExit("bad V7 execution freeze")
    parts=sh(["sinfo","-h","-o","%P|%a|%l|%c|%m|%G"]);assoc=sh(["sacctmgr","-n","-P","show","assoc",f"user={os.environ.get('USER','')}","format=Account,Partition,QOS"]);slurm=sh(["sinfo","--version"])
    from gmi_k5_bh_experiments import run
    samples=[]
    for i,lane in enumerate(sorted(ex["final_task_plan"])):
        vals=ex["final_task_plan"][lane]["values"];value=vals[len(vals)//2];seed=0x4B370000+i;t=time.perf_counter();raw=run(lane,seed,value);samples.append({"lane":lane,"value":value,"wall_seconds":time.perf_counter()-t,"admissible":raw.get("admissible")})
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;mx=max(x["wall_seconds"] for x in samples);rec={"schema":"LUNARCK5BHEnvProbeV7","status":"DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED","scientific_use":"SIZING_ONLY","host":platform.node(),"platform":platform.platform(),"python":sys.version,"execution_freeze_sha256":h(EXEC),"slurm_version":slurm,"partitions":parts,"associations":assoc,"lane_samples":samples,"max_lane_wall_seconds":mx,"peak_rss_kb":peak,"sizing_rule":{"time_safety_factor":20.0,"minimum_wall_seconds":300,"memory_safety_factor":4.0,"minimum_memory_mib":512}}
    json.dump(rec,open(OUT,"w"),indent=1,sort_keys=True);print(json.dumps({"wrote":OUT,"max_lane_wall_seconds":mx,"peak_rss_kb":peak}))
if __name__=="__main__":main()
