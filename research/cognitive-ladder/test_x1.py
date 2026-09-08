"""Integrity tests for X1, the cross-domain transfer test.

X1's whole claim rests on the ablated arm being E6's arm minus one line, so the
first tests are about fidelity. The second group is about the comparison being
made where section 7 allows it, because at E6's registered budget the ablated arm
posts a lower number purely by failing, and that is the number a reader meets
first.
"""

from __future__ import annotations

import difflib
import inspect
import json
import pathlib

import pytest

import support_arms as SA
import unanimity_transfer as X
import run_x1 as R
from support import SUPPORT_PLAN

RECEIPT = pathlib.Path(__file__).parent / "results" / "X1_UNANIMITY_TRANSFER_V1.json"


# --- fidelity ---------------------------------------------------------------

def test_the_ablation_differs_from_e6_by_exactly_one_line():
    original, ablated = X.source_diff()
    diff = [l for l in difflib.unified_diff(original.splitlines(), ablated.splitlines(),
                                            lineterm="", n=0)
            if l.startswith(("+", "-")) and not l.startswith(("---", "+++"))]
    assert len(diff) == 2, diff
    assert diff[0].lstrip("-").strip() == "if determined(candidate):"
    assert diff[1].lstrip("+").strip() == "if USE_DETERMINED and determined(candidate):"


def test_the_ablation_is_compiled_in_e6s_own_namespace():
    src = inspect.getsource(X.build_ablated_enumerator)
    assert "dict(vars(SA))" in src, (
        "the ablated function must call E6's helpers, not copies of them")


def test_a_changed_e6_makes_the_transfer_test_refuse_to_run():
    """If E6's enumerator is rewritten, this comparison is stale and must say so."""
    src = inspect.getsource(X.source_diff)
    assert "!= 1" in src and "stale" in src


def test_the_ablated_arm_changes_nothing_but_the_enumerator():
    assert issubclass(X.AblatedAdaptiveArm, SA.AdaptiveArm)
    for attr in ("_methods", "_candidates", "_breaks", "_file"):
        assert getattr(X.AblatedAdaptiveArm, attr, None) is getattr(SA.AdaptiveArm, attr)
    overridden = set(X.AblatedAdaptiveArm.__dict__) - {"__doc__", "__module__"}
    assert overridden == {"arm_id", "role", "discovery", "_discover"}, overridden


def test_registering_the_ablation_leaves_no_trace():
    before = dict(SA.ARMS)
    R.curve(1)
    assert SA.ARMS == before, "the E6 registry must be restored after the sweep"


# --- the comparison is made where it is admissible --------------------------

def test_the_headline_is_taken_at_matched_capability():
    doc = json.loads(RECEIPT.read_text())
    m = doc["matched_capability"]
    for arm in (R.ARM, R.ABLATED):
        assert m[arm]["precision"] == 1.0 and m[arm]["recall"] == 1.0, arm
    assert m[R.ARM]["budget_per_method"] < m[R.ABLATED]["budget_per_method"], (
        "the point of the curve is that the two reach the same capability at different "
        "budgets")


def test_the_misleading_registered_budget_row_is_published():
    doc = json.loads(RECEIPT.read_text())
    block = doc["why_the_registered_budget_misleads"]
    rows = block["rows"]
    assert rows[R.ABLATED]["recall"] < 1.0
    assert rows[R.ABLATED]["discovery_work"] < rows[R.ARM]["discovery_work"], (
        "the whole warning is that the failing arm posts the lower number")
    assert rows[R.ABLATED]["budget_exhausted_methods"] > 0
    assert "simply failing" in block["note"]


def test_the_soundness_audit_of_e6s_pruning_is_reported():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["X1_families_identical_at_matched_capability"] is True
    v = doc["predictions"]["X1_verdict"]
    assert "E6's pruning is SOUND" in v
    assert "budget exhaustion rather than unsoundness" in v
    assert "the wrong place to look" in v


def test_the_refuted_prediction_is_reported_as_refuted():
    doc = json.loads(RECEIPT.read_text())
    assert doc["predictions"]["X4_ablation_spends_more_total_work"] is False
    v = doc["predictions"]["X4_verdict"]
    assert v.startswith("REFUTED")
    assert "The refutation is the finding" in v


# --- the two columns stay apart ---------------------------------------------

def test_both_columns_are_reported_and_move_in_opposite_directions():
    doc = json.loads(RECEIPT.read_text())
    m = doc["matched_capability"]
    assert m["intervention_ratio_ablated_over_arm"] > 1.0
    assert m["work_ratio_ablated_over_arm"] < 1.0, (
        "if both moved the same way there would be no trade to report")
    assert "never summed" in doc["two_column_rule"]


def test_the_terminal_names_the_governing_quantity_and_both_signs():
    doc = json.loads(RECEIPT.read_text())
    reason = doc["terminal_reason"]
    assert "MORE INTERVENTIONS" in reason and "MORE TOTAL WORK" in reason
    assert "OPPOSITE sign from DEV-5" in reason
    assert "reasoning is cheap relative to asking" in reason
    assert "the contract is domain-neutral and its SIGN is not" in reason


def test_an_inert_mechanism_would_have_refuted_the_transfer():
    src = inspect.getsource(R._terminal)
    assert "TRANSFER_REFUTED_THE_MECHANISM_IS_INERT_HERE" in src
    assert "S3 cross-domain claim is REFUTED" in src


# --- honesty about how far two domains gets you -----------------------------

def test_the_receipt_does_not_call_two_domains_domain_neutrality():
    doc = json.loads(RECEIPT.read_text())
    note = doc["what_this_does_not_establish"]
    assert "Two domains is not domain-neutrality" in note
    assert "independence of implementation" in note


def test_the_receipt_withdraws_nothing_from_e6():
    doc = json.loads(RECEIPT.read_text())
    assert "withdraws nothing from that receipt" in doc["authority"]
    assert "E6's own numbers are the unablated column here and they reproduce" \
        in doc["authority"]


def test_e6s_unablated_numbers_reproduce_here():
    """If they did not, this experiment would be measuring a different E6."""
    doc = json.loads(RECEIPT.read_text())
    registered = SUPPORT_PLAN["intervention_budget_per_method"]
    row = next(r for r in doc["budget_curve"]
               if r["arm"] == R.ARM and r["budget_per_method"] == registered)
    e6 = json.loads((RECEIPT.parent / "SUPPORT_E6_V1.json").read_text())
    one_x = next(r for r in e6["table"] if r["arm"] == R.ARM and r["scale"] == "1x")
    assert row["discovery_interventions"] == one_x["discovery_interventions"]
    assert row["discovery_work"] == one_x["discovery_work"]


def test_the_receipt_claims_no_novelty_for_lattice_pruning():
    doc = json.loads(RECEIPT.read_text())
    assert "NONE CLAIMED" in doc["novelty"]
    assert "as old as version spaces" in doc["novelty"]
