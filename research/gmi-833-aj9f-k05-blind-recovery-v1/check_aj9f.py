from __future__ import annotations
import hashlib, importlib.util, json, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FREEZE_COMMIT="4603e36913cd28cf4a79f916946492d5bcd49e3a"
BENCH_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def main():
    blind_path=HERE/"blind_term_search_v1.py"; src=blind_path.read_text().casefold()
    forbidden=["symbolic","rewrite","theorem prover","k05","known_family_benchmark","posthoc_fingerprint","family_id"]
    hits=[x for x in forbidden if x in src]; assert not hits,hits
    assert "read_text(" not in src and "read_bytes(" not in src and "open(" not in src
    prefix="research/gmi-833-aj9f-k05-blind-recovery-v1/"
    subprocess.run(["git","merge-base","--is-ancestor",FREEZE_COMMIT,"HEAD"],check=True)
    for n in ("SEARCH_CONFIG_V1.json","FREEZE_V1.md"): subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{n}"],check=True)
    for n in ("blind_term_search_v1.py","BLIND_OUTCOME_V1.json","posthoc_adjudicate_v1.py","POSTHOC_RESULT_V1.json"):
        p=subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{n}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); assert p.returncode!=0,n
    cfg=json.loads((HERE/"SEARCH_CONFIG_V1.json").read_text()); assert len(cfg["searches"])==2 and cfg["evaluation"]["no_family_score"] is True
    blind=load_module("blind_term_search_v1",blind_path); a=blind.fifo_frontier_search(); b=blind.depth_limited_iteration()
    assert len(a["tags"])==2 and a["branching_at_start"]==2 and a["expanded_states"]==3 and a["generated_edges"]==4 and a["peak_frontier"]==2
    assert b["depth_limit"]==2 and b["branching_at_start"]==2 and b["visited_nodes"]==7 and b["generated_edges"]==4
    assert a["tags"][0]!=b["tags"][0]
    committed=json.loads((HERE/"BLIND_OUTCOME_V1.json").read_text()); assert committed["raw_resource_vector"]["solution_steps"]==2
    bench=ROOT/"research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json"; assert git_blob_sha(bench.read_bytes())==BENCH_BLOB
    post=load_module("posthoc_adjudicate_v1",HERE/"posthoc_adjudicate_v1.py"); ins=post.inspect(committed); assert ins["pass"]
    frozen=json.loads((HERE/"POSTHOC_RESULT_V1.json").read_text()); assert frozen["terminal"]=="RECOVERED" and frozen["frozen_required_clause_count"]==3 and frozen["frozen_observation_test_count"]==2
    result={"status":"GREEN","freeze_commit":FREEZE_COMMIT,"benchmark_blob":BENCH_BLOB,"blind_source_forbidden_hits":hits,"blind_search_file_reads":0,
      "searches":2,"presentations":2,"solution_steps":2,"initial_legal_successors":2,"opposite_first_branch_choices":True,
      "posthoc_terminal":"RECOVERED","predicted_selected":"NOT_CLAIMED","claim_ceiling":"AJ9F_K05_BLIND_COMPOSITIONAL_RULE_SEARCH_RECOVERY_AT_FROZEN_FINITE_SCOPE",
      "forbidden_promotions":["GENERAL_SYMBOLIC_AI_DERIVED","THEOREM_PROVING_DERIVED","PREDICTED_SELECTED","AJ9_ALL_FAMILIES_RECOVERED","COMPLETE_GMI"]}
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n"); print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
