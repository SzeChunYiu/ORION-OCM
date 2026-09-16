from __future__ import annotations
import hashlib, importlib.util, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FREEZE_COMMIT="1187bb843727331aef3c3922630c6d3fd3c7cf75"
BENCH_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def git_blob_sha(data): return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def main():
    blind_path=HERE/"blind_temporal_search_v1.py"
    src=blind_path.read_text().casefold()
    forbidden=["recurrent","rnn","elman","k02","known_family_benchmark","posthoc_fingerprint","family_id"]
    source_hits=[x for x in forbidden if x in src]
    assert not source_hits, source_hits
    assert "read_text(" not in src and "read_bytes(" not in src and "open(" not in src

    prefix="research/gmi-833-aj9c-k02-blind-recovery-v1/"
    subprocess.run(["git","merge-base","--is-ancestor",FREEZE_COMMIT,"HEAD"],check=True)
    for name in ("SEARCH_CONFIG_V1.json","FREEZE_V1.md"):
        subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{name}"],check=True)
    for name in ("blind_temporal_search_v1.py","BLIND_OUTCOME_V1.json","posthoc_adjudicate_v1.py","POSTHOC_RESULT_V1.json"):
        p=subprocess.run(["git","cat-file","-e",f"{FREEZE_COMMIT}:{prefix}{name}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        assert p.returncode!=0, name

    cfg=json.loads((HERE/"SEARCH_CONFIG_V1.json").read_text())
    assert cfg["candidate_capacity"]["total_candidates"]==260
    assert len(cfg["searches"])==2 and len(cfg["presentations"])==2
    assert cfg["evaluation"]["no_family_score"] is True

    blind=load_module("blind_temporal_search_v1",blind_path)
    a=blind.full_table_enumeration(); b=blind.constraint_filter_search()
    committed=json.loads((HERE/"BLIND_OUTCOME_V1.json").read_text())
    assert a["candidate_count"]==260
    assert a["zero_cell_exact"]==0 and a["one_cell_exact"]==1
    rows=a["solutions"][0][1]
    assert tuple(tuple(r) for r in committed["search_1"]["solution_rows"])==rows
    assert b["zero_cell_solutions"]==[] and b["one_cell_leaves"]==[rows]
    assert b["visited_partial_nodes"]==25 and b["pruned_partial_nodes"]==18
    assert committed["search_2"]["packed_solution"]==blind.pack_rows(rows)==228

    bench=ROOT/"research/gmi-833-aj9a-known-family-benchmark-v1/KNOWN_FAMILY_BENCHMARK_V1.json"
    assert git_blob_sha(bench.read_bytes())==BENCH_BLOB
    post=load_module("posthoc_adjudicate_v1",HERE/"posthoc_adjudicate_v1.py")
    i1=post.inspect(rows); i2=post.inspect(blind.unpack_rows(committed["search_2"]["packed_solution"]))
    assert i1["pass"] and i2["pass"]
    assert i1["same_input_witness"]=={"input":0,"state0_output":0,"state1_output":1}
    frozen_post=json.loads((HERE/"POSTHOC_RESULT_V1.json").read_text())
    assert frozen_post["terminal"]=="RECOVERED"
    assert frozen_post["frozen_required_clause_count"]==3
    assert frozen_post["frozen_observation_test_count"]==2

    result={
      "status":"GREEN",
      "freeze_commit":FREEZE_COMMIT,
      "benchmark_blob":BENCH_BLOB,
      "blind_source_forbidden_hits":source_hits,
      "blind_search_file_reads":0,
      "searches":2,
      "presentations":2,
      "candidate_count":260,
      "stateless_exact":0,
      "one_cell_exact":1,
      "constraint_search_visited":25,
      "constraint_search_pruned":18,
      "posthoc_terminal":"RECOVERED",
      "predicted_selected":"NOT_CLAIMED",
      "claim_ceiling":"AJ9C_K02_BLIND_STATEFUL_RECOVERY_AT_FROZEN_FINITE_SCOPE",
      "forbidden_promotions":["ALL_RECURRENT_ARCHITECTURES_DERIVED","RNN_TRAINING_DERIVED","PREDICTED_SELECTED","AJ9_ALL_FAMILIES_RECOVERED","COMPLETE_GMI"]
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
