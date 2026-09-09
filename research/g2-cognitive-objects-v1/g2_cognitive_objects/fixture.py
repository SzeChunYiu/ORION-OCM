"""Frozen transport fixture. Not causal-reuse evidence."""
from .types import (
    UNKNOWN,
    AcquisitionLineage,
    CheckStatus,
    CognitiveEpisodeV1,
    CorrectnessEvidence,
    CurrentAuthorizationState,
    EpisodeFixtureV1,
    FailureAttemptV1,
    FailureKind,
    G24Lifecycle,
    InformationVector,
    Liveness,
    MethodRecordV1,
    MethodSchemaV1,
    OriginCategory,
    PrimitiveAlias,
    RepresentationChangeV1,
    ResourceVector,
    ReuseEventV1,
    ScopeState,
    ScopeTransferV1,
    TransferOutcome,
    UsefulnessEvidence,
    Verdict,
)

SCOPE = ScopeState(contexts=("g2.fixture.v1",), epoch_start=0.0, epoch_end=None)

LINEAGE = AcquisitionLineage(
    origin_category=OriginCategory.TAUGHT_IMPORTED,
    episode_ids=("g2.fixture.episode.1",),
    donor_ids=(),
    prior_information_ids=("g2.fixture.prior.authored-cover",),
    source_sha256="UNKNOWN",
    training_task_ids=("g2.fixture.task.cover",),
    information=InformationVector(examples=2, explicit_lessons=1),
    resources=ResourceVector(verifier_calls=1, notes=("fixture partial vector",)),
    discovery_evidence_id="g2.fixture.discovery.1",
    status=CheckStatus.MEASURED,
)

CORRECT = CorrectnessEvidence(
    checker_id="g2.fixture.checker.universal-cover",
    proof_evidence_id="g2.fixture.proof.1",
    certificate_sha256="0" * 64,
    verdict=Verdict.PASS,
    independent_of_usefulness=True,
    status=CheckStatus.MEASURED,
)

USEFUL = UsefulnessEvidence(
    independent_of_correctness=True,
    status=CheckStatus.CANNOT_CHECK,
    cannot_check_reason="fixture is schema transport; later-task causal benefit is not established",
)

AUTH = CurrentAuthorizationState(
    admitted=True,
    proof_liveness=Liveness.LIVE,
    applicability_liveness=Liveness.LIVE,
    serving_liveness=Liveness.LIVE,
    warrant_ids=("g2.fixture.proof.1", "g2.fixture.utility.1"),
    scope=SCOPE,
    status=CheckStatus.MEASURED,
)


def frozen_episode() -> CognitiveEpisodeV1:
    return CognitiveEpisodeV1(
        episode_id="g2.fixture.episode.1",
        task_id="g2.fixture.task.cover",
        grammar="unary-cover.v1",
        outcome="VERIFIED_UNIVERSAL_COVER",
        trace_id="g2.fixture.trace.1",
        resources=ResourceVector(verifier_calls=1, work_units=8, notes=("fixture partial vector",)),
        information=InformationVector(examples=2, explicit_lessons=1),
        acquisition_lineage=LINEAGE,
        correctness=CORRECT,
        usefulness=USEFUL,
        authorization=AUTH,
        emitted_method_ids=("unary:method:g2.fixture.rule",),
        notes=("SCHEMA_TRANSPORT_ONLY", "not a G2.4 receipt"),
    )


def frozen_fixture() -> EpisodeFixtureV1:
    episode = frozen_episode()
    record = MethodRecordV1(
        method_id="unary:method:g2.fixture.rule",
        payload_sha256="1" * 64,
        method_schema_id="g2.fixture.schema.cover",
        source_schema="ocm.unary-method.data.v1",
        acquisition_lineage=LINEAGE,
        correctness=CORRECT,
        usefulness=USEFUL,
        authorization=AUTH,
        notes=("axes remain distinct: proof vs authored selection vs current liveness vs later usefulness",),
    )
    schema = MethodSchemaV1(
        method_schema_id="g2.fixture.schema.cover",
        pattern="universal-cover.v1 two-premise chain",
        originating_method_ids=("unary:method:g2.fixture.rule",),
        acquisition_lineage=LINEAGE,
        correctness=CORRECT,
        usefulness=USEFUL,
        authorization=AUTH,
        notes=("schema identity is not usefulness",),
    )
    reuse = ReuseEventV1(
        event_id="g2.fixture.reuse.1",
        method_ids=("unary:method:g2.fixture.rule",),
        task_id="g2.fixture.task.fresh",
        source_schema="ocm.unary-method.use.v1",
        invocation_witness_id="g2.fixture.packet.sha256",
        resources=ResourceVector(wall_seconds=0.01, notes=("fixture wall only",)),
        correctness=CORRECT,
        usefulness=USEFUL,
        authorization=AUTH,
        g24=G24Lifecycle(
            actually_invoked=True,
            execution_trace_identifies_object=True,
            complete=False,
            status=CheckStatus.CANNOT_CHECK,
            cannot_check_reason="fixture omits restart, fresh-task disjointness, ablation, and material effect",
        ),
        notes=("invocation witness is not G2.4 completeness",),
    )
    failure = FailureAttemptV1(
        attempt_id="g2.fixture.fail.1",
        method_id="unary:method:g2.fixture.rule",
        task_id="g2.fixture.task.mismatch",
        scope=SCOPE,
        budget="max_decisions=8",
        environment_version="g2.fixture.env",
        outcome="USE_REFUSED",
        feedback="METHOD_NOT_ELIGIBLE",
        failure_kind=FailureKind.AUTHORITY_REFUSAL,
        resources=ResourceVector(),
        acquisition_lineage=LINEAGE,
        correctness=CORRECT,
        usefulness=USEFUL,
        authorization=CurrentAuthorizationState(
            admitted=True,
            proof_liveness=Liveness.LIVE,
            applicability_liveness=Liveness.DEAD,
            serving_liveness=Liveness.DEAD,
            warrant_ids=("g2.fixture.proof.1",),
            scope=SCOPE,
            status=CheckStatus.MEASURED,
        ),
        notes=("DEAD applicability with LIVE proof: authority is not correctness",),
    )
    transfer = ScopeTransferV1(
        transfer_id="g2.fixture.transfer.1",
        method_id="unary:method:g2.fixture.rule",
        source_scope=SCOPE,
        target_scope=ScopeState(contexts=("other-domain.v1",)),
        correspondence_witness_id=UNKNOWN,
        outcome=TransferOutcome.UNKNOWN,
        acquisition_lineage=AcquisitionLineage(
            status=CheckStatus.CANNOT_CHECK,
            cannot_check_reason="no existing scope-transfer correspondence witness in repo receipts",
        ),
        correctness=CorrectnessEvidence(status=CheckStatus.UNKNOWN),
        usefulness=USEFUL,
        authorization=CurrentAuthorizationState(status=CheckStatus.UNKNOWN),
        notes=("ScopeTransferV1 is defined; repo sources remain UNKNOWN",),
    )
    change = RepresentationChangeV1(
        change_id="g2.fixture.repr.1",
        before_representation_id="primitive:minus",
        after_representation_id="fn_0",
        trigger="library-learning alias screen",
        primitive_alias=PrimitiveAlias.PRIMITIVE_ALIAS,
        lifecycle_equivalence=CheckStatus.UNKNOWN,
        acquisition_lineage=AcquisitionLineage(
            origin_category=OriginCategory.TAUGHT_IMPORTED,
            donor_ids=("stitch",),
            status=CheckStatus.MEASURED,
        ),
        correctness=CORRECT,
        usefulness=USEFUL,
        authorization=CurrentAuthorizationState(
            admitted=False,
            proof_liveness=Liveness.LIVE,
            applicability_liveness=Liveness.DEAD,
            serving_liveness=Liveness.DEAD,
            scope=SCOPE,
            status=CheckStatus.MEASURED,
        ),
        notes=("PRIMITIVE_ALIAS is not a useful new operator",),
    )
    return EpisodeFixtureV1(
        fixture_id="g2.fixture.episode-document.1",
        episode=episode,
        method_record=record,
        method_schema=schema,
        reuse_event=reuse,
        failure_attempt=failure,
        scope_transfer=transfer,
        representation_change=change,
    )
