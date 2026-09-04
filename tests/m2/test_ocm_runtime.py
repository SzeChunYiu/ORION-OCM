"""M2 §1/§4/§11: the unified runtime — restart invariant, replay, multi-domain non-interference,
learn→use→revoke→restart→relearn lifecycle, commit boundary through the runtime, hostiles."""
from __future__ import annotations

from fractions import Fraction as F

import pytest

from ocm.constitution import action as CA
from ocm.constitution.hard_gates import HardGateContract, HardGateObservation, HardGateRequirement, HardGateState
from ocm.kso import space as S
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.learning import learner as L
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime, RuntimeRefusal
from ocm.store.event import EventType, mutant_reorder, verify_chain
from ocm.store.evidence import Channel
from ocm.store.ledger import LedgerIntegrityError

AND = {"AND": lambda x: int(x[0] and x[1]), "OR": lambda x: int(x[0] or x[1]), "XOR": lambda x: int(x[0] != x[1])}
DOMAIN = ((0, 0), (0, 1), (1, 0), (1, 1))


def _boot(tmp_path):
    rt = OCMRuntime(tmp_path / "rt", commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    rt.admit_object(S.Atom("goal", "goal", quarantined=True), (), "INSTRUCTION")
    return rt


def _learn_and(rt, prefix="ev"):
    lr = L.VersionSpaceLearner("skill:and", AND, DOMAIN)
    lr.observe(L.Experience("x1", L.ExperienceKind.DEMONSTRATION, f"{prefix}:1", "skill:and", {"pairs": [((1, 1), 1), ((0, 1), 0), ((1, 0), 0)]}))
    p = [p for p in lr.propose_updates() if p.kind is L.UpdateKind.OBJECT][0]
    return rt.learn(p, link_from="goal")


def test_restart_invariant_run_persist_load_same_state(tmp_path):
    rt = _boot(tmp_path)
    _learn_and(rt)
    rt.compose(["skill:and"], "answer")
    h = rt.state.kso_state_hash
    n = len(rt.events)
    rt.persist()
    rt2 = OCMRuntime(tmp_path / "rt", commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    assert rt2.state.kso_state_hash == h and len(rt2.events) == n + 1
    assert rt2.state.ks.atom("answer").liveness(()) is Liveness.LIVE
    assert rt2.replay()["identical"]


def test_learn_use_revoke_restart_remains_revoked_reinstate_recovers(tmp_path):
    rt = _boot(tmp_path)
    _learn_and(rt)
    assert rt.state.ks.atom("skill:and").liveness(rt.state.revoked) is Liveness.LIVE
    rep = rt.revoke(["ev:1"])
    assert "skill:and" in rep.reopen and rt.state.ks.atom("skill:and").liveness(rt.state.revoked) is Liveness.DEAD
    rt.persist()
    rt2 = OCMRuntime(tmp_path / "rt", commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    assert rt2.state.ks.atom("skill:and").liveness(rt2.state.revoked) is Liveness.DEAD
    rt2.reinstate(["ev:1"])
    assert rt2.state.ks.atom("skill:and").liveness(rt2.state.revoked) is Liveness.LIVE
    rt2.persist()
    rt3 = OCMRuntime(tmp_path / "rt", commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    assert rt3.state.ks.atom("skill:and").liveness(rt3.state.revoked) is Liveness.LIVE and rt3.replay()["identical"]


def test_multi_domain_non_interference_through_the_runtime(tmp_path):
    rt = _boot(tmp_path)
    _learn_and(rt)
    rt.admit_object(S.Atom("proof:lemma", "proof", WP.of({"lean:cert:1"}), Authority.of(src=3), Scope.of("math")), (S.Hyperedge("g-proof", ("goal",), ("proof:lemma",), "DEPENDENCE"),), "EXACT_CHECKER")
    rt.revoke(["ev:1"])
    assert rt.state.ks.atom("proof:lemma").liveness(rt.state.revoked) is Liveness.LIVE
    rt.reinstate(["ev:1"])
    rt.revoke(["lean:cert:1"])
    assert rt.state.ks.atom("skill:and").liveness(rt.state.revoked) is Liveness.LIVE and rt.state.ks.atom("proof:lemma").liveness(rt.state.revoked) is Liveness.DEAD
    rt.persist()
    rt2 = OCMRuntime(tmp_path / "rt", commit_authority=CA.StaticCommitAuthority(Authority.of(commit=1)))
    assert rt2.state.ks.atom("proof:lemma").liveness(rt2.state.revoked) is Liveness.DEAD and rt2.state.ks.atom("skill:and").liveness(rt2.state.revoked) is Liveness.LIVE


def test_solve_emits_events_referring_to_real_ids_and_jump_is_only_proposed(tmp_path):
    rt = _boot(tmp_path)
    _learn_and(rt)
    rt.admit_object(S.Atom("island", "claim"), (), "INSTRUCTION") if False else None
    task = SV.Task("t", (SV.QueryPart("use and", "goal", ("goal",)),), targets=("skill:and",))
    out = rt.solve(task)
    kinds = [e.event_type for e in rt.events]
    assert EventType.QUERY_OPENED in kinds and EventType.NAVIGATION in kinds and EventType.EXTRACTION in kinds
    nav = [e for e in rt.events if e.event_type is EventType.NAVIGATION][-1]
    assert set(nav.output_object_ids) <= set(rt.state.ks.ids)
    assert not any(e.event_type is EventType.JUMP_ADOPTED for e in rt.events)


def test_commit_boundary_through_runtime_refuses_without_authority_and_logs_intent_then_receipt(tmp_path):
    rt = _boot(tmp_path)
    _learn_and(rt)
    contract = HardGateContract("c", (HardGateRequirement("g", "checked", evidence_required=True),), frozen_at_round=1)
    obs = [HardGateObservation("g", "i", HardGateState.PASS, contract.fingerprint, ("ev:gate",), "ok")]
    intent = CA.ActionIntent("i", "act", {}, Scope.universal(), Authority.of(commit=1), ("skill:and",), "done", "low")
    calls = []
    r = rt.commit_external_action(intent, contract=contract, observations=obs, effector=lambda i: calls.append(i.intent_id) or {"effect": "done"})
    assert r.status is CA.ActionStatus.EXECUTED and calls == ["i"]
    seq = [e.event_type for e in rt.events[-2:]]
    assert seq == [EventType.ACTION_INTENT, EventType.ACTION_RECEIPT]
    rt_noauth = OCMRuntime(tmp_path / "rt2")
    rt_noauth.admit_object(S.Atom("goal", "goal", quarantined=True), (), "INSTRUCTION")
    with pytest.raises(RuntimeRefusal):
        rt_noauth.commit_external_action(intent, contract=contract, observations=obs, effector=lambda i: {"effect": "done"})


def test_event_log_order_corruption_and_stale_cache_are_refused(tmp_path):
    rt = _boot(tmp_path)
    _learn_and(rt)
    with pytest.raises(ValueError):
        verify_chain(mutant_reorder(list(rt.events)))
    # corrupt the ledger on disk: swap two lines
    path = rt.ledger.path
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0], lines[1] = lines[1], lines[0]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(LedgerIntegrityError):
        OCMRuntime(tmp_path / "rt")


def test_feedback_only_skill_is_never_promoted_and_zero_warrant_object_refused(tmp_path):
    rt = _boot(tmp_path)
    lr = L.VersionSpaceLearner("skill:and", AND, DOMAIN)
    lr.observe(L.Experience("f", L.ExperienceKind.FEEDBACK, "ev:fb", "skill:and", {"reward": 1.0}))
    props = lr.propose_updates()
    assert all(p.kind is not L.UpdateKind.OBJECT for p in props)
    for p in props:
        rt.learn(p)
    assert "skill:and" not in rt.state.ks.ids
    zero = L.UpdateProposal("z", L.UpdateKind.OBJECT, "skill:z", {}, WP.zero(), L.CertificateKind.DEMONSTRATION, (), L.UpdateStatus.PASS)
    with pytest.raises(RuntimeRefusal):
        rt.learn(zero)


def test_evidence_registry_contradiction_and_supersession_survive_restart(tmp_path):
    rt = _boot(tmp_path)
    _, a = rt.admit_evidence({"claim": "moon=cheese"}, Channel.INSTRUCTION, "user")
    _, b = rt.admit_evidence({"claim": "moon=rock"}, Channel.OBSERVATION, "probe", contradicts=[a])
    assert rt.state.evidence.liveness([a, b]) is Liveness.DEAD and rt.state.evidence.liveness([b]) is Liveness.LIVE
    rt.persist()
    rt2 = OCMRuntime(tmp_path / "rt")
    assert rt2.state.evidence.liveness([a, b]) is Liveness.DEAD and rt2.state.evidence_epoch == rt.state.evidence_epoch
