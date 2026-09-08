"""Tests for the incremental re-index fix.

The equivalence gate is the load-bearing one: an optimisation that changes the
answer is not an optimisation, and the whole result is void if it fires.
"""

from __future__ import annotations

import json
import pathlib

import pytest

import reindex
import run_reindex
import subspace_arms as SA
from subspace import MAX_BUCKET_SIZE

HERE = pathlib.Path(__file__).parent
RECEIPT = json.loads((HERE / "results" / "REINDEX_E9_V1.json").read_text())
FROZEN = RECEIPT["frozen_sweep"]


def test_registration_adds_and_never_replaces():
    """The committed E1 receipt must stay reproducible."""
    before = dict(SA.ARMS)
    with reindex.registered():
        for arm_id, cls in before.items():
            assert SA.ARMS[arm_id] is cls, f"{arm_id} was replaced, not added alongside"
        assert reindex.INCREMENTAL_ARM_ID in SA.ARMS


def test_registration_is_scoped_and_leaves_no_trace():
    """The defect this guards: a permanent registration polluted test_subspace."""
    before = dict(SA.ARMS)
    with reindex.registered():
        assert reindex.INCREMENTAL_ARM_ID in SA.ARMS
    assert reindex.INCREMENTAL_ARM_ID not in SA.ARMS
    assert reindex.INCREMENTAL_ARM_ID not in SA.ARM_ROLES
    assert dict(SA.ARMS) == before


def test_exactly_one_machine_role_survives_outside_the_scope():
    """The invariant test_subspace asserts, checked here so it cannot break again."""
    machines = [a for a, r in SA.ARM_ROLES.items() if r == "MACHINE"]
    assert len(machines) == 1, f"registry left with {machines} outside a registered() scope"


def test_registration_refuses_an_unexpected_baseline():
    import subspace_arms as S
    saved = dict(S.ARMS)
    try:
        S.ARMS.clear()
        S.ARMS["something_else"] = object
        with pytest.raises(RuntimeError, match="refusing to register"):
            with reindex.registered():
                pass
    finally:
        S.ARMS.clear()
        S.ARMS.update(saved)


@pytest.mark.parametrize("cell", FROZEN, ids=[c["scale"] for c in FROZEN])
def test_equivalence_gate_same_feature_chosen(cell):
    assert cell["same_feature"], (
        f"at {cell['scale']} the incremental search chose a different feature; "
        "that is not an optimisation and voids the experiment"
    )


@pytest.mark.parametrize("cell", FROZEN, ids=[c["scale"] for c in FROZEN])
def test_capability_is_unchanged(cell):
    assert cell["machine_correct"] == cell["exhaustive_correct"]


@pytest.mark.parametrize("cell", FROZEN, ids=[c["scale"] for c in FROZEN])
def test_query_work_is_unchanged(cell):
    assert cell["incremental_query_work"] == cell["exhaustive_query_work"], (
        "the fix touches index construction only; a change here means it leaked into the "
        "query path"
    )


@pytest.mark.parametrize("cell", FROZEN, ids=[c["scale"] for c in FROZEN])
def test_index_work_never_increases(cell):
    assert cell["incremental_index_work"] <= cell["exhaustive_index_work"]


def test_the_saving_grows_with_scale():
    savings = [c["index_work_saving"] for c in FROZEN]
    assert savings == sorted(savings), "the saving should grow with N, not shrink"
    assert savings[-1] > 0.5


def test_the_terminal_that_was_solved_was_genuinely_unsolved_before():
    """Guards against declaring a fix for a problem that did not exist."""
    assert any(not c["crossover_reached_before"] for c in FROZEN)
    assert all(c["crossover_reached_after"] for c in FROZEN)
    assert RECEIPT["terminal"] == "INDEX_MAINTENANCE_TERMINAL_SOLVED"


def test_parent_sufficiency_is_still_reported_as_standing():
    """The fix must not be allowed to read as a win over the parent."""
    for c in FROZEN:
        assert c["parent_cheaper_by"] > 1.0, (
            f"at {c['scale']} the parent is no longer cheaper; the receipt's "
            "what_this_does_not_solve text would then be wrong"
        )
    text = " ".join(RECEIPT["what_this_does_not_solve"])
    assert "PARENT_SUFFICIENT stands" in text
    assert "No extrapolation is offered" in text


def test_the_unreachable_scale_is_reported_not_fabricated():
    note = RECEIPT["exploratory_extension"]["note"]
    assert "REFUSES 100x" in note
    assert "registered draw is exhausted" in " ".join(RECEIPT["what_this_does_not_solve"])


def test_monotonicity_assumption_is_defended_against_deletion():
    """Resumption is sound only while the store grows, and the code must say so.

    The soundness argument is that buckets never shrink, so a rejected candidate
    stays rejected. A store that deleted would break that, and the guard has to
    exist rather than the assumption being left implicit.
    """
    assert hasattr(reindex.IncrementalFeatureIndex, "note_deletion")
    doc = reindex.__doc__ or ""
    assert "deletes" in doc, "the deletion caveat must be stated, not assumed"
    idx = reindex.IncrementalFeatureIndex.__new__(reindex.IncrementalFeatureIndex)
    idx._resume_at, idx._resume_valid = 7, True
    idx.note_deletion()
    assert idx._resume_valid is False and idx._resume_at == 0, (
        "after a deletion the index must stop resuming and rescan from the start"
    )


def test_early_exit_respects_the_declared_bucket_bound():
    assert MAX_BUCKET_SIZE > 0
    src = pathlib.Path(HERE / "reindex.py").read_text()
    assert "> MAX_BUCKET_SIZE" in src, "the early exit must use the declared bound, not a literal"


def test_terminal_is_a_pure_function_of_the_table():
    terminal, _ = run_reindex.terminal_for({"frozen": FROZEN})
    assert terminal == RECEIPT["terminal"]
