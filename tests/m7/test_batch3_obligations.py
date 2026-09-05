"""Runtime obligations from ORION-V2 theory batch 3 (C2/C4/C5/C7 and B1(ii)): promoted atoms are
derived from their bridge, CANNOT_CHECK absorbs along the solve pipeline, certified alternatives
are ⊕ and uncertified ones ⊗, loops are metered, the contradiction verdict policy is UNKNOWN."""
from __future__ import annotations

import pytest

from ocm.dialogue import workspace as WS
from ocm.kso import procedures as PR
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language import meaning as M
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel


def prop(a, v, p):
    return M.MeaningGraph((M.MNode("x1", "entity", a), M.MNode("e", "event", v), M.MNode("x2", "entity", p)), (M.MEdge("ROLE:agent", ("e",), ("x1",)), M.MEdge("ROLE:patient", ("e",), ("x2",)), M.MEdge("TENSE", ("e",), ("e",), "past")), root="e")


def test_promoted_atom_is_derived_from_its_bridge_and_dies_with_it(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    ws = WS.DialogueWorkspace(rt, "c")
    c = ws.commit("alice", prop("paris", "in", "france"))
    bridge = rt.admit_evidence({"atlas": "paris in france"}, Channel.IMPORTED, "atlas", scope=Scope.universal())[1]
    r = ws.propose_promote(c.commitment_id, Scope.universal(), bridge_evidence=[bridge], bridge_authority=Authority.of(world_truth=1, speaker=1))
    assert r["promoted"]
    rec = rt.state.evidence.records[r["evidence_id"]]
    assert not rec.is_assumption and rec.warrant.evidence == {bridge, c.evidence_id}
    assert rt.state.evidence.liveness([r["evidence_id"]]) is Liveness.LIVE
    rt.revoke([bridge])
    assert rt.state.evidence.liveness([r["evidence_id"]]) is Liveness.DEAD     # B1(ii): retraction of the bridge reopens the promotion
    # replay reproduces the derived record (the event carries derived_from/authority)
    rt.persist()
    rt2 = OCMRuntime(tmp_path / "rt")
    assert not rt2.state.evidence.records[r["evidence_id"]].is_assumption
    assert rt2.state.evidence.liveness([r["evidence_id"]]) is Liveness.DEAD
    # an unknown bridge id is refused, never silently admitted as an assumption
    with pytest.raises(Exception):
        rt.admit_evidence({"x": 1}, Channel.IMPORTED, "t", derived_from=WarrantProfile.of({"ev:ghost"}))


def test_cannot_check_absorbs_along_the_pipeline():
    trace = SV.SolveTrace("t")
    trace.add(SV.StageResult(SV.Stage.NAVIGATION, SV.Status.PASS, "ok"))
    trace.add(SV.StageResult(SV.Stage.EXECUTION, SV.Status.CANNOT_CHECK, "ENABLING_UNKNOWN_FOR_SOME_EDGES"))
    task = SV.Task("t", parts=(), targets=()) if "parts" in SV.Task.__dataclass_fields__ else SV.Task("t")
    dec, out = SV.decide(trace, {}, [], task)
    assert dec.status is SV.Status.CANNOT_CHECK and out.decision is SV.Decision.CANNOT_CHECK and dec.reason.endswith("EXECUTION")


def test_certified_alternatives_join_uncertified_meet_and_loops_are_metered():
    from ocm.kso.warrant import live
    a = PR.Prim("a", lambda x: x + 1, (frozenset({"e1"}),))
    b = PR.Prim("b", lambda x: x + 1, (frozenset({"e2"}),))
    cert = PR.Alt(a, b, certified=True)
    unc = PR.Alt(a, b, certified=False)
    assert live(PR.static_warrant(cert), {"e1"})            # either derivation suffices
    assert not live(PR.static_warrant(unc), {"e1"})         # conjunctive without a certificate
    r = PR.run(cert, 1)
    assert r.output == 2 and r.fired == ("a",) and r.trace_warrant == (frozenset({"e1"}),)
    with pytest.raises(ValueError):
        PR.Loop(a, PR.Test("g", lambda x: True), bound=3, charge=0)
    lp = PR.Loop(a, PR.Test("g", lambda x: x < 3), bound=10, charge=1)
    assert PR.run(lp, 0).output == 3


def test_contradiction_verdict_policy(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    ws = WS.DialogueWorkspace(rt, "c")
    p = prop("robot", "open", "door")
    assert ws.verdict(p) == "NO_RECORD"
    ws.commit("alice", p)
    assert ws.verdict(p) == "ASSERTED_BY_SPEAKERS"
    for i in range(3):
        ws.commit(f"u{i}", p)
    b = ws.commit("bob", p, negated=True)
    assert ws.verdict(p) == "UNKNOWN"                                    # majority never resolves
    ws.retract(b.commitment_id)
    assert ws.verdict(p) == "ASSERTED_BY_SPEAKERS"                       # resolution by retraction only
