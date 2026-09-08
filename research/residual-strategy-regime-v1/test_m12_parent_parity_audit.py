from pathlib import Path

import pytest

from m12_parent_parity_audit import (
    EXPECTED_SOURCE_GIT_BLOB_SHA1,
    SOURCE,
    analyze_text,
    git_blob_sha1,
    run,
)


def test_current_m12_source_is_class_dispatched_and_not_architecture_causal():
    result = run()
    assert result["source"]["git_blob_sha1"] == EXPECTED_SOURCE_GIT_BLOB_SHA1
    assert result["causal_attribution"]["phase_D"]["status"] == "BLOCKED_BY_ARM_CLASS_DISPATCH"
    assert result["causal_attribution"]["phase_F"]["status"] == "BLOCKED_BY_ARM_CLASS_DISPATCH"
    assert result["causal_attribution"]["phase_G"]["status"] == "BLOCKED_BY_ARM_CLASS_DISPATCH"
    assert result["causal_attribution"]["phase_E"]["status"] == "PARTIALLY_EQUALIZED"
    assert result["claim_boundary"]["m12_engineering_regression_valid"] is True
    assert result["claim_boundary"]["m12_whole_system_ocm_residual_established"] is False
    assert result["claim_boundary"]["general_ocm_net_benefit_established"] is False
    assert result["terminal"] == "M12_ARCHITECTURE_CAUSAL_CLAIM_BLOCKED_PARENT_PARITY"


def test_source_custody_uses_git_blob_identity():
    raw = SOURCE.read_bytes()
    assert git_blob_sha1(raw) == EXPECTED_SOURCE_GIT_BLOB_SHA1


def test_mutating_causal_assignment_fails_closed():
    text = SOURCE.read_text(encoding="utf-8")
    mutant = text.replace('method = "backdoor" if is_ocm else "naive"', 'method = "backdoor"')
    assert mutant != text
    with pytest.raises(ValueError, match="source contract changed"):
        analyze_text(mutant)


def test_mutating_parent_repair_dispatch_fails_closed():
    text = SOURCE.read_text(encoding="utf-8")
    mutant = text.replace("if isinstance(arm, WholeSystemParent):", "if False:", 1)
    assert mutant != text
    with pytest.raises(ValueError, match="source contract changed"):
        analyze_text(mutant)
