from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "ocm" / "lifetime" / "phases.py"
EXPECTED_SOURCE_GIT_BLOB_SHA1 = "1327ca822fe8a2c958526c05e59853dd3ff3a4fd"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def _isinstance_sites(fn: ast.FunctionDef, class_name: str) -> list[int]:
    sites: list[int] = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "isinstance" or len(node.args) < 2:
            continue
        obj, cls = node.args[:2]
        if (
            isinstance(obj, ast.Name)
            and obj.id == "arm"
            and isinstance(cls, ast.Name)
            and cls.id == class_name
        ):
            sites.append(node.lineno)
    return sorted(sites)


def _attribute_names(fn: ast.FunctionDef) -> set[str]:
    return {node.attr for node in ast.walk(fn) if isinstance(node, ast.Attribute)}


def _string_literals(fn: ast.FunctionDef) -> set[str]:
    return {
        node.value
        for node in ast.walk(fn)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def analyze_text(text: str, *, source_blob_sha1: str | None = None) -> dict[str, Any]:
    tree = ast.parse(text)
    funcs = _functions(tree)
    required = {"phase_D", "phase_E", "phase_F", "phase_G"}
    if not required.issubset(funcs):
        raise ValueError(f"missing M12 phase functions: {sorted(required - set(funcs))}")

    d, e, f, g = (funcs[name] for name in ("phase_D", "phase_E", "phase_F", "phase_G"))
    d_persistent = _isinstance_sites(d, "PersistentOCM")
    e_persistent = _isinstance_sites(e, "PersistentOCM")
    f_persistent = _isinstance_sites(f, "PersistentOCM")
    g_parent = _isinstance_sites(g, "WholeSystemParent")

    d_attrs = _attribute_names(d)
    d_strings = _string_literals(d)
    f_attrs = _attribute_names(f)
    g_attrs = _attribute_names(g)

    anchors = {
        "phase_D_has_ocm_class_gate": bool(d_persistent),
        "phase_D_switches_causal_estimator": {"backdoor", "naive"}.issubset(d_strings),
        "phase_D_switches_experiment_selector": {"select_ocm", "select_entropy"}.issubset(d_attrs),
        "phase_D_switches_commitment_gate": "gate_sentence" in d_attrs,
        "phase_F_has_ocm_class_gates": len(f_persistent) >= 2,
        "phase_F_contains_source_revision": "revoke_source" in f_attrs,
        "phase_F_contains_science_retraction": "retract" in f_attrs,
        "phase_G_has_parent_class_gate": bool(g_parent),
        "phase_G_contains_parent_repair": "_parent_repair" in {
            node.id for node in ast.walk(g) if isinstance(node, ast.Name)
        },
        "phase_E_has_ocm_class_gate": bool(e_persistent),
    }
    if not all(anchors.values()):
        missing = sorted(k for k, v in anchors.items() if not v)
        raise ValueError(f"M12 source contract changed; missing anchors: {missing}")

    return {
        "schema": "ocm.m12.parent-parity-audit.v1",
        "source": {
            "path": "src/ocm/lifetime/phases.py",
            "git_blob_sha1": source_blob_sha1,
        },
        "class_dispatch_sites": {
            "phase_D.PersistentOCM": d_persistent,
            "phase_E.PersistentOCM": e_persistent,
            "phase_F.PersistentOCM": f_persistent,
            "phase_G.WholeSystemParent": g_parent,
        },
        "causal_attribution": {
            "phase_D": {
                "status": "BLOCKED_BY_ARM_CLASS_DISPATCH",
                "assigned_by_class": [
                    "causal estimator: backdoor vs naive",
                    "experiment selector: select_ocm vs select_entropy",
                    "communication commitment gate",
                    "science persistence representation",
                ],
            },
            "phase_E": {
                "status": "PARTIALLY_EQUALIZED",
                "reason": "the semantic WholeSystemParent receives the shared transfer contract, but the phase still branches on OCM identity",
            },
            "phase_F": {
                "status": "BLOCKED_BY_ARM_CLASS_DISPATCH",
                "assigned_by_class": [
                    "source-aware knowledge revocation",
                    "science-ledger retraction",
                ],
            },
            "phase_G": {
                "status": "BLOCKED_BY_ARM_CLASS_DISPATCH",
                "assigned_by_class": [
                    "parent repair procedure vs OCM self-model diagnosis/proposal path"
                ],
            },
        },
        "strong_parent_requirement": {
            "id": "P6_COMPOSITE_WHOLE_SYSTEM_PARENT",
            "must_match": [
                "task-relevant information and protected inputs",
                "persistent memory permission and lifetime",
                "retrieval/index powers",
                "executable skill/library reuse",
                "continual adaptation permission",
                "truth/reason-maintenance and revocation semantics",
                "tools, checkers and search budgets",
            ],
            "evaluation_repair": (
                "Prospectively dispatch phase mechanisms by registered capability/treatment, not Python arm class; "
                "then rerun continued/reset/P6 arms with complete lifecycle resource vectors."
            ),
        },
        "claim_boundary": {
            "m12_engineering_regression_valid": True,
            "m12_descriptive_lifetime_evidence_valid": True,
            "m12_whole_system_ocm_residual_established": False,
            "general_ocm_net_benefit_established": False,
            "reason": "current M12 mechanism assignment is not capability-equalized against the strongest whole-system parent",
        },
        "terminal": "M12_ARCHITECTURE_CAUSAL_CLAIM_BLOCKED_PARENT_PARITY",
    }


def run(source_path: Path = SOURCE) -> dict[str, Any]:
    raw = source_path.read_bytes()
    actual = git_blob_sha1(raw)
    if actual != EXPECTED_SOURCE_GIT_BLOB_SHA1:
        raise RuntimeError(
            f"M12 source custody drift: expected {EXPECTED_SOURCE_GIT_BLOB_SHA1}, got {actual}"
        )
    return analyze_text(raw.decode("utf-8"), source_blob_sha1=actual)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    if args.github_notice:
        print(
            "::notice title=M12 strongest-parent parity::"
            "current lifetime harness remains descriptive; architecture-level OCM residual blocked by class-dispatched mechanisms"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
