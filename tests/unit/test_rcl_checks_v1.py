"""Unit tests for the RCL V1 exact checks (repair of three VACUOUS_CONTRAST controls).

The V0 modules stay untouched and their tests keep running; these tests bind the
V1 checker's own denominators and require every planted failure to fire.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANE = ROOT / "research" / "orion-machine" / "revocation_complete_learning"
MODULE_PATH = LANE / "rcl_checks_v1.py"


def load_v1():
    lane_text = str(LANE)
    if lane_text not in sys.path:
        sys.path.insert(0, lane_text)
    spec = importlib.util.spec_from_file_location("rcl_checks_v1", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V1 = load_v1()


def test_v0_files_are_not_modified_by_v1() -> None:
    # V1 imports V0's model; it must not shadow or rewrite the V0 checkers.
    import rcl_checks_core  # noqa: F401  (V0, hash-bound in the review packets)
    import rcl_checks_finish  # noqa: F401

    assert (LANE / "rcl_checks_core.py").exists()
    assert "bits[:stored] + bits[stored:]" in (LANE / "rcl_checks_core.py").read_text()
    assert "bits[:stored] + bits[stored:]" not in MODULE_PATH.read_text().split('"""', 2)[2]


def test_frontier_v1_has_real_withheld_summary_and_collisions() -> None:
    result = V1.verify_storage_query_frontier_v1(5)
    assert result["reconstruction_checks"] == 28863
    assert result["distinct_candidate_completeness_checks"] == 28863
    assert result["splits_on_or_above_frontier"] == 22
    assert result["splits_below_frontier"] == 64
    assert result["collision_pairs_exhibited"] == 64
    n5 = next(c for c in result["cases"] if c["n"] == 5)
    assert n5["variable_warrant_bits"] == 9 and n5["profile_count"] == 512
    below = [p for p in n5["frontier_points"] if not p["theorem_predicts_exact"]]
    assert below and all(p["collision"] is not None and not p["observed_exact"] for p in below)
    exact = [p for p in n5["frontier_points"] if p["theorem_predicts_exact"]]
    assert len(exact) == 10 and all(p["observed_exact"] and p["sum"] == 9 for p in exact)


def test_frontier_v1_exactness_is_computed_not_literal() -> None:
    src = MODULE_PATH.read_text()
    body = src.split("def verify_storage_query_frontier_v1", 1)[1].split("\ndef ", 1)[0]
    assert '"exact": True' not in body
    assert "observed_exact" in body


def test_mutations_are_applied_and_detected() -> None:
    result = V1.verify_mutation_controls_v1()
    assert result["mutations_planted"] == 6 and result["mutations_detected"] == 6
    cases = result["cases"]
    for name in (
        "M1_live_ignores_revocation",
        "M2_constant_signature",
        "M3_negated_coordinate_oracle",
        "M4_reconstructor_drops_last_coordinate",
        "M5_complement_updater",
        "M6_reconstructor_collapses_fillings",
    ):
        assert cases[name]["applied"] is True
    assert cases["M1_live_ignores_revocation"]["injectivity_survives"] is False
    assert cases["M2_constant_signature"]["injectivity_survives"] is False
    assert cases["M3_negated_coordinate_oracle"]["detected"] is True
    assert cases["M4_reconstructor_drops_last_coordinate"]["detected"] is True
    assert cases["M5_complement_updater"]["detected"] is True
    assert cases["M6_reconstructor_collapses_fillings"]["detected"] is True
    assert "candidates" in cases["M6_reconstructor_collapses_fillings"]["failure"]
    assert cases["M0_unmutated"] == {"injectivity": True, "frontier": True}


def test_below_frontier_arm_is_falsifiable() -> None:
    """The below-frontier arm must be able to fail: a reconstructor that collapses
    every filling makes the distinct-candidate count wrong, and candidate_profiles
    deduplicates so the count is a real quantity."""
    honest = V1.candidate_profiles({0: True}, 4)
    assert len(honest) == 2 ** (len(V1.fixed_certificate_profiles(4)[1]) - 1)
    assert len(set(honest)) == len(honest)

    def collapse(bits, n):
        return V1.profile_from_bits(tuple(False for _ in bits), n)

    assert len(V1.candidate_profiles({0: True}, 4, collapse)) == 1
    try:
        V1.verify_storage_query_frontier_v1(4, reconstruct=collapse)
    except AssertionError as exc:
        assert "candidates" in str(exc)
    else:
        raise AssertionError("collapsing reconstructor passed the frontier check")


def test_no_alarm_uses_three_distinct_updaters_and_a_planted_incomplete_one() -> None:
    result = V1.verify_no_alarm_v1(4)
    assert result["complete_updaters"] == 3
    assert result["agreement"] == result["denominator"] == 2688
    assert result["planted_incomplete_updater_disagreements"] == 485
    assert result["rcl_2b_over_retraction_fires"] is True


def test_rsd_is_fibrewise_vc_dimension() -> None:
    result = V1.verify_rsd_is_fibrewise_vc(4)
    assert result["profiles_on_fibre"] == 32 and result["admitted_revocations"] == 16
    assert result["recorded_rsd"] == 5 and result["vc_dimension_of_liveness_class"] == 5
    assert result["equal"] is True and result["planted_single_function_vc"] == 0


def test_self_test_exit_codes() -> None:
    result = V1.run_v1_self_test()
    assert result["terminal"] == "PASS" and result["exit_code"] == 0
    assert result["supersedes"]["withdrawn_figure"] == "storage_query_reconstruction_checks: 5329"
    assert result["supersedes"]["v0_files_modified"] is False
    assert result["authority"]["novelty_established"] is False
    assert V1.main(["--self-test"]) == 0


def test_cannot_check_is_distinct_from_fail() -> None:
    try:
        V1.verify_no_alarm_v1(5)
    except V1.CannotCheck:
        pass
    else:
        raise AssertionError("n above the exhaustive cap must be CANNOT_CHECK")
    try:
        V1.verify_storage_query_frontier_v1(0)
    except V1.CannotCheck:
        pass
    else:
        raise AssertionError("max_n=0 must be CANNOT_CHECK")
