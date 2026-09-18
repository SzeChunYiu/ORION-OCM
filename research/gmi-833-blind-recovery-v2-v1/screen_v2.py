"""No-smuggling screen v2 — lexical layer + #855 A2 semantic layer.

First wiring of the merged A2 semantic-fingerprint standard
(research/gmi-833-no-smuggling-audit-v1/audit_core_v1.py) into a
blind-recovery package. Two layers:

  LEXICAL: denylist scan of every SEARCH-SIDE file (battery generator, engine,
  tranche runner) for family vocabulary; hostile controls must fire.

  A2 SEMANTIC: builds the v2 PriorAuditRecord — every search-visible primitive
  carries the full 11-coordinate signature; registered target fingerprints
  (attention aggregate, translation-shared local kernel, recurrent macro)
  are asserted to be satisfied by NO single v2 primitive (expressivity !=
  smuggling), with positive controls (fake primitives carrying family-shaped
  signatures MUST be flagged) and the negative control (the v2 basis MUST be
  clean).
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / "gmi-833-no-smuggling-audit-v1"

SEARCH_SIDE_FILES = [
    "battery_generate_v1.py", "neutral_search_v2.py", "run_v2_tranches.py",
    "NEUTRAL_BATTERY_FREEZE_V1.json", "BASIS_GRID_V1.json",
]

DENYLIST_V2 = {
    "version": "D2",
    "entries": sorted({
        # v1's D1 core
        "transformer", "self_attention", "conv2d", "lstm_gate", "rag_retriever",
        # family names and macros from the frozen benchmark vocabulary
        "neural", "neuron", "perceptron", "mlp", "backprop", "feed_forward",
        "feedforward", "recurrent_layer", "gru", "convolution", "shared_kernel",
        "attention", "query_key_value", "softmax", "rewrite_engine",
        "bayes_update", "bayesian_network", "planner_macro", "content_retriever",
        "genetic_algorithm", "genetic_crossover", "sygus", "synthesizer_macro",
        "self_modify_macro", "godel_machine", "shift_register",
    }),
}


def load_audit_core():
    spec = importlib.util.spec_from_file_location(
        "audit_core_v1", AUDIT / "audit_core_v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lexical_layer():
    hits = {}
    for fname in SEARCH_SIDE_FILES:
        p = HERE / fname
        if not p.exists():
            hits[fname] = {"missing": True}
            continue
        text = p.read_text().lower()
        found = [tok for tok in DENYLIST_V2["entries"]
                 if re.sub(r"[^a-z0-9]+", "_", tok) in re.sub(r"[^a-z0-9]+", "_", text)]
        hits[fname] = {"hits": sorted(set(found))}
    # explicit positive control for the lexical matcher itself:
    control_text = "this config uses a self_attention macro and an lstm_gate"
    control_hits = [t for t in DENYLIST_V2["entries"]
                    if t in re.sub(r"[^a-z0-9]+", "_", control_text)]
    clean = all(not (isinstance(v, dict) and v.get("hits")) for v in hits.values())
    return {"denylist": DENYLIST_V2, "files": hits,
            "search_side_clean": clean,
            "matcher_positive_control_fired": bool(
                {"self_attention", "lstm_gate"} & set(control_hits))}


SIG_KEYS = ["arity", "types", "state_access", "locality", "addressability",
            "content_dependent_routing", "parameter_sharing", "recurrence",
            "stochasticity", "verifier_access", "resource_class"]


def sig(**kw):
    assert set(kw) == set(SIG_KEYS), set(kw) ^ set(SIG_KEYS)
    return kw


def a2_semantic_layer(core):
    v2_primitives = [
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
        {"id": "INPUT_ATOM",
         "features": sig(arity=0, types="->scalar", state_access="none",
                         locality="local", addressability=False,
                         content_dependent_routing=False, parameter_sharing=False,
                         recurrence=False, stochasticity=False,
                         verifier_access=False, resource_class="O(1)")},
        {"id": "STATE_CELL",
         "features": sig(arity=1, types="scalar->scalar",
                         state_access="read_write", locality="local",
                         addressability=False, content_dependent_routing=False,
                         parameter_sharing=False, recurrence=False,
                         stochasticity=False, verifier_access=False,
                         resource_class="O(1)")},
    ]
    target_fingerprints = [
        {"name": "content_route_weighted_aggregate",
         "required_features": {"content_dependent_routing": True,
                               "locality": "global",
                               "resource_class": "O(n^2)"}},
        {"name": "translation_shared_local_kernel",
         "required_features": {"locality": "neighborhood",
                               "parameter_sharing": True}},
        {"name": "recurrent_state_macro",
         "required_features": {"recurrence": True,
                               "state_access": "read_write"}},
    ]
    record = {
        "search_visible_identifiers": [p["id"] for p in v2_primitives],
        "denylist": DENYLIST_V2,
        "primitives": v2_primitives,
        "target_fingerprints": target_fingerprints,
        "cost": {
            "coordinates": ["operations"],
            "candidates": [{"id": "uniform_op_count", "resources":
                            {"operations": "1"}}],
            "scalarizations": [{"name": "plain", "weights": {"operations": "1"}}],
            "claim_mode": "CONDITIONAL", "target_adjustments": {},
            "operator_costs": [{"operator": p["id"], "target_privileged": False,
                                "cost": "1"} for p in v2_primitives]},
        "search": {
            "candidates": [{"id": "layer0", "objective": "0"},
                           {"id": "layerK", "objective": "K"}],
            "budget": 16, "strategies": [
                {"name": "cost_layered_dp", "order": ["layer0", "layerK"]},
                {"name": "best_first", "order": ["layer0", "layerK"]}],
            "tie_rule": "FIRST_SEEN", "pruning_rule": "GUARD_ONLY",
            "stopping_rule": "TARGET_OR_SATURATION", "randomness": "NONE",
            "seeds": [], "exhaustive_certificate": True},
        "evaluation": {
            "uses_architecture_ids_in_score": False, "target_id_bonus": "0",
            "thresholds_frozen_pre_outcome": True,
            "posthoc_classifier_feeds_score": False,
            "metric_rankings": {"protected_task_error": ["layer0", "layerK"]},
            "claim_mode": "CONDITIONAL"},
        "ecology": {
            "frame_status": "KNOWN",
            "frame": [{"id": "B_BOOL2", "target_favoring": False},
                      {"id": "B_BOOL3", "target_favoring": False},
                      {"id": "B_DELAY", "target_favoring": False},
                      {"id": "B_LOCAL", "target_favoring": False}],
            "sample_ids": ["B_BOOL2", "B_BOOL3", "B_DELAY", "B_LOCAL"],
            "matched_negative_registered": True, "inclusion_rule": "CENSUS",
            "exclusion_rule": "NONE", "claim_requires_representativeness": True},
    }
    base = core.semantic(record)

    def findings_of(res):
        if isinstance(res, dict):
            return res.get("findings", [])
        return res
    # positive controls: family-shaped single primitives MUST be flagged
    def with_primitive(rec, prim):
        r = json.loads(json.dumps(rec))
        r["primitives"].append(prim)
        r["search_visible_identifiers"].append(prim["id"])
        return r
    hostile_mix = {"id": "mix", "features": sig(
        arity=3, types="sequence->sequence", state_access="read",
        locality="global", addressability=True, content_dependent_routing=True,
        parameter_sharing=False, recurrence=False, stochasticity=False,
        verifier_access=False, resource_class="O(n^2)")}
    hostile_kernel = {"id": "local_apply", "features": sig(
        arity=2, types="grid,kernel->grid", state_access="read",
        locality="neighborhood", addressability=False,
        content_dependent_routing=False, parameter_sharing=True,
        recurrence=False, stochasticity=False, verifier_access=False,
        resource_class="O(n)")}
    hostile_rnn = {"id": "cell_step", "features": sig(
        arity=2, types="state,input->state", state_access="read_write",
        locality="local", addressability=False, content_dependent_routing=False,
        parameter_sharing=True, recurrence=True, stochasticity=False,
        verifier_access=False, resource_class="O(1)")}
    controls = {
        "attention_shaped_primitive_flagged":
            findings_of(core.semantic(with_primitive(record, hostile_mix))) != [],
        "shared_kernel_primitive_flagged":
            findings_of(core.semantic(with_primitive(record, hostile_kernel))) != [],
        "recurrent_macro_primitive_flagged":
            findings_of(core.semantic(with_primitive(record, hostile_rnn))) != [],
    }
    return {"record_summary": {
                "primitives": [p["id"] for p in v2_primitives],
                "target_fingerprints": [t["name"] for t in target_fingerprints]},
            "v2_basis_semantic_findings": base,
            "v2_basis_clean": findings_of(base) == []
            and (not isinstance(base, dict)
                 or base.get("terminal") == "CLEAN_AT_REGISTERED_AUDIT_SCOPE"),
            "positive_controls_fire": all(controls.values()),
            "controls": controls}


def main():
    core = load_audit_core()
    lex = lexical_layer()
    a2 = a2_semantic_layer(core)
    full = {"schema": "V2_NO_SMUGGLING_SCREEN_V1",
            "lexical": lex, "a2_semantic": a2,
            "screen_verdict": "CLEAN" if (
                lex["search_side_clean"] and lex["matcher_positive_control_fired"]
                and a2["v2_basis_clean"] and a2["positive_controls_fire"])
            else "NOT_CLEAN"}
    (HERE / "SCREEN_RESULT_V1.json").write_text(
        json.dumps(full, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"screen_verdict": full["screen_verdict"],
                      "lexical_clean": lex["search_side_clean"],
                      "a2_basis_clean": a2["v2_basis_clean"],
                      "a2_findings": a2["v2_basis_semantic_findings"],
                      "controls_fire": a2["positive_controls_fire"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
