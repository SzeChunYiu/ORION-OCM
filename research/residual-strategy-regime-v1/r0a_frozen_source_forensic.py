"""Forensic source census for the frozen R0 first-PASS tail opportunities.

This is deliberately weaker than a runtime certificate.  It reconstructs the
historical test fixtures from byte-identical source files at the frozen R0 commit
and shows that the 20 multi-PASS opportunities came from factories whose checkers
are trivial ``lambda ...: SV.Status.PASS`` expressions.  The result is a migration
*coverage upper bound* for that historical test donor, not production authority.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import r0a_suffix_elision as R0A


TERMINAL = "FROZEN_R0_TEST_TAILS_FORENSICALLY_PURE_NOT_RUNTIME_CERTIFIED"
FROZEN_COMMIT = "47d706ab42d8528060356c7d4a267e1454ce9e7a"

# These files are byte-identical between the frozen R0 commit and the current
# research branch.  Git blob identity is checked in CI before any AST claim.
SOURCES = {
    "tests/m2/test_navigation_serving_runtime.py": {
        "blob": "55224956133d7b3c2a5c1078d06998e4ed0bd3a2",
        "factory": "operators",
        "trivial_pass_checkers": 2,
        "opportunity_families": {
            "test_complete_solve_matches_dense_ranking_tie_and_resources": 4,
            "test_actual_runtime_records_path_revocation_and_restart": 3,
        },
    },
    "tests/m2/test_runtime_extraction_index.py": {
        "blob": "90397bb6fc68ab20fda182b0b9ab9fb3b38b6867",
        "factory": "_ops",
        "trivial_pass_checkers": 2,
        "opportunity_families": {
            "test_default_and_indexed_solve_preserve_all_semantic_trace_fields": 4,
            "test_actual_runtime_selected_path_forbids_incumbent_reaction_and_greedy": 1,
            "test_reused_index_reports_caller_build_without_recurring_query_charge": 2,
            "test_actual_runtime_revocation_and_reinstatement_reuse_same_snapshot": 2,
            "test_restart_requires_rebinding_index_to_replayed_space": 2,
        },
    },
    "tests/m2/test_solve_operator_index.py": {
        "blob": "dd354658b67f2307f1c9c3743eb8705d0c51de53",
        "factory": "op",
        "trivial_pass_checkers": 1,
        "opportunity_families": {
            "test_real_solve_keeps_first_passing_answer_and_checks_live_warrant": 2,
        },
    },
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def _attribute_name(node: ast.AST) -> str | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _factory(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            if not isinstance(node, ast.FunctionDef):
                raise RuntimeError(f"unexpected async factory {name}")
            return node
    raise RuntimeError(f"missing factory {name}")


def _trivial_pass_checkers(factory: ast.FunctionDef) -> int:
    count = 0
    for node in ast.walk(factory):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "checker" or not isinstance(keyword.value, ast.Lambda):
                continue
            if _attribute_name(keyword.value.body) == "SV.Status.PASS":
                count += 1
    return count


def inspect_source(path: Path, spec: dict[str, Any]) -> dict[str, Any]:
    raw = path.read_bytes()
    blob = _git_blob_sha(raw)
    tree = ast.parse(raw.decode("utf-8"), filename=str(path))
    factory = _factory(tree, spec["factory"])
    pass_checkers = _trivial_pass_checkers(factory)
    return {
        "git_blob_sha1": blob,
        "expected_git_blob_sha1": spec["blob"],
        "blob_matches_frozen": blob == spec["blob"],
        "factory": spec["factory"],
        "trivial_pass_checker_occurrences": pass_checkers,
        "expected_trivial_pass_checker_occurrences": spec["trivial_pass_checkers"],
        "factory_matches_registered_trivial_pass_shape": pass_checkers == spec["trivial_pass_checkers"],
        "opportunity_families": dict(spec["opportunity_families"]),
        "opportunities": sum(spec["opportunity_families"].values()),
    }


def build_report(root: Path | None = None) -> dict[str, Any]:
    root = _repo_root() if root is None else root
    files = {name: inspect_source(root / name, spec) for name, spec in SOURCES.items()}
    reconstructed = sum(row["opportunities"] for row in files.values())
    corrected = R0A.corrected_r0_accounting()["check_stage_verification_units_potentially_removed_by_break"]
    controls = {
        "all_source_blobs_match_frozen_commit": all(row["blob_matches_frozen"] for row in files.values()),
        "all_registered_factories_have_only_expected_trivial_pass_checkers": all(
            row["factory_matches_registered_trivial_pass_shape"] for row in files.values()
        ),
        "forensic_opportunity_total_matches_corrected_r0_tail": reconstructed == corrected == 20,
    }
    terminal = TERMINAL if all(controls.values()) else "R0A_FROZEN_SOURCE_FORENSIC_CONTROL_FAILURE"
    return {
        "schema": "ocm.residual-strategy-regime.r0a.frozen-source-forensic.v1",
        "authority": "historical test-source forensic reconstruction; not runtime checker authority",
        "frozen_commit": FROZEN_COMMIT,
        "sources": files,
        "forensic_opportunities": {
            "navigation_serving_runtime": files["tests/m2/test_navigation_serving_runtime.py"]["opportunities"],
            "runtime_extraction_index": files["tests/m2/test_runtime_extraction_index.py"]["opportunities"],
            "solve_operator_index": files["tests/m2/test_solve_operator_index.py"]["opportunities"],
            "total": reconstructed,
            "corrected_r0_check_tail": corrected,
            "source_level_trivial_pass_coverage_fraction": reconstructed / corrected if corrected else 0.0,
        },
        "controls": controls,
        "findings": {
            "all_frozen_test_tail_opportunities_reconstruct_to_trivial_PASS_checker_factories": reconstructed == 20,
            "recorded_runtime_manifest_bound_those_checker_bodies": False,
            "literal_check_trace_preserved_by_elision": False,
            "production_checker_population_represented_by_this_test_donor": False,
        },
        "claim_boundary": [
            "This is a forensic source-level coverage upper bound for a historical test donor.",
            "Byte-identical source plus AST shape does not retroactively create a runtime effect certificate.",
            "The R0A checker-provenance terminal remains valid because historical manifests/replay did not bind checker code.",
            "The existing suffix-elision hostile still blocks unrestricted production early exit and literal trace equivalence.",
            "No claim is made that production checkers are trivial, pure, or represented by these fixtures.",
            "No ML or learned routing is authorized.",
        ],
        "next_experiment": (
            "Use the 20/20 forensic result only to justify a prospective migration experiment: "
            "bind certified pure checker identity before execution, define the protected trace projection, "
            "and rerun a frozen non-test checker population with migration/build/replay costs charged."
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
        f = report["forensic_opportunities"]
        print(
            "::notice title=R0A frozen source forensic::"
            f"coverage={f['total']}/{f['corrected_r0_check_tail']}; terminal={report['terminal']}"
        )
    if report["terminal"] != TERMINAL:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
