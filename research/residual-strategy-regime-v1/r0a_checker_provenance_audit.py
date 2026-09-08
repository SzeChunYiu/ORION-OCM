"""R0A checker-provenance hostile audit; research-only, no runtime change.

The frozen R0 opportunity counted post-first-PASS work but did not bind the
checker implementation that produced each verdict.  Current operator manifests
also declare only that a checker is required and label executable code as
HOST_SUPPLIED_UNVERIFIED.  This module makes the resulting identifiability gap
constructive: two checker implementations with different effects have exactly the
same persistent operator fingerprint/manifest.

The pure-checker calculus is used only as a prospective control.  Its certificate
*does* bind a language version and AST digest, showing the minimum kind of
content-bound identity a future migration can register before execution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pure_checker_contract as PC
import r0a_suffix_elision as R0A
from ocm.operators.registry import BackendKind, OperatorSpec
from ocm.runtime.ocm_runtime import _operator_manifest


FROZEN_INSTRUMENT_BLOB = "2af3f979932bbe0156970f619bbfe28e217008fe"
FROZEN_RECEIPT_BLOB = "2de217fda11b00708ad143ebe64b5a1ff6fef90d"
FROZEN_CANDIDATE_RECORD_FIELDS = (
    "operator_id",
    "input_atoms",
    "verdict",
    "composition_work",
    "verification_calls",
)
PROSPECTIVE_BINDING_FIELDS = (
    "checker_certificate_schema",
    "checker_language_version",
    "checker_ast_sha256",
    "checker_claimed_effects",
)
TERMINAL = "CHECKER_PROVENANCE_INSUFFICIENT_R0A"


def _backend(*_args, **_kwargs):
    return {"answer": 42}


def manifest_collision() -> dict[str, Any]:
    """Two effect-distinct checkers that current persistence cannot distinguish."""
    effects: list[str] = []

    def pure_checker(_candidate):
        return "PASS"

    def effectful_checker(_candidate):
        effects.append("host_effect")
        return "PASS"

    common = dict(
        operator_id="same",
        version="1",
        kind=BackendKind.PROGRAMMATIC,
        backend=_backend,
        input_atoms=("fact",),
        output_type="claim",
        expected_effects=(),  # a declaration can be incomplete; it is not a code proof
    )
    pure = OperatorSpec(**common, checker=pure_checker)
    effectful = OperatorSpec(**common, checker=effectful_checker)

    pure_manifest = _operator_manifest(pure)
    effectful_manifest = _operator_manifest(effectful)
    before = list(effects)
    pure_result = pure.checker({"answer": 42}) if pure.checker is not None else None
    after_pure = list(effects)
    effectful_result = effectful.checker({"answer": 42}) if effectful.checker is not None else None
    after_effectful = list(effects)

    return {
        "same_operator_fingerprint": pure.fingerprint == effectful.fingerprint,
        "same_serialized_operator_metadata": pure.as_dict() == effectful.as_dict(),
        "same_persistent_runtime_manifest": pure_manifest == effectful_manifest,
        "manifest": pure_manifest,
        "checker_results_equal": pure_result == effectful_result == "PASS",
        "effects_before": before,
        "effects_after_pure": after_pure,
        "effects_after_effectful": after_effectful,
        "effect_semantics_differ": after_pure == before and after_effectful != after_pure,
    }


def prospective_binding(certificate: dict[str, Any]) -> dict[str, Any]:
    cert = PC.verify_certificate(certificate)
    return {
        "checker_certificate_schema": cert["schema"],
        "checker_language_version": cert["language_version"],
        "checker_ast_sha256": cert["ast_sha256"],
        "checker_claimed_effects": list(cert["claimed_effects"]),
    }


def pure_certificate_control() -> dict[str, Any]:
    pass_cert = PC.issue_certificate({"op": "STATUS", "status": "PASS"})
    fail_cert = PC.issue_certificate({"op": "STATUS", "status": "FAIL"})
    pass_binding = prospective_binding(pass_cert)
    fail_binding = prospective_binding(fail_cert)
    return {
        "pass_binding": pass_binding,
        "fail_binding": fail_binding,
        "same_schema": pass_binding["checker_certificate_schema"] == fail_binding["checker_certificate_schema"],
        "same_language": pass_binding["checker_language_version"] == fail_binding["checker_language_version"],
        "different_ast_identity": pass_binding["checker_ast_sha256"] != fail_binding["checker_ast_sha256"],
        "effects_empty_by_construction": (
            pass_binding["checker_claimed_effects"] == []
            and fail_binding["checker_claimed_effects"] == []
        ),
    }


def build_report() -> dict[str, Any]:
    collision = manifest_collision()
    pure = pure_certificate_control()
    accounting = R0A.corrected_r0_accounting()
    current = R0A.current_purity_contract_audit()

    frozen_tail = accounting["check_stage_verification_units_potentially_removed_by_break"]
    controls = {
        "frozen_tail_is_twenty_actual_check_callbacks_max": frozen_tail == 20,
        "frozen_instrument_channel_did_not_record_checker_identity": not any(
            name in FROZEN_CANDIDATE_RECORD_FIELDS
            for name in (
                "checker_digest", "checker_ast_sha256", "checker_effect_certificate",
                "checker_language_version", "checker_implementation_identity",
            )
        ),
        "current_manifest_is_not_code_identity_proof": (
            current["manifest_implementation_identity"] == "HOST_SUPPLIED_UNVERIFIED"
        ),
        "effect_distinct_checkers_collide_under_current_manifest": (
            collision["same_operator_fingerprint"]
            and collision["same_serialized_operator_metadata"]
            and collision["same_persistent_runtime_manifest"]
            and collision["checker_results_equal"]
            and collision["effect_semantics_differ"]
        ),
        "prospective_pure_certificate_binds_checker_ast": (
            pure["same_schema"] and pure["same_language"]
            and pure["different_ast_identity"] and pure["effects_empty_by_construction"]
        ),
    }
    if not all(controls.values()):
        terminal = "R0A_CHECKER_PROVENANCE_AUDIT_CONTROL_FAILURE"
    else:
        terminal = TERMINAL

    return {
        "schema": "ocm.residual-strategy-regime.r0a.checker-provenance.audit.v1",
        "study": "R0A checker implementation/effect provenance identifiability audit",
        "authority": "research-only source-custodied hostile; no production migration",
        "source_custody": {
            "frozen_r0_branch": R0A.FROZEN_R0["branch"],
            "frozen_r0_commit": R0A.FROZEN_R0["commit"],
            "frozen_instrument_blob": FROZEN_INSTRUMENT_BLOB,
            "frozen_derived_receipt_blob": FROZEN_RECEIPT_BLOB,
            "instrument_candidate_record_fields": list(FROZEN_CANDIDATE_RECORD_FIELDS),
            "frozen_tail_check_callbacks_max": frozen_tail,
        },
        "current_manifest_collision": collision,
        "prospective_pure_certificate_control": pure,
        "required_prospective_manifest_binding": list(PROSPECTIVE_BINDING_FIELDS),
        "controls": controls,
        "findings": {
            "retrospective_tail_checker_purity_identifiable": False,
            "current_operator_identity_implies_checker_effect_identity": False,
            "pure_checker_calculus_has_content_bound_checker_identity": True,
            "production_manifest_binds_pure_checker_certificate": False,
        },
        "claim_boundary": {
            "production_early_exit_authorized": False,
            "frozen_twenty_callbacks_declared_pure": False,
            "host_checker_effects_inferable_from_PASS_verdict": False,
            "prospective_migration_required": True,
            "migration_must_bind_certificate_before_execution": True,
            "replay_must_reject_checker_binding_drift": True,
            "ml_authorized": False,
        },
        "next_experiment": (
            "Prospectively bind pure-checker certificate schema/language/AST digest/effects into "
            "operator manifest and replay identity, migrate a frozen checker population before "
            "observing savings, then rerun the CHECK-tail census under that restricted contract."
        ),
        "terminal": terminal,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.github_notice:
        print(
            "::notice title=R0A checker provenance::"
            f"tail={report['source_custody']['frozen_tail_check_callbacks_max']}; "
            f"manifest_collision={report['controls']['effect_distinct_checkers_collide_under_current_manifest']}; "
            f"terminal={report['terminal']}"
        )
    if report["terminal"] != TERMINAL:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
