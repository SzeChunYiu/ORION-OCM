"""M11.2: the runtime obligations reported by theory batch 6 (F1, F4, F5, consequence 5 and 7)."""
from __future__ import annotations

from pathlib import Path

import pytest

from ocm.chat.session import ChatSession
from ocm.selfmodel import jump_evidence as J
from ocm.kso.warrant import WarrantProfile as WP
from ocm.lifetime import machine as MC
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.selfmodel import diagnose as DG
from ocm.selfmodel import govern as GV
from ocm.selfmodel import model as SM
from ocm.selfmodel import proposal as PR


def test_F4_dead_warrant_on_path_caps_the_layer_and_emits_local_candidates():
    f = SM.FailureRecord("f", "t", "env", "o", "e", ("ev:trace",), (SM.Layer.D2_OPERATOR, SM.Layer.D3_REPRESENTATION), (SM.AblationEvidence("new representation", SM.Layer.D3_REPRESENTATION, True, "a"),), {}, "DEAD", "high", 1, "s")
    d, cands = DG.diagnose_with_path(f, dead_on_path=["ev:demo"], registry={SM.Layer.D1_ROUTING: ("alt_skill",)})
    assert d.minimum_sufficient == "D2" and "F4:dead-warrant-on-path" in d.evidence and not d.architecture_alarm
    assert {(c.kind, c.target) for c in cands} == {("reinstate", "ev:demo"), ("reroute", "alt_skill")}
    assert DG.mutant_escalate_over_dead_path(f, ["ev:demo"]) == "D3"          # the hostile escalates over a dead path
    d2, _ = DG.diagnose_with_path(f, dead_on_path=[])
    assert d2.minimum_sufficient == "D3"                                           # no dead warrant: the ablation evidence stands


def test_consequence7_jump_assessment_is_derived_from_evidence():
    class _T:  # minimal trigger/proposal doubles
        is_admissible = True

    class _P:
        trigger = _T()
        is_formally_complete = True
        level = 3
    p = _P()
    assert J.assess_jump_from_evidence(p, minimum_sufficient_local=True, certificate_valid=True, donor_product_ties=False) is J.JumpAssessment.NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT
    assert J.assess_jump_from_evidence(p, minimum_sufficient_local=None, certificate_valid=True, donor_product_ties=False) is J.JumpAssessment.INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED
    assert J.assess_jump_from_evidence(p, minimum_sufficient_local=False, certificate_valid=False, donor_product_ties=False) is J.JumpAssessment.INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED
    assert J.assess_jump_from_evidence(p, minimum_sufficient_local=False, certificate_valid=True, donor_product_ties=False) is J.JumpAssessment.CANDIDATE_FOR_PROTECTED_EVALUATION

    class _Q(_P):
        def __init__(self, level):
            self.level = level
    with pytest.raises(ValueError):
        J.minimum_sufficient_proposal((_Q(1), _Q(2)), 3)                          # nothing at or above the evidence level
    assert J.minimum_sufficient_proposal((_Q(1), _Q(3), _Q(4)), 3).level == 3


def test_F5_identity_is_the_ledger_chain_not_the_path(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    rt.admit_evidence({"x": 1}, "observation", "s")
    before = MC.identity_chain(rt)
    rt.admit_evidence({"x": 2}, "observation", "s")
    assert MC.chain_continuous(before, rt)                                         # extended chain: same machine
    rt2 = OCMRuntime(tmp_path / "rt2")
    rt2.admit_evidence({"y": 1}, "observation", "s")
    fake = {**before, "root": str(rt2.root)}
    assert not MC.chain_continuous(fake, rt2) and MC.mutant_identity_by_path(fake, rt2)   # a replaced log at the same path passes the hostile only


def test_consequence5_adoption_artifacts_survive_a_restart(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    pred = PR.Prediction(("target",), (), {}, ("preservation",), (), (), 0.1)
    p = PR.SelfChangeProposal("p", "1", (), "operator.x", "D2", "inc", PR.ChangeClass.C2_OPERATOR, {"replace": "v2"}, lambda a: {**a, "op": "v2"}, pred, ("preservation",), (), "target", "restore", "s", "w", PR.Origin.RECOMBINATION)
    led = GV.AdoptionLedger(rt)
    led.propose(p)
    dec = GV.ExternalAdopter("tok").decide(p, GV.Assurance(True, {}, ()))
    comps = {"operator.x": {"artifact": "inc"}}
    led.adopt(p, dec, {"op": "v1"}, comps, cache={"c": 1})
    rt.persist()
    rt2 = OCMRuntime(tmp_path / "rt")                                              # identity-preserving restart
    led2 = GV.AdoptionLedger.load(rt2)
    assert p.fingerprint() in led2.adopted and led2.meter.charges == [1.0] and len(led2.decisions) == 1
    stamp = led2.adopted[p.fingerprint()].stamped_evidence
    assert rt2.state.evidence.liveness([stamp]).value == "LIVE"
    cache = {"c": 2}
    restored, comps_back, exact = led2.rollback(p.fingerprint(), cache=cache)
    assert exact and comps_back == comps and cache == {"c": 1} and restored == {"op": "v1"}
    assert rt2.state.evidence.liveness([stamp]).value == "DEAD"
    assert p.fingerprint() in GV.AdoptionLedger.load(rt2).adopted  # prepared is recoverable until host installation
    led2.acknowledge_rollback_installation(p.fingerprint(), components=comps_back, cache=cache)
    assert not GV.AdoptionLedger.load(rt2).adopted


def test_F1_revocation_reports_the_live_remainder(tmp_path):
    s = ChatSession(tmp_path / "chat")
    s.say("teach: crate = shipping container")
    s.say("the robot lifted the crate")
    lesson = s.traces[-2].warrant_ids[0] if s.traces[-2].warrant_ids else s.traces[-1].warrant_ids[0]
    s.say("teach: crate = wooden box")                                            # a second live sense for the same word
    r = s.say(f"revoke {lesson}")
    assert r.startswith("Revoked") and "'crate' as 'wooden box' still supported" in r
    assert "revoke all crate" not in r  # no nonexistent command is advertised
