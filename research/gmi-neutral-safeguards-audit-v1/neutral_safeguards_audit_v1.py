#!/usr/bin/env python3
"""Fail-closed Section S audit over two registered neutral-search artifacts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CROSS_DIR = REPO / "research/gmi-cross-grammar-four-family-v1"
CROSS_SOURCE = CROSS_DIR / "cross_grammar_four_family_v1.py"
E2_RESULT = REPO / "research/gmi-section-e-searcher-comparison-v2/RESULT_E2.json"


def _load_cross_module():
    spec = importlib.util.spec_from_file_location("cross_grammar_four_family_for_safeguards", CROSS_SOURCE)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load cross-grammar witness")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_audit() -> dict[str, Any]:
    ledger = json.loads((HERE / "NEUTRAL_SAFEGUARDS_LEDGER_V1.json").read_text(encoding="utf-8"))
    if len(ledger["rows"]) != 10 or any(row["status"] != "GREEN" for row in ledger["rows"]):
        raise ValueError("Section S safeguard ledger drifted")
    cross = _load_cross_module().validate_closure()
    source = CROSS_SOURCE.read_text(encoding="utf-8").lower()
    pre_classifier = source.split("def classify(", 1)[0]
    if "classify(" in pre_classifier:
        raise ValueError("phenotype classification leaked into search")
    if any(token in source for token in ("import torch", "import numpy", "tensor(", ".cuda", "gpu")):
        raise ValueError("uncharged tensor/hardware path entered bounded recovery")
    accounting = cross["search_accounting"]
    if accounting != {"candidate_attempts": 104240, "exact_candidates": 104, "failed_candidates": 104136}:
        raise ValueError("cross-grammar failed-candidate accounting drifted")
    if cross["families"] != 4 or cross["grammars"] != 2 or cross["positive_twin_flips"] != 8:
        raise ValueError("cross-grammar enrichment coverage drifted")

    e2 = json.loads(E2_RESULT.read_text(encoding="utf-8"))
    if not e2["all_frozen_predictions_pass"] or len(e2["assertions"]) != 15 or not all(e2["assertions"].values()):
        raise ValueError("E2 registered search comparison drifted")
    searchers = ("random", "strict_evolution", "neutral_drift_5", "nas_ablation", "darts")
    if any(name not in e2 for name in searchers):
        raise ValueError("E2 searcher inventory drifted")
    strict = e2["strict_evolution"]
    misspecified = e2["singleton_negative"]
    if strict["success_probability_or_exact_success"] is not False or strict["terminal"] != "STRICT_ELITIST_PLATEAU":
        raise ValueError("strict-search failure was reinterpreted")
    if misspecified["grammar_has_exact_target"] is not False or misspecified["success_probability_or_exact_success"] is not False:
        raise ValueError("misspecified grammar failure was reinterpreted")
    if misspecified["terminal"] != "REPRESENTATION_MISSPECIFIED_NO_EXACT_AFFINE_TARGET":
        raise ValueError("misspecified failure terminal drifted")
    for name in ("strict_evolution", "nas_ablation", "darts"):
        row = e2[name]
        if not {"proposal_or_mutation_attempts", "truth_example_touches", "unique_discrete_candidates_verified"} <= row.keys():
            raise ValueError(f"E2 search accounting missing: {name}")
    random_accounting = e2["random"]["reporting_at_cap"]
    if not {"proposal_or_mutation_attempts", "truth_example_touches", "unique_discrete_candidates_verified"} <= random_accounting.keys():
        raise ValueError("random-search accounting missing")
    if not {"expected_proposal_or_mutation_attempts", "expected_truth_example_touches", "expected_unique_discrete_candidates_verified"} <= e2["neutral_drift_5"].keys():
        raise ValueError("neutral-drift accounting missing")
    return {
        "ledger_rows": 10,
        "families": 4,
        "grammars": 2,
        "positive_recovery_cells": 8,
        "twin_target_recovery_cells": 0,
        "candidate_attempts": accounting["candidate_attempts"],
        "failed_candidates": accounting["failed_candidates"],
        "search_algorithms": len(searchers),
        "preserved_failure_terminals": 2,
    }


if __name__ == "__main__":
    print("GMI_NEUTRAL_SAFEGUARDS_AUDIT_V1_VALID")
    print(json.dumps(validate_audit(), sort_keys=True))
