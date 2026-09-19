"""Route B -- independently written oracle for #833 Section Z, subsection Z4.

Does not import, exec or read `z4_universality_v1.py`.  Differences:
the universe is rebuilt output-table-major; the resource-response profile is
keyed by a formatted string rather than a nested tuple; Pareto frontiers are
computed by a sorted sweep with a running minimum instead of pairwise
domination; the stateless delayed minimum is derived analytically from the
independence of consecutive input bits and then checked against the
enumeration; and the family membership predicates are written from the
dependence definitions rather than the bit-mask forms.

Run:  python3 -I -B independent_universality_oracle_v1.py
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LS = (2, 3, 4)


def run_counts(bits, nxt, tab, L):
    kn = kd = 0
    for seq in itertools.product((0, 1), repeat=L):
        for mode in (0, 1):
            st = 0
            for t in range(L):
                x = seq[t]
                if bits == 0:
                    o = (tab >> (2 * mode + x)) & 1
                else:
                    a = 4 * st + 2 * mode + x
                    o = (tab >> a) & 1
                    st = (nxt >> a) & 1
                if t:
                    tgt = x if mode == 0 else seq[t - 1]
                    if o != tgt:
                        if mode:
                            kd += 1
                        else:
                            kn += 1
    return kn, kd


def beh(bits, nxt, tab):
    s = []
    for mode in (0, 1):
        for seq in itertools.product((0, 1), repeat=3):
            st = 0
            for t in range(3):
                x = seq[t]
                if bits == 0:
                    s.append((tab >> (2 * mode + x)) & 1)
                else:
                    a = 4 * st + 2 * mode + x
                    s.append((tab >> a) & 1)
                    st = (nxt >> a) & 1
    return "".join(str(b) for b in s)


def canonical_order():
    u = [(0, None, t) for t in range(16)]
    for nxt in range(256):
        for tab in range(256):
            u.append((1, nxt, tab))
    return u


def table_major_order():
    u = [(0, None, t) for t in range(16)]
    for tab in range(256):
        for nxt in range(256):
            u.append((1, nxt, tab))
    return u


def frontier_sweep(points):
    """Minimal points of a 2-D integer set by a sorted sweep."""
    pts = sorted(set(points))
    out = []
    best_y = None
    for (x, y) in pts:
        if best_y is None or y < best_y:
            out.append((x, y))
            best_y = y
    return tuple(out)


def frontier_sweep3(points):
    """Minimal points of a 3-D integer set (kn, kd, bits) by blocks."""
    out = []
    for b in sorted(set(p[2] for p in points)):
        sub = [(p[0], p[1]) for p in points if p[2] == b]
        for (x, y) in frontier_sweep(sub):
            out.append((x, y, b))
    # drop points dominated across blocks
    keep = []
    for a in out:
        if not any(c != a and all(ci <= ai for ci, ai in zip(c, a))
                   for c in out):
            keep.append(a)
    return tuple(sorted(keep))


def deps(tab, nxt, bits):
    T = {}
    Nn = {}
    for s in (0, 1):
        for m in (0, 1):
            for x in (0, 1):
                if bits == 0:
                    T[(s, m, x)] = (tab >> (2 * m + x)) & 1
                    Nn[(s, m, x)] = 0
                else:
                    a = 4 * s + 2 * m + x
                    T[(s, m, x)] = (tab >> a) & 1
                    Nn[(s, m, x)] = (nxt >> a) & 1

    def dep(d, ax):
        for k in d:
            k2 = list(k)
            k2[ax] = 1 - k2[ax]
            if d[k] != d[tuple(k2)]:
                return True
        return False
    return dep(T, 0), dep(T, 2), Nn, T


def main():
    canon = canonical_order()
    tmaj = table_major_order()
    total = len(canon)
    assert set(canon) == set(tmaj) and len(set(tmaj)) == total

    prof = {}
    behs = {}
    cnt = {}
    for c in tmaj:
        bits, nxt, tab = c
        e = tuple(run_counts(bits, nxt, tab, L) for L in LS)
        cnt[c] = e
        behs[c] = beh(bits, nxt, tab)

    block_front = {}
    for b in (0, 1):
        for i, L in enumerate(LS):
            pts = set(cnt[c][i] for c in canon if c[0] == b)
            block_front[(b, L)] = frontier_sweep(pts)

    def profile(c):
        i0 = canon.index if False else None
        bits = c[0]
        parts = []
        for i, L in enumerate(LS):
            parts.append("%d:%d" % cnt[c][i])
        dom = []
        for i, L in enumerate(LS):
            dom.append("1" if cnt[c][i] in block_front[(bits, L)] else "0")
        return "|".join(parts) + "#" + "".join(dom)

    classes = {}
    for c in tmaj:
        classes.setdefault(profile(c), []).append(c)
    sizes = sorted(len(v) for v in classes.values())

    fam = {"F_STATELESS": set(), "F_DEAD_TABLE": set(), "F_FROZEN_STATE": set(),
           "F_MOORE": set(), "F_MEALY_PURE": set(), "F_IDENTITY_STATE": set()}
    for c in canon:
        bits, nxt, tab = c
        if bits == 0:
            fam["F_STATELESS"].add(c)
            continue
        dep_state, dep_input, Nn, _T = deps(tab, nxt, bits)
        if not dep_state:
            fam["F_DEAD_TABLE"].add(c)
        if len(set(Nn.values())) == 1:
            fam["F_FROZEN_STATE"].add(c)
        if not dep_input:
            fam["F_MOORE"].add(c)
        else:
            fam["F_MEALY_PURE"].add(c)
        if all(Nn[(s, m, x)] == x for s in (0, 1) for m in (0, 1)
               for x in (0, 1)):
            fam["F_IDENTITY_STATE"].add(c)

    fam_front = dict((k, frontier_sweep(set(cnt[c][1] for c in v)))
                     for k, v in fam.items())

    # analytic: consecutive input bits are independent and uniform, so a
    # stateless delayed predictor is a function of the current bit alone and
    # errs on exactly half of the (L-1)*2^L scored moments per mode
    analytic = dict((L, (L - 1) * (2 ** (L - 1))) for L in LS)
    enumerated = dict((L, min(cnt[c][i][1] for c in canon if c[0] == 0))
                      for i, L in enumerate(LS))
    enumerated1 = dict((L, min(cnt[c][i][1] for c in canon if c[0] == 1))
                       for i, L in enumerate(LS))

    # distinctions
    beh_members = {}
    for c in canon:
        beh_members.setdefault(behs[c], []).append(c)

    def state_relabel(c):
        bits, nxt, tab = c
        if bits == 0:
            return c
        n2 = t2 = 0
        for s in (0, 1):
            for m in (0, 1):
                for x in (0, 1):
                    i2 = 4 * s + 2 * m + x
                    i1 = 4 * (1 - s) + 2 * m + x
                    n2 |= (1 - ((nxt >> i1) & 1)) << i2
                    t2 |= ((tab >> i1) & 1) << i2
        return (1, n2, t2)

    def out_flip(c):
        bits, nxt, tab = c
        return (bits, nxt, (~tab) & (0xF if bits == 0 else 0xFF))

    gcache = {}

    def gb(c, g):
        k = (c, g)
        if k not in gcache:
            d = state_relabel(c) if g == "s" else out_flip(c)
            gcache[k] = (beh(*d), run_counts(d[0], d[1], d[2], 3) + (d[0],))
        return gcache[k]

    def clause1(A, B):
        for _b, mem in beh_members.items():
            inA = any(c in A for c in mem)
            inB = any(c in B for c in mem)
            if inA and inB:
                return False
        return True

    def clause2(members):
        base_b = frozenset(behs[c] for c in members)
        base_f = frontier_sweep3(set(cnt[c][1] + (c[0],) for c in members))
        for g in ("s", "o"):
            bs = frozenset(gb(c, g)[0] for c in members)
            fs = frontier_sweep3(set(gb(c, g)[1] for c in members))
            if bs != base_b or fs != base_f:
                return False
        return True

    b0 = set(c for c in canon if c[0] == 0)
    b1 = set(canon) - b0
    pairs = [("bits0_vs_bits1", b0, b1)]
    fn = sorted(fam)
    for i in range(len(fn)):
        for j in range(i + 1, len(fn)):
            A = fam[fn[i]] - fam[fn[j]]
            B = fam[fn[j]] - fam[fn[i]]
            if A and B:
                pairs.append(("%s_vs_%s" % (fn[i], fn[j]), A, B))

    verdict = {}
    for label, A, B in pairs:
        c1 = clause1(A, B)
        c2 = clause2(A) and clause2(B) if c1 else None
        verdict[label] = {"clause1": c1, "clause2": c2,
                          "IRREDUCIBLE": bool(c1 and c2)}

    out = {
        "schema": "GMI_833_Z4_UNIVERSALITY_ORACLE_V1",
        "route": "B_independent",
        "universe_candidates": total,
        "behaviour_classes_at_L3": len(beh_members),
        "resource_response_classes": len(classes),
        "class_size_min": sizes[0],
        "class_size_max": sizes[-1],
        "singleton_classes": sum(1 for s in sizes if s == 1),
        "block_frontiers": dict(("bits%d_L%d" % k, [list(x) for x in v])
                                for k, v in block_front.items()),
        "family_frontiers_L3": dict((k, [list(x) for x in v])
                                    for k, v in fam_front.items()),
        "family_sizes": dict((k, len(v)) for k, v in fam.items()),
        "stateless_min_delay_analytic": analytic,
        "stateless_min_delay_enumerated": enumerated,
        "stateful_min_delay_enumerated": enumerated1,
        "analytic_matches_enumeration":
            all(analytic[L] == enumerated[L] for L in LS),
        "distinctions": verdict,
        "irreducible": sorted(k for k, v in verdict.items() if v["IRREDUCIBLE"]),
        "fail_clause1": sorted(k for k, v in verdict.items()
                               if not v["clause1"]),
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print(json.dumps({"classes": len(classes), "beh": len(beh_members),
                      "sizes": [sizes[0], sizes[-1]],
                      "irr": out["irreducible"], "failc1": out["fail_clause1"],
                      "analytic_ok": out["analytic_matches_enumeration"],
                      "moore": out["family_frontiers_L3"]["F_MOORE"],
                      "mealy": out["family_frontiers_L3"]["F_MEALY_PURE"]},
                     sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
