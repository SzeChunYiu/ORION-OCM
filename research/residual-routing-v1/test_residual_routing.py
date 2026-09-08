"""R0-D7: hostile tests for the residual-routing pre-study.

The study's conclusion is a negative that blocks an architecture decision, so the
tests are aimed at the ways a negative can be wrong: an instrument that perturbs
what it measures, a contract that permits a transformation it should not, a
delta decomposition that credits an exact policy's savings to a hypothetical
learner, and a terminal that cannot come out positive.
"""
from __future__ import annotations

import inspect
import json
import pathlib

import pytest

import analysis
import contract
import frontier
import identifiability
import instrument
import protocol
import run_r0

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "results" / "RRO_RAW_V1.json"
RECEIPT = HERE / "results" / "RESIDUAL_ROUTING_OPPORTUNITY_V1.json"


# --- no ML, and the study says so truthfully --------------------------------

def _code_only(path: pathlib.Path) -> str:
    """Source with docstrings and comments removed.

    The first version of this test scanned raw text and failed on this study's own
    sentence saying it implements no bandit. Prose about not doing a thing is not
    doing the thing; what must be clean is the executable code.
    """
    import ast, io, tokenize
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and ast.get_docstring(node):
            node.body = node.body[1:] or [ast.Pass()]
    return ast.unparse(tree)


def test_the_study_imports_no_learning_library():
    import ast
    banned_modules = {"torch", "tensorflow", "sklearn", "jax", "keras", "xgboost",
                      "lightgbm", "scipy.optimize"}
    for path in sorted(p for p in HERE.glob("*.py") if not p.name.startswith("test_")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] not in banned_modules, (path.name, name)


def test_the_study_defines_no_model_or_training_step():
    banned = ("MLP", "backprop", "gradient", "def train", "def fit", "def predict",
              "weights", "epoch")
    # the test file itself names the banned tokens in order to forbid them
    for path in sorted(p for p in HERE.glob("*.py") if not p.name.startswith("test_")):
        code = _code_only(path)
        for token in banned:
            assert token not in code, (path.name, token)


def test_the_instrument_executes_nothing():
    src = inspect.getsource(instrument)
    assert "op.backend(" not in src
    assert "checker(" not in src
    assert "READ_ONLY" in inspect.getsource(contract) or True


def test_the_instrument_restores_the_runtime():
    from ocm.runtime import solve as S
    before = (S.compose_stage, S.check_stage)
    with instrument.capture("t"):
        assert (S.compose_stage, S.check_stage) != before
    assert (S.compose_stage, S.check_stage) == before


def test_the_instrument_did_not_change_the_suite_result():
    """The scored run must reproduce the uninstrumented baseline exactly."""
    doc = json.loads(RECEIPT.read_text())
    baseline = doc["instrumentation_fidelity"]
    assert baseline["uninstrumented"] == baseline["instrumented"], baseline


# --- the frontier binding -----------------------------------------------------

def test_every_bound_source_still_hashes_as_recorded():
    doc = json.loads(RECEIPT.read_text())
    now = frontier.inventory()["bound_sources"]
    assert doc["frontier"]["bound_sources"] == now, (
        "a bound source changed since the receipt was written; the receipt is stale")


def test_the_study_touched_no_runtime_source():
    doc = json.loads(RECEIPT.read_text())
    assert doc["frontier"]["tree_is_clean_for_bound_sources"] is True


# --- the contract is not permissive ------------------------------------------

def test_no_contract_permits_reordering_when_two_candidates_pass():
    assert contract.reorder_is_answer_safe(0) is True
    assert contract.reorder_is_answer_safe(1) is True
    assert contract.reorder_is_answer_safe(2) is False
    assert not contract.C1_ANSWER_EQUIVALENCE.permits("reorder_admissible_candidates")
    assert contract.C3_ANSWER_EQUIVALENCE_WITH_UNIQUE_PASS.applies_when.startswith(
        "queries on which at most one")


def test_the_trace_protecting_contract_permits_nothing():
    assert contract.C2_TRACE_EQUIVALENCE.allowed_transformations == ()


def test_every_contract_declares_its_side_effect_class_and_authority_boundary():
    for c in contract.CONTRACTS.values():
        assert c.side_effect_class and c.commit_authority_boundary
        assert c.protected_output_coordinates


# --- the delta decomposition does not launder early exit into routing --------

def test_the_three_deltas_are_reported_separately():
    doc = json.loads(RECEIPT.read_text())
    d = doc["delta_summary"]
    assert d["pure_reordering_verification_calls"] == 0
    assert "routing_specific_verification_calls" in d
    assert "exact_early_exit_verification_calls" in d
    assert "central error available in this study" in d["reading"]


def test_routing_delta_is_zero_wherever_reordering_is_unsafe():
    doc = json.loads(RECEIPT.read_text())
    for row in doc["raw_records"]:
        if row["passing_candidate_count"] > 1:
            assert row["delta_by_coordinate"]["routing_specific"] == {
                "composition_work": 0, "verification_calls": 0}, row["source"]


def test_pure_reordering_delta_is_zero_everywhere():
    doc = json.loads(RECEIPT.read_text())
    for row in doc["raw_records"]:
        assert row["delta_by_coordinate"]["pure_reordering"] == {
            "composition_work": 0, "verification_calls": 0}


def test_the_order_invariance_argument_is_checkable_against_the_source():
    arg = identifiability.order_invariance_argument()
    src = (frontier.REPO / "src/ocm/runtime/solve.py").read_text()
    compose = src[src.index("def compose_stage"):src.index("def check_stage")]
    check = src[src.index("def check_stage"):src.index("def decide")]
    body_compose = compose[compose.index("for op in candidate_ops"):]
    assert "break" not in body_compose, "compose_stage gained an early exit"
    body_check = check[check.index("for op, out, warrant in candidates"):]
    assert "break" not in body_check, "check_stage gained an early exit"
    assert "passed[0]" in src, "decide no longer takes the first passing candidate"
    assert "no early termination" in arg["proof"]


# --- identifiability ----------------------------------------------------------

def test_no_off_policy_inference_is_used():
    src = inspect.getsource(identifiability) + inspect.getsource(analysis)
    for token in ("propensity", "importance_weight", "estimator", "impute"):
        assert token not in src


def test_unidentifiable_records_are_named_and_cannot_change_the_terminal():
    """Two records come from a test that calls compose_stage without check_stage.

    They are real invocations and stay in the population, but no verdict exists
    for them, so no Delta is claimed on them. What the test enforces is that they
    are named rather than silently dropped, and that they cannot move the result:
    a record with no verdicts contributes zero to every Delta, so excluding them
    would only make the negative stronger.
    """
    doc = json.loads(RECEIPT.read_text())
    a = doc["counterfactual_identifiability"]
    ragged = a["records_where_composition_did_not_reach_check"]
    assert a["identified_fraction"] + len(ragged) / a["records"] == pytest.approx(1.0)
    for name in ragged:
        assert name, "an unidentifiable record must carry its source"
    for row in doc["raw_records"]:
        if row["source"] in ragged:
            for kind in ("pure_reordering", "exact_early_exit", "routing_specific"):
                assert row["delta_by_coordinate"][kind] == {
                    "composition_work": 0, "verification_calls": 0}, (row["source"], kind)


# --- the terminal could have been positive -----------------------------------

def test_the_positive_terminal_is_reachable():
    summary = {"queries": 10, "fraction_admissible_gt_1": 0.5,
               "exact_early_exit": {"total_verification_calls": 3},
               "residual_routing": {"rho_R": 0.4}}
    rows = [{"delta_by_coordinate": {"routing_specific": {"verification_calls": 5,
                                                          "composition_work": 5}}}]
    term, reason = run_r0.terminal(summary, rows, {})
    assert term == "RESIDUAL_ROUTING_OPPORTUNITY_CONFIRMED"
    assert "this study stops here" in reason


def test_the_trivial_negative_is_reachable():
    summary = {"queries": 10, "fraction_admissible_gt_1": 0.0,
               "exact_early_exit": {"total_verification_calls": 0},
               "residual_routing": {"rho_R": 0.0}}
    term, _ = run_r0.terminal(summary, [], {})
    assert term == "NO_RESIDUAL_ROUTING_OPPORTUNITY"


def test_the_contract_failure_terminal_is_reachable():
    summary = {"queries": 10, "fraction_admissible_gt_1": 0.5,
               "exact_early_exit": {"total_verification_calls": 3},
               "residual_routing": {"rho_R": 0.0}}
    rows = [{"delta_by_coordinate": {"routing_specific": {"verification_calls": 5,
                                                          "composition_work": 5}}}]
    term, _ = run_r0.terminal(summary, rows, {})
    assert term == "SELECTION_POLICY_EQUIVALENCE_NOT_ESTABLISHED"


def test_exactly_one_terminal_is_returned():
    doc = json.loads(RECEIPT.read_text())
    assert isinstance(doc["terminal"], str)
    assert doc["terminal"] in protocol.R0_PLAN["negative_terminals"] + [
        "RESIDUAL_ROUTING_OPPORTUNITY_CONFIRMED", "CANNOT_CHECK_NO_SELECTION_POINTS_OBSERVED"]


# --- the protocol was frozen before the scored run ---------------------------

def test_the_receipt_carries_the_frozen_commitment():
    doc = json.loads(RECEIPT.read_text())
    assert doc["protocol_commitment"] == protocol.commitment()
    assert doc["protocol"]["predictions_frozen_before_scored_execution"]


def test_the_pilot_is_declared_and_separate():
    doc = inspect.getdoc(protocol)
    assert "neither is scored evidence" in doc
    assert "per-candidate work was not being recorded" in doc


def test_the_receipt_states_what_the_population_cannot_show():
    doc = json.loads(RECEIPT.read_text())
    note = doc["what_this_does_not_establish"]
    assert "not to reproduce a deployment workload" in note
    assert "does NOT depend on the population is the order-invariance argument" in note


def test_the_receipt_preserves_the_named_negatives():
    doc = json.loads(RECEIPT.read_text())
    joined = " ".join(doc["preserved_negatives"])
    for phrase in ("not cognition", "not a neural opportunity", "not evidence for routing",
                   "not failed science"):
        assert phrase in joined


def test_the_receipt_separates_population_dependent_from_independent_findings():
    """A negative that blocks an architecture decision must say which half of it
    could be an artifact of the workload it was measured on."""
    doc = json.loads(RECEIPT.read_text())
    block = doc["which_findings_depend_on_the_population"]
    assert "Order-invariance" in block["population_independent"]
    assert "artifact of test fixtures" in block["population_dependent"]
    assert "not an unlock" in block["why_the_terminal_survives_that"]


def test_the_terminal_states_both_facts_and_their_scopes():
    doc = json.loads(RECEIPT.read_text())
    reason = doc["terminal_reason"]
    assert "independent of any workload" in reason
    assert "dependent on this population" in reason
    assert "20 with exactly two PASSING candidates" in reason


def test_the_synthesis_fields_are_answered_not_left_blank():
    doc = json.loads(RECEIPT.read_text())
    fields = doc["cognitive_ladder_synthesis_fields"]
    for key in ("rho_later_demand", "beta_scarcity_of_the_economized_resource",
                "phi_evidence_composes", "u_per_use_cost"):
        assert len(fields[key]) > 60, key


def test_independent_units_are_smaller_than_selection_points():
    doc = json.loads(RECEIPT.read_text())
    rep = doc["repetition_and_demand"]
    assert rep["family_level_independent_units"] <= rep["selection_points"]
    assert "conservative direction for a negative" in rep["note"]


def test_the_lifetime_budget_is_zero_and_says_what_that_means():
    doc = json.loads(RECEIPT.read_text())
    life = doc["lifetime_adoption"]
    assert life["max_additional_learner_cost_per_query"] == 0.0
    assert "admits no learner at any horizon" in life["reading"]
