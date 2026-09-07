"""Tests for scoped failure knowledge, its registered worlds and its parents.

These tests are written to document a *discrimination*, not to certify a
success.  Asserting only that the governed policy gets everything right would
leave the interesting question unasked: whether anything simpler gets everything
right too.  So every world is scored for all four arms against a hard-coded
expected row, and each parent's specific failure mode is asserted by name.  If
someone later weakens a parent to flatter the governed policy, the expected rows
change and these tests break, which is the point of writing them down.

The ground-truth facts every world rests on are recomputed here directly from
``games.py`` and ``methods.py`` rather than imported from ``failure_worlds``, so
a world cannot pass by asserting its own premise.
"""

from __future__ import annotations

import pytest

from failure import (
    Assumption,
    EXCLUSION_BEARING_CAUSES,
    Exclusion,
    FailureCause,
    FailureKnowledge,
    FailureStore,
    Observation,
    ResourceBound,
    Success,
    derive_exclusions,
)
from failure_parents import (
    POLICIES,
    GovernedPolicy,
    NogoodPolicy,
    NoMemoryPolicy,
    TranscriptPolicy,
    sufficiency_report,
    table,
)
from failure_worlds import (
    A_NIM_BINARY,
    A_NIM_WIDE,
    A_S1,
    A_S2,
    A_S2_BAD_CHECKER,
    WORLDS,
    Attempt,
    QueryKind,
    RegimeChange,
    run,
    scoreboard,
    world_by_id,
)
from games import MultiHeapGame, SubtractionGame
from methods import COMBINERS, XOR_LOOKALIKES_ON_BINARY_VALUES

HORIZON = 40


# ==========================================================================
# 0. ground truth, recomputed from the game families themselves
# ==========================================================================


def test_mod3_is_exactly_the_p_rule_of_sub12_and_wrong_on_sub123():
    """The whole of FW1, FW2 and FW7 rests on this pair of facts."""
    table12 = SubtractionGame((1, 2)).grundy_upto(HORIZON)
    table123 = SubtractionGame((1, 2, 3)).grundy_upto(HORIZON)
    assert all((n % 3 == 0) == (table12[n] == 0) for n in range(HORIZON + 1))
    wrong = [n for n in range(HORIZON + 1) if (n % 3 == 0) != (table123[n] == 0)]
    assert wrong, "n mod 3 must be refutable on SUB(1,2,3) or FW1 tests nothing"
    assert {3, 4, 9, 16, 33} <= set(wrong)


def test_mod4_is_exactly_the_p_rule_of_sub123():
    """FW6's method is correct everywhere; only its checker was broken."""
    table123 = SubtractionGame((1, 2, 3)).grundy_upto(HORIZON)
    assert all((n % 4 == 0) == (table123[n] == 0) for n in range(HORIZON + 1))


def test_defective_checker_really_does_disagree_with_the_exact_one():
    """FW6's defect must be a real disagreement, not a stipulated one."""
    table12 = SubtractionGame((1, 2)).grundy_upto(HORIZON)
    table123 = SubtractionGame((1, 2, 3)).grundy_upto(HORIZON)
    assert (table12[4] == 0) != (table123[4] == 0)


def test_lookalikes_are_indistinguishable_from_xor_on_binary_heaps():
    """FW4's recovery context and FW5's non-identifying probe set."""
    binary = [(a, b) for a in range(2) for b in range(2)]
    xor = COMBINERS["XOR"]
    for name in XOR_LOOKALIKES_ON_BINARY_VALUES:
        fn = COMBINERS[name]
        assert all((fn(p) == 0) == (xor(p) == 0) for p in binary)
    assert "SUM_MOD_2" in XOR_LOOKALIKES_ON_BINARY_VALUES


def test_wider_heaps_do_separate_sum_mod_2_from_xor():
    """FW4's exclusion context: the refutation at (1,3) must be genuine."""
    xor, sm2 = COMBINERS["XOR"], COMBINERS["SUM_MOD_2"]
    assert (sm2((1, 3)) == 0) != (xor((1, 3)) == 0)
    assert (sm2((2, 4)) == 0) != (xor((2, 4)) == 0)


def test_xor_is_the_true_rule_of_nim2():
    """FW5's worst case: excluding XOR forfeits the answer outright."""
    nim = MultiHeapGame.nim(2, 4)
    xor = COMBINERS["XOR"]
    assert all(
        nim.is_p_position((a, b)) == (xor((a, b)) == 0)
        for a in range(5)
        for b in range(5)
    )


# ==========================================================================
# 1. failure.py semantics: the cause filter
# ==========================================================================

_NO_PRESSURE = ResourceBound(
    expansions=1000, checker_calls=1000, spent_expansions=10, spent_checker_calls=1
)
_SPENT = ResourceBound(
    expansions=8, checker_calls=8, spent_expansions=8, spent_checker_calls=0
)
_REFUTING = (Observation(position="n=3", method_says=True, checker_says=False),)
_AGREEING = (Observation(position="n=3", method_says=False, checker_says=False),)


def _record(cause: FailureCause, **overrides) -> FailureKnowledge:
    kwargs = dict(
        attempted_method="grundy_mod3",
        task="T[n=3]",
        representation="heap_size",
        assumptions=A_S2,
        evidence=_REFUTING if cause is FailureCause.REFUTED_BY_CHECKER else _AGREEING,
        resource_bound=(
            _SPENT if cause is FailureCause.BUDGET_EXHAUSTED else _NO_PRESSURE
        ),
        observed_failure="no solution found",
        diagnosed_responsibility=cause,
        scope="SUB(1,2,3), one heap, n <= 40",
        reopen_conditions=("move_set changes",),
    )
    kwargs.update(overrides)
    return FailureKnowledge.build(**kwargs)


def test_exactly_two_causes_may_exclude():
    assert EXCLUSION_BEARING_CAUSES == {
        FailureCause.REFUTED_BY_CHECKER,
        FailureCause.ASSUMPTION_VIOLATED,
    }
    assert set(FailureCause) - EXCLUSION_BEARING_CAUSES == {
        FailureCause.BUDGET_EXHAUSTED,
        FailureCause.NON_IDENTIFYING_EXPERIMENT,
        FailureCause.EVALUATOR_DEFECT,
    }


@pytest.mark.parametrize(
    "cause", sorted(EXCLUSION_BEARING_CAUSES, key=lambda c: c.name)
)
def test_exclusion_bearing_causes_do_create_an_exclusion(cause):
    store = FailureStore()
    created = store.record(_record(cause))
    assert len(created) == 1
    assert store.excluded("grundy_mod3", A_S2)


@pytest.mark.parametrize(
    "cause",
    [
        FailureCause.BUDGET_EXHAUSTED,
        FailureCause.NON_IDENTIFYING_EXPERIMENT,
        FailureCause.EVALUATOR_DEFECT,
    ],
)
def test_non_bearing_causes_create_nothing(cause):
    """The central discipline: three of the five causes exclude nothing at all."""
    store = FailureStore()
    knowledge = _record(cause)
    assert knowledge.justified_exclusions == ()
    assert store.record(knowledge) == ()
    assert not store.excluded("grundy_mod3", A_S2)
    assert store.attempts, "the attempt is still recorded; only the conclusion is refused"


@pytest.mark.parametrize(
    "cause",
    [
        FailureCause.BUDGET_EXHAUSTED,
        FailureCause.NON_IDENTIFYING_EXPERIMENT,
        FailureCause.EVALUATOR_DEFECT,
    ],
)
def test_an_exclusion_cannot_even_be_constructed_for_a_non_bearing_cause(cause):
    """The refusal is structural, not a policy choice made at record time."""
    with pytest.raises(ValueError, match="may not create an exclusion"):
        Exclusion(
            method="grundy_mod3",
            assumptions=frozenset(A_S2),
            cause=cause,
            scope="anything",
            reopen_conditions=("never",),
        )
    assert derive_exclusions(
        cause=cause,
        method="grundy_mod3",
        assumptions=A_S2,
        scope="anything",
        reopen_conditions=("never",),
        evidence=_REFUTING,
    ) == ()


def test_hand_written_exclusion_on_a_non_bearing_cause_is_rejected():
    """A world author cannot smuggle an exclusion past the diagnosis."""
    smuggled = derive_exclusions(
        cause=FailureCause.REFUTED_BY_CHECKER,
        method="grundy_mod3",
        assumptions=A_S2,
        scope="s",
        reopen_conditions=("move_set changes",),
        evidence=_REFUTING,
    )
    with pytest.raises(ValueError, match="justifies no exclusion"):
        FailureKnowledge(
            attempted_method="grundy_mod3",
            task="T[n=3]",
            representation="heap_size",
            assumptions=A_S2,
            evidence=_AGREEING,
            resource_bound=_SPENT,
            observed_failure="no solution found",
            diagnosed_responsibility=FailureCause.BUDGET_EXHAUSTED,
            justified_exclusions=smuggled,
            still_live_alternatives=(),
            preserved_successes=(),
            scope="s",
            reopen_conditions=("move_set changes",),
        )


def test_refutation_without_a_witness_is_refused():
    with pytest.raises(ValueError, match="without a refuting observation"):
        _record(FailureCause.REFUTED_BY_CHECKER, evidence=_AGREEING)


def test_budget_exhaustion_without_a_spent_budget_is_refused():
    with pytest.raises(ValueError, match="bound was not reached"):
        _record(FailureCause.BUDGET_EXHAUSTED, resource_bound=_NO_PRESSURE)


def test_an_exclusion_without_a_reopen_condition_cannot_exist():
    """No one-way doors, enforced in the constructor."""
    with pytest.raises(ValueError, match="one-way door"):
        Exclusion(
            method="grundy_mod3",
            assumptions=frozenset(A_S2),
            cause=FailureCause.REFUTED_BY_CHECKER,
            scope="s",
            reopen_conditions=(),
        )


def test_a_method_cannot_be_excluded_and_live_at_once():
    with pytest.raises(ValueError, match="live alternative"):
        _record(
            FailureCause.REFUTED_BY_CHECKER,
            still_live_alternatives=("grundy_mod3",),
        )


def test_store_refuses_to_contradict_a_preserved_success():
    """A checker that certifies and refutes the same pair is defective, not decisive."""
    store = FailureStore()
    store.note_success(
        Success(method="grundy_mod3", assumptions=A_S2, task="T[n=9]")
    )
    with pytest.raises(ValueError, match="checker contradicts itself"):
        store.record(_record(FailureCause.REFUTED_BY_CHECKER))


def test_attempt_id_is_content_addressed_and_stable():
    assert _record(FailureCause.REFUTED_BY_CHECKER).attempt_id == _record(
        FailureCause.REFUTED_BY_CHECKER
    ).attempt_id
    assert (
        _record(FailureCause.REFUTED_BY_CHECKER).attempt_id
        != _record(FailureCause.REFUTED_BY_CHECKER, task="T[n=9]").attempt_id
    )


# ==========================================================================
# 2. failure.py semantics: the key and the reopening
# ==========================================================================


def test_exclusion_is_keyed_on_method_and_assumptions_not_task():
    """Different task, same regime: excluded.  Same task, different regime: not."""
    store = FailureStore()
    store.record(_record(FailureCause.REFUTED_BY_CHECKER, task="T[n=3]"))
    assert store.excluded("grundy_mod3", A_S2)
    assert not store.excluded("grundy_mod3", A_S1)
    assert not store.excluded("grundy_mod4", A_S2)
    # the public reader has no task parameter at all, so a task-keyed answer is
    # not expressible; this is the structural half of the A10 control
    with pytest.raises(TypeError):
        store.excluded("grundy_mod3", A_S2, "T[n=3]")  # type: ignore[call-arg]


def test_the_key_is_exact_set_equality_not_containment():
    """The documented conservative choice, pinned so it cannot drift silently.

    An exclusion earned under ``A`` does not carry to ``A`` plus one more
    assumption, and does not carry to a subset of ``A`` either.  This costs real
    transfer -- the exclusion must be re-earned in the richer context -- and the
    module docstring says so.  It is asserted here because the alternative
    (containment) would pass every registered world, all of whose assumption
    sets happen to have the same cardinality, while quietly manufacturing false
    exclusions in any context that grew an assumption.
    """
    store = FailureStore()
    store.record(_record(FailureCause.REFUTED_BY_CHECKER))
    assert store.excluded("grundy_mod3", A_S2)

    richer = A_S2 + (Assumption("probe_channel", "grundy_values"),)
    assert not store.excluded("grundy_mod3", richer)

    poorer = A_S2[:-1]
    assert not store.excluded("grundy_mod3", poorer)


def test_assumption_order_does_not_change_the_key():
    store = FailureStore()
    store.record(_record(FailureCause.REFUTED_BY_CHECKER))
    assert store.excluded("grundy_mod3", tuple(reversed(A_S2)))


def test_reopen_fires_exactly_on_a_depended_on_assumption():
    store = FailureStore()
    (exclusion,) = store.record(_record(FailureCause.REFUTED_BY_CHECKER))
    assert exclusion.depends_on == {"move_set", "play", "checker"}

    assert store.reopen("representation") == set(), "must not fire on an unrelated name"
    assert store.excluded("grundy_mod3", A_S2)

    fired = store.reopen("move_set")
    assert fired == {exclusion}
    assert not store.excluded("grundy_mod3", A_S2)
    assert exclusion in store.reopened_exclusions


@pytest.mark.parametrize("trigger", ["move_set", "move_set=1,2", Assumption("move_set", "1,2")])
def test_reopen_accepts_every_shape_of_trigger(trigger):
    store = FailureStore()
    store.record(_record(FailureCause.REFUTED_BY_CHECKER))
    assert len(store.reopen(trigger)) == 1


def test_reopen_leaves_exclusions_that_did_not_depend_on_the_change():
    store = FailureStore()
    store.record(_record(FailureCause.REFUTED_BY_CHECKER))
    store.record(
        _record(
            FailureCause.REFUTED_BY_CHECKER,
            attempted_method="sum_mod_2_combiner",
            assumptions=A_NIM_WIDE,
            reopen_conditions=("heap_values changes",),
        )
    )
    fired = store.reopen("move_set")
    assert {e.method for e in fired} == {"grundy_mod3"}
    assert store.excluded("sum_mod_2_combiner", A_NIM_WIDE)


def test_a_reopened_exclusion_can_be_re_earned():
    """Reopening is a lease expiring, not knowledge being deleted for good."""
    store = FailureStore()
    store.record(_record(FailureCause.REFUTED_BY_CHECKER))
    store.reopen("move_set")
    assert not store.excluded("grundy_mod3", A_S2)
    store.record(_record(FailureCause.REFUTED_BY_CHECKER, task="T[n=21]"))
    assert store.excluded("grundy_mod3", A_S2)


def test_nothing_in_the_store_can_ever_be_permanently_closed():
    store = FailureStore()
    for cause in FailureCause:
        store.record(_record(cause, task=f"T[{cause.name}]"))
    assert store.permanently_closed() == ()
    for exclusion in store.live_exclusions:
        assert exclusion.reopen_conditions


def test_a_later_success_reopens_the_failure():
    """CL-R4 scope_recovery: a success in the same scope must retire the failure."""
    store = FailureStore()
    store.record(_record(FailureCause.REFUTED_BY_CHECKER))
    assert store.excluded("grundy_mod3", A_S2)
    store.note_success(Success(method="grundy_mod3", assumptions=A_S2, task="T[n=12]"))
    assert not store.excluded("grundy_mod3", A_S2)
    assert len(store.reopened_exclusions) == 1


# ==========================================================================
# 3. the worlds are well formed and hostile where they claim to be
# ==========================================================================


def test_all_seven_registered_worlds_are_present():
    assert [w.world_id for w in WORLDS] == [
        "FW1_SCOPED_REFUTATION_TRANSFERS",
        "FW2_REGIME_RESTORED_MUST_REOPEN",
        "FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE",
        "FW4_HOSTILE_CHANGED_ASSUMPTIONS",
        "FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT",
        "FW6_HOSTILE_EVALUATOR_DEFECT",
        "FW7_HOSTILE_BROKEN_SHUT",
    ]
    assert sum(1 for w in WORLDS if w.hostile) == 5
    assert all(w.hostile == ("HOSTILE" in w.world_id) for w in WORLDS)


@pytest.mark.parametrize("world", WORLDS, ids=lambda w: w.world_id)
def test_every_world_has_queries_and_a_stated_test(world):
    assert world.queries, "a world with no query scores nothing"
    assert world.tests.strip()
    for query in world.queries:
        assert query.work_if_attempted > 0
        assert query.ground_truth.strip(), "every verdict must state its construction"


@pytest.mark.parametrize("world", WORLDS, ids=lambda w: w.world_id)
def test_every_attempt_obeys_the_cause_filter(world):
    for event in world.script:
        if isinstance(event, Attempt):
            cause = event.knowledge.diagnosed_responsibility
            assert event.knowledge.created_exclusions == cause.may_exclude


def test_fw3_presents_two_causes_under_one_label():
    """The hostile is only hostile if the surface labels really are identical."""
    world = world_by_id("FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE")
    attempts = [e.knowledge for e in world.script if isinstance(e, Attempt)]
    assert len(attempts) == 2
    assert attempts[0].observed_failure == attempts[1].observed_failure == "no solution found"
    assert attempts[0].diagnosed_responsibility is FailureCause.REFUTED_BY_CHECKER
    assert attempts[1].diagnosed_responsibility is FailureCause.BUDGET_EXHAUSTED
    assert attempts[0].created_exclusions and not attempts[1].created_exclusions


def test_fw6_label_is_indistinguishable_from_a_genuine_refutation():
    world = world_by_id("FW6_HOSTILE_EVALUATOR_DEFECT")
    attempt = next(e.knowledge for e in world.script if isinstance(e, Attempt))
    assert attempt.observed_failure.startswith("refuted by checker")
    assert attempt.diagnosed_responsibility is FailureCause.EVALUATOR_DEFECT
    assert any(o.refutes for o in attempt.evidence), "the disagreement is real"
    assert not attempt.created_exclusions, "but the checker is the party that is wrong"


def test_fw5_probe_set_contains_no_refutation():
    world = world_by_id("FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT")
    attempt = next(e.knowledge for e in world.script if isinstance(e, Attempt))
    assert not any(o.refutes for o in attempt.evidence)
    assert attempt.diagnosed_responsibility is FailureCause.NON_IDENTIFYING_EXPERIMENT


def test_fw2_and_fw7_hold_the_task_identity_fixed_across_the_regime_change():
    """Attack A10 in one assertion: same task, changed rules, must re-succeed."""
    for world_id in ("FW2_REGIME_RESTORED_MUST_REOPEN", "FW7_HOSTILE_BROKEN_SHUT"):
        world = world_by_id(world_id)
        failed_tasks = {
            e.knowledge.task for e in world.script if isinstance(e, Attempt)
        }
        reopen_tasks = {
            q.task for q in world.queries if q.kind is QueryKind.MUST_REOPEN
        }
        assert reopen_tasks & failed_tasks, (
            "a reopen query must re-present a task that has already failed, or a "
            "task-keyed blacklist is never put under any pressure"
        )


def test_fw1_puts_a_never_attempted_task_under_the_exclusion():
    world = world_by_id("FW1_SCOPED_REFUTATION_TRANSFERS")
    attempted = {e.knowledge.task for e in world.script if isinstance(e, Attempt)}
    must_block = [q for q in world.queries if q.kind is QueryKind.MUST_BLOCK]
    assert any(q.task not in attempted for q in must_block)


def test_fw7_alternates_exclusion_and_reopening():
    world = world_by_id("FW7_HOSTILE_BROKEN_SHUT")
    kinds = [
        "A" if isinstance(e, Attempt) else "R" if isinstance(e, RegimeChange) else e.kind.name
        for e in world.script
    ]
    assert kinds == [
        "A",
        "MUST_BLOCK",
        "R",
        "MUST_REOPEN",
        "R",
        "A",
        "MUST_BLOCK",
        "R",
        "MUST_REOPEN",
    ]


# ==========================================================================
# 4. the governed policy on every world
# ==========================================================================


@pytest.mark.parametrize("world", WORLDS, ids=lambda w: w.world_id)
def test_governed_policy_is_correct_on_every_query(world):
    """Per-query, not just per-score, so a failure names the episode."""
    policy = GovernedPolicy()
    for event in world.script:
        if isinstance(event, Attempt):
            policy.record(event.knowledge)
        elif isinstance(event, RegimeChange):
            policy.regime_change(event.changed)
        else:
            blocked = policy.blocked(event.method, event.assumptions, event.task)
            expected = event.kind is QueryKind.MUST_BLOCK
            assert blocked == expected, (
                f"{world.world_id}: {event.method} on {event.task} "
                f"({event.kind.name}) -- {event.ground_truth}"
            )


@pytest.mark.parametrize("world", WORLDS, ids=lambda w: w.world_id)
def test_governed_policy_makes_no_error_of_any_kind(world):
    score = run(world, GovernedPolicy)
    assert score.error_columns == (0, 0, 0)
    assert score.repeated_wasted_work == 0
    assert score.wasted_work_avoided == world.available_work_saving


def test_regime_change_actually_retires_the_exclusion_it_invalidates():
    """FW2 and FW7: reopening is an event, not an accident of the key.

    An assumption-keyed policy answers the MUST_REOPEN query correctly even if
    it retires nothing, because the new context is simply a different key.  That
    makes the score blind to whether the stale exclusion was actually let go, so
    the obligation is asserted here against the store: the regime change must
    return the excluded method, and the exclusion must move to the reopened
    list.  A store that merely sidesteps a stale exclusion keeps accumulating
    them, which is the slow version of being broken shut.
    """
    for world_id in ("FW2_REGIME_RESTORED_MUST_REOPEN", "FW7_HOSTILE_BROKEN_SHUT"):
        world = world_by_id(world_id)
        policy = GovernedPolicy()
        retired: list[set[str]] = []
        for event in world.script:
            if isinstance(event, Attempt):
                policy.record(event.knowledge)
            elif isinstance(event, RegimeChange):
                retired.append(policy.regime_change(event.changed))
        assert any("grundy_mod3" in fired for fired in retired), world_id
        assert policy.store.reopened_exclusions, world_id
        assert not policy.store.live_exclusions, (
            f"{world_id} ends in the reopened regime, so nothing should still be excluded"
        )


def test_governed_policy_never_leaves_a_method_unreachable():
    """The broken-shut column, checked at the store rather than the score."""
    policy = GovernedPolicy()
    for world in WORLDS:
        for event in world.script:
            if isinstance(event, Attempt):
                policy.record(event.knowledge)
            elif isinstance(event, RegimeChange):
                policy.regime_change(event.changed)
    assert policy.store.permanently_closed() == ()


# ==========================================================================
# 5. each parent's specific failure mode
# ==========================================================================

#: Hard-coded expected rows, per world and per policy:
#: (work avoided, work repeated, false exclusions, missed reopenings, broken shut).
#: Written out in full rather than computed, so that a change in any policy's
#: behaviour is a test failure with a name rather than a silently moving target.
EXPECTED = {
    ("FW1_SCOPED_REFUTATION_TRANSFERS", "governed"): (88, 0, 0, 0, 0),
    ("FW1_SCOPED_REFUTATION_TRANSFERS", "no_memory"): (0, 88, 0, 0, 0),
    ("FW1_SCOPED_REFUTATION_TRANSFERS", "transcript"): (20, 68, 0, 0, 0),
    ("FW1_SCOPED_REFUTATION_TRANSFERS", "nogood"): (88, 0, 0, 0, 0),
    ("FW2_REGIME_RESTORED_MUST_REOPEN", "governed"): (68, 0, 0, 0, 0),
    ("FW2_REGIME_RESTORED_MUST_REOPEN", "no_memory"): (0, 68, 0, 0, 0),
    ("FW2_REGIME_RESTORED_MUST_REOPEN", "transcript"): (68, 0, 0, 1, 1),
    ("FW2_REGIME_RESTORED_MUST_REOPEN", "nogood"): (68, 0, 0, 0, 0),
    ("FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE", "governed"): (124, 0, 0, 0, 0),
    ("FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE", "no_memory"): (0, 124, 0, 0, 0),
    ("FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE", "transcript"): (0, 124, 0, 0, 0),
    ("FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE", "nogood"): (124, 0, 1, 0, 0),
    ("FW4_HOSTILE_CHANGED_ASSUMPTIONS", "governed"): (32, 0, 0, 0, 0),
    ("FW4_HOSTILE_CHANGED_ASSUMPTIONS", "no_memory"): (0, 32, 0, 0, 0),
    ("FW4_HOSTILE_CHANGED_ASSUMPTIONS", "transcript"): (0, 32, 0, 0, 0),
    ("FW4_HOSTILE_CHANGED_ASSUMPTIONS", "nogood"): (32, 0, 0, 0, 0),
    ("FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT", "governed"): (0, 0, 0, 0, 0),
    ("FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT", "no_memory"): (0, 0, 0, 0, 0),
    ("FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT", "transcript"): (0, 0, 1, 0, 0),
    ("FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT", "nogood"): (0, 0, 1, 0, 0),
    ("FW6_HOSTILE_EVALUATOR_DEFECT", "governed"): (0, 0, 0, 0, 0),
    ("FW6_HOSTILE_EVALUATOR_DEFECT", "no_memory"): (0, 0, 0, 0, 0),
    ("FW6_HOSTILE_EVALUATOR_DEFECT", "transcript"): (0, 0, 1, 0, 0),
    ("FW6_HOSTILE_EVALUATOR_DEFECT", "nogood"): (0, 0, 2, 0, 0),
    ("FW7_HOSTILE_BROKEN_SHUT", "governed"): (328, 0, 0, 0, 0),
    ("FW7_HOSTILE_BROKEN_SHUT", "no_memory"): (0, 328, 0, 0, 0),
    ("FW7_HOSTILE_BROKEN_SHUT", "transcript"): (68, 260, 0, 1, 1),
    ("FW7_HOSTILE_BROKEN_SHUT", "nogood"): (328, 0, 0, 0, 0),
}


@pytest.mark.parametrize("key", sorted(EXPECTED), ids=lambda k: f"{k[0]}-{k[1]}")
def test_score_matrix_matches_the_registered_expectation(key):
    world_id, policy_name = key
    score = run(world_by_id(world_id), POLICIES[policy_name])
    assert (
        score.wasted_work_avoided,
        score.repeated_wasted_work,
        score.false_exclusions,
        score.missed_reopenings,
        score.broken_shut,
    ) == EXPECTED[key]


# ---- no_memory: safe, and useless -----------------------------------------


@pytest.mark.parametrize("world", WORLDS, ids=lambda w: w.world_id)
def test_no_memory_parent_blocks_nothing_ever(world):
    score = run(world, NoMemoryPolicy)
    assert score.error_columns == (0, 0, 0), "it cannot be wrong because it never decides"
    assert score.wasted_work_avoided == 0
    assert score.repeated_wasted_work == world.available_work_saving


def test_no_memory_parent_repeats_every_avoidable_unit_of_work():
    """Its whole cost is in one column; a scalar score would call it excellent."""
    rows = scoreboard(POLICIES)
    assert rows["no_memory"].wasted_work_avoided == 0
    assert rows["no_memory"].repeated_wasted_work == rows["governed"].wasted_work_avoided
    assert rows["no_memory"].error_columns == rows["governed"].error_columns


# ---- transcript: the A10 task-ID blacklist --------------------------------


def test_transcript_parent_fails_to_transfer_to_a_fresh_task():
    """FW1: the refutation is real and the parent cannot carry it one task over."""
    world = world_by_id("FW1_SCOPED_REFUTATION_TRANSFERS")
    policy = TranscriptPolicy()
    for event in world.script:
        if isinstance(event, Attempt):
            policy.record(event.knowledge)
    fresh = [
        q
        for q in world.queries
        if q.kind is QueryKind.MUST_BLOCK
        and q.task not in {e.knowledge.task for e in world.script if isinstance(e, Attempt)}
    ]
    assert fresh
    for query in fresh:
        assert not policy.blocked(query.method, query.assumptions, query.task)
    assert run(world, TranscriptPolicy).repeated_wasted_work > 0


def test_transcript_parent_is_broken_shut_on_the_scope_recovery_worlds():
    """FW2 and FW7: the same task after the rules changed stays blacklisted."""
    for world_id in ("FW2_REGIME_RESTORED_MUST_REOPEN", "FW7_HOSTILE_BROKEN_SHUT"):
        score = run(world_by_id(world_id), TranscriptPolicy)
        assert score.missed_reopenings == 1
        assert score.broken_shut == 1
    assert TranscriptPolicy().regime_change("move_set") == set(), (
        "a transcript records what happened, not what it depended on, so there is "
        "nothing for a rule change to retract"
    )


def test_transcript_parent_excludes_on_a_defective_checker_and_a_dud_experiment():
    """FW5 and FW6: cause-blind, so the surface label is all it has."""
    assert run(world_by_id("FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT"), TranscriptPolicy).false_exclusions == 1
    assert run(world_by_id("FW6_HOSTILE_EVALUATOR_DEFECT"), TranscriptPolicy).false_exclusions == 1


def test_transcript_parent_is_the_only_arm_that_is_ever_broken_shut():
    rows = scoreboard(POLICIES)
    assert rows["transcript"].broken_shut == 2
    assert all(
        rows[name].broken_shut == 0 for name in POLICIES if name != "transcript"
    )


# ---- nogood: strong, and cause-blind --------------------------------------


def test_nogood_parent_excludes_a_correct_method_on_a_spent_budget():
    """FW3: the exhaustive DP is games.py's own oracle and it gets blacklisted."""
    world = world_by_id("FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE")
    score = run(world, NogoodPolicy)
    assert score.false_exclusions == 1
    assert run(world, GovernedPolicy).false_exclusions == 0

    policy = NogoodPolicy()
    for event in world.script:
        if isinstance(event, Attempt):
            policy.record(event.knowledge)
    assert policy.blocked("grundy_dp_exhaustive", A_S2, "T[n=16]")


def test_nogood_parent_excludes_xor_on_a_probe_set_that_could_not_discriminate():
    """FW5: the worst available error, made by an otherwise excellent policy."""
    policy = NogoodPolicy()
    world = world_by_id("FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT")
    for event in world.script:
        if isinstance(event, Attempt):
            policy.record(event.knowledge)
    assert policy.blocked("xor_combiner", A_NIM_BINARY, "T[binary-probe-set]")
    assert run(world, NogoodPolicy).false_exclusions == 1


def test_nogood_parent_excludes_on_a_defective_checker_until_it_is_repaired():
    """FW6: two answers forfeited before the repair, recovered only afterwards."""
    world = world_by_id("FW6_HOSTILE_EVALUATOR_DEFECT")
    assert run(world, NogoodPolicy).false_exclusions == 2

    policy = NogoodPolicy()
    for event in world.script:
        if isinstance(event, Attempt):
            policy.record(event.knowledge)
    assert policy.blocked("grundy_mod4", A_S2_BAD_CHECKER, "T[n=4]")
    assert policy.regime_change("checker") == {"grundy_mod4"}
    assert not policy.blocked("grundy_mod4", A_S2, "T[n=20]")


def test_nogood_parent_gets_the_key_and_the_reopening_right():
    """It is not weakened: assumption keying and retraction both work correctly."""
    policy = NogoodPolicy()
    policy.record(_record(FailureCause.REFUTED_BY_CHECKER))
    assert policy.blocked("grundy_mod3", A_S2, "any")
    assert not policy.blocked("grundy_mod3", A_S1, "any")
    assert policy.regime_change("move_set") == {"grundy_mod3"}
    assert not policy.blocked("grundy_mod3", A_S2, "any")


# ==========================================================================
# 6. the comparison, reported honestly
# ==========================================================================


def test_nogood_parent_is_sufficient_where_every_failure_is_a_real_refutation():
    """The honest half of the result: on four of seven worlds it ties exactly."""
    report = sufficiency_report()
    assert set(report["nogood"]["tied_worlds"]) == {
        "FW1_SCOPED_REFUTATION_TRANSFERS",
        "FW2_REGIME_RESTORED_MUST_REOPEN",
        "FW4_HOSTILE_CHANGED_ASSUMPTIONS",
        "FW7_HOSTILE_BROKEN_SHUT",
    }
    assert set(report["nogood"]["discriminated_worlds"]) == {
        "FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE",
        "FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT",
        "FW6_HOSTILE_EVALUATOR_DEFECT",
    }


def test_the_residual_is_confined_to_the_cause_discriminating_worlds():
    """Where the governed policy differs from the nogood parent, and only there."""
    for world_id in (
        "FW3_HOSTILE_SAME_LABEL_DIFFERENT_CAUSE",
        "FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT",
        "FW6_HOSTILE_EVALUATOR_DEFECT",
    ):
        world = world_by_id(world_id)
        governed = run(world, GovernedPolicy)
        nogood = run(world, NogoodPolicy)
        assert nogood.false_exclusions > governed.false_exclusions == 0
        assert nogood.wasted_work_avoided == governed.wasted_work_avoided, (
            "the cause filter must not be buying its accuracy with lost work saving; "
            "if it were, the comparison would be a trade rather than a residual"
        )


def test_no_parent_is_sufficient_overall():
    report = sufficiency_report()
    assert set(report) == {"no_memory", "transcript", "nogood"}
    assert all(entry["verdict"] == "DISCRIMINATED" for entry in report.values())


def test_no_memory_ties_only_where_there_is_no_work_to_save():
    """An honest tie, and worth reporting: two worlds have no MUST_BLOCK query."""
    report = sufficiency_report()
    tied = set(report["no_memory"]["tied_worlds"])
    assert tied == {
        "FW5_HOSTILE_NON_IDENTIFYING_EXPERIMENT",
        "FW6_HOSTILE_EVALUATOR_DEFECT",
    }
    for world_id in tied:
        assert world_by_id(world_id).available_work_saving == 0


def test_governed_policy_is_the_unique_arm_with_a_clean_row():
    rows = scoreboard(POLICIES)
    clean = {
        name
        for name, score in rows.items()
        if score.error_columns == (0, 0, 0)
        and score.repeated_wasted_work == 0
        and score.wasted_work_avoided == sum(w.available_work_saving for w in WORLDS)
    }
    assert clean == {"governed"}


def test_the_scoring_table_renders_every_policy_and_verdict():
    rendered = table()
    for name in POLICIES:
        assert name in rendered
    assert "PARENT_SUFFICIENT" in rendered or "DISCRIMINATED" in rendered
    assert "broken shut" in rendered
