"""Historical errors remain negative controls; repaired live captures must complete."""
from pathlib import Path
import sys
import copy
import json
import hashlib
import shutil
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_adapter import module

HISTORICAL = Path(__file__).resolve().parents[1] / "results/representation-donor-absorption-20260906/raw/functional-v1"
HISTORICAL_SEAL = "a8ed46941d8764d93aefa3899f31e9c9c0f868ecdc7b482e76c37edc611d3273"


def historical_archive():
    """Verify the immutable original receipt, without invoking its old actor."""
    seal = HISTORICAL / "SHA256.json"
    assert hashlib.sha256(seal.read_bytes()).hexdigest() == HISTORICAL_SEAL
    for name, expected in json.loads(seal.read_text()).items():
        assert hashlib.sha256((HISTORICAL / name).read_bytes()).hexdigest() == expected
    return HISTORICAL


def test_error_does_not_hide_observed_fine_vector_or_request_mismatch():
    G = module("representation_donor_grade")
    old = historical_archive()
    reference = json.loads((old / "records/withdraw_rule-full.json").read_text())
    actual = json.loads((old / "records/withdraw_rule-ocm.json").read_text())
    assert actual["consumer"]["error"] == reference["consumer"]["error"] == "math domain error"
    assert G.compare(reference, actual)["terminal"] == "CANNOT_CHECK_CONSUMER_FAILURE"
    for kind in ("vectors", "request"):
        wrong = copy.deepcopy(actual)
        if kind == "vectors":
            atom = next(iter(wrong["vectors"][0]["values"]))
            wrong["vectors"][0]["values"][atom] = "999/1"
        else:
            wrong["request"]["task"]["task_id"] = "wrong-task"
        grade = G.compare(reference, wrong)
        assert grade["terminal"] == "FUNCTIONAL_MISMATCH"
        assert grade["consumer_failed"] is True


def test_repaired_capture_completes_and_binds_arms(tmp_path, monkeypatch):
    C = module("representation_donor_capture")
    output = tmp_path / "capture"
    C.capture(output, scenarios=("base", "withdraw_rule"))
    grade = C.grade_archive(output)
    assert grade["recorded_scenarios"] == grade["completed_scenarios"] == 2
    assert grade["completed_arm_records"] == 6 and grade["consumer_error_arm_records"] == 0
    monkeypatch.setattr(sys, "argv", ["capture", "--output", str(output), "--grade-only"])
    assert C.main() == 0
    row = output / "records/base-ocm.json"
    data = json.loads(row.read_text()); data["arm"] = "full"
    row.write_text(json.dumps(data))
    seal = output / "SHA256.json"
    inventory = json.loads(seal.read_text()); inventory["records/base-ocm.json"] = hashlib.sha256(row.read_bytes()).hexdigest()
    seal.write_text(json.dumps(inventory))
    with pytest.raises(ValueError, match="ARM_BINDING_MISMATCH"):
        C.grade_archive(output)


def test_immutable_historical_partial_capture_keeps_distinct_cli_status(tmp_path, monkeypatch):
    C = module("representation_donor_capture")
    output = tmp_path / "historical"
    shutil.copytree(historical_archive(), output)
    grade = C.grade_archive(output)
    assert grade["recorded_scenarios"] == 19 and grade["completed_scenarios"] == 16
    assert grade["completed_arm_records"] == 48 and grade["consumer_error_arm_records"] == 9
    assert grade["consumer_failed_comparisons"] == 6
    assert grade["terminal"] == "PARTIAL_PARITY__CANNOT_CHECK_CONSUMER_REVISION"
    monkeypatch.setattr(sys, "argv", ["capture", "--output", str(output), "--grade-only"])
    assert C.main() == 2
