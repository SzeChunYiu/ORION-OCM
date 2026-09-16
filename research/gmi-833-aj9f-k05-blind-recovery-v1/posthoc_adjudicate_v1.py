from __future__ import annotations
import hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BENCH=ROOT/"gmi-833-aj9a-known-family-benchmark-v1"/"KNOWN_FAMILY_BENCHMARK_V1.json"
OUTCOME=HERE/"BLIND_OUTCOME_V1.json"
EXPECTED_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"

def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def tup(x): return tuple(tup(v) for v in x) if isinstance(x,list) else x

def parse_prefix(tokens,i=0):
    tok=tokens[i]
    if tok!="N": return tok,i+1
    l,j=parse_prefix(tokens,i+1); r,k=parse_prefix(tokens,j); return ("N",l,r),k

def leaves_without_e(t):
    if not isinstance(t,tuple): return () if t=="E" else (t,)
    return leaves_without_e(t[1])+leaves_without_e(t[2])

def compositional(t): return isinstance(t,tuple) and t and t[0]=="N" and (isinstance(t[1],tuple) or isinstance(t[2],tuple))

def inspect(outcome):
    p1=[tup(x) for x in outcome["search_1"]["path"]]
    p2=[]
    for tokens in outcome["search_2"]["path"]:
        t,end=parse_prefix(tuple(tokens)); assert end==len(tokens); p2.append(t)
    sem1=[leaves_without_e(t) for t in p1]; sem2=[leaves_without_e(t) for t in p2]
    invariant=(len(set(sem1))==1 and len(set(sem2))==1 and sem1[0]==("A","B") and sem2[0]==("A","B"))
    multi=(len(p1)>=3 and len(p2)>=3)
    branch=(outcome["search_1"]["branching_at_start"]>=2 and outcome["search_2"]["branching_at_start"]>=2)
    local_rule_tags=all("DROP_" in tag for tag in outcome["search_1"]["tags"]+outcome["search_2"]["tags"])
    different_control=(outcome["search_1"]["tags"][0]!=outcome["search_2"]["tags"][0])
    structured=compositional(p1[0]) and compositional(p2[0])
    exact_goal=(p1[-1]==("N","A","B") and p2[-1]==("N","A","B"))
    checks={
      "explicit_compositional_discrete_state":structured,
      "local_rule_based_transformations":local_rule_tags,
      "multi_step_semantics_preserving_derivation":multi and invariant,
      "multiple_legal_successors_from_one_state":branch,
      "control_selects_among_derivation_paths":different_control,
      "protected_goal_reached":exact_goal
    }
    return {"pass":all(checks.values()),"checks":checks,"semantic_trace_1":[list(x) for x in sem1],"semantic_trace_2":[list(x) for x in sem2]}

def main():
    data=BENCH.read_bytes(); assert git_blob_sha(data)==EXPECTED_BLOB
    family=next(f for f in json.loads(data)["families"] if f["family_id"]=="K05")
    outcome=json.loads(OUTCOME.read_text()); ins=inspect(outcome)
    result={"schema":"AJ9F_POSTHOC_ADJUDICATION_V1","benchmark_blob":EXPECTED_BLOB,"family_id":"K05","paper_name":family["paper_name"],
      "adjudication_started_after_blind_outcome":True,"inspection":ins,
      "frozen_required_clause_count":len(family["posthoc_fingerprint"]["required"]),"frozen_observation_test_count":len(family["minimum_observation_tests"]),
      "terminal":"RECOVERED" if ins["pass"] else "NOT_RECOVERED_AT_SCOPE"}
    (HERE/"POSTHOC_RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n"); print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
