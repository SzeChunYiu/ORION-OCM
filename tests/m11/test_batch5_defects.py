"""M11.1: the six runtime defects reported by theory batch 5 (E1–E7), each with its hostile."""
from __future__ import annotations

import pytest

from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.selfmodel import diagnose as DG
from ocm.selfmodel import govern as GV
from ocm.selfmodel import model as SM
from ocm.selfmodel import proposal as PR
from ocm.store.evidence import Channel


def _proposal(**kw):
    pred = PR.Prediction(("target",), (), {"steps": 0}, ("preservation",), (), ("none",), 0.1)
    base = dict(proposal_id="p", version="1", trigger_evidence=(), target_component="operator.x", target_layer="D2", incumbent_fingerprint="inc", change_class=PR.ChangeClass.C2_OPERATOR, change={"replace": "v2"}, apply=lambda a: {**a, "op": "v2"}, prediction=pred, preserved_capabilities=("preservation",), reopened_capabilities=(), discriminator="target", rollback_plan="restore", scope="s", expiry="w", origin=PR.Origin.RECOMBINATION)
    base.update(kw)
    return PR.SelfChangeProposal(**base)


RUN = lambda art, tasks: {"success": sum(1 for t in tasks if art.get("op") == "v2" or t % 2 == 0), "n": len(tasks), "resources": {"steps": len(tasks)}}  # noqa: E731
SUITES = {"target": [1, 3, 5, 7], "preservation": [0, 2, 4, 6]}


def test_E4_E5_prediction_receipt_precedes_shadow_and_dev_tasks_are_refused(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    p = _proposal()
    receipt = GV.register_prediction(rt, p)                       # K_self receipt admitted BEFORE the shadow
    sh = GV.shadow_evaluate(rt, {"op": "v1"}, p, RUN, SUITES)
    a = GV.assure(p, sh, protocol_hash="h", frozen_protocol_hash="h", budget={"steps": 10}, rollback_exists=True, prediction_receipt=receipt, runtime=rt, held_out_task_ids=["t1", "t3"])
    assert a.passed and "legacy_digest_string" not in a.checks
    late = GV.PredictionReceipt(receipt.evidence_id, receipt.digest, sh.events_before + 5)   # a receipt "registered" after the shadow
    b = GV.assure(p, sh, protocol_hash="h", frozen_protocol_hash="h", budget={"steps": 10}, rollback_exists=True, prediction_receipt=late, runtime=rt)
    assert not b.passed and "no_leakage" in b.reasons
    dev = PR.mutant_graded_on_dev_tasks(p, ["t1", "t3"])
    c = GV.assure(dev, sh, protocol_hash="h", frozen_protocol_hash="h", budget={"steps": 10}, rollback_exists=True, prediction_receipt=GV.register_prediction(rt, dev), runtime=rt, held_out_task_ids=["t1", "t3"])
    assert not c.passed and "REFUSED_TASKS_SEEN_BY_PROPOSER" in c.reasons


def test_E5_shadow_runner_that_writes_the_ledger_breaks_non_interference(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    p = _proposal()
    sh = GV.shadow_evaluate(rt, {"op": "v1"}, p, GV.mutant_runner_writes_object_state(rt), SUITES)
    assert not sh.non_interference and sh.event_head_before != sh.event_head_after


def test_E6_ledger_owns_cache_and_exactness(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    p = _proposal()
    ledger = GV.AdoptionLedger(rt)
    ledger.propose(p)
    dec = GV.ExternalAdopter("tok").decide(p, GV.Assurance(True, {}, ()))
    cache = {"compiled": "v1"}
    comps = {"operator.x": {"artifact": "inc"}}
    challenger, info = ledger.adopt(p, dec, {"op": "v1"}, comps, cache=cache)
    cache["compiled"] = "v2"                                                  # the adoption recompiled the cache
    restored, comps_back, exact = ledger.rollback(p.fingerprint(), cache=cache)
    assert exact and cache == {"compiled": "v1"} and comps_back == comps and restored == {"op": "v1"}
    assert GV.mutant_rollback_keeps_cache(GV.RollbackArtifact("x", None, "", "", {}), {"compiled": "v2"}) == {"compiled": "v2"}   # the hostile keeps the compiled cache


def test_E7_meter_is_outside_every_proposal_write_set_and_non_decreasing(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    p = _proposal()
    ledger = GV.AdoptionLedger(rt, meter=GV.Meter(charge=1.0, budget=2.0))
    with pytest.raises(PermissionError):
        ledger.propose(PR.mutant_nested_meter_edit(p))                        # nested key reaches the meter → refused
    with pytest.raises(PermissionError):
        ledger.propose(_proposal(change={"params": {"budget": 99}}))
    assert not hasattr(p, "meter") and ledger.meter.bound == 2
    with pytest.raises(ValueError):
        ledger.meter.raise_charge(0.5)                                        # non-decreasing
    with pytest.raises(AttributeError):
        ledger.meter.charge = 0.0                                             # read-only
    ledger.propose(p); ledger.propose(_proposal(proposal_id="q"))
    with pytest.raises(ValueError):
        ledger.propose(_proposal(proposal_id="r"))                            # livelock bound ⌊B/δ⌋ = 2


def _failure(ablations, freq):
    return SM.FailureRecord("f", "t", "env", "o", "e", ("ev:trace1",), (SM.Layer.D2_OPERATOR, SM.Layer.D3_REPRESENTATION), tuple(ablations), {}, "LIVE", "high", freq, "s")


def test_E2_E3_alarm_needs_certificate_not_frequency_and_registry_closure():
    f = _failure([SM.AblationEvidence("op", SM.Layer.D2_OPERATOR, False, "a"), SM.AblationEvidence("rep", SM.Layer.D3_REPRESENTATION, True, "b")], freq=9)
    assert not DG.diagnose(f).architecture_alarm and DG.mutant_repeated_failure_is_architecture(f)      # frequency never contributes
    live = WP.of({"e"})
    registry = {SM.Layer.D2_OPERATOR: ("op_a", "op_b", "op_c")}
    partial = DG.ObstructionCertificate(SM.Layer.D2_OPERATOR, "solve", ("op_a", "op_b"), (DG.Attempt("op_a", SM.Layer.D2_OPERATOR, live, False), DG.Attempt("op_b", SM.Layer.D2_OPERATOR, live, False)), {}, ("ceiling",), "x")
    assert partial.valid() and DG.mutant_certificate_lists_its_own_alternatives(partial)                 # its own list passes
    assert not partial.valid(registry) and not DG.diagnose(f, certificate=partial, registry=registry).architecture_alarm   # the registry closure does not
    assert not DG.escalation_allowed(DG.diagnose(f, certificate=partial, registry=registry), partial, registry)[0]
    full = DG.ObstructionCertificate(SM.Layer.D2_OPERATOR, "solve", ("op_a", "op_b", "op_c"), tuple(DG.Attempt(o, SM.Layer.D2_OPERATOR, live, False) for o in ("op_a", "op_b", "op_c")), {}, ("ceiling",), "x")
    assert full.valid(registry) and DG.diagnose(f, certificate=full, registry=registry).architecture_alarm


def test_E1_failure_records_are_derived_from_their_traces(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    _, trace = rt.admit_evidence({"trace": 1}, Channel.OBSERVATION, "runner")
    sm = SM.SelfModel(rt)
    f = SM.FailureRecord("f", "t", "env", "o", "e", (trace,), (SM.Layer.D2_OPERATOR,), (), {}, "LIVE", "high", 1, "s")
    eid = sm.ingest_failure(f)
    assert rt.state.evidence.liveness([eid]).value == "LIVE"
    rt.revoke([trace])
    assert rt.state.evidence.liveness([eid]).value == "DEAD"                  # revoking the trace reopens the diagnosis record
