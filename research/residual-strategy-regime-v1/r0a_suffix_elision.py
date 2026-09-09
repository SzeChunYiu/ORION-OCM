"""R0A source-derived suffix-elision hostile audit; no production change.

This module executes the current check_stage against two controls:

1. a later checker mutates the real OCMRuntime after an earlier PASS.  The
   incumbent callback guard must invalidate the earlier PASS; checking only the
   first candidate must diverge.  This is the lifecycle counterexample.
2. pure PASS tail checkers preserve the selected first candidate, but a prefix
   CHECK record differs from the incumbent full CHECK record.  This is the
   literal trace-equivalence counterexample.

It also corrects the frozen R0 accounting using the old instrument's own
per-candidate charging rule.  No learned policy is used or authorized.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import fields
from pathlib import Path

from ocm.kso.space import Atom, Hyperedge
from ocm.kso.surprise import SurpriseModel
from ocm.kso.warrant import WarrantProfile as WP
from ocm.operators.registry import BackendKind, OperatorSpec as RegistryOperatorSpec
from ocm.runtime import solve as SV
from ocm.runtime.ocm_runtime import OCMRuntime, _operator_manifest


FROZEN_R0 = {
    "branch": "claude/machine-epistemics-cognitive-ladder-69lo4d",
    "commit": "47d706ab42d8528060356c7d4a267e1454ce9e7a",
    "instrument_blob": "2af3f979932bbe0156970f619bbfe28e217008fe",
    "derived_receipt_blob": "2de217fda11b00708ad143ebe64b5a1ff6fef90d",
    "queries": 96,
    "answering_queries": 44,
    "multi_candidate_answers_with_two_passes": 20,
    "first_pass_index_zero_for_all_answers": True,
    "reported_tail_composition_work": 33,
    "reported_tail_verification_calls": 40,
}


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def _runtime(root):
    rt = OCMRuntime(root, config=SV.SolveConfig(surprise_model=SurpriseModel.PROPAGATED))
    rt.admit_object(Atom("q", "goal", quarantined=True), (), "INSTRUCTION")
    rt.admit_object(
        Atom("fact", "claim", WP.of({"support"})),
        (Hyperedge("qf", ("q",), ("fact",), "SUPPORT"),),
        "INSTRUCTION",
    )
    return rt


def _guard(rt):
    """The actual OCMRuntime callback checkpoint relation, isolated for audit."""
    def changed(before, after):
        return (
            any(a is not b for a, b in zip(before[0], after[0], strict=True))
            or before[1:] != after[1:]
        )

    def guarded(callback, *args):
        before = rt._solve_callback_checkpoint()
        try:
            return callback(*args)
        finally:
            after = rt._solve_callback_checkpoint()
            if changed(before, after):
                raise SV.CallbackStateChanged("RUNTIME_STATE_CHANGED_DURING_CALLBACK")

    return guarded


def _hostile_candidates(rt, calls):
    def checker(name):
        def run(_out):
            calls.append(name)
            if name == "second":
                rt.revoke(("support",))
            return SV.Status.PASS
        return run

    warrant = WP.of({"support"})
    return tuple(
        (
            SV.OperatorSpec(
                name,
                "1",
                lambda *args: {"answer": 42},
                ("fact",),
                checker=checker(name),
            ),
            {"answer": 42},
            warrant,
        )
        for name in ("first", "second", "third")
    )


def hostile_runtime_mutation_audit(root):
    """Compare full incumbent CHECK to first-PASS prefix on fresh runtimes."""
    baseline_root = Path(root) / "baseline"
    prefix_root = Path(root) / "prefix"

    baseline_rt = _runtime(baseline_root)
    baseline_calls = []
    baseline_candidates = _hostile_candidates(baseline_rt, baseline_calls)
    baseline_stage, baseline_checked = SV.check_stage(
        baseline_candidates,
        baseline_rt.state.revoked,
        callback_guard=_guard(baseline_rt),
    )

    prefix_rt = _runtime(prefix_root)
    prefix_calls = []
    prefix_candidates = _hostile_candidates(prefix_rt, prefix_calls)
    prefix_stage, prefix_checked = SV.check_stage(
        prefix_candidates[:1],
        prefix_rt.state.revoked,
        callback_guard=_guard(prefix_rt),
    )

    return {
        "baseline": {
            "calls": baseline_calls,
            "check_status": baseline_stage.status.value,
            "reason": baseline_stage.reason,
            "verdicts": baseline_stage.payload.get("verdicts", {}),
            "checked": len(baseline_checked),
            "support_revoked": "support" in baseline_rt.state.revoked,
        },
        "first_pass_prefix": {
            "calls": prefix_calls,
            "check_status": prefix_stage.status.value,
            "reason": prefix_stage.reason,
            "verdicts": prefix_stage.payload.get("verdicts", {}),
            "checked": len(prefix_checked),
            "support_revoked": "support" in prefix_rt.state.revoked,
        },
        "protected_divergence": (
            baseline_stage.status is not prefix_stage.status
            and ("support" in baseline_rt.state.revoked)
            != ("support" in prefix_rt.state.revoked)
        ),
    }


def pure_trace_audit():
    calls = []

    def checker(name, verdict):
        def run(_out):
            calls.append(name)
            return verdict
        return run

    candidates = (
        (
            SV.OperatorSpec("first", "1", lambda *a: {"answer": 42}, (),
                            checker=checker("first", SV.Status.PASS)),
            {"answer": 42}, WP.one(),
        ),
        (
            SV.OperatorSpec("second", "1", lambda *a: {"answer": 43}, (),
                            checker=checker("second", SV.Status.PASS)),
            {"answer": 43}, WP.one(),
        ),
        (
            SV.OperatorSpec("third", "1", lambda *a: {"answer": 44}, (),
                            checker=checker("third", SV.Status.FAIL)),
            {"answer": 44}, WP.one(),
        ),
    )

    full_stage, full_checked = SV.check_stage(candidates, ())
    full_calls = tuple(calls)
    calls.clear()
    prefix_stage, prefix_checked = SV.check_stage(candidates[:1], ())
    prefix_calls = tuple(calls)

    def first_pass(checked):
        return next(op.operator_id for op, _, _, verdict in checked if verdict is SV.Status.PASS)

    same_selected = first_pass(full_checked) == first_pass(prefix_checked) == "first"
    trace_equal = (
        full_stage.object_ids == prefix_stage.object_ids
        and full_stage.payload == prefix_stage.payload
        and full_stage.resources == prefix_stage.resources
    )
    return {
        "full": {
            "calls": list(full_calls),
            "status": full_stage.status.value,
            "object_ids": list(full_stage.object_ids),
            "verdicts": full_stage.payload["verdicts"],
            "verification_calls": full_stage.resources.verification_calls,
        },
        "prefix": {
            "calls": list(prefix_calls),
            "status": prefix_stage.status.value,
            "object_ids": list(prefix_stage.object_ids),
            "verdicts": prefix_stage.payload["verdicts"],
            "verification_calls": prefix_stage.resources.verification_calls,
        },
        "same_selected_first_pass": same_selected,
        "literal_check_trace_equal": trace_equal,
    }


def current_purity_contract_audit():
    runtime_fields = {field.name for field in fields(SV.OperatorSpec)}
    registry_op = RegistryOperatorSpec(
        "audit",
        "1",
        BackendKind.PROGRAMMATIC,
        lambda *_: {"answer": 1},
        (),
        checker=lambda _out: "PASS",
    )
    manifest = _operator_manifest(registry_op)
    purity_keys = {
        "checker_pure", "checker_effects", "checker_effect_certificate",
        "checker_proof", "checker_capabilities",
    }
    return {
        "runtime_operator_fields": sorted(runtime_fields),
        "runtime_has_checker_callable": "checker" in runtime_fields,
        "runtime_has_purity_metadata": bool(runtime_fields & purity_keys),
        "manifest_checker_required": manifest.get("checker_required"),
        "manifest_implementation_identity": manifest.get("implementation_identity"),
        "manifest_has_purity_metadata": bool(set(manifest) & purity_keys),
        "expected_effects_is_not_checked_as_checker_purity_certificate": True,
    }


def corrected_r0_accounting():
    # The frozen instrument assigns each checked candidate one compose-side
    # verification unit and then increments it by one at check_stage.
    reported = FROZEN_R0["reported_tail_verification_calls"]
    if reported % 2:
        raise ValueError("frozen tail verification count violates instrument charging rule")
    tail_candidates = reported // 2
    if tail_candidates != FROZEN_R0["multi_candidate_answers_with_two_passes"]:
        raise ValueError("frozen aggregate no longer matches two-PASS tail population")
    return {
        "frozen_r0": dict(FROZEN_R0),
        "tail_candidates": tail_candidates,
        "compose_side_verification_already_spent": tail_candidates,
        "check_stage_verification_units_potentially_removed_by_break": tail_candidates,
        "composition_work_potentially_removed_by_check_stage_break": 0,
        "reported_tail_composition_work_already_spent": FROZEN_R0["reported_tail_composition_work"],
        "tail_candidates_are_passes_and_therefore_have_executable_checkers": True,
        "tail_checker_calls_authorized_for_omission_under_current_unrestricted_contract": 0,
    }


def build_report(root=None):
    if root is None:
        with tempfile.TemporaryDirectory(prefix="r0a-suffix-") as tmp:
            hostile = hostile_runtime_mutation_audit(tmp)
    else:
        hostile = hostile_runtime_mutation_audit(root)
    pure = pure_trace_audit()
    purity = current_purity_contract_audit()
    accounting = corrected_r0_accounting()

    controls = {
        "hostile_full_check_fails_closed": (
            hostile["baseline"]["check_status"] == SV.Status.CANNOT_CHECK.value
            and hostile["baseline"]["support_revoked"]
        ),
        "hostile_prefix_misses_state_change": (
            hostile["first_pass_prefix"]["check_status"] == SV.Status.PASS.value
            and not hostile["first_pass_prefix"]["support_revoked"]
        ),
        "hostile_protected_divergence": hostile["protected_divergence"],
        "pure_prefix_preserves_selected_answer_candidate": pure["same_selected_first_pass"],
        "pure_prefix_changes_literal_check_trace": not pure["literal_check_trace_equal"],
        "no_current_checker_purity_certificate": (
            not purity["runtime_has_purity_metadata"]
            and not purity["manifest_has_purity_metadata"]
            and purity["manifest_implementation_identity"] == "HOST_SUPPLIED_UNVERIFIED"
        ),
        "old_40_corrects_to_20_check_units": (
            accounting["check_stage_verification_units_potentially_removed_by_break"] == 20
        ),
        "check_break_cannot_remove_composition_work": (
            accounting["composition_work_potentially_removed_by_check_stage_break"] == 0
        ),
    }
    all_controls = all(controls.values())
    terminal = (
        "EARLY_EXIT_OUTPUT_ONLY_NOT_LIFECYCLE_EQUIVALENT"
        if all_controls
        else "R0A_SUFFIX_ELISION_AUDIT_CONTROL_FAILURE"
    )
    return {
        "schema": "ocm.residual-strategy-regime.r0a.suffix-elision.audit.v1",
        "study": "Current-contract first-PASS suffix-elision audit; no ML",
        "hostile_runtime_mutation": hostile,
        "pure_trace_control": pure,
        "current_purity_contract": purity,
        "corrected_r0_accounting": accounting,
        "controls": controls,
        "claim_boundary": {
            "answer_only_prefix_equivalence_under_effect_free_tail": True,
            "unrestricted_host_checker_elision_safe": False,
            "literal_current_check_trace_equivalent": False,
            "production_early_exit_authorized": False,
            "compose_check_interleaving_authorized": False,
            "checker_effect_certificate_required": True,
            "backend_effect_certificate_required_to_skip_backend_tail": True,
            "ml_authorized": False,
        },
        "subterminal": "CHECKER_EFFECT_CERTIFICATE_REQUIRED_R0A",
        "terminal": terminal,
    }


def _notice(report):
    accounting = report["corrected_r0_accounting"]
    return {
        "terminal": report["terminal"],
        "subterminal": report["subterminal"],
        "hostile": report["hostile_runtime_mutation"],
        "corrected_old_r0": {
            "reported_tail_verification_calls": accounting["frozen_r0"]["reported_tail_verification_calls"],
            "actual_check_stage_units_max": accounting["check_stage_verification_units_potentially_removed_by_break"],
            "composition_work_removed_by_check_break": accounting["composition_work_potentially_removed_by_check_stage_break"],
            "currently_authorized_tail_checker_omissions": accounting["tail_checker_calls_authorized_for_omission_under_current_unrestricted_contract"],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    report = build_report()
    _write_json(args.out, report)
    rendered = json.dumps(_notice(report), sort_keys=True, separators=(",", ":"))
    if args.github_notice:
        print(f"::notice title=R0A suffix elision audit::{rendered}")
    else:
        print(rendered)
    if report["terminal"] != "EARLY_EXIT_OUTPUT_ONLY_NOT_LIFECYCLE_EQUIVALENT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
