"""Self-change custody: exact predecessors and recoverable rollback evidence."""
from dataclasses import replace

import pytest

from ocm.kso.warrant import Liveness
from ocm.runtime.ocm_runtime import OCMRuntime, RuntimeRefusal
from ocm.selfmodel import govern as GV
from ocm.selfmodel import proposal as PR
from ocm.store.evidence import Channel
from ocm.store.ledger import StaleLedgerHead


def _setup(root):
    rt = OCMRuntime(root)
    prediction = PR.Prediction(("target",), (), {}, (), (), (), 0.0)
    p = PR.SelfChangeProposal("change", "1", (), "operator.x", "D2", "incumbent", PR.ChangeClass.C2_OPERATOR,
                              {"replace": "v2"}, lambda a: {**a, "op": "v2"}, prediction, (), (), "target", "restore", "self", "window", PR.Origin.HUMAN)
    decision = GV.ExternalAdopter("host").decide(p, GV.Assurance(True, {}, ()))
    components = {"operator.x": {"artifact": "incumbent", "nested": {"version": 1}}, "unrelated": {"artifact": "control"}}
    return rt, GV.AdoptionLedger(rt), p, decision, components


def test_adoption_refuses_decision_for_another_proposal_without_running_callback(tmp_path):
    rt, ledger, p, decision, components = _setup(tmp_path)
    calls = []
    p = replace(p, apply=lambda a: calls.append("applied") or a)
    decision = replace(decision, proposal_fingerprint="different")
    with pytest.raises(PermissionError, match="proposal"):
        ledger.adopt(p, decision, {"op": "v1"}, components)
    assert not calls and not ledger.decisions and not rt.events


@pytest.mark.parametrize("case", ["wrong", "missing"])
def test_adoption_requires_exact_target_predecessor(tmp_path, case):
    rt, ledger, p, decision, components = _setup(tmp_path)
    if case == "wrong":
        components["operator.x"]["artifact"] = "another-incumbent"
    else:
        del components["operator.x"]
    with pytest.raises(RuntimeRefusal, match="INCUMBENT_FINGERPRINT_MISMATCH"):
        ledger.adopt(p, decision, {"op": "v1"}, components)
    assert not rt.events and not ledger.adopted
    assert components["unrelated"] == {"artifact": "control"}


def test_direct_adoption_still_checks_protected_targets(tmp_path):
    rt, ledger, p, _, components = _setup(tmp_path)
    p = replace(p, change_class=PR.ChangeClass.C6_CONSTITUTION, target_component="constitution.gate")
    decision = GV.ExternalAdopter("host").decide(p, GV.Assurance(True, {}, ()))
    with pytest.raises(PermissionError, match="protected"):
        ledger.adopt(p, decision, {"op": "v1"}, components)
    assert not rt.events and not ledger.decisions


def test_rollback_snapshots_do_not_alias_caller_mutable_state(tmp_path):
    rt, ledger, p, decision, components = _setup(tmp_path)
    incumbent = {"op": "v1", "nested": {"value": 1}}
    _, info = ledger.adopt(p, decision, incumbent, components)
    incumbent["nested"]["value"] = 99
    components["operator.x"]["nested"]["version"] = 99
    restored, previous, exact = ledger.rollback(p.fingerprint())
    assert exact and restored["nested"]["value"] == 1
    assert previous["operator.x"]["nested"]["version"] == 1
    assert previous["unrelated"] == {"artifact": "control"}
    assert rt.state.evidence.liveness([info["stamped_evidence"]]) is Liveness.DEAD


def test_failed_rollback_preserves_artifact_for_retry(tmp_path):
    rt, ledger, p, decision, components = _setup(tmp_path)
    _, info = ledger.adopt(p, decision, {"op": "v1"}, components, cache={"compiled": "v1"})
    current = OCMRuntime(tmp_path)
    control = current.admit_evidence("unrelated", Channel.OBSERVATION, "control")[1]
    cache = {"compiled": "v2"}
    with pytest.raises(StaleLedgerHead):
        ledger.rollback(p.fingerprint(), cache=cache)
    assert p.fingerprint() in ledger.adopted and cache == {"compiled": "v2"}
    assert current.state.evidence.liveness([info["stamped_evidence"]]) is Liveness.LIVE
    rt.replay()
    restored, previous, exact = ledger.rollback(p.fingerprint(), cache=cache)
    assert exact and restored == {"op": "v1"} and previous == components and cache == {"compiled": "v1"}
    assert rt.state.evidence.liveness([control]) is Liveness.LIVE


def test_restart_retains_adoption_metadata_without_claiming_host_rollback_artifact(tmp_path):
    rt, ledger, p, decision, components = _setup(tmp_path)
    # Plain JSON snapshots now have a registered recovery path. Arbitrary host
    # objects still have no executable deserialization path after restart.
    p = replace(p, apply=lambda artifact: artifact)
    _, info = ledger.adopt(p, decision, object(), components)
    rt.persist()
    restarted = GV.AdoptionLedger(OCMRuntime(tmp_path))
    record = restarted.adoption_history[p.fingerprint()]
    assert record["incumbent"] == p.incumbent_fingerprint
    assert record["evidence_id"] == info["stamped_evidence"] and record["liveness"] == "LIVE"
    assert record["rollback_available"] is False
    before = restarted.runtime.ledger.path.read_bytes()
    with pytest.raises(RuntimeRefusal, match="CANNOT_CHECK_ROLLBACK_ARTIFACT_UNAVAILABLE"):
        restarted.rollback(p.fingerprint())
    assert restarted.runtime.ledger.path.read_bytes() == before
    assert restarted.runtime.state.evidence.liveness([info["stamped_evidence"]]) is Liveness.LIVE


def test_failed_challenger_construction_does_not_record_completed_adoption(tmp_path):
    rt, ledger, p, decision, components = _setup(tmp_path)

    def fail(_):
        raise ValueError("cannot construct challenger")

    p = replace(p, apply=fail)
    with pytest.raises(ValueError, match="cannot construct challenger"):
        ledger.adopt(p, decision, {"op": "v1"}, components)
    assert not rt.events and not ledger.decisions and not ledger.adopted


def test_same_proposal_cannot_readopt_onto_its_revoked_stamp(tmp_path):
    rt, ledger, p, decision, components = _setup(tmp_path)
    _, info = ledger.adopt(p, decision, {"op": "v1"}, components)
    _, restored, _ = ledger.rollback(p.fingerprint())
    ledger.acknowledge_rollback_installation(p.fingerprint(), components=restored)
    with pytest.raises(RuntimeRefusal, match="ADOPTION_ALREADY_RECORDED"):
        ledger.adopt(p, decision, {"op": "v1"}, components)
    assert rt.state.evidence.liveness([info["stamped_evidence"]]) is Liveness.DEAD
    assert not ledger.adopted


def test_rollback_requires_reverse_adoption_order_and_preserves_successor(tmp_path):
    rt, ledger, p, decision, components = _setup(tmp_path)
    first_artifact, first = ledger.adopt(p, decision, {"op": "v1"}, components)
    successor = replace(p, proposal_id="successor", incumbent_fingerprint=p.fingerprint())
    next_decision = GV.ExternalAdopter("host").decide(successor, GV.Assurance(True, {}, ()))
    _, second = ledger.adopt(successor, next_decision, first_artifact, first["components"])
    before = rt.ledger.path.read_bytes()
    with pytest.raises(RuntimeRefusal, match="ROLLBACK_OUT_OF_ORDER"):
        ledger.rollback(p.fingerprint())
    assert rt.ledger.path.read_bytes() == before
    assert rt.state.evidence.liveness([second["stamped_evidence"]]) is Liveness.LIVE
    assert len(ledger.adopted) == 2
    _, restored_first, ok = ledger.rollback(successor.fingerprint())
    assert ok and restored_first == first["components"]
    ledger.acknowledge_rollback_installation(successor.fingerprint(), components=restored_first)
    _, restored_original, ok = ledger.rollback(p.fingerprint())
    assert ok and restored_original == components
    assert restored_original["unrelated"] == {"artifact": "control"}


def test_cache_restoration_failure_is_staged_before_revocation(tmp_path, monkeypatch):
    rt, ledger, p, decision, components = _setup(tmp_path)
    _, info = ledger.adopt(p, decision, {"op": "v1"}, components, cache={"compiled": "v1"})
    cache = {"compiled": "v2"}
    snapshot = ledger.adopted[p.fingerprint()].cache_snapshot
    original_copy = GV.copy.deepcopy

    def fail_on_cache(value, *args, **kwargs):
        if value is snapshot:
            raise ValueError("cache restoration unavailable")
        return original_copy(value, *args, **kwargs)

    monkeypatch.setattr(GV.copy, "deepcopy", fail_on_cache)
    before = rt.ledger.path.read_bytes()
    with pytest.raises(ValueError, match="cache restoration unavailable"):
        ledger.rollback(p.fingerprint(), cache=cache)
    assert rt.ledger.path.read_bytes() == before and cache == {"compiled": "v2"}
    assert rt.state.evidence.liveness([info["stamped_evidence"]]) is Liveness.LIVE
    assert p.fingerprint() in ledger.adopted
