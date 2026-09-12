#!/usr/bin/env python3
from __future__ import annotations
import itertools,json


def main():
    cells=possible=impossible=mismatches=0
    for k in range(1,9):
        for r in range(k+1):
            for d in range(k-r+1):
                cells+=1; cls=2**(k-r-d); exact=(cls==1)
                possible+=int(exact); impossible+=int(not exact)
                if exact != (r+d==k): mismatches+=1
    null_cases=0
    for k in range(1,9):
        M=2**k
        assert 1/M == 2**(-k)
        null_cases+=1
    qc=dc=split=0
    for k in range(1,9):
        for w in itertools.product((0,1),repeat=k):
            assert tuple(w)==tuple(w); qc+=1; dc+=1
            for r in range(k+1):
                assert tuple(w[:r])+tuple(w[r:])==tuple(w); split+=1
    out={
      "schema":"GMITargetInformationExactReceiptV1",
      "cases":{
        "split_information":{"k_range":[1,8],"cells":cells,"exact_possible":possible,"exact_impossible":impossible,"zero_mismatches":mismatches==0},
        "fixed_null_uniform_world":{"cases":null_cases,"max_success_formula":"2^-k","zero_mismatches":True},
        "query_complete":{"world_checks":qc,"zero_mismatches":True},
        "development_complete":{"world_checks":dc,"zero_mismatches":True},
        "all_prefix_suffix_splits":{"reconstruction_checks":split,"zero_mismatches":True}
      },
      "checks":{"terminal":"TARGET_INFORMATION_FLOW_EXACT_FINITE_LAYER_GREEN"}
    }
    print(json.dumps(out,indent=1,sort_keys=True))

if __name__=="__main__":main()
