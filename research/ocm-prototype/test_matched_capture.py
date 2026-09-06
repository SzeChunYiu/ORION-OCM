"""A real crashed child must preserve planned denominators and fail admission."""
from pathlib import Path
import json
import sys
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import capture_g1_matched as C


def test_crashed_child_retains_missing_items(tmp_path, monkeypatch):
    model = tmp_path / "INVALID_MODEL_BYTES.udpipe"
    model.write_bytes(b"FAILURE_CONTROL_NOT_A_LANGUAGE_MODEL")
    training = tmp_path / "training.json"
    training.write_text(json.dumps({"model_sha256": C.digest(model), "role": "UNIT_FAILURE_CONTROL"}))
    original = C.subprocess.Popen
    code = ("import json,sys;from pathlib import Path; c=json.loads(Path(sys.argv[1]).read_text());"
            "Path(c['rows']).write_text(json.dumps({'arm':c['arm'],'id':c['items'][0]['id'],"
            "'result':{'status':'CANNOT_CHECK'}})+'\\n');sys.exit(7)")
    def crash(command, **kwargs):
        return original([sys.executable, "-c", code, command[-1]], **kwargs)
    monkeypatch.setattr(C.subprocess, "Popen", crash)
    result = C.run(HERE / "results/g1-matched-plan-v1", model, training, tmp_path / "result")
    assert result["status"] == "CANNOT_CHECK_INCOMPLETE_EXECUTION"
    assert result["chunks"][0]["exit_code"] == 7
    assert result["chunks"][0]["complete_cpu_custody"] is False
    assert len(result["written_ids_by_arm"]["native"]) == 1
    assert len(result["missing_ids_by_arm"]["native"]) == 104
    assert len(result["missing_ids_by_arm"]["ocm"]) == 105


def test_model_training_mismatch_refused_before_execution(tmp_path):
    model = tmp_path / "INVALID_MODEL_BYTES.udpipe"; model.write_bytes(b"mismatch")
    training = tmp_path / "training.json"; training.write_text('{"model_sha256":"wrong"}')
    with pytest.raises(ValueError, match="exact completed model"):
        C.run(HERE / "results/g1-matched-plan-v1", model, training, tmp_path / "result")
    assert not (tmp_path / "result").exists()
