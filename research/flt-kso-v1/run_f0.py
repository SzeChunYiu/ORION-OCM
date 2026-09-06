#!/usr/bin/env python3
"""Run the source-bound F0 masked-composition apparatus gate.

The generator receives only registered typed JSON and emits a proof AST.  This trusted host validates
that AST, renders Lean, checks it with exact Lean 4.33.1, and only then admits proof support into KSO.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any, Mapping

from flt_contract import EnvironmentIdentity, SOURCE_BASE, Terminal, base_receipt, sha256_text
from sealer import sanitized_environment, scan_generated_lean

F0_CHALLENGE_ID = "F0_MASKED_COMPOSITION_001"
F0_MAX_EXPANSIONS = 128
F0_MAX_CANDIDATES = 256
F0_MAX_CHECKER_CALLS = 16
FOUNDATION_BLOB = "4cce6e295bc1f3e8e289be9ebd7a41ee801d859c"
COMPOSITION_BLOB = "bd32922dd220085b5695140f7e684d87cb6f37c7"
ALLOWED_LEMMAS = (
    "MEFoundation.agreement_sound",
    "MEFoundation.agreement_refinement",
)
F0_STATEMENT = (
    "{H A : Type} (V W : H → Prop) (q : H → A) (answer : A) (actual : H) "
    "(member : W actual) (subset : ∀ h, W h → V h) "
    "(agreement : ∀ h, V h → q h = answer) : q actual = answer"
)


def m(name: str) -> list[str]:
    return ["?", name]


def app(fn: Any, *args: Any) -> list[Any]:
    return ["app", fn, *args]


def imp(a: Any, b: Any) -> list[Any]:
    return ["imp", a, b]


def forall(typ: Any, body: Any) -> list[Any]:
    return ["forall", typ, body]


def eq(a: Any, b: Any) -> list[Any]:
    return ["eq", a, b]


def bvar(index: int = 0) -> list[Any]:
    return ["b", index]


def f0_request(*, local_names: Mapping[str, str] | None = None, max_expansions: int = F0_MAX_EXPANSIONS) -> dict[str, Any]:
    names = {"member": "member", "subset": "subset", "agreement": "agreement"}
    names.update(local_names or {})
    h = "H"; V = "V"; W = "W"; q = "q"; answer = "answer"; actual = "actual"; x = bvar()
    return {
        "schema": "flt-kso-v1.f0-generator-request.v1",
        "challenge_id": F0_CHALLENGE_ID,
        "target": eq(app(q, actual), answer),
        "context": [
            {"id": names["member"], "type": app(W, actual)},
            {"id": names["subset"], "type": forall(h, imp(app(W, x), app(V, x)))},
            {"id": names["agreement"], "type": forall(h, imp(app(V, x), eq(app(q, x), answer)))},
        ],
        "rules": [
            {
                "id": ALLOWED_LEMMAS[0],
                "conclusion": eq(app(m("q"), m("actual")), m("answer")),
                "premises": [
                    app(m("V"), m("actual")),
                    forall(m("H"), imp(app(m("V"), x), eq(app(m("q"), x), m("answer")))),
                ],
                "render_metas": ["V", "q", "answer", "actual"],
            },
            {
                "id": ALLOWED_LEMMAS[1],
                "conclusion": forall(m("H"), imp(app(m("W"), x), eq(app(m("q"), x), m("answer")))),
                "premises": [
                    forall(m("H"), imp(app(m("W"), x), app(m("V"), x))),
                    forall(m("H"), imp(app(m("V"), x), eq(app(m("q"), x), m("answer")))),
                ],
                "render_metas": ["V", "W", "q", "answer"],
            },
        ],
        "budget": {"max_expansions": max_expansions, "max_candidates": F0_MAX_CANDIDATES},
        "llm_calls_allowed": 0,
        "foundation_model_calls_allowed": 0,
    }


def _git_blob(repo_root: Path, rel: str) -> str | None:
    try:
        cp = subprocess.run(["git", "-C", str(repo_root), "rev-parse", f"HEAD:{rel}"], capture_output=True, text=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return cp.stdout.strip()


def _trace_forbidden(trace: str) -> str | None:
    if "Composition.lean" in trace:
        return "GENERATOR_OPENED_MASKED_COMPOSITION"
    if "Foundation.lean" in trace:
        return "GENERATOR_OPENED_FOUNDATION_SOURCE"
    if re.search(r"\bconnect\(", trace):
        return "GENERATOR_ATTEMPTED_NETWORK_CONNECT"
    return None


def invoke_generator(request: dict[str, Any], *, generator_path: Path, require_strace: bool = True) -> dict[str, Any]:
    python = shutil.which("python3") or shutil.which("python")
    if not python:
        return {"terminal": "CANNOT_CHECK_F0_PYTHON", "executed": False}
    strace = shutil.which("strace")
    if require_strace and not strace:
        return {"terminal": "CANNOT_CHECK_F0_CUSTODY_TRACE", "executed": False}
    with tempfile.TemporaryDirectory(prefix="flt-kso-f0-generator-") as td:
        trace_path = Path(td) / "trace.txt"
        command = [python, "-I", str(generator_path.resolve())]
        if strace:
            command = [strace, "-f", "-yy", "-e", "trace=open,openat,openat2,connect", "-o", str(trace_path), *command]
        cp = subprocess.run(
            command,
            cwd=td,
            env=sanitized_environment(),
            input=json.dumps(request, sort_keys=True),
            capture_output=True,
            text=True,
            timeout=20,
        )
        trace = trace_path.read_text(encoding="utf-8", errors="replace") if trace_path.is_file() else ""
        forbidden = _trace_forbidden(trace)
        if forbidden:
            return {"terminal": forbidden, "executed": True, "returncode": cp.returncode, "trace_sha256": sha256_text(trace)}
        if cp.returncode != 0:
            return {"terminal": "F0_GENERATOR_PROCESS_FAILED", "executed": True, "returncode": cp.returncode, "stderr": cp.stderr, "trace_sha256": sha256_text(trace)}
        try:
            result = json.loads(cp.stdout)
        except json.JSONDecodeError:
            return {"terminal": "F0_GENERATOR_INVALID_JSON", "executed": True, "stdout": cp.stdout, "stderr": cp.stderr}
        result["custody_trace_sha256"] = sha256_text(trace)
        result["custody_trace"] = "CLEAR" if strace else "NOT_CHECKED"
        result["generator_source_sha256"] = sha256_text(generator_path.read_text(encoding="utf-8"))
        return result


def _render_data_expr(x: Any) -> str:
    if isinstance(x, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", x):
        return x
    raise ValueError(f"untrusted/non-atomic render binding: {x!r}")


def render_ast(ast: dict[str, Any], *, allowed_locals: set[str]) -> str:
    op = ast.get("op")
    if op == "LOCAL_HYPOTHESIS":
        ident = ast.get("id")
        if ident not in allowed_locals:
            raise ValueError(f"undeclared local hypothesis: {ident!r}")
        return str(ident)
    if op != "APPLY_LEMMA":
        raise ValueError(f"unregistered AST operation: {op!r}")
    lemma = ast.get("id")
    if lemma not in ALLOWED_LEMMAS:
        raise ValueError(f"undeclared proof lemma: {lemma!r}")
    expected = ["V", "q", "answer", "actual"] if lemma == ALLOWED_LEMMAS[0] else ["V", "W", "q", "answer"]
    bindings = ast.get("bindings")
    premises = ast.get("premises")
    if not isinstance(bindings, dict) or not isinstance(premises, list):
        raise ValueError("malformed APPLY_LEMMA AST")
    if set(bindings) != set(expected):
        raise ValueError("renderer binding closure mismatch")
    data = [_render_data_expr(bindings[name]) for name in expected]
    children = [render_ast(child, allowed_locals=allowed_locals) for child in premises]
    return " ".join([str(lemma), *data, *[f"({child})" if " " in child else child for child in children]])


def emit_f0_lean(ast: dict[str, Any], *, theorem_name: str = "masked_refinement_then_sound", local_names: Mapping[str, str] | None = None) -> str:
    names = {"member": "member", "subset": "subset", "agreement": "agreement"}
    names.update(local_names or {})
    allowed_locals = set(names.values())
    term = render_ast(ast, allowed_locals=allowed_locals)
    source = "\n".join([
        "import Foundation",
        "",
        "namespace F0Generated",
        f"theorem {theorem_name} {{H A : Type}} (V W : H → Prop)",
        "    (q : H → A) (answer : A) (actual : H)",
        f"    ({names['member']} : W actual) ({names['subset']} : ∀ h, W h → V h)",
        f"    ({names['agreement']} : ∀ h, V h → q h = answer) : q actual = answer :=",
        f"  {term}",
        "",
        f"#print axioms F0Generated.{theorem_name}",
        "end F0Generated",
        "",
    ])
    scan_generated_lean(source, allowed_theorem_modules=())
    if "Composition" in source or "refinement_then_sound" in source:
        raise ValueError("masked target constant/body leaked into rendered source")
    return source


def _lean_version(lean: str) -> str | None:
    cp = subprocess.run([lean, "--version"], capture_output=True, text=True, env=sanitized_environment(), timeout=10)
    match = re.search(r"Lean \(version ([0-9.]+)", cp.stdout + cp.stderr)
    return match.group(1) if match else None


def check_f0_sources(*, repo_root: Path, native_source: str, parent_source: str, lean: str | None = None) -> dict[str, Any]:
    lean = lean or shutil.which("lean")
    if not lean:
        return {"terminal": Terminal.CANNOT_CHECK_PINNED_FLT_ENVIRONMENT.value, "checker_calls": 0, "reason": "lean-not-found"}
    if _lean_version(lean) != "4.33.1":
        return {"terminal": Terminal.CHECKER_OR_ENVIRONMENT_MISMATCH.value, "checker_calls": 0, "observed_lean_version": _lean_version(lean)}
    foundation = repo_root / "research" / "proof-replay-v1" / "Foundation.lean"
    with tempfile.TemporaryDirectory(prefix="flt-kso-f0-check-") as td:
        root = Path(td)
        shutil.copyfile(foundation, root / "Foundation.lean")
        (root / "Native.lean").write_text(native_source, encoding="utf-8")
        (root / "Parent.lean").write_text(parent_source, encoding="utf-8")
        outputs: list[dict[str, Any]] = []
        for argv in ([lean, "-o", "Foundation.olean", "Foundation.lean"], [lean, "Native.lean"], [lean, "Parent.lean"]):
            cp = subprocess.run(argv, cwd=root, env=sanitized_environment(), capture_output=True, text=True, timeout=30)
            outputs.append({"argv": argv[1:], "returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr})
            if cp.returncode != 0:
                return {"terminal": "LEAN_CHECK_FAILED", "checker_calls": len(outputs), "runs": outputs}
        native_text = outputs[1]["stdout"] + outputs[1]["stderr"]
        parent_text = outputs[2]["stdout"] + outputs[2]["stderr"]
        native_clear = "F0Generated.masked_f0_native does not depend on any axioms" in native_text
        parent_clear = "F0Generated.masked_f0_parent does not depend on any axioms" in parent_text
        if not native_clear or not parent_clear:
            return {"terminal": "AXIOM_REPORT_NOT_CLEAR", "checker_calls": 3, "runs": outputs}
        evidence = "lean-kernel:" + sha256_text(native_source + native_text)
        return {"terminal": "F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED", "checker_calls": 3, "lean_version": "4.33.1", "native_axiom_clear": True, "parent_axiom_clear": True, "checker_evidence": evidence}


def run(*, source_sha: str, repo_root: Path, lean: str | None = None) -> dict[str, Any]:
    from ocm.kso.warrant import Liveness
    from ocm.operators.indexed_registry import IndexedOperatorRegistry
    from theorem_kso import admit_checked_proof, compose_proof_candidate, empty_space, open_obligation, proof_operator

    receipt = base_receipt(source_sha=source_sha, arm="OCM_NATIVE", challenge_id=F0_CHALLENGE_ID)
    receipt["information_regime"] = "F0_MASKED_AUTHORED_FIXTURE"
    receipt["claim_scope"] = "APPARATUS_ONLY_NO_DISCOVERY_NOVELTY"
    foundation_blob = _git_blob(repo_root, "research/proof-replay-v1/Foundation.lean")
    composition_blob = _git_blob(repo_root, "research/proof-replay-v1/Composition.lean")
    receipt["foundation_blob"] = foundation_blob
    receipt["masked_composition_blob"] = composition_blob
    if foundation_blob != FOUNDATION_BLOB or composition_blob != COMPOSITION_BLOB:
        receipt["terminal"] = Terminal.CHECKER_OR_ENVIRONMENT_MISMATCH.value
        receipt["checker_calls"] = 0
        return receipt

    env = EnvironmentIdentity()
    goal = open_obligation(theorem_name="masked_f0", statement=F0_STATEMENT, environment=env)
    ks = empty_space().with_atoms(goal)
    request = f0_request()
    generator_path = repo_root / "research" / "flt-kso-v1" / "f0_generator.py"

    def backend(_ks, _context):
        return invoke_generator(request, generator_path=generator_path, require_strace=True)

    op = proof_operator(goal_atom_id=goal.atom_id, backend=backend)
    registry = IndexedOperatorRegistry()
    registry.register(op)
    applicable = registry.applicable(ks, ())
    if len(applicable) != 1 or applicable[0].fingerprint != op.fingerprint:
        raise RuntimeError("F0 proof operator did not pass production applicability boundary")
    generated = applicable[0].backend(ks, {"challenge_id": F0_CHALLENGE_ID})
    receipt.update({
        "generator_terminal": generated.get("terminal"),
        "generator_custody_trace": generated.get("custody_trace"),
        "generator_custody_trace_sha256": generated.get("custody_trace_sha256"),
        "generator_source_sha256": generated.get("generator_source_sha256"),
        "proof_state_expansions": generated.get("proof_state_expansions", 0),
        "operator_candidates_considered": generated.get("operator_candidates_considered", 0),
        "duplicate_states_avoided": generated.get("duplicate_states_avoided", 0),
        "search_events": generated.get("events", []),
        "goal_liveness_before_check": goal.liveness(()).value,
        "allowed_lemmas": list(ALLOWED_LEMMAS),
        "allowed_ast_ops": ["LOCAL_HYPOTHESIS", "APPLY_LEMMA"],
        "search_budget": {"max_expansions": F0_MAX_EXPANSIONS, "max_candidates": F0_MAX_CANDIDATES, "max_checker_calls": F0_MAX_CHECKER_CALLS},
        "composition_body_given_to_generator": False,
        "foundation_source_given_to_generator": False,
    })
    if generated.get("terminal") != "CANDIDATE_AST_CONSTRUCTED":
        receipt["terminal"] = generated.get("terminal", "F0_GENERATOR_FAILED")
        receipt["checker_calls"] = 0
        return receipt
    ast = generated["proof_ast"]
    native_source = emit_f0_lean(ast, theorem_name="masked_f0_native")
    pending = compose_proof_candidate(ks, op, {"goal_atom_id": goal.atom_id, "proof_ast": ast}, checker_evidence=None)
    if pending.liveness(()) is not Liveness.UNKNOWN:
        raise RuntimeError("unchecked F0 proof candidate promoted above UNKNOWN")

    parent = invoke_generator(request, generator_path=generator_path, require_strace=True)
    if parent.get("terminal") != "CANDIDATE_AST_CONSTRUCTED" or parent.get("proof_ast") != ast:
        receipt["terminal"] = "F0_MATCHED_PARENT_MISMATCH"
        receipt["checker_calls"] = 0
        return receipt
    parent_source = emit_f0_lean(parent["proof_ast"], theorem_name="masked_f0_parent")
    checked = check_f0_sources(repo_root=repo_root, native_source=native_source, parent_source=parent_source, lean=lean)
    receipt["checker"] = checked
    receipt["checker_calls"] = int(checked.get("checker_calls", 0))
    receipt["candidate_liveness_before_check"] = pending.liveness(()).value
    receipt["native_proof_source_sha256"] = sha256_text(native_source)
    receipt["matched_parent"] = {"same_typed_request": True, "same_grammar": True, "same_budget": True, "same_checker": True, "proof_ast_equal": True}
    if checked.get("terminal") != "F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED":
        receipt["terminal"] = checked.get("terminal")
        return receipt
    exact = compose_proof_candidate(ks, op, {"goal_atom_id": goal.atom_id, "proof_ast": ast}, checker_evidence=str(checked["checker_evidence"]))
    admitted = admit_checked_proof(ks, goal=goal, candidate=exact, proof_source_hash=sha256_text(native_source), checker_evidence=str(checked["checker_evidence"]))
    claim_id = goal.atom_id.replace("theorem-goal:", "theorem-claim:", 1)
    receipt.update({
        "candidate_liveness_after_check": exact.liveness(()).value,
        "claim_liveness_after_admission": admitted.atom_map()[claim_id].liveness(()).value,
        "terminal": "F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED",
        "comparison_terminal": Terminal.PARENT_SUFFICIENT.value,
        "ocm_residual_claim": "NONE_AT_F0",
        "discovery_claim": "NONE_AUTHORED_PUBLIC_FIXTURE",
    })
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", SOURCE_BASE))
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--lean")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    receipt = run(source_sha=args.source_sha, repo_root=args.repo_root.resolve(), lean=args.lean)
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if receipt["terminal"] in {"F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED", Terminal.CANNOT_CHECK_PINNED_FLT_ENVIRONMENT.value} else 1


if __name__ == "__main__":
    raise SystemExit(main())
