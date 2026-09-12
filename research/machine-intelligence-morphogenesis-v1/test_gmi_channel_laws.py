"""Boundary-case lattice of the GMI channel capability law family (RV-377-130 .. 134).

Every identity here is an analytic containment claim made in a freeze document; the tests
pin the closed forms in gmi_channel_laws.py to those claims. No world is drawn.
"""
import math

import gmi_channel_laws as cl

L = 64
RS = list(range(0, 65, 4))


def close(a, b, tol=1e-12):
    return abs(a - b) <= tol


# ---- CL-1 / CL-2 --------------------------------------------------------------------

def test_cl2_contains_cl1_at_p0():
    for r in RS:
        assert close(cl.ti2(L, r, 0.0), cl.ti1(L, r))


# ---- CL-3 noisy development -----------------------------------------------------------

def test_cl3_q0_is_cl1_for_every_k():
    for k in (1, 3, 5, 7):
        for r in RS:
            assert close(cl.ceiling3(L, r, 0.0, k), cl.ti1(L, r))


def test_cl3_q_half_collapses_to_half():
    for k in (1, 3, 5):
        for r in RS:
            assert close(cl.ceiling3(L, r, 0.5, k), 0.5)


def test_cl3_q1_k1_is_cl1_by_inversion():
    for r in RS:
        assert close(cl.ceiling3(L, r, 1.0, 1), cl.ti1(L, r))
        assert close(cl.naive3(L, r, 1.0, 1), 0.5 - r / (2 * L))


def test_cl3_naive_equals_ceiling_iff_q_at_most_half():
    for q in (0.0, 0.1, 0.25, 0.4, 0.5):
        assert close(cl.naive3(L, 32, q), cl.ceiling3(L, 32, q))
    for q in (0.6, 0.75, 1.0):
        assert cl.naive3(L, 32, q) < cl.ceiling3(L, 32, q)
        assert cl.naive3(L, 32, q) < 0.5


def test_cl3_majority_improves_with_k_below_half():
    for q in (0.1, 0.25, 0.4):
        assert close(cl.majority_correct(1, q), 1 - q)
        assert cl.majority_correct(1, q) < cl.majority_correct(3, q) < cl.majority_correct(5, q)
        assert cl.unanimity_correct(3, q) < cl.majority_correct(3, q)


# ---- CL-4 bounded state ---------------------------------------------------------------

def test_cl4_s_ge_r_is_cl1_and_s0_is_half():
    for r in (7, 15, 31, 63):
        assert close(cl.ceiling4(L, r, r), cl.ti1(L, r))
        assert close(cl.ceiling4(L, r, r + 5), cl.ti1(L, r))
        assert close(cl.ceiling4(L, r, 0), 0.5)


def test_cl4_coincides_with_truncation_at_s_r_minus_1_and_beats_it_between():
    for r in (7, 15, 31, 63):
        assert close(cl.ceiling4(L, r, r - 1), cl.naive4(L, r, r - 1))
        for s in range(1, r - 1):
            assert cl.ceiling4(L, r, s) > cl.naive4(L, r, s) + 1e-9


def test_cl4_perfect_code_points_exact():
    assert close(cl.sphere_covering_distortion(7, 4), 1 / 8)        # Hamming(7,4)
    assert close(cl.sphere_covering_distortion(15, 11), 1 / 16)     # Hamming(15,11)
    assert close(cl.sphere_covering_distortion(3, 1), 1 / 4)        # repetition r=3
    assert close(cl.sphere_covering_distortion(7, 1), 308 / 896)    # repetition r=7
    assert close(cl.sphere_covering_distortion(7, 6), 1 / 14)       # even-weight r=7
    assert cl.hamming_m(7) == 3 and cl.hamming_m(63) == 6 and cl.hamming_m(8) is None


def test_cl4_distortion_monotone_in_s():
    for r in (7, 15):
        prev = 1.0
        for s in range(0, r + 1):
            d = cl.sphere_covering_distortion(r, s)
            assert d <= prev + 1e-12
            prev = d


def test_cl4_hamming_quantizer_is_a_perfect_code():
    # every 7-bit string lands within distance 1 of its codeword; exactly 16 codewords
    words = set()
    for x in range(128):
        bits = [(x >> i) & 1 for i in range(7)]
        c = cl._hamming_quantize(bits, 3)
        assert sum(a != b for a, b in zip(bits, c)) <= 1
        words.add(tuple(c))
    assert len(words) == 16


# ---- CL-5 structured world ------------------------------------------------------------

def test_cl5_H_eq_L_is_cl1_closed_form():
    for r in RS:
        assert close(cl.ceiling5_rep_closed(L, 64, r), cl.ti1(L, r))


def test_cl5_rep_closed_form_monotone_and_endpoints():
    for H in (16, 32):
        prev = 0.0
        for r in range(0, 65):
            v = cl.ceiling5_rep_closed(L, H, r)
            assert v >= prev - 1e-12
            assert v >= cl.ti1(L, r) - 1e-12
            prev = v
        assert close(cl.ceiling5_rep_closed(L, H, 0), 0.5)
        assert close(cl.ceiling5_rep_closed(L, H, 64), 1.0)


def test_cl5_span_solver_identity_matrix_reduces_to_table():
    G = cl.make_G(L, 64, "rep", 0)
    assert cl.gf2_rank(G) == 64
    ans = cl.span_solve(G, [3, 10, 20], [1, 0, 1])
    assert ans[3] == 1 and ans[10] == 0 and ans[20] == 1
    assert sum(a is not None for a in ans) == 3


def test_cl5_random_G_is_full_rank_and_square_case_independent():
    G = cl.make_G(L, 64, "rand", 123)
    assert cl.gf2_rank(G) == 64
    ans = cl.span_solve(G, list(range(10)), [0] * 10)
    assert sum(a is not None for a in ans) == 10


# ---- CL-6 verifier channel ------------------------------------------------------------

def test_cl6_m1_k1_is_cl1_and_k_ge_2m_is_one():
    for r in RS:
        assert close(cl.ceiling6(L, r, 1, 1), cl.ti1(L, r))
        assert close(cl.ceiling6(L, r, 1, 2), 1.0)
        assert close(cl.ceiling6(L, r, 4, 16), 1.0)


def test_cl6_hypergeometric_sums_to_one_and_is_monotone_in_k():
    for m in (1, 4, 8):
        for r in (0, 16, 32, 48):
            assert close(sum(cl.p_unrevealed_in_block(L, r, m, u) for u in range(m + 1)), 1.0)
            assert cl.ceiling6(L, r, m, 1) <= cl.ceiling6(L, r, m, 2) <= cl.ceiling6(L, r, m, 4)


# ---- CL-7 external store --------------------------------------------------------------

def test_cl7_is_cl2_with_p_eq_c_rho():
    for r in RS:
        for c in (0.0, 0.25, 0.5, 1.0):
            for rho in (0.0, 0.5, 1.0):
                assert close(cl.ceiling7(L, r, c, rho), cl.ti2(L, r, c * rho))
        assert close(cl.ceiling7(L, r, 0.0, 1.0), cl.ti1(L, r))
        assert close(cl.ceiling7(L, r, 1.0, 0.0), cl.ti1(L, r))
        assert close(cl.ceiling7(L, r, 1.0, 1.0), 1.0)


def test_cl7_precedence_shortfall_vanishes_iff_rho_one():
    for r in (16, 32, 48):
        assert close(cl.store_first_line(L, r, 0.5, 1.0), cl.ceiling7(L, r, 0.5, 1.0))
        assert cl.store_first_line(L, r, 0.5, 0.5) < cl.ceiling7(L, r, 0.5, 0.5)
        assert close(cl.store_first_line(L, r, 1.0, 0.0), 0.5)
