"""The two runtime defects surfaced by the ORION-V2 one-day theorem batch (T1 / MEG-04, T2 / MEG-06),
now fixed: internal composition never reaches commit authority; a budgeted FOUND is sound."""
from __future__ import annotations

from fractions import Fraction as F

from ocm.kso import abstraction as AB
from ocm.kso import admission as AD
from ocm.kso import navigation as N
from ocm.kso import space as S
from ocm.kso.types import Authority, internal_authority
from ocm.kso.warrant import WarrantProfile as WP
from ocm.operators import registry as R


def test_two_committed_tails_compose_to_zero_commit_everywhere():
    ks = S.KnowledgeSpace((S.Atom("r1", "claim", WP.of({1}), Authority.of(commit=1, src=2)), S.Atom("r2", "claim", WP.of({2}), Authority.of(commit=1, src=3))), ())
    _, rc = AD.compose(ks, ["r1", "r2"], "c")
    assert rc.authority.rank("commit") == 0 and rc.authority.rank("src") == 2
    _, sr = AB.summarize(ks, ["r1", "r2"], "S")
    assert sr.authority.rank("commit") == 0
    op = R.OperatorSpec("o", "1", R.BackendKind.PROGRAMMATIC, lambda ks, a: {}, ("r1", "r2"), authority=Authority.of(commit=1, src=9))
    assert R.compose_candidate(ks, op, {}).authority.rank("commit") == 0
    assert internal_authority([Authority.of(commit=1)]).rank("commit") == 0


def test_found_at_budget_is_sound_for_the_fixed_point_on_the_chain_witness():
    """Chain s→v1→…→v17: iterating from s (the frozen reference) reports FOUND at θ=1e-3 although
    a*(v17) < θ; iterating from α·s (canonical) does not."""
    chain = ("s",) + tuple(f"v{i}" for i in range(1, 18))
    atoms = tuple(S.Atom(x, "claim") for x in chain)
    edges = tuple(S.Hyperedge(f"e{i}", (chain[i],), (chain[i + 1],), "DEPENDENCE") for i in range(len(chain) - 1))
    ks = S.KnowledgeSpace(atoms, edges)
    seed = N.seed_vector(ks, {"s": F(1)})
    alpha, theta = F(1, 3), F(1, 1000)
    exact = N.fixed_point(ks, seed, alpha)
    assert exact["v17"] < theta
    r = N.navigate(ks, seed, "v17", N.NavigationBudget(steps=40, restarts=1, depth=40), alpha=alpha, threshold=theta)
    assert r.outcome is N.NavigationOutcome.GAP_NOT_FOUND and r.reason == "BUDGET_BRACKET_EXCLUDES_THRESHOLD"
    # the frozen reference's start vector overshoots and would report FOUND (the T2 mutant)
    p = N.navigation_matrix(ks).as_lists()
    a = list(seed)
    found_from_s = False
    for _ in range(40):
        a = N.restart_step(p, seed, a, alpha)
        if a[ks.ids.index("v17")] >= theta:
            found_from_s = True
            break
    assert found_from_s
    # and every FOUND the canonical walker reports is below-or-equal the exact value
    r2 = N.navigate(ks, seed, "v3", N.NavigationBudget(steps=40, restarts=1, depth=40), alpha=alpha, threshold=theta)
    assert r2.outcome is N.NavigationOutcome.FOUND and r2.activation <= exact["v3"]
