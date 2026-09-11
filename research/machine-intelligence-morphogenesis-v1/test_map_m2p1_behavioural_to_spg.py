from pathlib import Path

import pytest

from map_m2p1_behavioural_to_spg import (
    EXPECTED_EARLIER,
    EXPECTED_EQUAL,
    EXPECTED_LATER,
    EXPECTED_TARGETS,
    SOURCE_JSON_GIT_BLOB,
    SOURCE_MD_GIT_BLOB,
    build_capsule,
    git_blob_sha,
)


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]


def test_actual_reviewed_m2p1_receipt_maps_to_k1_spg():
    capsule = build_capsule(REPO_ROOT)
    assert capsule["schema"] == "GMIRealSPGEvidenceCapsuleV1"
    assert capsule["source"]["machine_receipt_git_blob_sha1"] == SOURCE_JSON_GIT_BLOB
    assert capsule["source"]["narrative_receipt_git_blob_sha1"] == SOURCE_MD_GIT_BLOB
    assert capsule["aggregate"]["targets"] == EXPECTED_TARGETS
    assert capsule["aggregate"]["continued_rank_earlier"] == EXPECTED_EARLIER
    assert capsule["aggregate"]["continued_rank_equal"] == EXPECTED_EQUAL
    assert capsule["aggregate"]["continued_rank_later"] == EXPECTED_LATER
    assert capsule["aggregate"]["median_source_registered_bits_saved"] == 1.91
    assert capsule["aggregate"]["worlds_every_target_earlier"] == 18
    assert capsule["gmi_terminal"] == "REAL_OCM_SEMANTIC_PROPOSAL_GEOMETRY_SHIFT_SUPPORTED_AT_REGISTERED_SCOPE"


def test_mapping_is_pre_solution_and_fresh_target_bound():
    capsule = build_capsule(REPO_ROOT)
    guards = capsule["freshness_and_causality_guards"]
    assert guards["target_solution_absent_from_development_history"] is True
    assert guards["measurement_is_pre_solution_proposal_geometry"] is True
    assert guards["reset_rank_equals_recorded_baseline_index_every_target"] is True
    assert guards["leakage_fail_closed_by_runner"] == "LEAKAGE_ALARM"


def test_adapter_cannot_promote_source_beyond_k1_c2():
    capsule = build_capsule(REPO_ROOT)
    attr = capsule["developmental_attribution"]
    assert attr["candidate_capital_level"] == "K1"
    assert attr["claim_rung"] == "C2"
    assert attr["k2_status"] == "NOT_ESTABLISHED_BY_THIS_RECEIPT"
    assert attr["k3_status"] == "NOT_ESTABLISHED_BY_THIS_RECEIPT"
    ceiling = capsule["claim_ceiling"].lower()
    assert "not k2/k3" in ceiling
    assert "not a cross-paradigm gmi law" in ceiling


def test_current_receipt_arithmetic_retains_equal_rank_targets():
    # This explicitly prevents a stale summary from silently replacing the
    # current authoritative source counts.
    assert EXPECTED_EARLIER + EXPECTED_EQUAL + EXPECTED_LATER == EXPECTED_TARGETS
    assert EXPECTED_EQUAL == 3
    assert EXPECTED_LATER == 202


def test_git_blob_identity_function_matches_reviewed_sources():
    json_path = REPO_ROOT / "research/m2-traversal-capital-v1/m2p1/records/BEHAVIOURAL_RECEIPT.json"
    md_path = REPO_ROOT / "research/m2-traversal-capital-v1/m2p1/BEHAVIOURAL_RECEIPT.md"
    assert git_blob_sha(json_path.read_bytes()) == SOURCE_JSON_GIT_BLOB
    assert git_blob_sha(md_path.read_bytes()) == SOURCE_MD_GIT_BLOB


def test_tampered_copy_fails_blob_identity(tmp_path):
    source_json = REPO_ROOT / "research/m2-traversal-capital-v1/m2p1/records/BEHAVIOURAL_RECEIPT.json"
    source_md = REPO_ROOT / "research/m2-traversal-capital-v1/m2p1/BEHAVIOURAL_RECEIPT.md"
    root = tmp_path
    json_dst = root / "research/m2-traversal-capital-v1/m2p1/records/BEHAVIOURAL_RECEIPT.json"
    md_dst = root / "research/m2-traversal-capital-v1/m2p1/BEHAVIOURAL_RECEIPT.md"
    json_dst.parent.mkdir(parents=True)
    md_dst.parent.mkdir(parents=True, exist_ok=True)
    json_dst.write_bytes(source_json.read_bytes() + b"\n")
    md_dst.write_bytes(source_md.read_bytes())
    with pytest.raises(ValueError, match="source identity mismatch"):
        build_capsule(root)
