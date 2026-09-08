"""Tests for E5: library discovery versus reuse opportunity.

These are not smoke tests.  Each one asserts a property the experiment's
conclusion depends on, and several of them are written to fail if a future edit
makes the result easier:

* the four generator certifications, individually;
* the flat-mining ablation finding NOTHING on evidence where the step-level arm
  finds an admissible composite;
* the independent checker's independence, by source inspection;
* a REAL operating-system process boundary, failing if ``pid_before ==
  pid_after``;
* the tautological control showing no benefit -- without which a positive on
  the essential set means nothing;
* each parent's specific behaviour, including the two that share the mechanism
  under test on purpose;
* the leakage discipline adopted from the frozen protected protocol on branch
  ``codex/ocm-evolvability-independent-20260908``;
* the registered ``>=2`` threshold not having been lowered, and semantic
  weakening not having been added.
"""

from __future__ import annotations

import inspect
import itertools
import json
import math
import pathlib
import re

import pytest

import libdisc
import libdisc_arms
import libdisc_discovery
import libdisc_parents
from libdisc import (
    CHAIN2_SCHEMA,
    CHAIN_SCHEMA,
    CONTROL_TASKS,
    ESSENTIAL_COMPOSITE_TASKS,
    LEARNER_VISIBLE_EPISODE_FIELDS,
    LEARNER_VISIBLE_TASK_FIELDS,
    MERGE_SCHEMA,
    N_ASSIGNMENTS,
    N_PREDS,
    REPEATED_SUPPORT_THRESHOLD,
    TAUTOLOGICAL_CONTROL_TASKS,
    TRAINING_EPISODES,
    UNSOUND_TRAP_TASKS,
    LearnerView,
    Task,
    TaskView,
    certify_draw,
    entails,
    instantiate,
    learner_views,
    match_schema,
    min_derivation_length,
    resolve,
    schema_from_body,
    schema_is_sound,
    solve,
    subsumes,
)

HERE = pathlib.Path(__file__).resolve().parent
ARM = "libdisc_discovery_arm"
REFERENCE = "reset_arm"


# --------------------------------------------------------------------------
# fixtures: computed once, because several of them spawn processes
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def views():
    return learner_views()


@pytest.fixture(scope="module")
def certification():
    return certify_draw()


@pytest.fixture(scope="module")
def discovery(views):
    return libdisc_discovery.discover(views)


@pytest.fixture(scope="module")
def ablation(views):
    return libdisc_discovery.flat_mining_ablation(views)


@pytest.fixture(scope="module")
def sweep_out(views):
    return libdisc_arms.sweep(views)


@pytest.fixture(scope="module")
def summary(sweep_out):
    return libdisc_arms.summarise(sweep_out)


@pytest.fixture(scope="module")
def benefit(summary):
    return libdisc_arms.benefit_table(summary, REFERENCE)


@pytest.fixture(scope="module")
def custody():
    return libdisc_arms.custody_cycle()


# --------------------------------------------------------------------------
# the world is exact
# --------------------------------------------------------------------------


def test_domain_is_the_declared_one():
    assert N_PREDS == 8
    assert N_ASSIGNMENTS == 256
    assert libdisc.every(0, 1) == ((0, False), (1, True))
    assert libdisc.no(0, 1) == ((0, False), (1, False))


def test_checker_agrees_with_resolution_on_every_registered_task():
    """Whatever the search derives, the checker independently confirms."""
    for task in (ESSENTIAL_COMPOSITE_TASKS + TAUTOLOGICAL_CONTROL_TASKS
                 + CONTROL_TASKS):
        assert entails(task.premises, task.query)
    for task in UNSOUND_TRAP_TASKS:
        assert not entails(task.premises, task.query)


def test_resolution_is_sound():
    """Every resolvent the world can produce is entailed by its parents."""
    clauses = [libdisc.clause((a, sa), (b, sb))
               for a in range(4) for b in range(4) if a < b
               for sa in (False, True) for sb in (False, True)]
    checked = 0
    for c1, c2 in itertools.combinations(clauses, 2):
        for pivot in libdisc.pivots(c1, c2):
            r = resolve(c1, c2, pivot)
            if r is None:
                continue
            assert entails([c1, c2], r)
            checked += 1
    assert checked > 50


# --------------------------------------------------------------------------
# CERTIFICATION 1..4 -- the four properties, asserted individually
# --------------------------------------------------------------------------


def test_certification_1_flat_fragments_are_pairwise_distinct(certification):
    assert certification.flat_fragments_distinct
    assert certification.flat_fragment_max_multiplicity == 1
    assert certification.flat_fragment_count >= 3, (
        "the ablation must accept some fragments, or its emptiness is vacuous")


def test_certification_2_a_step_schema_recurs(certification):
    assert certification.step_schema_recurs
    assert certification.recurring_schema_episodes >= REPEATED_SUPPORT_THRESHOLD
    assert certification.recurring_schema_instances > (
        certification.recurring_schema_episodes - 1)
    assert certification.composite_schema_episodes >= REPEATED_SUPPORT_THRESHOLD
    assert certification.recurring_schema_id == CHAIN_SCHEMA.schema_id


def test_certification_3_essential_composite_tasks_exist(certification):
    assert certification.essential_composite_exists
    assert certification.essential_rows
    for row in certification.essential_rows:
        assert not row["tautology"]
        assert row["matched"]
        assert row["min_depth_without"] > row["min_depth_with"], row


def test_certification_4_tautological_and_bypassable_tasks_exist(certification):
    assert certification.tautological_control_exists
    assert certification.tautology_count > 0
    assert certification.bypass_count > 0
    for row in certification.control_rows:
        assert row["matched"], "a control row the schema does not match proves nothing"
        assert row["tautology"] or row["min_depth_without"] == row["min_depth_with"]


def test_all_four_certifications_pass_together(certification):
    assert certification.all_certified, certification.failures
    assert certification.fresh_disjoint_from_training


def test_minimal_derivation_length_is_computed_not_asserted():
    """Recompute properties 3 and 4 directly, without the certification path."""
    for task in ESSENTIAL_COMPOSITE_TASKS:
        without = min_derivation_length(task.premises, task.query, ())
        with_ = min_derivation_length(task.premises, task.query, (CHAIN2_SCHEMA,))
        assert without is not None and with_ is not None
        assert without > with_
    for task in TAUTOLOGICAL_CONTROL_TASKS:
        without = min_derivation_length(task.premises, task.query, ())
        with_ = min_derivation_length(task.premises, task.query, (CHAIN2_SCHEMA,))
        assert without == with_


# --------------------------------------------------------------------------
# the flat ablation finds nothing
# --------------------------------------------------------------------------


def test_flat_mining_ablation_returns_an_empty_pool(ablation):
    assert ablation.pool == ()
    assert ablation.funnel["pool"] == 0
    assert ablation.funnel["valid_essential"] > 0, (
        "the miner must accept sound, essential fragments and STILL find no "
        "repeated support; an empty candidate set would be a different failure")
    assert ablation.funnel["singleton_groups_excluded"] == (
        ablation.funnel["distinct_fragments"])


def test_step_level_finds_what_flat_level_cannot(discovery, ablation):
    assert ablation.funnel["pool"] == 0
    assert len(discovery.pool) > 0
    assert any(d.schema.step_count >= 2 for d in discovery.pool)


def test_the_ablation_arm_reaches_the_diagnosed_terminal(summary):
    for set_name in ("essential_composite", "tautological_control"):
        assert (summary["flat_mining_ablation"][set_name]["work_total"]
                == summary[REFERENCE][set_name]["work_total"])


# --------------------------------------------------------------------------
# CL-D1(c): the checker is independent, by source inspection
# --------------------------------------------------------------------------


FORBIDDEN_IN_CHECKER = (
    "schema", "Schema", "library", "Library", "store", "Store", "method",
    "Method", "learn", "discover", "pool", "macro", "episode", "Episode",
    "cache", "memo",
)


def _checker_code_without_docstring() -> str:
    """The executable body of ``entails``, with signature and prose removed."""
    import ast
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(entails)))
    fn = tree.body[0]
    stmts = fn.body[1:] if (
        isinstance(fn.body[0], ast.Expr)
        and isinstance(fn.body[0].value, ast.Constant)
        and isinstance(fn.body[0].value.value, str)) else fn.body
    return "\n".join(ast.unparse(node) for node in stmts)


def test_checker_source_mentions_no_learned_object():
    body = _checker_code_without_docstring()
    for token in FORBIDDEN_IN_CHECKER:
        assert token not in body, f"entails() mentions {token!r}"


def test_checker_signature_carries_no_state():
    sig = inspect.signature(entails)
    assert list(sig.parameters) == ["premises", "query"]
    for param in sig.parameters.values():
        assert param.default is inspect.Parameter.empty, (
            "a default argument is a channel for learned state")


def test_checker_calls_only_pure_clause_helpers():
    """Every name the checker's executable body touches is enumerated here.

    The point is not tidiness: an exhaustive whitelist means a future edit that
    reaches for a store, an index or a memo cannot pass this test quietly.
    """
    import ast

    names = {
        n.id if hasattr(n, "id") else getattr(n, "attr", "")
        for n in ast.walk(ast.parse(_checker_code_without_docstring()))
        if n.__class__.__name__ in ("Name", "Attribute")
    }
    assert names <= {
        "premises", "query", "assignment", "ok", "c", "range",
        "N_ASSIGNMENTS", "satisfies"}, names


def test_world_module_does_not_import_any_learner():
    src = (HERE / "libdisc.py").read_text()
    for module in ("libdisc_discovery", "libdisc_parents", "libdisc_arms"):
        assert f"import {module}" not in src
        assert f"from {module}" not in src


def test_checker_verdict_is_the_ground_truth_on_every_row(sweep_out):
    for row in sweep_out["rows"]:
        assert row["correct"], row
        if row["task_set"] == "unsound_traps":
            assert not row["entailed"]
            assert not row["solved"], (
                "an arm reported a non-entailment as proved; that is an unsound "
                "macro firing")


# --------------------------------------------------------------------------
# leakage discipline (adopted from the frozen protected protocol)
# --------------------------------------------------------------------------


def test_learner_visible_fields_are_exactly_the_input_and_correct_actions():
    assert tuple(LearnerView.__dataclass_fields__) == LEARNER_VISIBLE_EPISODE_FIELDS
    assert tuple(TaskView.__dataclass_fields__) == LEARNER_VISIBLE_TASK_FIELDS
    assert "episode_id" not in LearnerView.__dataclass_fields__
    assert "role" not in TaskView.__dataclass_fields__
    assert "task_id" not in TaskView.__dataclass_fields__


def test_evaluator_only_fields_exist_on_the_evaluator_records():
    assert TRAINING_EPISODES[0].episode_id
    assert ESSENTIAL_COMPOSITE_TASKS[0].task_id
    assert ESSENTIAL_COMPOSITE_TASKS[0].role
    for view in learner_views():
        assert not hasattr(view, "episode_id")
        assert not hasattr(view, "role")


EVALUATOR_ONLY_TOKENS = (
    ".episode_id", ".task_id", ".role", "certify_draw", "Certification",
    "ESSENTIAL_COMPOSITE_TASKS", "TAUTOLOGICAL_CONTROL_TASKS", "CONTROL_TASKS",
    "UNSOUND_TRAP_TASKS", "CHAIN2_SCHEMA", "TRAINING_EPISODES",
)


@pytest.mark.parametrize("module", ["libdisc_discovery.py", "libdisc_parents.py"])
def test_no_learner_module_can_reach_an_evaluator_only_field(module):
    src = (HERE / module).read_text()
    code = "\n".join(
        line for line in src.splitlines()
        if not line.lstrip().startswith("#"))
    code = re.sub(r'""".*?"""', "", code, flags=re.S)
    for token in EVALUATOR_ONLY_TOKENS:
        assert token not in code, f"{module} reaches evaluator-only {token!r}"


def test_learners_consume_learner_views_only(views):
    for fn in (libdisc_discovery.discover, libdisc_discovery.flat_mining_ablation,
               *libdisc_parents.PARENTS):
        params = list(inspect.signature(fn).parameters)
        assert params[0] == "views", fn.__name__
    assert all(isinstance(v, LearnerView) for v in views)


# --------------------------------------------------------------------------
# discipline: the threshold was not lowered, weakening was not added
# --------------------------------------------------------------------------


def test_repeated_support_threshold_is_two_everywhere():
    assert REPEATED_SUPPORT_THRESHOLD == 2
    assert (inspect.signature(libdisc_discovery.discover)
            .parameters["threshold"].default == 2)
    assert (inspect.signature(libdisc_discovery.admit)
            .parameters["threshold"].default == 2)
    assert (inspect.signature(libdisc_discovery.flat_mining_ablation)
            .parameters["threshold"].default == 2)


def test_singletons_are_refused_and_the_refusal_costs_something(discovery):
    singletons = [d for d in discovery.rejected
                  if d.admission.verdict == "REJECTED_SINGLETON_SUPPORT"]
    assert singletons, "a draw with no singleton is not testing the gate"
    for d in singletons:
        assert d.supports < REPEATED_SUPPORT_THRESHOLD
        assert d.schema.schema_id not in {p.schema.schema_id for p in discovery.pool}
    assert any(d.schema.step_count == 2 for d in singletons), (
        "the gate must be shown refusing a COMPOSITE too, which is where it "
        "costs the arm a row it would have won")


def test_redundant_sound_matches_are_counted_and_never_in_the_benefit(sweep_out):
    rows = [r for r in sweep_out["rows"] if r["arm"] == ARM]
    assert sum(r["redundant_sound_matches"] for r in rows) > 0, (
        "the semantic-incompleteness column must be exercised")
    src = inspect.getsource(libdisc_arms.benefit_table)
    assert "redundant" not in src, (
        "the benefit table must not read the redundant-match column")
    for row in rows:
        if row["redundant_sound_matches"] and not row["macro_fired"]:
            assert row["macro_ids"] == [], (
                "a redundant match must never be credited as an invocation")
    fired_rows = [r for r in rows if r["macro_fired"]]
    assert fired_rows
    for row in fired_rows:
        assert row["trace_length"] > 0


def test_no_wall_clock_enters_any_result():
    for name in ("libdisc.py", "libdisc_discovery.py", "libdisc_parents.py",
                 "libdisc_arms.py", "run_libdisc.py"):
        src = (HERE / name).read_text()
        assert "import time" not in src
        assert "perf_counter" not in src
        assert "datetime" not in src
        assert "time.time" not in src


# --------------------------------------------------------------------------
# CL-D1 admission is real
# --------------------------------------------------------------------------


def test_every_admitted_schema_is_sound_under_every_injective_binding(discovery):
    for d in discovery.pool:
        assert schema_is_sound(d.schema, sample_bindings=None)


def test_admission_requires_strict_compression_and_extrapolation(discovery):
    for d in discovery.pool:
        rec = d.admission
        assert rec.verdict == "ADMISSIBLE"
        assert rec.mdl.compression_ok
        assert rec.mdl.bits_method + rec.mdl.bits_residual < rec.mdl.bits_data
        assert rec.extrapolation_probes > 0
        assert rec.extrapolation_failures == 0
        assert rec.held_out_trials > 0 and rec.held_out_failures == 0
        assert rec.independence_ok


def test_a_verbatim_cache_would_be_inadmissible(discovery):
    """CL-T2 made concrete: coding the supports verbatim never compresses."""
    for d in discovery.pool:
        rec = d.admission
        verbatim_bits = rec.mdl.bits_data
        assert rec.mdl.bits_method + rec.mdl.bits_residual < verbatim_bits
        assert rec.mdl.bits_residual < verbatim_bits


def test_extrapolation_probes_lie_strictly_beyond_the_training_support(discovery):
    for d in discovery.pool:
        max_pred = max(p for prem, concl in d.instances
                       for c in tuple(prem) + (concl,) for p, _ in c)
        for binding in libdisc.extrapolation_probes(d.schema, max_pred):
            assert min(binding.values()) > max_pred


def test_scope_revision_narrows_rather_than_deletes(discovery):
    assert discovery.revisions
    narrowed = [r for r in discovery.revisions if r.outcome == "SCOPE_NARROWED"]
    assert narrowed, "the revision path must actually fire"
    for r in narrowed:
        assert not r.proposed_sound
        assert r.counterexample is not None
        assert r.revised_sound
        assert r.merged_variables and len(r.merged_variables) == 2


def test_the_discovered_composite_is_the_certified_reference(discovery):
    macros = [d.schema for d in discovery.pool if d.schema.step_count >= 2]
    assert len(macros) == 1
    assert (libdisc_discovery.semantic_key(macros[0])
            == libdisc_discovery.semantic_key(CHAIN2_SCHEMA))
    assert macros[0].schema_id == CHAIN2_SCHEMA.schema_id


def test_semantic_equivalence_is_decided_exactly_not_heuristically():
    assert (libdisc_discovery.semantic_key(CHAIN_SCHEMA)
            != libdisc_discovery.semantic_key(MERGE_SCHEMA))
    assert (libdisc_discovery.semantic_key(CHAIN2_SCHEMA)
            != libdisc_discovery.semantic_key(CHAIN_SCHEMA))
    relabelled = libdisc.canonical_schema(CHAIN_SCHEMA)
    assert (libdisc_discovery.semantic_key(relabelled)
            == libdisc_discovery.semantic_key(CHAIN_SCHEMA))


def test_one_step_schemas_are_admitted_but_never_applied(discovery):
    singles = [d for d in discovery.pool if d.schema.step_count == 1]
    assert singles, "the false-common-pattern control needs an admitted singleton"
    for task in ESSENTIAL_COMPOSITE_TASKS:
        res = solve(task.premises, task.query, [d.schema for d in singles],
                    check_answer=False)
        assert not res.macro_fired
        assert res.work.macro_match_attempts == 0


# --------------------------------------------------------------------------
# THE DECISIVE CONTRAST
# --------------------------------------------------------------------------


def test_the_arm_benefits_on_the_essential_composite_set(benefit):
    row = benefit[ARM]["essential_composite"]
    assert row["delta_vs_reset"] > 0
    assert row["tasks_helped"] > row["tasks_harmed"]


def test_the_tautological_control_shows_no_benefit(benefit, summary):
    """Without this the positive above means nothing."""
    row = benefit[ARM]["tautological_control"]
    assert row["delta_vs_reset"] <= 0, (
        "the control set must not benefit; if it does, the contrast does not "
        "identify the demand term")
    assert row["tasks_helped"] == 0
    assert summary[ARM]["tautological_control"]["macro_match_attempts"] > 0, (
        "the control rows must be MATCHED and paid for, exactly as the "
        "clause-revival negative reported 4,425 matching-work units")


def test_the_control_set_is_present_and_is_matched(certification):
    assert TAUTOLOGICAL_CONTROL_TASKS
    assert all(r["matched"] for r in certification.control_rows)
    assert certification.tautology_count >= 1
    assert certification.bypass_count >= 1


def test_the_same_schema_produced_both_outcomes(sweep_out):
    ess = {r["task_id"]: r for r in sweep_out["rows"]
           if r["arm"] == ARM and r["task_set"] == "essential_composite"}
    ctl = {r["task_id"]: r for r in sweep_out["rows"]
           if r["arm"] == ARM and r["task_set"] == "tautological_control"}
    fired_ess = {mid for r in ess.values() for mid in r["macro_ids"]}
    assert fired_ess, "the macro must fire where the opportunity exists"
    assert all(r["macro_ids"] == [] or set(r["macro_ids"]) <= fired_ess
               for r in ctl.values()), (
        "the control set must be exercised by the SAME schema, not another one")


def test_harmful_abstraction_is_reported_not_hidden(sweep_out, summary):
    ref = summary[REFERENCE]
    harmed = [
        r for r in sweep_out["rows"] if r["arm"] == ARM
        and r["work_total"] > ref[r["task_set"]]["per_task_work"][r["task_id"]]]
    assert harmed, (
        "an abstraction that never hurts anywhere would be suspicious at this "
        "scale; S5 must have something to report")
    assert any(r["task_set"] == "essential_composite" for r in harmed), (
        "harm inside the set where the opportunity exists is the honest case "
        "and must be visible")


# --------------------------------------------------------------------------
# parents: each one's specific behaviour
# --------------------------------------------------------------------------


def test_anti_unification_parent_finds_nothing_at_the_flat_level(views, summary):
    p = libdisc_parents.anti_unification_parent(views)
    assert p.library == ()
    assert p.funnel["flat_objects"] == len(views)
    for set_name in ("essential_composite", "tautological_control"):
        assert (summary[p.name][set_name]["work_total"]
                == summary[REFERENCE][set_name]["work_total"])


def test_stitch_parent_finds_the_arms_schema_and_more(views, discovery, summary):
    p = libdisc_parents.stitch_parent(views)
    arm_macros = {d.schema.schema_id for d in discovery.pool
                  if d.schema.step_count >= 2}
    stitch_macros = {s.schema_id for s in p.applicable}
    assert arm_macros <= stitch_macros, (
        "corpus MDL over trace subsequences must be given every chance to find "
        "the step-level structure; it does")
    assert len(stitch_macros) > len(arm_macros)
    assert p.funnel["kept_single_occurrence"] > 0, (
        "its admission criterion has no support gate, which is the faithful "
        "difference from the arm")
    assert (summary[p.name]["essential_composite"]["work_total"]
            > summary[ARM]["essential_composite"]["work_total"]), (
        "the extra macros pay no rent and cost matching work")


def test_dreamcoder_parent_refits_and_converges(views, discovery, summary):
    p = libdisc_parents.dreamcoder_parent(views)
    assert p.funnel["accepted"] > 0
    assert p.funnel["corpus_bits_end"] < p.funnel["corpus_bits_start"], (
        "the refit loop must actually shorten the corpus")
    assert p.funnel["rounds"] <= 6
    arm_macros = {d.schema.schema_id for d in discovery.pool
                  if d.schema.step_count >= 2}
    assert arm_macros <= {s.schema_id for s in p.applicable}
    assert (summary[p.name]["essential_composite"]["work_total"]
            > summary[ARM]["essential_composite"]["work_total"])


def test_symbolic_compact_parent_ties_on_schemas_and_differs_only_by_caching(
        views, discovery, sweep_out, summary):
    p = libdisc_parents.symbolic_compact_parent(views)
    assert ({s.schema_id for s in p.library}
            == {d.schema.schema_id for d in discovery.pool}), (
        "this parent runs the identical learner; a difference in schemas would "
        "mean it was not faithfully ported")
    assert p.relevance_index is False
    assert p.funnel["shares_mechanism_under_test"] is True
    arm = sweep_out["arms"][ARM]
    assert arm["relevance_index"] is True
    for set_name in ("essential_composite", "tautological_control"):
        a = summary[ARM][set_name]
        b = summary[p.name][set_name]
        assert a["macro_fired"] == b["macro_fired"], (
            "identical libraries must fire identically; only cost may differ")
        assert b["work_total"] >= a["work_total"]
        assert (b["work_total"] - a["work_total"]
                == b["macro_match_attempts"] - a["macro_match_attempts"]), (
            "the whole residual against this parent must be matching work, "
            "i.e. infrastructure, not knowledge")


def test_symbolic_incremental_memory_parent_never_hits_its_archive(
        views, sweep_out, summary):
    p = libdisc_parents.symbolic_incremental_memory_parent(views)
    assert len(p.archive) == len(views)
    rows = [r for r in sweep_out["rows"] if r["arm"] == p.name]
    assert rows
    assert all(not r["archive_hit"] for r in rows), (
        "fresh tasks are disjoint from the training draw by construction, so a "
        "hit would mean the disjointness certification is wrong")
    for set_name in ("essential_composite", "tautological_control"):
        assert (summary[p.name][set_name]["work_total"]
                > summary["symbolic_compact_parent"][set_name]["work_total"]), (
            "the archive is paid for on every row and never repays")


def test_no_library_baseline_and_reset_arm_are_identical_at_query_time(summary):
    for set_name in ("essential_composite", "tautological_control",
                     "registered_controls", "unsound_traps"):
        assert (summary["no_library_baseline"][set_name]["work_total"]
                == summary[REFERENCE][set_name]["work_total"])


def test_reset_arm_discovered_and_then_held_nothing(views):
    p = libdisc_parents.reset_arm(views)
    assert p.library == ()
    assert p.funnel["discovered_then_discarded"] > 0, (
        "the reset arm must have paid for discovery and thrown it away, or it "
        "is not the right reference for the causal chain")


def test_removing_the_schema_removes_the_advantage(summary):
    stripped = "libdisc_discovery_arm_schema_removed"
    for set_name in ("essential_composite", "tautological_control"):
        assert (summary[stripped][set_name]["work_total"]
                == summary[REFERENCE][set_name]["work_total"])
        assert summary[stripped][set_name]["macro_fired"] == 0


# --------------------------------------------------------------------------
# CL-T1: a REAL process boundary
# --------------------------------------------------------------------------


def test_custody_used_a_real_process_boundary(custody):
    assert custody["terminal"] == "CUSTODY_OK", custody
    assert custody["pid_before"] != custody["pid_after"], (
        "pid_before == pid_after is CUSTODY_VIOLATION; an in-process "
        "'simulated restart' is design evidence only and never confirmatory")
    assert custody["pid_before"] != custody["pid_orchestrator"]
    assert custody["pid_after"] != custody["pid_orchestrator"]
    assert custody["distinct_pids"] == 3
    assert custody["acquire_exit_status"] == 0
    assert custody["use_exit_status"] == 0


def test_custody_state_survived_the_boundary_unchanged(custody):
    assert custody["digests_agree"]
    assert custody["state_digest_before"] == custody["state_digest_after"]
    assert custody["state_bytes"] > 0
    assert custody["applicable_persisted"]


def test_custody_children_are_isolated_from_this_process(custody):
    assert custody["interpreter_flags"] == ["-I", "-S", "-B"]
    assert set(custody["child_environment"]) <= {"PATH", "LC_ALL"}
    assert "PYTHONPATH" not in custody["child_environment"]


def test_the_causal_chain_completes_after_the_restart(custody):
    rows = custody["rows_after_restart"]
    ess = [r for r in rows if r["task_set"] == "essential_composite"]
    assert ess
    assert all(r["correct"] for r in rows)
    fired = [r for r in ess if r["macro_fired"]]
    assert fired, "the persisted schema must fire on unseen tasks"
    for r in fired:
        assert r["trace_length"] > 0, (
            "presence in memory is not use; CL-R3 needs an execution trace")
        assert r["macro_ids"]


def test_removing_the_schema_after_the_restart_removes_the_advantage(custody):
    cb = libdisc_arms.custody_benefit(custody)
    assert cb["delta_by_set"]["essential_composite"] > 0
    assert cb["delta_by_set"]["tautological_control"] < 0
    assert (cb["with_schema"]["essential_composite"]["macro_fired"] > 0)
    assert (cb["with_schema_removed"]["essential_composite"]["macro_fired"] == 0)


def test_serialized_schemas_round_trip_exactly(discovery):
    for d in discovery.pool:
        assert schema_from_body(d.schema.body).schema_id == d.schema.schema_id


# --------------------------------------------------------------------------
# controls
# --------------------------------------------------------------------------


def test_false_common_pattern_is_admitted_and_never_demanded(discovery, sweep_out):
    singles = [d for d in discovery.pool if d.schema.step_count == 1]
    assert len(singles) >= 2
    assert all(d.admission.admissible for d in singles)
    fc = [r for r in sweep_out["rows"]
          if r["arm"] == ARM and r["task_id"] == "FC1"]
    assert fc and not fc[0]["macro_fired"], (
        "the composite the >=2 gate refused would have helped FC1; the refusal "
        "is the cost of not lowering the threshold and is reported as one")


def test_surface_similar_control_would_have_fired_a_sign_blind_matcher():
    total, refuted = 0, 0
    for task in ESSENTIAL_COMPOSITE_TASKS + CONTROL_TASKS:
        m, r = libdisc_discovery.polarity_blind_refutations(
            CHAIN_SCHEMA, task.premises)
        total += m
        refuted += r
    assert total > 0
    assert refuted > 0, (
        "if no polarity-blind match is ever refuted, refusing to generalise "
        "across polarity costs nothing and the control is inert")


def test_unsound_traps_are_really_not_entailed_and_nobody_solves_them(sweep_out):
    for task in UNSOUND_TRAP_TASKS:
        assert not entails(task.premises, task.query)
    rows = [r for r in sweep_out["rows"] if r["task_set"] == "unsound_traps"]
    assert rows
    assert all(not r["solved"] for r in rows)
    assert all(r["correct"] for r in rows)


# --------------------------------------------------------------------------
# terminal
# --------------------------------------------------------------------------


def test_terminal_is_a_pure_function_of_the_table(summary, benefit, sweep_out,
                                                  certification, custody):
    import run_libdisc

    terminal, reason = run_libdisc.terminal_for(
        summary, benefit, sweep_out["arms"], certification.as_dict(), custody)
    assert terminal in {
        "CUSTODY_VIOLATION", "GENERATOR_CERTIFICATION_FAILED",
        "NO_METHOD_ACQUIRED", "PARENT_SUFFICIENT", "NO_DEVELOPMENT_BENEFIT",
        "OPPORTUNITY_NOT_ISOLATED", "DISCOVERY_SEPARATES_FROM_OPPORTUNITY"}
    assert reason
    again = run_libdisc.terminal_for(
        summary, benefit, sweep_out["arms"], certification.as_dict(), custody)
    assert again == (terminal, reason)


def test_terminal_would_flip_if_the_control_set_also_benefited(
        summary, benefit, sweep_out, certification, custody):
    """The terminal must be sensitive to the control, not decorative."""
    import copy

    import run_libdisc

    faked = copy.deepcopy(benefit)
    faked[ARM]["tautological_control"]["delta_vs_reset"] = 1
    terminal, _ = run_libdisc.terminal_for(
        summary, faked, sweep_out["arms"], certification.as_dict(), custody)
    assert terminal == "OPPORTUNITY_NOT_ISOLATED"

    faked2 = copy.deepcopy(benefit)
    faked2[ARM]["essential_composite"]["delta_vs_reset"] = 0
    terminal2, _ = run_libdisc.terminal_for(
        summary, faked2, sweep_out["arms"], certification.as_dict(), custody)
    assert terminal2 == "NO_DEVELOPMENT_BENEFIT"


def test_plan_records_the_frozen_threshold_and_the_refusal_to_weaken():
    plan = libdisc.LIBDISC_PLAN
    assert plan["repeated_support_threshold"] == 2
    assert "not lowered" in plan["threshold_is_frozen"]
    assert plan["semantic_weakening"].startswith("NOT IMPLEMENTED")
    assert "PROTECTED_PROTOCOL_V3.md" in plan["leakage"]["adopted_from"]
