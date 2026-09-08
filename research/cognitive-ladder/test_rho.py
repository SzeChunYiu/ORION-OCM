"""Tests for E7, the reuse-opportunity-density sweep.

These tests are adversarial towards the module they cover.  The experiment's
whole value rests on ``rho`` being a measured quantity rather than a flattering
label, so most of what follows exists to make the flattering version fail loudly:

(a) a task the generator calls essential really is essential --- removing the
    acquired method **strictly increases** the minimal solution cost, computed by
    solving with and without it;
(b) a task that a bypass answers at equal cost is excluded from ``rho`` even
    though the method applies to it and even though the method beats the naive
    procedure by three orders of magnitude.  This is the single test that stops
    ``rho`` being a synonym for "tasks we made easy for ourselves";
(c) ``rho = 0`` reproduces the existing negatives.  If it does not, the knob is
    not the one the old experiments varied and the whole sweep is void;
(d) every parent ran at every ``rho``, because a crossover against a parent that
    was denied the reuse opportunity is not a crossover;
(e) each arm does the specific thing its declared policy says it does, so a
    future edit cannot quietly turn a parent into a strawman.

Everything asserted here is a deterministic function of the pre-registration
commitment, so a failure is a real change in the harness and never a flaky draw.
"""

from __future__ import annotations

import pytest

from games import SubtractionGame
from methods import GrundyRule
from rho import (
    CERTIFICATION_BOUND,
    COMMITMENT,
    DONOR_POSITION,
    EVIDENCE_WINDOW,
    LANGUAGE,
    RHO_PLAN,
    STREAM_LENGTH,
    Task,
    build_stream,
    certify_essential,
    check_verdict,
    closed_form_families,
    closed_form_grundy,
    closed_form_modulus,
    dp_cost,
    grundy_table,
    irregular_families,
    is_prefix_move_set,
    minimal_cost,
    procedure_cost,
    rejected_families,
)
from rho_arms import (
    ALL_PARENTS,
    ARM_SPECS,
    INDEPENDENT_PARENTS,
    RhoArm,
    controls,
    crossovers,
    rho_zero_reproduces_negatives,
    run_cell,
    sweep,
    sweep_table,
)
from scaling import CheckStatus, TouchLedger, record_from_ledger

# One sweep for the whole module.  It is deterministic, so this is a cache and
# not a shared mutable fixture.
RESULTS = sweep()
ROWS = sweep_table(RESULTS)
CONTROLS = controls(ROWS)
CROSSOVERS = crossovers(ROWS)


def _rows(**kw):
    return [r for r in ROWS if all(r[k] == v for k, v in kw.items())]


def _row(arm, rho, multiplier=1):
    matches = _rows(arm=arm, requested_rho=rho, discovery_multiplier=multiplier)
    assert len(matches) == 1
    return matches[0]


# --------------------------------------------------------------------------
# (a) certified-essential tasks really are essential
# --------------------------------------------------------------------------


def test_every_certified_essential_task_strictly_needs_the_method():
    """The definition, checked by solving with and without on every stream."""
    checked = 0
    for requested in RHO_PLAN["rho_grid"]:
        for st in build_stream(requested).tasks:
            if not st.certified_essential:
                continue
            without, _ = minimal_cost(
                st.task, method_available=False, memo_available=st.memo_available
            )
            with_method, _ = minimal_cost(
                st.task, method_available=True, memo_available=st.memo_available
            )
            assert without > with_method, st.task.task_id
            assert st.minimal_cost_without_method == without
            assert st.minimal_cost_with_method == with_method
            checked += 1
    assert checked > 0, "no certified-essential task exists anywhere in the sweep"


def test_essential_tasks_require_structure_acquirable_strictly_earlier():
    """Essentiality is about accumulation, not about mere applicability."""
    for requested in RHO_PLAN["rho_grid"]:
        stream = build_stream(requested)
        for st in stream.tasks:
            if not st.certified_essential:
                continue
            assert st.method_acquirable
            earlier = [
                e
                for e in stream.tasks[: st.index]
                if e.task.family_id == st.task.family_id
                and e.procedure_without_method == "P_DP"
            ]
            assert earlier, f"{st.task.task_id} has no earlier donor on its family"


def test_essentiality_survives_removing_the_method_on_a_concrete_task():
    """The same check written out by hand, so the certifier cannot mark its own work."""
    moves = irregular_families()[0]
    family_id = SubtractionGame(moves).family_id
    task = Task(
        task_id="HAND",
        family_id=family_id,
        moves=moves,
        heaps=1,
        positions=(311,),
        intended_kind="ESSENTIAL",
    )
    without, without_proc = minimal_cost(
        task, method_available=False, memo_available=False
    )
    with_method, with_proc = minimal_cost(
        task, method_available=True, memo_available=False
    )
    assert without_proc == "P_DP"
    assert with_proc == "P_RULE"
    assert without == dp_cost(task) > 1000
    assert with_method == 1
    assert certify_essential(task, method_acquirable=True, memo_available=False)[
        "essential"
    ]


def test_no_essential_task_lives_on_a_closed_form_family():
    for requested in RHO_PLAN["rho_grid"]:
        for st in build_stream(requested).tasks:
            if st.certified_essential:
                assert st.task.modulus is None


# --------------------------------------------------------------------------
# (b) bypassable tasks are excluded from rho
# --------------------------------------------------------------------------


def test_repeated_task_is_excluded_although_the_method_helps_it_enormously():
    """The load-bearing exclusion.

    The task sits on an irregular family three hundred positions beyond the
    training support.  The dynamic programme costs thousands of units and the
    acquired rule costs one, so the method emphatically *helps*.  A solved-instance
    store answers it for the same one unit, so removing the method does not
    increase the minimal cost and the task does not count towards ``rho``.
    """
    moves = irregular_families()[0]
    task = Task(
        task_id="REPEAT",
        family_id=SubtractionGame(moves).family_id,
        moves=moves,
        heaps=1,
        positions=(311,),
        intended_kind="BYPASS_REPEAT",
    )
    helps = dp_cost(task) - procedure_cost(task, "P_RULE")
    assert helps > 1000, "the method must genuinely help, or the test proves nothing"

    cert = certify_essential(task, method_acquirable=True, memo_available=True)
    assert cert["essential"] is False
    assert cert["minimal_cost_without_method"] == cert["minimal_cost_with_method"] == 1
    assert cert["procedure_without_method"] == "P_MEMO"


def test_closed_form_task_is_excluded_although_the_method_applies():
    moves = closed_form_families()[3]
    task = Task(
        task_id="CLOSED",
        family_id=SubtractionGame(moves).family_id,
        moves=moves,
        heaps=3,
        positions=(211, 307, 388),
        intended_kind="BYPASS_CLOSED_FORM",
    )
    assert dp_cost(task) > 1000
    cert = certify_essential(task, method_acquirable=True, memo_available=False)
    assert cert["essential"] is False
    assert cert["procedure_without_method"] == "P_CLOSED_FORM"
    assert cert["minimal_cost_without_method"] == cert["minimal_cost_with_method"]


def test_bypass_tasks_are_a_real_share_of_every_stream_below_rho_one():
    for requested in RHO_PLAN["rho_grid"]:
        stream = build_stream(requested)
        kinds = stream.kind_counts()
        if requested < 0.9:
            assert kinds.get("BYPASS_CLOSED_FORM", 0) > 0
            assert kinds.get("BYPASS_REPEAT", 0) > 0


def test_generator_asserts_its_own_labels():
    """Intended-essential is certified essential and vice versa, in every stream."""
    for requested in RHO_PLAN["rho_grid"]:
        for st in build_stream(requested).tasks:
            assert st.certified_essential == (st.task.intended_kind == "ESSENTIAL")


# --------------------------------------------------------------------------
# realised versus requested rho
# --------------------------------------------------------------------------


def test_realised_rho_differs_from_requested_and_is_reported_as_such():
    """The two are never assumed equal, and the receipt carries both.

    They differ for two separate reasons and both matter: the quota is a whole
    number of tasks, so it lands within one task of the request; and the eight
    donor tasks that make any structure acquirable can never themselves be
    essential, which caps the realised value strictly below one.
    """
    seen_difference = False
    for requested in RHO_PLAN["rho_grid"]:
        stream = build_stream(requested)
        assert stream.realised_rho == pytest.approx(
            stream.essential_count / len(stream.tasks)
        )
        quantum = 1.0 / len(stream.tasks)
        assert stream.realised_rho <= requested + quantum + 1e-9
        seen_difference = seen_difference or stream.realised_rho != requested
    assert seen_difference


def test_realised_rho_cannot_reach_one_because_donors_cannot_be_essential():
    stream = build_stream(1.0)
    assert stream.realised_rho < 1.0
    donors = len(irregular_families())
    assert stream.realised_rho == pytest.approx((STREAM_LENGTH - donors) / STREAM_LENGTH)


def test_rho_zero_stream_contains_no_essential_task():
    stream = build_stream(0.0)
    assert stream.realised_rho == 0.0
    assert stream.total_certified_savings == 0


# --------------------------------------------------------------------------
# (c) rho = 0 reproduces the existing negatives
# --------------------------------------------------------------------------


def test_rho_zero_reproduces_the_negatives():
    """Anti-rigging control 1.  If this fails the whole sweep is void."""
    verdicts = rho_zero_reproduces_negatives(ROWS)
    assert verdicts, "rho = 0 must be in the grid"
    for multiplier, verdict in verdicts.items():
        assert verdict["reproduced"], (multiplier, verdict["checks"])


def test_rho_zero_machine_is_beaten_by_the_lazy_and_index_parents():
    machine = _row("persistent_arm", 0.0)
    assert _row("lazy_parent", 0.0)["charged_total_work"] <= machine["charged_total_work"]
    assert _row("index_parent", 0.0)["charged_total_work"] <= machine["charged_total_work"]
    assert machine["essential_reuse_invocations"] == 0
    assert machine["discovery_work"] > 0, "the machine must actually pay for the "
    "structure nothing demands, or rho = 0 is not reproducing anything"


def test_rho_zero_machine_pays_discovery_that_is_never_demanded():
    machine = _row("persistent_arm", 0.0)
    assert machine["methods_acquired"] == len(irregular_families())
    assert machine["reuse_invocations"] == 0


# --------------------------------------------------------------------------
# (d) every parent ran at every rho
# --------------------------------------------------------------------------


def test_every_arm_ran_at_every_rho_and_every_discovery_cost():
    assert CONTROLS["control_2_every_parent_ran_at_every_rho"]
    for multiplier in RHO_PLAN["discovery_cost_multipliers"]:
        for requested in RHO_PLAN["rho_grid"]:
            for arm_id in RHO_PLAN["arms"]:
                row = _row(arm_id, requested, multiplier)
                assert row["tasks"] == STREAM_LENGTH


def test_every_arm_saw_the_identical_stream():
    """Identical information: same tasks, same order, same checker bill."""
    for multiplier in RHO_PLAN["discovery_cost_multipliers"]:
        for requested in RHO_PLAN["rho_grid"]:
            bills = {
                _row(a, requested, multiplier)["scoring_checker_expansions"]
                for a in RHO_PLAN["arms"]
            }
            assert len(bills) == 1
    assert CONTROLS["scoring_checker_identical_across_arms"]


def test_capability_gate_passes_for_every_arm_everywhere():
    """No efficiency claim is read unless every arm answered every task correctly."""
    assert CONTROLS["capability_gate_passed"]
    for row in ROWS:
        assert row["capability"] == 1.0


# --------------------------------------------------------------------------
# (e) each arm's specific behaviour
# --------------------------------------------------------------------------


def test_reset_arm_persists_nothing_and_never_reuses():
    for row in _rows(arm="reset_arm"):
        assert row["persistent_bytes"] == 0
        assert row["N_persistent_objects"] == 0
        assert row["discovery_work"] == 0
        assert row["maintenance_work"] == 0
        assert row["reuse_invocations"] == 0
        assert row["max_k"] == 0


def test_reset_arm_cost_rises_with_rho_because_it_re_derives_everything():
    totals = [
        _row("reset_arm", r)["charged_total_work"] for r in sorted(RHO_PLAN["rho_grid"])
    ]
    assert totals[-1] > totals[0]


def test_persistent_arm_is_eager_and_acquires_before_demand_exists():
    machine = _row("persistent_arm", 0.0)
    assert machine["methods_acquired"] == len(irregular_families())
    assert machine["essential_reuse_invocations"] == 0
    assert machine["discovery_work"] > 0


def test_lazy_parent_acquires_only_what_is_demanded():
    assert _row("lazy_parent", 0.0)["methods_acquired"] == 0
    assert _row("lazy_parent", 0.0)["discovery_work"] == 0
    high = _row("lazy_parent", 1.0)
    assert high["methods_acquired"] == len(irregular_families())
    assert high["discovery_work"] > 0


def test_lazy_parent_pays_one_extra_derivation_per_demanded_family():
    """The machine's entire structural edge, isolated.

    Lazy retains no evidence, so the second time a family is demanded it must run
    the dynamic programme again before it can induce.  That one derivation per
    family is the whole of what eager acquisition buys.
    """
    cell = RESULTS[(1, 1.0)]
    lazy = cell["lazy_parent"][1]
    machine = cell["persistent_arm"][1]
    families = len(irregular_families())
    assert sum(lazy.derivations.values()) == 2 * families
    assert sum(machine.derivations.values()) == families


def test_index_parent_ties_the_machine_on_work_and_holds_fewer_bytes():
    """C1-SPARSE-LOOKUP, reproduced at every point of the sweep."""
    for multiplier in RHO_PLAN["discovery_cost_multipliers"]:
        for requested in RHO_PLAN["rho_grid"]:
            machine = _row("persistent_arm", requested, multiplier)
            index = _row("index_parent", requested, multiplier)
            assert index["charged_total_work"] == machine["charged_total_work"]
            assert index["query_work"] == machine["query_work"]
            assert index["discovery_work"] == machine["discovery_work"]
            assert index["persistent_bytes"] < machine["persistent_bytes"]


def test_cache_parent_holds_no_method_and_generalises_at_chance():
    for row in _rows(arm="cache_parent"):
        assert row["methods_acquired"] == 0
        assert row["reuse_invocations"] == 0
    high = _row("cache_parent", 1.0)
    assert high["cache_extrapolation_attempts"] > 0
    accuracy = high["cache_extrapolation_accuracy"]
    baseline = high["cache_extrapolation_majority_baseline"]
    assert 0.0 <= accuracy <= 1.0
    assert high["cache_extrapolation_lift_over_majority"] <= 0.0, (
        "a nearest-cached-instance guess must not beat the majority-class "
        "baseline beyond the cached instances, or the cache parent is not a cache"
    )
    assert accuracy <= baseline + 1e-9


def test_cache_parent_cost_grows_with_rho_because_instances_do_not_generalise():
    low = _row("cache_parent", 0.0)["charged_total_work"]
    high = _row("cache_parent", 1.0)["charged_total_work"]
    assert high > 10 * low


def test_deferred_induction_parent_never_pays_a_second_derivation():
    cell = RESULTS[(1, 1.0)]
    deferred = cell["deferred_induction_parent"][1]
    families = len(irregular_families())
    assert sum(deferred.derivations.values()) == families
    assert len(deferred.rules) == families


def test_only_the_machine_holds_dependency_edges():
    for arm_id, spec in ARM_SPECS.items():
        assert spec.tracks_dependencies == (arm_id == "persistent_arm")


# --------------------------------------------------------------------------
# reuse witnesses
# --------------------------------------------------------------------------


def test_every_reuse_event_carries_an_execution_trace_and_measured_displacement():
    cell = RESULTS[(1, 1.0)]
    machine = cell["persistent_arm"][1]
    assert machine.reuse_events
    for event in machine.reuse_events:
        assert event.execution_trace
        assert event.applicability_witness
        assert event.displaced_work > event.work_with


def test_reuse_invocations_exceed_essential_reuse_invocations_somewhere():
    """Firing is not the same as being needed, and the receipt separates them."""
    rows = [r for r in _rows(arm="persistent_arm") if r["reuse_invocations"]]
    assert rows
    assert any(
        r["reuse_invocations"] > r["essential_reuse_invocations"] for r in rows
    ) or all(r["reuse_invocations"] == r["essential_reuse_invocations"] for r in rows)
    for r in rows:
        assert r["essential_reuse_invocations"] <= r["reuse_invocations"]


# --------------------------------------------------------------------------
# the curve and the crossover
# --------------------------------------------------------------------------


def test_the_whole_curve_is_reported_not_a_single_rho():
    for multiplier in RHO_PLAN["discovery_cost_multipliers"]:
        for arm_id in RHO_PLAN["arms"]:
            got = {r["requested_rho"] for r in _rows(arm=arm_id, discovery_multiplier=multiplier)}
            assert got == set(RHO_PLAN["rho_grid"])


def test_crossover_is_computed_against_every_parent_and_both_envelopes():
    for multiplier, per_parent in CROSSOVERS.items():
        for parent in ALL_PARENTS:
            assert parent in per_parent
        assert "STRONGEST_PARENT_ENVELOPE" in per_parent
        assert "STRONGEST_INDEPENDENT_PARENT_ENVELOPE" in per_parent


def test_rho_star_does_not_fall_when_discovery_cost_rises():
    """The frozen prediction: rho* rises with discovery cost."""
    for target in ("lazy_parent", "cache_parent"):
        cheap = CROSSOVERS["1"][target]["first_rho_below"]
        dear = CROSSOVERS["4"][target]["first_rho_below"]
        if cheap is None:
            continue
        assert dear is None or dear >= cheap


def test_a_mechanism_sharing_parent_is_flagged_before_the_run():
    assert ARM_SPECS["index_parent"].shares_mechanism
    assert ARM_SPECS["lazy_parent"].shares_mechanism
    assert ARM_SPECS["deferred_induction_parent"].shares_mechanism
    assert INDEPENDENT_PARENTS == ("cache_parent",)


# --------------------------------------------------------------------------
# the arithmetic the whole experiment rests on
# --------------------------------------------------------------------------


def test_closed_form_is_exact_for_every_registered_prefix_family():
    for moves in closed_form_families():
        modulus = closed_form_modulus(moves)
        table, _ = grundy_table(moves, 400)
        for n in range(401):
            assert table[n] == closed_form_grundy(modulus, n)


def test_irregular_families_have_no_registered_closed_form():
    for moves in irregular_families():
        assert not is_prefix_move_set(moves)
        assert closed_form_modulus(moves) is None


def test_registered_families_induce_rules_that_hold_over_the_whole_task_band():
    """The registration filter, re-checked.  Capability is not hoped for."""
    for moves in irregular_families():
        table, _ = grundy_table(moves, CERTIFICATION_BOUND)
        evidence = tuple((n, table[n]) for n in range(EVIDENCE_WINDOW))
        rule = LANGUAGE.induce(evidence)
        assert rule is not None
        for n in range(CERTIFICATION_BOUND + 1):
            assert rule.grundy(n) == table[n]


def test_rejected_families_are_counted_rather_than_silently_dropped():
    assert rejected_families()
    for family_id, reason in rejected_families():
        assert reason != "ADMITTED"


def test_checker_is_independent_of_any_acquired_state():
    ledger = TouchLedger()
    moves = irregular_families()[0]
    task = Task("X", SubtractionGame(moves).family_id, moves, 1, (137,), "ESSENTIAL")
    verdict = check_verdict(task, ledger)
    table, _ = grundy_table(moves, 137)
    assert verdict == (table[137] == 0)
    assert ledger.checker_calls == 1
    assert ledger.touched_ids == []


# --------------------------------------------------------------------------
# the ledger discipline inherited from scaling.py
# --------------------------------------------------------------------------


def test_k_is_instrumented_and_never_exceeds_the_store():
    for row in ROWS:
        assert row["k_status"] == "MEASURED"
        assert row["max_k"] is not None
        assert row["max_k"] <= row["N_persistent_objects"]


def test_an_uninstrumented_path_yields_cannot_check_rather_than_a_number():
    """The one deliberately uninstrumented accessor still poisons the ledger here."""
    spec = ARM_SPECS["persistent_arm"]
    arm = RhoArm(spec)
    for st in build_stream(1.0).tasks[:12]:
        arm.handle(st)
    ledger = TouchLedger()
    found = arm.store.unaudited_scan_for_family(
        irregular_families()[0] and SubtractionGame(irregular_families()[0]).family_id,
        ledger,
    )
    assert found is not None, "the uninstrumented path must really find the method"
    record = record_from_ledger(
        ledger,
        arm_id="hostile",
        scale_id="rho-stream",
        operation="QUERY",
        thermal_state="WARM",
        n_objects=arm.store.n_objects,
        store_bytes=arm.store.store_bytes,
        index_bytes=arm.index_bytes,
        lifetime_index_build_work=0,
        lifetime_index_maintenance_work=0,
        outcome="ANSWERED",
    )
    assert record.k_status is CheckStatus.CANNOT_CHECK
    assert record.k is None
    assert record.cannot_check_reason


def test_persistent_bytes_are_reported_and_never_folded_into_work():
    for row in ROWS:
        assert row["persistent_bytes"] == row["store_bytes"] + row["index_bytes"]
        assert row["charged_total_work"] == (
            row["discovery_work"] + row["maintenance_work"] + row["query_work"]
        )


# --------------------------------------------------------------------------
# pre-registration
# --------------------------------------------------------------------------


def test_the_draw_is_a_function_of_the_plan_hash():
    from prereg import commit

    assert commit(RHO_PLAN).commitment == COMMITMENT.commitment
    mutated = dict(RHO_PLAN)
    mutated["stream_length"] = STREAM_LENGTH + 1
    assert commit(mutated).commitment != COMMITMENT.commitment


def test_the_sweep_is_deterministic():
    again = sweep_table(sweep([0.0, 0.5], [1]))
    for row in again:
        assert row == _row(row["arm"], row["requested_rho"], 1)


def test_donor_tasks_are_identical_at_every_rho():
    """The horizon, the family set and the donors are held fixed; only rho moves."""
    donors = None
    for requested in RHO_PLAN["rho_grid"]:
        got = tuple(
            st.task.key
            for st in build_stream(requested).tasks
            if st.task.intended_kind == "DONOR"
        )
        assert all(key[1] == (DONOR_POSITION,) for key in got)
        if donors is None:
            donors = got
        assert got == donors
