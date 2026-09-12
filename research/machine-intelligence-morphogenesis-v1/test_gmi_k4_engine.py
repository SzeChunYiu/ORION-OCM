import copy
import json
from pathlib import Path

import gmi_k4_search as k4

HERE = Path(__file__).resolve().parent
FREEZE = json.loads((HERE / "GMI_K4_LOFO_FREEZE_V1.json").read_text())
SAFE = copy.deepcopy(FREEZE)
SAFE.pop("name_key", None)


def test_all_frozen_obligations_have_an_executable_generator():
    obligations = {v["obligation_class"] for v in SAFE["families"].values()}
    assert obligations == set(k4.OBLIGATION_KIND)
    assert len(SAFE["families"]) == 22
    assert len(SAFE["grammars"]) == 3


def test_historical_names_are_not_search_primitives():
    forbidden = {str(x).lower() for x in FREEZE.get("name_key", {}).values()}
    surface = json.dumps([
        {"fid": f.fid, "caps": f.caps, "vector": f.vector()} for f in k4.FORMS
    ], sort_keys=True).lower()
    # We do not require token-wise avoidance of generic words like 'linear'; the architecture names themselves
    # must not appear as candidate identifiers or named macros.
    for name in forbidden:
        assert name not in {f.fid.lower() for f in k4.FORMS}
    for banned in ("transformer", "mixture_of_experts", "lstm", "cnn", "rag"):
        assert banned not in surface


def test_frozen_property_vector_cannot_change_search_winner():
    fid = "K4-A01"; grammar = "G1_TENSOR_GRAPH"; cell = "w2"
    a = k4.run_cell(fid, grammar, cell, freeze=copy.deepcopy(SAFE), seed=123, budget=1_000_000)
    altered = copy.deepcopy(SAFE)
    altered["families"][fid]["property_vector"] = {
        **altered["families"][fid]["property_vector"],
        "external_authority": not altered["families"][fid]["property_vector"]["external_authority"],
    }
    b = k4.run_cell(fid, grammar, cell, freeze=altered, seed=123, budget=1_000_000)
    assert a["winner_neutral_form"] == b["winner_neutral_form"]
    assert a["winner_knob"] == b["winner_knob"]
    assert a["scalar_lifecycle_cost"] == b["scalar_lifecycle_cost"]
    assert a["measured_property_vector"] == b["measured_property_vector"]
    # Only post-search scoring is allowed to notice the changed frozen prediction.
    assert a["target_vector_match"] != b["target_vector_match"]


def test_negative_twin_is_part_of_green_gate():
    fid = "K4-A01"
    r = k4.run_cell(fid, "G1_TENSOR_GRAPH", "w2", freeze=copy.deepcopy(SAFE), seed=456, budget=1_000_000)
    if r["verdict"] == "K4_RECOVERY_GREEN":
        assert r["target_vector_match"]
        assert r["negative_twin_flipped"]
    elif r["verdict"] == "THEORY_RED":
        assert (not r["target_vector_match"]) or (not r["negative_twin_flipped"])
    else:
        assert r["verdict"].startswith("INCONCLUSIVE_")


def test_unknown_grammar_fails_closed():
    r = k4.run_cell("K4-A01", "G_UNKNOWN", "w1", freeze=copy.deepcopy(SAFE), seed=1, budget=100)
    assert r["verdict"] == "INCONCLUSIVE_GRAMMAR"


def test_controls_recovered_before_scientific_verdict():
    for grammar in sorted(SAFE["grammars"]):
        r = k4.run_cell("K4-A01", grammar, "w1", freeze=copy.deepcopy(SAFE), seed=99, budget=1_000_000)
        assert all(v["recovered"] for v in r["controls"].values())
        assert r["coverage"]["exhaustive"] is True


def test_name_key_is_irrelevant_even_if_present():
    with_name = copy.deepcopy(FREEZE)
    without_name = copy.deepcopy(FREEZE); without_name.pop("name_key", None)
    a = k4.run_cell("K4-A03", "G2_SYMBOLIC_PROGRAM", "w4", freeze=with_name, seed=1001, budget=1_000_000)
    b = k4.run_cell("K4-A03", "G2_SYMBOLIC_PROGRAM", "w4", freeze=without_name, seed=1001, budget=1_000_000)
    assert a == b
