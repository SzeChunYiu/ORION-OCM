"""M2 §9 commit boundary: fixed sequence, CANNOT_CHECK never success, no self-granted authority."""
from __future__ import annotations

import pytest

from ocm.constitution import action as A
from ocm.constitution import boundary as B
from ocm.constitution.hard_gates import HardGateContract, HardGateObservation, HardGateRequirement, HardGateState
from ocm.kso import space as S
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile as WP


def _ks():
    return S.KnowledgeSpace((S.Atom("plan", "procedure", WP.of({1}), Authority.of(src=2)), S.Atom("maybe", "claim", WP.partial([frozenset({2})]))), ())


def _intent(support=("plan",), required=Authority.of(commit=1)):
    return A.ActionIntent("i1", "send_email", {"to": "x"}, Scope.of("ops"), required, support, "email sent", "low")


def _contract(seq=1):
    return HardGateContract("c1", (HardGateRequirement("g1", "recipient verified", evidence_required=True),), frozen_at_round=seq)


def _obs(state=HardGateState.PASS, evidence=("ev:recipient",), contract=None):
    c = contract or _contract()
    return HardGateObservation("g1", "i1", state, c.fingerprint, evidence, "ok")


def _effector_counter():
    calls = []

    def eff(intent):
        calls.append(intent.intent_id)
        return {"effect": "sent", "resources": {"io_calls": 1}}

    return eff, calls


def test_executes_only_when_live_pass_and_granted_and_logs_intent_before_receipt():
    eff, calls = _effector_counter()
    log = B.BoundaryLog()
    r = B.commit_external_action(_intent(), ks=_ks(), revoked=(), contract=_contract(1), observations=[_obs()], authority=A.StaticCommitAuthority(Authority.of(commit=1)), effector=eff, log=log, sequence=5)
    assert r.status is A.ActionStatus.EXECUTED and calls == ["i1"] and r.observed_resources.io_calls == 1
    assert [e["kind"] for e in log.entries] == ["ACTION_INTENT", "ACTION_RECEIPT"] and log.entries[0]["status"] == "PROPOSAL"


@pytest.mark.parametrize("case", ["warrant_dead", "warrant_unknown", "gate_fail", "gate_cannot_check", "authority_insufficient", "gate_no_evidence"])
def test_every_refusal_path_performs_no_effect(case):
    eff, calls = _effector_counter()
    log = B.BoundaryLog()
    kw = dict(ks=_ks(), revoked=(), contract=_contract(1), observations=[_obs()], authority=A.StaticCommitAuthority(Authority.of(commit=1)), effector=eff, log=log, sequence=5)
    intent = _intent()
    if case == "warrant_dead":
        kw["revoked"] = (1,)
    elif case == "warrant_unknown":
        intent = _intent(support=("maybe",))
        kw["revoked"] = (2,)
    elif case == "gate_fail":
        kw["observations"] = [_obs(HardGateState.FAIL)]
    elif case == "gate_cannot_check":
        kw["observations"] = []
    elif case == "authority_insufficient":
        kw["authority"] = A.StaticCommitAuthority(Authority.of(commit=0))
    elif case == "gate_no_evidence":
        kw["observations"] = [_obs(evidence=())]
    r = B.commit_external_action(intent, **kw)
    assert calls == [] and r.status in (A.ActionStatus.REFUSED, A.ActionStatus.CANNOT_CHECK) and r.actual_effect == "NONE"
    if case in ("warrant_unknown", "gate_cannot_check", "gate_no_evidence"):
        assert r.status is A.ActionStatus.CANNOT_CHECK
    assert log.entries[-1]["kind"] == "ACTION_RECEIPT"


def test_contract_frozen_after_the_round_is_not_accepted():
    eff, calls = _effector_counter()
    r = B.commit_external_action(_intent(), ks=_ks(), revoked=(), contract=_contract(9), observations=[_obs(contract=_contract(9))], authority=A.StaticCommitAuthority(Authority.of(commit=1)), effector=eff, log=B.BoundaryLog(), sequence=5)
    assert calls == [] and r.status in (A.ActionStatus.REFUSED, A.ActionStatus.CANNOT_CHECK)


def test_internal_authority_never_reaches_commit_and_self_grant_is_the_mutant():
    a = Authority.of(src=3, verification=2).meet(Authority.of(src=1))
    assert A.internal_authority_has_no_commit(a)
    m = A.mutant_self_granting_authority(_intent())
    assert m.granted and m.source == "runtime"       # what the boundary forbids
    eff, calls = _effector_counter()
    r = B.mutant_skip_gate(_intent(), ks=_ks(), revoked=(), authority=A.StaticCommitAuthority(Authority.of(commit=1)), effector=eff)
    assert r.status is A.ActionStatus.EXECUTED and r.gate_state == "SKIPPED"   # the convenience path executes without gates


def test_effector_failure_is_a_failed_receipt_never_silent():
    def boom(intent):
        raise RuntimeError("smtp down")

    r = B.commit_external_action(_intent(), ks=_ks(), revoked=(), contract=_contract(1), observations=[_obs()], authority=A.StaticCommitAuthority(Authority.of(commit=1)), effector=boom, log=B.BoundaryLog(), sequence=5)
    assert r.status is A.ActionStatus.FAILED and "smtp down" in r.actual_effect
