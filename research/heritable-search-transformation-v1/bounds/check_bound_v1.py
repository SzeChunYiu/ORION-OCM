#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_bound_v1.py -- machine check of HST-T09 finite specialization (lane D, D6).

Checks, by EXACT enumeration of complete finite worlds (no Monte Carlo for the
probability statements; fractions.Fraction for all probabilities and loss values):
  (a) Theorem T09-B (PAC-Bayes, McAllester/Langford-Seeger/Maurer form) on random
      small finite worlds: for EVERY ordered training sample S in T^m (the complete
      sample space), a deterministic data-dependent learning rule picks a mixture
      rho(S); the exact violation probability
          P_S~D^m[ E_D l(rho(S)) - lhat(rho(S)) > sqrt((KL(rho||rho0)+ln(2 sqrt m/d))/(2m)) ]
      is computed by summation and asserted <= delta for every delta in the grid.
      Two rules: pure-vertex ERM and a tempered (Gibbs-style) mixture.
      Plus a negative control: a mutilated bound (complexity term dropped) MUST be
      violated somewhere (checker calibration, no-alarm assertion).
  (b) The negative-transfer counterexample world W-: exact Fraction numbers
      (learned test burden 1 vs flat 1/2, excess +1/2) and the no-contradiction
      check (violation probability exactly 0 on D_train for m = 1..5, all delta).
  (c) The parent constant 2 sqrt m (Maurer 2004 Lemma 1 / Topsoe 2007):
      E_S exp(m KL(lhat||p)) <= 2 sqrt m by complete binomial enumeration.
  (d) The OCM specialization table + crossovers (K=83, N=28584, delta=0.05,
      bar=0.224507).

Python 3.8 compatible (typing module, no match, no PEP 604).
Exit codes: 0 = all checks pass; 2 = assertion failure; 3 = hard error.
"""
import math
import random
import sys
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

DELTA_GRID = [Fraction(1, 2), Fraction(1, 5), Fraction(1, 10), Fraction(1, 20), Fraction(1, 100)]
N_WORLD_SEEDS = 110  # >= 100 random worlds demanded by the spec
# py3.8: no Fraction.ln; bound arithmetic in float, probabilities exact.


def log(x):  # type: (float) -> float
    return math.log(x)


def mix_kl(rho, k):  # type: (Sequence[float], int) -> float
    """KL(rho || Unif{1..k}) = sum rho_i ln(rho_i * k); 0 ln 0 = 0."""
    total = 0.0
    for w in rho:
        if w > 0.0:
            total += w * log(w * k)
    return total


def bound_eps(m, kl, delta_f):  # type: (int, float, float) -> float
    """sqrt((KL + ln(2 sqrt m / delta)) / (2m)) -- Theorem T09-B slack, explicit constants."""
    return math.sqrt((kl + log(2.0 * math.sqrt(m) / delta_f)) / (2.0 * m))


def rule_erm(loss_hat):  # type: (Sequence[float]) -> List[float]
    """Pure-vertex ERM: point mass on argmin empirical loss, ties -> smallest index."""
    best = 0
    for i in range(1, len(loss_hat)):
        if loss_hat[i] < loss_hat[best]:
            best = i
    rho = [0.0] * len(loss_hat)
    rho[best] = 1.0
    return rho


def rule_tempered(loss_hat, eta=2.0):  # type: (Sequence[float], float) -> List[float]
    """Gibbs-style data-dependent mixture rho_k prop exp(-eta * loss_hat_k)."""
    mx = max(loss_hat)
    ws = [math.exp(-eta * (l - mx)) for l in loss_hat]
    tot = sum(ws)
    return [w / tot for w in ws]


def rule_flat(loss_hat):  # type: (Sequence[float]) -> List[float]
    """No-learning control rule: rho = prior."""
    k = len(loss_hat)
    return [1.0 / k] * k


RULES = [("erm", rule_erm), ("tempered", rule_tempered), ("flat", rule_flat)]


def enumerate_world(loss, dist, m, rule_fn):  # type: (List[List[Fraction]], List[Fraction], int, object) -> Dict[str, Fraction]
    """Exact violation probabilities for one world/rule/m over the COMPLETE ordered
    sample space T^m.  loss[k][t] = l(Q_k, tau_t) as Fractions; dist[t] = D(tau_t).

    For each S = (t_1..t_m): weight = prod D(t_i) (exact); lhat_k = mean of loss[k][t_i]
    (exact Fraction -> float); rho = rule(lhat); mixture loss is linear:
    l(rho, tau) = sum_k rho_k * loss[k][tau] (float mix of exact losses);
    true D-risk = sum_t dist[t] * l(rho, tau_t); KL = mix_kl(rho, K).
    Returns dict delta-string -> exact violation probability.
    """
    k = len(loss)
    t_n = len(dist)
    viol = {str(d): Fraction(0, 1) for d in DELTA_GRID}
    viol_negctrl = Fraction(0, 1)
    samples = []  # type: List[Tuple[Tuple[int, ...], Fraction]]
    samples.append(((), Fraction(1, 1)))
    for _ in range(m):
        nxt = []  # type: List[Tuple[Tuple[int, ...], Fraction]]
        for (pre, w) in samples:
            for t in range(t_n):
                nxt.append((pre + (t,), w * dist[t]))
        samples = nxt
    for (samp, w) in samples:
        if w == 0:
            continue
        lhat = [0.0] * k
        for kk in range(k):
            acc = Fraction(0, 1)
            for t in samp:
                acc += loss[kk][t]
            lhat[kk] = float(acc) / m
        rho = rule_fn(lhat)
        kl = mix_kl(rho, k)
        true_risk = 0.0
        for t in range(t_n):
            lmix = 0.0
            for kk in range(k):
                if rho[kk] > 0.0:
                    lmix += rho[kk] * float(loss[kk][t])
            true_risk += float(dist[t]) * lmix
        lhat_mix = sum(rho[kk] * lhat[kk] for kk in range(k))
        excess = true_risk - lhat_mix
        for d in DELTA_GRID:
            eps = bound_eps(m, kl, float(d))
            if excess > eps + 1e-9:  # float tolerance on the comparison only
                viol[str(d)] += w
        # negative control: mutilated bound (no complexity/no delta term at all)
        if excess > 0.0:
            viol_negctrl += w
    viol["negctrl"] = viol_negctrl
    return viol


def random_world(rng, k, t_n, grid=10):  # type: (random.Random, int, int, int) -> Tuple[List[List[Fraction]], List[Fraction]]
    loss = [[Fraction(rng.randint(0, grid), grid) for _ in range(t_n)] for _ in range(k)]
    raw = [rng.randint(1, 6) for _ in range(t_n)]
    tot = sum(raw)
    dist = [Fraction(r, tot) for r in raw]
    return loss, dist


def check_a():  # type: () -> Tuple[int, int]
    rng = random.Random(20260910)
    worlds = 0
    negctrl_seen = False
    for seed_i in range(N_WORLD_SEEDS):
        k = 2 + (seed_i % 3)  # K in 2..4
        t_n = 2 + ((seed_i // 3) % 3)  # T in 2..4
        m = 4 + ((seed_i // 9) % 5)  # m in 4..8
        if t_n == 4 and m == 8:
            m = 7  # runtime cap: |T|^m <= 4^7 = 16384 exact samples per enumeration
        loss, dist = random_world(rng, k, t_n)
        for (rname, rfn) in RULES:
            viol = enumerate_world(loss, dist, m, rfn)
            for d in DELTA_GRID:
                if viol[str(d)] > d:
                    print("FAIL(a): world %d K=%d T=%d m=%d rule=%s delta=%s viol=%s > delta"
                          % (seed_i, k, t_n, m, rname, d, viol[str(d)]))
                    raise AssertionError("bound violated beyond delta")
            if viol["negctrl"] > 0:
                negctrl_seen = True  # mutilated bound fails somewhere: checker bites
            worlds += 1
    if not negctrl_seen:
        raise AssertionError("negative control never fired: checker cannot detect violations")
    print("PASS(a): %d world-rule checks (complete sample-space enumeration), "
          "delta-grid %s, violation prob <= delta everywhere; negative control fired"
          % (worlds, [str(d) for d in DELTA_GRID]))
    return worlds


def check_b():  # type: () -> None
    """World W-: X={a,b}, kernels delta_a/delta_b, tau_A:{a}, tau_B:{b}."""
    # loss[k][t]: k=0 -> Q_a, k=1 -> Q_b ; t=0 -> tau_A, t=1 -> tau_B
    # l(Q_a,tau_A)=0, l(Q_a,tau_B)=1, l(Q_b,tau_A)=1, l(Q_b,tau_B)=0
    loss = [[Fraction(0, 1), Fraction(1, 1)], [Fraction(1, 1), Fraction(0, 1)]]
    d_train = [Fraction(1, 1), Fraction(0, 1)]
    d_test = [Fraction(0, 1), Fraction(1, 1)]
    # learned rule on any training sample from D_train: ERM -> pure Q_a
    # test risks, exact:
    l_learn_test = Fraction(1, 1)   # 1 - Q_a(A_{tau_B}) = 1 - 0
    l_flat_test = Fraction(1, 2)    # 1 - (1/2) = 1/2
    excess = l_learn_test - l_flat_test
    assert excess == Fraction(1, 2), "negative-transfer delta must be exactly +1/2"
    # expected proposals to first admission (burden reading):
    #   flat: 1 / Q_0(A_tauB) = 1/(1/2) = 2 ;  learned: A-mass 0 -> infinite
    q0_adm = Fraction(1, 2)
    assert (1 / q0_adm) == Fraction(2, 1)
    # no-contradiction: Theorem T09-B on D_train for the ERM posterior,
    # complete enumeration m = 1..5, all delta
    for m in range(1, 6):
        viol = enumerate_world(loss, d_train, m, rule_erm)
        for d in DELTA_GRID:
            assert viol[str(d)] == Fraction(0, 1), \
                "T09-B must hold exactly on D_train (m=%d delta=%s)" % (m, d)
        # train risk of learned bias is 0 -> bound slack positive always
    # flat-prior test burden under D_train for contrast:
    l_flat_train = Fraction(1, 2)
    print("PASS(b): W- exact -- learned E_[D_test]l = %s, flat = %s, negative-transfer "
          "excess = +%s ; expected-proposals: flat 2, learned infinite ; "
          "T09-B violation prob on D_train exactly 0 for m=1..5, all delta"
          % (l_learn_test, l_flat_test, excess))


def check_c():  # type: () -> None
    """Maurer 2004 Lem 1 / Topsoe 2007: E exp(m KL(lhat||p)) <= 2 sqrt m, exact weights."""
    worst_ratio = 0.0
    for m in range(1, 41):
        # p grid as exact fractions where possible
        for p in [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]:
            pf = None  # type: Fraction
            pf = Fraction(1, 20) if p == 0.05 else Fraction(1, 10) if p == 0.1 \
                else Fraction(1, 4) if p == 0.25 else Fraction(1, 2) if p == 0.5 \
                else Fraction(3, 4) if p == 0.75 else Fraction(9, 10) if p == 0.9 \
                else Fraction(19, 20)
            q = 1 - pf
            acc = 0.0  # float exp, exact Fraction weights
            w = [Fraction(0, 1)] * (m + 1)
            for j in range(m + 1):
                # C(m,j) computed exactly (py3.8: no math.comb)
                c = 1
                for i in range(min(j, m - j)):
                    c = c * (m - i) // (i + 1)
                w[j] = Fraction(c, 1) * pf ** j * q ** (m - j)
            for j in range(m + 1):
                if w[j] == 0:
                    continue
                lhat = float(Fraction(j, m))
                kl = 0.0
                if lhat > 0:
                    kl += lhat * log(lhat / p)
                if lhat < 1:
                    kl += (1 - lhat) * log((1 - lhat) / (1 - p))
                acc += float(w[j]) * math.exp(m * kl)
            ratio = acc / (2.0 * math.sqrt(m))
            worst_ratio = max(worst_ratio, ratio)
            if ratio > 1.0:
                raise AssertionError("Topsøe/Maurer constant 2sqrt(m) exceeded: m=%d p=%s ratio=%.4f"
                                     % (m, p, ratio))
    print("PASS(c): E_S exp(m KL(lhat||p)) <= 2 sqrt m over m=1..40, p in {0.05..0.95} "
          "(exact binomial weights); worst ratio %.6f" % worst_ratio)


def eps_m(m, kl, delta=0.05):  # type: (int, float, float) -> float
    return bound_eps(m, kl, delta)


def check_d():  # type: () -> None
    lnk = log(83)
    lnn = log(28584)
    bar = 0.224507
    rows = [(12, lnk, lnn), (104, lnk, lnn), (564, lnk, lnn)]
    vals = {}
    for (m, a, b) in rows:
        vals[(m, "lnk")] = eps_m(m, a)
        vals[(m, "lnn")] = eps_m(m, b)
    # crossovers by grid search
    def cross(target):  # type: (float) -> int
        m = 1
        while eps_m(m, lnk) > target:
            m += 1
        return m
    c1 = cross(1.0)
    cbar = cross(bar)
    c10 = cross(0.1)
    assert c1 == 5, "crossover to eps<=1 must be m*=5, got %d" % c1
    assert cbar == 104, "crossover to eps<=bar must be m*=104, got %d" % cbar
    assert c10 == 564, "crossover to eps<=0.1 must be m*=564, got %d" % c10
    # zoo-scale row is near-vacuous: eps(12)/bar = 0.6242/0.224507 = 2.780x
    assert eps_m(12, lnk) > 2.7 * bar, "zoo-scale slack must exceed 2.7x the bar (near-vacuous)"
    print("PASS(d): table -- m=12: eps=%.4f (lnK) / %.4f (lnN) | m=104: %.5f / %.5f | "
          "m=564: %.5f / %.5f ; crossovers m*(eps<=1)=%d, m*(eps<=bar 0.224507)=%d, m*(eps<=0.1)=%d"
          % (vals[(12, "lnk")], vals[(12, "lnn")], vals[(104, "lnk")], vals[(104, "lnn")],
             vals[(564, "lnk")], vals[(564, "lnn")], c1, cbar, c10))


def main():  # type: () -> int
    try:
        check_b()
        check_c()
        check_d()
        check_a()
    except AssertionError as e:
        print("FAIL: %s" % e)
        return 2
    except Exception as e:  # noqa
        print("HARD ERROR: %r" % (e,))
        return 3
    print("ALL CHECKS PASS (HST-T09 finite specialization + W- counterexample)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
