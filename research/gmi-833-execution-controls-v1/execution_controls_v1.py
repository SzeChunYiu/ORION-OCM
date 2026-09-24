#!/usr/bin/env python3
"""Route A executor for #859 / #833-D execution controls (freeze 3682a045).

Executes D-X1 (matched mechanism-removal twin, plus the D-X1E ecology twin),
D-X2 (semantics-preserving alternate encoding), D-X3 (materially distinct
search procedures) and D-X4 (raw Pareto relation plus positive scalarizations,
with the derived metric-perturbation control) end to end on the registered
#901 result family, assembles `DerivationRobustnessRecord`s, and runs the
fail-closed admission census through `robustness_record_v1.validate_record`.

Usage:
    python3 -I -B execution_controls_v1.py          write RESULT_V1.json and the record files
    python3 -I -B execution_controls_v1.py --check  byte-compare against the committed files

Exact rationals only; stdlib only; deterministic (no RNG, no clock, no hash
randomisation reaches the output); byte-identical under `python -O`.
"""
from __future__ import annotations

from collections import Counter
import copy
from fractions import Fraction
import hashlib
import importlib.util
from itertools import product
from math import gcd
from pathlib import Path
import sys
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise ImportError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


R = _load("gmi859_robustness_record_v1", "robustness_record_v1.py")
S = _load("gmi859_substrate_v1", "substrate_v1.py")
E2 = _load("gmi859_encoding_e2_v1", "encoding_e2_v1.py")
SP = _load("gmi859_search_procedures_v1", "search_procedures_v1.py")

F = Fraction
FREEZE_COMMIT = "3682a045774ccfa83a2a43fdc81d176431bf7f0c"
FROZEN_FROM_MAIN = "f4d9d7d55fb009213d4068235e510f960907036e"
CLAIM_CEILING = "GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "ALL_GMI_DERIVATIONS_ROBUST",
    "ARCHITECTURE_PRIOR_FREE_UNIVERSALLY",
    "REPRESENTATION_INDEPENDENT_UNIVERSALLY",
    "SEARCH_INDEPENDENT_UNIVERSALLY",
    "RESOURCE_PRICE_INDEPENDENT_UNIVERSALLY",
    "KNOWN_FAMILY_RECOVERY_COMPLETE",
    "COMPLETE_GMI",
]
RESULT_FILE = "RESULT_V1.json"
RECORD_FILE = "DERIVATION_ROBUSTNESS_RECORD_POSITIVE_V1.json"
SCHEMA_FILE = "DERIVATION_ROBUSTNESS_RECORD_SCHEMA_V1.json"
COORDS = ["error_now", "error_delay", "state_bits"]
STATELESS, PERSISTENT = S.STATELESS, S.PERSISTENT

# --------------------------------------------------------------------------
# #855 arm audit inputs (registered here, before any audit ran on this substrate)
# --------------------------------------------------------------------------
DENYLIST = {"version": "GMI859-DENY-V1",
            "entries": ["recurrent", "persistent_state", "stateless", "delay_line",
                        "lstm_gate", "gru_cell", "rnn_cell", "shift_register"]}
_BASE = dict(arity=0, types="->bit", state_access="none", locality="local", addressability=False,
             content_dependent_routing=False, parameter_sharing=False, recurrence=False,
             stochasticity=False, verifier_access=False, resource_class="O(1)")
FEATURES = {
    "READ_MODE": dict(_BASE),
    "READ_INPUT": dict(_BASE),
    "OUT_LOOKUP": dict(_BASE, arity=3, types="bits->bit", addressability=True),
    "NEXT_LOOKUP": dict(_BASE, arity=3, types="bits->bit", addressability=True),
    "REGISTER_READ": dict(_BASE, state_access="explicit_priced", recurrence=True),
    "REGISTER_WRITE": dict(_BASE, arity=1, types="bit->", state_access="explicit_priced", recurrence=True),
    "READ_PREV": dict(_BASE, types="input_history->bit", state_access="hidden", recurrence=True),
    "READ_MODE_SYMBOL": dict(_BASE, types="->symbol"),
    "READ_DATA_SYMBOL": dict(_BASE, types="->symbol"),
    "EMIT_RULE": dict(_BASE, arity=3, types="symbols->symbol", addressability=True),
    "STEP_RULE": dict(_BASE, arity=3, types="symbols->symbol", addressability=True),
    "REGISTER_SYMBOL": dict(_BASE, types="->symbol", state_access="explicit_priced", recurrence=True),
}
E2_OPERATORS = ["EMIT_RULE", "READ_DATA_SYMBOL", "READ_MODE_SYMBOL", "REGISTER_SYMBOL", "STEP_RULE"]
FINGERPRINTS = [{"name": "hidden_previous_input_macro",
                 "required_features": {"state_access": "hidden", "recurrence": True}}]
INVARIANTS = [
    {"invariant_id": "I1_FRONTIER_ED_BELOW_8_IMPLIES_STATE",
     "if": {"coordinate": "error_delay", "op": "lt", "value": "8"},
     "then": {"coordinate": "state_bits", "op": "eq", "value": "1"}},
    {"invariant_id": "I2_FRONTIER_NOW_ERROR_ZERO",
     "if": {"coordinate": "state_bits", "op": "ge", "value": "0"},
     "then": {"coordinate": "error_now", "op": "eq", "value": "0"}},
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def props(xs) -> List[str]:
    return sorted(set(xs))


# --------------------------------------------------------------------------
# the registered D-X2 bijection phi: E1 (#901 tables) -> E2 (rule lists)
# --------------------------------------------------------------------------
def phi_index(i: int) -> int:
    if i < 16:
        code = 0
        for k in range(4):
            code |= ((i >> E2.GRAY_ADDRESSES_2[k]) & 1) << k
        return E2.STATEFUL_COUNT + E2.gray_inverse(code)

    def code3(table: int) -> int:
        g = 0
        for k in range(8):
            a = E2.GRAY_ADDRESSES_3[k]
            mode, state, x = (a >> 2) & 1, (a >> 1) & 1, a & 1
            g |= ((table >> (4 * state + 2 * mode + x)) & 1) << k
        return g

    next_table, out_table = (i - 16) >> 8, (i - 16) & 255
    return E2.gray_inverse(code3(next_table)) * 256 + E2.gray_inverse(code3(out_table))


# --------------------------------------------------------------------------
# #855 audit records per compared arm
# --------------------------------------------------------------------------
def frame_for(g: Dict[str, Any]) -> List[Tuple[str, bool]]:
    return [("m%d:%s" % (m, "".join(map(str, seq))), g["mode_targets"][m] == S.PREVIOUS)
            for m in (0, 1) for seq in g["sequences"]]


def ns_record(*, identifiers: Sequence[str], operators: Sequence[str], points: Dict[Any, int],
              frame: Sequence[Tuple[str, bool]], per_mode: int, positive_worlds: Sequence[Dict[str, Any]],
              reference_world: Dict[str, Any], extra_operator_costs: Sequence[Dict[str, Any]] = (),
              drop: str | None = None) -> Dict[str, Any]:
    pid = {r: S.rho_id(r) for r in points}
    ordered = sorted(points)
    a, b, c = S.world_weights(reference_world, per_mode)
    val = {r: a * r[1] + b * r[2] + c * r[0] for r in ordered}
    s2 = [pid[r] for r in SP.s2_order(ordered, c)]
    s3 = [pid[r] for r in sorted(ordered, key=lambda r: (b * r[2] + c * r[0], r))]
    rec = {
        "search_visible_identifiers": list(identifiers),
        "denylist": copy.deepcopy(DENYLIST),
        "primitives": [{"id": op, "features": dict(FEATURES[op])} for op in operators],
        "target_fingerprints": copy.deepcopy(FINGERPRINTS),
        "cost": {"coordinates": list(COORDS),
                 "candidates": [{"id": pid[r], "resources": {"error_now": str(r[1]), "error_delay": str(r[2]),
                                                             "state_bits": str(r[0])}} for r in ordered],
                 "scalarizations": [{"name": w["world_id"],
                                     "weights": dict(zip(COORDS, (str(x) for x in S.world_weights(w, per_mode))))}
                                    for w in positive_worlds],
                 "claim_mode": "CONDITIONAL", "target_adjustments": {},
                 "operator_costs": [{"operator": "REGISTER", "target_privileged": False, "cost": "1"}] + list(extra_operator_costs)},
        "search": {"candidates": [{"id": pid[r], "objective": str(val[r])} for r in ordered], "budget": len(ordered),
                   "strategies": [{"name": "S1_census_order", "order": [pid[r] for r in ordered]},
                                  {"name": "S2_price_sorted", "order": s2},
                                  {"name": "S3_lower_bound_heap", "order": s3}],
                   "tie_rule": S.TIE_RULE, "pruning_rule": "ADMISSIBLE_LOWER_BOUND",
                   "stopping_rule": "EXHAUSTIVE_OR_CERTIFICATE", "randomness": "NONE", "seeds": [],
                   "exhaustive_certificate": True},
        "evaluation": {"uses_architecture_ids_in_score": False, "target_id_bonus": "0",
                       "thresholds_frozen_pre_outcome": True, "posthoc_classifier_feeds_score": False,
                       "metric_rankings": {"error_now": [pid[r] for r in sorted(ordered, key=lambda r: (r[1], r))],
                                           "error_delay": [pid[r] for r in sorted(ordered, key=lambda r: (r[2], r))]},
                       "claim_mode": "CONDITIONAL"},
        "ecology": {"frame_status": "KNOWN", "frame": [{"id": i, "target_favoring": f} for i, f in frame],
                    "sample_ids": [i for i, _ in frame], "matched_negative_registered": True,
                    "inclusion_rule": "CENSUS", "exclusion_rule": "NONE", "claim_requires_representativeness": True},
    }
    if drop is not None:
        del rec[drop]
    return rec


def _finding_kind(sub: str, f: Any) -> str:
    if isinstance(f, dict) and "kind" in f:
        return str(f["kind"])
    return {"lexical": "DENYLIST_SUBSTRING", "semantic": "TARGET_FINGERPRINT_MATCH"}.get(sub, "UNTYPED_FINDING")


def ns_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    out = S.ns_audit.audit(record)
    subs = {}
    for k, v in sorted(out["subaudits"].items()):
        subs[k] = {"terminal": v["terminal"], "finding_kinds": sorted({_finding_kind(k, f) for f in v.get("findings", [])})}
    return {"terminal": out["terminal"], "subaudits": subs}


# --------------------------------------------------------------------------
# the executor
# --------------------------------------------------------------------------
def conclusion_entry(best: Fraction, properties) -> Dict[str, Any]:
    return {"best": str(best), "properties": props(properties)}


def build() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    checks: Dict[str, bool] = {}
    self_test = R.self_test()
    checks["validator_self_test_no_alarm_and_alarms"] = all(self_test.values())

    W = S.worlds()
    WID = [w["world_id"] for w in W]
    BY_ID = {w["world_id"]: w for w in W}
    endpoints = [w for w in W if w["kind"] != "boundary"]
    boundaries = [w for w in W if w["kind"] == "boundary"]
    positive_worlds = [w for w in endpoints if w["case"] <= 15]      # frozen: cases 1-15, both endpoints
    claim_props = {w["world_id"]: list(S.claimed_properties(w)) for w in W}
    cp = {k: tuple(sorted(v)) for k, v in claim_props.items()}

    # ---------------------------------------------------------------- substrate
    universe = S.full.build_universe()
    frontier_points, frontier_meta = S.frontier.build_risk_points()
    census_rhos = [(u.state_bits, u.error_now_count, u.error_delay_count) for u in universe]
    hist_full = dict(sorted(Counter(census_rhos).items()))
    hist_frontier = {(p.state_bits, p.error_now_count, p.error_delay_count): p.multiplicity for p in frontier_points}
    gp = S.evaluate_grammar(S.G_PLUS)
    hist_fast = S.compress(gp)
    checks["substrate_census_65552"] = len(universe) == S.CENSUS == frontier_meta["raw_candidates"] == len(gp)
    checks["substrate_three_histograms_identical"] = hist_full == hist_frontier == hist_fast
    checks["substrate_146_risk_points"] = len(hist_full) == 146
    checks["substrate_stateless_delay_floor_8_attained"] = min(r[2] for r in census_rhos if r[0] == 0) == 8
    checks["substrate_stateful_zero_zero_exists"] = (1, 0, 0) in hist_full
    checks["substrate_fast_evaluator_matches_901_per_candidate"] = all(
        (g[1], g[2], g[3]) == r for g, r in zip(gp, census_rhos)) and all(g[0] == u.surface_id for g, u in zip(gp, universe))
    substrate = {
        "census": len(universe), "risk_points": len(hist_full),
        "stateless_min_error_delay": min(r[2] for r in census_rhos if r[0] == 0),
        "stateful_zero_zero_multiplicity": hist_full[(1, 0, 0)],
        "k_carriers_in_g_plus": sum(1 for c in gp if c[4]),
        "k_free_in_g_plus": sum(1 for c in gp if not c[4]),
        "every_ed_below_8_candidate_carries_k": all(c[4] for c in gp if c[3] < 8),
        "registered_worlds": {"endpoints": len(endpoints), "boundaries": len(boundaries),
                              "positive_scalarizations": 2 * 15, "boundary_probes": len(boundaries)},
    }
    checks["substrate_k_target_only_realized_by_k"] = substrate["every_ed_below_8_candidate_carries_k"]

    # ---------------------------------------------------------------- D-X1 grammars
    grammars = [S.G_PLUS, S.G_MINUS, S.H1A_CAPACITY, S.H1B_MACRO, S.H1C_SEQUENCES, S.H1D_BUDGET]
    arm_data: Dict[str, Dict[str, Any]] = {}
    for g in grammars:
        census = gp if g is S.G_PLUS else S.evaluate_grammar(g)
        per_mode = S.scored_per_mode(g)
        pts = S.compress(census)
        outs = {w["world_id"]: S.outcome(pts, w, per_mode) for w in W}
        arm_data[g["grammar_id"]] = {
            "grammar": g, "census": census, "points": pts, "per_mode": per_mode,
            "descriptor": S.descriptor(g, census), "operators": S.operators(g),
            "k_count": sum(1 for c in census if c[4]),
            "k_target_realizable": any(F(c[3], per_mode) < F(1, 2) for c in census),
            "k_target_realized_by_winner": any(F(r[2], per_mode) < F(1, 2) for o in outs.values() for r in o["winners"]),
            "multiplicity": S.k_free_multiplicity(census),
            "outcomes": outs,
        }
    ge = S.evaluate_grammar(S.G_PLUS_IN_E_MINUS)
    ge_pts = S.compress(ge)
    arm_data["E_MINUS"] = {"points": ge_pts, "per_mode": 16, "grammar": S.G_PLUS_IN_E_MINUS,
                           "outcomes": {w["world_id"]: S.outcome(ge_pts, w) for w in W}}

    # #855 audits on every arm
    ids_e1 = [c[0] for c in gp]
    ns_arms: Dict[str, Dict[str, Any]] = {}

    def audit_grammar_arm(name: str, g: Dict[str, Any], pts, per_mode, identifiers, extra=(), drop=None):
        rec = ns_record(identifiers=list(S.operators(g)) + list(identifiers),
                        operators=S.operators(g), points=pts, frame=frame_for(g), per_mode=per_mode,
                        positive_worlds=positive_worlds, reference_world=W[0], extra_operator_costs=extra, drop=drop)
        ns_arms[name] = ns_summary(rec)

    for name in ("G_PLUS", "G_MINUS", "H1A_CAPACITY_DELETE_STATEFUL", "H1C_HALVED_SEQUENCE_SET", "H1D_HALVED_BUDGET"):
        d = arm_data[name]
        audit_grammar_arm(name, d["grammar"], d["points"], d["per_mode"], identifiers=[c[0] for c in d["census"]])
    d = arm_data["H1B_MACRO_PREV"]
    audit_grammar_arm("H1B_MACRO_PREV", d["grammar"], d["points"], d["per_mode"], identifiers=[c[0] for c in d["census"]],
                      extra=[{"operator": "READ_PREV", "target_privileged": True, "cost": "0"}])
    audit_grammar_arm("E_MINUS", S.G_PLUS_IN_E_MINUS, ge_pts, 16, identifiers=ids_e1)
    # registered cross-control hostile arms (C4: leaky surface ids; C5: undisclosed evaluation)
    dm = arm_data["G_MINUS"]
    audit_grammar_arm("G_MINUS_LEAKY_SURFACE_IDS", S.G_MINUS, dm["points"], 16,
                      identifiers=["stateless_" + c[0] for c in dm["census"]])
    audit_grammar_arm("G_MINUS_UNDISCLOSED_EVALUATION", S.G_MINUS, dm["points"], 16,
                      identifiers=[c[0] for c in dm["census"]], drop="evaluation")

    def twin_block(twin: str, twin_arm: str | None = None) -> Dict[str, Any]:
        p, t = arm_data["G_PLUS"], arm_data[twin]
        block = {
            "positive_arm": "G_PLUS", "twin_arm": twin_arm or twin,
            "descriptor_positive": p["descriptor"], "descriptor_twin": t["descriptor"],
            "operators_positive": p["operators"], "operators_twin": t["operators"],
            "twin_k_fingerprint_count": t["k_count"], "twin_k_target_realizable": t["k_target_realizable"],
            "positive_k_target_realized": p["k_target_realized_by_winner"],
            "multiplicity_reweighting": {"reported": True, "positive": p["multiplicity"], "twin": t["multiplicity"]},
            "outcome_positive_by_world": {w: list(p["outcomes"][w]["properties"]) for w in WID},
            "outcome_twin_by_world": {w: list(t["outcomes"][w]["properties"]) for w in WID},
            "interpretation": "K_DEPENDENCE_INTERPRETED_AGAINST_MATCHED_TWIN",
            "declared_terminal": None,
        }
        return block

    def seal(block: Dict[str, Any], evaluate, *args) -> Dict[str, Any]:
        block["declared_terminal"] = evaluate(block, *args, check_declared=False)["terminal"]
        return block

    ns_positive_block = {"arms": {k: ns_arms[k] for k in ("G_PLUS", "G_MINUS", "E_MINUS")}}
    twin_blocks = {}
    for twin in ("G_MINUS", "H1A_CAPACITY_DELETE_STATEFUL", "H1B_MACRO_PREV", "H1C_HALVED_SEQUENCE_SET", "H1D_HALVED_BUDGET"):
        ns_for = {"arms": {"G_PLUS": ns_arms["G_PLUS"], twin: ns_arms[twin]}}
        twin_blocks[twin] = seal(twin_block(twin), R.evaluate_matched_twin, ns_for)
    d_x1_gates = {}
    for twin, blk in twin_blocks.items():
        ns_for = {"arms": {"G_PLUS": ns_arms["G_PLUS"], twin: ns_arms[twin]}}
        v = R.evaluate_matched_twin(blk, ns_for)
        t = arm_data[twin]
        d_x1_gates[twin] = {
            "terminal": v["terminal"], "reasons": v["reasons"],
            "mismatched_coordinates": [c for c in R.DESCRIPTOR_COORDINATES if blk["descriptor_positive"][c] != blk["descriptor_twin"][c]],
            "candidate_count": t["descriptor"]["candidate_count"], "budget": t["descriptor"]["budget"],
            "k_fingerprint_count": t["k_count"], "k_target_realizable": t["k_target_realizable"],
            "min_error_delay": min(c[3] for c in t["census"]), "scored_events_per_mode": t["per_mode"],
            "low_endpoints_persistent": sum(1 for w in endpoints if w["kind"] == "low" and t["outcomes"][w["world_id"]]["properties"] == (PERSISTENT,)),
            "low_endpoint_best_rises_vs_g_plus": sum(1 for w in endpoints if w["kind"] == "low"
                                                     and t["outcomes"][w["world_id"]]["best"] > arm_data["G_PLUS"]["outcomes"][w["world_id"]]["best"]),
            "no_smuggling_terminal": ns_arms[twin]["terminal"],
        }
    gp_out, gm_out = arm_data["G_PLUS"]["outcomes"], arm_data["G_MINUS"]["outcomes"]
    d_x1 = {
        "registered_twin": "G_MINUS (state-register ablation in place: every next-state table replaced by the constant-0 table)",
        "descriptor_g_plus": arm_data["G_PLUS"]["descriptor"],
        "gates": d_x1_gates,
        "k_free_multiplicity_reweighting": {"G_PLUS": arm_data["G_PLUS"]["multiplicity"], "G_MINUS": arm_data["G_MINUS"]["multiplicity"]},
        "g_minus_risk_points": [[S.rho_id(r), m] for r, m in arm_data["G_MINUS"]["points"].items()],
        "phase_law_on_g_plus": {"transitions_persistent_to_stateless": sum(
            1 for cid in range(1, 21) if gp_out["c%02d_low" % cid]["properties"] == (PERSISTENT,) and gp_out["c%02d_high" % cid]["properties"] == (STATELESS,)),
            "boundary_ties": sum(1 for w in boundaries if gp_out[w["world_id"]]["properties"] == (PERSISTENT, STATELESS))},
        "phase_law_on_matched_twin": {"transitions_persistent_to_stateless": sum(
            1 for cid in range(1, 21) if gm_out["c%02d_low" % cid]["properties"] == (PERSISTENT,) and gm_out["c%02d_high" % cid]["properties"] == (STATELESS,)),
            "worlds_stateless": sum(1 for w in W if gm_out[w["world_id"]]["properties"] == (STATELESS,))},
        "worlds_where_twin_outcome_differs": sum(1 for w in WID if gp_out[w]["properties"] != gm_out[w]["properties"]),
    }
    checks["dx1_registered_twin_matched"] = d_x1_gates["G_MINUS"]["terminal"] == R.MATCHED
    checks["dx1_twin_count_equal_65552"] = d_x1_gates["G_MINUS"]["candidate_count"] == 65552
    checks["dx1_twin_collapses_onto_16_k_free_behaviours_x4097"] = arm_data["G_MINUS"]["multiplicity"] == {
        "classes": 16, "min_per_class": 4097, "max_per_class": 4097, "total_k_free": 65552}
    checks["dx1_positive_k_free_16_behaviours_x33"] = arm_data["G_PLUS"]["multiplicity"] == {
        "classes": 16, "min_per_class": 33, "max_per_class": 33, "total_k_free": 528}
    checks["dx1_twin_k_target_unrealizable"] = arm_data["G_MINUS"]["k_target_realizable"] is False
    checks["dx1_phase_law_20_of_20_on_g_plus"] = d_x1["phase_law_on_g_plus"]["transitions_persistent_to_stateless"] == 20 and d_x1["phase_law_on_g_plus"]["boundary_ties"] == 20
    checks["dx1_persistent_regime_vanishes_in_matched_twin"] = d_x1["phase_law_on_matched_twin"]["worlds_stateless"] == 60
    checks["dx1_h1a_capacity_unmatched"] = d_x1_gates["H1A_CAPACITY_DELETE_STATEFUL"]["terminal"] == R.UNMATCHED and "candidate_count" in d_x1_gates["H1A_CAPACITY_DELETE_STATEFUL"]["mismatched_coordinates"]
    checks["dx1_h1a_performance_falls_yet_refused"] = d_x1_gates["H1A_CAPACITY_DELETE_STATEFUL"]["low_endpoint_best_rises_vs_g_plus"] == 20
    checks["dx1_h1b_macro_unmatched"] = d_x1_gates["H1B_MACRO_PREV"]["terminal"] == R.UNMATCHED and "COMPENSATING_OPERATOR:READ_PREV" in d_x1_gates["H1B_MACRO_PREV"]["reasons"]
    checks["dx1_h1c_sequences_unmatched"] = d_x1_gates["H1C_HALVED_SEQUENCE_SET"]["terminal"] == R.UNMATCHED and "DESCRIPTOR_MISMATCH:sequence_set" in d_x1_gates["H1C_HALVED_SEQUENCE_SET"]["reasons"]
    checks["dx1_h1d_budget_unmatched"] = d_x1_gates["H1D_HALVED_BUDGET"]["terminal"] == R.UNMATCHED and d_x1_gates["H1D_HALVED_BUDGET"]["mismatched_coordinates"] == ["budget"]
    checks["dx1_no_smuggling_admissible_on_both_registered_twins"] = all(
        R._ns_arm_state({"arms": ns_arms}, k) == "ADMISSIBLE" for k in ("G_PLUS", "G_MINUS"))

    # ---------------------------------------------------------------- D-X1E ecology twin
    def eco_gate(e: Dict[str, Any]) -> Dict[str, Any]:
        dp, dm_ = S.ecology_descriptor(S.E_PLUS), S.ecology_descriptor(e)
        mism = [k for k in dp if dp[k] != dm_[k]]
        removed = S.PREVIOUS not in e["mode_targets"] and e["mode_targets"] != S.E_PLUS["mode_targets"]
        return {"terminal": "MATCHED_ECOLOGY_TWIN" if (not mism and removed) else "ECOLOGY_TWIN_UNMATCHED",
                "mismatched_coordinates": mism, "k_relevant_demand_removed": removed,
                "mode_targets": list(e["mode_targets"])}
    eo = arm_data["E_MINUS"]["outcomes"]
    d_x1e = {
        "descriptor_e_plus": S.ecology_descriptor(S.E_PLUS),
        "gates": {e["ecology_id"]: eco_gate(e) for e in (S.E_MINUS, S.E_MINUS_HALVED, S.E_MINUS_ETA)},
        "g_plus_in_e_minus": {"stateless_zero_zero_multiplicity": ge_pts.get((0, 0, 0), 0),
                              "worlds_stateless": sum(1 for w in W if eo[w["world_id"]]["properties"] == (STATELESS,)),
                              "worlds_persistent_or_tie": sum(1 for w in W if PERSISTENT in eo[w["world_id"]]["properties"])},
        "no_smuggling_terminal_e_minus": ns_arms["E_MINUS"]["terminal"],
    }
    checks["dx1e_registered_ecology_twin_matched"] = d_x1e["gates"]["E_MINUS"]["terminal"] == "MATCHED_ECOLOGY_TWIN"
    checks["dx1e_halved_sequences_unmatched"] = d_x1e["gates"]["E_MINUS_HOSTILE_HALVED_SEQUENCES"]["terminal"] == "ECOLOGY_TWIN_UNMATCHED"
    checks["dx1e_eta_rescale_unmatched"] = d_x1e["gates"]["E_MINUS_HOSTILE_ETA_RESCALED"]["terminal"] == "ECOLOGY_TWIN_UNMATCHED"
    checks["dx1e_persistent_regime_vanishes_without_memory_demand"] = d_x1e["g_plus_in_e_minus"]["worlds_stateless"] == 60

    # ---------------------------------------------------------------- D-X2 encodings
    e2 = E2.evaluate_census()
    e2_rho = {x[0]: (x[1], x[2], x[3]) for x in e2}
    phi = {u.surface_id: E2.surface_id(phi_index(i)) for i, u in enumerate(universe)}
    injective = len(set(phi.values())) == len(phi)
    surjective = set(phi.values()) == set(e2_rho)
    proj_mism = sum(1 for u, r in zip(universe, census_rhos) if e2_rho.get(phi[u.surface_id]) != r)
    # resource fingerprint r = (en, ed, s) as exact rationals, compared coordinatewise
    res_mism = sum(1 for u, r in zip(universe, census_rhos)
                   if (e2_rho[phi[u.surface_id]][1], e2_rho[phi[u.surface_id]][2], e2_rho[phi[u.surface_id]][0]) != (r[1], r[2], r[0]))
    e2_classes: Dict[Any, List[str]] = {}
    for sid, r in e2_rho.items():
        e2_classes.setdefault(r, []).append(sid)
    e2_hist = {r: len(v) for r, v in e2_classes.items()}

    s1_results = {w["world_id"]: S.full.search(universe, w["p"], w["eta"], w["lambda"]) for w in W}

    def e2_outcome(classes: Dict[Any, List[str]], w: Dict[str, Any]) -> Tuple[Fraction, List[str], List[Any]]:
        a, b, c = S.world_weights(w)
        vals = {r: a * r[1] + b * r[2] + c * r[0] for r in classes}
        best = min(vals.values())
        win = sorted((r for r, v in vals.items() if v == best), key=lambda r: (r[0], r[1], r[2]))
        return best, sorted(i for r in win for i in classes[r]), win

    enc_e1, enc_e2, lex_e1, lex_e2 = {}, {}, {}, {}
    winner_ids_agree = 0
    for w in W:
        r1 = s1_results[w["world_id"]]
        best2, ids2, win2 = e2_outcome(e2_classes, w)
        enc_e1[w["world_id"]] = conclusion_entry(r1["best"], [S.PROPERTY_OF_STATE_BITS[b] for b in r1["winner_state_bits"]])
        enc_e2[w["world_id"]] = conclusion_entry(best2, [S.PROPERTY_OF_STATE_BITS[int(r[0])] for r in win2])
        winner_ids_agree += int(sorted(phi[i] for i in r1["winner_ids"]) == ids2)
        first1 = min(r1["winner_ids"])
        first2 = min(ids2)
        lex_e1[w["world_id"]] = conclusion_entry(r1["best"], [S.PROPERTY_OF_STATE_BITS[universe[int(first1[1:])].state_bits]])
        lex_e2[w["world_id"]] = conclusion_entry(best2, [S.PROPERTY_OF_STATE_BITS[int(e2_rho[first2][0])]])

    def enc_block(e2_census_size: int, bij: Dict[str, Any], pm: int, rm: int, rule: str,
                  c1: Dict[str, Any], c2: Dict[str, Any], e2_arm: str) -> Dict[str, Any]:
        return {"reference_census_size": S.CENSUS,
                "encodings": [{"encoding_id": "E1_TABLE", "arm": "G_PLUS", "surface_alphabet": ["0", "1"],
                               "surface_id_pattern": "q[0-9]{5}", "census_size": len(universe)},
                              {"encoding_id": "E2_RULE_LIST", "arm": e2_arm, "surface_alphabet": list(E2.SURFACE_ALPHABET),
                               "surface_id_pattern": E2.SURFACE_ID_PATTERN, "census_size": e2_census_size}],
                "bijection": bij, "projection_mismatches": pm, "resource_fingerprint_mismatches": rm,
                "decision_rule": rule, "conclusion_by_encoding": {"E1_TABLE": c1, "E2_RULE_LIST": c2},
                "declared_terminal": None}

    bij_ok = {"domain_size": len(phi), "codomain_size": len(e2_rho), "injective": injective, "surjective": surjective}
    enc_positive = seal(enc_block(len(e2), bij_ok, proj_mism, res_mism, "SEMANTIC_ARGMIN_SET", enc_e1, enc_e2, "G_PLUS_E2"),
                        R.evaluate_encoding, cp)
    # H2a: an alleged encoding whose map silently deletes one candidate (q00002, a stateless optimum)
    dropped = phi["q00002"]
    e2_classes_h2a = {r: [i for i in v if i != dropped] for r, v in e2_classes.items()}
    e2_classes_h2a = {r: v for r, v in e2_classes_h2a.items() if v}
    h2a_c2 = {w["world_id"]: conclusion_entry(*(lambda o: (o[0], [S.PROPERTY_OF_STATE_BITS[int(r[0])] for r in o[2]]))(e2_outcome(e2_classes_h2a, w))) for w in W}
    bij_h2a = {"domain_size": len(phi) - 1, "codomain_size": len(e2_rho) - 1, "injective": True, "surjective": True}
    enc_h2a = seal(enc_block(len(e2) - 1, bij_h2a, 0, 0, "SEMANTIC_ARGMIN_SET", enc_e1, h2a_c2, "G_PLUS_E2"),
                   R.evaluate_encoding, cp)
    # H2b: an E2 evaluator that scales delay error by 15/16
    e2b = E2.evaluate_census(delay_error_scale=F(15, 16))
    e2b_rho = {x[0]: (x[1], x[2], x[3]) for x in e2b}
    pm_b = sum(1 for u, r in zip(universe, census_rhos) if e2b_rho[phi[u.surface_id]] != r)
    e2b_classes: Dict[Any, List[str]] = {}
    for sid, r in e2b_rho.items():
        e2b_classes.setdefault(r, []).append(sid)
    h2b_c2 = {w["world_id"]: conclusion_entry(*(lambda o: (o[0], [S.PROPERTY_OF_STATE_BITS[int(r[0])] for r in o[2]]))(e2_outcome(e2b_classes, w))) for w in W}
    enc_h2b = seal(enc_block(len(e2b), bij_ok, pm_b, pm_b, "SEMANTIC_ARGMIN_SET", enc_e1, h2b_c2, "G_PLUS_E2_H2B"),
                   R.evaluate_encoding, cp)
    # H2c: a decision rule that tie-breaks on lexicographic surface ids
    enc_h2c = seal(enc_block(len(e2), bij_ok, proj_mism, res_mism, "LEXICOGRAPHIC_SURFACE_TIE_BREAK", lex_e1, lex_e2, "G_PLUS_E2"),
                   R.evaluate_encoding, cp)
    e2_pts = {r: len(v) for r, v in e2_classes.items()}
    ns_arms["G_PLUS_E2"] = ns_summary(ns_record(
        identifiers=E2_OPERATORS + list(E2.SURFACE_ALPHABET) + sorted(e2_rho), operators=E2_OPERATORS,
        points={(int(r[0]), int(r[1]), int(r[2])): m for r, m in e2_pts.items()}, frame=frame_for(S.G_PLUS), per_mode=16,
        positive_worlds=positive_worlds, reference_world=W[0]))
    e2b_pts: Dict[Any, int] = {}
    for r, v in e2b_classes.items():
        e2b_pts[(int(r[0]), r[1], r[2])] = len(v)
    ns_arms["G_PLUS_E2_H2B"] = ns_summary(ns_record(
        identifiers=E2_OPERATORS + list(E2.SURFACE_ALPHABET) + sorted(e2b_rho), operators=E2_OPERATORS,
        points=e2b_pts, frame=frame_for(S.G_PLUS), per_mode=16, positive_worlds=positive_worlds, reference_world=W[0]))
    enc_gates = {}
    for name, blk in (("E1_E2_REGISTERED", enc_positive), ("H2A_DELETION", enc_h2a), ("H2B_COST_MUTATION", enc_h2b), ("H2C_SURFACE_TIE", enc_h2c)):
        v = R.evaluate_encoding(blk, cp)
        enc_gates[name] = {"terminal": v["terminal"], "reasons": v["reasons"][:6], "reason_count": len(v["reasons"])}
    d_x2 = {
        "encodings": {"E1_TABLE": {"surface_id_pattern": "q[0-9]{5}", "alphabet": ["0", "1"], "census": len(universe)},
                      "E2_RULE_LIST": {"surface_id_pattern": E2.SURFACE_ID_PATTERN, "alphabet": list(E2.SURFACE_ALPHABET), "census": len(e2)}},
        "bijection": bij_ok, "projection_mismatches": proj_mism, "resource_fingerprint_mismatches": res_mism,
        "histograms_equal": e2_hist == hist_full,
        "worlds_with_phi_mapped_winner_ids_equal": winner_ids_agree,
        "gates": enc_gates,
        "h2a": {"dropped_e1_candidate": "q00002", "dropped_e2_candidate": dropped,
                "conclusions_still_agree_after_projection": h2a_c2 == enc_e2},
        "h2b": {"delay_error_scale": "15/16", "projection_mismatches": pm_b},
        "h2c": {"worlds_where_lexicographic_rule_disagrees": sum(1 for w in WID if lex_e1[w] != lex_e2[w]),
                "e1_boundary_choice": lex_e1["c01_boundary"]["properties"], "e2_boundary_choice": lex_e2["c01_boundary"]["properties"]},
    }
    checks["dx2_e2_census_65552"] = len(e2) == 65552
    checks["dx2_bijection_total"] = injective and surjective and len(phi) == 65552
    checks["dx2_zero_projection_mismatches_full_census"] = proj_mism == 0 and res_mism == 0
    checks["dx2_histograms_equal"] = d_x2["histograms_equal"]
    checks["dx2_winner_ids_agree_all_60_worlds"] = winner_ids_agree == 60
    checks["dx2_registered_pair_encoding_robust"] = enc_gates["E1_E2_REGISTERED"]["terminal"] == R.ENC_ROBUST
    checks["dx2_h2a_deletion_not_equivalent"] = enc_gates["H2A_DELETION"]["terminal"] == R.ENC_NOT_EQUIVALENT and d_x2["h2a"]["conclusions_still_agree_after_projection"]
    checks["dx2_h2b_cost_mutation_not_equivalent"] = enc_gates["H2B_COST_MUTATION"]["terminal"] == R.ENC_NOT_EQUIVALENT
    checks["dx2_h2c_surface_tie_sensitive"] = enc_gates["H2C_SURFACE_TIE"]["terminal"] == R.ENC_SENSITIVE and d_x2["h2c"]["worlds_where_lexicographic_rule_disagrees"] == 20

    # ---------------------------------------------------------------- D-X3 search procedures
    point_rhos = [(p.state_bits, p.error_now_count, p.error_delay_count) for p in frontier_points]
    labelled = [("z%03d" % (len(point_rhos) - 1 - i), r) for i, r in enumerate(point_rhos)]
    class_index = {r: i for i, r in enumerate(sorted(hist_full))}
    census_idx = [class_index[r] for r in census_rhos]
    classes_sorted = sorted(hist_full)
    s1_trace_digest = SP.trace_digest(census_rhos)
    runs: Dict[str, Dict[str, Dict[str, Any]]] = {k: {} for k in SP.DIFFERENCE_TABLES}
    s1_agree = s2_agree = 0
    for w in W:
        wid = w["world_id"]
        wt = S.world_weights(w)
        # S1: #901 code for the conclusion; census-order acceptance sequence for the trace certificate
        r1 = s1_results[wid]
        exact = [SP.value(r, wt) for r in classes_sorted]
        scale = 1
        for v in exact:
            scale = scale * v.denominator // gcd(scale, v.denominator)
        vals = [int(v * scale) for v in exact]
        best = None
        letters = []
        winners = 0
        for ci in census_idx:
            v = vals[ci]
            if best is None or v < best:
                best, winners = v, 1
                letters.append("N")
            elif v == best:
                winners += 1
                letters.append("T")
            else:
                letters.append("R")
        s1_agree += int(F(best, scale) == r1["best"] and winners == len(r1["winner_ids"]))
        runs["S1_FULL_ENUMERATION"][wid] = {"best": r1["best"], "properties": [S.PROPERTY_OF_STATE_BITS[b] for b in r1["winner_state_bits"]],
                                            "trace": s1_trace_digest, "accept": SP.acceptance_digest(letters),
                                            "evaluations": len(census_idx), "pruned": 0, "certificate": len(census_idx) == S.CENSUS,
                                            "winner_vectors": sorted({(r[1], r[2], r[0]) for r in (census_rhos[int(i[1:])] for i in r1["winner_ids"])})}
        r2 = S.frontier.search(frontier_points, w["p"], w["eta"], w["lambda"])
        t2 = SP.s2_run(point_rhos, wt)
        s2_agree += int(t2["best"] == r2["best"] and t2["evaluated_points"] == r2["evaluated_points"]
                        and t2["pruned_points"] == r2["pruned_points"]
                        and sorted({r[0] for r in t2["winner_rhos"]}) == list(r2["winner_state_bits"]))
        runs["S2_RISK_FRONTIER_BRANCH_BOUND"][wid] = {"best": r2["best"], "properties": [S.PROPERTY_OF_STATE_BITS[b] for b in r2["winner_state_bits"]],
                                                      "trace": SP.trace_digest(t2["trace"]), "accept": SP.acceptance_digest(t2["acceptance"]),
                                                      "evaluations": t2["evaluated_points"], "pruned": t2["pruned_points"],
                                                      "certificate": t2["certificate_verified"],
                                                      "winner_vectors": sorted({(r[1], r[2], r[0]) for r in t2["winner_rhos"]})}
        for key, fn, arg in (("S3_BEST_FIRST_CERTIFICATE", SP.s3_run, point_rhos),
                             ("H3A_FIRST_ACCEPT_PRICE_SORTED", SP.h3a_run, point_rhos),
                             ("H3B_REENCODED_BRANCH_BOUND", SP.h3b_run, labelled)):
            t = fn(arg, wt)
            runs[key][wid] = {"best": t["best"], "properties": [S.PROPERTY_OF_STATE_BITS[r[0]] for r in t["winner_rhos"]],
                              "trace": SP.trace_digest(t["trace"]), "accept": SP.acceptance_digest(t["acceptance"]),
                              "evaluations": t.get("evaluations", t.get("evaluated_points")),
                              "pruned": t.get("pruned_points", 0), "certificate": t["certificate_verified"],
                              "winner_vectors": sorted({(r[1], r[2], r[0]) for r in t["winner_rhos"]})}
    coverage_kind = {"S1_FULL_ENUMERATION": "EXHAUSTIVE_CONSTRUCTION", "S2_RISK_FRONTIER_BRANCH_BOUND": "ADMISSIBLE_BOUND",
                     "S3_BEST_FIRST_CERTIFICATE": "OPTIMALITY_CERTIFICATE", "H3A_FIRST_ACCEPT_PRICE_SORTED": "INCOMPLETE",
                     "H3B_REENCODED_BRANCH_BOUND": "ADMISSIBLE_BOUND"}

    def searcher_record(key: str) -> Dict[str, Any]:
        rr = runs[key]
        verified = all(rr[w]["certificate"] for w in WID) and coverage_kind[key] != "INCOMPLETE"
        return {"searcher_id": key, "difference_table": dict(SP.DIFFERENCE_TABLES[key]),
                "coverage": {"kind": coverage_kind[key], "verified": verified},
                "search_cost": {"evaluations_total": sum(rr[w]["evaluations"] for w in WID),
                                "pruned_total": sum(rr[w]["pruned"] for w in WID),
                                "evaluations_min_per_world": min(rr[w]["evaluations"] for w in WID),
                                "evaluations_max_per_world": max(rr[w]["evaluations"] for w in WID)},
                "candidate_resource_cost_by_world": {w: {"objective": str(rr[w]["best"]), "winner_resource_vectors": [list(v) for v in rr[w]["winner_vectors"]]} for w in WID},
                "conclusion_by_world": {w: conclusion_entry(rr[w]["best"], rr[w]["properties"]) for w in WID},
                "trace_digest_by_probe": {w: rr[w]["trace"] for w in WID},
                "acceptance_digest_by_probe": {w: rr[w]["accept"] for w in WID}}

    def search_block(keys: Sequence[str]) -> Dict[str, Any]:
        return seal({"probes": list(WID), "searchers": [searcher_record(k) for k in keys], "declared_terminal": None},
                    R.evaluate_search, cp)

    search_positive = search_block(["S1_FULL_ENUMERATION", "S2_RISK_FRONTIER_BRANCH_BOUND", "S3_BEST_FIRST_CERTIFICATE"])
    search_h3a = search_block(["S1_FULL_ENUMERATION", "S2_RISK_FRONTIER_BRANCH_BOUND", "S3_BEST_FIRST_CERTIFICATE", "H3A_FIRST_ACCEPT_PRICE_SORTED"])
    search_h3b = search_block(["S2_RISK_FRONTIER_BRANCH_BOUND", "H3B_REENCODED_BRANCH_BOUND"])
    vpos, vh3a, vh3b = (R.evaluate_search(b, cp) for b in (search_positive, search_h3a, search_h3b))
    d_x3 = {
        "procedures": {k: {"coverage": searcher_record(k)["coverage"], "search_cost": searcher_record(k)["search_cost"],
                           "difference_table": SP.DIFFERENCE_TABLES[k]} for k in SP.DIFFERENCE_TABLES},
        "s1_trace_matches_901_counters_worlds": s1_agree,
        "s2_trace_matches_901_counters_worlds": s2_agree,
        "registered_triple": {"terminal": vpos["terminal"], "distinctness": vpos["distinctness"], "exhaustive_searchers": vpos["exhaustive_searchers"]},
        "h3a_early_stop": {"terminal": vh3a["terminal"], "disagreements": len(vh3a["reasons"]),
                           "disagreeing_worlds": sorted({r.split(":")[2] for r in vh3a["reasons"] if r.startswith("DISAGREES:")}),
                           "low_endpoints_wrong": sum(1 for w in endpoints if w["kind"] == "low" and runs["H3A_FIRST_ACCEPT_PRICE_SORTED"][w["world_id"]]["properties"] != [PERSISTENT])},
        "h3b_reencoding_masquerade": {"terminal": vh3b["terminal"], "distinctness": vh3b["distinctness"], "reasons": vh3b["reasons"]},
        "search_cost_separate_from_candidate_resource_cost": True,
    }
    checks["dx3_s1_trace_validated_against_901_all_worlds"] = s1_agree == 60
    checks["dx3_s2_trace_validated_against_901_all_worlds"] = s2_agree == 60
    checks["dx3_all_three_certificates_verified"] = all(searcher_record(k)["coverage"]["verified"] for k in ("S1_FULL_ENUMERATION", "S2_RISK_FRONTIER_BRANCH_BOUND", "S3_BEST_FIRST_CERTIFICATE"))
    checks["dx3_registered_triple_search_robust"] = vpos["terminal"] == R.SEARCH_ROBUST
    checks["dx3_three_pairs_materially_distinct"] = len(vpos["distinctness"]) == 3 and all(p["distinct"] for p in vpos["distinctness"])
    checks["dx3_h3a_search_sensitive_surfaced"] = vh3a["terminal"] == R.SEARCH_SENSITIVE and d_x3["h3a_early_stop"]["low_endpoints_wrong"] == 20
    checks["dx3_h3b_masquerade_not_distinct"] = vh3b["terminal"] == R.SEARCH_NOT_DISTINCT and vh3b["distinctness"][0]["reencoding"] is True and len(vh3b["distinctness"][0]["declared_axes_differing"]) >= 2

    # ---------------------------------------------------------------- D-X4 Pareto / scalarizations
    vectors = {S.rho_id(r): (F(r[1]), F(r[2]), F(r[0])) for r in hist_full}
    front = R.pareto_ids(vectors)
    mult_by_id = {S.rho_id(r): m for r, m in hist_full.items()}

    def scal_entry(w: Dict[str, Any], boundary: bool) -> Dict[str, Any]:
        wt = S.world_weights(w)
        return {"scalarization_id": w["world_id"], "weights": [str(x) for x in wt], "boundary_probe": boundary,
                "winners": R.argmin_ids(vectors, wt), "claimed_properties": list(S.claimed_properties(w))}

    scal_list = [scal_entry(w, False) for w in positive_worlds] + [scal_entry(w, True) for w in boundaries]
    raw_vectors = [{"point_id": S.rho_id(r), "vector": [str(r[1]), str(r[2]), str(r[0])], "multiplicity": m,
                    "property": S.PROPERTY_OF_STATE_BITS[r[0]]} for r, m in hist_full.items()]

    def scal_block(scals: List[Dict[str, Any]], claim: Dict[str, Any]) -> Dict[str, Any]:
        return seal({"coordinates": list(COORDS), "raw_vectors": raw_vectors, "pareto_set": front,
                     "scalarizations": scals, "declared_terminal": None}, R.evaluate_scalarization, claim)

    claim = {
        "claim_id": "GMI901_PHASE_LAW_K_DEPENDENCE_AT_REGISTERED_SCOPE",
        "mechanism": S.K_MECHANISM, "k_fingerprint": S.K_FINGERPRINT, "k_target_property": S.K_TARGET,
        "wording": "PRICE_CONDITIONAL",
        "scope": "#901 universe (65,552 candidates), 20 frozen cases: 40 endpoint worlds + 20 boundary worlds",
        "statement": "the argmin state property is PERSISTENT_STATE for lambda < eta*p/2 and STATELESS for lambda > eta*p/2 "
                     "(both at equality); the PERSISTENT_STATE regime is absent in the matched state-register ablation twin",
        "conclusion_by_world": claim_props,
        "frontier_invariants": copy.deepcopy(INVARIANTS),
    }
    claim_universal = dict(copy.deepcopy(claim), wording="UNIVERSAL_WINNER",
                           statement="PERSISTENT_STATE is the winner at registered scope (universal-winner wording)")
    scal_positive = scal_block(scal_list, claim)
    v4 = R.evaluate_scalarization(scal_positive, claim)
    v4u = R.evaluate_scalarization(scal_block(scal_list, claim_universal), claim_universal)
    # the issue's literal hostile: (1,4) vs (4,1) under weights (4,1) and (1,4)
    lit_claim = {"wording": "UNIVERSAL_WINNER", "frontier_invariants": []}
    lit_block = {"coordinates": ["r1", "r2"],
                 "raw_vectors": [{"point_id": "a", "vector": ["1", "4"], "multiplicity": 1, "property": "A"},
                                 {"point_id": "b", "vector": ["4", "1"], "multiplicity": 1, "property": "B"}],
                 "pareto_set": ["a", "b"],
                 "scalarizations": [{"scalarization_id": "w41", "weights": ["4", "1"], "boundary_probe": False, "winners": ["a"]},
                                    {"scalarization_id": "w14", "weights": ["1", "4"], "boundary_probe": False, "winners": ["b"]}],
                 "declared_terminal": R.SCAL_SENSITIVE}
    vlit = R.evaluate_scalarization(lit_block, lit_claim)
    zero_weight_probes = [s for s in scal_list if s["boundary_probe"] and any(F(x) == 0 for x in s["weights"])]
    d_x4 = {
        "coordinates": COORDS,
        "pareto_set": [{"point_id": k, "vector": [str(x) for x in vectors[k]], "multiplicity": mult_by_id[k]} for k in front],
        "registered_scalarizations": {"strictly_positive": len([s for s in scal_list if not s["boundary_probe"]]), "boundary_probes": len(boundaries),
                                      "boundary_probes_with_a_zero_weight": len(zero_weight_probes)},
        "winner_under_each_scalarization": {s["scalarization_id"]: s["winners"] for s in scal_list},
        "positive_winners_all_on_frontier": all(k in front for s in scal_list if not s["boundary_probe"] for k in s["winners"]),
        "dominated_points_in_argmin_at_zero_weight_probes": {s["scalarization_id"]: len([k for k in s["winners"] if k not in front]) for s in zero_weight_probes},
        "census_reversal_pair": {"a": "s0n0d8", "b": "s1n0d0", "incomparable": not R._dominates(vectors["s0n0d8"], vectors["s1n0d0"]) and not R._dominates(vectors["s1n0d0"], vectors["s0n0d8"]),
                                 "c01_low_winner": next(s["winners"] for s in scal_list if s["scalarization_id"] == "c01_low"),
                                 "c01_high_winner": next(s["winners"] for s in scal_list if s["scalarization_id"] == "c01_high"),
                                 "projection_ed_s": {"s0n0d8": ["8", "0"], "s1n0d0": ["0", "1"]}},
        "invariant_claims": v4["invariants_holding"],
        "price_conditional_claims": ["argmin state property follows lambda* = eta*p/2 at every registered scalarization"],
        "universal_winner_wording": {"terminal": v4u["terminal"], "reasons": v4u["reasons"]},
        "literal_issue_hostile_1_4_vs_4_1": {"terminal": vlit["terminal"], "reasons": vlit["reasons"]},
        "registered_price_conditional_terminal": v4["terminal"],
    }
    checks["dx4_pareto_set_two_points"] = front == ["s0n0d8", "s1n0d0"]
    checks["dx4_positive_scalarizations_30"] = d_x4["registered_scalarizations"]["strictly_positive"] == 30
    checks["dx4_positive_never_picks_dominated"] = d_x4["positive_winners_all_on_frontier"]
    checks["dx4_census_pair_reverses"] = d_x4["census_reversal_pair"]["incomparable"] and d_x4["census_reversal_pair"]["c01_low_winner"] == ["s1n0d0"] and d_x4["census_reversal_pair"]["c01_high_winner"] == ["s0n0d8"]
    checks["dx4_price_conditional_consistent"] = v4["terminal"] == R.PARETO_OK and v4["winner_reversal"] is True
    checks["dx4_universal_wording_sensitive"] = v4u["terminal"] == R.SCAL_SENSITIVE
    checks["dx4_literal_1_4_4_1_sensitive"] = vlit["terminal"] == R.SCAL_SENSITIVE
    checks["dx4_frontier_invariants_hold"] = v4["invariants_holding"] == [i["invariant_id"] for i in INVARIANTS]
    checks["dx4_zero_weight_probes_admit_dominated_ties"] = len(zero_weight_probes) == 4 and all(v > 0 for v in d_x4["dominated_points_in_argmin_at_zero_weight_probes"].values())

    # ---------------------------------------------------------------- metric perturbation control
    remint = {u.surface_id: "z%05d" % (S.CENSUS - 1 - i) for i, u in enumerate(universe)}
    e1_classes: Dict[Any, List[str]] = {}
    for u, r in zip(universe, census_rhos):
        e1_classes.setdefault(r, []).append(u.surface_id)
    rm_classes = {r: sorted(remint[i] for i in v) for r, v in e1_classes.items()}
    class_bijection_ok = all(sorted(phi[i] for i in v) == sorted(e2_classes[r]) for r, v in e1_classes.items()) and \
        len(set(remint.values())) == S.CENSUS
    tables = {"E1_TABLE": {r: len(v) for r, v in e1_classes.items()},
              "E1_ID_RELABEL": {r: len(v) for r, v in rm_classes.items()},
              "E2_RULE_LIST": {r: len(v) for r, v in e2_classes.items()}}
    clustering_equal = tables["E1_TABLE"] == tables["E1_ID_RELABEL"] == tables["E2_RULE_LIST"] and len(tables["E1_TABLE"]) == 146
    perturbed = stable = boundary_ties = mirrored_flips = excluded = 0
    argmin_cell_stable_positive = argmin_cell_changed_zero_weight = 0
    bound_holds = True
    for w in endpoints:
        thr = w["eta"] * w["p"] / 2
        m = abs(w["lambda"] - thr)
        base_now, base_delay, base_price = w["eta"] * (1 - w["p"]), w["eta"] * w["p"], w["lambda"]
        base = {k: S.outcome(t, w) for k, t in tables.items()}
        for d0, d1, d2 in product((-m / 2, F(0), m / 2), repeat=3):
            wn, wd, lam = base_now + d0, base_delay + d1, base_price + d2
            if wn < 0 or wd <= 0 or lam <= 0:
                excluded += 1
                continue
            perturbed += 1
            bound_holds = bound_holds and abs(d2 - d1 / 2) < m
            wt = (wn / 16, wd / 16, lam)
            outs = {k: S.outcome(t, w, weights=wt) for k, t in tables.items()}
            if all(outs[k]["properties"] == base[k]["properties"] == base["E1_TABLE"]["properties"] for k in tables):
                stable += 1
            if base_now > 0:
                argmin_cell_stable_positive += int(outs["E1_TABLE"]["winners"] == base["E1_TABLE"]["winners"])
            elif outs["E1_TABLE"]["winners"] != base["E1_TABLE"]["winners"]:
                argmin_cell_changed_zero_weight += 1
        at_boundary = {k: S.outcome(t, w, weights=(base_now / 16, base_delay / 16, thr)) for k, t in tables.items()}
        boundary_ties += int(all(o["properties"] == (PERSISTENT, STATELESS) for o in at_boundary.values()))
        mirrored = {k: S.outcome(t, w, weights=(base_now / 16, base_delay / 16, 2 * thr - w["lambda"])) for k, t in tables.items()}
        flipped = (STATELESS,) if base["E1_TABLE"]["properties"] == (PERSISTENT,) else (PERSISTENT,)
        mirrored_flips += int(all(o["properties"] == flipped for o in mirrored.values()))
    positive_perturbed = sum(1 for w in endpoints if w["p"] < 1) * 27
    perturbation = {
        "rule": "delta in {-m/2, 0, +m/2} on (eta*(1-p), eta*p, lambda) with m = |lambda - eta*p/2| of the perturbed world; "
                "worlds with a negative error weight or nonpositive price are excluded",
        "endpoint_worlds": len(endpoints), "perturbed_worlds": perturbed, "excluded_invalid": excluded,
        "winner_state_partition_stable_all_three_encodings": stable,
        "analytic_bound_abs_dprice_minus_half_ddelay_below_margin": bound_holds,
        "exact_boundary_ties_all_three_encodings": boundary_ties,
        "mirrored_price_flips_all_three_encodings": mirrored_flips,
        "risk_clustering_146_classes_identical_across_encodings": clustering_equal,
        "class_level_bijections_verified": class_bijection_ok,
        "diagnostic_argmin_cell": {"stable_at_strictly_positive_worlds": argmin_cell_stable_positive,
                                   "strictly_positive_perturbed_worlds": positive_perturbed,
                                   "changed_at_zero_weight_worlds_under_positive_now_weight": argmin_cell_changed_zero_weight},
    }
    checks["perturbation_partition_stable_inside_bound"] = stable == perturbed and bound_holds
    checks["perturbation_flips_exactly_at_boundary"] = boundary_ties == 40 and mirrored_flips == 40
    checks["perturbation_clustering_and_remints_preserved"] = clustering_equal and class_bijection_ok
    checks["perturbation_argmin_cell_stable_at_positive_worlds"] = argmin_cell_stable_positive == positive_perturbed

    # ---------------------------------------------------------------- admission records + census
    ns_all = {"arms": {k: ns_arms[k] for k in ("G_PLUS", "G_MINUS", "E_MINUS", "G_PLUS_E2")}}
    positive = {"schema": R.SCHEMA_ID, "record_id": "GMI859_POSITIVE_WITNESS_901_FAMILY", "claim": claim,
                "controls": {"MATCHED_TWIN": twin_blocks["G_MINUS"], "ENCODING": enc_positive, "SEARCH": search_positive,
                             "SCALARIZATION": scal_positive, "NO_SMUGGLING": ns_all}}

    def variant(rid: str, **changes: Any) -> Dict[str, Any]:
        r = copy.deepcopy(positive)
        r["record_id"] = rid
        for k, v in changes.items():
            if k == "claim":
                r["claim"] = copy.deepcopy(v)
            elif v is None:
                del r["controls"][k]
            else:
                r["controls"][k] = copy.deepcopy(v)
        return r

    def with_arm(twin: str) -> Dict[str, Any]:
        n = copy.deepcopy(ns_all)
        n["arms"][twin] = ns_arms[twin]
        return n

    ns_h2b = copy.deepcopy(ns_all)
    ns_h2b["arms"]["G_PLUS_E2_H2B"] = ns_arms["G_PLUS_E2_H2B"]
    twin_c4 = copy.deepcopy(twin_blocks["G_MINUS"])
    twin_c4["twin_arm"] = "G_MINUS_LEAKY_SURFACE_IDS"
    twin_c5 = copy.deepcopy(twin_blocks["G_MINUS"])
    twin_c5["twin_arm"] = "G_MINUS_UNDISCLOSED_EVALUATION"
    scal_empty = scal_block([], claim)
    scal_zero_only = scal_block([dict(s, boundary_probe=False) for s in zero_weight_probes], claim)
    census_records = [
        (positive, R.ROBUST, []),
        (variant("DELETE_MATCHED_TWIN", MATCHED_TWIN=None), R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.CONTROL_MISSING)]),
        (variant("DELETE_ENCODING", ENCODING=None), R.CANNOT_PREFIX + "ENCODING", [("ENCODING", R.CONTROL_MISSING)]),
        (variant("DELETE_SEARCH", SEARCH=None), R.CANNOT_PREFIX + "SEARCH", [("SEARCH", R.CONTROL_MISSING)]),
        (variant("DELETE_SCALARIZATION", SCALARIZATION=None), R.CANNOT_PREFIX + "SCALARIZATION", [("SCALARIZATION", R.CONTROL_MISSING)]),
        (variant("DELETE_NO_SMUGGLING", NO_SMUGGLING=None), R.CANNOT_PREFIX + "NO_SMUGGLING",
         [("MATCHED_TWIN", R.TWIN_AUDIT_NOT_EVALUABLE), ("NO_SMUGGLING", R.CONTROL_MISSING)]),
        (variant("H1A_CAPACITY", MATCHED_TWIN=twin_blocks["H1A_CAPACITY_DELETE_STATEFUL"], NO_SMUGGLING=with_arm("H1A_CAPACITY_DELETE_STATEFUL")),
         R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.UNMATCHED)]),
        (variant("H1B_MACRO", MATCHED_TWIN=twin_blocks["H1B_MACRO_PREV"], NO_SMUGGLING=with_arm("H1B_MACRO_PREV")),
         R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.UNMATCHED), ("NO_SMUGGLING", R.NS_NOT_CLEAN)]),
        (variant("H1C_SEQUENCES", MATCHED_TWIN=twin_blocks["H1C_HALVED_SEQUENCE_SET"], NO_SMUGGLING=with_arm("H1C_HALVED_SEQUENCE_SET")),
         R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.UNMATCHED)]),
        (variant("H1D_BUDGET", MATCHED_TWIN=twin_blocks["H1D_HALVED_BUDGET"], NO_SMUGGLING=with_arm("H1D_HALVED_BUDGET")),
         R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.UNMATCHED)]),
        (variant("C1_TWIN_VALID_ENCODING_CENSUS_BROKEN_H2A", ENCODING=enc_h2a), R.CANNOT_PREFIX + "ENCODING", [("ENCODING", R.ENC_NOT_EQUIVALENT)]),
        (variant("H2B_COST_MUTATION", ENCODING=enc_h2b, NO_SMUGGLING=ns_h2b), R.CANNOT_PREFIX + "ENCODING", [("ENCODING", R.ENC_NOT_EQUIVALENT)]),
        (variant("H2C_SURFACE_TIE", ENCODING=enc_h2c), R.CANNOT_PREFIX + "ENCODING", [("ENCODING", R.ENC_SENSITIVE)]),
        (variant("H3A_EARLY_STOP", SEARCH=search_h3a), R.CANNOT_PREFIX + "SEARCH", [("SEARCH", R.SEARCH_SENSITIVE)]),
        (variant("C2_SEARCH_REENCODINGS_ONLY_H3B", SEARCH=search_h3b), R.CANNOT_PREFIX + "SEARCH", [("SEARCH", R.SEARCH_NOT_DISTINCT)]),
        (variant("H4A_UNIVERSAL_WINNER_WORDING", claim=claim_universal, SCALARIZATION=scal_block(scal_list, claim_universal)),
         R.CANNOT_PREFIX + "SCALARIZATION", [("SCALARIZATION", R.SCAL_SENSITIVE)]),
        (variant("C3_EMPTY_SCALARIZATION_SET", SCALARIZATION=scal_empty), R.CANNOT_PREFIX + "SCALARIZATION", [("SCALARIZATION", R.SCAL_INSUFFICIENT)]),
        (variant("C3B_ZERO_WEIGHT_PROBES_ONLY", SCALARIZATION=scal_zero_only), R.CANNOT_PREFIX + "SCALARIZATION", [("SCALARIZATION", R.SCAL_INSUFFICIENT)]),
        (variant("C4_UNCLEAN_NEGATIVE_ARM", MATCHED_TWIN=twin_c4, NO_SMUGGLING=with_arm("G_MINUS_LEAKY_SURFACE_IDS")),
         R.CANNOT_PREFIX + "NO_SMUGGLING", [("NO_SMUGGLING", R.NS_NOT_CLEAN)]),
        (variant("C5_UNEVALUABLE_NEGATIVE_ARM", MATCHED_TWIN=twin_c5, NO_SMUGGLING=with_arm("G_MINUS_UNDISCLOSED_EVALUATION")),
         R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.TWIN_AUDIT_NOT_EVALUABLE), ("NO_SMUGGLING", R.NS_NOT_CLEAN)]),
        (variant("C6_TWIN_AND_SEARCH_HOSTILE", MATCHED_TWIN=twin_blocks["H1A_CAPACITY_DELETE_STATEFUL"],
                 NO_SMUGGLING=with_arm("H1A_CAPACITY_DELETE_STATEFUL"), SEARCH=search_h3a),
         R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.UNMATCHED), ("SEARCH", R.SEARCH_SENSITIVE)]),
        (variant("C7_ALL_FOUR_CONTROLS_HOSTILE", MATCHED_TWIN=twin_blocks["H1A_CAPACITY_DELETE_STATEFUL"],
                 NO_SMUGGLING=with_arm("H1A_CAPACITY_DELETE_STATEFUL"), ENCODING=enc_h2c, SEARCH=search_h3a,
                 claim=claim_universal, SCALARIZATION=scal_block(scal_list, claim_universal)),
         R.CANNOT_PREFIX + "MATCHED_TWIN", [("MATCHED_TWIN", R.UNMATCHED), ("ENCODING", R.ENC_SENSITIVE),
                                            ("SEARCH", R.SEARCH_SENSITIVE), ("SCALARIZATION", R.SCAL_SENSITIVE)]),
    ]
    census = []
    census_ok = True
    for rec, want_terminal, want_failures in census_records:
        v = R.validate_record(rec)
        got = [(c, v["control_terminals"][c]) for c in v["failing_controls"]]
        ok = v["terminal"] == want_terminal and got == [tuple(x) for x in want_failures]
        census_ok = census_ok and ok
        census.append({"record_id": rec["record_id"], "record_sha256": sha256_text(R.canonical_json(rec)),
                       "terminal": v["terminal"], "failing_controls": [[c, t] for c, t in got],
                       "expected_terminal": want_terminal, "expected_failing_controls": [list(x) for x in want_failures],
                       "exact_match": ok})
    vpos_rec = R.validate_record(positive)
    checks["admission_positive_witness_robust"] = vpos_rec["terminal"] == R.ROBUST and all(vpos_rec["conditions"].values())
    checks["admission_census_exact_typed_terminals"] = census_ok
    checks["admission_every_single_control_deletion_fails_closed"] = all(e["exact_match"] for e in census if e["record_id"].startswith("DELETE_"))
    checks["no_smuggling_positive_arms_admissible"] = vpos_rec["details"]["NO_SMUGGLING"]["arm_states"] == {k: "ADMISSIBLE" for k in ns_all["arms"]}
    checks["no_float_in_positive_record"] = _no_float(positive)

    shared = {
        "census": S.CENSUS, "risk_points": len(hist_full),
        "risk_histogram_digest": sha256_text(R.canonical_json([[S.rho_id(r), m] for r, m in hist_full.items()])),
        "g_minus_risk_points": [[S.rho_id(r), m] for r, m in arm_data["G_MINUS"]["points"].items()],
        "k_free_multiplicity": {"G_PLUS": arm_data["G_PLUS"]["multiplicity"], "G_MINUS": arm_data["G_MINUS"]["multiplicity"]},
        "k_carriers_in_g_plus": substrate["k_carriers_in_g_plus"],
        "descriptor_mismatches": {k: v["mismatched_coordinates"] for k, v in d_x1_gates.items()},
        "k_target_realizable": {k: arm_data[k]["k_target_realizable"] for k in d_x1_gates},
        "outcome_properties": {arm: {w: list(arm_data[arm]["outcomes"][w]["properties"]) for w in WID}
                               for arm in ("G_PLUS", "G_MINUS", "E_MINUS", "H1A_CAPACITY_DELETE_STATEFUL", "H1B_MACRO_PREV")},
        "outcome_best": {arm: {w: str(arm_data[arm]["outcomes"][w]["best"]) for w in WID} for arm in ("G_PLUS", "G_MINUS", "E_MINUS")},
        "pareto_set": front,
        "scalarization_winners": {s["scalarization_id"]: s["winners"] for s in scal_list},
        "h3a_properties": {w: runs["H3A_FIRST_ACCEPT_PRICE_SORTED"][w]["properties"] for w in WID},
        "trace_digests": {k: {w: runs[k][w]["trace"] for w in WID} for k in ("S2_RISK_FRONTIER_BRANCH_BOUND", "S3_BEST_FIRST_CERTIFICATE", "H3B_REENCODED_BRANCH_BOUND")},
        "acceptance_digests": {k: {w: runs[k][w]["accept"] for w in WID} for k in SP.DIFFERENCE_TABLES},
        "s1_trace_digest": s1_trace_digest,
        "perturbation": {k: perturbation[k] for k in ("perturbed_worlds", "excluded_invalid", "winner_state_partition_stable_all_three_encodings",
                                                       "exact_boundary_ties_all_three_encodings", "mirrored_price_flips_all_three_encodings")},
        "admission_census": {e["record_id"]: [e["terminal"], e["failing_controls"]] for e in census},
    }
    verdict = "GREEN" if all(checks.values()) else "RED"
    receipt = {
        "schema": "GMI833ExecutionControlsResultV1",
        "issue": 859, "parent_issue": 833,
        "freeze_commit": FREEZE_COMMIT, "frozen_from_main": FROZEN_FROM_MAIN,
        "claim_ceiling": CLAIM_CEILING, "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "verdict": verdict, "failed_checks": sorted(k for k, v in checks.items() if not v), "checks": checks,
        "registered_substrate": {"package": "gmi-833-heldout-20-transitions-v1", "issue": 901, **substrate},
        "d_x1_matched_twin": d_x1, "d_x1e_ecology_twin": d_x1e, "d_x2_encoding": d_x2,
        "d_x3_search": d_x3, "d_x4_scalarization": d_x4, "metric_perturbation_control": perturbation,
        "no_smuggling_arms": {k: {"terminal": v["terminal"], "non_clean": {s: x for s, x in v["subaudits"].items() if x["terminal"] != S.ns_audit.CLEAN}}
                              for k, v in sorted(ns_arms.items())},
        "admission": {"schema": R.SCHEMA_ID, "validator_self_test": self_test,
                      "positive_record_file": RECORD_FILE, "positive_record_sha256": sha256_text(R.canonical_json(positive)),
                      "positive_verdict": {k: vpos_rec[k] for k in ("terminal", "failing_controls", "control_terminals", "conditions")},
                      "census": census},
        "shared_facts": shared,
        "reconciliation": {"emitted": False,
                           "reason": "the four #833 Section-D rows named by #859 and the four rows registered in FREEZE_V1.md "
                                     "(Sections B, B, F, G) are already checked on #833 by other packages at their own scope; "
                                     "this package delivers the admission gate and does not re-close any row"},
        "deviations_from_freeze": DEVIATIONS,
    }
    return receipt, positive


DEVIATIONS = [
    "RECONCILIATION_NOT_EMITTED: the freeze commits to a PR check-only / main-push apply-only reconciliation of four rows; all four are already [x] on #833 (and the four #859 Section-D rows were checked via #863), so no reconciliation spec is emitted",
    "K_FINGERPRINT_READING: 'next-state table is not state/input-constant' is read as 'not constant as a function of (S,M,X)'; under the finer reading (depends on (M,X)) the registered G_MINUS construction would fail its own descriptor check on the K-free behaviour set, so the literal reading is the only one consistent with the frozen construction",
    "K_TARGET_AS_RATE: the K-dependent target 'ed < 8' is evaluated as error_delay/scored_events < 1/2, which equals 'ed < 8' at the registered 16 scored events and stays meaningful for the H1c half-sequence twin",
    "SUPPLEMENTARY_HOSTILE_H1D: a halved-budget in-place ablation twin is added to the frozen H1a/H1b/H1c (the issue's 'halve depth/candidate budget' wording); it is an addition, not a change",
    "NO_SMUGGLING_CLEAN_OR_EVALUABLE: D-X1 item 5 is read as 'the #855 audit ran on both twins and returned no CANNOT_AUDIT_* terminal'; admission condition 5 is read as 'every compared arm is clean or carries only sensitivity findings routed to a registered control' (cost scalarization reversal -> SCALARIZATION, search order -> SEARCH)",
    "CLUSTERING_OBJECT: the '146-point clustering' is the rho-quotient of the census (146 classes with multiplicities); it is metric-free by construction, so its stability is a certified structural check, and the metric-sensitive object is the winner-state partition; the argmin-cell partition is reported as a disclosed diagnostic",
    "SCALARIZATION_SET_AS_REGISTERED: the freeze registers the endpoints of cases 1-15 as the 30 positive scalarizations; the case-16 endpoints are also strictly positive but are not added",
    "S1_S2_TRACES_RECONSTRUCTED: S1/S2 conclusions come from #901's own code; their canonical traces are reconstructed from their declared exploration orders and validated against #901's returned counters at every registered world (not by instrumenting #901)",
]


def _no_float(x: Any) -> bool:
    if isinstance(x, float):
        return False
    if isinstance(x, dict):
        return all(_no_float(v) for v in x.values())
    if isinstance(x, (list, tuple)):
        return all(_no_float(v) for v in x)
    return True


def outputs() -> Dict[str, str]:
    receipt, positive = build()
    return {RESULT_FILE: R.canonical_json(receipt), RECORD_FILE: R.canonical_json(positive),
            SCHEMA_FILE: R.canonical_json(R.SCHEMA)}


def main(argv: Sequence[str]) -> int:
    outs = outputs()
    if "--check" in argv:
        drift = [name for name, text in sorted(outs.items()) if (HERE / name).read_text(encoding="utf-8") != text]
        if drift:
            print("DRIFT: " + ", ".join(drift))
            return 1
        print("receipts byte-identical: " + ", ".join(sorted(outs)))
        return 0
    for name, text in sorted(outs.items()):
        (HERE / name).write_text(text, encoding="utf-8")
    import json
    r = json.loads(outs[RESULT_FILE])
    print("%s verdict=%s failed=%s sha256=%s" % (RESULT_FILE, r["verdict"], r["failed_checks"], sha256_text(outs[RESULT_FILE])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
