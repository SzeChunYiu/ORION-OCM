"""Prospective content-bound pure-checker replay identity for R0A.

Research-only.  This does not modify or authorize the production runtime.  It
constructs the manifest shape a future migration would need: current operator
semantic metadata plus a recomputable pure-checker certificate identity.  Replay
verification fails closed on operator, checker AST, language, certificate, or
binding drift.

The bound evaluator intentionally executes the restricted checker DSL directly;
it never calls ``OperatorSpec.checker``.  This is the key distinction from merely
attaching a certificate beside an arbitrary host callback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import pure_checker_contract as PC
from ocm.operators.registry import OperatorSpec
from ocm.runtime.ocm_runtime import _operator_manifest


SCHEMA = "ocm.r0a.pure-checker.operator-binding.v1"
ALGORITHM = "sha256-canonical-json-v1"
EXECUTION_MODE = "PURE_CHECKER_DSL_ONLY"
IMPLEMENTATION_IDENTITY = "PURE_CHECKER_CERTIFIED"


class BindingRejected(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _certificate_identity(cert: Mapping[str, Any]) -> dict[str, Any]:
    checked = PC.verify_certificate(cert)
    if checked["claimed_effects"] != []:
        raise BindingRejected("pure checker must claim an empty effect set")
    return {
        "checker_certificate_schema": checked["schema"],
        "checker_language_version": checked["language_version"],
        "checker_ast_sha256": checked["ast_sha256"],
        "checker_claimed_effects": list(checked["claimed_effects"]),
    }


def _identity(spec: OperatorSpec, cert: Mapping[str, Any]) -> dict[str, Any]:
    current = _operator_manifest(spec)
    if not current.get("checker_required"):
        raise BindingRejected("prospective migration requires a checker-bearing operator")
    if list(current.get("expected_effects", [])):
        raise BindingRejected("pure migration refuses an operator declaring checker effects")
    checker = _certificate_identity(cert)
    prospective = dict(current)
    prospective["implementation_identity"] = IMPLEMENTATION_IDENTITY
    prospective["checker_execution_mode"] = EXECUTION_MODE
    prospective.update(checker)
    return {
        "schema": SCHEMA,
        "binding_algorithm": ALGORITHM,
        "operator_manifest": prospective,
    }


def issue_binding(spec: OperatorSpec, cert: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic content binding and explicit raw accounting."""
    checked = PC.verify_certificate(cert)
    identity = _identity(spec, checked)
    payload = _canonical(identity)
    digest = hashlib.sha256(payload).hexdigest()
    return {
        **identity,
        "binding_sha256": digest,
        "work": {
            # verify_certificate regenerates and hashes the checker AST once;
            # this function then hashes the canonical operator+checker identity once.
            "certificate_validation_ast_nodes": checked["node_count"],
            "certificate_validation_literal_bytes": checked["literal_bytes"],
            "certificate_sha256_recomputations": 1,
            "binding_sha256_recomputations": 1,
            "binding_sha256_input_bytes": len(payload),
            "persistent_identity_bytes": len(payload),
        },
    }


def verify_binding(
    spec: OperatorSpec,
    cert: Mapping[str, Any],
    binding: Mapping[str, Any],
) -> dict[str, Any]:
    if type(binding) is not dict:
        raise BindingRejected("binding must be a plain dict")
    expected = issue_binding(spec, cert)
    if binding != expected:
        raise BindingRejected("operator/checker binding drift")
    return expected


def evaluate_bound(
    spec: OperatorSpec,
    cert: Mapping[str, Any],
    binding: Mapping[str, Any],
    candidate: Any,
):
    """Verify replay identity, then execute only the bounded DSL checker."""
    verified = verify_binding(spec, cert, binding)
    status, checker_work = PC.evaluate(cert, candidate)
    return status, {
        "binding_work": dict(verified["work"]),
        "checker_work": checker_work,
        "host_checker_calls": 0,
        "execution_mode": EXECUTION_MODE,
    }


def demo_receipt() -> dict[str, Any]:
    """Small exact control used by CI; not an operational population."""
    from ocm.operators.registry import BackendKind
    from ocm.runtime import solve as SV

    host_calls: list[str] = []

    def backend(*_args):
        return {"answer": 42}

    def hostile_host_checker(_candidate):
        host_calls.append("called")
        return SV.Status.FAIL

    spec = OperatorSpec(
        operator_id="prospective-bound-demo",
        version="1",
        kind=BackendKind.PROGRAMMATIC,
        backend=backend,
        input_atoms=("fact",),
        output_type="claim",
        checker=hostile_host_checker,
        expected_effects=(),
    )
    cert = PC.issue_certificate({"op": "STATUS", "status": "PASS"})
    binding = issue_binding(spec, cert)
    status, work = evaluate_bound(spec, cert, binding, {"answer": 42})
    return {
        "study": "R0A_PROSPECTIVE_PURE_CHECKER_BINDING_DEMO_V1",
        "authority": "research-only prospective replay-binding control",
        "binding": binding,
        "result": status.value,
        "work": work,
        "host_checker_observed_calls": list(host_calls),
        "controls": {
            "bound_execution_uses_dsl_not_host_callback": (
                status is SV.Status.PASS and host_calls == [] and work["host_checker_calls"] == 0
            ),
            "content_bound_checker_identity_present": (
                len(binding["operator_manifest"]["checker_ast_sha256"]) == 64
                and binding["operator_manifest"]["checker_claimed_effects"] == []
            ),
            "binding_cost_is_nonzero_and_explicit": (
                binding["work"]["binding_sha256_input_bytes"] > 0
                and binding["work"]["certificate_validation_ast_nodes"] == 1
            ),
        },
        "claim_boundary": [
            "No production runtime integration or early-exit authorization.",
            "The arbitrary host checker is deliberately present but never executed by the bound path.",
            "This proves a fail-closed identity mechanism can be constructed, not that a production checker population is migratable.",
            "Binding validation/storage work is explicit and must be charged in any adoption study.",
            "No ML or learned routing is authorized.",
        ],
        "terminal": "PROSPECTIVE_PURE_CHECKER_BINDING_CONSTRUCTIVE_PARENT_ONLY",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args(argv)
    receipt = demo_receipt()
    if not all(receipt["controls"].values()):
        raise SystemExit("prospective checker-binding control failure")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if args.github_notice:
        work = receipt["binding"]["work"]
        print(
            "::notice title=R0A prospective checker binding::"
            f"identity_bytes={work['persistent_identity_bytes']}; "
            f"host_checker_calls={receipt['work']['host_checker_calls']}; "
            f"terminal={receipt['terminal']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
