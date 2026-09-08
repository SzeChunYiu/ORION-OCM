from __future__ import annotations

import r0a_suffix_elision as R


def test_later_runtime_mutation_refutes_unrestricted_first_pass_elision(tmp_path):
    report = R.hostile_runtime_mutation_audit(tmp_path)
    assert report["baseline"]["calls"] == ["first", "second"]
    assert report["baseline"]["check_status"] == "CANNOT_CHECK"
    assert report["baseline"]["support_revoked"] is True
    assert report["first_pass_prefix"]["calls"] == ["first"]
    assert report["first_pass_prefix"]["check_status"] == "PASS"
    assert report["first_pass_prefix"]["support_revoked"] is False
    assert report["protected_divergence"] is True


def test_pure_tail_preserves_first_choice_but_not_literal_check_trace():
    report = R.pure_trace_audit()
    assert report["same_selected_first_pass"] is True
    assert report["full"]["status"] == report["prefix"]["status"] == "PASS"
    assert report["full"]["verification_calls"] == 3
    assert report["prefix"]["verification_calls"] == 1
    assert report["literal_check_trace_equal"] is False


def test_current_operator_contract_has_no_checker_purity_certificate():
    report = R.current_purity_contract_audit()
    assert report["runtime_has_checker_callable"] is True
    assert report["runtime_has_purity_metadata"] is False
    assert report["manifest_checker_required"] is True
    assert report["manifest_implementation_identity"] == "HOST_SUPPLIED_UNVERIFIED"
    assert report["manifest_has_purity_metadata"] is False


def test_frozen_r0_40_units_correct_to_20_check_stage_units():
    report = R.corrected_r0_accounting()
    assert report["frozen_r0"]["reported_tail_verification_calls"] == 40
    assert report["frozen_r0"]["reported_tail_composition_work"] == 33
    assert report["tail_candidates"] == 20
    assert report["compose_side_verification_already_spent"] == 20
    assert report["check_stage_verification_units_potentially_removed_by_break"] == 20
    assert report["composition_work_potentially_removed_by_check_stage_break"] == 0
    assert report["tail_candidates_are_passes_and_therefore_have_executable_checkers"] is True
    assert report["tail_checker_calls_authorized_for_omission_under_current_unrestricted_contract"] == 0


def test_report_terminal_rejects_current_contract_early_exit(tmp_path):
    report = R.build_report(tmp_path)
    assert all(report["controls"].values())
    assert report["terminal"] == "EARLY_EXIT_OUTPUT_ONLY_NOT_LIFECYCLE_EQUIVALENT"
    assert report["subterminal"] == "CHECKER_EFFECT_CERTIFICATE_REQUIRED_R0A"
    assert report["claim_boundary"]["production_early_exit_authorized"] is False
    assert report["claim_boundary"]["ml_authorized"] is False
