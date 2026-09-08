#!/usr/bin/env python3
"""Independent PR #150 factorization survival experiment.

Stdlib-only, deterministic, no task/regime/seed/generator metadata is exposed to learners.
The protected protocol is frozen in PROTECTED_PROTOCOL_V1.md.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import statistics
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
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
    raw = hashlib.sha256(f"E150-V1|{seed}|{stream}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def all_clauses_of_width(rng: random.Random, width: int, n: int = 2) -> tuple[Clause, ...]:
    out: list[Clause] = []
    while len(out) < n:
        c = tuple(sorted(rng.sample(range(D), width)))
        if c not in out:
            out.append(c)
    return tuple(out)


@dataclass
class World:
    regime: str
    supports: list[tuple[Clause, ...]]
    drift_rng: random.Random

    @classmethod
    def make(cls, seed: int, regime: str) -> "World":
        srng = rng_for(seed, f"hidden|{regime}")
        width = 2 if regime in {"sparse_stable", "drift"} else 6
        supports = [all_clauses_of_width(srng, width, 2) for _ in range(ACTIONS)]
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
        rows = list(self.supports[action])
        rows[slot] = fresh
        self.supports[action] = tuple(rows)

    def labels(self, x: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(int(any(all(x[i] for i in clause) for clause in self.supports[a])) for a in range(ACTIONS))


@dataclass(frozen=True)
class Episode:
    x: tuple[int, ...]
    correct_actions: tuple[int, ...]


def episodes(world: World, seed: int, regime: str, generation: int, kind: str, n: int) -> list[Episode]:
    rng = rng_for(seed, f"{kind}|{regime}|g{generation}")
    rows = []
    for _ in range(n):
        x = tuple(rng.randrange(2) for _ in range(D))
        rows.append(Episode(x, world.labels(x)))
    return rows


@dataclass
class Cost:
    primitive_literal_evals: int = 0
    induction_candidates: int = 0
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



def clause_holds(clause: Clause, x: tuple[int, ...], cost: Cost | None = None) -> bool:
    for i in clause:
        if cost is not None:
            cost.primitive_literal_evals += 1
        if not x[i]:
            return False
    return True


def predict_model(model: Model, x: tuple[int, ...], cost: Cost | None = None, prediction: bool = False) -> int:
    for clause in model:
        ok = True
        for i in clause:
            if cost is not None:
                if prediction:
                    cost.prediction_literal_evals += 1
                else:
                    cost.primitive_literal_evals += 1
            if not x[i]:
                ok = False
                break
        if ok:
            return 1
    return 0


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
    for clause in candidates:
        cost.induction_candidates += 1
        covered_pos = False
        pure = True
        for e in rows:
            cost.validation_examples += 1
            if clause_holds(clause, e.x, cost):
                if e.correct_actions[action]:
                    covered_pos = True
                else:
                    pure = False
                    break
        if pure and covered_pos:
            valid.append(clause)
    # First remove supersets. Then use an MDL-like set cover over positive witnesses rather than
    # retaining every incomparable pure clause; the latter is a known finite-sample overfit.
    antichain: list[Clause] = []
    for clause in valid:
        s = set(clause)
        if not any(set(prev).issubset(s) for prev in antichain):
            antichain.append(clause)
    positives = [e for e in rows if e.correct_actions[action]]
    uncovered = set(range(len(positives)))
    chosen: list[Clause] = []
    while uncovered:
        best = None
        best_key = None
        for clause in antichain:
            cover = {j for j in uncovered if all(positives[j].x[i] for i in clause)}
            if not cover:
                continue
            # Prefer broad clauses, then fewer literals, then deterministic lexical order.
            key = (len(cover) / len(clause), len(cover), -len(clause), tuple(-i for i in clause))
            if best_key is None or key > best_key:
                best_key, best = key, (clause, cover)
        if best is None:
            break
        clause, cover = best
        chosen.append(clause)
        uncovered -= cover
        antichain = [c for c in antichain if c != clause]
    # Drop clauses whose positive coverage is redundant under the rest.
    pruned = list(chosen)
    changed = True
    while changed:
        changed = False
        for clause in list(pruned):
            others = [c for c in pruned if c != clause]
            if all(any(all(e.x[i] for i in c) for c in others) for e in positives):
                pruned.remove(clause)
                changed = True
                break
    return tuple(sorted(pruned, key=lambda c: (len(c), c))), cost


def predict_actions(models: Sequence[Model], rows: Sequence[Episode], cost: Cost) -> tuple[float, list[tuple[int, ...]]]:
    correct = 0
    total = 0
    preds: list[tuple[int, ...]] = []
    for e in rows:
        p = tuple(predict_model(models[a], e.x, cost, prediction=True) for a in range(ACTIONS))
        preds.append(p)
        for a in range(ACTIONS):
            correct += int(p[a] == e.correct_actions[a])
            total += 1
    return correct / total, preds


def exact_support_metrics(models: Sequence[Model], oracle: Sequence[tuple[Clause, ...]], identifiable: Sequence[set[Clause]]) -> tuple[float | None, float | None, float | None, int]:
    target = set()
    learned = set()
    for a in range(ACTIONS):
        for c in identifiable[a]:
            target.add((a, c))
        for c in models[a]:
            learned.add((a, c))
    if not target:
        return None, None, None, 0
    tp = len(target & learned)
    precision = tp / len(learned) if learned else 0.0
    recall = tp / len(target)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return precision, recall, f1, len(target)


def identifiable_supports(rows: Sequence[Episode], oracle: Sequence[tuple[Clause, ...]]) -> list[set[Clause]]:
    out: list[set[Clause]] = []
    for a in range(ACTIONS):
        ids: set[Clause] = set()
        for clause in oracle[a]:
            positives = [e for e in rows if e.correct_actions[a] and all(e.x[i] for i in clause)]
            if not positives:
                continue
            good = True
            # Every one-literal deletion needs a separating negative witness.
            # That suffices for monotone conjunction minimality under this frozen grammar.
            for drop in clause:
                sub = tuple(i for i in clause if i != drop)
                if not any((not e.correct_actions[a]) and all(e.x[i] for i in sub) for e in rows):
                    good = False
                    break
            if good:
                ids.add(clause)
        out.append(ids)
    return out


def relevance_metrics(models: Sequence[Model], oracle: Sequence[tuple[Clause, ...]]) -> tuple[float, float]:
    learned = {i for m in models for c in m for i in c}
    true = {i for supports in oracle for c in supports for i in c}
    tp = len(learned & true)
    p = tp / len(learned) if learned else 0.0
    r = tp / len(true) if true else 1.0
    return p, r


def state_bytes(models: Sequence[Model], relevance: Iterable[int] | None = None) -> int:
    obj = {"models": models}
    if relevance is not None:
        obj["relevance"] = sorted(relevance)
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())
