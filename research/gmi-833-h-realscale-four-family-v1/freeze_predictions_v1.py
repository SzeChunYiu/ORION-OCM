#!/usr/bin/env python3
"""Frozen prediction table (FREEZE F7): per-cell predicted champion, computed
from the NOISE-FREE battery only, before any noisy outcome run.

The prediction runs the frozen band-fiber selection on the noise-free
materialization of every registry task (noise stripped; null-arm permutation
stripped) and records the predicted champion machine and its class.  The
noisy outcomes must match cell-by-cell on census cells; every mismatch is a
reported boundary finding.  Committed at the battery commit (pre-outcome).
"""
from __future__ import annotations

import json
from pathlib import Path

import battery_realscale_v1 as bat
import search_realscale_v1 as S

HERE = Path(__file__).resolve().parent


def noise_free(task: dict) -> dict:
    t = dict(task)
    t["sigma_exp"] = None
    t["eps_exp"] = None
    # the perm-null permutation is part of the TASK (its definition), not a
    # noise channel: it stays, so nulls are predicted NOT-recovered.
    return t


def class_of(gen: str, lag: int | None) -> str:
    """Posthoc-side class vocabulary appears only in this prediction map."""
    if gen == "affine":
        return "AFFINE_SHARED_RESPONSE"
    if gen == "decision":
        return "BINARY_DECISION_ON_AFFINE_SCORE"
    if gen == "mono_step":
        return "MONOTONE_LINK_OF_AFFINE_SCORE"
    if gen == "pair_lift":
        return "CROSS_COORDINATE_LIFTED_INTERACTION"
    if gen == "constant":
        return "CONSTANT_RESPONSE"
    if gen in ("delay_real", "delay_binary"):
        return "PERSISTENT_DELAY_CELLS" if (lag or 0) >= 1 else "MEMORYLESS_PROJECTION"
    raise ValueError(gen)


def predicted_row(task: dict) -> dict:
    t = noise_free(task)
    data = bat.materialize(t)
    band = {"mode": "zero"}
    sel = S.proc1_select(data, band)
    return {
        "id": task["id"],
        "gen": task["gen"],
        "predicted_champion": sel["champion"],
        "predicted_stratum": sel["champion_stratum"],
        "predicted_cells": sel["champion_cells"],
        "predicted_class": class_of(task["gen"], task.get("lag")),
        "predicted_persistent": sel["champion_cells"] >= 1,
        "predicted_risk": S.frac_str(sel["champion_risk"]),
    }


def build(jobs: int = 1) -> dict:
    reg = json.loads((HERE / "BATTERY_REGISTRY_V1.json").read_text())
    tasks = list(reg["tasks"])
    if jobs > 1:
        import multiprocessing as mp
        with mp.Pool(jobs) as pool:
            rows = pool.map(predicted_row, tasks, chunksize=4)
    else:
        rows = [predicted_row(t) for t in tasks]
    return {
        "schema": "GMI833HRealScaleFrozenPredictionsV1",
        "rule": "band-fiber selection on the noise-free materialization (F7, AMENDMENT A)",
        "rows": sorted(rows, key=lambda r: r["id"]),
    }


if __name__ == "__main__":
    import sys
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    doc = build(jobs)
    (HERE / "FROZEN_PREDICTIONS_V1.json").write_text(json.dumps(doc, sort_keys=True, indent=1) + "\n")
    print("predictions:", len(doc["rows"]))
