"""Tests for failure diagnosis, its registered worlds and its parents.

Written to document a *discrimination and its limits*, not to certify a success.
Asserting only that the governed policy diagnoses everything correctly would
leave the interesting questions unasked: whether anything simpler diagnoses
everything correctly too (it does), what each simpler thing gets wrong and why
(named, per arm, below), and what the governed policy pays for its one
advantage.

Every ground-truth fact the worlds rest on is recomputed here directly from
``games.py`` and ``methods.py`` rather than imported from ``diagnosis_worlds``,
so a world cannot pass by asserting its own premise.

The single most important test in this file is
``test_no_arm_can_read_the_ground_truth_cause``.  Everything else is
bookkeeping if that one does not hold.
"""

from __future__ import annotations

import inspect

import pytest

import diagnosis_parents
from diagnosis import (
    ALL_PROBES,
    CAUSE_ORDER,
    CAUSE_PRIOR,
    CAUSE_TO_FAILURE_CAUSE,
    COMMITMENT,
    DIAGNOSIS_PLAN,
    OBSERVED_SIGNAL,
    PROBE_COST,
    PROBE_ORDER,
    TRUE_CAUSES,
    Cause,
    CheckerMemory,
    Probe,
    ScopeBlindCheckerMemory,
    candidates,
    expected_elimination,
    expected_outcome,
    probe_score,
    record_diagnosis,
    select_probe,
)
from diagnosis_parents import (
    ARMS,
    FIXED_TREE_ORDER,
    PARENTS,
    AssumeRefutationParent,
    DecisionTreeParent,
    ExhaustiveProbeParent,
    GovernedDiagnosis,
    RetryOnceParent,
    ScopeBlindCacheAblation,
    sufficiency_report,
    table,
)
from diagnosis_worlds import (
    CHECKER_SOUNDNESS,
    EXACT_NIM,
    EXACT_SUB,
    NIM_DUAL,
    PROBE_BUDGET,
    SUB_DUAL,
    WORLDS,
    DownstreamQuery,
    Episode,
    QueryKind,
    RegimeChange,
    constant_predictor_baseline,
    cause_counts,
    run,
    scoreboard,
    target_counts,
    world_by_id,
)
from failure import FailureCause, FailureStore
from games import MultiHeapGame, SubtractionGame
from methods import COMBINERS, XOR_LOOKALIKES_ON_BINARY_VALUES
from prereg import commit

HORIZON = 40


# --------------------------------------------------------------------------
# the worlds' premises, recomputed from first principles
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def tables():
    return (
        SubtractionGame((1, 2)).grundy_upto(HORIZON),
        SubtractionGame((1, 2, 3)).grundy_upto(HORIZON),
    )


def test_mod3_and_mod4_are_each_exact_in_one_scope_and_refutable_in_the_other(tables):
    t12, t123 = tables
    assert all((n % 3 == 0) == (t12[n] == 0) for n in range(HORIZON + 1))
    assert any((n % 3 == 0) != (t123[n] == 0) for n in range(HORIZON + 1))
    assert all((n % 4 == 0) == (t123[n] == 0) for n in range(HORIZON + 1))
    assert any((n % 4 == 0) != (t12[n] == 0) for n in range(HORIZON + 1))


def test_the_subtraction_checker_is_defective_in_one_scope_and_exact_in_the_other(tables):
    """One checker id, two scopes, opposite verdicts.  Computed, not declared."""
    t12, t123 = tables
    wrong_on_sub123 = [n for n in range(HORIZON + 1) if (t12[n] == 0) != (t123[n] == 0)]
    assert wrong_on_sub123, "the SUB(1,2) table must be wrong somewhere on SUB(1,2,3)"
    assert CHECKER_SOUNDNESS[(SUB_DUAL, "SUB123")] is False
    assert CHECKER_SOUNDNESS[(SUB_DUAL, "SUB12")] is True


def test_the_nim_checker_is_exact_on_binary_heaps_and_defective_on_wide_ones(tables):
    t12, _ = tables
    xor = COMBINERS["XOR"]

    def via_sub12(p):
        return t12[p[0]] ^ t12[p[1]]

    binary = [(a, b) for a in range(2) for b in range(2)]
    wide = [(a, b) for a in range(5) for b in range(5)]
    assert all((via_sub12(p) == 0) == (xor(p) == 0) for p in binary)
    assert any((via_sub12(p) == 0) != (xor(p) == 0) for p in wide)
    assert CHECKER_SOUNDNESS[(NIM_DUAL, "NIM_BINARY")] is True
    assert CHECKER_SOUNDNESS[(NIM_DUAL, "NIM_WIDE")] is False


def test_the_binary_scope_has_both_a_lookalike_and_a_refutable_combiner():
    """``SUM_MOD_2`` is indistinguishable from ``XOR`` there; ``MAX_MOD_2`` is not.

    The hostile needs both: a method that cannot be refuted on binary heaps, so
    a non-identifying probe set is a real possibility there, and a method that
    can be, so a genuine refutation is a real possibility too.
    """
    xor = COMBINERS["XOR"]
    binary = [(a, b) for a in range(2) for b in range(2)]
    assert "SUM_MOD_2" in XOR_LOOKALIKES_ON_BINARY_VALUES
    assert all(
        (COMBINERS[name](p) == 0) == (xor(p) == 0)
        for name in XOR_LOOKALIKES_ON_BINARY_VALUES
        for p in binary
    )
    assert "MAX_MOD_2" not in XOR_LOOKALIKES_ON_BINARY_VALUES
    assert any((COMBINERS["MAX_MOD_2"](p) == 0) != (xor(p) == 0) for p in binary)


def test_xor_is_the_true_rule_of_nim2():
    nim = MultiHeapGame.nim(2, 4)
    xor = COMBINERS["XOR"]
    for a in range(5):
        for b in range(5):
            assert nim.is_p_position((a, b)) == (xor((a, b)) == 0)


# --------------------------------------------------------------------------
# the discipline: the cause is never on offer
# --------------------------------------------------------------------------


def test_no_arm_can_read_the_ground_truth_cause():
    """Enforced structurally, in the style of ``test_scaling.py``'s ``true_cone``.

    No arm class may mention ``true_cause`` anywhere in its source.  Only the
    world objects and the scoring loop, which compare after the fact, are
    allowed to touch it.
    """
    import diagnosis_worlds

    for factory in ARMS.values():
        assert "true_cause" not in inspect.getsource(factory)
    assert "true_cause" not in inspect.getsource(diagnosis_parents)
    # the ground truth lives on the world object and reaches the scorer only
    # through ``Episode.target``, which is a comparison made after the fact
    assert "true_cause" in inspect.getsource(Episode)
    assert "true_cause" in inspect.getsource(diagnosis_worlds._episode)
    assert "true_cause" not in inspect.getsource(run)
    assert "event.target" in inspect.getsource(run)


def test_a_live_bench_holds_no_cause_anywhere_in_it():
    """Reflection is closed too, not only the source.

    The bench is constructed from a pre-computed outcome vector rather than from
    the episode, so there is no reference path from an arm to the cause even for
    an arm that went looking through ``vars``.
    """
    episode = WORLDS[0].episodes[0]
    bench = episode.bench()
    for value in vars(bench).values():
        assert not isinstance(value, Cause)
        if isinstance(value, dict):
            assert not any(isinstance(v, Cause) for v in value.values())
        assert not isinstance(value, Episode)
    assert not hasattr(bench, "true_cause")


def test_the_case_a_machine_sees_has_no_cause_field():
    case = WORLDS[0].episodes[0].case
    assert "cause" not in case.as_dict()
    assert not any("cause" in name for name in vars(case))


def test_every_case_in_every_world_presents_the_identical_observed_signal():
    for world in WORLDS:
        for episode in world.episodes:
            assert episode.case.observed_signal == OBSERVED_SIGNAL
            assert episode.case.resource_bound.exhausted
            assert any(o.refutes for o in episode.case.evidence)


def test_a_world_may_not_carry_cannot_identify_as_a_cause():
    assert Cause.CANNOT_IDENTIFY not in TRUE_CAUSES
    for world in WORLDS:
        for episode in world.episodes:
            assert episode.true_cause in TRUE_CAUSES


def test_an_evaluator_defect_cannot_be_placed_where_the_checker_is_sound():
    for world in WORLDS:
        for episode in world.episodes:
            if episode.true_cause is Cause.EVALUATOR_DEFECT:
                assert episode.checker_sound is False


def test_the_registered_probe_budget_never_binds():
    """Stated in the module and tested rather than taken on trust."""
    assert sum(PROBE_COST.values()) < PROBE_BUDGET
    for world in WORLDS:
        for episode in world.episodes:
            assert episode.case.probe_budget == PROBE_BUDGET
            assert (
                sum(PROBE_COST[p] for p in episode.case.available_probes)
                <= PROBE_BUDGET
            )


def test_the_bench_refuses_a_probe_the_situation_does_not_offer():
    episode = world_by_id("DW4_WITHHELD_PROBES_HOSTILE").episodes[0]
    bench = episode.bench()
    assert Probe.SECOND_CHECKER not in episode.case.available_probes
    with pytest.raises(ValueError, match="not available"):
        bench.run(Probe.SECOND_CHECKER)


def test_the_bench_charges_the_registered_price_and_returns_an_observation():
    episode = WORLDS[0].episodes[0]
    bench = episode.bench()
    outcome = bench.run(Probe.PRECONDITION_AUDIT)
    assert outcome.cost == PROBE_COST[Probe.PRECONDITION_AUDIT]
    assert bench.spent == outcome.cost
    assert bench.probes_run == (Probe.PRECONDITION_AUDIT,)
    assert "precondition" in outcome.detail
    assert outcome.detail != Cause.ASSUMPTION_VIOLATED.name


def test_the_commitment_is_a_function_of_the_frozen_plan():
    assert commit(DIAGNOSIS_PLAN).commitment == COMMITMENT.commitment


# --------------------------------------------------------------------------
# the cause distribution, and the constant predictor that eats it
# --------------------------------------------------------------------------


def test_the_cause_distribution_is_non_degenerate():
    counts = cause_counts()
    assert set(counts) == {c.name for c in CAUSE_ORDER}
    assert all(n > 0 for n in counts.values())
    total = sum(counts.values())
    assert max(counts.values()) / total < 0.5


def test_the_constant_predictor_baseline_is_reported_and_beatable():
    """A skewed distribution makes a constant answer look like a policy.

    So the baseline is computed against the same targets every arm is scored on,
    and ``assume_refutation_parent`` *is* that constant predictor, which lets a
    reader see how much of any arm's accuracy is structure and how much is the
    base rate.
    """
    baseline = constant_predictor_baseline()
    assert baseline["best_constant_answer"] == Cause.TRUE_REFUTATION.name
    assert 0.2 < baseline["best_constant_accuracy"] < 0.35
    row = scoreboard({"assume_refutation_parent": AssumeRefutationParent})[
        "assume_refutation_parent"
    ]
    assert row.accuracy == pytest.approx(baseline["best_constant_accuracy"])


def test_targets_include_honest_refusals_and_the_worlds_are_not_all_refusal():
    counts = target_counts()
    assert counts[Cause.CANNOT_IDENTIFY.name] > 0
    assert counts[Cause.CANNOT_IDENTIFY.name] < sum(counts.values()) / 4


# --------------------------------------------------------------------------
# the registered response table and its inversion
# --------------------------------------------------------------------------


@pytest.mark.parametrize("cause", CAUSE_ORDER)
def test_the_full_probe_vector_identifies_every_cause(cause):
    for sound in (True, False):
        if cause is Cause.EVALUATOR_DEFECT and sound:
            continue
        observed = {p: expected_outcome(cause, p, sound) for p in PROBE_ORDER}
        assert candidates(observed, None) == frozenset({cause})


def test_the_cheap_control_battery_narrows_but_does_not_convict():
    """A failed control battery says the checker is unreliable in this scope.

    It does not say this verdict was wrong.  Only the most expensive probe on
    the list settles that, which is the asymmetry the whole design rests on.
    """
    assert candidates({Probe.CHECKER_CONTROL_BATTERY: False}, None) == frozenset(
        CAUSE_ORDER
    )
    assert candidates({Probe.CHECKER_CONTROL_BATTERY: True}, None) == frozenset(
        set(CAUSE_ORDER) - {Cause.EVALUATOR_DEFECT}
    )


def test_without_the_second_checker_a_defect_and_a_refutation_are_the_same_thing():
    observed = {
        Probe.PRECONDITION_AUDIT: True,
        Probe.SPLIT_TEST: True,
        Probe.RERUN_LARGER_BUDGET: False,
        Probe.CHECKER_CONTROL_BATTERY: False,
    }
    assert candidates(observed, None) == frozenset(
        {Cause.TRUE_REFUTATION, Cause.EVALUATOR_DEFECT}
    )


def test_a_remembered_scope_fact_shrinks_the_candidate_set_for_free():
    """The mechanism under test, in three lines and with no probe purchased."""
    assert len(candidates({}, None)) == 5
    assert len(candidates({}, True)) == 4
    assert Cause.EVALUATOR_DEFECT not in candidates({}, True)


def test_the_greedy_rule_reproduces_the_hand_authored_ordering():
    """The strongest realistic parent is sufficient on probe ordering.

    Greedy expected-elimination-per-cost, run forward from an empty observation
    set on a stationary distribution, produces exactly
    ``diagnosis_parents.FIXED_TREE_ORDER``.  This is asserted rather than hoped
    for, and it is the reason the receipt reports the ordering question closed.
    """
    observed: dict[Probe, bool] = {}
    picked: list[Probe] = []
    known = None
    while True:
        live = candidates(observed, known)
        if len(live) <= 1:
            break
        probe = select_probe(live, known, set(ALL_PROBES) - set(observed))
        if probe is None:
            break
        picked.append(probe)
        # walk the branch that keeps the most causes alive, so the whole
        # ordering is exercised rather than the first short branch
        observed[probe] = expected_outcome(Cause.TRUE_REFUTATION, probe, False)
        if probe is Probe.CHECKER_CONTROL_BATTERY:
            known = observed[probe]
    assert tuple(picked) == FIXED_TREE_ORDER


def test_a_probe_that_cannot_discriminate_is_never_bought():
    live = frozenset({Cause.TRUE_REFUTATION, Cause.BUDGET_EXHAUSTED})
    assert expected_elimination(Probe.CHECKER_CONTROL_BATTERY, live, True) == 0.0
    assert probe_score(Probe.SECOND_CHECKER, live, True) == 0.0
    assert select_probe(live, True, {Probe.CHECKER_CONTROL_BATTERY}) is None


# --------------------------------------------------------------------------
# the downstream half, built on the prior pilot's store
# --------------------------------------------------------------------------


def test_a_refusal_records_no_negative_knowledge_at_all():
    """``CANNOT_IDENTIFY`` is never silently converted into a guess.

    ``FailureKnowledge`` has no cause meaning "I do not know", and inventing one
    would be exactly that conversion.  The attempt is simply not turned into a
    conclusion -- and the honest cost of that shows up as repeated work.
    """
    store = FailureStore()
    case = WORLDS[0].episodes[0].case
    assert record_diagnosis(store, case, Cause.CANNOT_IDENTIFY) is None
    assert store.attempts == ()
    assert store.live_exclusions == ()


@pytest.mark.parametrize("cause", CAUSE_ORDER)
def test_only_the_two_information_bearing_causes_create_an_exclusion(cause):
    store = FailureStore()
    case = world_by_id("DW1_STATIONARY_SOUND_CHECKER").episodes[0].case
    record_diagnosis(store, case, cause)
    expected = CAUSE_TO_FAILURE_CAUSE[cause].may_exclude
    assert bool(store.live_exclusions) is expected


def test_the_bridge_to_the_prior_taxonomy_is_total_and_injective():
    assert set(CAUSE_TO_FAILURE_CAUSE) == set(CAUSE_ORDER)
    assert len(set(CAUSE_TO_FAILURE_CAUSE.values())) == len(CAUSE_ORDER)
    assert CAUSE_TO_FAILURE_CAUSE[Cause.TRUE_REFUTATION] is FailureCause.REFUTED_BY_CHECKER


# --------------------------------------------------------------------------
# world shape
# --------------------------------------------------------------------------


def test_all_five_registered_worlds_are_present_and_two_are_hostile():
    assert [w.world_id for w in WORLDS] == [
        "DW1_STATIONARY_SOUND_CHECKER",
        "DW2_DEFECTIVE_CHECKER_ONE_SCOPE",
        "DW3_ONE_CHECKER_TWO_SCOPES_HOSTILE",
        "DW4_WITHHELD_PROBES_HOSTILE",
        "DW5_COMMITMENT_DRAWN_SEQUENCE",
    ]
    assert sum(1 for w in WORLDS if w.hostile) == 2


@pytest.mark.parametrize("world", WORLDS, ids=lambda w: w.world_id)
def test_every_world_states_what_it_tests_and_queries_its_conclusions(world):
    assert world.tests
    assert world.episodes
    assert any(isinstance(e, DownstreamQuery) for e in world.script)


def test_dw1_never_makes_the_evaluator_branch_live():
    world = world_by_id("DW1_STATIONARY_SOUND_CHECKER")
    assert all(e.checker_sound for e in world.episodes)
    assert world.cause_counts[Cause.EVALUATOR_DEFECT] == 0


def test_dw2_repeats_one_scope_so_the_checker_fact_is_worth_remembering():
    world = world_by_id("DW2_DEFECTIVE_CHECKER_ONE_SCOPE")
    assert len({e.case.memory_key for e in world.episodes}) == 1
    assert all(not e.checker_sound for e in world.episodes)


def test_dw3_puts_one_checker_on_both_sides_of_a_soundness_boundary():
    world = world_by_id("DW3_ONE_CHECKER_TWO_SCOPES_HOSTILE")
    assert {e.case.checker_id for e in world.episodes} == {SUB_DUAL}
    assert {e.checker_sound for e in world.episodes} == {True, False}
    sound_refutations = [
        e
        for e in world.episodes
        if e.checker_sound and e.true_cause is Cause.TRUE_REFUTATION
    ]
    assert len(sound_refutations) >= 4, (
        "the hostile needs genuine refutations on the sound side; they are what a "
        "scope-blind memory excuses as another instance of the defect"
    )


def test_dw4_withholds_probes_and_most_of_it_is_unanswerable():
    world = world_by_id("DW4_WITHHELD_PROBES_HOSTILE")
    unanswerable = [e for e in world.episodes if not e.identifiable]
    assert len(unanswerable) == 7
    assert len(world.episodes) - len(unanswerable) == 2, (
        "an arm must not be able to pass this world by refusing everything"
    )
    assert all(
        Probe.CHECKER_CONTROL_BATTERY in e.case.available_probes for e in world.episodes
    ), (
        "the control battery stays available here, so a scope memory can never pin "
        "more than the episode's own probes would have and the targets are well "
        "defined independently of what an arm remembers"
    )


def test_dw5_is_drawn_from_the_commitment_and_spans_a_soundness_boundary():
    world = world_by_id("DW5_COMMITMENT_DRAWN_SEQUENCE")
    assert len(world.episodes) == DIAGNOSIS_PLAN["sequence_length"]
    keys = {e.case.memory_key for e in world.episodes}
    assert len(keys) == 4
    nim = {e.checker_sound for e in world.episodes if e.case.checker_id == NIM_DUAL}
    assert nim == {True, False}


def test_a_regime_change_reopens_and_no_arm_is_left_broken_shut():
    """The store is held constant across arms, so this is a control column.

    Every arm files its conclusions in the same unmodified ``FailureStore``,
    which reopens on the changed assumption name.  ``missed_reopenings`` is
    therefore expected to be zero for every arm, and it is reported as evidence
    that the downstream half is wired up rather than as a discrimination.
    """
    changed = [w for w in WORLDS if w.regime_change is not None]
    assert changed
    assert any(
        isinstance(e, DownstreamQuery) and e.kind is QueryKind.MUST_REOPEN
        for w in changed
        for e in w.script
    )
    for name, factory in ARMS.items():
        for world in changed:
            assert run(world, factory).missed_reopenings == 0, name


# --------------------------------------------------------------------------
# each arm's specific failure mode, by name
# --------------------------------------------------------------------------


def test_assume_refutation_parent_never_buys_a_single_probe():
    for world in WORLDS:
        score = run(world, AssumeRefutationParent)
        assert score.probe_cost == 0
        assert score.probes_bought == 0


def test_assume_refutation_parent_is_exactly_the_constant_predictor():
    scores = scoreboard({"a": AssumeRefutationParent})["a"]
    verdicts = {v for _, v, _ in scores.confusion}
    assert verdicts == {Cause.TRUE_REFUTATION.name}
    assert scores.correct == target_counts()[Cause.TRUE_REFUTATION.name]


def test_assume_refutation_parent_pays_for_it_in_false_exclusions():
    """Its cost is not zero; it is moved into a column it does not read."""
    scores = scoreboard({"a": AssumeRefutationParent})["a"]
    assert scores.false_exclusions > 0
    assert scores.probe_cost == 0


def test_retry_once_parent_has_no_branch_for_not_knowing():
    """A structural property of the heuristic, not an incidental weakness."""
    assert "CANNOT_IDENTIFY" not in inspect.getsource(RetryOnceParent)
    for world in WORLDS:
        arm = RetryOnceParent()
        for episode in world.episodes:
            assert arm.diagnose(episode.bench()).verdict is not Cause.CANNOT_IDENTIFY
    scores = scoreboard({"r": RetryOnceParent})["r"]
    assert scores.correct_cannot_identify == 0
    assert scores.missed_cannot_identify > 0


def test_retry_once_parent_solves_the_budget_confusion_and_no_other():
    arm = RetryOnceParent()
    verdicts = {}
    for world in WORLDS:
        arm = RetryOnceParent()
        for episode in world.episodes:
            if not episode.identifiable:
                continue
            verdicts.setdefault(episode.true_cause, set()).add(
                arm.diagnose(episode.bench()).verdict
            )
    assert verdicts[Cause.BUDGET_EXHAUSTED] == {Cause.BUDGET_EXHAUSTED}
    for cause in (
        Cause.EVALUATOR_DEFECT,
        Cause.NON_IDENTIFYING_EXPERIMENT,
        Cause.ASSUMPTION_VIOLATED,
    ):
        assert verdicts[cause] == {Cause.TRUE_REFUTATION}, (
            "the commonest real heuristic collapses three distinct causes onto the "
            "one that reads off the label"
        )


def test_retry_once_parent_buys_exactly_one_probe_per_episode():
    for world in WORLDS:
        score = run(world, RetryOnceParent)
        offered = sum(
            1
            for e in world.episodes
            if Probe.RERUN_LARGER_BUDGET in e.case.available_probes
        )
        assert score.probes_bought == offered


def test_exhaustive_probe_parent_buys_everything_every_time():
    for world in WORLDS:
        score = run(world, ExhaustiveProbeParent)
        assert score.probe_cost == sum(
            PROBE_COST[p] for e in world.episodes for p in e.case.available_probes
        )


def test_exhaustive_probe_parent_is_the_accuracy_ceiling():
    """No arm can end an episode knowing more than every available probe says."""
    rows = scoreboard(ARMS)
    ceiling = rows["exhaustive_probe_parent"].correct
    for name, score in rows.items():
        assert score.correct <= ceiling, name


def test_the_governed_policy_does_not_beat_the_ceiling_it_only_undercuts_it():
    rows = scoreboard(ARMS)
    assert rows["governed_diagnosis"].correct == rows["exhaustive_probe_parent"].correct
    assert (
        rows["governed_diagnosis"].probe_cost
        < rows["exhaustive_probe_parent"].probe_cost
    ), (
        "if the governed policy could not beat the exhaustive parent on cost at "
        "equal accuracy it would have no reason to exist, and the receipt would "
        "have to say so"
    )


def test_decision_tree_parent_is_sufficient_on_accuracy():
    """The headline half of the result, asserted rather than discovered late.

    A fixed hand-authored ordering matches the governed policy's accuracy on
    every registered world.  The ordering question is closed by the parent.
    """
    for world in WORLDS:
        assert (
            run(world, DecisionTreeParent).correct
            == run(world, GovernedDiagnosis).correct
        )


def test_decision_tree_parent_is_stateless_and_pays_the_same_price_twice():
    """Two identical episodes cost it exactly the same, which is the residual."""
    world = world_by_id("DW2_DEFECTIVE_CHECKER_ONE_SCOPE")
    arm = DecisionTreeParent()
    costs = [arm.diagnose(e.bench()).cost for e in world.episodes]
    defect_costs = [
        c
        for c, e in zip(costs, world.episodes)
        if e.true_cause is Cause.EVALUATOR_DEFECT
    ]
    assert len(set(defect_costs)) == 1
    assert not hasattr(arm, "memory")


def test_the_governed_policy_and_the_tree_agree_on_the_very_first_episode():
    """With nothing remembered there is nothing to be gained, and none is.

    The residual is therefore not a per-case ordering advantage; it appears only
    once a scope has been seen before.
    """
    for world in WORLDS:
        episode = world.episodes[0]
        governed = GovernedDiagnosis().diagnose(episode.bench())
        tree = DecisionTreeParent().diagnose(episode.bench())
        assert governed.cost == tree.cost
        assert governed.verdict is tree.verdict


def test_the_governed_saving_is_exactly_the_remembered_scope_facts():
    """The residual is confined to episodes where a checker fact was reused."""
    world = world_by_id("DW2_DEFECTIVE_CHECKER_ONE_SCOPE")
    governed = GovernedDiagnosis()
    tree = DecisionTreeParent()
    for episode in world.episodes:
        g = governed.diagnose(episode.bench())
        t = tree.diagnose(episode.bench())
        assert g.verdict is t.verdict
        if not g.reused:
            assert g.cost == t.cost
        else:
            assert g.cost <= t.cost
    assert governed.memory.reuses > 0


def test_the_governed_policy_beats_the_tree_only_where_scopes_repeat():
    rows = scoreboard(ARMS)
    assert rows["governed_diagnosis"].probe_cost < rows["decision_tree_parent"].probe_cost
    single = run(world_by_id("DW1_STATIONARY_SOUND_CHECKER"), GovernedDiagnosis)
    assert single.reused_facts > 0
    for world in WORLDS:
        assert (
            run(world, GovernedDiagnosis).probe_cost
            <= run(world, DecisionTreeParent).probe_cost
        ), world.world_id


def test_the_governed_policy_refuses_exactly_where_refusal_is_correct():
    for world in WORLDS:
        arm = GovernedDiagnosis()
        for episode in world.episodes:
            result = arm.diagnose(episode.bench())
            assert result.refused == (not episode.identifiable), episode.case.case_id
            if not result.refused:
                assert result.verdict is episode.true_cause


def test_no_shared_inference_arm_ever_beats_the_target():
    """Naming the cause on evidence that cannot single it out is a guess.

    The arms that run the shared inference cannot do it; the arms that do not
    (``assume_refutation`` and ``retry_once``) can and do, and it is scored as a
    miss rather than a hit.
    """
    for factory in (GovernedDiagnosis, DecisionTreeParent, ExhaustiveProbeParent):
        for world in WORLDS:
            arm = factory()
            for episode in world.episodes:
                if episode.identifiable:
                    continue
                assert arm.diagnose(episode.bench()).verdict is Cause.CANNOT_IDENTIFY
    guessers = scoreboard(
        {"a": AssumeRefutationParent, "r": RetryOnceParent}
    )
    assert guessers["a"].missed_cannot_identify > 0
    assert guessers["r"].missed_cannot_identify > 0


def test_refusing_costs_the_governed_policy_real_work():
    """Refusal is not free and the receipt must not pretend it is.

    On the withheld-probe hostile the governed policy declines to conclude, so
    it files no exclusion, so it repeats work a guesser avoids.  It buys that
    back in the false-exclusion column, and the two are reported side by side
    and never summed.
    """
    governed = run(world_by_id("DW4_WITHHELD_PROBES_HOSTILE"), GovernedDiagnosis)
    guesser = run(world_by_id("DW4_WITHHELD_PROBES_HOSTILE"), AssumeRefutationParent)
    assert governed.repeated_wasted_work > 0
    assert guesser.repeated_wasted_work == 0
    assert guesser.wasted_work_avoided > governed.wasted_work_avoided
    assert guesser.false_exclusions > governed.false_exclusions == 0


# --------------------------------------------------------------------------
# the over-generalisation hostile
# --------------------------------------------------------------------------


def test_the_scope_blind_ablation_over_generalises_and_is_punished():
    hostile = run(
        world_by_id("DW3_ONE_CHECKER_TWO_SCOPES_HOSTILE"), ScopeBlindCacheAblation
    )
    assert hostile.over_generalisations > 0
    assert hostile.correct < run(
        world_by_id("DW3_ONE_CHECKER_TWO_SCOPES_HOSTILE"), GovernedDiagnosis
    ).correct
    assert hostile.repeated_wasted_work > 0, (
        "excusing a genuine refutation as another instance of a known defect files "
        "no exclusion, so the wall gets ground a second time"
    )


def test_the_governed_policy_never_over_generalises_anywhere():
    for world in WORLDS:
        assert run(world, GovernedDiagnosis).over_generalisations == 0


def test_the_ablation_differs_from_the_treatment_only_where_scopes_differ():
    """On a single-scope world the two are the same object, by measurement."""
    world = world_by_id("DW1_STATIONARY_SOUND_CHECKER")
    treatment = run(world, GovernedDiagnosis)
    ablation = run(world, ScopeBlindCacheAblation)
    assert treatment.correct == ablation.correct
    assert treatment.probe_cost == ablation.probe_cost


def test_the_two_memories_differ_only_in_their_key():
    scoped = CheckerMemory()
    blind = ScopeBlindCheckerMemory()
    scoped.witness_defect(("C", "WIDE"))
    blind.witness_defect(("C", "WIDE"))
    assert scoped.belief(("C", "BINARY")) is None
    assert blind.belief(("C", "BINARY")) is False
    assert scoped.belief(("C", "WIDE")) is False


def test_the_ablation_is_not_counted_as_a_parent():
    assert "scope_blind_cache_ablation" not in PARENTS
    assert "governed_diagnosis" not in PARENTS
    assert set(PARENTS) == {
        "assume_refutation_parent",
        "retry_once_parent",
        "exhaustive_probe_parent",
        "decision_tree_parent",
    }


# --------------------------------------------------------------------------
# the registered scoreboard
# --------------------------------------------------------------------------

#: Frozen expectations.  If someone later weakens a parent to flatter the
#: governed policy, or strengthens the governed policy by changing what a world
#: shows it, these rows change and this test breaks.  That is what they are for.
EXPECTED = {
    #  arm                        correct cost  ok-refuse guessed over-gen false-excl
    "governed_diagnosis": (59, 531, 7, 0, 0, 0),
    "assume_refutation_parent": (17, 0, 0, 7, 0, 29),
    "retry_once_parent": (26, 285, 0, 7, 0, 29),
    "exhaustive_probe_parent": (59, 1031, 7, 0, 0, 0),
    "decision_tree_parent": (59, 573, 7, 0, 0, 0),
    "scope_blind_cache_ablation": (45, 420, 5, 2, 6, 0),
}


@pytest.mark.parametrize("arm", sorted(EXPECTED))
def test_score_matrix_matches_the_registered_expectation(arm):
    score = scoreboard(ARMS)[arm]
    assert (
        score.correct,
        score.probe_cost,
        score.correct_cannot_identify,
        score.missed_cannot_identify,
        score.over_generalisations,
        score.false_exclusions,
    ) == EXPECTED[arm]


def test_the_sufficiency_report_says_the_tree_is_equally_accurate():
    report = sufficiency_report()
    assert report["decision_tree_parent"]["verdict"] == "EQUALLY_ACCURATE_MORE_EXPENSIVE"
    assert report["exhaustive_probe_parent"]["verdict"] == "EQUALLY_ACCURATE_MORE_EXPENSIVE"
    assert report["assume_refutation_parent"]["verdict"] == "LESS_ACCURATE"
    assert report["retry_once_parent"]["verdict"] == "LESS_ACCURATE"


def test_the_cumulative_cost_curve_is_monotone_and_ends_at_the_total():
    for name, factory in ARMS.items():
        for world in WORLDS:
            score = run(world, factory)
            assert len(score.cost_curve) == score.episodes
            assert all(
                b >= a for a, b in zip(score.cost_curve, score.cost_curve[1:])
            ), name
            if score.cost_curve:
                assert score.cost_curve[-1] == score.probe_cost


def test_the_scoring_table_renders_every_arm_and_every_verdict():
    rendered = table()
    for name in ARMS:
        assert name in rendered
    assert "PARENT" in rendered or "ACCURATE" in rendered


def test_no_column_is_ever_collapsed_into_a_scalar_score():
    score = run(WORLDS[0], GovernedDiagnosis)
    assert not hasattr(score, "score")
    assert not hasattr(score, "total")
