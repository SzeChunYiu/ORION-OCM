"""Tests for the active-subspace scaling harness.

These tests are adversarial towards the module they cover.  Each of the five
required assertions is a way the sparse claim could be faked, and the test
exists to make the fake fail loudly:

(a) ``k`` for the indexed arms is bounded and tiny relative to ``N`` at every
    frozen scale -- the claim itself;
(b) the global-scan ablation's ``k`` equals ``N`` exactly -- the harness's own
    self-check, because a harness in which the linear arm does not look linear
    cannot be believed about the sparse one;
(c) index build work is charged to the operation that triggered it and is
    visible in the record -- an arm that scanned all ``N`` to look sparse must
    be detectable from its own receipt;
(d) revoking a globally shared support produces a large cone while revoking a
    local one produces a small cone -- exactness cuts both ways, and a
    dependency structure that reported the global change as local would be
    broken rather than efficient;
(e) a deliberately uninstrumented path yields ``CANNOT_CHECK`` rather than the
    flattering number its result set would suggest.

A sixth thing is asserted throughout and matters more than any of them: the
plain index parent **ties** the OCM arm on ``k``, ``k/N`` and query work at
every scale.  Several tests below exist specifically to fail if a future edit
quietly breaks that tie in the OCM arm's favour, because the likeliest way for
that to happen is a weakened parent rather than an improved arm.

The sweep is run once per module.  Everything asserted here is a deterministic
function of the pre-registration commitment, so a failure is a real change in
the harness and never a flaky draw.
"""

from __future__ import annotations

import math

import pytest

from scaling import (
    COMMITMENT,
    SCALING_PLAN,
    SHARED_SUPPORT_ID,
    SPARSE_FRACTION,
    CheckStatus,
    ResourceRecord,
    TouchLedger,
    build_catalogue,
    fit_loglog,
    populate_store,
    probe_positions,
    record_from_ledger,
)
from scaling_arms import (
    ARMS,
    ARM_ROLES,
    CacheParent,
    GlobalScanAblation,
    IndexParent,
    OcmArm,
    RebuildIndexHostile,
    UnauditedScanHostile,
    fits_for,
    local_support_id,
    run_arm,
    run_sweep,
    sweep,
    sweep_table,
)

INDEXED_ARMS = ("ocm_arm", "index_parent")
#: arms that persist induced methods and therefore genuinely depend on the
#: shared periodicity lemma
METHOD_HOLDING_ARMS = (
    "ocm_arm",
    "index_parent",
    "global_scan_ablation",
    "rebuild_index_hostile",
    "unaudited_scan_hostile",
)


@pytest.fixture(scope="module")
def swept():
    return run_sweep()


@pytest.fixture(scope="module")
def catalogue():
    return build_catalogue(1)


# --------------------------------------------------------------------------
# the frozen plan
# --------------------------------------------------------------------------


def test_commitment_is_a_pure_function_of_the_plan():
    from prereg import commit

    assert commit(SCALING_PLAN).commitment == COMMITMENT.commitment


def test_probe_positions_lie_strictly_above_the_training_support():
    """Extrapolation, not recall.  CL-D1(b) applied to the scaling probe.

    If a probe position sat inside the training support the cache parent would
    hit, and the comparison would measure lookup speed rather than the
    difference between a method and a stored answer.
    """
    training_max = SCALING_PLAN["evidence_blocks"] * SCALING_PLAN["evidence_block_size"] - 1
    assert all(p > training_max for p in probe_positions())
    assert len(set(probe_positions())) == SCALING_PLAN["probe_positions"]


def test_scales_are_nested_so_a_k_change_cannot_be_a_family_change():
    small = build_catalogue(1)
    large = build_catalogue(3)
    assert [f.family_id for f in large.families][: len(small.families)] == [
        f.family_id for f in small.families
    ]
    assert small.probe_family_id == large.probe_family_id


def test_probe_family_rule_is_the_true_periodic_rule():
    """The induced probe method is the real Sprague--Grundy rule, not a decoy.

    ``SUB(1,3,4)`` has Grundy period 7.  Asserted rather than assumed, because
    a probe family whose induced rule were wrong would make every correctness
    column in the sweep a statement about the checker instead of about the
    method.
    """
    from games import SubtractionGame

    spec = build_catalogue(1).probe
    truth = SubtractionGame(spec.moves).grundy_upto(96)
    assert spec.rule.period == 7
    assert all(spec.rule.grundy(n) == truth[n] for n in range(97))


# --------------------------------------------------------------------------
# (a) k << N for the indexed arms at every scale
# --------------------------------------------------------------------------


@pytest.mark.parametrize("arm_id", INDEXED_ARMS)
def test_indexed_arm_k_is_bounded_and_tiny_at_every_scale(swept, arm_id):
    rows = swept.rows_for(arm_id)
    assert len(rows) == len(SCALING_PLAN["multipliers"])
    for row in rows:
        assert row.k_status is CheckStatus.MEASURED
        assert row.k == 1
        assert row.k_over_n is not None and row.k_over_n <= SPARSE_FRACTION
        assert row.sparse_verdict == "SPARSE"


@pytest.mark.parametrize("arm_id", INDEXED_ARMS)
def test_indexed_arm_k_does_not_grow_with_n(swept, arm_id):
    rows = swept.rows_for(arm_id)
    assert len({row.k for row in rows}) == 1
    fit = swept.fits[arm_id]["k"]
    assert fit.verdict == "CONSTANT_IN_N"
    assert fit.slope == 0.0


@pytest.mark.parametrize("arm_id", INDEXED_ARMS)
def test_indexed_arm_query_work_does_not_grow_with_n(swept, arm_id):
    assert swept.fits[arm_id]["query_work"].verdict == "CONSTANT_IN_N"


@pytest.mark.parametrize("arm_id", INDEXED_ARMS)
def test_indexed_arms_answer_every_probe_correctly(swept, arm_id):
    for row in swept.rows_for(arm_id):
        assert row.answered_queries == row.queries
        assert row.correct_queries == row.queries
        assert row.outcome == "ANSWERED"


def test_the_index_parent_ties_the_ocm_arm_exactly(swept):
    """PARENT_SUFFICIENT on ``k(N)``, asserted rather than hoped.

    The plain database index performs the same probe and the same read, so it
    matches the OCM arm on ``k``, ``k/N`` and query work at every scale.  This
    test fails if a future edit makes the OCM arm look *better* on query cost,
    which would almost certainly mean the parent had been weakened rather than
    the arm improved.  It also fails if the parent is made to look better,
    which would mean the OCM arm had acquired an unaccounted advantage.
    """
    ocm = {r.scale_id: r for r in swept.rows_for("ocm_arm")}
    parent = {r.scale_id: r for r in swept.rows_for("index_parent")}
    assert set(ocm) == set(parent)
    for scale, row in ocm.items():
        assert parent[scale].k == row.k
        assert parent[scale].k_over_n == row.k_over_n
        assert parent[scale].query_work_cold == row.query_work_cold
        assert parent[scale].query_work_warm_max == row.query_work_warm_max
        assert parent[scale].store_bytes == row.store_bytes


def test_the_ocm_arm_pays_for_its_dependency_edges_in_index_bytes(swept):
    """The only thing the OCM arm has that the parent lacks, charged for.

    A dependency map is persistent index state.  Leaving it out of the byte
    accounting would be precisely the hiding this module exists to prevent, so
    the OCM arm carries strictly more index bytes -- one entry per declared
    support, three per method -- and its ``persistent_bytes`` are larger than
    the parent's at every scale.
    """
    ocm = {r.scale_id: r for r in swept.rows_for("ocm_arm")}
    parent = {r.scale_id: r for r in swept.rows_for("index_parent")}
    for scale, row in ocm.items():
        assert row.index_bytes == 4 * parent[scale].index_bytes
        assert row.persistent_bytes > parent[scale].persistent_bytes


# --------------------------------------------------------------------------
# (b) the ablation's k tracks N
# --------------------------------------------------------------------------


def test_global_scan_ablation_k_equals_n_exactly(swept):
    for row in swept.rows_for("global_scan_ablation"):
        assert row.k == row.n_objects
        assert row.k_over_n == 1.0
        assert row.sparse_verdict == "NOT_SPARSE"


def test_global_scan_ablation_k_has_unit_log_log_slope(swept):
    fit = swept.fits["global_scan_ablation"]["k"]
    assert fit.verdict == "POWER_LAW_CONSISTENT"
    assert fit.slope == pytest.approx(1.0, abs=1e-9)
    assert fit.rms_log_residual == pytest.approx(0.0, abs=1e-12)


def test_global_scan_query_work_is_linear_in_n(swept):
    fit = swept.fits["global_scan_ablation"]["query_work"]
    assert fit.slope == pytest.approx(1.0, abs=0.02)
    assert fit.rms_log_residual < SCALING_PLAN["loglog_residual_threshold"]


def test_the_store_scan_touches_every_object(catalogue):
    """The instrumented no-index path cannot answer without touching all N."""
    store = populate_store(catalogue)
    ledger = TouchLedger()
    found = store.query(catalogue.probe_family_id, ledger)
    assert found is not None
    assert ledger.k == store.n_objects
    assert ledger.enumerated_items == store.n_objects


# --------------------------------------------------------------------------
# (c) index build work is charged and is not hidden
# --------------------------------------------------------------------------


def test_rebuild_hostile_pays_a_full_scan_that_appears_in_its_record(catalogue):
    arm = RebuildIndexHostile(catalogue)
    cold = arm.query(probe_positions()[0])
    assert cold.k == 1  # a sparse-looking touch count ...
    assert cold.index_build_work == arm.n_objects  # ... bought with a full scan
    assert cold.charged_total_work >= arm.n_objects


def test_rebuild_hostile_is_flagged_rather_than_believed(swept):
    for row in swept.rows_for("rebuild_index_hostile"):
        assert row.index_build_work_cold == row.n_objects
        assert row.sparse_verdict == "SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN"


def test_rebuild_hostile_is_indistinguishable_from_the_ocm_arm_on_k_alone(swept):
    """Why ``k`` is not admissible evidence on its own.

    The hostile fakes the touch count perfectly.  Only the build charge and the
    lifetime total separate the two, which is the entire argument for reporting
    them in the same row.
    """
    ocm = {r.scale_id: r for r in swept.rows_for("ocm_arm")}
    hostile = {r.scale_id: r for r in swept.rows_for("rebuild_index_hostile")}
    for scale, row in ocm.items():
        assert hostile[scale].k == row.k
        assert hostile[scale].query_work_cold == row.query_work_cold
        # ... and only here do they part company
        assert hostile[scale].lifetime_index_build_work == 5 * row.lifetime_index_build_work
        assert row.sparse_verdict != hostile[scale].sparse_verdict


def test_the_hidden_build_touches_survive_in_the_receipt(catalogue):
    """The hostile hides the build from ``k``; it cannot hide it from the record."""
    arm = RebuildIndexHostile(catalogue)
    arm.query(probe_positions()[0])
    build = arm.last_build_record
    assert build is not None
    assert build.operation == "INDEX_BUILD"
    assert build.k == arm.n_objects
    assert build.index_build_work == arm.n_objects


def test_an_honest_index_pays_the_build_scan_once_and_says_so(swept):
    """Not "no scan" -- one scan, amortised, and reported.

    An index cannot be built over an existing store without enumerating it.
    The honest arms pay that once at install and nothing per query; the hostile
    pays it on every query.  Both totals are in the row, so the difference is
    amortisation rather than concealment.
    """
    for arm_id in INDEXED_ARMS:
        for row in swept.rows_for(arm_id):
            assert row.index_build_work_cold == 0
            assert row.index_build_work_warm_total == 0
            assert row.lifetime_index_build_work == row.n_objects
    for row in swept.rows_for("global_scan_ablation"):
        assert row.lifetime_index_build_work == 0


def test_sparse_verdict_catches_a_build_scan_even_with_k_of_one():
    """The detector is a property of the accounting, not of a particular arm."""
    ledger = TouchLedger()
    ledger.touch("M:only", 10)
    ledger.index_build_work = 1000
    record = record_from_ledger(
        ledger,
        arm_id="synthetic",
        scale_id="test",
        operation="QUERY",
        thermal_state="COLD",
        n_objects=1000,
        store_bytes=10_000,
        index_bytes=0,
        lifetime_index_build_work=1000,
        lifetime_index_maintenance_work=0,
        outcome="ANSWERED",
    )
    assert record.k == 1
    assert record.sparse_verdict == "SPARSE_ONLY_AFTER_GLOBAL_BUILD_SCAN"


# --------------------------------------------------------------------------
# (d) the shared revocation must not look local
# --------------------------------------------------------------------------


def test_local_revocation_cone_is_small_and_constant(swept):
    for row in swept.rows_for("ocm_arm"):
        assert row.cone_local == 2
        assert row.true_cone_local == 2
        assert row.cone_local / row.n_objects < 0.05
        assert row.exact_local
        assert row.stale_survivors_local == 0
    assert swept.fits["ocm_arm"]["revision_work_local"].verdict == "CONSTANT_IN_N"


def test_shared_revocation_cone_is_large_and_grows_with_n(swept):
    """The hostile control.  A global change reported as local is a defect.

    Every induced periodic rule genuinely rests on the periodicity lemma, so
    the cone must cover all of them.  An arm whose dependency structure
    returned a small cone here would be silently keeping stale methods alive,
    which is worse than a slow scan and must never read as an efficiency win.
    """
    rows = sorted(swept.rows_for("ocm_arm"), key=lambda r: r.n_objects)
    for row in rows:
        families = row.n_objects // 3
        assert row.cone_shared >= families
        assert row.cone_shared / row.n_objects > 0.3
        assert row.cone_shared > 10 * row.cone_local
        assert row.exact_shared
    assert [r.cone_shared for r in rows] == sorted(r.cone_shared for r in rows)
    fit = swept.fits["ocm_arm"]["cone_shared"]
    assert fit.slope == pytest.approx(1.0, abs=0.05)
    assert fit.verdict == "POWER_LAW_CONSISTENT"


def test_shared_and_local_cones_diverge_as_n_grows(swept):
    rows = sorted(swept.rows_for("ocm_arm"), key=lambda r: r.n_objects)
    ratios = [r.cone_shared / r.cone_local for r in rows]
    assert ratios == sorted(ratios)
    assert ratios[-1] > 10 * ratios[0]


def test_ocm_revision_work_tracks_the_cone_not_the_store(swept):
    rows = sorted(swept.rows_for("ocm_arm"), key=lambda r: r.n_objects)
    for row in rows:
        assert row.revision_work_local == 4  # probe, support read, method read, unindex
        assert row.revision_work_shared < row.n_objects
        assert row.revision_work_shared > row.cone_shared
    fit = swept.fits["ocm_arm"]["revision_work_shared"]
    assert fit.slope == pytest.approx(1.0, abs=0.05)


def test_arms_without_dependency_edges_do_nothing_and_leave_stale_survivors(swept):
    """The parent's cost is not work, it is the cone left standing.

    A plain index holds no support-to-dependent edges, so a revocation costs it
    nothing and changes nothing: the entire true cone survives, stale.  Stating
    it as ``revision_work == 0`` without ``stale_survivors == true cone`` beside
    it would read as the parent being cheap, which is the opposite of what
    happened.
    """
    for arm_id in ("index_parent", "global_scan_ablation", "cache_parent", "rebuild_index_hostile"):
        for row in swept.rows_for(arm_id):
            assert row.cone_local == 0 and row.cone_shared == 0
            assert row.revision_work_local == 0 and row.revision_work_shared == 0
            assert row.stale_survivors_local == row.true_cone_local
            assert row.stale_survivors_shared == row.true_cone_shared
            assert not row.exact_local and not row.exact_shared


def test_cache_parent_truly_does_not_depend_on_the_lemma(swept):
    """Reported because it is against the module's own thesis.

    An exactly solved position depends on no lemma, so the true cone of the
    shared periodicity support in the cache store is the support alone.  The
    cache is genuinely immune to that revocation; its exposure is to the
    evidence block that produced its entries, whose true cone is nine objects.
    """
    for row in swept.rows_for("cache_parent"):
        assert row.true_cone_shared == 1
        assert row.true_cone_local == 1 + SCALING_PLAN["evidence_block_size"]


def test_cache_parent_answers_none_of_the_probes(swept):
    for row in swept.rows_for("cache_parent"):
        assert row.outcome == "NO_CACHED_POSITION"
        assert row.answered_queries == 0
        assert row.correct_queries == 0
        assert row.k == 0
        # the sparsest arm in the sweep, and the only one that cannot answer
        assert row.sparse_verdict == "SPARSE"


def test_cache_parent_pays_for_the_same_information_in_objects_and_bytes(swept):
    ocm = {r.scale_id: r for r in swept.rows_for("ocm_arm")}
    for row in swept.rows_for("cache_parent"):
        assert row.n_objects > 5 * ocm[row.scale_id].n_objects
        assert row.persistent_bytes > 3 * ocm[row.scale_id].persistent_bytes


# --------------------------------------------------------------------------
# (e) an uninstrumented path may not report a number
# --------------------------------------------------------------------------


def test_unaudited_arm_reports_cannot_check_not_a_flattering_k(catalogue):
    arm = UnauditedScanHostile(catalogue)
    record = arm.query(probe_positions()[0])
    assert record.k is None
    assert record.k_status is CheckStatus.CANNOT_CHECK
    assert record.cannot_check_reason
    assert record.touched_ids == ()
    assert record.sparse_verdict == "CANNOT_CHECK"
    # it answered correctly; correctness is not what is unmeasurable here
    assert record.verdict_correct is True


def test_unaudited_revocation_reports_no_revision_work(catalogue):
    """It gets the cone exactly right and still may not report its cost.

    Scanning declared supports recovers the true cone, so this hostile is
    incidentally the strongest revocation in the sweep -- and its work is
    unmeasurable, which is why it is a hostile and not a parent.
    """
    arm = UnauditedScanHostile(catalogue)
    revision = arm.revoke(SHARED_SUPPORT_ID, trigger_kind="GLOBALLY_SHARED")
    assert revision.k is None
    assert revision.revision_work is None
    assert revision.k_status is CheckStatus.CANNOT_CHECK
    assert revision.exact_revocation
    assert revision.cone_size > 1


def test_a_poisoned_ledger_cannot_be_talked_into_a_number(catalogue):
    store = populate_store(catalogue)
    ledger = TouchLedger()
    store.read(f"M:{catalogue.probe_family_id}", ledger)
    assert ledger.k == 1
    store.unaudited_scan_for_family(catalogue.probe_family_id, ledger)
    assert ledger.k is None
    record = record_from_ledger(
        ledger,
        arm_id="synthetic",
        scale_id="test",
        operation="QUERY",
        thermal_state="COLD",
        n_objects=store.n_objects,
        store_bytes=store.store_bytes,
        index_bytes=0,
        lifetime_index_build_work=0,
        lifetime_index_maintenance_work=0,
        outcome="ANSWERED",
    )
    assert record.k is None and record.k_status is CheckStatus.CANNOT_CHECK


def test_cannot_check_propagates_through_the_fit(swept):
    for coordinate in ("k", "revision_work_local", "revision_work_shared"):
        fit = swept.fits["unaudited_scan_hostile"][coordinate]
        assert fit.verdict == "CANNOT_CHECK"
        assert fit.slope is None


def test_a_record_may_not_carry_both_cannot_check_and_a_number():
    with pytest.raises(ValueError):
        ResourceRecord(
            arm_id="liar",
            scale_id="test",
            operation="QUERY",
            thermal_state="COLD",
            n_objects=100,
            persistent_bytes=10,
            store_bytes=10,
            index_bytes=0,
            k=1,
            k_status=CheckStatus.CANNOT_CHECK,
            touched_ids=(),
            active_bytes=0,
            index_probes=0,
            index_build_work=0,
            index_maintenance_work=0,
            lifetime_index_build_work=0,
            lifetime_index_maintenance_work=0,
            search_expansions=0,
            checker_calls=1,
            checker_expansions=0,
            object_reads=0,
            enumerated_items=0,
            predicate_evaluations=0,
            query_work=1,
            outcome="ANSWERED",
            cannot_check_reason="unaudited",
        )


def test_k_may_not_be_inferred_from_a_result_set():
    """``k`` must equal the instrumented touch count, not a plausible number."""
    with pytest.raises(ValueError):
        ResourceRecord(
            arm_id="liar",
            scale_id="test",
            operation="QUERY",
            thermal_state="COLD",
            n_objects=100,
            persistent_bytes=10,
            store_bytes=10,
            index_bytes=0,
            k=1,
            k_status=CheckStatus.MEASURED,
            touched_ids=(),
            active_bytes=0,
            index_probes=0,
            index_build_work=0,
            index_maintenance_work=0,
            lifetime_index_build_work=0,
            lifetime_index_maintenance_work=0,
            search_expansions=0,
            checker_calls=1,
            checker_expansions=0,
            object_reads=0,
            enumerated_items=0,
            predicate_evaluations=0,
            query_work=1,
            outcome="ANSWERED",
        )


# --------------------------------------------------------------------------
# instrumentation and fitting discipline
# --------------------------------------------------------------------------


def test_repeated_touches_are_reads_not_new_identities(catalogue):
    store = populate_store(catalogue)
    ledger = TouchLedger()
    method_id = f"M:{catalogue.probe_family_id}"
    for _ in range(5):
        store.read(method_id, ledger)
    assert ledger.k == 1
    assert ledger.object_reads == 5


def test_no_arm_consults_the_ground_truth_cone():
    """The true cone is the scorer's, in the style of ``escalation.py``.

    Enforced structurally: no arm class may mention ``true_cone`` anywhere in
    its source.  Only the shared ``revoke`` scaffolding, which compares after
    the fact, is allowed to read it.
    """
    import inspect

    import scaling_arms

    for cls in (
        OcmArm,
        IndexParent,
        GlobalScanAblation,
        CacheParent,
        RebuildIndexHostile,
        UnauditedScanHostile,
    ):
        assert "true_cone" not in inspect.getsource(cls)
    assert "true_cone" in inspect.getsource(scaling_arms.ScalingArm.revoke)


def test_fit_refuses_a_slope_when_a_point_is_missing():
    assert fit_loglog([1, 2, 3], [1.0, 0.0, 3.0]).verdict == "UNDEFINED_NONPOSITIVE_VALUES"
    assert fit_loglog([1, 2, 3], [1.0, None, 3.0]).verdict == "CANNOT_CHECK"
    assert fit_loglog([1, 2], [1.0, 2.0]).verdict == "TOO_FEW_POINTS"
    assert fit_loglog([2, 2, 2], [1.0, 2.0, 3.0]).verdict == "DEGENERATE_X"


def test_fit_reports_that_a_power_law_does_not_hold_when_it_does_not():
    """The model's failure is reported, not smoothed over.

    An exponential is not a power law.  The fitted slope is still returned so a
    reader can see what was fitted, but ``verdict`` and ``fits`` both say the
    line does not describe the points, and the note forbids quoting the slope
    as an exponent.
    """
    xs = [1, 10, 100, 1000]
    ys = [math.exp(x / 100.0) for x in xs]
    fit = fit_loglog(xs, ys, label="exponential")
    assert fit.verdict == "POWER_LAW_NOT_SUPPORTED"
    assert not fit.fits
    assert fit.slope is not None
    assert fit.rms_log_residual > SCALING_PLAN["loglog_residual_threshold"]
    assert "must not be quoted" in fit.note


def test_fit_recovers_a_known_slope_exactly():
    xs = [1, 10, 100, 1000]
    fit = fit_loglog(xs, [3.0 * x**2 for x in xs], label="quadratic")
    assert fit.slope == pytest.approx(2.0, abs=1e-9)
    assert fit.rms_log_residual == pytest.approx(0.0, abs=1e-12)
    assert fit.verdict == "POWER_LAW_CONSISTENT"


def test_a_constant_coordinate_is_not_given_an_r_squared():
    fit = fit_loglog([1, 10, 100, 1000], [7, 7, 7, 7])
    assert fit.verdict == "CONSTANT_IN_N"
    assert fit.slope == 0.0
    assert fit.r_squared is None


# --------------------------------------------------------------------------
# the sweep as a whole
# --------------------------------------------------------------------------


def test_every_registered_arm_runs_at_every_frozen_scale(swept):
    assert len(swept.rows) == len(ARMS) * len(SCALING_PLAN["multipliers"])
    assert swept.scales == tuple(f"{m}x" for m in SCALING_PLAN["multipliers"])
    assert swept.commitment == COMMITMENT.commitment
    assert set(ARM_ROLES) == set(ARMS)


def test_all_arms_receive_identical_information(swept):
    """Same probes, same checker calls, same correctness gate.

    A comparison in which one arm saw more is not a comparison.  Checker calls
    are the observable proxy here: every arm is certified on every probe,
    whether or not it managed to answer, so an arm cannot look cheap by
    declining to establish the truth.
    """
    per_arm: dict[str, set] = {}
    for row in swept.rows:
        per_arm.setdefault(row.arm_id, set()).add(
            (row.scale_id, row.checker_calls_total, row.queries)
        )
    reference = per_arm["ocm_arm"]
    for arm_id, seen in per_arm.items():
        assert seen == reference, arm_id


def test_every_arm_that_answered_answered_correctly(swept):
    """Capability gate before any efficiency reading (protocol §8).

    No efficiency number in this module is bought with a wrong answer.  The
    cache parent answers nothing, which is a capability failure and is reported
    as one rather than as a sparse win.
    """
    for row in swept.rows:
        assert row.correct_queries == row.answered_queries
        if row.arm_id == "cache_parent":
            assert row.answered_queries == 0
        else:
            assert row.answered_queries == row.queries


def test_persistent_bytes_is_the_sum_of_its_declared_parts(swept):
    for row in swept.rows:
        assert row.persistent_bytes == row.store_bytes + row.index_bytes


def test_the_sweep_states_its_own_limitations(swept):
    joined = " ".join(swept.notes)
    assert "A9" in joined
    assert "PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM" in joined
    assert "extrapolation licence" in joined
    assert "PARENT_SUFFICIENT" in joined


def test_the_sweep_is_deterministic():
    """No wall clock, no unseeded randomness: two runs must agree exactly."""
    first = run_sweep([1])
    second = run_sweep([1])
    assert [r.as_dict() for r in first.rows] == [r.as_dict() for r in second.rows]


# --------------------------------------------------------------------------
# the flat receipt surface used by ``run_scaling.py``
# --------------------------------------------------------------------------

REQUIRED_ROW_KEYS = (
    "arm",
    "scale",
    "N",
    "k",
    "k_over_N",
    "k_status",
    "query_work",
    "index_build_work",
    "persistent_bytes",
    "total_work_including_build",
    "answered",
    "correct",
    "local_cone_exact",
    "global_cone_exact",
    "local_cone_size",
    "global_cone_size",
)


def test_sweep_table_carries_every_key_the_receipt_needs():
    rows = sweep_table(sweep(["ocm_arm", "unaudited_scan_hostile"]))
    assert rows
    for row in rows:
        for key in REQUIRED_ROW_KEYS:
            assert key in row, key


def test_sweep_table_refuses_to_average_an_unmeasurable_k():
    rows = sweep_table(sweep(["unaudited_scan_hostile"]))
    for row in rows:
        assert row["k"] is None
        assert row["k_over_N"] is None
        assert row["k_status"] == "CANNOT_CHECK"


def test_the_flat_table_reproduces_the_parent_sufficient_tie():
    """The same tie, read off the receipt surface rather than the sweep object."""
    rows = sweep_table(sweep(["ocm_arm", "index_parent"]))
    ocm = {r["N"]: r for r in rows if r["arm"] == "ocm_arm"}
    parent = {r["N"]: r for r in rows if r["arm"] == "index_parent"}
    assert set(ocm) == set(parent)
    for n, row in ocm.items():
        assert parent[n]["k"] == row["k"]
        assert parent[n]["query_work"] == row["query_work"]


def test_fits_for_returns_a_verdict_for_every_registered_coordinate():
    rows = sweep_table(sweep(["ocm_arm"]))
    fits = fits_for(rows)
    assert set(fits) == {"ocm_arm"}
    for coordinate, fit in fits["ocm_arm"].items():
        assert "verdict" in fit, coordinate
        assert "rms_log_residual" in fit, coordinate


def test_run_arm_matches_the_sweep_for_one_cell():
    result = run_arm("ocm_arm", 1)
    assert result.arm_id == "ocm_arm"
    assert result.scale_id == "1x"
    assert len(result.queries) == len(probe_positions())
    assert result.local_revision is not None and result.global_revision is not None
    assert result.local_revision.trigger_support_id == local_support_id(build_catalogue(1))
