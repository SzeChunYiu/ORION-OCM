from __future__ import annotations
import math, random
from typing import Sequence
from factor_core_v1 import *
class FactorLocal:
    name = "factor_local"
    def __init__(self):
        self.models: list[Model] = [tuple() for _ in range(ACTIONS)]
        self.relevance: set[int] = set()
        self.cost = Cost()

    def update(self, rows: Sequence[Episode], generation: int) -> None:
        touched = []
        for a in range(ACTIONS):
            if generation == 1 or any(predict_model(self.models[a], e.x) != e.correct_actions[a] for e in rows):
                touched.append(a)
        for a in touched:
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)
        old = self.relevance.copy()
        self.relevance = {i for m in self.models for c in m for i in c}
        # explicit relevance maintenance is charged; this is not free metadata.
        self.cost.maintenance_ops += len(old ^ self.relevance) + len(touched)


class SymbolicIncremental(FactorLocal):
    name = "symbolic_incremental_parent"
    def __init__(self):
        super().__init__()
        self.relevance = set()  # no separate cached relevance state

    def update(self, rows: Sequence[Episode], generation: int) -> None:
        touched = []
        for a in range(ACTIONS):
            if generation == 1 or any(predict_model(self.models[a], e.x) != e.correct_actions[a] for e in rows):
                touched.append(a)
        for a in touched:
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)
        # Parent derives variable use from clauses when needed; no duplicate relevance cache maintenance.


class ResetFactor(FactorLocal):
    name = "reset_factor_ablation"
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.models = [tuple() for _ in range(ACTIONS)]
        self.relevance = set()
        for a in range(ACTIONS):
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)
        self.relevance = {i for m in self.models for c in m for i in c}
        self.cost.maintenance_ops += len(self.relevance) + ACTIONS


class GlobalRefit(SymbolicIncremental):
    name = "global_refit_parent"
    def __init__(self):
        super().__init__()
        self.history: list[Episode] = []
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.history.extend(rows)
        for a in range(ACTIONS):
            m, c = learn_minimal_dnf(self.history, a)
            self.models[a] = m
            self.cost.add(c)


class LazySymbolic(SymbolicIncremental):
    name = "symbolic_lazy_parent"
    def __init__(self):
        super().__init__()
        self.current: list[Episode] = []
        self.models = [tuple() for _ in range(ACTIONS)]
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.current = list(rows)
        self.models = [tuple() for _ in range(ACTIONS)]
        # no induction/maintenance now
    def materialize(self) -> None:
        for a in range(ACTIONS):
            m, c = learn_minimal_dnf(self.current, a)
            self.models[a] = m
            self.cost.add(c)


class SurrogateParent:
    name = "surrogate_parent"
    def __init__(self):
        self.models: list[dict[tuple[int, ...], tuple[int, int]]] = [dict() for _ in range(ACTIONS)]
        self.cost = Cost()
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.models = [dict() for _ in range(ACTIONS)]
        for a in range(ACTIONS):
            self.cost.update_components_touched += 1
            for e in rows:
                feats = [i for i, b in enumerate(e.x) if b]
                keys = [(i,) for i in feats] + list(itertools.combinations(feats, 2))
                for k in keys:
                    pos, total = self.models[a].get(k, (0, 0))
                    self.models[a][k] = (pos + e.correct_actions[a], total + 1)
                    self.cost.maintenance_ops += 1
    def predict(self, x: tuple[int, ...], a: int) -> int:
        feats = [i for i, b in enumerate(x) if b]
        keys = [(i,) for i in feats] + list(itertools.combinations(feats, 2))
        best = 0.0
        for k in keys:
            self.cost.prediction_literal_evals += len(k)
            pos, total = self.models[a].get(k, (0, 0))
            if total >= 2:
                best = max(best, pos / total)
        return int(best >= 0.9)
    def accuracy(self, rows: Sequence[Episode]) -> float:
        good = 0
        total = 0
        for e in rows:
            for a in range(ACTIONS):
                good += int(self.predict(e.x, a) == e.correct_actions[a])
                total += 1
        return good / total
    def size(self) -> int:
        enc = [{"-".join(map(str, k)): v for k, v in m.items()} for m in self.models]
        return len(json.dumps(enc, sort_keys=True, separators=(",", ":")).encode())


def loo_relevance(rows: Sequence[Episode]) -> set[int]:
    # Known-incomplete proxy: single-feature conditional lift only; misses pure higher-order/XOR-like relations.
    rel = set()
    for i in range(D):
        for a in range(ACTIONS):
            on = [e.correct_actions[a] for e in rows if e.x[i]]
            off = [e.correct_actions[a] for e in rows if not e.x[i]]
            if on and off and abs(sum(on)/len(on) - sum(off)/len(off)) >= 0.20:
                rel.add(i)
                break
    return rel


# Small population search secondary parent. It is included for breadth, never treated as stronger
# than the exact symbolic parent unless its observed vector actually dominates.
def evolutionary_fit(rows: Sequence[Episode], action: int, rng: random.Random, budget: int) -> tuple[Model, Cost]:
    cost = Cost(update_components_touched=1, rediscovery_ops=1)
    population: list[Model] = []
    for _ in range(24):
        population.append(tuple(tuple(sorted(rng.sample(range(D), rng.randint(1, MAX_WIDTH)))) for _ in range(2)))
    best: Model = tuple()
    best_acc = -1.0
    while cost.primitive_literal_evals < max(1, budget):
        scored = []
        for model in population:
            if cost.primitive_literal_evals >= budget:
                break
            good = 0
            seen = 0
            for e in rows:
                if cost.primitive_literal_evals >= budget:
                    break
                p = predict_model(model, e.x, cost)
                good += int(p == e.correct_actions[action])
                seen += 1
                cost.validation_examples += 1
            acc = good / max(1, seen)
            scored.append((acc, model))
            cost.induction_candidates += 1
            if acc > best_acc:
                best_acc, best = acc, model
        scored.sort(reverse=True, key=lambda z: z[0])
        elites = [m for _, m in scored[:6]] or [best]
        population = elites.copy()
        while len(population) < 24:
            parent = list(rng.choice(elites))
            slot = rng.randrange(len(parent))
            clause = list(parent[slot])
            if rng.random() < 0.5 and len(clause) < MAX_WIDTH:
                avail = [i for i in range(D) if i not in clause]
                if avail:
                    clause.append(rng.choice(avail))
            elif len(clause) > 1:
                clause.pop(rng.randrange(len(clause)))
            else:
                clause[0] = rng.randrange(D)
            parent[slot] = tuple(sorted(set(clause)))
            population.append(tuple(parent))
    return best, cost
