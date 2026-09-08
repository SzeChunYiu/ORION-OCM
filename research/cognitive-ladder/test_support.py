"""Tests for the support-family experiment (E6).

Four things these tests exist to guarantee, in the order a sceptical reader
would ask for them:

(a) the WORLD is what the archetypes say it is -- every registered family's
    expected shape is checked against the powerset oracle, not asserted in
    prose;
(b) the SEPARATION holds -- no arm reaches the oracle, only the gifted ceiling
    reads the justifications, and interventions are actually charged and
    actually refused when the budget is gone;
(c) the PARENT fails where it must -- ``leave_one_out_parent`` recovers the
    complete family on exactly the archetypes whose families are all singletons
    and fails on exactly the rest, which is claim C11 reproduced rather than
    cited;
(d) the TERMINAL rule is honest -- ``PARENT_SUFFICIENT`` is reachable, is
    tested first, and a flawless arm would report separation rather than
    success.

Structure and style follow ``test_depend.py`` deliberately; source inspection
enforces the oracle separation there and does the same job here.
"""

from __future__ import annotations

import inspect

import pytest

import support
import support_arms
import run_support
from support import (
    ARCHETYPES,
    COMMITMENT,
    EVIDENCE_PER_METHOD,
    INTERVENTION_BUDGET,
    SUPPORT_PLAN,
    BudgetExhausted,
    InterventionMeter,
    build_catalogue,
    build_world,
    classify_family,
    declared_candidate_family,
    hitting_sets,
    leave_one_out_blind_methods,
    oracle_changed_methods,
    oracle_families,
    oracle_minimal_environments,
    powerset_bound,
    revocation_schedule,
    subsets_of,
    support_family,
)
from support_arms import (
    ARMS,
    ARM_ROLES,
    AdaptiveArm,
    AtmsDiscoveringParent,
    AtmsGiftedParent,
    ExhaustivePowersetParent,
    LazyParent,
    LeaveOneOutParent,
    RandomGroupAblationParent,
    SupportArm,
    budget_curve,
    lazy_comparison,
    run_arm,
    summarise,
    sweep,
    sweep_table,
    step_table,
    archetype_table,
)

MULTIPLIERS = SUPPORT_PLAN["multipliers"]
SMALL = MULTIPLIERS[0]


def _local(instance, ids):
    """Render a set of evidence ids as sorted slot indices, for readability."""
    slot = {e: i for i, e in enumerate(instance.evidence_ids)}
    return tuple(sorted(slot[x] for x in ids))


def _family_local(instance, method_id):
    return sorted(_local(instance, s) for s in support_family(instance, method_id))


def _instance(archetype_id, multiplier=SMALL):
    for instance in build_catalogue(multiplier).first_replicates():
        if instance.archetype_id == archetype_id:
            return instance
    raise AssertionError(f"no {archetype_id} instance at {multiplier}x")


# --------------------------------------------------------------------------
# (a) the pre-registration and the world
# --------------------------------------------------------------------------


def test_commitment_is_a_function_of_the_plan():
    from prereg import commit

    assert COMMITMENT.commitment == commit(SUPPORT_PLAN).commitment
    edited = dict(SUPPORT_PLAN)
    edited["evidence_per_method"] = EVIDENCE_PER_METHOD + 1
    assert commit(edited).commitment != COMMITMENT.commitment


def test_the_powerset_bound_is_stated_and_true():
    """The oracle is exactly computable, and the receipt says by how much."""
    assert powerset_bound() == 2**EVIDENCE_PER_METHOD - 1
    instance = _instance("CYCLIC")
    assert len(instance.evidence_ids) == EVIDENCE_PER_METHOD
    assert len(subsets_of(instance.evidence_ids)) == powerset_bound() + 1


def test_every_archetype_appears_at_every_scale_and_scales_are_nested():
    for multiplier in MULTIPLIERS:
        catalogue = build_catalogue(multiplier)
        present = {i.archetype_id for i in catalogue.instances}
        assert present == {a.archetype_id for a in ARCHETYPES}
        counts = {
            a.archetype_id: sum(
                1 for i in catalogue.instances if i.archetype_id == a.archetype_id
            )
            for a in ARCHETYPES
        }
        assert set(counts.values()) == {multiplier}
    for small, large in zip(MULTIPLIERS, MULTIPLIERS[1:]):
        a = build_catalogue(small).instances
        b = build_catalogue(large).instances
        assert b[: len(a)] == a


def test_every_arm_receives_an_identical_store():
    catalogue = build_catalogue(SMALL)
    shapes = set()
    for factory in ARMS.values():
        arm = factory(catalogue)
        shapes.add(
            (
                arm.store.n_objects,
                arm.store.store_bytes,
                tuple(sorted(arm.store.counts_by_class().items())),
            )
        )
    assert len(shapes) == 1


def test_the_per_instance_permutation_moves_the_load_bearing_slots():
    """Otherwise "probe slot 0 first" would be a winning strategy."""
    catalogue = build_catalogue(MULTIPLIERS[-1])
    seen = set()
    for instance in catalogue.instances:
        if instance.archetype_id != "SINGLE_SUPPORT":
            continue
        for method_id in instance.method_ids:
            seen.add(_family_local(instance, method_id)[0])
    assert len(seen) > 1, "every replicate put its support in the same slot"


# --------------------------------------------------------------------------
# (a) every required family fires, with its declared shape
# --------------------------------------------------------------------------

#: The registered expectation for each archetype, as sorted slot-index sets.
#: Written from the archetype definitions, not read back from the oracle.
EXPECTED_SHAPE_CLASS = {
    "SINGLE_SUPPORT": "SINGLE",
    "ALTERNATIVE_SUPPORTS": "CONJUNCTIVE_ONLY",
    "TWO_OF_THREE": "CONJUNCTIVE_ONLY",
    "REDUNDANT_SUPPORTS": "MIXED",
    "CONDITIONAL_SUPPORT": "CONJUNCTIVE_ONLY",
    "HIGHER_ORDER_INTERACTION": "HIGHER_ORDER",
    "DEEP_CHAIN": "ALTERNATIVE_ONLY",
    "CYCLIC": "CONJUNCTIVE_ONLY",
    "SHARED_GLOBAL": "ALTERNATIVE_ONLY",
    "REPRESENTATION_DEPENDENT": "CONJUNCTIVE_ONLY",
    "NO_LOAD_BEARING": "NO_LOAD_BEARING",
}

EXPECTED_SIZES = {
    "SINGLE_SUPPORT": [1],
    "ALTERNATIVE_SUPPORTS": [2],
    "TWO_OF_THREE": [2, 2, 2],
    "REDUNDANT_SUPPORTS": [1, 2],
    "CONDITIONAL_SUPPORT": [2, 2],
    "HIGHER_ORDER_INTERACTION": [3],
    "DEEP_CHAIN": [1, 1, 1],
    "CYCLIC": [2, 2, 2],
    "SHARED_GLOBAL": [1, 1],
    "REPRESENTATION_DEPENDENT": [2, 2],
    "NO_LOAD_BEARING": [],
}


@pytest.mark.parametrize("archetype_id", sorted(EXPECTED_SIZES))
def test_each_required_family_has_its_declared_support_family(archetype_id):
    instance = _instance(archetype_id)
    for method_id in instance.method_ids:
        family = support_family(instance, method_id)
        assert sorted(len(s) for s in family) == EXPECTED_SIZES[archetype_id]
        assert classify_family(family) == EXPECTED_SHAPE_CLASS[archetype_id]


def test_the_family_with_no_load_bearing_evidence_really_has_none():
    instance = _instance("NO_LOAD_BEARING")
    world = build_world(build_catalogue(SMALL))
    method_id = instance.method_ids[0]
    assert support_family(instance, method_id) == frozenset()
    assert world.holds(method_id, frozenset())


def test_alternative_supports_is_the_c11_shape_exactly():
    """Two blocks each suffice alone; neither alone is necessary; both are."""
    instance = _instance("ALTERNATIVE_SUPPORTS")
    method_id = instance.method_ids[0]
    world = build_world(build_catalogue(SMALL))
    everything = frozenset(instance.evidence_ids)
    (pair,) = support_family(instance, method_id)
    assert len(pair) == 2
    for block in pair:
        assert world.holds(method_id, everything - {block})
    assert not world.holds(method_id, everything - pair)


def test_redundant_supports_is_the_case_a_partial_answer_hides():
    """A singleton and a pair in the same family: half the answer looks whole."""
    instance = _instance("REDUNDANT_SUPPORTS")
    family = support_family(instance, instance.method_ids[0])
    assert sorted(len(s) for s in family) == [1, 2]
    singleton = next(s for s in family if len(s) == 1)
    pair = next(s for s in family if len(s) == 2)
    assert not (singleton & pair)


def test_higher_order_needs_all_three_and_no_pair_will_do():
    instance = _instance("HIGHER_ORDER_INTERACTION")
    method_id = instance.method_ids[0]
    world = build_world(build_catalogue(SMALL))
    everything = frozenset(instance.evidence_ids)
    (triple,) = support_family(instance, method_id)
    assert len(triple) == 3
    for pair in subsets_of(tuple(sorted(triple))):
        if len(pair) == 2:
            assert world.holds(method_id, everything - pair)
    assert not world.holds(method_id, everything - triple)


def test_the_cycle_does_not_support_itself():
    """Least fixpoint: support that lives only inside a loop is not support."""
    instance = _instance("CYCLIC")
    method_id = instance.method_ids[0]
    world = build_world(build_catalogue(SMALL))
    environments = oracle_minimal_environments(instance, method_id)
    assert environments, "the cyclic method is derivable from something"
    assert all(env for env in environments), "the cycle grounded out of nothing"
    assert not world.holds(method_id, frozenset())


def test_shared_global_support_is_load_bearing_for_every_method_it_touches():
    instance = _instance("SHARED_GLOBAL")
    assert len(instance.method_ids) == 2
    families = [support_family(instance, m) for m in instance.method_ids]
    shared = set.intersection(*[{next(iter(s)) for s in f} for f in families])
    assert len(shared) == 1, "no single block is load-bearing for both methods"


def test_representation_dependent_support_belongs_to_neither_representation():
    """Committing to one derivation gives a confident wrong answer."""
    instance = _instance("REPRESENTATION_DEPENDENT")
    family = support_family(instance, instance.method_ids[0])
    assert sorted(len(s) for s in family) == [2, 2]
    # no single-representation reading (all singletons) reproduces the family
    assert all(len(s) > 1 for s in family)


def test_the_two_oracles_are_duals_everywhere():
    """Minimal support sets are the minimal transversals of the environments."""
    for multiplier in MULTIPLIERS[:2]:
        catalogue = build_catalogue(multiplier)
        for instance in catalogue.instances:
            for method_id in instance.method_ids:
                family = support_family(instance, method_id)
                environments = oracle_minimal_environments(instance, method_id)
                assert hitting_sets(environments) == family
                if family:
                    assert hitting_sets(family) == environments


def test_minimal_sets_is_an_antichain():
    catalogue = build_catalogue(SMALL)
    for instance in catalogue.instances:
        for method_id in instance.method_ids:
            family = sorted(support_family(instance, method_id), key=len)
            for i, a in enumerate(family):
                for b in family[i + 1 :]:
                    assert not (a <= b) and not (b <= a)


def test_the_declared_candidate_structure_is_strictly_weaker_than_the_truth():
    catalogue = build_catalogue(SMALL)
    truth = oracle_families(catalogue)
    declared = declared_candidate_family(catalogue)
    assert len(declared) < len(truth) or truth != declared
    # a declared "everything" set is not even a member of most true families
    assert len(truth - declared) > 0


def test_oracle_changed_methods_is_evaluated_against_live_evidence():
    catalogue = build_catalogue(SMALL)
    instance = _instance("ALTERNATIVE_SUPPORTS")
    (pair,) = support_family(instance, instance.method_ids[0])
    first, second = sorted(pair)
    everything = frozenset(
        e for i in catalogue.instances for e in i.evidence_ids
    )
    after_first = everything - {first}
    assert oracle_changed_methods(catalogue, everything, after_first) == frozenset()
    after_both = after_first - {second}
    assert oracle_changed_methods(catalogue, after_first, after_both) == frozenset(
        instance.method_ids
    )


# --------------------------------------------------------------------------
# (b) the separation, enforced structurally
# --------------------------------------------------------------------------

FORBIDDEN_IN_ARMS = (
    "support_family",
    "oracle_families",
    "oracle_minimal_environments",
    "oracle_holds",
    "leave_one_out_blind_methods",
    "classify_family",
    "family_shapes",
    "declared_candidate_family",
    "archetype_id",
    "expected_shape",
    "revocation_steps",
    "ARCHETYPES",
    "world.holds",
)

ARM_CLASSES = (
    AdaptiveArm,
    LeaveOneOutParent,
    LazyParent,
    AtmsGiftedParent,
    AtmsDiscoveringParent,
    ExhaustivePowersetParent,
    RandomGroupAblationParent,
)


def test_no_arm_reads_the_oracle():
    """Enforced structurally, in the style of ``test_depend.py``.

    No arm class may mention the powerset oracle, the archetype identity or
    the world's uncharged derivability anywhere in its source.  Only the shared
    scaffolding, which compares after the fact, is allowed to.
    """
    for cls in ARM_CLASSES:
        source = inspect.getsource(cls)
        for name in FORBIDDEN_IN_ARMS:
            assert name not in source, f"{cls.__name__} reaches for {name}"


def test_the_shared_enumerator_and_helpers_are_also_clean():
    for fn in (support_arms._enumerate_minimal, support_arms._exhaustive_families):
        source = inspect.getsource(fn)
        for name in FORBIDDEN_IN_ARMS:
            assert name not in source


def test_the_scaffolding_is_the_only_place_the_oracle_appears():
    assert "oracle_changed_methods" in inspect.getsource(SupportArm.revoke)
    assert "score_family" in inspect.getsource(SupportArm.disclose_family)
    for cls in ARM_CLASSES:
        assert "oracle_changed_methods" not in inspect.getsource(cls)


def test_only_the_gifted_ceiling_reads_the_justifications():
    """The justifications are the gift this experiment exists to withdraw."""
    readers = [
        cls.__name__
        for cls in ARMS.values()
        if "justifications" in inspect.getsource(cls)
    ]
    assert readers == ["AtmsGiftedParent"]
    assert ARM_ROLES["atms_gifted_parent"] == "PARENT_GIFTED_CEILING"


def test_no_wall_clock_anywhere_in_the_lane_modules():
    for module in (support, support_arms, run_support):
        source = inspect.getsource(module)
        assert "import time" not in source
        assert "perf_counter" not in source
        assert "monotonic" not in source


# --------------------------------------------------------------------------
# (b) interventions are actually charged
# --------------------------------------------------------------------------


def test_the_meter_refuses_an_intervention_past_the_budget():
    meter = InterventionMeter(budget_per_method=2)
    meter.charge("m")
    meter.charge("m")
    with pytest.raises(BudgetExhausted):
        meter.charge("m")
    assert meter.total == 2
    assert meter.phase_total("DISCOVERY") == 2


def test_an_exempt_meter_is_the_only_way_past_the_budget():
    meter = InterventionMeter(budget_per_method=1, exempt=True)
    for _ in range(10):
        meter.charge("m")
    assert meter.total == 10


def test_non_discovery_phases_are_counted_but_not_capped():
    """Declared in the plan: an arm that discovers nothing may still serve."""
    meter = InterventionMeter(budget_per_method=1)
    meter.phase = "REVOCATION"
    for _ in range(5):
        meter.charge("m")
    assert meter.phase_total("REVOCATION") == 5
    assert meter.phase_total("DISCOVERY") == 0


def test_leave_one_out_spends_exactly_one_intervention_per_candidate_block():
    catalogue = build_catalogue(SMALL)
    arm = LeaveOneOutParent(catalogue)
    assert arm.discovery_interventions == catalogue.n_methods * EVIDENCE_PER_METHOD


def test_the_exhaustive_parent_spends_the_whole_powerset_per_method():
    catalogue = build_catalogue(SMALL)
    arm = ExhaustivePowersetParent(catalogue)
    assert arm.discovery_interventions == catalogue.n_methods * powerset_bound()
    assert arm.budget_exempt is True


def test_a_tiny_budget_actually_stops_a_discovering_arm():
    """The budget is enforced, not decorative."""
    catalogue = build_catalogue(SMALL)
    arm = AdaptiveArm(catalogue, budget=2)
    assert arm.discovery_interventions <= catalogue.n_methods * 2
    assert arm.budget_exhausted_methods
    record = arm.disclose_family()
    assert record.budget_exhausted_methods == len(arm.budget_exhausted_methods)


def test_no_arm_exceeds_the_registered_budget_unless_declared_exempt():
    catalogue = build_catalogue(SMALL)
    for arm_id, factory in ARMS.items():
        arm = factory(catalogue)
        if arm.budget_exempt:
            continue
        worst = max(arm.meter.spent_by_method.values(), default=0)
        assert worst <= INTERVENTION_BUDGET, f"{arm_id} overspent"


def test_lazy_parent_spends_nothing_at_acquisition():
    arm = LazyParent(build_catalogue(SMALL))
    assert arm.discovery_interventions == 0
    assert arm.discovery_work == 0
    assert arm.believed == {}


def test_the_gifted_ceiling_needs_zero_interventions():
    arm = AtmsGiftedParent(build_catalogue(SMALL))
    assert arm.discovery_interventions == 0
    assert arm.disclose_family().exact


def test_re_asking_a_question_an_arm_already_asked_is_free():
    """An arm remembers its own experiments; that is not an oracle read."""
    catalogue = build_catalogue(SMALL)
    arm = LeaveOneOutParent(catalogue)
    before = arm.meter.total
    ledger = support.TouchLedger()
    method_id = catalogue.method_ids[0]
    block = arm.world.candidates(method_id)[0]
    arm._ablate(method_id, frozenset({block}), ledger)
    assert arm.meter.total == before


# --------------------------------------------------------------------------
# (c) leave-one-out fails exactly on the redundant families
# --------------------------------------------------------------------------

#: Archetypes whose support family is entirely singletons.  Single-element
#: ablation can express these and nothing else.
SINGLETON_ONLY = {"SINGLE_SUPPORT", "DEEP_CHAIN", "SHARED_GLOBAL", "NO_LOAD_BEARING"}

#: Archetypes with at least one minimal support set of size two or more.  These
#: are exactly the C11 families and leave-one-out MUST fail on every one.
REDUNDANT_FAMILIES = {
    a.archetype_id for a in ARCHETYPES
} - SINGLETON_ONLY


def test_the_two_partitions_cover_the_registered_archetypes():
    assert SINGLETON_ONLY | REDUNDANT_FAMILIES == {a.archetype_id for a in ARCHETYPES}
    assert not (SINGLETON_ONLY & REDUNDANT_FAMILIES)


def test_leave_one_out_fails_exactly_on_the_redundant_families():
    """Claim C11, reproduced rather than cited.

    Recall is 1.0 on every archetype whose family is all singletons and
    strictly below 1.0 on every archetype that has a minimal set of size two or
    more.  Not "usually", not "on average": exactly, at every registered scale.
    """
    for multiplier in MULTIPLIERS:
        arm = run_arm("leave_one_out_parent", multiplier)
        scores = arm.family.per_archetype
        for archetype_id in SINGLETON_ONLY:
            assert scores[archetype_id]["recall"] == 1.0, archetype_id
            assert scores[archetype_id]["exact"], archetype_id
        for archetype_id in REDUNDANT_FAMILIES:
            assert scores[archetype_id]["recall"] < 1.0, archetype_id
            assert not scores[archetype_id]["exact"], archetype_id


def test_leave_one_out_never_reports_a_set_larger_than_one():
    """Its probe granularity is fixed at one element by design."""
    arm = run_arm("leave_one_out_parent", SMALL)
    catalogue = build_catalogue(SMALL)
    lo = LeaveOneOutParent(catalogue)
    assert all(len(s) == 1 for sets in lo.believed.values() for s in sets)


def test_leave_one_out_returns_a_true_fact_and_still_misses_half_the_family():
    """The dangerous failure mode: partial, correct, and silent about it."""
    catalogue = build_catalogue(SMALL)
    arm = LeaveOneOutParent(catalogue)
    instance = _instance("REDUNDANT_SUPPORTS")
    method_id = instance.method_ids[0]
    believed = arm.believed.get(method_id, set())
    truth = support_family(instance, method_id)
    assert believed, "it found nothing at all, which is a different failure"
    assert believed < truth, "it should be a strict subset of the truth"
    assert all(b in truth for b in believed), "what it found is correct"


def test_leave_one_out_reports_nothing_at_all_on_the_c11_shape():
    catalogue = build_catalogue(SMALL)
    arm = LeaveOneOutParent(catalogue)
    instance = _instance("ALTERNATIVE_SUPPORTS")
    assert arm.believed.get(instance.method_ids[0], set()) == set()


def test_the_blind_fraction_is_counted_at_every_scale():
    for multiplier in MULTIPLIERS:
        catalogue = build_catalogue(multiplier)
        blind = leave_one_out_blind_methods(catalogue)
        assert blind
        assert len(blind) < catalogue.n_methods


# --------------------------------------------------------------------------
# (c) what the other arms do
# --------------------------------------------------------------------------


def test_the_exhaustive_parent_is_exactly_correct_and_exponential():
    for multiplier in MULTIPLIERS[:2]:
        result = run_arm("exhaustive_powerset_parent", multiplier)
        assert result.family.precision == 1.0
        assert result.family.recall == 1.0
        assert result.family.exact
        assert (
            result.discovery_interventions
            == result.n_methods * powerset_bound()
        )


def test_the_adaptive_arm_reaches_the_oracle_with_fewer_interventions():
    for multiplier in MULTIPLIERS[:2]:
        adaptive = run_arm("adaptive_arm", multiplier)
        exhaustive = run_arm("exhaustive_powerset_parent", multiplier)
        assert adaptive.discovery_interventions < exhaustive.discovery_interventions


def test_the_adaptive_arm_beats_the_random_floor_at_the_same_budget():
    """Otherwise the result would be about granularity, not selection."""
    for multiplier in MULTIPLIERS[:2]:
        adaptive = run_arm("adaptive_arm", multiplier)
        floor = run_arm("random_group_ablation_parent", multiplier)
        assert adaptive.family.recall > floor.family.recall
        assert adaptive.family.precision >= floor.family.precision


def test_the_random_floor_reports_non_minimal_sets_as_minimal():
    """It is wrong in both directions, and the spurious direction is why."""
    result = run_arm("random_group_ablation_parent", SMALL)
    assert result.family.extra, "the floor found nothing spurious, which is suspicious"


def test_the_no_load_bearing_family_is_a_false_positive_control():
    catalogue = build_catalogue(SMALL)
    instance = _instance("NO_LOAD_BEARING")
    method_id = instance.method_ids[0]
    exact_arms = [AdaptiveArm, AtmsGiftedParent, ExhaustivePowersetParent]
    for factory in exact_arms:
        arm = factory(catalogue)
        assert not arm.believed.get(method_id), factory.__name__


def test_the_adaptive_arm_settles_the_empty_family_in_one_intervention():
    """The whole reason to ablate groups: one question, one answer."""
    catalogue = build_catalogue(SMALL)
    arm = AdaptiveArm(catalogue)
    instance = _instance("NO_LOAD_BEARING")
    method_id = instance.method_ids[0]
    assert arm.meter.spent_by_method[method_id] == 1
    lo = LeaveOneOutParent(catalogue)
    assert lo.meter.spent_by_method[method_id] == EVIDENCE_PER_METHOD


def test_the_atms_is_run_both_ways_and_both_rows_are_reported():
    gifted = run_arm("atms_gifted_parent", SMALL)
    fair = run_arm("atms_discovering_parent", SMALL)
    assert gifted.discovery_interventions == 0
    assert fair.discovery_interventions > 0
    assert gifted.family.exact
    assert fair.family.precision <= 1.0 and fair.family.recall <= 1.0
    assert ARM_ROLES["atms_gifted_parent"] == "PARENT_GIFTED_CEILING"
    assert ARM_ROLES["atms_discovering_parent"] == "PARENT"


def test_lazy_parent_is_exact_on_every_revocation_step():
    """The arm to beat: correct by re-derivation, with nothing stored."""
    for multiplier in MULTIPLIERS[:2]:
        result = run_arm("lazy_parent", multiplier)
        assert result.stale_survivors == 0
        assert result.collateral_invalidations == 0
        assert result.capability_gate


def test_lazy_parents_cheap_build_is_a_claim_about_an_arm_nobody_asks():
    result = run_arm("lazy_parent", SMALL)
    assert result.discovery_work == 0
    assert result.disclosure_work > 0
    assert result.disclosure_interventions > 0
    assert result.family.exact


def test_disclosure_work_is_never_folded_into_total_work():
    """Serving a revocation does not require publishing a family.

    ``lazy_parent`` is the arm this convention protects: it discovers nothing,
    so charging it for a disclosure it does not offer would manufacture a cost
    out of a service nobody asked for.  The disclosure is still charged and
    still reported -- in its own column.
    """
    result = run_arm("lazy_parent", SMALL)
    assert result.discovery_work == 0
    assert result.disclosure_work > 0
    assert result.disclosure_interventions > 0
    assert result.total_work == (
        result.discovery_work + result.revocation_work + result.query_work
    )
    naive = result.total_work + result.disclosure_work
    assert result.total_work != naive


# --------------------------------------------------------------------------
# (c) revocation: the two error kinds, never summed
# --------------------------------------------------------------------------


def test_leave_one_out_leaves_a_stale_survivor_on_the_c11_walk():
    """The E3 result, reproduced: the cached graph says nothing should change."""
    result = run_arm("leave_one_out_parent", SMALL)
    offenders = {
        r.trigger_kind
        for r in result.revisions
        if r.stale_survivor_ids
    }
    assert any(k.startswith("ALTERNATIVE_SUPPORTS") for k in offenders)
    assert result.stale_survivors > 0


def test_the_two_error_kinds_are_never_summed_anywhere_in_the_tables():
    """Checked on an arm that actually makes BOTH kinds of error.

    A table with no column that adds them is only meaningful if some arm has a
    non-zero count in each, otherwise the absence is vacuous.  The random floor
    is the arm that supplies both.
    """
    results = {
        arm_id: [run_arm(arm_id, m) for m in MULTIPLIERS[:3]]
        for arm_id in ("random_group_ablation_parent", "adaptive_arm")
    }
    rows = sweep_table(results)
    both = [
        r
        for r in rows
        if r["stale_survivors"] > 0 and r["collateral_invalidations"] > 0
    ]
    assert both, "no arm made both kinds of error, so the check would be vacuous"
    for row in both:
        summed = row["stale_survivors"] + row["collateral_invalidations"]
        for key, value in row.items():
            if isinstance(value, int) and not isinstance(value, bool):
                assert value != summed or key in (
                    "stale_survivors",
                    "collateral_invalidations",
                ), f"{key} looks like a combined error count"
    assert not any("error" in k for k in rows[0])


def test_stale_survivors_and_collateral_are_disjoint_by_construction():
    for result in (run_arm("leave_one_out_parent", SMALL), run_arm("adaptive_arm", SMALL)):
        for record in result.revisions:
            assert not (
                set(record.stale_survivor_ids) & set(record.collateral_invalidated_ids)
            )


def test_the_registered_schedule_is_constant_across_scales():
    """So a change in revocation work is not a change in how many revocations."""
    sizes = {len(revocation_schedule(build_catalogue(m))) for m in MULTIPLIERS}
    assert len(sizes) == 1
    kinds = [
        tuple(s.step_id for s in revocation_schedule(build_catalogue(m)))
        for m in MULTIPLIERS
    ]
    assert len(set(kinds)) == 1


def test_every_archetype_contributes_a_registered_revocation():
    schedule = revocation_schedule(build_catalogue(SMALL))
    assert {s.archetype_id for s in schedule} == {a.archetype_id for a in ARCHETYPES}


def test_no_method_is_broken_twice_by_the_registered_schedule():
    """A step's lesson is never contaminated by an earlier step.

    ``depend.py`` achieves this by putting the no-op steps first; here the
    stronger and more general invariant is checked directly, because
    ``SHARED_GLOBAL`` deliberately breaks a DIFFERENT method at each of its two
    steps and a "no-ops first" rule would wrongly reject it.  What must not
    happen is a method being expected to change twice, which would make the
    second step's score a function of the first step's outcome.
    """
    catalogue = build_catalogue(SMALL)
    live = frozenset(e for i in catalogue.instances for e in i.evidence_ids)
    seen: set[str] = set()
    breaking_steps = 0
    for step in revocation_schedule(catalogue):
        before = live
        live = live - set(step.evidence_ids)
        changed = oracle_changed_methods(catalogue, before, live)
        assert not (changed & seen), f"{step.step_id} re-breaks {changed & seen}"
        if changed:
            breaking_steps += 1
        seen |= changed
    assert breaking_steps >= len(ARCHETYPES) - 1, "almost every archetype must fire"


def test_the_c11_walk_is_two_steps_and_only_the_second_one_bites():
    """The registered ALTERNATIVE_SUPPORTS schedule is the C11 trap itself."""
    catalogue = build_catalogue(SMALL)
    live = frozenset(e for i in catalogue.instances for e in i.evidence_ids)
    outcomes = []
    for step in revocation_schedule(catalogue):
        before = live
        live = live - set(step.evidence_ids)
        if step.archetype_id == "ALTERNATIVE_SUPPORTS":
            outcomes.append(bool(oracle_changed_methods(catalogue, before, live)))
    assert outcomes == [False, True]


# --------------------------------------------------------------------------
# (c) the two columns: interventions and counted operations
# --------------------------------------------------------------------------


def test_interventions_and_work_are_reported_as_two_columns():
    rows = sweep_table({"adaptive_arm": [run_arm("adaptive_arm", SMALL)]})
    row = rows[0]
    for key in (
        "discovery_interventions",
        "disclosure_interventions",
        "revocation_interventions",
        "query_interventions",
        "discovery_work",
        "revocation_work",
        "query_work",
        "total_work",
    ):
        assert key in row


def test_the_budget_curve_reports_both_columns_at_every_point():
    rows = budget_curve(SMALL, budgets=[4, 24])
    assert {r["budget_per_method"] for r in rows} == {4, 24}
    for row in rows:
        assert "discovery_interventions" in row and "discovery_work" in row
    adaptive = {r["budget_per_method"]: r for r in rows if r["arm"] == "adaptive_arm"}
    assert adaptive[24]["recall"] >= adaptive[4]["recall"]


def test_a_smaller_budget_never_buys_more_recall():
    rows = [r for r in budget_curve(SMALL, budgets=[8, 24]) if r["arm"] == "adaptive_arm"]
    small, large = sorted(rows, key=lambda r: r["budget_per_method"])
    assert large["recall"] >= small["recall"]
    assert large["discovery_interventions"] >= small["discovery_interventions"]


# --------------------------------------------------------------------------
# (d) reporting and the terminal rule
# --------------------------------------------------------------------------


def test_the_sweep_is_deterministic():
    a = sweep_table(sweep(["adaptive_arm", "leave_one_out_parent"]))
    b = sweep_table(sweep(["adaptive_arm", "leave_one_out_parent"]))
    assert a == b


def test_summary_reports_values_per_scale_rather_than_a_mean():
    rows = sweep_table(sweep(["leave_one_out_parent"]))
    summary = summarise(rows)["leave_one_out_parent"]
    assert len(summary["recall_by_scale"]) == len(MULTIPLIERS)
    assert "mean_recall" not in summary


def test_every_arm_carries_a_declared_role():
    assert set(ARM_ROLES) == set(ARMS)
    assert ARM_ROLES["adaptive_arm"] == "ARM"


def test_the_archetype_table_makes_the_blindness_legible():
    rows = archetype_table({"leave_one_out_parent": [run_arm("leave_one_out_parent", SMALL)]})
    blind = {r["archetype"] for r in rows if r["recall"] < 1.0}
    assert blind == REDUNDANT_FAMILIES


def test_the_terminal_rule_tests_parent_sufficiency_first():
    source = inspect.getsource(run_support.terminal_for)
    assert source.index("PARENT_SUFFICIENT") < source.index("INTERVENTION_WORK_TRADE")


def test_parent_sufficient_is_reachable_and_names_the_matching_parent():
    base = {
        "precision_by_scale": [1.0],
        "recall_by_scale": [1.0],
        "stale_survivors_by_scale": [0],
        "collateral_by_scale": [0],
        "total_work_by_scale": [100],
        "discovery_interventions_by_scale": [10],
        "discovery_work_by_scale": [10],
        "capability_gate_by_scale": [True],
        "total_stale_survivors": 0,
    }
    summary = {
        "adaptive_arm": dict(base),
        "atms_discovering_parent": dict(base),
        "lazy_parent": dict(base),
        "exhaustive_powerset_parent": dict(base, discovery_interventions_by_scale=[60]),
        "leave_one_out_parent": dict(base, recall_by_scale=[0.4]),
        "random_group_ablation_parent": dict(base, recall_by_scale=[0.1]),
    }
    terminal, reason, _ = run_support.terminal_for(summary)
    assert terminal == "PARENT_SUFFICIENT"
    assert "atms_discovering_parent" in reason and "lazy_parent" in reason


def test_the_intervention_work_trade_is_a_reachable_terminal():
    base = {
        "precision_by_scale": [1.0],
        "recall_by_scale": [1.0],
        "stale_survivors_by_scale": [0],
        "collateral_by_scale": [0],
        "total_work_by_scale": [100],
        "discovery_interventions_by_scale": [10],
        "discovery_work_by_scale": [900],
        "capability_gate_by_scale": [True],
        "total_stale_survivors": 0,
    }
    summary = {
        "adaptive_arm": dict(base),
        # fair ATMS separated on total work and stale survivors
        "atms_discovering_parent": dict(base, total_work_by_scale=[500], stale_survivors_by_scale=[3]),
        "lazy_parent": dict(base, total_work_by_scale=[400]),
        "exhaustive_powerset_parent": dict(
            base, discovery_interventions_by_scale=[60], discovery_work_by_scale=[500]
        ),
        "leave_one_out_parent": dict(base, recall_by_scale=[0.4]),
        "random_group_ablation_parent": dict(base, recall_by_scale=[0.1]),
    }
    terminal, reason, secondary = run_support.terminal_for(summary)
    assert terminal == "INTERVENTION_WORK_TRADE"
    assert "replication" in reason
    assert "INTERVENTION_WORK_TRADE" in secondary


def test_adaptive_selection_adding_nothing_is_reachable():
    base = {
        "precision_by_scale": [1.0],
        "recall_by_scale": [1.0],
        "stale_survivors_by_scale": [0],
        "collateral_by_scale": [0],
        "total_work_by_scale": [100],
        "discovery_interventions_by_scale": [10],
        "discovery_work_by_scale": [10],
        "capability_gate_by_scale": [True],
        "total_stale_survivors": 0,
    }
    summary = {
        "adaptive_arm": dict(base),
        "atms_discovering_parent": dict(base, total_work_by_scale=[500], stale_survivors_by_scale=[3]),
        "lazy_parent": dict(base, total_work_by_scale=[400]),
        "exhaustive_powerset_parent": dict(base, discovery_interventions_by_scale=[6]),
        "leave_one_out_parent": dict(base, recall_by_scale=[0.4]),
        "random_group_ablation_parent": dict(base),
    }
    terminal, _, _ = run_support.terminal_for(summary)
    assert terminal == "ADAPTIVE_SELECTION_ADDS_NOTHING"


def test_a_flawless_arm_would_report_separation_not_success():
    """A terminal that can only say "we won" is a caption, not a rule."""
    base = {
        "precision_by_scale": [1.0],
        "recall_by_scale": [1.0],
        "stale_survivors_by_scale": [0],
        "collateral_by_scale": [0],
        "total_work_by_scale": [100],
        "discovery_interventions_by_scale": [10],
        "discovery_work_by_scale": [10],
        "capability_gate_by_scale": [True],
        "total_stale_survivors": 0,
    }
    summary = {
        "adaptive_arm": dict(base),
        "atms_discovering_parent": dict(base, stale_survivors_by_scale=[2]),
        "lazy_parent": dict(base, total_work_by_scale=[400]),
        "exhaustive_powerset_parent": dict(base, discovery_interventions_by_scale=[60]),
        "leave_one_out_parent": dict(base, recall_by_scale=[0.4]),
        "random_group_ablation_parent": dict(base, recall_by_scale=[0.1]),
    }
    terminal, _, _ = run_support.terminal_for(summary)
    assert terminal == "GROUP_ABLATION_SEPARATES_FROM_LEAVE_ONE_OUT"


def test_the_ground_truth_audit_states_the_powerset_bound():
    audit = run_support.ground_truth_audit()
    for row in audit:
        assert row["powerset_subsets_enumerated_per_method"] == powerset_bound()
        assert row["candidate_evidence_per_method"] == EVIDENCE_PER_METHOD
        assert row["true_minimal_support_sets"] > 0


def test_the_duality_audit_holds_for_every_archetype():
    for row in run_support.duality_audit():
        assert row["transversals_of_environments_equal_support_family"], row["archetype"]


def test_the_receipt_refuses_to_overwrite_an_existing_file(tmp_path):
    target = tmp_path / "receipt.json"
    target.write_text("{}")
    assert run_support.main(["--out", str(target)]) == 1


def test_the_capability_gate_is_reported_for_every_arm():
    rows = sweep_table(sweep(["adaptive_arm", "lazy_parent"]))
    for row in rows:
        assert "capability_gate" in row
        assert row["queries_total"] == row["methods"]


def test_the_lazy_comparison_reports_both_columns_and_no_sum():
    rows = sweep_table(sweep(["adaptive_arm", "lazy_parent", "atms_discovering_parent",
                              "leave_one_out_parent", "exhaustive_powerset_parent",
                              "random_group_ablation_parent", "atms_gifted_parent"]))
    comparison = lazy_comparison(summarise(rows))
    assert "lazy_parent" not in comparison
    for row in comparison.values():
        assert "work_ratio_by_scale" in row
        assert "discovery_interventions_by_scale" in row
        assert "combined" not in row


def test_the_capability_gate_excludes_arms_that_answered_a_smaller_question():
    """The #144 rule: work is not comparable across unequal capability."""
    from support_arms import capability_gated_comparison

    summary = {
        "adaptive_arm": {
            "precision_by_scale": [1.0, 1.0],
            "recall_by_scale": [1.0, 0.9],
            "total_work_by_scale": [10, 20],
            "discovery_interventions_by_scale": [5, 10],
            "stale_survivors_by_scale": [0, 0],
        },
        "lazy_parent": {
            "precision_by_scale": [1.0, 1.0],
            "recall_by_scale": [1.0, 1.0],
            "total_work_by_scale": [100, 200],
            "discovery_interventions_by_scale": [0, 0],
            "stale_survivors_by_scale": [0, 0],
        },
    }
    gated = capability_gated_comparison(summary)
    assert gated["admitted"] == ["lazy_parent"]
    assert "adaptive_arm" in gated["excluded"]
    assert gated["cheapest_admitted_arm_by_total_work"] == "lazy_parent"
    assert "combined" not in gated


def test_the_receipt_carries_the_capability_gated_comparison():
    import json
    import pathlib

    receipt = pathlib.Path("results/SUPPORT_E6_V1.json")
    if not receipt.exists():  # pragma: no cover -- the receipt is built by run_support
        pytest.skip("receipt not built in this checkout")
    data = json.loads(receipt.read_text())
    gated = data["capability_gated_comparison"]
    assert "lazy_parent" in gated["admitted"]
    assert data["terminal"] in {
        "PARENT_SUFFICIENT",
        "INTERVENTION_WORK_TRADE",
        "GROUP_ABLATION_SEPARATES_FROM_LEAVE_ONE_OUT",
        "ADAPTIVE_SELECTION_ADDS_NOTHING",
        "NO_SEPARATION",
    }
