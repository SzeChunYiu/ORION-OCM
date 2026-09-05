"""Population guarantees cannot certify a selected output's exact truth."""
from fractions import Fraction

import pytest

from ocm.constitution.action import ActionIntent, StaticCommitAuthority
from ocm.kso.space import Atom, KnowledgeSpace
from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.operators.registry import BackendKind, CoverageCertificate, OperatorSpec, compose_candidate


def _case(delta=Fraction(1, 20), coverage_scope=None):
    ks = KnowledgeSpace((Atom("input", "claim", WP.of({"input:evidence"}), scope=Scope.of("en")),), ())
    op = OperatorSpec("statistical", "1", BackendKind.STATISTICAL, lambda ks, args: {"answer": 999}, ("input",), warrant=WP.of({"operator:evidence"}), scope=Scope.of("en", "de"))
    cert = CoverageCertificate(op.fingerprint, coverage_scope or Scope.of("en"), delta, "exchangeability", "calibration:evidence")
    return ks, op, cert


@pytest.mark.parametrize("delta", [Fraction(0), Fraction(1, 20), Fraction(1, 2)])
def test_population_guarantee_does_not_make_selected_answer_exact_or_authorized(delta):
    ks, op, cert = _case(delta)
    candidate = compose_candidate(ks, op, {"answer": 999}, score=1.0, coverage=cert, context="en")
    assert candidate.liveness(()) is Liveness.UNKNOWN
    assert candidate.certificate is None and candidate.authority.rank("commit") == 0
    assert candidate.guarantee.kind == "OPERATOR_GUARANTEE"
    assert candidate.guarantee.certificate == cert and candidate.guarantee.liveness(()) is Liveness.LIVE
    intent = ActionIntent("intent", "publish exact answer", {}, Scope.of("en"), Authority.of(commit=1), ("candidate",), "published", "low")
    decision = StaticCommitAuthority(Authority.of(commit=1)).decide(intent, gate_state="PASS", warrant_liveness=candidate.liveness(()).value)
    assert not decision.granted


def test_revoking_coverage_retracts_only_the_guarantee_and_exact_proof_remains_independent():
    ks, op, cert = _case()
    candidate = compose_candidate(ks, op, {"answer": 999}, coverage=cert, context="en")
    assert candidate.liveness(()) is Liveness.UNKNOWN
    assert candidate.guarantee.liveness((cert.evidence_id,)) is Liveness.DEAD
    assert candidate.liveness((cert.evidence_id,)) is Liveness.UNKNOWN
    exact = compose_candidate(ks, op, {"answer": 7}, exact_certificate_evidence="proof:evidence", context="en")
    assert exact.liveness((cert.evidence_id,)) is Liveness.LIVE
    assert exact.liveness(("proof:evidence",)) is Liveness.DEAD
    assert candidate.guarantee.liveness(("unrelated",)) is Liveness.LIVE


def test_guarantee_cannot_apply_outside_intersection_of_input_and_certificate_scopes():
    ks, op, cert = _case(coverage_scope=Scope.of("en", "de"))
    candidate = compose_candidate(ks, op, {"answer": 999}, coverage=cert, context="de")
    assert candidate.liveness(()) is Liveness.UNKNOWN
    assert candidate.guarantee is None
