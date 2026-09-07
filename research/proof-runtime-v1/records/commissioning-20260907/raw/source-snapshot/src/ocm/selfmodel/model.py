"""Self-model fibre (M11 §1–§2): an evidence-grounded view of the machine itself, tied to
identities (component fingerprints, config digests, receipt hashes, event ids).  A textual
self-description carries no authority: every self-model atom is an OBSERVATION / derived record in
its own fibre `K_self`, and nothing in K_self can raise the warrant or authority of an object-level
atom (theory batch 5 E1; batch-1 T7 no self-authority).

* `Component` — runtime component with a fingerprint (sha256 of its declared source/config),
  version, kind (representation / operator / router / learner / checker / resource / constitution),
  known limitations, lineage.
* `FailureRecord` — a structured failure: task/environment, observed vs expected, trace/event ids,
  candidate responsible layers with evidence, counterfactual/ablation evidence (what restored the
  behaviour), resource state, uncertainty, severity/frequency, scope.  A single low score is never
  an architecture problem (`architecture_alarm` needs repeated failures across instances *and* a
  live obstruction certificate, `diagnose.py`).
* `SelfModel` — the fibre: components, failure history, benchmark results, limitations, active
  proposals, lineage; `record()` admits self-observations as evidence in the runtime under the
  scope `self`, authority `{self_model: 1}` (no `world_truth`, no `commit`).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel


class ComponentKind(str, Enum):
    PARAMETER = "parameter"
    ROUTER = "router"
    OPERATOR = "operator"
    REPRESENTATION = "representation"
    LEARNER = "learner"
    ORGANISATION = "organisation"
    CHECKER = "checker"
    RESOURCE = "resource"
    CONSTITUTION = "constitution"


@dataclass(frozen=True)
class Component:
    component_id: str
    kind: ComponentKind
    version: str
    fingerprint: str                          # sha256 of declared source/config
    limitations: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()

    @staticmethod
    def fingerprint_of(obj: Any) -> str:
        return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


class Layer(str, Enum):
    """Diagnostic layer taxonomy (M11 §3) — revalidated against the J-programme, not copied."""
    D0_PARAMETER = "D0"
    D1_ROUTING = "D1"
    D2_OPERATOR = "D2"
    D3_REPRESENTATION = "D3"
    D4_TASK_FORMULATION = "D4"
    D5_VOCABULARY = "D5"
    D6_LEARNING_POLICY = "D6"
    D7_ORGANISATION = "D7"
    D8_CONSTITUTION = "D8"


@dataclass(frozen=True)
class AblationEvidence:
    """Counterfactual evidence: what was changed and whether the failing task then succeeded."""
    change: str                                # e.g. "restore operator X", "swap router", "reinstate evidence e"
    layer: Layer
    task_succeeded: bool
    evidence_id: str


@dataclass(frozen=True)
class FailureRecord:
    failure_id: str
    task_id: str
    environment: str
    observed: str
    expected: str
    trace_ids: tuple[str, ...]
    candidate_layers: tuple[Layer, ...]
    ablations: tuple[AblationEvidence, ...]
    resource_state: Mapping[str, Any]
    uncertainty: str                           # LIVE | UNKNOWN (was the failure itself checkable?)
    severity: str
    frequency: int                             # occurrences across distinct instances
    scope: str


@dataclass
class SelfModel:
    runtime: OCMRuntime
    components: dict[str, Component] = field(default_factory=dict)
    failures: dict[str, FailureRecord] = field(default_factory=dict)
    benchmarks: list[dict[str, Any]] = field(default_factory=list)
    proposals: dict[str, str] = field(default_factory=dict)          # proposal id → status
    evidence: dict[str, str] = field(default_factory=dict)          # self-model record → runtime evidence id
    authority: Authority = field(default_factory=lambda: Authority.of(self_model=1))

    def register(self, c: Component) -> str:
        self.components[c.component_id] = c
        return self.record(f"component:{c.component_id}@{c.version}", {"component": c.component_id, "kind": c.kind.value, "version": c.version, "fingerprint": c.fingerprint})

    def record(self, key: str, payload: Mapping[str, Any], *, channel: Channel = Channel.OBSERVATION, derived_from: Sequence[str] = ()) -> str:
        """A self-observation: evidence scoped to `self` with self-model authority only.  A record
        derived from traces cites them (E1): revoking a trace reopens every diagnosis built on it."""
        known = [e for e in derived_from if e in self.runtime.state.evidence.records]
        _, eid = self.runtime.admit_evidence({"self": key, **payload}, channel, "self_model", scope=Scope.of("self"), authority=self.authority, derived_from=WarrantProfile.of(set(known)) if known else None)
        self.evidence[key] = eid
        return eid

    def ingest_failure(self, f: FailureRecord) -> str:
        self.failures[f.failure_id] = f
        return self.record(f"failure:{f.failure_id}", {"task": f.task_id, "env": f.environment, "observed": f.observed, "expected": f.expected, "traces": list(f.trace_ids), "layers": [l.value for l in f.candidate_layers], "frequency": f.frequency, "severity": f.severity}, derived_from=f.trace_ids)

    def record_benchmark(self, name: str, result: Mapping[str, Any]) -> str:
        self.benchmarks.append({"name": name, **result})
        return self.record(f"benchmark:{name}:{len(self.benchmarks)}", dict(result))

    def fingerprint(self) -> str:
        return hashlib.sha256(json.dumps({k: v.fingerprint for k, v in sorted(self.components.items())}, sort_keys=True).encode()).hexdigest()[:16]

    def statements_tied_to_identities(self) -> bool:
        """Every self-model record cites a runtime evidence id (no free-text authority)."""
        return all(e in self.runtime.state.evidence.records for e in self.evidence.values())


def self_authority_never_raises_object(self_model: SelfModel, object_authority: Authority) -> Authority:
    """E1: an object-level atom's authority meets with the self-model's — never rises."""
    return object_authority.meet(self_model.authority)


def mutant_self_description_as_authority(text: str) -> Authority:
    """Planted (M11 §1 hostile): a textual self-description granting itself world-truth authority."""
    return Authority.of(world_truth=1, self_model=1) if "improved" in text else Authority.of(self_model=1)
