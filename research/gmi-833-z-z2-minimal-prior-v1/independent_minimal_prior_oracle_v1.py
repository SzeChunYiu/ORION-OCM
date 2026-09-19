"""Route B -- independently written oracle for #833 Section Z, subsection Z2.

This file does not import, exec or read `z2_minimal_prior_v1.py`.  It
reconstructs the registered universe in a different order (output-table major
instead of next-state major), keys semantics by a tuple of per-mode output
tuples instead of a packed 48-bit integer, accumulates the class histogram with
`collections.Counter`, computes the total-variation distance by the
positive-part identity rather than the half-sum-of-absolute-differences form,
and scores every learner by iterating candidates one at a time with weight one
instead of grouping by semantic class and weighting by class size.

Run:  python3 -I -B independent_minimal_prior_oracle_v1.py
"""
import collections
import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
LEN = 3
SEQS = tuple(itertools.product((0, 1), repeat=LEN))
SCORED = (LEN - 1) * len(SEQS)

PGRID = ("1/5", "2/5", "1/2", "3/5", "4/5")
EGRID = ("1", "2", "3", "4")

# the features Route B re-scores at candidate level (freeze §2 + amendment 3
# registered alphabet, plus the extremal swept specifications Route A reports)
PRIMNAMES = ("p01_has_state", "p02_out_depends_on_input",
             "p03_out_depends_on_state", "p04_out_depends_on_mode",
             "p05_out_constant", "p06_next_depends_on_input",
             "p07_next_depends_on_state", "p08_next_depends_on_mode",
             "p09_next_constant", "p10_next_equals_input",
             "p11_next_equals_state", "p12_out_equals_input")


def emit(bits, nxt, tab, mode, seq):
    res = []
    st = 0
    for step in range(LEN):
        x = seq[step]
        if bits == 0:
            res.append((tab >> (2 * mode + x)) & 1)
        else:
            a = 4 * st + 2 * mode + x
            res.append((tab >> a) & 1)
            st = (nxt >> a) & 1
    return tuple(res)


def sem_key(bits, nxt, tab):
    return (tuple(emit(bits, nxt, tab, 0, s) for s in SEQS),
            tuple(emit(bits, nxt, tab, 1, s) for s in SEQS))


def canonical_universe():
    """Same registered set, canonical (Route A) index order."""
    u = []
    for tab in range(16):
        u.append((0, None, tab))
    for nxt in range(256):
        for tab in range(256):
            u.append((1, nxt, tab))
    return u


def table_major_universe():
    """Same registered set, a different traversal order."""
    u = []
    for tab in range(16):
        u.append((0, None, tab))
    for tab in range(256):
        for nxt in range(256):
            u.append((1, nxt, tab))
    return u


def err_pair(k):
    a, b = 0, 0
    for si, s in enumerate(SEQS):
        for t in range(1, LEN):
            if k[0][si][t] != s[t]:
                a += 1
            if k[1][si][t] != s[t - 1]:
                b += 1
    return a, b


def tv_positive_part(counter, total):
    """TV(P, U) = sum_x max(0, P(x) - U(x)); equal to the half-sum form."""
    k = len(counter)
    acc = Fraction(0)
    for n in counter.values():
        d = Fraction(n, total) - Fraction(1, k)
        if d > 0:
            acc += d
    return acc


def obs_and_target():
    out = []
    for k in range(len(SEQS)):
        obs = [(0, si, t) for si in range(len(SEQS)) for t in (1, 2)]
        obs += [(1, si, t) for si in range(k) for t in (1, 2)]
        for s in range(k, len(SEQS)):
            out.append((tuple(obs), (1, s, 2)))
    return out


def prim_values(bits, nxt, tab):
    T = {}
    Nn = {}
    for st in (0, 1):
        for m in (0, 1):
            for x in (0, 1):
                if bits == 0:
                    T[(st, m, x)] = (tab >> (2 * m + x)) & 1
                    Nn[(st, m, x)] = 0
                else:
                    a = 4 * st + 2 * m + x
                    T[(st, m, x)] = (tab >> a) & 1
                    Nn[(st, m, x)] = (nxt >> a) & 1

    def dep(d, ax):
        for st in (0, 1):
            for m in (0, 1):
                for x in (0, 1):
                    k1 = [st, m, x]
                    k2 = [st, m, x]
                    k2[ax] = 1 - k2[ax]
                    if d[tuple(k1)] != d[tuple(k2)]:
                        return True
        return False

    v = {}
    v["p01_has_state"] = bits == 1
    v["p02_out_depends_on_input"] = dep(T, 2)
    v["p03_out_depends_on_state"] = bits == 1 and dep(T, 0)
    v["p04_out_depends_on_mode"] = dep(T, 1)
    v["p05_out_constant"] = len(set(T.values())) == 1
    v["p06_next_depends_on_input"] = bits == 1 and dep(Nn, 2)
    v["p07_next_depends_on_state"] = bits == 1 and dep(Nn, 0)
    v["p08_next_depends_on_mode"] = bits == 1 and dep(Nn, 1)
    v["p09_next_constant"] = bits == 1 and len(set(Nn.values())) == 1
    v["p10_next_equals_input"] = bits == 1 and all(
        Nn[(a, b, c)] == c for a in (0, 1) for b in (0, 1) for c in (0, 1))
    v["p11_next_equals_state"] = bits == 1 and all(
        Nn[(a, b, c)] == a for a in (0, 1) for b in (0, 1) for c in (0, 1))
    v["p12_out_equals_input"] = all(
        T[(a, b, c)] == c for a in (0, 1) for b in (0, 1) for c in (0, 1))
    return v


def main():
    canon = canonical_universe()
    tmaj = table_major_universe()
    total = len(canon)

    keys_canon = [sem_key(*c) for c in canon]
    keys_tmaj = [sem_key(*c) for c in tmaj]
    hist = collections.Counter(keys_tmaj)
    K = len(hist)
    d_tv = tv_positive_part(hist, total)
    sizes = sorted(hist.values())

    first = {}
    for i, k in enumerate(keys_canon):
        if k not in first:
            first[k] = i + 1
    fh = sorted(first.values())

    # ------------------------------------------------ learners, candidate level
    probs = obs_and_target()
    prims = [prim_values(*c) for c in canon]
    cls_size = [hist[k] for k in keys_canon]
    max_size = max(sizes)
    med = sizes[len(sizes) // 2]

    def get(k, mode, si, t):
        return k[mode][si][t]

    feats = collections.OrderedDict()
    feats["B1_bits_eq_0"] = [c[0] == 0 for c in canon]
    feats["B2_bits_eq_1"] = [c[0] == 1 for c in canon]
    feats["B3_table_popcount_le_4"] = [bin(c[2]).count("1") <= 4 for c in canon]
    feats["B4_table_popcount_gt_4"] = [bin(c[2]).count("1") > 4 for c in canon]
    feats["B5_state_never_changes"] = [c[1] is None or c[1] in (0, 255)
                                       for c in canon]
    feats["B6_state_changes"] = [not (c[1] is None or c[1] in (0, 255))
                                 for c in canon]
    feats["B7_index_low_half"] = [i < total // 2 for i in range(total)]
    feats["B8_index_high_half"] = [i >= total // 2 for i in range(total)]
    feats["B9_singleton_class"] = [cls_size[i] == 1 for i in range(total)]
    feats["B10_largest_class"] = [cls_size[i] == max_size for i in range(total)]
    feats["B11_class_above_median"] = [cls_size[i] > med for i in range(total)]
    feats["B12_class_below_median"] = [cls_size[i] < med for i in range(total)]
    # extremal swept specifications re-scored independently
    swept = {
        "SWEEP_p03_out_depends_on_state,!p06_next_depends_on_input":
            (("p03_out_depends_on_state", True),
             ("p06_next_depends_on_input", False)),
        "SWEEP_!p05_out_constant,p07_next_depends_on_state":
            (("p05_out_constant", False), ("p07_next_depends_on_state", True)),
        "SWEEP_p07_next_depends_on_state":
            (("p07_next_depends_on_state", True),),
    }
    for nm, lits in swept.items():
        feats[nm] = [all(prims[i][a] == b for a, b in lits)
                     for i in range(total)]

    names = list(feats)
    det = 0
    und = 0
    syn_ok = 0
    sem_ok = 0
    dis_full = 0
    dis_und = 0
    und2 = dict((n, 0) for n in names)
    for obs, m in probs:
        groups = {}
        for i, k in enumerate(keys_canon):
            sig = tuple(get(k, a, b, c) for (a, b, c) in obs)
            bit = get(k, m[0], m[1], m[2])
            g = groups.get(sig)
            if g is None:
                g = groups[sig] = [[0, 0], set(), []]
            g[0][bit] += 1
            g[1].add((keys_canon[i], bit))
            g[2].append((i, bit))
        for sig in groups:
            n0, n1 = groups[sig][0]
            k0 = sum(1 for (_k, b) in groups[sig][1] if b == 0)
            k1 = sum(1 for (_k, b) in groups[sig][1] if b == 1)
            tot = n0 + n1
            psyn = 0 if n0 >= n1 else 1
            psem = 0 if k0 >= k1 else 1
            syn_ok += groups[sig][0][psyn]
            sem_ok += groups[sig][0][psem]
            if psyn != psem:
                dis_full += 1
            if n0 > 0 and n1 > 0:
                und += tot
                if psyn != psem:
                    dis_und += 1
                for n in names:
                    msk = feats[n]
                    q0 = 0
                    q1 = 0
                    for (i, bit) in groups[sig][2]:
                        if msk[i]:
                            if bit:
                                q1 += 1
                            else:
                                q0 += 1
                    if q0 > 0 and q1 == 0:
                        und2[n] += 2 * n0
                    elif q1 > 0 and q0 == 0:
                        und2[n] += 2 * n1
                    else:
                        und2[n] += tot
            else:
                det += tot

    full = det + und
    a_syn_f = Fraction(syn_ok, full)
    a_sem_f = Fraction(sem_ok, full)
    # undetermined accuracy: subtract the determined pairs, all of which every
    # learner gets right
    a_syn_u = Fraction(syn_ok - det, und)
    a_sem_u = Fraction(sem_ok - det, und)
    feat_u = dict((n, Fraction(und2[n], 2 * und)) for n in names)

    # ------------------------------------------------------- family recovery
    fams = {"F_STATELESS": set(), "F_DEAD_TABLE": set(), "F_FROZEN_STATE": set(),
            "F_MOORE": set(), "F_MEALY_PURE": set(), "F_IDENTITY_STATE": set()}
    for i, (bits, nxt, tab) in enumerate(canon):
        if bits == 0:
            fams["F_STATELESS"].add(i)
            continue
        v = prims[i]
        if not v["p03_out_depends_on_state"]:
            fams["F_DEAD_TABLE"].add(i)
        if v["p09_next_constant"]:
            fams["F_FROZEN_STATE"].add(i)
        if not v["p02_out_depends_on_input"]:
            fams["F_MOORE"].add(i)
        else:
            fams["F_MEALY_PURE"].add(i)
        if v["p10_next_equals_input"]:
            fams["F_IDENTITY_STATE"].add(i)
    # syntactic ground truth, written independently of the property predicates
    truth = {"F_STATELESS": set(), "F_DEAD_TABLE": set(),
             "F_FROZEN_STATE": set(), "F_MOORE": set(), "F_MEALY_PURE": set(),
             "F_IDENTITY_STATE": set()}
    for i, (bits, nxt, tab) in enumerate(canon):
        if bits == 0:
            truth["F_STATELESS"].add(i)
            continue
        if all(((tab >> (2 * m + x)) & 1) == ((tab >> (4 + 2 * m + x)) & 1)
               for m in (0, 1) for x in (0, 1)):
            truth["F_DEAD_TABLE"].add(i)
        if nxt in (0, 255):
            truth["F_FROZEN_STATE"].add(i)
        if all(((tab >> (4 * st + 2 * m)) & 1) == ((tab >> (4 * st + 2 * m + 1)) & 1)
               for st in (0, 1) for m in (0, 1)):
            truth["F_MOORE"].add(i)
        else:
            truth["F_MEALY_PURE"].add(i)
        if nxt == 0b10101010:
            truth["F_IDENTITY_STATE"].add(i)

    # ------------------------------------------------------------ invariance
    def relabel_state(c):
        bits, nxt, tab = c
        if bits == 0:
            return c
        n2 = t2 = 0
        for st in (0, 1):
            for m in (0, 1):
                for x in (0, 1):
                    i2 = 4 * st + 2 * m + x
                    i1 = 4 * (1 - st) + 2 * m + x
                    n2 |= (1 - ((nxt >> i1) & 1)) << i2
                    t2 |= ((tab >> i1) & 1) << i2
        return (1, n2, t2)

    def flip_out(c):
        bits, nxt, tab = c
        return (bits, nxt, (~tab) & (0xF if bits == 0 else 0xFF))

    def summaries(us):
        cc = collections.Counter()
        for c in us:
            cc[err_pair(sem_key(*c)) + (c[0],)] += 1
        return cc

    def grid(cc):
        rows = []
        for ps in PGRID:
            for es in EGRID:
                p = Fraction(ps)
                eta = Fraction(es)
                ls = eta * p / 2
                for tag, lam in (("low", ls / 2), ("high", ls * 3 / 2)):
                    best = None
                    bb = None
                    for (e0, e1, bits) in cc:
                        j = (eta * p * Fraction(e1, SCORED)
                             + eta * (1 - p) * Fraction(e0, SCORED) + lam * bits)
                        if best is None or j < best or (j == best and bits < bb):
                            best, bb = j, bits
                    rows.append((str(best), "STATELESS" if bb == 0
                                 else "PERSISTENT_STATE"))
        return rows

    base_cc = summaries(canon)
    base_grid = grid(base_cc)
    inv = {}
    for nm, img in (("g_state", [relabel_state(c) for c in canon]),
                    ("g_out", [flip_out(c) for c in canon])):
        cc = summaries(img)
        kk = collections.Counter(sem_key(*c) for c in img)
        inv[nm] = {
            "is_bijection_of_U": set(img) == set(canon) and len(set(img)) == total,
            "K_invariant": len(kk) == K,
            "histogram_invariant": sorted(kk.values()) == sizes,
            "min_J_and_winner_invariant": grid(cc) == base_grid,
            "per_candidate_membership_invariant":
                all(sem_key(*img[i]) == keys_canon[i] for i in range(total)),
        }

    out = {
        "schema": "GMI_833_Z2_MINIMAL_PRIOR_ORACLE_V1",
        "route": "B_independent",
        "universe_candidates": total,
        "K_semantic_classes": K,
        "class_size_min": sizes[0],
        "class_size_max": sizes[-1],
        "D_TV_syntax_vs_uniform_over_classes": str(d_tv),
        "first_hit_min_probe": fh[0],
        "first_hit_max_probe": fh[-1],
        "first_hit_max_over_min": str(Fraction(fh[-1], fh[0])),
        "scored_pairs_full": full,
        "scored_pairs_determined": det,
        "scored_pairs_undetermined": und,
        "determined_fraction": str(Fraction(det, full)),
        "A_syn_full": str(a_syn_f),
        "A_sem_full": str(a_sem_f),
        "A_syn_undetermined": str(a_syn_u),
        "A_sem_undetermined": str(a_sem_u),
        "disagreeing_buckets_full": dis_full,
        "disagreeing_buckets_undetermined": dis_und,
        "preference_only_accuracy_undetermined":
            dict((n, str(feat_u[n])) for n in names),
        "families_property_first_match_syntactic":
            dict((k, fams[k] == truth[k]) for k in truth),
        "family_sizes": dict((k, len(truth[k])) for k in truth),
        "invariance": inv,
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh2:
        json.dump(out, fh2, indent=1, sort_keys=True)
        fh2.write("\n")
    print(json.dumps({"K": K, "D_TV": str(d_tv), "A_syn_und": str(a_syn_u),
                      "det_frac": str(Fraction(det, full)),
                      "fams_ok": all(fams[k] == truth[k] for k in truth)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
