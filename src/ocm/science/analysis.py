"""Statistical / data-analysis lifecycle (M10 §6) on synthetic datasets with exact oracle effects,
and the multiple-testing hostile.

Lifecycle operators (registered roles, so M9 skills transfer partially): inspect → clarify estimand
→ quality check → select test → check assumptions → sensitivity → run → diagnostics → revise →
report (effect + uncertainty + limitations).  The analysis is *pre-registered per task*: the
estimand and the test are fixed before the outcome is computed; a run that searched analyses
until significance is the planted hostile (`mutant_p_hack`), and the receipt reports the number
of analyses tried.  Exact permutation test for a two-group mean difference (stdlib), exact
binomial for proportions; no p-value is reported without its pre-registered test id.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from itertools import combinations
from math import comb
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class Dataset:
    dataset_id: str
    groups: Mapping[str, tuple[float, ...]]
    oracle_effect: float                       # hidden true mean difference (treatment − control)
    schema: Mapping[str, str]
    missing: int = 0


def make_dataset(i: int, *, effect: float, n: int = 8, seed: str = "OCM-M10-DATA", noise: float = 1.0, missing: int = 0) -> Dataset:
    rng = random.Random(f"{seed}|{i}|{effect}|{n}")
    control = tuple(round(rng.gauss(10.0, noise), 3) for _ in range(n))
    treat = tuple(round(rng.gauss(10.0 + effect, noise), 3) for _ in range(n))
    return Dataset(f"ds{i}", {"control": control, "treatment": treat}, effect, {"control": "float", "treatment": "float"}, missing)


def permutation_p(a: Sequence[float], b: Sequence[float], *, max_exact: int = 24) -> tuple[float, float]:
    """Exact two-sided permutation p-value for the mean difference when n_a + n_b ≤ max_exact,
    else a seeded Monte-Carlo approximation (reported as such by the caller)."""
    obs = sum(a) / len(a) - sum(b) / len(b)
    pool = list(a) + list(b)
    na = len(a)
    if len(pool) <= max_exact:
        total = comb(len(pool), na)
        extreme = 0
        for idx in combinations(range(len(pool)), na):
            s = set(idx)
            ma = sum(pool[i] for i in idx) / na
            mb = sum(pool[i] for i in range(len(pool)) if i not in s) / (len(pool) - na)
            if abs(ma - mb) >= abs(obs) - 1e-12:
                extreme += 1
        return obs, extreme / total
    rng = random.Random("perm")
    extreme = 0
    R = 4000
    for _ in range(R):
        rng.shuffle(pool)
        ma = sum(pool[:na]) / na
        mb = sum(pool[na:]) / (len(pool) - na)
        if abs(ma - mb) >= abs(obs) - 1e-12:
            extreme += 1
    return obs, extreme / R


@dataclass
class AnalysisPlan:
    estimand: str
    test_id: str
    alpha: float
    preregistered: bool = True
    analyses_tried: int = 0


@dataclass(frozen=True)
class AnalysisReport:
    estimand: str
    effect: float
    p_value: float
    test_id: str
    significant: bool
    ci_note: str
    limitations: tuple[str, ...]
    analyses_tried: int
    provenance: tuple[str, ...]


def run_lifecycle(ds: Dataset, plan: AnalysisPlan) -> AnalysisReport:
    a, b = ds.groups["treatment"], ds.groups["control"]
    lim = []
    if len(a) + len(b) <= 24:
        method = "exact permutation"
    else:
        method = "monte-carlo permutation (4000)"
        lim.append("p-value is a Monte-Carlo approximation")
    if ds.missing:
        lim.append(f"{ds.missing} missing values excluded")
    eff, p = permutation_p(a, b)
    plan.analyses_tried += 1
    if len(a) < 10:
        lim.append("small sample: low power")
    return AnalysisReport(plan.estimand, round(eff, 4), round(p, 4), plan.test_id, p < plan.alpha, method, tuple(lim), plan.analyses_tried, (ds.dataset_id, plan.test_id))


def mutant_p_hack(ds: Dataset, alpha: float = 0.05, max_tries: int = 12) -> AnalysisReport:
    """Planted (M10 §17): search subsets/transforms until one analysis is significant."""
    a, b = list(ds.groups["treatment"]), list(ds.groups["control"])
    tries = 0
    rng = random.Random("hack")
    best = None
    while tries < max_tries:
        tries += 1
        aa = a[:] if tries == 1 else [x for x in a if rng.random() < 0.8]
        bb = b[:] if tries == 1 else [x for x in b if rng.random() < 0.8]
        if len(aa) < 3 or len(bb) < 3:
            continue
        eff, p = permutation_p(aa, bb)
        best = AnalysisReport("mean difference (searched)", round(eff, 4), round(p, 4), f"search#{tries}", p < alpha, "post-hoc subset", ("analysis selected after inspection",), tries, (ds.dataset_id,))
        if p < alpha:
            return best
    return best


def false_confidence_rate(reports: Sequence[AnalysisReport], oracle_effects: Sequence[float]) -> dict[str, Any]:
    """Significant claims on datasets whose oracle effect is zero, over the null datasets."""
    nulls = [(r, e) for r, e in zip(reports, oracle_effects) if e == 0.0]
    fp = sum(1 for r, _ in nulls if r.significant)
    return {"null_datasets": len(nulls), "false_positives": fp, "rate": (fp / len(nulls)) if nulls else None}
