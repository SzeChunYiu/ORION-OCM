"""Tests for E4: blind perturbation and the policy-independent repair oracle.

These tests are written to fail loudly if the experiment quietly turns back
into the thing it was built to replace.  Three properties carry the weight:

* the oracle cannot see the perturbation record --- asserted behaviourally, by
  source inspection of its call graph, and by poisoning it at runtime;
* no arm can reach the oracle or the record either;
* multi-perturbation worlds really do decouple the ground-truth level from the
  edits that produced them.  A draw in which they do not is a degenerate draw
  and the experiment has failed at its one job, so the assertion is made on the
  protected draw itself rather than on a convenient one.

The remaining tests pin each arm's specific failure mode, so that a change
which quietly strengthens a parent fails here rather than silently inflating
the governed policy's apparent advantage.
"""

from __future__ import annotations

import ast
import inspect
import textwrap

import pytest

import escalation
import escalation_independent as ei
import escalation_parents
from escalation import JUMP_THRESHOLD, Level, diagnose
from escalation_parents import PARENTS, cegar_parent, saturation_parent, timeout_parent
from games import MultiHeapGame, SubtractionGame
from prereg import commit
from run_escalation_independent import (
    ARTIFACT_TOLERANCE,
    MATERIAL_MARGIN_FRACTION,
    PLAN,
    generator_artifact_verdict,
    terminal_for,
)

# --------------------------------------------------------------------------
# the protected draw, computed once
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def commitment():
    return commit(PLAN)


@pytest.fixture(scope="module")
def protected(commitment):
    return ei.draw_suite(commitment.protected_seed, PLAN["worlds"])


@pytest.fixture(scope="module")
def scored(protected):
    return ei.evaluate(protected)


@pytest.fixture(scope="module")
def verdicts(protected):
    return [ei.minimum_sufficient_level(w) for w in protected]


# --------------------------------------------------------------------------
# hand-built worlds: one family, exhaustive evidence, one edit at a time
# --------------------------------------------------------------------------

#: a family whose truth is expressible with XOR and with nothing else, so that
#: removing XOR is a genuine operator insufficiency rather than a cosmetic edit
XOR_ONLY_FAMILY = ei.Family(moves=(1, 2, 3), heaps=2, top=7)


def build(perturbations, observed=None, family=XOR_ONLY_FAMILY, world_id="T"):
    """A working setup for ``family`` carrying exactly ``perturbations``."""
    size = len(ei.family_positions(family))
    every = tuple(range(size))
    baseline = ei.Config(
        period_bound=ei.MAX_PERIOD,
        preperiod_bound=ei.MAX_PREPERIOD,
        value_bound=ei.MAX_VALUE,
        operators=ei.OPERATORS,
        representations=(ei.IDENTIFYING_REPRESENTATION,),
        conventions=("normal",),
        allowed_probes=every,
        probe_budget=size,
        observed=every if observed is None else tuple(observed),
    )
    return ei.build_world(world_id, family, baseline, tuple(perturbations))


def level_of(world) -> Level:
    return ei.minimum_sufficient_level(world).level


# --------------------------------------------------------------------------
# pre-registration
# --------------------------------------------------------------------------


def test_draw_is_deterministic_in_the_commitment(commitment):
    one = ei.draw_suite(commitment.protected_seed, 40)
    two = ei.draw_suite(commitment.protected_seed, 40)
    assert [w.world_id for w in one] == [w.world_id for w in two]
    assert [w.config for w in one] == [w.config for w in two]
    assert [w.actual_convention for w in one] == [w.actual_convention for w in two]


def test_changing_the_plan_changes_the_protected_draw():
    a = commit(dict(PLAN, worlds=PLAN["worlds"] + 1))
    b = commit(PLAN)
    assert a.protected_seed != b.protected_seed
    assert [w.config for w in ei.draw_suite(a.protected_seed, 20)] != [
        w.config for w in ei.draw_suite(b.protected_seed, 20)
    ]


# --------------------------------------------------------------------------
# the worlds are well posed and the truth is exact
# --------------------------------------------------------------------------


def test_every_registered_family_is_expressible_under_both_conventions():
    screen = ei.well_posedness_screen()
    assert screen["well_posed"], screen["families_not_expressible"]


@pytest.mark.parametrize(
    "family",
    [ei.Family((1, 2, 3), 2, 7), ei.Family((1, 3, 4), 3, 3), ei.Family((2, 3), 1, 40)],
    ids=lambda f: f.family_id,
)
def test_backward_induction_agrees_with_the_registered_sprague_grundy_oracle(family):
    """The new exact truth must not disagree with ``games.py``'s own oracle."""
    game = MultiHeapGame(SubtractionGame(family.moves), family.heaps)
    bits = ei.truth_bits(family, "normal")
    for i, position in enumerate(ei.family_positions(family)):
        assert bool((bits >> i) & 1) == game.is_p_position(position), position


def test_misere_truth_actually_differs_from_normal_play():
    for family in (XOR_ONLY_FAMILY, ei.Family((2, 3), 1, 40)):
        assert ei.truth_bits(family, "misere") != ei.truth_bits(family, "normal")


def test_hypothesis_pool_is_extensionally_deduplicated():
    pool = ei.hypothesis_pool(
        XOR_ONLY_FAMILY, ei.MAX_PERIOD, ei.MAX_PREPERIOD, ei.MAX_VALUE,
        ei.OPERATORS, (ei.IDENTIFYING_REPRESENTATION,), ("normal",),
    )
    assert len(pool) == len(set(pool))
    assert ei.truth_bits(XOR_ONLY_FAMILY, "normal") in pool


# --------------------------------------------------------------------------
# the oracle is independent of the perturbation record
# --------------------------------------------------------------------------


def _referenced_names(fn) -> set[str]:
    """Every name and attribute the function's own source mentions.

    Parsed, not grepped, so a docstring that *talks about* the perturbation
    record does not count as reading it --- which is exactly the distinction
    under test.
    """
    tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


ORACLE_CALL_GRAPH = (
    ei.minimum_sufficient_level,
    ei.minimum_sufficient_level_by_powerset,
    ei.identifies,
    ei.closure,
    ei.apply_repair,
    ei.hypothesis_pool,
    ei.consistent,
    ei.truth_bits,
)

FORBIDDEN_IN_ORACLE = {
    "perturbations",
    "perturbation_kinds",
    "perturbation_count",
    "nominal_intent_level",
    "NOMINAL_INTENT",
    "Perturbation",
    "_apply_perturbation",
    "_draw_perturbation",
}


@pytest.mark.parametrize("fn", ORACLE_CALL_GRAPH, ids=lambda f: f.__name__)
def test_oracle_call_graph_never_mentions_the_perturbation_record(fn):
    leaked = _referenced_names(fn) & FORBIDDEN_IN_ORACLE
    assert not leaked, f"{fn.__name__} reaches {sorted(leaked)}"


def test_oracle_verdict_is_unchanged_when_the_perturbation_record_is_falsified(protected):
    """Behavioural independence: rewrite the record, keep the verdict."""
    import dataclasses

    fake = (ei.Perturbation("flip_play_convention", ()),) * 2
    checked = 0
    for world in protected[:250]:
        forged = dataclasses.replace(world, perturbations=fake)
        assert ei.minimum_sufficient_level(forged) == ei.minimum_sufficient_level(world)
        checked += 1
    assert checked == 250


def test_level_walk_is_exhaustive_over_the_whole_repair_powerset(protected):
    """Walking levels must equal minimising ``max(cost)`` over every subset."""
    for world in protected[:60]:
        assert ei.minimum_sufficient_level(world).level == ei.minimum_sufficient_level_by_powerset(world)


def test_every_drawn_world_is_repairable_within_the_lattice(verdicts):
    assert len(verdicts) == PLAN["worlds"]
    assert all(v.level in ei.LEVELS for v in verdicts)


# --------------------------------------------------------------------------
# no arm can reach the oracle or the record
# --------------------------------------------------------------------------

ARM_CALL_GRAPH = (
    diagnose,
    escalation._survivors,
    escalation._find_splitting_probe,
    escalation.identifiability_witness,
    escalation_parents._base,
    ei.to_escalation_world,
) + tuple(PARENTS.values())

FORBIDDEN_IN_ARMS = FORBIDDEN_IN_ORACLE | {
    "minimum_sufficient_level",
    "minimum_sufficient_level_by_powerset",
    "OracleVerdict",
    "identifies",
    "apply_repair",
    "closure",
    "intent_audit",
    "decoupling_audit",
}


@pytest.mark.parametrize("fn", ARM_CALL_GRAPH, ids=lambda f: f.__name__)
def test_no_arm_reaches_the_oracle_or_the_perturbation_record(fn):
    leaked = _referenced_names(fn) & FORBIDDEN_IN_ARMS
    assert not leaked, f"{fn.__name__} reaches {sorted(leaked)}"


def test_arms_still_run_with_the_oracle_poisoned(protected, monkeypatch):
    """Runtime proof, not just a source read: break the oracle, run every arm."""
    views = [ei.to_escalation_world(w) for w in protected[:120]]

    def poisoned(*_args, **_kwargs):
        raise AssertionError("an arm called the repair oracle")

    monkeypatch.setattr(ei, "minimum_sufficient_level", poisoned)
    monkeypatch.setattr(ei, "minimum_sufficient_level_by_powerset", poisoned)
    for fn in ei.ARMS.values():
        for view in views:
            assert isinstance(fn(view).level, Level)


def test_the_adapter_never_carries_the_ground_truth_level(protected, verdicts):
    """``EscalationWorld.minimum_sufficient_level`` must stay uninformative."""
    escalated = [w for w, v in zip(protected, verdicts) if v.level >= JUMP_THRESHOLD]
    assert escalated, "the draw contains no world above the Jump threshold"
    for world in escalated[:50]:
        assert ei.to_escalation_world(world).minimum_sufficient_level is Level.L0_NO_ESCALATION


def test_every_arm_is_scored_on_identical_visible_state(protected):
    for world in protected[:60]:
        view = ei.to_escalation_world(world)
        for fn in ei.ARMS.values():
            d = fn(view)
            assert d.budget_remaining == world.config.probe_budget
            assert d.version_space_size >= 0


# --------------------------------------------------------------------------
# the draw is not degenerate
# --------------------------------------------------------------------------


def test_multi_perturbation_worlds_occur(protected):
    counts = {0: 0, 1: 0, 2: 0}
    for world in protected:
        counts[world.perturbation_count] += 1
    assert counts[0] > 0
    assert counts[1] > 0
    assert counts[2] > 0, "no world carries two simultaneous perturbations"


def test_every_registered_perturbation_kind_is_actually_drawn(protected):
    drawn = {k for w in protected for k in w.perturbation_kinds}
    assert drawn == set(ei.PERTURBATION_KINDS), set(ei.PERTURBATION_KINDS) - drawn


def test_the_draw_reaches_every_registered_level(verdicts):
    seen = {v.level for v in verdicts}
    missing = set(ei.LEVELS) - seen
    assert not missing, f"no world requires {sorted(l.name for l in missing)}"


def test_zero_perturbation_worlds_are_the_no_escalation_control(protected, verdicts):
    controls = [v for w, v in zip(protected, verdicts) if w.perturbation_count == 0]
    assert controls
    assert all(v.level < JUMP_THRESHOLD for v in controls)


def test_two_perturbation_levels_decouple_from_the_individual_edits(protected):
    """The load-bearing property.  Without it the generator is still degenerate.

    ``higher_than_both`` counts worlds where neither edit alone required that
    level: dropping evidence needs a probe, restricting the channel removes the
    probe that would have worked, and only widening the channel repairs both.
    """
    audit = ei.decoupling_audit(protected)
    assert audit["two_perturbation_worlds"] > 0
    assert audit["higher_than_both"] > 0, (
        "no two-perturbation world requires a higher level than either edit alone; "
        "the joint level is a function of the individual edits and the generator is degenerate"
    )


def test_the_oracle_disagrees_with_the_generator_intent_label(protected):
    """The old procedure's label is not the ground truth, and this shows it."""
    audit = ei.intent_audit(protected)
    assert audit["intent_agreement_rate"] < 1.0
    assert audit["intent_overstates_required_level"] > 0
    assert audit["oracle_below_both_intents"] > 0, (
        "no two-perturbation world lands below both of its edits' nominal defect levels; "
        "the perturbations are still standing in for defect types"
    )


# --------------------------------------------------------------------------
# the oracle's verdicts on hand-built worlds
# --------------------------------------------------------------------------


def test_a_working_setup_needs_no_escalation():
    assert level_of(build(())) is Level.L0_NO_ESCALATION


def test_a_spent_budget_never_changes_the_ground_truth():
    """Exhaustion is not an obstruction, made a property of the oracle."""
    baseline = level_of(build(()))
    for spent in (0, 1, 2):
        assert level_of(build((ei.Perturbation("cut_probe_budget", (spent,)),))) is baseline
    dropped = (ei.Perturbation("drop_evidence", (0, 1, 2)),)
    with_budget = level_of(build(dropped))
    without = level_of(build(dropped + (ei.Perturbation("cut_probe_budget", (0,)),)))
    assert with_budget is without


def test_a_bound_that_excludes_the_truth_is_a_local_repair():
    world = build((ei.Perturbation("shrink_value_bound", (2,)),))
    verdict = ei.minimum_sufficient_level(world)
    assert verdict.level is Level.L3_LOCAL_REPAIR
    assert verdict.repair == "relax_value_bound"


def test_removing_the_only_operator_that_fits_is_operator_insufficiency():
    world = build((ei.Perturbation("remove_operators", ("XOR",)),))
    verdict = ei.minimum_sufficient_level(world)
    assert verdict.level is Level.L4_OPERATOR_INSUFFICIENT
    assert verdict.repair == "widen_operator_vocabulary"


def test_a_colliding_representation_is_a_representation_change():
    world = build((ei.Perturbation("coarsen_representation", ("token_total",)),))
    verdict = ei.minimum_sufficient_level(world)
    assert verdict.level is Level.L5_REPRESENTATION_CHANGE
    assert verdict.repair == "add_identifying_representation"


def test_a_coarsening_that_does_not_collide_costs_nothing():
    """``sorted_heaps`` is a coarsening; only the oracle can say it is harmless."""
    world = build((ei.Perturbation("coarsen_representation", ("sorted_heaps",)),))
    assert level_of(world) is Level.L0_NO_ESCALATION


def test_the_wrong_play_convention_is_a_formulation_change():
    world = build((ei.Perturbation("flip_play_convention", ()),))
    verdict = ei.minimum_sufficient_level(world)
    assert verdict.level is Level.L6_FORMULATION_CHANGE
    assert verdict.repair == "admit_misere_convention"


def test_a_probe_channel_confined_to_what_is_already_observed_needs_more_evidence():
    world = build(
        (ei.Perturbation("restrict_probe_set", (0, 1)),),
        observed=(0, 1, 2),
    )
    verdict = ei.minimum_sufficient_level(world)
    assert verdict.level is Level.L2_MORE_EVIDENCE
    assert verdict.repair == "widen_probe_channel"


def test_two_bounds_that_are_individually_harmless_can_bind_together():
    """A worked instance of ``higher_than_both``, built rather than found."""
    family = ei.Family((1, 3), 1, 40)
    alone_a = build((ei.Perturbation("drop_evidence", ()),), observed=(), family=family)
    alone_b = build((ei.Perturbation("restrict_probe_set", (0,)),), family=family)
    both = build(
        (ei.Perturbation("drop_evidence", ()), ei.Perturbation("restrict_probe_set", (0,))),
        family=family,
    )
    assert int(level_of(both)) > max(int(level_of(alone_a)), int(level_of(alone_b)))


# --------------------------------------------------------------------------
# each arm's specific behaviour
# --------------------------------------------------------------------------


def test_governed_policy_refuses_to_escalate_on_budget_exhaustion():
    """The single most important hostile, restated on a blindly built world."""
    world = build(
        (
            ei.Perturbation("drop_evidence", (0,)),
            ei.Perturbation("cut_probe_budget", (0,)),
        )
    )
    assert level_of(world) is Level.L1_SEARCH_MORE
    view = ei.to_escalation_world(world)
    governed = diagnose(view)
    assert governed.terminal == "BUDGET_EXHAUSTED"
    assert not governed.is_jump
    assert governed.splitting_probe is not None
    assert timeout_parent(view).is_jump, "the timeout parent must escalate here"
    verdict = ei.minimum_sufficient_level(world)
    assert not ei.score_row(world, governed, verdict)["false_escalation"]
    assert ei.score_row(world, timeout_parent(view), verdict)["false_escalation"]


def test_saturation_alone_does_not_authorise_escalation():
    world = build((ei.Perturbation("restrict_probe_set", (0, 1)),), observed=(0, 1, 2))
    view = ei.to_escalation_world(world)
    governed = diagnose(view)
    assert governed.terminal == "SATURATED_WITHIN_REGISTERED_SPACE"
    assert governed.level is Level.L2_MORE_EVIDENCE
    assert not governed.is_jump
    assert saturation_parent(view).is_jump, "the saturation parent must escalate here"


def test_cegar_parent_over_refines_on_a_bound_defect():
    world = build((ei.Perturbation("shrink_value_bound", (2,)),))
    view = ei.to_escalation_world(world)
    assert diagnose(view).level is Level.L3_LOCAL_REPAIR
    assert cegar_parent(view).level is Level.L5_REPRESENTATION_CHANGE


def test_exact_repair_planner_matches_the_governed_policy_on_a_bound_defect():
    """The fully-resourced parent is not weakened; on its home ground it ties."""
    world = build((ei.Perturbation("shrink_value_bound", (2,)),))
    view = ei.to_escalation_world(world)
    planner = PARENTS["exact_repair_planner"](view)
    assert planner.level is Level.L3_LOCAL_REPAIR
    assert planner.terminal == "MINIMUM_REPAIR_IS_A_BOUND"
    assert planner.level == diagnose(view).level


def test_representation_obstruction_is_exhibited_not_inferred():
    world = build((ei.Perturbation("coarsen_representation", ("token_total",)),))
    view = ei.to_escalation_world(world)
    governed = diagnose(view)
    assert governed.level is Level.L5_REPRESENTATION_CHANGE
    assert governed.obstruction_witness is not None
    a, b = governed.obstruction_witness
    assert view.representation.image(a) == view.representation.image(b)
    assert view.truth(a) != view.truth(b)


def test_saturation_terminal_is_never_impossibility(protected):
    for world in protected[:200]:
        assert diagnose(ei.to_escalation_world(world)).terminal != "PROBLEM_IMPOSSIBLE"


def test_the_governed_policy_makes_no_false_escalations_on_the_protected_draw(scored):
    """Replicates the programme's known asymmetry rather than discovering it."""
    assert scored["arms"]["governed"]["false_escalation"] == 0


@pytest.mark.parametrize("parent", ["timeout", "saturation", "cegar"])
def test_the_naive_parents_do_false_escalate(scored, parent):
    assert scored["arms"][parent]["false_escalation"] > 0


def test_every_arm_is_scored_on_the_same_worlds(scored):
    sizes = {v["n"] for v in scored["arms"].values()}
    assert sizes == {PLAN["worlds"]}
    assert set(scored["arms"]) == set(ei.ARMS)


def test_the_confusion_matrix_accounts_for_every_world(scored):
    for name, summary in scored["arms"].items():
        total = sum(sum(row.values()) for row in summary["confusion_matrix"].values())
        assert total == summary["n"], name


def test_accuracy_is_reported_for_every_perturbation_count(scored):
    for name, summary in scored["arms"].items():
        assert set(summary["accuracy_by_perturbation_count"]) == {"0", "1", "2"}
        assert all(cell["n"] > 0 for cell in summary["accuracy_by_perturbation_count"].values()), name


# --------------------------------------------------------------------------
# scoring and the decision rules
# --------------------------------------------------------------------------


def test_overreach_is_counted_even_below_the_jump_threshold():
    world = build(())
    verdict = ei.minimum_sufficient_level(world)
    assert verdict.level is Level.L0_NO_ESCALATION
    fake = escalation.Diagnosis(
        level=Level.L1_SEARCH_MORE, terminal="X", version_space_size=2,
        splitting_probe=None, obstruction_witness=None, budget_remaining=0,
        rationale="", work={},
    )
    row = ei.score_row(world, fake, verdict)
    assert row["overreach"] and not row["underreach"]
    assert not row["false_escalation"], "L1 is below the Jump threshold"


def test_missed_escalation_is_counted_when_the_truth_is_above_the_threshold():
    world = build((ei.Perturbation("flip_play_convention", ()),))
    verdict = ei.minimum_sufficient_level(world)
    fake = escalation.Diagnosis(
        level=Level.L1_SEARCH_MORE, terminal="X", version_space_size=2,
        splitting_probe=None, obstruction_witness=None, budget_remaining=0,
        rationale="", work={},
    )
    row = ei.score_row(world, fake, verdict)
    assert row["missed_escalation"] and row["underreach"]


def _summary(exact, false_escalation=0, n=1000):
    return {"n": n, "exact_match": exact, "accuracy": exact / n,
            "false_escalation": false_escalation}


def _pair(governed, parent, false_escalation=0, n=1000):
    return {"arms": {
        "governed": _summary(governed, false_escalation, n),
        "exact_repair_planner": _summary(parent, 0, n),
    }}


OLD = {"arms": {"governed": _summary(70, 0, 70), "exact_repair_planner": _summary(56, 0, 70)}}


def test_terminal_rule_reports_parent_sufficient_when_a_parent_wins():
    terminal, _ = terminal_for(_pair(800, 850), OLD)
    assert terminal == "PARENT_SUFFICIENT"


def test_terminal_rule_refuses_to_call_a_sub_margin_lead_a_separation():
    lead = int(MATERIAL_MARGIN_FRACTION * 1000)
    terminal, _ = terminal_for(_pair(800 + lead, 800), OLD)
    assert terminal == "PARENT_SUFFICIENT_WITHIN_REGISTERED_MARGIN"


def test_terminal_rule_reports_a_separation_only_beyond_the_margin():
    lead = int(MATERIAL_MARGIN_FRACTION * 1000) + 1
    terminal, _ = terminal_for(_pair(800 + lead, 800), OLD)
    assert terminal == "GOVERNED_POLICY_SEPARATES_ON_INDEPENDENTLY_GENERATED_WORLDS"
    terminal, _ = terminal_for(_pair(800 + lead, 800, false_escalation=1), OLD)
    assert terminal == "GOVERNED_POLICY_SEPARATES_BUT_FALSE_ESCALATES"


def test_artifact_verdict_fires_on_a_large_drop():
    verdict = generator_artifact_verdict(_pair(600, 600), OLD)
    assert verdict["verdict"] == "GENERATOR_ARTIFACT_CONFIRMED"
    assert verdict["accuracy_drop"] > ARTIFACT_TOLERANCE


def test_artifact_verdict_does_not_fire_inside_the_tolerance():
    verdict = generator_artifact_verdict(_pair(int(1000 * (1 - ARTIFACT_TOLERANCE / 2)), 900), OLD)
    assert verdict["verdict"] == "NO_ARTIFACT_AT_REGISTERED_TOLERANCE"


def test_old_generator_reference_reproduces_the_published_seventy_of_seventy():
    """The contrast is recomputed from the old plan, never quoted."""
    old = ei.old_generator_reference()
    assert old["n"] == 70
    assert old["arms"]["governed"]["exact_match"] == 70
    assert old["arms"]["governed"]["accuracy"] == 1.0
    assert old["arms"]["exact_repair_planner"]["exact_match"] < 70


def test_the_plan_names_every_arm_and_every_perturbation_kind():
    assert sorted(PLAN["arms"]) == sorted(ei.ARMS)
    assert set(PLAN["perturbation_kinds"]) == set(ei.PERTURBATION_KINDS)
    assert PLAN["jump_threshold"] == JUMP_THRESHOLD.name
