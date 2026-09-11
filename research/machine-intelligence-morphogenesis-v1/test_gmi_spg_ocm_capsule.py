import json
from pathlib import Path

from map_m2p1_behavioural_to_spg import build_capsule


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CAPSULE = HERE / "GMI_SPG_OCM_M2P1_EVIDENCE_V1.json"


def test_committed_capsule_exactly_matches_bound_source_mapping():
    committed = json.loads(CAPSULE.read_text(encoding="utf-8"))
    generated = build_capsule(REPO_ROOT)
    assert committed == generated


def test_capsule_does_not_claim_probability_from_rank_proxy():
    capsule = json.loads(CAPSULE.read_text(encoding="utf-8"))
    assert "not treated as normalized probability" in capsule["spg_mapping"]["information_proxy"]


def test_capsule_keeps_verification_separate_from_proposal():
    capsule = json.loads(CAPSULE.read_text(encoding="utf-8"))
    assert capsule["spg_mapping"]["verification_separate_from_proposal"] is True
