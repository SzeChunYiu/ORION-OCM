#!/usr/bin/env python3
"""Fresh finite tests of a frozen corrected descriptor theorem and price law.

Does not repair or overwrite V1 predictions. No held-family or real transfer claim.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PARENT = ROOT / "run_gmi_primitive_closure_v1.py"
PARENT_HASH = "875c51fc49e6ca323eb6732095a435f55a18c20d0d5ac613ff1f5c535f620a4c"
FREEZE = ROOT / "GMI_CLOSURE_SUCCESSOR_FREEZE_V1.json"
SPEC = {
    "parent_source_sha256": PARENT_HASH,
    "parent_freeze_commit": "66aa16fbf4f390f4afac56e46d8971768e27f9ea",
    "failed_atom": "Balance plus coordinate influence determines one exact cost/feasibility label",
    "successor": "A descriptor collision requires a set of possible labels or extra information, not an invented scalar prediction. Computing that set without outcome access remains a separate open estimator problem.",
    "descriptor_theorem": "On a finite uniform collection, the minimum errors of a deterministic descriptor-only predictor equal N-sum_z max_y count(z,y). Exact auxiliary labels require at least ceil(log2 max_z number_of_distinct_labels(z)) worst-case fixed bits, and that many suffice when the descriptor is shared.",
    "fresh_descriptor_scope": "All 9330 assignments of binary descriptors and ternary labels to N=1..5 cases; compare with all 9 descriptor-only predictors. Not previously used Boolean functions and not an empirical holdout.",
    "price_theorem": "For three-input select, with NOT=AND=OR=2 and XOR=k>0, minimum formula cost is min(2+2*k,8). This is a formula-tree statement, not shared-DAG or hardware optimality.",
    "fresh_prices": "NOT=AND=OR=22; XOR=m for m=1..88 excluding multiples of 11. Eighty disjoint noninteger normalized price cells. Predict min(22+2*m,88).",
    "proof_parent": "V1 certified all 256 formula optima at k=3. A selector is not affine, so a formula needs AND/OR; non-XOR cost is an even number at least 2. For zero XORs the k=3 certificate gives cost>=8; one XOR gives non-XOR cost>=6; two or more XORs give cost>=2+2*k for k<=3. Monotonicity proves the k>=3 side. Two explicit constructions attain the bound.",
    "kill_conditions": ["any predictor-error identity mismatch", "any incorrect residual code", "any set coverage miss", "any frozen price miss", "any certificate verification failure", "parent/source hash mismatch"],
    "status": "FROZEN_BEFORE_SUCCESSOR_EXECUTION",
    "scope_ceiling": "Corrected finite information theorem and exact operator-price calibration only. Known-family and real-regime closure remain blocked."
}


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")


def freeze() -> dict:
    return {"specification": SPEC, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def run() -> None:
    if hashlib.sha256(PARENT.read_bytes()).hexdigest() != PARENT_HASH:
        raise ValueError("Parent source changed")
    if json.loads(FREEZE.read_text()) != freeze():
        raise ValueError("Successor source/freeze mismatch")
    import run_gmi_primitive_closure_v1 as parent
    maps = predictor_evaluations = identity_failures = code_failures = coverage_misses = 0
    for n in range(1, 6):
        for descriptors in product(range(2), repeat=n):
            for labels in product(range(3), repeat=n):
                groups = defaultdict(list)
                for z, label in zip(descriptors, labels):
                    groups[z].append(label)
                predicted_errors = n - sum(max(Counter(values).values()) for values in groups.values())
                brute_errors = n
                for predictor in product(range(3), repeat=2):
                    brute_errors = min(brute_errors, sum(predictor[z] != label for z, label in zip(descriptors, labels)))
                    predictor_evaluations += 1
                identity_failures += brute_errors != predicted_errors
                cardinality = max(len(set(values)) for values in groups.values())
                bits = (cardinality - 1).bit_length()
                code_failures += (1 << bits) < cardinality or (bits > 0 and (1 << (bits - 1)) >= cardinality)
                codebooks = {z: sorted(set(values)) for z, values in groups.items()}
                for z, label in zip(descriptors, labels):
                    code = codebooks[z].index(label)
                    code_failures += codebooks[z][code] != label or code >= (1 << bits)
                    coverage_misses += label not in codebooks[z]
                maps += 1
    certificates, price_rows = [], []
    totals = Counter()
    target = sum((((x >> 1) & 1) if x & 1 else ((x >> 2) & 1)) << x for x in range(8))
    for m in range(1, 89):
        if m % 11 == 0:
            continue
        certificate = parent.synthesize(3, {"not": 22, "and": 22, "or": 22, "xor": m})
        verified = parent.certify(certificate)
        totals.update(verified)
        totals["relaxations"] += certificate["relaxations"]
        certificates.append(certificate)
        price_rows.append({"xor_price": m, "predicted": min(22 + 2 * m, 88), "observed": certificate["costs"][target]})
    misses = sum(row["predicted"] != row["observed"] for row in price_rows)
    receipt = {
        "status": "EXACT_SUCCESSOR_FINITE_GREEN" if not any((identity_failures, code_failures, coverage_misses, misses)) else "EXACT_SUCCESSOR_FINITE_RED",
        "source_sha256": freeze()["source_sha256"],
        "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(),
        "descriptor_maps": maps, "brute_predictor_evaluations": predictor_evaluations,
        "error_identity_failures": identity_failures, "code_failures": code_failures, "coverage_misses": coverage_misses,
        "fresh_price_cells": len(price_rows), "function_price_optima": 256 * len(price_rows),
        "price_predictions": price_rows, "price_prediction_misses": misses, "certificate_checks": dict(totals),
        "certificate_canonical_sha256": parent.digest(certificates),
        "original_descriptor_prediction": "FALSIFIED_UNCHANGED",
        "cheap_pre_outcome_descriptor_estimator": "OPEN_BLOCKING",
        "protected_empirical_or_held_family_runs": 0,
        "global_terminals": {"NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE": False, "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE": False}
    }
    write_new(ROOT / "GMI_CLOSURE_SUCCESSOR_CERTIFICATES_V1.json", certificates)
    write_new(ROOT / "GMI_CLOSURE_SUCCESSOR_RECEIPT_V1.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if receipt["status"].endswith("RED"):
        raise SystemExit(1)


if __name__ == "__main__":
    if sys.argv[1:] == ["--freeze"]:
        write_new(FREEZE, freeze())
        print(FREEZE.read_text())
    elif sys.argv[1:] == ["--run"]:
        run()
    else:
        raise SystemExit("Use --freeze before committing source and freeze; then --run in a fresh directory.")
