#!/usr/bin/env python3
"""GMI #833 AE15 -- independent oracle, route B.

This module imports nothing from ae15_world_model_necessity_v1.  It rebuilds
the registered roster from the frozen specification and recomputes every
claimed quantity by a materially different algorithm:

  route A                                     route B (here)
  ------------------------------------------  ----------------------------
  optimal value by a memoised backward         Smallwood-Sondik alpha-vector
  recursion over REACHABLE BELIEF POINTS       backward enumeration of every
                                               conditional plan over the WHOLE
                                               belief simplex, with exact
                                               pointwise-dominance pruning
  class values by forward propagation of a     exhaustive enumeration of every
  state distribution, one step at a time       complete state/observation
                                               trajectory with its exact path
                                               probability
  observation-level lookahead tables by        the same tables accumulated by
  matrix recursion                             enumerating every (action
                                               sequence, state path) pair
  phase boundary from the closed form          the boundary re-differenced from
  c*(G) = V_mb(G) - V_mf(G)                    independently recomputed values
  SCM joints by functional evaluation          exhaustive enumeration of the
                                               latent x X x Y product space

Stdlib only; exact rational arithmetic throughout.
"""
from fractions import Fraction as F

HALF = F(1, 2)


# ---------------------------------------------------------------------------
# the registered roster, rebuilt from the frozen specification
# ---------------------------------------------------------------------------
def w_reactive_opt():
    return {
        "name": "K_REACTIVE_OPT",
        "S": ["s0", "s1"], "A": ["a0", "a1"], "O": ["o0", "o1"],
        "T": {("s0", "a0"): {"s1": F(1)}, ("s0", "a1"): {"s0": F(1)},
              ("s1", "a0"): {"s1": F(1)}, ("s1", "a1"): {"s1": F(1)}},
        "Z": {"s0": {"o0": F(1)}, "s1": {"o1": F(1)}},
        "R": {("s0", "a0"): F(0), ("s0", "a1"): F(1, 4),
              ("s1", "a0"): F(1), ("s1", "a1"): F(1)},
        "b0": {"s0": F(1)}, "gamma": HALF, "H": 3,
    }


def w_model_needed():
    S = ["s0", "s1", "sD", "sG"]
    A = ["a0", "a1", "a2"]
    T = {("s0", "a0"): {"s1": HALF, "sG": HALF}}
    for s in S:
        for a in A:
            if (s, a) not in T:
                T[(s, a)] = {"sD": F(1)}
    R = dict(((s, a), F(0)) for s in S for a in A)
    R[("s1", "a1")] = F(1)
    R[("sG", "a2")] = F(1)
    return {
        "name": "K_MODEL_NEEDED", "S": S, "A": A, "O": ["oa", "ob", "oc"],
        "T": T,
        "Z": {"s0": {"oa": F(1)}, "s1": {"oa": F(1)},
              "sG": {"ob": F(1)}, "sD": {"oc": F(1)}},
        "R": R, "b0": {"s0": F(1)}, "gamma": HALF, "H": 3,
    }


def w_phase(g):
    W = w_model_needed()
    W = dict(W)
    W["name"] = "K_PHASE[%d]" % g
    R = dict(W["R"])
    R[("s1", "a1")] = F(g)
    R[("sG", "a2")] = F(g)
    W["R"] = R
    return W


def w_swap():
    S = ["s0", "sP", "sQ"]
    A = ["a0", "a1"]
    T = {("s0", "a0"): {"sP": F(1)}, ("s0", "a1"): {"sQ": F(1)},
         ("sP", "a0"): {"sP": F(1)}, ("sP", "a1"): {"sP": F(1)},
         ("sQ", "a0"): {"sQ": F(1)}, ("sQ", "a1"): {"sQ": F(1)}}
    R = dict(((s, a), F(0)) for s in S for a in A)
    R[("sP", "a0")] = F(1)
    R[("sP", "a1")] = F(1)
    return {"name": "K_SWAP", "S": S, "A": A, "O": ["o0", "oP", "oQ"],
            "T": T, "Z": {"s0": {"o0": F(1)}, "sP": {"oP": F(1)},
                          "sQ": {"oQ": F(1)}},
            "R": R, "b0": {"s0": F(1)}, "gamma": HALF, "H": 3}


def w_swap_alt():
    W = dict(w_swap())
    W["name"] = "K_SWAP_R_ALT"
    R = dict(((s, a), F(0)) for s in W["S"] for a in W["A"])
    R[("sQ", "a0")] = F(1)
    R[("sQ", "a1")] = F(1)
    W["R"] = R
    return W


def oracle_roster():
    return {"K_REACTIVE_OPT": w_reactive_opt(),
            "K_MODEL_NEEDED": w_model_needed(),
            "K_SWAP": w_swap(),
            "K_SWAP_R_ALT": w_swap_alt()}


# ---------------------------------------------------------------------------
# route B: alpha-vector backward enumeration over the whole belief simplex
# ---------------------------------------------------------------------------
def _prune(vectors, S):
    """Remove pointwise-dominated vectors.  An alpha with alpha <= beta
    everywhere is never the maximum at any belief, so dropping it cannot change
    the upper envelope."""
    uniq = sorted(set(tuple(v[s] for s in S) for v in vectors))
    keep = []
    for i, v in enumerate(uniq):
        dominated = False
        for j, u in enumerate(uniq):
            if i == j:
                continue
            if all(u[k] >= v[k] for k in range(len(S))):
                if any(u[k] > v[k] for k in range(len(S))):
                    dominated = True
                    break
                if j < i:
                    dominated = True
                    break
        if not dominated:
            keep.append(v)
    return [dict(zip(S, v)) for v in keep]


def oracle_opt_value(W):
    S, A, O = W["S"], W["A"], W["O"]
    gamma, H = W["gamma"], W["H"]
    stage = [dict((s, F(0)) for s in S)]
    for _ in range(H):
        built = []
        for a in A:
            choices = [{}]
            for o in O:
                nxt = []
                for c in choices:
                    for idx in range(len(stage)):
                        d = dict(c)
                        d[o] = idx
                        nxt.append(d)
                choices = nxt
            for c in choices:
                alpha = {}
                for s in S:
                    acc = W["R"][(s, a)]
                    fut = F(0)
                    for sp, tp in sorted(W["T"][(s, a)].items()):
                        if not tp:
                            continue
                        for o, zp in sorted(W["Z"][sp].items()):
                            if zp:
                                fut += tp * zp * stage[c[o]][sp]
                    alpha[s] = acc + gamma * fut
                built.append(alpha)
        stage = _prune(built, S)
        if len(stage) > 4096:
            raise RuntimeError("alpha set blew up")
    best = None
    for alpha in stage:
        v = F(0)
        for s, p in sorted(W["b0"].items()):
            v += p * alpha[s]
        if best is None or v > best:
            best = v
    return best


# ---------------------------------------------------------------------------
# route B: exhaustive enumeration of complete trajectories
# ---------------------------------------------------------------------------
def oracle_eval(W, chooser):
    """Exact value of an arbitrary deterministic policy, obtained by summing
    over every complete state/observation trajectory."""
    acc = [F(0)]

    def rec(t, s, p, hist):
        if t == W["H"] or not p:
            return
        disc = W["gamma"] ** t
        for o, zp in sorted(W["Z"][s].items()):
            if not zp:
                continue
            a = chooser(t, hist, o)
            w = p * zp
            r = W["R"][(s, a)]
            if r:
                acc[0] += disc * w * r
            for sp, tp in sorted(W["T"][(s, a)].items()):
                if tp:
                    rec(t + 1, sp, w * tp, hist + ((o, a),))

    for s, bp in sorted(W["b0"].items()):
        rec(0, s, bp, ())
    return acc[0]


def _maps(keys, values):
    out = [{}]
    for k in keys:
        nxt = []
        for p in out:
            for v in values:
                d = dict(p)
                d[k] = v
                nxt.append(d)
        out = nxt
    return out


def oracle_all_reactive(W):
    return _maps(W["O"], W["A"])


def oracle_best_reactive(W):
    best = None
    bp = None
    for pi in oracle_all_reactive(W):
        v = oracle_eval(W, lambda t, h, o, _p=pi: _p[o])
        key = tuple(pi[o] for o in W["O"])
        if best is None or v > best or (v == best and key < bp):
            best = v
            bp = key
    return best, dict(zip(W["O"], bp))


def oracle_all_sequences(W):
    out = [()]
    for _ in range(W["H"]):
        nxt = []
        for p in out:
            for a in W["A"]:
                nxt.append(p + (a,))
        out = nxt
    return out


def oracle_initial_contexts(W):
    out = {}
    for s, p in sorted(W["b0"].items()):
        for o, zp in sorted(W["Z"][s].items()):
            if zp:
                out[o] = out.get(o, F(0)) + p * zp
    return out


def oracle_best_cached(W):
    """A cached skill maps the registered context (the initial observation) to
    a fixed action sequence and replays it."""
    total = F(0)
    table = {}
    for o0 in sorted(oracle_initial_contexts(W)):
        best = None
        bseq = None
        for seq in oracle_all_sequences(W):
            def ch(t, h, o, _s=seq, _c=o0):
                return _s[t]
            v = oracle_eval_from_context(W, o0, ch)
            if best is None or v > best or (v == best and seq < bseq):
                best = v
                bseq = seq
        total += oracle_initial_contexts(W)[o0] * best
        table[o0] = list(bseq)
    return total, table


def oracle_eval_from_context(W, o0, chooser):
    """Value conditioned on the initial observation being o0."""
    weight = F(0)
    acc = [F(0)]
    for s, p in sorted(W["b0"].items()):
        weight += p * W["Z"][s].get(o0, F(0))
    if not weight:
        return F(0)

    def rec(t, s, p, hist, forced):
        if t == W["H"] or not p:
            return
        disc = W["gamma"] ** t
        obs = [(o0, W["Z"][s].get(o0, F(0)))] if forced else sorted(
            W["Z"][s].items())
        for o, zp in obs:
            if not zp:
                continue
            a = chooser(t, hist, o)
            w = p * zp
            r = W["R"][(s, a)]
            if r:
                acc[0] += disc * w * r
            for sp, tp in sorted(W["T"][(s, a)].items()):
                if tp:
                    rec(t + 1, sp, w * tp, hist + ((o, a),), False)

    for s, p in sorted(W["b0"].items()):
        rec(0, s, p, (), True)
    return acc[0] / weight


# ---------------------------------------------------------------------------
# route B: observation-level lookahead tables by enumeration
# ---------------------------------------------------------------------------
def oracle_reference_conditional(W):
    """rho(s) is accumulated by enumerating every (action sequence, state
    path) pair under the uniform-action process."""
    rho = dict((s, F(0)) for s in W["S"])
    inv = F(1, len(W["A"]))

    def rec(t, s, p):
        if t == W["H"] or not p:
            return
        rho[s] += p
        for a in W["A"]:
            for sp, tp in sorted(W["T"][(s, a)].items()):
                if tp:
                    rec(t + 1, sp, p * inv * tp)

    for s, bp in sorted(W["b0"].items()):
        rec(0, s, bp)
    tot = sum(rho.values())
    if tot:
        rho = dict((s, rho[s] / tot) for s in W["S"])
    out = {}
    for o in W["O"]:
        w = F(0)
        for s in W["S"]:
            w += rho[s] * W["Z"][s].get(o, F(0))
        if w:
            out[o] = dict((s, rho[s] * W["Z"][s].get(o, F(0)) / w)
                          for s in W["S"])
        else:
            supp = [s for s in W["S"] if W["Z"][s].get(o, F(0))] or W["S"]
            out[o] = dict((s, F(1, len(supp)) if s in supp else F(0))
                          for s in W["S"])
    return out


def oracle_lookahead(W):
    pref = oracle_reference_conditional(W)
    rhat = {}
    phat = {}
    for o in W["O"]:
        for a in W["A"]:
            rhat[(o, a)] = sum(pref[o][s] * W["R"][(s, a)] for s in W["S"])
            row = dict((op, F(0)) for op in W["O"])
            for s in W["S"]:
                if not pref[o][s]:
                    continue
                for sp, tp in sorted(W["T"][(s, a)].items()):
                    for op, zp in sorted(W["Z"][sp].items()):
                        if tp and zp:
                            row[op] += pref[o][s] * tp * zp
            phat[(o, a)] = row
    return rhat, phat


def oracle_value_grid(W):
    rmax = max(W["R"].values())
    hi = F(0)
    disc = F(1)
    for _ in range(W["H"]):
        hi += disc * rmax
        disc *= W["gamma"]
    n = int(hi * 4)
    return [F(k, 4) for k in range(0, n + 1)] or [F(0)]


def oracle_greedy(W, V, rhat, phat):
    pi = {}
    for o in W["O"]:
        best_a = None
        best_q = None
        for a in W["A"]:
            q = rhat[(o, a)]
            for op in W["O"]:
                q += W["gamma"] * phat[(o, a)][op] * V[op]
            if best_q is None or q > best_q:
                best_q = q
                best_a = a
        pi[o] = best_a
    return pi


def oracle_realizable_greedy(W):
    rhat, phat = oracle_lookahead(W)
    out = {}
    for V in _maps(W["O"], oracle_value_grid(W)):
        pi = oracle_greedy(W, V, rhat, phat)
        key = tuple(pi[o] for o in W["O"])
        if key not in out:
            out[key] = dict(V)
    return out, rhat, phat


def oracle_best_value_representation(W):
    seen, rhat, phat = oracle_realizable_greedy(W)
    best = None
    bkey = None
    for key in sorted(seen):
        pi = dict(zip(W["O"], key))
        v = oracle_eval(W, lambda t, h, o, _p=pi: _p[o])
        if best is None or v > best:
            best = v
            bkey = key
    return best, bkey, seen, rhat, phat


def oracle_lookahead_groups(W):
    rhat, phat = oracle_lookahead(W)
    bound = 1
    per_obs = []
    for o in W["O"]:
        groups = {}
        for a in W["A"]:
            k = (rhat[(o, a)], tuple(phat[(o, a)][op] for op in W["O"]))
            groups.setdefault(k, []).append(a)
        per_obs.append(sorted(sorted(v) for v in groups.values()))
        bound *= len(groups)
    return per_obs, bound


# ---------------------------------------------------------------------------
# route B: the explicitly relaxed one-step-memory class
# ---------------------------------------------------------------------------
def oracle_reachable_readouts(W):
    seen = set()

    def rec(t, s, p, prev):
        if t == W["H"] or not p:
            return
        for o, zp in sorted(W["Z"][s].items()):
            if not zp:
                continue
            seen.add((prev, o))
            for a in W["A"]:
                for sp, tp in sorted(W["T"][(s, a)].items()):
                    if tp:
                        rec(t + 1, sp, p * zp * tp, o)

    for s, bp in sorted(W["b0"].items()):
        rec(0, s, bp, "-")
    return sorted(seen)


def oracle_best_one_step_memory(W):
    keys = oracle_reachable_readouts(W)
    best = None
    btab = None
    for tab in _maps(keys, W["A"]):
        def ch(t, h, o, _tab=tab):
            prev = h[-1][0] if h else "-"
            return _tab[(prev, o)]
        v = oracle_eval(W, ch)
        if best is None or v > best:
            best = v
            btab = tab
    return best, dict(("%s|%s" % k, v) for k, v in sorted(btab.items()))


# ---------------------------------------------------------------------------
# route B: phase boundary and reward-swap probe
# ---------------------------------------------------------------------------
def oracle_phase(g):
    W = w_phase(g)
    vmb = oracle_opt_value(W)
    vr = oracle_best_reactive(W)[0]
    vc = oracle_best_cached(W)[0]
    vv = oracle_best_value_representation(W)[0]
    vmf = max(vr, vc, vv)
    return {"G": g, "V_mb": vmb, "V_mf": vmf, "c_star": vmb - vmf,
            "V_reactive": vr, "V_cached": vc, "V_value_rep": vv}


def oracle_probe():
    W = w_swap()
    WA = w_swap_alt()
    out = {}
    piR = oracle_best_reactive(W)[1]
    out["REACTIVE_POLICY"] = {
        "after": oracle_eval(WA, lambda t, h, o, _p=piR: _p[o]),
        "class_best": oracle_best_reactive(WA)[0]}
    tabR = oracle_best_cached(W)[1]
    ctx = oracle_initial_contexts(WA)
    after = F(0)
    for o0 in sorted(ctx):
        if o0 in tabR:
            after += ctx[o0] * oracle_eval_from_context(
                WA, o0, lambda t, h, o, _s=tabR[o0]: _s[t])
    out["CACHED_SKILL"] = {"after": after,
                           "class_best": oracle_best_cached(WA)[0]}
    _b, bkey, seen, rhat, phat = oracle_best_value_representation(W)
    VR = seen[bkey]
    stale = oracle_greedy(W, VR, rhat, phat)
    out["VALUE_REPRESENTATION"] = {
        "after": oracle_eval(WA, lambda t, h, o, _p=stale: _p[o]),
        "class_best": oracle_best_value_representation(WA)[0]}
    out["EXPLICIT_GENERATIVE_MODEL"] = {
        "after": oracle_opt_value(WA), "class_best": oracle_opt_value(WA)}
    for k in sorted(out):
        out[k]["shortfall"] = out[k]["class_best"] - out[k]["after"]
        out[k]["reoptimizes"] = out[k]["after"] == out[k]["class_best"]
    return out


# ---------------------------------------------------------------------------
# route B: structural causal models by product-space enumeration
# ---------------------------------------------------------------------------
SCM_A = {"name": "SCM_LATENT_A", "latent": "U",
         "probs": {"u0": F(1, 2), "u1": F(1, 2)},
         "edges": [("U", "X"), ("U", "Y")],
         "fx": {"u0": "x0", "u1": "x1"},
         "fy_from_latent": {"u0": "y0", "u1": "y1"},
         "fy_from_x": None}
SCM_B = {"name": "SCM_LATENT_B", "latent": "V",
         "probs": {"v0": F(1, 4), "v1": F(1, 4),
                   "v2": F(1, 4), "v3": F(1, 4)},
         "edges": [("V", "X"), ("X", "Y")],
         "fx": {"v0": "x0", "v1": "x1", "v2": "x0", "v3": "x1"},
         "fy_from_latent": None,
         "fy_from_x": {"x0": "y0", "x1": "y1"}}
SCM_ID = {"name": "SCM_LATENT_ID", "latent": "L",
          "probs": {"l0": F(1, 3), "l1": F(1, 3), "l2": F(1, 3)},
          "edges": [("L", "X"), ("L", "Y")],
          "fx": {"l0": "x0", "l1": "x1", "l2": "x2"},
          "fy_from_latent": {"l0": "y0", "l1": "y1", "l2": "y2"},
          "fy_from_x": None}


def _y_of(M, u, x):
    if M["fy_from_latent"] is not None:
        return M["fy_from_latent"][u]
    return M["fy_from_x"][x]


def oracle_full_table(M):
    """The complete latent x X x Y product space with exact weights."""
    rows = []
    for u in sorted(M["probs"]):
        x = M["fx"][u]
        rows.append((u, x, _y_of(M, u, x), M["probs"][u]))
    return sorted(rows)


def oracle_profile(M):
    joint = {}
    for _u, x, y, p in oracle_full_table(M):
        joint[(x, y)] = joint.get((x, y), F(0)) + p
    px = {}
    py = {}
    for (x, y), p in sorted(joint.items()):
        px[x] = px.get(x, F(0)) + p
        py[y] = py.get(y, F(0)) + p
    return {
        "joint_XY": dict(("%s,%s" % k, str(v)) for k, v in sorted(joint.items())),
        "marginal_X": dict((k, str(v)) for k, v in sorted(px.items())),
        "marginal_Y": dict((k, str(v)) for k, v in sorted(py.items())),
        "predictive_Y_given_X": dict(
            ("%s|%s" % (y, x), str(p / px[x]))
            for (x, y), p in sorted(joint.items()) if px[x]),
        "predictive_X_given_Y": dict(
            ("%s|%s" % (x, y), str(p / py[y]))
            for (x, y), p in sorted(joint.items()) if py[y]),
    }


def oracle_do(M, c):
    out = {}
    for u in sorted(M["probs"]):
        y = _y_of(M, u, c)
        out[y] = out.get(y, F(0)) + M["probs"][u]
    return dict((k, str(v)) for k, v in sorted(out.items()))


def oracle_relabel(M, mapping):
    inv = dict((v, k) for k, v in mapping.items())
    N = dict(M)
    N["name"] = M["name"] + "_RELABELLED"
    N["probs"] = dict((mapping[u], p) for u, p in M["probs"].items())
    N["fx"] = dict((mapping[u], x) for u, x in M["fx"].items())
    if M["fy_from_latent"] is not None:
        N["fy_from_latent"] = dict((mapping[u], y)
                                   for u, y in M["fy_from_latent"].items())
    N["_inv"] = inv
    return N


def oracle_recovery_map(M):
    return dict((x, u) for u, x in sorted(M["fx"].items()))
