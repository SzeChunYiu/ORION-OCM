"""
phase_rv_boundary_route2.py — independent route 2 for the morphology R/V
boundary theorems (MORPHOLOGY_PHASE_RV_BOUNDARY_THEOREM_V2.md, REV-L45-073).

MATERIALLY DISTINCT from route 1 (gmi-morphology-phase-rv-v1/phase_rv_witness.py):
route 1 enumerates the argmin over the three burden functions on grid cells.
Route 2 never enumerates an argmin and never compares three burdens: it
evaluates ONLY the closed forms of the theorems —

  - pairwise thresholds V*_ij(R) = -(da_ij + dS_ij(R)) / db_ij   (T2)
  - region predicates (T4(i)): n wins iff V > V*_ns and V > V*_pn, etc.
  - resource-crossover branches R*(V) (T3(iv), with branch validity),
  - the crossing-convexity identity (E3),
  - the sandwich-for-all-R cell-endpoint exact evaluation (T4(ii) + Sec. 11),

in exact fractions.Fraction arithmetic wherever the inputs are exact.
Numerical root-finding (bisection on a single pairwise burden difference) is
provided as a third, closed-form-independent cross-check.

Registered constants only (no new ones): N=100, H=50, alpha_v=10, alpha_r=1,
the archetype vectors of phase_rv_witness.py, grids anchored at the registered
sweep endpoints R in [2,60], V in [0.1,0.8] (edges of the claim domain V in
[0,1] included), ladder resolutions {40,120,360}, seed 42 (V1 registered).

Python 3.8 safe, stdlib only, no network. Run: python3 -I -B phase_rv_boundary_route2.py
"""

import json
import os
import random
import sys
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

KERNEL_DIV = "div"
KERNEL_HNG = "hng"


# ---------------------------------------------------------------------------
# Definition 1.1: morphology tuple + kernel closed forms (Lemma K)
# ---------------------------------------------------------------------------

class Morph:
    """Morphology tuple (name, a, b, rho); numbers may be float or Fraction."""

    def __init__(self, name, a, b, rho):
        assert rho > 0, "rho must be positive"
        self.name = name
        self.a = a
        self.b = b
        self.rho = rho


def S_of(kernel: str, alpha_r, rho, R):
    """S_M(R) = alpha_r * k(rho / R)  (Definition 1.1; Lemma K closed form)."""
    if kernel == KERNEL_DIV:
        return alpha_r * rho / R
    if kernel == KERNEL_HNG:
        x = rho / R - 1
        return alpha_r * x if x > 0 else (alpha_r * 0)
    raise ValueError(kernel)


def dS_of(kernel: str, alpha_r, rho_i, rho_j, R):
    """dS_ij(R) = S_i(R) - S_j(R)."""
    return S_of(kernel, alpha_r, rho_i, R) - S_of(kernel, alpha_r, rho_j, R)


def burden(kernel: str, alpha_r, m: Morph, R, V):
    """B_M(R,V) = a + b V + S_M(R).  Reference ONLY (bisection cross-check);
    the route-2 predicates below never call this."""
    return m.a + m.b * V + S_of(kernel, alpha_r, m.rho, R)


# ---------------------------------------------------------------------------
# Route 2 core: closed-form pairwise thresholds (T2) + predicates (T4(i))
# ---------------------------------------------------------------------------

def v_star(kernel: str, alpha_r, i: Morph, j: Morph, R):
    """V*_ij(R) = -(da + dS(R)) / db   (T2(i)). Requires db != 0."""
    db = i.b - j.b
    assert db != 0, "T2 requires db_ij != 0"
    return -((i.a - j.a) + dS_of(kernel, alpha_r, i.rho, j.rho, R)) / db


def v_inf(i: Morph, j: Morph):
    """lim_{R->inf} V*_ij(R) = -da_ij / db_ij exactly (K4: S -> 0).
    For the hinge kernel this equals V* on the whole constant cell
    [rho_>, inf); for the divisor kernel it is the exact limit."""
    db = i.b - j.b
    assert db != 0, "v_inf requires db_ij != 0"
    return -(i.a - j.a) / db


def beats(i: Morph, j: Morph, V, v_ij):
    """E1: i strictly beats j at V iff (b_i - b_j)(V - V*_ij) < 0."""
    return (i.b - j.b) * (V - v_ij) < 0


def winner_route2(kernel: str, alpha_r, n: Morph, s: Morph, p: Morph, R, V,
                  tol=0):
    """T4(i) region predicates (requires slope order b_n < b_p < b_s, R+).
    Returns the winning name, or None on a pairwise boundary (exact tie, or
    within tol of one — the knife-edge guard for float grids; tol=0 gives the
    exact-arithmetic boundary semantics)."""
    assert n.b < p.b < s.b, "route-2 predicate requires R+ slope order"
    v_ns = v_star(kernel, alpha_r, n, s, R)
    v_sp = v_star(kernel, alpha_r, s, p, R)
    v_pn = v_star(kernel, alpha_r, p, n, R)
    if tol:
        if (abs(V - v_ns) < tol or abs(V - v_sp) < tol or
                abs(V - v_pn) < tol):
            return None
    elif V == v_ns or V == v_sp or V == v_pn:
        return None  # boundary cell (Definition 1.3 tie set)
    n_wins = beats(n, s, V, v_ns) and beats(n, p, V, v_pn)
    s_wins = beats(s, n, V, v_ns) and beats(s, p, V, v_sp)
    p_wins = beats(p, s, V, v_sp) and beats(p, n, V, v_pn)
    winners = [name for name, w in
               ((n.name, n_wins), (s.name, s_wins), (p.name, p_wins)) if w]
    assert len(winners) == 1, "T4(i) predicates must select exactly one winner"
    return winners[0]


# ---------------------------------------------------------------------------
# T3(iv): resource crossover closed forms with branch validity
# ---------------------------------------------------------------------------

def r_star(kernel: str, alpha_r, n: Morph, s: Morph, V):
    """T3(iv). Hypotheses H3: rho_n > rho_s, db_ns < 0, alpha_r > 0.
    Returns (R*, branch) when G(V) < 0, else None (no crossing, T3(iii))."""
    assert n.rho > s.rho and (n.b - s.b) < 0 and alpha_r > 0, "H3 violated"
    G = (n.a - s.a) + (n.b - s.b) * V
    if G >= 0:
        return None
    if kernel == KERNEL_DIV:
        return (alpha_r * (n.rho - s.rho) / (-G), "div-single")
    num = alpha_r * (n.rho - s.rho)
    if num < (-G) * s.rho:
        return (num / (-G), "hng-both-active")
    return (alpha_r * n.rho / (alpha_r - G), "hng-n-active")


# ---------------------------------------------------------------------------
# Registered instantiations (exact Fractions; Section 1 registered constants)
# ---------------------------------------------------------------------------

def _fr(*args) -> Fraction:
    return Fraction(*args)  # exact: registered constants are terminating decimals


def registered_D() -> Tuple[str, Fraction, List[Morph]]:
    """Instantiation D (V1 doc model): hng kernel, cp = 0, alpha_r = 1."""
    nh, sh = _fr(100), _fr(50)  # N/H = 2 with N=100, H=50
    n = Morph("neural", _fr(15) + _fr(4) + nh / sh * _fr("0.1"),
              nh / sh * _fr("0.1") * _fr(10) + _fr(0), _fr(90))
    s = Morph("symbolic", _fr(5) + _fr(1) + nh / sh * _fr(1),
              nh / sh * _fr(1) * _fr(10) + _fr(0), _fr(12))
    p = Morph("probabilistic", _fr(10) + _fr(2) + nh / sh * _fr("0.5"),
              nh / sh * _fr("0.5") * _fr(10) + _fr(0), _fr(45))
    return KERNEL_HNG, _fr(1), [n, s, p]


def registered_W() -> Tuple[str, Fraction, List[Morph]]:
    """Instantiation W (V1 witness model): div kernel, alpha_r = 1, cp as
    registered (0.3 / 4.0 / 2.0). Same a and rho as D."""
    _, _, d = registered_D()
    cps = {"neural": _fr("0.3"), "symbolic": _fr(4), "probabilistic": _fr(2)}
    out = []
    for m in d:
        out.append(Morph(m.name, m.a, m.b + cps[m.name], m.rho))
    return KERNEL_DIV, _fr(1), out


# ---------------------------------------------------------------------------
# Sandwich-for-all-R: exact cell-endpoint evaluation (T4(ii) + Section 11)
# ---------------------------------------------------------------------------

def sandwich_min_gap(kernel: str, alpha_r, n: Morph, s: Morph, p: Morph):
    """Exact infimum of V*_pn(R) - V*_sp(R) over R > 0 (T4(ii) sandwich gap).

    The difference is p + q/R on each cell of the joint breakpoint partition
    (K6). Its infimum over a cell is attained at a cell endpoint (or as a
    0+/inf limit). Returns (min_gap, is_strictly_positive_for_all_R, witnesses)
    in exact arithmetic when inputs are exact.
    """
    v_star(kernel, alpha_r, s, p, _fr(1))  # asserts db_sp != 0
    v_star(kernel, alpha_r, p, n, _fr(1))  # asserts db_pn != 0
    bps = sorted({s.rho, p.rho, n.rho})
    # cells: (0, bps[0]), [bps[0], bps[1]), ..., [bps[-1], inf)
    cell_lefts = [None] + bps  # None = open 0+ limit
    cell_rights = bps + [None]  # None = inf limit
    def gap_at(R):
        return v_star(kernel, alpha_r, p, n, R) - v_star(kernel, alpha_r, s, p, R)
    worst = None
    for left, right in zip(cell_lefts, cell_rights):
        # representative interior point of the cell
        lo = Fraction(1, 1000000) if left is None else left
        hi = (right if right is not None else (lo * 1000000 + 1))
        # express gap = c0 + c1/R on this cell via two exact evaluations
        r1, r2 = lo + (hi - lo) / 3, lo + 2 * (hi - lo) / 3
        g1, g2 = gap_at(r1), gap_at(r2)
        c1 = (g2 - g1) / ((1 / r2) - (1 / r1))
        c0 = g1 - c1 * (1 / r1)
        # infimum of c0 + c1/R on the cell:
        vals = []
        if left is not None:
            vals.append(c0 + c1 / left)
        else:
            vals.append(None)  # 0+ limit: +inf if c1>0, -inf if c1<0, c0 if 0
        if right is not None:
            vals.append(c0 + c1 / right)
        else:
            vals.append(c0)  # inf limit
        # resolve the 0+ limit
        fin = [v for v in vals if v is not None]
        if vals[0] is None:
            if c1 < 0:
                return (c1, False, ("unbounded-below-as-R->0", left, right))
            # c1 >= 0: 0+ limit is +inf or c0; not the infimum
        m = min(fin)
        if worst is None or m < worst:
            worst = m
    return (worst, worst > 0, ("min-over-cell-endpoints", worst))


# ---------------------------------------------------------------------------
# Bisection cross-check (closed-form-independent third route)
# ---------------------------------------------------------------------------

def bisect_root(f, lo, hi, iters=200):
    """Bisection on f over [lo, hi]; returns root or None if no sign change."""
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if (flo < 0) == (fhi < 0):
        return None
    for _ in range(iters):
        mid = (lo + hi) / 2
        fm = f(mid)
        if fm == 0:
            return mid
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi, fhi = mid, fm
    return (lo + hi) / 2


def v_star_by_bisection(kernel, alpha_r, i, j, R, lo=-1000.0, hi=1000.0):
    """Root of D_ij(R, .) in V (D1 affine). Float route."""
    f = lambda V: (i.a - j.a) + (i.b - j.b) * V + \
        dS_of(kernel, alpha_r, i.rho, j.rho, R)
    return bisect_root(f, lo, hi)


def r_star_by_bisection(kernel, alpha_r, n, s, V, hi=None):
    """Root of D_ns(., V) in R on (0, rho_n] (hng) / (0, hi] (div). Float."""
    f = lambda R: (n.a - s.a) + (n.b - s.b) * V + \
        dS_of(kernel, alpha_r, n.rho, s.rho, R)
    top = hi if hi is not None else (float(n.rho) if kernel == KERNEL_HNG
                                     else max(float(n.rho) * 10, 1e6))
    return bisect_root(f, top * Fraction(1, 10 ** 12) if isinstance(top, Fraction)
                       else top * 1e-12, top)


# ---------------------------------------------------------------------------
# Route-1 witness import (the actual V1 file; never modified)
# ---------------------------------------------------------------------------

def import_route1():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "gmi-morphology-phase-rv-v1",
                        "phase_rv_witness.py")
    import importlib.util
    spec = importlib.util.spec_from_file_location("phase_rv_witness", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def route1_grid(kernel_unused, morphs_w, R_values, V_values):
    """Route-1 winner grid via the V1 witness argmin (floats)."""
    w = import_route1()
    return w.compute_phase_grid(morphs_w, R_values, V_values, N=100, H=50.0,
                                alpha_v=10.0)


# ---------------------------------------------------------------------------
# Battery
# ---------------------------------------------------------------------------

REGISTERED_R = [2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 60.0]
REGISTERED_V = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
LADDER = [40, 120, 360]
SEED = 42


def _float_morphs(morphs):
    return [Morph(m.name, float(m.a), float(m.b), float(m.rho)) for m in morphs]


def battery() -> Dict:
    """Full two-route battery. Returns a summary dict (receipt payload)."""
    out: Dict = {}

    # ---- exact registered targets (Section 11) ----
    kD, aD, (nD, sD, pD) = registered_D()
    kW, aW, (nW, sW, pW) = registered_W()
    tg = {}
    tg["D/V*_ns(inf)"] = v_inf(nD, sD)
    tg["D/V*_sp(inf)"] = v_inf(sD, pD)
    tg["D/V*_pn(inf)"] = v_inf(pD, nD)
    tg["W/V*_ns(inf)"] = v_inf(nW, sW)
    tg["W/V*_sp(inf)"] = v_inf(sW, pW)
    tg["W/V*_pn(inf)"] = v_inf(pW, nW)
    rs08 = r_star(kW, aW, nW, sW, _fr("0.8"))
    tg["W/R*(0.8)"] = rs08[0]
    expected = {
        "D/V*_ns(inf)": Fraction(28, 45),
        "D/V*_sp(inf)": Fraction(1, 2),
        "D/V*_pn(inf)": Fraction(31, 40),
        "W/V*_ns(inf)": Fraction(112, 217),
        "W/V*_sp(inf)": Fraction(5, 12),
        "W/V*_pn(inf)": Fraction(62, 97),
        "W/R*(0.8)": Fraction(975, 77),
    }
    tg_ok = {k: (tg[k] == expected[k], str(tg[k]), str(expected[k]))
             for k in expected}
    out["exact_targets"] = {k: v[0] for k, v in tg_ok.items()}
    out["exact_targets_detail"] = {k: v[1:] for k, v in tg_ok.items()}
    out["exact_targets_all_match"] = all(v[0] for v in tg_ok.values())

    # ---- sandwich for all R (exact) ----
    sw_D = sandwich_min_gap(kD, aD, nD, sD, pD)
    sw_W = sandwich_min_gap(kW, aW, nW, sW, pW)
    out["sandwich_all_R"] = {
        "D": {"holds": sw_D[1], "min_gap": str(sw_D[0])},
        "W": {"holds": sw_W[1], "min_gap": str(sw_W[0])},
    }

    # ---- two-route winner agreement, registered 8x8 grid (exact) ----
    w = import_route1()
    morphs_witness = w.register_archetypes()
    grid1 = route1_grid(None, morphs_witness, REGISTERED_R, REGISTERED_V)
    agree = disagree = boundary = 0
    disagreements = []
    for i, V in enumerate(REGISTERED_V):
        for j, R in enumerate(REGISTERED_R):
            # exact route 2 on Fractions at the exact grid point
            w2 = winner_route2(kW, aW, nW, sW, pW, _fr(R), _fr(V))
            if w2 is None:
                boundary += 1
                continue
            if w2 == grid1[i][j]:
                agree += 1
            else:
                disagree += 1
                disagreements.append((R, V, w2, grid1[i][j]))
    out["registered_8x8"] = {
        "agree": agree, "disagree": disagree, "boundary_cells": boundary,
        "disagreements": disagreements,
        "all_winners_route1": sorted({c for row in grid1 for c in row}),
    }

    # ---- resolution ladder + claim-domain edges (float route 2 vs route 1) ----
    ladder = {}
    for res in LADDER:
        Rs = [2.0 + (60.0 - 2.0) * k / (res - 1) for k in range(res)]
        Vs = [k / (res - 1) for k in range(res)]  # [0, 1] claim-domain edges
        nWf, sWf, pWf = _float_morphs([nW, sW, pW])
        g1 = route1_grid(None, morphs_witness, Rs, Vs)
        ag = dis = bnd = 0
        diss = []
        for i, V in enumerate(Vs):
            for j, R in enumerate(Rs):
                w2 = winner_route2(KERNEL_DIV, 1.0, nWf, sWf, pWf, R, V,
                                   tol=1e-9)
                if w2 is None:
                    bnd += 1
                    continue
                if w2 == g1[i][j]:
                    ag += 1
                else:
                    dis += 1
                    if len(diss) < 5:
                        diss.append((R, V, w2, g1[i][j]))
        ladder[res] = {"agree": ag, "disagree": dis, "boundary_cells": bnd,
                       "disagreements_sample": diss}
    out["ladder"] = ladder

    # ---- fixed-seed random points ----
    rng = random.Random(SEED)
    nWf, sWf, pWf = _float_morphs([nW, sW, pW])
    ag = dis = bnd = 0
    for _ in range(5000):
        R = 2.0 + (60.0 - 2.0) * rng.random()
        V = rng.random()
        w2 = winner_route2(KERNEL_DIV, 1.0, nWf, sWf, pWf, R, V, tol=1e-9)
        if w2 is None:
            bnd += 1
            continue
        burdens = {"neural": None, "symbolic": None, "probabilistic": None}
        m = {"neural": nWf, "symbolic": sWf, "probabilistic": pWf}
        best = min(m, key=lambda nm: m[nm].a + m[nm].b * V +
                   S_of(KERNEL_DIV, 1.0, m[nm].rho, R))
        # (this min is the check ORACLE, not route 2's predicate)
        if w2 == best:
            ag += 1
        else:
            dis += 1
    out["random_5000"] = {"agree": ag, "disagree": dis, "boundary": bnd}

    # ---- closed forms vs bisection (both kernels, registered + draws) ----
    max_dev_v = 0.0
    max_dev_r = 0.0
    for kernel, alpha_r, morphs in ((kD, aD, [nD, sD, pD]),
                                    (kW, aW, [nW, sW, pW])):
        mf = _float_morphs(morphs)
        for _ in range(200):
            R = 0.05 + 200.0 * rng.random()
            i, j = mf[0], mf[1]
            vs = v_star(kernel, float(alpha_r), i, j, R)
            vb = v_star_by_bisection(kernel, float(alpha_r), i, j, R)
            if vb is not None:
                max_dev_v = max(max_dev_v, abs(vs - float(vb)))
        for _ in range(200):
            V = rng.random()
            rs = r_star(kernel, alpha_r, morphs[0], morphs[1], _fr(V)
                        if isinstance(alpha_r, Fraction) else V)
            rb = r_star_by_bisection(kernel, float(alpha_r),
                                     _float_morphs([morphs[0]])[0],
                                     _float_morphs([morphs[1]])[0], V)
            if rs is None:
                if rb is not None:
                    # closed form says no crossing but bisection found one
                    max_dev_r = float("inf")
            elif rb is not None:
                max_dev_r = max(max_dev_r, abs(float(rs[0]) - float(rb)))
    out["bisection_max_dev"] = {"v_star": max_dev_v, "r_star": max_dev_r}

    # ---- structural properties on random exact draws ----
    out["structural"] = structural_properties(SEED, draws=300)
    return out


def structural_properties(seed: int, draws: int) -> Dict:
    """K3/D2/T3/E3/T4 property checks on random Fraction parameter draws."""
    rng = random.Random(seed)
    res = {"draws": draws, "skipped": 0, "violations": []}

    def viol(msg):
        res["violations"].append(msg)

    for t in range(draws):
        kernel = [KERNEL_DIV, KERNEL_HNG][t % 2]
        alpha_r = [Fraction(0), Fraction(1), Fraction(2),
                   Fraction(1, 2)][t % 4]

        def rmorph(name):
            return Morph(name,
                         Fraction(rng.randrange(0, 400), 10),
                         Fraction(rng.randrange(-300, 300), 10),
                         Fraction(rng.randrange(1, 1000), 10))

        m1, m2 = rmorph("i"), rmorph("j")
        if m1.b == m2.b:
            res["skipped"] += 1
            continue
        # K3: S non-increasing; D2: dS non-increasing when rho_i > rho_j
        Rs = [Fraction(rng.randrange(1, 10 ** 6), 10 ** 3) for _ in range(30)]
        Rs.sort()
        prev_s = prev_d = None
        for R in Rs:
            sv = S_of(kernel, alpha_r, m1.rho, R)
            if prev_s is not None and sv > prev_s:
                viol("K3: S increased at kernel=%s R=%s" % (kernel, R))
            prev_s = sv
            if m1.rho > m2.rho:
                dv = dS_of(kernel, alpha_r, m1.rho, m2.rho, R)
                if prev_d is not None and dv > prev_d:
                    viol("D2: dS increased at kernel=%s R=%s" % (kernel, R))
                prev_d = dv
        # T2: v_star matches a Fraction solve of D = 0 for the pair
        R = Rs[7]
        vs = v_star(kernel, alpha_r, m1, m2, R)
        Dv = (m1.a - m2.a) + (m1.b - m2.b) * vs + \
            dS_of(kernel, alpha_r, m1.rho, m2.rho, R)
        if Dv != 0:
            viol("T2: v_star not a root (kernel=%s)" % kernel)
        # T3: branch exclusivity + root property under H3
        n3, s3 = rmorph("n"), rmorph("s")
        if n3.rho > s3.rho and n3.b < s3.b and alpha_r > 0:
            V = Fraction(rng.randrange(0, 10), 10)
            rs = r_star(kernel, alpha_r, n3, s3, V)
            G = (n3.a - s3.a) + (n3.b - s3.b) * V
            if rs is None:
                if G < 0:
                    viol("T3(ii): missing crossing though G<0")
            else:
                D = (n3.a - s3.a) + (n3.b - s3.b) * V + \
                    dS_of(kernel, alpha_r, n3.rho, s3.rho, rs[0])
                if abs(D) != 0:
                    viol("T3(iv): R* not a root (kernel=%s branch=%s)"
                         % (kernel, rs[1]))
                if kernel == KERNEL_HNG:
                    A = alpha_r * (n3.rho - s3.rho) / (-G)
                    condA = A < s3.rho
                    if condA and rs[1] != "hng-both-active":
                        viol("T3(iv): branch A condition held but %s" % rs[1])
                    if (not condA) and rs[1] != "hng-n-active":
                        viol("T3(iv): branch B condition held but %s" % rs[1])
        # E3: crossing convexity under slope order
        a3, b3, c3 = rmorph("s"), rmorph("p"), rmorph("n")
        if a3.b > b3.b > c3.b and a3.b != b3.b and b3.b != c3.b:
            R = Rs[11]
            v_sp = v_star(kernel, alpha_r, a3, b3, R)
            v_pn = v_star(kernel, alpha_r, b3, c3, R)
            v_sn = v_star(kernel, alpha_r, a3, c3, R)
            lhs = v_sn * (a3.b - c3.b)
            rhs = v_sp * (a3.b - b3.b) + v_pn * (b3.b - c3.b)
            if lhs != rhs:
                viol("E3: identity failed (kernel=%s)" % kernel)
            if not (min(v_sp, v_pn) <= v_sn <= max(v_sp, v_pn)):
                viol("E3: betweenness failed (kernel=%s)" % kernel)
    return res


def _main(argv):
    summary = battery()
    pretty = json.dumps(summary, indent=1, default=str)
    print(pretty)
    if len(argv) > 2 and argv[1] == "--emit-receipt":
        with open(argv[2], "w") as fh:
            json.dump(summary, fh, indent=1, default=str)
        print("receipt written: %s" % argv[2], file=sys.stderr)
    # hard-fail signals
    ok = (summary["exact_targets_all_match"]
          and summary["registered_8x8"]["disagree"] == 0
          and all(lad["disagree"] == 0 for lad in summary["ladder"].values())
          and summary["random_5000"]["disagree"] == 0
          and summary["sandwich_all_R"]["D"]["holds"]
          and summary["sandwich_all_R"]["W"]["holds"]
          and not summary["structural"]["violations"]
          and summary["bisection_max_dev"]["v_star"] < 1e-6
          and summary["bisection_max_dev"]["r_star"] < 1e-6)
    print("ROUTE2_BATTERY_%s" % ("GREEN" if ok else "RED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
