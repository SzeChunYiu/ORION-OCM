"""Tests for the escalation discriminator, the generator and the parents.

These tests document the *discrimination*, not merely success: each parent's
specific failure mode is asserted, so that a change which quietly makes a parent
stronger will fail here rather than silently inflate the governed policy's
apparent advantage.
"""

from __future__ import annotations

import pytest

from escalation import JUMP_THRESHOLD, Level, diagnose, identifiability_witness, score
from escalation_generator import LEVELS, draw_suite
from escalation_parents import PARENTS, cegar_parent, saturation_parent, timeout_parent
from escalation_worlds import WORLDS, world_by_id
from prereg import commit


@pytest.mark.parametrize("world", WORLDS, ids=[w.world_id for w in WORLDS])
def test_governed_policy_matches_registered_ground_truth(world):
    assert diagnose(world).level == world.minimum_sufficient_level


def test_budget_exhaustion_is_not_an_obstruction():
    """The single most important hostile: exhaustion must not escalate."""
    w = world_by_id("W1H_BUDGET_EXHAUSTED")
    d = diagnose(w)
    assert d.terminal == "BUDGET_EXHAUSTED"
    assert not d.is_jump
    assert d.splitting_probe is not None, "a splitting probe must still exist"


def test_timeout_parent_false_escalates_on_exhaustion():
    w = world_by_id("W1H_BUDGET_EXHAUSTED")
    assert timeout_parent(w).is_jump
    assert score(w, timeout_parent(w))["false_jump"]


def test_saturation_alone_does_not_authorise_escalation():
    """W2 is saturated within the permitted probe set, but evidence is binding."""
    w = world_by_id("W2_MORE_EVIDENCE")
    d = diagnose(w)
    assert d.terminal == "SATURATED_WITHIN_REGISTERED_SPACE"
    assert d.level is Level.L2_MORE_EVIDENCE
    assert not d.is_jump
    assert saturation_parent(w).is_jump, "the saturation parent must escalate here"


def test_saturation_terminal_is_never_impossibility():
    for w in WORLDS:
        assert diagnose(w).terminal != "PROBLEM_IMPOSSIBLE"


def test_cegar_parent_over_refines_on_a_bound_defect():
    w = world_by_id("W3_LOCAL_REPAIR")
    assert diagnose(w).level is Level.L3_LOCAL_REPAIR
    assert cegar_parent(w).level is Level.L5_REPRESENTATION_CHANGE


def test_representation_obstruction_is_exhibited_not_inferred():
    w = world_by_id("W5_REPRESENTATION_NON_IDENTIFYING")
    d = diagnose(w)
    assert d.obstruction_witness is not None
    a, b = d.obstruction_witness
    assert w.representation.image(a) == w.representation.image(b)
    assert w.truth(a) != w.truth(b)


def test_no_escalation_world_is_not_escalated():
    w = world_by_id("W7_NO_ESCALATION")
    d = diagnose(w)
    assert d.level is Level.L0_NO_ESCALATION
    assert not score(w, d)["overreach"]


def test_identifiability_witness_returns_none_when_representation_separates():
    w = world_by_id("W4_OPERATOR_INSUFFICIENT")
    assert identifiability_witness(w.representation, w.positions, w.truth) is None


def test_overreach_is_counted_even_below_the_jump_threshold():
    w = world_by_id("W7_NO_ESCALATION")
    s = score(w, timeout_parent(w))
    assert s["overreach"] == (int(timeout_parent(w).level) > int(w.minimum_sufficient_level))


def test_generated_draw_is_deterministic_in_the_commitment():
    c = commit({"a": 1})
    one = draw_suite(c.protected_seed, 2)
    two = draw_suite(c.protected_seed, 2)
    assert [w.world_id for w in one] == [w.world_id for w in two]
    assert [w.minimum_sufficient_level for w in one] == [w.minimum_sufficient_level for w in two]


def test_changing_the_plan_changes_the_protected_draw():
    """This is the property that makes the pre-registration mechanically checkable."""
    a = commit({"plan": "one"})
    b = commit({"plan": "two"})
    assert a.commitment != b.commitment
    assert a.protected_seed != b.protected_seed
    assert a.pilot_seed != a.protected_seed


def test_generator_covers_every_registered_level():
    c = commit({"gen": "coverage"})
    suite = draw_suite(c.protected_seed, 1)
    assert {w.minimum_sufficient_level for w in suite} == set(LEVELS)


def test_governed_policy_never_false_escalates_on_the_generated_draw():
    c = commit({"gen": "false-jump"})
    suite = draw_suite(c.protected_seed, 4)
    rows = [score(w, diagnose(w)) for w in suite]
    assert sum(r["false_jump"] for r in rows) == 0


def test_every_parent_is_scored_on_identical_visible_state():
    """No parent may be given information the governed policy lacks."""
    c = commit({"gen": "fairness"})
    for w in draw_suite(c.protected_seed, 1):
        for fn in PARENTS.values():
            d = fn(w)
            assert d.version_space_size >= 0
            assert d.budget_remaining == w.probe_budget


def test_jump_threshold_is_where_the_formulation_changes():
    assert JUMP_THRESHOLD is Level.L4_OPERATOR_INSUFFICIENT
    assert not any(
        lvl >= JUMP_THRESHOLD for lvl in (Level.L1_SEARCH_MORE, Level.L2_MORE_EVIDENCE,
                                          Level.L3_LOCAL_REPAIR)
    )
