from __future__ import annotations
import hashlib, importlib.util, json, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FREEZE_COMMIT="ab63abd49c623329c6a78c930921d9c5297251d8"
BENCH_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def main():
    blind_path=HERE/"blind_boolean_search_v1.py"; src=blind_path.read_text().casefold()
    forbidden=["attention","softmax","query-key-value","routing","selector","multiplexer","k04","known_family_benchmark","posthoc_fingerprint","family_id"]
    hits=[x for x in forbidden if x in src]
    assert not hits, hits
    assert "read_text(" not in src and "read_bytes(" not in src and "open(" not in src
    prefix="research/gmi-833-aj9e-k04-blind-recovery-v1/"
    subprocess.run(["git","merge-base","--is-ancestor",FREEZE_COMMIT,"HEAD"],check=True)
    for n in ("SEARCH_CONFIG_V1.json","FREEZE_V1.md"):
        subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{n}"],check=True)
    for n in ("blind_boolean_search_v1.py","BLIND_OUTCOME_V1.json","posthoc_adjudicate_v1.py","POSTHOC_RESULT_V1.json"):
        p=subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{n}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        assert p.returncode!=0, n
    cfg=json.loads((HERE/"SEARCH_CONFIG_V1.json").read_text())
    assert len(cfg["searches"])==2 and len(cfg["presentations"])==2 and cfg["evaluation"]["no_family_score"] is True
    blind=load_module("blind_boolean_search_v1",blind_path)
    a=blind.size_layered_expression_search(); b=blind.exact_dnf_cube_cover()
    assert a["first_exact_cost"]==4 and a["new_semantics_by_cost"]==[5,9,26,44,37]
    assert b["valid_implicants"]==7 and b["cover_candidates_checked"]==28 and b["cube_count"]==2 and b["literal_count"]==4
    committed=json.loads((HERE/"BLIND_OUTCOME_V1.json").read_text())
    assert tuple(a["semantics"])==tuple(committed["required_semantics"])
    assert set(b["cubes"])=={(0,1,-1),(1,-1,1)}
    bench=ROOT/"research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json"
    assert git_blob_sha(bench.read_bytes())==BENCH_BLOB
    post=load_module("posthoc_adjudicate_v1",HERE/"posthoc_adjudicate_v1.py")
    ins=post.inspect_ast(post.tup(committed["search_1"]["expression"])); dnf=post.inspect_dnf(committed["search_2"]["cubes"])
    assert ins["pass"] and dnf["pass"]
    frozen=json.loads((HERE/"POSTHOC_RESULT_V1.json").read_text()); assert frozen["terminal"]=="RECOVERED"
    result={"status":"GREEN","freeze_commit":FREEZE_COMMIT,"benchmark_blob":BENCH_BLOB,"blind_source_forbidden_hits":hits,"blind_search_file_reads":0,
      "searches":2,"presentations":2,"first_exact_operation_cost":4,"valid_dnf_implicants":7,"dnf_cover_candidates_checked":28,
      "posthoc_terminal":"RECOVERED","predicted_selected":"NOT_CLAIMED",
      "claim_ceiling":"AJ9E_K04_BLIND_DYNAMIC_ROUTING_RECOVERY_AT_FROZEN_FINITE_SCOPE",
      "forbidden_promotions":["TRANSFORMER_ATTENTION_DERIVED","SOFTMAX_QKV_DERIVED","PREDICTED_SELECTED","AJ9_ALL_FAMILIES_RECOVERED","COMPLETE_GMI"]}
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n"); print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
