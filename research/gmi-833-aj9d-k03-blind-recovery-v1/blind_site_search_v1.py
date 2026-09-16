from __future__ import annotations
import itertools, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BITS=(0,1)
STATES=tuple(itertools.product(BITS,repeat=3))


def target(site,state):
    return int(state[site] != state[(site+1)%3])


def target_vector(site): return tuple(target(site,s) for s in STATES)


def table_eval(vector,state):
    idx=(state[0]<<2)|(state[1]<<1)|state[2]
    return vector[idx]


def full_global_truth_search():
    results=[]; checked=0
    for site in range(3):
        want=target_vector(site); hits=[]
        for vec in itertools.product(BITS,repeat=8):
            checked+=1
            if vec==want: hits.append(vec)
        assert len(hits)==1
        # Generic exact dependency audit: bit j matters iff some matched-context flip changes output.
        deps=[]
        for j in range(3):
            matters=False
            for s in STATES:
                t=list(s); t[j]=1-t[j]; t=tuple(t)
                if table_eval(hits[0],s)!=table_eval(hits[0],t): matters=True; break
            if matters: deps.append(j)
        results.append({"site":site,"global_vector":hits[0],"exact_dependencies":deps})
    return {"functions_checked":checked,"outputs":results}


def eval_subset(subset,table,state):
    idx=0
    for j in subset: idx=(idx<<1)|state[j]
    return table[idx]


def minimum_dependency_search():
    outputs=[]; candidates_checked=0
    for site in range(3):
        want=target_vector(site); found=[]
        for k in range(4):
            for subset in itertools.combinations(range(3),k):
                for table in itertools.product(BITS,repeat=(1<<k)):
                    candidates_checked+=1
                    got=tuple(eval_subset(subset,table,s) for s in STATES)
                    if got==want: found.append((subset,table))
            if found: break
        assert len(found)==1
        subset,table=found[0]
        outputs.append({"site":site,"dependency_subset":subset,"table":table,"dependency_count":len(subset)})
    return {"candidates_checked":candidates_checked,"outputs":outputs}


def canonical_rule_tables(outputs):
    return tuple(tuple(o["table"]) for o in outputs)


def main():
    a=full_global_truth_search(); b=minimum_dependency_search()
    assert a["functions_checked"]==768
    for x,y in zip(a["outputs"],b["outputs"]):
        assert tuple(x["exact_dependencies"])==tuple(y["dependency_subset"])
        assert len(x["exact_dependencies"])==2
    tables=canonical_rule_tables(b["outputs"])
    assert len(set(tables))==1
    assert tables[0]==(0,1,1,0)
    deps=tuple(tuple(o["dependency_subset"]) for o in b["outputs"])
    assert deps==((0,1),(1,2),(0,2))
    result={
      "schema":"AJ9D_BLIND_SITE_OUTCOME_V1",
      "status":"SEARCH_COMPLETE",
      "global_states":len(STATES),
      "search_1":{"id":"FULL_GLOBAL_TRUTH_TABLE_ENUMERATION","presentation":"GLOBAL_TRUTH_VECTOR",**a},
      "search_2":{"id":"MINIMUM_DEPENDENCY_SYNTHESIS","presentation":"SUBSET_PLUS_LOCAL_TABLE",**b},
      "minimum_dependency_counts":[o["dependency_count"] for o in b["outputs"]],
      "distinct_minimal_rule_tables":len(set(tables)),
      "minimal_rule_table":tables[0],
      "raw_resource_vector":{"dependency_count_per_output":[2,2,2],"truth_rows_per_output":[4,4,4],"distinct_semantic_rule_tables_after_coordinate_alignment":1},
      "registry_data_used":False
    }
    (HERE/"BLIND_OUTCOME_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
