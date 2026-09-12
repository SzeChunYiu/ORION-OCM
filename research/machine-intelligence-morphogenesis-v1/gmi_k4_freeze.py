#!/usr/bin/env python3
"""Freeze artifact for the K4 leave-one-family-out neutral rediscovery benchmark (brief part A).

WHAT IS FROZEN AND WHY IT IS FROZEN BEFORE ANY SEARCH RUNS. The brief requires that "before search, GMI must freeze the
expected implementation-invariant property vector and quantitative phase prediction". This module emits that freeze and
nothing else. It performs no search, reads no protected outcome and imports no search code, so committing its output
timestamps the prediction ahead of every result (sub-gate IG-3, closed by third-party-witnessed commit order --
see GMI_INDEPENDENCE_GATE_DECOMPOSITION_V1.md).

THE NAME BARRIER. The search process is handed an OBLIGATION and a GRAMMAR. It is never handed a family name, a
property vector, a reference implementation or a historical architecture. The mapping from opaque family id to
architecture name lives in `name_key`, which the runner is forbidden to read and which exists only so a human can
adjudicate afterwards. A name, template or protected-outcome leak invalidates the zero-prior evidence, per the
register's universal failure rules.

IMPLEMENTATION-INVARIANT PROPERTY VECTOR. Ten axes, each measurable from a machine's structure and behaviour WITHOUT
knowing what it is called. They are deliberately about where state lives, what serving costs and what the update
touches -- not about layer types:

    state_scales_with        what the retained state grows with
    serve_scales_with        what one query costs
    update_locality          how much of the state one feedback event moves
    routing                  whether the computation path depends on the input
    sharing                  whether one parameter set serves all inputs
    retrieval                how a stored item is addressed, if at all
    serve_iterations         whether serving is one pass or many
    stochastic_serve         whether serving consumes random bits
    verifier_gated           whether an answer is checked before it is emitted
    external_authority       whether an answer depends on state outside the machine

A family is NOT defined here by its name; it is defined by this vector plus the obligation it is the cheapest answer
to. If two registered families collide on the vector, that is a REPORTED RESULT, not a bug to be tuned away: it means
the vector does not separate them and the benchmark cannot claim to have rediscovered one rather than the other.

VERDICTS, per the brief:
    K4_RECOVERY_GREEN     a name-blind search over a legal grammar produced an admissible machine whose MEASURED
                          property vector equals the FROZEN predicted vector for the held-out family
    THEORY_RED            an admissible machine was found whose measured vector CONTRADICTS the frozen prediction
    INCONCLUSIVE_GRAMMAR  the held-out semantics is not expressible in this grammar at the declared caps
    INCONCLUSIVE_SEARCH   expressible, but the budget ran out AND the preregistered known-control recovery passed

The asymmetry in the last two is the brief's rule and is load-bearing: "a failure cannot be blamed on search unless
known-control recovery and search-coverage requirements were preregistered and fail". The control set and the coverage
bound are therefore frozen HERE, not chosen after a disappointing run.
"""
import hashlib
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json")

AX = ("state_scales_with", "serve_scales_with", "update_locality", "routing", "sharing",
      "retrieval", "serve_iterations", "stochastic_serve", "verifier_gated", "external_authority")


def P(state, serve, upd, routing, sharing, retrieval, iters, stoch, ver, ext):
    return dict(zip(AX, (state, serve, upd, routing, sharing, retrieval, iters, stoch, ver, ext)))


# family id -> (property vector, obligation class, phase prediction, negative twin, kill condition)
# The obligation is what the search is given. It never mentions the family.
FAM = {
 "K4-A01": (P("n_features", "n_features", "global", "none", "shared", "none", "one", False, False, False),
            "OBL_LINEAR_RESPONSE", "wins when the target is an affine function of the inputs and reuse is high; loses to memory when the input set is small enough to enumerate",
            "replace the shared affine law with independent per-input labels", "a cheaper admissible parent exists at the predicted crossover"),
 "K4-A02": (P("n_retained_sections", "n_retained_sections", "global", "none", "shared", "metric", "one", False, False, False),
            "OBL_FIXED_BASIS_RESPONSE", "wins when the target is smooth in a fixed similarity and the sample is small; loses when an explicit small feature map suffices",
            "destroy similarity-label alignment", "an explicit finite feature map dominates at matched risk"),
 "K4-A03": (P("n_records", "log_n_records", "local", "none", "unshared", "exact_key", "one", False, False, False),
            "OBL_ARBITRARY_RECALL", "wins when records are independent and volatile; loses when a low-dimensional law generates them",
            "values generated by a stable low-dimensional law with high reuse", "an unpriced index, or aliasing across records"),
 "K4-A04": (P("n_hypotheses", "n_hypotheses", "global", "none", "shared", "none", "one", False, False, False),
            "OBL_UNCERTAIN_DECISION", "wins when the utility is uncertainty-sensitive and evidence is ambiguous; loses under a restricted loss where a point estimate suffices",
            "fully observed deterministic states", "posterior aliasing under a separating utility"),
 "K4-A05": (P("n_constraints", "search_tree", "global", "none", "shared", "none", "many", False, True, False),
            "OBL_CONSTRAINT_SATISFACTION", "wins when constraints are exact and the answer must be certified; loses when an approximate response is admissible",
            "constraints relaxed to a smooth objective", "an approximate parent is admissible at the same theta"),
 "K4-A06": (P("program_size", "search_tree", "none", "none", "shared", "none", "many", False, True, False),
            "OBL_EXACT_PROGRAM_ANSWER", "wins at low reuse where compiling is not amortized; loses at high reuse to a compiled table",
            "remove the verifier so candidates cannot be checked", "an admissible compiled parent is cheaper at H=1"),
 "K4-A07": (P("hidden_width", "hidden_width_times_length", "global", "none", "shared", "none", "many", False, False, False),
            "OBL_SEQUENTIAL_DEPENDENCE", "wins when the dependence is long-range and the state is small; loses to full-context comparison when length is short",
            "shuffle the sequence so order carries no information", "a stateless parent matches at the same theta"),
 "K4-A08": (P("state_dim", "state_dim_times_length", "global", "none", "shared", "none", "many", False, False, False),
            "OBL_LINEAR_DYNAMICAL_RESPONSE", "wins when the dynamics are linear-time-invariant and length is large",
            "make the dynamics input-dependent and nonlinear", "a nonlinear recurrent parent is required for admissibility"),
 "K4-A09": (P("kernel_size", "kernel_size_times_positions", "global", "none", "shared", "none", "one", False, False, False),
            "OBL_TRANSLATION_EQUIVARIANT_RESPONSE", "wins when the target commutes with the declared shift group; loses when position matters",
            "break the equivariance by making the answer position-dependent", "an unshared parent is not more expensive at matched risk"),
 "K4-A10": (P("edge_features", "n_edges_times_rounds", "global", "none", "shared", "none", "many", False, False, False),
            "OBL_RELATIONAL_PROPAGATION", "wins when the answer depends on graph neighbourhoods; loses when the graph is complete or empty",
            "randomize the edge set so adjacency carries no information", "a graph-blind parent matches"),
 "K4-A11": (P("n_positions_squared", "n_positions_squared", "global", "input_dependent", "shared", "metric", "one", False, False, False),
            "OBL_CONTENT_ADDRESSED_MIXING", "wins when which inputs matter depends on the input itself; loses to fixed routing when the dependence is static",
            "fix the mixing pattern so it cannot depend on content", "a fixed-routing parent matches at the same theta"),
 "K4-A12": (P("n_positions_times_window", "n_positions_times_window", "global", "input_dependent", "shared", "metric", "one", False, False, False),
            "OBL_SPARSE_CONTENT_MIXING", "wins when the content dependence is local or low-rank; the crossover against dense mixing is at the declared window fraction",
            "make the required dependence dense and long-range", "dense mixing is cheaper at the predicted window fraction"),
 "K4-A13": (P("n_experts_times_expert_size", "active_expert_size", "local", "input_dependent", "unshared", "none", "one", False, False, False),
            "OBL_HETEROGENEOUS_MODES", "wins when modes are separable and the router is accurate; loses to a dense parent when modes overlap",
            "make the modes fully overlapping so no partition helps", "a dense parent matches at matched quality and lower total burden"),
 "K4-A14": (P("corpus_size", "retrieval_plus_core", "none", "input_dependent", "shared", "exact_key", "one", False, False, True),
            "OBL_EXTERNAL_AUTHORITY_RECALL", "wins when facts are volatile and must be attributable; loses when facts are stable and few",
            "make every fact stable and small enough to internalize", "an internalized parent is admissible and cheaper"),
 "K4-A15": (P("rank_times_dim", "core_plus_rank", "local", "none", "shared", "none", "one", False, False, False),
            "OBL_SMALL_TARGETED_REVISION", "wins when the revision is low-rank relative to the core; loses when it is full-rank",
            "require a full-rank revision", "a full update is cheaper at the predicted rank"),
 "K4-A16": (P("n_members_times_member_size", "n_members_times_member_size", "global", "none", "unshared", "none", "one", True, False, False),
            "OBL_VARIANCE_REDUCTION", "wins when member errors are weakly correlated; loses when they are correlated",
            "make all members identical so averaging buys nothing", "a single member matches at the same risk"),
 "K4-A17": (P("proposer_plus_verifier", "n_proposals_times_check", "none", "none", "shared", "none", "many", True, True, False),
            "OBL_CERTIFIED_ANSWER_UNDER_UNRELIABLE_PROPOSAL", "wins when checking is much cheaper than proposing and proposals are unreliable",
            "make verification as expensive as proposing", "an unverified parent is admissible at the same theta"),
 "K4-A18": (P("dynamics_model_size", "rollout_depth_times_branch", "global", "none", "shared", "none", "many", False, False, False),
            "OBL_GOAL_REUSE_UNDER_KNOWN_DYNAMICS", "wins when dynamics are reused across many goals; loses at a single fixed goal",
            "a single fixed goal for the whole lifetime", "a direct policy parent is cheaper across the goal distribution"),
 "K4-A19": (P("policy_size", "policy_size", "global", "none", "shared", "none", "one", True, False, False),
            "OBL_SINGLE_GOAL_CONTROL", "wins at a fixed goal with cheap interaction; loses when goals change and dynamics are reusable",
            "make the goal change every episode", "a model-based parent is cheaper across the goal distribution"),
 "K4-A20": (P("vocab_times_context", "sequence_length", "global", "none", "shared", "none", "many", True, False, False),
            "OBL_SEQUENTIAL_GENERATION", "wins when the factorization order is natural and latency is per-token; loses when global coherence dominates",
            "require a jointly consistent answer with no admissible order", "a non-sequential parent matches at lower total burden"),
 "K4-A21": (P("score_model_size", "n_steps_times_model", "global", "none", "shared", "none", "many", True, False, False),
            "OBL_JOINT_SAMPLE_GENERATION", "wins when the target is high-dimensional and jointly constrained; the crossover against sequential is at the declared step count",
            "reduce the target to one dimension", "a sequential parent matches at fewer total charged steps"),
 "K4-A22": (P("latent_dim_plus_decoder", "decoder_size", "global", "none", "shared", "none", "one", True, False, False),
            "OBL_COMPRESSED_GENERATION", "wins when the data lie near a low-dimensional manifold; loses when they do not",
            "make the data full-dimensional with no manifold structure", "a full-dimensional parent matches at the same quality"),
}

NAME_KEY = {  # adjudication only. The runner MUST NOT read this file section.
 "K4-A01": "linear / GLM", "K4-A02": "kernel / fixed basis", "K4-A03": "exemplar / kNN memory",
 "K4-A04": "Bayesian belief / probabilistic state", "K4-A05": "symbolic / constraint system",
 "K4-A06": "search / planning", "K4-A07": "recurrent state", "K4-A08": "state-space system",
 "K4-A09": "CNN / equivariant sharing", "K4-A10": "GNN / message passing",
 "K4-A11": "dynamic routing / attention", "K4-A12": "sparse attention",
 "K4-A13": "conditional specialization / MoE", "K4-A14": "RAG / external authority memory",
 "K4-A15": "low-rank adapters", "K4-A16": "ensembles", "K4-A17": "verifier-gated proposal",
 "K4-A18": "model-based planning", "K4-A19": "model-free value/policy", "K4-A20": "autoregressive generation",
 "K4-A21": "diffusion / score generation", "K4-A22": "latent-variable generation",
}

GRAMMARS = {
 "G1_TENSOR_GRAPH": "typed dataflow over finite-width numeric buffers: elementwise arithmetic, reduction, indexed "
                    "gather/scatter, comparison, branch, bounded iteration, explicit random-bit draw. No convolution, "
                    "attention, gate, expert, retriever or adapter macro.",
 "G2_SYMBOLIC_PROGRAM": "register machine over scalars and arrays: load/store, arithmetic, comparison, conditional "
                        "jump, bounded loop, explicit random-bit draw, callable sub-programs. No architecture macro.",
 "G3_FSM_MESSAGE": "finite-state automata with typed message passing on a declared topology: local transition tables, "
                   "send/receive, bounded rounds, explicit random-bit draw. No architecture macro.",
}

CONTROL = {
 "purpose": "preregistered known-control recovery. INCONCLUSIVE_SEARCH may be claimed ONLY if every control below is "
            "recovered by the same grammar, budget and seed policy in the same cell. If a control fails, the cell is "
            "INCONCLUSIVE_GRAMMAR or a harness fault -- never INCONCLUSIVE_SEARCH, and never THEORY_RED.",
 "controls": ["CTL_IDENTITY: reproduce the input", "CTL_CONSTANT: emit the majority label",
              "CTL_LOOKUP: recall 4 taught key-value pairs exactly",
              "CTL_AFFINE: an affine function of 4 inputs with coefficients on the declared grid"],
 "coverage_bound": "a cell is search-limited only if scored candidates >= 1e6 OR the expressible set at the declared "
                   "caps was exhausted; both are recorded per cell.",
}

COSTS = ["development_compute", "search_compute", "description_compiler_burden", "state_storage",
         "serve_compute_latency", "update_retraining", "communication", "verification", "human_external_intervention"]


def main():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        sha = "UNKNOWN"
    fams = {}
    for fid, (vec, obl, phase, twin, kill) in FAM.items():
        fams[fid] = {"property_vector": vec, "obligation_class": obl, "phase_prediction": phase,
                     "negative_twin": twin, "kill_condition": kill}
    # collisions are a REPORTED RESULT, not something to tune away
    seen, collisions = {}, []
    for fid, f in fams.items():
        k = json.dumps(f["property_vector"], sort_keys=True)
        if k in seen:
            collisions.append([seen[k], fid])
        seen[k] = fid
    body = {
        "schema": "GMIK4LOFOFreezeV1",
        "frozen_at_commit_parent": sha,
        "issue": [431, 433, 434, 435, 426],
        "purpose": "leave-one-family-out neutral rediscovery; prediction frozen BEFORE any search",
        "n_families": len(fams),
        "property_axes": list(AX),
        "families": fams,
        "grammars": GRAMMARS,
        "grammar_independence_note":
            "three grammars with disjoint primitive sets and disjoint state models. Reminting one grammar does not "
            "count as independence and is not done here. NOTE under IG-5: all three are authored by the same process, "
            "so agreement between them rules out implementation artifacts but NOT shared conceptual bias about which "
            "primitives are natural. That residue is open and is not claimed closed.",
        "known_control_recovery": CONTROL,
        "charged_cost_channels": COSTS,
        "verdicts": {
            "K4_RECOVERY_GREEN": "admissible machine found by name-blind search whose MEASURED property vector equals "
                                 "the frozen predicted vector for the held-out family",
            "THEORY_RED": "admissible machine found whose measured vector CONTRADICTS the frozen prediction",
            "INCONCLUSIVE_GRAMMAR": "held-out semantics not expressible in this grammar at the declared caps",
            "INCONCLUSIVE_SEARCH": "expressible, budget exhausted, AND every known control recovered in the same cell"},
        "property_vector_collisions": collisions,
        "collision_disclosure":
            "families sharing a property vector cannot be distinguished by this benchmark. Any such pair is reported "
            "as a limitation of the vector and BOTH are scored as unresolved, rather than crediting a recovery to "
            "whichever family is convenient.",
        "independence_status": {
            "IG-1_generator": "CLOSED_BY_EXHAUSTION where the obligation class is a complete enumeration at the "
                              "declared cap; otherwise IG-2 applies",
            "IG-2_seed": "CLOSED_BY_FUTURE_ENTROPY -- seed rule committed here, resolved against a public value that "
                         "does not exist yet",
            "IG-3_leakage": "CLOSED_BY_WITNESSED_COMMIT -- this freeze is pushed to GitHub before any result exists",
            "IG-4_meter": "PENDING_INDEPENDENT_BUCKETING",
            "IG-5_encoding": "PENDING_INDEPENDENT_PRIMITIVES"},
        "name_key_warning": "name_key is for human adjudication AFTER scoring. The runner must not read it. A name "
                            "leak invalidates the zero-prior evidence.",
        "name_key": NAME_KEY,
    }
    body["freeze_sha256"] = hashlib.sha256(
        json.dumps({k: v for k, v in body.items() if k != "freeze_sha256"}, sort_keys=True).encode()).hexdigest()
    json.dump(body, open(OUT, "w"), indent=1, sort_keys=True)
    print(f"wrote {OUT}")
    print(f"  families {len(fams)}  grammars {len(GRAMMARS)}  cost channels {len(COSTS)}")
    print(f"  property-vector collisions: {collisions if collisions else 'none'}")
    print(f"  freeze sha256 {body['freeze_sha256'][:16]}")


if __name__ == "__main__":
    main()
