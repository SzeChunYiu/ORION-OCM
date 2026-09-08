"""Integrity tests for E11, the discharge of N8.

E11 removes a gift, so the first thing to check is that the gift is actually
gone: no arm but the declared ceiling may consult the true semantics table. The
second is that the comparison is a comparison -- an arm that reaches the accuracy
target on a minority of worlds must not post a better cases-to-target number than
an arm that reaches it on nearly all of them, which is what the unpaired mean
did and what the paired comparison exists to prevent.
"""

from __future__ import annotations

import inspect
import json
import pathlib

import pytest

import probesem as P
import probesem_arms as A
import run_probesem as R

RECEIPT = pathlib.Path(__file__).parent / "results" / "PROBESEM_E11_V1.json"
LEARNERS = ("semantics_learner", "mapping_parent", "naive_bayes_parent",
            "random_probe_parent", "fixed_order_parent")


# --- the gift is gone -------------------------------------------------------

@pytest.mark.parametrize("arm_id", LEARNERS)
def test_no_learner_reads_the_true_semantics(arm_id):
    src = inspect.getsource(A.ARMS[arm_id])
    assert "world.semantics" not in src, arm_id
    assert "sem.observe" not in src, arm_id
    assert "expected_outcome" not in src, arm_id


def test_only_the_declared_ceiling_is_handed_the_table():
    assert "world.semantics" in inspect.getsource(A.given_semantics_ceiling)
    assert A.ARM_ROLES["given_semantics_ceiling"] == "CEILING"
    assert sum(1 for r in A.ARM_ROLES.values() if r == "CEILING") == 1


def test_the_learner_observes_only_what_it_pays_for():
    src = inspect.getsource(A.semantics_learner)
    assert src.count("world.observe") == 1, (
        "every observation must go through the one charged call")
    assert "trace.probe_cost += cost_of" in src


def test_e11_contains_e2s_world_rather_than_replacing_it():
    from diagnosis import expected_outcome
    for probe in P.BASE_PROBES:
        for cause in P.CAUSES:
            assert (P.REGISTERED_WORLD.table[(probe.value, cause.value)]
                    == expected_outcome(cause, probe, True))
    assert P.REGISTERED_WORLD.identifiable([p.value for p in P.BASE_PROBES])


def test_drawn_worlds_are_identifiable_or_rejected():
    import random
    probes = [p.value for p in P.BASE_PROBES] + [P.EXTRA_PROBE]
    for seed in range(12):
        world = P.draw_world(random.Random(seed))
        assert world.semantics.identifiable(probes), seed


def test_the_scope_probe_carries_no_cause_information():
    import random
    world = P.draw_world(random.Random(3))
    sp = world.semantics.scope_probe
    values = {world.observe(sp, c) for c in P.CAUSES}
    assert len(values) == 1, "the scope probe answers a scope question, not a case question"


# --- the harness does not favour either representation ---------------------

def test_both_learners_get_the_same_exploration_rule():
    """mapping_parent delegates, so its rule lives in the shared implementation."""
    for fn in (A.semantics_learner, A.naive_bayes_parent, A._mapping_arm):
        assert "OPTIMISM" in inspect.getsource(fn), fn.__name__
    assert "_mapping_arm" in inspect.getsource(A.mapping_parent)


def test_the_optimism_bonus_is_what_makes_the_extension_a_real_test():
    """Without it the mapping parent never buys the sixth probe and 'survives'."""
    assert A.OPTIMISM > 0
    src = inspect.getsource(A._mapping_arm)
    assert "return OPTIMISM" in src, (
        "an instrument with no counts must score above zero or it is never tried")


def test_the_one_knob_only_the_machine_has_is_declared():
    assert A.UNKNOWN_CELL_BONUS > 0
    assert "UNKNOWN_CELL_BONUS" in inspect.getsource(A.semantics_learner)
    for arm_id in ("mapping_parent", "naive_bayes_parent"):
        assert "UNKNOWN_CELL_BONUS" not in inspect.getsource(A.ARMS[arm_id])


# --- the comparison is paired -----------------------------------------------

def test_the_paired_mean_fixes_the_sample():
    per_arm = {
        "a": [{"world": "w1", "cases_to_target": 10, "reached_target": True},
              {"world": "w2", "cases_to_target": 90, "reached_target": True}],
        "b": [{"world": "w1", "cases_to_target": 20, "reached_target": True},
              {"world": "w2", "cases_to_target": None, "reached_target": False}],
    }
    out = R.paired(per_arm, ("a", "b"))
    assert out["worlds_compared"] == 1
    assert out["mean_cases_to_target"] == {"a": 10, "b": 20}, (
        "b must not benefit from the world it failed to solve")


def test_the_receipt_puts_the_reach_count_before_the_mean():
    doc = json.loads(RECEIPT.read_text())
    block = doc["reach_rate_is_the_first_coordinate"]
    assert "fixed_order_parent" in block["note"]
    reach = block["worlds_reaching_target"]
    assert reach["semantics_learner"] > reach["fixed_order_parent"], (
        "the receipt's own example must hold in the receipt's own numbers")
    unpaired = doc["summary"]["fixed_order_parent"]["mean_cases_to_target"]
    paired_learner = doc["paired_comparison"]["mean_cases_to_target"]["semantics_learner"]
    assert unpaired is not None and unpaired < doc["summary"]["mapping_parent"]["mean_cases_to_target"], (
        "the whole point of the warning is that this misleading number exists")
    assert paired_learner is not None


# --- terminals --------------------------------------------------------------

def _summary(**kw):
    base = {a: {"accuracy": 0.5, "worlds_reaching_target": 5, "mean_cases_to_target": 100.0}
            for a in A.ARMS}
    for k, v in kw.items():
        base[k].update(v)
    return base


def _pair(**kw):
    means = {a: 100.0 for a in ("semantics_learner", "mapping_parent",
                                "naive_bayes_parent", "given_semantics_ceiling")}
    means.update(kw)
    return {"mean_cases_to_target": means, "worlds_compared": 5}


def test_parent_sufficient_is_reachable():
    t, reason = R._terminal(_summary(given_semantics_ceiling={"accuracy": 0.9}),
                            _pair(semantics_learner=120.0, mapping_parent=100.0))
    assert t == "PARENT_SUFFICIENT"
    assert "REFUTED rather than completed" in reason


def test_beating_the_ceiling_voids_rather_than_discovers():
    t, _ = R._terminal(_summary(semantics_learner={"accuracy": 0.99},
                                given_semantics_ceiling={"accuracy": 0.5}), _pair())
    assert t == "VOID_CEILING_IMPLEMENTED_WRONGLY"


def test_not_reaching_the_target_blocks_the_comparison():
    t, _ = R._terminal(_summary(mapping_parent={"worlds_reaching_target": 0}), _pair())
    assert t == "TARGET_NOT_REACHED"


def test_the_narrowing_terminal_is_reachable():
    t, reason = R._terminal(
        _summary(given_semantics_ceiling={"accuracy": 0.9}),
        _pair(semantics_learner=90.0, naive_bayes_parent=95.0, mapping_parent=130.0))
    assert t == "PER_PROBE_EVIDENCE_SEPARATES_FROM_PER_ROW_EVIDENCE"
    assert "not about semantics" in reason


# --- the receipt ------------------------------------------------------------

def test_the_receipt_discharges_n8_by_name():
    doc = json.loads(RECEIPT.read_text())
    assert "N8-DIAGNOSIS-RESIDUAL" in doc["discharges"]
    assert "PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED" in doc["discharges"]


def test_the_receipt_reports_r3_with_its_failed_clause_if_any():
    doc = json.loads(RECEIPT.read_text())
    verdict = doc["predictions"]["R3_extension_verdict"]
    assert verdict in ("HELD",) or verdict.startswith(("PARTIALLY HELD", "REFUTED"))
    if verdict != "HELD":
        assert "recorded as wrong" in verdict or "does not" in verdict


def test_the_receipt_states_what_it_does_not_establish():
    doc = json.loads(RECEIPT.read_text())
    for phrase in ("noise-free", "revealed on", "five then six"):
        assert phrase in doc["what_this_does_not_establish"], phrase
    assert "NONE CLAIMED" in doc["novelty"]


def test_the_receipt_carries_no_wall_clock():
    text = RECEIPT.read_text().lower()
    for banned in ("elapsed", "timestamp", "duration_ms", "wall"):
        assert banned not in text, banned


def test_the_receipt_carries_the_plan_it_was_run_under():
    doc = json.loads(RECEIPT.read_text())
    assert doc["commitment"]["commitment"] == P.COMMITMENT.commitment
    assert doc["plan"] == json.loads(json.dumps(P.PROBESEM_PLAN))


def test_selection_is_shown_not_to_be_free():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["R5_selection_is_not_free"] is True
    reach = doc["summary"]
    assert reach["random_probe_parent"]["worlds_reaching_target"] < \
        reach["semantics_learner"]["worlds_reaching_target"]
