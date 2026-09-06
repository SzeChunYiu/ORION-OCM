"""Real refusal, no-import and state-change controls; no comparative timing."""
from fractions import Fraction as F
import json
import subprocess
import sys
from pathlib import Path
import pytest
from sympy.polys.matrices import DomainMatrix
from ocm.kso import navigation as N
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import CannotCheck
import exact_sparse_donor as D
from test_exact import field


def test_real_singular_system_keeps_cannot_check():
    ks = KnowledgeSpace((Atom("a", "claim"), Atom("b", "claim")),
         (Hyperedge("loop", ("a",), ("a",), "SUPPORT"),
          Hyperedge("out", ("a",), ("b",), "DEPENDENCE")))
    kwargs = {"relevance": {"SUPPORT": F(3), "DEPENDENCE": F(-1)}}
    for implementation in (N.fixed_point, D.fixed_point):
        with pytest.raises(CannotCheck, match="singular exact system"):
            implementation(ks, [F(1), F(0)], F(1,3), **kwargs)


def test_bad_solver_certificate_is_refused(monkeypatch):
    original = DomainMatrix.solve_den
    def wrong(A, B, **kwargs):
        numerator, denominator = original(A, B, **kwargs)
        return numerator.zeros(numerator.shape, numerator.domain), denominator
    monkeypatch.setattr(DomainMatrix, "solve_den", wrong)
    with pytest.raises(CannotCheck, match="ALGEBRAIC_CERTIFICATE_FAILED"):
        D.fixed_point(field(), [F(1), F(0), F(0), F(0), F(0)], F(1,3))


def test_zero_denominator_certificate_is_refused(monkeypatch):
    original = DomainMatrix.solve_den
    def wrong(A, B, **kwargs):
        numerator, denominator = original(A, B, **kwargs)
        return numerator, A.domain.zero
    monkeypatch.setattr(DomainMatrix, "solve_den", wrong)
    with pytest.raises(CannotCheck, match="ALGEBRAIC_CERTIFICATE_FAILED"):
        D.fixed_point(field(), [F(1), F(0), F(0), F(0), F(0)], F(1,3))


def test_wrong_candidate_kernel_is_caught_by_independent_original_residual(monkeypatch):
    original = D.assemble
    def wrong(*args, **kwargs):
        A, B = original(*args, **kwargs)
        return A.eye(A.shape, A.domain).to_sparse(), B
    monkeypatch.setattr(D, "assemble", wrong)
    with pytest.raises(CannotCheck, match="ORIGINAL_RESIDUAL_NONZERO"):
        D.fixed_point(field(), [F(1), F(0), F(0), F(0), F(0)], F(1,3))


def test_repeated_call_and_changed_relevance_rebuild_exact_values():
    ks, seed = field(), [F(1), F(0), F(0), F(0), F(0)]
    relevance = {"SUPPORT": F(1)}
    first = D.fixed_point(ks, seed, F(1,3), relevance=relevance)
    relevance["SUPPORT"] = F(4)
    second = D.fixed_point(ks, seed, F(1,3), relevance=relevance)
    assert first != second == N.fixed_point(ks, seed, F(1,3), relevance=relevance)
    assert D.fixed_point(ks, seed, F(1,3), relevance=relevance) == second


def test_reference_consumer_does_not_import_unused_sympy():
    code = """
import json, sys
from representation_donor_fixture import fixture
from exact_sparse_donor_consumer import evaluate
f=fixture()
out=evaluate(f['ks'],f['task'],f['operators'],arm='reference',
             config=f['config'],commit_authority=f['authority'])
print(json.dumps({'sympy_imported': any(x == 'sympy' or x.startswith('sympy.') for x in sys.modules),
                  'status':out['consumer']['status'], 'channels':len(out['vectors'])}))
"""
    run = subprocess.run([sys.executable, "-c", code], text=True, capture_output=True, timeout=15)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout) == {"sympy_imported": False, "status": "COMPLETED", "channels": 4}


@pytest.mark.parametrize("variant", ["incoming", "mixed_warrant"])
def test_changed_field_modes_have_full_consumer_parity(variant):
    from dataclasses import replace
    from ocm.kso import surprise as SP
    from representation_donor_fixture import fixture
    from exact_sparse_donor_consumer import evaluate
    f = fixture(variant)
    for model in SP.SurpriseModel:
        kwargs = dict(revoked=("background_support",),
            config=replace(f["config"], surprise_model=model), commit_authority=f["authority"])
        reference = evaluate(f["ks"], f["task"], f["operators"], arm="reference", **kwargs)
        candidate = evaluate(f["ks"], f["task"], f["operators"], arm="sympy", **kwargs)
        for key in ("consumer", "vectors", "surprise"):
            assert candidate[key] == reference[key]
