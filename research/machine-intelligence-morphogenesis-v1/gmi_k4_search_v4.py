from __future__ import annotations

"""K4 V4 successor removing DG-10's supplied resource-axis answer.

Search draws factorized low-level programs from `gmi_k4_resource_native_v4`: retained-state law,
per-query work law, capability atoms and the remaining morphology axes are independently sampled.
The frozen property vector is absent from generation/ranking.  Only after the search stream has
finished is the target vector read for scoring and to construct a non-ranked expressibility witness.

Coverage follows the already-frozen K4 rule: >=1e6 scored candidates is a registered stochastic
search cap.  Failure to recover an expressible target witness at that cap is INCONCLUSIVE_SEARCH,
not a theory failure.  A cheaper admissible non-target candidate than the explicit target witness
is a concrete counterexample and therefore THEORY_RED.
"""

import hashlib
import json

import gmi_k4_search as base
import gmi_k4_search_v2 as phase
import gmi_k4_resource_native_v4 as rn

THRESHOLD = 0.98
REGISTERED_STOCHASTIC_BUDGET = 1_000_000


def _scalar(cost): return sum(float(cost[k]) for k in base.CHANNELS)


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


def _search_projection(win, twin, profile, controls, budget):
    body = {
        "winner": None if win is None else [win[3].cid, win[0], win[1], win[3].vector()],
        "twin": None if twin is None else [twin[3].cid, twin[0], twin[1], twin[3].vector()],
        "profile": profile, "controls": controls, "budget": budget,
    }
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def run_cell(family: str, grammar: str, cell: str, *, freeze: dict, seed: int, budget: int = REGISTERED_STOCHASTIC_BUDGET):
    fr = dict(freeze); fr.pop("name_key", None)
    if family not in fr.get("families", {}):
        return {"schema":"GMIK4MeasuredResourceCellV4","verdict":"INCONCLUSIVE_GRAMMAR","reason":"unknown family id",
                "family":family,"grammar":grammar,"cell":cell,"seed":seed,"world_profile":None,"winner_candidate_id":None}
    if grammar not in rn.PREFIX or grammar not in fr.get("grammars", {}):
        return {"schema":"GMIK4MeasuredResourceCellV4","verdict":"INCONCLUSIVE_GRAMMAR","reason":"unimplemented grammar",
                "family":family,"grammar":grammar,"cell":cell,"seed":seed,"world_profile":None,"winner_candidate_id":None}
    if cell not in ("w1","w2","w4","w8"): raise ValueError(cell)

    # The target vector is intentionally not bound here.  Search sees only the obligation.
    spec = fr["families"][family]
    task = base.OBLIGATION_KIND.get(spec["obligation_class"])
    if task is None:
        return {"schema":"GMIK4MeasuredResourceCellV4","verdict":"INCONCLUSIVE_GRAMMAR","reason":"no obligation evaluator",
                "family":family,"grammar":grammar,"cell":cell,"seed":seed,"world_profile":None,"winner_candidate_id":None}
    scale = int(cell[1:]); profile = phase.world_profile(seed, task, scale)

    best = None; best_twin = None
    control_names = ("CTL_IDENTITY","CTL_CONSTANT","CTL_LOOKUP","CTL_AFFINE")
    cbest = {k:(-1.0,None) for k in control_names}
    n = max(0, int(budget))
    for i in range(n):
        cand = rn.sampled_candidate(grammar, seed, i)
        for ctl in control_names:
            sctl = _control_score(cand, ctl)
            if sctl > cbest[ctl][0]: cbest[ctl] = (sctl, cand.cid)

        s = _semantic(cand, task, scale, False, profile)
        if s >= THRESHOLD:
            cost = rn.lifecycle(cand, scale, profile); total = _scalar(cost)
            row = (s, total, cost, cand)
            if best is None or (total, len(cand.tokens()), cand.cid) < (best[1], len(best[3].tokens()), best[3].cid): best = row
        st = _semantic(cand, task, scale, True, profile)
        if st >= THRESHOLD:
            costt = rn.lifecycle(cand, scale, profile); totalt = _scalar(costt)
            rowt = (st, totalt, costt, cand)
            if best_twin is None or (totalt, len(cand.tokens()), cand.cid) < (best_twin[1], len(best_twin[3].tokens()), best_twin[3].cid): best_twin = rowt

    controls = {k:{"score":v[0],"candidate":v[1],"recovered":v[0]>=THRESHOLD} for k,v in cbest.items()}
    search_digest = _search_projection(best, best_twin, profile, controls, n)
    coverage = {"exhaustive":False,"scored_candidates":n,"registered_stochastic_budget":REGISTERED_STOCHASTIC_BUDGET,
                "budget_requirement_met":n>=REGISTERED_STOCHASTIC_BUDGET,
                "generator":"factorized_hash_sampler_v4","target_vector_used_in_search":False}

    common = {"schema":"GMIK4MeasuredResourceCellV4","family":family,"grammar":grammar,"cell":cell,"seed":seed,
              "obligation_class":spec["obligation_class"],"world_profile":profile,"controls":controls,"coverage":coverage,
              "search_digest":search_digest,"winner_candidate_id":None if best is None else best[3].cid,
              "winner_program_tokens":None if best is None else list(best[3].tokens()),
              "measured_property_vector":None if best is None else best[3].vector(),
              "scalar_lifecycle_cost":None if best is None else best[1],
              "lifecycle_cost":None if best is None else best[2],
              "negative_twin_candidate_id":None if best_twin is None else best_twin[3].cid,
              "negative_twin_measured_vector":None if best_twin is None else best_twin[3].vector(),
              "resource_measurement":None if best is None else {
                  "state_trace_label":rn.measure_state_law(best[3].state_expr),
                  "serve_trace_label":rn.measure_serve_law(best[3].serve_expr),
                  "state_and_serve_selected_independently":True,
                  "candidate_contains_prepaired_resource_label":False,
              },
              "independence":{"DG-10":"CLOSED_BY_MEASURED_FACTORISED_RESOURCE_AXES_AT_V4_SCOPE",
                              "IG-4":"PENDING_INDEPENDENT_BUCKETING","IG-5":"PENDING_INDEPENDENT_PRIMITIVES"},
              "search_inputs_used":["obligation_class","grammar_native_factor_sampler","cell_scale","protected_seed","lifecycle_constitution"],
              "search_inputs_not_used":["name_key","frozen_property_vector_for_generation_or_ranking"]}

    if not all(x["recovered"] for x in controls.values()):
        return {**common,"verdict":"INCONCLUSIVE_GRAMMAR","reason":"known-control recovery failed at registered search budget"}

    # From this point onward we may read the frozen target because ranking is already frozen in `best`.
    target = dict(spec["property_vector"])
    witness = rn.witness_from_target(grammar, target, task)
    witness_score = _semantic(witness, task, scale, False, profile)
    witness_cost = rn.lifecycle(witness, scale, profile); witness_total = _scalar(witness_cost)
    witness_ok = witness.vector() == target and witness_score >= THRESHOLD
    common["expressibility_witness"] = {"candidate_id":witness.cid,"measured_property_vector":witness.vector(),
                                         "semantic_score":witness_score,"scalar_lifecycle_cost":witness_total,
                                         "expressible":witness_ok,"used_in_search_ranking":False}

    if not witness_ok:
        return {**common,"verdict":"INCONCLUSIVE_GRAMMAR","reason":"frozen target vector lacks an admissible measured-resource witness"}
    if best is None:
        return {**common,"verdict":"INCONCLUSIVE_SEARCH","reason":"target is expressible but stochastic search found no admissible positive candidate"}
    measured = best[3].vector(); common["target_vector_match"] = measured == target
    if measured != target:
        if best[1] + 1e-12 < witness_total:
            return {**common,"verdict":"THEORY_RED","reason":"concrete admissible non-target frontier is cheaper than frozen target witness"}
        return {**common,"verdict":"INCONCLUSIVE_SEARCH","reason":"target witness is no dearer than recovered non-target; search did not recover the target frontier"}
    if best_twin is None:
        return {**common,"verdict":"INCONCLUSIVE_SEARCH","reason":"positive target recovered but negative-twin frontier was not recovered"}
    common["negative_twin_flipped"] = best_twin[3].vector() != target
    if not common["negative_twin_flipped"]:
        return {**common,"verdict":"THEORY_RED","reason":"negative twin preserves the frozen target vector"}
    if n < REGISTERED_STOCHASTIC_BUDGET:
        return {**common,"verdict":"INCONCLUSIVE_SEARCH","reason":"target recovered in development budget below frozen stochastic coverage cap"}
    return {**common,"verdict":"K4_RECOVERY_GREEN","reason":"measured-resource target vector recovered and negative twin flips at frozen stochastic budget"}
