# -*- coding: utf-8 -*-
"""AG3 route A -- the presentation-equivalence strength order, computed exactly.

Everything here is integer/set arithmetic.  No float is constructed anywhere, and
no claim depends on one.  Definitions, universe, gates and falsifiers are fixed in
FREEZE_V1.md, committed before this file existed.

    python3 -I -B ag3_presentation_equivalence_v1.py
"""

import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

A_LETTERS = (0, 1)              # the external alphabet {a, b}
S0 = 0                          # the start state of every presentation
PROG_MAXLEN = 2                 # |prog(x)| <= 2
W_WINDOW = 6                    # behaviour window
K_LADDER = (1, 2, 3, 5)         # the registered overhead ladder; 5 is AJ5's bound
MAX_COMPILE_LEN = PROG_MAXLEN * max(K_LADDER)   # 10


# ---------------------------------------------------------------- state maps

def ident(n):
    return tuple(range(n))


def compose(t2, t1):
    """Apply t1 first, then t2."""
    return tuple(t2[t1[s]] for s in range(len(t1)))


def basis(n):
    """The frozen generating set T_n of FREEZE_V1.md section 3."""
    idn = ident(n)
    succ = tuple((s + 1) % n for s in range(n))
    pred = tuple((s - 1) % n for s in range(n))
    const0 = tuple(0 for _ in range(n))
    tau01 = tuple({0: 1, 1: 0}.get(s, s) for s in range(n))
    out = []
    for t in (idn, succ, pred, const0, tau01):
        if t not in out:
            out.append(t)
    return tuple(out)


def obs(regime, n):
    if regime == "BINARY":
        return tuple(1 if s == 0 else 0 for s in range(n))
    return tuple(range(n))


# ---------------------------------------------------------------- presentations

def words_upto(nsym, maxlen):
    out = [()]
    cur = [()]
    for _ in range(maxlen):
        nxt = []
        for w in cur:
            for f in range(nsym):
                nxt.append(w + (f,))
        out.extend(nxt)
        cur = nxt
    return tuple(out)


def build_universe():
    pres = []
    for regime in ("BINARY", "FULL"):
        for n in (2, 3):
            T = basis(n)
            for f0, f1 in itertools.permutations(range(len(T)), 2):
                sig = (T[f0], T[f1])
                for wa in words_upto(2, PROG_MAXLEN):
                    for wb in words_upto(2, PROG_MAXLEN):
                        pres.append((n, sig, (wa, wb), regime))
    return tuple(pres)


def act(sig, n, word):
    t = ident(n)
    for f in word:
        t = compose(sig[f], t)
    return t


def monoid(sig, n):
    seen = {ident(n)}
    frontier = [ident(n)]
    while frontier:
        nxt = []
        for t in frontier:
            for g in sig:
                u = compose(g, t)
                if u not in seen:
                    seen.add(u)
                    nxt.append(u)
        frontier = nxt
    return frozenset(seen)


def realizable_by_len(sig, n, maxlen):
    """realizable[L] = set of state maps realized by some word of length <= L."""
    cur = {ident(n)}
    out = [frozenset(cur)]
    for _ in range(maxlen):
        nxt = set(cur)
        for t in cur:
            for g in sig:
                nxt.add(compose(g, t))
        cur = nxt
        out.append(frozenset(cur))
    return tuple(out)


def derive(p):
    n, sig, prog, regime = p
    o = obs(regime, n)
    letter = tuple(act(sig, n, prog[x]) for x in A_LETTERS)
    reach = {S0}
    frontier = [S0]
    while frontier:
        nxt = []
        for s in frontier:
            for t in letter:
                if t[s] not in reach:
                    reach.add(t[s])
                    nxt.append(t[s])
        frontier = nxt
    beh = []
    cur = {(): S0}
    for _ in range(W_WINDOW + 1):
        for w in sorted(cur):
            beh.append((len(w), w, o[cur[w]]))
        nxt = {}
        for w, s in cur.items():
            for x in A_LETTERS:
                nxt[w + (x,)] = letter[x][s]
        cur = nxt
    beh_full = tuple(v for _, _, v in sorted(beh))
    beh_short = tuple(v for L, _, v in sorted(beh) if L <= W_WINDOW - 1)
    return {
        "n": n, "sig": sig, "prog": prog, "regime": regime, "obs": o,
        "letter": letter, "reach": frozenset(reach),
        "monoid": monoid(sig, n),
        "real": realizable_by_len(sig, n, MAX_COMPILE_LEN),
        "beh": beh_full, "beh_short": beh_short,
    }


# ---------------------------------------------------------------- the levels

def state_bijections(d1, d2):
    """Bijections S_{n1} -> S_{n2} fixing s0 and preserving the observation."""
    if d1["n"] != d2["n"]:
        return ()
    n = d1["n"]
    out = []
    for perm in itertools.permutations(range(n)):
        if perm[S0] != S0:
            continue
        if any(d2["obs"][perm[s]] != d1["obs"][s] for s in range(n)):
            continue
        out.append(perm)
    return tuple(out)


def canon_l1(d):
    """Canonical form under (symbol renaming, state relabeling). L1 = equality."""
    n = d["n"]
    best = None
    for perm in state_bijections(d, d):
        inv = [0] * n
        for s in range(n):
            inv[perm[s]] = s
        for rho in itertools.permutations(range(2)):
            sig2 = tuple(tuple(perm[d["sig"][rho.index(j)][inv[s]]] for s in range(n))
                         for j in range(2))
            prog2 = tuple(tuple(rho[f] for f in d["prog"][x]) for x in A_LETTERS)
            cand = (d["regime"], n, sig2, prog2)
            if best is None or cand < best:
                best = cand
    return best


def canon_l2(d):
    """Canonical form for definitional/term equivalence. L2 = equality."""
    n = d["n"]
    best = None
    for perm in state_bijections(d, d):
        inv = [0] * n
        for s in range(n):
            inv[perm[s]] = s
        mon = tuple(sorted(tuple(perm[t[inv[s]]] for s in range(n)) for t in d["monoid"]))
        let = tuple(tuple(perm[d["letter"][x][inv[s]]] for s in range(n)) for x in A_LETTERS)
        cand = (d["regime"], n, mon, let)
        if best is None or cand < best:
            best = cand
    return best


def encodings(src, dst, use_reach=True, need_obs=True, need_inj=True):
    """Injective maps src.reach -> S_{dst.n} fixing s0 and preserving observation."""
    dom = sorted(src["reach"]) if use_reach else list(range(src["n"]))
    if S0 not in dom:
        dom = sorted(set(dom) | {S0})
    others = [s for s in dom if s != S0]
    targets = [t for t in range(dst["n"]) if t != S0]
    if need_inj and len(dom) > dst["n"]:
        return ()
    picks = (itertools.permutations(targets, len(others)) if need_inj
             else itertools.product(range(dst["n"]), repeat=len(others)))
    out = []
    for pick in picks:
        e = {S0: S0}
        for s, t in zip(others, pick):
            e[s] = t
        if need_obs and any(dst["obs"][e[s]] != src["obs"][s] for s in dom):
            continue
        out.append(e)
    return tuple(out)


def _one_way_k(src, dst, use_reach=True, need_obs=True, cap=MAX_COMPILE_LEN,
               need_inj=True):
    """Least integer k such that every src letter compiles into dst within k*|prog|."""
    dom = sorted(src["reach"]) if use_reach else list(range(src["n"]))
    best = None
    for e in encodings(src, dst, use_reach, need_obs, need_inj):
        worst = 0
        ok = True
        for x in A_LETTERS:
            L = len(src["prog"][x])
            if L == 0:
                continue                       # the empty program compiles to the empty word
            target = {}
            for s in dom:
                target[e[s]] = e[src["letter"][x][s]]
            found = None
            for m in range(0, cap + 1):
                hit = False
                for t in dst["real"][m]:
                    if all(t[a] == b for a, b in target.items()):
                        hit = True
                        break
                if hit:
                    found = m
                    break
            if found is None:
                ok = False
                break
            need = -(-found // L)              # ceil(found / L), integers only
            if need > worst:
                worst = need
        if ok and (best is None or worst < best):
            best = worst
    return best


def kmin(d1, d2, use_reach=True, need_obs=True, need_inj=True):
    """Least overhead factor at which the pair is compiler-equivalent, or None."""
    a = _one_way_k(d1, d2, use_reach, need_obs, MAX_COMPILE_LEN, need_inj)
    if a is None:
        return None
    b = _one_way_k(d2, d1, use_reach, need_obs, MAX_COMPILE_LEN, need_inj)
    if b is None:
        return None
    return a if a > b else b


def certificate(src, dst, k):
    """An encoding witnessing that src compiles into dst within overhead k."""
    dom = sorted(src["reach"])
    for e in encodings(src, dst, True, True):
        lens = {}
        ok = True
        for x in A_LETTERS:
            L = len(src["prog"][x])
            if L == 0:
                lens[x] = 0
                continue
            target = dict((e[s], e[src["letter"][x][s]]) for s in dom)
            found = None
            for m in range(0, k * L + 1):
                for t in dst["real"][m]:
                    if all(t[a] == b for a, b in target.items()):
                        found = m
                        break
                if found is not None:
                    break
            if found is None:
                ok = False
                break
            lens[x] = found
        if ok:
            return {"encoding": dict((str(a), b) for a, b in sorted(e.items())),
                    "compiled_lengths": dict((str(x), lens[x]) for x in A_LETTERS)}
    return None


def verify_certificate(src, dst, cert, k):
    """Independent re-check of a stored L3 certificate. Used by the detector."""
    if cert is None:
        return False
    e = dict((int(a), b) for a, b in cert["encoding"].items())
    dom = sorted(src["reach"])
    if sorted(e) != dom:
        return False
    if len(set(e.values())) != len(e):
        return False
    if e.get(S0) != S0:
        return False
    for s in dom:
        if dst["obs"][e[s]] != src["obs"][s]:
            return False
    for x in A_LETTERS:
        L = len(src["prog"][x])
        m = cert["compiled_lengths"][str(x)]
        if m > k * L:
            return False
        target = dict((e[s], e[src["letter"][x][s]]) for s in dom)
        if not any(all(t[a] == b for a, b in target.items()) for t in dst["real"][m]):
            return False
    return True


# ---------------------------------------------------------------- partitions

def partition_from_labels(labels):
    first = {}
    out = []
    for i, lab in enumerate(labels):
        if lab not in first:
            first[lab] = i
        out.append(first[lab])
    return tuple(out)


def partition_from_edges(nelem, edges):
    parent = list(range(nelem))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in edges:
        a, b = find(i), find(j)
        if a != b:
            parent[max(a, b)] = min(a, b)
    return partition_from_labels([find(i) for i in range(nelem)])


def pair_count(part):
    sizes = {}
    for lab in part:
        sizes[lab] = sizes.get(lab, 0) + 1
    return sum(s * (s - 1) // 2 for s in sizes.values())


def meet(p, q):
    return partition_from_labels(list(zip(p, q)))


def join(p, q):
    edges = []
    for part in (p, q):
        firstseen = {}
        for i, lab in enumerate(part):
            if lab in firstseen:
                edges.append((firstseen[lab], i))
            else:
                firstseen[lab] = i
    return partition_from_edges(len(p), edges)


def refines(p, q):
    """p <= q: every p-class sits inside a q-class (p is the finer/stronger level)."""
    seen = {}
    for a, b in zip(p, q):
        if a in seen:
            if seen[a] != b:
                return False
        else:
            seen[a] = b
    return True


def generated_sublattice(gens, cap=256):
    elems = set(gens)
    changed = True
    while changed and len(elems) <= cap:
        changed = False
        for p, q in itertools.combinations(sorted(elems), 2):
            for r in (meet(p, q), join(p, q)):
                if r not in elems:
                    elems.add(r)
                    changed = True
    return elems


# ---------------------------------------------------------------- main

def build():
    uni = build_universe()
    derived = [derive(p) for p in uni]
    index = dict((uni[i], i) for i in range(len(uni)))
    return uni, derived, index


def named_witness(n, syms, prog, regime):
    T = basis(n)
    return (n, tuple(T[i] for i in syms), prog, regime)


def witness_specs():
    """Registered witness pairs. W-* separate the levels; PW-* are the registered
    analogues of the witness KINDS the merged parents already own."""
    return {
        "W-RENAME": (named_witness(3, (1, 0), ((0,), (0, 0)), "BINARY"),
                     named_witness(3, (1, 2), ((0,), (1,)), "BINARY"),
                     "definitional extension: same generated monoid, same external "
                     "actions, no symbol bijection -- the L2 witness no merged package had"),
        "W-STATESPACE": (named_witness(2, (1, 0), ((0,), ()), "BINARY"),
                         named_witness(3, (4, 0), ((0,), ()), "BINARY"),
                         "same presented object through a state-space change, so no state "
                         "bijection exists and term equivalence cannot hold"),
        "W-OVERHEAD": (named_witness(3, (1, 0), ((0,), ()), "FULL"),
                       named_witness(3, (2, 0), ((0, 0), ()), "FULL"),
                       "under full observation the encoding is forced to the identity and "
                       "succ costs two pred steps, so overhead 1 does not suffice"),
        "PW-RELABEL": (named_witness(3, (1, 3), ((0,), (1,)), "BINARY"),
                       named_witness(3, (2, 3), ((0,), (1,)), "BINARY"),
                       "the relabeling kind certified by gmi-833-g0-grammar-bias-v1 "
                       "(24 certified isometric relabelings, 0 invariant failures)"),
        "PW-COMPILER": (named_witness(2, (1, 0), ((0,), (0, 0)), "BINARY"),
                        named_witness(3, (4, 0), ((0,), (0, 0)), "BINARY"),
                        "the charged-overhead lowering kind certified by "
                        "gmi-833-aj5-g0-lowering-v1 (lower_ops <= 5 * G0_steps)"),
    }


LEVEL_NAMES = ["L1", "L2"] + ["L3(%d)" % k for k in K_LADDER] + ["L4"]


def level_vector(d1, d2):
    """Membership of one pair in every registered level.

    L3 is the frozen section-2 clause INTERSECTED with L4.  Section 1 of the
    freeze requires every strength to imply equality of the presented object;
    section 2's clause does not deliver that on its own, and section 1 governs.
    The raw clause is reported separately as L3raw so the defect is visible.
    """
    k = kmin(d1, d2)
    same = d1["beh"] == d2["beh"] and d1["regime"] == d2["regime"]
    v = {"L1": canon_l1(d1) == canon_l1(d2),
         "L2": canon_l2(d1) == canon_l2(d2),
         "L4": same,
         "kmin_raw": k}
    for kk in K_LADDER:
        v["L3(%d)" % kk] = same and k is not None and k <= kk
        v["L3raw(%d)" % kk] = k is not None and k <= kk
    return v


def minimal_levels(v, order):
    """The levels holding for this pair that no other holding level refines."""
    holding = [nm for nm in LEVEL_NAMES if v[nm]]
    out = []
    for nm in holding:
        if not any(other != nm and order.get("%s<=%s" % (other, nm), False)
                   for other in holding):
            out.append(nm)
    return out


def main():                                                    # noqa: C901
    uni, derived, index = build()
    N = len(uni)

    l1 = partition_from_labels([canon_l1(d) for d in derived])
    l2 = partition_from_labels([canon_l2(d) for d in derived])
    l4 = partition_from_labels([(d["regime"], d["beh"]) for d in derived])
    l4_short = partition_from_labels([(d["regime"], d["beh_short"]) for d in derived])

    byclass = {}
    for i, lab in enumerate(l4):
        byclass.setdefault(lab, []).append(i)
    k_edges = {}
    for lab in sorted(byclass):
        for a, b in itertools.combinations(byclass[lab], 2):
            k = kmin(derived[a], derived[b])
            if k is not None:
                k_edges[(a, b)] = k

    # The raw section-2 clause, measured across the whole comparable universe:
    # how often does bounded mutual simulation relate presentations of DIFFERENT
    # objects?  This is result AG3L-2.
    reg = {}
    for i, d in enumerate(derived):
        reg.setdefault(d["regime"], []).append(i)
    raw_cross = 0
    raw_example = None
    for r in sorted(reg):
        for a, b in itertools.combinations(reg[r], 2):
            if l4[a] == l4[b]:
                continue
            if kmin(derived[a], derived[b]) is not None:
                raw_cross += 1
                if raw_example is None:
                    raw_example = [uni[a], uni[b]]

    l3 = {}
    for kk in K_LADDER:
        edges = [ab for ab, k in k_edges.items() if k <= kk]
        l3[kk] = {"edges": len(edges), "closure": partition_from_edges(N, edges),
                  "edge_list": edges}

    # --- gate: L1 and L2 imply equality of the presented object -------------
    viol_beh = {"L1": 0, "L2": 0}
    for part, name in ((l1, "L1"), (l2, "L2")):
        cls = {}
        for i, lab in enumerate(part):
            cls.setdefault(lab, []).append(i)
        for lab in cls:
            for a, b in itertools.combinations(cls[lab], 2):
                if derived[a]["beh"] != derived[b]["beh"] or \
                        derived[a]["regime"] != derived[b]["regime"]:
                    viol_beh[name] += 1

    # --- L3 certificates and their independent re-check ---------------------
    cert_checked = 0
    cert_bad = 0
    for (a, b) in l3[K_LADDER[0]]["edge_list"]:
        c1 = certificate(derived[a], derived[b], K_LADDER[0])
        c2 = certificate(derived[b], derived[a], K_LADDER[0])
        cert_checked += 2
        if not verify_certificate(derived[a], derived[b], c1, K_LADDER[0]):
            cert_bad += 1
        if not verify_certificate(derived[b], derived[a], c2, K_LADDER[0]):
            cert_bad += 1

    # --- the order -----------------------------------------------------------
    named = [("L1", l1), ("L2", l2)]
    for kk in K_LADDER:
        named.append(("L3*(%d)" % kk, l3[kk]["closure"]))
    named.append(("L4", l4))
    order = {}
    for (na, pa), (nb, pb) in itertools.permutations(named, 2):
        order["%s<=%s" % (na, nb)] = refines(pa, pb)
    order_for_levels = {}
    for a in LEVEL_NAMES:
        for b in LEVEL_NAMES:
            ka = a.replace("L3(", "L3*(")
            kb = b.replace("L3(", "L3*(")
            order_for_levels["%s<=%s" % (a, b)] = (a == b) or order.get("%s<=%s" % (ka, kb), False)

    def separator(pa, pb):
        cls = {}
        for i, lab in enumerate(pb):
            cls.setdefault(lab, []).append(i)
        for lab in sorted(cls):
            for a, b in itertools.combinations(cls[lab], 2):
                if pa[a] != pa[b]:
                    return [uni[a], uni[b]]
        return None

    strict, equalities = {}, []
    for (na, pa), (nb, pb) in itertools.permutations(named, 2):
        if refines(pa, pb):
            if pa == pb:
                if na < nb:
                    equalities.append("%s == %s" % (na, nb))
            else:
                sp = separator(pa, pb)
                strict["%s<%s" % (na, nb)] = {"separator": sp, "certified": sp is not None}

    incomparable = {}
    for (na, pa), (nb, pb) in itertools.combinations(named, 2):
        if not refines(pa, pb) and not refines(pb, pa):
            incomparable["%s~%s" % (na, nb)] = {
                "in_%s_not_%s" % (na, nb): separator(pb, pa),
                "in_%s_not_%s" % (nb, na): separator(pa, pb)}

    total_pairs = sum(len(v) * (len(v) - 1) // 2 for v in reg.values())
    vac = {}
    for na, pa in named:
        c = pair_count(pa)
        vac[na] = {"related_pairs": c, "strictly_above_identity": c > 0,
                   "strictly_below_total": c < total_pairs}

    kstar = None
    for kk in K_LADDER:
        if refines(l2, l3[kk]["closure"]):
            kstar = kk
            break

    nontransitive = {}
    for kk in K_LADDER:
        adj = {}
        for (a, b) in l3[kk]["edge_list"]:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
        found = None
        for a in sorted(adj):
            for b in sorted(adj[a]):
                for c in sorted(adj.get(b, ())):
                    if c != a and c not in adj[a]:
                        found = [uni[a], uni[b], uni[c]]
                        break
                if found:
                    break
            if found:
                break
        nontransitive[str(kk)] = found

    gens = [p for _, p in named]
    lat = generated_sublattice(gens)
    gen_names = dict((p, n) for n, p in named)
    lat_elems = sorted(lat)
    hasse = []
    for pp in lat_elems:
        for qq in lat_elems:
            if pp == qq or not refines(pp, qq):
                continue
            if any(r not in (pp, qq) and refines(pp, r) and refines(r, qq) for r in lat_elems):
                continue
            hasse.append([gen_names.get(pp, "MEET%d" % lat_elems.index(pp)),
                          gen_names.get(qq, "MEET%d" % lat_elems.index(qq))])

    # --- W-BEHAVIOUR: does any pair sit in L4 and in no registered L3(k)? ----
    w_behaviour = None
    for lab in sorted(byclass):
        for a, b in itertools.combinations(byclass[lab], 2):
            if (a, b) not in k_edges or k_edges[(a, b)] > max(K_LADDER):
                w_behaviour = [uni[a], uni[b]]
                break
        if w_behaviour:
            break

    wit = {}
    for name, (p, q, why) in sorted(witness_specs().items()):
        d1, d2 = derive(p), derive(q)
        v = level_vector(d1, d2)
        wit[name] = {"why": why, "levels": v,
                     "minimal_levels": minimal_levels(v, order_for_levels),
                     "in_universe": (p in index and q in index)}

    # --- nulls ---------------------------------------------------------------
    rng = random.Random(8331433)
    choices = LEVEL_NAMES + ["NONE"]
    hits = 0
    for _ in range(200):
        guess = dict((nm, [rng.choice(choices)]) for nm in sorted(wit))
        if all(guess[nm] == wit[nm]["minimal_levels"] for nm in sorted(wit)):
            hits += 1
    null_assign = {"draws": 200, "reproduced": hits}

    hits2 = 0
    for _ in range(200):
        ok = True
        for nm, (p, q, _why) in sorted(witness_specs().items()):
            n, sig, prog, regime = q
            scrambled = (n, tuple(tuple(rng.randrange(n) for _ in range(n)) for _ in sig),
                         prog, regime)
            v = level_vector(derive(p), derive(scrambled))
            if minimal_levels(v, order_for_levels) != wit[nm]["minimal_levels"]:
                ok = False
                break
        if ok:
            hits2 += 1
    null_scramble = {"draws": 200, "reproduced": hits2}

    hostiles, inapplicable = run_hostiles(uni, derived, l1, l2, l3, l4, byclass)

    gates = [
        ("window_sufficient", l4 == l4_short),
        ("l1_l2_imply_the_presented_object", all(v == 0 for v in viol_beh.values())),
        ("l3_certificates_valid", cert_bad == 0 and cert_checked > 0),
        ("anti_vacuity", all(v["strictly_above_identity"] and v["strictly_below_total"]
                             for v in vac.values())),
        ("every_strict_inclusion_certified", all(v["certified"] for v in strict.values())),
        ("incomparability_certified",
         all(all(x is not None for x in v.values()) for v in incomparable.values())),
        ("l1_below_l2", order["L1<=L2"]),
        ("l2_and_l31_incomparable", "L2~L3*(1)" in incomparable),
        ("l3_tolerance_exhibited", nontransitive["1"] is not None),
        ("lattice_closed", len(lat) <= 256),
        ("all_hostiles_detected", all(h["detected"] for h in hostiles)),
        ("every_hostile_moved_its_quantity", all(h["control_moved"] for h in hostiles)),
        ("null_assignment_clean", null_assign["reproduced"] == 0),
        ("null_scramble_clean", null_scramble["reproduced"] == 0),
        ("no_alarm_on_true_configuration",
         all(v == 0 for v in viol_beh.values()) and cert_bad == 0
         and all(v["certified"] for v in strict.values())),
    ]
    failed = [g for g, ok in gates if not ok]

    result = {
        "schema": "AG3_PRESENTATION_EQUIVALENCE_RESULT_V1",
        "issue": 833, "section": "AG3", "row_index": 14,
        "claim_ceiling": ("AG3_PRESENTATION_EQUIVALENCE_STRENGTHS_DEFINED_AND_ORDERED_"
                          "AT_REGISTERED_FINITE_SCOPE"),
        "results": ["AG3L-1", "AG3L-2", "AG3L-3", "AG3L-4", "AG3L-5"],
        "universe_size": N,
        "comparable_pairs": total_pairs,
        "level_classes": dict([(nm, len(set(p))) for nm, p in named]),
        "level_related_pairs": dict([(nm, pair_count(p)) for nm, p in named]),
        "anti_vacuity": vac,
        "violations_l1_l2": viol_beh,
        "l3_raw_clause_cross_object_pairs": raw_cross,
        "l3_raw_clause_counterexample": raw_example,
        "l3_certificates_checked": cert_checked,
        "l3_certificates_invalid": cert_bad,
        "order": order,
        "strict_inclusions": strict,
        "level_equalities_on_this_universe": sorted(equalities),
        "incomparable_pairs": incomparable,
        "k_star_l2_inside_l3": kstar,
        "l3_tolerance_edges": dict((str(kk), l3[kk]["edges"]) for kk in K_LADDER),
        "l3_nontransitive_triple": nontransitive,
        "pair_in_L4_and_in_no_registered_L3": w_behaviour,
        "generated_sublattice_size": len(lat),
        "generated_sublattice_new_elements": len(lat) - len(set(gens)),
        "hasse_edges": sorted(hasse),
        "witnesses": wit,
        "null_random_level_assignment": null_assign,
        "null_scrambled_interpretation": null_scramble,
        "hostiles": hostiles,
        "inapplicable_perturbations": inapplicable,
        "gates": dict(gates),
        "failed_gates": failed,
        "status": "GREEN" if not failed else "RED",
        "forbidden_promotions": [
            "PRESENTATION_EQUIVALENCE_IS_SOLVED", "UNIQUE_PRESENTATION_EQUIVALENCE_STRENGTH",
            "COMPILER_MAKES_SEARCH_BIAS_INVARIANT", "LATTICE_IS_COMPLETE_FOR_ALL_PRESENTATIONS",
            "BASIS_INDEPENDENT_OPERATION_THEORY_CLAIMED", "THEORY_INVARIANCE_PROVEN_FOR_GMI",
            "ALL_PRESENTATIONS_ENUMERATED", "COMPLETE_GMI"],
        "scope_note": ("The order is computed over one registered finite universe of "
                       "presentations. No level of this order transfers instruction "
                       "description length, micro-step cost, mutation distance or "
                       "search/reachability geometry: gmi-833-aj5-g0-lowering-v1's "
                       "non-transfer boundary is preserved, and L3 charges an overhead "
                       "factor exactly because those quantities are not carried."),
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print(json.dumps({"status": result["status"], "failed_gates": failed,
                      "universe": N, "classes": result["level_classes"],
                      "related": result["level_related_pairs"],
                      "k_star": kstar, "lattice": len(lat),
                      "raw_cross": raw_cross,
                      "equalities": sorted(equalities),
                      "incomparable": sorted(incomparable),
                      "witness_levels": dict((k, v["minimal_levels"])
                                             for k, v in wit.items())}, sort_keys=True))
    return 0 if not failed else 1


def run_hostiles(uni, derived, l1, l2, l3, l4, byclass):
    """Each hostile must (a) move the quantity it perturbs and (b) be caught.

    A perturbation that cannot move its quantity at this scope is a test of
    nothing.  Such a perturbation is measured, recorded in `inapplicable`, and
    NOT counted as a hostile.
    """
    out = []
    inapplicable = []
    N = len(uni)

    def beh_violations(part):
        cls = {}
        for i, lab in enumerate(part):
            cls.setdefault(lab, []).append(i)
        v = 0
        for lab in cls:
            for a, b in itertools.combinations(cls[lab], 2):
                if derived[a]["beh"] != derived[b]["beh"]:
                    v += 1
        return v

    def canon_l1_variant(d, keep_prog=True, keep_obs=True):
        n = d["n"]
        best = None
        for perm in itertools.permutations(range(n)):
            if perm[S0] != S0:
                continue
            if keep_obs and any(d["obs"][perm[s]] != d["obs"][s] for s in range(n)):
                continue
            inv = [0] * n
            for s in range(n):
                inv[perm[s]] = s
            for rho in itertools.permutations(range(2)):
                sig2 = tuple(tuple(perm[d["sig"][rho.index(j)][inv[s]]] for s in range(n))
                             for j in range(2))
                if keep_prog:
                    prog2 = tuple(tuple(rho[f] for f in d["prog"][x]) for x in A_LETTERS)
                else:
                    prog2 = None
                cand = (d["regime"], n, sig2, prog2)
                if best is None or cand < best:
                    best = cand
        return best

    # H1 -- L1 without the program-translation condition
    h1 = partition_from_labels([canon_l1_variant(d, keep_prog=False) for d in derived])
    out.append({"name": "H1_L1_without_program_translation",
                "control_moved": pair_count(h1) != pair_count(l1),
                "control_before": pair_count(l1), "control_after": pair_count(h1),
                "detector": "l1_l2_imply_the_presented_object",
                "detected": beh_violations(h1) > 0, "finding": beh_violations(h1)})

    # H2 -- L1 without observation preservation
    h2 = partition_from_labels([canon_l1_variant(d, keep_obs=False) for d in derived])
    out.append({"name": "H2_L1_without_observation_preservation",
                "control_moved": pair_count(h2) != pair_count(l1),
                "control_before": pair_count(l1), "control_after": pair_count(h2),
                "detector": "l1_l2_imply_the_presented_object",
                "detected": beh_violations(h2) > 0, "finding": beh_violations(h2)})

    # H3 -- L2 without the external-action condition
    def canon_l2_nolet(d):
        n = d["n"]
        best = None
        for perm in state_bijections(d, d):
            inv = [0] * n
            for s in range(n):
                inv[perm[s]] = s
            mon = tuple(sorted(tuple(perm[t[inv[s]]] for s in range(n)) for t in d["monoid"]))
            cand = (d["regime"], n, mon)
            if best is None or cand < best:
                best = cand
        return best
    h3 = partition_from_labels([canon_l2_nolet(d) for d in derived])
    out.append({"name": "H3_L2_without_external_action_condition",
                "control_moved": pair_count(h3) != pair_count(l2),
                "control_before": pair_count(l2), "control_after": pair_count(h3),
                "detector": "l1_l2_imply_the_presented_object",
                "detected": beh_violations(h3) > 0, "finding": beh_violations(h3)})

    # H4 -- L3 computed over the whole state space instead of the reachable part
    specs = witness_specs()
    p, q, _ = specs["W-STATESPACE"]
    d1, d2 = derive(p), derive(q)
    true_k, bad_k = kmin(d1, d2), kmin(d1, d2, use_reach=False)
    out.append({"name": "H4_L3_without_reachability_restriction",
                "control_moved": true_k != bad_k,
                "control_before": true_k, "control_after": bad_k,
                "detector": "incomparability_certified", "detected": bad_k is None,
                "finding": "the L2/L3 separating pair is lost" if bad_k is None else "none"})

    # H5 -- L3 with an encoding that need not be injective
    bad_cert, moved = 0, 0
    for lab in sorted(byclass):
        for a, b in itertools.combinations(byclass[lab], 2):
            if kmin(derived[a], derived[b]) is not None:
                continue
            if kmin(derived[a], derived[b], need_inj=False) is not None:
                moved += 1
                c = certificate_perturbed(derived[a], derived[b], K_LADDER[0],
                                          need_inj=False)
                if c is not None and not verify_certificate(derived[a], derived[b],
                                                            c, K_LADDER[0]):
                    bad_cert += 1
    inapplicable.append({
        "name": "P5_L3_encoding_not_required_injective",
        "control_before": 0, "control_after": moved, "control_moved": moved > 0,
        "certificates_rejected": bad_cert,
        "excluded_reason": ("measured and found unable to move its quantity at this "
                            "scope: inside an L4 class no pair is gained by dropping "
                            "injectivity, so the perturbation would be a test of "
                            "nothing and is NOT shipped as a hostile")})

    # H6 -- L3 with the overhead bound removed, measured against k = 1
    edges_inf = []
    for lab in sorted(byclass):
        for a, b in itertools.combinations(byclass[lab], 2):
            if kmin(derived[a], derived[b]) is not None:
                edges_inf.append((a, b))
    p_inf = partition_from_edges(N, edges_inf)
    out.append({"name": "H6_L3_with_unbounded_overhead",
                "control_moved": len(edges_inf) != l3[K_LADDER[0]]["edges"],
                "control_before": l3[K_LADDER[0]]["edges"], "control_after": len(edges_inf),
                "detector": "l2_and_l31_incomparable",
                "detected": refines(l2, p_inf),
                "finding": ("L3 collapses so far that L2 falls below it and the "
                            "incomparability is destroyed") if refines(l2, p_inf) else "none"})

    # H7 -- the frozen section-2 clause with the observation dropped from the
    # encoding, measured where it is applicable: across DIFFERENT presented
    # objects, which is the only place the constraint can bind.
    reg = {}
    for i, d in enumerate(derived):
        reg.setdefault(d["regime"], []).append(i)
    moved7, bad7 = 0, 0
    for r in sorted(reg):
        for a, b in itertools.combinations(reg[r], 2):
            if l4[a] == l4[b]:
                continue
            if kmin(derived[a], derived[b]) is not None:
                continue
            if kmin(derived[a], derived[b], need_obs=False) is not None:
                moved7 += 1
                c = certificate_perturbed(derived[a], derived[b], K_LADDER[0],
                                          need_obs=False)
                if c is not None and not verify_certificate(derived[a], derived[b],
                                                            c, K_LADDER[0]):
                    bad7 += 1
    out.append({"name": "H7_raw_clause_encoding_without_observation_preservation",
                "control_moved": moved7 > 0, "control_before": 0, "control_after": moved7,
                "detector": "l3_certificates_valid", "detected": bad7 > 0,
                "finding": bad7})
    return out, inapplicable


def certificate_perturbed(src, dst, k, need_obs=True, need_inj=True):
    dom = sorted(src["reach"])
    for e in encodings(src, dst, True, need_obs, need_inj):
        lens, ok = {}, True
        for x in A_LETTERS:
            L = len(src["prog"][x])
            if L == 0:
                lens[x] = 0
                continue
            target = dict((e[s], e[src["letter"][x][s]]) for s in dom)
            found = None
            for m in range(0, k * L + 1):
                for t in dst["real"][m]:
                    if all(t[a] == b for a, b in target.items()):
                        found = m
                        break
                if found is not None:
                    break
            if found is None:
                ok = False
                break
            lens[x] = found
        if ok:
            return {"encoding": dict((str(a), b) for a, b in sorted(e.items())),
                    "compiled_lengths": dict((str(x), lens[x]) for x in A_LETTERS)}
    return None


if __name__ == "__main__":
    sys.exit(main())
