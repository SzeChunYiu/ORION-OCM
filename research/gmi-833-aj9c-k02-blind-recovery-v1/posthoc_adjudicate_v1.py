from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BENCH=ROOT/"gmi-833-aj9a-known-family-benchmark-v1"/"KNOWN_FAMILY_BENCHMARK_V1.json"
OUTCOME=HERE/"BLIND_OUTCOME_V1.json"
EXPECTED_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"


def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def run_rows(rows,word):
    s=0; out=[]; states=[s]
    for x in word:
        s,y=rows[2*s+x]; out.append(y); states.append(s)
    return tuple(out),tuple(states)


def inspect(rows):
    # State 0 is initial; state 1 is reachable after input 1.
    reach1=run_rows(rows,(1,))[1][-1]==1
    same_input_diff_output=(rows[0][1]!=rows[2][1])  # input 0 at states 0 vs 1
    update_used=(run_rows(rows,(1,0))[0][-1]!=run_rows(rows,(0,0))[0][-1])
    cycle=(rows[1][0]==1 and rows[2][0]==0)
    updated=(rows[0][0]!=rows[1][0] or rows[2][0]!=rows[3][0])
    exact=True
    words=[()]
    for n in range(1,4):
        import itertools
        words.extend(itertools.product((0,1),repeat=n))
    for w in words:
        prev=0; target=[]
        for x in w: target.append(prev); prev=x
        if run_rows(rows,w)[0]!=tuple(target): exact=False; break
    checks={
      "protected_io":exact,
      "persistent_internal_value_reachable":reach1,
      "matched_current_input_prior_internal_value_changes_output":same_input_diff_output,
      "internal_value_updated":updated,
      "updated_value_causally_used_later":update_used,
      "state_update_cycle":cycle
    }
    return {"pass":all(checks.values()),"checks":checks,
            "same_input_witness":{"input":0,"state0_output":rows[0][1],"state1_output":rows[2][1]},
            "cycle_witness":"0 --input1--> 1 --input0--> 0"}


def main():
    data=BENCH.read_bytes(); assert git_blob_sha(data)==EXPECTED_BLOB
    bench=json.loads(data); family=next(f for f in bench["families"] if f["family_id"]=="K02")
    outcome=json.loads(OUTCOME.read_text())
    rows1=tuple(tuple(r) for r in outcome["search_1"]["solution_rows"])
    rows2=tuple(tuple(r) for r in outcome["search_2"]["solution_rows"])
    assert rows1==rows2
    i1=inspect(rows1); i2=inspect(rows2)
    result={
      "schema":"AJ9C_POSTHOC_ADJUDICATION_V1",
      "benchmark_blob":EXPECTED_BLOB,
      "family_id":"K02",
      "paper_name":family["paper_name"],
      "adjudication_started_after_blind_outcome":True,
      "search_1":i1,"search_2":i2,
      "frozen_required_clause_count":len(family["posthoc_fingerprint"]["required"]),
      "frozen_observation_test_count":len(family["minimum_observation_tests"]),
      "terminal":"RECOVERED" if i1["pass"] and i2["pass"] else "NOT_RECOVERED_AT_SCOPE"
    }
    (HERE/"POSTHOC_RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
