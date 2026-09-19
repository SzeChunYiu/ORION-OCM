"""Family-blind enumeration and exact-agreement search over G_H, the exhaustive
matcher pool of FREEZE_V1.md section 8.1, the blind held-out construction of
section 8.2, and the dual base-rate census of section 8.5.

Exact rational arithmetic. The engine receives a scope id and a response
vector for the SEARCH rows; it never receives a family name, a family
identifier or a candidate menu. The held-out construction receives programs
and channel rows only and is asserted by a test to receive no response.
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
    """(affine in U, depends on U) — the second is new here, section 6.2."""
    return (_affine(tree, "U", ["U", "PARAM2"]),
            _depends(tree, "U", ["U", "PARAM2"]))


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


def program_output(cfg, bodies_e, body2_e, head_e, row, state):
    """One row's output for a program, given the delay state. Exact."""
    p = cfg["p"]
    bias = row["Q"][0]
    if cfg["L"] == 2:
        s1 = fold_L2(bodies_e[0]["fn"], cfg["ops"][0], p, body2_e["fn"],
                     cfg["ops"][1], row)
        s2 = ZERO
    else:
        s1 = fold_L1(bodies_e[0]["fn"], cfg["ops"][0], p, row)
        s2 = (fold_L1(bodies_e[1]["fn"], cfg["ops"][1], p, row)
              if cfg["r"] == 2 else ZERO)
    return emit(head_e["fn"], s1, s2, bias, state, cfg["kind"])


def full_match(cfg, bodies_e, body2_e, head_e, rows, ys, idxs, order=None):
    """Exact agreement on every listed row. `order` may permute the rows only
    when the head does not read STATE."""
    if order is not None:
        idxs = order
    state = ZERO
    for t in idxs:
        out = program_output(cfg, bodies_e, body2_e, head_e, rows[t], state)
        if out != ys[t]:
            return False
        state = out
    return True


def search(eco, idxs, tables, max_cost, gs_only=False, all_costs=False):
    """Ascending-cost exact-agreement search.

    With all_costs=False (the recovery), returns the cheapest matches and
    stops at that cost. With all_costs=True (the pool of section 8.1), no
    stratum is skipped once a match is found: every match at every cost up to
    max_cost is returned, with the per-cost counts.

    Two filter rows are used, both registered search rows: a memoryless
    program is first tested on the search row whose response is rarest; a
    program whose head reads STATE is first tested on the first search row,
    where the delay cell is still zero. Both are exact necessary conditions,
    so neither changes the result.
    """
    heads, bodies, bodies2 = tables
    cfgs = configs()
    if gs_only:
        cfgs = [c for c in cfgs
                if c["r"] == 1 and c["L"] == 1 and c["p"] == G.N_INDEX
                and c["kind"] == "NONE" and c["ops"] == ("ADD",)]
        heads = [h for h in heads if not h["occ_S2"] and not h["occ_RESP"]]
    rows = eco["rows"]
    ys = eco["y"]

    freq = {}
    for t in idxs:
        freq[ys[t]] = freq.get(ys[t], 0) + 1
    order = sorted(idxs, key=lambda t: (freq[ys[t]], t))
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
            hit = fold_L1(bi["fn"], op, p, rows[t])
            fold1_cache[key] = hit
        return hit

    def u_at(b1, op1, p, t):
        key = (b1["key"], op1, p, t)
        hit = stage1_cache.get(key)
        if hit is None:
            row = rows[t]
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
            qc = rows[t]["Q"]
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
    per_cost = {}
    all_hits = []
    first_cost = None
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
                y_t = ys[trow]
                bias_t = rows[trow]["Q"][0]
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
                                        if full_match(cfg, [b1], b2, h, rows,
                                                      ys, idxs, torder):
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
                                if full_match(cfg, [ba], None, h, rows, ys,
                                              idxs, torder):
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
                                                      rows, ys, idxs, torder):
                                            hits.append((cfg, [ba, bb], None,
                                                         h))
        per_cost[cost] = len(hits)
        if hits:
            if first_cost is None:
                first_cost = cost
            all_hits.extend(_render_hits(hits))
            if not all_costs:
                break
    all_hits.sort(key=lambda z: (z[5], z[0]))
    if first_cost is None:
        return {"cost": None, "matches": [], "visited": visited,
                "found": False, "per_cost": per_cost}
    cheapest = [z for z in all_hits if z[5] == first_cost]
    return {"cost": first_cost, "matches": cheapest, "visited": visited,
            "found": True, "per_cost": per_cost, "pool": all_hits}


def _render_hits(hits):
    out = []
    for cfg, bs, b2, h in hits:
        flags = _flags(cfg)
        btrees = [b["tree"] for b in bs]
        b2t = b2["tree"] if b2 is not None else None
        out.append((G.render(flags, btrees, b2t, h["tree"]), cfg, bs, b2, h,
                    G.charged_cost(flags, btrees, b2t, h["tree"])))
    return out


def describe(entry):
    render_s, cfg, bs, b2, h = entry[0], entry[1], entry[2], entry[3], entry[4]
    flags = _flags(cfg)
    hs = sig_dict(head_sig(h["tree"]))
    bsg = {"aff_ARG": body_sig(bs[0]["tree"])}
    if b2 is not None:
        a_u, d_u = body2_sig(b2["tree"])
        b2g = {"aff_U": a_u, "dep_U": d_u}
    else:
        b2g = None
    cls = G.classify(flags, hs, bsg, b2g)
    btrees = [b["tree"] for b in bs]
    b2t = b2["tree"] if b2 is not None else None
    return {
        "render": render_s,
        "equivalence_key": G.equivalence_key(flags, btrees, b2t, h["tree"]),
        "normal_key": G.normal_key(flags, btrees, b2t, h["tree"]),
        "flags": {"r": flags["r"], "L": flags["L"], "p": flags["p"],
                  "kind": flags["kind"], "ops": list(flags["ops"])},
        "bodies": [G.show(b["tree"]) for b in bs],
        "body2": G.show(b2["tree"]) if b2 is not None else None,
        "head": G.show(h["tree"]),
        "head_predicates": hs,
        "body_predicates": bsg,
        "body2_predicates": b2g,
        "mul_bank_head_read": G.mul_bank_head_read(flags, hs, b2g),
        "class": cls,
        "cost": G.charged_cost(flags, btrees, b2t, h["tree"]),
    }


# ------------------------------------------- held-out construction, 8.2

def construct_heldout(pool, cand_rows, target=12, forced_first=None):
    """FREEZE_V1.md section 8.2. Reads programs and channel rows ONLY.

    `pool` is a list of (render, cfg, bodies, body2, head, cost) entries.
    Returns (chosen candidate indices, per-candidate disagreement flags,
    number of candidates examined). A candidate is appended when the pool's
    outputs on it are not all equal; every member's delay state advances only
    on appended rows. `forced_first`, when given, is a candidate index that is
    always the first held-out row (the pinned E34 tie row).
    """
    states = [ZERO] * len(pool)
    chosen = []
    disagree = []
    examined = 0
    for k, row in enumerate(cand_rows):
        if len(chosen) >= target:
            break
        examined += 1
        outs = [program_output(e[1], e[2], e[3], e[4], row, states[i])
                for i, e in enumerate(pool)]
        distinct = len(set(outs)) > 1
        forced = (forced_first is not None and k == forced_first)
        disagree.append(distinct)
        if distinct or forced:
            chosen.append(k)
            states = outs
    return chosen, disagree, examined


def evaluate_on(pool, cand_rows, chosen, ys):
    """Which pool members reproduce the chosen rows exactly, in order, with
    the delay cell reset to zero. Returns a list of booleans."""
    out = []
    for e in pool:
        state = ZERO
        ok = True
        for j, k in enumerate(chosen):
            got = program_output(e[1], e[2], e[3], e[4], cand_rows[k], state)
            if got != ys[j]:
                ok = False
                break
            state = got
        out.append(ok)
    return out


# ------------------------------------------------------- census, 8.5

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


def base_rate(tables, max_cost, gs_only=False, classify=None):
    """Exact structural-class census of the whole well-formed enumeration up
    to max_cost, under the section 6.2 classifier (or a supplied one, for the
    hostile that compares it with the parent's rule). Integer counts only."""
    classify = classify or G.classify
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
                        cls = classify(flags, hsd, {"aff_ARG": aff_arg},
                                       {"aff_U": b2key[1][0],
                                        "dep_U": b2key[1][1]})
                        counts[cls] = counts.get(cls, 0) + hn * bn * b2n
                        total += hn * bn * b2n
            elif cfg["r"] == 1:
                for bkey, bn in bg.items():
                    n1, occ_p, aff_arg = bkey
                    if n1 != rest:
                        continue
                    if cfg["p"] != G.N_INDEX and not occ_p:
                        continue
                    cls = classify(flags, hsd, {"aff_ARG": aff_arg}, None)
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
                        cls = classify(flags, hsd, {"aff_ARG": aff_arg},
                                       None)
                        counts[cls] = counts.get(cls, 0) + hn * bn * b2n
                        total += hn * bn * b2n
    return {"counts": counts, "total": total}
