"""Stage 1b (V2 levers applied): negative twins, randomised nulls, and the registered automaton.

Runs on laptop-billy against the same sha256-verified real sources. Consumes the
committed REAL_RUNS/scope_*.json parameters; emits REAL_RUNS/controls.json.
Every emitted number is an exact integer or exact rational.
"""
from __future__ import print_function
from fractions import Fraction as F
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_v1 as G                      # noqa: E402
import grammar_v2 as G2                     # noqa: E402
import run_real_scale_v1 as R               # noqa: E402
import run_real_scale_v2 as V2              # noqa: E402

OUT = R.OUT
N_NULL = 200


def frac(s):
    n, d = s.split("/")
    return F(int(n), int(d))


def symbol_scores(body, params, d):
    """Exact fold value per one-hot symbol. 27 exact rationals."""
    base = sum((G.ev(body, {"ARG": F(0), "PARAM": params[j]}) for j in range(d)), F(0))
    out = []
    for k in range(d):
        out.append(base - G.ev(body, {"ARG": F(0), "PARAM": params[k]})
                   + G.ev(body, {"ARG": F(1), "PARAM": params[k]}))
    return out


def run_automaton(head, S, bias, syms, y, reads_state):
    """Exact memoised run. Returns (errors, states, transitions)."""
    memo = {}
    states = {}
    trans = {}
    st = F(0)
    err = 0
    for t in range(len(syms)):
        c = int(syms[t])
        key = (c, st)
        v = memo.get(key)
        if v is None:
            v = G.ev(head, {"S": S[c], "BIAS": bias, "STATE": st})
            memo[key] = v
        if st not in states:
            states[st] = len(states)
        if (F(1) if v > 0 else F(0)) != y[t]:
            err += 1
        trans[(c, st)] = v
        if reads_state:
            st = v
    return err, states, trans


def affine_exact_sse(P, B, Xi, Yi, xden, yden, pden):
    """Exact SSE for a prediction sum_i p_i x_i + b, via integer numerators."""
    L = pden * xden
    num = Xi.dot(np.asarray(P, dtype=np.int64)) + int(B) * xden
    scale = L // yden
    resid = num - np.asarray(Yi, dtype=np.int64) * scale
    tot = 0
    for v in resid.tolist():
        tot += v * v
    return F(tot, L * L)


def main():
    src, d1b, pcm, lines, _ = R.load_sources()
    res = {"n_null": N_NULL}

    # ---- SIGMA_H01: twin ecology, automaton, order-randomised null ----------
    rec = json.load(open(os.path.join(OUT, "scope_H01.json")))
    eco = R.ecology_H01(d1b)
    sl = V2.slices_v2(eco)
    body = R.parse_expr(rec["winner"]["body"])
    head = R.parse_expr(rec["winner"]["head"])
    cls = G.classify(body, head)
    params = [frac(x) for x in rec["winner"]["params"]]
    bias = frac(rec["winner"]["bias"])
    S = symbol_scores(body, params, eco["d"])
    hidx = sl["held"]
    syms = eco["sym"][hidx]
    yv = [F(int(v)) for v in eco["y"][hidx]]
    t0 = time.time()
    err, states, trans = run_automaton(head, S, bias, syms, yv, cls["reads_state"])
    sb = R.parse_expr(rec["arms"]["stateless_best"]["body"])
    sh = R.parse_expr(rec["arms"]["stateless_best"]["head"])
    sp = [frac(x) for x in rec["arms"]["stateless_best"]["params"]]
    sbi = frac(rec["arms"]["stateless_best"]["bias"])
    S2 = symbol_scores(sb, sp, eco["d"])
    err2, _, _ = run_automaton(sh, S2, sbi, syms, yv, False)
    res["H01_automaton"] = {
        "reachable_states": len(states),
        "alphabet": eco["d"],
        "transition_entries": len(trans),
        "state_values": [R.fs(s) for s in sorted(states)][:16],
        "held_errors_stateful": err,
        "held_errors_stateless": err2,
        "n_held": int(len(hidx)),
        "seconds": round(time.time() - t0, 1)}
    print("H01 automaton states=%d stateful_err=%d stateless_err=%d (%.1fs)"
          % (len(states), err, err2, time.time() - t0))

    rs = np.random.RandomState(8330001)
    beat = 0
    t0 = time.time()
    for i in range(N_NULL):
        perm = rs.permutation(len(hidx))
        e1, _, _ = run_automaton(head, S, bias, syms[perm],
                                 [yv[j] for j in perm], cls["reads_state"])
        e2, _, _ = run_automaton(sh, S2, sbi, syms[perm],
                                 [yv[j] for j in perm], False)
        if e1 < e2:
            beat += 1
    res["H01_null"] = {"controls": N_NULL, "stateful_strictly_better": beat,
                       "seconds": round(time.time() - t0, 1)}
    print("H01 null: stateful beat stateless in %d/%d order-randomised controls"
          % (beat, N_NULL))

    # twin ecology: identical symbol multiset, order destroyed
    rs2 = np.random.RandomState(8330002)
    twin = dict(eco)
    order = rs2.permutation(len(eco["sym"]))
    tsym = eco["sym"][order]
    twin = {"kind": "onehot", "sym": tsym[:-1],
            "y": (tsym[1:] == R.SEP).astype(np.int64), "d": 27,
            "xden": 1, "yden": 1, "loss": "decision"}
    pairs, _ = G2.build_candidates_v2()
    sl_t = V2.slices_v2(twin)
    Xt, yt = R.design(twin, sl_t["search"][:R.N_SCREEN])
    sct = R.screen(pairs, Xt, yt, twin["loss"], twin["d"])[:R.KEEP]
    Xt2, yt2 = R.design(twin, sl_t["search"][:R.N_SEARCH])
    ranked_t = []
    for (_, _, br, hr, bb, hh, st) in sct:
        _p, _b, L, _h = R.generic_fit(bb, hh, st, Xt2, yt2, twin["d"], twin["loss"])
        ranked_t.append({"loss": L, "body": br, "head": hr,
                         "nodes": G.size(bb) + G.size(hh)})
    ranked_t.sort(key=lambda r: (r["loss"], r["nodes"], r["body"], r["head"]))
    wt = ranked_t[0]
    ct = G.classify(R.parse_expr(wt["body"]), R.parse_expr(wt["head"]))
    res["H01_twin"] = {"body": wt["body"], "head": wt["head"],
                       "class": ct["class"], "reads_state": ct["reads_state"],
                       "selects_stateless": (not ct["reads_state"])}
    print("H01 twin class=%s reads_state=%s" % (ct["class"], ct["reads_state"]))

    # ---- SIGMA_H02: row-permuted design null --------------------------------
    rec2 = json.load(open(os.path.join(OUT, "scope_H02.json")))
    eco2 = V2.reorder(R.ecology_H02(pcm))
    sl2 = V2.slices_v2(eco2)
    Xf, yf = R.design(eco2, sl2["fit"])
    Xh_i = eco2["Xi"][sl2["held"]]
    Yh_i = eco2["yi"][sl2["held"]]
    cden = R.RAT_DEN
    cval = int(round(float(yf.mean()) * cden))
    const_sse = affine_exact_sse([0] * 32, cval, Xh_i, Yh_i, eco2["xden"],
                                 eco2["yden"], cden)
    rs3 = np.random.RandomState(8330003)
    lower = 0
    t0 = time.time()
    for i in range(N_NULL):
        perm = rs3.permutation(len(yf))
        beta = R.ols(Xf[perm], yf)
        P = [int(round(v * cden)) for v in beta[:32]]
        B = int(round(beta[32] * cden))
        s = affine_exact_sse(P, B, Xh_i, Yh_i, eco2["xden"], eco2["yden"], cden)
        if s < const_sse:
            lower += 1
    res["H02_null"] = {"controls": N_NULL, "control_beats_constant": lower,
                       "constant_sse": R.fs(const_sse),
                       "seconds": round(time.time() - t0, 1)}
    print("H02 null: %d/%d row-permuted controls beat the constant arm"
          % (lower, N_NULL))
    res["H02_true_affine_sse"] = rec2["winner"]["evaluation"]["held"].get("sse")

    with open(os.path.join(OUT, "controls.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    print("WROTE controls.json")


if __name__ == "__main__":
    main()
