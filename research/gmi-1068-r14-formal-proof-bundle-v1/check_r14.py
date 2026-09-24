#!/usr/bin/env python3
import json,pathlib,sys,re
HERE=pathlib.Path(__file__).resolve().parent
RESEARCH=HERE.parent
def need(cond,msg):
    if not cond: raise RuntimeError(msg)
r13=json.loads((RESEARCH/"gmi-1068-r13-real-scale-evidence-adjudication-v1/RESULT_V1.json").read_text())
need(r13["unearned_external_gates"]==3,"R13_EXTERNAL_GAPS_NOT_PRESERVED")
cov=json.loads((HERE/"FORMAL_COVERAGE_V1.json").read_text())
need(cov["lean_version"]=="4.19.0","LEAN_VERSION")
need(len(cov["theorem_bundle"])==12,"FORMAL_BUNDLE_COUNT")
src=(HERE/"GrandGMI.lean").read_text()
for fid,_,_ in cov["theorem_bundle"]:
    need(fid in src,"MISSING_FORMAL_ID:"+fid)
need(len(cov["empirical_claims_not_proved_by_kernel"])>=4,"EMPIRICAL_BOUNDARY")
res=json.loads((HERE/"RESULT_V1.json").read_text())
need(res["flagship_items"]==12,"RESULT_ITEM_COUNT")
need(res["status"] in {"PENDING_CI_KERNEL_CHECK_UNTIL_WORKFLOW_GREEN","GREEN_KERNEL_CHECKED_FLAGSHIP_BUNDLE"},"RESULT_STATUS")
print(json.dumps({"status":"GREEN_MANIFEST","formal_items":12,"lean_version":"4.19.0","external_empirical_gaps":3},sort_keys=True))
