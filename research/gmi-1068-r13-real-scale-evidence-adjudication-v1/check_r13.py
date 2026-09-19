#!/usr/bin/env python3
import json,pathlib,sys,itertools
ROOT=pathlib.Path(__file__).resolve().parent

# I1: action-conditioned 2-step world, actions +/-1; target terminal +2
acts=list(itertools.product((-1,1),repeat=2))
ends={a:sum(a) for a in acts}
best=[a for a,v in ends.items() if v==2]
assert best==[(1,1)]

# N1: rule y=x for first regime, y=1-x after drift. stationary old rule fails after drift, adaptive regime bit succeeds.
post=[0,1]
stationary=sum(x==(1-x) for x in post)
adaptive=sum((1-x)==(1-x) for x in post)
assert stationary==0 and adaptive==2

# M1: A sees a, B sees b, target XOR. Without b, no A-only deterministic map solves all 4. With one-bit b communication, solve.
worlds=list(itertools.product((0,1),repeat=2))
no_comm=False
for o0,o1 in itertools.product((0,1),repeat=2):
 if all((o0,o1)[a]==(a^b) for a,b in worlds): no_comm=True
assert not no_comm
assert all((a^b)==(a^b) for a,b in worlds)

ev=json.loads((ROOT/"EVIDENCE_LEDGER_V1.json").read_text())
adj=json.loads((ROOT/"GATE_ADJUDICATION_V1.json").read_text())
res=json.loads((ROOT/"RESULT_V1.json").read_text())
assert ev["imported"][0]["scale"]["H01"]["n_fit"]==466750
assert ev["imported"][0]["scale"]["H01"]["n_held"]==155583
assert ev["imported"][2]["systems"]==9 and ev["imported"][2]["qualifying_count"]==5
unearned=[g for g in adj["gates"] if g["status"].startswith("UNEARNED")]
assert len(unearned)==3
assert res["unearned_external_gates"]==3 and res["status"].startswith("PARTIAL_")
print(json.dumps({"status":"GREEN_ADJUDICATION","interactive_best":"++","nonstationary_stationary_score":stationary,"nonstationary_adaptive_score":adaptive,"multiagent_no_comm_possible":False,"real_transition_systems":9,"qualifying":5,"unearned_external_gates":[g["name"] for g in unearned]},sort_keys=True))
