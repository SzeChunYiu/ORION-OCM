from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BENCH=ROOT/"gmi-833-aj9a-known-family-benchmark-v1"/"KNOWN_FAMILY_BENCHMARK_V1.json"
OUTCOME=HERE/"BLIND_OUTCOME_V1.json"
EXPECTED_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"


def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def tup(x): return tuple(tup(y) for y in x) if isinstance(x,list) else x


def eval_ast(e,c,a,b):
    op=e[0]
    if op=="v": return (c,a,b)[e[1]]
    if op=="k": return e[1]
    if op=="not": return 1-eval_ast(e[1],c,a,b)
    x=eval_ast(e[1],c,a,b); y=eval_ast(e[2],c,a,b)
    return (x & y) if op=="and" else (x | y)


def inspect_ast(e):
    expected=("or",("and",("not",("v",0)),("v",1)),("and",("v",0),("v",2)))
    explicit_two_branch=(e==expected)
    # Influence of A/B under fixed context, exact Boolean derivative tests.
    infl_a_c0=eval_ast(e,0,0,0)!=eval_ast(e,0,1,0)
    infl_a_c1=eval_ast(e,1,0,0)!=eval_ast(e,1,1,0)
    infl_b_c0=eval_ast(e,0,0,0)!=eval_ast(e,0,0,1)
    infl_b_c1=eval_ast(e,1,0,0)!=eval_ast(e,1,0,1)
    context_changes_influence=infl_a_c0 and not infl_a_c1 and not infl_b_c0 and infl_b_c1
    two_sources_dominate=(eval_ast(e,0,1,0)==1 and eval_ast(e,1,1,0)==0 and eval_ast(e,0,0,1)==0 and eval_ast(e,1,0,1)==1)
    checks={
      "context_dependent_branch_quantities_computed":explicit_two_branch,
      "source_influence_changes_with_context":context_changes_influence,
      "selected_source_information_aggregated":explicit_two_branch,
      "two_candidate_sources_dominate_in_different_contexts":two_sources_dominate
    }
    return {"pass":all(checks.values()),"checks":checks,
      "influence":{"A_at_C0":infl_a_c0,"A_at_C1":infl_a_c1,"B_at_C0":infl_b_c0,"B_at_C1":infl_b_c1}}


def inspect_dnf(cubes):
    cube_set={tuple(c) for c in cubes}
    expected={(0,1,-1),(1,-1,1)}
    return {"pass":cube_set==expected,"context_conditioned_cubes":sorted(cube_set)}


def main():
    data=BENCH.read_bytes(); assert git_blob_sha(data)==EXPECTED_BLOB
    family=next(f for f in json.loads(data)["families"] if f["family_id"]=="K04")
    outcome=json.loads(OUTCOME.read_text())
    a=inspect_ast(tup(outcome["search_1"]["expression"]))
    b=inspect_dnf(outcome["search_2"]["cubes"])
    result={
      "schema":"AJ9E_POSTHOC_ADJUDICATION_V1","benchmark_blob":EXPECTED_BLOB,
      "family_id":"K04","paper_name":family["paper_name"],"adjudication_started_after_blind_outcome":True,
      "search_1":a,"search_2":b,
      "frozen_required_clause_count":len(family["posthoc_fingerprint"]["required"]),
      "frozen_observation_test_count":len(family["minimum_observation_tests"]),
      "terminal":"RECOVERED" if a["pass"] and b["pass"] else "NOT_RECOVERED_AT_SCOPE"
    }
    (HERE/"POSTHOC_RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
