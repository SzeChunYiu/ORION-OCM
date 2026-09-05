"""Shared execution and real process-boundary lifecycle regressions."""
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def pilot():
    assert importlib.util.find_spec("vessel_pilot") is not None, "shared-loop pilot has not been implemented"
    from vessel_pilot import run_study
    return run_study


@pytest.fixture(scope="module")
def receipt(tmp_path_factory):
    return pilot()(tmp_path_factory.mktemp("vessel"))


def test_shared_loop_is_implemented():
    pilot()


def test_both_domains_use_full_catalogue_and_same_host_fixture(receipt):
    assert receipt["checks"]["shared_core_and_catalogue"]
    assert receipt["checks"]["actual_full_stage_traces"]
    assert receipt["checks"]["both_domains_checked_and_admitted"]


def test_acquired_language_reloads_and_revokes_without_disabling_math(receipt):
    assert receipt["checks"]["fresh_process_reuse"]
    assert receipt["checks"]["language_alternate_support"]
    assert receipt["checks"]["language_last_support_revoked"]
    assert receipt["checks"]["unrelated_arithmetic_retained"]
    assert receipt["checks"]["language_restored"]


def test_generator_revocation_preserves_primitive_mathematical_fallback(receipt):
    assert receipt["checks"]["generator_reused"]
    assert receipt["checks"]["generator_revoked_primitive_fallback"]
    assert receipt["checks"]["unrelated_language_retained"]
    assert receipt["checks"]["generator_restored"]


def test_rejected_proposals_cannot_be_admitted(receipt):
    assert receipt["checks"]["wrong_output_refused"]
    assert receipt["checks"]["missing_checker_refused"]
    assert receipt["checks"].get("wrong_scope_refused") is True
    assert receipt["checks"]["budget_exhaustion_refused"]
    assert receipt["checks"]["input_payload_cannot_select_checker"]


def test_costs_and_claim_scope_are_explicit(receipt):
    assert receipt["measurements"]["wall_seconds"] > 0
    assert receipt["measurements"]["cpu_seconds"] > 0
    assert receipt["measurements"]["persistent_bytes"] > 0
    assert receipt["unmeasured"]
    assert receipt["claim_scope"] == "trusted-host same-loop engineering gate"
    assert receipt["comparator"]["independently_executed"] is True
    assert receipt["comparator"]["shared_solver_invoked"] is False
    assert receipt["comparator"]["polynomial"]["enumerated_programs"] == 341
    assert all(receipt["checks"].values())


def test_study_refuses_nonempty_custody_directory(tmp_path):
    (tmp_path / "existing-custody.txt").write_text("keep")
    with pytest.raises(ValueError, match="empty"):
        pilot()(tmp_path)
    assert (tmp_path / "existing-custody.txt").read_text() == "keep"
