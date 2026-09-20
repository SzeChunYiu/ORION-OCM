#!/usr/bin/env python3
import copy
import importlib.util
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("gov",ROOT/"check_governance_v2.py")
gov=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gov)

def need(cond,msg):
    if not cond:
        raise RuntimeError(msg)

def load(name):
    return json.loads((ROOT/name).read_text())

def rejected(dag,stat,add):
    try:
        gov.validate(dag,stat,add)
    except Exception:
        return True
    return False

def main():
    dag=load("DEPENDENCY_DAG_V2.json")
    stat=load("ROUND_STATUS_V2.json")
    add=load("R17_ATOMIC_ADDENDUM_V2.json")
    gov.validate(dag,stat,add)

    d1=copy.deepcopy(dag)
    d1["dependencies"]["R0"]=["R17"]
    need(rejected(d1,stat,add),"HOSTILE_CYCLE_NOT_CAUGHT")

    s1=copy.deepcopy(stat)
    s1["rounds"]["R5"]={"status":"EARNED","evidence":["forged"]}
    need(rejected(dag,s1,add),"HOSTILE_FALSE_REEARN_NOT_CAUGHT")

    s2=copy.deepcopy(stat)
    s2["rounds"]["R8"]={"status":"EARNED","evidence":["forged"]}
    need(rejected(dag,s2,add),"HOSTILE_EARNED_DESCENDANT_NOT_CAUGHT")

    s3=copy.deepcopy(stat)
    s3["rounds"]["R9"]={"status":"IN_PROGRESS","evidence":["forged"]}
    need(rejected(dag,s3,add),"HOSTILE_STALE_PARENT_START_NOT_CAUGHT")

    a1=copy.deepcopy(add)
    a1["rows"][0]["id"]="GMI2-R17-999"
    need(rejected(dag,stat,a1),"HOSTILE_R17_ID_DRIFT_NOT_CAUGHT")

    touched=gov.infer_rounds([
        "research/gmi-1068-r4-equivalence-state-quotient-v1/THEORY_V2.md",
        ".github/workflows/gmi-1068-r5-successor-v2.yml",
        "research/gmi-1068-governance-v2/ROUND_STATUS_V2.json"
    ])
    need(touched=={"R4","R5"},f"ROUND_INFERENCE:{touched}")

    print(json.dumps({"status":"GREEN","hostiles_caught":5,"round_inference":sorted(touched)},sort_keys=True))

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("GOVERNANCE_V2_TEST_RED:"+repr(exc),file=sys.stderr)
        sys.exit(1)
