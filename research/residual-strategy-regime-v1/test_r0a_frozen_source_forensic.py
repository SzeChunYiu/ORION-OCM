from __future__ import annotations

import r0a_frozen_source_forensic as F


def test_frozen_source_blobs_and_checker_factories_are_exact():
    report = F.build_report()
    assert report["frozen_commit"] == "47d706ab42d8528060356c7d4a267e1454ce9e7a"
    assert report["controls"]["all_source_blobs_match_frozen_commit"] is True
    assert report["controls"]["all_registered_factories_have_only_expected_trivial_pass_checkers"] is True
    assert report["sources"]["tests/m2/test_navigation_serving_runtime.py"]["git_blob_sha1"] == "55224956133d7b3c2a5c1078d06998e4ed0bd3a2"
    assert report["sources"]["tests/m2/test_runtime_extraction_index.py"]["git_blob_sha1"] == "90397bb6fc68ab20fda182b0b9ab9fb3b38b6867"
    assert report["sources"]["tests/m2/test_solve_operator_index.py"]["git_blob_sha1"] == "dd354658b67f2307f1c9c3743eb8705d0c51de53"


def test_forensic_family_counts_cover_exactly_the_corrected_twenty():
    report = F.build_report()
    opportunities = report["forensic_opportunities"]
    assert opportunities["navigation_serving_runtime"] == 7
    assert opportunities["runtime_extraction_index"] == 11
    assert opportunities["solve_operator_index"] == 2
    assert opportunities["total"] == opportunities["corrected_r0_check_tail"] == 20
    assert opportunities["source_level_trivial_pass_coverage_fraction"] == 1.0
    assert report["controls"]["forensic_opportunity_total_matches_corrected_r0_tail"] is True


def test_forensic_purity_does_not_upgrade_runtime_authority():
    report = F.build_report()
    assert report["terminal"] == "FROZEN_R0_TEST_TAILS_FORENSICALLY_PURE_NOT_RUNTIME_CERTIFIED"
    assert report["findings"]["all_frozen_test_tail_opportunities_reconstruct_to_trivial_PASS_checker_factories"] is True
    assert report["findings"]["recorded_runtime_manifest_bound_those_checker_bodies"] is False
    assert report["findings"]["literal_check_trace_preserved_by_elision"] is False
    assert report["findings"]["production_checker_population_represented_by_this_test_donor"] is False
    assert any("No ML" in item for item in report["claim_boundary"])
