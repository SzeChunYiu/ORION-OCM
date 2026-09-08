from __future__ import annotations

import copy

import pytest

import pure_checker_contract as P
from ocm.runtime import solve as SV


def _program():
    return {
        "op": "IF",
        "predicate": {
            "op": "AND",
            "left": {"op": "HAS", "path": ["answer"]},
            "right": {"op": "TYPE", "path": ["answer"], "kind": "int"},
        },
        "then": {"op": "STATUS", "status": "PASS"},
        "else": {"op": "STATUS", "status": "CANNOT_CHECK"},
    }


def test_certificate_is_recomputed_and_effect_set_is_empty():
    cert = P.issue_certificate(_program())
    assert cert["schema"] == P.SCHEMA
    assert cert["language_version"] == P.LANGUAGE
    assert cert["claimed_effects"] == []
    # One node per opcode: IF + AND + HAS + TYPE + two STATUS leaves.
    assert cert["node_count"] == 6
    assert cert["max_path_length"] == 1
    assert P.verify_certificate(cert) == cert


def test_tampered_certificate_is_rejected():
    cert = P.issue_certificate(_program())
    bad = copy.deepcopy(cert)
    bad["ast_sha256"] = "0" * 64
    with pytest.raises(P.CertificateRejected):
        P.verify_certificate(bad)


def test_syntax_sort_is_checked_at_admission():
    with pytest.raises(P.CertificateRejected):
        P.issue_certificate({"op": "TRUE"})
    with pytest.raises(P.CertificateRejected):
        P.issue_certificate({
            "op": "IF",
            "predicate": {"op": "STATUS", "status": "PASS"},
            "then": {"op": "STATUS", "status": "PASS"},
            "else": {"op": "STATUS", "status": "FAIL"},
        })
    with pytest.raises(P.CertificateRejected):
        P.issue_certificate({
            "op": "IF",
            "predicate": {"op": "TRUE"},
            "then": {"op": "HAS", "path": ["answer"]},
            "else": {"op": "STATUS", "status": "FAIL"},
        })


def test_evaluation_uses_only_detached_candidate_and_returns_registered_status():
    cert = P.issue_certificate(_program())
    status, work = P.evaluate(cert, {"answer": 42, "other": [1, 2]})
    assert status is SV.Status.PASS
    assert work["ast_nodes"] > 0 and work["path_steps"] == 2
    status, _ = P.evaluate(cert, {"answer": "42"})
    assert status is SV.Status.CANNOT_CHECK
    status, _ = P.evaluate(cert, {})
    assert status is SV.Status.CANNOT_CHECK


def test_bool_does_not_satisfy_int_type_exactness():
    cert = P.issue_certificate({
        "op": "IF",
        "predicate": {"op": "TYPE", "path": ["answer"], "kind": "int"},
        "then": {"op": "STATUS", "status": "PASS"},
        "else": {"op": "STATUS", "status": "FAIL"},
    })
    assert P.evaluate(cert, {"answer": 1})[0] is SV.Status.PASS
    assert P.evaluate(cert, {"answer": True})[0] is SV.Status.FAIL


def test_candidate_outside_detached_data_grammar_is_rejected():
    cert = P.issue_certificate({"op": "STATUS", "status": "PASS"})
    with pytest.raises(P.CertificateRejected):
        P.evaluate(cert, {"answer": object()})


def test_checker_language_has_no_callback_or_runtime_escape_opcode():
    for opcode in ("CALL", "IMPORT", "EVAL", "EXEC", "SET", "WRITE", "REVOKE"):
        with pytest.raises(P.CertificateRejected):
            P.issue_certificate({"op": opcode})


def test_break_even_horizon_charges_fixed_and_per_use_costs():
    assert P.break_even_horizon(10, 5, 4, 1) == 6  # 6*4 > 15 + 6*1
    assert P.break_even_horizon(0, 0, 1, 0) == 1
    assert P.break_even_horizon(1, 1, 1, 1) is None
    assert P.break_even_horizon(1, 1, 0.5, 1) is None
