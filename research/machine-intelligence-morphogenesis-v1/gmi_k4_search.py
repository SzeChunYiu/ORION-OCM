from __future__ import annotations

"""Executable K4 name-blind mechanism search.

This is the missing engine referenced by GMI_EMPIRICAL_CLOSURE_PROGRAMME_STATUS_V1.md.
It is deliberately narrower than a claim of historical-architecture rediscovery:

* search is exhaustive over a finite neutral mechanism palette, so coverage is auditable;
* no historical architecture name is a candidate primitive;
* `name_key` is deleted defensively;
* the frozen property vector is removed from the search/ranking specification and is read only
  after the positive winner is frozen;
* every positive world is paired with its frozen negative twin;
* the same-author primitive-selection limitation (IG-5) remains explicit in every result.

A RED is a RED at this registered engine scope. Do not tune the palette or cost law on the
protected result; freeze a successor and retire the split instead.
"""

from dataclasses import dataclass
import math

AXES = (
    "state_scales_with", "serve_scales_with", "update_locality", "routing", "sharing",
    "retrieval", "serve_iterations", "stochastic_serve", "verifier_gated", "external_authority",
)
CHANNELS = (
    "development_compute", "search_compute", "description_compiler_burden", "state_storage",
    "serve_compute_latency", "update_retraining", "communication", "verification",
    "human_external_intervention",
)


@dataclass(frozen=True)
class Form:
    fid: str
    state_scales_with: str
    serve_scales_with: str
    update_locality: str
    routing: str
    sharing: str
    retrieval: str
    serve_iterations: str
    stochastic_serve: bool
    verifier_gated: bool
    external_authority: bool
    caps: tuple[str, ...]
    complexity: float = 1.0

    def vector(self):
        return {k: getattr(self, k) for k in AXES}


# Neutral state/routing/update motifs. These identifiers are local codes, not historical-family names.
FORMS = [
    Form("F01", "n_features", "n_features", "global", "none", "shared", "none", "one", False, False, False, ("affine", "direct_numeric"), 1.0),
    Form("F02", "n_retained_sections", "n_retained_sections", "global", "none", "shared", "metric", "one", False, False, False, ("similarity", "fixed_basis"), 1.15),
    Form("F03", "n_records", "log_n_records", "local", "none", "unshared", "exact_key", "one", False, False, False, ("exact_lookup", "volatile_records"), 1.05),
    Form("F04", "n_hypotheses", "n_hypotheses", "global", "none", "shared", "none", "one", False, False, False, ("uncertainty", "belief_update"), 1.15),
    Form("F05", "n_constraints", "search_tree", "global", "none", "shared", "none", "many", False, True, False, ("constraints", "exact_search"), 1.45),
    Form("F06", "program_size", "search_tree", "none", "none", "shared", "none", "many", False, True, False, ("program_search", "exact_search"), 1.35),
    Form("F07", "hidden_width", "hidden_width_times_length", "global", "none", "shared", "none", "many", False, False, False, ("sequence_state", "nonlinear_state"), 1.2),
    Form("F08", "state_dim", "state_dim_times_length", "global", "none", "shared", "none", "many", False, False, False, ("linear_dynamics", "sequence_state"), 1.0),
    Form("F09", "kernel_size", "kernel_size_times_positions", "global", "none", "shared", "none", "one", False, False, False, ("local_tied", "equivariant"), 0.9),
    Form("F10", "edge_features", "n_edges_times_rounds", "global", "none", "shared", "none", "many", False, False, False, ("graph_local", "message_rounds"), 1.15),
    Form("F11", "n_positions_squared", "n_positions_squared", "global", "input_dependent", "shared", "metric", "one", False, False, False, ("content_route", "dense_pair"), 1.3),
    Form("F12", "n_positions_times_window", "n_positions_times_window", "global", "input_dependent", "shared", "metric", "one", False, False, False, ("content_route", "sparse_pair"), 0.95),
    Form("F13", "n_experts_times_expert_size", "active_expert_size", "local", "input_dependent", "unshared", "none", "one", False, False, False, ("mode_partition", "specialist"), 1.2),
    Form("F14", "corpus_size", "retrieval_plus_core", "none", "input_dependent", "shared", "exact_key", "one", False, False, True, ("exact_lookup", "authority"), 1.25),
    Form("F15", "rank_times_dim", "core_plus_rank", "local", "none", "shared", "none", "one", False, False, False, ("low_rank_revision", "direct_numeric"), 0.85),
    Form("F16", "n_members_times_member_size", "n_members_times_member_size", "global", "none", "unshared", "none", "one", True, False, False, ("aggregate", "variance_reduce"), 1.35),
    Form("F17", "proposer_plus_verifier", "n_proposals_times_check", "none", "none", "shared", "none", "many", True, True, False, ("proposal", "checker"), 1.35),
    Form("F18", "dynamics_model_size", "rollout_depth_times_branch", "global", "none", "shared", "none", "many", False, False, False, ("world_model", "planning"), 1.35),
    Form("F19", "policy_size", "policy_size", "global", "none", "shared", "none", "one", True, False, False, ("direct_policy",), 0.9),
    Form("F20", "vocab_times_context", "sequence_length", "global", "none", "shared", "none", "many", True, False, False, ("ordered_factorization", "sequence_model"), 1.1),
    Form("F21", "score_model_size", "n_steps_times_model", "global", "none", "shared", "none", "many", True, False, False, ("iterative_denoise", "joint_model"), 1.4),
    Form("F22", "latent_dim_plus_decoder", "decoder_size", "global", "none", "shared", "none", "one", True, False, False, ("latent_compress", "joint_model"), 1.0),
]

GRAMMAR_FACTOR = {
    "G1_TENSOR_GRAPH": {
        "default": 1.0, "exact_lookup": 1.22, "program_search": 1.30, "constraints": 1.25,
        "graph_local": 1.08, "message_rounds": 1.08,
    },
    "G2_SYMBOLIC_PROGRAM": {
        "default": 1.08, "exact_lookup": 0.95, "program_search": 0.90, "constraints": 0.92,
        "checker": 0.95, "affine": 1.18, "content_route": 1.15,
        "iterative_denoise": 1.25, "latent_compress": 1.20,
    },
    "G3_FSM_MESSAGE": {
        "default": 1.12, "sequence_state": 0.90, "linear_dynamics": 0.95,
        "graph_local": 0.88, "message_rounds": 0.88, "local_tied": 0.95,
        "exact_lookup": 1.02, "content_route": 1.08, "latent_compress": 1.28,
        "iterative_denoise": 1.30,
    },
}

OBLIGATION_KIND = {
    "OBL_LINEAR_RESPONSE": "linear",
    "OBL_FIXED_BASIS_RESPONSE": "basis",
    "OBL_ARBITRARY_RECALL": "recall",
    "OBL_UNCERTAIN_DECISION": "belief",
    "OBL_CONSTRAINT_SATISFACTION": "constraint",
    "OBL_EXACT_PROGRAM_ANSWER": "program",
    "OBL_SEQUENTIAL_DEPENDENCE": "sequence",
    "OBL_LINEAR_DYNAMICAL_RESPONSE": "lti",
    "OBL_TRANSLATION_EQUIVARIANT_RESPONSE": "equivariant",
    "OBL_RELATIONAL_PROPAGATION": "graph",
    "OBL_CONTENT_ADDRESSED_MIXING": "content",
    "OBL_SPARSE_CONTENT_MIXING": "sparse_content",
    "OBL_HETEROGENEOUS_MODES": "modes",
    "OBL_EXTERNAL_AUTHORITY_RECALL": "authority",
    "OBL_SMALL_TARGETED_REVISION": "lowrank",
    "OBL_VARIANCE_REDUCTION": "ensemble",
    "OBL_CERTIFIED_ANSWER_UNDER_UNRELIABLE_PROPOSAL": "verify",
    "OBL_GOAL_REUSE_UNDER_KNOWN_DYNAMICS": "model_based",
    "OBL_SINGLE_GOAL_CONTROL": "policy",
    "OBL_SEQUENTIAL_GENERATION": "ordered_gen",
    "OBL_JOINT_SAMPLE_GENERATION": "joint_gen",
    "OBL_COMPRESSED_GENERATION": "latent_gen",
}


def semantic_score(form: Form, task: str, scale: int, twin: bool = False) -> float:
    """Semantic admissibility model. It uses only neutral operational capabilities.

    Several forms can be semantically adequate for most obligations. The winner is determined only after
    the lifecycle meter is applied; this intentionally permits strong-parent reductions and REDs.
    """
    c = set(form.caps)
    if task == "linear":
        if twin:
            return 1.0 if ("exact_lookup" in c or "program_search" in c) else 0.55 if "affine" in c else 0.45
        return 1.0 if "affine" in c else 1.0 if "program_search" in c else 0.80 if "exact_lookup" in c else 0.72 if "fixed_basis" in c else 0.5
    if task == "basis":
        if twin:
            return 1.0 if "exact_lookup" in c else 0.66 if "fixed_basis" in c else 0.6
        return 1.0 if "fixed_basis" in c else 0.93 if "program_search" in c else 0.78 if "affine" in c else 0.72
    if task == "recall":
        if twin:
            return 1.0 if "affine" in c else 0.82 if "exact_lookup" in c else 0.6
        return 1.0 if "exact_lookup" in c else 0.92 if "program_search" in c else 0.55
    if task == "belief":
        if twin:
            return 1.0 if ("direct_numeric" in c or "direct_policy" in c or "exact_lookup" in c) else 0.8
        return 1.0 if "uncertainty" in c else 0.84 if "aggregate" in c else 0.72
    if task == "constraint":
        if twin:
            return 1.0 if ("affine" in c or "direct_numeric" in c) else 0.94 if "exact_search" in c else 0.7
        return 1.0 if ("constraints" in c and form.verifier_gated) else 0.99 if ("exact_search" in c and form.verifier_gated) else 0.6
    if task == "program":
        if twin:
            return 1.0 if ("affine" in c or "exact_lookup" in c or "direct_policy" in c) else 0.75
        return 1.0 if ("program_search" in c and form.verifier_gated) else 0.99 if ("constraints" in c and form.verifier_gated) else 0.7
    if task == "sequence":
        if twin:
            return 1.0 if ("affine" in c or "exact_lookup" in c) else 0.75 if "sequence_state" in c else 0.6
        return 1.0 if "sequence_state" in c else 0.93 if "ordered_factorization" in c else 0.7
    if task == "lti":
        if twin:
            return 1.0 if "nonlinear_state" in c else 0.82 if "linear_dynamics" in c else 0.7
        return 1.0 if "linear_dynamics" in c else 0.99 if "sequence_state" in c else 0.65
    if task == "equivariant":
        if twin:
            return 1.0 if ("exact_lookup" in c or "mode_partition" in c) else 0.72 if "equivariant" in c else 0.6
        return 1.0 if "equivariant" in c else 0.88 if "content_route" in c else 0.7
    if task == "graph":
        if twin:
            return 1.0 if ("affine" in c or "aggregate" in c) else 0.72 if "graph_local" in c else 0.6
        return 1.0 if "graph_local" in c else 0.94 if "content_route" in c else 0.6
    if task == "content":
        if twin:
            return 1.0 if ("affine" in c or "local_tied" in c) else 0.85 if "content_route" in c else 0.6
        return 1.0 if ("content_route" in c and "dense_pair" in c) else 0.96 if "sparse_pair" in c else 0.65
    if task == "sparse_content":
        if twin:
            return 1.0 if ("content_route" in c and "dense_pair" in c) else 0.90 if "sparse_pair" in c else 0.65
        return 1.0 if "sparse_pair" in c else 1.0 if "dense_pair" in c else 0.62
    if task == "modes":
        if twin:
            return 1.0 if ("affine" in c or "direct_numeric" in c) else 0.88 if "mode_partition" in c else 0.65
        return 1.0 if "mode_partition" in c else 0.82 if "aggregate" in c else 0.65
    if task == "authority":
        if twin:
            return 1.0 if (("exact_lookup" in c and not form.external_authority) or "affine" in c) else 0.8
        return 1.0 if ("authority" in c and "exact_lookup" in c) else 0.0 if "exact_lookup" in c else 0.55
    if task == "lowrank":
        if twin:
            return 1.0 if (("direct_numeric" in c and "low_rank_revision" not in c) or "program_search" in c) else 0.70 if "low_rank_revision" in c else 0.6
        return 1.0 if "low_rank_revision" in c else 1.0 if "direct_numeric" in c else 0.65
    if task == "ensemble":
        if twin:
            return 1.0 if ("affine" in c or "direct_policy" in c) else 0.88 if "aggregate" in c else 0.7
        return 1.0 if "variance_reduce" in c else 0.94 if "affine" in c else 0.7
    if task == "verify":
        if twin:
            return 1.0 if (("program_search" in c or "direct_policy" in c) and not form.verifier_gated) else 0.91 if "checker" in c else 0.65
        return 1.0 if ("proposal" in c and "checker" in c and form.verifier_gated) else 0.97 if ("exact_search" in c and form.verifier_gated) else 0.55
    if task == "model_based":
        if twin:
            return 1.0 if "direct_policy" in c else 0.96 if "world_model" in c else 0.65
        return 1.0 if ("world_model" in c and "planning" in c) else 0.90 if "direct_policy" in c else 0.65
    if task == "policy":
        if twin:
            return 1.0 if ("world_model" in c and "planning" in c) else 0.86 if "direct_policy" in c else 0.65
        return 1.0 if "direct_policy" in c else 1.0 if ("world_model" in c and "planning" in c) else 0.65
    if task == "ordered_gen":
        if twin:
            return 1.0 if ("iterative_denoise" in c or "latent_compress" in c) else 0.86 if "ordered_factorization" in c else 0.65
        return 1.0 if "ordered_factorization" in c else 0.96 if "joint_model" in c else 0.65
    if task == "joint_gen":
        if twin:
            return 1.0 if ("ordered_factorization" in c or "latent_compress" in c) else 0.87 if "iterative_denoise" in c else 0.65
        return 1.0 if "iterative_denoise" in c else 0.97 if "ordered_factorization" in c else 0.94 if "latent_compress" in c else 0.65
    if task == "latent_gen":
        if twin:
            return 1.0 if ("ordered_factorization" in c or "iterative_denoise" in c) else 0.72 if "latent_compress" in c else 0.65
        return 1.0 if "latent_compress" in c else 0.95 if "joint_model" in c else 0.65
    raise KeyError(task)


def _driver_values(scale: int):
    nfeat = 4 * scale
    nrec = 16 * scale
    npos = 8 * scale
    win = max(2, scale)
    state = 4 * scale
    edges = 12 * scale
    return {
        "n_features": nfeat,
        "n_retained_sections": 8 * scale,
        "n_records": nrec,
        "log_n_records": math.log2(max(2, nrec)),
        "n_hypotheses": 4 * scale,
        "n_constraints": 12 * scale,
        "search_tree": 16 * scale * scale,
        "program_size": 8 * scale,
        "hidden_width": state,
        "hidden_width_times_length": state * (8 * scale),
        "state_dim": state,
        "state_dim_times_length": state * (8 * scale),
        "kernel_size": 3 * scale,
        "kernel_size_times_positions": 3 * scale * npos,
        "edge_features": 4 * scale,
        "n_edges_times_rounds": edges * max(2, scale),
        "n_positions_squared": npos * npos,
        "n_positions_times_window": npos * win,
        "n_experts_times_expert_size": (2 * scale) * (4 * scale),
        "active_expert_size": 4 * scale,
        "corpus_size": 32 * scale,
        "retrieval_plus_core": math.log2(32 * scale + 1) + 8 * scale,
        "rank_times_dim": max(1, scale) * (8 * scale),
        "core_plus_rank": 32 * scale + max(1, scale),
        "n_members_times_member_size": max(2, scale) * (8 * scale),
        "proposer_plus_verifier": 16 * scale,
        "n_proposals_times_check": max(2, scale) * 4 * scale,
        "dynamics_model_size": state * state,
        "rollout_depth_times_branch": max(2, scale) * 3 * scale,
        "policy_size": 8 * scale,
        "vocab_times_context": 16 * (8 * scale),
        "sequence_length": 16 * scale,
        "score_model_size": 32 * scale,
        "n_steps_times_model": max(2, scale) * 32 * scale,
        "latent_dim_plus_decoder": 4 * scale + 16 * scale,
        "decoder_size": 16 * scale,
    }


def grammar_factor(grammar: str, form: Form) -> float:
    g = GRAMMAR_FACTOR.get(grammar)
    if g is None:
        return float("inf")
    vals = [g.get(cap) for cap in form.caps if cap in g]
    return min(vals) if vals else g["default"]


def lifecycle(form: Form, grammar: str, scale: int, knob: int):
    d = _driver_values(scale)
    sf, sv = d[form.state_scales_with], d[form.serve_scales_with]
    gf = grammar_factor(grammar, form)
    k = max(1, knob)
    state = sf * (1 + 0.08 * (k - 1)) * form.complexity * gf
    serve = sv * (1 + 0.04 * (k - 1)) * form.complexity * gf
    update_base = {"none": 0.05, "local": 0.30, "global": 1.0}[form.update_locality]
    upd = update_base * state
    comm = 0.25 * serve if form.routing == "input_dependent" else 0.03 * serve
    ver = 0.25 * serve if form.verifier_gated else 0.0
    human = 0.05 * serve if form.external_authority else 0.0
    dev = (state + upd) * (1.0 if form.sharing == "shared" else 1.20)
    desc = 0.5 * state + 4.0 * form.complexity
    search = 1.0 + 0.1 * k + 0.25 * form.complexity
    return {
        "development_compute": float(dev),
        "search_compute": float(search),
        "description_compiler_burden": float(desc),
        "state_storage": float(state),
        "serve_compute_latency": float(serve),
        "update_retraining": float(upd),
        "communication": float(comm),
        "verification": float(ver),
        "human_external_intervention": float(human),
    }


def scalar_cost(cost, weights):
    return sum(float(weights.get(k, 1.0)) * cost[k] for k in CHANNELS)


def _candidate_space(grammar, scale):
    if grammar not in GRAMMAR_FACTOR:
        return []
    return [(f, knob) for f in FORMS for knob in (1, 2, 4, 8) if math.isfinite(grammar_factor(grammar, f))]


def _controls(grammar, scale):
    controls = {
        "CTL_IDENTITY": lambda f: 1.0 if ("affine" in f.caps or "program_search" in f.caps or "sequence_state" in f.caps) else 0.5,
        "CTL_CONSTANT": lambda f: 1.0 if (f.serve_iterations == "one" or "program_search" in f.caps) else 0.8,
        "CTL_LOOKUP": lambda f: 1.0 if "exact_lookup" in f.caps else 0.65,
        "CTL_AFFINE": lambda f: 1.0 if "affine" in f.caps else 0.85 if "program_search" in f.caps else 0.55,
    }
    space = _candidate_space(grammar, scale)
    res = {}
    for name, fn in controls.items():
        best = max((fn(f), -lifecycle(f, grammar, scale, k)["serve_compute_latency"], f.fid, k) for f, k in space)
        res[name] = {"score": best[0], "recovered": best[0] >= 0.98, "candidate": best[2], "knob": best[3]}
    return res


def run_cell(family: str, grammar: str, cell: str, *, freeze: dict, seed: int, budget: int = 1_000_000):
    # Defense in depth: callers outside the SLURM wrapper also cannot leak the architecture-name key.
    fr = dict(freeze)
    fr.pop("name_key", None)
    if family not in fr.get("families", {}):
        return {"verdict": "INCONCLUSIVE_GRAMMAR", "reason": "unknown family id", "family": family, "grammar": grammar, "cell": cell}
    if grammar not in fr.get("grammars", {}):
        return {"verdict": "INCONCLUSIVE_GRAMMAR", "reason": "unimplemented/unknown grammar", "family": family, "grammar": grammar, "cell": cell}
    if cell not in ("w1", "w2", "w4", "w8"):
        raise ValueError(cell)

    scale = int(cell[1:])
    spec = dict(fr["families"][family])
    target_vec = spec.pop("property_vector")  # removed before ranking; used only after winner freeze
    obl = spec["obligation_class"]
    task = OBLIGATION_KIND.get(obl)
    if task is None:
        return {"verdict": "INCONCLUSIVE_GRAMMAR", "reason": f"no generator for {obl}", "family": family, "grammar": grammar, "cell": cell}

    weights = {k: 1.0 for k in CHANNELS}
    space = _candidate_space(grammar, scale)
    controls = _controls(grammar, scale)
    if not all(v["recovered"] for v in controls.values()):
        return {"verdict": "INCONCLUSIVE_GRAMMAR", "reason": "known control failure", "controls": controls, "family": family, "grammar": grammar, "cell": cell}

    exhaustive = len(space) <= budget
    scored = []
    for f, knob in space[:budget]:
        score = semantic_score(f, task, scale, False)
        cost = lifecycle(f, grammar, scale, knob)
        scored.append((score, scalar_cost(cost, weights), f, knob, cost))
    admissible = [x for x in scored if x[0] >= 0.98]
    coverage = {"exhaustive": exhaustive, "scored_candidates": len(scored), "palette_size": len(space), "budget": budget}
    if not admissible:
        return {
            "verdict": "INCONCLUSIVE_GRAMMAR", "reason": "no admissible candidate in declared palette", "controls": controls,
            "coverage": coverage, "family": family, "grammar": grammar, "cell": cell,
        }

    win = min(admissible, key=lambda x: (x[1], x[2].complexity, x[2].fid, x[3]))
    score, total, form, knob, cost = win
    measured = form.vector()

    twin_admissible = []
    for f, k in space[:budget]:
        s = semantic_score(f, task, scale, True)
        c = lifecycle(f, grammar, scale, k)
        if s >= 0.98:
            twin_admissible.append((s, scalar_cost(c, weights), f, k, c))
    twin = None if not twin_admissible else min(twin_admissible, key=lambda x: (x[1], x[2].complexity, x[2].fid, x[3]))
    twin_vec = None if twin is None else twin[2].vector()

    if measured != target_vec:
        verdict, reason = "THEORY_RED", "frontier winner measured vector contradicts frozen prediction"
    elif twin is None:
        verdict, reason = "THEORY_RED", "negative twin has no admissible realization inside a grammar that passed controls"
    elif twin_vec == target_vec:
        verdict, reason = "THEORY_RED", "negative twin failed to change winning measured property vector"
    else:
        verdict, reason = "K4_RECOVERY_GREEN", "positive frontier vector matches freeze and negative twin flips frontier vector"

    return {
        "schema": "GMIK4CellResultV1",
        "family": family, "grammar": grammar, "cell": cell, "seed": seed, "obligation_class": obl,
        "verdict": verdict, "reason": reason, "semantic_score": score,
        "winner_neutral_form": form.fid, "winner_knob": knob,
        "measured_property_vector": measured, "target_vector_match": measured == target_vec,
        "lifecycle_cost": cost, "scalar_lifecycle_cost": total,
        "negative_twin_winner": None if twin is None else twin[2].fid,
        "negative_twin_measured_vector": twin_vec,
        "negative_twin_flipped": twin_vec is not None and twin_vec != target_vec,
        "controls": controls, "coverage": coverage,
        "independence": {"IG-4": "PENDING_INDEPENDENT_BUCKETING", "IG-5": "PENDING_INDEPENDENT_PRIMITIVES"},
        "search_inputs_used": ["obligation_class", "cell_scale", "grammar", "seed", "candidate_palette", "lifecycle_meter"],
        "search_inputs_explicitly_not_used": ["name_key", "frozen_property_vector_for_ranking"],
    }
