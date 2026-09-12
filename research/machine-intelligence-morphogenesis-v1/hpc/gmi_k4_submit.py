#!/usr/bin/env python3
"""Render/submit protected null-aware K4 V6 from a measured development-only probe."""
from __future__ import annotations
import argparse,hashlib,json,math,os,re,subprocess,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));PROBE=os.path.join(ROOT,"LUNARC_ENV_PROBE_V1.json");PRED=os.path.join(ROOT,"GMI_K4_LOFO_FREEZE_V1.json");SCI=os.path.join(ROOT,"GMI_K4_NULL_AWARE_SUCCESSOR_FREEZE_V5.json");EXEC=os.path.join(ROOT,"GMI_K4_EXECUTION_FREEZE_V6.json");BEACON=os.path.join(ROOT,"GMI_K4_PUBLIC_BEACON_V6.json");TEMPLATE=os.path.join(ROOT,"hpc","gmi_k4_array.sbatch");RENDERED=os.path.join(ROOT,"hpc","gmi_k4_array.rendered.sbatch");RECEIPT=os.path.join(ROOT,"hpc","GMI_K4_SUBMISSION_RECEIPT_V7.json")
def h(p):return hashlib.sha256(open(p,"rb").read()).hexdigest()
def hhmmss(x):
    s=max(60,int(math.ceil(x/60.0)*60));hh,r=divmod(s,3600);mm,ss=divmod(r,60);return f"{hh:02d}:{mm:02d}:{ss:02d}"
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--account",required=True);ap.add_argument("--partition",required=True);ap.add_argument("--submit",action="store_true");ap.add_argument("--array-concurrency",type=int,default=64);a=ap.parse_args()
    for p in (PROBE,PRED,SCI,EXEC,BEACON,TEMPLATE):
        if not os.path.exists(p):raise SystemExit(f"required V6 artifact absent: {p}")
    pr=json.load(open(PROBE));sci=json.load(open(SCI));ex=json.load(open(EXEC));b=json.load(open(BEACON))
    if pr.get("schema")!="LUNARCEnvProbeV7" or pr.get("status")!="DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED":raise SystemExit("bad V6 probe")
    if sci.get("status")!="FROZEN_BEFORE_V5_PUBLIC_BEACON_AND_ANY_V5_SEARCH_RESULT":raise SystemExit("bad science freeze")
    if ex.get("status")!="FROZEN_BEFORE_K4_V6_BEACON_AND_PROTECTED_EXECUTION":raise SystemExit("bad execution freeze")
    if b.get("schema")!="GMIK4PublicBeaconV6" or b.get("status")!="ACQUIRED_NO_REROLL" or not b.get("sha256_signature_consistency_verified"):raise SystemExit("bad V6 beacon")
    hs={"prediction":h(PRED),"science":h(SCI),"execution":h(EXEC)}
    if pr.get("freeze_hashes")!=hs:raise SystemExit("stale V6 development probe")
    if a.partition not in pr.get("partitions",{}).get("stdout",""):raise SystemExit("partition absent from measured sinfo")
    if a.account not in pr.get("associations",{}).get("stdout",""):raise SystemExit("account absent from measured associations")
    pilot=pr["pilot"];sizing=pr["sizing_rule"];wall=max(float(sizing["minimum_wall_seconds"]),float(pilot["projected_protected_wall_seconds"])*float(sizing["time_safety_factor_on_projected_full_run"]));mem=max(int(sizing["minimum_memory_mib"]),int(math.ceil((max(1.0,float(pilot["peak_rss_kb"]))/1024.0)*float(sizing["memory_safety_factor"]))))
    n=264;conc=max(1,min(a.array_concurrency,n));arr=f"0-{n-1}%{conc}";src=open(TEMPLATE).read();rep={"__ACCOUNT__":a.account,"__PARTITION__":a.partition,"__WALLTIME__":hhmmss(wall),"__MEM__":f"{mem}M","__ARRAY__":arr}
    for x,y in rep.items():src=src.replace(x,y)
    left=sorted(set(re.findall(r"__[A-Z_]+__",src)))
    if left:raise SystemExit(f"unrendered placeholders: {left}")
    open(RENDERED,"w").write(src);rec={"schema":"GMIK4SubmissionReceiptV7","status":"RENDERED_NOT_SUBMITTED","freeze_hashes":hs,"public_beacon_sha256":h(BEACON),"public_beacon_round":b.get("target_round"),"probe_sha256":h(PROBE),"probe_host":pr.get("host"),"account":a.account,"partition":a.partition,"rendered":{"walltime":rep["__WALLTIME__"],"mem_per_cpu":rep["__MEM__"],"array":arr},"rendered_sha256":hashlib.sha256(src.encode()).hexdigest(),"job_id":None,"submitted_at_unix":None,"sbatch_stdout":None,"sbatch_stderr":None}
    if a.submit:
        p=subprocess.run(["sbatch",RENDERED],cwd=ROOT,text=True,capture_output=True);rec["submitted_at_unix"]=time.time();rec["sbatch_stdout"]=p.stdout.strip();rec["sbatch_stderr"]=p.stderr.strip();rec["status"]="SUBMISSION_FAILED" if p.returncode else "SUBMITTED";m=re.search(r"Submitted batch job\s+(\d+)",p.stdout);rec["job_id"]=None if not m else int(m.group(1))
    json.dump(rec,open(RECEIPT,"w"),indent=1,sort_keys=True);print(json.dumps({"status":rec["status"],"job_id":rec["job_id"],"beacon_round":rec["public_beacon_round"],"rendered":rec["rendered"]},sort_keys=True));return 3 if rec["status"]=="SUBMISSION_FAILED" else 0
if __name__=="__main__":raise SystemExit(main())
