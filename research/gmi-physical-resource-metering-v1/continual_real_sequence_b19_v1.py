#!/usr/bin/env python3
"""B19 real-task-sequence continual-learning witness at planted microworld scope.

Closes the open Issue #602 B19 box "Test under real task sequences" without
raising the claim above planted sequential classification. Regime prices remain
registered constants; orderings under those prices are the scientific object.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Callable, Iterable, Sequence


HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Example:
    features: tuple[int, ...]
    label: int
    task_id: int


@dataclass(frozen=True)
class TaskSpec:
    task_id: int
    active_dims: tuple[int, ...]
    target_parity_dims: tuple[int, ...]


@dataclass(frozen=True)
class SequenceSpec:
    name: str
    dim: int
    tasks: tuple[TaskSpec, ...]
    n_train: int
    n_test: int
    seed: int


@dataclass(frozen=True)
class RegimeResult:
    regime: str
    retention: Fraction
    plasticity: Fraction
    cost: Fraction
    per_task_acc: tuple[Fraction, ...]
    feasible: bool


def _label_for(features: Sequence[int], task: TaskSpec) -> int:
    return sum(features[i] for i in task.target_parity_dims) % 2


def materialize_sequence(spec: SequenceSpec) -> list[list[Example]]:
    rng = random.Random(spec.seed)
    streams: list[list[Example]] = []
    for task in spec.tasks:
        examples: list[Example] = []
        for _ in range(spec.n_train + spec.n_test):
            feats = [0] * spec.dim
            for d in task.active_dims:
                feats[d] = rng.randrange(2)
            examples.append(Example(tuple(feats), _label_for(feats, task), task.task_id))
        streams.append(examples)
    return streams


def accuracy(model: Callable[[Example], int], data: Iterable[Example]) -> Fraction:
    rows = list(data)
    if not rows:
        return Fraction(0)
    correct = sum(1 for ex in rows if model(ex) == ex.label)
    return Fraction(correct, len(rows))


class ExactStore:
    """Finite exact lookup on full feature vectors with hard capacity."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.table: dict[tuple[int, ...], int] = {}
        self.order: list[tuple[int, ...]] = []

    def fit(self, data: Sequence[Example], protect: set[tuple[int, ...]] | None = None) -> int:
        """Return count of training keys that could not be admitted."""
        protect = protect or set()
        rejected = 0
        for ex in data:
            key = ex.features
            if key in protect:
                # protected keys keep their prior label
                if key not in self.table:
                    rejected += 1
                continue
            if key not in self.table and len(self.table) >= self.capacity:
                evicted = False
                for old in list(self.order):
                    if old not in protect:
                        self.order.remove(old)
                        del self.table[old]
                        evicted = True
                        break
                if not evicted:
                    rejected += 1
                    continue
            if key not in self.table:
                self.order.append(key)
            self.table[key] = ex.label
        return rejected

    def predict(self, ex: Example) -> int:
        return self.table.get(ex.features, 0)


def _split(stream: Sequence[Example], n_train: int) -> tuple[list[Example], list[Example]]:
    return list(stream[:n_train]), list(stream[n_train:])


def _unique_keys(streams: Sequence[Sequence[Example]]) -> set[tuple[int, ...]]:
    return {ex.features for stream in streams for ex in stream}


def run_expand(
    streams: list[list[Example]],
    specs: Sequence[TaskSpec],
    n_train: int,
    base_cap: int,
    prices: dict[str, Fraction],
) -> RegimeResult:
    need = len(_unique_keys([[ex for ex in stream[:n_train]] for stream in streams]))
    extra = max(0, need - base_cap)
    store = ExactStore(base_cap + extra)
    tests: list[list[Example]] = []
    for stream in streams:
        train, test = _split(stream, n_train)
        store.fit(train)
        tests.append(test)
    accs = tuple(accuracy(store.predict, test) for test in tests)
    retention = _mean(accs[:-1]) if len(accs) > 1 else Fraction(1)
    feasible = all(a >= Fraction(3, 4) for a in accs)
    return RegimeResult("expand", retention, accs[-1], prices["capacity"] * extra, accs, feasible)


def run_regularize(
    streams: list[list[Example]],
    specs: Sequence[TaskSpec],
    n_train: int,
    base_cap: int,
    prices: dict[str, Fraction],
) -> RegimeResult:
    store = ExactStore(base_cap)
    protected: set[tuple[int, ...]] = set()
    tests: list[list[Example]] = []
    lost = 0
    for stream in streams:
        train, test = _split(stream, n_train)
        lost += store.fit(train, protect=set(protected))
        protected.update(ex.features for ex in train)
        tests.append(test)
    accs = tuple(accuracy(store.predict, test) for test in tests)
    retention = _mean(accs[:-1]) if len(accs) > 1 else Fraction(1)
    # Feasible only if old tasks stay and new task is acquired.
    feasible = retention >= Fraction(3, 4) and accs[-1] >= Fraction(3, 4)
    return RegimeResult(
        "regularize", retention, accs[-1], prices["lost_distinction"] * lost, accs, feasible
    )


def run_modularize(
    streams: list[list[Example]],
    specs: Sequence[TaskSpec],
    n_train: int,
    base_cap: int,
    prices: dict[str, Fraction],
) -> RegimeResult:
    modules = [ExactStore(base_cap) for _ in specs]
    tests: list[list[Example]] = []
    for idx, stream in enumerate(streams):
        train, test = _split(stream, n_train)
        modules[idx].fit(train)
        tests.append(test)

    def predict(ex: Example) -> int:
        return modules[ex.task_id].predict(ex)

    accs = tuple(accuracy(predict, test) for test in tests)
    retention = _mean(accs[:-1]) if len(accs) > 1 else Fraction(1)
    cost = prices["store"] * len(specs) * base_cap + prices["route"] * len(specs)
    feasible = all(a >= Fraction(3, 4) for a in accs)
    return RegimeResult("modularize", retention, accs[-1], cost, accs, feasible)


def run_replay(
    streams: list[list[Example]],
    specs: Sequence[TaskSpec],
    n_train: int,
    base_cap: int,
    prices: dict[str, Fraction],
    overwrite: Fraction,
) -> RegimeResult:
    need = len(_unique_keys([[ex for ex in stream[:n_train]] for stream in streams]))
    # Replay cannot create capacity: illegal when need > base.
    if need > base_cap:
        accs = tuple(Fraction(0) for _ in streams)
        return RegimeResult("replay", Fraction(0), Fraction(0), Fraction(10**9), accs, False)

    store = ExactStore(base_cap)
    memory: list[Example] = []
    tests: list[list[Example]] = []
    replay_charges = 0
    for stream in streams:
        train, test = _split(stream, n_train)
        if overwrite > 0 and store.table:
            drop_n = max(1, int(float(overwrite) * len(store.table)))
            for key in list(store.table.keys())[:drop_n]:
                del store.table[key]
                if key in store.order:
                    store.order.remove(key)
        batch = list(memory) + list(train)
        store.fit(batch)
        replay_charges += len(memory)
        memory.extend(train)
        tests.append(test)
    accs = tuple(accuracy(store.predict, test) for test in tests)
    retention = _mean(accs[:-1]) if len(accs) > 1 else Fraction(1)
    feasible = all(a >= Fraction(3, 4) for a in accs)
    return RegimeResult("replay", retention, accs[-1], prices["replay"] * replay_charges, accs, feasible)


def _mean(vals: Sequence[Fraction]) -> Fraction:
    if not vals:
        return Fraction(0)
    return sum(vals, Fraction(0)) / len(vals)


def planted_sequences() -> tuple[SequenceSpec, ...]:
    """Two concrete sequences with different geometries, same price ledger."""
    seq_a = SequenceSpec(
        name="disjoint_parity_ladder",
        dim=6,
        tasks=(
            TaskSpec(0, (0, 1), (0, 1)),
            TaskSpec(1, (2, 3), (2, 3)),
            TaskSpec(2, (4, 5), (4, 5)),
        ),
        n_train=24,
        n_test=12,
        seed=60219,
    )
    seq_b = SequenceSpec(
        name="shifted_parity_ladder",
        dim=6,
        tasks=(
            TaskSpec(0, (0, 2), (0, 2)),
            TaskSpec(1, (1, 3), (1, 3)),
            TaskSpec(2, (4, 5), (4, 5)),
        ),
        n_train=24,
        n_test=12,
        seed=60221,
    )
    return seq_a, seq_b


def evaluate_sequence(
    spec: SequenceSpec,
    prices: dict[str, Fraction],
    base_cap: int,
    overwrite: Fraction,
) -> dict[str, object]:
    streams = materialize_sequence(spec)
    results = [
        run_expand(streams, spec.tasks, spec.n_train, base_cap, prices),
        run_regularize(streams, spec.tasks, spec.n_train, base_cap, prices),
        run_modularize(streams, spec.tasks, spec.n_train, base_cap, prices),
        run_replay(streams, spec.tasks, spec.n_train, base_cap, prices, overwrite),
    ]
    feasible = [r for r in results if r.feasible]
    if not feasible:
        raise AssertionError(f"no regime feasible on sequence {spec.name}: {[as_row(r) for r in results]}")
    best_cost = min(r.cost for r in feasible)
    winners = sorted(r.regime for r in feasible if r.cost == best_cost)
    return {
        "sequence": spec.name,
        "unique_train_keys": len(_unique_keys([[ex for ex in stream[: spec.n_train]] for stream in streams])),
        "base_cap": base_cap,
        "winners": winners,
        "results": [as_row(r) for r in results],
    }


def as_row(r: RegimeResult) -> dict[str, object]:
    return {
        "regime": r.regime,
        "retention": str(r.retention),
        "plasticity": str(r.plasticity),
        "cost": str(r.cost),
        "feasible": r.feasible,
        "per_task_acc": [str(a) for a in r.per_task_acc],
    }


def run_witness() -> dict[str, object]:
    # Registered prices (constants). Cheap capacity favors expand; dear capacity
    # + cheap stores/routing favors modularize. Replay stays illegal when the
    # unique-key load exceeds base capacity (capacity failure, not overwrite).
    prices_cheap = {
        "capacity": Fraction(1),
        "lost_distinction": Fraction(20),
        "store": Fraction(4),
        "route": Fraction(4),
        "replay": Fraction(3),
    }
    prices_dear = {
        "capacity": Fraction(30),
        "lost_distinction": Fraction(20),
        "store": Fraction(1, 2),
        "route": Fraction(1, 2),
        "replay": Fraction(9),
    }

    seqs = planted_sequences()
    base_cap = 4  # each 2-bit task has up to 4 keys; three tasks need ~12

    cheap_rows = [evaluate_sequence(s, prices_cheap, base_cap=base_cap, overwrite=Fraction(0)) for s in seqs]
    for row in cheap_rows:
        if row["winners"] != ["expand"]:
            raise AssertionError(
                f"cheap-capacity prediction failed on {row['sequence']}: {row['winners']} :: {row['results']}"
            )

    dear_rows = [evaluate_sequence(s, prices_dear, base_cap=base_cap, overwrite=Fraction(0)) for s in seqs]
    for row in dear_rows:
        if row["winners"] != ["modularize"]:
            raise AssertionError(
                f"dear-capacity prediction failed on {row['sequence']}: {row['winners']} :: {row['results']}"
            )

    cheap_winners = {tuple(r["winners"]) for r in cheap_rows}
    if len(cheap_winners) != 1:
        raise AssertionError("winner set should be stable across concrete sequences at fixed prices")

    digest = sha256(
        json.dumps({"cheap": cheap_rows, "dear": dear_rows}, sort_keys=True).encode("utf-8")
    ).hexdigest()

    return {
        "schema": "gmi-b19-real-sequence-witness-v1",
        "claim_ceiling": "REAL_SEQUENCE_WITNESS_AT_PLANTED_SCOPE",
        "sequences": [s.name for s in seqs],
        "cheap_capacity": cheap_rows,
        "dear_capacity": dear_rows,
        "stable_across_sequences_at_fixed_prices": True,
        "price_ratio_moves_winner": True,
        "digest": digest,
        "non_claims": [
            "not a real-world continual-learning benchmark transfer claim",
            "price magnitudes are registered constants, not universal constants",
        ],
    }


def write_receipt(path: Path | None = None) -> dict[str, object]:
    result = run_witness()
    out = path or (HERE / "receipts" / "B19_REAL_SEQUENCE_RECEIPT_V1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = write_receipt()
    print(json.dumps({"claim_ceiling": result["claim_ceiling"], "digest": result["digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
