"""M4 §1, §2, §5, §10, §14: workspace persistence and restart, three layers, supersession reopens
exactly, promotion needs a bridge, planted hostiles differ."""
from __future__ import annotations

import pytest

from ocm.dialogue import workspace as WS
from ocm.dialogue import reference as R
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness
from ocm.language import meaning as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel


def prop(agent, verb, patient):
    return M.MeaningGraph((M.MNode("x1", "entity", agent), M.MNode("e", "event", verb), M.MNode("x2", "entity", patient)), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")


def flight(day):
    return M.MeaningGraph((M.MNode("f", "entity", "flight"), M.MNode("d", "value", day)), (M.MEdge("ROLE:time", ("f",), ("d",)),), root="f")


def test_three_layers_and_restart_survives_with_ledger_consistency(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    ws = WS.DialogueWorkspace(rt, "c1")
    ws.record_turn("user", "the robot opened the door", "ASSERT", "INTERPRETED")
    c = ws.commit("user", prop("robot", "open", "door"), utterance="the robot opened the door")
    rec = rt.state.evidence.records[c.evidence_id]
    assert rec.channel is Channel.OBSERVATION and rec.source == "user" and rec.scope.contexts == frozenset({"c1"})
    assert ws.machine_liveness([c.evidence_id]) is Liveness.LIVE          # the *said* record is live …
    assert ws.propose_promote(c.commitment_id, Scope.universal())["promoted"] is False   # … but it is not machine knowledge
    h = ws.state_hash()
    rt.persist()
    # restart: new runtime over the same root, workspace reloaded, hashes equal, evidence ids valid
    rt2 = OCMRuntime(tmp_path / "rt")
    ws2 = WS.DialogueWorkspace.load(rt2, "c1")
    assert ws2.state_hash() == h and ws2.active_commitments()[0].evidence_id == c.evidence_id
    # a workspace referencing evidence absent from the ledger is CANNOT_CHECK, never a partial state
    ws2.commitments["cmt:c1:999"] = WS.Commitment("cmt:c1:999", 1, "user", "d", False, "ev:ghost", {})
    ws2.save()
    with pytest.raises(WS.WorkspaceRefusal) as ex:
        WS.DialogueWorkspace.load(OCMRuntime(tmp_path / "rt"), "c1")
    assert ex.value.code == "CANNOT_CHECK"


def test_correction_supersedes_and_reopens_exactly_while_history_is_kept(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    ws = WS.DialogueWorkspace(rt, "c2")
    ws.record_turn("user", "my flight is tuesday", "ASSERT", "INTERPRETED")
    t1 = ws.commit("user", flight("tuesday"), utterance="my flight is tuesday")
    ws.record_turn("user", "the robot opened the door", "ASSERT", "INTERPRETED")
    other = ws.commit("user", prop("robot", "open", "door"))
    # a derived dialogue conclusion depending on the Tuesday commitment
    plan_ev = rt.admit_evidence({"plan": "book taxi tuesday"}, Channel.INTERACTION, "planner", scope=Scope.of("c2"))[1]
    ws.record_turn("user", "correction, it is wednesday", "CORRECT", "INTERPRETED")
    t3 = ws.commit("user", flight("wednesday"), supersedes=t1.commitment_id, utterance="correction, it is wednesday")
    assert ws.commitments[t1.commitment_id].status is WS.CommitmentStatus.SUPERSEDED and ws.commitments[t1.commitment_id].superseded_by == t3.commitment_id
    assert t3.supersedes == t1.commitment_id and len(ws.turns) == 3            # history intact
    assert t1.evidence_id in rt.state.revoked and other.evidence_id not in rt.state.revoked   # unrelated entity untouched
    assert rt.state.evidence.records[t3.evidence_id].superseded_by is None and rt.state.evidence.records[t1.evidence_id].superseded_by == t3.evidence_id
    assert [c.commitment_id for c in ws.active_commitments()] == [other.commitment_id, t3.commitment_id]
    # the planted hostile edits history instead
    before = ws.commitments[other.commitment_id].digest
    WS.mutant_correction_overwrites_history(ws, other.commitment_id, prop("cat", "push", "box"))
    assert ws.commitments[other.commitment_id].digest != before and ws.commitments[other.commitment_id].status is WS.CommitmentStatus.ACTIVE


def test_ten_speakers_do_not_promote_and_promotion_needs_a_live_bridge(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    ws = WS.DialogueWorkspace(rt, "c3")
    p = prop("paris", "in", "germany")
    ids = [ws.commit(f"u{i}", p).commitment_id for i in range(10)]
    assert len(ws.active_commitments()) == 10 and ws.machine_commitments == []
    r = ws.propose_promote(ids[0], Scope.universal())
    assert r["promoted"] is False and "NO_BRIDGE" in r["reason"]
    bridge = rt.admit_evidence({"atlas": "paris in france"}, Channel.IMPORTED, "atlas", scope=Scope.universal())[1]
    r2 = ws.propose_promote(ids[0], Scope.universal(), bridge_evidence=[bridge], bridge_authority=Authority.of(world_truth=1, speaker=1))
    assert r2["promoted"] is True and r2["authority"].rank("world_truth") == 0     # meet with speaker record: never above the said layer
    rt.revoke([bridge])
    r3 = ws.propose_promote(ids[1], Scope.universal(), bridge_evidence=[bridge], bridge_authority=Authority.of(world_truth=1))
    assert r3["promoted"] is False and "DEAD" in r3["reason"]
    assert len(WS.mutant_promote_all_assertions(ws)) == 10                        # the hostile the rule forbids


def test_reference_resolution_is_four_valued_and_never_nearest_noun(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    ws = WS.DialogueWorkspace(rt, "c4")
    ws.record_turn("user", "the robot opened the door", "ASSERT", "INTERPRETED")
    robot = ws.introduce("entity", "the robot", features={"animate": "no"})
    door = ws.introduce("entity", "the door", features={"animate": "no"})
    ws.record_turn("user", "mary repaired it", "ASSERT", "AMBIGUOUS")
    mary = ws.introduce("entity", None, alias="Mary", features={"animate": "yes", "gender": "f"})
    it = R.resolve(ws, R.Mention("it"))
    assert it.status is R.ReferenceStatus.AMBIGUOUS and set(it.candidates) == {robot.entity_id, door.entity_id}
    assert R.resolve(ws, R.Mention("it"), matters=True).status is R.ReferenceStatus.NEEDS_CLARIFICATION
    assert R.resolve(ws, R.Mention("she")).candidates == (mary.entity_id,)
    assert R.resolve(ws, R.Mention("the door")).status is R.ReferenceStatus.RESOLVED
    assert R.resolve(ws, R.Mention("the second one")).candidates == (door.entity_id,)
    assert R.resolve(ws, R.Mention("the cat")).status is R.ReferenceStatus.UNKNOWN_REFERENT
    assert R.resolve(ws, R.Mention("Mary")).status is R.ReferenceStatus.RESOLVED
    # hostiles: nearest-noun picks Mary for "it" (animate mismatch); recent-turn-only forgets the robot/door
    assert R.mutant_nearest_noun(ws, R.Mention("it")) == mary.entity_id
    assert robot.entity_id not in R.mutant_most_recent_turn_only(ws, R.Mention("it"))
    # reference after a 12-turn gap still resolves (no hard clipping)
    for i in range(12):
        ws.record_turn("user", f"filler {i}", "ACKNOWLEDGE", "INTERPRETED")
    assert R.resolve(ws, R.Mention("the robot")).candidates == (robot.entity_id,)


def test_topics_and_preferences_are_conversation_scoped(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    ws = WS.DialogueWorkspace(rt, "c5")
    ws.push_topic("flights"); ws.push_topic("hotel"); ws.push_topic("flights")
    assert ws.topics == ["hotel", "flights"] and ws.current_topic == "flights"
    ws.set_preference("style", "brief")
    ws2 = WS.DialogueWorkspace(rt, "c6")
    assert ws2.preferences == {}                                              # no global leak
