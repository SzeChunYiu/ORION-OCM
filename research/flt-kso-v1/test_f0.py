from __future__ import annotations

import copy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import pytest

from f0_generator import solve
from run_f0 import ALLOWED_LEMMAS, emit_f0_lean, f0_request, invoke_generator, render_ast


def test_f0_generic_typed_search_constructs_ast_without_lean_source():
    result = solve(f0_request())
    assert result["terminal"] == "CANDIDATE_AST_CONSTRUCTED"
    assert result["llm_calls"] == result["llm_tokens"] == result["foundation_model_calls"] == 0
    assert result["proof_state_expansions"] <= 128
    assert result["operator_candidates_considered"] <= 256
    term = render_ast(result["proof_ast"], allowed_locals={"member", "subset", "agreement"})
    assert term == (
        "MEFoundation.agreement_sound W q answer actual member "
        "(MEFoundation.agreement_refinement V W q answer subset agreement)"
    )
    source = emit_f0_lean(result["proof_ast"])
    assert "Composition" not in source
    assert "refinement_then_sound" not in source
    assert "sorry" not in source and "native_decide" not in source


def test_f0_is_deterministic_and_local_names_are_not_route_dispatch():
    a = solve(f0_request())
    b = solve(f0_request())
    assert a["proof_ast"] == b["proof_ast"]
    renamed = {"member": "m0", "subset": "s0", "agreement": "a0"}
    r = solve(f0_request(local_names=renamed))
    assert r["terminal"] == "CANDIDATE_AST_CONSTRUCTED"
    term = render_ast(r["proof_ast"], allowed_locals=set(renamed.values()))
    assert term.endswith("m0 (MEFoundation.agreement_refinement V W q answer s0 a0)")
    source = emit_f0_lean(r["proof_ast"], local_names=renamed)
    assert "(m0 : W actual)" in source and "(s0 : ∀ h, W h → V h)" in source


def test_f0_missing_premise_and_wrong_type_fail_without_refuting_target():
    missing = f0_request()
    missing["context"] = [x for x in missing["context"] if x["id"] != "subset"]
    assert solve(missing)["terminal"] == "NO_PROOF_FOUND_UNDER_GRAMMAR"

    wrong = f0_request()
    wrong["context"][0]["type"] = ["app", "V", "actual"]
    assert solve(wrong)["terminal"] == "NO_PROOF_FOUND_UNDER_GRAMMAR"


def test_f0_budget_is_explicit_negative_terminal():
    result = solve(f0_request(max_expansions=1))
    assert result["terminal"] == "FAILED_UNDER_BUDGET"


def test_f0_renderer_rejects_unregistered_dispatch_and_data_terms():
    with pytest.raises(ValueError, match="unregistered AST operation"):
        render_ast({"op": "LEAN_SOURCE", "source": "exact True.intro"}, allowed_locals=set())
    with pytest.raises(ValueError, match="undeclared proof lemma"):
        render_ast({"op": "APPLY_LEMMA", "id": "OCMProofReplay.refinement_then_sound", "bindings": {}, "premises": []}, allowed_locals=set())
    with pytest.raises(ValueError, match="undeclared local hypothesis"):
        render_ast({"op": "LOCAL_HYPOTHESIS", "id": "hidden"}, allowed_locals={"member"})

    result = solve(f0_request())
    malicious = copy.deepcopy(result["proof_ast"])
    malicious["bindings"]["V"] = ["app", "Hidden", "proof"]
    with pytest.raises(ValueError, match="untrusted/non-atomic"):
        render_ast(malicious, allowed_locals={"member", "subset", "agreement"})


def test_f0_only_registered_lemmas_are_present_in_request():
    request = f0_request()
    assert tuple(rule["id"] for rule in request["rules"]) == ALLOWED_LEMMAS
    assert "theorem_name" not in request and "proof_source" not in request and "lean_source" not in request


def test_f0_generator_subprocess_custody_trace_when_strace_available():
    if not __import__("shutil").which("strace"):
        pytest.skip("strace unavailable")
    result = invoke_generator(f0_request(), generator_path=HERE / "f0_generator.py", require_strace=True)
    assert result["terminal"] == "CANDIDATE_AST_CONSTRUCTED", result
    assert result["custody_trace"] == "CLEAR"
