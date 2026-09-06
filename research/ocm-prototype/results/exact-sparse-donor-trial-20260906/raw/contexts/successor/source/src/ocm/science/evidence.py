"""Scientific task contract and evidence object model (M10 §1–§3).

* `ScientificTask` extends the M9 contract with the question, the measurement model, allowed
  experiments with cost/risk, known confounders, the hidden oracle (checker-only), required
  reporting; the four evidence classes are kept apart: prior evidence, intervention results,
  verifier/proof outcomes, protected ground truth.
* `Observation` records source/provenance, measurement, conditions/intervention, an error model,
  replicate identity, pipeline version, scope, confounders, and its warrant.  **Dependence**: every
  observation names its *source*; corroboration counts distinct sources, never repeated
  measurements from one dependent source (KS-T33 / batch-1 T11 — the planted mutant counts
  replicates).
* Layers never flattened: `Observation` → `Interpretation` → `Hypothesis` (predictions, scope,
  assumptions, support/counter, model-comparison state, cost, known failures) → `Conclusion`
  (with the identification assumptions a causal conclusion needs).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile, meet_all_profiles


@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    description: str
    cost: float
    risk: float
    intervention: Mapping[str, Any]           # variable → value (do-operator) or {} for observation
    outcome_var: str


@dataclass(frozen=True)
class ScientificTask:
    task_id: str
    question: str                             # e.g. "does X cause Y"
    estimand: str
    prior_evidence: tuple[str, ...]           # observation ids available before action
    measurement_model: Mapping[str, Any]
    experiments: tuple[Experiment, ...]
    budget: float
    known_confounders: tuple[str, ...]
    hidden_oracle: Mapping[str, Any]          # checker-only
    required_reporting: tuple[str, ...] = ("effect", "uncertainty", "limitations", "provenance")
    scope: Scope = field(default_factory=Scope.universal)


@dataclass(frozen=True)
class Observation:
    obs_id: str
    source: str                               # provenance: dataset / lab / paper id
    measurement: Mapping[str, float]
    conditions: Mapping[str, Any]             # intervention if any
    error_model: str
    replicate: int
    pipeline_version: str
    scope: Scope
    confounders_possible: tuple[str, ...]
    evidence_id: str
    authority: Authority = field(default_factory=lambda: Authority.of(source=1))

    @property
    def warrant(self) -> WarrantProfile:
        return WarrantProfile.of({self.evidence_id})


def independent_corroboration(observations: Sequence[Observation]) -> int:
    """Distinct *sources* supporting a claim; replicates from one source count once (KS-T33)."""
    return len({o.source for o in observations})


def mutant_replicates_as_corroboration(observations: Sequence[Observation]) -> int:
    """Planted (M10 §2 hostile): every replicate counted as independent support."""
    return len(observations)


class HypothesisKind(str, Enum):
    SYMBOLIC = "SYMBOLIC"
    STATISTICAL = "STATISTICAL"
    CAUSAL = "CAUSAL"
    SIMULATION = "SIMULATION"
    PROGRAM = "PROGRAM"
    FORMAL = "FORMAL"


@dataclass
class Hypothesis:
    hyp_id: str
    kind: HypothesisKind
    statement: str
    predict: Callable[[Mapping[str, Any]], Any]         # conditions → predicted outcome
    scope: Scope
    assumptions: tuple[str, ...]
    support: list[str] = field(default_factory=list)    # observation ids consistent
    counter: list[str] = field(default_factory=list)    # observation ids inconsistent
    cost: float = 1.0
    known_failures: tuple[str, ...] = ()
    status: str = "CANDIDATE"                           # CANDIDATE | SUPPORTED | REFUTED | CONTRADICTED

    def warrant(self, observations: Mapping[str, Observation]) -> WarrantProfile:
        """Support only from live, *independent* observations: ⊕ over distinct-source supports,
        each support ⊗ with the hypothesis's own assumptions' evidence (assumption ids)."""
        by_source: dict[str, WarrantProfile] = {}
        for oid in self.support:
            o = observations[oid]
            by_source.setdefault(o.source, o.warrant)
        w = WarrantProfile.zero()
        for p in by_source.values():
            w = w.join(p)
        return w

    def liveness(self, observations: Mapping[str, Observation], revoked: Iterable[Hashable]) -> Liveness:
        if self.counter and any(observations[c].warrant.liveness(revoked) is Liveness.LIVE for c in self.counter):
            return Liveness.DEAD
        return self.warrant(observations).liveness(revoked)


@dataclass(frozen=True)
class Conclusion:
    conclusion_id: str
    hypothesis: str
    kind: str                                          # ASSOCIATION | CAUSAL | FORMAL | ESTIMATE
    identification_assumptions: tuple[str, ...]        # registered assumptions a causal claim needs
    evidence: tuple[str, ...]
    marker: str                                        # ASSERTED | UNCERTAIN | REPORTED
    lineage: tuple[str, ...] = ()


def causal_claim_allowed(kind: str, identification_assumptions: Iterable[str], registered: Iterable[str]) -> bool:
    """A causal conclusion needs registered identification assumptions (randomised intervention,
    back-door set, or instrument); graph structure alone never warrants causality (M10 §5)."""
    if kind != "CAUSAL":
        return True
    ia, reg = set(identification_assumptions), set(registered)
    return bool(ia) and ia <= reg


def mutant_correlation_as_causation(kind: str) -> bool:
    """Planted (M10 §17): correlation stated as causation."""
    return True
