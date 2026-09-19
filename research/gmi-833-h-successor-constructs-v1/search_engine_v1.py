"""Family-blind enumeration and exact-agreement search over G_H.

FREEZE_V1.md section 6, FREEZE_V1_ADDENDUM.md A4/A5/A8. Exact rational
arithmetic. The engine receives a scope id and a response vector; it never
receives a family name, a family identifier or a candidate menu.
"""
from fractions import Fraction as Q
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import grammar_h_v1 as G          # noqa: E402

HEAD_ORDER = ("S1", "S2", "BIAS", "STATE", "RESP")
BODY_ORDER = ("ARG", "PARAM")
BODY2_ORDER = ("U", "PARAM2")
ZERO = Q(0)


def occurs(tree, leaf):
    if tree[0] == "LEAF":
        return tree[1] == leaf
    for kid in tree[1:]:
        if occurs(kid, leaf):
            return True
    return False


def _depends(tree, leaf, leaves):
    if not occurs(tree, leaf):
        return False
    others = [x for x in leaves if x != leaf and occurs(tree, x)]
    return G.depends_on(tree, leaf, others)


def _affine(tree, leaf, leaves):
    if not occurs(tree, leaf):
        return True
    others = [x for x in leaves if x != leaf and occurs(tree, x)]
    return G.affine_in(tree, leaf, others + [leaf])


def build_tables():
    heads = []
    for t in G.all_trees(G.HEAD_BUDGET, G.HEAD_LEAVES):
        heads.append({
            "tree": t, "n": G.nodes(t), "fn": G.compile_tree(t, HEAD_ORDER),
            "occ_S1": occurs(t, "S1"), "occ_S2": occurs(t, "S2"),
            "occ_RESP": occurs(t, "RESP"), "key": G.show(t),
            "occ_STATE": occurs(t, "STATE"),
        })
    bodies = []
    for t in G.all_trees(G.BODY_BUDGET, G.BODY_LEAVES):
        bodies.append({"tree": t, "n": G.nodes(t),
                       "fn": G.compile_tree(t, BODY_ORDER),
                       "occ_PARAM": occurs(t, "PARAM"), "key": G.show(t)})
    bodies2 = []
    for t in G.all_trees(G.BODY2_BUDGET, G.BODY2_LEAVES):
        bodies2.append({"tree": t, "n": G.nodes(t),
                        "fn": G.compile_tree(t, BODY2_ORDER), "key": G.show(t)})
    return heads, bodies, bodies2


def head_sig(tree):
    lv = list(HEAD_ORDER)
    return (_depends(tree, "S1", lv), _depends(tree, "S2", lv),
            _depends(tree, "STATE", lv), _depends(tree, "RESP", lv),
            _affine(tree, "S1", lv), _affine(tree, "S2", lv))


def sig_dict(sig):
    return {"dep_S1": sig[0], "dep_S2": sig[1], "dep_STATE": sig[2],
            "dep_RESP": sig[3], "aff_S1": sig[4], "aff_S2": sig[5]}


def body_sig(tree):
    return _affine(tree, "ARG", ["ARG", "PARAM"])


def body2_sig(tree):
    return _affine(tree, "U", ["U", "PARAM2"])


def fold_L1(body_fn, op, p, row):
    acc = G.COMBINER_IDENTITY[op]
    A = row["A"]
    P = row["P"]
    if op == "ADD":
        for i in range(G.N_INDEX):
            acc = acc + body_fn((A[i], P[i % p]))
    else:
        for i in range(G.N_INDEX):
            acc = acc * body_fn((A[i], P[i % p]))
    return acc


def fold_L2(body1_fn, op1, p, body2_fn, op2, row):
    M = row["M"]
    A = row["A"]
    Qc = row["Q"]
    acc2 = G.COMBINER_IDENTITY[op2]
    for j in range(G.W_STAGE):
        acc = G.COMBINER_IDENTITY[op1]
        if op1 == "ADD":
            for i in range(G.N_INDEX):
                acc = acc + body1_fn((A[i], M[i % p][j]))
        else:
            for i in range(G.N_INDEX):
                acc = acc * body1_fn((A[i], M[i % p][j]))
        u = body2_fn((acc, Qc[j]))
        if op2 == "ADD":
            acc2 = acc2 + u
        else:
            acc2 = acc2 * u
    return acc2


def emit(head_fn, s1, s2, bias, state, kind):
    if kind == "NONE":
        return head_fn((s1, s2, bias, state, ZERO))
    if kind == "RSUM":
        tot = ZERO
        for y in G.RESPONSE_SET:
            tot = tot + head_fn((s1, s2, bias, state, y))
        return tot
    best = None
    best_e = None
    for y in G.RESPONSE_SET:
        e = head_fn((s1, s2, bias, state, y))
        if best_e is None or e < best_e:
            best_e = e
            best = y
    return best


def configs():
    """All (r, L, ops, p, kind) configurations, family-blind."""
    out = []
    for L in (1, 2):
        rs = (1, 2) if L == 1 else (1,)
        for r in rs:
            nops = r if L == 1 else 2
            for ops in _op_tuples(nops):
                for p in G.TIE_MODULI:
                    for kind in G.REDUCTIONS:
                        charge = 0
                        if r == 2:
                            charge += 1
                        if L == 2:
                            charge += 1
                        if p != G.N_INDEX:
                            charge += 1
                        if kind != "NONE":
                            charge += 1
                        out.append({"r": r, "L": L, "ops": ops, "p": p,
                                    "kind": kind, "charge": charge})
    return out


def _op_tuples(k):
    if k == 1:
        return [("ADD",), ("MUL",)]
    return [(a, b) for a in G.COMBINERS for b in G.COMBINERS]


def _flags(cfg):
    return {"r": cfg["r"], "L": cfg["L"], "p": cfg["p"], "kind": cfg["kind"],
            "ops": cfg["ops"]}


def full_match(cfg, bodies_e, body2_e, head_e, eco, idxs, order=None):
    """Exact agreement on every row of the slice. `order` may permute the rows
    only when the head does not read STATE, in which case the program is
    memoryless and the row order cannot change the verdict."""
    if order is not None:
        idxs = order
    state = ZERO
    p = cfg["p"]
    kind = cfg["kind"]
    for t in idxs:
        row = eco["rows"][t]
        bias = row["Q"][0]
        if cfg["L"] == 2:
            s1 = fold_L2(bodies_e[0]["fn"], cfg["ops"][0], p,
                         body2_e["fn"], cfg["ops"][1], row)
            s2 = ZERO
        else:
            s1 = fold_L1(bodies_e[0]["fn"], cfg["ops"][0], p, row)
            s2 = (fold_L1(bodies_e[1]["fn"], cfg["ops"][1], p, row)
                  if cfg["r"] == 2 else ZERO)
        out = emit(head_e["fn"], s1, s2, bias, state, kind)
        if out != eco["y"][t]:
            return False
        state = out
    return True


def search(eco, idxs, tables, max_cost, gs_only=False, tie_break=None,
           collect_all_at_cost=True):
    """Ascending-cost exact-agreement search. Returns the cheapest matches.

    Two filter rows are used, both of them registered slice rows: a memoryless
    program is first tested on the slice row whose response value is rarest,
    and a program whose head reads STATE is first tested on the first slice row
    where the delay cell is still zero. Both are exact necessary conditions for
    a full-slice match, so neither changes the result; they only decide which
    row is examined first.
    """
    heads, bodies, bodies2 = tables
    cfgs = configs()
    if gs_only:
        cfgs = [c for c in cfgs
                if c["r"] == 1 and c["L"] == 1 and c["p"] == G.N_INDEX
                and c["kind"] == "NONE" and c["ops"] == ("ADD",)]
        heads = [h for h in heads if not h["occ_S2"] and not h["occ_RESP"]]

    freq = {}
    for t in idxs:
        freq[eco["y"][t]] = freq.get(eco["y"][t], 0) + 1
    order = sorted(idxs, key=lambda t: (freq[eco["y"][t]], t))
    rare = order[0]
    first = idxs[0]

    head_variant = {}
    for want_s2 in (False, True):
        for want_resp in (False, True):
            for want_s1 in (False, True):
                for stateful in (False, True):
                    sel = {}
                    for h in heads:
                        if h["occ_S2"] != want_s2:
                            continue
                        if h["occ_RESP"] != want_resp:
                            continue
                        if want_s1 and not h["occ_S1"]:
                            continue
                        if h["occ_STATE"] != stateful:
                            continue
                        sel.setdefault(h["n"], []).append(h)
                    head_variant[(want_s2, want_resp, want_s1,
                                  stateful)] = sel
    by_n_body = {}
    for b in bodies:
        by_n_body.setdefault(b["n"], []).append(b)
    by_n_body2 = {}
    for b in bodies2:
        by_n_body2.setdefault(b["n"], []).append(b)

    fold1_cache = {}
    stage1_cache = {}
    stage2_cache = {}

    def f1(bi, op, p, t):
        key = (bi["key"], op, p, t)
        hit = fold1_cache.get(key)
        if hit is None:
            hit = fold_L1(bi["fn"], op, p, eco["rows"][t])
            fold1_cache[key] = hit
        return hit

    def u_at(b1, op1, p, t):
        key = (b1["key"], op1, p, t)
        hit = stage1_cache.get(key)
        if hit is None:
            row = eco["rows"][t]
            A = row["A"]
            M = row["M"]
            fn = b1["fn"]
            vals = []
            for j in range(G.W_STAGE):
                acc = G.COMBINER_IDENTITY[op1]
                if op1 == "ADD":
                    for i in range(G.N_INDEX):
                        acc = acc + fn((A[i], M[i % p][j]))
                else:
                    for i in range(G.N_INDEX):
                        acc = acc * fn((A[i], M[i % p][j]))
                vals.append(acc)
            hit = tuple(vals)
            stage1_cache[key] = hit
        return hit

    def s_l2(b1, op1, p, b2, op2, t):
        key = (b1["key"], op1, p, b2["key"], op2, t)
        hit = stage2_cache.get(key)
        if hit is None:
            uv = u_at(b1, op1, p, t)
            qc = eco["rows"][t]["Q"]
            acc = G.COMBINER_IDENTITY[op2]
            f2 = b2["fn"]
            if op2 == "ADD":
                for j in range(G.W_STAGE):
                    acc = acc + f2((uv[j], qc[j]))
            else:
                for j in range(G.W_STAGE):
                    acc = acc * f2((uv[j], qc[j]))
            hit = acc
            stage2_cache[key] = hit
        return hit

    visited = 0
    for cost in range(1, max_cost + 1):
        hits = []
        for cfg in cfgs:
            budget = cost - cfg["charge"]
            if budget < 2:
                continue
            p = cfg["p"]
            kind = cfg["kind"]
            plain = (kind == "NONE")
            for stateful in (False, True):
                sel = head_variant[(cfg["r"] == 2, kind != "NONE",
                                    cfg["L"] == 2, stateful)]
                trow = first if stateful else rare
                torder = None if stateful else order
                y_t = eco["y"][trow]
                bias_t = eco["rows"][trow]["Q"][0]
                for nh in sorted(sel):
                    if nh > budget - 1:
                        continue
                    hs = sel[nh]
                    if not hs:
                        continue
                    hfns = [h["fn"] for h in hs]
                    nfn = len(hfns)
                    hcache = {}

                    def matching(s1v, s2v, _hfns=hfns, _hc=hcache,
                                 _b=bias_t, _y=y_t, _n=nfn):
                        k = (s1v, s2v)
                        got = _hc.get(k)
                        if got is None:
                            vec = (s1v, s2v, _b, ZERO, ZERO)
                            acc = []
                            for hi in range(_n):
                                if _hfns[hi](vec) == _y:
                                    acc.append(hi)
                            got = tuple(acc)
                            if len(_hc) < 300000:
                                _hc[k] = got
                        return got

                    def slow(s1v, s2v, _hfns=hfns, _b=bias_t, _y=y_t,
                             _n=nfn, _k=kind):
                        acc = []
                        for hi in range(_n):
                            if emit(_hfns[hi], s1v, s2v, _b, ZERO, _k) == _y:
                                acc.append(hi)
                        return acc

                    rest = budget - nh
                    if cfg["L"] == 2:
                        for n1 in sorted(by_n_body):
                            n2 = rest - n1
                            if n2 not in by_n_body2:
                                continue
                            for b1 in by_n_body[n1]:
                                if p != G.N_INDEX and not b1["occ_PARAM"]:
                                    continue
                                for b2 in by_n_body2[n2]:
                                    s1 = s_l2(b1, cfg["ops"][0], p, b2,
                                              cfg["ops"][1], trow)
                                    visited += nfn
                                    cand = (matching(s1, ZERO) if plain
                                            else slow(s1, ZERO))
                                    for hi in cand:
                                        h = hs[hi]
                                        if full_match(cfg, [b1], b2, h, eco,
                                                      idxs, torder):
                                            hits.append((cfg, [b1], b2, h))
                    elif cfg["r"] == 1:
                        if rest not in by_n_body:
                            continue
                        for ba in by_n_body[rest]:
                            if p != G.N_INDEX and not ba["occ_PARAM"]:
                                continue
                            s1 = f1(ba, cfg["ops"][0], p, trow)
                            visited += nfn
                            cand = (matching(s1, ZERO) if plain
                                    else slow(s1, ZERO))
                            for hi in cand:
                                h = hs[hi]
                                if full_match(cfg, [ba], None, h, eco, idxs,
                                              torder):
                                    hits.append((cfg, [ba], None, h))
                    else:
                        for na in sorted(by_n_body):
                            nb = rest - na
                            if nb not in by_n_body:
                                continue
                            for ba in by_n_body[na]:
                                sa = None
                                for bb in by_n_body[nb]:
                                    if p != G.N_INDEX and not (
                                            ba["occ_PARAM"]
                                            or bb["occ_PARAM"]):
                                        continue
                                    if sa is None:
                                        sa = f1(ba, cfg["ops"][0], p, trow)
                                    s2 = f1(bb, cfg["ops"][1], p, trow)
                                    visited += nfn
                                    cand = (matching(sa, s2) if plain
                                            else slow(sa, s2))
                                    for hi in cand:
                                        h = hs[hi]
                                        if full_match(cfg, [ba, bb], None, h,
                                                      eco, idxs, torder):
                                            hits.append((cfg, [ba, bb], None,
                                                         h))
        if hits:
            rendered = []
            for cfg, bs, b2, h in hits:
                rendered.append((
                    G.render(_flags(cfg), [b["tree"] for b in bs],
                             b2["tree"] if b2 is not None else None,
                             h["tree"]),
                    cfg, bs, b2, h))
            rendered.sort(key=lambda z: z[0])
            return {"cost": cost, "matches": rendered, "visited": visited,
                    "found": True}
    return {"cost": None, "matches": [], "visited": visited, "found": False}


def describe(entry):
    render_s, cfg, bs, b2, h = entry
    flags = _flags(cfg)
    hs = sig_dict(head_sig(h["tree"]))
    bsg = {"aff_ARG": body_sig(bs[0]["tree"])}
    b2g = {"aff_U": body2_sig(b2["tree"])} if b2 is not None else None
    cls = G.classify(flags, hs, bsg, b2g)
    return {
        "render": render_s,
        "equivalence_key": G.equivalence_key(
            flags, [b["tree"] for b in bs],
            b2["tree"] if b2 is not None else None, h["tree"]),
        "flags": {"r": flags["r"], "L": flags["L"], "p": flags["p"],
                  "kind": flags["kind"], "ops": list(flags["ops"])},
        "bodies": [G.show(b["tree"]) for b in bs],
        "body2": G.show(b2["tree"]) if b2 is not None else None,
        "head": G.show(h["tree"]),
        "head_predicates": hs,
        "body_predicates": bsg,
        "body2_predicates": b2g,
        "class": cls,
        "cost": G.charged_cost(flags, [b["tree"] for b in bs],
                               b2["tree"] if b2 is not None else None,
                               h["tree"]),
    }


def signature_groups(tables, gs_only=False):
    heads, bodies, bodies2 = tables
    if gs_only:
        heads = [h for h in heads if not h["occ_S2"] and not h["occ_RESP"]]
    hg = {}
    for h in heads:
        key = (h["n"], h["occ_S1"], h["occ_S2"], h["occ_RESP"],
               head_sig(h["tree"]))
        hg[key] = hg.get(key, 0) + 1
    bg = {}
    for b in bodies:
        key = (b["n"], b["occ_PARAM"], body_sig(b["tree"]))
        bg[key] = bg.get(key, 0) + 1
    b2g = {}
    for b in bodies2:
        key = (b["n"], body2_sig(b["tree"]))
        b2g[key] = b2g.get(key, 0) + 1
    return hg, bg, b2g


def base_rate(tables, max_cost, gs_only=False):
    """Exact structural-class census of the whole well-formed enumeration up to
    max_cost. Integer counts only. Used as the registered null."""
    hg, bg, b2g = signature_groups(tables, gs_only)
    cfgs = configs()
    if gs_only:
        cfgs = [c for c in cfgs
                if c["r"] == 1 and c["L"] == 1 and c["p"] == G.N_INDEX
                and c["kind"] == "NONE" and c["ops"] == ("ADD",)]
    counts = {}
    total = 0
    for cfg in cfgs:
        flags = _flags(cfg)
        budget = max_cost - cfg["charge"]
        if budget < 2:
            continue
        want_s2 = cfg["r"] == 2
        want_resp = cfg["kind"] != "NONE"
        want_s1 = cfg["L"] == 2
        for hkey, hn in hg.items():
            nh, occ_s1, occ_s2, occ_resp, hsig = hkey
            if occ_s2 != want_s2 or occ_resp != want_resp:
                continue
            if want_s1 and not occ_s1:
                continue
            rest = budget - nh
            if rest < 1:
                continue
            hsd = sig_dict(hsig)
            if cfg["L"] == 2:
                for bkey, bn in bg.items():
                    n1, occ_p, aff_arg = bkey
                    if cfg["p"] != G.N_INDEX and not occ_p:
                        continue
                    n2 = rest - n1
                    for b2key, b2n in b2g.items():
                        if b2key[0] != n2:
                            continue
                        cls = G.classify(flags, hsd, {"aff_ARG": aff_arg},
                                         {"aff_U": b2key[1]})
                        counts[cls] = counts.get(cls, 0) + hn * bn * b2n
                        total += hn * bn * b2n
            elif cfg["r"] == 1:
                for bkey, bn in bg.items():
                    n1, occ_p, aff_arg = bkey
                    if n1 != rest:
                        continue
                    if cfg["p"] != G.N_INDEX and not occ_p:
                        continue
                    cls = G.classify(flags, hsd, {"aff_ARG": aff_arg}, None)
                    counts[cls] = counts.get(cls, 0) + hn * bn
                    total += hn * bn
            else:
                for bkey, bn in bg.items():
                    n1, occ_p, aff_arg = bkey
                    for b2key, b2n in bg.items():
                        n2, occ_p2, _ = b2key
                        if n1 + n2 != rest:
                            continue
                        if cfg["p"] != G.N_INDEX and not (occ_p or occ_p2):
                            continue
                        cls = G.classify(flags, hsd, {"aff_ARG": aff_arg},
                                         None)
                        counts[cls] = counts.get(cls, 0) + hn * bn * b2n
                        total += hn * bn * b2n
    return {"counts": counts, "total": total}
