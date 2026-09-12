#!/usr/bin/env python3
"""Render/submit the protected 256-task K5 V6 array from a measured probe."""
from __future__ import annotations
import argparse,hashlib,json,math,os,re,subprocess,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));PROBE=os.path.join(ROOT,"LUNARC_K5_BH_ENV_PROBE_V6.json");EXEC=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V6.json");BEACON=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V6.json");TEMPLATE=os.path.join(ROOT,"hpc","gmi_k5_bh_array.sbatch");RENDERED=os.path.join(ROOT,"hpc","gmi_k5_bh_array.rendered.sbatch");RECEIPT=os.path.join(ROOT,"hpc","GMI_K5_BH_SUBMISSION_RECEIPT_V6.json")
def h(p):return hashlib.sha256(open(p,"rb").read()).hexdigest()
def hhmmss(x):s=max(60,int(math.ceil(x/60)*60));hh,r=divmod(s,3600);mm,ss=divmod(r,60);return f"{hh:02d}:{mm:02d}:{ss:02d}"
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--account",required=True);ap.add_argument("--partition",required=True);ap.add_argument("--submit",action="store_true");ap.add_argument("--array-concurrency",type=int,default=64);a=ap.parse_args()
    for p in (PROBE,EXEC,BEACON,TEMPLATE):
        if not os.path.exists(p):raise SystemExit(f"required V6 artifact absent: {p}")
    pr=json.load(open(PROBE));ex=json.load(open(EXEC));b=json.load(open(BEACON))
    if pr.get("schema")!="LUNARCK5BHEnvProbeV6" or pr.get("status")!="DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED":raise SystemExit("bad K5 V6 probe")
    if ex.get("status")!="FROZEN_BEFORE_K5_V6_BEACON_AND_PROTECTED_EXECUTION":raise SystemExit("bad execution freeze")
    from hpc.gmi_beacon_verify import verify_beacon
    verified=verify_beacon(repo_root=ROOT,freeze_path=EXEC,beacon=b,expected_schema="GMIK5BHPublicBeaconV6")
    if pr.get("execution_freeze_sha256")!=h(EXEC):raise SystemExit("stale K5 V6 probe")
    if a.partition not in pr.get("partitions",{}).get("stdout",""):raise SystemExit("partition absent from measured sinfo")
    if a.account not in pr.get("associations",{}).get("stdout",""):raise SystemExit("account absent from measured associations")
    s=pr["sizing_rule"];wall=max(float(s["minimum_wall_seconds"]),float(pr["max_lane_wall_seconds"])*float(s["time_safety_factor"]));mem=max(int(s["minimum_memory_mib"]),int(math.ceil((max(1.0,float(pr["peak_rss_kb"]))/1024)*float(s["memory_safety_factor"]))))
    n=int(ex["expected_tasks"]);conc=max(1,min(a.array_concurrency,n));arr=f"0-{n-1}%{conc}";src=open(TEMPLATE).read();repl={"__ACCOUNT__":a.account,"__PARTITION__":a.partition,"__WALLTIME__":hhmmss(wall),"__MEM__":f"{mem}M","__ARRAY__":arr}
    for x,y in repl.items():src=src.replace(x,y)
    left=sorted(set(re.findall(r"__[A-Z_]+__",src)))
    if left:raise SystemExit(f"unrendered placeholders: {left}")
    open(RENDERED,"w").write(src);rec={"schema":"GMIK5BHSubmissionReceiptV6","status":"RENDERED_NOT_SUBMITTED","execution_freeze_sha256":h(EXEC),"public_beacon_sha256":h(BEACON),"verified_beacon_contract":verified,"probe_sha256":h(PROBE),"probe_host":pr.get("host"),"account":a.account,"partition":a.partition,"rendered":{"walltime":repl["__WALLTIME__"],"mem_per_cpu":repl["__MEM__"],"array":arr},"rendered_sha256":hashlib.sha256(src.encode()).hexdigest(),"job_id":None,"submitted_at_unix":None,"sbatch_stdout":None,"sbatch_stderr":None}
    if a.submit:
        p=subprocess.run(["sbatch",RENDERED],cwd=ROOT,text=True,capture_output=True);rec["submitted_at_unix"]=time.time();rec["sbatch_stdout"]=p.stdout.strip();rec["sbatch_stderr"]=p.stderr.strip();rec["status"]="SUBMISSION_FAILED" if p.returncode else "SUBMITTED";m=re.search(r"Submitted batch job\s+(\d+)",p.stdout);rec["job_id"]=None if not m else int(m.group(1))
    json.dump(rec,open(RECEIPT,"w"),indent=1,sort_keys=True);print(json.dumps({"status":rec["status"],"job_id":rec["job_id"],"beacon_round":verified["target_round"],"rendered":rec["rendered"]},sort_keys=True));return 3 if rec["status"]=="SUBMISSION_FAILED" else 0
if __name__=="__main__":raise SystemExit(main())
