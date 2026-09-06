"""Public/private challenge sealer and leakage guard for Anthropic FLT challenges."""
from __future__ import annotations

from dataclasses import asdict
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any, Iterable, Mapping

from anthropic_dag import Node, active_imports
from flt_contract import EnvironmentIdentity, Terminal, canonical_json, sha256_text

FORBIDDEN_SHORTCUTS = (
    r"\bsorry\b",
    r"\badmit\b",
    r"\baxiom\b",
    r"\bnative_decide\b",
    r"\bunsafe\b",
)


class LeakageError(RuntimeError):
    pass


def scan_generated_lean(text: str, *, allowed_theorem_modules: Iterable[str] = ()) -> None:
    allowed = set(allowed_theorem_modules)
    for pattern in FORBIDDEN_SHORTCUTS:
        if re.search(pattern, text):
            raise LeakageError(f"forbidden proof shortcut: {pattern}")
    for module in active_imports(text):
        if module.startswith("P2M.Sol."):
            raise LeakageError(f"forbidden hidden solution import: {module}")
        if module.startswith("Theorems.Thm_") and module not in allowed:
            raise LeakageError(f"forbidden hidden theorem import: {module}")


def _safe_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_packages(
    *,
    node: Node,
    output_root: Path,
    regime: str,
    boundary_statements: Mapping[str, str] | None = None,
) -> tuple[Path, Path]:
    if regime not in {"R2", "R3"}:
        raise ValueError("this sealer tranche supports R2/R3 only")
    if output_root.exists():
        shutil.rmtree(output_root)
    public = output_root / "public"
    private = output_root / "private"
    public.mkdir(parents=True)
    private.mkdir(parents=True)
    env = EnvironmentIdentity()
    boundary_statements = dict(boundary_statements or {})

    public_manifest: dict[str, Any] = {
        "schema": "flt-kso-v1.public-challenge.v1",
        "regime": regime,
        "environment": asdict(env),
        "environment_digest": env.digest,
        "target_id": node.theorem_id,
        "target_statement": node.statement_source,
        "allowed_boundary_statements": boundary_statements,
        "hidden_solution_text": False,
        "hidden_dependency_topology": regime == "R3",
        "llm_calls_allowed": 0,
    }
    if regime == "R2":
        public_manifest["exposed_dependency_statements"] = sorted(boundary_statements)
    private_manifest = {
        "schema": "flt-kso-v1.private-evaluator.v1",
        "regime": regime,
        "environment": asdict(env),
        "target_id": node.theorem_id,
        "wrapper_path": node.wrapper_path,
        "solution_path": node.solution_path,
        "original_dependencies": list(node.dependencies),
        "target_statement_sha256": sha256_text(node.statement_source),
        "original_wrapper_sha256": node.wrapper_sha256,
        "original_proof_sha256": node.solution_sha256,
    }
    _safe_write(public / "challenge.json", canonical_json(public_manifest) + "\n")
    _safe_write(private / "evaluator.json", canonical_json(private_manifest) + "\n")
    audit_public_tree(public, private_root=private)
    return public, private


def audit_public_tree(public_root: Path, *, private_root: Path | None = None) -> None:
    public_root = public_root.resolve()
    private_resolved = private_root.resolve() if private_root is not None else None
    for path in public_root.rglob("*"):
        if path.is_symlink():
            raise LeakageError(f"public package contains symlink: {path}")
        if not path.is_file():
            continue
        resolved = path.resolve()
        if public_root not in resolved.parents:
            raise LeakageError(f"public file escapes root: {path}")
        rel = path.relative_to(public_root).as_posix()
        if rel.startswith("html/") or "/html/" in f"/{rel}/":
            raise LeakageError("html/ is forbidden in solver package")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if private_resolved is not None and str(private_resolved) in text:
            raise LeakageError("public package embeds private-root path")
        if "P2M/Sol/" in text or "P2M.Sol." in text:
            raise LeakageError("public package leaks hidden solution path/import")
        if path.suffix == ".lean":
            scan_generated_lean(text)


def sanitized_environment(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    keep = ("HOME", "PATH", "LANG", "LC_ALL", "TMPDIR", "TEMP", "TMP")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    env.update({"PYTHONNOUSERSITE": "1"})
    for key, value in (extra or {}).items():
        if key in {"LEAN_PATH", "PYTHONPATH", "ELAN_TOOLCHAIN"} or "API_KEY" in key or "TOKEN" in key:
            raise LeakageError(f"forbidden environment override: {key}")
        env[key] = value
    return env


def private_open_guard_capability() -> str:
    return "STRACE" if shutil.which("strace") else Terminal.CANNOT_CHECK_PRIVATE_OPEN_GUARD.value


def _trace_touches_private(trace_text: str, *, public_root: Path, private_root: Path) -> bool:
    """Resolve both absolute and cwd-relative file arguments observed by strace.

    `strace -yy` normally annotates resolved descriptor paths, but quoted syscall arguments can
    still be relative.  Treat the solver package root as the initial cwd and fail closed on any
    quoted path that canonicalizes into the private evaluator tree.  Future R2/R3 execution also
    uses a physically separate public-only job, so this guard is defense in depth rather than the
    isolation boundary by itself.
    """
    public = public_root.resolve()
    private = private_root.resolve()
    if str(private) in trace_text:
        return True
    for raw in re.findall(r'"((?:[^"\\]|\\.)*)"', trace_text):
        # strace escapes uncommon bytes; ordinary filesystem path escapes are sufficient here.
        candidate_text = raw.replace(r'\"', '"').replace(r'\\', '\\')
        candidate = Path(candidate_text)
        try:
            resolved = candidate.resolve() if candidate.is_absolute() else (public / candidate).resolve()
        except OSError:
            continue
        if resolved == private or private in resolved.parents:
            return True
    return False


def run_public_process(
    argv: list[str],
    *,
    public_root: Path,
    private_root: Path,
    timeout_s: float,
) -> dict[str, Any]:
    public_root = public_root.resolve()
    private_root = private_root.resolve()
    audit_public_tree(public_root, private_root=private_root)
    if any(str(private_root) in x for x in argv):
        raise LeakageError("private root appears in solver argv")
    strace = shutil.which("strace")
    if strace is None:
        return {"terminal": Terminal.CANNOT_CHECK_PRIVATE_OPEN_GUARD.value, "executed": False}
    with tempfile.TemporaryDirectory(prefix="flt-kso-trace-") as td:
        trace = Path(td) / "open.trace"
        command = [strace, "-f", "-yy", "-e", "trace=open,openat,openat2", "-o", str(trace), *argv]
        cp = subprocess.run(command, cwd=public_root, env=sanitized_environment(), capture_output=True, text=True, timeout=timeout_s)
        trace_text = trace.read_text(encoding="utf-8", errors="replace")
        if _trace_touches_private(trace_text, public_root=public_root, private_root=private_root):
            raise LeakageError("solver process opened private tree")
        return {
            "terminal": "PROCESS_GUARD_CLEAR" if cp.returncode == 0 else "PROCESS_FAILED",
            "executed": True,
            "returncode": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "trace_sha256": sha256_text(trace_text),
        }
