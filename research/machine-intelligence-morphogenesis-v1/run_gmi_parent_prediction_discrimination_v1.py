#!/usr/bin/env python3
"""Exact finite parent-discrimination calibration for Track B B1.

This checker is intentionally small and architecture-free. It evaluates the
pre-frozen A2-A5 atomic semantic-pressure predicates over all 2^9 registered
binary cells, compares them with the frozen parent-product predictor, and
runs deliberately wrong positive-control predictors to verify sensitivity.

It does NOT test morphology-frontier optimality or held-family transfer.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Dict, Iterable, Mapping

EXPECTED_FREEZE_SHA256 = "299718c29acbc1fed9ff51071daf511b797b232f7f8e6930a499054cf32f1906"

VARIABLES = (
    "local_update_cone",
    "local_query_cone",
    "rejectable_update",
    "incumbent_must_remain_available",
    "historical_query_required",
    "serving_compilation_aliases_dev_states",
    "aliased_dev_distinction_future_relevant",
    "high_update_rate",
    "high_reuse",
)

MECHANISMS = (
    "A2_dev_side_information_required",
    "A3_incremental_repair_opportunity",
    "A4_rejection_recoverability_required",
    "A5_lineage_persistence_required",
)


def canonical_sha256(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def iter_cells() -> Iterable[Dict[str, bool]]:
    for bits in itertools.product((False, True), repeat=len(VARIABLES)):
        yield dict(zip(VARIABLES, bits))


def gmi_atomic(row: Mapping[str, bool]) -> Dict[str, bool]:
    return {
        "A2_dev_side_information_required": (
            row["serving_compilation_aliases_dev_states"]
            and row["aliased_dev_distinction_future_relevant"]
        ),
        "A3_incremental_repair_opportunity": row["local_update_cone"],
        "A4_rejection_recoverability_required": (
            row["rejectable_update"] and row["incumbent_must_remain_available"]
        ),
        "A5_lineage_persistence_required": row["historical_query_required"],
    }


def parent_product(row: Mapping[str, bool]) -> Dict[str, bool]:
    # These are deliberately written independently rather than aliasing
    # gmi_atomic(), so the exhaustive checker can catch transcription drift.
    return {
        "A2_dev_side_information_required": (
            row["serving_compilation_aliases_dev_states"]
            and row["aliased_dev_distinction_future_relevant"]
        ),
        "A3_incremental_repair_opportunity": row["local_update_cone"],
        "A4_rejection_recoverability_required": (
            row["rejectable_update"] and row["incumbent_must_remain_available"]
        ),
        "A5_lineage_persistence_required": row["historical_query_required"],
    }


def positive_controls(row: Mapping[str, bool]) -> Dict[str, bool]:
    return {
        "A2_alias_only_proxy": row["serving_compilation_aliases_dev_states"],
        "A3_query_locality_proxy": row["local_query_cone"],
        "A4_update_rate_proxy": row["high_update_rate"],
        "A5_drift_only_proxy": row["high_update_rate"],
    }


def run_exact(freeze: Mapping[str, object]) -> Dict[str, object]:
    freeze_sha = canonical_sha256(freeze)
    if freeze_sha != EXPECTED_FREEZE_SHA256:
        raise AssertionError(
            f"freeze hash mismatch: expected {EXPECTED_FREEZE_SHA256}, got {freeze_sha}"
        )

    expected = freeze["predeclared_expected_checks"]
    if not isinstance(expected, dict):
        raise AssertionError("predeclared_expected_checks must be an object")

    cells = list(iter_cells())
    encoded = {tuple(row[name] for name in VARIABLES) for row in cells}
    if len(cells) != 512 or len(encoded) != 512:
        raise AssertionError("truth-table cell coverage is not exactly 512 unique cells")

    parent_total = 0
    parent_by_mechanism = {name: 0 for name in MECHANISMS}
    first_parent_witnesses = []
    control_mismatches = {
        "A2_alias_only_proxy": 0,
        "A3_query_locality_proxy": 0,
        "A4_update_rate_proxy": 0,
        "A5_drift_only_proxy": 0,
    }
    first_control_witnesses = {name: None for name in control_mismatches}

    for row in cells:
        g = gmi_atomic(row)
        p = parent_product(row)

        row_diff = False
        for mechanism in MECHANISMS:
            if g[mechanism] != p[mechanism]:
                parent_by_mechanism[mechanism] += 1
                row_diff = True
        if row_diff:
            parent_total += 1
            if len(first_parent_witnesses) < 8:
                first_parent_witnesses.append({"cell": dict(row), "gmi": g, "parent": p})

        controls = positive_controls(row)
        target_by_control = {
            "A2_alias_only_proxy": g["A2_dev_side_information_required"],
            "A3_query_locality_proxy": g["A3_incremental_repair_opportunity"],
            "A4_update_rate_proxy": g["A4_rejection_recoverability_required"],
            "A5_drift_only_proxy": g["A5_lineage_persistence_required"],
        }
        for name, prediction in controls.items():
            if prediction != target_by_control[name]:
                control_mismatches[name] += 1
                if first_control_witnesses[name] is None:
                    first_control_witnesses[name] = {
                        "cell": dict(row),
                        "target": target_by_control[name],
                        "proxy": prediction,
                    }

    checks = {
        "cells": len(cells),
        "parent_product_total_mismatches": parent_total,
        "parent_product_mismatches_by_mechanism": parent_by_mechanism,
        "positive_control_mismatches": control_mismatches,
    }

    required = {
        "parent_product_total_mismatches": int(expected["parent_product_total_mismatches"]),
        "A2_alias_only_proxy": int(expected["A2_alias_only_proxy_mismatches"]),
        "A3_query_locality_proxy": int(expected["A3_query_locality_proxy_mismatches"]),
        "A4_update_rate_proxy": int(expected["A4_update_rate_proxy_mismatches"]),
        "A5_drift_only_proxy": int(expected["A5_drift_only_proxy_mismatches"]),
    }
    if parent_total != required["parent_product_total_mismatches"]:
        raise AssertionError(
            f"parent-product mismatch count {parent_total} != {required['parent_product_total_mismatches']}"
        )
    for name in control_mismatches:
        if control_mismatches[name] != required[name]:
            raise AssertionError(
                f"{name} mismatch count {control_mismatches[name]} != {required[name]}"
            )

    terminal = (
        "ATOMIC_MECHANISM_PREDICTIONS_PARENT_PRODUCT_SUFFICIENT_AT_REGISTERED_BINARY_SCOPE"
        if parent_total == 0
        else "PARENT_PRODUCT_COLLISION_ASSUMPTION_FALSE__INSPECT_WITNESS_BEFORE_CLAIM"
    )

    return {
        "schema": "GMI_PARENT_PREDICTION_DISCRIMINATION_RECEIPT_V1",
        "freeze_sha256": freeze_sha,
        "scope": "A2-A5 finite binary semantic necessity/opportunity calibration only",
        "checks": checks,
        "first_parent_witnesses": first_parent_witnesses,
        "first_positive_control_witnesses": first_control_witnesses,
        "terminal": terminal,
        "overall_B1": "OPEN__DISTINCT_JOINT_OR_CROSS_FAMILY_PREDICTION_AND_INDEPENDENT_C5_STILL_REQUIRED",
        "claim_ceiling": (
            "Atomic A2-A5 predictions are parent-product-covered at this exact scope. "
            "No morphology frontier, phase law, fundamental basis, neutral recovery, or novel-form claim follows."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--freeze",
        type=Path,
        default=Path(__file__).with_name("GMI_PARENT_PREDICTION_DISCRIMINATION_FREEZE_V1.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    freeze = json.loads(args.freeze.read_text(encoding="utf-8"))
    receipt = run_exact(freeze)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
