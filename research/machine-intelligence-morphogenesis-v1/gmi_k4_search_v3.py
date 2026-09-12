from __future__ import annotations

"""Grammar-native K4 search successor.

Unlike V1/V2, G1/G2/G3 now enumerate separate program serializations with disjoint primitive token
inventories (`gmi_k4_grammar_native.py`). The search is still same-authored and therefore cannot close
IG-5 external primitive-selection independence, but the implementation-level disjoint-grammar clause is
now mechanically satisfied.

V3 is retained as DEVELOPMENT evidence after PR #445 identified DG-10: two resource axes were supplied
by the StateShape token.  This file is not promoted by the receipt-completeness fix below; V4 is the
DG-10 successor.  The fix only guarantees that hostile tests can inspect early inconclusive paths.
"""

import hashlib
import json

import gmi_k4_search as base
import gmi_k4_search_v2 as phase
import gmi_k4_grammar_native as gn

THRESHOLD = 0.98


def _lifecycle(cand, grammar, scale, profile):
    form = cand.as_form()
    cost = base.lifecycle(form, grammar, scale, cand.width_knob)
    cost = phase._lifecycle_adjust(cost, form, "__placeholder__", profile)
    cost["description_compiler_burden"] += cand.token_cost
    cost["search_compute"] += cand.token_cost
    return cost


def _semantic(cand, task, scale, twin, profile):
    f = cand.as_form()
    return phase._semantic_adjust(base.semantic_score(f, task, scale, twin), f, task, twin, profile)


def _control_score(cand, name):
    c = set(cand.caps())
    if name == "CTL_IDENTITY": return 1.0 if ("affine" in c or "program_search" in c or "sequence_state" in c) else 0.5
    if name == "CTL_CONSTANT": return 1.0 if cand.serve_iterations == "one" else 0.82
    if name == "CTL_LOOKUP": return 1.0 if cand.retrieval == "exact_key" else 0.65
    if name == "CTL_AFFINE": return 1.0 if "affine" in c else 0.86 if "program_search" in c else 0.55
    raise KeyError(name)


def _scalar(cost): return sum(cost[k] for k in base.CHANNELS)


def _controls(space):
    out = {}
    for name in ("CTL_IDENTITY", "CTL_CONSTANT", "CTL_LOOKUP", "CTL_AFFINE"):
        best = max((_control_score(c, name), -c.token_cost, c.cid, c) for c in space)
        out[name] = {"score": best[0], "recovered": best[0] >= THRESHOLD, "candidate": best[2]}
    return out


def _winner(space, grammar, task, scale, profile, twin, budget):
    exhausted = len(space) <= budget
    scored = []
    for cand in space[:budget]:
        s = _semantic(cand, task, scale, twin, profile)
        if s < THRESHOLD: continue
        c = _lifecycle(cand, grammar, scale, profile)
        scored.append((s, _scalar(c), cand.token_cost, cand.cid, cand, c))
    if not scored: return None, exhausted
    return min(scored, key=lambda x: (x[1], x[2], x[3])), exhausted


def _digest(win, twin, profile, controls, family, grammar, cell):
    body = {
        "winner": None if win is None else [win[4].cid, win[1], win[4].vector()],
        "twin": None if twin is None else [twin[4].cid, twin[1], twin[4].vector()],
        "profile": profile, "controls": controls,
        "family": family, "grammar": grammar, "cell": cell,
    }
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def run_cell(family: str, grammar: str, cell: str, *, freeze: dict, seed: int, budget: int = 1_000_000):
    fr = dict(freeze); fr.pop("name_key", None)
    if family not in fr.get("families", {}):
        return {"verdict":"INCONCLUSIVE_GRAMMAR","reason":"unknown family id","family":family,"grammar":grammar,"cell":cell,
                "seed":seed,"world_profile":None,"winner_candidate_id":None,"search_digest":None}
    if grammar not in gn.PREFIX or grammar not in fr.get("grammars", {}):
        return {"verdict":"INCONCLUSIVE_GRAMMAR","reason":"unimplemented grammar","family":family,"grammar":grammar,"cell":cell,
                "seed":seed,"world_profile":None,"winner_candidate_id":None,"search_digest":None}
    if cell not in ("w1", "w2", "w4", "w8"): raise ValueError(cell)

    spec = dict(fr["families"][family]); target = spec.pop("property_vector")
    task = base.OBLIGATION_KIND.get(spec["obligation_class"])
    if task is None:
        return {"verdict":"INCONCLUSIVE_GRAMMAR","reason":f"no obligation evaluator for {spec['obligation_class']}",
                "family":family,"grammar":grammar,"cell":cell,"seed":seed,"world_profile":None,"winner_candidate_id":None,"search_digest":None}
    scale = int(cell[1:]); profile = phase.world_profile(seed, task, scale)
    space = list(gn.iter_candidates(grammar)); controls = _controls(space)
    if not all(x["recovered"] for x in controls.values()):
        dig = _digest(None, None, profile, controls, family, grammar, cell)
        return {"verdict":"INCONCLUSIVE_GRAMMAR","reason":"known-control recovery failed","controls":controls,
                "family":family,"grammar":grammar,"cell":cell,"seed":seed,"world_profile":profile,
                "winner_candidate_id":None,"search_digest":dig,
                "grammar_inventory_size":gn.DISJOINT_INVENTORY_SIZES.get(grammar),"candidate_space_size":len(space)}

    win, exhausted = _winner(space, grammar, task, scale, profile, False, budget)
    twin, twin_exhausted = _winner(space, grammar, task, scale, profile, True, budget)
    coverage = {"exhaustive":exhausted and twin_exhausted,"candidate_space_size":len(space),
                "positive_candidates_examined":min(len(space), budget),"negative_twin_candidates_examined":min(len(space), budget),
                "budget":budget}
    dig = _digest(win, twin, profile, controls, family, grammar, cell)
    if win is None:
        return {"schema":"GMIK4GrammarNativeCellV3","verdict":"INCONCLUSIVE_GRAMMAR","reason":"no admissible positive candidate",
                "controls":controls,"coverage":coverage,"family":family,"grammar":grammar,"cell":cell,"seed":seed,
                "world_profile":profile,"winner_candidate_id":None,"winner_program_tokens":None,
                "measured_property_vector":None,"scalar_lifecycle_cost":None,"target_vector_match":False,
                "negative_twin_candidate_id":None if twin is None else twin[4].cid,
                "negative_twin_measured_vector":None if twin is None else twin[4].vector(),
                "search_digest":dig,"grammar_inventory_size":gn.DISJOINT_INVENTORY_SIZES.get(grammar)}

    score, total, _, _, cand, cost = win
    measured = cand.vector(); twin_cand = None if twin is None else twin[4]; twin_vec = None if twin_cand is None else twin_cand.vector()
    if not coverage["exhaustive"]:
        verdict, reason = "INCONCLUSIVE_SEARCH", "declared grammar-native candidate space not exhausted within budget"
    elif measured != target:
        verdict, reason = "THEORY_RED", "grammar-native frontier property vector contradicts frozen prediction"
    elif twin_cand is None:
        verdict, reason = "THEORY_RED", "negative twin has no admissible candidate despite recovered controls"
    elif twin_vec == target:
        verdict, reason = "THEORY_RED", "negative twin does not flip grammar-native frontier vector"
    else:
        verdict, reason = "K4_RECOVERY_GREEN", "grammar-native positive frontier matches freeze and negative twin flips"

    return {
        "schema":"GMIK4GrammarNativeCellV3","family":family,"grammar":grammar,"cell":cell,"seed":seed,
        "obligation_class":spec["obligation_class"],"verdict":verdict,"reason":reason,
        "semantic_score":score,"winner_candidate_id":cand.cid,"winner_program_tokens":list(cand.tokens),
        "winner_width_knob":cand.width_knob,"measured_property_vector":measured,"target_vector_match":measured == target,
        "lifecycle_cost":cost,"scalar_lifecycle_cost":total,
        "negative_twin_candidate_id":None if twin_cand is None else twin_cand.cid,
        "negative_twin_program_tokens":None if twin_cand is None else list(twin_cand.tokens),
        "negative_twin_measured_vector":twin_vec,"negative_twin_flipped":twin_vec is not None and twin_vec != target,
        "world_profile":profile,"controls":controls,"coverage":coverage,"search_digest":dig,
        "grammar_inventory_size":gn.DISJOINT_INVENTORY_SIZES.get(grammar),
        "all_grammar_inventory_sizes":dict(gn.DISJOINT_INVENTORY_SIZES),"grammar_token_prefix":gn.PREFIX[grammar],
        "independence":{"implementation_disjointness":"MECHANICALLY_CHECKED","IG-4":"PENDING_INDEPENDENT_BUCKETING","IG-5":"PENDING_INDEPENDENT_PRIMITIVES","DG-10":"OPEN_IN_V3__SEE_V4"},
        "search_inputs_used":["obligation_class","grammar_native_candidate_space","cell_scale","protected_seed","lifecycle_constitution"],
        "search_inputs_not_used":["name_key","frozen_property_vector_for_ranking"],
    }
