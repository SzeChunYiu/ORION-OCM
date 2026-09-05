"""MEG-32 adopted statistics: exact values, TOST verdicts, the 'p > α ⇒ equivalent' hostile."""
from __future__ import annotations

from fractions import Fraction

from ocm.evaluation import stats as ST


def test_exact_binomial_and_mcnemar_values():
    # 8 vs 2 discordant: two-sided exact p = 2 * P(X <= 2 | n=10, 1/2) = 2 * 56/1024
    m = ST.mcnemar_exact(8, 2)
    assert m["discordant"] == 10 and abs(m["p_two_sided"] - 2 * 56 / 1024) < 1e-12 and m["direction"] == "A"
    assert ST.exact_binomial_two_sided(0, 0) == 1
    lo, hi = ST.clopper_pearson(0, 20)
    assert lo == 0.0 and 0.16 < hi < 0.17            # 1 - 0.025^(1/20) ≈ 0.168


def test_tost_verdicts_and_the_hostile():
    equiv = ST.tost_equivalence(ST.PairedComparison(80, 70, 70, 0, 0))
    assert equiv["verdict"] == "EQUIVALENT"
    res = ST.tost_equivalence(ST.PairedComparison(80, 78, 40, 38, 0))
    assert res["verdict"] == "RESIDUAL_A" and res["difference"] > 0.4
    inc = ST.tost_equivalence(ST.PairedComparison(20, 12, 10, 4, 2))
    assert inc["verdict"] == "INCONCLUSIVE"
    # the hostile: a non-significant McNemar read as equivalence
    assert ST.mutant_p_greater_than_alpha_means_equivalent(ST.PairedComparison(20, 12, 10, 4, 2)) == "EQUIVALENT"


def test_power_curve_is_monotone_in_n():
    p40, p80 = ST.power_exact(40, 0.15), ST.power_exact(80, 0.15)
    assert 0.0 <= p40 <= p80 <= 1.0
