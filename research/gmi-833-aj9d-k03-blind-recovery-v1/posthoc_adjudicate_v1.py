from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BENCH=ROOT/"gmi-833-aj9a-known-family-benchmark-v1"/"KNOWN_FAMILY_BENCHMARK_V1.json"
OUTCOME=HERE/"BLIND_OUTCOME_V1.json"
EXPECTED_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"
BITS=(0,1)
STATES=tuple(itertools.product(BITS,repeat=3))


def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def eval_table(subset,table,state):
    idx=0
    for j in subset: idx=(idx<<1)|state[j]
    return table[idx]


def inspect(outputs):
    by_site={o["site"]:o for o in outputs}
    local_neighbors=True; shared=True; remote_no_effect=True; relabel=True
    tables=[]
    for i in range(3):
        o=by_site[i]; subset=tuple(o["dependency_subset"]); table=tuple(o["table"])
        expected=set((i,(i+1)%3))
        local_neighbors &= set(subset)==expected
        tables.append(table)
        remote=({0,1,2}-expected).pop()
        for s in STATES:
            t=list(s); t[remote]=1-t[remote]; t=tuple(t)
            remote_no_effect &= eval_table(subset,table,s)==eval_table(subset,table,t)
    shared=(len(set(tables))==1)
    # Rotation equivariance under old site i -> new site i+1.
    for s in STATES:
        rotated=(s[2],s[0],s[1])
        y=[]; yr=[]
        for i in range(3):
            o=by_site[i]; y.append(eval_table(tuple(o["dependency_subset"]),tuple(o["table"]),s))
            r=by_site[(i+1)%3]; yr.append(eval_table(tuple(r["dependency_subset"]),tuple(r["table"]),rotated))
        # Output at new site i+1 equals output at original site i.
        relabel &= all(yr[i]==y[i] for i in range(3))
    # Same local 2-bit pattern produces same response at every site: enumerate matched pairs.
    same_local=True
    canonical=tables[0]
    for pair in itertools.product(BITS,repeat=2):
        expected=canonical[(pair[0]<<1)|pair[1]]
        for i in range(3):
            state=[0,0,0]; state[i]=pair[0]; state[(i+1)%3]=pair[1]
            o=by_site[i]
            same_local &= eval_table(tuple(o["dependency_subset"]),tuple(o["table"]),tuple(state))==expected
    checks={
      "common_transform_multiple_sites":shared,
      "registered_local_neighborhood_only":local_neighbors and remote_no_effect,
      "site_relabel_rotation_covariance":relabel,
      "same_local_pattern_same_transform":same_local,
      "remote_non_neighbor_no_one_step_effect":remote_no_effect
    }
    return {"pass":all(checks.values()),"checks":checks,"shared_rule_table":canonical,
            "dependency_sets":[by_site[i]["dependency_subset"] for i in range(3)]}


def main():
    data=BENCH.read_bytes(); assert git_blob_sha(data)==EXPECTED_BLOB
    family=next(f for f in json.loads(data)["families"] if f["family_id"]=="K03")
    outcome=json.loads(OUTCOME.read_text())
    inspection=inspect(outcome["search_2"]["outputs"])
    deps1=[o["exact_dependencies"] for o in outcome["search_1"]["outputs"]]
    deps2=[o["dependency_subset"] for o in outcome["search_2"]["outputs"]]
    agreement=(deps1==deps2)
    result={
      "schema":"AJ9D_POSTHOC_ADJUDICATION_V1",
      "benchmark_blob":EXPECTED_BLOB,
      "family_id":"K03",
      "paper_name":family["paper_name"],
      "adjudication_started_after_blind_outcome":True,
      "inspection":inspection,
      "cross_search_dependency_agreement":agreement,
      "frozen_required_clause_count":len(family["posthoc_fingerprint"]["required"]),
      "frozen_observation_test_count":len(family["minimum_observation_tests"]),
      "terminal":"RECOVERED" if inspection["pass"] and agreement else "NOT_RECOVERED_AT_SCOPE"
    }
    (HERE/"POSTHOC_RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
