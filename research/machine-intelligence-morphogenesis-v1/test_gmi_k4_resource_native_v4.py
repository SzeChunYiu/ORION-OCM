import copy
import json
from pathlib import Path

import gmi_k4_resource_native_v4 as rn
import gmi_k4_search_v4 as k4

HERE = Path(__file__).resolve().parent
FREEZE = json.loads((HERE / "GMI_K4_LOFO_FREEZE_V1.json").read_text())
SAFE = copy.deepcopy(FREEZE); SAFE.pop("name_key", None)


def test_reference_resource_laws_are_recovered_only_by_measurement():
    for label, expr in rn.STATE_REFERENCE.items(): assert rn.measure_state_law(expr) == label
    for label, expr in rn.SERVE_REFERENCE.items(): assert rn.measure_serve_law(expr) == label
    for expr in rn.STATE_DISTRACTORS: assert rn.measure_state_law(expr) == "UNCLASSIFIED_STATE_LAW"
    for expr in rn.SERVE_DISTRACTORS: assert rn.measure_serve_law(expr) == "UNCLASSIFIED_SERVE_LAW"


def test_candidate_does_not_store_resource_axis_labels():
    c = rn.sampled_candidate("G1_TENSOR_GRAPH", 123, 7)
    assert not hasattr(c, "state_scales_with")
    assert not hasattr(c, "serve_scales_with")
    v = c.vector()
    assert v["state_scales_with"] == rn.measure_state_law(c.state_expr)
    assert v["serve_scales_with"] == rn.measure_serve_law(c.serve_expr)


def test_state_and_serve_laws_are_independent_factors_not_22_prepaired_answers():
    pairs = set()
    target_pairs = {(x["property_vector"]["state_scales_with"], x["property_vector"]["serve_scales_with"])
                    for x in SAFE["families"].values()}
    for i in range(5000):
        c = rn.sampled_candidate("G2_SYMBOLIC_PROGRAM", 991, i)
        pairs.add((rn.measure_state_law(c.state_expr), rn.measure_serve_law(c.serve_expr)))
    assert len(pairs) > len(target_pairs) * 3
    assert any(p not in target_pairs for p in pairs)


def test_v4_grammar_token_inventories_are_pairwise_disjoint():
    inv = {g: rn.inventory(g, 3000) for g in rn.PREFIX}
    gs = sorted(inv)
    for i, a in enumerate(gs):
        for b in gs[i+1:]: assert inv[a].isdisjoint(inv[b])


def test_target_vector_does_not_change_v4_search_digest():
    fid = "K4-A11"; grammar = "G1_TENSOR_GRAPH"; cell = "w2"; seed = 0xD610
    a = k4.run_cell(fid, grammar, cell, freeze=copy.deepcopy(SAFE), seed=seed, budget=5000)
    alt = copy.deepcopy(SAFE)
    alt["families"][fid]["property_vector"] = {**alt["families"][fid]["property_vector"],
                                                "external_authority": not alt["families"][fid]["property_vector"]["external_authority"]}
    b = k4.run_cell(fid, grammar, cell, freeze=alt, seed=seed, budget=5000)
    assert a["search_digest"] == b["search_digest"]
    assert a["winner_candidate_id"] == b["winner_candidate_id"]
    assert a["world_profile"] == b["world_profile"]


def test_expressibility_witness_is_not_search_ranked():
    r = k4.run_cell("K4-A01", "G3_FSM_MESSAGE", "w1", freeze=copy.deepcopy(SAFE), seed=177, budget=3000)
    w = r.get("expressibility_witness")
    if w is not None:
        assert w["used_in_search_ranking"] is False
        assert w["measured_property_vector"] == SAFE["families"]["K4-A01"]["property_vector"]


def test_v4_same_seed_replays_and_new_seed_changes_world():
    a = k4.run_cell("K4-A18", "G2_SYMBOLIC_PROGRAM", "w2", freeze=copy.deepcopy(SAFE), seed=17, budget=3000)
    b = k4.run_cell("K4-A18", "G2_SYMBOLIC_PROGRAM", "w2", freeze=copy.deepcopy(SAFE), seed=17, budget=3000)
    c = k4.run_cell("K4-A18", "G2_SYMBOLIC_PROGRAM", "w2", freeze=copy.deepcopy(SAFE), seed=18, budget=3000)
    assert a == b
    assert a["world_profile"] != c["world_profile"]
    assert a["search_digest"] != c["search_digest"]


def test_green_is_impossible_below_registered_million_draw_cap():
    r = k4.run_cell("K4-A01", "G1_TENSOR_GRAPH", "w1", freeze=copy.deepcopy(SAFE), seed=5, budget=2000)
    assert r["verdict"] != "K4_RECOVERY_GREEN"
    assert r["coverage"]["budget_requirement_met"] is False
