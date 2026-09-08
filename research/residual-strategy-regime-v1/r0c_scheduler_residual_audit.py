"""Source-derived R0C scheduler residual audit over the merged native donor.

This is deliberately an oracle *upper bound*, not a selector.  The donor has only
four authored target/mode cells and the outcome label (positive/false) is not a
legal pre-search selector feature.  We therefore ask only how much whole-process
cost a free cell-identity oracle could possibly save over the best static exact
scheduler.  If that upper bound is already tiny, a learned scheduler has no
payable claim at this donor scope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 40
D = Decimal
EXPECTED_SOURCE_BLOB = "fb5c1ecdcccf68023e328cd6b59309fb0262f407"
SOURCE_REL = Path("native-indexed-deduction-evidence-v1/SUMMARY.json")
TERMINAL = "R0C_DONOR_ORACLE_BOUND_ONLY_NO_SELECTION_POPULATION"
SCHEDULERS = ("layered", "indexed")


def _git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode()
    return hashlib.sha1(header + raw).hexdigest()


def _default_source() -> Path:
    return Path(__file__).resolve().parents[1] / SOURCE_REL


def _decimal_json(value: D) -> dict:
    return {"exact_decimal": format(value, "f"), "float": float(value)}


def _load(source: Path) -> tuple[dict, str]:
    raw = source.read_bytes()
    sha = _git_blob_sha(raw)
    if sha != EXPECTED_SOURCE_BLOB:
        raise RuntimeError(f"native donor drift: {sha} != {EXPECTED_SOURCE_BLOB}")
    return json.loads(raw, parse_float=D), sha


def _pair_rows(doc: dict) -> list[dict]:
    arms = doc["arms"]
    by_key = {(a["target"], a["mode"], a["scheduler"]): a for a in arms}
    cells = sorted({(a["target"], a["mode"]) for a in arms})
    if len(cells) != 4:
        raise RuntimeError(f"expected four authored cells, got {cells!r}")
    if set(a["scheduler"] for a in arms) != set(SCHEDULERS):
        raise RuntimeError("scheduler population drift")

    rows = []
    for target, mode in cells:
        pair = {s: by_key[(target, mode, s)] for s in SCHEDULERS}
        layered, indexed = pair["layered"], pair["indexed"]
        if layered["terminal"] != indexed["terminal"]:
            raise RuntimeError(f"terminal mismatch for {(target, mode)!r}")
        if layered["tree_cost"] != indexed["tree_cost"]:
            raise RuntimeError(f"proof-cost mismatch for {(target, mode)!r}")
        if layered["ordinary_instance_sha256"] != indexed["ordinary_instance_sha256"]:
            raise RuntimeError(f"ordinary-instance drift for {(target, mode)!r}")

        wall = {s: pair[s]["process"]["wall_seconds"] for s in SCHEDULERS}
        search = {s: pair[s]["timings_seconds"]["search_seconds"] for s in SCHEDULERS}
        best_wall = min(SCHEDULERS, key=lambda s: (wall[s], s))
        best_search = min(SCHEDULERS, key=lambda s: (search[s], s))
        rows.append({
            "target_outcome_label_oracle_only": target,
            "mode": mode,
            "terminal": layered["terminal"],
            "tree_cost": layered["tree_cost"],
            "whole_process_wall_seconds": {s: _decimal_json(wall[s]) for s in SCHEDULERS},
            "search_seconds": {s: _decimal_json(search[s]) for s in SCHEDULERS},
            "best_whole_process_scheduler": best_wall,
            "best_search_scheduler": best_search,
            "whole_process_scheduler_disagreement": wall["layered"] != wall["indexed"],
            "search_scheduler_disagreement": search["layered"] != search["indexed"],
        })
    return rows


def _aggregate(rows: list[dict], field: str) -> dict:
    def cost(row: dict, scheduler: str) -> D:
        return D(row[field][scheduler]["exact_decimal"])

    static = {s: sum((cost(r, s) for r in rows), D(0)) for s in SCHEDULERS}
    best_static = min(SCHEDULERS, key=lambda s: (static[s], s))
    oracle = sum((min(cost(r, s) for s in SCHEDULERS) for r in rows), D(0))
    residual = (static[best_static] - oracle) / static[best_static]
    return {
        "equal_weight_authored_cells": len(rows),
        "static_totals": {s: _decimal_json(static[s]) for s in SCHEDULERS},
        "best_static_scheduler": best_static,
        "free_cell_identity_oracle_total": _decimal_json(oracle),
        "oracle_improvement_over_best_static_fraction": _decimal_json(residual),
        "oracle_improvement_over_best_static_percent": _decimal_json(residual * D(100)),
    }


def build_receipt(source: Path | None = None) -> dict:
    source = _default_source() if source is None else source
    doc, blob = _load(source)
    if doc.get("terminal") != "EXACT_FINITE_PARITY_WITH_MIXED_OBSERVED_COST":
        raise RuntimeError("native donor terminal drift")
    rows = _pair_rows(doc)
    whole = _aggregate(rows, "whole_process_wall_seconds")
    search = _aggregate(rows, "search_seconds")

    whole_pct = D(whole["oracle_improvement_over_best_static_percent"]["exact_decimal"])
    if whole_pct >= D("0.5"):
        raise RuntimeError(f"frozen donor whole-process oracle bound no longer tiny: {whole_pct}%")

    return {
        "study": "R0C_NATIVE_SCHEDULER_RESIDUAL_AUDIT_V1",
        "authority": "source-derived merged donor audit; free oracle upper bound only",
        "source": {
            "path": str(SOURCE_REL),
            "git_blob_sha1": blob,
            "donor_terminal": doc["terminal"],
            "donor_interpretation": doc["interpretation"],
        },
        "cells": rows,
        "aggregate": {
            "whole_process_wall_seconds": whole,
            "search_seconds": search,
        },
        "findings": {
            "scheduler_sign_varies_across_authored_cells": len({r["best_whole_process_scheduler"] for r in rows}) > 1,
            "best_static_whole_process_scheduler": whole["best_static_scheduler"],
            "whole_process_oracle_residual_below_half_percent": whole_pct < D("0.5"),
            "search_local_residual_exceeds_whole_process_residual": (
                D(search["oracle_improvement_over_best_static_fraction"]["exact_decimal"])
                > D(whole["oracle_improvement_over_best_static_fraction"]["exact_decimal"])
            ),
        },
        "terminal": TERMINAL,
        "ml_authorized": False,
        "claim_boundary": [
            "only four authored target/mode cells; not a selection population",
            "positive/false is an outcome label and forbidden as a deployable pre-search feature",
            "cell identity is given to the oracle for free, making the residual an intentionally unfair upper bound",
            "equal cell weighting is a calibration convention, not an empirical theorem-demand distribution",
            "wall-clock numbers are one fixed-order observation per authored cell, not a statistical speed study",
            "the donor itself states cold compilation dominates and claims no default scheduler adoption",
            "no learned proof scheduler or production routing change is authorized",
        ],
        "next_experiment": (
            "Only expand R0C after prospectively freezing a materially larger proof-task population and a lifetime "
            "regime where scheduler-local savings can plausibly survive whole-process startup/index/checker costs."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args(argv)
    receipt = build_receipt(args.source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if args.github_notice:
        whole = receipt["aggregate"]["whole_process_wall_seconds"]
        search = receipt["aggregate"]["search_seconds"]
        print(
            "::notice title=R0C scheduler donor residual::"
            f"whole oracle residual={whole['oracle_improvement_over_best_static_percent']['exact_decimal']}%; "
            f"search oracle residual={search['oracle_improvement_over_best_static_percent']['exact_decimal']}%; "
            f"terminal={receipt['terminal']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
