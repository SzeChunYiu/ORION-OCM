#!/usr/bin/env python3
"""GMI #833 AE15 -- world-model necessity boundary, route A (executor).

Emits RESULT_V1.json on stdout.  Stdlib only, exact rational arithmetic
(fractions.Fraction and int) everywhere; no float appears in any emitted
value, check, bound, hostile or null record.

Route A computes
  * the model-based optimum by a MEMOISED BACKWARD RECURSION OVER REACHABLE
    BELIEF POINTS (normalised belief vectors keyed in a memo table), and
  * every class value by FORWARD PROPAGATION OF AN EXACT STATE DISTRIBUTION
    one step at a time, and
  * the phase boundary in CLOSED FORM from the algebraic identity
    c*(G) = V_mb(G) - V_mf(G).

Route B (independent_world_model_oracle_v1.py) recomputes all of it by the
Smallwood-Sondik alpha-vector backward enumeration over the whole belief
simplex with exact pointwise-dominance pruning, and by enumerating complete
state/observation trajectories.  It never imports this module.
"""
import hashlib
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))

SCHEMA = "GMI_833_AE15_WORLD_MODEL_NECESSITY_RESULT_V1"
PACKAGE = "gmi-833-ae-ae15-world-model-necessity-v1"
ISSUE = 833
ISSUE_COMMENT_ID = 5692689542
SECTION = "AE15"
SOURCE_MAIN = "0dcdec54fbece041ee2b7cd1f630469ad85d19d3"
# custody shas supplied by the lane owner; these are the shas that exist on the
# branch.  The register carries its own `freeze_commit` field and the executor
# checks it against this value rather than assuming it (see results.custody).
FREEZE_COMMIT = "0f166240f67cce4dc7da8ab5acd1189d67ea1107"
REGISTER_COMMIT = "bbba259b86f9fc53402527dd662405422296fb3f"
CLAIM_CEILING = ("GMI_833_AE15_WORLD_MODEL_NECESSITY_BOUNDARY_DERIVED_ON_"
                 "REGISTERED_FINITE_POMDP_ROSTER")

# FORBIDDEN promotions, de-duplicated from FREEZE_V1.md (the freeze lists
# WORLD_MODEL_ALWAYS_REQUIRED twice; the freeze is not edited).
FORBIDDEN_PROMOTIONS = [
    "ALL_LEARNING_IS_COMPRESSION",
    "ARCHITECTURE_SELECTION_LAW",
    "ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER",
    "COMPLETE_GMI",
    "FREE_ENERGY_PRINCIPLE_PROVED",
    "GENERAL_REASONING_REDUCED_TO_PREDICTION",
    "GMI_MORPHOLOGY_PREDICTION",
    "INTELLIGENCE_EQUALS_COMPRESSION",
    "LATENTS_ARE_HUMAN_INTERPRETABLE",
    "MANIFOLD_HYPOTHESIS_UNIVERSAL",
    "MODEL_BASED_DOMINATES_MODEL_FREE",
    "MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE",
    "REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT",
    "THERMODYNAMIC_INTELLIGENCE_LAW",
    "WORLD_MODEL_ALWAYS_REQUIRED",
    "WORLD_MODEL_NEVER_REQUIRED",
]

CLASSES = [
    "CACHED_SKILL",
    "EXPLICIT_GENERATIVE_MODEL",
    "PREDICTIVE_STATE",
    "REACTIVE_POLICY",
    "VALUE_REPRESENTATION",
]

# The registered interface coordinates.  c1..c7 are all COMPUTED on the
# registered roster; none is asserted as prose.
COORDS = [
    "c1_emits_an_action",
    "c2_observation_closed_loop",
    "c3_time_or_history_varying",
    "c4_predicts_future_observations_exactly",
    "c5_stores_reward_derived_rationals",
    "c6_probe_reoptimizes",
    "c7_realizes_every_memoryless_action_map",
]


def fs(x):
    """Exact rational as a string."""
    return str(F(x))


# ---------------------------------------------------------------------------
# registered finite POMDPs
# ---------------------------------------------------------------------------
class World(object):
    """A registered finite POMDP K = (S, O, A, T, Z, R, gamma, H)."""

    def __init__(self, name, snames, anames, onames, trans, zobs, rew, b0,
                 gamma, horizon):
        self.name = name
        self.snames = list(snames)
        self.anames = list(anames)
        self.onames = list(onames)
        self.nS = len(snames)
        self.nA = len(anames)
        self.nO = len(onames)
        si = dict((n, i) for i, n in enumerate(self.snames))
        ai = dict((n, i) for i, n in enumerate(self.anames))
        oi = dict((n, i) for i, n in enumerate(self.onames))
        self.T = [[tuple(F(0) for _ in range(self.nS)) for _ in range(self.nS)]
                  for _ in range(self.nA)]
        for (s, a), row in sorted(trans.items()):
            vec = [F(0)] * self.nS
            for sp, p in sorted(row.items()):
                vec[si[sp]] = F(p)
            self.T[ai[a]][si[s]] = tuple(vec)
        self.Z = [tuple(F(0) for _ in range(self.nO)) for _ in range(self.nS)]
        for s, row in sorted(zobs.items()):
            vec = [F(0)] * self.nO
            for o, p in sorted(row.items()):
                vec[oi[o]] = F(p)
            self.Z[si[s]] = tuple(vec)
        self.R = [[F(0)] * self.nS for _ in range(self.nA)]
        for (s, a), v in sorted(rew.items()):
            self.R[ai[a]][si[s]] = F(v)
        vec = [F(0)] * self.nS
        for s, p in sorted(b0.items()):
            vec[si[s]] = F(p)
        self.b0 = tuple(vec)
        self.gamma = F(gamma)
        self.horizon = int(horizon)

    def with_reward(self, name, rew):
        w = World.__new__(World)
        w.__dict__.update(self.__dict__)
        w.name = name
        w.R = [[F(0)] * self.nS for _ in range(self.nA)]
        ai = dict((n, i) for i, n in enumerate(self.anames))
        si = dict((n, i) for i, n in enumerate(self.snames))
        for (s, a), v in sorted(rew.items()):
            w.R[ai[a]][si[s]] = F(v)
        return w

    def with_horizon(self, name, horizon):
        w = World.__new__(World)
        w.__dict__.update(self.__dict__)
        w.name = name
        w.horizon = int(horizon)
        return w

    def with_gamma(self, name, gamma):
        w = World.__new__(World)
        w.__dict__.update(self.__dict__)
        w.name = name
        w.gamma = F(gamma)
        return w

    def with_obs(self, name, onames, zobs):
        return World(name, self.snames, self.anames, onames,
                     self._trans_dict(), zobs, self._rew_dict(),
                     self._b0_dict(), self.gamma, self.horizon)

    def _trans_dict(self):
        out = {}
        for ia, a in enumerate(self.anames):
            for i, s in enumerate(self.snames):
                out[(s, a)] = dict((self.snames[j], self.T[ia][i][j])
                                   for j in range(self.nS)
                                   if self.T[ia][i][j])
        return out

    def _rew_dict(self):
        out = {}
        for ia, a in enumerate(self.anames):
            for i, s in enumerate(self.snames):
                out[(s, a)] = self.R[ia][i]
        return out

    def _b0_dict(self):
        return dict((self.snames[i], self.b0[i]) for i in range(self.nS)
                    if self.b0[i])

    def tables(self):
        """The EXPLICIT_GENERATIVE_MODEL stored object: T and Z only.  It
        carries no reward table, which is exactly why it survives a reward
        swap."""
        return {
            "T": dict(("%s|%s" % (self.snames[i], self.anames[ia]),
                       [fs(self.T[ia][i][j]) for j in range(self.nS)])
                      for ia in range(self.nA) for i in range(self.nS)),
            "Z": dict((self.snames[i], [fs(self.Z[i][o])
                                        for o in range(self.nO)])
                      for i in range(self.nS)),
        }


def build_worlds():
    """The registered roster.  |S| <= 4, |O| <= 3, |A| <= 3, gamma = 1/2,
    H = 3, exactly as PROSPECTIVE_REGISTER_V1.json fixes them."""
    half = F(1, 2)

    # K_REACTIVE_OPT -- a fully observed MDP (the observation map is the
    # identity).  The optimal action at s0 is NOT the myopically greedy one,
    # so the task is a genuine planning problem, yet a single memoryless
    # deterministic map O -> A attains the exact optimum.
    reactive_opt = World(
        "K_REACTIVE_OPT",
        ["s0", "s1"], ["a0", "a1"], ["o0", "o1"],
        {("s0", "a0"): {"s1": 1}, ("s0", "a1"): {"s0": 1},
         ("s1", "a0"): {"s1": 1}, ("s1", "a1"): {"s1": 1}},
        {"s0": {"o0": 1}, "s1": {"o1": 1}},
        {("s0", "a0"): F(0), ("s0", "a1"): F(1, 4),
         ("s1", "a0"): F(1), ("s1", "a1"): F(1)},
        {"s0": 1}, half, 3)

    # K_MODEL_NEEDED -- observation aliasing.  s0 and s1 both emit oa and
    # require different actions, so no memoryless map can be optimal; and the
    # branch taken out of s0 is a fair coin revealed only through the next
    # observation, so no open-loop replay can be optimal either.
    model_needed = World(
        "K_MODEL_NEEDED",
        ["s0", "s1", "sD", "sG"], ["a0", "a1", "a2"], ["oa", "ob", "oc"],
        {("s0", "a0"): {"s1": half, "sG": half},
         ("s0", "a1"): {"sD": 1}, ("s0", "a2"): {"sD": 1},
         ("s1", "a0"): {"sD": 1}, ("s1", "a1"): {"sD": 1},
         ("s1", "a2"): {"sD": 1},
         ("sG", "a0"): {"sD": 1}, ("sG", "a1"): {"sD": 1},
         ("sG", "a2"): {"sD": 1},
         ("sD", "a0"): {"sD": 1}, ("sD", "a1"): {"sD": 1},
         ("sD", "a2"): {"sD": 1}},
        {"s0": {"oa": 1}, "s1": {"oa": 1}, "sG": {"ob": 1}, "sD": {"oc": 1}},
        {("s1", "a1"): F(1), ("sG", "a2"): F(1)},
        {"s0": 1}, half, 3)

    # K_SWAP -- the reward-swap probe world.
    swap = World(
        "K_SWAP",
        ["s0", "sP", "sQ"], ["a0", "a1"], ["o0", "oP", "oQ"],
        {("s0", "a0"): {"sP": 1}, ("s0", "a1"): {"sQ": 1},
         ("sP", "a0"): {"sP": 1}, ("sP", "a1"): {"sP": 1},
         ("sQ", "a0"): {"sQ": 1}, ("sQ", "a1"): {"sQ": 1}},
        {"s0": {"o0": 1}, "sP": {"oP": 1}, "sQ": {"oQ": 1}},
        {("sP", "a0"): F(1), ("sP", "a1"): F(1)},
        {"s0": 1}, half, 3)
    swap_alt = swap.with_reward(
        "K_SWAP_R_ALT", {("sQ", "a0"): F(1), ("sQ", "a1"): F(1)})
    return reactive_opt, model_needed, swap, swap_alt


def phase_world(base, g):
    """K_PHASE[G]: the registered aliased world carrying G goal tokens, each
    worth exactly 1, all collected on the rewarding transition."""
    return base.with_reward("K_PHASE[%d]" % g,
                            {("s1", "a1"): F(g), ("sG", "a2"): F(g)})


# ---------------------------------------------------------------------------
# route A: model-based optimum by memoised backward recursion over beliefs
# ---------------------------------------------------------------------------
def _predict(W, b, a):
    pred = [F(0)] * W.nS
    row = W.T[a]
    for s in range(W.nS):
        if b[s]:
            tr = row[s]
            for sp in range(W.nS):
                if tr[sp]:
                    pred[sp] += b[s] * tr[sp]
    return pred


def opt_value(W, b=None, t=0, memo=None):
    """Exact optimal value of the belief b at step t under the registered
    horizon.  Memoised on (t, belief)."""
    if b is None:
        b = W.b0
    if memo is None:
        memo = {}
    if t >= W.horizon:
        return F(0)
    key = (t, b)
    if key in memo:
        return memo[key]
    best = None
    for a in range(W.nA):
        imm = F(0)
        for s in range(W.nS):
            if b[s] and W.R[a][s]:
                imm += b[s] * W.R[a][s]
        pred = _predict(W, b, a)
        fut = F(0)
        for o in range(W.nO):
            w = F(0)
            for sp in range(W.nS):
                if pred[sp] and W.Z[sp][o]:
                    w += pred[sp] * W.Z[sp][o]
            if w:
                nb = tuple(pred[sp] * W.Z[sp][o] / w for sp in range(W.nS))
                fut += w * opt_value(W, nb, t + 1, memo)
        v = imm + W.gamma * fut
        if best is None or v > best:
            best = v
    memo[key] = best
    return best


def opt_policy_action(W, b, t, memo=None):
    """The registered tie-break is lexicographic by action name, ascending."""
    if memo is None:
        memo = {}
    best_a = None
    best_v = None
    for a in range(W.nA):
        imm = F(0)
        for s in range(W.nS):
            if b[s] and W.R[a][s]:
                imm += b[s] * W.R[a][s]
        pred = _predict(W, b, a)
        fut = F(0)
        for o in range(W.nO):
            w = F(0)
            for sp in range(W.nS):
                if pred[sp] and W.Z[sp][o]:
                    w += pred[sp] * W.Z[sp][o]
            if w:
                nb = tuple(pred[sp] * W.Z[sp][o] / w for sp in range(W.nS))
                fut += w * opt_value(W, nb, t + 1, memo)
        v = imm + W.gamma * fut
        if best_v is None or v > best_v:
            best_v = v
            best_a = a
    return best_a


# ---------------------------------------------------------------------------
# route A: class values by forward state-distribution propagation
# ---------------------------------------------------------------------------
def eval_memoryless(W, pi, d0=None):
    """pi: tuple of action index per observation index."""
    d = list(W.b0 if d0 is None else d0)
    total = F(0)
    disc = F(1)
    for _ in range(W.horizon):
        nd = [F(0)] * W.nS
        for s in range(W.nS):
            if not d[s]:
                continue
            for o in range(W.nO):
                zp = W.Z[s][o]
                if not zp:
                    continue
                w = d[s] * zp
                a = pi[o]
                if W.R[a][s]:
                    total += disc * w * W.R[a][s]
                tr = W.T[a][s]
                for sp in range(W.nS):
                    if tr[sp]:
                        nd[sp] += w * tr[sp]
        d = nd
        disc *= W.gamma
    return total


def eval_open_loop(W, seq, d0=None):
    d = list(W.b0 if d0 is None else d0)
    total = F(0)
    disc = F(1)
    for t in range(W.horizon):
        a = seq[t]
        nd = [F(0)] * W.nS
        for s in range(W.nS):
            if not d[s]:
                continue
            if W.R[a][s]:
                total += disc * d[s] * W.R[a][s]
            tr = W.T[a][s]
            for sp in range(W.nS):
                if tr[sp]:
                    nd[sp] += d[s] * tr[sp]
        d = nd
        disc *= W.gamma
    return total


def all_memoryless(W):
    out = [()]
    for _ in range(W.nO):
        nxt = []
        for p in out:
            for a in range(W.nA):
                nxt.append(p + (a,))
        out = nxt
    return out


def all_sequences(W):
    out = [()]
    for _ in range(W.horizon):
        nxt = []
        for p in out:
            for a in range(W.nA):
                nxt.append(p + (a,))
        out = nxt
    return out


def best_memoryless(W):
    best_v = None
    best_pi = None
    for pi in all_memoryless(W):
        v = eval_memoryless(W, pi)
        if best_v is None or v > best_v or (v == best_v and pi < best_pi):
            best_v = v
            best_pi = pi
    return best_v, best_pi


def initial_observation_contexts(W):
    """The registered finite context set for CACHED_SKILL: the observation
    emitted by the initial state, with the exact conditional over states."""
    out = []
    for o in range(W.nO):
        w = F(0)
        for s in range(W.nS):
            if W.b0[s] and W.Z[s][o]:
                w += W.b0[s] * W.Z[s][o]
        if w:
            cond = tuple(W.b0[s] * W.Z[s][o] / w for s in range(W.nS))
            out.append((o, w, cond))
    return out


def best_cached_skill(W):
    """A cached skill maps the registered context to a fixed action sequence
    and replays it; it cannot re-plan."""
    total = F(0)
    table = {}
    for o, w, cond in initial_observation_contexts(W):
        bv = None
        bseq = None
        for seq in all_sequences(W):
            v = eval_open_loop(W, seq, cond)
            if bv is None or v > bv or (v == bv and seq < bseq):
                bv = v
                bseq = seq
        total += w * bv
        table[W.onames[o]] = [W.anames[a] for a in bseq]
    return total, table


# ---------------------------------------------------------------------------
# route A: VALUE_REPRESENTATION
# ---------------------------------------------------------------------------
def reference_conditional(W):
    """P_ref(s|o): the registered observation-level state estimate a
    representation with no belief tracking can hold.  It is the occupancy of
    the uniform-action exploration process over the registered horizon,
    conditioned on the observation.  It is computed from observation-level
    statistics only; T and Z are not exposed to the representation."""
    rho = [F(0)] * W.nS
    d = list(W.b0)
    inv = F(1, W.nA)
    for _ in range(W.horizon):
        for s in range(W.nS):
            rho[s] += d[s]
        nd = [F(0)] * W.nS
        for s in range(W.nS):
            if not d[s]:
                continue
            for a in range(W.nA):
                tr = W.T[a][s]
                for sp in range(W.nS):
                    if tr[sp]:
                        nd[sp] += d[s] * inv * tr[sp]
        d = nd
    tot = sum(rho)
    if tot:
        rho = [r / tot for r in rho]
    out = []
    for o in range(W.nO):
        w = F(0)
        for s in range(W.nS):
            if rho[s] and W.Z[s][o]:
                w += rho[s] * W.Z[s][o]
        if w:
            out.append(tuple(rho[s] * W.Z[s][o] / w for s in range(W.nS)))
        else:
            supp = [s for s in range(W.nS) if W.Z[s][o]]
            if not supp:
                supp = list(range(W.nS))
            out.append(tuple(F(1, len(supp)) if s in supp else F(0)
                             for s in range(W.nS)))
    return out


def lookahead_tables(W):
    """The registered one-step lookahead a VALUE_REPRESENTATION owns:
    rhat(o,a) and Phat(o'|o,a), both observation-level statistics.  rhat is
    reward-derived, so a reward swap makes it stale and it cannot be refreshed
    without further interaction."""
    pref = reference_conditional(W)
    rhat = [[F(0)] * W.nA for _ in range(W.nO)]
    phat = [[[F(0)] * W.nO for _ in range(W.nA)] for _ in range(W.nO)]
    for o in range(W.nO):
        for a in range(W.nA):
            acc = F(0)
            for s in range(W.nS):
                if pref[o][s] and W.R[a][s]:
                    acc += pref[o][s] * W.R[a][s]
            rhat[o][a] = acc
            for s in range(W.nS):
                if not pref[o][s]:
                    continue
                tr = W.T[a][s]
                for sp in range(W.nS):
                    if not tr[sp]:
                        continue
                    for op in range(W.nO):
                        if W.Z[sp][op]:
                            phat[o][a][op] += pref[o][s] * tr[sp] * W.Z[sp][op]
    return rhat, phat


def greedy_policy(W, V, rhat, phat):
    pi = []
    for o in range(W.nO):
        best_a = 0
        best_q = None
        for a in range(W.nA):
            q = rhat[o][a]
            for op in range(W.nO):
                if phat[o][a][op]:
                    q += W.gamma * phat[o][a][op] * V[op]
            if best_q is None or q > best_q:
                best_q = q
                best_a = a
        pi.append(best_a)
    return tuple(pi)


def value_grid(W):
    """The registered rational grid for V: quarters from 0 to the exact
    maximum attainable discounted return."""
    rmax = F(0)
    for a in range(W.nA):
        for s in range(W.nS):
            if W.R[a][s] > rmax:
                rmax = W.R[a][s]
    hi = F(0)
    disc = F(1)
    for _ in range(W.horizon):
        hi += disc * rmax
        disc *= W.gamma
    n = int(hi * 4)
    return [F(k, 4) for k in range(0, n + 1)] or [F(0)]


def realizable_greedy_policies(W):
    rhat, phat = lookahead_tables(W)
    grid = value_grid(W)
    combos = [()]
    for _ in range(W.nO):
        nxt = []
        for p in combos:
            for v in grid:
                nxt.append(p + (v,))
        combos = nxt
    seen = {}
    for V in combos:
        pi = greedy_policy(W, V, rhat, phat)
        if pi not in seen:
            seen[pi] = V
    return seen, rhat, phat


def lookahead_action_groups(W):
    """Actions whose one-step lookahead rows coincide are indistinguishable to
    EVERY value function, so the registered lexicographic tie-break fixes the
    chosen action there.  The product of the group counts is a grid-free upper
    bound on the number of memoryless maps VALUE_REPRESENTATION can realize."""
    rhat, phat = lookahead_tables(W)
    per_obs = []
    bound = 1
    for o in range(W.nO):
        keys = {}
        for a in range(W.nA):
            k = (rhat[o][a], tuple(phat[o][a]))
            keys.setdefault(k, []).append(a)
        per_obs.append(sorted([W.anames[a] for a in v]
                              for v in keys.values()))
        bound *= len(keys)
    return per_obs, bound


def best_value_representation(W):
    seen, rhat, phat = realizable_greedy_policies(W)
    best_v = None
    best_pi = None
    best_V = None
    for pi in sorted(seen):
        v = eval_memoryless(W, pi)
        if best_v is None or v > best_v:
            best_v = v
            best_pi = pi
            best_V = seen[pi]
    return best_v, best_pi, best_V, seen, rhat, phat


# ---------------------------------------------------------------------------
# route A: predictive state
# ---------------------------------------------------------------------------
def reachable_histories(W):
    """Every (observation, action) history reachable under SOME action
    sequence, with the exact conditional state distribution.  Action-
    independent reachability: the tree does not depend on the policy being
    evaluated."""
    out = []
    frontier = []
    for o in range(W.nO):
        w = F(0)
        for s in range(W.nS):
            if W.b0[s] and W.Z[s][o]:
                w += W.b0[s] * W.Z[s][o]
        if w:
            cond = tuple(W.b0[s] * W.Z[s][o] / w for s in range(W.nS))
            frontier.append(((o,), cond))
    for t in range(W.horizon):
        out.extend((h, b, t) for h, b in frontier)
        nxt = []
        for h, b in frontier:
            for a in range(W.nA):
                pred = _predict(W, b, a)
                for o in range(W.nO):
                    w = F(0)
                    for sp in range(W.nS):
                        if pred[sp] and W.Z[sp][o]:
                            w += pred[sp] * W.Z[sp][o]
                    if w:
                        nb = tuple(pred[sp] * W.Z[sp][o] / w
                                   for sp in range(W.nS))
                        nxt.append((h + (a, o), nb))
        frontier = nxt
    return out


def future_observation_joint(W, b, depth):
    """Exact distribution over future observation sequences of the given
    depth, under the registered uniform-action test policy.  The predictive
    state is this object; it never touches R."""
    cur = {(): (b, F(1))}
    inv = F(1, W.nA)
    for _ in range(depth):
        nxt = {}
        for seq, (bb, p) in sorted(cur.items()):
            mix = [F(0)] * W.nS
            for a in range(W.nA):
                pred = _predict(W, bb, a)
                for sp in range(W.nS):
                    if pred[sp]:
                        mix[sp] += inv * pred[sp]
            for o in range(W.nO):
                w = F(0)
                for sp in range(W.nS):
                    if mix[sp] and W.Z[sp][o]:
                        w += mix[sp] * W.Z[sp][o]
                if w:
                    nb = tuple(mix[sp] * W.Z[sp][o] / w for sp in range(W.nS))
                    key = seq + (o,)
                    if key in nxt:
                        ob, op = nxt[key]
                        nxt[key] = (nb, op + p * w)
                    else:
                        nxt[key] = (nb, p * w)
        cur = nxt
    return dict((tuple(W.onames[o] for o in seq), pr)
                for seq, (_, pr) in sorted(cur.items()))


def predictive_state(W, b, depth):
    j = future_observation_joint(W, b, depth)
    return tuple(sorted((k, fs(v)) for k, v in j.items()))


def eval_history_policy(W, fn):
    """Exact value of an arbitrary history-dependent deterministic policy.
    fn(history, t) -> action index."""
    total = F(0)
    frontier = []
    for o in range(W.nO):
        w = F(0)
        for s in range(W.nS):
            if W.b0[s] and W.Z[s][o]:
                w += W.b0[s] * W.Z[s][o]
        if w:
            cond = tuple(W.b0[s] * W.Z[s][o] / w for s in range(W.nS))
            frontier.append(((o,), cond, w))
    disc = F(1)
    for t in range(W.horizon):
        nxt = []
        for h, b, w in frontier:
            a = fn(h, t)
            imm = F(0)
            for s in range(W.nS):
                if b[s] and W.R[a][s]:
                    imm += b[s] * W.R[a][s]
            if imm:
                total += disc * w * imm
            pred = _predict(W, b, a)
            for o in range(W.nO):
                ww = F(0)
                for sp in range(W.nS):
                    if pred[sp] and W.Z[sp][o]:
                        ww += pred[sp] * W.Z[sp][o]
                if ww:
                    nb = tuple(pred[sp] * W.Z[sp][o] / ww
                               for sp in range(W.nS))
                    nxt.append((h + (a, o), nb, w * ww))
        frontier = nxt
        disc *= W.gamma
    return total


def best_one_step_memory(W):
    """The explicitly RELAXED class used as a falsifying witness: a policy
    that may read ONE step of history (the previous observation) in addition
    to the current one.  Outside the registered REACTIVE_POLICY interface."""
    readouts = sorted(set((h[-3] if len(h) >= 3 else -1, h[-1])
                          for h, _b, _t in reachable_histories(W)))
    idx = dict((r, i) for i, r in enumerate(readouts))
    best = None
    best_tab = None
    total = W.nA ** len(readouts)
    for code in range(total):
        tab = []
        c = code
        for _ in range(len(readouts)):
            tab.append(c % W.nA)
            c //= W.nA
        tab = tuple(tab)

        def fn(h, t, _tab=tab):
            return _tab[idx[(h[-3] if len(h) >= 3 else -1, h[-1])]]

        v = eval_history_policy(W, fn)
        if best is None or v > best:
            best = v
            best_tab = tab
    return best, dict(("%s|%s" % ("-" if r[0] < 0 else W.onames[r[0]],
                                  W.onames[r[1]]), W.anames[best_tab[i]])
                      for i, r in enumerate(readouts))


def readout(cls, W, h, t):
    """What the representation of the given class exposes at a history."""
    if cls == "REACTIVE_POLICY" or cls == "VALUE_REPRESENTATION":
        return ("obs", W.onames[h[-1]])
    if cls == "CACHED_SKILL":
        return ("context_time", W.onames[h[0]], t)
    if cls == "PREDICTIVE_STATE":
        return ("predictive_state", h)
    return ("belief", h)


# ---------------------------------------------------------------------------
# structural causal models (row 5)
# ---------------------------------------------------------------------------
class SCM(object):
    def __init__(self, name, latent_name, latents, probs, edges, fx, fy):
        self.name = name
        self.latent_name = latent_name
        self.latents = list(latents)
        self.probs = dict((k, F(v)) for k, v in sorted(probs.items()))
        self.edges = sorted(edges)
        self.fx = fx
        self.fy = fy

    def observational(self):
        j = {}
        for u in self.latents:
            x = self.fx(u)
            y = self.fy(u, x)
            j[(x, y)] = j.get((x, y), F(0)) + self.probs[u]
        return dict(sorted(j.items()))

    def do_x(self, c):
        j = {}
        for u in self.latents:
            y = self.fy(u, c)
            j[y] = j.get(y, F(0)) + self.probs[u]
        return dict(sorted(j.items()))

    def relabel(self, mapping):
        inv = dict((v, k) for k, v in mapping.items())
        return SCM(self.name + "_RELABELLED", self.latent_name,
                   [mapping[u] for u in self.latents],
                   dict((mapping[u], self.probs[u]) for u in self.latents),
                   self.edges,
                   lambda u, _f=self.fx, _i=inv: _f(_i[u]),
                   lambda u, x, _f=self.fy, _i=inv: _f(_i[u], x))

    def stored(self):
        return {
            "latent_symbol": self.latent_name,
            "latent_support": sorted(self.latents),
            "latent_cardinality": len(self.latents),
            "latent_probabilities": dict((k, fs(v))
                                         for k, v in self.probs.items()),
            "edges": ["%s->%s" % (a, b) for a, b in self.edges],
        }


def observable_profile(M):
    """Every observational and predictive joint the model induces."""
    joint = M.observational()
    px = {}
    py = {}
    for (x, y), p in sorted(joint.items()):
        px[x] = px.get(x, F(0)) + p
        py[y] = py.get(y, F(0)) + p
    cond_y_given_x = {}
    for (x, y), p in sorted(joint.items()):
        if px[x]:
            cond_y_given_x["%s|%s" % (y, x)] = p / px[x]
    cond_x_given_y = {}
    for (x, y), p in sorted(joint.items()):
        if py[y]:
            cond_x_given_y["%s|%s" % (x, y)] = p / py[y]
    return {
        "joint_XY": dict(("%s,%s" % k, fs(v)) for k, v in sorted(joint.items())),
        "marginal_X": dict((k, fs(v)) for k, v in sorted(px.items())),
        "marginal_Y": dict((k, fs(v)) for k, v in sorted(py.items())),
        "predictive_Y_given_X": dict((k, fs(v)) for k, v
                                     in sorted(cond_y_given_x.items())),
        "predictive_X_given_Y": dict((k, fs(v)) for k, v
                                     in sorted(cond_x_given_y.items())),
    }


def interventional_profile(M, values):
    out = {}
    for c in values:
        d = M.do_x(c)
        out["do_X=%s" % c] = dict((k, fs(v)) for k, v in sorted(d.items()))
    return out


def behaviour_differs(M1, M2):
    """The registered identifiability checker: it compares OBSERVABLE
    behaviour only.  A pure relabelling of a latent must leave it silent."""
    return observable_profile(M1) != observable_profile(M2)


def build_scms():
    a = SCM("SCM_LATENT_A", "U", ["u0", "u1"],
            {"u0": F(1, 2), "u1": F(1, 2)},
            [("U", "X"), ("U", "Y")],
            lambda u: "x0" if u == "u0" else "x1",
            lambda u, x: "y0" if u == "u0" else "y1")
    b = SCM("SCM_LATENT_B", "V", ["v0", "v1", "v2", "v3"],
            {"v0": F(1, 4), "v1": F(1, 4), "v2": F(1, 4), "v3": F(1, 4)},
            [("V", "X"), ("X", "Y")],
            lambda u: "x0" if u in ("v0", "v2") else "x1",
            lambda u, x: "y0" if x == "x0" else "y1")
    ident = SCM("SCM_LATENT_ID", "L", ["l0", "l1", "l2"],
                {"l0": F(1, 3), "l1": F(1, 3), "l2": F(1, 3)},
                [("L", "X"), ("L", "Y")],
                lambda u: {"l0": "x0", "l1": "x1", "l2": "x2"}[u],
                lambda u, x: {"l0": "y0", "l1": "y1", "l2": "y2"}[u])
    return a, b, ident


def permutations_of(items):
    if not items:
        return [()]
    out = []
    for i, it in enumerate(items):
        for rest in permutations_of(items[:i] + items[i + 1:]):
            out.append((it,) + rest)
    return out


# ---------------------------------------------------------------------------
# registered exact-rational sampler (the null)
# ---------------------------------------------------------------------------
class LCG(object):
    """Seeded from the register's own self_digest_sha256, so the sampler is a
    registered constant and no seed is invented after the fact."""

    MOD = 1 << 64
    MUL = 6364136223846793005
    INC = 1442695040888963407

    def __init__(self, digest_hex):
        self.x = int(digest_hex[:16], 16) % self.MOD

    def next_int(self, n):
        self.x = (self.MUL * self.x + self.INC) % self.MOD
        return (self.x >> 33) % n


def random_world(rng, name):
    snames = ["s0", "s1", "s2", "s3"]
    anames = ["a0", "a1", "a2"]
    onames = ["oa", "ob", "oc"]
    trans = {}
    for s in snames:
        for a in anames:
            counts = [0, 0, 0, 0]
            for _ in range(8):
                counts[rng.next_int(4)] += 1
            trans[(s, a)] = dict((snames[i], F(counts[i], 8))
                                 for i in range(4) if counts[i])
    zobs = dict((s, {onames[rng.next_int(3)]: 1}) for s in snames)
    rew = {}
    for s in snames:
        for a in anames:
            rew[(s, a)] = F(rng.next_int(5), 4)
    return World(name, snames, anames, onames, trans, zobs, rew,
                 {"s0": 1}, F(1, 2), 3)


def optimal_action_conflict(W):
    """True when two reachable histories carry the SAME current observation
    but the model-based optimal policy takes different actions there -- the
    structural reason a memoryless map cannot be optimal."""
    memo = {}
    seen = {}
    for h, b, t in reachable_histories(W):
        a = opt_policy_action(W, b, t, memo)
        o = h[-1]
        if o in seen and seen[o] != a:
            return True
        seen[o] = a
    return False


def necessity_gap(W):
    vmb = opt_value(W)
    vr, _ = best_memoryless(W)
    vc, _ = best_cached_skill(W)
    vmf = vr if vr >= vc else vc
    return vmb - vmf, vmb, vmf


# ---------------------------------------------------------------------------
# class enumeration helpers used by the interface coordinates
# ---------------------------------------------------------------------------
def cached_members(W):
    ctxs = [o for o, _w, _c in initial_observation_contexts(W)]
    combos = [{}]
    for o in ctxs:
        nxt = []
        for p in combos:
            for seq in all_sequences(W):
                q = dict(p)
                q[o] = seq
                nxt.append(q)
        combos = nxt
    return combos


def class_behaviours(W, cls):
    hs = reachable_histories(W)
    out = []
    if cls == "REACTIVE_POLICY":
        for pi in all_memoryless(W):
            out.append((pi, dict((h, pi[h[-1]]) for h, _b, _t in hs)))
    elif cls == "VALUE_REPRESENTATION":
        seen, _r, _p = realizable_greedy_policies(W)
        for pi in sorted(seen):
            out.append((pi, dict((h, pi[h[-1]]) for h, _b, _t in hs)))
    elif cls == "CACHED_SKILL":
        for tab in cached_members(W):
            out.append((tuple(sorted((k, v) for k, v in tab.items())),
                        dict((h, tab[h[0]][t]) for h, _b, t in hs)))
    elif cls == "EXPLICIT_GENERATIVE_MODEL":
        memo = {}
        out.append(("optimal_under_R",
                    dict((h, opt_policy_action(W, b, t, memo))
                         for h, b, t in hs)))
    return out


def coord_c2(W, cls):
    hs = reachable_histories(W)
    for _lab, beh in class_behaviours(W, cls):
        for h1, _b1, t1 in hs:
            for h2, _b2, t2 in hs:
                if t1 == t2 and h1[-1] != h2[-1] and beh[h1] != beh[h2]:
                    return True
    return False


def coord_c3(W, cls):
    hs = reachable_histories(W)
    for _lab, beh in class_behaviours(W, cls):
        for h1, _b1, t1 in hs:
            for h2, _b2, t2 in hs:
                if t1 != t2 and h1[-1] == h2[-1] and beh[h1] != beh[h2]:
                    return True
    return False


def coord_c7(W, cls):
    hs = reachable_histories(W)
    targets = {}
    for pi in all_memoryless(W):
        targets[pi] = dict((h, pi[h[-1]]) for h, _b, _t in hs)
    realized = 0
    behs = [beh for _lab, beh in class_behaviours(W, cls)]
    for pi in sorted(targets):
        if any(beh == targets[pi] for beh in behs):
            realized += 1
    return realized, len(targets)


PRED_DEPTH = 2


def coord_c4(worlds, cls):
    """Equal readout must imply an equal exact future-observation joint."""
    for W in worlds:
        seen = {}
        for h, b, t in reachable_histories(W):
            key = readout(cls, W, h, t)
            if cls == "PREDICTIVE_STATE":
                key = ("predictive_state", predictive_state(W, b, PRED_DEPTH))
            elif cls == "EXPLICIT_GENERATIVE_MODEL":
                key = ("belief", b)
            ps = predictive_state(W, b, PRED_DEPTH)
            if key in seen and seen[key] != ps:
                return False, W.name
            seen[key] = ps
    return True, "REGISTERED_ROSTER"


def stored_object(cls, W):
    if cls == "REACTIVE_POLICY":
        _v, pi = best_memoryless(W)
        return ({}, {"policy": dict((W.onames[o], W.anames[pi[o]])
                                    for o in range(W.nO))})
    if cls == "CACHED_SKILL":
        _v, tab = best_cached_skill(W)
        return ({}, {"skill": tab})
    if cls == "VALUE_REPRESENTATION":
        _v, _pi, V, _seen, rhat, _phat = best_value_representation(W)
        return ({"V": dict((W.onames[o], fs(V[o])) for o in range(W.nO)),
                 "rhat": dict(("%s|%s" % (W.onames[o], W.anames[a]),
                               fs(rhat[o][a]))
                              for o in range(W.nO) for a in range(W.nA))}, {})
    if cls == "PREDICTIVE_STATE":
        return ({"predictive_state_at_b0":
                 [list(k) + [v] for k, v in
                  predictive_state(W, W.b0, PRED_DEPTH)]}, {})
    return (W.tables(), {})


def best_cached_skill_idx(W):
    total = F(0)
    table = {}
    for o, w, cond in initial_observation_contexts(W):
        bv = None
        bseq = None
        for seq in all_sequences(W):
            v = eval_open_loop(W, seq, cond)
            if bv is None or v > bv or (v == bv and seq < bseq):
                bv = v
                bseq = seq
        total += w * bv
        table[o] = bseq
    return total, table


def eval_cached_table(W, table):
    total = F(0)
    for o, w, cond in initial_observation_contexts(W):
        if o in table:
            total += w * eval_open_loop(W, table[o], cond)
    return total


def reward_swap_probe(swap, swap_alt):
    """The registered probe: R is replaced by R_ALT and each representation is
    re-queried with NO further interaction."""
    out = {}

    piR = best_memoryless(swap)[1]
    out["REACTIVE_POLICY"] = {
        "value_under_R": fs(eval_memoryless(swap, piR)),
        "value_after_probe": eval_memoryless(swap_alt, piR),
        "class_best_under_R_ALT": best_memoryless(swap_alt)[0],
    }

    _v, tabR = best_cached_skill_idx(swap)
    out["CACHED_SKILL"] = {
        "value_under_R": fs(eval_cached_table(swap, tabR)),
        "value_after_probe": eval_cached_table(swap_alt, tabR),
        "class_best_under_R_ALT": best_cached_skill_idx(swap_alt)[0],
    }

    vR, piV, VR, _seen, rhatR, phatR = best_value_representation(swap)
    stale = greedy_policy(swap, VR, rhatR, phatR)
    out["VALUE_REPRESENTATION"] = {
        "value_under_R": fs(vR),
        "value_after_probe": eval_memoryless(swap_alt, stale),
        "class_best_under_R_ALT": best_value_representation(swap_alt)[0],
        "stale_greedy_policy_equals_fitted": stale == piV,
    }

    out["PREDICTIVE_STATE"] = {
        "value_under_R": None,
        "value_after_probe": None,
        "class_best_under_R_ALT": None,
        "predictive_state_invariant_under_reward_swap":
            predictive_state(swap, swap.b0, PRED_DEPTH)
            == predictive_state(swap_alt, swap_alt.b0, PRED_DEPTH),
    }

    out["EXPLICIT_GENERATIVE_MODEL"] = {
        "value_under_R": fs(opt_value(swap)),
        "value_after_probe": opt_value(swap_alt),
        "class_best_under_R_ALT": opt_value(swap_alt),
    }

    for cls in sorted(out):
        rec = out[cls]
        va = rec["value_after_probe"]
        cb = rec["class_best_under_R_ALT"]
        if va is None or cb is None:
            rec["shortfall"] = None
            rec["reoptimizes_under_probe"] = False
        else:
            rec["shortfall"] = fs(cb - va)
            rec["reoptimizes_under_probe"] = (va == cb)
            rec["value_after_probe"] = fs(va)
            rec["class_best_under_R_ALT"] = fs(cb)
    return out


def chosen_class_at(vmb, vmf, cost, mf_name):
    lhs = vmb - cost
    if lhs > vmf:
        return "EXPLICIT_GENERATIVE_MODEL"
    if lhs < vmf:
        return mf_name
    return min("EXPLICIT_GENERATIVE_MODEL", mf_name)


GUARD_TOKENS = ("forbidden", "not claimed", "never claimed", "refus",
                "must not", "no artifact", "never asserts")

SCANNED_FILES = [
    "AE15_THEOREMS_V1.md",
    "CORE.md",
    "FREEZE_V1.md",
    "ISSUE_833_RECONCILIATION_AE15_WORLD_MODEL_NECESSITY_V1.json",
    "MANIFEST_V1.json",
    "PARENT_OWNERSHIP_V1.md",
    "PROSPECTIVE_REGISTER_V1.json",
    "ae15_world_model_necessity_v1.py",
    "independent_world_model_oracle_v1.py",
    "test_ae15_world_model_necessity_v1.py",
]


def _json_offenders(obj, fn, path):
    bad = []
    if isinstance(obj, dict):
        for k in sorted(obj):
            bad.extend(_json_offenders(obj[k], fn, path + [str(k)]))
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, str) and item in FORBIDDEN_PROMOTIONS:
                if not (path and "forbidden_promotion" in path[-1]):
                    bad.append("%s:%s:%s" % (fn, "/".join(path), item))
            else:
                bad.extend(_json_offenders(item, fn, path))
    elif isinstance(obj, str):
        low = obj.lower()
        guarded = any(g in low for g in GUARD_TOKENS)
        for term in FORBIDDEN_PROMOTIONS:
            if obj == term:
                if not (path and "forbidden_promotion" in path[-1]):
                    bad.append("%s:%s:%s" % (fn, "/".join(path), term))
            elif term.lower() in low and not guarded:
                bad.append("%s:%s:%s" % (fn, "/".join(path), term))
    return bad


def _text_offenders(text, fn):
    bad = []
    lines = text.split("\n")
    blocks = []
    heading = ""
    cur = []
    for ln in lines:
        if fn.endswith(".md") and ln.startswith("#"):
            if cur:
                blocks.append((heading, cur))
                cur = []
            heading = ln
            continue
        if ln.strip() == "":
            if cur:
                blocks.append((heading, cur))
                cur = []
            continue
        cur.append(ln)
    if cur:
        blocks.append((heading, cur))
    for head, blk in blocks:
        joined = (head + "\n" + "\n".join(blk)).lower()
        guarded = any(g in joined for g in GUARD_TOKENS)
        for term in FORBIDDEN_PROMOTIONS:
            if term.lower() in joined and not guarded:
                bad.append("%s:%s" % (fn, term))
    return sorted(set(bad))


def scan_forbidden_assertions():
    """No artifact of this package asserts a forbidden promotion.  A
    declaration inside a forbidden-promotion list is not an assertion."""
    bad = []
    for fn in SCANNED_FILES:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        fh = open(p)
        try:
            text = fh.read()
        finally:
            fh.close()
        if fn.endswith(".json"):
            bad.extend(_json_offenders(json.loads(text), fn, []))
        else:
            bad.extend(_text_offenders(text, fn))
    return sorted(set(bad))


def load_register():
    p = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
    fh = open(p)
    try:
        reg = json.loads(fh.read())
    finally:
        fh.close()
    core = dict(reg)
    core.pop("self_digest_sha256", None)
    core.pop("self_digest_note", None)
    digest = hashlib.sha256(json.dumps(
        core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if digest != reg.get("self_digest_sha256"):
        raise SystemExit("register digest mismatch: refusing to emit")
    return reg, digest


# ---------------------------------------------------------------------------
# the receipt
# ---------------------------------------------------------------------------
def build():
    reg, digest = load_register()
    rc = reg["registered_constants"]

    reactive_opt, model_needed, swap, swap_alt = build_worlds()
    phases = [(g, phase_world(model_needed, g)) for g in (1, 2, 3, 4)]
    roster = [reactive_opt, model_needed, swap]

    res = {}

    res["custody"] = {
        "freeze_commit": FREEZE_COMMIT,
        "register_commit": REGISTER_COMMIT,
        "register_digest_recomputed": digest,
        "register_digest_matches": digest == reg["self_digest_sha256"],
        "register_declared_freeze_commit": reg["freeze_commit"],
        "register_declared_freeze_commit_equals_lane_owner_sha":
            reg["freeze_commit"] == FREEZE_COMMIT,
        "note": ("the register is binding and is never edited; its declared "
                 "freeze sha is compared with the lane owner's custody sha "
                 "rather than assumed, and the digest is recomputed from the "
                 "register's own canonical serialization before any value is "
                 "emitted"),
    }

    res["registered_scope"] = {
        "gamma": rc["gamma"],
        "horizon": rc["horizon"],
        "max_states": rc["max_states"],
        "max_obs": rc["max_obs"],
        "max_actions": rc["max_actions"],
        "null_trials": rc["null_trials"],
        "tie_break": rc["tie_break"],
        "phase_family": rc["phase_family"],
        "reward_swap_probe": rc["reward_swap_probe"],
        "worlds": dict((W.name, {"states": W.snames, "actions": W.anames,
                                 "observations": W.onames,
                                 "gamma": fs(W.gamma),
                                 "horizon": W.horizon})
                       for W in roster),
        "scope_respected": all(W.nS <= rc["max_states"]
                               and W.nO <= rc["max_obs"]
                               and W.nA <= rc["max_actions"]
                               and W.horizon == rc["horizon"]
                               and W.gamma == F(rc["gamma"])
                               for W in roster),
    }

    # ---- row 1: five interfaces, computed coordinates, distinctness --------
    vectors = {}
    realized = {}
    for cls in CLASSES:
        c1 = bool(class_behaviours(reactive_opt, cls))
        c2 = coord_c2(model_needed, cls)
        c3 = coord_c3(model_needed, cls)
        c4, _wt = coord_c4(roster, cls)
        numR = stored_object(cls, swap)[0]
        numA = stored_object(cls, swap_alt)[0]
        c5 = bool(numR) and numR != numA
        r, tot = coord_c7(model_needed, cls)
        realized[cls] = r
        vectors[cls] = {
            COORDS[0]: c1, COORDS[1]: c2, COORDS[2]: c3, COORDS[3]: c4,
            COORDS[4]: c5, COORDS[5]: False, COORDS[6]: (r == tot),
        }
    probe = reward_swap_probe(swap, swap_alt)
    for cls in CLASSES:
        vectors[cls][COORDS[5]] = bool(probe[cls]["reoptimizes_under_probe"])

    witness_task = {
        COORDS[0]: "K_REACTIVE_OPT", COORDS[1]: "K_MODEL_NEEDED",
        COORDS[2]: "K_MODEL_NEEDED", COORDS[3]: "REGISTERED_ROSTER",
        COORDS[4]: "K_SWAP", COORDS[5]: "K_SWAP",
        COORDS[6]: "K_MODEL_NEEDED",
    }
    table = []
    strict = 0
    dominated = 0
    for c1n in CLASSES:
        for c2n in CLASSES:
            if c1n == c2n:
                continue
            coord = None
            for cd in COORDS:
                if vectors[c1n][cd] and not vectors[c2n][cd]:
                    coord = cd
                    break
            if coord is not None:
                strict += 1
                table.append({"from": c1n, "to": c2n,
                              "separating_coordinate": coord,
                              "witness_task": witness_task[coord],
                              "direction": "from_strictly_above_to",
                              "dominated": False})
            else:
                rev = None
                for cd in COORDS:
                    if vectors[c2n][cd] and not vectors[c1n][cd]:
                        rev = cd
                        break
                dominated += 1
                table.append({"from": c1n, "to": c2n,
                              "separating_coordinate": rev,
                              "witness_task": witness_task[rev],
                              "direction": "to_strictly_above_from",
                              "dominated": True})
    unordered_ok = True
    for i, a in enumerate(CLASSES):
        for b in CLASSES[i + 1:]:
            if vectors[a] == vectors[b]:
                unordered_ok = False

    res["interfaces"] = {
        "classes": CLASSES,
        "coordinates": COORDS,
        "coordinate_basis": dict((c, "computed") for c in COORDS),
        "vectors": vectors,
        "memoryless_action_maps_realized": realized,
        "memoryless_action_maps_total": len(all_memoryless(model_needed)),
        "pairwise_distinctness": table,
        "ordered_pairs_total": len(table),
        "ordered_pairs_strict": strict,
        "ordered_pairs_dominated": dominated,
        "every_unordered_pair_separated": unordered_ok,
        "predictive_state_resolves_the_aliased_pair":
            predictive_state(model_needed, model_needed.b0, PRED_DEPTH)
            != predictive_state(
                model_needed,
                tuple(F(1) if s == 1 else F(0)
                      for s in range(model_needed.nS)), PRED_DEPTH),
    }
    res["reward_swap_probe"] = probe
    res["reward_swap_probe_summary"] = {
        "reoptimizing_classes": sorted(
            c for c in CLASSES if probe[c]["reoptimizes_under_probe"]),
        "explicit_generative_model_alone": sorted(
            c for c in CLASSES
            if probe[c]["reoptimizes_under_probe"]
        ) == ["EXPLICIT_GENERATIVE_MODEL"],
    }

    # ---- row 2 -------------------------------------------------------------
    v_ro = opt_value(reactive_opt)
    br_ro, pi_ro = best_memoryless(reactive_opt)
    res["reactive_optimal_task"] = {
        "task": "K_REACTIVE_OPT",
        "observation_map_is_identity": all(
            sum(1 for o in range(reactive_opt.nO) if reactive_opt.Z[s][o]) == 1
            for s in range(reactive_opt.nS)
        ) and reactive_opt.nS == reactive_opt.nO,
        "model_based_optimum": fs(v_ro),
        "best_reactive_value": fs(br_ro),
        "gap": fs(v_ro - br_ro),
        "attaining_reactive_policy": dict(
            (reactive_opt.onames[o], reactive_opt.anames[pi_ro[o]])
            for o in range(reactive_opt.nO)),
        "reactive_policies_enumerated": len(all_memoryless(reactive_opt)),
        "myopically_greedy_action_at_s0_is_not_optimal":
            reactive_opt.anames[pi_ro[0]] != "a1",
        "value_of_myopically_greedy_reactive_policy":
            fs(eval_memoryless(reactive_opt, (1, 1))),
    }

    # ---- row 3 -------------------------------------------------------------
    v_mn = opt_value(model_needed)
    br_mn, pi_mn = best_memoryless(model_needed)
    bc_mn, tab_mn = best_cached_skill(model_needed)
    bv_mn, pi_v, V_v, seen_v, _rh, _ph = best_value_representation(model_needed)
    res["model_needed_task"] = {
        "task": "K_MODEL_NEEDED",
        "aliased_observation": "oa",
        "aliased_states": ["s0", "s1"],
        "model_based_optimum": fs(v_mn),
        "best_value_by_class": {
            "REACTIVE_POLICY": fs(br_mn),
            "CACHED_SKILL": fs(bc_mn),
            "VALUE_REPRESENTATION": fs(bv_mn),
        },
        "gap_by_class": {
            "REACTIVE_POLICY": fs(v_mn - br_mn),
            "CACHED_SKILL": fs(v_mn - bc_mn),
            "VALUE_REPRESENTATION": fs(v_mn - bv_mn),
        },
        "gap": fs(v_mn - max(br_mn, bc_mn, bv_mn)),
        "all_strictly_suboptimal": (br_mn < v_mn and bc_mn < v_mn
                                    and bv_mn < v_mn),
        "class_sizes_enumerated": {
            "REACTIVE_POLICY": len(all_memoryless(model_needed)),
            "CACHED_SKILL": len(cached_members(model_needed)),
            "VALUE_REPRESENTATION_realizable_greedy_policies": len(seen_v),
        },
        "value_representation_lookahead_action_groups":
            lookahead_action_groups(model_needed)[0],
        "value_representation_structural_upper_bound_on_realizable_maps":
            lookahead_action_groups(model_needed)[1],
        "value_representation_upper_bound_is_memoryless_best": fs(br_mn),
        "value_representation_best_equals_upper_bound": bv_mn == br_mn,
        "value_representation_suboptimal_for_any_memoryless_lookahead":
            br_mn < v_mn,
        "attaining_reactive_policy": dict(
            (model_needed.onames[o], model_needed.anames[pi_mn[o]])
            for o in range(model_needed.nO)),
        "attaining_cached_skill": tab_mn,
        "attaining_value_function": dict(
            (model_needed.onames[o], fs(V_v[o]))
            for o in range(model_needed.nO)),
        "optimal_history_dependent_actions": dict(
            ("|".join(model_needed.onames[x] if i % 2 == 0
                      else model_needed.anames[x]
                      for i, x in enumerate(h)),
             model_needed.anames[opt_policy_action(model_needed, b, t)])
            for h, b, t in reachable_histories(model_needed)),
    }

    # ---- row 4: the phase boundary ----------------------------------------
    delta = F(1, 8)
    rows = []
    cstars = []
    for g, W in phases:
        vmb = opt_value(W)
        vr = best_memoryless(W)[0]
        vc = best_cached_skill(W)[0]
        vv = best_value_representation(W)[0]
        vmf = max(vr, vc, vv)
        attaining = sorted(n for n, v in (("REACTIVE_POLICY", vr),
                                          ("CACHED_SKILL", vc),
                                          ("VALUE_REPRESENTATION", vv))
                           if v == vmf)
        mf_name = attaining[0]
        cstar = vmb - vmf
        cstars.append(cstar)
        rows.append({
            "G": g,
            "V_mb": fs(vmb),
            "V_mf": fs(vmf),
            "V_mf_attaining_classes": attaining,
            "c_star": fs(cstar),
            "closed_form_c_star": fs(F(g, 4)),
            "closed_form_matches": cstar == F(g, 4),
            "chosen_below": chosen_class_at(vmb, vmf, cstar - delta, mf_name),
            "chosen_at": chosen_class_at(vmb, vmf, cstar, mf_name),
            "chosen_above": chosen_class_at(vmb, vmf, cstar + delta, mf_name),
            "margin_below": fs((vmb - (cstar - delta)) - vmf),
            "margin_at": fs((vmb - cstar) - vmf),
            "margin_above": fs((vmb - (cstar + delta)) - vmf),
            "advantage_per_goal_token": fs(cstar / g),
        })
    strictly_increasing = all(cstars[i] < cstars[i + 1]
                              for i in range(len(cstars) - 1))
    flips = all(r["chosen_below"] == "EXPLICIT_GENERATIVE_MODEL"
                and r["chosen_above"] != "EXPLICIT_GENERATIVE_MODEL"
                for r in rows)
    res["phase_boundary"] = {
        "family": "K_PHASE[G], G in {1,2,3,4}, G goal tokens each worth 1",
        "probe_offset": fs(delta),
        "identity": ("D(c) = (V_mb(G) - c) - V_mf(G) = c*(G) - c, exactly "
                     "linear in c with slope -1"),
        "rows": rows,
        "all_exact_rational": True,
        "strictly_increasing_in_G": strictly_increasing,
        "flips_strictly_on_both_sides": flips,
        "tie_at_c_star_broken_lexicographically": [r["chosen_at"]
                                                   for r in rows],
        "linear_by_construction_disclosure": (
            "the registered family scales one goal token linearly, so the "
            "registered range does not separate linear from nonlinear growth "
            "of the boundary"),
    }

    # ---- row 5: identifiability -------------------------------------------
    scm_a, scm_b, scm_id = build_scms()
    prof_a = observable_profile(scm_a)
    prof_b = observable_profile(scm_b)
    do_a = interventional_profile(scm_a, ["x0", "x1"])
    do_b = interventional_profile(scm_b, ["x0", "x1"])
    relabel_map = {"v0": "w3", "v1": "w2", "v2": "w1", "v3": "w0"}
    scm_b_rel = scm_b.relabel(relabel_map)
    recovery = dict((scm_id.fx(u), u) for u in scm_id.latents)
    recovery_exact = all(recovery[scm_id.fx(u)] == u for u in scm_id.latents)
    perms = permutations_of(list(scm_id.latents))
    relabel_recoveries = []
    for p in perms:
        m = dict(zip(scm_id.latents, p))
        M = scm_id.relabel(m)
        rec = dict((M.fx(u), u) for u in M.latents)
        relabel_recoveries.append({
            "permutation": ["%s->%s" % (k, m[k]) for k in sorted(m)],
            "observable_profile_unchanged":
                observable_profile(M) == observable_profile(scm_id),
            "recovered_exactly": all(rec[M.fx(u)] == u for u in M.latents),
        })
    res["identifiability"] = {
        "pair": ["SCM_LATENT_A", "SCM_LATENT_B"],
        "SCM_LATENT_A": scm_a.stored(),
        "SCM_LATENT_B": scm_b.stored(),
        "observable_profile_A": prof_a,
        "observable_profile_B": prof_b,
        "observational_and_predictive_joints_identical": prof_a == prof_b,
        "latent_factorizations_differ": (
            scm_a.edges != scm_b.edges
            or len(scm_a.latents) != len(scm_b.latents)),
        "latent_cardinalities": [len(scm_a.latents), len(scm_b.latents)],
        "interventional_profile_A": do_a,
        "interventional_profile_B": do_b,
        "interventionally_distinguishable": do_a != do_b,
        "SCM_LATENT_ID": scm_id.stored(),
        "recovery_map": dict((k, recovery[k]) for k in sorted(recovery)),
        "latent_recovered_exactly": recovery_exact,
        "relabelling_permutations_checked": len(perms),
        "relabelling_recovery": relabel_recoveries,
        "recovered_up_to_relabelling": all(
            r["observable_profile_unchanged"] and r["recovered_exactly"]
            for r in relabel_recoveries),
        "relabelled_B_object_changed":
            scm_b.stored() != scm_b_rel.stored(),
        "relabelled_B_flagged_by_checker":
            behaviour_differs(scm_b, scm_b_rel),
    }

    # ---- row 6 -------------------------------------------------------------
    offenders = scan_forbidden_assertions()
    res["forbidden_promotion_closure"] = {
        "registered_forbidden_promotion": "LATENTS_ARE_HUMAN_INTERPRETABLE",
        "machine_checked_evidence": (
            "SCM_LATENT_A and SCM_LATENT_B have identical observational and "
            "predictive joints under different latent factorizations, so a "
            "latent that reproduces behaviour need not be a recoverable "
            "world factor"),
        "evidence_result_id": "AE15-5",
        "scanned_files": SCANNED_FILES,
        "assertions_found": offenders,
        "no_artifact_asserts_a_forbidden_promotion": offenders == [],
    }

    # ---- bounds ------------------------------------------------------------
    adv_per_goal = cstars[0] / 1
    relaxed_gamma_rows = []
    for g, W in phases:
        Wr = W.with_gamma("K_PHASE[%d]|RELAXED_DISCOUNT" % g, F(1))
        vmb = opt_value(Wr)
        vmf = max(best_memoryless(Wr)[0], best_cached_skill(Wr)[0])
        relaxed_gamma_rows.append({"G": g, "V_mb": fs(vmb), "V_mf": fs(vmf),
                                   "advantage_per_goal_token":
                                       fs((vmb - vmf) / g)})
    relaxed_adv = max(F(r["advantage_per_goal_token"])
                      for r in relaxed_gamma_rows)

    mem_v, mem_tab = best_one_step_memory(model_needed)

    piR_alt = best_memoryless(swap_alt)[1]
    refit_short = best_memoryless(swap_alt)[0] - eval_memoryless(swap_alt,
                                                                 piR_alt)

    bounds = [
        {
            "id": "AE15-B1",
            "quantity": ("model-based advantage per goal token "
                         "A(G)/G = (V_mb(G) - V_mf(G))/G on K_PHASE[G]"),
            "kind": "upper",
            "bound_value": fs(F(1, 4)),
            "range_lo": fs(F(0)),
            "range_hi": fs(F(7, 4)),
            "range_derivation": (
                "A(G) >= 0 because the model-based optimum maximizes over a "
                "superset of the behaviours the three model-free interfaces "
                "induce, so A(G)/G >= 0; and A(G) <= 7G/4 because a gamma=1/2, "
                "H=3 discounted return with per-step reward in [0,G] is at "
                "most G(1 + 1/2 + 1/4) while V_mf(G) >= 0, so A(G)/G <= 7/4"),
            "vacuous": F(1, 4) >= F(7, 4),
            "attained_by": {
                "object": "K_PHASE[G] for every G in {1,2,3,4}",
                "value": [r["advantage_per_goal_token"] for r in rows],
            },
            "violated_by": {
                "relaxed_class": "RELAXED_DISCOUNT",
                "relaxation": ("the registered gamma = 1/2 is relaxed to "
                               "gamma = 1; every other registered constant is "
                               "unchanged"),
                "object": "K_PHASE[G] under gamma = 1",
                "value": fs(relaxed_adv),
                "breaks_bound": relaxed_adv > F(1, 4),
                "rows": relaxed_gamma_rows,
            },
        },
        {
            "id": "AE15-B2",
            "quantity": ("best value attainable on K_MODEL_NEEDED by any "
                         "member of REACTIVE_POLICY, CACHED_SKILL or "
                         "VALUE_REPRESENTATION"),
            "kind": "upper",
            "bound_value": fs(max(br_mn, bc_mn, bv_mn)),
            "range_lo": fs(F(0)),
            "range_hi": fs(F(7, 4)),
            "range_derivation": (
                "the value is a gamma=1/2 discounted sum of H=3 rewards each "
                "in [0,1], so by definition it lies in "
                "[0, 1 + 1/2 + 1/4] = [0, 7/4]"),
            "vacuous": max(br_mn, bc_mn, bv_mn) >= F(7, 4),
            "attained_by": {
                "object": ("the reactive map " + json.dumps(dict(
                    (model_needed.onames[o], model_needed.anames[pi_mn[o]])
                    for o in range(model_needed.nO)), sort_keys=True)),
                "value": fs(br_mn),
            },
            "violated_by": {
                "relaxed_class": "RELAXED_ONE_STEP_MEMORY",
                "relaxation": ("REACTIVE_POLICY is relaxed so that a policy "
                               "may read one step of history (the previous "
                               "observation) in addition to the current one"),
                "object": mem_tab,
                "value": fs(mem_v),
                "breaks_bound": mem_v > max(br_mn, bc_mn, bv_mn),
            },
        },
        {
            "id": "AE15-B3",
            "quantity": ("post-probe shortfall on K_SWAP of a model-free "
                         "interface: its class best under R_ALT minus the "
                         "value its unchanged stored object attains"),
            "kind": "lower",
            "bound_value": fs(F(3, 4)),
            "range_lo": fs(F(0)),
            "range_hi": fs(F(7, 4)),
            "range_derivation": (
                "a shortfall is a difference of two values of the same "
                "gamma=1/2, H=3 discounted return with per-step reward in "
                "[0,1]; the class best is by definition at least the value "
                "the stored object attains, so the shortfall lies in "
                "[0, 1 + 1/2 + 1/4] = [0, 7/4]"),
            "vacuous": F(3, 4) <= F(0),
            "attained_by": {
                "object": ["CACHED_SKILL", "REACTIVE_POLICY",
                           "VALUE_REPRESENTATION"],
                "value": [probe[c]["shortfall"]
                          for c in ("CACHED_SKILL", "REACTIVE_POLICY",
                                    "VALUE_REPRESENTATION")],
            },
            "violated_by": {
                "relaxed_class": "RELAXED_PROBE_REFIT",
                "relaxation": ("the registered probe condition -- re-queried "
                               "with no further interaction -- is relaxed to "
                               "permit a re-fit of the stored object under "
                               "R_ALT"),
                "object": "REACTIVE_POLICY re-fitted under R_ALT",
                "value": fs(refit_short),
                "breaks_bound": refit_short < F(3, 4),
            },
        },
    ]
    for b in bounds:
        b["has_violated_by_witness"] = bool(
            b["violated_by"]["breaks_bound"])
        b["status"] = ("FALSIFIABLE_BOUND" if b["has_violated_by_witness"]
                       else "UNFALSIFIED_BOUND")
    res["bounds_note"] = ("every bound carries a violated_by witness drawn "
                          "from an explicitly relaxed class; attainment is "
                          "recorded but is not evidence of non-vacuity")

    # ---- hostiles ----------------------------------------------------------
    mn_mf = max(br_mn, bc_mn, bv_mn)
    dealiased = model_needed.with_obs(
        "K_MODEL_NEEDED|H_ALIAS_BREAK", ["oa", "ob", "oc", "od"],
        {"s0": {"oa": 1}, "s1": {"od": 1}, "sG": {"ob": 1}, "sD": {"oc": 1}})
    dg, dvmb, dvmf = necessity_gap(dealiased)

    horizon_rows = []
    for W in roster:
        Wh = W.with_horizon(W.name + "|H_HORIZON", 1)
        horizon_rows.append({"task": W.name, "V_mb_registered": fs(opt_value(W)),
                             "V_mb_perturbed": fs(opt_value(Wh))})
    horizon_moved = any(r["V_mb_registered"] != r["V_mb_perturbed"]
                        for r in horizon_rows)
    named_vmb = {"K_MODEL_NEEDED": F(1, 2), "K_REACTIVE_OPT": F(3, 4),
                 "K_SWAP": F(3, 4)}
    horizon_named_numbers_hold = all(
        F(r["V_mb_perturbed"]) == named_vmb[r["task"]] for r in horizon_rows)

    cost_rows = []
    for r in rows:
        cs = F(r["c_star"])
        vmb = F(r["V_mb"])
        vmf = F(r["V_mf"])
        mf_name = r["V_mf_attaining_classes"][0]
        cost_rows.append({
            "G": r["G"],
            "registered_probe_cost": fs(cs - delta),
            "chosen_at_registered_probe_cost": chosen_class_at(
                vmb, vmf, cs - delta, mf_name),
            "perturbed_probe_cost": fs(cs + delta),
            "chosen_at_perturbed_probe_cost": chosen_class_at(
                vmb, vmf, cs + delta, mf_name),
        })
    cost_moved = all(c["chosen_at_registered_probe_cost"]
                     != c["chosen_at_perturbed_probe_cost"]
                     for c in cost_rows)
    cost_checker_holds = all(c["chosen_at_perturbed_probe_cost"]
                             == "EXPLICIT_GENERATIVE_MODEL"
                             for c in cost_rows)

    hostiles = [
        {
            "name": "H_MEMORY_LEAK",
            "inverted": False,
            "perturbs": ("the reactive class so a policy may read one step "
                         "of history"),
            "true_quantity": fs(mn_mf),
            "perturbed_quantity": fs(mem_v),
            "potent": mem_v != mn_mf,
            "checker": ("every member of REACTIVE_POLICY, CACHED_SKILL and "
                        "VALUE_REPRESENTATION is strictly suboptimal on "
                        "K_MODEL_NEEDED"),
            "detection_predicate": ("strict inequality against the model-based "
                                    "optimum 1/2, not a comparison with the "
                                    "true model-free best"),
            "detected": not (mem_v < v_mn),
            "witness": mem_tab,
        },
        {
            "name": "H_ALIAS_BREAK",
            "inverted": False,
            "perturbs": ("the observation map of K_MODEL_NEEDED so the "
                         "aliasing disappears; the perturbed world uses four "
                         "observations and is deliberately outside the "
                         "registered |O| <= 3 scope"),
            "true_quantity": fs(v_mn - mn_mf),
            "perturbed_quantity": fs(dg),
            "potent": dg != v_mn - mn_mf,
            "checker": "the model-necessity gap on K_MODEL_NEEDED is positive",
            "detection_predicate": ("positivity of the perturbed gap, not a "
                                    "comparison with the true gap"),
            "detected": not (dg > 0),
            "witness": {"V_mb": fs(dvmb), "V_mf": fs(dvmf),
                        "Z": {"s0": "oa", "s1": "od", "sG": "ob",
                              "sD": "oc"}},
        },
        {
            "name": "H_HORIZON",
            "inverted": False,
            "perturbs": "the horizon so the model-based optimum changes",
            "true_quantity": fs(v_mn),
            "perturbed_quantity": fs(opt_value(
                model_needed.with_horizon("h1", 1))),
            "potent": horizon_moved,
            "checker": ("every registered task's model-based optimum equals "
                        "its named value: 1/2 on K_MODEL_NEEDED, 3/4 on "
                        "K_REACTIVE_OPT, 3/4 on K_SWAP"),
            "detection_predicate": ("an equality against the named literals, "
                                    "independent of the potency comparison "
                                    "against the recomputed registered values"),
            "detected": not horizon_named_numbers_hold,
            "witness": horizon_rows,
        },
        {
            "name": "H_COST_SHIFT",
            "inverted": False,
            "perturbs": "the planning cost so the phase boundary moves",
            "true_quantity": "EXPLICIT_GENERATIVE_MODEL",
            "perturbed_quantity": cost_rows[0][
                "chosen_at_perturbed_probe_cost"],
            "potent": cost_moved,
            "checker": ("at the probe cost handed to it the chosen class is "
                        "EXPLICIT_GENERATIVE_MODEL for every registered G"),
            "detection_predicate": ("evaluated on the perturbed cost alone; it "
                                    "never references the choice made at the "
                                    "registered cost, so detection is not the "
                                    "potency comparison relabelled"),
            "detected": not cost_checker_holds,
            "witness": cost_rows,
        },
        {
            "name": "H_LATENT_RELABEL",
            "inverted": True,
            "perturbs": ("SCM_LATENT_B by a relabelling that must NOT be "
                         "detected as a difference"),
            "true_quantity": "observable profile of SCM_LATENT_B",
            "perturbed_quantity": "observable profile of the relabelled SCM",
            "object_changed": scm_b.stored() != scm_b_rel.stored(),
            "potent": scm_b.stored() != scm_b_rel.stored(),
            "checker": "behaviour_differs compares observable behaviour only",
            "detection_predicate": ("INVERTED: the assertion is the checker's "
                                    "silence on the relabelled object, while "
                                    "potency is the change in the stored "
                                    "object"),
            "checker_flagged": behaviour_differs(scm_b, scm_b_rel),
            "detected": not behaviour_differs(scm_b, scm_b_rel),
            "silence_asserted": True,
            "witness": ["%s->%s" % (k, relabel_map[k])
                        for k in sorted(relabel_map)],
        },
    ]

    # ---- null --------------------------------------------------------------
    ntr = rc["null_trials"]
    witness_mag0 = v_mn - mn_mf
    rng = LCG(digest)
    fires = 0
    largest = F(0)
    for i in range(ntr):
        Wn = random_world(rng, "NULL_%03d" % i)
        g, _a, _b = necessity_gap(Wn)
        if g > 0:
            fires += 1
        if g > largest:
            largest = g
    rng2 = LCG(digest)
    fires2 = 0
    largest2 = F(0)
    largest2_unaliased = F(0)
    at_or_above = 0
    at_or_above_aliased = 0
    aliased_trials = 0
    conf = [0, 0, 0, 0]
    onames = model_needed.onames
    for i in range(ntr):
        z = dict((s, {onames[rng2.next_int(3)]: 1})
                 for s in model_needed.snames)
        Wn = model_needed.with_obs("NULLZ_%03d" % i, onames, z)
        g, _a, _b = necessity_gap(Wn)
        aliased = optimal_action_conflict(Wn)
        if aliased:
            aliased_trials += 1
        if g > 0:
            fires2 += 1
        if g > largest2:
            largest2 = g
        if not aliased and g > largest2_unaliased:
            largest2_unaliased = g
        if g >= witness_mag0:
            at_or_above += 1
            if aliased:
                at_or_above_aliased += 1
        if aliased and g > 0:
            conf[0] += 1
        elif aliased and g <= 0:
            conf[1] += 1
        elif (not aliased) and g > 0:
            conf[2] += 1
        else:
            conf[3] += 1
    witness_mag = v_mn - mn_mf
    clean = []
    for W in (reactive_opt, swap):
        g, _a, _b = necessity_gap(W)
        if g > 0:
            clean.append(W.name)
    null = {
        "detector": ("the model-based optimum strictly exceeds the best value "
                     "attainable by REACTIVE_POLICY, CACHED_SKILL or "
                     "VALUE_REPRESENTATION"),
        "planted_positive": "K_MODEL_NEEDED",
        "planted_positive_magnitude": fs(witness_mag),
        "detector_fires_on_witness": witness_mag > 0,
        "known_clean_witnesses": ["K_REACTIVE_OPT", "K_SWAP"],
        "known_clean_witnesses_flagged": sorted(clean),
        "no_alarm_on_clean": clean == [],
        "primary": {
            "sampler": ("registered exact-rational sampler: a 64-bit LCG "
                        "seeded from the register's own self_digest_sha256, "
                        "drawing dyadic transition rows with denominator 8, "
                        "deterministic emissions and rewards in "
                        "{0,1/4,1/2,3/4,1}"),
            "trials": ntr,
            "fired": fires,
            "rate": "%d/%d" % (fires, ntr),
            "largest_null_magnitude": fs(largest),
            "witness_exceeds_largest_null_magnitude": witness_mag > largest,
        },
        "structure_matched": {
            "sampler": ("K_MODEL_NEEDED with T and R held fixed and only the "
                        "observation map randomized over the registered three "
                        "observations"),
            "trials": ntr,
            "fired": fires2,
            "rate": "%d/%d" % (fires2, ntr),
            "largest_null_magnitude": fs(largest2),
            "witness_exceeds_largest_null_magnitude": witness_mag > largest2,
            "trials_with_an_optimal_action_conflict": aliased_trials,
            "trials_at_or_above_witness_magnitude": at_or_above,
            "trials_at_or_above_witness_magnitude_with_a_conflict":
                at_or_above_aliased,
            "largest_null_magnitude_without_a_conflict":
                fs(largest2_unaliased),
            "conflict_vs_gap_confusion": {
                "conflict_and_gap_positive": conf[0],
                "conflict_and_gap_zero": conf[1],
                "no_conflict_and_gap_positive": conf[2],
                "no_conflict_and_gap_zero": conf[3],
            },
            "conflict_predicts_a_positive_gap_exactly":
                conf[1] == 0 and conf[2] == 0,
            "attribution": ("this control does NOT beat the witness: a "
                            "redrawn observation map frequently rebuilds an "
                            "aliasing of equal strength, so the largest "
                            "control magnitude equals the witness magnitude. "
                            "Its value is mechanism attribution, reported as "
                            "a two-way confusion table against the structural "
                            "predicate, not a magnitude comparison"),
        },
    }

    # ---- prospective predictions ------------------------------------------
    claims = dict((p["id"], p["claim"]) for p in reg["prospective_predictions"])
    ident = res["identifiability"]
    preds = [
        {
            "id": "AE15-P1", "claim": claims["AE15-P1"],
            "status": ("CONFIRMED" if (unordered_ok and res[
                "reward_swap_probe_summary"]["explicit_generative_model_alone"])
                else "REFUTED"),
            "values": {
                "ordered_pairs_total": len(table),
                "ordered_pairs_strict": strict,
                "ordered_pairs_dominated": dominated,
                "every_unordered_pair_separated": unordered_ok,
                "reoptimizing_classes": res["reward_swap_probe_summary"][
                    "reoptimizing_classes"],
            },
        },
        {
            "id": "AE15-P2", "claim": claims["AE15-P2"],
            "status": "CONFIRMED" if v_ro == br_ro else "REFUTED",
            "values": {"model_based_optimum": fs(v_ro),
                       "best_reactive_value": fs(br_ro),
                       "gap": fs(v_ro - br_ro),
                       "reactive_policies_enumerated":
                           len(all_memoryless(reactive_opt))},
        },
        {
            "id": "AE15-P3", "claim": claims["AE15-P3"],
            "status": ("CONFIRMED" if (br_mn < v_mn and bc_mn < v_mn
                                       and bv_mn < v_mn) else "REFUTED"),
            "values": {"model_based_optimum": fs(v_mn),
                       "REACTIVE_POLICY": fs(br_mn),
                       "CACHED_SKILL": fs(bc_mn),
                       "VALUE_REPRESENTATION": fs(bv_mn),
                       "gap": fs(v_mn - mn_mf)},
        },
        {
            "id": "AE15-P4", "claim": claims["AE15-P4"],
            "status": ("CONFIRMED" if (strictly_increasing and flips)
                       else "REFUTED"),
            "values": {"c_star": [r["c_star"] for r in rows],
                       "strictly_increasing_in_G": strictly_increasing,
                       "flips_strictly_on_both_sides": flips},
        },
        {
            "id": "AE15-P5", "claim": claims["AE15-P5"],
            "status": ("CONFIRMED" if (
                ident["observational_and_predictive_joints_identical"]
                and ident["latent_factorizations_differ"]
                and ident["recovered_up_to_relabelling"]) else "REFUTED"),
            "values": {
                "joints_identical":
                    ident["observational_and_predictive_joints_identical"],
                "latent_cardinalities": ident["latent_cardinalities"],
                "interventionally_distinguishable":
                    ident["interventionally_distinguishable"],
                "recovered_up_to_relabelling":
                    ident["recovered_up_to_relabelling"],
                "relabelling_permutations_checked":
                    ident["relabelling_permutations_checked"],
            },
        },
        {
            "id": "AE15-P6", "claim": claims["AE15-P6"],
            "status": ("CONFIRMED" if (offenders == [] and res[
                "forbidden_promotion_closure"]["evidence_result_id"]
                == "AE15-5") else "REFUTED"),
            "values": {"assertions_found": offenders,
                       "evidence_result_id": "AE15-5"},
        },
    ]

    checks = {
        "register_digest_matches": res["custody"]["register_digest_matches"],
        "registered_scope_respected": res["registered_scope"][
            "scope_respected"],
        "register_declared_freeze_commit_matches_custody_sha":
            res["custody"]["register_declared_freeze_commit_equals_lane_owner_sha"],
        "five_interfaces_pairwise_distinct": unordered_ok,
        "every_ordered_pair_has_a_separating_coordinate": all(
            e["separating_coordinate"] is not None for e in table),
        "reward_swap_probe_reoptimized_by_explicit_model_alone":
            res["reward_swap_probe_summary"]["explicit_generative_model_alone"],
        "predictive_state_is_reward_invariant": bool(
            probe["PREDICTIVE_STATE"][
                "predictive_state_invariant_under_reward_swap"]),
        "reactive_optimal_gap_is_exactly_zero": v_ro == br_ro,
        "reactive_optimum_enumerated_exhaustively":
            len(all_memoryless(reactive_opt))
            == reactive_opt.nA ** reactive_opt.nO,
        "model_needed_all_three_classes_strictly_suboptimal":
            br_mn < v_mn and bc_mn < v_mn and bv_mn < v_mn,
        "model_needed_value_representation_bound_is_exact":
            bv_mn == br_mn,
        "model_needed_suboptimal_for_any_memoryless_lookahead": br_mn < v_mn,
        "phase_boundary_matches_closed_form": all(r["closed_form_matches"]
                                                  for r in rows),
        "phase_boundary_strictly_increasing": strictly_increasing,
        "phase_boundary_flips_strictly_on_both_sides": flips,
        "scm_pair_joints_identical":
            ident["observational_and_predictive_joints_identical"],
        "scm_pair_latent_factorizations_differ":
            ident["latent_factorizations_differ"],
        "scm_pair_interventionally_distinguishable":
            ident["interventionally_distinguishable"],
        "scm_identifiable_latent_recovered_up_to_relabelling":
            ident["recovered_up_to_relabelling"],
        "latent_relabelling_not_flagged":
            not ident["relabelled_B_flagged_by_checker"],
        "no_artifact_asserts_a_forbidden_promotion": offenders == [],
        "every_bound_is_falsifiable": all(b["status"] == "FALSIFIABLE_BOUND"
                                          for b in bounds),
        "no_bound_is_vacuous": all(not b["vacuous"] for b in bounds),
        "every_hostile_is_potent": all(h["potent"] for h in hostiles),
        "every_hostile_is_detected": all(h["detected"] for h in hostiles),
        "null_detector_fires_on_witness": null["detector_fires_on_witness"],
        "null_no_alarm_on_clean_witnesses": null["no_alarm_on_clean"],
        "value_representation_cannot_realize_every_memoryless_map":
            lookahead_action_groups(model_needed)[1]
            < len(all_memoryless(model_needed)),
        "null_positive_gap_requires_an_optimal_action_conflict":
            null["structure_matched"]["conflict_vs_gap_confusion"][
                "no_conflict_and_gap_positive"] == 0,
        "null_witness_exceeds_largest_primary_null_magnitude":
            null["primary"]["witness_exceeds_largest_null_magnitude"],
        "all_prospective_predictions_reported":
            len(preds) == len(reg["prospective_predictions"]),
        "all_prospective_predictions_confirmed": all(
            p["status"] == "CONFIRMED" for p in preds),
    }

    out = {
        "schema": SCHEMA,
        "issue": ISSUE,
        "issue_comment_id": ISSUE_COMMENT_ID,
        "section": SECTION,
        "package": PACKAGE,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "register_commit": REGISTER_COMMIT,
        "register_digest": digest,
        "claim_ceiling": CLAIM_CEILING,
        "theorems": ["AE15-1", "AE15-2", "AE15-3", "AE15-4", "AE15-5",
                     "AE15-6"],
        "results": res,
        "bounds": bounds,
        "hostiles": hostiles,
        "null": null,
        "prospective_predictions": preds,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }
    return out


def main():
    out = build()
    sys.stdout.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0 if out["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
