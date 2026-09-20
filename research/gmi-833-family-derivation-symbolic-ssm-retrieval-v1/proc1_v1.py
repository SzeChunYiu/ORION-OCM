"""PROC1 v1 — exact certificates for the derivation tranches (GMI #833).

BLIND: reads only the frozen battery, the frozen basis, and declared caps.
Numpy is a search-side dependency (guarded import).

Components:
  w2_pairing_dp        — cost-layered pairing DP over M_STREAM(k=1):
                         update exprs deduped by state trajectory on the
                         battery stream; readout exprs deduped by the exact
                         49-row table over (s, x) in D; pairing by numpy table
                         gather; per-target minimal cost + machine within the
                         completed scope; caps reported, never silent.
  gatefree_k1_exhaust  — exhaustive integer coefficient enumeration of all
                         gate-free M_STREAM(k=1) machines (trajectory
                         legality), deciding gate-free realizability exactly
                         at the guard-relevant coefficient bound.
  realize_gatefree_k1  — constructive expression realization with node-level
                         guard legality for a coefficient tuple.
  gatefree_k2_delay    — exhaustive coefficient enumeration of gate-free
                         M_STREAM(k=2) machines on the delay subtranche
                         stream (bound 1 complete; bound 2 with bounded
                         readout coefficients).
  ep_affine_exhaust    — exhaustive coefficient-tuple check that no affine
                         final-output form (all gate-free M_STREAM machines,
                         any k) solves B_EP.
  contr_readout_certs  — exhaustive sparse-affine and single-gate readout
                         certificates over the 18-cell task layout.
"""
from __future__ import annotations

import itertools

try:
    import numpy as np
except ImportError:  # pragma: no cover - search side only
    np = None

from machinery_v1 import (DOMAIN, CONSTS, GUARD, UNARIES, expr_ops,
                          expr_eval, sim_stream)


# ---------------------------------------------------------------------------
# expression-table closure (49-row tables over (s, x))
# ---------------------------------------------------------------------------

UNARY_NAMES = sorted(UNARIES)


MARK = 99  # guard-violation marker: pointwise illegal value


def table_of(e, atoms):
    """Flat GUARDED table of e over atoms (each atom ranging over D),
    lexicographic in atom order (last atom fastest). Every node evaluated
    with the guard; any violation yields MARK at that point. Two exprs with
    equal guarded tables are interchangeable for correctness AND pointwise
    legality on every evaluation set."""
    n = len(atoms)

    def go(e, env):
        t = e[0]
        if t == "atom":
            return env[atoms.index(e[1])]
        if t == "const":
            return e[1]
        if t == "un":
            v = go(e[2], env)
            if v == MARK:
                return MARK
            return UNARIES[e[1]](v)
        a = go(e[1], env)
        if a == MARK:
            return MARK
        b = go(e[2], env)
        if b == MARK:
            return MARK
        s = a + b
        if s < -GUARD or s > GUARD:
            return MARK
        return s

    out = []
    for combo in itertools.product(DOMAIN, repeat=n):
        out.append(go(e, list(combo)))
    return tuple(out)


def apply_unary_table(tbl, name):
    if name == "NEG":
        return tuple(MARK if v == MARK else -v for v in tbl)
    c = int(name[2:])
    return tuple(MARK if v == MARK else (1 if v >= c else 0) for v in tbl)


def add_tables(a, b):
    out = []
    for x, y in zip(a, b):
        if x == MARK or y == MARK:
            out.append(MARK)
            continue
        s = x + y
        out.append(MARK if (s < -GUARD or s > GUARD) else s)
    return tuple(out)


def table_closure(cost_cap, width_cap=60_000):
    """Dedup enumeration of expressions over atoms ('s0','x') + consts by
    49-row table semantics. Returns (dedup, buckets, binding):
    dedup: table -> (cost, expr); buckets[c] = [(table, expr)] at exact
    minimal cost c."""
    atoms = ["s0", "x"]
    dedup = {}
    buckets = [[]]
    for a in atoms:
        e = ["atom", a]
        t = table_of(e, atoms)
        if t not in dedup:
            dedup[t] = (0, e)
            buckets[0].append((t, e))
    for c in CONSTS:
        e = ["const", c]
        t = table_of(e, atoms)
        if t not in dedup:
            dedup[t] = (0, e)
            buckets[0].append((t, e))
    binding = {"cost_cap": False, "width_cap": False}
    for cost in range(1, cost_cap + 1):
        layer = []
        for t0, e0 in buckets[cost - 1]:
            for u in UNARY_NAMES:
                t = apply_unary_table(t0, u)
                if t in dedup:
                    continue
                e = ["un", u, e0]
                dedup[t] = (cost, e)
                layer.append((t, e))
        for i in range(cost):
            j = cost - 1 - i
            if j < 0 or i >= len(buckets) or j >= len(buckets):
                continue
            bi, bj = buckets[i], buckets[j]
            for ta, ea in bi:
                for tb, eb in bj:
                    t = add_tables(ta, tb)
                    if t in dedup:
                        continue
                    e = ["add", ea, eb]
                    dedup[t] = (cost, e)
                    layer.append((t, e))
        buckets.append(layer)
        if sum(len(b) for b in buckets) > width_cap:
            binding["width_cap"] = True
            break
    binding["total_tables"] = sum(len(b) for b in buckets)
    binding["max_cost_reached"] = len(buckets) - 1
    return dedup, buckets, binding


# ---------------------------------------------------------------------------
# B_W2 pairing DP
# ---------------------------------------------------------------------------

def traj_of_update(e, stream):
    """State trajectory of a k=1 update expr on the stream from s=0."""
    s = 0
    traj = [0]
    for x in stream:
        v = expr_eval(e, {"s0": s, "x": x})
        if v is None:
            return None
        s = v
        traj.append(v)
    return tuple(traj)


def w2_pairing_dp(stream, targets, rho=1, cost_cap=12, width_cap=60_000):
    """targets: dict trace_tuple -> task_id. Enumerate (update, readout)
    pairs; per-task minimal cost + machine within the completed scope."""
    dedup, buckets, binding = table_closure(cost_cap, width_cap)
    # update candidates: dedup further by trajectory (equivalent updates)
    traj_cost = {}
    traj_expr = {}
    for t, (c, e) in dedup.items():
        tr = traj_of_update(e, stream)
        if tr is None:
            continue
        if tr not in traj_cost or c < traj_cost[tr]:
            traj_cost[tr] = c
            traj_expr[tr] = (c, e)
    trajs = sorted(traj_cost, key=lambda k: (traj_cost[k], k))
    # readout tables as numpy arrays for gather
    tabs = []
    tab_cost = []
    tab_expr = []
    for t, (c, e) in dedup.items():
        tabs.append(t)
        tab_cost.append(c)
        tab_expr.append(e)
    T = np.array(tabs, dtype=np.int64)  # (B, 49)
    B = T.shape[0]
    n_pos = len(stream)
    # target index
    tgt_arr = np.array([list(k) for k in targets], dtype=np.int64)
    tgt_ids = [targets[k] for k in targets]
    order = np.lexsort(tgt_arr.T[::-1])
    tgt_sorted = tgt_arr[order]
    tgt_ids_sorted = [tgt_ids[i] for i in order]
    best = {}
    binding_details = {"n_trajs": len(trajs), "n_readout_tables": B}
    # flat index of (s, x): s + (x+GUARD)*(2*GUARD+1)
    for tr in trajs:
        cu, eu = traj_expr[tr]
        idx = np.array([(s + GUARD) * (2 * GUARD + 1) + (x + GUARD)
                        for s, x in zip(tr[:-1], stream)], dtype=np.int64)
        traces = T[:, idx]  # (B, n_pos); MARK = illegal at a visited point
        ok = ~(traces == MARK).any(axis=1)
        # match against sorted targets: encode rows as single ints (base 9,
        # MARK encoded as 8 -> never matches a target)
        enc_tr = np.where(ok[:, None], traces + GUARD, 8)
        enc = np.zeros(B, dtype=np.int64)
        for t in range(n_pos):
            enc = enc * 9 + enc_tr[:, t]
        tenc = np.zeros(tgt_sorted.shape[0], dtype=np.int64)
        for t in range(n_pos):
            tenc = tenc * 9 + (tgt_sorted[:, t] + GUARD)
        pos = np.searchsorted(tenc, enc)
        pos_clip = np.clip(pos, 0, len(tenc) - 1)
        hit = (tenc[pos_clip] == enc) & ok
        for bi in np.nonzero(hit)[0]:
            ti = pos_clip[bi]
            tid = tgt_ids_sorted[ti]
            c = rho + cu + int(tab_cost[bi])
            if tid not in best or c < best[tid]["cost"]:
                best[tid] = {"cost": c,
                             "machine": {"model": "M_STREAM", "cells": 1,
                                         "update": [eu],
                                         "readout": tab_expr[bi], "rho": rho},
                             "update_cost": cu, "readout_cost": int(tab_cost[bi])}
    return {"per_task": best, "binding": binding,
            "details": binding_details,
            "trajs": {str(list(k)): traj_cost[k] for k in trajs}}


# ---------------------------------------------------------------------------
# gate-free exhaustive certificates
# ---------------------------------------------------------------------------

def gatefree_k1_exhaust(stream, targets, coef_bound=3):
    """All gate-free M_STREAM(k=1) machines: s' = a s + b x + c,
    y = d s + e x + f. Exhaustive over [-bound,bound]^6 with trajectory
    legality. Returns (realized {task_id: coeffs}, stats)."""
    N = len(stream)
    xs = np.array(stream, dtype=np.int64)
    ranges = range(-coef_bound, coef_bound + 1)
    tuples = np.array(list(itertools.product(ranges, repeat=6)),
                      dtype=np.int64)
    M = tuples.shape[0]
    tgt_keys = {tuple(k): v for k, v in targets.items()}
    tgt_keys_list = list(targets)
    tgt_ids_list = [targets[k] for k in tgt_keys_list]
    tgt_rows = np.array([list(k) for k in targets], dtype=np.int64)
    order = np.lexsort(tgt_rows.T[::-1])
    tgt_sorted = tgt_rows[order]
    tgt_ids_sorted = [tgt_ids_list[i] for i in order]
    realized = {}
    for cs in range(0, M, 20000):
        ch = tuples[cs:cs + 20000]
        n = ch.shape[0]
        s = np.zeros(n, dtype=np.int64)
        legal = np.ones(n, dtype=bool)
        outs = np.zeros((n, N), dtype=np.int64)
        for t in range(N):
            x_t = xs[t]
            ns = ch[:, 0] * s + ch[:, 1] * x_t + ch[:, 2]
            y = ch[:, 3] * s + ch[:, 4] * x_t + ch[:, 5]
            legal &= (ns >= -GUARD) & (ns <= GUARD)
            legal &= (y >= -GUARD) & (y <= GUARD)
            outs[:, t] = y
            s = ns
        if not legal.any():
            continue
        leg_rows = outs[legal]
        leg_coef = ch[legal]
        enc = np.zeros(leg_rows.shape[0], dtype=np.int64)
        for t in range(N):
            enc = enc * 7 + (leg_rows[:, t] + GUARD)
        tenc = np.zeros(tgt_sorted.shape[0], dtype=np.int64)
        for t in range(N):
            tenc = tenc * 7 + (tgt_sorted[:, t] + GUARD)
        pos = np.searchsorted(tenc, enc)
        pos_clip = np.clip(pos, 0, len(tenc) - 1)
        hit = tenc[pos_clip] == enc
        for ri in np.nonzero(hit)[0]:
            tid = tgt_ids_sorted[pos_clip[ri]]
            if tid not in realized:
                realized[tid] = [int(v) for v in leg_coef[ri]]
    return realized, {"tuples_enumerated": int(M)}


def realize_gatefree_k1(coeffs, stream):
    """Construct gate-free expressions for coefficients (a,b,c,d,e,f) with
    node-level guard legality verified by exact simulation."""
    def lin_expr(terms, const):
        parts = []
        for atom, a in terms:
            for _ in range(abs(a)):
                t = ["atom", atom]
                if a < 0:
                    t = ["un", "NEG", t]
                parts.append(t)
        if abs(const) > 0:
            for _ in range(abs(const)):
                parts.append(["const", 1 if const > 0 else -1])
        if not parts:
            return ["const", 0]
        e = parts[0]
        for p in parts[1:]:
            e = ["add", e, p]
        return e

    a, b, c, d, e_, f = coeffs
    m = {"model": "M_STREAM", "cells": 1,
         "update": [lin_expr([("s0", a), ("x", b)], c)],
         "readout": lin_expr([("s0", d), ("x", e_)], f), "rho": 1}
    outs, trajs, legal = sim_stream(m, stream)
    return m if legal else None


def gatefree_k2_delay(stream, targets, ab_bound=2, ro_bound=1):
    """Gate-free M_STREAM(k=2): s1' = a11 s1 + a12 s2 + b1 x + c1;
    s2' = a21 s1 + a22 s2 + b2 x + c2; y = d1 s1 + d2 s2 + e x + f.
    Exhaustive over (A,B,c) in [-ab_bound,ab]^8 and (d1,d2,e,f) in
    [-ro_bound,ro]^4. Returns (realized {trace: coeffs}, stats)."""
    N = len(stream)
    xs = np.array(stream, dtype=np.int64)
    abc = list(itertools.product(range(-ab_bound, ab_bound + 1), repeat=8))
    ro = list(itertools.product(range(-ro_bound, ro_bound + 1), repeat=4))
    abc_arr = np.array(abc, dtype=np.int64)
    ro_arr = np.array(ro, dtype=np.int64)
    tgt_rows = np.array([list(k) for k in targets], dtype=np.int64)
    tgt_keys_list = [tuple(k) for k in targets]
    order = np.lexsort(tgt_rows.T[::-1])
    tgt_sorted = tgt_rows[order]
    tenc = np.zeros(tgt_sorted.shape[0], dtype=np.int64)
    for t in range(N):
        tenc = tenc * 9 + (tgt_sorted[:, t] + GUARD)
    tenc_order = np.sort(tenc)
    realized = {}
    n_pairs = abc_arr.shape[0] * ro_arr.shape[0]
    for abc_i in range(abc_arr.shape[0]):
        a11, a12, b1, c1, a21, a22, b2, c2 = abc_arr[abc_i]
        for ro_chunk in range(0, ro_arr.shape[0], 500):
            rch = ro_arr[ro_chunk:ro_chunk + 500]
            n = rch.shape[0]
            s1 = np.zeros(n, dtype=np.int64)
            s2 = np.zeros(n, dtype=np.int64)
            legal = np.ones(n, dtype=bool)
            outs = np.zeros((n, N), dtype=np.int64)
            for t in range(N):
                x_t = xs[t]
                ns1 = a11 * s1 + a12 * s2 + b1 * x_t + c1
                ns2 = a21 * s1 + a22 * s2 + b2 * x_t + c2
                y = rch[:, 0] * s1 + rch[:, 1] * s2 + rch[:, 2] * x_t + rch[:, 3]
                legal &= (ns1 >= -GUARD) & (ns1 <= GUARD)
                legal &= (ns2 >= -GUARD) & (ns2 <= GUARD)
                legal &= (y >= -GUARD) & (y <= GUARD)
                outs[:, t] = y
                s1, s2 = ns1, ns2
            if not legal.any():
                continue
            enc = np.zeros(int(legal.sum()), dtype=np.int64)
            leg_outs = outs[legal]
            for t in range(N):
                enc = enc * 9 + (leg_outs[:, t] + GUARD)
            hit_mask = np.isin(enc, tenc_order)
            for ri in np.nonzero(hit_mask)[0]:
                key = tuple(int(v) for v in leg_outs[ri])
                if key in targets and key not in realized:
                    realized[key] = [int(v) for v in abc_arr[abc_i]] + \
                        [int(v) for v in rch[legal][ri]]
    return realized, {"pairs_enumerated": int(n_pairs)}


# ---------------------------------------------------------------------------
# B_EP affine final-output exhaustion
# ---------------------------------------------------------------------------

def ep_affine_exhaust(episodes, coef_bound=3):
    streams = [tuple(r["stream"]) for r in episodes]
    req = [r["required_final_output"] for r in episodes]
    ranges = range(-coef_bound, coef_bound + 1)
    matches = []
    M = 0
    for coeffs in itertools.product(ranges, repeat=6):
        M += 1
        ok = True
        for st, y in zip(streams, req):
            v = coeffs[0] + sum(coeffs[i + 1] * st[i] for i in range(5))
            if v != y:
                ok = False
                break
        if ok:
            matches.append(list(coeffs))
    return matches, {"tuples_enumerated": M}


# ---------------------------------------------------------------------------
# B_CONTR readout certificates
# ---------------------------------------------------------------------------

def contr_readout_certs(layouts, required, max_nz=4):
    X = np.array(layouts, dtype=np.int64)
    y = np.array(required, dtype=np.int64)
    n_cells = X.shape[1]
    supports = [c for k in range(1, max_nz + 1)
                for c in itertools.combinations(range(n_cells), k)]
    n_cand = 0
    affine_sol = []
    gate_sol = []
    for S in supports:
        Xs = X[:, S]
        k = len(S)
        for sg in set(itertools.product((-1, 1), repeat=k)):
            n_cand += 1
            v = Xs @ np.array(sg, dtype=np.int64)
            for b in DOMAIN:
                pred = v + b
                if np.array_equal(pred, y):
                    affine_sol.append({"support": list(S),
                                       "signs": list(sg), "bias": int(b)})
                for c in DOMAIN:
                    if np.array_equal(np.where(pred >= c, 1, 0), y):
                        gate_sol.append({"support": list(S),
                                         "signs": list(sg), "bias": int(b),
                                         "cut": int(c)})
    return {"candidates_enumerated": n_cand,
            "n_supports": len(supports),
            "affine_solutions": affine_sol,
            "gate_solutions": gate_sol}
