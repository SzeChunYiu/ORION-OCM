"""Ported from ORION tests/unit/engine/test_cycle.py (commit adb97ec).

Operator vocabulary adapted: ``CycleOperator.SEARCH`` → ``OCMOperator.QUERY``
for the non-authority case; ``CycleOperator.ABSORB`` (ORION's one
authority-capable operator) → ``OCMOperator.COMMIT_ACTION``. One test is added
to pin the whole non-authority set.
"""

import pytest

from ocm.runtime.transition import (
    OCMOperator,
    Responsibility,
    Transition,
    local_reframe_allowed,
    revision_allowed,
)


def test_query_cannot_mint_authority():
    transition = Transition(
        operator=OCMOperator.QUERY,
        input_epoch=0,
        output_epoch=1,
        authority_increase=True,
        scientific_authority_certificate_ids=("certificate:fake",),
    )
    with pytest.raises(ValueError, match="cannot directly increase"):
        transition.validate()


def test_every_operator_except_commit_action_cannot_mint_authority():
    for operator in OCMOperator:
        transition = Transition(
            operator=operator,
            input_epoch=0,
            output_epoch=1,
            authority_increase=True,
            scientific_authority_certificate_ids=("certificate:1",),
        )
        if operator is OCMOperator.COMMIT_ACTION:
            transition.validate()
        else:
            with pytest.raises(ValueError, match="cannot directly increase"):
                transition.validate()


def test_authority_increase_requires_certificate():
    transition = Transition(
        operator=OCMOperator.COMMIT_ACTION,
        input_epoch=1,
        output_epoch=2,
        authority_increase=True,
    )
    with pytest.raises(ValueError, match="requires certificate"):
        transition.validate()


def test_transition_cannot_move_backward_in_epoch():
    with pytest.raises(ValueError, match="cannot move backward"):
        Transition(OCMOperator.PERSIST, input_epoch=2, output_epoch=1).validate()


def test_reframe_blocked_under_ambiguous_responsibility():
    assert not revision_allowed((Responsibility.SEARCH, Responsibility.METHOD))
    assert revision_allowed((Responsibility.SEARCH,))
    assert not revision_allowed(())
    assert local_reframe_allowed(Responsibility.SEARCH)
    assert not local_reframe_allowed(Responsibility.EXECUTION)
