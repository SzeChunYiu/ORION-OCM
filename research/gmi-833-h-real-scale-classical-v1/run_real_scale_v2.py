"""Stage 1, revival pass V2. laptop-billy only.

Applies exactly the three levers registered in FREEZE_V2_ADDENDUM.md and nothing
else. run_real_scale_v1.py is imported unchanged and every routine it owns —
grammar, enumeration, quotient, classifier, generic fitter, cost model, exact
evaluation, slices, arms, remint, verification slices — is reused verbatim.

  L1  exchangeable presentation of the three non-sequential ecologies
      (E_H02, E_H03, E_H04) under one registered target-independent
      permutation; E_H01 is left sequential because its row is about sequence.
  L2  the search loss at SIGMA_H03 is the absolute closeness criterion that
      FREEZE_V1_ECOLOGY_ADDENDUM.md A3 already froze as that scope's protected
      interface, instead of squared error.
  L3  route B is given its own least-squares path (central differences + QR)
      so that independence is tested on implementation, not on optimiser
      strength, and agreement is recorded on the recovered structural class.
"""
from __future__ import print_function
from fractions import Fraction
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_v1 as G           # noqa: E402
import grammar_v2 as G2          # noqa: E402
import run_real_scale_v1 as R    # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "REAL_RUNS")
ORDER_MULT = 2654435761          # Knuth multiplicative hash, registered
BOUNDARY_DROP = 64


def registered_order(n):
    """L1: one fixed, target-independent permutation.

    Rows 0 .. n80-1 are permuted among themselves; rows n80+64 .. n-1 are
    permuted among themselves. The two regions never mix, so the contiguous
    tail stays temporally disjoint from the fit region while no slice can
    exploit source order.
    """
    n80 = int(n * 0.8)
    lo = np.arange(n80, dtype=np.int64)
    hi = np.arange(n80 + BOUNDARY_DROP, n, dtype=np.int64)
    klo = (lo * ORDER_MULT) % (2 ** 32)
    khi = (hi * ORDER_MULT) % (2 ** 32)
    return np.concatenate([lo[np.argsort(klo, kind="stable")],
                           hi[np.argsort(khi, kind="stable")]]), n80


def reorder(eco):
    n = len(eco["y"]) if eco["kind"] == "onehot" else len(eco["yi"])
    order, n80 = registered_order(n)
    out = dict(eco)
    if eco["kind"] == "onehot":
        out["sym"] = eco["sym"][order]
        out["y"] = eco["y"][order]
    else:
        out["Xi"] = eco["Xi"][order]
        out["yi"] = eco["yi"][order]
    out["_order_applied"] = True
    out["_tail_start"] = int(n80)
    return out


def slices_v2(eco):
    """FREEZE_V2_ADDENDUM.md section 4: the slice residues rotate, so the V2
    held-out set is disjoint from every set V1 searched or evaluated on."""
    n = len(eco["y"]) if eco["kind"] == "onehot" else len(eco["yi"])
    ts = eco.get("_tail_start", int(n * 0.8))
    i = np.arange(n)
    m = i % 5
    return {"fit": i[(m != 1) & (m != 2) & (i < ts)],
            "search": i[(m == 1) & (i < ts)],
            "held": i[(m == 2) & (i < ts)],
            "tail": i[i >= ts],
            "remint_fit": i[(m == 0) & (i < ts)],
            "remint_held": i[(m == 3) & (i < ts)]}


def lsq_fit_b(bf, hn, hs, rs, X, y, d):
    """Route B: central differences at step 2, solved by QR least squares."""
    base = R.predict(bf, hn, hs, rs, X, np.zeros(d), 0.0)
    cols = []
    for j in range(d + 1):
        p = np.zeros(d)
        bi = 0.0
        if j < d:
            p[j] = 2.0
        else:
            bi = 2.0
        hi = R.predict(bf, hn, hs, rs, X, p, bi)
        if j < d:
            p[j] = -2.0
        else:
            bi = -2.0
        lo = R.predict(bf, hn, hs, rs, X, p, bi)
        cols.append((hi - lo) / 4.0)
    Z = np.stack(cols, axis=1)
    v = np.linalg.lstsq(Z, y - base, rcond=None)[0]
    return v[:d], float(v[d])


def search_route_b(kept, eco, sl):
    d = eco["d"]
    kind = eco["loss"]
    X, y = R.design(eco, sl["search"][:R.N_SEARCH])
    rs_ = np.random.RandomState(833833)
    out = []
    for (_, _, br, hr, b, h, st) in kept:
        bf, hn, hs = R.body_fn(b), R.head_fn_np(h), R.head_fn_scalar(h)
        cand = []
        try:
            if R.affine_in_params(bf, hn, hs, st, X, d):
                p, bi = lsq_fit_b(bf, hn, hs, st, X, y, d)
                if kind != "squared":
                    p, bi, L = R.cd_fit(bf, hn, hs, st, X, y, d, kind, p, bi, 4)
                else:
                    L = R.loss_of(kind, R.predict(bf, hn, hs, st, X, p, bi), y)
                cand.append(L)
        except (ValueError, np.linalg.LinAlgError):
            pass
        best = None
        for _ in range(40):
            p = rs_.randint(-4, 5, size=d).astype(np.float64) * 0.5
            bi = float(rs_.randint(-4, 5)) * 0.5
            try:
                L = R.loss_of(kind, R.predict(bf, hn, hs, st, X, p, bi), y)
            except (ValueError, FloatingPointError):
                continue
            if np.isfinite(L) and (best is None or L < best):
                best, bp, bb = L, p.copy(), bi
        if best is not None:
            p, bi, L = R.cd_fit(bf, hn, hs, st, X, y, d, kind, bp, bb, 4)
            cand.append(L)
        if not cand:
            continue
        out.append({"loss": min(cand), "body": br, "head": hr,
                    "nodes": G.size(b) + G.size(h)})
    out.sort(key=lambda r: (r["loss"], r["nodes"], r["body"], r["head"]))
    return out


def run_scope_v2(name, eco, verify_rows):
    sl = slices_v2(eco)
    pairs, meta = G2.build_candidates_v2()
    n = len(eco["y"]) if eco["kind"] == "onehot" else len(eco["yi"])
    rec = {"scope": name, "n_rows": int(n), "grammar": meta,
           "n_fit": int(len(sl["fit"])), "n_held": int(len(sl["held"])),
           "n_tail": int(len(sl["tail"])), "n_search": int(len(sl["search"])),
           "levers": {"order_applied": bool(eco.get("_order_applied", False)),
                      "order_mult": ORDER_MULT, "search_loss": eco["loss"]}}
    d = eco["d"]
    Xs, ys = R.design(eco, sl["search"][:R.N_SCREEN])
    t0 = time.time()
    scored = R.screen(pairs, Xs, ys, eco["loss"], d)
    kept = scored[:R.KEEP]
    Xf, yf = R.design(eco, sl["search"][:R.N_SEARCH])
    ranked = []
    for (_, _, br, hr, b, h, st) in kept:
        p, bi, L, how = R.generic_fit(b, h, st, Xf, yf, d, eco["loss"])
        ranked.append({"loss": L, "body": br, "head": hr,
                       "nodes": G.size(b) + G.size(h),
                       "reads_state": bool(st), "fit": how})
    ranked.sort(key=lambda r: (r["loss"], r["nodes"], r["body"], r["head"]))
    print("[%s] screen+search %.1fs winner %s | %s loss=%.6g"
          % (name, time.time() - t0, ranked[0]["body"], ranked[0]["head"],
             ranked[0]["loss"]))
    rb = search_route_b(kept, eco, sl)
    w = ranked[0]
    b, h = R.parse_expr(w["body"]), R.parse_expr(w["head"])
    cls = G.classify(b, h)
    rbc = (G.classify(R.parse_expr(rb[0]["body"]), R.parse_expr(rb[0]["head"]))
           ["class"] if rb else None)
    rec["winner"] = {"body": w["body"], "head": w["head"], "class": cls["class"],
                     "attributes": cls, "search_loss": w["loss"],
                     "fit_route": w["fit"]}
    rec["search"] = {"ranked_top10": ranked[:10], "route_b_top10": rb[:10],
                     "route_b_class": rbc,
                     "route_b_agrees": bool(rbc == cls["class"]),
                     "route_b_same_expression": bool(
                         rb and rb[0]["body"] == w["body"]
                         and rb[0]["head"] == w["head"]),
                     "screen_top20": [{"loss": s[0], "body": s[2], "head": s[3]}
                                      for s in scored[:20]]}
    print("[%s] class=%s routeB_class=%s agrees=%s"
          % (name, cls["class"], rbc, rec["search"]["route_b_agrees"]))

    params, bias, how = R.fit_arm(b, h, cls["reads_state"], eco, sl["fit"],
                                  eco["loss"])
    rec["winner"].update({"fit_rows": int(len(sl["fit"])),
                          "params": [R.fs(p) for p in params],
                          "bias": R.fs(bias), "full_fit_route": how})
    ev = {}
    for slot in ("held", "tail"):
        e = exact_stats(b, h, cls["reads_state"], eco, sl[slot], params, bias,
                        eco["loss"])
        ev[slot] = e
        print("[%s] %s n=%d %s" % (name, slot, e["n"],
                                   e.get("errors", e.get("sse"))))
    rec["winner"]["evaluation"] = ev

    eco2 = dict(eco)
    sl2 = {"search": sl["remint_fit"], "fit": sl["remint_fit"],
           "held": sl["remint_held"], "tail": sl["tail"]}
    Xr, yr = R.design(eco2, sl2["search"][:R.N_SCREEN])
    sc2 = R.screen(pairs, Xr, yr, eco["loss"], d)[:R.KEEP]
    Xr2, yr2 = R.design(eco2, sl2["search"][:R.N_SEARCH])
    r2 = []
    for (_, _, br, hr, bb, hh, st) in sc2:
        p, bi, L, _h = R.generic_fit(bb, hh, st, Xr2, yr2, d, eco["loss"])
        r2.append({"loss": L, "body": br, "head": hr,
                   "nodes": G.size(bb) + G.size(hh)})
    r2.sort(key=lambda r: (r["loss"], r["nodes"], r["body"], r["head"]))
    c2 = G.classify(R.parse_expr(r2[0]["body"]), R.parse_expr(r2[0]["head"]))
    rec["remint"] = {"body": r2[0]["body"], "head": r2[0]["head"],
                     "class": c2["class"],
                     "class_matches": bool(c2["class"] == cls["class"]),
                     "expression_matches": bool(r2[0]["body"] == w["body"]
                                                and r2[0]["head"] == w["head"]),
                     "n_rows": int(len(sl["remint_fit"]))}
    print("[%s] remint class=%s matches=%s"
          % (name, c2["class"], rec["remint"]["class_matches"]))

    vidx = sl["held"][:verify_rows]
    vstat = exact_stats(b, h, cls["reads_state"], eco, vidx, params, bias,
                        eco["loss"])
    v = {"rows": int(len(vidx)), "slot": "held_prefix"}
    if eco["kind"] == "onehot":
        v["syms"] = [int(x) for x in eco["sym"][vidx]]
        v["y"] = [int(x) for x in eco["y"][vidx]]
        v["partial_errors"] = vstat["errors"]
    else:
        v["Xi"] = [[int(x) for x in r] for r in eco["Xi"][vidx]]
        v["yi"] = [int(x) for x in eco["yi"][vidx]]
        v["xden"] = (list(eco["xden"]) if isinstance(eco["xden"], tuple)
                     else int(eco["xden"]))
        v["yden"] = int(eco["yden"])
        v["partial_sse"] = vstat["sse"]
    rec["verification"] = v
    return rec, sl, b, h, cls, params, bias, ranked


# ------------------------- streaming exact evaluation ------------------------
# Same arithmetic as run_real_scale_v1.exact_eval, evaluated row by row so that
# no slice ever materialises 10^5 x 32 Fraction objects at once. laptop-billy
# has other tenants; the V1 SIGMA_H04 run was killed for memory.

def exact_stats(body, head, rs, eco, idx, params, bias, loss, cap=20000):
    st = Fraction(0)
    err = 0
    sse = Fraction(0)
    sae = Fraction(0)
    pos = 0
    vals = set()
    ys = set()
    n = len(idx)
    if eco["kind"] == "onehot":
        d = eco["d"]
        base = sum((G.ev(body, {"ARG": Fraction(0), "PARAM": params[j]})
                    for j in range(d)), Fraction(0))
        pre = [base - G.ev(body, {"ARG": Fraction(0), "PARAM": params[k]})
               + G.ev(body, {"ARG": Fraction(1), "PARAM": params[k]})
               for k in range(d)]
        syms = eco["sym"][idx]
        yy = eco["y"][idx]
        for t in range(n):
            out = G.ev(head, {"S": pre[int(syms[t])], "BIAS": bias, "STATE": st})
            y = Fraction(int(yy[t]))
            if (Fraction(1) if out > 0 else Fraction(0)) != y:
                err += 1
            if out > 0:
                pos += 1
            if len(vals) < cap:
                vals.add(out)
            if len(ys) < cap:
                ys.add(y)
            if rs:
                st = out
    else:
        xd = eco["xden"]
        Xs = eco["Xi"][idx]
        Ys = eco["yi"][idx]
        yden = eco["yden"]
        for t in range(n):
            row = Xs[t]
            tot = Fraction(0)
            for j in range(len(row)):
                q = xd[j] if isinstance(xd, tuple) else xd
                tot += G.ev(body, {"ARG": Fraction(int(row[j]), q),
                                   "PARAM": params[j]})
            out = G.ev(head, {"S": tot, "BIAS": bias, "STATE": st})
            if rs:
                st = out
            y = Fraction(int(Ys[t]), yden)
            r = out - y
            sse += r * r
            sae += r if r >= 0 else -r
            if out > 0:
                pos += 1
            if len(vals) < cap:
                vals.add(out)
            if len(ys) < cap:
                ys.add(y)
    nd = {"distinct_predictions": len(vals), "distinct_responses": len(ys),
          "predicted_positive": pos, "predicted_negative": n - pos,
          "both_classes_predicted": bool(0 < pos < n)}
    nd["non_degenerate"] = bool(nd["distinct_predictions"] > 1
                                and nd["distinct_responses"] > 1)
    out = {"n": n, "nondegeneracy": nd}
    if loss == "decision":
        out["errors"] = err
    else:
        out["sse"] = R.fs(sse)
        out["sae"] = R.fs(sae)
    return out


def exact_constant_stats(eco, idx, c):
    """Exact SSE / sign errors of a constant arm, streaming."""
    sse = Fraction(0)
    err = 0
    yden = eco["yden"]
    Ys = eco["yi"][idx]
    cpos = 1 if c > 0 else 0
    for t in range(len(idx)):
        y = Fraction(int(Ys[t]), yden)
        r = c - y
        sse += r * r
        if (1 if y > 0 else 0) != cpos:
            err += 1
    return {"n": len(idx), "sse": R.fs(sse), "sign_errors": err}


# --------------------------- memory-safe SIGMA_H04 arms ----------------------
# Identical arithmetic to run_real_scale_v1.arms_H04; the only change is that
# the landmark and degree-two designs are accumulated in row blocks instead of
# being materialised whole. The V1 run was killed while materialising them.

CHUNK = 4000


def kernel_block(X, L):
    d2 = ((X[:, None, :] - L[None, :, :]) ** 2).sum(axis=2)
    K = 1.0 / (1.0 + d2)
    return np.round(K * R.KERNEL_DEN) / R.KERNEL_DEN


def _blocks(n, c=CHUNK):
    for i in range(0, n, c):
        yield i, min(i + c, n)


def ols_blocked(make, n, k, y):
    A = np.zeros((k + 1, k + 1))
    b = np.zeros(k + 1)
    for i, j in _blocks(n):
        Z = np.concatenate([make(i, j), np.ones((j - i, 1))], axis=1)
        A += Z.T.dot(Z)
        b += Z.T.dot(y[i:j])
    A += 1e-8 * np.eye(k + 1)
    return np.linalg.solve(A, b)


def predict_blocked(make, n, beta):
    out = np.empty(n)
    for i, j in _blocks(n):
        Z = np.concatenate([make(i, j), np.ones((j - i, 1))], axis=1)
        out[i:j] = Z.dot(beta)
    return out


def arms_H04_v2(eco, sl):
    arms = {}
    p, bi, how = R.fit_arm(R.AFFINE_BODY, R.AFFINE_HEAD, False, eco, sl["fit"],
                           "squared")
    arms["affine"] = {"body": G.render(R.AFFINE_BODY),
                      "head": G.render(R.AFFINE_HEAD),
                      "params": [R.fs(x) for x in p], "bias": R.fs(bi),
                      "fit_route": how,
                      "cost": G.program_cost(R.AFFINE_BODY, R.AFFINE_HEAD,
                                             eco["d"], False)}
    for slot in ("held", "tail"):
        arms["affine"][slot] = exact_stats(R.AFFINE_BODY, R.AFFINE_HEAD, False,
                                           eco, sl[slot], p, bi, "squared")
    Xf, yf = R.design(eco, sl["fit"])
    Xh, _ = R.design(eco, sl["held"])
    d = eco["d"]
    yh = [Fraction(int(v), eco["yden"]) for v in eco["yi"][sl["held"]]]
    arms["landmark"] = {}
    for q in (1, 2, 4, 8, 16, 32, 64):
        step = max(1, Xf.shape[0] // q)
        L = Xf[[j * step for j in range(q)]]
        beta = ols_blocked(lambda i, j: kernel_block(Xf[i:j], L),
                           Xf.shape[0], q, yf)
        pr = [R.rat(v) for v in predict_blocked(
            lambda i, j: kernel_block(Xh[i:j], L), Xh.shape[0], beta)]
        arms["landmark"][str(q)] = {
            "sse_held": R.fs(R.exact_sse_from_pred(pr, yh)),
            "ops": q * (3 * d + 4) + 2 * q, "storage": q * (d + 1) + 1,
            "total": q * (3 * d + 4) + 2 * q + q * (d + 1) + 1}
    nb = d + d * (d + 1) // 2
    beta = ols_blocked(lambda i, j: R.basis2(Xf[i:j]), Xf.shape[0], nb, yf)
    pr = [R.rat(v) for v in predict_blocked(
        lambda i, j: R.basis2(Xh[i:j]), Xh.shape[0], beta)]
    arms["basis2"] = {"n_features": int(nb),
                      "sse_held": R.fs(R.exact_sse_from_pred(pr, yh)),
                      "ops": 3 * nb, "storage": nb + 1, "total": 4 * nb + 1}
    return arms


def arms_H01_v2(eco, sl, ranked):
    """The registered stateless comparison arm.

    Preferred: the best stateless survivor of the same blind ranking. If the
    ranking contains no stateless survivor at all, the canonical stateless
    program MUL(ARG,PARAM) | ADD(S,BIAS) is fitted instead and labelled as such,
    so the comparison arm always exists.
    """
    stateless = None
    for r in ranked:
        if not r["reads_state"]:
            stateless = r
            break
    if stateless is None:
        stateless = {"body": G.render(R.AFFINE_BODY),
                     "head": G.render(R.AFFINE_HEAD),
                     "source": "CANONICAL_STATELESS_FALLBACK"}
    else:
        stateless = dict(stateless)
        stateless["source"] = "BEST_STATELESS_SURVIVOR_OF_THE_SAME_RANKING"
    b2, h2 = R.parse_expr(stateless["body"]), R.parse_expr(stateless["head"])
    p2, bi2, how2 = R.fit_arm(b2, h2, False, eco, sl["fit"], "decision")
    arms = {"stateless_best": {"body": stateless["body"],
                               "head": stateless["head"],
                               "source": stateless["source"],
                               "params": [R.fs(x) for x in p2],
                               "bias": R.fs(bi2), "fit_route": how2}}
    for slot in ("held", "tail"):
        arms["stateless_best"][slot] = exact_stats(b2, h2, False, eco, sl[slot],
                                                   p2, bi2, "decision")
    yfit = eco["y"][sl["fit"]]
    maj = 1 if yfit.mean() > 0.5 else 0
    arms["majority_class"] = {"predict": int(maj)}
    for slot in ("held", "tail"):
        ys = eco["y"][sl[slot]]
        arms["majority_class"][slot] = {"n": int(len(ys)),
                                        "errors": int((ys != maj).sum())}
    return arms


def arms_H02_v2(eco, sl):
    _, yf = R.design(eco, sl["fit"])
    c = R.rat(float(yf.mean()))
    arms = {"best_constant": {"value": R.fs(c)}}
    for slot in ("held", "tail"):
        arms["best_constant"][slot] = exact_constant_stats(eco, sl[slot], c)
    pos = int((yf > 0).sum())
    maj = 1 if pos * 2 > len(yf) else 0
    arms["majority_sign"] = {"predict": maj}
    for slot in ("held", "tail"):
        Ys = eco["yi"][sl[slot]]
        err = int(((Ys > 0).astype(np.int64) != maj).sum())
        arms["majority_sign"][slot] = {"n": int(len(Ys)), "errors": err}
    return arms


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    src, d1b, pcm, lines, _ = R.load_sources()
    with open(os.path.join(OUT, "sources.json"), "w") as f:
        json.dump(src, f, indent=1, sort_keys=True)
    for name in ("H01", "H02", "H03", "H04"):
        if which not in ("all", name):
            continue
        t0 = time.time()
        if name == "H01":
            eco = R.ecology_H01(d1b)            # L1 does not apply: sequential
        elif name == "H02":
            eco = reorder(R.ecology_H02(pcm))
        elif name == "H03":
            eco = reorder(R.ecology_H03(lines))
            eco["loss"] = "absolute"            # L2
        else:
            eco = reorder(R.ecology_H04(pcm))
        vr = 4000 if name in ("H01", "H03") else 1200
        rec, sl, b, h, cls, params, bias, ranked_all = run_scope_v2(
            "SIGMA_" + name, eco, vr)
        if name == "H01":
            rec["arms"] = arms_H01_v2(eco, sl, ranked_all)
        elif name == "H02":
            rec["arms"] = arms_H02_v2(eco, sl)
        elif name == "H03":
            rec["arms"] = R.arms_H03(eco, sl)
        else:
            rec["arms"] = arms_H04_v2(eco, sl)
        rec["winner"]["cost"] = G.program_cost(b, h, eco["d"], cls["reads_state"])
        rec["winner"]["table_crossover_m"] = G.table_crossover(
            b, h, cls["reads_state"])
        rec["seconds"] = round(time.time() - t0, 1)
        with open(os.path.join(OUT, "scope_%s.json" % name), "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        print("[%s] WROTE scope_%s.json in %.1fs" % (name, name, rec["seconds"]))


if __name__ == "__main__":
    main()
