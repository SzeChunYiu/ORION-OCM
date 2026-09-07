"""Real tiny Git worker with mocked aggregate boundary; production inputs are never used."""
import json
from pathlib import Path
import pytest
from materialize_test_support import prepared


def test_ten_tree_clean_continuation(tmp_path, monkeypatch):
    loaded, args, authority, calls = prepared(tmp_path, monkeypatch)
    value = loaded["materialize_run"].run(*args)
    assert value["terminal"] == "MATERIALIZED_READY", value.get("error")
    assert len(calls) == 1 and calls[0]["owned"] == [args[1], args[3]]
    assert len(value["worker"]["materials"]) == 10
    assert value["whole_deadline_monotonic"] == authority["start"]["whole_deadline_monotonic"]
    assert value["semantic_checks_reached"] == 0
    rows = json.loads((args[3] / "ROWS-AFTER-MATERIALIZATION.json").read_bytes())
    assert rows["keys"] == ["0", "1", "2", "3"] and rows["continuation_cursor"] == 4
    assert not list(args[3].rglob(".lake"))
    assert (args[3] / "sources/resource_setup.py").is_file()


@pytest.mark.parametrize("change,reason", [
    ("missing", "WORKER_RESULT"), ("extra", "WORKER_RESULT"), ("row", "MATERIAL_DENOMINATOR"),
    ("workspace", "WORKSPACE_BLOB"), ("source", "INPUT_DRIFT"),
    ("cleanup", "PROCESS_CUSTODY"), ("pid", "WORKER_PID"), ("request", "WORKER_REQUEST")])
def test_after_worker_fault_refuses(tmp_path, monkeypatch, change, reason):
    def corrupt(out, receipt, authority):
        path = out / "materials/RESULT.json"; value = json.loads(path.read_bytes())
        if change == "missing": value["materials"].pop()
        elif change == "extra": value["materials"].append(value["materials"][0])
        elif change == "row": value["materials"][0]["name"] = "replacement"
        elif change == "workspace": (out / "materials/corpus/workspace/plain").write_bytes(b"changed")
        elif change == "source":
            with (out / "sources/materialize_git.py").open("a") as stream: stream.write("\n# drift\n")
        elif change == "cleanup": receipt["cleanup"]["members_empty"] = False
        elif change == "pid": value["pid"] = True
        elif change == "request": value["request"]["sha256"] = "0" * 64
        path.write_text(json.dumps(value))
    loaded, args, _, calls = prepared(tmp_path, monkeypatch, corrupt)
    value = loaded["materialize_run"].run(*args)
    assert value["terminal"] == "CANNOT_CHECK", value
    assert reason in value["error"]["message"], value["error"]
    assert len(calls) == 1 and (args[3] / "materials/RESULT.json").is_file()


def test_partial_last_failure_retains_all_attempts(tmp_path, monkeypatch):
    loaded, args, authority, calls = prepared(tmp_path, monkeypatch)
    authority["materials"][-1]["commit"] = "f" * 40
    value = loaded["materialize_run"].run(*args)
    assert value["terminal"] == "CANNOT_CHECK" and len(calls) == 1
    assert len(value["worker"]["materials"]) == 10
    assert [r["result"]["terminal"] for r in value["worker"]["materials"]].count("MATERIALIZED") == 9
    assert (args[3] / "materials/dependency9/RESULT.json").is_file()


def test_input_drift_during_source_copy_never_dispatches(tmp_path, monkeypatch):
    loaded, args, authority, calls = prepared(tmp_path, monkeypatch)
    c = loaded["acquisition_contract"]; original = c.write
    def write(path, value):
        original(path, value)
        if path.name == "SOURCE-FREEZE.json":
            Path(authority["inputs"][0]["path"]).write_text("changed")
    monkeypatch.setattr(c, "write", write)
    value = loaded["materialize_run"].run(*args)
    assert value["terminal"] == "CANNOT_CHECK" and "INPUT_DRIFT" in value["error"]["message"]
    assert calls == []


def test_final_custody_expiry_cannot_publish_ready(tmp_path, monkeypatch):
    loaded, args, authority, calls = prepared(tmp_path, monkeypatch)
    phase = loaded["materialize_phase"]; original = phase.clock
    def clock(start, *a, **kw):
        if (args[3] / "MATERIAL-REVALIDATION.json").exists():
            raise TimeoutError("WHOLE_EPISODE_DEADLINE")
        return original(start, *a, **kw)
    monkeypatch.setattr(phase, "clock", clock)
    value = loaded["materialize_run"].run(*args)
    assert value["terminal"] == "CANNOT_CHECK" and len(calls) == 1
    assert value["error"]["message"] == "WHOLE_EPISODE_DEADLINE"


@pytest.mark.parametrize("fault,reason", [("stream", "MATERIAL_COMMAND_STREAMS"),
                                          ("request", "MATERIAL_COMMAND_REQUEST"),
                                          ("sequence", "MATERIAL_COMMAND_REQUEST")])
def test_consistently_rebound_command_metadata_still_refuses(tmp_path, monkeypatch, fault, reason):
    def corrupt(out, receipt, authority):
        from hashlib import sha256
        top = out / "materials/RESULT.json"; worker = json.loads(top.read_bytes())
        row = worker["materials"][0]; command = row["result"]["commands"][0]
        path = Path(command["record"])
        if fault == "stream": command["streams"].pop("stdin")
        elif fault == "sequence": command["argv"][-1] = "status"
        else:
            request = json.loads((path / "REQUEST.json").read_bytes()); request["argv"][-1] = "status"
            (path / "REQUEST.json").write_text(json.dumps(request))
        (path / "RESULT.json").write_text(json.dumps(command))
        material = out / "materials/corpus/RESULT.json"; material.write_text(json.dumps(row["result"]))
        raw = material.read_bytes()
        row["receipt"] = dict(path=str(material), sha256=sha256(raw).hexdigest(), bytes=len(raw))
        top.write_text(json.dumps(worker))
    loaded, args, _, _ = prepared(tmp_path, monkeypatch, corrupt)
    value = loaded["materialize_run"].run(*args)
    assert value["terminal"] == "CANNOT_CHECK" and reason in value["error"]["message"], value
