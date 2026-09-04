"""M2 §7 operator registry and the MEG-02 statistical-operator warrant rule."""
from __future__ import annotations

from fractions import Fraction as F

import pytest

from ocm.kso import space as S
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.operators import registry as R


def _ks():
    return S.KnowledgeSpace((S.Atom("x", "claim", WP.of({1}), Authority.of(src=2), Scope.of("en", "de")), S.Atom("y", "claim", WP.of({2}), Authority.of(src=3), Scope.of("en"))), ())


def _op(kind, checker=None):
    return R.OperatorSpec("guess", "1", kind, lambda ks, args: {"answer": 7}, ("x", "y"), warrant=WP.of({9}), authority=Authority.of(src=2), scope=Scope.of("en", "fr"), checker=checker)


def test_programmatic_candidate_is_warranted_by_inputs_and_operator():
    c = R.compose_candidate(_ks(), _op(R.BackendKind.PROGRAMMATIC), {"answer": 7})
    assert c.warrant.lower == (frozenset({1, 2, 9}),) and c.liveness(()) is Liveness.LIVE and c.liveness((9,)) is Liveness.DEAD
    assert c.authority == Authority.of(src=2) and c.scope.contexts == frozenset({"en"})


def test_statistical_candidate_enters_unknown_and_score_is_not_warrant():
    c = R.compose_candidate(_ks(), _op(R.BackendKind.STATISTICAL), {"answer": 7}, score=0.99)
    assert c.liveness(()) is Liveness.UNKNOWN and c.score == 0.99 and c.certificate is None
    bad = R.mutant_score_promoted_to_warrant(_ks(), _op(R.BackendKind.STATISTICAL), {"answer": 7}, 0.99)
    assert bad.liveness(()) is Liveness.LIVE  # the laundering the rule forbids


def test_coverage_certificate_licenses_only_inside_its_scope():
    op = _op(R.BackendKind.STATISTICAL)
    cert = R.CoverageCertificate(op.fingerprint, Scope.of("en"), F(1, 20), "exchangeability", "ev:calib:1")
    inside = R.compose_candidate(_ks(), op, {"answer": 7}, coverage=cert, context="en")
    assert inside.liveness(()) is Liveness.LIVE and inside.certificate.startswith("COVERAGE") and inside.liveness(("ev:calib:1",)) is Liveness.DEAD
    outside = R.compose_candidate(_ks(), op, {"answer": 7}, coverage=cert, context="de")
    assert outside.liveness(()) is Liveness.UNKNOWN
    other = R.CoverageCertificate("not-this-operator", Scope.of("en"), F(1, 20), "exch", "ev:calib:2")
    with pytest.raises(S.TypedRejection):
        R.compose_candidate(_ks(), op, {"answer": 7}, coverage=other, context="en")
    with pytest.raises(S.TypedRejection):
        R.CoverageCertificate(op.fingerprint, Scope.of("en"), F(1, 20), "x", "ev", channel=R.CertificateKind.FEEDBACK)


def test_exact_checker_certificate_makes_statistical_candidate_live():
    c = R.compose_candidate(_ks(), _op(R.BackendKind.STATISTICAL), {"answer": 7}, exact_certificate_evidence="ev:lean:proof")
    assert c.liveness(()) is Liveness.LIVE and c.certificate == "EXACT_CHECKER" and c.liveness(("ev:lean:proof",)) is Liveness.DEAD


def test_all_unknown_components_never_compose_live():
    a = R.compose_candidate(_ks(), _op(R.BackendKind.STATISTICAL), {"a": 1})
    b = R.compose_candidate(_ks(), _op(R.BackendKind.STATISTICAL), {"b": 2})
    assert a.warrant.meet(b.warrant).liveness(()) is Liveness.UNKNOWN and a.warrant.join(b.warrant).liveness(()) is Liveness.UNKNOWN


def test_proof_backend_without_kernel_verdict_is_unknown_and_external_tool_needs_intent():
    c = R.compose_candidate(_ks(), _op(R.BackendKind.PROOF), {"proof": "..."})
    assert c.liveness(()) is Liveness.UNKNOWN
    with pytest.raises(S.TypedRejection) as exc:
        R.compose_candidate(_ks(), _op(R.BackendKind.EXTERNAL_TOOL), {})
    assert exc.value.code == "EXTERNAL_TOOL_REQUIRES_ACTION_INTENT"


def test_registry_applicability_respects_liveness_and_preconditions():
    reg = R.OperatorRegistry()
    op = _op(R.BackendKind.PROGRAMMATIC)
    reg.register(op)
    reg.register(R.OperatorSpec("needs-z", "1", R.BackendKind.PROGRAMMATIC, lambda ks, a: {}, ("x",), preconditions=("z",)))
    ks = _ks()
    assert [o.operator_id for o in reg.applicable(ks, ["x", "y"])] == ["guess"]
    assert reg.applicable(ks, ["x", "y"], revoked={2}) == []
    with pytest.raises(S.TypedRejection):
        reg.register(R.OperatorSpec("guess", "1", R.BackendKind.SEARCH, lambda ks, a: {}, ("x",)))  # same key, different fingerprint
