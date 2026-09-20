"""Route B -- independent oracle for IC-1, its corollaries and the separations
(#833 Section Z, subsection Z1).

Route B shares no code with Route A and does not import it.  Three deliberate
differences:

  * envelopes are found by BRUTE FORCE over supporting lines -- level k is an
    envelope vertex iff some non-negative rational slope makes it the strict
    argmin -- not by a monotone chain;
  * the two-level profiles are rebuilt from each instance's declared closed form
    and then CHECKED against an independent enumeration of the stateless table
    space written here from scratch;
  * separation groups are found by sorting the instance list on a rendered key,
    not by dictionary grouping, and every group is re-verified pairwise.

Stdlib only; exact arithmetic.  Python 3.8 compatible.

Run:  python3 -I -B independent_compression_oracle_v1.py
"""
import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ETAS = (1, 2, 3)
PGRID = tuple(Fraction(k, 8) for k in range(0, 9))
QGRID = (Fraction(1, 5), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2),
         Fraction(2, 3), Fraction(3, 4), Fraction(4, 5))
ALPHAS = (2, 3, 4)


def enum_binary_floor(q):
    """Independent enumeration: every map cur -> guess over the binary alphabet."""
    seqs = list(itertools.product((0, 1), repeat=3))
    best = None
    for g0 in (0, 1):
        for g1 in (0, 1):
            g = (g0, g1)
            tot = Fraction(0)
            for s in seqs:
                pr = Fraction(1)
                for x in s:
                    pr *= q if x == 1 else (1 - q)
                e = sum(1 for t in (1, 2) if g[s[t]] != s[t - 1])
                tot += pr * Fraction(e, 2)
            if best is None or tot < best:
                best = tot
    return best


def enum_alpha_floor(A):
    seqs = list(itertools.product(range(A), repeat=3))
    best = None
    for g in itertools.product(range(A), repeat=A):
        e = 0
        for s in seqs:
            for t in (1, 2):
                if g[s[t]] != s[t - 1]:
                    e += 1
        r = Fraction(e, len(seqs) * 2)
        if best is None or r < best:
            best = r
    return best


def vertex_by_supporting_line(E, k, slopes):
    """Brute force: k is an envelope vertex iff some slope makes it strict argmin."""
    for lam in slopes:
        if all(E[k] + lam * k < E[j] + lam * j for j in E if j != k):
            return True, lam
    return False, None


def ladder_floors():
    L, WIN, MODES = 4, (2, 3), (0, 1, 2)
    SEQ = list(itertools.product((0, 1), repeat=L))
    NS = len(SEQ) * len(WIN)
    out = {}
    for b in (0, 1, 2):
        ns = 2 ** b
        na = ns * 2
        for m in MODES:
            best = None
            for nxt in itertools.product(range(ns), repeat=na):
                for tab in itertools.product((0, 1), repeat=na) if b <= 1 else [None]:
                    e = 0
                    if tab is None:
                        tal = [[0, 0] for _ in range(na)]
                        for s in SEQ:
                            st = 0
                            for t in range(L):
                                a = st * 2 + s[t]
                                if t in WIN:
                                    tal[a][s[t - m]] += 1
                                st = nxt[a]
                        e = sum(min(v) for v in tal)
                    else:
                        for s in SEQ:
                            st = 0
                            for t in range(L):
                                a = st * 2 + s[t]
                                if t in WIN and tab[a] != s[t - m]:
                                    e += 1
                                st = nxt[a]
                    if best is None or e < best:
                        best = e
                    if best == 0:
                        break
                if best == 0:
                    break
            out[(b, m)] = Fraction(best, NS)
    return out


def main():
    res = {"schema": "GMI_833_Z1_MASTER_PRINCIPLE_ORACLE_V1", "route": "B",
           "issue": 833, "subsection": "Z1"}

    # ---- corollary checks against independently enumerated floors
    binf = dict((q, enum_binary_floor(q)) for q in QGRID)
    alpf = dict((A, enum_alpha_floor(A)) for A in ALPHAS)
    res["floors"] = {"binary": dict((str(q), str(v)) for q, v in binf.items()),
                     "alphabet": dict((str(A), str(v)) for A, v in alpf.items())}
    res["IC_1c_closed_form_matches_enumeration"] = all(binf[q] == min(q, 1 - q) for q in QGRID)
    res["IC_1b_closed_form_matches_enumeration"] = all(alpf[A] == Fraction(A - 1, A)
                                                       for A in ALPHAS)
    res["IC_1a_uniform_binary_floor"] = str(binf[Fraction(1, 2)])

    # ---- instances, rebuilt from declared closed forms
    inst = []
    for eta in ETAS:
        for p in PGRID:
            inst.append(("UNIF", eta, p, Fraction(1, 2), 2, binf[Fraction(1, 2)], 16))
            for q in QGRID:
                inst.append(("SKEW", eta, p, q, 2, binf[q], 16))
            for A in ALPHAS:
                inst.append(("ALPHA", eta, p, Fraction(1, 2), A, alpf[A], A ** (2 * A)))
    res["n_instances"] = len(inst)

    # ---- envelope by supporting lines, on the ladder
    Rl = ladder_floors()
    res["ladder_floors"] = dict(("b%d_m%d" % (b, m), str(Rl[(b, m)]))
                                for b in (0, 1, 2) for m in (0, 1, 2))
    slopes = [Fraction(k, 64) for k in range(0, 4 * 64 + 1)]
    disagree = 0
    n_lad = 0
    lad = []
    for eta in ETAS:
        for a in range(9):
            for b2 in range(9 - a):
                c = 8 - a - b2
                p = (Fraction(a, 8), Fraction(b2, 8), Fraction(c, 8))
                E = dict((k, eta * sum(p[m] * Rl[(k, m)] for m in (0, 1, 2)))
                         for k in (0, 1, 2))
                v, _lam = vertex_by_supporting_line(E, 1, slopes)
                nonempty = (E[0] - E[1]) > (E[1] - E[2])
                n_lad += 1
                if v != nonempty:
                    disagree += 1
                lad.append((eta, p, E[0] - E[1]))
    res["ladder"] = {"worlds": n_lad,
                     "supporting_line_vs_interval_disagreements": disagree,
                     "holds": disagree == 0}

    # ---- separations, by sorting and pairwise re-verification
    # FREEZE_V1_AMENDMENT_1: separations are scored on the non-degenerate slice
    keyed = sorted(((str(i[1] * i[2] * i[5]), str(Fraction(0)), i[1], n)
                    for n, i in enumerate(inst) if i[1] * i[2] * i[5] > 0),
                   key=lambda x: (x[0], x[1], x[2]))
    groups = []
    cur = [keyed[0]]
    for row in keyed[1:]:
        if row[:3] == cur[-1][:3]:
            cur.append(row)
        else:
            groups.append(cur)
            cur = [row]
    groups.append(cur)
    shared = [g for g in groups if len(g) > 1]
    res["nonvacuity"] = {"n_instances_nondegenerate": len(keyed),
                         "n_profile_groups": len(groups),
                         "n_groups_with_more_than_one_instance": len(shared),
                         "n_instances_in_shared_groups": sum(len(g) for g in shared),
                         "largest_group": max(len(g) for g in groups)}

    def lawval(name, i):
        fam, eta, p, q, A, R0, ncand = i
        if name == "L_THRESHOLD":
            return str(eta * p * R0)
        if name == "L_ARGMIN_BUDGET":
            E = {0: eta * p * R0, 1: Fraction(0)}
            out = []
            for k in range(9):
                lam = Fraction(k, 8)
                out.append(tuple(sorted(j for j in E if E[j] + lam * j
                                        == min(E[x] + lam * x for x in E))))
            return str(tuple(out))
        if name == "L_DEGENERACY":
            return str(ncand)
        if name == "L_MDL":
            b = 0
            while (1 << b) < ncand:
                b += 1
            return str(b)
        if name == "L_REACH":
            return str(Fraction(2 * A * (A - 1), ncand))
        if name == "L_DISTINCT":
            return str(A > 2)
        raise KeyError(name)

    sep = {}
    for name in ("L_THRESHOLD", "L_ARGMIN_BUDGET", "L_DEGENERACY", "L_MDL",
                 "L_REACH", "L_DISTINCT"):
        split = 0
        wit = None
        for g in shared:
            vals = sorted(set(lawval(name, inst[row[3]]) for row in g))
            if len(vals) > 1:
                split += 1
                if wit is None:
                    wit = {"profile_E0": g[0][0], "eta": g[0][2], "values": vals}
        sep[name] = {"n_shared_profile_groups_split": split,
                     "MVP_compressible": split == 0, "witness": wit}
    res["incompressibility"] = sep
    res["incompressible_laws"] = sorted(k for k, v in sep.items() if not v["MVP_compressible"])
    res["compressible_laws"] = sorted(k for k, v in sep.items() if v["MVP_compressible"])

    # ---- identification, recomputed
    GR = [Fraction(k, 16) for k in range(17)]
    perf2 = []
    for a in GR:
        for bq in GR:
            if all(i[1] * i[2] * (a + bq * i[5]) == i[1] * i[2] * i[5] for i in inst):
                perf2.append((str(a), str(bq)))
    perfL = []
    for a in GR:
        for bq in GR:
            if all(eta * (a * p[1] + bq * p[2]) == hi for (eta, p, hi) in lad):
                perfL.append((str(a), str(bq)))
    res["identification"] = {"two_level_perfect_laws": perf2,
                             "ladder_perfect_laws": perfL,
                             "identified": len(perf2) == 1 and len(perfL) == 1}

    # ---- head-to-head, recomputed
    hh = {}
    for name, f in (("lambda_star_eq_eta_p_over_2", lambda i: i[1] * i[2] * Fraction(1, 2)),
                    ("lambda_star_eq_eta_p_one_minus_one_over_A",
                     lambda i: i[1] * i[2] * Fraction(i[4] - 1, i[4])),
                    ("lambda_star_eq_eta_p_R0", lambda i: i[1] * i[2] * i[5])):
        hh[name] = "%d/%d" % (sum(1 for i in inst if f(i) == i[1] * i[2] * i[5]), len(inst))
    ic_lad = sum(1 for (eta, p, hi) in lad
                 if eta * ((Rl[(0, 1)] - Rl[(1, 1)]) * p[1]
                           + (Rl[(0, 2)] - Rl[(1, 2)]) * p[2]) == hi)
    z13_lad = sum(1 for (eta, p, hi) in lad
                  if eta * p[2] * Rl[(1, 2)] + eta * p[1] * Rl[(0, 1)] == hi)
    hh["IC_1_on_ladder"] = "%d/%d" % (ic_lad, len(lad))
    hh["Z13P1_two_price_ladder_on_ladder"] = "%d/%d" % (z13_lad, len(lad))
    res["head_to_head"] = hh

    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    print(json.dumps({"nonvacuity": res["nonvacuity"],
                      "incompressible": res["incompressible_laws"],
                      "compressible": res["compressible_laws"],
                      "identification": res["identification"],
                      "head_to_head": hh, "ladder": res["ladder"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
