#!/usr/bin/env python3
"""Exact finite epistemic/aleatoric variance-decomposition oracle for #750.

The checker uses fractions only.  It proves nothing by floating-point sampling: the P1
mathematics lives in PROOFS_V1.md, while this program provides finite exact controls,
a non-identifiability witness, hostile fail-closed checks, and a deterministic receipt.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "UNCERTAINTY_CONTRACT_V1.json"
PROOFS_PATH = ROOT / "PROOFS_V1.md"
README_PATH = ROOT / "README.md"

EXACT_RE = re.compile(r"^-?[0-9]+(?:/[0-9]+)?$")
CLAIM_CEILING = "EXACT_EPISTEMIC_ALEATORIC_SEPARATION_FOR_REGISTERED_FINITE_LATENT_MODELS"


class ContractError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def fail(code: str) -> None:
    raise ContractError(code)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_exact(value) -> Fraction:
    """Accept only integers or explicit integer/rational strings, never floats/decimals."""
    if isinstance(value, bool) or isinstance(value, float):
        fail("NON_EXACT_RATIONAL")
    if isinstance(value, int):
        return Fraction(value, 1)
    if not isinstance(value, str) or not EXACT_RE.fullmatch(value):
        fail("NON_EXACT_RATIONAL")
    try:
        if "/" in value:
            numerator, denominator = value.split("/", 1)
            denominator_int = int(denominator)
            if denominator_int == 0:
                fail("NON_EXACT_RATIONAL")
            return Fraction(int(numerator), denominator_int)
        return Fraction(int(value), 1)
    except (ValueError, ZeroDivisionError):
        fail("NON_EXACT_RATIONAL")
    raise AssertionError("unreachable")


def fmt(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def parse_kernel(raw_kernel) -> dict[Fraction, Fraction]:
    if not isinstance(raw_kernel, dict) or not raw_kernel:
        fail("INVALID_OUTCOME_KERNEL")
    kernel: dict[Fraction, Fraction] = {}
    total = Fraction(0)
    for raw_outcome, raw_mass in raw_kernel.items():
        outcome = parse_exact(raw_outcome)
        if outcome in kernel:
            fail("DUPLICATE_RATIONAL_OUTCOME")
        mass = parse_exact(raw_mass)
        if mass < 0:
            fail("INVALID_OUTCOME_KERNEL")
        kernel[outcome] = mass
        total += mass
    if total != 1:
        fail("INVALID_OUTCOME_KERNEL")
    return kernel


def parse_model(model) -> list[tuple[str, Fraction, dict[Fraction, Fraction]]]:
    if not isinstance(model, dict) or model.get("latent_semantics") != "registered":
        fail("CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS")
    raw_latent = model.get("latent")
    if not isinstance(raw_latent, list) or not raw_latent:
        fail("INVALID_LATENT_WEIGHTS")

    seen_ids: set[str] = set()
    parsed: list[tuple[str, Fraction, dict[Fraction, Fraction]]] = []
    total_weight = Fraction(0)
    for entry in raw_latent:
        if not isinstance(entry, dict):
            fail("INVALID_LATENT_WEIGHTS")
        latent_id = entry.get("id")
        if not isinstance(latent_id, str) or not latent_id:
            fail("INVALID_LATENT_WEIGHTS")
        if latent_id in seen_ids:
            fail("DUPLICATE_LATENT_ID")
        seen_ids.add(latent_id)

        weight = parse_exact(entry.get("weight"))
        if weight < 0:
            fail("INVALID_LATENT_WEIGHTS")
        kernel = parse_kernel(entry.get("kernel"))
        parsed.append((latent_id, weight, kernel))
        total_weight += weight

    if total_weight != 1:
        fail("INVALID_LATENT_WEIGHTS")
    return parsed


def decomposition(model) -> dict:
    parsed = parse_model(model)

    conditional_means: dict[str, Fraction] = {}
    conditional_variances: dict[str, Fraction] = {}
    marginal: dict[Fraction, Fraction] = defaultdict(Fraction)

    for latent_id, weight, kernel in parsed:
        mean = sum((outcome * mass for outcome, mass in kernel.items()), Fraction(0))
        variance = sum(((outcome - mean) ** 2 * mass for outcome, mass in kernel.items()), Fraction(0))
        conditional_means[latent_id] = mean
        conditional_variances[latent_id] = variance
        for outcome, mass in kernel.items():
            marginal[outcome] += weight * mass

    mu = sum(
        (weight * conditional_means[latent_id] for latent_id, weight, _ in parsed),
        Fraction(0),
    )
    aleatoric = sum(
        (weight * conditional_variances[latent_id] for latent_id, weight, _ in parsed),
        Fraction(0),
    )
    epistemic_mean = sum(
        (weight * (conditional_means[latent_id] - mu) ** 2 for latent_id, weight, _ in parsed),
        Fraction(0),
    )
    total = sum(((outcome - mu) ** 2 * mass for outcome, mass in marginal.items()), Fraction(0))

    if total != aleatoric + epistemic_mean:
        fail("TOTAL_VARIANCE_IDENTITY_VIOLATED")

    return {
        "mu": mu,
        "aleatoric": aleatoric,
        "epistemic_mean": epistemic_mean,
        "total": total,
        "conditional_means": conditional_means,
        "conditional_variances": conditional_variances,
        "marginal": dict(marginal),
    }


def canonical_result(result: dict) -> dict:
    return {
        "mu": fmt(result["mu"]),
        "aleatoric": fmt(result["aleatoric"]),
        "epistemic_mean": fmt(result["epistemic_mean"]),
        "total": fmt(result["total"]),
        "marginal": {
            fmt(outcome): fmt(mass)
            for outcome, mass in sorted(result["marginal"].items())
            if mass != 0
        },
    }


def expected_result(raw: dict) -> dict:
    expected_marginal: dict[Fraction, Fraction] = {}
    for raw_outcome, raw_mass in raw["marginal"].items():
        outcome = parse_exact(raw_outcome)
        if outcome in expected_marginal:
            fail("DUPLICATE_RATIONAL_OUTCOME")
        expected_marginal[outcome] = parse_exact(raw_mass)
    return {
        "mu": parse_exact(raw["mu"]),
        "aleatoric": parse_exact(raw["aleatoric"]),
        "epistemic_mean": parse_exact(raw["epistemic_mean"]),
        "total": parse_exact(raw["total"]),
        "marginal": expected_marginal,
    }


def results_equal(actual: dict, expected: dict) -> bool:
    return all(actual[key] == expected[key] for key in ("mu", "aleatoric", "epistemic_mean", "total", "marginal"))


def half_grid_kernels() -> list[dict[str, str]]:
    """All exact distributions on {-1,0,1} with masses in {0,1/2,1}."""
    kernels: list[dict[str, str]] = []
    for a in range(3):
        for b in range(3 - a):
            c = 2 - a - b
            masses = (Fraction(a, 2), Fraction(b, 2), Fraction(c, 2))
            kernel = {
                outcome: fmt(mass)
                for outcome, mass in zip(("-1", "0", "1"), masses)
                if mass != 0
            }
            kernels.append(kernel)
    return kernels


def exhaustive_identity_and_collisions() -> tuple[int, int]:
    kernels = half_grid_kernels()
    weight_pairs = [(Fraction(0), Fraction(1)), (Fraction(1, 2), Fraction(1, 2)), (Fraction(1), Fraction(0))]
    by_marginal: dict[tuple[tuple[str, str], ...], set[tuple[str, str]]] = defaultdict(set)
    checked = 0

    for (w0, w1), kernel0, kernel1 in itertools.product(weight_pairs, kernels, kernels):
        model = {
            "latent_semantics": "registered",
            "latent": [
                {"id": "theta0", "weight": fmt(w0), "kernel": kernel0},
                {"id": "theta1", "weight": fmt(w1), "kernel": kernel1},
            ],
        }
        result = decomposition(model)
        checked += 1
        canonical = canonical_result(result)
        marginal_key = tuple(sorted(canonical["marginal"].items()))
        by_marginal[marginal_key].add((canonical["aleatoric"], canonical["epistemic_mean"]))

    collisions = sum(1 for decompositions in by_marginal.values() if len(decompositions) > 1)
    return checked, collisions


def main() -> int:
    failures: list[str] = []
    contract = load_json(CONTRACT_PATH)

    if contract.get("schema") != "GMI_UNCERTAINTY_DECOMPOSITION_V1":
        failures.append("contract schema mismatch")
    if contract.get("claim_ceiling") != CLAIM_CEILING:
        failures.append("claim ceiling mismatch")

    proofs_text = PROOFS_PATH.read_text(encoding="utf-8")
    for theorem in ("UD-T1", "UD-T2", "UD-T3", "UD-T4"):
        if theorem not in proofs_text:
            failures.append(f"missing proof anchor {theorem}")

    case_results: dict[str, dict] = {}
    for case in contract.get("cases", []):
        case_id = case.get("id", "<missing>")
        try:
            actual = decomposition(case["model"])
            expected = expected_result(case["expected"])
            if not results_equal(actual, expected):
                failures.append(
                    f"case {case_id}: expected {canonical_result(expected)} got {canonical_result(actual)}"
                )
            case_results[case_id] = actual
        except (KeyError, ContractError) as exc:
            failures.append(f"case {case_id}: unexpected failure {exc}")

    pair = contract.get("nonidentifiability_pair", {})
    left_id = pair.get("left_case")
    right_id = pair.get("right_case")
    if left_id not in case_results or right_id not in case_results:
        failures.append("non-identifiability pair missing case result")
    else:
        left = case_results[left_id]
        right = case_results[right_id]
        if left["marginal"] != right["marginal"]:
            failures.append("UD-T2: full predictive marginals are not identical")
        if (left["aleatoric"], left["epistemic_mean"]) == (right["aleatoric"], right["epistemic_mean"]):
            failures.append("UD-T2: decomposition did not differ across identical marginals")

    narrow = case_results.get("identical_means_different_higher_moments")
    if narrow is None:
        failures.append("UD-T3 control missing")
    else:
        means = set(narrow["conditional_means"].values())
        if narrow["epistemic_mean"] != 0 or len(means) != 1:
            failures.append("UD-T3: expected identical conditional means and epistemic_mean=0")
        model = next(
            case["model"] for case in contract["cases"]
            if case["id"] == "identical_means_different_higher_moments"
        )
        kernels = [entry["kernel"] for entry in model["latent"]]
        if kernels[0] == kernels[1]:
            failures.append("UD-T3: higher-moment/model-uncertainty control is vacuous")

    hostile_passes = 0
    for hostile in contract.get("hostiles", []):
        hostile_id = hostile.get("id", "<missing>")
        expected_code = hostile.get("error")
        try:
            decomposition(hostile.get("model"))
            failures.append(f"hostile {hostile_id}: unexpectedly accepted")
        except ContractError as exc:
            if exc.code != expected_code:
                failures.append(f"hostile {hostile_id}: expected {expected_code}, got {exc.code}")
            else:
                hostile_passes += 1

    exhaustive_checked, collision_marginals = exhaustive_identity_and_collisions()
    if exhaustive_checked != 108:
        failures.append(f"exhaustive census drifted: {exhaustive_checked} != 108")
    if collision_marginals < 1:
        failures.append("exhaustive grid found no marginal with multiple decompositions")

    readme = README_PATH.read_text(encoding="utf-8")
    for forbidden in contract.get("forbidden_claims", []):
        if forbidden not in readme:
            failures.append(f"README missing forbidden-claim ceiling {forbidden}")

    receipt = {
        "schema": "GMI_UNCERTAINTY_DECOMPOSITION_RECEIPT_V1",
        "verdict": "PASS" if not failures else "FAIL",
        "claim_ceiling": CLAIM_CEILING,
        "cases_checked": len(contract.get("cases", [])),
        "hostiles_checked": len(contract.get("hostiles", [])),
        "hostiles_passed": hostile_passes,
        "exhaustive_models_checked": exhaustive_checked,
        "exhaustive_marginals_with_multiple_decompositions": collision_marginals,
        "nonidentifiability_full_marginal_equal": (
            left_id in case_results
            and right_id in case_results
            and case_results[left_id]["marginal"] == case_results[right_id]["marginal"]
        ),
        "input_sha256": {
            CONTRACT_PATH.name: sha256(CONTRACT_PATH),
            PROOFS_PATH.name: sha256(PROOFS_PATH),
            README_PATH.name: sha256(README_PATH),
        },
        "failures": failures,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
