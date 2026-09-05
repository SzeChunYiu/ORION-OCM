"""Cold rollback restores registered plain data, never executable host objects."""
from dataclasses import replace
import json

import pytest

from ocm.runtime.ocm_runtime import OCMRuntime, RuntimeRefusal
from ocm.selfmodel import govern as GV
from ocm.store.evidence import Channel
from test_assurance_completeness import proposal


def adopt(root):
    rt = OCMRuntime(root)
    ledger = GV.AdoptionLedger(rt)
    p = proposal()
    decision = GV.ExternalAdopter("host").decide(p, GV.Assurance(True, {}, ()))
    components = {"operator.x": {"artifact": "inc"}, "unrelated": {"artifact": "control"}}
    challenger, info = ledger.adopt(p, decision, {"op": "v1", "items": [1, 2]}, components,
                                   cache={"compiled": ["v1"]})
    return rt, ledger, p, components, challenger, info


def test_data_artifact_survives_fresh_session_and_exact_rollback(tmp_path):
    rt, _, p, components, _, info = adopt(tmp_path)
    control = rt.admit_evidence({"control": True}, Channel.OBSERVATION, "control")[1]
    restarted = GV.AdoptionLedger(OCMRuntime(tmp_path))
    assert restarted.adoption_history[p.fingerprint()]["rollback_available"]
    cache = {"compiled": ["v2"]}
    restored, table, exact = restarted.rollback(p.fingerprint(), cache=cache)
    assert restored == {"op": "v1", "items": [1, 2]} and table == components and exact
    assert cache == {"compiled": ["v1"]}
    again = GV.AdoptionLedger(OCMRuntime(tmp_path))
    assert again.runtime.state.evidence.liveness([info["stamped_evidence"]]).value == "DEAD"
    assert again.runtime.state.evidence.liveness([control]).value == "LIVE"
    before = again.runtime.ledger.path.read_bytes()
    # A crash after durable preparation but before return remains recoverable.
    assert again.rollback(p.fingerprint())[0] == restored
    assert again.runtime.ledger.path.read_bytes() == before
    assert not again.adoption_history[p.fingerprint()]["rollback_completed"]
    again.acknowledge_rollback_installation(p.fingerprint(), components=table, cache=cache)
    with pytest.raises(RuntimeRefusal, match="ROLLBACK_ALREADY_COMPLETED"):
        GV.AdoptionLedger(OCMRuntime(tmp_path)).rollback(p.fingerprint())


def test_revoking_successor_stamp_is_not_restoring_its_component_table(tmp_path):
    rt, ledger, p, _, challenger, info = adopt(tmp_path)
    q = replace(p, proposal_id="successor", incumbent_fingerprint=p.fingerprint())
    dec = GV.ExternalAdopter("host").decide(q, GV.Assurance(True, {}, ()))
    _, successor = ledger.adopt(q, dec, challenger, info["components"])
    rt.revoke([successor["stamped_evidence"]])
    with pytest.raises(RuntimeRefusal, match="ROLLBACK_OUT_OF_ORDER"):
        ledger.rollback(p.fingerprint())
    restarted = GV.AdoptionLedger(OCMRuntime(tmp_path))
    _, table, _ = restarted.rollback(q.fingerprint())
    with pytest.raises(RuntimeRefusal, match="ROLLBACK_OUT_OF_ORDER"):
        restarted.rollback(p.fingerprint())
    restarted.acknowledge_rollback_installation(q.fingerprint(), components=table)
    assert restarted.rollback(p.fingerprint())[2]


@pytest.mark.parametrize("damage", ["missing", "changed"])
def test_unavailable_or_modified_snapshot_refuses_before_revocation(tmp_path, damage):
    rt, _, p, _, _, info = adopt(tmp_path)
    binding = GV.AdoptionLedger(OCMRuntime(tmp_path)).adoption_history[p.fingerprint()]["rollback_data"]
    artifact = tmp_path / "rollback-data" / (binding["sha256"] + ".json")
    if damage == "missing":
        artifact.unlink()
    else:
        data = json.loads(artifact.read_text())
        data["previous_artifact"]["op"] = "tampered"
        artifact.write_text(json.dumps(data))
    restarted = GV.AdoptionLedger(OCMRuntime(tmp_path))
    before = restarted.runtime.ledger.path.read_bytes()
    with pytest.raises(RuntimeRefusal, match="CANNOT_CHECK_ROLLBACK"):
        restarted.rollback(p.fingerprint())
    assert restarted.runtime.ledger.path.read_bytes() == before
    assert restarted.runtime.state.evidence.liveness([info["stamped_evidence"]]).value == "LIVE"


def test_unsupported_host_object_is_never_deserialized(tmp_path):
    rt = OCMRuntime(tmp_path)
    ledger = GV.AdoptionLedger(rt)
    p = replace(proposal(), apply=lambda incumbent: incumbent)
    dec = GV.ExternalAdopter("host").decide(p, GV.Assurance(True, {}, ()))
    _, info = ledger.adopt(p, dec, object(), {"operator.x": {"artifact": "inc"}})
    restarted = GV.AdoptionLedger(OCMRuntime(tmp_path))
    record = restarted.adoption_history[p.fingerprint()]
    assert record["rollback_data"]["status"] == "HOST_ARTIFACT_UNAVAILABLE"
    assert not record["rollback_available"]
    with pytest.raises(RuntimeRefusal, match="CANNOT_CHECK_ROLLBACK_ARTIFACT_UNAVAILABLE"):
        restarted.rollback(p.fingerprint())
    assert restarted.runtime.state.evidence.liveness([info["stamped_evidence"]]).value == "LIVE"


def test_custom_cache_callback_is_refused_before_preparation(tmp_path):
    rt, ledger, p, _, _, info = adopt(tmp_path)

    class FailedCache(dict):
        def update(self, *_args, **_kwargs):
            raise ValueError("host update failed")

    cache = FailedCache({"compiled": ["v2"]})
    before = rt.ledger.path.read_bytes()
    with pytest.raises(RuntimeRefusal, match="CANNOT_CHECK_ROLLBACK_CACHE_TYPE"):
        ledger.rollback(p.fingerprint(), cache=cache)
    assert cache == {"compiled": ["v2"]} and rt.ledger.path.read_bytes() == before
    assert not ledger.adoption_history[p.fingerprint()]["rollback_prepared"]
    assert rt.state.evidence.liveness([info["stamped_evidence"]]).value == "LIVE"


def test_imported_incomplete_completion_does_not_discharge_restoration(tmp_path):
    rt, ledger, p, _, challenger, info = adopt(tmp_path)
    q = replace(p, proposal_id="successor", incumbent_fingerprint=p.fingerprint())
    dec = GV.ExternalAdopter("host").decide(q, GV.Assurance(True, {}, ()))
    ledger.adopt(q, dec, challenger, info["components"])
    rt.admit_evidence({"rolled_back": q.fingerprint()}, Channel.IMPORTED, "external_adopter_rollback")
    rt.admit_evidence({"rollback_prepared": q.fingerprint()}, Channel.IMPORTED, "external_adopter_rollback")
    rt.admit_evidence({"rollback_acknowledged": q.fingerprint()}, Channel.IMPORTED, "external_adopter_rollback_ack")
    assert not ledger.adoption_history[q.fingerprint()]["rollback_completed"]
    with pytest.raises(RuntimeRefusal, match="ROLLBACK_OUT_OF_ORDER"):
        ledger.rollback(p.fingerprint())


@pytest.mark.parametrize("wrong", ["components", "cache"])
def test_host_ack_requires_exact_prepared_state(tmp_path, wrong):
    rt, ledger, p, _, _, _ = adopt(tmp_path)
    cache = {}
    _, components, _ = ledger.rollback(p.fingerprint(), cache=cache)
    if wrong == "components":
        components["unrelated"] = {"artifact": "wrong"}
    else:
        cache["compiled"] = ["wrong"]
    before = rt.ledger.path.read_bytes()
    with pytest.raises(RuntimeRefusal, match="ROLLBACK_ACK_"):
        ledger.acknowledge_rollback_installation(p.fingerprint(), components=components, cache=cache)
    assert rt.ledger.path.read_bytes() == before
    assert not ledger.adoption_history[p.fingerprint()]["rollback_completed"]
