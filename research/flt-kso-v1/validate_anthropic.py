#!/usr/bin/env python3
"""Fail-closed validation of the frozen Anthropic FLT evaluator source and generated wrapper DAG."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time

from anthropic_dag import ExtractionError, extract_graph, validate_dependency_targets
from flt_contract import (
    ANTHROPIC_COMMIT,
    LEAN_TOOLCHAIN,
    MATHLIB_COMMIT,
    Terminal,
    canonical_json,
    sha256_file,
    sha256_text,
)

EXPECTED_MODULES = 29511


def _git_head(root: Path) -> str | None:
    try:
        cp = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return cp.stdout.strip()


def _mathlib_rev(root: Path) -> str | None:
    try:
        body = json.loads((root / "lake-manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for package in body.get("packages", []):
        if package.get("name") == "mathlib":
            return package.get("rev")
    return None


def validate(root: Path) -> dict[str, object]:
    started = time.perf_counter()
    root = root.resolve()
    head = _git_head(root)
    toolchain_path = root / "lean-toolchain"
    manifest_path = root / "lake-manifest.json"
    observed_toolchain = toolchain_path.read_text(encoding="utf-8").strip() if toolchain_path.is_file() else None
    observed_mathlib = _mathlib_rev(root)
    wrapper_count = len(tuple((root / "Theorems").glob("Thm_*.lean")))
    solution_count = len(tuple((root / "P2M" / "Sol").glob("S_*.lean")))

    identity_errors: list[str] = []
    if head != ANTHROPIC_COMMIT:
        identity_errors.append(f"anthropic commit {head!r} != {ANTHROPIC_COMMIT}")
    if observed_toolchain != LEAN_TOOLCHAIN:
        identity_errors.append(f"lean toolchain {observed_toolchain!r} != {LEAN_TOOLCHAIN}")
    if observed_mathlib != MATHLIB_COMMIT:
        identity_errors.append(f"mathlib {observed_mathlib!r} != {MATHLIB_COMMIT}")
    if wrapper_count != EXPECTED_MODULES:
        identity_errors.append(f"wrapper count {wrapper_count} != {EXPECTED_MODULES}")
    if solution_count != EXPECTED_MODULES:
        identity_errors.append(f"solution count {solution_count} != {EXPECTED_MODULES}")
    if identity_errors:
        return {
            "schema": "flt-kso-v1.anthropic-source-validation.v1",
            "terminal": Terminal.CHECKER_OR_ENVIRONMENT_MISMATCH.value,
            "errors": identity_errors,
            "observed": {
                "anthropic_commit": head,
                "lean_toolchain": observed_toolchain,
                "mathlib_commit": observed_mathlib,
                "wrapper_count": wrapper_count,
                "solution_count": solution_count,
            },
        }

    try:
        graph = extract_graph(root, require_count=EXPECTED_MODULES)
    except ExtractionError as exc:
        return {
            "schema": "flt-kso-v1.anthropic-source-validation.v1",
            "terminal": Terminal.CANNOT_CHECK_SIGNATURE_EXTRACTION_COVERAGE.value,
            "error": str(exc),
        }
    missing = validate_dependency_targets(graph)
    if missing:
        return {
            "schema": "flt-kso-v1.anthropic-source-validation.v1",
            "terminal": Terminal.CANNOT_CHECK_SIGNATURE_EXTRACTION_COVERAGE.value,
            "error": "dependency imports point outside extracted theorem set",
            "missing_dependency_count": len(missing),
            "missing_dependency_sample": list(missing[:20]),
        }

    edge_count = sum(len(node.dependencies) for node in graph.values())
    statement_bytes = sum(len(node.statement_source.encode("utf-8")) for node in graph.values())
    proof_bytes = sum((root / node.solution_path).stat().st_size for node in graph.values())
    return {
        "schema": "flt-kso-v1.anthropic-source-validation.v1",
        "terminal": "ANTHROPIC_DAG_EXTRACTION_VALIDATED",
        "anthropic_commit": head,
        "lean_toolchain": observed_toolchain,
        "mathlib_commit": observed_mathlib,
        "wrapper_count": wrapper_count,
        "solution_count": solution_count,
        "dependency_edge_count": edge_count,
        "statement_bytes": statement_bytes,
        "hidden_proof_bytes": proof_bytes,
        "lean_toolchain_sha256": sha256_file(toolchain_path),
        "lake_manifest_sha256": sha256_file(manifest_path),
        "graph_identity_sha256": sha256_text(canonical_json({
            theorem_id: {
                "statement": sha256_text(node.statement_source),
                "proof": node.solution_sha256,
                "dependencies": list(node.dependencies),
            }
            for theorem_id, node in sorted(graph.items())
        })),
        "wall_seconds": time.perf_counter() - started,
        "html_consumed": False,
        "llm_calls": 0,
        "llm_tokens": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    result = validate(args.root)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["terminal"] == "ANTHROPIC_DAG_EXTRACTION_VALIDATED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
