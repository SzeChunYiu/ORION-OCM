"""Finite deterministic experimental identification with revocable observations.

The host supplies observations. This module proposes a separating experiment;
it does not perform external experiments or treat simulated outcomes as nature.
"""
from dataclasses import dataclass, field

from ocm.kso.ids import content_hash


@dataclass(frozen=True)
class ModelClass:
    queries: tuple[str, ...]
    predictions: tuple[tuple[str, tuple[str, ...]], ...]

    def __post_init__(self):
        queries = tuple(self.queries)
        predictions = tuple((name, tuple(values)) for name, values in self.predictions)
        if (not queries or len(set(queries)) != len(queries) or not predictions
                or len(set(name for name, _ in predictions)) != len(predictions)
                or any(type(q) is not str or not q for q in queries)
                or any(type(name) is not str or not name or len(values) != len(queries)
                       or any(type(v) is not str or not v for v in values) for name, values in predictions)):
            raise ValueError("model class requires distinct identities and complete predictions")
        object.__setattr__(self, "queries", queries)
        object.__setattr__(self, "predictions", predictions)

    @property
    def fingerprint(self):
        return content_hash({"queries": self.queries, "predictions": self.predictions,
                             "assumptions": "finite-deterministic-noiseless.v1"})


@dataclass(frozen=True)
class Observation:
    evidence_id: str
    query: str
    outcome: str
    source: str
    model_class: str

    def __post_init__(self):
        if any(type(x) is not str or not x for x in (self.evidence_id, self.query, self.outcome, self.source, self.model_class)):
            raise ValueError("observation needs an identity, query, outcome, source and class binding")


@dataclass
class ExperimentLearner:
    model_class: ModelClass
    _observations: dict[str, Observation] = field(default_factory=dict, init=False, repr=False)

    def observe(self, observation: Observation):
        if observation.model_class != self.model_class.fingerprint or observation.query not in self.model_class.queries:
            raise ValueError("observation is outside this frozen experimental contract")
        previous = self._observations.get(observation.evidence_id)
        if previous is not None and previous != observation:
            raise ValueError("evidence identity already belongs to another observation")
        self._observations[observation.evidence_id] = observation

    def assess(self, revoked=()):
        revoked = frozenset(revoked)
        observations = tuple(o for eid, o in self._observations.items() if eid not in revoked)
        positions = {q: i for i, q in enumerate(self.model_class.queries)}
        survivors = tuple((name, values) for name, values in self.model_class.predictions
                          if all(values[positions[o.query]] == o.outcome for o in observations))
        if not survivors:
            status, query = "MODEL_CLASS_REFUTED_OR_OBSERVATIONS_CONFLICT", None
        elif len(survivors) == 1:
            status, query = "IDENTIFIED_WITHIN_DECLARED_MODEL_CLASS", None
        else:
            # Minimise worst-case survivor count (generalised binary search).
            scores = []
            for i, q in enumerate(self.model_class.queries):
                groups = {}
                for _, values in survivors:
                    groups[values[i]] = groups.get(values[i], 0) + 1
                if len(groups) > 1:
                    scores.append((max(groups.values()), q))
            status, query = ("EXPERIMENT_REQUIRED", min(scores)[1]) if scores else ("OBSERVATIONALLY_EQUIVALENT", None)
        return {"status": status, "survivors": tuple(name for name, _ in survivors), "next_query": query,
                "model_class": self.model_class.fingerprint,
                "support": tuple(o.evidence_id for o in observations),
                "history": tuple(self._observations),
                "scope": "Conditional on a complete deterministic model class and accurate live observations; not external scientific truth"}
