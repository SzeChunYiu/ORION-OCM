#!/usr/bin/env python3
import json,pathlib,sys,itertools
ROOT=pathlib.Path(__file__).resolve().parent
def need(cond,msg):
 if not cond: raise RuntimeError(msg)
r12=json.loads((ROOT.parent/"gmi-1068-r12-ai-findings-registry-v1/RESULT_V1.json").read_text())
need(r12["status"]=="GREEN_CANONICAL_FINDING_REGISTRY_SCOPE","R12_PARENT_NOT_GREEN")
acts=list(itertools.product((-1,1),repeat=2));ends={a:sum(a) for a in acts};best=[a for a,v in ends.items() if v==2]
need(best==[(1,1)],"INTERACTIVE")
post=[0,1];stationary=sum(x==(1-x) for x in post);adaptive=sum((1-x)==(1-x) for x in post)
need(stationary==0 and adaptive==2,"NONSTATIONARY")
worlds=list(itertools.product((0,1),repeat=2));no_comm=False
for o0,o1 in itertools.product((0,1),repeat=2):
 if all((o0,o1)[a]==(a^b) for a,b in worlds):no_comm=True
need(not no_comm,"MULTIAGENT_NO_COMM")
need(all((a^b)==(a^b) for a,b in worlds),"MULTIAGENT_WITH_COMM")
ev=json.loads((ROOT/"EVIDENCE_LEDGER_V1.json").read_text());adj=json.loads((ROOT/"GATE_ADJUDICATION_V1.json").read_text());res=json.loads((ROOT/"RESULT_V1.json").read_text())
need(ev["imported"][0]["scale"]["H01"]["n_fit"]==466750,"FIT")
need(ev["imported"][0]["scale"]["H01"]["n_held"]==155583,"HELD")
need(ev["imported"][2]["systems"]==9 and ev["imported"][2]["qualifying_count"]==5,"TRANSITIONS")
unearned=[g for g in adj["gates"] if g["status"].startswith("UNEARNED")]
need(len(unearned)==3,"UNEARNED_COUNT")
need(res["unearned_external_gates"]==3 and res["status"].startswith("PARTIAL_"),"RESULT")
print(json.dumps({"status":"GREEN_ADJUDICATION","interactive_best":"++","nonstationary_stationary_score":stationary,"nonstationary_adaptive_score":adaptive,"multiagent_no_comm_possible":False,"real_transition_systems":9,"qualifying":5,"unearned_external_gates":[g["name"] for g in unearned]},sort_keys=True))
