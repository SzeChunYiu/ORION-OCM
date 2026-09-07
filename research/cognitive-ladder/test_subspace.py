"""Tests for the discovered-indexing experiment.

These tests are adversarial towards the module they cover.  The experiment's
claim is that an arm can find the relevant part of a store when nothing names
it, keep the work bounded as the store grows, and stay correct.  Each of those
three clauses is a place the claim could be faked, and there is a test whose job
is to make the fake fail loudly:

(a) the machine arm's ``k`` stays inside the *declared* bucket bound at every
    scale, and its ``k`` is counted by instrumented touches only;
(b) the ablation that never re-indexes has ``k`` tracking ``N`` -- the harness's
    own self-check, because a harness in which not-noticing looks free cannot be
    believed about noticing;
(c) every arm's correctness is asserted on **both** query classes.  An arm that
    answers nothing passes the sparsity test and fails here; so does an arm that
    answers everything.

Each parent additionally has a test named after its specific failure mode:

* ``oracle_key_parent`` cannot run at all without the family identity, and is
  the only arm in the module allowed to see it;
* ``exact_scan_parent`` is never wrong and its ``k`` is exactly ``N``;
* ``signature_hash_parent`` is adequate -- and *better than the machine arm* --
  at the small scales, and loses adequacy only when growth breaks its
  hand-specified prefix;
* ``nearest_neighbour_parent`` has ``k = 1``, query work linear in ``N``, and
  gets every absent-family query wrong because a top-1 retrieval cannot abstain.

The sweep is run once per module.  Everything asserted here is a deterministic
function of the pre-registration commitment, so a failure is a real change in
the harness and never a flaky draw.
"""

from __future__ import annotations

import inspect
import math

import pytest

from scaling import CheckStatus, TouchLedger, record_from_ledger
from subspace import (
    COMMITMENT,
    MAX_BUCKET_SIZE,
    OBSERVATION_WINDOW,
    SIGNATURE_PREFIX,
    SUBSPACE_PLAN,
    Feature,
    FeatureLanguage,
    Query,
    adequacy_of,
    admissible_rules,
    build_catalogue,
    feature_bits,
    feature_identifiability_witness,
    feature_language,
    feature_pool,
    populate_store,
    query_positions,
    query_stream,
    rule_admissibility,
    smallest_adequate_feature,
)
from subspace_arms import (
    ARM_ROLES,
    ARMS,
    SWEEP_NOTES,
    DiscoveringArm,
    ExactScanParent,
    FixedFeatureArm,
    NearestNeighbourParent,
    OracleKeyParent,
    SignatureHashParent,
    SubspaceArm,
    crossover_table,
    fits_for,
    format_feature_table,
    format_fit_table,
    format_sweep_table,
    run_lifetime,
    sweep,
    sweep_table,
    unaudited_probe,
)
from run_subspace import terminal_for

BLIND_ARMS = (
    DiscoveringArm,
    FixedFeatureArm,
    SignatureHashParent,
    ExactScanParent,
    NearestNeighbourParent,
)


@pytest.fixture(scope="module")
def swept():
    return sweep()


@pytest.fixture(scope="module")
def rows(swept):
    return sweep_table(swept)


@pytest.fixture(scope="module")
def catalogue():
    return build_catalogue(1)


def _cells(swept, arm_id):
    return swept[arm_id].cells


def _rows_for(rows, arm_id):
    return [r for r in rows if r["arm_id"] == arm_id]


# --------------------------------------------------------------------------
# the frozen plan and the registered draw
# --------------------------------------------------------------------------


def test_commitment_is_a_pure_function_of_the_plan():
    from prereg import commit

    assert commit(SUBSPACE_PLAN).commitment == COMMITMENT.commitment


def test_query_positions_lie_far_outside_the_observation_window():
    """Answering needs the rule, not an echo of a handed-over observation."""
    assert all(p >= OBSERVATION_WINDOW for p in query_positions())
    assert min(query_positions()) >= SUBSPACE_PLAN["query_position_low"]
    assert len(set(query_positions())) == SUBSPACE_PLAN["query_positions"]


def test_scales_are_nested_so_a_k_change_cannot_be_a_method_change():
    small, large = build_catalogue(1), build_catalogue(3)
    assert large.stored[: small.n_methods] == small.stored
    assert small.n_objects == 2 * small.n_methods + 1


def test_every_stored_rule_extrapolates_to_every_query_position():
    """CL-D1(b).  If this failed, the correctness column would be measuring
    induction quality rather than retrieval."""
    from games import SubtractionGame

    for spec in build_catalogue(1).stored + build_catalogue(30).stored[-5:]:
        table = SubtractionGame(spec.moves).grundy_upto(max(query_positions()))
        for p in query_positions():
            assert spec.rule.grundy(p) == table[p]


def test_stored_rules_are_pairwise_distinct_on_the_observation_window():
    """Two methods are observation-equivalent iff they are equal.

    This is what makes ``exact_scan_parent`` a ground truth: at most one stored
    method can survive the observations, so ``AMBIGUOUS_MATCH`` cannot arise and
    a disagreement between arms is a retrieval difference, not a tie-break.
    """
    stored = build_catalogue(30).stored
    assert len({s.observations for s in stored}) == len(stored)


def test_held_out_families_are_served_by_no_stored_method_at_any_scale():
    largest = build_catalogue(30)
    stored = {s.observations for s in largest.stored}
    for spec in largest.held_out:
        assert spec.observations not in stored


def test_the_draw_reports_what_it_rejected():
    draw = admissible_rules()
    total = (
        len(draw.specs)
        + draw.rejected_value_out_of_language
        + draw.rejected_no_hypothesis
        + draw.rejected_extrapolation
        + draw.rejected_duplicate_rule
    )
    assert total == draw.candidates
    assert draw.rejected_extrapolation > 0


def test_a_stored_method_is_admissible_in_the_cl_d1_sense():
    verdict = rule_admissibility(build_catalogue(1).stored[0])
    assert verdict.verdict == "ADMISSIBLE"
    assert verdict.extrapolation_failures == 0


# --------------------------------------------------------------------------
# the feature language, counted exactly
# --------------------------------------------------------------------------


def test_feature_language_size_and_prior_bits_are_exact():
    language = feature_language()
    assert language.size() == 2 ** len(feature_pool()) - 1
    assert language.prior_bits() == pytest.approx(math.log2(language.size()))
    assert len(language.features()) == language.size()


def test_feature_language_is_enumerated_in_canonical_order():
    """Arity first, then lexicographic: 'the smallest adequate feature' has to
    mean one thing, or an arm's choice is an artefact of iteration order."""
    features = feature_language().features()
    keys = [(f.size, f.positions) for f in features]
    assert keys == sorted(keys)
    assert len(set(keys)) == len(keys)


def test_feature_images_are_a_function_of_the_method_alone():
    spec = build_catalogue(1).stored[0]
    feature = Feature((1, 5))
    assert feature.image(spec.observations) == feature.image_of_rule(spec.rule)


def test_feature_bits_acquired_grow_as_the_store_grows():
    """The store's own contents are what supply the information about where to
    key the index; at 1x almost nothing is ruled out."""
    small = feature_bits(build_catalogue(1).stored)
    large = feature_bits(build_catalogue(30).stored)
    assert small is not None and large is not None
    assert small.prior_bits == pytest.approx(feature_language().prior_bits())
    assert large.acquired_bits > small.acquired_bits
    assert large.consistent_size < small.consistent_size


def test_the_language_can_be_exhausted_and_says_so_with_a_witness():
    """The witnessed-obstruction path, exercised on a degenerate language.

    ``G(0) = 0`` for every subtraction family, so a language whose only feature
    is position ``0`` cannot separate anything.  The correct report is not "no
    adequate feature found after a while" but an exhibited pair of methods that
    share an image and disagree at a registered query position, which any third
    party can recompute.
    """
    stored = build_catalogue(10).stored
    degenerate = FeatureLanguage((0,))
    chosen, tried = smallest_adequate_feature(stored, degenerate)
    assert chosen is None
    assert tried == degenerate.size()
    witness = feature_identifiability_witness(stored, Feature((0,)))
    assert witness is not None
    a, b, position = witness
    by_id = {s.method_id: s for s in stored}
    assert by_id[a].image(Feature((0,))) == by_id[b].image(Feature((0,)))
    assert by_id[a].predicts(position) != by_id[b].predicts(position)


def test_an_identifying_feature_has_no_witness():
    stored = build_catalogue(1).stored
    feature, _ = smallest_adequate_feature(stored)
    assert feature is not None
    full = Feature(tuple(range(OBSERVATION_WINDOW)))
    assert feature_identifiability_witness(stored, full) is None


# --------------------------------------------------------------------------
# the query stream: both classes, and both load-bearing
# --------------------------------------------------------------------------


def test_the_query_stream_contains_both_classes_and_withholds_nothing_else():
    stream = query_stream()
    assert sum(1 for q in stream if q.in_store) > 0
    assert sum(1 for q in stream if not q.in_store) > 0
    assert len({len(q.observations) for q in stream}) == 1
    assert all(len(q.observations) == OBSERVATION_WINDOW for q in stream)
    assert all(q.position in query_positions() for q in stream)


def test_in_store_queries_are_served_at_every_scale_and_absent_ones_never():
    for multiplier in SUBSPACE_PLAN["multipliers"]:
        stored = {s.observations for s in build_catalogue(multiplier).stored}
        for query in query_stream():
            assert (query.observations in stored) is query.in_store


def test_expected_outcome_is_declared_by_the_query_not_by_the_arm():
    stream = query_stream()
    assert {q.expected_outcome for q in stream} == {"ANSWERED", "NO_METHOD_APPLIES"}


# --------------------------------------------------------------------------
# (a) the machine arm
# --------------------------------------------------------------------------


def test_discovering_arm_k_stays_inside_the_declared_bucket_bound(swept):
    for cell in _cells(swept, "discovering_arm"):
        assert not cell.k_unmeasured
        assert cell.k_max is not None and cell.k_max <= MAX_BUCKET_SIZE


def test_discovering_arm_k_over_n_falls_as_the_store_grows(swept):
    ratios = [c.k_max / c.n_objects for c in _cells(swept, "discovering_arm")]
    assert ratios == sorted(ratios, reverse=True)
    assert ratios[-1] < ratios[0] / 10


def test_discovering_arm_re_indexes_when_growth_breaks_its_feature(swept):
    cells = _cells(swept, "discovering_arm")
    features = [c.feature_id for c in cells]
    assert len(set(features)) > 1, "a feature that never changed did not need discovering"
    assert [c.re_index_count for c in cells] == sorted(c.re_index_count for c in cells)
    assert cells[-1].re_index_count >= len(set(features)) - 1


def test_discovering_arm_holds_an_adequate_feature_at_every_scale(swept):
    for cell in _cells(swept, "discovering_arm"):
        assert cell.adequacy is not None
        assert cell.adequacy.adequate
        assert cell.adequacy.max_bucket <= MAX_BUCKET_SIZE


def test_discovering_arm_reproduces_the_scorers_smallest_adequate_feature(swept):
    """The arm searches; the scorer computes.  They must land on the same
    feature, or the arm's search is not the procedure the receipt describes."""
    for cell in _cells(swept, "discovering_arm"):
        catalogue = build_catalogue(cell.multiplier)
        expected, _ = smallest_adequate_feature(catalogue.stored)
        assert expected is not None
        assert cell.feature_id == expected.feature_id


def test_discovering_arm_is_correct_on_both_query_classes(swept):
    for cell in _cells(swept, "discovering_arm"):
        assert cell.in_store_correct == cell.in_store_queries
        assert cell.absent_correct == cell.absent_queries
        assert cell.false_matches == 0 and cell.missed_matches == 0


def test_re_index_cost_is_charged_as_maintenance_and_never_to_a_query(swept):
    """Attack A8 in this experiment's coordinates: an arm cannot look sparse per
    query by doing its re-indexing on a ledger the query never sees, because the
    growth record carries it and the row prints the lifetime total."""
    cells = _cells(swept, "discovering_arm")
    for cell in cells:
        for record in cell.records:
            assert record.index_build_work == 0
            assert record.index_maintenance_work == 0
    growth = [c.growth_record for c in cells if c.growth_record is not None]
    assert any(g.index_maintenance_work > 0 for g in growth)
    assert cells[-1].lifetime_index_maintenance_work > cells[0].lifetime_index_maintenance_work


def test_the_discovering_arm_pays_for_its_search_cache_in_index_bytes(swept):
    """The ability to re-index is persistent state and is charged as such."""
    machine = {c.scale_id: c for c in _cells(swept, "discovering_arm")}
    parent = {c.scale_id: c for c in _cells(swept, "signature_hash_parent")}
    for scale, cell in machine.items():
        assert cell.index_bytes > parent[scale].index_bytes


# --------------------------------------------------------------------------
# (b) the ablation, and the harness self-check it provides
# --------------------------------------------------------------------------


def test_fixed_feature_arm_never_re_indexes_and_keeps_its_first_feature(swept):
    cells = _cells(swept, "fixed_feature_arm")
    assert {c.feature_id for c in cells} == {cells[0].feature_id}
    assert all(c.re_index_count == 0 for c in cells)


def test_fixed_feature_arm_k_tracks_n(swept):
    """The self-check.  A harness in which not-noticing looks free cannot be
    believed about noticing."""
    cells = _cells(swept, "fixed_feature_arm")
    ks = [c.k_max for c in cells]
    ns = [c.n_objects for c in cells]
    assert ks == sorted(ks)
    slope = math.log10(ks[-1] / ks[0]) / math.log10(ns[-1] / ns[0])
    assert slope > 0.8
    assert cells[-1].adequacy is not None and not cells[-1].adequacy.adequate


def test_fixed_feature_arm_is_dense_but_still_exactly_as_correct(swept):
    """Not noticing costs work, not answers.  Reporting it as a correctness
    failure would overstate the machine arm's advantage."""
    machine = {c.scale_id: c for c in _cells(swept, "discovering_arm")}
    fixed = {c.scale_id: c for c in _cells(swept, "fixed_feature_arm")}
    for scale, cell in fixed.items():
        assert cell.decisions_correct == machine[scale].decisions_correct
        assert cell.k_max >= machine[scale].k_max


def test_the_ablation_differs_from_the_machine_arm_only_after_growth(swept):
    """One class, one flag.  At the install scale the two arms are identical."""
    machine = _cells(swept, "discovering_arm")[0]
    fixed = _cells(swept, "fixed_feature_arm")[0]
    assert machine.feature_id == fixed.feature_id
    assert machine.k_max == fixed.k_max
    assert machine.query_work_mean == fixed.query_work_mean
    assert machine.lifetime_index_build_work == fixed.lifetime_index_build_work
    assert FixedFeatureArm.chooses_feature is DiscoveringArm.chooses_feature
    assert FixedFeatureArm.re_indexes is not DiscoveringArm.re_indexes


# --------------------------------------------------------------------------
# each parent's specific failure mode
# --------------------------------------------------------------------------


def test_oracle_key_parent_is_the_only_arm_given_the_family_identity():
    """The gift is a visible override, not a discipline nobody can check."""
    assert "_answer" in OracleKeyParent.__dict__
    for cls in BLIND_ARMS:
        assert "_answer" not in cls.__dict__
        source = inspect.getsource(cls)
        assert "family_id" not in source
        assert ".moves" not in source
        assert "in_store" not in source
        assert ".truth" not in source
    assert "query.moves" in inspect.getsource(SubspaceArm.query)


def test_oracle_key_parent_cannot_answer_without_the_identity_it_was_given():
    """Its failure mode: remove the gift and the arm has no procedure at all."""
    arm = OracleKeyParent(build_catalogue(1))
    with pytest.raises(AssertionError):
        arm._answer_blind(query_stream()[0].observations, 40, TouchLedger())


def test_oracle_key_parent_is_the_ceiling_on_k_and_query_work(swept):
    oracle = _cells(swept, "oracle_key_parent")
    assert {c.k_max for c in oracle} == {1}
    assert len({c.query_work_mean for c in oracle}) == 1
    for arm_id in ARMS:
        for mine, theirs in zip(oracle, _cells(swept, arm_id)):
            assert mine.query_work_mean <= theirs.query_work_mean + 1e-9


def test_exact_scan_parent_touches_every_object_and_is_never_wrong(swept):
    """Its failure mode is cost, not correctness, which is why it is the
    denominator of the crossover query count."""
    for cell in _cells(swept, "exact_scan_parent"):
        assert cell.k_max == cell.n_objects
        assert cell.k_mean == cell.n_objects
        assert cell.decisions_correct == len(cell.outcomes)
        assert cell.lifetime_index_build_work == 0
        assert cell.lifetime_index_maintenance_work == 0


def test_exact_scan_parent_query_work_is_linear_in_n(rows):
    fit = fits_for(rows)["exact_scan_parent"]["query_work(N)"]
    assert fit["verdict"] == "POWER_LAW_CONSISTENT"
    assert fit["slope"] == pytest.approx(1.0, abs=0.05)


def test_signature_hash_parent_is_adequate_and_wins_at_the_small_scales(swept):
    """The result the discipline requires to be reported as the headline: where
    the hand-specified prefix is adequate the ordinary index is not merely
    sufficient, it is cheaper, because it pays no search."""
    machine = {c.scale_id: c for c in _cells(swept, "discovering_arm")}
    parent = _cells(swept, "signature_hash_parent")
    adequate = [c for c in parent if c.adequacy is not None and c.adequacy.adequate]
    assert adequate, "no scale at which the hand-specified feature is adequate"
    for cell in adequate:
        mine = machine[cell.scale_id]
        assert cell.k_max <= mine.k_max
        assert cell.query_work_mean <= mine.query_work_mean
        assert cell.lifetime_index_work < mine.lifetime_index_work
        assert cell.decisions_correct == mine.decisions_correct


def test_signature_hash_parent_loses_adequacy_when_growth_breaks_its_prefix(swept):
    """Its failure mode: the key gets slower, never wrong.  A hand-specified
    prefix that collides still separates on verification, at the price of
    reading the whole bucket."""
    parent = _cells(swept, "signature_hash_parent")
    inadequate = [c for c in parent if c.adequacy is not None and not c.adequacy.adequate]
    assert inadequate, "the hand-specified prefix never became inadequate"
    machine = {c.scale_id: c for c in _cells(swept, "discovering_arm")}
    for cell in inadequate:
        assert cell.adequacy.max_bucket > MAX_BUCKET_SIZE
        assert cell.k_max > machine[cell.scale_id].k_max
        assert cell.decisions_correct == len(cell.outcomes)
    assert all(c.re_index_count == 0 for c in parent)
    assert SignatureHashParent.chooses_feature is False


def test_signature_hash_parent_key_is_non_identifying_before_it_is_inadequate(swept):
    """Adequacy and identifiability are different properties, and the sweep
    reports both rather than conflating them."""
    prefix = Feature(SIGNATURE_PREFIX)
    witnesses = {
        m: feature_identifiability_witness(build_catalogue(m).stored, prefix)
        for m in SUBSPACE_PLAN["multipliers"]
    }
    assert any(w is not None for w in witnesses.values())
    for multiplier, witness in witnesses.items():
        if witness is None:
            continue
        stored = {s.method_id: s for s in build_catalogue(multiplier).stored}
        a, b, position = witness
        assert stored[a].image(prefix) == stored[b].image(prefix)
        assert stored[a].predicts(position) != stored[b].predicts(position)


def test_nearest_neighbour_parent_answers_everything_including_what_it_should_not(swept):
    """Its failure mode, measured and not hidden: a top-1 retrieval cannot
    abstain, so every absent-family query becomes a false match."""
    for cell in _cells(swept, "nearest_neighbour_parent"):
        assert cell.answered == len(cell.outcomes)
        assert cell.false_matches == cell.absent_queries
        assert cell.absent_correct == 0
        assert cell.in_store_correct == cell.in_store_queries
        assert cell.decision_error_rate == pytest.approx(
            cell.absent_queries / len(cell.outcomes)
        )


def test_nearest_neighbour_parent_has_k_of_one_and_linear_query_work(swept, rows):
    """The second reason ``k`` is never read alone: an arm can read exactly one
    object and still do work linear in ``N`` to decide which one."""
    cells = _cells(swept, "nearest_neighbour_parent")
    assert {c.k_max for c in cells} == {1}
    fit = fits_for(rows)["nearest_neighbour_parent"]["query_work(N)"]
    assert fit["slope"] == pytest.approx(1.0, abs=0.1)


def test_a_sparse_arm_can_still_be_the_worst_arm_in_the_table(swept):
    """The cache_parent lesson from the previous pilot, restated in this one's
    coordinates and asserted rather than described."""
    nn = _cells(swept, "nearest_neighbour_parent")[-1]
    scan = _cells(swept, "exact_scan_parent")[-1]
    assert nn.k_max < scan.k_max
    assert nn.decisions_correct < scan.decisions_correct


# --------------------------------------------------------------------------
# (c) correctness, identical information, and the shared scaffolding
# --------------------------------------------------------------------------


def test_every_arm_answers_the_same_queries_against_the_same_store(swept):
    shapes = {
        arm_id: [(c.n_objects, c.n_methods, c.store_bytes, len(c.outcomes)) for c in cells.cells]
        for arm_id, cells in swept.items()
    }
    assert len(set(map(str, shapes.values()))) == 1


def test_every_arm_calls_the_checker_exactly_once_per_query(swept):
    for result in swept.values():
        for cell in result.cells:
            assert all(r.checker_calls == 1 for r in cell.records)


def test_no_arm_reports_a_k_larger_than_n_or_unequal_to_its_touches(swept):
    for result in swept.values():
        for cell in result.cells:
            for record in cell.records:
                assert record.k == len(record.touched_ids)
                assert record.k <= record.n_objects
                assert record.k_status is CheckStatus.MEASURED


def test_no_arm_answers_an_absent_query_correctly_by_accident(swept):
    """An arm that guesses on an absent query and happens to be right about the
    P-position is not correct here: the thing under test is whether it can tell
    that nothing in its memory applies."""
    for result in swept.values():
        for cell in result.cells:
            for outcome in cell.outcomes:
                if outcome.query.in_store:
                    continue
                if outcome.record.outcome == "ANSWERED":
                    assert outcome.decision_correct is False


def test_growth_adds_objects_without_rebuilding_the_arm():
    arm = DiscoveringArm(build_catalogue(1))
    before = arm.n_objects
    store_id = id(arm.store)
    record = arm.grow(build_catalogue(3))
    assert id(arm.store) == store_id
    assert arm.n_objects > before
    assert record.operation == "GROWTH"
    assert record.k == len(record.touched_ids)


def test_growth_refuses_a_non_nested_or_shrinking_scale():
    arm = DiscoveringArm(build_catalogue(3))
    with pytest.raises(ValueError):
        arm.grow(build_catalogue(1))


# --------------------------------------------------------------------------
# the accounting discipline inherited from scaling.py
# --------------------------------------------------------------------------


def test_the_uninstrumented_path_reports_cannot_check_not_a_flattering_k():
    record = unaudited_probe()
    assert record.k is None
    assert record.k_status is CheckStatus.CANNOT_CHECK
    assert record.touched_ids == ()
    assert record.cannot_check_reason
    assert record.sparse_verdict == "CANNOT_CHECK"


def test_a_poisoned_ledger_cannot_be_talked_into_a_number(catalogue):
    store = populate_store(catalogue)
    ledger = TouchLedger()
    store.read(catalogue.stored[0].method_id, ledger)
    assert ledger.k == 1
    list(store.unaudited_all_objects(ledger))
    assert ledger.k is None
    record = record_from_ledger(
        ledger,
        arm_id="x",
        scale_id=catalogue.scale_id,
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


def test_persistent_bytes_is_the_sum_of_its_declared_parts(swept):
    for result in swept.values():
        for cell in result.cells:
            assert cell.persistent_bytes == cell.store_bytes + cell.index_bytes
            for record in cell.records:
                assert record.persistent_bytes == record.store_bytes + record.index_bytes


def test_cannot_check_propagates_through_the_fit():
    from scaling import fit_loglog

    assert fit_loglog([1, 2, 3, 4], [1.0, None, 3.0, 4.0]).verdict == "CANNOT_CHECK"


# --------------------------------------------------------------------------
# the crossover, the table and the terminal
# --------------------------------------------------------------------------


def test_crossover_is_reported_for_every_arm_at_every_scale(rows):
    crossover = crossover_table(rows)
    assert "exact_scan_parent" not in crossover
    for arm_id in ARMS:
        if arm_id == "exact_scan_parent":
            continue
        assert set(crossover[arm_id]) == {
            f"{m}x" for m in SUBSPACE_PLAN["multipliers"]
        }
        for cell in crossover[arm_id].values():
            assert cell["queries_in_registered_stream"] == len(query_stream())


def test_an_index_that_never_repays_itself_is_reported_as_unreached(rows):
    """§4 of the scaling spec: an arm that looks sparse per query but never
    reaches crossover has moved the cost, not removed it."""
    crossover = crossover_table(rows)
    reached = {
        (arm, scale): cell["reached_within_stream"]
        for arm, per_scale in crossover.items()
        for scale, cell in per_scale.items()
    }
    assert False in reached.values() or None in reached.values(), (
        "no arm failed to reach crossover; the endpoint is not discriminating here "
        "and the receipt must say so"
    )


def test_sweep_table_carries_every_key_the_receipt_needs(rows):
    required = {
        "arm_id",
        "role",
        "scale",
        "N",
        "k_max",
        "k_over_N",
        "k_status",
        "query_work_mean",
        "lifetime_index_build_work",
        "lifetime_index_maintenance_work",
        "persistent_bytes",
        "decisions_correct",
        "in_store_correct",
        "absent_correct",
        "false_matches",
        "feature",
        "feature_adequacy",
        "re_indexes",
        "sparse_verdict",
    }
    for row in rows:
        assert required <= set(row)


def test_terminal_is_a_pure_function_of_the_table(rows):
    crossover = crossover_table(rows)
    assert terminal_for(rows, crossover) == terminal_for(rows, crossover)


def test_terminal_puts_correctness_before_sparsity(rows):
    """The gate declared in ``run_subspace``: an arm that is sparse and wrong is
    not better, and no sparsity coordinate is read past that point."""
    broken = [dict(r) for r in rows]
    for row in broken:
        if row["arm_id"] == "discovering_arm":
            row["decisions_correct"] = "40/50"
    terminal, _ = terminal_for(broken, crossover_table(rows))
    assert terminal == "DISCOVERED_INDEX_NOT_CORRECT"


def test_terminal_reports_parent_sufficient_when_the_parent_ties(rows):
    """If a future edit made the hand-specified index match the machine arm
    everywhere, the receipt must say PARENT_SUFFICIENT and not bury it."""
    tied = []
    for row in rows:
        copy = dict(row)
        if copy["arm_id"] == "signature_hash_parent":
            machine = next(
                r for r in rows if r["arm_id"] == "discovering_arm" and r["scale"] == copy["scale"]
            )
            copy.update(
                {
                    "k_max": machine["k_max"],
                    "query_work_mean": machine["query_work_mean"],
                    "lifetime_index_work": machine["lifetime_index_work"],
                    "decisions_correct": machine["decisions_correct"],
                }
            )
        tied.append(copy)
    terminal, reason = terminal_for(tied, crossover_table(rows))
    assert terminal == "PARENT_SUFFICIENT"
    assert "property of the key" in reason or "plain inverted index" in reason


def test_terminal_reports_cannot_check_above_everything_else(rows):
    poisoned = [dict(r) for r in rows]
    for row in poisoned:
        if row["arm_id"] == "discovering_arm":
            row["k_status"] = "CANNOT_CHECK"
    terminal, _ = terminal_for(poisoned, crossover_table(rows))
    assert terminal == "CANNOT_CHECK_UNINSTRUMENTED_RETRIEVAL_PATH"


def test_the_registered_terminal_of_this_sweep(rows):
    """The terminal this table actually produces, pinned so that a future edit
    which changes it has to change this test and say why."""
    terminal, _ = terminal_for(rows, crossover_table(rows))
    assert terminal == "INDEX_MAINTENANCE_DOMINATES"


# --------------------------------------------------------------------------
# determinism, roles and the notes
# --------------------------------------------------------------------------


def test_the_sweep_is_deterministic():
    first = sweep(["discovering_arm", "signature_hash_parent"], multipliers=[1, 3])
    second = sweep(["discovering_arm", "signature_hash_parent"], multipliers=[1, 3])
    assert sweep_table(first) == sweep_table(second)


def test_run_lifetime_matches_the_sweep_for_one_arm():
    one = run_lifetime("fixed_feature_arm", multipliers=[1, 3])
    many = sweep(["fixed_feature_arm"], multipliers=[1, 3])["fixed_feature_arm"]
    assert [c.as_dict() for c in one.cells] == [c.as_dict() for c in many.cells]


def test_every_registered_arm_runs_at_every_frozen_scale(swept):
    assert set(swept) == set(ARMS) == set(SUBSPACE_PLAN["arms"])
    for result in swept.values():
        assert [c.scale_id for c in result.cells] == [
            f"{m}x" for m in SUBSPACE_PLAN["multipliers"]
        ]


def test_roles_are_declared_and_exactly_one_arm_is_the_machine():
    assert sum(1 for r in ARM_ROLES.values() if r == "MACHINE") == 1
    assert sum(1 for r in ARM_ROLES.values() if r == "CEILING") == 1
    assert sum(1 for r in ARM_ROLES.values() if r == "ABLATION") == 1
    assert sum(1 for r in ARM_ROLES.values() if r == "PARENT") == 3


def test_the_sweep_states_its_own_limitations():
    joined = " ".join(SWEEP_NOTES).lower()
    for phrase in (
        "property of the key",
        "parent_sufficient",
        "cannot abstain",
        "no early exit",
        "prototype_scale_too_small_for_claim",
    ):
        assert phrase in joined


def test_the_report_renders(swept, rows):
    assert "discovering_arm" in format_sweep_table(swept)
    assert "witness" in format_feature_table(swept)
    assert "verdict" in format_fit_table(rows)
