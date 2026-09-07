"""Tests for the dependency-discovery harness.

These tests are adversarial towards the module they cover.  The experiment's
credibility rests on four things being true, and each has a test whose job is
to fail loudly when it stops being true:

(a) the leave-one-out oracle really is leave-one-out re-induction, verified by
    an independent re-derivation inside the test rather than by calling the
    module's own function and agreeing with it;
(b) no arm can reach the oracle or the declared cone -- enforced by source
    inspection, exactly as ``test_scaling.py`` enforces the ``true_cone``
    separation;
(c) every registered hostile actually fires: the globally-dependent method, the
    redundantly-supported method whose support leave-one-out cannot see, and
    the revocation of evidence that was never load-bearing;
(d) each parent fails in its own declared way and not in some other way -- a
    parent that failed for an unregistered reason would be a bug in the harness
    dressed up as a result.

A fifth thing is asserted throughout and matters more than any of them:
``learned_dependency_arm`` scores precision and recall of exactly ``1.0``
against the oracle **and still leaves a stale survivor**.  Several tests below
exist specifically to fail if a future edit makes that stale survivor go away
by accident, because the likeliest way for that to happen is a weakened hostile
rather than an improved arm.

The sweep is run once per module.  Everything asserted here is a deterministic
function of the pre-registration commitment, so a failure is a real change in
the harness and never a flaky draw.
"""

from __future__ import annotations

import inspect

import depend
import depend_arms
from depend import (
    COMMITMENT,
    DEPEND_PLAN,
    INDUCTION_EXPANSIONS,
    LANGUAGE,
    all_pairs_edges,
    build_catalogue,
    declared_edges,
    joint_witnesses,
    loo_dependency_edges,
    oracle_changed_methods,
    oracle_edges,
    redundant_support_methods,
    registered_roles,
    revocation_schedule,
    score_graph,
)
from depend_arms import (
    ARMS,
    ARM_ROLES,
    AllEvidenceParent,
    CoOccurrenceParent,
    DeclaredSupportsParent,
    DependencyArm,
    FullRecomputationParent,
    LazyLearnerArm,
    LearnedDependencyArm,
    crossover_revocations,
    crossovers_for,
    run_arm,
    step_table,
    summarise,
    sweep,
    sweep_table,
)

MULTIPLIERS = tuple(DEPEND_PLAN["multipliers"])
SMALLEST = MULTIPLIERS[0]

RESULTS = sweep()
ROWS = sweep_table(RESULTS)
STEPS = step_table(RESULTS)
SUMMARY = summarise(ROWS)


def rows_for(arm_id: str) -> list[dict]:
    return [r for r in ROWS if r["arm"] == arm_id]


def steps_for(arm_id: str, scale: str | None = None) -> list[dict]:
    return [
        s
        for s in STEPS
        if s["arm"] == arm_id and (scale is None or s["scale"] == scale)
    ]


def step_named(arm_id: str, step_id: str, scale: str) -> dict:
    return next(s for s in steps_for(arm_id, scale) if s["step"] == step_id)


# --------------------------------------------------------------------------
# the pre-registration
# --------------------------------------------------------------------------


def test_commitment_is_a_function_of_the_plan():
    """Editing the plan must change the draw, or the registration is decoration."""
    from prereg import commit

    assert commit(DEPEND_PLAN).commitment == COMMITMENT.commitment
    drifted = dict(DEPEND_PLAN)
    drifted["base_families"] = DEPEND_PLAN["base_families"] + 1
    assert commit(drifted).commitment != COMMITMENT.commitment


def test_scales_are_nested_so_a_change_between_them_is_a_change_of_N():
    small = build_catalogue(MULTIPLIERS[0])
    large = build_catalogue(MULTIPLIERS[-1])
    small_ids = [f.family_id for f in small.families]
    large_ids = [f.family_id for f in large.families]
    assert large_ids[: len(small_ids)] == small_ids


def test_every_arm_receives_an_identical_store():
    """Identical information, so any difference is a difference of architecture."""
    catalogue = build_catalogue(SMALLEST)
    arms = [factory(catalogue) for factory in ARMS.values()]
    assert len({a.n_objects for a in arms}) == 1
    assert len({a.store.store_bytes for a in arms}) == 1
    assert len({a.store.object_ids() for a in arms}) == 1


# --------------------------------------------------------------------------
# (a) the oracle really is leave-one-out re-induction
# --------------------------------------------------------------------------


def test_oracle_matches_an_independent_leave_one_out_rederivation():
    """Re-derive the oracle here, from the plan's own words, and compare.

    ``depend.loo_dependency_edges`` is memoised, shares helpers with the rest
    of the module and is the definition every endpoint is scored against.  A
    test that called it and agreed with itself would assert nothing, so this
    one rebuilds the definition from ``GrundyRuleLanguage.induce`` directly.
    """
    catalogue = build_catalogue(SMALLEST)
    for family in catalogue.families:
        everything = sorted({o for b in family.blocks for o in b.observations})
        base = LANGUAGE.induce(tuple(everything))
        expected = set()
        for block in family.blocks:
            without = sorted(
                {
                    o
                    for b in family.blocks
                    if b.block_id != block.block_id
                    for o in b.observations
                }
            )
            if LANGUAGE.induce(tuple(without)) != base:
                expected.add(block.block_id)
        assert loo_dependency_edges(family) == frozenset(expected)


def test_a_rule_cannot_depend_on_evidence_it_never_saw():
    """The true graph is a subgraph of the declared candidate graph."""
    catalogue = build_catalogue(SMALLEST)
    assert oracle_edges(catalogue) <= declared_edges(catalogue)


def test_the_declared_graph_is_strictly_larger_than_the_true_graph():
    """The gift is a real gift: declaration over-claims dependency.

    This is the sentence the prior scaling pilot's exactness rested on.  If
    declaration and dependency ever coincide here, ``declared_supports_parent``
    stops being a ceiling and the experiment has no question left.
    """
    for multiplier in MULTIPLIERS:
        catalogue = build_catalogue(multiplier)
        assert oracle_edges(catalogue) < declared_edges(catalogue)


def test_oracle_changed_methods_is_evaluated_against_live_evidence():
    """A schedule of successive revocations is scored step by step, not once."""
    catalogue = build_catalogue(SMALLEST)
    family = catalogue.probe
    everything = frozenset(b.block_id for f in catalogue.families for b in f.blocks)
    witness = next(w for w in joint_witnesses(family) if len(w) == 2)
    first, second = witness
    after_first = everything - {first}
    assert oracle_changed_methods(catalogue, everything, after_first) == frozenset()
    assert oracle_changed_methods(catalogue, after_first, after_first - {second}) == (
        frozenset({family.method_id})
    )


# --------------------------------------------------------------------------
# (b) discipline: no arm reaches the oracle
# --------------------------------------------------------------------------

FORBIDDEN_IN_ARMS = (
    "true_cone",
    "loo_dependency_edges",
    "oracle_edges",
    "oracle_changed_methods",
    "joint_witnesses",
    "redundant_support_methods",
    "registered_roles",
)


def test_no_arm_consults_the_ground_truth():
    """Enforced structurally, in the style of ``test_scaling.py``.

    No arm class may mention the oracle anywhere in its source.  Only the
    shared ``revoke`` scaffolding, which compares after the fact, is allowed to
    read it.
    """
    for cls in (
        LearnedDependencyArm,
        LazyLearnerArm,
        FullRecomputationParent,
        DeclaredSupportsParent,
        CoOccurrenceParent,
        AllEvidenceParent,
        depend_arms._ReverseIndexArm,
    ):
        source = inspect.getsource(cls)
        for name in FORBIDDEN_IN_ARMS:
            assert name not in source, f"{cls.__name__} reaches for {name}"
    assert "oracle_changed_methods" in inspect.getsource(DependencyArm.revoke)


def test_the_shared_rederivation_helper_is_also_clean():
    """``_rederive_edges`` is arm code and must not touch the oracle either."""
    source = inspect.getsource(depend_arms._rederive_edges)
    for name in FORBIDDEN_IN_ARMS:
        assert name not in source


def test_only_the_gifted_ceiling_reads_the_declarations():
    """``supports`` is the declaration this experiment exists to withdraw."""
    readers = [
        cls.__name__
        for cls in ARMS.values()
        if ".supports" in inspect.getsource(cls)
    ]
    assert readers == ["DeclaredSupportsParent"]


def test_no_wall_clock_anywhere_in_the_lane_modules():
    for module in (depend, depend_arms):
        source = inspect.getsource(module)
        assert "import time" not in source
        assert "perf_counter" not in source
        assert "monotonic" not in source


# --------------------------------------------------------------------------
# (c) the registered hostiles fire
# --------------------------------------------------------------------------


def test_the_four_registered_roles_fill_and_are_distinct():
    for multiplier in MULTIPLIERS:
        roles = registered_roles(build_catalogue(multiplier))
        assert set(roles) == {"REDUNDANT", "GLOBAL", "ABOVE_SPAN", "INERT"}
        assert len(set(roles.values())) == 4


def test_roles_are_stable_across_scales_because_the_order_is_nested():
    first = registered_roles(build_catalogue(MULTIPLIERS[0]))
    for multiplier in MULTIPLIERS[1:]:
        assert registered_roles(build_catalogue(multiplier)) == first


def test_hostile_one_a_genuinely_global_dependency():
    """Every block of the GLOBAL family matters, so locality is not free.

    A harness in which every method's dependency set happened to be a small
    local neighbourhood would be proving a property of the benchmark.
    """
    catalogue = build_catalogue(SMALLEST)
    family = next(
        f
        for f in catalogue.families
        if f.family_id == registered_roles(catalogue)["GLOBAL"]
    )
    assert loo_dependency_edges(family) == frozenset(family.block_ids)
    assert len(family.blocks) == DEPEND_PLAN["evidence_blocks"]


def test_hostile_two_redundant_support_is_invisible_to_leave_one_out():
    """The classic leave-one-out false negative, named and measured.

    Two blocks each suffice alone.  Leave-one-out finds NEITHER individually
    necessary and therefore reports that the method depends on nothing, while
    removing both changes the rule.  This is a limitation of the discovery
    method.  It is not corrected for anywhere in this lane.
    """
    catalogue = build_catalogue(SMALLEST)
    family = next(
        f
        for f in catalogue.families
        if f.family_id == registered_roles(catalogue)["REDUNDANT"]
    )
    assert loo_dependency_edges(family) == frozenset()
    witness = next(w for w in joint_witnesses(family) if len(w) == 2)
    everything = frozenset(family.block_ids)
    base = depend._rule_from_ids(family, everything)
    for block_id in witness:
        assert depend._rule_from_ids(family, everything - {block_id}) == base
    assert depend._rule_from_ids(family, everything - frozenset(witness)) != base


def test_the_false_negative_is_counted_at_every_scale_not_just_witnessed():
    """A named anecdote is not a measurement; the count is the report."""
    for multiplier in MULTIPLIERS:
        catalogue = build_catalogue(multiplier)
        invisible = redundant_support_methods(catalogue)
        assert catalogue.probe.method_id in invisible
        assert 0 < len(invisible) < len(catalogue.families)


def test_hostile_three_evidence_that_was_never_load_bearing():
    """Revoking it should change nothing, so the expected cone is the block."""
    catalogue = build_catalogue(SMALLEST)
    step = revocation_schedule(catalogue)[0]
    assert step.step_id == "NEVER_LOAD_BEARING"
    family = catalogue.family_of_block(step.block_ids[0])
    assert step.block_ids[0] not in loo_dependency_edges(family)
    for arm_id in ARMS:
        record = step_named(arm_id, "NEVER_LOAD_BEARING", f"{SMALLEST}x")
        assert record["expected_cone"] == 1


def test_the_above_span_block_is_load_bearing_and_positionally_invisible():
    """The co-occurrence heuristic's blind spot is a fact about the world."""
    catalogue = build_catalogue(SMALLEST)
    step = next(
        s for s in revocation_schedule(catalogue) if s.step_id == "LOAD_BEARING_ABOVE_SPAN"
    )
    family = catalogue.family_of_block(step.block_ids[0])
    block = next(b for b in family.blocks if b.block_id == step.block_ids[0])
    assert step.block_ids[0] in loo_dependency_edges(family)
    assert min(block.positions) >= family.span


def test_the_schedule_puts_the_no_op_steps_before_the_breaking_ones():
    """Otherwise a step's lesson is contaminated by the step before it."""
    catalogue = build_catalogue(SMALLEST)
    schedule = revocation_schedule(catalogue)
    ids = [s.step_id for s in schedule]
    assert ids.index("REDUNDANT_FIRST") < ids.index("REDUNDANT_SECOND")
    families = [s.family_id for s in schedule]
    assert families.count(schedule[0].family_id) == 1


# --------------------------------------------------------------------------
# (d) each arm's specific behaviour
# --------------------------------------------------------------------------


def test_learned_arm_is_exact_against_the_oracle_and_pays_for_it():
    """Precision and recall 1.0, and a build cost that is not zero.

    The graph score is not a finding: this arm runs the oracle's own
    procedure, so agreeing with it is arithmetic.  What the test protects is
    that the agreement was *bought* -- a build work of zero would mean the
    graph came from somewhere it should not have.
    """
    for row in rows_for("learned_dependency_arm"):
        assert row["graph_precision"] == 1.0
        assert row["graph_recall"] == 1.0
        assert row["graph_exact"] is True
        assert row["build_work"] > 0
        expected_inductions = row["methods"] * (DEPEND_PLAN["evidence_blocks"] + 1)
        assert row["build_work"] > expected_inductions * INDUCTION_EXPANSIONS * 0.9


def test_learned_arm_still_leaves_a_stale_survivor_on_the_redundant_pair():
    """The headline.  Exact discovery, cached, and still wrong.

    At acquisition neither half of the redundant pair was individually
    necessary, so no edge was stored for either.  Withdraw both and the belief
    is left standing on evidence that is gone.  A cached leave-one-out graph is
    not composable under multi-block revocation, and this is the number that
    says so.
    """
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        failing = [
            s
            for s in steps_for("learned_dependency_arm", scale)
            if s["stale_survivors"]
        ]
        assert [s["step"] for s in failing] == ["REDUNDANT_SECOND"]
        assert failing[0]["stale_survivor_ids"] == [
            build_catalogue(multiplier).probe.method_id
        ]
        assert all(
            s["collateral_invalidations"] == 0
            for s in steps_for("learned_dependency_arm", scale)
        )


def test_lazy_learner_builds_nothing_and_is_exact_on_every_step():
    """Correctness by re-derivation, which is old and is not a finding.

    What is worth reporting is that it survives the redundant pair the cached
    arm fails, because it never relied on a snapshot of which evidence
    mattered.
    """
    for row in rows_for("lazy_learner_arm"):
        assert row["build_work"] == 0
        assert row["stale_survivors"] == 0
        assert row["collateral_invalidations"] == 0
        assert row["graph_precision"] == 1.0
        assert row["graph_recall"] == 1.0
    assert all(s["exact"] for s in steps_for("lazy_learner_arm"))


def test_lazy_learners_cheap_build_is_a_claim_about_an_arm_nobody_asks():
    """Disclosing a graph costs it the whole discovery it skipped."""
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        lazy = next(r for r in rows_for("lazy_learner_arm") if r["scale"] == scale)
        learned = next(
            r for r in rows_for("learned_dependency_arm") if r["scale"] == scale
        )
        assert lazy["build_work"] == 0
        assert lazy["graph_disclosure_work"] >= learned["build_work"] * 0.9


def test_lazy_learner_costs_more_per_revocation_than_the_cached_arm():
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        lazy = next(r for r in rows_for("lazy_learner_arm") if r["scale"] == scale)
        learned = next(
            r for r in rows_for("learned_dependency_arm") if r["scale"] == scale
        )
        assert lazy["mean_revocation_work"] > learned["mean_revocation_work"]


def test_full_recomputation_is_the_correctness_and_the_cost_ceiling():
    """Never wrong, and it re-induces every method every time.

    The induction floor is checked explicitly: an implementation that quietly
    started skipping methods would still be exactly correct on this schedule
    and would no longer be the ceiling it is reported as.
    """
    for row in rows_for("full_recomputation_parent"):
        assert row["build_work"] == 0
        assert row["stale_survivors"] == 0
        assert row["collateral_invalidations"] == 0
        floor = row["methods"] * INDUCTION_EXPANSIONS
        assert row["mean_revocation_work"] >= floor
    assert all(s["exact"] for s in steps_for("full_recomputation_parent"))
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        full = next(
            r for r in rows_for("full_recomputation_parent") if r["scale"] == scale
        )
        lazy = next(r for r in rows_for("lazy_learner_arm") if r["scale"] == scale)
        assert full["mean_revocation_work"] > lazy["mean_revocation_work"]


def test_declared_supports_parent_gets_recall_free_and_pays_in_precision():
    """The gifted ceiling's failure mode: it over-claims, never under-claims.

    Recall is ``1.0`` by construction because a rule cannot depend on evidence
    it was never shown.  Precision is strictly below ``1.0`` because most of
    the declared blocks are not dependencies, and every one of those is a
    collateral invalidation waiting to happen.
    """
    for row in rows_for("declared_supports_parent"):
        assert row["graph_recall"] == 1.0
        assert row["graph_precision"] < 1.0
        assert row["stale_survivors"] == 0
        assert row["collateral_invalidations"] > 0
        assert row["believed_edges"] == row["blocks"]
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        assert step_named("declared_supports_parent", "NEVER_LOAD_BEARING", scale)[
            "collateral_invalidations"
        ] == 1
        assert step_named("declared_supports_parent", "REDUNDANT_FIRST", scale)[
            "collateral_invalidations"
        ] == 1


def test_declared_supports_parent_pays_no_inductions():
    """It is not doing discovery; that is the point of calling it a gift."""
    arm = DeclaredSupportsParent(build_catalogue(SMALLEST))
    assert arm.build_ledger.search_expansions == 0


def test_co_occurrence_parent_is_wrong_in_both_directions():
    """A stale survivor above the span and a collateral below it.

    Measured, not hidden.  A heuristic tuned until one of these went away
    would be the oracle wearing a hat.
    """
    for row in rows_for("co_occurrence_parent"):
        assert row["graph_recall"] < 1.0
        assert row["graph_precision"] < 1.0
        assert row["stale_survivors"] > 0
        assert row["collateral_invalidations"] > 0
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        above = step_named("co_occurrence_parent", "LOAD_BEARING_ABOVE_SPAN", scale)
        assert above["stale_survivors"] == 1
        assert above["stale_survivor_ids"] == [
            f"M:{registered_roles(build_catalogue(multiplier))['ABOVE_SPAN']}"
        ]
        assert step_named("co_occurrence_parent", "NEVER_LOAD_BEARING", scale)[
            "collateral_invalidations"
        ] == 1


def test_co_occurrence_parent_catches_the_pair_the_learned_arm_misses():
    """The crude heuristic is accidentally safe where the sound one is not.

    Not a point in the heuristic's favour.  It over-links, and over-linking
    fails in the wasteful direction rather than the dangerous one, which is
    exactly why the two error kinds are never summed.
    """
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        assert step_named("co_occurrence_parent", "REDUNDANT_SECOND", scale)[
            "stale_survivors"
        ] == 0
        assert step_named("learned_dependency_arm", "REDUNDANT_SECOND", scale)[
            "stale_survivors"
        ] == 1


def test_co_occurrence_parent_pays_no_inductions():
    arm = CoOccurrenceParent(build_catalogue(SMALLEST))
    assert arm.build_ledger.search_expansions == 0


def test_all_evidence_parent_never_misses_and_destroys_the_store():
    """Recall 1.0 under every revocation pattern, at catastrophic precision.

    Its collateral count on every step is every method that did not change.
    This arm is the reason a combined error total is refused: on any such
    total it would look like a reasonable middle option.
    """
    for row in rows_for("all_evidence_parent"):
        assert row["graph_recall"] == 1.0
        assert row["stale_survivors"] == 0
        assert row["graph_precision"] < 0.1
        assert row["believed_edges"] == row["blocks"] * row["methods"]
    for multiplier in MULTIPLIERS:
        scale = f"{multiplier}x"
        methods = next(r for r in rows_for("all_evidence_parent") if r["scale"] == scale)[
            "methods"
        ]
        for record in steps_for("all_evidence_parent", scale):
            changed = record["expected_cone"] - 1  # the withdrawn block itself
            assert record["collateral_invalidations"] == methods - changed


def test_recall_one_does_not_mean_correct():
    """Three arms have recall 1.0 and only one of them is worth having."""
    perfect_recall = {
        arm
        for arm in ARMS
        if all(r["graph_recall"] == 1.0 for r in rows_for(arm))
    }
    assert {"declared_supports_parent", "all_evidence_parent"} <= perfect_recall
    assert SUMMARY["all_evidence_parent"]["total_collateral"] > 100


# --------------------------------------------------------------------------
# the endpoints
# --------------------------------------------------------------------------


def test_the_two_error_kinds_are_never_summed_anywhere_in_the_tables():
    """Asymmetric errors reported separately, as the plan requires."""
    for row in ROWS + STEPS:
        assert "stale_survivors" in row
        assert "collateral_invalidations" in row
        assert not any(
            key
            for key in row
            if "error" in key.lower() or key in ("total_errors", "errors")
        )


def test_stale_survivors_and_collateral_are_disjoint_by_construction():
    for arm_id, per_scale in RESULTS.items():
        for result in per_scale:
            for record in result.revisions:
                assert not set(record.stale_survivor_ids) & set(
                    record.collateral_invalidated_ids
                )


def test_learned_arm_crosses_over_against_both_recomputing_arms():
    """The crossover is the endpoint that decides whether discovery pays.

    Against full recomputation it crosses over quickly, because that arm pays
    ``F`` inductions per revocation.  Against the lazy learner it takes longer,
    because the lazy learner only re-induces what a withdrawn block could
    possibly have touched.  Both must be finite, or the arm under test never
    pays for itself at any workload and the report should say so.
    """
    crossovers = crossovers_for(ROWS)
    for scale, others in crossovers.items():
        assert others["full_recomputation_parent"] is not None
        assert others["lazy_learner_arm"] is not None
        assert others["full_recomputation_parent"] < others["lazy_learner_arm"]


def test_crossover_reports_none_rather_than_a_fabricated_number():
    """An arm that never catches up gets ``None``, not a large integer."""
    assert crossover_revocations(1000.0, 10.0, 0.0, 1.0, horizon=50) is None
    assert crossover_revocations(10.0, 1.0, 0.0, 5.0, horizon=50) == 3
    assert crossover_revocations(0.0, 1.0, 5.0, 1.0, horizon=50) == 1


def test_build_work_grows_with_N_for_the_arm_that_discovers_at_acquisition():
    rows = rows_for("learned_dependency_arm")
    works = [r["build_work"] for r in rows]
    assert works == sorted(works)
    assert works[-1] > works[0] * 5


def test_the_sweep_is_deterministic():
    """Nothing here reads a clock or an unseeded source of randomness."""
    again = sweep_table(sweep(["co_occurrence_parent", "learned_dependency_arm"]))
    mine = [r for r in ROWS if r["arm"] in ("co_occurrence_parent", "learned_dependency_arm")]
    assert sorted(again, key=lambda r: (r["arm"], r["scale"])) == sorted(
        mine, key=lambda r: (r["arm"], r["scale"])
    )


# --------------------------------------------------------------------------
# the records
# --------------------------------------------------------------------------


def test_graph_record_precision_and_recall_edge_cases():
    """An empty claim against a non-empty truth is precision 0, not 1."""
    catalogue = build_catalogue(SMALLEST)
    empty = score_graph("none", catalogue, [], 0)
    assert empty.precision == 0.0
    assert empty.recall == 0.0
    assert not empty.exact
    everything = score_graph("all", catalogue, all_pairs_edges(catalogue), 0)
    assert everything.recall == 1.0
    assert everything.precision < 0.1


def test_a_revision_record_reports_the_true_cone_next_to_the_observed_one():
    """An arm that invalidated nothing cannot be mistaken for one that was right."""
    result = run_arm("declared_supports_parent", SMALLEST)
    for record in result.revisions:
        assert record.expected_cone_size >= 1
        assert record.dependency_recall == 1.0


def test_roles_are_declared_and_every_arm_carries_one():
    assert set(ARM_ROLES) == set(DEPEND_PLAN["arms"])
    assert ARM_ROLES["declared_supports_parent"] == "PARENT_GIFTED_CEILING"
    assert sum(1 for v in ARM_ROLES.values() if v.startswith("PARENT")) == 4


def test_summary_reports_values_per_scale_rather_than_a_mean():
    """An arm that fails at one scale must not be averaged into looking fine."""
    for arm_id, entry in SUMMARY.items():
        assert len(entry["recall_by_scale"]) == len(MULTIPLIERS)
        assert len(entry["stale_survivors_by_scale"]) == len(MULTIPLIERS)


def test_no_parent_matches_the_learned_arm_on_all_four_reported_coordinates():
    """The condition the terminal rule tests, asserted rather than assumed.

    If a parent ever does match on precision, recall, stale survivors and
    total work, the terminal is ``PARENT_SUFFICIENT`` and this test is the
    thing that has to be updated deliberately rather than noticed later.
    """
    learned = SUMMARY["learned_dependency_arm"]
    for name in ("declared_supports_parent", "co_occurrence_parent"):
        other = SUMMARY[name]
        assert (
            other["precision_by_scale"],
            other["recall_by_scale"],
            other["stale_survivors_by_scale"],
            other["total_work_by_scale"],
        ) != (
            learned["precision_by_scale"],
            learned["recall_by_scale"],
            learned["stale_survivors_by_scale"],
            learned["total_work_by_scale"],
        )


# --------------------------------------------------------------------------
# the terminal rule, which was written before the numbers
# --------------------------------------------------------------------------


def test_the_terminal_rule_tests_exactly_the_declared_coordinates():
    """A coordinate added after the fact could keep a parent out; freeze them."""
    import run_depend

    assert run_depend.MATCH_COORDINATES == (
        "precision_by_scale",
        "recall_by_scale",
        "stale_survivors_by_scale",
        "total_work_by_scale",
    )
    assert run_depend.CHALLENGERS == (
        "declared_supports_parent",
        "co_occurrence_parent",
    )


def test_the_terminal_is_the_leave_one_out_limitation():
    """The registered rule, applied to the registered summary."""
    import run_depend

    terminal, reason = run_depend.terminal_for(SUMMARY)
    assert terminal == "LEAVE_ONE_OUT_DISCOVERY_INCOMPLETE"
    assert "redundant" in reason.lower()


def test_parent_sufficient_is_reachable_and_is_tested_first():
    """PARENT_SUFFICIENT is a successful terminal, not a failure branch.

    Constructed here by making a challenger match on the four declared
    coordinates, so the rule's first branch is exercised by a real call rather
    than trusted to be reachable.
    """
    import copy

    import run_depend

    rigged = copy.deepcopy(SUMMARY)
    learned = rigged["learned_dependency_arm"]
    for key in run_depend.MATCH_COORDINATES:
        rigged["co_occurrence_parent"][key] = list(learned[key])
    terminal, reason = run_depend.terminal_for(rigged)
    assert terminal == "PARENT_SUFFICIENT"
    assert "co_occurrence_parent" in reason


def test_a_flawless_learned_arm_would_report_separation_not_success():
    """Even with no stale survivors the terminal names what it compared."""
    import copy

    import run_depend

    rigged = copy.deepcopy(SUMMARY)
    rigged["learned_dependency_arm"]["total_stale_survivors"] = 0
    terminal, _ = run_depend.terminal_for(rigged)
    assert terminal == "DEPENDENCY_DISCOVERY_SEPARATES_FROM_DECLARATION"


def test_the_ground_truth_audit_reports_the_gap_the_prior_pilot_stood_on():
    import run_depend

    audit = run_depend.ground_truth_audit()
    assert len(audit) == len(MULTIPLIERS)
    for row in audit:
        assert 0.0 < row["declared_precision_if_taken_as_truth"] < 1.0
        assert row["methods_with_support_invisible_to_leave_one_out"] > 0
        assert any(
            int(size) >= 2 for size in row["minimal_joint_witnesses_by_size"]
        )
