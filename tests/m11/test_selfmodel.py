"""M11 §1–§5, §9–§12: self-model without self-authority, diagnosis as a distribution with the
obstruction certificate, proposals with pre-outcome prediction, shadow non-interference,
assurance, external adoption only, exact rollback, meter."""
from __future__ import annotations

import pytest

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.selfmodel import diagnose as DG
from ocm.selfmodel import govern as GV
from ocm.selfmodel import model as SM
from ocm.selfmodel import proposal as PR


def test_self_model_records_tie_to_identities_and_never_raise_object_authority(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    sm = SM.SelfModel(rt)
    eid = sm.register(SM.Component("router.v1", SM.ComponentKind.ROUTER, "1", SM.Component.fingerprint_of({"policy": "typed"})))
    rec = rt.state.evidence.records[eid]
    assert rec.scope.contexts == frozenset({"self"}) and rec.authority.rank("self_model") == 1 and rec.authority.rank("world_truth") == 0 and rec.authority.rank("commit") == 0
    assert sm.statements_tied_to_identities()
    obj = Authority.of(world_truth=1, source=1)
    assert SM.self_authority_never_raises_object(sm, obj).rank("world_truth") == 0      # meet with the self-model: never rises
    assert SM.mutant_self_description_as_authority("we improved").rank("world_truth") == 1  # the hostile


def _failure(ablations, freq=1):
    return SM.FailureRecord("f1", "t1", "enterprise", "wrong action", "smallest action", ("ev:trace1",), (SM.Layer.D1_ROUTING, SM.Layer.D2_OPERATOR, SM.Layer.D3_REPRESENTATION), tuple(ablations), {}, "LIVE", "high", freq, "enterprise")


def test_diagnosis_is_a_distribution_minimum_sufficient_and_escalation_needs_a_valid_certificate():
    # restoring the operator fixes the task; swapping the router does not → D2 minimum-sufficient
    f = _failure([SM.AblationEvidence("swap router", SM.Layer.D1_ROUTING, False, "ev:a1"), SM.AblationEvidence("restore operator", SM.Layer.D2_OPERATOR, True, "ev:a2")])
    d = DG.diagnose(f)
    assert d.weights == {"D1": 0.0, "D2": 1.0} and d.unknown == ("D3",) and d.minimum_sufficient == "D2" and not d.architecture_alarm
    ok, why = DG.escalation_allowed(d, None)
    assert not ok and "local" in why
    assert DG.mutant_low_score_is_architecture(f)                                    # the hostile
    # representation ceiling: only a representation change restores; escalation needs the certificate
    f3 = _failure([SM.AblationEvidence("restore operator", SM.Layer.D2_OPERATOR, False, "ev:b1"), SM.AblationEvidence("new representation", SM.Layer.D3_REPRESENTATION, True, "ev:b2")], freq=4)
    live, dead = WP.of({"e1"}), WP.of({"e2"})
    good = DG.ObstructionCertificate(SM.Layer.D2_OPERATOR, "solve t1", ("op_a", "op_b"), (DG.Attempt("op_a", SM.Layer.D2_OPERATOR, live, False), DG.Attempt("op_b", SM.Layer.D2_OPERATOR, live, False)), {"steps": 8}, ("ceiling:xor-not-affine",), "no operator composition distinguishes the states")
    assert good.valid() and DG.escalation_allowed(DG.diagnose(f3, certificate=good), good)[0]
    assert DG.diagnose(f3, certificate=good).architecture_alarm
    untried = DG.ObstructionCertificate(SM.Layer.D2_OPERATOR, "solve t1", ("op_a", "op_b"), (DG.Attempt("op_a", SM.Layer.D2_OPERATOR, live, False),), {}, ("ceiling",), "x")
    assert not untried.valid() and "untried" in untried.reasons()[0]
    deadw = DG.ObstructionCertificate(SM.Layer.D2_OPERATOR, "solve t1", ("op_a",), (DG.Attempt("op_a", SM.Layer.D2_OPERATOR, dead, False),), {}, ("ceiling",), "x", revoked=frozenset({"e2"}))
    assert not deadw.valid() and "reinstate" in deadw.reasons()[0] and DG.mutant_dead_warrant_obstruction(deadw)   # the hostile accepts it
    # false structural alarm: the failure is a revoked dependency (S5) — reinstating fixes it at D0/D2, not D7
    f5 = _failure([SM.AblationEvidence("reinstate evidence", SM.Layer.D2_OPERATOR, True, "ev:c1"), SM.AblationEvidence("rewrite organisation", SM.Layer.D7_ORGANISATION, True, "ev:c2")], freq=5)
    assert DG.diagnose(f5).minimum_sufficient == "D2" and not DG.diagnose(f5, certificate=good).architecture_alarm


def _proposal(cls=PR.ChangeClass.C2_OPERATOR, target="operator.smallest", change=None):
    pred = PR.Prediction(("target",), (), {"steps": 0}, ("preservation",), (), ("none",), 0.1)
    return PR.SelfChangeProposal("p1", "1", ("ev:f1",), target, "D2", "fp-inc", cls, change or {"replace": "op_v2"}, lambda a: {**a, "op": "v2"}, pred, ("preservation",), (), "target", "restore previous artifact", "enterprise", "window-1", PR.Origin.RECOMBINATION)


def test_shadow_assurance_external_adoption_and_exact_rollback(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    incumbent = {"op": "v1"}
    p = _proposal()
    assert p.authority.rank("commit") == 0 and PR.is_minimum_sufficient(p, "D2") and not PR.is_minimum_sufficient(_proposal(PR.ChangeClass.C5_ORGANISATION), "D2")
    runner = lambda art, tasks: {"success": sum(1 for t in tasks if art["op"] == "v2" or t % 2 == 0), "n": len(tasks), "resources": {"steps": len(tasks)}}  # noqa: E731
    suites = {"target": [1, 3, 5, 7], "preservation": [0, 2, 4, 6]}
    sh = GV.shadow_evaluate(rt, incumbent, p, runner, suites)
    assert sh.non_interference and sh.challenger["target"]["success"] == 4 and sh.incumbent["target"]["success"] == 0 and sh.challenger["preservation"]["success"] == 4
    a = GV.assure(p, sh, protocol_hash="h", frozen_protocol_hash="h", prediction_digest_before_access=p.prediction.digest(), budget={"steps": 10}, rollback_exists=True)
    assert a.passed, a.reasons
    bad = GV.assure(p, sh, protocol_hash="h", frozen_protocol_hash="h2", prediction_digest_before_access="tampered", budget={"steps": 10}, rollback_exists=False)
    assert not bad.passed and set(bad.reasons) >= {"protocol_intact", "no_leakage", "rollback_artifact"}
    ledger = GV.AdoptionLedger(rt)
    ledger.propose(p)
    with pytest.raises(PermissionError):
        ledger.propose(PR.mutant_proposal_edits_evaluator(p))                        # touches a protected target
    with pytest.raises(PermissionError):
        ledger.adopt(p, GV.mutant_self_approve(p), incumbent, {})                   # self-approval has no token
    adopter = GV.ExternalAdopter("secret-token")
    dec = adopter.decide(p, a)
    assert dec.approved and dec.authority_token != "no-token"
    comps = {"operator.smallest": {"artifact": "fp-inc"}, "skill.enterprise": {"artifact": "s", "depends_on": "operator.smallest"}}
    ks0 = rt.state.ks.digest()                                                     # object-level knowledge space
    challenger, info = ledger.adopt(p, dec, incumbent, comps)
    assert challenger == {"op": "v2"} and info["migration"]["revalidate"] == ["skill.enterprise"] and info["migration"]["lineage"] == ["fp-inc", p.fingerprint()]
    assert rt.state.evidence.liveness([info["stamped_evidence"]]).value == "LIVE"
    restored, comps_back, ok = ledger.rollback(p.fingerprint())
    assert ok and restored == incumbent and comps_back == comps and rt.state.evidence.liveness([info["stamped_evidence"]]).value == "DEAD"
    assert rt.state.ks.digest() == ks0                                             # object-level KS untouched by the self-change path (the ledger keeps the adoption and its revocation)
    assert GV.mutant_rollback_keeps_cache(ledger.adopted.get(p.fingerprint()) or GV.RollbackArtifact("x", None, "", "", {}), {"compiled": 1}) == {"compiled": 1}   # the hostile
    # constitutional proposals are recommendation packets only
    c6 = _proposal(PR.ChangeClass.C6_CONSTITUTION, target="constitution.gate")
    assert not c6.adoptable_through_cognition()
    # monitoring triggers rollback on regression / authority violation
    mon = GV.monitor([{"target_success": 0.9, "preservation_success": 1.0}, {"target_success": 0.4, "authority_violations": 1}], target_threshold=0.8, preservation_min=0.9)
    assert mon["rollback_recommended"] and ("target_regression" in [t for _, t in mon["triggers"]])
