"""Prospective fixed-profile and capture controls, with no model inference."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_g1_stanza_donor import donor_fixture
import g1_stanza_profile as P
import g1_stanza_capture as B
import capture_g1_matched as C
from grade_g1_matched import resources

HERE = Path(__file__).resolve().parent


@pytest.fixture
def successor(donor_fixture, tmp_path, monkeypatch):
    model, profile = donor_fixture
    plan_dir = tmp_path/"plan"; plan_dir.mkdir()
    original = HERE/"results/g1-matched-plan-v1"
    for name in ("public-items.json", "plan.json"):
        (plan_dir/("predecessor-plan.json" if name=="plan.json" else name)).write_bytes((original/name).read_bytes())
    lineage = tmp_path/"lineage.json"; lineage.write_text('{"status":"UNIT_LINEAGE"}')
    monkeypatch.setattr(P, "LINEAGE_SHA", C.digest(lineage))
    profile = P.describe([])
    profile_path = tmp_path/"profile.json"; profile_path.write_bytes(P.encoded(profile))
    plan = json.loads((original/"plan.json").read_text())
    plan.update(registered_utc=datetime.now(timezone.utc).isoformat(),
        donor="stanza-recurrent", donor_profile_id=profile["id"],
        predecessor_plan_sha256=B.PREDECESSOR_SHA,
        model_role="IMPORTED_FIXED_RECURRENT_DONOR",
        source_identity=C.G.content_hash(C.G.identities("syntax:stanza-recurrent")),
        training_lineage_sha256=P.LINEAGE_SHA, required_model="Fixed imported recurrent Stanza")
    (plan_dir/"plan.json").write_text(json.dumps(plan))
    return plan_dir, plan, model, lineage, profile_path, profile


def test_successor_exact_predecessor_profile_and_lineage(successor):
    directory, plan, model, lineage, path, profile = successor
    actual, training, detail = B.bind(directory, plan, model, lineage, path)
    assert actual == profile and training["original_training_costs"] == "UNKNOWN"
    assert training["training_reproduced_here"] is False
    assert detail["model_bytes"] == sum(profile["model_sizes"].values())+profile["resources_bytes"]
    for change in ({"registered_utc":"2000-01-01T00:00:00+00:00"},
                   {"model_role":"TRAIN_ONLY"}, {"donor_profile_id":"wrong"},
                   {"outer_seconds_per_chunk":601}, {"required_model":"TRAIN-only UDPipe"}):
        with pytest.raises(ValueError): B.bind(directory, plan|change, model, lineage, path)
    lineage.write_text("{}")
    with pytest.raises(ValueError): B.bind(directory, plan, model, lineage, path)


def test_capture_fixed_worker_and_unknown_cpu_without_inference(successor, tmp_path, monkeypatch):
    directory, plan, model, lineage, profile_path, profile = successor
    commands = []
    class FakeProcess:
        pid = 999999; returncode = 0
        def __init__(self, command, stdout, stderr, **kwargs):
            commands.append(command)
            config = json.loads(Path(command[-1]).read_text())
            assert config["donor_profile"] == profile
            assert config["training_manifest"]["role"] == "IMPORTED_STANZA_TRAINING_LINEAGE"
            rows = Path(config["rows"]); rows.write_text("{}\n"*21)
            stdout.write(json.dumps({"source_files": C.G.identities("syntax:stanza-recurrent"),
                                    "durable_state_bytes":123}))
        def wait(self, timeout=None): return self.returncode
    monkeypatch.setattr(C.subprocess, "Popen", FakeProcess)
    output = tmp_path/"capture"
    record = C.run(directory, model, lineage, output, donor="stanza-recurrent", profile_path=profile_path)
    assert record["status"] == "EXECUTED_NOT_GRADED" and len(commands)==10
    assert all(Path(c[1]).name=="g1_stanza_worker.py" for c in commands)
    assert all(c["complete_cpu_custody"] is False for c in record["chunks"])
    assert record["model_bytes"] == sum(v["bytes"] for v in P.inventory(profile).values())
    assert record["capture_body_wall_s"] >= record["prelaunch_binding_wall_s"] >= 0
    for arm in ("native", "ocm"):
        resource = resources(record["chunks"], arm)
        assert resource["total_process_tree_cpu_s"] is None and resource["complete_cpu_custody"] is False
    with pytest.raises(ValueError, match="overwrite"):
        C.run(directory, model, lineage, output, donor="stanza-recurrent", profile_path=profile_path)
    with pytest.raises(ValueError, match="only fixed"):
        C.run(directory, model, lineage, tmp_path/"bad", donor="arbitrary-worker")
    (directory/"plan.json").write_text(json.dumps(plan | {"source_identity":"0"*64}))
    changed_output = tmp_path/"changed-source"
    with pytest.raises(ValueError, match="prospective source"):
        C.run(directory, model, lineage, changed_output, donor="stanza-recurrent", profile_path=profile_path)
    assert not changed_output.exists()


def test_legacy_resource_accessor_is_unchanged():
    legacy = [{"arm":"native", "wall_s":1, "reaped_process_tree_cpu_s":2,
               "complete_cpu_custody":True, "source_stable":True,
               "worker":{"durable_state_bytes":3}}]*5
    assert resources(legacy, "native") == {"observed_outer_wall_s":5,
        "observed_reaped_cpu_s":10, "complete_cpu_custody":True,
        "last_reported_state_bytes":3, "state_report_is_final":True}
