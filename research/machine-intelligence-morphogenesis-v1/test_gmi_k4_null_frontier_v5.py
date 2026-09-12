import copy
import json
from pathlib import Path

import gmi_k4_search as base
import gmi_k4_search_v2 as phase
import gmi_k4_null_frontier_v5 as nf
import gmi_k4_search_v5 as k4

HERE=Path(__file__).resolve().parent
FREEZE=json.loads((HERE/"GMI_K4_LOFO_FREEZE_V1.json").read_text());SAFE=copy.deepcopy(FREEZE);SAFE.pop("name_key",None)


def sem(cand,task,scale,twin,profile):
    f=cand.as_form();return phase._semantic_adjust(base.semantic_score(f,task,scale,twin),f,task,twin,profile)


def test_null_registry_contains_constant_and_multiple_fixed_function_parents():
    ns=nf.null_candidates("G1_TENSOR_GRAPH")
    assert "NULL_CONSTANT" in ns
    assert len(ns)>=6
    assert all(c.update_locality=="none" for c in ns.values())


def test_nulls_pay_no_development_or_retraining_but_keep_other_costs():
    profile=phase.world_profile(17,"linear",2)
    for c in nf.null_candidates("G2_SYMBOLIC_PROGRAM").values():
        cost=nf.null_cost(c,2,profile)
        assert cost["development_compute"]==0.0
        assert cost["update_retraining"]==0.0
        assert cost["description_compiler_burden"]>=0
        assert cost["state_storage"]>=0
        assert cost["serve_compute_latency"]>=0


def test_fixed_numeric_is_an_admissible_linear_null_under_same_semantics():
    profile=phase.world_profile(23,"linear",1)
    aud=nf.audit("G1_TENSOR_GRAPH","linear",1,profile,sem,0.98)
    row={r["null_id"]:r for r in aud["rows"]}["NULL_FIXED_NUMERIC"]
    assert row["semantic_score"]>=0.98
    assert row["admissible"] is True


def test_null_audit_does_not_read_or_change_frozen_target_vector():
    fid="K4-A01";grammar="G1_TENSOR_GRAPH";cell="w1";seed=0x9090
    a=k4.run_cell(fid,grammar,cell,freeze=copy.deepcopy(SAFE),seed=seed,budget=3000)
    alt=copy.deepcopy(SAFE);alt["families"][fid]["property_vector"]={**alt["families"][fid]["property_vector"],"external_authority":not alt["families"][fid]["property_vector"]["external_authority"]}
    b=k4.run_cell(fid,grammar,cell,freeze=alt,seed=seed,budget=3000)
    assert a["search_digest"]==b["search_digest"]
    assert a["null_search_digest"]==b["null_search_digest"]
    assert a["world_profile"]==b["world_profile"]


def test_null_dominance_is_never_reported_as_green():
    for fid in ("K4-A01","K4-A03","K4-A06","K4-A20"):
        r=k4.run_cell(fid,"G2_SYMBOLIC_PROGRAM","w1",freeze=copy.deepcopy(SAFE),seed=41,budget=2000)
        if r["verdict"]=="THEORY_RED_NULL_DOMINATES":
            assert r["null_vs_target_witness_margin"]>0
            assert r["null_dominating_id"].startswith("NULL_")
        assert r["verdict"]!="K4_RECOVERY_GREEN"  # sub-million development budget can never green
