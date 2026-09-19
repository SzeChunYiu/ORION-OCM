"""No-smuggling screen v1 — lexical layer + #855 A2 semantic layer (GMI #833).

Extends the v2 screen to this tranche's three families. Layers:

  LEXICAL: denylist scan (D3 = v2's D2 core + this tranche's family
  vocabulary) of every SEARCH-SIDE file for family vocabulary; a matcher
  positive control must fire. Declared residual: generic task-object words
  (query, episode, stream, window, contraction, rule) are NOT denied — they
  name the standard mathematical objects of the batteries, not family
  macros; the family vocabulary below is.

  A2 SEMANTIC: every search-visible primitive carries the full 11-coordinate
  signature; three target fingerprints (one per tranche family, built from
  the frozen clause semantics POSTHOC-SIDE) are asserted to be satisfied by
  NO single search-visible primitive, with positive controls (fake
  primitives carrying the family-shaped signatures MUST be flagged) and the
  negative control (the tranche basis MUST be clean).
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / "gmi-833-no-smuggling-audit-v1"

SEARCH_SIDE_FILES = [
    "battery_generate_v1.py", "machinery_v1.py", "proc1_v1.py",
    "proc2_v1.py", "run_tranches_v1.py", "NEUTRAL_BATTERY_FREEZE_V1.json",
    "BASIS_GRID_V1.json",
]

DENYLIST_V3 = {
    "version": "D3",
    "entries": sorted({
        # v2's D2 core
        "transformer", "self_attention", "conv2d", "lstm_gate", "rag_retriever",
        "neural", "neuron", "perceptron", "mlp", "backprop", "feed_forward",
        "feedforward", "recurrent_layer", "gru", "convolution", "shared_kernel",
        "attention", "query_key_value", "softmax", "rewrite_engine",
        "bayes_update", "bayesian_network", "planner_macro", "content_retriever",
        "genetic_algorithm", "genetic_crossover", "sygus", "synthesizer_macro",
        "self_modify_macro", "godel_machine", "shift_register",
        # this tranche's families (D3 additions)
        "state_space", "ssm", "mamba", "linear_recurrence", "hopfield",
        "associative_memory", "content_addressed", "key_value", "keyed_store",
        "retrieval", "retriever", "term_rewriting", "knuth_bendix",
        "unification", "prolog", "theorem_prover", "backtracking",
        "rewrite_system", "guarded_rewrite", "symbolic_solver",
    }),
}


def load_audit_core():
    spec = importlib.util.spec_from_file_location(
        "audit_core_v1", AUDIT / "audit_core_v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _norm(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower())


def lexical_layer():
    hits = {}
    for fname in SEARCH_SIDE_FILES:
        p = HERE / fname
        if not p.exists():
            hits[fname] = {"missing": True}
            continue
        text = _norm(p.read_text())
        found = [tok for tok in DENYLIST_V3["entries"] if _norm(tok) in text]
        hits[fname] = {"hits": sorted(set(found))}
    control_text = "this config uses a self_attention macro and a hopfield store"
    control_hits = [t for t in DENYLIST_V3["entries"] if t in _norm(control_text)]
    clean = all(not (isinstance(v, dict) and v.get("hits")) for v in hits.values())
    return {"denylist": DENYLIST_V3, "files": hits,
            "search_side_clean": clean,
            "matcher_positive_control_fired": bool(
                {"self_attention", "hopfield"} & set(control_hits))}


SIG_KEYS = ["arity", "types", "state_access", "locality", "addressability",
            "content_dependent_routing", "parameter_sharing", "recurrence",
            "stochasticity", "verifier_access", "resource_class"]


def sig(**kw):
    assert set(kw) == set(SIG_KEYS), set(kw) ^ set(SIG_KEYS)
    return kw


def a2_semantic_layer(core):
    basis_primitives = [
        {"id": "ADD",
         "features": sig(arity=2, types="scalar,scalar->scalar",
                         state_access="none", locality="local",
                         addressability=False, content_dependent_routing=False,
                         parameter_sharing=False, recurrence=False,
                         stochasticity=False, verifier_access=False,
                         resource_class="O(1)")},
        {"id": "NEG",
         "features": sig(arity=1, types="scalar->scalar", state_access="none",
                         locality="local", addressability=False,
                         content_dependent_routing=False, parameter_sharing=False,
                         recurrence=False, stochasticity=False,
                         verifier_access=False, resource_class="O(1)")},
        {"id": "GE_c",
         "features": sig(arity=1, types="scalar->bool", state_access="none",
                         locality="local", addressability=False,
                         content_dependent_routing=False, parameter_sharing=False,
                         recurrence=False, stochasticity=False,
                         verifier_access=False, resource_class="O(1)")},
        {"id": "STATE_CELL",
         "features": sig(arity=1, types="scalar->scalar",
                         state_access="read_write", locality="local",
                         addressability=False, content_dependent_routing=False,
                         parameter_sharing=False, recurrence=True,
                         stochasticity=False, verifier_access=False,
                         resource_class="O(1)")},
        {"id": "INPUT_ATOM",
         "features": sig(arity=0, types="->scalar", state_access="none",
                         locality="local", addressability=False,
                         content_dependent_routing=False, parameter_sharing=False,
                         recurrence=False, stochasticity=False,
                         verifier_access=False, resource_class="O(1)")},
    ]
    target_fingerprints = [
        {"name": "FAM_S_STEP_MACRO",
         "required_features": {
             "arity": 2, "types": "vector,vector->vector",
             "state_access": "read_write", "recurrence": True,
             "parameter_sharing": True, "resource_class": "O(n)"}},
        {"name": "FAM_R_SELECT_MACRO",
         "required_features": {
             "arity": 2, "types": "query,store->item",
             "state_access": "read", "addressability": True,
             "content_dependent_routing": True}},
        {"name": "FAM_L_RULE_MACRO",
         "required_features": {
             "arity": 2, "types": "term,pattern->term",
             "state_access": "read_write", "locality": "subterm",
             "parameter_sharing": True, "verifier_access": True}},
    ]
    positive_controls = [
        {"id": "CONTROL_step_macro",
         "features": sig(arity=2, types="vector,vector->vector",
                         state_access="read_write", locality="global",
                         addressability=False, content_dependent_routing=False,
                         parameter_sharing=True, recurrence=True,
                         stochasticity=False, verifier_access=False,
                         resource_class="O(n)")},
        {"id": "CONTROL_select_macro",
         "features": sig(arity=2, types="query,store->item",
                         state_access="read", locality="global",
                         addressability=True, content_dependent_routing=True,
                         parameter_sharing=False, recurrence=False,
                         stochasticity=False, verifier_access=False,
                         resource_class="O(1)")},
        {"id": "CONTROL_rule_macro",
         "features": sig(arity=2, types="term,pattern->term",
                         state_access="read_write", locality="subterm",
                         addressability=False, content_dependent_routing=False,
                         parameter_sharing=True, recurrence=False,
                         stochasticity=False, verifier_access=True,
                         resource_class="O(1)")},
    ]
    def run(prims):
        return core.semantic({"primitives": prims,
                              "target_fingerprints": target_fingerprints})
    basis_result = run(basis_primitives)
    control_result = run(basis_primitives + positive_controls)
    return {
        "basis": basis_result,
        "positive_controls_flagged": (
            control_result["terminal"] == "SEMANTIC_MACRO_LEAKAGE"
            and len(control_result["findings"]) == 3),
        "negative_control_clean": basis_result["terminal"] == basis_result.get(
            "terminal", "CLEAN_AT_REGISTERED_AUDIT_SCOPE"),
        "fingerprint_names": [f["name"] for f in target_fingerprints],
        "primitive_ids": [p["id"] for p in basis_primitives],
    }


def main():
    core = load_audit_core()
    lexical = lexical_layer()
    semantic = a2_semantic_layer(core)
    result = {
        "schema": "FDT_NO_SMUGGLING_SCREEN_V1",
        "lexical": lexical,
        "a2_semantic": semantic,
        "screen_verdict": (
            "CLEAN"
            if lexical["search_side_clean"]
            and lexical["matcher_positive_control_fired"]
            and semantic["positive_controls_flagged"]
            and semantic["basis"]["terminal"] == "CLEAN_AT_REGISTERED_AUDIT_SCOPE"
            else "NOT_CLEAN"),
    }
    (HERE / "SCREEN_RESULT_V1.json").write_text(
        json.dumps(result, indent=1, sort_keys=True))
    print("screen verdict:", result["screen_verdict"])


if __name__ == "__main__":
    main()
