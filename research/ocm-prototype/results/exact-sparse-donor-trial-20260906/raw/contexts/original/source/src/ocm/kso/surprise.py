"""Registered reaction-surprise models (M2.1 revival of the underperforming extraction stage).

The frozen model (``UNIFORM``, contract §6): ρ_Q(v) = a_Q(v)·[log(a_Q(v)/π(v))]₊ with π the fixed
point of the uniform seed.  The M2 receipt (`results/KSO_M2_SOLVE_OUTCOME_V1.md`) found it
structurally weak under fan-out: a decisive live atom one or two hops from the seed scores 0
because π(v) contains the direct restart mass α/n at v while a_Q(v) contains none.

Two facts settle the lever:

* **Lemma (seed-count background is a no-op).**  a* is linear in the seed s (KS-T05: a* =
  α(I−(1−α)Pᵀ)⁻¹ s).  The expected fixed point over uniformly random seed supports of any fixed
  size k equals the fixed point of the uniform seed.  So "seed-count-conditioned background" — the
  lever the receipt named — changes nothing.  (Checked exhaustively in ``check_seed_count_lemma``.)
* **PROPAGATED model.**  Restart mass is the query's prior, not a reaction.  Split a = α s + b
  where b = (1−α)Pᵀ a is the mass received *through structure*, and compare propagated mass to
  propagated background: ρ'_Q(v) = b_Q(v)·[log(b_Q(v)/b_π(v))]₊.  A hub still receives most of its
  background through structure (large b_π), so KS-T06/T06b are preserved (checked on the hub
  witness); a deep decisive atom is no longer penalised for the background's self-teleport.

Parents: personalised PageRank contributions excluding the teleport term (Andersen, Chung & Lang
2006 contribution vectors); IDF; Bayesian surprise.  A design choice, registered and compared —
never tuned to an outcome.  The default stays UNIFORM until the M2 dev-split comparison is frozen.
"""
from __future__ import annotations

import math
from enum import Enum
from fractions import Fraction
from itertools import combinations
from typing import Any, Mapping, Sequence

from . import navigation as N
from .space import KnowledgeSpace


class SurpriseModel(str, Enum):
    UNIFORM = "UNIFORM"          # frozen contract §6
    PROPAGATED = "PROPAGATED"    # M2.1 revival candidate


def propagated_mass(ks: KnowledgeSpace, activation: Mapping[str, Fraction], seed: Sequence[Fraction], alpha: Fraction, *, revoked=(), mode: N.NavigationMode = N.NavigationMode.WARRANTED) -> dict[str, Fraction]:
    """b = a − α·s_{Q,R}: the part of the fixed point received through structure."""
    s = N.gated_seed(ks, seed, revoked, mode)
    return {x: activation[x] - alpha * sv for x, sv in zip(ks.ids, s, strict=True)}


def surprise(
    ks: KnowledgeSpace,
    activation: Mapping[str, Fraction],
    background: Mapping[str, Fraction],
    seed: Sequence[Fraction],
    alpha: Fraction,
    model: SurpriseModel = SurpriseModel.UNIFORM,
    *,
    revoked=(),
    mode: N.NavigationMode = N.NavigationMode.WARRANTED,
) -> dict[str, float]:
    if model is SurpriseModel.UNIFORM:
        return N.surprise_vector(activation, background)
    b_q = propagated_mass(ks, activation, seed, alpha, revoked=revoked, mode=mode)
    b_pi = propagated_mass(ks, background, N.uniform_seed(ks), alpha, revoked=revoked, mode=mode)
    return {x: N.reaction_surprise(b_q[x], b_pi[x]) for x in ks.ids}


def check_seed_count_lemma(ks: KnowledgeSpace, alpha: Fraction, *, revoked=()) -> dict[str, Any]:
    """Expected fixed point over all seed supports of size k equals the uniform-seed fixed point,
    for every k — exact over ℚ (linearity of a* in s)."""
    ids = ks.ids
    n = len(ids)
    pi = N.fixed_point(ks, N.uniform_seed(ks), alpha, revoked=revoked)
    checks = 0
    for k in range(1, n + 1):
        total = {x: Fraction(0, 1) for x in ids}
        count = 0
        for support in combinations(ids, k):
            seed = N.seed_vector(ks, {x: Fraction(1, 1) for x in support})
            a = N.fixed_point(ks, seed, alpha, revoked=revoked)
            for x in ids:
                total[x] += a[x]
            count += 1
        mean = {x: total[x] / count for x in ids}
        assert mean == pi, (k, mean, pi)
        checks += 1
    return {"seed_sizes_checked": checks, "mean_equals_uniform_background": 1}


def check_hub_theorem_under_model(model: SurpriseModel) -> dict[str, Any]:
    """KS-T06b must survive any registered surprise model (no-regression gate)."""
    from ocm.historical import load_reference
    from . import space as S

    frz = load_reference("kso_m0_freeze_checks_v1")
    ks = S.from_reference(frz.hub_witness_space())
    alpha = Fraction(1, 2)
    background = N.fixed_point(ks, N.uniform_seed(ks), alpha)
    seed_both = N.seed_vector(ks, {"x1": Fraction(1)})
    both = N.fixed_point(ks, seed_both, alpha)
    sur_both = surprise(ks, both, background, seed_both, alpha, model)
    rank_sur = N.rank_by(sur_both, exclude=("x1",))
    pop = N.mutant_popularity_rank(both, exclude=("x1",))
    assert pop[0] == "H" and rank_sur[0] == "sp", (model, pop, rank_sur)
    seed_hub = N.seed_vector(ks, {"x2": Fraction(1)})
    only_hub = N.fixed_point(ks, seed_hub, alpha)
    sur_hub = surprise(ks, only_hub, background, seed_hub, alpha, model)
    assert N.rank_by(sur_hub, exclude=("x2",))[0] == "H", (model, sur_hub)
    zero = surprise(ks, background, background, N.uniform_seed(ks), alpha, model)
    assert all(v == 0.0 for v in zero.values())
    return {"model": model.value, "direction_i": 1, "direction_ii": 1, "background_zero": len(zero)}


def compare_models_on_target(ks: KnowledgeSpace, seed: Sequence[Fraction], alpha: Fraction, target: str, *, revoked=()) -> dict[str, float]:
    """Diagnostic: the surprise each model assigns to one atom (used by the revival study)."""
    a = N.fixed_point(ks, seed, alpha, revoked=revoked)
    pi = N.fixed_point(ks, N.uniform_seed(ks), alpha, revoked=revoked)
    return {m.value: surprise(ks, a, pi, seed, alpha, m, revoked=revoked)[target] for m in SurpriseModel}
