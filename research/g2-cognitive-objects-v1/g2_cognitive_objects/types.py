"""G2.1 cognitive-object dataclasses. Axes stay distinct."""
from __future__ import annotations

from dataclasses import dataclass, field, fields as dc_fields
from enum import Enum
from typing import Any, TypeVar

from .canonical import SchemaError, dumps
from .schema import validate_named

T = TypeVar("T")
UNKNOWN = "UNKNOWN"


class CheckStatus(str, Enum):
    MEASURED = "MEASURED"
    UNKNOWN = "UNKNOWN"
    CANNOT_CHECK = "CANNOT_CHECK"


class Liveness(str, Enum):
    LIVE = "LIVE"
    DEAD = "DEAD"
    UNKNOWN = "UNKNOWN"


class OriginCategory(str, Enum):
    TAUGHT_IMPORTED = "TAUGHT_IMPORTED"
    LEARNED_APPLICABILITY = "LEARNED_APPLICABILITY"
    LEARNED_COMPOSITION = "LEARNED_COMPOSITION"
    INDEPENDENT_REDISCOVERY = "INDEPENDENT_REDISCOVERY"
    UNKNOWN = "UNKNOWN"


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    CANNOT_CHECK = "CANNOT_CHECK"


class FailureKind(str, Enum):
    METHOD_FAILURE = "METHOD_FAILURE"
    TASK_IMPOSSIBILITY = "TASK_IMPOSSIBILITY"
    AUTHORITY_REFUSAL = "AUTHORITY_REFUSAL"
    UNKNOWN = "UNKNOWN"


class TransferOutcome(str, Enum):
    TRANSFERRED = "TRANSFERRED"
    REFUSED = "REFUSED"
    HARMFUL = "HARMFUL"
    UNKNOWN = "UNKNOWN"
    CANNOT_CHECK = "CANNOT_CHECK"


class PrimitiveAlias(str, Enum):
    PRIMITIVE_ALIAS = "PRIMITIVE_ALIAS"
    NO_NEW_ABSTRACTION = "NO_NEW_ABSTRACTION"
    NOT_ASSESSED = "NOT_ASSESSED"
    UNKNOWN = "UNKNOWN"


def _unique(items: tuple[str, ...], label: str) -> None:
    if len(set(items)) != len(items):
        raise SchemaError(f"{label} must be unique")


def _reason_ok(status: CheckStatus, reason: str | None, label: str) -> None:
    if status is CheckStatus.CANNOT_CHECK and not reason:
        raise SchemaError(f"{label} CANNOT_CHECK requires a reason")
    if status is not CheckStatus.CANNOT_CHECK and reason is not None:
        raise SchemaError(f"{label} reason only allowed for CANNOT_CHECK")


def _enum(cls: type[Enum], value: Any) -> Enum:
    if isinstance(value, cls):
        return value
    return cls(value)


@dataclass(frozen=True)
class ResourceVector:
    """ADOPT ME lifetime resource vector; coordinates are not collapsed."""

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
        for item in dc_fields(self):
            if item.name == "notes":
                continue
            if getattr(self, item.name) < 0:
                raise SchemaError("resource coordinates must be non-negative")


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
        if any(getattr(self, item.name) < 0 for item in dc_fields(self)):
            raise SchemaError("information coordinates must be non-negative")


@dataclass(frozen=True)
class ScopeState:
    contexts: tuple[str, ...] | None = None
    epoch_start: float = 0.0
    epoch_end: float | None = None

    def __post_init__(self) -> None:
        if self.contexts is not None:
            _unique(self.contexts, "scope contexts")


@dataclass(frozen=True)
class AuthorityRank:
    coordinate: str
    rank: int

    def __post_init__(self) -> None:
        if not self.coordinate or self.rank < 0:
            raise SchemaError("invalid authority rank")


@dataclass(frozen=True)
class AcquisitionLineage:
    origin_category: OriginCategory = OriginCategory.UNKNOWN
    episode_ids: tuple[str, ...] = ()
    donor_ids: tuple[str, ...] = ()
    prior_information_ids: tuple[str, ...] = ()
    source_sha256: str = UNKNOWN
    training_task_ids: tuple[str, ...] = ()
    information: InformationVector = field(default_factory=InformationVector)
    resources: ResourceVector = field(default_factory=ResourceVector)
    discovery_evidence_id: str = UNKNOWN
    status: CheckStatus = CheckStatus.UNKNOWN
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin_category", _enum(OriginCategory, self.origin_category))
        object.__setattr__(self, "status", _enum(CheckStatus, self.status))
        _unique(self.episode_ids, "episode_ids")
        _unique(self.donor_ids, "donor_ids")
        _unique(self.prior_information_ids, "prior_information_ids")
        _unique(self.training_task_ids, "training_task_ids")
        _reason_ok(self.status, self.cannot_check_reason, "acquisition_lineage")


@dataclass(frozen=True)
class CorrectnessEvidence:
    checker_id: str = UNKNOWN
    proof_evidence_id: str = UNKNOWN
    certificate_sha256: str = UNKNOWN
    verdict: Verdict = Verdict.UNKNOWN
    counterexample: dict[str, Any] | None = None
    independent_of_usefulness: bool = True
    status: CheckStatus = CheckStatus.UNKNOWN
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "verdict", _enum(Verdict, self.verdict))
        object.__setattr__(self, "status", _enum(CheckStatus, self.status))
        if self.independent_of_usefulness is not True:
            raise SchemaError("correctness must remain independent of usefulness")
        _reason_ok(self.status, self.cannot_check_reason, "correctness")


@dataclass(frozen=True)
class UsefulnessEvidence:
    fresh_task_id: str = UNKNOWN
    effect_coordinate: str = UNKNOWN
    effect_observed: bool | None = None
    invocation_witness_id: str = UNKNOWN
    ablation_witness_id: str = UNKNOWN
    restart_witness_id: str = UNKNOWN
    independent_of_correctness: bool = True
    status: CheckStatus = CheckStatus.UNKNOWN
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", _enum(CheckStatus, self.status))
        if self.independent_of_correctness is not True:
            raise SchemaError("usefulness must remain independent of correctness")
        if self.effect_observed is True and self.invocation_witness_id == UNKNOWN:
            raise SchemaError("observed usefulness requires an invocation witness")
        if self.status is CheckStatus.MEASURED and self.effect_observed is None:
            raise SchemaError("MEASURED usefulness requires effect_observed")
        _reason_ok(self.status, self.cannot_check_reason, "usefulness")


@dataclass(frozen=True)
class CurrentAuthorizationState:
    admitted: bool | None = None
    proof_liveness: Liveness = Liveness.UNKNOWN
    applicability_liveness: Liveness = Liveness.UNKNOWN
    serving_liveness: Liveness = Liveness.UNKNOWN
    revoked_support_ids: tuple[str, ...] = ()
    warrant_ids: tuple[str, ...] = ()
    scope: ScopeState = field(default_factory=ScopeState)
    authority_ranks: tuple[AuthorityRank, ...] = ()
    status: CheckStatus = CheckStatus.UNKNOWN
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "proof_liveness", _enum(Liveness, self.proof_liveness))
        object.__setattr__(self, "applicability_liveness", _enum(Liveness, self.applicability_liveness))
        object.__setattr__(self, "serving_liveness", _enum(Liveness, self.serving_liveness))
        object.__setattr__(self, "status", _enum(CheckStatus, self.status))
        _unique(self.revoked_support_ids, "revoked_support_ids")
        _unique(self.warrant_ids, "warrant_ids")
        if self.serving_liveness is Liveness.LIVE:
            if self.admitted is not True:
                raise SchemaError("LIVE serving requires admitted=true")
            if self.proof_liveness is not Liveness.LIVE or self.applicability_liveness is not Liveness.LIVE:
                raise SchemaError("LIVE serving requires LIVE proof and applicability")
        if self.proof_liveness is Liveness.DEAD or self.applicability_liveness is Liveness.DEAD:
            if self.serving_liveness is Liveness.LIVE:
                raise SchemaError("DEAD warrant cannot yield LIVE serving")
        _reason_ok(self.status, self.cannot_check_reason, "authorization")


def _g24_complete(
    admitted_before_fresh_task: bool | None,
    process_restarted: bool | None,
    fresh_task_disjoint_from_acquisition: bool | None,
    actually_invoked: bool | None,
    execution_trace_identifies_object: bool | None,
    material_effect: CheckStatus,
    removal_ablation: CheckStatus,
    answer_cache_excluded: CheckStatus,
    retrieval_only_excluded: CheckStatus,
) -> bool:
    flags = (
        admitted_before_fresh_task,
        process_restarted,
        fresh_task_disjoint_from_acquisition,
        actually_invoked,
        execution_trace_identifies_object,
    )
    statuses = (material_effect, removal_ablation, answer_cache_excluded, retrieval_only_excluded)
    return all(flag is True for flag in flags) and all(status is CheckStatus.MEASURED for status in statuses)


@dataclass(frozen=True)
class G24Lifecycle:
    admitted_before_fresh_task: bool | None = None
    process_restarted: bool | None = None
    fresh_task_disjoint_from_acquisition: bool | None = None
    actually_invoked: bool | None = None
    execution_trace_identifies_object: bool | None = None
    material_effect: CheckStatus = CheckStatus.UNKNOWN
    removal_ablation: CheckStatus = CheckStatus.UNKNOWN
    answer_cache_excluded: CheckStatus = CheckStatus.UNKNOWN
    retrieval_only_excluded: CheckStatus = CheckStatus.UNKNOWN
    complete: bool = False
    status: CheckStatus = CheckStatus.UNKNOWN
    cannot_check_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "material_effect", _enum(CheckStatus, self.material_effect))
        object.__setattr__(self, "removal_ablation", _enum(CheckStatus, self.removal_ablation))
        object.__setattr__(self, "answer_cache_excluded", _enum(CheckStatus, self.answer_cache_excluded))
        object.__setattr__(self, "retrieval_only_excluded", _enum(CheckStatus, self.retrieval_only_excluded))
        object.__setattr__(self, "status", _enum(CheckStatus, self.status))
        expected = _g24_complete(
            self.admitted_before_fresh_task,
            self.process_restarted,
            self.fresh_task_disjoint_from_acquisition,
            self.actually_invoked,
            self.execution_trace_identifies_object,
            self.material_effect,
            self.removal_ablation,
            self.answer_cache_excluded,
            self.retrieval_only_excluded,
        )
        if self.complete and not expected:
            raise SchemaError("G2.4 complete requires every lifecycle gate MEASURED and satisfied")
        if self.actually_invoked is True and self.execution_trace_identifies_object is not True:
            raise SchemaError("actual invocation requires an identifying execution trace")
        _reason_ok(self.status, self.cannot_check_reason, "g24")


def unknown_usefulness(*, reason: str | None = None, status: CheckStatus = CheckStatus.UNKNOWN) -> UsefulnessEvidence:
    return UsefulnessEvidence(status=status, cannot_check_reason=reason)


def unknown_correctness(*, reason: str | None = None, status: CheckStatus = CheckStatus.UNKNOWN) -> CorrectnessEvidence:
    return CorrectnessEvidence(status=status, cannot_check_reason=reason)


def unknown_lineage(*, reason: str | None = None, status: CheckStatus = CheckStatus.UNKNOWN) -> AcquisitionLineage:
    return AcquisitionLineage(status=status, cannot_check_reason=reason)


def unknown_authorization(*, reason: str | None = None, status: CheckStatus = CheckStatus.UNKNOWN) -> CurrentAuthorizationState:
    return CurrentAuthorizationState(status=status, cannot_check_reason=reason)


@dataclass(frozen=True)
class CognitiveEpisodeV1:
    episode_id: str
    task_id: str
    grammar: str
    outcome: str
    trace_id: str
    resources: ResourceVector
    information: InformationVector
    acquisition_lineage: AcquisitionLineage
    correctness: CorrectnessEvidence
    usefulness: UsefulnessEvidence
    authorization: CurrentAuthorizationState
    emitted_method_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    schema: str = "ocm.g2.cognitive-episode.v1"

    def __post_init__(self) -> None:
        if self.schema != "ocm.g2.cognitive-episode.v1":
            raise SchemaError("CognitiveEpisodeV1 schema")
        _unique(self.emitted_method_ids, "emitted_method_ids")
        _four_axes(self)


@dataclass(frozen=True)
class MethodRecordV1:
    method_id: str
    payload_sha256: str
    method_schema_id: str
    source_schema: str
    acquisition_lineage: AcquisitionLineage
    correctness: CorrectnessEvidence
    usefulness: UsefulnessEvidence
    authorization: CurrentAuthorizationState
    notes: tuple[str, ...] = ()
    schema: str = "ocm.g2.method-record.v1"

    def __post_init__(self) -> None:
        if self.schema != "ocm.g2.method-record.v1":
            raise SchemaError("MethodRecordV1 schema")
        _four_axes(self)


@dataclass(frozen=True)
class MethodSchemaV1:
    method_schema_id: str
    pattern: str
    originating_method_ids: tuple[str, ...]
    acquisition_lineage: AcquisitionLineage
    correctness: CorrectnessEvidence
    usefulness: UsefulnessEvidence
    authorization: CurrentAuthorizationState
    notes: tuple[str, ...] = ()
    schema: str = "ocm.g2.method-schema.v1"

    def __post_init__(self) -> None:
        if self.schema != "ocm.g2.method-schema.v1":
            raise SchemaError("MethodSchemaV1 schema")
        _unique(self.originating_method_ids, "originating_method_ids")
        _four_axes(self)


@dataclass(frozen=True)
class ReuseEventV1:
    event_id: str
    method_ids: tuple[str, ...]
    task_id: str
    source_schema: str
    invocation_witness_id: str
    resources: ResourceVector
    correctness: CorrectnessEvidence
    usefulness: UsefulnessEvidence
    authorization: CurrentAuthorizationState
    g24: G24Lifecycle
    notes: tuple[str, ...] = ()
    schema: str = "ocm.g2.reuse-event.v1"

    def __post_init__(self) -> None:
        if self.schema != "ocm.g2.reuse-event.v1":
            raise SchemaError("ReuseEventV1 schema")
        if not self.method_ids:
            raise SchemaError("ReuseEventV1 requires method_ids")
        _unique(self.method_ids, "method_ids")
        if self.g24.actually_invoked is True and self.invocation_witness_id == UNKNOWN:
            raise SchemaError("invoked reuse requires invocation_witness_id")
        _four_axes(self)


@dataclass(frozen=True)
class FailureAttemptV1:
    attempt_id: str
    method_id: str
    task_id: str
    scope: ScopeState
    budget: str
    environment_version: str
    outcome: str
    feedback: str
    failure_kind: FailureKind
    resources: ResourceVector
    acquisition_lineage: AcquisitionLineage
    correctness: CorrectnessEvidence
    usefulness: UsefulnessEvidence
    authorization: CurrentAuthorizationState
    notes: tuple[str, ...] = ()
    schema: str = "ocm.g2.failure-attempt.v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "failure_kind", _enum(FailureKind, self.failure_kind))
        if self.schema != "ocm.g2.failure-attempt.v1":
            raise SchemaError("FailureAttemptV1 schema")
        _four_axes(self)


@dataclass(frozen=True)
class ScopeTransferV1:
    transfer_id: str
    method_id: str
    source_scope: ScopeState
    target_scope: ScopeState
    correspondence_witness_id: str
    outcome: TransferOutcome
    acquisition_lineage: AcquisitionLineage
    correctness: CorrectnessEvidence
    usefulness: UsefulnessEvidence
    authorization: CurrentAuthorizationState
    notes: tuple[str, ...] = ()
    schema: str = "ocm.g2.scope-transfer.v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcome", _enum(TransferOutcome, self.outcome))
        if self.schema != "ocm.g2.scope-transfer.v1":
            raise SchemaError("ScopeTransferV1 schema")
        if self.outcome is TransferOutcome.TRANSFERRED and self.correspondence_witness_id == UNKNOWN:
            raise SchemaError("transferred scope requires a correspondence witness")
        _four_axes(self)


@dataclass(frozen=True)
class RepresentationChangeV1:
    change_id: str
    before_representation_id: str
    after_representation_id: str
    trigger: str
    primitive_alias: PrimitiveAlias
    lifecycle_equivalence: CheckStatus
    acquisition_lineage: AcquisitionLineage
    correctness: CorrectnessEvidence
    usefulness: UsefulnessEvidence
    authorization: CurrentAuthorizationState
    notes: tuple[str, ...] = ()
    schema: str = "ocm.g2.representation-change.v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "primitive_alias", _enum(PrimitiveAlias, self.primitive_alias))
        object.__setattr__(self, "lifecycle_equivalence", _enum(CheckStatus, self.lifecycle_equivalence))
        if self.schema != "ocm.g2.representation-change.v1":
            raise SchemaError("RepresentationChangeV1 schema")
        _four_axes(self)


@dataclass(frozen=True)
class EpisodeFixtureV1:
    fixture_id: str
    episode: CognitiveEpisodeV1
    method_record: MethodRecordV1
    method_schema: MethodSchemaV1
    reuse_event: ReuseEventV1
    failure_attempt: FailureAttemptV1
    scope_transfer: ScopeTransferV1
    representation_change: RepresentationChangeV1
    claim_authority: str = "SCHEMA_TRANSPORT_ONLY"
    schema: str = "ocm.g2.episode-fixture.v1"

    def __post_init__(self) -> None:
        if self.schema != "ocm.g2.episode-fixture.v1":
            raise SchemaError("EpisodeFixtureV1 schema")
        if self.claim_authority != "SCHEMA_TRANSPORT_ONLY":
            raise SchemaError("fixture has no scientific claim authority")


def _four_axes(obj: Any) -> None:
    axes = (obj.correctness, obj.usefulness, obj.authorization)
    if isinstance(obj, (CognitiveEpisodeV1, MethodRecordV1, MethodSchemaV1, FailureAttemptV1, ScopeTransferV1, RepresentationChangeV1)):
        axes = (obj.correctness, obj.usefulness, obj.authorization)
        if obj.acquisition_lineage is obj.correctness:  # pragma: no cover - identity guard
            raise SchemaError("acquisition lineage collapsed into correctness")
    identities = [id(obj.correctness), id(obj.usefulness), id(obj.authorization)]
    if hasattr(obj, "acquisition_lineage"):
        identities.append(id(obj.acquisition_lineage))
    if len(set(identities)) != len(identities):
        raise SchemaError("G2.1 axes must be distinct objects")


def to_plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [to_plain(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        out = {}
        for item in dc_fields(value):
            out[item.name] = to_plain(getattr(value, item.name))
        return out
    return value


def from_plain(cls: type[T], data: dict[str, Any]) -> T:
    if cls is ResourceVector:
        return ResourceVector(**{**data, "notes": tuple(data.get("notes", ()))})  # type: ignore[return-value]
    if cls is InformationVector:
        return InformationVector(**data)  # type: ignore[return-value]
    if cls is ScopeState:
        contexts = data["contexts"]
        return ScopeState(None if contexts is None else tuple(contexts), data["epoch_start"], data["epoch_end"])  # type: ignore[return-value]
    if cls is AuthorityRank:
        return AuthorityRank(**data)  # type: ignore[return-value]
    if cls is AcquisitionLineage:
        return AcquisitionLineage(
            origin_category=data["origin_category"],
            episode_ids=tuple(data["episode_ids"]),
            donor_ids=tuple(data["donor_ids"]),
            prior_information_ids=tuple(data["prior_information_ids"]),
            source_sha256=data["source_sha256"],
            training_task_ids=tuple(data["training_task_ids"]),
            information=from_plain(InformationVector, data["information"]),
            resources=from_plain(ResourceVector, data["resources"]),
            discovery_evidence_id=data["discovery_evidence_id"],
            status=data["status"],
            cannot_check_reason=data["cannot_check_reason"],
        )  # type: ignore[return-value]
    if cls is CorrectnessEvidence:
        return CorrectnessEvidence(**data)  # type: ignore[return-value]
    if cls is UsefulnessEvidence:
        return UsefulnessEvidence(**data)  # type: ignore[return-value]
    if cls is CurrentAuthorizationState:
        return CurrentAuthorizationState(
            admitted=data["admitted"],
            proof_liveness=data["proof_liveness"],
            applicability_liveness=data["applicability_liveness"],
            serving_liveness=data["serving_liveness"],
            revoked_support_ids=tuple(data["revoked_support_ids"]),
            warrant_ids=tuple(data["warrant_ids"]),
            scope=from_plain(ScopeState, data["scope"]),
            authority_ranks=tuple(AuthorityRank(**row) for row in data["authority_ranks"]),
            status=data["status"],
            cannot_check_reason=data["cannot_check_reason"],
        )  # type: ignore[return-value]
    if cls is G24Lifecycle:
        return G24Lifecycle(**data)  # type: ignore[return-value]
    if cls is CognitiveEpisodeV1:
        return CognitiveEpisodeV1(
            schema=data["schema"],
            episode_id=data["episode_id"],
            task_id=data["task_id"],
            grammar=data["grammar"],
            outcome=data["outcome"],
            trace_id=data["trace_id"],
            resources=from_plain(ResourceVector, data["resources"]),
            information=from_plain(InformationVector, data["information"]),
            acquisition_lineage=from_plain(AcquisitionLineage, data["acquisition_lineage"]),
            correctness=from_plain(CorrectnessEvidence, data["correctness"]),
            usefulness=from_plain(UsefulnessEvidence, data["usefulness"]),
            authorization=from_plain(CurrentAuthorizationState, data["authorization"]),
            emitted_method_ids=tuple(data["emitted_method_ids"]),
            notes=tuple(data["notes"]),
        )  # type: ignore[return-value]
    if cls is MethodRecordV1:
        return MethodRecordV1(
            schema=data["schema"],
            method_id=data["method_id"],
            payload_sha256=data["payload_sha256"],
            method_schema_id=data["method_schema_id"],
            source_schema=data["source_schema"],
            acquisition_lineage=from_plain(AcquisitionLineage, data["acquisition_lineage"]),
            correctness=from_plain(CorrectnessEvidence, data["correctness"]),
            usefulness=from_plain(UsefulnessEvidence, data["usefulness"]),
            authorization=from_plain(CurrentAuthorizationState, data["authorization"]),
            notes=tuple(data["notes"]),
        )  # type: ignore[return-value]
    if cls is MethodSchemaV1:
        return MethodSchemaV1(
            schema=data["schema"],
            method_schema_id=data["method_schema_id"],
            pattern=data["pattern"],
            originating_method_ids=tuple(data["originating_method_ids"]),
            acquisition_lineage=from_plain(AcquisitionLineage, data["acquisition_lineage"]),
            correctness=from_plain(CorrectnessEvidence, data["correctness"]),
            usefulness=from_plain(UsefulnessEvidence, data["usefulness"]),
            authorization=from_plain(CurrentAuthorizationState, data["authorization"]),
            notes=tuple(data["notes"]),
        )  # type: ignore[return-value]
    if cls is ReuseEventV1:
        return ReuseEventV1(
            schema=data["schema"],
            event_id=data["event_id"],
            method_ids=tuple(data["method_ids"]),
            task_id=data["task_id"],
            source_schema=data["source_schema"],
            invocation_witness_id=data["invocation_witness_id"],
            resources=from_plain(ResourceVector, data["resources"]),
            correctness=from_plain(CorrectnessEvidence, data["correctness"]),
            usefulness=from_plain(UsefulnessEvidence, data["usefulness"]),
            authorization=from_plain(CurrentAuthorizationState, data["authorization"]),
            g24=from_plain(G24Lifecycle, data["g24"]),
            notes=tuple(data["notes"]),
        )  # type: ignore[return-value]
    if cls is FailureAttemptV1:
        return FailureAttemptV1(
            schema=data["schema"],
            attempt_id=data["attempt_id"],
            method_id=data["method_id"],
            task_id=data["task_id"],
            scope=from_plain(ScopeState, data["scope"]),
            budget=data["budget"],
            environment_version=data["environment_version"],
            outcome=data["outcome"],
            feedback=data["feedback"],
            failure_kind=data["failure_kind"],
            resources=from_plain(ResourceVector, data["resources"]),
            acquisition_lineage=from_plain(AcquisitionLineage, data["acquisition_lineage"]),
            correctness=from_plain(CorrectnessEvidence, data["correctness"]),
            usefulness=from_plain(UsefulnessEvidence, data["usefulness"]),
            authorization=from_plain(CurrentAuthorizationState, data["authorization"]),
            notes=tuple(data["notes"]),
        )  # type: ignore[return-value]
    if cls is ScopeTransferV1:
        return ScopeTransferV1(
            schema=data["schema"],
            transfer_id=data["transfer_id"],
            method_id=data["method_id"],
            source_scope=from_plain(ScopeState, data["source_scope"]),
            target_scope=from_plain(ScopeState, data["target_scope"]),
            correspondence_witness_id=data["correspondence_witness_id"],
            outcome=data["outcome"],
            acquisition_lineage=from_plain(AcquisitionLineage, data["acquisition_lineage"]),
            correctness=from_plain(CorrectnessEvidence, data["correctness"]),
            usefulness=from_plain(UsefulnessEvidence, data["usefulness"]),
            authorization=from_plain(CurrentAuthorizationState, data["authorization"]),
            notes=tuple(data["notes"]),
        )  # type: ignore[return-value]
    if cls is RepresentationChangeV1:
        return RepresentationChangeV1(
            schema=data["schema"],
            change_id=data["change_id"],
            before_representation_id=data["before_representation_id"],
            after_representation_id=data["after_representation_id"],
            trigger=data["trigger"],
            primitive_alias=data["primitive_alias"],
            lifecycle_equivalence=data["lifecycle_equivalence"],
            acquisition_lineage=from_plain(AcquisitionLineage, data["acquisition_lineage"]),
            correctness=from_plain(CorrectnessEvidence, data["correctness"]),
            usefulness=from_plain(UsefulnessEvidence, data["usefulness"]),
            authorization=from_plain(CurrentAuthorizationState, data["authorization"]),
            notes=tuple(data["notes"]),
        )  # type: ignore[return-value]
    if cls is EpisodeFixtureV1:
        return EpisodeFixtureV1(
            schema=data["schema"],
            fixture_id=data["fixture_id"],
            claim_authority=data["claim_authority"],
            episode=from_plain(CognitiveEpisodeV1, data["episode"]),
            method_record=from_plain(MethodRecordV1, data["method_record"]),
            method_schema=from_plain(MethodSchemaV1, data["method_schema"]),
            reuse_event=from_plain(ReuseEventV1, data["reuse_event"]),
            failure_attempt=from_plain(FailureAttemptV1, data["failure_attempt"]),
            scope_transfer=from_plain(ScopeTransferV1, data["scope_transfer"]),
            representation_change=from_plain(RepresentationChangeV1, data["representation_change"]),
        )  # type: ignore[return-value]
    raise SchemaError(f"no loader for {cls}")


SCHEMA_FILES = {
    "ocm.g2.cognitive-episode.v1": "cognitive_episode_v1.json",
    "ocm.g2.method-record.v1": "method_record_v1.json",
    "ocm.g2.method-schema.v1": "method_schema_v1.json",
    "ocm.g2.reuse-event.v1": "reuse_event_v1.json",
    "ocm.g2.failure-attempt.v1": "failure_attempt_v1.json",
    "ocm.g2.scope-transfer.v1": "scope_transfer_v1.json",
    "ocm.g2.representation-change.v1": "representation_change_v1.json",
    "ocm.g2.episode-fixture.v1": "episode_fixture_v1.json",
}


def emit(obj: Any, *, schema_name: str | None = None) -> bytes:
    plain = to_plain(obj)
    name = schema_name or SCHEMA_FILES.get(plain.get("schema") if isinstance(plain, dict) else "", "")
    if name:
        validate_named(plain, name)
    return dumps(plain)


def parse(cls: type[T], data: bytes, *, schema_name: str | None = None) -> T:
    from .canonical import loads

    plain = loads(data)
    name = schema_name
    if name is None and isinstance(plain, dict):
        name = SCHEMA_FILES.get(plain.get("schema", ""), None)
    if name:
        validate_named(plain, name)
    return from_plain(cls, plain)
