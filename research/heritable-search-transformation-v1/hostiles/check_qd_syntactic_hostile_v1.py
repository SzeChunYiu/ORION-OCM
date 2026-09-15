#!/usr/bin/env python3
"""Exact hostile for #233: syntactic QD diversity can collapse to one phenotype."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
WITNESS = ROOT / "W_QD_syntactic_one_phenotype.json"

ALLOWED_AST = (
    ast.Expression,
    ast.BinOp,
    ast.Name,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.USub,
    ast.UnaryOp,
    ast.Load,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def eval_expr(source: str, x: int) -> int:
    tree = ast.parse(source, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_AST):
            raise ValueError(f"unsupported syntax node: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id != "x":
            raise ValueError(f"unsupported name: {node.id}")
        if isinstance(node, ast.Constant) and (isinstance(node.value, bool) or not isinstance(node.value, int)):
            raise ValueError("only integer constants are allowed")
    return int(eval(compile(tree, "<qd-hostile>", "eval"), {"__builtins__": {}}, {"x": x}))


def behavior(source: str, domain: list[int]) -> tuple[int, ...]:
    return tuple(eval_expr(source, x) for x in domain)


def main() -> int:
    witness = load_json(WITNESS)
    failures: list[str] = []

    if witness.get("schema") != "HST_HOSTILE_QD_SYNTACTIC_ONE_PHENOTYPE_V1":
        failures.append("schema mismatch")

    domain = witness.get("domain")
    if domain != [-1, 0, 1]:
        failures.append(f"domain drift: {domain!r}")

    archive = witness.get("archive", [])
    syntax = [row.get("syntax") for row in archive]
    if len(archive) != 4:
        failures.append(f"archive size {len(archive)} != 4")
    if len(set(syntax)) != len(syntax):
        failures.append("archive syntaxes are not distinct")

    computed: dict[str, tuple[int, ...]] = {}
    for row in archive:
        row_id = row.get("id", "<missing>")
        try:
            values = behavior(row["syntax"], domain)
        except Exception as exc:
            failures.append(f"{row_id}: expression evaluation failed: {exc}")
            continue
        computed[row_id] = values
        declared = tuple(row.get("declared_behavior", []))
        if values != declared:
            failures.append(f"{row_id}: declared {declared} != computed {values}")

    phenotype_count = len(set(computed.values())) if computed else 0
    expected = witness.get("expected", {})
    if phenotype_count != expected.get("behavioral_phenotypes"):
        failures.append(
            f"behavioral phenotype count {phenotype_count} != {expected.get('behavioral_phenotypes')}"
        )
    if len(set(syntax)) != expected.get("distinct_syntaxes"):
        failures.append("distinct syntax count mismatch")

    negative = witness.get("negative_control", {})
    try:
        negative_behavior = behavior(negative["syntax"], domain)
    except Exception as exc:
        failures.append(f"negative control evaluation failed: {exc}")
        negative_behavior = ()
    if negative_behavior != tuple(negative.get("declared_behavior", [])):
        failures.append("negative control declared behavior mismatch")

    combined = set(computed.values())
    if negative_behavior:
        combined.add(negative_behavior)
    if len(combined) != expected.get("with_negative_control_behavioral_phenotypes"):
        failures.append("negative-control phenotype count mismatch")

    if negative_behavior in set(computed.values()):
        failures.append("negative control is behaviorally identical to the archive")

    receipt = {
        "schema": "HST_HOSTILE_QD_SYNTACTIC_ONE_PHENOTYPE_RECEIPT_V1",
        "verdict": "PASS" if not failures else "FAIL",
        "domain": domain,
        "archive_entries": len(archive),
        "distinct_syntaxes": len(set(syntax)),
        "behavioral_phenotypes": phenotype_count,
        "negative_control_behavior": list(negative_behavior),
        "with_negative_control_behavioral_phenotypes": len(combined),
        "witness_sha256": hashlib.sha256(WITNESS.read_bytes()).hexdigest(),
        "failures": failures,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
