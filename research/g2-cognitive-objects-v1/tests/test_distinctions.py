"""G2.1 axes stay distinct; collapsing them is refused."""
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from g2_cognitive_objects.canonical import SchemaError
from g2_cognitive_objects.fixture import AUTH, CORRECT, LINEAGE, USEFUL
from g2_cognitive_objects.types import (
    CheckStatus,
    CurrentAuthorizationState,
    G24Lifecycle,
    Liveness,
    MethodRecordV1,
    ResourceVector,
    ReuseEventV1,
    UsefulnessEvidence,
)


def test_resource_vector_rejects_negative():
    with pytest.raises(SchemaError):
        ResourceVector(wall_seconds=-1)


def test_live_serving_requires_live_proof_and_applicability():
    with pytest.raises(SchemaError):
        CurrentAuthorizationState(
            admitted=True,
            proof_liveness=Liveness.LIVE,
            applicability_liveness=Liveness.DEAD,
            serving_liveness=Liveness.LIVE,
            status=CheckStatus.MEASURED,
        )


def test_dead_applicability_can_block_a_correct_method():
    state = CurrentAuthorizationState(
        admitted=True,
        proof_liveness=Liveness.LIVE,
        applicability_liveness=Liveness.DEAD,
        serving_liveness=Liveness.DEAD,
        status=CheckStatus.MEASURED,
    )
    assert state.proof_liveness is Liveness.LIVE
    assert state.serving_liveness is Liveness.DEAD


def test_usefulness_cannot_be_claimed_without_invocation_witness():
    with pytest.raises(SchemaError):
        UsefulnessEvidence(effect_observed=True, invocation_witness_id="UNKNOWN", status=CheckStatus.MEASURED)


def test_g24_complete_refused_when_gates_missing():
    with pytest.raises(SchemaError):
        G24Lifecycle(complete=True, actually_invoked=True, execution_trace_identifies_object=True)


def test_reuse_invocation_requires_witness():
    with pytest.raises(SchemaError):
        ReuseEventV1(
            event_id="e",
            method_ids=("m",),
            task_id="t",
            source_schema="ocm.unary-method.use.v1",
            invocation_witness_id="UNKNOWN",
            resources=ResourceVector(),
            correctness=CORRECT,
            usefulness=USEFUL,
            authorization=AUTH,
            g24=G24Lifecycle(actually_invoked=True, execution_trace_identifies_object=True),
        )


def test_method_record_keeps_four_objects():
    record = MethodRecordV1(
        method_id="m",
        payload_sha256="p",
        method_schema_id="s",
        source_schema="ocm.unary-method.data.v1",
        acquisition_lineage=LINEAGE,
        correctness=CORRECT,
        usefulness=USEFUL,
        authorization=AUTH,
    )
    assert record.correctness is not record.usefulness
    assert record.authorization is not record.correctness
    assert record.acquisition_lineage is not record.usefulness
    assert record.usefulness.status is CheckStatus.CANNOT_CHECK
    assert record.correctness.status is CheckStatus.MEASURED
