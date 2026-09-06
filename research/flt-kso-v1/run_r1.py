#!/usr/bin/env python3
"""Execute the preregistered R1 native composition and, when available, exact Lean kernel check."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

from flt_contract import (
    LEAN_VERSION,
    R1_CHALLENGE_ID,
    R1_MAX_CHECKER_CALLS,
    R1_MAX_EXPANSIONS,
    SOURCE_BASE,
    Terminal,
    base_receipt,
    sha256_text,
)
from native_prop import r1_backend_output
from sealer import sanitized_environment, scan_generated_lean


def lean_version(lean: str) -> str | None:
    cp = subprocess.run([lean, "--version"], capture_output=True, text=True, env=sanitized_environment(), timeout=10)
    text = cp.stdout + cp.stderr
    m = re.search(r"Lean \(version ([0-9.]+)", text)
    return m.group(1) if m else None


def check_lean_source(source: str, *, lean: str | None = None) -> dict[str, Any]:
    scan_generated_lean(source)
    lean = lean or shutil.which("lean")
    if not lean:
        return {"terminal": Terminal.CANNOT_CHECK_PINNED_FLT_ENVIRONMENT.value, "checker_calls": 0, "reason": "lean-not-found"}
    version = lean_version(lean)
    if version != LEAN_VERSION:
        return {
            "terminal": Terminal.CHECKER_OR_ENVIRONMENT_MISMATCH.value,
            "checker_calls": 0,
            "observed_lean_version": version,
            "expected_lean_version": LEAN_VERSION,
        }
    with tempfile.TemporaryDirectory(prefix="flt-kso-r1-") as td:
        path = Path(td) / "R1.lean"
        path.write_text(source, encoding="utf-8")
        started = time.perf_counter()
        cp = subprocess.run([lean, str(path)], capture_output=True, text=True, env=sanitized_environment(), timeout=30)
        wall = time.perf_counter() - started
        stdout, stderr = cp.stdout, cp.stderr
        if cp.returncode != 0:
            return {"terminal": "LEAN_CHECK_FAILED", "checker_calls": 1, "returncode": cp.returncode, "stdout": stdout, "stderr": stderr, "wall_seconds": wall}
        axiom_text = stdout + stderr
        axiom_clear = "does not depend on any axioms" in axiom_text or "depends on axioms: []" in axiom_text
        if not axiom_clear:
            return {"terminal": "AXIOM_REPORT_NOT_CLEAR", "checker_calls": 1, "returncode": cp.returncode, "stdout": stdout, "stderr": stderr, "wall_seconds": wall}
        return {
            "terminal": Terminal.UNSEEN_COMPOSITION_SUPPORTED.value,
            "checker_calls": 1,
            "returncode": 0,
            "stdout": stdout,
            "stderr": stderr,
            "wall_seconds": wall,
            "lean_version": version,
            "axiom_clear": True,
            "checker_evidence": "lean-kernel:" + sha256_text(source + "\n" + axiom_text),
        }


def run(*, source_sha: str, lean: str | None = None, max_expansions: int = R1_MAX_EXPANSIONS) -> dict[str, Any]:
    from ocm.kso.warrant import Liveness
    from ocm.operators.indexed_registry import IndexedOperatorRegistry
    from theorem_kso import admit_checked_proof, compose_proof_candidate, empty_space, open_obligation, proof_operator
    from flt_contract import EnvironmentIdentity, R1_STATEMENT

    receipt = base_receipt(source_sha=source_sha, arm="OCM_NATIVE", challenge_id=R1_CHALLENGE_ID)
    environment = EnvironmentIdentity()
    goal = open_obligation(theorem_name="r1_prop_chain_001", statement=R1_STATEMENT, environment=environment)
    ks = empty_space().with_atoms(goal)
    before_digest = ks.digest()

    def backend(_ks, context):
        return r1_backend_output(max_expansions=int(context["max_expansions"]))

    op = proof_operator(goal_atom_id=goal.atom_id, backend=backend)
    registry = IndexedOperatorRegistry()
    registry_key = registry.register(op)
    candidate_keys = registry.candidate_keys(())
    applicable = registry.applicable(ks, ())
    if [x.fingerprint for x in applicable] != [op.fingerprint]:
        raise RuntimeError("native proof operator did not pass production applicability boundary")
    output = applicable[0].backend(ks, {"max_expansions": max_expansions, "goal_atom_id": goal.atom_id})

    receipt.update({
        "information_regime": "R1",
        "allowed_operators": ["proof.intro", "proof.assumption", "proof.apply_local"],
        "search_budget": {"max_expansions": max_expansions, "max_checker_calls": R1_MAX_CHECKER_CALLS},
        "proof_state_expansions": output["proof_state_expansions"],
        "unique_proof_states": output["unique_proof_states"],
        "duplicate_states_avoided": output["duplicate_states_avoided"],
        "operator_candidates_considered": output["operator_candidates_considered"],
        "search_events": output["search_events"],
        "search_terminal": output["search_terminal"],
        "kso_before_digest": before_digest,
        "kso_before_resources": ks.resource_counts(),
        "operator_registry_key": registry_key,
        "operator_index_candidates": list(candidate_keys),
        "operator_index_stats": registry.index_stats(),
        "goal_liveness_before_check": goal.liveness(()).value,
        "mathlib_loaded_for_r1": False,
        "checker_environment_scope": "LEAN_4_33_1_KERNEL_ONLY_R1",
        "active_subspace_claim": "NOT_TESTED_AT_R1",
    })
    if output["search_terminal"] != "CANDIDATE_CONSTRUCTED":
        receipt["terminal"] = Terminal.FAILED_UNDER_BUDGET.value if output["search_terminal"] == "FAILED_UNDER_BUDGET" else output["search_terminal"]
        receipt["checker_calls"] = 0
        return receipt

    source = str(output["proof_source"])
    receipt["proof_source"] = source
    receipt["proof_source_sha256"] = sha256_text(source)
    pending = compose_proof_candidate(ks, op, {"goal_atom_id": goal.atom_id, "source": source}, checker_evidence=None)
    if pending.liveness(()) is not Liveness.UNKNOWN:
        raise RuntimeError("unchecked proof candidate was promoted above UNKNOWN")
    receipt["candidate_liveness_before_check"] = pending.liveness(()).value

    parent_output = r1_backend_output(max_expansions=max_expansions)
    if parent_output.get("proof_source") != source:
        raise RuntimeError("matched parent changed the proof grammar/trajectory")

    native_check = check_lean_source(source, lean=lean)
    parent_check = check_lean_source(str(parent_output["proof_source"]), lean=lean)
    checker_calls = int(native_check.get("checker_calls", 0)) + int(parent_check.get("checker_calls", 0))
    if checker_calls > R1_MAX_CHECKER_CALLS:
        raise RuntimeError("checker-call budget violated")
    receipt["checker_calls"] = checker_calls
    receipt["checker"] = native_check
    receipt["matched_parent"] = {
        "same_operator_grammar": True,
        "same_search_budget": True,
        "same_checker": True,
        "proof_state_expansions": parent_output["proof_state_expansions"],
        "operator_candidates_considered": parent_output["operator_candidates_considered"],
        "proof_source_sha256": sha256_text(str(parent_output["proof_source"])),
        "checker": parent_check,
    }

    if native_check["terminal"] != Terminal.UNSEEN_COMPOSITION_SUPPORTED.value:
        receipt["terminal"] = native_check["terminal"]
        receipt["comparison_terminal"] = (
            Terminal.PARENT_SUFFICIENT.value
            if parent_check["terminal"] == Terminal.UNSEEN_COMPOSITION_SUPPORTED.value
            else "COMPARISON_CANNOT_CHECK"
        )
        return receipt

    evidence = str(native_check["checker_evidence"])
    exact = compose_proof_candidate(ks, op, {"goal_atom_id": goal.atom_id, "source": source}, checker_evidence=evidence)
    if exact.liveness(()) is not Liveness.LIVE:
        raise RuntimeError("exact Lean checker evidence did not produce a LIVE proof candidate")
    admitted = admit_checked_proof(
        ks,
        goal=goal,
        candidate=exact,
        proof_source_hash=receipt["proof_source_sha256"],
        checker_evidence=evidence,
    )
    claim_id = goal.atom_id.replace("theorem-goal:", "theorem-claim:", 1)
    claim = admitted.atom_map()[claim_id]
    if claim.liveness(()) is not Liveness.LIVE:
        raise RuntimeError("checked theorem claim is not LIVE after admission")
    receipt.update({
        "candidate_liveness_after_check": exact.liveness(()).value,
        "claim_liveness_after_admission": claim.liveness(()).value,
        "kso_after_digest": admitted.digest(),
        "kso_after_resources": admitted.resource_counts(),
        "terminal": Terminal.UNSEEN_COMPOSITION_SUPPORTED.value,
        "comparison_terminal": (
            Terminal.PARENT_SUFFICIENT.value
            if parent_check["terminal"] == Terminal.UNSEEN_COMPOSITION_SUPPORTED.value
            else "PARENT_DID_NOT_MATCH_NATIVE_SUCCESS"
        ),
        "ocm_residual_claim": "NONE_AT_R1",
    })
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", SOURCE_BASE))
    ap.add_argument("--lean")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--max-expansions", type=int, default=R1_MAX_EXPANSIONS)
    args = ap.parse_args()
    receipt = run(source_sha=args.source_sha, lean=args.lean, max_expansions=args.max_expansions)
    text = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    terminal = receipt["terminal"]
    return 0 if terminal in {Terminal.UNSEEN_COMPOSITION_SUPPORTED.value, Terminal.CANNOT_CHECK_PINNED_FLT_ENVIRONMENT.value} else 1


if __name__ == "__main__":
    raise SystemExit(main())
