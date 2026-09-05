"""Cross-cutting lifetime metrics for ORION-OCM issue #50.

The purpose of this module is measurement discipline, not a favorable score. In
particular, ``k`` means *instrumented persistent objects actually touched* by an
operation. It is never inferred from the returned top-k result, non-zero
activation count, or sparse edge count. If a code path can perform an
uninstrumented global scan, the sparse-computation claim is CANNOT_CHECK.

Raw resource coordinates are preserved as a vector. This module intentionally
does not convert them to dollars/FLOPs or a single intelligence/efficiency score.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping


class CheckStatus(str, Enum):
    MEASURED = "MEASURED"
    CANNOT_CHECK = "CANNOT_CHECK"


class MatchStatus(str, Enum):
    MATCHED = "MATCHED"
    REFERENCE = "REFERENCE"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ResourceVector:
    """Non-collapsed resource accounting for one operation or run."""

    wall_seconds: float = 0.0
    cpu_seconds: float = 0.0
    gpu_seconds: float = 0.0
    peak_memory_bytes: int = 0
    persistent_read_bytes: int = 0
    persistent_write_bytes: int = 0
    index_read_entries: int = 0
    index_write_entries: int = 0
    external_io_calls: int = 0
    tool_calls: int = 0
    verifier_calls: int = 0
    work_units: int = 0
    preprocessing_work_units: int = 0
    maintenance_work_units: int = 0
    static_model_parameters: int = 0
    persistent_storage_bytes: int = 0
    index_storage_bytes: int = 0
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        numeric = asdict(self)
        numeric.pop("notes", None)
        if any(v < 0 for v in numeric.values()):
            raise ValueError("resource coordinates must be non-negative")

    def plus(self, other: "ResourceVector") -> "ResourceVector":
        data = {}
        for name in self.__dataclass_fields__:
            if name == "notes":
                continue
            data[name] = getattr(self, name) + getattr(other, name)
        data["notes"] = self.notes + other.notes
        return ResourceVector(**data)


@dataclass(frozen=True)
class InformationVector:
    words: int = 0
    tokens: int = 0
    examples: int = 0
    demonstrations: int = 0
    labels: int = 0
    explicit_lessons: int = 0
    interaction_turns: int = 0
    grounded_observations: int = 0
    source_assertions: int = 0
    annotations: int = 0

    def __post_init__(self) -> None:
        if any(v < 0 for v in asdict(self).values()):
            raise ValueError("information coordinates must be non-negative")


@dataclass(frozen=True)
class StateMeasure:
    """Logical persistent state at a declared measurement boundary.

    N is ``logical_n`` = the number of persistent, identity-bearing objects in
    the declared object grammar. Auxiliary non-identity cardinalities are
    reported separately and cannot pad the denominator of k/N. Atom count must
    not be compared numerically with neural parameter count; cross-architecture
    comparisons use storage/resource/information vectors.
    """

    object_counts: Mapping[str, int]
    auxiliary_counts: Mapping[str, int] = field(default_factory=dict)
    bytes_by_class: Mapping[str, int] = field(default_factory=dict)
    index_entries: int = 0
    index_bytes: int = 0
    object_grammar: str = "unspecified"
    status: CheckStatus = CheckStatus.MEASURED
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        if any(v < 0 for v in self.object_counts.values()):
            raise ValueError("object counts must be non-negative")
        if any(v < 0 for v in self.auxiliary_counts.values()):
            raise ValueError("auxiliary counts must be non-negative")
        if any(v < 0 for v in self.bytes_by_class.values()):
            raise ValueError("byte counts must be non-negative")
        if self.index_entries < 0 or self.index_bytes < 0:
            raise ValueError("index counts must be non-negative")
        if self.status is CheckStatus.CANNOT_CHECK and not self.cannot_check_reason:
            raise ValueError("CANNOT_CHECK state measure requires a reason")

    @property
    def logical_n(self) -> int:
        return sum(self.object_counts.values())

    @property
    def logical_bytes(self) -> int:
        return sum(self.bytes_by_class.values())


@dataclass(frozen=True)
class TouchMeasure:
    """Actual persistent identities touched by one scoped operation."""

    touched_ids: tuple[str, ...]
    touched_by_class: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    index_entries_touched: int = 0
    global_scan_items: int = 0
    status: CheckStatus = CheckStatus.MEASURED
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        if len(set(self.touched_ids)) != len(self.touched_ids):
            raise ValueError("touched_ids must be unique; repeated work belongs in resources")
        if self.index_entries_touched < 0 or self.global_scan_items < 0:
            raise ValueError("touch counters must be non-negative")
        if self.status is CheckStatus.MEASURED and self.global_scan_items > self.k:
            raise ValueError("a measured global scan must be represented in k")
        if self.touched_by_class:
            classified = [item for ids in self.touched_by_class.values() for item in ids]
            if len(classified) != len(set(classified)):
                raise ValueError("a touched identity cannot be assigned to multiple object classes")
            if set(classified) != set(self.touched_ids):
                raise ValueError("touched_by_class must partition touched_ids when supplied")
        if self.status is CheckStatus.CANNOT_CHECK and not self.cannot_check_reason:
            raise ValueError("CANNOT_CHECK touch measure requires a reason")

    @property
    def k(self) -> int:
        return len(self.touched_ids)

    def k_over_n(self, state: StateMeasure) -> float | None:
        if self.status is not CheckStatus.MEASURED or state.status is not CheckStatus.MEASURED:
            return None
        if state.logical_n == 0:
            return 0.0 if self.k == 0 else None
        if self.k > state.logical_n:
            raise ValueError("k cannot exceed N under one declared object grammar")
        return self.k / state.logical_n


@dataclass(frozen=True)
class AcquisitionMeasure:
    task_id: str
    threshold_id: str
    threshold_met: bool
    information: InformationVector
    resources: ResourceVector
    new_object_ids: tuple[str, ...] = ()
    reused_operator_ids: tuple[str, ...] = ()
    reuse_witness_ids: tuple[str, ...] = ()
    status: CheckStatus = CheckStatus.MEASURED
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        if len(set(self.new_object_ids)) != len(self.new_object_ids):
            raise ValueError("new object ids must be unique")
        if len(set(self.reused_operator_ids)) != len(self.reused_operator_ids):
            raise ValueError("reused operator ids must be unique")
        if self.reused_operator_ids and not self.reuse_witness_ids:
            raise ValueError("a reuse event requires an execution/causal witness")
        if self.status is CheckStatus.CANNOT_CHECK and not self.cannot_check_reason:
            raise ValueError("CANNOT_CHECK acquisition measure requires a reason")


@dataclass(frozen=True)
class QueryMeasure:
    query_id: str
    state_before: StateMeasure
    touches: TouchMeasure
    resources: ResourceVector
    outcome: str
    status: CheckStatus = CheckStatus.MEASURED
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        self.touches.k_over_n(self.state_before)
        if self.status is CheckStatus.CANNOT_CHECK and not self.cannot_check_reason:
            raise ValueError("CANNOT_CHECK query measure requires a reason")


@dataclass(frozen=True)
class RevisionMeasure:
    event_id: str
    trigger_support_ids: tuple[str, ...]
    expected_changed_ids: tuple[str, ...]
    observed_changed_ids: tuple[str, ...]
    touched_ids: tuple[str, ...]
    unrelated_probe_ids: tuple[str, ...]
    unrelated_changed_ids: tuple[str, ...]
    stale_survivor_ids: tuple[str, ...]
    collateral_invalidated_ids: tuple[str, ...]
    restoration_expected_ids: tuple[str, ...] = ()
    restoration_observed_ids: tuple[str, ...] = ()
    resources: ResourceVector = field(default_factory=ResourceVector)
    status: CheckStatus = CheckStatus.MEASURED
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        fields = (
            self.expected_changed_ids,
            self.observed_changed_ids,
            self.touched_ids,
            self.unrelated_probe_ids,
            self.unrelated_changed_ids,
            self.stale_survivor_ids,
            self.collateral_invalidated_ids,
        )
        if any(len(set(xs)) != len(xs) for xs in fields):
            raise ValueError("revision identity lists must be unique")
        if self.status is CheckStatus.CANNOT_CHECK and not self.cannot_check_reason:
            raise ValueError("CANNOT_CHECK revision measure requires a reason")

    @property
    def dependency_precision(self) -> float:
        expected, observed = set(self.expected_changed_ids), set(self.observed_changed_ids)
        if not observed:
            return 1.0 if not expected else 0.0
        return len(expected & observed) / len(observed)

    @property
    def dependency_recall(self) -> float:
        expected, observed = set(self.expected_changed_ids), set(self.observed_changed_ids)
        if not expected:
            return 1.0
        return len(expected & observed) / len(expected)

    @property
    def unrelated_retention(self) -> float:
        probes, changed = set(self.unrelated_probe_ids), set(self.unrelated_changed_ids)
        if not probes:
            return 1.0
        return 1.0 - len(probes & changed) / len(probes)

    def affected_fraction(self, state: StateMeasure) -> float | None:
        if self.status is not CheckStatus.MEASURED or state.status is not CheckStatus.MEASURED:
            return None
        if state.logical_n == 0:
            return 0.0
        return len(self.observed_changed_ids) / state.logical_n

    @property
    def exact_revocation(self) -> bool:
        return (
            set(self.expected_changed_ids) == set(self.observed_changed_ids)
            and not self.stale_survivor_ids
            and not self.collateral_invalidated_ids
            and not self.unrelated_changed_ids
        )

    @property
    def exact_restoration(self) -> bool:
        return set(self.restoration_expected_ids) == set(self.restoration_observed_ids)


@dataclass(frozen=True)
class ComparatorManifest:
    comparator_id: str
    persistent_memory: bool
    retrieval_index: bool
    post_deployment_adaptation: bool
    reusable_skill_library: bool
    dependency_truth_maintenance: bool
    exact_revocation: bool
    same_information: bool
    same_tools: bool
    same_verifiers: bool
    full_resource_accounting: bool
    role: MatchStatus = MatchStatus.MATCHED
    notes: tuple[str, ...] = ()

    def missing_for(self, requirements: Iterable[str]) -> tuple[str, ...]:
        missing = []
        for name in requirements:
            if not hasattr(self, name):
                raise ValueError(f"unknown comparator requirement: {name}")
            if not bool(getattr(self, name)):
                missing.append(name)
        return tuple(missing)

    def match_for(self, requirements: Iterable[str]) -> tuple[MatchStatus, tuple[str, ...]]:
        missing = self.missing_for(requirements)
        parity = self.same_information and self.same_tools and self.same_verifiers and self.full_resource_accounting
        if self.role is MatchStatus.REFERENCE:
            return MatchStatus.REFERENCE, missing
        if missing or not parity:
            parity_missing = []
            if not self.same_information:
                parity_missing.append("same_information")
            if not self.same_tools:
                parity_missing.append("same_tools")
            if not self.same_verifiers:
                parity_missing.append("same_verifiers")
            if not self.full_resource_accounting:
                parity_missing.append("full_resource_accounting")
            return MatchStatus.CANNOT_CHECK, tuple((*missing, *parity_missing))
        return MatchStatus.MATCHED, ()


@dataclass(frozen=True)
class LifetimeReceipt:
    receipt_id: str
    arm_id: str
    task_id: str
    state: StateMeasure
    acquisition: AcquisitionMeasure | None = None
    query: QueryMeasure | None = None
    revision: RevisionMeasure | None = None
    comparator: ComparatorManifest | None = None
    protected_outcome: Mapping[str, Any] = field(default_factory=dict)
    integrity_gates: Mapping[str, bool] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        def conv(value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            if hasattr(value, "__dataclass_fields__"):
                return {k: conv(v) for k, v in asdict(value).items()}
            if isinstance(value, Mapping):
                return {str(k): conv(v) for k, v in value.items()}
            if isinstance(value, (tuple, list)):
                return [conv(v) for v in value]
            return value

        return conv(self)


def kso_state_measure(ks: Any, *, object_grammar: str = "KnowledgeSpace.v1") -> StateMeasure:
    """Adapter for the current KSO without inventing deep memory bytes.

    Only identity-bearing atom/hyperedge counts enter N. The current
    ``warrant_size`` aggregate is reported as auxiliary cardinality because the
    runtime does not yet expose one touchable identity per warrant entry.
    """
    counts = dict(ks.resource_counts())
    object_counts = {
        "atoms": int(counts.get("object_count", 0)),
        "hyperedges": int(counts.get("relation_count", 0)),
    }
    auxiliary_counts = {"warrant_entries": int(counts.get("warrant_size", 0))}
    index_entries = index_bytes = 0
    if hasattr(ks, "index_resources"):
        rv = ks.index_resources()
        index_entries = int(getattr(rv, "index_size", 0))
        index_bytes = int(getattr(rv, "memory_bytes", 0))
    return StateMeasure(
        object_counts=object_counts,
        auxiliary_counts=auxiliary_counts,
        bytes_by_class={},
        index_entries=index_entries,
        index_bytes=index_bytes,
        object_grammar=object_grammar,
    )


def cannot_check_touch(reason: str, *, global_scan_items: int = 0) -> TouchMeasure:
    return TouchMeasure((), {}, 0, global_scan_items, CheckStatus.CANNOT_CHECK, reason)
