"""Finite baseline-representation-retention learners; no donor/scorer imports.

All policy structure is human-supplied conventional learning machinery. Evidence
effects are learned by paid membership queries. Four-block candidate grouping
and the justified monotone hypothesis class are supplied equally to all arms.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


@dataclass
class Cost:
    learner_operations: int = 0
    query_calls: int = 0
    source_shape_checks: int = 0
    source_observation_reads: int = 0
    serialization_bytes_written: int = 0
    serialization_bytes_read: int = 0

    @property
    def counted_operations(self):
        return self.learner_operations + self.source_shape_checks + self.source_observation_reads


def monotone_tables(bits: int, cost: Cost) -> tuple[int, ...]:
    """Exhaustive conventional finite version-space construction, fully charged.

    The baseline at the full live set is already known to be retained. All other
    functions satisfying monotonicity remain possible, including constant one.
    """
    if type(bits) is not int or bits != 4:
        raise ValueError("only registered four-block source scope supported")
    n = 1 << bits
    result = []
    for table in range(1 << n):
        cost.learner_operations += 1
        if not (table >> (n - 1)) & 1:
            continue
        valid = True
        for mask in range(n):
            cost.learner_operations += 1
            if not (table >> mask) & 1:
                continue
            for bit in range(bits):
                cost.learner_operations += 1
                if not (table >> (mask | (1 << bit))) & 1:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            result.append(table)
    return tuple(result)


@dataclass
class SupportLearner:
    arm: str
    bits: int
    context: dict
    cost: Cost
    tables: tuple[int, ...] = ()
    observations: dict[int, bool] = field(default_factory=dict)
    probe_order: list[int] = field(default_factory=list)

    def __post_init__(self):
        if type(self.bits) is not int or self.bits != 4:
            raise ValueError("only registered four-block source scope supported")
        if self.arm not in ("active_monotone", "antichain_parent", "eager_table", "lazy_cache", "loo_ablation"):
            raise ValueError("unregistered arm")
        self.context = json.loads(canonical(self.context))
        self.observations.setdefault((1 << self.bits) - 1, True)

    def _validate_mask(self, mask):
        if type(mask) is not int or not 0 <= mask < (1 << self.bits):
            raise ValueError("mask outside registered four-block live-set domain")

    def predict(self, mask: int, *, generalize: bool = True):
        self._validate_mask(mask)
        self.cost.learner_operations += 1
        if mask in self.observations:
            return self.observations[mask]
        if not generalize or self.arm == "lazy_cache":
            return None
        if self.arm == "active_monotone":
            values = set()
            for table in self.tables:
                self.cost.learner_operations += 1
                values.add(bool((table >> mask) & 1))
                if len(values) == 2:
                    return None
            if not values:
                raise ValueError("empty version space: assumption violated")
            return next(iter(values))
        if self.arm == "loo_ablation":
            # Explicit weak negative ablation: an absent singleton dependency
            # is treated as no effect; known redundant-support failure expected.
            full = (1 << self.bits) - 1
            for bit in range(self.bits):
                self.cost.learner_operations += 1
                if not (mask & (1 << bit)) and self.observations.get(full ^ (1 << bit)) is False:
                    return False
            return True
        for observed, retained in self.observations.items():
            self.cost.learner_operations += 1
            if retained and observed & mask == observed:
                return True
            if not retained and observed | mask == observed:
                return False
        return None

    def observe(self, mask: int, retained: bool):
        if type(retained) is not bool:
            raise ValueError("membership oracle must return explicit bool")
        previous = self.predict(mask) if self.arm != "loo_ablation" else self.observations.get(mask)
        if previous is not None and previous != retained:
            raise ValueError("monotonicity or source identity assumption violated")
        self.observations[mask] = retained
        if self.arm == "active_monotone":
            survivors = []
            for table in self.tables:
                self.cost.learner_operations += 1
                if bool((table >> mask) & 1) == retained:
                    survivors.append(table)
            self.tables = tuple(survivors)
            if not self.tables:
                raise ValueError("empty learned version space")

    def next_probe(self):
        full = (1 << self.bits) - 1
        if self.arm == "lazy_cache":
            return None
        if self.arm == "loo_ablation":
            return next((full ^ (1 << bit) for bit in range(self.bits)
                         if full ^ (1 << bit) not in self.observations), None)
        if self.arm == "eager_table":
            return next((mask for mask in range(full + 1) if mask not in self.observations), None)
        unknown = [mask for mask in range(full + 1) if self.predict(mask) is None]
        if not unknown:
            return None
        if self.arm == "active_monotone":
            scores = []
            for mask in unknown:
                yes = 0
                for table in self.tables:
                    self.cost.learner_operations += 1
                    yes += (table >> mask) & 1
                scores.append((max(yes, len(self.tables) - yes), mask))
            return min(scores)[1]
        # Conventional antichain parent minimizes worst-case unresolved masks
        # using order closure, without materializing a truth-function library.
        scores = []
        for mask in unknown:
            yes, no = 0, 0
            for other in unknown:
                self.cost.learner_operations += 2
                yes += mask & other == mask
                no += mask | other == mask
            scores.append((max(len(unknown) - yes, len(unknown) - no), mask))
        return min(scores)[1]

    def acquire(self, oracle: Callable[[int], bool]):
        while (mask := self.next_probe()) is not None:
            self.cost.query_calls += 1
            retained = oracle(mask)
            self.probe_order.append(mask)
            self.observe(mask, retained)

    def answer(self, mask: int, oracle: Callable[[int], bool], *, generalize=True):
        prediction = self.predict(mask, generalize=generalize)
        inferred = mask not in self.observations and prediction is not None
        if prediction is None:
            self.cost.query_calls += 1
            prediction = oracle(mask)
            self.observe(mask, prediction)
        return prediction, inferred

    def record(self):
        """Keep alternative structures while unresolved; no false minimality."""
        positives = []
        unknown = []
        for mask in range(1 << self.bits):
            prediction = self.predict(mask)
            if prediction is True:
                positives.append(mask)
            elif prediction is None:
                unknown.append(mask)
        minimal = []
        for mask in positives:
            self.cost.learner_operations += len(positives)
            if not any(other != mask and other & mask == other for other in positives):
                minimal.append(mask)
        return {"schema": "ocm.baseline_retention_effect.v1", "arm": self.arm,
                "bits": self.bits, "context": json.loads(canonical(self.context)),
                "observations": {str(k): v for k, v in self.observations.items()},
                "version_space": list(self.tables), "probe_order": self.probe_order,
                "predicted_minimal_positive_masks": minimal,
                "unknown_masks": unknown, "predictions_cover_domain": not unknown,
                "minimality_scope": "minimal among currently predicted positives; not a global minimal-support certificate when unknown masks remain",
                "certification": "UNSOUND_ABLATION" if self.arm == "loo_ablation" else "CONDITIONAL_ON_BOUND_FIXED_ORDER_MONOTONICITY",
                "claim": "fixed induced representation retained; arbitrary revised rule not predicted",
                "origin": "human supplied algorithm; effects acquired by measured interventions"}

    def persist(self, path: Path):
        record = self.record()
        payload = canonical({"record": record, "sha256": sha(record)}).encode()
        path.write_bytes(payload)
        self.cost.serialization_bytes_written += len(payload)
        return sha(record)

    @classmethod
    def restart(cls, path: Path, *, expected_hash: str, expected_context: dict, cost: Cost):
        payload = path.read_bytes()
        cost.serialization_bytes_read += len(payload)
        envelope = json.loads(payload)
        record = envelope["record"]
        if sha(record) != expected_hash or envelope["sha256"] != expected_hash:
            raise ValueError("effect snapshot mismatch")
        if record["context"] != expected_context:
            raise ValueError("effect scope invalidated: source/evidence/baseline changed")
        return cls(record["arm"], record["bits"], record["context"], cost,
                   tuple(record["version_space"]),
                   {int(k): v for k, v in record["observations"].items()}, record["probe_order"])
