"""Exercise the real report boundary using archived phases; no lifetime machine runs."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from ocm.evaluation import m12_paired_eval as PE

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V5.json"
FROZEN = tuple(sorted((ROOT / "research/ocm-m12").glob("*V5*"))) + tuple(
    sorted((ROOT / "docs/provenance").glob("*V5*")))


def frozen_hashes():
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN if p.is_file()}


@pytest.fixture
def archived_phases(monkeypatch):
    archived = json.loads(RESULT.read_text())
    before = frozen_hashes()
    def recorded_lifetime(arm, stream, root, *, matched_cells=False):
        # Reused V5 phases test reporting in other modes, not their outcomes.
        assert isinstance(matched_cells, bool)
        k = stream["lifetime"]
        return {"arm": arm, "lifetime": k, "ordering": archived["deterministic"]["orderings"][k],
                "stream_sha256": stream["sha256"], "phases": copy.deepcopy(archived["phases"][arm][k]),
                "chain_continuous": True, "chain": archived["chains"][k] if arm == "ocm" else [("start", None)],
                "no_reset": True, "information": copy.deepcopy(archived["information"][arm][k]),
                "resources": copy.deepcopy(archived["resources"][arm][k])}
    monkeypatch.setattr(PE, "run_lifetime", recorded_lifetime)
    yield archived
    assert frozen_hashes() == before


@pytest.mark.parametrize("name", ["engineering.json", "PROTECTED_V5_NEW_NAME.json"])
def test_new_v5_output_cannot_promote_positive_historical_rule(tmp_path, archived_phases, capsys, name):
    output = tmp_path / name
    assert PE.main(["--v5", "--out", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["deterministic"]["decision"] == "CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION"
    assert result["deterministic"]["historical_rule_diagnostic"] == "OCM_LIFETIME_RESIDUAL_SUPPORTED"
    assert result["deterministic"]["tests"] == archived_phases["deterministic"]["tests"]
    assert result["study_status"] == "ENGINEERING_REGRESSION_ONLY__AFTER_OUTCOME_ACCESS"
    assert result["receipt"] == "M12_PAIRED_LIFETIMES_V5_ENGINEERING_REPLAY"
    assert result["current_scientific_promotion"] == "NOT_ESTABLISHED"
    assert result["protected_reevaluation"] == "NOT_RUN"
    assert "protected streams" not in result["authority"]
    printed = json.loads(capsys.readouterr().out)
    assert printed["decision"] == result["deterministic"]["decision"]
    assert printed["study_status"] == result["study_status"]


@pytest.mark.parametrize("flags,mode", [([], "V3"), (["--v4"], "V4"), (["--v5"], "V5")])
def test_every_new_mode_has_engineering_authority(tmp_path, archived_phases, flags, mode):
    output = tmp_path / "mode.json"
    assert PE.main([*flags, "--out", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["deterministic"]["decision"] == "CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION"
    assert "historical_rule_diagnostic" in result["deterministic"]
    assert result["current_scientific_promotion"] == "NOT_ESTABLISHED"
    assert result["protected_reevaluation"] == "NOT_RUN"
    assert result["study_status"] == "ENGINEERING_REGRESSION_ONLY__AFTER_OUTCOME_ACCESS"
    assert result["authority"] == (f"Engineering replay on exposed {mode} streams; historical-rule diagnostic only; "
                                   "comparator adequacy and scientific promotion are not established")


@pytest.mark.parametrize("symlink", [False, True])
def test_existing_or_symlink_output_refuses_before_execution(tmp_path, monkeypatch, symlink):
    target = tmp_path / "frozen.json"
    target.write_bytes(b"IMMUTABLE_CONTROL\n")
    output = tmp_path / "alias.json" if symlink else target
    if symlink:
        output.symlink_to(target)
    def forbidden(*args, **kwargs):
        raise AssertionError("output refusal must precede any lifetime execution")
    monkeypatch.setattr(PE, "run_lifetime", forbidden)
    with pytest.raises(SystemExit):
        PE.main(["--v5", "--out", str(output)])
    assert target.read_bytes() == b"IMMUTABLE_CONTROL\n"


def test_manifest_only_has_no_outcome_or_protected_authority(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("manifest-only must not execute a lifetime")
    monkeypatch.setattr(PE, "run_lifetime", forbidden)
    output = tmp_path / "manifest.json"
    assert PE.main(["--v5", "--manifest-only", "--out", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["sha256"] == json.loads(PE.V5["manifest"].read_text())["sha256"]
    assert "decision" not in result and "deterministic" not in result
    assert "study_status" not in result and "authority" not in result
