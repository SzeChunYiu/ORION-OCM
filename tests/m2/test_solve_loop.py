"""M2 canonical solve loop: structured stages, CANNOT_CHECK propagation, commitment gate."""
from __future__ import annotations

from fractions import Fraction as F

import pytest

from ocm.kso import space as S
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import WarrantProfile as WP
from ocm.runtime import solve as SV


def _space():
    one = WP.one()
    atoms = (
        S.Atom("q", "query_seed", one),
        S.Atom("fact", "claim", WP.of({1}), Authority.of(src=2), Scope.of("en")),
        S.Atom("rule", "procedure", WP.of({2}), Authority.of(src=2), Scope.of("en")),
        S.Atom("far", "claim", one),
        S.Atom("island", "claim", one),
        S.Atom("maybe", "claim", WP.partial([frozenset({3})])),
    )
    edges = (
        S.Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),
        S.Hyperedge("fr", ("fact",), ("rule",), "DEPENDENCE"),
        S.Hyperedge("rfar", ("rule",), ("far",), "DEPENDENCE"),
        S.Hyperedge("qm", ("q",), ("maybe",), "SUPPORT"),
    )
    return S.KnowledgeSpace(atoms, edges)


def _op(checker=lambda out: SV.Status.PASS, **kw):
    return SV.OperatorSpec("apply_rule", "1", lambda ks, oid, args: {"result": 42, "inputs": list(args["inputs"])}, ("fact", "rule"), authority=Authority.of(src=2), scope=Scope.of("en"), checker=checker, **kw)


def _cfg():
    from ocm.kso import surprise as SP

    return SV.SolveConfig(surprise_model=SP.SurpriseModel.PROPAGATED)


def _task(**kw):
    base = dict(targets=("rule",), context="en", required_authority=Authority.of(src=1))
    base.update(kw)
    return SV.Task("t1", (SV.QueryPart("what follows", "claim", ("q",)),), **base)


def test_answer_committed_when_everything_is_live_and_checked():
    out = SV.solve(_space(), _task(), [_op()], config=_cfg(), commit_authority=Authority.of(src=3))
    assert out.decision is SV.Decision.ANSWER and out.answer["result"] == 42
    assert SV.committed(out)
    stages = [s.stage.value for s in out.trace.stages]
    assert stages == ["TASK", "GROUNDING", "REPRESENTATION", "NAVIGATION", "EXTRACTION", "EXECUTION", "COMPOSITION", "CHECK", "DECISION", "COMMITMENT"]
    assert all(s.object_ids or s.stage in (SV.Stage.TASK, SV.Stage.REPRESENTATION) for s in out.trace.stages)


def test_cannot_check_checker_is_never_promoted_to_success():
    out = SV.solve(_space(), _task(), [_op(checker=None)], config=_cfg(), commit_authority=Authority.of(src=3))
    assert out.decision is SV.Decision.CANNOT_CHECK and not SV.committed(out)
    assert out.trace.stages[-1].reason.startswith("REFUSED")


def test_revoked_input_kills_the_candidate_and_reopens_as_learn():
    out = SV.solve(_space(), _task(), [_op()], revoked={2}, commit_authority=Authority.of(src=3))
    assert out.decision in (SV.Decision.LEARN, SV.Decision.UNKNOWN) and not SV.committed(out)
    nav = next(s for s in out.trace.stages if s.stage is SV.Stage.NAVIGATION)
    assert nav.status is SV.Status.FAIL and "WARRANT_GATED" in nav.reason


def test_unknown_warrant_target_yields_clarify():
    t = SV.Task("t2", (SV.QueryPart("is it", "claim", ("q",)),), targets=("maybe",), context="en")
    out = SV.solve(_space(), t, [], revoked={3})
    assert out.decision is SV.Decision.CLARIFY and not SV.committed(out)


def test_obstruction_becomes_a_jump_proposal_not_an_answer():
    t = SV.Task("t3", (SV.QueryPart("reach the island", "claim", ("q",)),), targets=("island",))
    out = SV.solve(_space(), t, [_op()])
    assert out.decision is SV.Decision.JUMP_PROPOSAL and out.witness is not None and out.witness.to_jump_trigger().is_admissible
    assert not SV.committed(out)


def test_commitment_refuses_insufficient_authority_and_scope():
    out = SV.solve(_space(), _task(required_authority=Authority.of(src=5)), [_op()], config=_cfg(), commit_authority=Authority.of(src=3))
    assert out.decision is SV.Decision.ANSWER and not SV.committed(out) and out.trace.stages[-1].reason == "REFUSED:AUTHORITY_INSUFFICIENT"
    out2 = SV.solve(_space(), _task(context="fr"), [_op()], config=_cfg(), commit_authority=Authority.of(src=3))
    assert not SV.committed(out2) and out2.trace.stages[-1].reason == "REFUSED:OUT_OF_SCOPE"


def test_unbound_seed_is_a_clarify_gap_with_structured_reason():
    t = SV.Task("t4", (SV.QueryPart("x", "claim", ("nope",)),))
    out = SV.solve(_space(), t)
    assert out.decision is SV.Decision.CLARIFY and out.trace.stages[1].reason == "UNBOUND_SEED"


def test_crashing_backend_is_a_failed_candidate_never_a_pass():
    bad = SV.OperatorSpec("boom", "1", lambda ks, oid, args: 1 / 0, ("fact", "rule"), checker=lambda out: SV.Status.PASS)
    out = SV.solve(_space(), _task(), [bad], config=_cfg(), commit_authority=Authority.of(src=3))
    assert out.decision is not SV.Decision.ANSWER and not SV.committed(out)


def test_trace_resources_are_a_vector_sum():
    out = SV.solve(_space(), _task(), [_op()], config=_cfg(), commit_authority=Authority.of(src=3))
    r = out.trace.resources
    assert r.navigation_work > 0 and r.verification_calls >= 1 and r.as_dict()["composition_work"] >= 2


def test_propagated_surprise_recovers_the_deep_decisive_atom():
    """M2.1 revival: under the frozen UNIFORM model the decisive atom 'rule' scores 0 surprise
    (fan-out defect); under PROPAGATED it is extracted and the operator applies."""
    from ocm.kso import surprise as SP

    uni = SV.solve(_space(), _task(), [_op()], commit_authority=Authority.of(src=3))
    assert uni.decision is not SV.Decision.ANSWER
    cfg = SV.SolveConfig(surprise_model=SP.SurpriseModel.PROPAGATED)
    prop = SV.solve(_space(), _task(), [_op()], config=cfg, commit_authority=Authority.of(src=3))
    assert prop.decision is SV.Decision.ANSWER and SV.committed(prop)
    ext = next(s for s in prop.trace.stages if s.stage is SV.Stage.EXTRACTION)
    assert "rule" in ext.payload["warranted_atoms"]


def test_hub_theorem_survives_both_surprise_models_and_seed_count_lemma():
    from ocm.kso import surprise as SP

    for m in SP.SurpriseModel:
        r = SP.check_hub_theorem_under_model(m)
        assert r["direction_i"] == r["direction_ii"] == 1
    assert SP.check_seed_count_lemma(_space(), F(1, 3))["mean_equals_uniform_background"] == 1
