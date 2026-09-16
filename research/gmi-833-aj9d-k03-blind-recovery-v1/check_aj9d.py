from __future__ import annotations
import hashlib, importlib.util, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FREEZE_COMMIT="23924380bcffcb52e056e52735fa0e83349d8bb1"
BENCH_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def main():
    blind_path=HERE/"blind_site_search_v1.py"; src=blind_path.read_text().casefold()
    forbidden=["convolution","convnet","cnn","shared-transform","k03","known_family_benchmark","posthoc_fingerprint","family_id","weight-sharing"]
    hits=[x for x in forbidden if x in src]
    assert not hits, hits
    assert "read_text(" not in src and "read_bytes(" not in src and "open(" not in src

    prefix="research/gmi-833-aj9d-k03-blind-recovery-v1/"
    subprocess.run(["git","merge-base","--is-ancestor",FREEZE_COMMIT,"HEAD"],check=True)
    for n in ("SEARCH_CONFIG_V1.json","FREEZE_V1.md"):
        subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{n}"],check=True)
    for n in ("blind_site_search_v1.py","BLIND_OUTCOME_V1.json","posthoc_adjudicate_v1.py","POSTHOC_RESULT_V1.json"):
        p=subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{n}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        assert p.returncode!=0, n

    cfg=json.loads((HERE/"SEARCH_CONFIG_V1.json").read_text())
    assert cfg["candidate_space"]["full_functions_per_output"]==256
    assert len(cfg["searches"])==2 and len(cfg["presentations"])==2
    assert cfg["evaluation"]["no_family_score"] is True

    blind=load_module("blind_site_search_v1",blind_path)
    a=blind.full_global_truth_search(); b=blind.minimum_dependency_search()
    committed=json.loads((HERE/"BLIND_OUTCOME_V1.json").read_text())
    assert a["functions_checked"]==committed["search_1"]["functions_checked"]==768
    assert b["candidates_checked"]==committed["search_2"]["candidates_checked"]==186
    deps1=[o["exact_dependencies"] for o in a["outputs"]]
    deps2=[list(o["dependency_subset"]) for o in b["outputs"]]
    assert deps1==deps2==[[0,1],[1,2],[0,2]]
    tables=[tuple(o["table"]) for o in b["outputs"]]
    assert len(set(tables))==1 and tables[0]==(0,1,1,0)

    bench=ROOT/"research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json"
    assert git_blob_sha(bench.read_bytes())==BENCH_BLOB
    post=load_module("posthoc_adjudicate_v1",HERE/"posthoc_adjudicate_v1.py")
    ins=post.inspect(committed["search_2"]["outputs"])
    assert ins["pass"]
    frozen=json.loads((HERE/"POSTHOC_RESULT_V1.json").read_text())
    assert frozen["terminal"]=="RECOVERED" and frozen["cross_search_dependency_agreement"]
    assert frozen["frozen_required_clause_count"]==3 and frozen["frozen_observation_test_count"]==2

    result={
      "status":"GREEN","freeze_commit":FREEZE_COMMIT,"benchmark_blob":BENCH_BLOB,
      "blind_source_forbidden_hits":hits,"blind_search_file_reads":0,
      "searches":2,"presentations":2,"global_functions_checked":768,"dependency_candidates_checked":186,
      "minimum_dependency_counts":[2,2,2],"distinct_minimal_rule_tables":1,
      "posthoc_terminal":"RECOVERED","predicted_selected":"NOT_CLAIMED",
      "claim_ceiling":"AJ9D_K03_BLIND_LOCAL_SHARED_TRANSFORM_RECOVERY_AT_FROZEN_FINITE_SCOPE",
      "forbidden_promotions":["ALL_CONVOLUTIONAL_ARCHITECTURES_DERIVED","CNN_TRAINING_DERIVED","PREDICTED_SELECTED","AJ9_ALL_FAMILIES_RECOVERED","COMPLETE_GMI"]
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
