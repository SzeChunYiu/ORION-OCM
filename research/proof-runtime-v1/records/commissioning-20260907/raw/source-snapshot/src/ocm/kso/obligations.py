"""Theorem / obligation registry (M1 I) — load, validate and run every registered checker.

Each obligation row records: status ∈ {PROVED, FINITE_CALIBRATION, CONJECTURE, PARENT_OWNED,
CANNOT_CHECK, OPEN}, a proof/reference, the checker (``module:function``), the planted mutant, the
parent and the known limitation.  ``verify_registry`` runs every resolvable checker and reports
PASS / FAIL / CANNOT_CHECK per row — never collapsing the three.
"""
from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .warrant import CannotCheck

STATUSES = ("PROVED", "FINITE_CALIBRATION", "CONJECTURE", "PARENT_OWNED", "CANNOT_CHECK", "OPEN")
REQUIRED_FIELDS = ("id", "statement", "status", "proof", "checker", "mutant", "parent", "limitation")


def registry_path(root: Path | None = None) -> Path:
    from ocm.historical import repository_root

    base = root or repository_root()
    return base / "docs" / "theorems" / "KSO_OBLIGATION_REGISTRY_V1.json"


def load_registry(root: Path | None = None) -> dict[str, Any]:
    data = json.loads(registry_path(root).read_text(encoding="utf-8"))
    ids = [row["id"] for row in data["obligations"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate obligation id in registry")
    for row in data["obligations"]:
        missing = [f for f in REQUIRED_FIELDS if f not in row]
        if missing:
            raise ValueError(f"obligation {row.get('id')} missing fields {missing}")
        if row["status"] not in STATUSES:
            raise ValueError(f"obligation {row['id']} has unknown status {row['status']}")
        if row["status"] in ("PROVED", "FINITE_CALIBRATION") and row["checker"] in ("—", ""):
            raise ValueError(f"obligation {row['id']} claims {row['status']} without a checker")
    return data


def resolve_checker(spec: str):
    if ":" not in spec or spec.startswith("research/"):
        return None
    module_name, func = spec.split(":", 1)
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None
    return getattr(module, func, None)


@dataclass(frozen=True)
class ObligationResult:
    obligation_id: str
    status: str
    outcome: str          # PASS | FAIL | CANNOT_CHECK | NOT_RUNNABLE
    detail: dict[str, Any] | str


def verify_registry(root: Path | None = None) -> list[ObligationResult]:
    data = load_registry(root)
    out: list[ObligationResult] = []
    cache: dict[str, tuple[str, Any]] = {}
    for row in data["obligations"]:
        fn = resolve_checker(row["checker"])
        if fn is None:
            out.append(ObligationResult(row["id"], row["status"], "NOT_RUNNABLE", row["checker"]))
            continue
        key = row["checker"]
        if key not in cache:
            try:
                cache[key] = ("PASS", fn())
            except CannotCheck as exc:
                cache[key] = ("CANNOT_CHECK", str(exc))
            except AssertionError as exc:
                cache[key] = ("FAIL", f"AssertionError: {exc}")
            except Exception as exc:  # noqa: BLE001 — any other exception is a failure, never a pass
                cache[key] = ("FAIL", f"{type(exc).__name__}: {exc}")
        outcome, detail = cache[key]
        out.append(ObligationResult(row["id"], row["status"], outcome, detail))
    return out


def summarize(results: list[ObligationResult]) -> dict[str, Any]:
    counts = {"PASS": 0, "FAIL": 0, "CANNOT_CHECK": 0, "NOT_RUNNABLE": 0}
    for r in results:
        counts[r.outcome] += 1
    proved_without_pass = [r.obligation_id for r in results if r.status in ("PROVED", "FINITE_CALIBRATION") and r.outcome != "PASS"]
    return {"counts": counts, "proved_or_calibrated_without_passing_checker": proved_without_pass, "rows": [r.obligation_id for r in results]}
