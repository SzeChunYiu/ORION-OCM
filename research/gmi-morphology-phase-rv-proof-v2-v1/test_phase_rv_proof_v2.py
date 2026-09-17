"""
test_phase_rv_proof_v2.py — controls for MORPHOLOGY_PHASE_RV_BOUNDARY_THEOREM_V2
(REV-L45-073 proof strengthening). Verifies, in exact fractions.Fraction
arithmetic wherever the inputs are exact:

  - the registered-instantiation closed-form targets (Theorem doc Sec. 11)
  - two-route winner agreement: route 2 closed-form predicates vs the V1
    witness argmin (route 1), registered 8x8 grid + resolution ladder + edges
  - sandwich nonemptiness for ALL R > 0 (both instantiations; T4(ii))
  - T3 branch selection, root property, and R*(V) strict decrease
  - T2(iv)/C3(ii) V*(R) monotonicity; T2(iii) non-linearity of the hinge
    middle cell (the V1 "piecewise-linear" correction pinned)
  - E3 crossing convexity; T4(iii) winner-sequence law
  - C1' corner regimes incl. the explicit R_0 threshold
  - CX-1 sign-error regression: the V1 printed R* formula is negative in the
    crossing regime while the corrected R* is positive
  - P5 held-out determinism identity (control status)

Python 3.8 safe, unittest, stdlib only, no network.
Run: python3 -I -B test_phase_rv_proof_v2.py -v
"""

import os
import sys
import unittest
from fractions import Fraction

_SPEC = None
_MOD = None
_W1 = None


def _import_route2():
    global _SPEC, _MOD
    if _MOD is not None:
        return _MOD
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "phase_rv_boundary_route2.py")
    import importlib.util
    _SPEC = importlib.util.spec_from_file_location("phase_rv_boundary_route2",
                                                   path)
    _MOD = importlib.util.module_from_spec(_SPEC)
    _SPEC.loader.exec_module(_MOD)
    return _MOD


def _import_route1():
    global _W1
    if _W1 is not None:
        return _W1
    r2 = _import_route2()
    _W1 = r2.import_route1()
    return _W1


def _fr(*args):
    return Fraction(*args)


class TestExactTargets(unittest.TestCase):
    """Sec. 11 control targets, exact."""

    def test_registered_targets(self):
        r2 = _import_route2()
        kD, aD, (nD, sD, pD) = r2.registered_D()
        kW, aW, a3 = r2.registered_W()
        nW, sW, pW = a3
        self.assertEqual(r2.v_inf(nD, sD), Fraction(28, 45))
        self.assertEqual(r2.v_inf(sD, pD), Fraction(1, 2))
        self.assertEqual(r2.v_inf(pD, nD), Fraction(31, 40))
        self.assertEqual(r2.v_inf(nW, sW), Fraction(112, 217))
        self.assertEqual(r2.v_inf(sW, pW), Fraction(5, 12))
        self.assertEqual(r2.v_inf(pW, nW), Fraction(62, 97))
        # hinge kernel: v_inf equals v_star on the constant cell R >= rho_>
        self.assertEqual(r2.v_star(kD, aD, nD, sD, Fraction(10 ** 9)),
                         Fraction(28, 45))

    def test_registered_crossover_W(self):
        r2 = _import_route2()
        kW, aW, (nW, sW, pW) = r2.registered_W()
        rs = r2.r_star(kW, aW, nW, sW, _fr("0.8"))
        self.assertIsNotNone(rs)
        self.assertEqual(rs[0], Fraction(975, 77))
        self.assertEqual(rs[1], "div-single")

    def test_registered_crossover_D_branch(self):
        r2 = _import_route2()
        kD, aD, (nD, sD, pD) = r2.registered_D()
        # V=0.8: G = 11.2 - 18*0.8 = -3.2 < 0; A-branch needs
        # 78 < 3.2*12 = 38.4 (false) => n-active branch
        rs = r2.r_star(kD, aD, nD, sD, _fr("0.8"))
        self.assertEqual(rs[1], "hng-n-active")
        # R*_B = 90/(1 + 3.2) = 90/4.2 = 150/7
        self.assertEqual(rs[0], Fraction(150, 7))
        # V in (0.6222, 0.9833) n-active; V = 0.99: G = 11.2 - 17.82 = -6.62,
        # A-branch needs 78 < 6.62*12 = 79.44 (true) => both-active
        rs2 = r2.r_star(kD, aD, nD, sD, _fr("0.99"))
        self.assertEqual(rs2[1], "hng-both-active")
        self.assertEqual(rs2[0], Fraction(78 * 100, 662))  # 78/6.62


class TestTwoRouteAgreement(unittest.TestCase):
    """Route 2 closed-form predicates vs route 1 V1-witness argmin."""

    def test_registered_8x8_exact_agreement(self):
        r2 = _import_route2()
        w1 = _import_route1()
        kW, aW, (nW, sW, pW) = r2.registered_W()
        grid1 = w1.compute_phase_grid(w1.register_archetypes(),
                                      r2.REGISTERED_R, r2.REGISTERED_V,
                                      N=100, H=50.0, alpha_v=10.0)
        agree = disagree = 0
        for i, V in enumerate(r2.REGISTERED_V):
            for j, R in enumerate(r2.REGISTERED_R):
                w2 = r2.winner_route2(kW, aW, nW, sW, pW,
                                      _fr(R), _fr(V))
                if w2 is None:
                    continue  # boundary cell (none exist on this grid)
                if w2 == grid1[i][j]:
                    agree += 1
                else:
                    disagree += 1
        self.assertEqual(disagree, 0)
        self.assertEqual(agree, 64)

    def test_ladder_and_domain_edges(self):
        r2 = _import_route2()
        w1 = _import_route1()
        kW, aW, (nW, sW, pW) = r2.registered_W()
        nWf, sWf, pWf = r2._float_morphs([nW, sW, pW])
        morphs = w1.register_archetypes()
        for res in (40, 120):
            Rs = [2.0 + 58.0 * k / (res - 1) for k in range(res)]
            Vs = [k / (res - 1) for k in range(res)]
            g1 = w1.compute_phase_grid(morphs, Rs, Vs, N=100, H=50.0,
                                       alpha_v=10.0)
            disagree = 0
            for i, V in enumerate(Vs):
                for j, R in enumerate(Rs):
                    w2 = r2.winner_route2(kW, 1.0, nWf, sWf, pWf, R, V,
                                          tol=1e-9)
                    if w2 is not None and w2 != g1[i][j]:
                        disagree += 1
            self.assertEqual(disagree, 0, "res=%d" % res)

    def test_random_points_agree(self):
        import random
        r2 = _import_route2()
        kW, aW, (nW, sW, pW) = r2.registered_W()
        nWf, sWf, pWf = r2._float_morphs([nW, sW, pW])
        rng = random.Random(42)
        disagree = 0
        checked = 0
        for _ in range(1000):
            R = 2.0 + 58.0 * rng.random()
            V = rng.random()
            w2 = r2.winner_route2(kW, 1.0, nWf, sWf, pWf, R, V, tol=1e-9)
            if w2 is None:
                continue
            m = {"neural": nWf, "symbolic": sWf, "probabilistic": pWf}
            best = min(m, key=lambda nm: m[nm].a + m[nm].b * V +
                       r2.S_of(kW, 1.0, m[nm].rho, R))
            checked += 1
            if w2 != best:
                disagree += 1
        self.assertEqual(disagree, 0)
        self.assertGreater(checked, 900)


class TestSandwichAllR(unittest.TestCase):
    """T4(ii): p-band nonempty for every R > 0 at the registered point."""

    def test_sandwich_holds_both_instantiations(self):
        r2 = _import_route2()
        kD, aD, (nD, sD, pD) = r2.registered_D()
        kW, aW, (nW, sW, pW) = r2.registered_W()
        gap_D, holds_D, _ = r2.sandwich_min_gap(kD, aD, nD, sD, pD)
        gap_W, holds_W, _ = r2.sandwich_min_gap(kW, aW, nW, sW, pW)
        self.assertTrue(holds_D)
        self.assertTrue(holds_W)
        # infimum attained as R -> inf: V*_pn - V*_sp at S=0
        self.assertEqual(gap_D, Fraction(31, 40) - Fraction(1, 2))
        self.assertEqual(gap_W, Fraction(62, 97) - Fraction(5, 12))

    def test_e3_identity_registered(self):
        r2 = _import_route2()
        for kernel, alpha_r, (n, s, p) in (r2.registered_D(),
                                           r2.registered_W()):
            for R in (_fr(1), _fr(7), _fr(30), _fr(200)):
                v_sp = r2.v_star(kernel, alpha_r, s, p, R)
                v_pn = r2.v_star(kernel, alpha_r, p, n, R)
                v_sn = r2.v_star(kernel, alpha_r, s, n, R)
                lhs = v_sn * (s.b - n.b)
                rhs = v_sp * (s.b - p.b) + v_pn * (p.b - n.b)
                self.assertEqual(lhs, rhs)
                self.assertTrue(min(v_sp, v_pn) <= v_sn <= max(v_sp, v_pn))


class TestMonotonicityAndBranches(unittest.TestCase):
    """T2(iv)/C3(ii)/T3(v) comparative statics, exact."""

    def test_v_star_nonincreasing_in_R(self):
        r2 = _import_route2()
        for kernel, alpha_r, (n, s, p) in (r2.registered_D(),
                                           r2.registered_W()):
            Rs = [_fr(k) for k in range(1, 300)]
            for i, j in ((n, s), (s, p), (p, n)):
                prev = None
                for R in Rs:
                    v = r2.v_star(kernel, alpha_r, i, j, R)
                    if prev is not None:
                        self.assertLessEqual(v, prev)
                    prev = v

    def test_r_star_strictly_decreasing_in_V(self):
        r2 = _import_route2()
        for kernel, alpha_r, (n, s, p) in (r2.registered_D(),
                                           r2.registered_W()):
            db = n.b - s.b
            da = n.a - s.a
            Vs = [_fr(k, 100) for k in range(60, 100)]  # 0.60 .. 0.99
            prev = None
            for V in Vs:
                if da + db * V >= 0:
                    continue  # no crossing regime (T3(iii))
                rs = r2.r_star(kernel, alpha_r, n, s, V)
                self.assertIsNotNone(rs)
                if prev is not None:
                    self.assertLess(rs[0], prev)
                prev = rs[0]

    def test_hinge_middle_cell_not_linear(self):
        """T2(iii) correction: the hinge middle cell is reciprocal-affine,
        NOT linear — pin the correction with an exact second difference."""
        r2 = _import_route2()
        kD, aD, (nD, sD, pD) = r2.registered_D()
        # middle cell [rho_s=12, rho_n=90) for the pair (n, s)
        h = _fr(1)
        v1 = r2.v_star(kD, aD, nD, sD, _fr(30))
        v2 = r2.v_star(kD, aD, nD, sD, _fr(31))
        v3 = r2.v_star(kD, aD, nD, sD, _fr(32))
        # linear iff v2 - v1 == v3 - v2
        self.assertNotEqual(v2 - v1, v3 - v2)

    def test_cx1_sign_error_regression(self):
        """CX-1: the V1 printed R* formula (numerator over G(V)) is NEGATIVE
        in the crossing regime, while the corrected R* is positive."""
        r2 = _import_route2()
        kW, aW, (nW, sW, pW) = r2.registered_W()
        V = _fr("0.8")
        G = (nW.a - sW.a) + (nW.b - sW.b) * V
        self.assertLess(G, 0)  # crossing regime
        printed_v1 = (nW.rho - sW.rho) / G  # V1 Corollary 2 as printed
        self.assertLess(printed_v1, 0)
        corrected = r2.r_star(kW, aW, nW, sW, V)
        self.assertGreater(corrected[0], 0)


class TestEnvelopeSequence(unittest.TestCase):
    """T4(iii): winner sequence along V is a subsequence of (s, p, n)."""

    def test_sequence_law_registered(self):
        r2 = _import_route2()
        order = {"symbolic": 0, "probabilistic": 1, "neural": 2}
        for kernel, alpha_r, (n, s, p) in (r2.registered_D(),
                                           r2.registered_W()):
            for R in (_fr(3), _fr(15), _fr(40), _fr(1000)):
                seq = []
                for k in range(0, 1001):
                    V = _fr(k, 1000)
                    w = r2.winner_route2(kernel, alpha_r, n, s, p, R, V)
                    if w is None:
                        continue
                    if not seq or seq[-1] != w:
                        seq.append(w)
                self.assertLessEqual(len(seq), 3)
                ranks = [order[x] for x in seq]
                self.assertEqual(ranks, sorted(ranks),
                                 "sequence not slope-ordered: %s" % seq)

    def test_probabilistic_band_matches_domain_criterion(self):
        """T4(i)/(ii): p appears in the claim domain [0,1] iff the band
        (V*_sp, V*_pn) intersects it; the intersection is governed exactly by
        V*_sp(R) < 1 (V*_pn > 0 always at the registered point). Note this is
        a genuinely conditional statement: for the hinge model at R=5 the
        band is (1.16, 1.9) — above the domain — so symbolic wins everywhere
        (a C1'(a) corner fact), while at R >= ~12 the band has entered."""
        r2 = _import_route2()
        for kernel, alpha_r, (n, s, p) in (r2.registered_D(),
                                           r2.registered_W()):
            for R in (_fr(5), _fr(12), _fr(20), _fr(60), _fr(500)):
                v_sp = r2.v_star(kernel, alpha_r, s, p, R)
                band_intersects = v_sp < 1
                found = None
                for k in range(0, 1001):
                    V = _fr(k, 1000)
                    w = r2.winner_route2(kernel, alpha_r, n, s, p, R, V)
                    if w == "probabilistic":
                        found = (R, V)
                        break
                self.assertEqual(
                    found is not None, band_intersects,
                    "R=%s kernel=%s v_sp=%s found=%s" %
                    (R, kernel, float(v_sp), found))


class TestCornerRegimes(unittest.TestCase):
    """C1' corners under R+ at the registered point."""

    def test_sparse_corner_symbolic_everywhere_below_R0(self):
        r2 = _import_route2()
        kW, aW, (nW, sW, pW) = r2.registered_W()
        # C1'(a) explicit threshold: R_0 = min(78/10.5, 33/7) = 33/7
        m_ns = (nW.a - sW.a) + min(nW.b - sW.b, 0)
        m_ps = (pW.a - sW.a) + min(pW.b - sW.b, 0)
        r0 = min((nW.rho - sW.rho) / (-m_ns), (pW.rho - sW.rho) / (-m_ps))
        self.assertEqual(r0, Fraction(33, 7))
        for k in range(1, 33):
            R = _fr(k, 7)  # R = k/7 < 33/7
            for j in range(0, 11):
                V = _fr(j, 10)
                w = r2.winner_route2(kW, aW, nW, sW, pW, R, V)
                if w is not None:
                    self.assertEqual(w, "symbolic",
                                     "R=%s V=%s" % (R, V))

    def test_high_corner_neural(self):
        r2 = _import_route2()
        for kernel, alpha_r, (n, s, p) in (r2.registered_D(),
                                           r2.registered_W()):
            w = r2.winner_route2(kernel, alpha_r, n, s, p, _fr(10 ** 6),
                                 _fr(1))
            self.assertEqual(w, "neural")

    def test_build_corner_symbolic_at_V0(self):
        r2 = _import_route2()
        for kernel, alpha_r, (n, s, p) in (r2.registered_D(),
                                           r2.registered_W()):
            for R in (_fr(2), _fr(12), _fr(50), _fr(10 ** 6)):
                w = r2.winner_route2(kernel, alpha_r, n, s, p, R, _fr(0))
                self.assertEqual(w, "symbolic", "R=%s" % R)


class TestHeldoutControl(unittest.TestCase):
    """P5: determinism identity (control status, no discriminative power)."""

    def test_heldout_accuracy_is_exactly_one(self):
        r2 = _import_route2()
        w1 = _import_route1()
        result = w1.held_out_prediction(
            w1.register_archetypes(), r2.REGISTERED_R, r2.REGISTERED_V,
            fraction_held=0.25, seed=42)
        self.assertEqual(result["prediction_accuracy"], 1.0)


class TestStructuralDraws(unittest.TestCase):
    """Random exact-draw property battery (smaller than the receipt run)."""

    def test_no_violations(self):
        r2 = _import_route2()
        res = r2.structural_properties(42, draws=60)
        self.assertEqual(res["violations"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
