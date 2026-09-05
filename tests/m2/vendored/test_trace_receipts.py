"""Ported from ORION tests/unit/engine/test_trace_receipts.py (commit adb97ec).

Operator vocabulary adapted (``SEARCH`` → ``QUERY``, ``FRAME`` → ``ADMIT``) and
mechanic ids follow ``MECHANIC_ID_BY_OPERATOR`` (``kso.query``, ``kso.admit``)
instead of ``SEARCH.v1`` / ``FRAME.v1``. Assertions are the source's.
"""

import pytest

from ocm.operators.receipt import MechanicReceipt, MechanicRunStatus
from ocm.runtime.trace import MECHANIC_ID_BY_OPERATOR, SolveTrace, TraceEvent
from ocm.runtime.transition import OCMOperator, Transition


def _receipt(**changes):
    values = {
        "receipt_id": "receipt:query",
        "mechanic_id": "kso.query",
        "status": MechanicRunStatus.PARTIAL,
        "action_ids": ("QUERY",),
        "handoff_values": (("changed_coordinates", "W.QUERIED"),),
        "residual_ids": ("coverage-open",),
        "failure_signature": ("query_incomplete",),
        "evidence_ids": ("e:1",),
        "evidence_bindings": (("e:1", "a" * 64),),
        "provenance_ids": ("certificate:1",),
    }
    values.update(changes)
    return MechanicReceipt(**values)


def _transition():
    return Transition(
        OCMOperator.QUERY,
        input_epoch=0,
        output_epoch=1,
        evidence_ids=("e:1",),
        residual_ids=("coverage-open",),
        scientific_authority_certificate_ids=("certificate:1",),
        changed_coordinates=("W.QUERIED",),
    )


def test_every_operator_has_a_kso_mechanic_id():
    assert set(MECHANIC_ID_BY_OPERATOR) == set(OCMOperator)
    assert MECHANIC_ID_BY_OPERATOR[OCMOperator.COMMIT_ACTION] == "kso.commit_action"
    assert len(set(MECHANIC_ID_BY_OPERATOR.values())) == len(OCMOperator)


@pytest.mark.parametrize(
    ("change", "message"),
    (
        ({"residual_ids": ("erased",)}, "residual mismatch"),
        (
            {
                "evidence_ids": ("e:2",),
                "evidence_bindings": (("e:2", "b" * 64),),
            },
            "evidence mismatch",
        ),
        ({"provenance_ids": ("certificate:other",)}, "provenance mismatch"),
        (
            {"handoff_values": (("changed_coordinates", "K.CLAIMS"),)},
            "handoff mismatch",
        ),
        ({"mechanic_id": "kso.admit"}, "receipt/mechanic mismatch"),
    ),
)
def test_trace_event_rejects_receipt_transition_substitution(change, message):
    with pytest.raises(ValueError, match=message):
        TraceEvent(
            OCMOperator.QUERY,
            1,
            "fixture",
            _transition(),
            _receipt(**change),
            "1" * 64,
            "2" * 64,
        )


def test_trace_event_rejects_backward_transition():
    transition = Transition(OCMOperator.QUERY, input_epoch=2, output_epoch=1)
    receipt = MechanicReceipt(
        "receipt:backward",
        "kso.query",
        MechanicRunStatus.SUCCEEDED,
        action_ids=("QUERY",),
        handoff_values=(("changed_coordinates", ""),),
    )
    with pytest.raises(ValueError, match="cannot move backward"):
        TraceEvent(
            OCMOperator.QUERY,
            1,
            "backward",
            transition,
            receipt,
            "1" * 64,
            "2" * 64,
        )


def _event(operator, input_epoch, output_epoch, receipt_id, pre, post):
    return TraceEvent(
        operator,
        output_epoch,
        operator.value.lower(),
        Transition(operator, input_epoch, output_epoch),
        MechanicReceipt(
            receipt_id,
            MECHANIC_ID_BY_OPERATOR[operator],
            MechanicRunStatus.SUCCEEDED,
            action_ids=(operator.value,),
            handoff_values=(("changed_coordinates", ""),),
        ),
        pre,
        post,
    )


def test_solve_trace_rejects_discontinuous_state_chain():
    first = _event(OCMOperator.ADMIT, 0, 1, "receipt:admit", "a" * 64, "b" * 64)
    second = _event(OCMOperator.QUERY, 7, 8, "receipt:query-2", "c" * 64, "d" * 64)
    with pytest.raises(ValueError, match="state-hash chain"):
        SolveTrace("trace:broken", (first, second))


def test_solve_trace_rejects_discontinuous_epoch_chain_and_binds_endpoints():
    first = _event(OCMOperator.ADMIT, 0, 1, "receipt:admit", "a" * 64, "b" * 64)
    skipped = _event(OCMOperator.QUERY, 5, 6, "receipt:query", "b" * 64, "c" * 64)
    with pytest.raises(ValueError, match="epoch chain"):
        SolveTrace("trace:epoch", (first, skipped))

    second = _event(OCMOperator.QUERY, 1, 2, "receipt:query", "b" * 64, "c" * 64)
    trace = SolveTrace("trace:ok", (first, second))
    assert trace.operator_sequence == (OCMOperator.ADMIT, OCMOperator.QUERY)
    trace.validate_endpoints(pre_state_hash="a" * 64, post_state_hash="c" * 64)
    with pytest.raises(ValueError, match="post-state endpoint"):
        trace.validate_endpoints(pre_state_hash="a" * 64, post_state_hash="d" * 64)
    with pytest.raises(ValueError, match="receipt ids must be unique"):
        SolveTrace("trace:dup", (first, _event(OCMOperator.QUERY, 1, 2, "receipt:admit", "b" * 64, "c" * 64)))
