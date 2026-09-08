#!/usr/bin/env python3
"""Protected-ready PR #150 learned-factorization survival experiment V3.

Self-contained to make the protocol/code audit finite. No protected seed is a default.
Learners see only x and the vector of correct actions; generator metadata is evaluator-only.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import statistics
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

D = 12
ACTIONS = 4
GENERATIONS = 8
TRAIN_N = 96
EVAL_N = 256
MAX_WIDTH = 6
Clause = tuple[int, ...]
Model = tuple[Clause, ...]


def rng_for(seed: int, stream: str) -> random.Random:
    raw = hashlib.sha256(f"E150-V3|{seed}|{stream}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


@dataclass(frozen=True)
class Episode:
    x: tuple[int, ...]
    correct_actions: tuple[int, ...]


@dataclass
class World:
    regime: str
    supports: list[tuple[Clause, ...]]
    drift_rng: random.Random

    @classmethod
    def make(cls, seed: int, regime: str) -> "World":
        rng = rng_for(seed, f"hidden|{regime}")
        width = 2 if regime in {"sparse_stable", "drift"} else 6
        supports: list[tuple[Clause, ...]] = []
        for _ in range(ACTIONS):
            clauses: list[Clause] = []
            while len(clauses) < 2:
                c = tuple(sorted(rng.sample(range(D), width)))
                if c not in clauses:
                    clauses.append(c)
            supports.append(tuple(clauses))
        return cls(regime, supports, rng_for(seed, f"drift|{regime}"))

    def advance(self, generation: int) -> None:
        if self.regime != "drift" or generation not in {3, 5, 7}:
            return
        action = self.drift_rng.randrange(ACTIONS)
        slot = self.drift_rng.randrange(2)
        old = self.supports[action][slot]
        fresh = old
        while fresh == old:
            fresh = tuple(sorted(self.drift_rng.sample(range(D), 2)))
        row = list(self.supports[action])
        row[slot] = fresh
        self.supports[action] = tuple(row)

    def labels(self, x: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(int(any(all(x[i] for i in c) for c in self.supports[a])) for a in range(ACTIONS))


def episodes(world: World, seed: int, regime: str, generation: int, kind: str, n: int) -> list[Episode]:
    rng = rng_for(seed, f"{kind}|{regime}|g{generation}")
    out = []
    for _ in range(n):
        x = tuple(rng.randrange(2) for _ in range(D))
        out.append(Episode(x, world.labels(x)))
    return out


@dataclass
class Cost:
    induction_literal_evals: int = 0
    induction_candidates: int = 0
    induction_selection_ops: int = 0
    invalidation_literal_evals: int = 0
    invalidation_examples: int = 0
    update_components_touched: int = 0
    prediction_literal_evals: int = 0
    validation_examples: int = 0
    maintenance_ops: int = 0
    rediscovery_ops: int = 0

    def add(self, other: "Cost") -> None:
        for k in self.__dataclass_fields__:
            setattr(self, k, getattr(self, k) + getattr(other, k))

    def as_dict(self) -> dict[str, int]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def _holds_induction(c: Clause, x: tuple[int, ...], cost: Cost) -> bool:
    for i in c:
        cost.induction_literal_evals += 1
        if not x[i]:
            return False
    return True


def _predict_invalidation(model: Model, x: tuple[int, ...], cost: Cost) -> int:
    for c in model:
        ok = True
        for i in c:
            cost.invalidation_literal_evals += 1
            if not x[i]:
                ok = False
                break
        if ok:
            return 1
    return 0


def _predict_eval(model: Model, x: tuple[int, ...], cost: Cost) -> int:
    for c in model:
        ok = True
        for i in c:
            cost.prediction_literal_evals += 1
            if not x[i]:
                ok = False
                break
        if ok:
            return 1
    return 0


def contradicted(model: Model, rows: Sequence[Episode], action: int, cost: Cost) -> bool:
    for e in rows:
        cost.invalidation_examples += 1
        if _predict_invalidation(model, e.x, cost) != e.correct_actions[action]:
            return True
    return False


def candidate_clauses(rows: Sequence[Episode], action: int) -> set[Clause]:
    cand: set[Clause] = set()
    for e in rows:
        if not e.correct_actions[action]:
            continue
        active = [i for i, bit in enumerate(e.x) if bit]
        for w in range(1, min(MAX_WIDTH, len(active)) + 1):
            cand.update(itertools.combinations(active, w))
    return cand


def learn_minimal_dnf(rows: Sequence[Episode], action: int) -> tuple[Model, Cost]:
    cost = Cost(update_components_touched=1, rediscovery_ops=1)
    candidates = sorted(candidate_clauses(rows, action), key=lambda c: (len(c), c))
    valid: list[Clause] = []
    for c in candidates:
        cost.induction_candidates += 1
        covered_pos = False
        pure = True
        for e in rows:
            cost.validation_examples += 1
            if _holds_induction(c, e.x, cost):
                if e.correct_actions[action]:
                    covered_pos = True
                else:
                    pure = False
                    break
        if pure and covered_pos:
            valid.append(c)

    antichain: list[Clause] = []
    for c in valid:
        s = set(c)
        cost.induction_selection_ops += len(antichain)
        if not any(set(prev).issubset(s) for prev in antichain):
            antichain.append(c)

    positives = [e for e in rows if e.correct_actions[action]]
    uncovered = set(range(len(positives)))
    chosen: list[Clause] = []
    while uncovered:
        best = None
        best_key = None
        for c in antichain:
            cover = set()
            for j in uncovered:
                ok = True
                for i in c:
                    cost.induction_selection_ops += 1
                    if not positives[j].x[i]:
                        ok = False
                        break
                if ok:
                    cover.add(j)
            if not cover:
                continue
            key = (len(cover) / len(c), len(cover), -len(c), tuple(-i for i in c))
            if best_key is None or key > best_key:
                best_key, best = key, (c, cover)
        if best is None:
            break
        c, cover = best
        chosen.append(c)
        uncovered -= cover
        antichain = [x for x in antichain if x != c]

    pruned = list(chosen)
    changed = True
    while changed:
        changed = False
        for c in list(pruned):
            others = [x for x in pruned if x != c]
            redundant = True
            for e in positives:
                explained = False
                for other in others:
                    ok = True
                    for i in other:
                        cost.induction_selection_ops += 1
                        if not e.x[i]:
                            ok = False
                            break
                    if ok:
                        explained = True
                        break
                if not explained:
                    redundant = False
                    break
            if redundant:
                pruned.remove(c)
                changed = True
                break
    return tuple(sorted(pruned, key=lambda c: (len(c), c))), cost


def identifiable_supports(rows: Sequence[Episode], oracle: Sequence[tuple[Clause, ...]]) -> list[set[Clause]]:
    out: list[set[Clause]] = []
    for a in range(ACTIONS):
        ids: set[Clause] = set()
        for clause in oracle[a]:
            if not any(e.correct_actions[a] and all(e.x[i] for i in clause) for e in rows):
                continue
            good = True
            for drop in clause:
                sub = tuple(i for i in clause if i != drop)
                if not any((not e.correct_actions[a]) and all(e.x[i] for i in sub) for e in rows):
                    good = False
                    break
            if good:
                ids.add(clause)
        out.append(ids)
    return out


def support_metrics(models: Sequence[Model], oracle: Sequence[tuple[Clause, ...]], identifiable: Sequence[set[Clause]]) -> dict:
    oracle_all = {(a, c) for a in range(ACTIONS) for c in oracle[a]}
    target = {(a, c) for a in range(ACTIONS) for c in identifiable[a]}
    nonident = oracle_all - target
    learned = {(a, c) for a in range(ACTIONS) for c in models[a]}
    learned_scored = learned - nonident
    if not target:
        return {"support_precision": None, "support_recall": None, "support_f1": None,
                "identifiable_supports": 0, "nonidentifiable_supports": len(nonident)}
    tp = len(target & learned_scored)
    p = tp / len(learned_scored) if learned_scored else 0.0
    r = tp / len(target)
    f1 = 0.0 if p + r == 0 else 2 * p * r / (p + r)
    return {"support_precision": p, "support_recall": r, "support_f1": f1,
            "identifiable_supports": len(target), "nonidentifiable_supports": len(nonident)}


def relevance_metrics(models: Sequence[Model], oracle: Sequence[tuple[Clause, ...]]) -> tuple[float, float]:
    learned = {i for m in models for c in m for i in c}
    true = {i for supports in oracle for c in supports for i in c}
    tp = len(learned & true)
    return (tp / len(learned) if learned else 0.0, tp / len(true) if true else 1.0)


def evaluate(models: Sequence[Model], rows: Sequence[Episode], cost: Cost) -> tuple[float, float]:
    correct = 0
    total = 0
    ba_terms: list[float] = []
    for a in range(ACTIONS):
        tp = tn = fp = fn = 0
        for e in rows:
            p = _predict_eval(models[a], e.x, cost)
            y = e.correct_actions[a]
            correct += int(p == y)
            total += 1
            if y and p: tp += 1
            elif y and not p: fn += 1
            elif not y and p: fp += 1
            else: tn += 1
        terms = []
        if tp + fn: terms.append(tp / (tp + fn))
        if tn + fp: terms.append(tn / (tn + fp))
        ba_terms.append(sum(terms) / len(terms))
    return correct / total, sum(ba_terms) / len(ba_terms)


def archive_bytes(rows: Sequence[Episode]) -> int:
    return len(json.dumps([{"x": e.x, "y": e.correct_actions} for e in rows], separators=(",", ":")).encode())


def model_bytes(models: Sequence[Model], relevance: Iterable[int] | None = None) -> int:
    obj = {"models": models}
    if relevance is not None:
        obj["relevance"] = sorted(relevance)
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())


class FactorLocal:
    name = "factor_local"
    def __init__(self):
        self.models: list[Model] = [tuple() for _ in range(ACTIONS)]
        self.relevance: set[int] = set()
        self.cost = Cost()
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        touched = []
        for a in range(ACTIONS):
            if generation == 1 or contradicted(self.models[a], rows, a, self.cost):
                touched.append(a)
        for a in touched:
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)
        if touched:
            new_rel: set[int] = set()
            for m in self.models:
                for c in m:
                    for i in c:
                        self.cost.maintenance_ops += 1
                        new_rel.add(i)
            self.cost.maintenance_ops += len(self.relevance ^ new_rel)
            self.relevance = new_rel
    def size(self) -> int:
        return model_bytes(self.models, self.relevance)


class SymbolicCompact(FactorLocal):
    name = "symbolic_compact_parent"
    def __init__(self):
        super().__init__()
        self.relevance = set()
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        touched = []
        for a in range(ACTIONS):
            if generation == 1 or contradicted(self.models[a], rows, a, self.cost):
                touched.append(a)
        for a in touched:
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)
    def size(self) -> int:
        return model_bytes(self.models)


class SymbolicMemory(SymbolicCompact):
    name = "symbolic_incremental_memory_parent"
    def __init__(self):
        super().__init__()
        self.history: list[Episode] = []
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.history.extend(rows)
        self.cost.maintenance_ops += len(rows) * (D + ACTIONS)
        super().update(rows, generation)
    def size(self) -> int:
        return model_bytes(self.models) + archive_bytes(self.history)


class LazySymbolic(SymbolicCompact):
    name = "symbolic_lazy_parent"
    def __init__(self):
        super().__init__()
        self.history: list[Episode] = []
        self.current: list[Episode] = []
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.current = list(rows)
        self.history.extend(rows)
        self.cost.maintenance_ops += len(rows) * (D + ACTIONS)
        self.models = [tuple() for _ in range(ACTIONS)]
    def materialize(self) -> None:
        for a in range(ACTIONS):
            m, c = learn_minimal_dnf(self.current, a)
            self.models[a] = m
            self.cost.add(c)
    def size(self) -> int:
        return model_bytes(self.models) + archive_bytes(self.history)


class GlobalRefit(SymbolicCompact):
    name = "global_refit_parent"
    def __init__(self):
        super().__init__()
        self.history: list[Episode] = []
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.history.extend(rows)
        self.cost.maintenance_ops += len(rows) * (D + ACTIONS)
        for a in range(ACTIONS):
            m, c = learn_minimal_dnf(self.history, a)
            self.models[a] = m
            self.cost.add(c)
    def size(self) -> int:
        return model_bytes(self.models) + archive_bytes(self.history)


class ResetFactor(FactorLocal):
    name = "reset_factor_ablation"
    def __init__(self):
        super().__init__()
        self.history: list[Episode] = []
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        self.history.extend(rows)
        self.cost.maintenance_ops += len(rows) * (D + ACTIONS)
        self.models = [tuple() for _ in range(ACTIONS)]
        self.relevance = set()
        for a in range(ACTIONS):
            m, c = learn_minimal_dnf(rows, a)
            self.models[a] = m
            self.cost.add(c)
        for m in self.models:
            for c in m:
                self.cost.maintenance_ops += len(c)
                self.relevance.update(c)
    def size(self) -> int:
        return model_bytes(self.models, self.relevance) + archive_bytes(self.history)


class Surrogate:
    def __init__(self, persistent: bool):
        self.persistent = persistent
        self.name = "surrogate_persistent_parent" if persistent else "surrogate_window_parent"
        self.models: list[dict[Clause, list[int]]] = [dict() for _ in range(ACTIONS)]
        self.cost = Cost()
    def update(self, rows: Sequence[Episode], generation: int) -> None:
        if not self.persistent:
            self.models = [dict() for _ in range(ACTIONS)]
        for a in range(ACTIONS):
            self.cost.update_components_touched += 1
            for e in rows:
                feats = [i for i, b in enumerate(e.x) if b]
                keys = [(i,) for i in feats] + list(itertools.combinations(feats, 2))
                for k in keys:
                    cell = self.models[a].setdefault(k, [0, 0])
                    cell[0] += e.correct_actions[a]
                    cell[1] += 1
                    self.cost.maintenance_ops += len(k) + 2
    def predict(self, x: tuple[int, ...], a: int) -> int:
        feats = [i for i, b in enumerate(x) if b]
        keys = [(i,) for i in feats] + list(itertools.combinations(feats, 2))
        best = 0.0
        for k in keys:
            self.cost.prediction_literal_evals += len(k)
            pos, total = self.models[a].get(k, [0, 0])
            if total >= 2:
                best = max(best, pos / total)
        return int(best >= 0.90)
    def evaluate(self, rows: Sequence[Episode]) -> tuple[float, float]:
        correct = total = 0
        ba = []
        for a in range(ACTIONS):
            tp = tn = fp = fn = 0
            for e in rows:
                p = self.predict(e.x, a)
                y = e.correct_actions[a]
                correct += int(p == y)
                total += 1
                if y and p: tp += 1
                elif y: fn += 1
                elif p: fp += 1
                else: tn += 1
            terms = []
            if tp + fn: terms.append(tp / (tp + fn))
            if tn + fp: terms.append(tn / (tn + fp))
            ba.append(sum(terms) / len(terms))
        return correct / total, sum(ba) / len(ba)
    def size(self) -> int:
        enc = [{"-".join(map(str, k)): v for k, v in m.items()} for m in self.models]
        return len(json.dumps(enc, sort_keys=True, separators=(",", ":")).encode())


def loo_relevance(rows: Sequence[Episode]) -> set[int]:
    rel = set()
    for i in range(D):
        for a in range(ACTIONS):
            on = [e.correct_actions[a] for e in rows if e.x[i]]
            off = [e.correct_actions[a] for e in rows if not e.x[i]]
            if on and off and abs(sum(on) / len(on) - sum(off) / len(off)) >= 0.20:
                rel.add(i)
                break
    return rel


def evo_score(model: Model, rows: Sequence[Episode], action: int, budget: int, cost: Cost) -> float:
    good = seen = 0
    for e in rows:
        if cost.induction_literal_evals >= budget:
            break
        pred = 0
        for c in model:
            ok = True
            for i in c:
                if cost.induction_literal_evals >= budget:
                    break
                cost.induction_literal_evals += 1
                if not e.x[i]:
                    ok = False
                    break
            if ok:
                pred = 1
                break
        good += int(pred == e.correct_actions[action])
        seen += 1
        cost.validation_examples += 1
    return good / max(1, seen)


def evolutionary_fit(rows: Sequence[Episode], action: int, rng: random.Random, budget: int, warm: Model) -> tuple[Model, Cost]:
    cost = Cost(update_components_touched=1, rediscovery_ops=1)
    budget = max(1, budget)
    pop: list[Model] = []
    if warm:
        pop.append(warm)
    pop.append(tuple())
    while len(pop) < 16:
        pop.append(tuple(tuple(sorted(rng.sample(range(D), rng.randint(1, MAX_WIDTH)))) for _ in range(2)))
    best = warm if warm else tuple()
    best_acc = -1.0
    while cost.induction_literal_evals < budget:
        scored = []
        for model in pop:
            if cost.induction_literal_evals >= budget:
                break
            acc = evo_score(model, rows, action, budget, cost)
            cost.induction_candidates += 1
            scored.append((acc, model))
            if acc > best_acc:
                best_acc, best = acc, model
        if not scored:
            break
        scored.sort(reverse=True, key=lambda z: z[0])
        elites = [m for _, m in scored[:4]]
        pop = list(elites)
        while len(pop) < 16:
            parent = list(rng.choice(elites) if elites else best)
            if not parent:
                parent = [tuple(sorted(rng.sample(range(D), rng.randint(1, MAX_WIDTH))))]
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
            pop.append(tuple(parent))
    return best, cost


class EvolutionWarm:
    name = "evolutionary_warm_parent"
    def __init__(self):
        self.models: list[Model] = [tuple() for _ in range(ACTIONS)]
        self.cost = Cost()
    def update(self, rows: Sequence[Episode], seed: int, regime: str, generation: int, total_budget: int) -> None:
        per = max(1, total_budget // ACTIONS)
        rng = rng_for(seed, f"evolution|{regime}|g{generation}")
        new = []
        for a in range(ACTIONS):
            m, c = evolutionary_fit(rows, a, rng, per, self.models[a])
            new.append(m)
            self.cost.add(c)
        self.models = new
    def size(self) -> int:
        return model_bytes(self.models)


def arm_row(arm, oracle, ident, fresh, before: dict[str, int]) -> dict:
    ec = Cost()
    acc, ba = evaluate(arm.models, fresh, ec)
    arm.cost.prediction_literal_evals += ec.prediction_literal_evals
    delta = {k: arm.cost.as_dict()[k] - before[k] for k in before}
    sp = support_metrics(arm.models, oracle, ident)
    rp, rr = relevance_metrics(arm.models, oracle)
    return {"heldout_accuracy": acc, "heldout_balanced_accuracy": ba, **sp,
            "relevance_precision": rp, "relevance_recall": rr, **delta,
            "state_bytes": arm.size(), "effective_coupling": delta["update_components_touched"] / ACTIONS}


def run_seed(seed: int, regime: str) -> dict:
    world = World.make(seed, regime)
    factor = FactorLocal()
    compact = SymbolicCompact()
    memory = SymbolicMemory()
    lazy = LazySymbolic()
    glob = GlobalRefit()
    reset = ResetFactor()
    arms = [factor, compact, memory, lazy, glob, reset]
    sw = Surrogate(False)
    spersist = Surrogate(True)
    evo = EvolutionWarm()
    generations = []
    for g in range(1, GENERATIONS + 1):
        world.advance(g)
        train = episodes(world, seed, regime, g, "train", TRAIN_N)
        fresh = episodes(world, seed, regime, g, "eval", EVAL_N)
        oracle = tuple(world.supports)
        ident = identifiable_supports(train, oracle)
        row = {"seed": seed, "regime": regime, "generation": g, "arms": {}}
        for arm in arms:
            before = arm.cost.as_dict()
            arm.update(train, g)
            if isinstance(arm, LazySymbolic):
                arm.materialize()
            row["arms"][arm.name] = arm_row(arm, oracle, ident, fresh, before)

        fdelta = row["arms"]["factor_local"]
        evo_budget = fdelta["induction_literal_evals"] + fdelta["invalidation_literal_evals"]
        before = evo.cost.as_dict()
        evo.update(train, seed, regime, g, evo_budget)
        row["arms"][evo.name] = arm_row(evo, oracle, ident, fresh, before)

        for sur in (sw, spersist):
            before = sur.cost.as_dict()
            sur.update(train, g)
            acc, ba = sur.evaluate(fresh)
            delta = {k: sur.cost.as_dict()[k] - before[k] for k in before}
            row["arms"][sur.name] = {
                "heldout_accuracy": acc, "heldout_balanced_accuracy": ba,
                "support_precision": None, "support_recall": None, "support_f1": None,
                "identifiable_supports": sum(map(len, ident)),
                "nonidentifiable_supports": 2 * ACTIONS - sum(map(len, ident)),
                "relevance_precision": None, "relevance_recall": None, **delta,
                "state_bytes": sur.size(), "effective_coupling": delta["update_components_touched"] / ACTIONS,
            }

        loo = loo_relevance(train)
        true_rel = {i for supports in oracle for c in supports for i in c}
        tp = len(loo & true_rel)
        row["arms"]["loo_dependency_ablation"] = {
            "heldout_accuracy": None, "heldout_balanced_accuracy": None,
            "support_precision": None, "support_recall": None, "support_f1": None,
            "identifiable_supports": sum(map(len, ident)),
            "nonidentifiable_supports": 2 * ACTIONS - sum(map(len, ident)),
            "relevance_precision": tp / len(loo) if loo else 0.0,
            "relevance_recall": tp / len(true_rel) if true_rel else 1.0,
            **Cost(update_components_touched=ACTIONS, maintenance_ops=D * ACTIONS, rediscovery_ops=ACTIONS).as_dict(),
            "state_bytes": len(json.dumps(sorted(loo)).encode()), "effective_coupling": 1.0,
        }
        generations.append(row)
    return {"seed": seed, "regime": regime, "generations": generations}


def med(xs):
    return statistics.median(xs) if xs else None


def life_sum(r, arm, key):
    return sum(g["arms"][arm][key] for g in r["generations"])


RESOURCE_KEYS = (
    "induction_literal_evals", "induction_candidates", "induction_selection_ops",
    "invalidation_literal_evals", "invalidation_examples", "update_components_touched",
    "prediction_literal_evals", "validation_examples", "maintenance_ops", "rediscovery_ops",
)


def dominates(parent_final, factor_final, parent_totals, factor_totals):
    sfp, sff = parent_final["support_f1"], factor_final["support_f1"]
    support_ok = sff is None or sfp is None or sfp >= sff - 0.01
    resources_ok = all(parent_totals[k] <= factor_totals[k] for k in RESOURCE_KEYS)
    strict = (parent_final["state_bytes"] < factor_final["state_bytes"] or
              any(parent_totals[k] < factor_totals[k] for k in RESOURCE_KEYS))
    return (parent_final["heldout_accuracy"] >= factor_final["heldout_accuracy"] - 0.01
        and parent_final["heldout_balanced_accuracy"] >= factor_final["heldout_balanced_accuracy"] - 0.01
        and support_ok
        and parent_final["relevance_precision"] >= factor_final["relevance_precision"] - 0.01
        and parent_final["relevance_recall"] >= factor_final["relevance_recall"] - 0.01
        and resources_ok and parent_final["state_bytes"] <= factor_final["state_bytes"] and strict)


def summarize(results: Sequence[dict]) -> dict:
    out = {}
    for regime in sorted({r["regime"] for r in results}):
        subset = [r for r in results if r["regime"] == regime]
        out[regime] = {}
        names = sorted(subset[0]["generations"][0]["arms"])
        for arm in names:
            finals = [r["generations"][-1]["arms"][arm] for r in subset]
            entry = {
                "g8_median_accuracy": med([x["heldout_accuracy"] for x in finals if x["heldout_accuracy"] is not None]),
                "g8_median_balanced_accuracy": med([x["heldout_balanced_accuracy"] for x in finals if x["heldout_balanced_accuracy"] is not None]),
                "g8_median_support_f1": med([x["support_f1"] for x in finals if x["support_f1"] is not None]),
                "g8_median_relevance_precision": med([x["relevance_precision"] for x in finals if x["relevance_precision"] is not None]),
                "g8_median_relevance_recall": med([x["relevance_recall"] for x in finals if x["relevance_recall"] is not None]),
                "g8_median_effective_coupling": med([x["effective_coupling"] for x in finals]),
                "g8_median_state_bytes": med([x["state_bytes"] for x in finals]),
            }
            for key in RESOURCE_KEYS:
                entry[f"lifetime_median_{key}"] = med([life_sum(r, arm, key) for r in subset])
            out[regime][arm] = entry
        dom = {"symbolic_compact_parent": 0, "symbolic_incremental_memory_parent": 0, "any_symbolic_parent": 0}
        for r in subset:
            f = r["generations"][-1]["arms"]["factor_local"]
            ft = {k: life_sum(r, "factor_local", k) for k in RESOURCE_KEYS}
            anyd = False
            for n in ("symbolic_compact_parent", "symbolic_incremental_memory_parent"):
                p = r["generations"][-1]["arms"][n]
                pt = {k: life_sum(r, n, k) for k in RESOURCE_KEYS}
                d = dominates(p, f, pt, ft)
                dom[n] += int(d)
                anyd |= d
            dom["any_symbolic_parent"] += int(anyd)
        dom["n"] = len(subset)
        out[regime]["factor_vs_symbolic_frontier"] = dom
    return out


def _task(t):
    return run_seed(*t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--regimes", default="sparse_stable,dense,drift")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args()
    seeds = [int(x) for x in a.seeds.split(",") if x]
    regimes = [x for x in a.regimes.split(",") if x]
    tasks = [(s, r) for s in seeds for r in regimes]
    results = list(ProcessPoolExecutor(max_workers=a.jobs).map(_task, tasks)) if a.jobs > 1 else [_task(t) for t in tasks]
    payload = {
        "experiment": "E150-factorization-survival-v3",
        "seeds": seeds,
        "regimes": regimes,
        "constants": {"D": D, "actions": ACTIONS, "generations": GENERATIONS, "train_n": TRAIN_N, "eval_n": EVAL_N, "max_width": MAX_WIDTH},
        "results": results,
        "summary": summarize(results),
        "neural_parent": "CANNOT_CHECK_NEURAL_MATCHED",
        "note": "Learner-visible Episode fields are only x and correct_actions. No task ID, regime, seed, hidden support, cause, donor identity or routing key is exposed.",
    }
    Path(a.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
