"""Formal utilities for the GMI ↔ RSI recursive-evolvability bridge.

This module is intentionally small and auditable.  It does not implement an
RSI system.  It formalises the evidence contract used by the research capsule:
what must be true before a lineage can be classified as persistent adaptation,
self-modification, recursive evolvability, or heritable recursive development.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
import math
from typing import Iterable, Sequence


class EvidenceError(ValueError):
    """Raised when an assay violates the registered evidence boundary."""


class RSILevel(IntEnum):
    R0_REFINEMENT = 0
    R1_PERSISTENT_ADAPTATION = 1
    R2_SELF_MODIFICATION = 2
    R3_RECURSIVE_EVOLVABILITY = 3
    R4_HERITABLE_RECURSIVE_DEVELOPMENT = 4
    R5_GENERAL_OPEN_ENDED_RSI = 5


@dataclass(frozen=True)
class ResourceVector:
    compute: float
    data: float
    evaluator: float
    human: float

    def validate(self) -> None:
        for name, value in self.__dict__.items():
            if not math.isfinite(value) or value < 0:
                raise EvidenceError(f"resource {name} must be finite and non-negative")

    def matched(self, other: "ResourceVector", *, atol: float = 1e-12) -> bool:
        self.validate()
        other.validate()
        return all(
            math.isclose(getattr(self, key), getattr(other, key), rel_tol=0.0, abs_tol=atol)
            for key in self.__dict__
        )

    @property
    def scalar_cost(self) -> float:
        """Registered synthetic assay scalar; not a universal GMI resource utility."""
        self.validate()
        return self.compute + self.data + self.evaluator + self.human


@dataclass(frozen=True)
class GenerationRecord:
    generation: int
    task_quality: float
    shadow_quality: float
    persistent_change: bool
    self_change: bool
    development_operator_changed: bool
    development_operator_digest: str
    machine_digest: str
    parent_digest: str | None = None
    development_operator_executed: bool = True
    machine_originated: bool = True
    externally_admitted: bool = True
    evaluator_proxy_changed: bool = False
    external_constitution_changed_by_agent: bool = False

    def validate(self) -> None:
        if self.generation < 0:
            raise EvidenceError("generation must be non-negative")
        for name in ("task_quality", "shadow_quality"):
            value = getattr(self, name)
            if not math.isfinite(value):
                raise EvidenceError(f"{name} must be finite")
        if not self.development_operator_digest:
            raise EvidenceError("development operator digest is required")
        if not self.machine_digest:
            raise EvidenceError("machine digest is required")
        if self.external_constitution_changed_by_agent:
            raise EvidenceError("agent-authored external constitution mutation is outside this bridge")


@dataclass(frozen=True)
class AssayArm:
    name: str
    records: tuple[GenerationRecord, ...]
    resources: ResourceVector
    root_machine_digest: str
    development_ecology: str
    held_out_ecology: str
    frozen_development_operator: bool
    shadow_evaluator_frozen: bool
    hidden_human_intervention: bool = False
    registered_utility: str = "shadow_quality"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if not self.name or not self.root_machine_digest or not self.development_ecology or not self.held_out_ecology:
            raise EvidenceError("arm identity, root machine, development ecology, and held-out ecology are required")
        if self.development_ecology == self.held_out_ecology:
            raise EvidenceError("held-out ecology must be distinct from development ecology")
        if self.registered_utility != "shadow_quality":
            raise EvidenceError("synthetic bridge assay is registered to shadow_quality")
        self.resources.validate()
        if len(self.records) < 2:
            raise EvidenceError("at least root and one descendant are required")
        expected = list(range(self.records[0].generation, self.records[0].generation + len(self.records)))
        actual = [r.generation for r in self.records]
        if actual != expected:
            raise EvidenceError("generations must be contiguous")
        for record in self.records:
            record.validate()
        if self.records[0].machine_digest != self.root_machine_digest:
            raise EvidenceError("first record must bind the registered root machine digest")
        if self.records[0].parent_digest is not None:
            raise EvidenceError("root record must not have a parent digest")
        for previous, current in zip(self.records, self.records[1:]):
            if current.parent_digest != previous.machine_digest:
                raise EvidenceError("lineage parent digest discontinuity")


@dataclass(frozen=True)
class MetaGain:
    mutable_metaproductivity: float
    frozen_metaproductivity: float
    delta: float
    resource_matched: bool
    same_root: bool
    same_ecology: bool


@dataclass(frozen=True)
class EvidenceAssessment:
    level: RSILevel
    reasons: tuple[str, ...]
    meta_gain: MetaGain | None


def descendant_utility(arm: AssayArm, *, horizon: int | None = None) -> float:
    """Best frozen-shadow descendant quality after the root.

    Best-descendant rather than endpoint quality is registered because the
    bridge explicitly permits stepping stones and temporary regressions.
    """
    arm.validate()
    descendants = arm.records[1:]
    if horizon is not None:
        if horizon < 1:
            raise EvidenceError("horizon must be >= 1")
        descendants = descendants[:horizon]
    if not descendants:
        raise EvidenceError("horizon contains no descendants")
    return max(record.shadow_quality for record in descendants)


def metaproductivity(arm: AssayArm, *, horizon: int | None = None) -> float:
    """Synthetic scalar metaproductivity under the registered utility.

    This is a protocol metric, not a universal scalarization theorem.  The
    accompanying theory keeps the full GMI resource/performance profile primary.
    """
    arm.validate()
    root = arm.records[0].shadow_quality
    cost = arm.resources.scalar_cost
    if cost <= 0:
        raise EvidenceError("positive registered resource cost is required")
    return (descendant_utility(arm, horizon=horizon) - root) / cost


def matched_meta_gain(mutable: AssayArm, frozen: AssayArm, *, horizon: int | None = None) -> MetaGain:
    mutable.validate()
    frozen.validate()
    same_root = mutable.root_machine_digest == frozen.root_machine_digest
    same_ecology = mutable.held_out_ecology == frozen.held_out_ecology
    resource_matched = mutable.resources.matched(frozen.resources)
    if not same_root:
        raise EvidenceError("mutable and frozen arms must share the same root machine")
    if not same_ecology:
        raise EvidenceError("mutable and frozen arms must share the held-out ecology")
    if not resource_matched:
        raise EvidenceError("mutable and frozen arms must be resource matched")
    if not frozen.frozen_development_operator:
        raise EvidenceError("comparator must freeze the development operator")
    m = metaproductivity(mutable, horizon=horizon)
    f = metaproductivity(frozen, horizon=horizon)
    return MetaGain(m, f, m - f, resource_matched, same_root, same_ecology)


def _raw_operator_changed(arm: AssayArm) -> bool:
    root = arm.records[0].development_operator_digest
    return any(
        record.development_operator_changed and record.development_operator_digest != root
        for record in arm.records[1:]
    )


def _operator_changed(arm: AssayArm) -> bool:
    root = arm.records[0].development_operator_digest
    return any(
        record.development_operator_changed
        and record.development_operator_digest != root
        and record.development_operator_executed
        and record.machine_originated
        and record.externally_admitted
        for record in arm.records[1:]
    )


def _operator_change_heritable(arm: AssayArm) -> bool:
    """Require an earned D change to persist into at least one later descendant."""
    records = arm.records
    for i in range(1, len(records) - 1):
        record = records[i]
        if record.development_operator_changed:
            digest = record.development_operator_digest
            if any(
                later.development_operator_digest == digest and later.development_operator_executed
                for later in records[i + 1 :]
            ):
                return True
    return False


def _has_persistent_change(arm: AssayArm) -> bool:
    return any(r.persistent_change for r in arm.records[1:])


def _has_self_change(arm: AssayArm) -> bool:
    return any(r.self_change for r in arm.records[1:])


def _evaluator_integrity(arm: AssayArm) -> bool:
    if any(r.evaluator_proxy_changed for r in arm.records[1:]):
        return arm.shadow_evaluator_frozen
    return True


def classify(
    candidate: AssayArm,
    *,
    frozen_comparator: AssayArm | None = None,
    min_meta_gain: float = 0.0,
    cross_domain_replications: int = 0,
    open_ended_generations: int = 0,
) -> EvidenceAssessment:
    """Fail-closed RSI evidence classification.

    R5 deliberately cannot be earned by this finite synthetic capsule.  The two
    arguments are recorded only so tests can prove finite replication does not
    get relabelled as general/open-ended RSI.
    """
    candidate.validate()
    reasons: list[str] = []
    level = RSILevel.R0_REFINEMENT

    if _has_persistent_change(candidate):
        level = RSILevel.R1_PERSISTENT_ADAPTATION
        reasons.append("persistent state change observed")
    if _has_self_change(candidate):
        level = RSILevel.R2_SELF_MODIFICATION
        reasons.append("self-directed persistent change observed")

    meta_gain: MetaGain | None = None
    if level >= RSILevel.R2_SELF_MODIFICATION and _raw_operator_changed(candidate) and not _operator_changed(candidate):
        reasons.append("D change lacks executed/machine-originated/external-admission receipt")

    if level >= RSILevel.R2_SELF_MODIFICATION and _operator_changed(candidate):
        reasons.append("qualified development operator change observed")
        if candidate.hidden_human_intervention:
            reasons.append("hidden human intervention blocks causal RSI evidence")
        elif not _evaluator_integrity(candidate):
            reasons.append("mutable evaluator lacks frozen shadow reference")
        elif frozen_comparator is None:
            reasons.append("no frozen-D comparator")
        else:
            try:
                meta_gain = matched_meta_gain(candidate, frozen_comparator)
            except EvidenceError as exc:
                reasons.append(f"counterfactual invalid: {exc}")
            else:
                if meta_gain.delta > min_meta_gain:
                    level = RSILevel.R3_RECURSIVE_EVOLVABILITY
                    reasons.append("positive resource-matched descendant meta-gain")
                else:
                    reasons.append("no positive descendant meta-gain")

    if level >= RSILevel.R3_RECURSIVE_EVOLVABILITY and _operator_change_heritable(candidate):
        level = RSILevel.R4_HERITABLE_RECURSIVE_DEVELOPMENT
        reasons.append("development-operator improvement persists into later descendant")

    # R5 is an explicit nonclaim: no finite number of replications or generations
    # establishes general/open-ended improvement competence.
    if cross_domain_replications or open_ended_generations:
        reasons.append("finite transfer/open-ended observations do not establish R5")

    return EvidenceAssessment(level, tuple(reasons), meta_gain)


def improvement_increments(values: Sequence[float]) -> tuple[float, ...]:
    if len(values) < 2:
        return tuple()
    return tuple(values[i + 1] - values[i] for i in range(len(values) - 1))


def is_strictly_accelerating(values: Sequence[float]) -> bool:
    """Separate RSI from acceleration: increments themselves must strictly rise."""
    inc = improvement_increments(values)
    return len(inc) >= 2 and all(inc[i + 1] > inc[i] for i in range(len(inc) - 1))


def assert_terminal_ledger(ledger: dict) -> None:
    """Validate recursive D0-D14 closure: complete leaves, valid dependencies, terminal states."""
    families = ledger.get("gap_families", [])
    if not ledger.get("recursive_ledger_terminal"):
        raise EvidenceError("ledger does not declare recursive terminality")
    by_id = {family.get("id"): family for family in families}
    if None in by_id or len(by_id) != len(families):
        raise EvidenceError("gap-family ids must be present and unique")
    allowed = {
        "CLOSED_DEFINITION",
        "CLOSED_FORMAL_REDUCTION",
        "CLOSED_PROTOCOL",
        "CLOSED_COUNTEREXAMPLE",
        "CLOSED_INTEGRATION",
        "INHERITED_CANNOT_CHECK",
        "OPEN_EMPIRICAL_NONCLAIM",
    }
    required_children = {"definition", "mechanism", "observable", "test", "counterexample", "boundary"}
    for family in families:
        if family.get("status") not in allowed:
            raise EvidenceError(f"family {family['id']} has nonterminal status")
        if not family.get("disposition") or not family.get("falsifier_or_reopen_condition"):
            raise EvidenceError(f"family {family['id']} lacks disposition or reopen condition")
        for dep in family.get("depends_on", []):
            if dep not in by_id:
                raise EvidenceError(f"family {family['id']} depends on missing {dep}")
        children = family.get("children", {})
        if set(children) != required_children:
            missing = required_children - set(children)
            extra = set(children) - required_children
            raise EvidenceError(f"family {family['id']} child mismatch missing={missing} extra={extra}")
        if not family.get("child_terminal_metadata"):
            raise EvidenceError(f"family {family['id']} does not declare child terminal-metadata inheritance")
        for kind, child_status in children.items():
            if child_status not in allowed:
                raise EvidenceError(f"family {family['id']} child {kind} is nonterminal")
