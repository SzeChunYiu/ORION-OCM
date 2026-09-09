from __future__ import annotations

import copy

import pytest

import pure_checker_contract as PC
import r0a_prospective_checker_binding as B
from ocm.operators.registry import BackendKind, OperatorSpec
from ocm.runtime import solve as SV


def _spec(*, version="1", expected_effects=(), host_calls=None):
    calls = [] if host_calls is None else host_calls

    def backend(*_args):
        return {"answer": 42}

    def hostile_host_checker(_candidate):
        calls.append("called")
        return SV.Status.FAIL

    return OperatorSpec(
        operator_id="bound",
        version=version,
        kind=BackendKind.PROGRAMMATIC,
        backend=backend,
        input_atoms=("fact",),
        output_type="claim",
        checker=hostile_host_checker,
        expected_effects=expected_effects,
    )


def _pass_cert():
    return PC.issue_certificate({"op": "STATUS", "status": "PASS"})


def test_binding_is_deterministic_and_content_bound():
    spec = _spec()
    cert = _pass_cert()
    left = B.issue_binding(spec, cert)
    right = B.issue_binding(spec, copy.deepcopy(cert))
    assert left == right
    manifest = left["operator_manifest"]
    assert manifest["implementation_identity"] == "PURE_CHECKER_CERTIFIED"
    assert manifest["checker_execution_mode"] == "PURE_CHECKER_DSL_ONLY"
    assert manifest["checker_certificate_schema"] == PC.SCHEMA
    assert manifest["checker_language_version"] == PC.LANGUAGE
    assert manifest["checker_ast_sha256"] == cert["ast_sha256"]
    assert manifest["checker_claimed_effects"] == []
    assert len(left["binding_sha256"]) == 64
    assert left["work"]["persistent_identity_bytes"] > 0
    assert left["work"]["binding_sha256_input_bytes"] == left["work"]["persistent_identity_bytes"]


def test_bound_evaluation_never_calls_arbitrary_host_checker():
    calls = []
    spec = _spec(host_calls=calls)
    cert = _pass_cert()
    binding = B.issue_binding(spec, cert)
    status, work = B.evaluate_bound(spec, cert, binding, {"answer": 42})
    assert status is SV.Status.PASS
    assert calls == []
    assert work["host_checker_calls"] == 0
    assert work["execution_mode"] == "PURE_CHECKER_DSL_ONLY"
    assert work["checker_work"]["ast_nodes"] == 1


def test_replay_rejects_operator_metadata_drift():
    cert = _pass_cert()
    original = _spec(version="1")
    binding = B.issue_binding(original, cert)
    changed = _spec(version="2")
    with pytest.raises(B.BindingRejected, match="binding drift"):
        B.verify_binding(changed, cert, binding)


def test_replay_rejects_valid_checker_ast_replacement():
    spec = _spec()
    pass_cert = _pass_cert()
    binding = B.issue_binding(spec, pass_cert)
    fail_cert = PC.issue_certificate({"op": "STATUS", "status": "FAIL"})
    assert fail_cert["ast_sha256"] != pass_cert["ast_sha256"]
    with pytest.raises(B.BindingRejected, match="binding drift"):
        B.verify_binding(spec, fail_cert, binding)


def test_certificate_tamper_language_drift_and_effect_drift_fail_closed():
    spec = _spec()
    cert = _pass_cert()

    tampered_ast = copy.deepcopy(cert)
    tampered_ast["ast"]["status"] = "FAIL"
    with pytest.raises(PC.CertificateRejected):
        B.issue_binding(spec, tampered_ast)

    language_drift = copy.deepcopy(cert)
    language_drift["language_version"] = "future-language"
    with pytest.raises(PC.CertificateRejected):
        B.issue_binding(spec, language_drift)

    effect_drift = copy.deepcopy(cert)
    effect_drift["claimed_effects"] = ["host-write"]
    with pytest.raises(PC.CertificateRejected):
        B.issue_binding(spec, effect_drift)


def test_binding_digest_tamper_fails_closed():
    spec = _spec()
    cert = _pass_cert()
    binding = B.issue_binding(spec, cert)
    tampered = copy.deepcopy(binding)
    tampered["binding_sha256"] = "0" * 64
    with pytest.raises(B.BindingRejected, match="binding drift"):
        B.verify_binding(spec, cert, tampered)


def test_pure_migration_refuses_declared_effectful_operator():
    spec = _spec(expected_effects=("host-write",))
    with pytest.raises(B.BindingRejected, match="declaring checker effects"):
        B.issue_binding(spec, _pass_cert())


def test_demo_receipt_keeps_production_claims_blocked_and_cost_explicit():
    receipt = B.demo_receipt()
    assert all(receipt["controls"].values())
    assert receipt["result"] == "PASS"
    assert receipt["host_checker_observed_calls"] == []
    assert receipt["terminal"] == "PROSPECTIVE_PURE_CHECKER_BINDING_CONSTRUCTIVE_PARENT_ONLY"
    assert any("No production runtime integration" in item for item in receipt["claim_boundary"])
    assert any("No ML" in item for item in receipt["claim_boundary"])
