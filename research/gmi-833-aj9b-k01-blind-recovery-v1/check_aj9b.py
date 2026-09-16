from __future__ import annotations
import hashlib, importlib.util, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FREEZE_COMMIT="5324b806afc06ff392b81e810aa86bc74921df4b"
BENCH_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def main():
    blind_path=HERE/"blind_search_v1.py"
    blind_source=blind_path.read_text().casefold()
    forbidden=["neural","feed-forward","feedforward","neuron","perceptron","relu","attention","bayesian","known_family_benchmark","posthoc_fingerprint","family_id\": \"k01"]
    source_hits=[x for x in forbidden if x in blind_source]
    assert not source_hits, source_hits
    assert "open(" not in blind_source and "read_text(" not in blind_source and "read_bytes(" not in blind_source

    # Freeze custody: generic config/freeze existed; implementation/outcome did not.
    prefix="research/gmi-833-aj9b-k01-blind-recovery-v1/"
    subprocess.run(["git","merge-base","--is-ancestor",FREEZE_COMMIT,"HEAD"],check=True)
    for name in ("SEARCH_CONFIG_V1.json","FREEZE_V1.md"):
        subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{name}"],check=True)
    for name in ("blind_search_v1.py","BLIND_OUTCOME_V1.json","posthoc_adjudicate_v1.py","POSTHOC_RESULT_V1.json"):
        p=subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{name}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        assert p.returncode!=0, name

    cfg=json.loads((HERE/"SEARCH_CONFIG_V1.json").read_text())
    assert cfg["task"]["required_outputs"]==[0,1,1,0]
    assert cfg["generic_primitives"]["unary"]==["NEGATE","POSITIVE_TEST"]
    assert cfg["generic_primitives"]["binary"]==["ADD"]
    assert len(cfg["searches"])==2 and len(cfg["presentations"])==2
    assert cfg["evaluation"]["no_family_score"] is True

    blind=load_module("blind_search_v1",blind_path)
    committed=json.loads((HERE/"BLIND_OUTCOME_V1.json").read_text())
    s1=blind.size_layered_search(); s2=blind.semantic_cost_closure()
    assert s1["first_exact_cost"]==committed["search_1"]["first_exact_cost"]==7
    assert s2["first_exact_cost"]==committed["search_2"]["first_exact_cost"]==7
    assert list(s1["semantics"])==committed["search_1"]["semantics"]==[0,1,1,0]
    assert list(s2["semantics"])==committed["search_2"]["semantics"]==[0,1,1,0]
    assert s1["new_semantics_by_cost"]==s2["new_semantics_by_cost"]==[5,11,26,39,67,88,105,118]
    assert s1["raw_resources"]==s2["raw_resources"]=={"operation_nodes":7,"positive_tests":2,"depth":5,"constant_uses":1}

    bench_path=ROOT/"research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json"
    assert git_blob_sha(bench_path.read_bytes())==BENCH_BLOB
    post=load_module("posthoc_adjudicate_v1",HERE/"posthoc_adjudicate_v1.py")
    ast=post.tup(committed["search_1"]["expression"])
    rpn=post.rpn_to_ast(committed["search_2"]["postfix"])
    i1=post.inspect_candidate(ast,committed["required_outputs"])
    i2=post.inspect_candidate(rpn,committed["required_outputs"])
    assert i1["pass"] and i2["pass"]
    assert len(i1["mixing_forms"])>=2 and len(i2["mixing_forms"])>=2

    frozen_post=json.loads((HERE/"POSTHOC_RESULT_V1.json").read_text())
    assert frozen_post["terminal"]=="RECOVERED"
    assert frozen_post["search_1"]["pass"] and frozen_post["search_2"]["pass"]

    result={
      "status":"GREEN",
      "freeze_commit":FREEZE_COMMIT,
      "benchmark_blob":BENCH_BLOB,
      "blind_source_forbidden_hits":source_hits,
      "blind_search_file_reads":0,
      "searches":2,
      "presentations":2,
      "first_exact_operation_cost":7,
      "no_exact_below_cost":7,
      "raw_resource_vector":{"operation_nodes":7,"positive_tests":2,"depth":5,"constant_uses":1},
      "posthoc_terminal":"RECOVERED",
      "learning_extension":"NOT_CLAIMED",
      "predicted_selected":"NOT_CLAIMED",
      "claim_ceiling":"AJ9B_K01_BLIND_STRUCTURAL_RECOVERY_AT_FROZEN_FINITE_SCOPE",
      "forbidden_promotions":["ALL_NEURAL_NETWORKS_DERIVED","NEURAL_LEARNING_DERIVED","BACKPROP_DERIVED","PREDICTED_SELECTED","AJ9_ALL_FAMILIES_RECOVERED","COMPLETE_GMI"]
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
