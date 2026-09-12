from __future__ import annotations

"""DG-10 successor: resource axes are measured, never stored as candidate labels.

V3 had one StateShape per held-out family and Candidate.vector() copied the frozen-style
`state_scales_with` / `serve_scales_with` labels out of that token.  This module removes that
channel.  A candidate carries two low-level integer resource expressions, one for retained state
and one for per-query work.  The two expressions are selected independently.  Their public
property labels are recovered only by executing them on a fixed measurement probe panel and
matching the resulting numeric trace to the preregistered reference laws.

Capability atoms and all other morphology axes are also selected independently of the resource
expressions.  Thus no candidate token contains a family id or a pre-paired state/serve signature.
The target property vector may be used only by the separate expressibility-witness path, never by
search generation or ranking.
"""

from dataclasses import dataclass
import hashlib
import json
import math
import random

import gmi_k4_search as base

# ------------------------------- expression calculus ---------------------------------
# ('v', name), ('mul', a, b), ('add', a, b), ('log2ceil', a), ('pow', a, b-int), ('const', k)

def V(name): return ("v", name)
def MUL(a, b): return ("mul", a, b)
def ADD(a, b): return ("add", a, b)
def LOG(a): return ("log2ceil", a)
def POW(a, n): return ("pow", a, int(n))
def C(n): return ("const", int(n))


def eval_expr(expr, env):
    op = expr[0]
    if op == "v": return int(env[expr[1]])
    if op == "const": return int(expr[1])
    if op == "mul": return eval_expr(expr[1], env) * eval_expr(expr[2], env)
    if op == "add": return eval_expr(expr[1], env) + eval_expr(expr[2], env)
    if op == "log2ceil": return max(1, int(math.ceil(math.log2(max(2, eval_expr(expr[1], env))))))
    if op == "pow": return eval_expr(expr[1], env) ** int(expr[2])
    raise KeyError(op)


STATE_REFERENCE = {
    "n_features": V("features"),
    "n_retained_sections": V("retained"),
    "n_records": V("records"),
    "n_hypotheses": V("hypotheses"),
    "n_constraints": V("constraints"),
    "program_size": V("program"),
    "hidden_width": V("hidden"),
    "state_dim": V("state_dim"),
    "kernel_size": V("kernel"),
    "edge_features": V("edges"),
    "n_positions_squared": POW(V("positions"), 2),
    "n_positions_times_window": MUL(V("positions"), V("window")),
    "n_experts_times_expert_size": MUL(V("experts"), V("expert_size")),
    "corpus_size": V("corpus"),
    "rank_times_dim": MUL(V("rank"), V("dim")),
    "n_members_times_member_size": MUL(V("members"), V("member_size")),
    "proposer_plus_verifier": ADD(V("proposer"), V("verifier")),
    "dynamics_model_size": V("dynamics"),
    "policy_size": V("policy"),
    "vocab_times_context": MUL(V("vocab"), V("context")),
    "score_model_size": V("score_model"),
    "latent_dim_plus_decoder": ADD(V("latent"), V("decoder")),
}
SERVE_REFERENCE = {
    "n_features": V("features"),
    "n_retained_sections": V("retained"),
    "log_n_records": LOG(V("records")),
    "n_hypotheses": V("hypotheses"),
    "search_tree": POW(V("search_branch"), 3),
    "hidden_width_times_length": MUL(V("hidden"), V("sequence_length")),
    "state_dim_times_length": MUL(V("state_dim"), V("sequence_length")),
    "kernel_size_times_positions": MUL(V("kernel"), V("positions")),
    "n_edges_times_rounds": MUL(V("edges"), V("rounds")),
    "n_positions_squared": POW(V("positions"), 2),
    "n_positions_times_window": MUL(V("positions"), V("window")),
    "active_expert_size": V("expert_size"),
    "retrieval_plus_core": ADD(V("retrieval"), V("core")),
    "core_plus_rank": ADD(V("core"), V("rank")),
    "n_members_times_member_size": MUL(V("members"), V("member_size")),
    "n_proposals_times_check": MUL(V("proposals"), V("check")),
    "rollout_depth_times_branch": MUL(V("rollout_depth"), V("branch")),
    "policy_size": V("policy"),
    "sequence_length": V("sequence_length"),
    "n_steps_times_model": MUL(V("steps"), V("model")),
    "decoder_size": V("decoder"),
}
# Search also contains laws that are not any frozen target coordinate.
STATE_DISTRACTORS = (C(1), V("positions"), POW(V("dim"), 2))
SERVE_DISTRACTORS = (C(1), V("records"), ADD(V("positions"), V("window")))
STATE_LAWS = tuple(STATE_REFERENCE.values()) + STATE_DISTRACTORS
SERVE_LAWS = tuple(SERVE_REFERENCE.values()) + SERVE_DISTRACTORS

# Probe worlds are deliberately asymmetric so different symbolic laws have different traces.
_RESOURCE_VARS = sorted({
    "features","retained","records","hypotheses","constraints","program","hidden","state_dim","kernel","edges",
    "positions","window","experts","expert_size","corpus","rank","dim","members","member_size","proposer","verifier",
    "dynamics","policy","vocab","context","score_model","latent","decoder","search_branch","sequence_length","rounds",
    "retrieval","core","proposals","check","rollout_depth","branch","steps","model",
})


def _probe_env(i):
    env = {v: 2 + ((j * 7 + i * 11) % 13) for j, v in enumerate(_RESOURCE_VARS)}
    # Force a few coordinates to mutually incommensurate values on every probe.
    env["search_branch"] = 2 + (i % 4)
    env["window"] = 2 + ((3 * i + 1) % 7)
    env["rank"] = 1 + (i % 5)
    return env

MEASUREMENT_PROBES = tuple(_probe_env(i) for i in range(19))


def signature(expr): return tuple(eval_expr(expr, p) for p in MEASUREMENT_PROBES)
STATE_SIG_TO_LABEL = {signature(e): k for k, e in STATE_REFERENCE.items()}
SERVE_SIG_TO_LABEL = {signature(e): k for k, e in SERVE_REFERENCE.items()}
if len(STATE_SIG_TO_LABEL) != len(STATE_REFERENCE):
    raise AssertionError("state measurement panel aliases reference laws")
if len(SERVE_SIG_TO_LABEL) != len(SERVE_REFERENCE):
    raise AssertionError("serve measurement panel aliases reference laws")


def measure_state_law(expr): return STATE_SIG_TO_LABEL.get(signature(expr), "UNCLASSIFIED_STATE_LAW")
def measure_serve_law(expr): return SERVE_SIG_TO_LABEL.get(signature(expr), "UNCLASSIFIED_SERVE_LAW")


def task_env(scale: int):
    s = max(1, int(scale))
    return {
        "features": 4*s, "retained": 8*s, "records": 16*s, "hypotheses": 4*s, "constraints": 8*s,
        "program": 8*s, "hidden": 8*s, "state_dim": 4*s, "kernel": 2*s+1, "edges": 16*s,
        "positions": 8*s, "window": 2*s, "experts": 4*s, "expert_size": 16*s, "corpus": 64*s,
        "rank": s, "dim": 16*s, "members": 4*s, "member_size": 8*s, "proposer": 8*s, "verifier": 4*s,
        "dynamics": 16*s, "policy": 16*s, "vocab": 32*s, "context": 8*s, "score_model": 16*s,
        "latent": 4*s, "decoder": 16*s, "search_branch": 2+s, "sequence_length": 8*s, "rounds": 2*s,
        "retrieval": 4*s, "core": 16*s, "proposals": 4*s, "check": 2*s, "rollout_depth": 4*s,
        "branch": 2*s, "steps": 4*s, "model": 16*s,
    }

# ------------------------------- capability / program factors -------------------------
CAP_ATOMS = tuple(sorted({
    "affine","direct_numeric","fixed_basis","volatile_records","uncertainty","belief_update","constraints","exact_search",
    "program_search","sequence_state","nonlinear_state","linear_dynamics","local_tied","equivariant","graph_local",
    "message_rounds","dense_pair","sparse_pair","specialist","external_store","low_rank_revision","aggregate",
    "variance_reduce","proposal","world_model","planning","direct_policy","ordered_factorization","sequence_model",
    "iterative_denoise","joint_model","latent_compress",
}))
ROUTING = ("none", "input_dependent")
SHARING = ("shared", "unshared")
RETRIEVAL = ("none", "exact_key", "metric")
ITERATIONS = ("one", "many")
LOCALITY = ("none", "local", "global")
BOOLS = (False, True)
PREFIX = {"G1_TENSOR_GRAPH": "TG4", "G2_SYMBOLIC_PROGRAM": "RP4", "G3_FSM_MESSAGE": "FM4"}
GRAMMAR_PRICE = {"G1_TENSOR_GRAPH": 1.0, "G2_SYMBOLIC_PROGRAM": 1.08, "G3_FSM_MESSAGE": 1.12}

# Minimal capability witnesses are outside search ranking and are used only to prove grammar expressibility.
REQUIRED_CAPS = {
    "linear": ("affine",), "basis": ("fixed_basis",), "recall": ("volatile_records",), "belief": ("uncertainty",),
    "constraint": ("constraints","exact_search"), "program": ("program_search","exact_search"),
    "sequence": ("sequence_state",), "lti": ("linear_dynamics",), "equivariant": ("equivariant",),
    "graph": ("graph_local",), "content": ("dense_pair",), "sparse_content": ("sparse_pair",),
    "modes": ("specialist",), "authority": ("external_store",), "lowrank": ("low_rank_revision",),
    "ensemble": ("variance_reduce",), "verify": ("proposal",), "model_based": ("world_model","planning"),
    "policy": ("direct_policy",), "ordered_gen": ("ordered_factorization",), "joint_gen": ("iterative_denoise",),
    "latent_gen": ("latent_compress",),
}

@dataclass(frozen=True)
class Candidate:
    grammar: str
    state_expr: tuple
    serve_expr: tuple
    cap_atoms: tuple[str, ...]
    routing: str
    sharing: str
    retrieval: str
    serve_iterations: str
    stochastic_serve: bool
    verifier_gated: bool
    external_authority: bool
    update_locality: str
    width_knob: int

    @property
    def cid(self):
        return hashlib.sha256(json.dumps(self.serial(), sort_keys=True).encode()).hexdigest()[:20]

    def caps(self):
        c = set(self.cap_atoms)
        if self.routing == "input_dependent": c.add("content_route")
        if self.retrieval == "exact_key": c.add("exact_lookup")
        if self.retrieval == "metric": c.add("similarity")
        if self.verifier_gated: c.add("checker")
        if self.external_authority: c.add("authority")
        if "specialist" in c and self.routing == "input_dependent": c.add("mode_partition")
        return tuple(sorted(c))

    def serial(self):
        return [self.grammar, self.state_expr, self.serve_expr, self.cap_atoms, self.routing, self.sharing,
                self.retrieval, self.serve_iterations, self.stochastic_serve, self.verifier_gated,
                self.external_authority, self.update_locality, self.width_knob]

    def tokens(self):
        p = PREFIX[self.grammar]
        hstate = hashlib.sha256(json.dumps(self.state_expr).encode()).hexdigest()[:10]
        hserve = hashlib.sha256(json.dumps(self.serve_expr).encode()).hexdigest()[:10]
        toks = [f"{p}_ALLOC_{hstate}", f"{p}_WORK_{hserve}"]
        toks += [f"{p}_CAP_{x.upper()}" for x in self.cap_atoms]
        toks += [f"{p}_ROUTE_{self.routing.upper()}", f"{p}_SHARE_{self.sharing.upper()}",
                 f"{p}_READ_{self.retrieval.upper()}", f"{p}_STEP_{self.serve_iterations.upper()}",
                 f"{p}_WRITE_{self.update_locality.upper()}", f"{p}_WIDTH_{self.width_knob}"]
        if self.stochastic_serve: toks.append(f"{p}_RAND")
        if self.verifier_gated: toks.append(f"{p}_CHECK")
        if self.external_authority: toks.append(f"{p}_EXTERNAL")
        return tuple(toks)

    def vector(self):
        return {
            "state_scales_with": measure_state_law(self.state_expr),
            "serve_scales_with": measure_serve_law(self.serve_expr),
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
        v = self.vector()
        return base.Form(self.cid, v["state_scales_with"], v["serve_scales_with"], self.update_locality,
                         self.routing, self.sharing, self.retrieval, self.serve_iterations,
                         self.stochastic_serve, self.verifier_gated, self.external_authority,
                         self.caps(), 1.0 + 0.04 * (len(self.cap_atoms) + self.width_knob))


def _pick(rng, seq): return seq[rng.randrange(len(seq))]

def sampled_candidate(grammar: str, seed: int, index: int) -> Candidate:
    if grammar not in PREFIX: raise KeyError(grammar)
    # Candidate index is mixed with seed; there is no family id or target vector in this generator.
    h = hashlib.sha256(f"K4V4:{grammar}:{seed}:{index}".encode()).digest()
    rng = random.Random(int.from_bytes(h[:8], "big"))
    k = 1 + rng.randrange(3)
    atoms = tuple(sorted(rng.sample(CAP_ATOMS, k)))
    return Candidate(grammar, _pick(rng, STATE_LAWS), _pick(rng, SERVE_LAWS), atoms,
                     _pick(rng, ROUTING), _pick(rng, SHARING), _pick(rng, RETRIEVAL), _pick(rng, ITERATIONS),
                     _pick(rng, BOOLS), _pick(rng, BOOLS), _pick(rng, BOOLS), _pick(rng, LOCALITY), 1 + rng.randrange(2))


def witness_from_target(grammar: str, target: dict, task: str) -> Candidate:
    """Constructive expressibility witness; forbidden from search ranking.

    It consumes the frozen target vector only so a non-exhaustive search failure can be attributed to search
    rather than grammar. The returned witness is reported separately and never inserted into the search stream.
    """
    state = STATE_REFERENCE[target["state_scales_with"]]
    serve = SERVE_REFERENCE[target["serve_scales_with"]]
    return Candidate(grammar, state, serve, REQUIRED_CAPS[task], target["routing"], target["sharing"],
                     target["retrieval"], target["serve_iterations"], bool(target["stochastic_serve"]),
                     bool(target["verifier_gated"]), bool(target["external_authority"]), target["update_locality"], 1)


def resource_counts(cand: Candidate, scale: int):
    env = task_env(scale)
    return eval_expr(cand.state_expr, env), eval_expr(cand.serve_expr, env)


def lifecycle(cand: Candidate, scale: int, profile: dict):
    state, work = resource_counts(cand, scale)
    gp = GRAMMAR_PRICE[cand.grammar]
    tokens = len(cand.tokens())
    local_factor = {"none": 0.0, "local": 0.15, "global": 1.0}[cand.update_locality]
    cost = {
        "development_compute": gp * (tokens + state * (0.5 + 0.15 * len(cand.cap_atoms))),
        "search_compute": gp * tokens,
        "description_compiler_burden": gp * (tokens + 0.15 * state),
        "state_storage": float(state),
        "serve_compute_latency": gp * float(work),
        "update_retraining": gp * state * local_factor,
        "communication": gp * work * (0.20 if cand.routing == "input_dependent" else 0.03),
        "verification": gp * work * (0.12 if cand.verifier_gated else 0.0),
        "human_external_intervention": 1.0 if cand.external_authority else 0.0,
    }
    # Fresh-world nuisance variables modify costs without consulting the frozen target vector.
    reuse = profile.get("reuse_multiplier", 1.0)
    cost["development_compute"] /= max(0.25, reuse)
    cost["description_compiler_burden"] /= max(0.5, reuse)
    if cand.retrieval == "exact_key":
        cost["update_retraining"] *= max(0.3, 1.2 - profile.get("volatility", 0.5))
    if cand.routing == "input_dependent":
        d = profile.get("dependence_density", 0.5)
        cost["serve_compute_latency"] *= 0.75 + 0.55*d
        cost["communication"] *= 0.75 + 0.70*d
    if "low_rank_revision" in cand.caps():
        f = max(0.08, min(1.0, profile.get("rank_fraction", 0.25) * 3.0))
        cost["state_storage"] *= f; cost["update_retraining"] *= f
    if cand.verifier_gated:
        cost["verification"] *= profile.get("checker_ratio", 0.15)
    return cost


def inventory(grammar: str, n: int = 5000):
    out = set()
    for i in range(n): out.update(sampled_candidate(grammar, 0xA11CE, i).tokens())
    return out


def assert_disjoint():
    inv = {g: inventory(g) for g in PREFIX}
    gs = sorted(inv)
    for i, a in enumerate(gs):
        for b in gs[i+1:]:
            if inv[a] & inv[b]: raise AssertionError((a, b, sorted(inv[a] & inv[b])[:5]))
    return {g: len(inv[g]) for g in gs}

DISJOINT_INVENTORY_SIZES = assert_disjoint()
