"""Actual failed-consumer records must retain independent numeric mismatch information."""
from pathlib import Path
import sys
import copy
import json
import hashlib
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_adapter import module


def test_error_does_not_hide_observed_fine_vector_or_request_mismatch():
    D, G = module("representation_donor"), module("representation_donor_grade")
    p = D.prepare(D.fixture("alternative"))
    reference = D.evaluate(p, arm="full", revoked=(2,))
    actual = D.evaluate(p, arm="ocm", revoked=(2,))
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


def test_capture_arms_are_bound_and_partial_cli_is_distinct(tmp_path, monkeypatch):
    C = module("representation_donor_capture")
    output = tmp_path / "capture"
    C.capture(output, scenarios=("base", "withdraw_rule"))
    grade = C.grade_archive(output)
    assert grade["recorded_scenarios"] == 2 and grade["completed_scenarios"] == 1
    assert grade["completed_arm_records"] == 3 and grade["consumer_error_arm_records"] == 3
    monkeypatch.setattr(sys, "argv", ["capture", "--output", str(output), "--grade-only"])
    assert C.main() == 2
    row = output / "records/base-ocm.json"
    data = json.loads(row.read_text()); data["arm"] = "full"
    row.write_text(json.dumps(data))
    seal = output / "SHA256.json"
    inventory = json.loads(seal.read_text()); inventory["records/base-ocm.json"] = hashlib.sha256(row.read_bytes()).hexdigest()
    seal.write_text(json.dumps(inventory))
    with pytest.raises(ValueError, match="ARM_BINDING_MISMATCH"):
        C.grade_archive(output)
