import copy
import json
from pathlib import Path

import gmi_k4_grammar_native as gn
import gmi_k4_search_v3 as k4

HERE = Path(__file__).resolve().parent
FREEZE = json.loads((HERE / "GMI_K4_LOFO_FREEZE_V1.json").read_text())
SAFE = copy.deepcopy(FREEZE); SAFE.pop("name_key", None)


def test_three_primitive_inventories_are_nonempty_and_pairwise_disjoint():
    inv = {g: gn.inventory(g) for g in sorted(gn.PREFIX)}
    assert all(inv[g] for g in inv)
    gs = sorted(inv)
    for i, a in enumerate(gs):
        for b in gs[i+1:]:
            assert inv[a].isdisjoint(inv[b]), (a, b, inv[a] & inv[b])


def test_candidate_serializations_use_only_their_grammar_prefix():
    for grammar, prefix in gn.PREFIX.items():
        sample = []
        for i, c in enumerate(gn.iter_candidates(grammar)):
            sample.append(c)
            if i >= 99: break
        assert sample
        for c in sample:
            assert all(t.startswith(prefix + "_") for t in c.tokens)


def test_candidate_space_is_combinatorial_not_one_candidate_per_family():
    sizes = {g: sum(1 for _ in gn.iter_candidates(g)) for g in gn.PREFIX}
    assert all(n > 1000 for n in sizes.values()), sizes
    assert len(set(sizes.values())) >= 1


def test_property_vector_does_not_change_grammar_native_search_winner():
    fid = "K4-A13"; grammar = "G1_TENSOR_GRAPH"; cell = "w4"; seed = 0x12345678
    a = k4.run_cell(fid, grammar, cell, freeze=copy.deepcopy(SAFE), seed=seed, budget=1_000_000)
    alt = copy.deepcopy(SAFE)
    alt["families"][fid]["property_vector"] = {
        **alt["families"][fid]["property_vector"],
        "external_authority": not alt["families"][fid]["property_vector"]["external_authority"],
    }
    b = k4.run_cell(fid, grammar, cell, freeze=alt, seed=seed, budget=1_000_000)
    assert a["winner_candidate_id"] == b["winner_candidate_id"]
    assert a["winner_program_tokens"] == b["winner_program_tokens"]
    assert a["measured_property_vector"] == b["measured_property_vector"]
    assert a["scalar_lifecycle_cost"] == b["scalar_lifecycle_cost"]
    assert a["target_vector_match"] != b["target_vector_match"]


def test_seed_changes_world_but_same_seed_replays():
    a = k4.run_cell("K4-A18", "G2_SYMBOLIC_PROGRAM", "w2", freeze=copy.deepcopy(SAFE), seed=17, budget=1_000_000)
    b = k4.run_cell("K4-A18", "G2_SYMBOLIC_PROGRAM", "w2", freeze=copy.deepcopy(SAFE), seed=17, budget=1_000_000)
    c = k4.run_cell("K4-A18", "G2_SYMBOLIC_PROGRAM", "w2", freeze=copy.deepcopy(SAFE), seed=18, budget=1_000_000)
    assert a == b
    assert a["world_profile"] != c["world_profile"]


def test_full_native_space_is_exhausted_at_registered_budget():
    for grammar in sorted(SAFE["grammars"]):
        r = k4.run_cell("K4-A01", grammar, "w1", freeze=copy.deepcopy(SAFE), seed=2026, budget=1_000_000)
        assert r["coverage"]["exhaustive"] is True
        assert r["coverage"]["candidate_space_size"] < 1_000_000
        assert all(v["recovered"] for v in r["controls"].values())


def test_name_key_never_changes_native_result():
    a = k4.run_cell("K4-A03", "G3_FSM_MESSAGE", "w2", freeze=copy.deepcopy(FREEZE), seed=999, budget=1_000_000)
    b = k4.run_cell("K4-A03", "G3_FSM_MESSAGE", "w2", freeze=copy.deepcopy(SAFE), seed=999, budget=1_000_000)
    assert a == b
