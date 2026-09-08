from __future__ import annotations

import r0a_checker_provenance_audit as A


def test_current_manifest_aliases_effect_distinct_checker_implementations():
    collision = A.manifest_collision()
    assert collision["same_operator_fingerprint"] is True
    assert collision["same_serialized_operator_metadata"] is True
    assert collision["same_persistent_runtime_manifest"] is True
    assert collision["checker_results_equal"] is True
    assert collision["effects_after_pure"] == collision["effects_before"] == []
    assert collision["effects_after_effectful"] == ["host_effect"]
    assert collision["effect_semantics_differ"] is True
    assert collision["manifest"]["checker_required"] is True
    assert collision["manifest"]["implementation_identity"] == "HOST_SUPPLIED_UNVERIFIED"


def test_pure_checker_certificate_is_a_content_bound_control():
    control = A.pure_certificate_control()
    assert control["same_schema"] is True
    assert control["same_language"] is True
    assert control["different_ast_identity"] is True
    assert control["effects_empty_by_construction"] is True
    assert len(control["pass_binding"]["checker_ast_sha256"]) == 64
    assert control["pass_binding"]["checker_claimed_effects"] == []


def test_frozen_r0_tail_cannot_be_retroactively_declared_pure():
    report = A.build_report()
    custody = report["source_custody"]
    assert custody["frozen_instrument_blob"] == "2af3f979932bbe0156970f619bbfe28e217008fe"
    assert custody["frozen_derived_receipt_blob"] == "2de217fda11b00708ad143ebe64b5a1ff6fef90d"
    assert custody["frozen_tail_check_callbacks_max"] == 20
    assert custody["instrument_candidate_record_fields"] == [
        "operator_id", "input_atoms", "verdict", "composition_work", "verification_calls"
    ]
    assert report["findings"]["retrospective_tail_checker_purity_identifiable"] is False
    assert report["claim_boundary"]["frozen_twenty_callbacks_declared_pure"] is False


def test_prospective_binding_is_required_and_ml_stays_blocked():
    report = A.build_report()
    assert report["terminal"] == "CHECKER_PROVENANCE_INSUFFICIENT_R0A"
    assert all(report["controls"].values())
    assert report["required_prospective_manifest_binding"] == [
        "checker_certificate_schema",
        "checker_language_version",
        "checker_ast_sha256",
        "checker_claimed_effects",
    ]
    assert report["findings"]["production_manifest_binds_pure_checker_certificate"] is False
    assert report["claim_boundary"]["production_early_exit_authorized"] is False
    assert report["claim_boundary"]["migration_must_bind_certificate_before_execution"] is True
    assert report["claim_boundary"]["replay_must_reject_checker_binding_drift"] is True
    assert report["claim_boundary"]["ml_authorized"] is False
