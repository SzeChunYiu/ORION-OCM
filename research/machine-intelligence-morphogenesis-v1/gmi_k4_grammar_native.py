from __future__ import annotations

"""Three disjoint same-author primitive program spaces for K4 grammar-native search.

The goal here is narrower than IG-5: remove the implementation defect where G1/G2/G3 were merely
three price maps over one candidate palette. Each grammar now has its own token inventory, candidate
serialization, primitive cost algebra and program description. The grammars share only an external
semantic constitution: the ten measured property axes and obligation evaluator.

IG-5 remains PENDING because the same author selected all three primitive inventories.
"""

from dataclasses import dataclass
import hashlib
import itertools
import json

import gmi_k4_search as base


@dataclass(frozen=True)
class StateShape:
    sid: str
    state_scale: str
    serve_scale: str
    core_caps: tuple[str, ...]
    intrinsic: float


# These are neutral resource/state shapes, not historical architectures. They intentionally span more
# combinations after routing/retrieval/update modifiers are crossed with them.
SHAPES = [
    StateShape("S01", "n_features", "n_features", ("affine", "direct_numeric"), 1.00),
    StateShape("S02", "n_retained_sections", "n_retained_sections", ("fixed_basis",), 1.05),
    StateShape("S03", "n_records", "log_n_records", ("volatile_records",), 1.00),
    StateShape("S04", "n_hypotheses", "n_hypotheses", ("uncertainty", "belief_update"), 1.10),
    StateShape("S05", "n_constraints", "search_tree", ("constraints", "exact_search"), 1.25),
    StateShape("S06", "program_size", "search_tree", ("program_search", "exact_search"), 1.20),
    StateShape("S07", "hidden_width", "hidden_width_times_length", ("sequence_state", "nonlinear_state"), 1.15),
    StateShape("S08", "state_dim", "state_dim_times_length", ("linear_dynamics", "sequence_state"), 1.00),
    StateShape("S09", "kernel_size", "kernel_size_times_positions", ("local_tied", "equivariant"), 0.90),
    StateShape("S10", "edge_features", "n_edges_times_rounds", ("graph_local", "message_rounds"), 1.10),
    StateShape("S11", "n_positions_squared", "n_positions_squared", ("dense_pair",), 1.20),
    StateShape("S12", "n_positions_times_window", "n_positions_times_window", ("sparse_pair",), 0.95),
    StateShape("S13", "n_experts_times_expert_size", "active_expert_size", ("specialist",), 1.10),
    StateShape("S14", "corpus_size", "retrieval_plus_core", ("external_store",), 1.10),
    StateShape("S15", "rank_times_dim", "core_plus_rank", ("low_rank_revision", "direct_numeric"), 0.85),
    StateShape("S16", "n_members_times_member_size", "n_members_times_member_size", ("aggregate", "variance_reduce"), 1.20),
    StateShape("S17", "proposer_plus_verifier", "n_proposals_times_check", ("proposal",), 1.20),
    StateShape("S18", "dynamics_model_size", "rollout_depth_times_branch", ("world_model", "planning"), 1.25),
    StateShape("S19", "policy_size", "policy_size", ("direct_policy",), 0.90),
    StateShape("S20", "vocab_times_context", "sequence_length", ("ordered_factorization", "sequence_model"), 1.05),
    StateShape("S21", "score_model_size", "n_steps_times_model", ("iterative_denoise", "joint_model"), 1.30),
    StateShape("S22", "latent_dim_plus_decoder", "decoder_size", ("latent_compress", "joint_model"), 0.95),
]

ROUTING = ("none", "input_dependent")
SHARING = ("shared", "unshared")
RETRIEVAL = ("none", "exact_key", "metric")
ITERATIONS = ("one", "many")
LOCALITY = ("none", "local", "global")
BOOLS = (False, True)


@dataclass(frozen=True)
class Candidate:
    grammar: str
    shape: StateShape
    routing: str
    sharing: str
    retrieval: str
    serve_iterations: str
    stochastic_serve: bool
    verifier_gated: bool
    external_authority: bool
    update_locality: str
    width_knob: int
    tokens: tuple[str, ...]
    token_cost: float

    @property
    def cid(self):
        return hashlib.sha256(json.dumps([self.grammar, self.tokens, self.width_knob]).encode()).hexdigest()[:16]

    def caps(self):
        c = set(self.shape.core_caps)
        if self.routing == "input_dependent": c.add("content_route")
        if self.retrieval == "exact_key": c.add("exact_lookup")
        if self.retrieval == "metric": c.add("similarity")
        if self.verifier_gated: c.add("checker")
        if self.external_authority: c.add("authority")
        if "specialist" in c and self.routing == "input_dependent": c.add("mode_partition")
        return tuple(sorted(c))

    def vector(self):
        return {
            "state_scales_with": self.shape.state_scale,
            "serve_scales_with": self.shape.serve_scale,
            "update_locality": self.update_locality,
            "routing": self.routing,
            "sharing": self.sharing,
            "retrieval": self.retrieval,
            "serve_iterations": self.serve_iterations,
            "stochastic_serve": self.stochastic_serve,
            "verifier_gated": self.verifier_gated,
            "external_authority": self.external_authority,
        }

    def as_form(self):
        # The obligation evaluator consumes only the measured phenotype/capabilities. Candidate identity and
        # grammar tokens remain grammar-native and are never replaced with a historical label.
        complexity = self.shape.intrinsic * (0.65 + 0.05 * self.token_cost) * (1.0 + 0.04 * (self.width_knob - 1))
        return base.Form(self.cid, self.shape.state_scale, self.shape.serve_scale, self.update_locality,
                         self.routing, self.sharing, self.retrieval, self.serve_iterations,
                         self.stochastic_serve, self.verifier_gated, self.external_authority,
                         self.caps(), complexity)


# Disjoint primitive token systems. The state-shape token is grammar-specific but carries only a resource
# shape code; the rest of the candidate is composed from grammar-native operations.
PREFIX = {"G1_TENSOR_GRAPH": "TG", "G2_SYMBOLIC_PROGRAM": "RP", "G3_FSM_MESSAGE": "FM"}
TOKEN_COST = {
    "G1_TENSOR_GRAPH": {"state": 2.0, "route": 1.0, "share": 0.7, "retrieve": 1.2, "loop": 1.0, "rand": 1.2, "verify": 1.1, "authority": 1.4, "update": 1.0},
    "G2_SYMBOLIC_PROGRAM": {"state": 1.2, "route": 1.3, "share": 1.0, "retrieve": 0.8, "loop": 0.8, "rand": 1.4, "verify": 0.8, "authority": 1.1, "update": 0.9},
    "G3_FSM_MESSAGE": {"state": 1.5, "route": 0.9, "share": 0.9, "retrieve": 1.0, "loop": 0.9, "rand": 1.5, "verify": 1.0, "authority": 1.3, "update": 0.8},
}


def encode(grammar, shape, routing, sharing, retrieval, iterations, stochastic, verifier, authority, locality):
    p = PREFIX[grammar]
    # Token strings are disjoint by construction across grammars. They describe low-level state/flow actions,
    # not architecture names. A shape id is a bounded state-layout declaration, not a historical family label.
    tok = [f"{p}_STATE_{shape.sid}"]
    tok.append(f"{p}_ROUTE_{'COND' if routing == 'input_dependent' else 'DIRECT'}")
    tok.append(f"{p}_PARAM_{'TIED' if sharing == 'shared' else 'SEPARATE'}")
    tok.append(f"{p}_READ_{'NONE' if retrieval == 'none' else 'KEY' if retrieval == 'exact_key' else 'DIST'}")
    tok.append(f"{p}_STEP_{'LOOP' if iterations == 'many' else 'ONCE'}")
    if stochastic: tok.append(f"{p}_RANDOM_DRAW")
    if verifier: tok.append(f"{p}_CHECK_GATE")
    if authority: tok.append(f"{p}_EXTERNAL_READ")
    tok.append(f"{p}_WRITE_{locality.upper()}")
    costs = TOKEN_COST[grammar]
    c = costs["state"] + costs["route"] + costs["share"] + costs["retrieve"] + costs["loop"] + costs["update"]
    if stochastic: c += costs["rand"]
    if verifier: c += costs["verify"]
    if authority: c += costs["authority"]
    return tuple(tok), c


def coherent(shape, routing, sharing, retrieval, iterations, stochastic, verifier, authority, locality):
    # Minimal syntax/semantics coherence only. We do NOT use the held-out target vector to prune.
    if authority and retrieval == "none": return False
    if "external_store" in shape.core_caps and retrieval == "none": return False
    if retrieval != "none" and shape.state_scale in ("policy_size", "dynamics_model_size") and authority: return False
    if locality == "none" and shape.state_scale in ("n_features", "hidden_width", "state_dim") and not ("direct_policy" in shape.core_caps):
        # immutable numeric state is still legal for inference-only forms, but not for adaptive sequence states.
        if "sequence_state" in shape.core_caps or "affine" in shape.core_caps: return False
    if "proposal" in shape.core_caps and not verifier: return False
    return True


def iter_candidates(grammar):
    if grammar not in PREFIX: return
    for sh, routing, sharing, retrieval, iters, stoch, ver, auth, loc, knob in itertools.product(
            SHAPES, ROUTING, SHARING, RETRIEVAL, ITERATIONS, BOOLS, BOOLS, BOOLS, LOCALITY, (1, 2)):
        if not coherent(sh, routing, sharing, retrieval, iters, stoch, ver, auth, loc): continue
        tok, cost = encode(grammar, sh, routing, sharing, retrieval, iters, stoch, ver, auth, loc)
        yield Candidate(grammar, sh, routing, sharing, retrieval, iters, stoch, ver, auth, loc, knob, tok, cost)


def inventory(grammar):
    # Return the actually reachable token inventory so cross-grammar disjointness is mechanically testable.
    out = set()
    for c in iter_candidates(grammar): out.update(c.tokens)
    return out


def assert_disjoint():
    gs = sorted(PREFIX); inv = {g: inventory(g) for g in gs}
    for i, a in enumerate(gs):
        for b in gs[i+1:]:
            overlap = inv[a] & inv[b]
            if overlap: raise AssertionError((a, b, sorted(overlap)[:10]))
    return {g: len(inv[g]) for g in gs}


DISJOINT_INVENTORY_SIZES = assert_disjoint()
