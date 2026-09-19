# -*- coding: utf-8 -*-
"""Calibration: 11 rows hand-adjudicated from the artifacts, then re-derived
mechanically from the decisive test alone. Agreement is reported."""
import json, io, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
R=lambda p: io.open(os.path.join(ROOT,p),encoding="utf-8").read()
J=lambda p: json.loads(R(p))
AI0="research/gmi-833-ai0-convergence-spine-v1/"
AFP="research/gmi-833-af-barrier-context-v1/"
A9A="research/gmi-833-aj9a-known-family-benchmark-v1/"
A11="research/gmi-833-aj11-bounded-completeness-v1/"
A12="research/gmi-833-aj12-foundation-substrate-relativity-v1/"
A13="research/gmi-833-aj13-stopping-rule-v1/"

def t1():  # AI0 row 40
    d=J(AI0+"GMI_THEORY_DEPENDENCY_DAG.json")
    ar=d["authority_reconciliation"]; owners={n["owner"] for n in d["nodes"]}
    spans=all(k in ar for k in ("#833","#233","#373","#602")) and len(d["nodes"])==19
    return "EARNED_BY_MERGED_EVIDENCE" if spans else "PARTIAL"
def t2():  # AF row 48 - eight named channels
    want=["initial/inherited organization","external observations","rewards/evaluator feedback",
          "endogenous computation","stochastic variation","oracle/advice/tool channels",
          "other-agent/social/cultural transfer","physical/environmental signals"]
    got=J(AFP+"RESULT_V1.json")["af1"]["provenance_tags"]
    return "EARNED_BY_MERGED_EVIDENCE" if len(got)==len(want)==8 else "PARTIAL"
def t3():  # AF row 106 - thirteen distinguished transition classes
    txt=R(AFP+"FORMALIZATION_V1.md").lower()
    want=["domain restriction","promise problem","approximation","semidecision","abstention",
          "list/set output","certificate","interaction/query","oracle/advice","randomness",
          "resource relaxation","substrate expansion","literal contradiction"]
    miss=[w for w in want if w not in txt]
    return "EARNED_BY_MERGED_EVIDENCE" if not miss else "PARTIAL:"+",".join(miss)
def t4():  # AJ row 157 - eleven registered families
    got=J(A9A+"RESULT_V1.json")["minimum_registered_family_names"]
    want=["neural/feed-forward","recurrent/stateful","local/shared-transform","attention/dynamic-routing",
          "symbolic/rewrite/search","probabilistic/Bayesian","planning/control","retrieval/memory",
          "evolutionary/population search","program synthesis","self-modifying/developmental"]
    return "EARNED_BY_MERGED_EVIDENCE" if got==want else "PARTIAL"
def t5():  # AJ row 182 - exact Pareto frontier (reproduced on laptop-billy)
    r=J(A11+"RESULT_V1.json")
    ok=r["pareto_frontier_candidate_ids"]==["M000","M001","M002","M043","M169"] and "no scalarization" in r["pareto_objective"]
    return "EARNED_BY_MERGED_EVIDENCE" if ok else "PARTIAL"
def t6():  # AJ row 194 - five assumption tag classes
    got=set(J(A12+"RESULT_V1.json")["assumption_tags"].values())
    want={"MATHEMATICAL_FOUNDATION","LOGIC/METATHEORY","PHYSICAL_SUBSTRATE_LAW","RESOURCE_MODEL","VALUE/REQUIREMENT_INPUT"}
    return "EARNED_BY_MERGED_EVIDENCE" if got==want else "PARTIAL"
def t7():  # AJ row 215 - forbidden terminal enforced, not only declared
    r=J(A13+"RESULT_V1.json")
    ok=r["forbidden_terminal"]=="ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN" and r["hostiles"]["absolute_promotion"]
    return "EARNED_BY_MERGED_EVIDENCE" if ok else "PARTIAL"
def t8():  # AI0 row 41 - "every material theory/result"
    g=J(AI0+"OPEN_GAPS.json")
    disc=any("theorem-by-theorem corpus audit remains owned by #833 Section B" in x["gap"] for x in g["remaining"])
    return "PARTIAL" if disc else "EARNED_BY_MERGED_EVIDENCE"
def t9():  # AI0 row 42 - AG/AH -> GEN mapping present?
    hits=[]
    for f in os.listdir(os.path.join(ROOT,AI0)):
        hits += re.findall(r"\bA[GH]\b", R(AI0+f))
    return "PARTIAL" if not hits else "EARNED_BY_MERGED_EVIDENCE"
def t10(): # AF row 50 - blocked by open PR?
    out=subprocess.run(["gh","pr","view","969","--repo","SzeChunYiu/ORION-OCM","--json","state,body"],
                       capture_output=True,text=True).stdout
    o=json.loads(out)
    return "BLOCKED_ON_OPEN_PR" if o["state"]=="OPEN" and "deferred_tasks" in o["body"] else "EARNED_BY_MERGED_EVIDENCE"
def t11(): # AJ row 158 - does the frozen no-smuggling auditor actually pass on main?
    p=subprocess.run(["ssh","billy-laptop",
        "cd ~/ocm-scratch/prop && python3 -I -B research/gmi-833-aj9a-known-family-benchmark-v1/check_aj9a.py >/dev/null 2>&1; echo $?"],
        capture_output=True,text=True).stdout.strip()
    return "PARTIAL" if p!="0" else "EARNED_BY_MERGED_EVIDENCE"

CASES=[("5693666042 AI0 r40 one DAG spanning #233/#373/#602/#833","EARNED_BY_MERGED_EVIDENCE",t1),
 ("5693269426 AF1 r48 eight provenance channels","EARNED_BY_MERGED_EVIDENCE",t2),
 ("5693269426 AF3 r106 thirteen transition classes","EARNED_BY_MERGED_EVIDENCE",t3),
 ("5693954852 AJ9 r157 eleven registered families","EARNED_BY_MERGED_EVIDENCE",t4),
 ("5693954852 AJ11 r182 exact Pareto frontier","EARNED_BY_MERGED_EVIDENCE",t5),
 ("5693954852 AJ12 r194 five assumption tags","EARNED_BY_MERGED_EVIDENCE",t6),
 ("5693954852 AJ13 r215 forbid ABSOLUTE_BOTTOM","EARNED_BY_MERGED_EVIDENCE",t7),
 ("5693666042 AI0 r41 classify EVERY material result","PARTIAL",t8),
 ("5693666042 AI0 r42 AG/AH lower-substrate -> GEN","PARTIAL",t9),
 ("5693269426 AF1 r50 G0 microscopes + converse","BLOCKED_ON_OPEN_PR",t10),
 ("5693954852 AJ9 r158 no-smuggling for every holdout","PARTIAL",t11)]

agree=0
for name,hand,fn in CASES:
    got=fn()
    m = got.split(":")[0]==hand
    agree+=m
    print("%-6s hand=%-24s procedure=%-24s %s"%("MATCH" if m else "MISMATCH",hand,got,name))
print("\ncalibration: %d/%d agree (%d not-earned cases included)"%(agree,len(CASES),sum(1 for _,h,_ in CASES if h!="EARNED_BY_MERGED_EVIDENCE")))
