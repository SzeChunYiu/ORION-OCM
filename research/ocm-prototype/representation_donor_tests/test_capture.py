from pathlib import Path
import sys
import copy
import json
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_adapter import module


def test_actual_capture_is_create_only_sealed_and_independently_graded(tmp_path):
    C = module("representation_donor_capture")
    out = tmp_path / "capture"
    C.capture(out, scenarios=("base", "incoming", "withdraw_rule"))
    grade = C.grade_archive(out)
    assert grade["assigned_scenarios"] == grade["recorded_scenarios"] == 3
    assert grade["completed_scenarios"] == 2
    assert grade["assigned_arm_records"] == grade["recorded_arm_records"] == 9
    assert grade["functionally_equal_comparisons"] == 4
    assert grade["consumer_failed_comparisons"] == 2
    assert grade["terminal"] == "PARTIAL_PARITY__CANNOT_CHECK_CONSUMER_REVISION"
    with pytest.raises(FileExistsError):
        C.capture(out, scenarios=("base",))
    row = out / "records" / "base-ocm.json"
    text = row.read_text()
    row.write_text(text.replace('"result": 42', '"result": 999'))
    with pytest.raises(ValueError, match="CAPTURE_DRIFT"):
        C.grade_archive(out)
