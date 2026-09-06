"""Experiment / analysis selection (M10 §4): information- and decision-aware.

    ExpectedValue(action) = expected downstream knowledge improvement − cost − risk

Knowledge improvement is measured on the *hypothesis set*: the expected number of live hypotheses
eliminated by the experiment's outcome (uniform prior over live hypotheses; predictions come from
each hypothesis's `predict` under the experiment's conditions, discretised by the measurement
model's resolution).  This is the M4 clarification value / M5 active-learning rule applied to
hypotheses (batch-3 C1).  Comparators: random, entropy (elimination only, cost-blind),
greedy confirmation (the experiment the *preferred* hypothesis predicts best — the planted
hostile), OCM full (elimination − cost − risk with a stopping rule).  Stopping: no experiment has
positive value, or one live hypothesis remains, or the task criterion is met.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable, Hashable, Mapping, Sequence

from .evidence import Experiment, Hypothesis


@dataclass(frozen=True)
class Choice:
    experiment: Experiment | None
    value: float
    values: dict[str, float]
    reason: str


def _bucket(v: Any, resolution: float) -> Hashable:
    try:
        return round(float(v) / resolution)
    except (TypeError, ValueError):
        return v


def expected_elimination(hyps: Sequence[Hypothesis], exp: Experiment, resolution: float) -> float:
    live = list(hyps)
    n = len(live)
    if n <= 1:
        return 0.0
    blocks: dict[Hashable, int] = {}
    for h in live:
        b = _bucket(h.predict(exp.intervention), resolution)
        blocks[b] = blocks.get(b, 0) + 1
    return sum((size / n) * (n - size) for size in blocks.values())


def select_ocm(hyps: Sequence[Hypothesis], experiments: Sequence[Experiment], *, resolution: float = 0.5, lam_cost: float = 1.0, lam_risk: float = 1.0, budget: float = float("inf")) -> Choice:
    if len(hyps) <= 1:
        return Choice(None, 0.0, {}, "one live hypothesis: stop")
    values = {}
    for e in experiments:
        if e.cost > budget:
            values[e.experiment_id] = float("-inf")
            continue
        values[e.experiment_id] = expected_elimination(hyps, e, resolution) - lam_cost * e.cost - lam_risk * e.risk
    best = max(values, key=lambda k: values[k])
    if values[best] <= 0:
        return Choice(None, values[best], values, "no experiment worth its cost and risk: stop")
    return Choice(next(e for e in experiments if e.experiment_id == best), values[best], values, "discriminates competing hypotheses")


def select_entropy(hyps: Sequence[Hypothesis], experiments: Sequence[Experiment], *, resolution: float = 0.5, **_) -> Choice:
    if len(hyps) <= 1:
        return Choice(None, 0.0, {}, "stop")
    values = {e.experiment_id: expected_elimination(hyps, e, resolution) for e in experiments}
    best = max(values, key=lambda k: values[k])
    return Choice(next(e for e in experiments if e.experiment_id == best), values[best], values, "max elimination, cost-blind")


def select_random(hyps: Sequence[Hypothesis], experiments: Sequence[Experiment], *, seed: str = "r", **_) -> Choice:
    if len(hyps) <= 1:
        return Choice(None, 0.0, {}, "stop")
    e = random.Random(seed).choice(list(experiments))
    return Choice(e, 0.0, {}, "random")


def select_greedy_confirmation(hyps: Sequence[Hypothesis], experiments: Sequence[Experiment], *, preferred: str, resolution: float = 0.5, **_) -> Choice:
    """Planted (M10 §17 'confirmation bias experiment chooser'): pick the experiment where the
    preferred hypothesis is *least* distinguishable from the others (it will look confirmed)."""
    if len(hyps) <= 1:
        return Choice(None, 0.0, {}, "stop")
    pref = next(h for h in hyps if h.hyp_id == preferred)
    values = {}
    for e in experiments:
        pb = _bucket(pref.predict(e.intervention), resolution)
        agree = sum(1 for h in hyps if _bucket(h.predict(e.intervention), resolution) == pb)
        values[e.experiment_id] = agree
    best = max(values, key=lambda k: values[k])
    return Choice(next(e for e in experiments if e.experiment_id == best), float(values[best]), values, "mutant: confirms the preferred hypothesis")


@dataclass
class Campaign:
    """Run a policy until it stops; outcomes come from the oracle; hypotheses are eliminated when
    their prediction disagrees with the observed bucket."""
    hyps: list[Hypothesis]
    experiments: list[Experiment]
    oracle: Callable[[Experiment], float]
    resolution: float = 0.5
    log: list[dict[str, Any]] = None

    def run(self, policy, *, max_steps: int = 10, **kw) -> dict[str, Any]:
        self.log = []
        live = list(self.hyps)
        spent = risk = 0.0
        for step in range(max_steps):
            ch = policy(live, self.experiments, **kw)
            if ch.experiment is None:
                self.log.append({"step": step, "stop": ch.reason})
                break
            e = ch.experiment
            y = self.oracle(e)
            yb = _bucket(y, self.resolution)
            survivors = [h for h in live if _bucket(h.predict(e.intervention), self.resolution) == yb]
            self.log.append({"step": step, "experiment": e.experiment_id, "eliminated": len(live) - len(survivors), "cost": e.cost, "risk": e.risk})
            spent += e.cost
            risk += e.risk
            live = survivors or live                     # an outcome no hypothesis predicted keeps the set (gap), never empties it
        return {"live": [h.hyp_id for h in live], "experiments": sum(1 for l in self.log if "experiment" in l), "cost": spent, "risk": risk}
