from __future__ import annotations
import hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
REG=HERE/"KNOWN_FAMILY_BENCHMARK_V1.json"
EXPECTED_BLOB="6b9ac3095c90d74e2717671a70ad7cc18955310c"
EXPECTED_IDS=[f"K{i:02d}" for i in range(1,12)]
EXPECTED_NAMES=[
 "neural/feed-forward","recurrent/stateful","local/shared-transform","attention/dynamic-routing",
 "symbolic/rewrite/search","probabilistic/Bayesian","planning/control","retrieval/memory",
 "evolutionary/population search","program synthesis","self-modifying/developmental"
]
MACRO_DENY={
 "neural","neuron","mlp","dense_layer","backprop","rnn","recurrent_layer","lstm","gru",
 "convolution","conv1d","conv2d","shared_kernel","attention","self_attention","query_key_value","transformer",
 "symbolic_solver","rewrite_engine","bayes_update","bayesian_network","planner_macro","content_retriever",
 "content_addressed_memory","genetic_algorithm","genetic_crossover","evolutionary_population","program_synthesis",
 "sygus","synthesizer_macro","self_modify_macro","godel_machine"
}
FORBIDDEN_KEYS={"target_family","family_id","paper_name","target_fingerprint","posthoc_fingerprint","family_bonus","family_penalty","taxonomy_label"}

def git_blob_sha(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def norm(s:str)->str:
    return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")

def walk(obj,path="$"):
    if isinstance(obj,dict):
        for k,v in obj.items():
            yield path,k,v
            yield from walk(v,path+"."+str(k))
    elif isinstance(obj,list):
        for i,v in enumerate(obj): yield from walk(v,path+f"[{i}]")

def audit_config(cfg, registry):
    reasons=[]
    serialized=json.dumps(cfg,sort_keys=True).lower()
    if "known_family_benchmark_v1" in serialized or EXPECTED_BLOB in serialized:
        reasons.append("ADJUDICATOR_REGISTRY_ACCESS")
    for path,k,v in walk(cfg):
        if str(k).lower() in FORBIDDEN_KEYS:
            reasons.append("FORBIDDEN_SCHEMA_KEY:"+str(k))
        if isinstance(v,str):
            nv=norm(v)
            for token in MACRO_DENY:
                if token in nv:
                    reasons.append("FAMILY_MACRO_OR_LABEL:"+token)
    # Literal reuse of a frozen post-hoc required fingerprint clause is target leakage.
    for fam in registry["families"]:
        req=fam["posthoc_fingerprint"]["required"]
        for phrase in req:
            if phrase.lower() in serialized:
                reasons.append("POSTHOC_FINGERPRINT_LEAK:"+fam["family_id"])
    return sorted(set(reasons))

def main():
    registry=json.loads(REG.read_text())
    assert git_blob_sha(REG)==EXPECTED_BLOB
    assert registry["schema"]=="AJ9_KNOWN_FAMILY_BENCHMARK_V1"
    assert registry["status"]=="FROZEN_BEFORE_HOLDOUT_RUNS"
    assert registry["role"]=="POSTHOC_ADJUDICATOR_ONLY"
    assert not registry["generator_access"] and not registry["search_access"] and not registry["evaluator_access"]
    fams=registry["families"]
    assert len(fams)==11
    assert [f["family_id"] for f in fams]==EXPECTED_IDS
    assert [f["paper_name"] for f in fams]==EXPECTED_NAMES
    for f in fams:
        assert f["hidden_from_generator"] and f["hidden_from_search"] and f["hidden_from_evaluator"]
        assert len(f["posthoc_fingerprint"]["required"])>=3
        assert len(f["exclusions_near_neighbors"])>=3
        assert len(f["minimum_observation_tests"])>=2
        assert f["equivalence_scope"] and f["parent_anchors"]

    clean={
      "substrate":"AJ1_AJ5_REGISTERED_GENERIC_PROCESSES",
      "environment":{"observations":"binary sequences","requirements":"predict protected output traces"},
      "resources":{"steps":128,"memory_cells":8},
      "generic_ops":["copy","add","multiply","compare","branch","store","read","compose","route"],
      "search":{"method":"enumerate_then_branch_bound","seed":7,"budget":1000},
      "evaluator":{"metric":"protected trace error","taxonomy_feedback":False}
    }
    assert audit_config(clean,registry)==[]

    hostiles=[
      {"target_family":"K01"},
      {"ops":["dense_layer"]},
      {"ops":["self_attention"]},
      {"ops":["bayes_update"]},
      {"ops":["genetic_algorithm"]},
      {"family_bonus":{"K04":-10}},
      {"registry_path":"KNOWN_FAMILY_BENCHMARK_V1.json"},
      {"target_fingerprint":fams[1]["posthoc_fingerprint"]["required"][0]},
      {"evaluator":{"taxonomy_label":"attention/dynamic-routing"}},
      {"macro":"program_synthesis"},
      {"macro":"self_modify_macro"}
    ]
    hostile_results=[audit_config(h,registry) for h in hostiles]
    assert all(r for r in hostile_results)

    result={
      "status":"GREEN",
      "benchmark_git_blob":EXPECTED_BLOB,
      "family_count":len(fams),
      "family_ids":EXPECTED_IDS,
      "minimum_registered_family_names":EXPECTED_NAMES,
      "all_family_fingerprints_posthoc_only":True,
      "clean_generic_config":"ACCEPTED",
      "hostile_configs_checked":len(hostiles),
      "hostile_configs_rejected":sum(bool(r) for r in hostile_results),
      "hostile_reason_classes":sorted({x.split(':')[0] for r in hostile_results for x in r}),
      "outcome_terminals":registry["outcome_terminals"],
      "unknown_reserved_for_AJ10":registry["novelty_terminal_reserved_for_AJ10"],
      "scientific_rows_earned":["AJ9_FREEZE_KNOWN_FAMILY_BENCHMARK","AJ9_INCLUDE_MINIMUM_REGISTERED_FAMILIES"],
      "scientific_rows_not_earned":["AJ9_NO_SMUGGLING_EXECUTED_FOR_EVERY_HOLDOUT","AJ9_FAMILY_RECOVERY","AJ9_TWO_PRESENTATIONS_SEARCHES","AJ9_PREDICTED_SELECTED"],
      "claim_ceiling":"AJ9A_KNOWN_FAMILY_BENCHMARK_AND_PROSPECTIVE_NO_SMUGGLING_CONTRACT_FROZEN"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
