"""M10 §10 proof-kernel boundary, §12 retraction lifecycle, §13 cross-field transfer, §14 communication gate."""
from __future__ import annotations

from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.science import lifecycle as LC
from ocm.science import proof as PF
from ocm.work import contracts as WC
from ocm.work import envs as E


def test_proof_kernel_keeps_kernel_and_correspondence_apart():
    taut = PF.FormalStatement("s1", "propositional", "(p -> q) -> (~q -> ~p)", "contraposition", ("review:1",))
    c = PF.check(taut, run_id="run:1")
    assert c.verdict is PF.KernelVerdict.PASS and c.proof_object_warrant().evidence == {"run:1"}
    assert c.correspondence_warrant.evidence == {"review:1"} and c.proof_object_warrant().evidence != c.correspondence_warrant.evidence
    bad = PF.check(PF.FormalStatement("s2", "propositional", "(p -> q) -> (q -> p)", "converse", ()), run_id="run:2")
    assert bad.verdict is PF.KernelVerdict.FAIL and bad.proof_object_warrant() is None and PF.theorem_false_from_fail(bad)   # complete kernel: countermodel
    lean = PF.check(PF.FormalStatement("s3", "lean4", "theorem t : 1 + 1 = 2 := rfl", "1+1=2", ("review:2",)), run_id="run:3")
    assert lean.verdict is PF.KernelVerdict.CANNOT_CHECK and lean.proof_object_warrant() is None
    assert PF.mutant_fail_means_false(bad) and PF.mutant_fail_means_false(PF.ProofCertificate("x", "lean4", PF.KernelVerdict.FAIL, "timeout", WP.zero(), WP.zero()))   # the hostile treats any FAIL as falsity
    mis = PF.FormalStatement("s4", "propositional", "p | ~p", "every even number is the sum of two primes", ())   # mistranslation: a tautology standing in for Goldbach
    cm = PF.check(mis, run_id="run:4")
    assert cm.verdict is PF.KernelVerdict.PASS and cm.correspondence_warrant.liveness(()) is Liveness.DEAD   # no correspondence evidence → the informal claim is not covered
    assert PF.mutant_accept_mistranslation(cm) is not None                # the hostile: kernel PASS used for the informal claim


def test_retraction_reopens_exactly_and_replacement_has_lineage(tmp_path):
    rt = OCMRuntime(tmp_path / "rt")
    L = LC.ScienceLedger(rt)
    L.observe("E1", "labA", {"x": 1.0}); L.observe("E2", "labB", {"x": 1.1}); L.observe("E3", "labC", {"y": 5.0})
    c1 = L.conclude("C1", "x is positive", support=["E1", "E2"], kind="ESTIMATE")
    c2 = L.conclude("C2", "y is large", support=["E3"], kind="ESTIMATE")
    assert L.liveness("C1") is Liveness.LIVE and L.liveness("C2") is Liveness.LIVE
    rep = L.retract("E1")
    assert rep["conclusions_dead"] == ["C1"] and L.liveness("C2") is Liveness.LIVE      # unrelated science stays
    L.observe("E4", "labD", {"x": 0.9})
    new = L.replace_support("C1", "E4")
    assert L.liveness("C1#2") is Liveness.LIVE and L.conclusions["C1#2"]["lineage"] == ["C1"] and L.liveness("C1") is Liveness.DEAD
    # replay reproduces the derived records
    rt.persist(); rt2 = OCMRuntime(tmp_path / "rt")
    assert rt2.state.evidence.liveness([L.conclusions["C1"]["evidence_id"]]) is Liveness.DEAD and rt2.state.evidence.liveness([L.conclusions["C1#2"]["evidence_id"]]) is Liveness.LIVE


def _science_ops():
    def op(oid, role):
        return WC.Operator(oid, "1", "science", lambda s: True, lambda s: s, (), lambda s: True, lambda s: True, role=role)
    return {o: op(o, r) for o, r in [("sci.inspect_evidence", "inspect_evidence"), ("sci.diagnose", "diagnose"), ("sci.check_assumptions", "check_assumptions"), ("sci.discriminating_experiment", "discriminating_experiment"), ("sci.validate", "validate"), ("sci.report", "report"), ("sci.work_verify_lookalike", "verify")]}


def test_cross_field_transfer_is_partial_and_refuses_lookalike_verifier():
    ent = E.enterprise_operators()
    src = WC.Skill("m:enterprise", E.ROLES, {r: next(o for o in ent if ent[o].role == r) for r in E.ROLES}, "enterprise", WP.of({"ev:demo"}))
    sci = _science_ops()
    tm = LC.science_transfer_map(src, sci, "corr:work->science")
    v, sk, why = LC.transported_science_skill(src, tm, sci)
    assert v is WC.TransferVerdict.TRANSFER and sk.bindings["verify"] == "sci.validate" and sk.warrant.evidence == {"ev:demo", "corr:work->science"}
    bad = WC.TransferMap(tm.transfer_id, tm.source_skill, "science", {**tm.role_mapping, "verify": "sci.work_verify_lookalike"}, tm.shared_preconditions, tm.invariant_core, tm.discarded, tm.adapter, 0.4, tm.required_tests, tm.correspondence_warrant)
    v2, _, why2 = LC.transported_science_skill(src, bad, sci)
    assert v2 is WC.TransferVerdict.REFUSE_TRANSFER and "validate" in why2            # a work verifier is not a statistical validation
    partial = {k: v_ for k, v_ in sci.items() if k != "sci.report"}
    assert LC.transported_science_skill(src, LC.science_transfer_map(src, partial, "c"), partial)[0] is WC.TransferVerdict.ADAPTER_REQUIRED


def test_communication_gate_downgrades_or_refuses_overclaims():
    assoc = {"liveness": "LIVE", "association": True}
    ok, s, why = LC.gate_sentence("The data suggests that X raises Y.", assoc)
    assert ok and "suggests" in s
    over = LC.mutant_fluent_overclaim("The data suggests that X raises Y.")
    ok2, s2, why2 = LC.gate_sentence(over, assoc)
    assert ok2 and "causes" not in s2 and "suggests" in s2 and "downgraded" in why2
    causal = {"liveness": "LIVE", "causal_identified": True}
    assert LC.gate_sentence("The intervention shows X causes Y.", causal)[0]
    proved = {"kernel": "PASS", "correspondence": "LIVE"}
    assert LC.gate_sentence("This proves the lemma.", proved)[0]
    cannot = {"kernel": "CANNOT_CHECK"}
    ok3, s3, why3 = LC.gate_sentence("Our elegant analysis proves the conjecture.", cannot)
    assert not ok3 and "cannot determine" in s3                                   # hostile: elegant language hiding CANNOT_CHECK
    assert not LC.gate_sentence("X and Y are related.", assoc)[0]                     # no marker: refused
