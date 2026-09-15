"""Hostile tests for the registered repaired-pricing K4 campaign (items 22/23/35-c)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import gmi_k4_resource_native_v4 as rn

HERE = Path(__file__).resolve().parent
PKG = HERE / "gmi_k4_repaired_campaign_v1"
if str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))

import repaired_campaign_v1 as camp  # noqa: E402

PROTOCOL = json.loads((PKG / "PROTOCOL_FREEZE_V1.json").read_text())


def test_protocol_decision_refuses_silent_frozen_mutation():
    d = PROTOCOL["protocol_decision"]
    assert d["adopt_repaired_pricing_for_this_campaign"] is True
    assert d["mutate_frozen_v4_v7_model"] is False
    assert d["rewrite_frozen_cell_verdicts"] is False
    assert PROTOCOL["frozen_model_pins"]["untouched"] is True
    assert PROTOCOL["predicted_object"]["kind"] == "PVR3_RETENTION_RECOVERY_UNDER_REUSE"
    assert "original_22_family_property_vectors" == PROTOCOL["predicted_object"]["not_predicted"]


def test_frozen_model_pins_match_bytes_on_disk():
    pins = camp.assert_frozen_untouched()
    assert pins["gmi_k4_resource_native_v4.py"]["ok"] is True
    assert pins["gmi_k4_search_v4.py"]["ok"] is True
    # Overlay must not replace rn.lifecycle in place.
    assert callable(rn.lifecycle)
    src = (HERE / "gmi_k4_resource_native_v4.py").read_text()
    assert "LOOKUP_RATIO" not in src
    assert "substitution_factor" not in src


def test_repair_module_is_overlay_only_not_inplace_patch():
    repair_src = (HERE / "gmi_k4_substitution_repair_v1.py").read_text()
    assert "The frozen model is NOT modified" in repair_src or "frozen model is NOT modified" in repair_src
    assert "def lifecycle" in repair_src
    # Must import rn and wrap costs, not assign rn.lifecycle = ...
    assert "rn.lifecycle =" not in repair_src
    assert "gmi_k4_resource_native_v4.lifecycle =" not in repair_src


def test_campaign_earns_green_cells_under_repaired_pricing():
    # Slightly smaller pool keeps CI fast; invariants still forced by runner.
    receipt = camp.run_campaign(n_candidates=2500)
    assert receipt["frozen_verdicts_rewritten"] is False
    assert receipt["summary"]["invalid_instrument"] == 0
    assert receipt["summary"]["green"] > 0
    assert receipt["summary"]["red"] == 0
    # Both sides of the onset must be represented among greens.
    greens = set(receipt["summary"]["green_reuses"])
    assert any(r < camp.RETENTION_ONSET for r in greens)
    assert any(r >= camp.RETENTION_ONSET for r in greens)
    assert receipt["invariants"]["frozen_never_retains"] is True
    assert receipt["invariants"]["green_cells_earned"] is True
    assert receipt["invariants"]["full_coverage_by_256"] is True


def test_full_coverage_by_256_requires_the_exact_registered_cell():
    # Regression for Bugbot finding: saturation at 512 must not retroactively
    # satisfy a prediction that requires full coverage by reuse 256.
    late_only = [
        {"reuse": 128, "repaired": {"coverage": 0.75}},
        {"reuse": 256, "repaired": {"coverage": 0.98}},
        {"reuse": 512, "repaired": {"coverage": 1.0}},
        {"reuse": 4096, "repaired": {"coverage": 1.0}},
    ]
    assert camp.full_coverage_at_registered_reuse(late_only) is False

    on_time = [
        {"reuse": 128, "repaired": {"coverage": 0.75}},
        {"reuse": 256, "repaired": {"coverage": 0.999}},
        {"reuse": 512, "repaired": {"coverage": 1.0}},
    ]
    assert camp.full_coverage_at_registered_reuse(on_time) is True


def test_full_coverage_by_256_fails_closed_if_cell_missing_or_duplicated():
    missing = [
        {"reuse": 128, "repaired": {"coverage": 0.9}},
        {"reuse": 512, "repaired": {"coverage": 1.0}},
    ]
    duplicated = [
        {"reuse": 256, "repaired": {"coverage": 1.0}},
        {"reuse": 256, "repaired": {"coverage": 1.0}},
    ]
    assert camp.full_coverage_at_registered_reuse(missing) is False
    assert camp.full_coverage_at_registered_reuse(duplicated) is False


def test_frozen_control_arm_earns_no_retention_greens():
    cands = camp.sample_pool(n=2000)
    for r in camp.REUSE_SCHEDULE:
        wf, _ = camp.winner(cands, r, "frozen")
        assert camp.retains(wf) is False


def test_campaign_id_and_collision_path_are_registered():
    assert PROTOCOL["campaign_id"] == "GMI_K4_REPAIRED_PRICING_CAMPAIGN_V1"
    assert "gmi_k4_repaired_campaign_v1" in PROTOCOL["collision_avoidance"]["package_dir"]
    assert "gmi-k4-substitution-cell-audit-v1" in str(PROTOCOL["collision_avoidance"]["not_using"])


def test_protocol_sha_pins_are_hex():
    for key, val in PROTOCOL["frozen_model_pins"].items():
        if key.endswith("_sha256"):
            assert len(val) == 64
            int(val, 16)
    assert len(PROTOCOL["repaired_pricing"]["module_sha256"]) == 64
