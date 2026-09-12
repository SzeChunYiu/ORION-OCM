#!/usr/bin/env python3
"""Render (and optionally submit) the protected K5 B-H revival V8 array. Sizing is fixed from the V8 execution freeze
(development max wall 0.79 s, peak RSS 22 MB; rendered 00:10:00 / 512M). Verifies the V8 beacon contract first."""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess,sys,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:sys.path.insert(0,ROOT)
EXEC=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V8.json");PLAN=os.path.join(ROOT,"GMI_K5_BH_REVIVAL_PLAN_V8.json");BEACON=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V8.json");TEMPLATE=os.path.join(ROOT,"hpc","gmi_k5_bh_array_v8.sbatch");RENDERED=os.path.join(ROOT,"hpc","gmi_k5_bh_array_v8.rendered.sbatch");RECEIPT=os.path.join(ROOT,"hpc","GMI_K5_BH_SUBMISSION_RECEIPT_V8.json")
def h(p):return hashlib.sha256(open(p,"rb").read()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--account",required=True);ap.add_argument("--partition",required=True);ap.add_argument("--submit",action="store_true");ap.add_argument("--array-concurrency",type=int,default=80);a=ap.parse_args()
    for p in (EXEC,PLAN,BEACON,TEMPLATE):
        if not os.path.exists(p):raise SystemExit(f"missing {p}")
    ex=json.load(open(EXEC));b=json.load(open(BEACON))
    if ex.get("status")!="FROZEN_BEFORE_K5_V8_BEACON_AND_PROTECTED_EXECUTION":raise SystemExit("bad V8 freeze")
    if ex.get("plan_sha256")!=h(PLAN):raise SystemExit("freeze does not pin the current plan")
    from hpc.gmi_beacon_verify import verify_beacon
    verified=verify_beacon(repo_root=ROOT,freeze_path=EXEC,beacon=b,expected_schema="GMIK5BHPublicBeaconV8")
    sz=ex["sizing_basis"]["rendered"];n=int(ex["expected_tasks"]);arr=f"0-{n-1}%{max(1,min(a.array_concurrency,n))}";src=open(TEMPLATE).read();rep={"__ACCOUNT__":a.account,"__PARTITION__":a.partition,"__WALLTIME__":sz["walltime"],"__MEM__":sz["mem_per_cpu"],"__ARRAY__":arr}
    for x,y in rep.items():src=src.replace(x,y)
    if re.findall(r"__[A-Z_]+__",src):raise SystemExit("unrendered placeholders")
    open(RENDERED,"w").write(src);rec={"schema":"GMIK5BHSubmissionReceiptV8","status":"RENDERED_NOT_SUBMITTED","execution_freeze_sha256":h(EXEC),"plan_sha256":h(PLAN),"public_beacon_sha256":h(BEACON),"verified_beacon_contract":verified,"account":a.account,"partition":a.partition,"rendered":{"walltime":sz["walltime"],"mem_per_cpu":sz["mem_per_cpu"],"array":arr},"job_id":None}
    if a.submit:
        p=subprocess.run(["sbatch",RENDERED],cwd=ROOT,text=True,capture_output=True);rec["status"]="SUBMISSION_FAILED" if p.returncode else "SUBMITTED";rec["sbatch_stdout"]=p.stdout.strip();rec["sbatch_stderr"]=p.stderr.strip();m=re.search(r"Submitted batch job\s+(\d+)",p.stdout);rec["job_id"]=None if not m else int(m.group(1));rec["submitted_at_unix"]=time.time()
    json.dump(rec,open(RECEIPT,"w"),indent=1,sort_keys=True);print(json.dumps({"status":rec["status"],"job_id":rec.get("job_id"),"beacon_round":verified["target_round"]}))
if __name__=="__main__":main()
