#!/usr/bin/env python3
"""Section D V5: statistical phase-boundary uncertainty + prospective scale extrapolation.

The raw uncertainty sample and tiny training receipt are inputs.  This witness
never regenerates the random sample and never refits after seeing held-out data.
"""
from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Dict, Mapping, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
STAGE1_FREEZE = "ab231d78aae98beb679ca0e0ce8c36c4651dc438"
STAGE2_FREEZE = "0a153e972dd920f61f394ce117d5dfa189ad964f"
TRAIN_SHA = "a559ca1ffcb6fded7bc9731ca273b7d04117bb462b7e57016e2e9d6dc477d016"
TRUE_P = Fraction(7, 8)
TRUE_Q = Fraction(32, 9)

COORDINATES = (
    "persistent_cells_single_orientation",
    "migration_ops",
    "key_block_ops",
    "value_block_ops",
)

FROZEN_FITS = {
    "persistent_cells_single_orientation": (1, 0),
    "migration_ops": (2, 0),
    "key_block_ops": (4, 3),
    "value_block_ops": (3, 4),
}

FROZEN_HOLDOUT = {
    17: {
        "persistent_cells_single_orientation": 17,
        "migration_ops": 34,
        "key_block_ops": 71,
        "value_block_ops": 55,
        "continuous_crossover": Fraction(17, 8),
        "first_strict_migration_horizon": 3,
        "m2_stay_key": 142,
        "m2_migrate_value": 144,
        "m3_stay_key": 213,
        "m3_migrate_value": 199,
        "distinct_obligations": 34,
    },
    31: {
        "persistent_cells_single_orientation": 31,
        "migration_ops": 62,
        "key_block_ops": 127,
        "value_block_ops": 97,
        "continuous_crossover": Fraction(31, 15),
        "first_strict_migration_horizon": 3,
        "m2_stay_key": 254,
        "m2_migrate_value": 256,
        "m3_stay_key": 381,
        "m3_migrate_value": 353,
        "distinct_obligations": 62,
    },
}


def frac_json(x: Fraction | None):
    if x is None:
        return None
    return {"numerator": x.numerator, "denominator": x.denominator}


def decimal_fraction(x: Fraction, places: int = 12) -> str:
    getcontext().prec = 50
    value = Decimal(x.numerator) / Decimal(x.denominator)
    return f"{value:.{places}f}"


def unpack_sample() -> Tuple[dict, list[int]]:
    data = json.loads((ROOT / "UNCERTAINTY_SAMPLE_V5.json").read_text(encoding="utf-8"))
    packed = bytes.fromhex(data["packed_bits_hex"])
    assert len(packed) == data["packed_bytes"] == 2048
    assert hashlib.sha256(packed).hexdigest() == data["packed_sha256"]
    bits = []
    for byte in packed:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    assert len(bits) == data["n"] == 16384
    assert sum(bits) == data["ones_count"]
    assert sum(bits[:64]) == data["first_64_ones_count"]
    assert data["authority_freeze_commit"] == STAGE1_FREEZE
    return data, bits


def hoeffding_boundary(bits: Sequence[int], n: int, epsilon: Fraction) -> dict:
    used = list(bits[:n])
    ones = sum(used)
    p_hat = Fraction(ones, n)
    p_lo = max(Fraction(0), p_hat - epsilon)
    p_hi = min(Fraction(1), p_hat + epsilon)

    exponent = Fraction(2 * n) * epsilon * epsilon
    getcontext().prec = 50
    failure_decimal = Decimal(2) * (-Decimal(exponent.numerator) / Decimal(exponent.denominator)).exp()

    if p_hi <= Fraction(1, 2):
        delta_lo = None
        delta_hi = None
        q_lo = None
        q_hi = None
        switches = []
    else:
        delta_hi = 6 * p_hi - 3
        q_lo = Fraction(8, 1) / delta_hi
        if p_lo <= Fraction(1, 2):
            delta_lo = None
            q_hi = None
            switches = list(range(q_lo.numerator // q_lo.denominator + 1, 65))
        else:
            delta_lo = 6 * p_lo - 3
            q_hi = Fraction(8, 1) / delta_lo
            first = q_lo.numerator // q_lo.denominator + 1
            last = q_hi.numerator // q_hi.denominator + 1
            switches = list(range(first, last + 1))

    return {
        "n": n,
        "ones": ones,
        "epsilon": frac_json(epsilon),
        "p_hat": frac_json(p_hat),
        "p_hat_decimal": decimal_fraction(p_hat),
        "p_interval": {"lo": frac_json(p_lo), "hi": frac_json(p_hi)},
        "delta_interval": {"lo": frac_json(delta_lo), "hi": frac_json(delta_hi)},
        "q_interval": {"lo": frac_json(q_lo), "hi": frac_json(q_hi)},
        "q_interval_decimal": {
            "lo": decimal_fraction(q_lo) if q_lo is not None else None,
            "hi": decimal_fraction(q_hi) if q_hi is not None else None,
        },
        "possible_first_strict_integer_switches": switches,
        "hoeffding_exponent": frac_json(exponent),
        "failure_bound_symbolic": "2*exp(-8)" if exponent == 8 else f"2*exp(-{exponent})",
        "failure_bound_decimal": f"{failure_decimal:.15f}",
        "coverage_lower_bound_decimal": f"{(Decimal(1)-failure_decimal):.15f}",
        "failure_bound_lt_0_001": failure_decimal < Decimal("0.001"),
    }


def load_training() -> dict:
    data = json.loads((ROOT / "TRAIN_V5.json").read_text(encoding="utf-8"))
    supplied = data["numeric_receipt_sha256"]
    body = {k: v for k, v in data.items() if k != "numeric_receipt_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    computed = hashlib.sha256(canonical).hexdigest()
    assert supplied == computed == TRAIN_SHA
    assert data["authority_freeze_commit"] == STAGE1_FREEZE
    assert data["training_sizes"] == [2, 3, 4, 5]
    return data


def fit_training(train: dict) -> dict:
    rows = train["rows"]
    by_n = {row["n"]: row for row in rows}
    assert sorted(by_n) == [2, 3, 4, 5]
    fits = {}
    for coordinate in COORDINATES:
        y2 = by_n[2][coordinate]
        y3 = by_n[3][coordinate]
        a = y3 - y2
        b = y2 - 2 * a
        residuals = {str(n): by_n[n][coordinate] - (a * n + b) for n in (4, 5)}
        fits[coordinate] = {
            "a": a,
            "b": b,
            "validation_residuals": residuals,
            "zero_validation_residual": all(v == 0 for v in residuals.values()),
            "matches_second_freeze": (a, b) == FROZEN_FITS[coordinate],
        }
    return fits


def make_relation(n: int, remint: bool = False):
    if remint:
        keys = [f"amber_{n - 1 - i}" for i in range(n)]
        values = [f"quartz_{(i + 5) % n}" for i in range(n)]
    else:
        keys = [f"k{i}" for i in range(n)]
        values = [f"v{i}" for i in range(n)]
    relation = {keys[i]: values[(i + 1) % n] for i in range(n)}
    return relation, keys, values


def inverse(relation: Mapping[str, str]):
    return {v: k for k, v in relation.items()}


def key_lookup(relation: Mapping[str, str], direction: str, token: str):
    if direction == "F":
        return relation[token], 1
    found = None
    ops = 0
    for key, value in relation.items():
        ops += 1
        if value == token:
            found = key
    assert found is not None
    return found, ops


def value_lookup(value_idx: Mapping[str, str], direction: str, token: str):
    if direction == "R":
        return value_idx[token], 1
    found = None
    ops = 0
    for value, key in value_idx.items():
        ops += 1
        if key == token:
            found = value
    assert found is not None
    return found, ops


def migrate(relation: Mapping[str, str]):
    output: Dict[str, str] = {}
    ops = 0
    for key, value in relation.items():
        ops += 1
        output[value] = key
        ops += 1
    return output, ops


def measurement_block(keys: Sequence[str], values: Sequence[str]):
    n = len(keys)
    return (
        ("F", keys[0]),
        ("F", keys[1 % n]),
        ("F", keys[(n - 1) % n]),
        ("R", values[0]),
        ("R", values[1 % n]),
        ("R", values[(n - 1) % n]),
        ("R", values[0]),
    )


def measure_holdout(n: int, remint: bool = False) -> dict:
    assert n in (17, 31), "only preregistered holdouts may be scored"
    relation, keys, values = make_relation(n, remint)
    inv = inverse(relation)

    key_exact = True
    value_exact = True
    key_checks = 0
    value_checks = 0

    for key in keys:
        kout, _ = key_lookup(relation, "F", key)
        vout, _ = value_lookup(inv, "F", key)
        key_exact = key_exact and kout == relation[key]
        value_exact = value_exact and vout == relation[key]
        key_checks += 1
        value_checks += 1
    for value in values:
        kout, _ = key_lookup(relation, "R", value)
        vout, _ = value_lookup(inv, "R", value)
        key_exact = key_exact and kout == inv[value]
        value_exact = value_exact and vout == inv[value]
        key_checks += 1
        value_checks += 1

    key_ops = 0
    value_ops = 0
    for direction, token in measurement_block(keys, values):
        _, ko = key_lookup(relation, direction, token)
        _, vo = value_lookup(inv, direction, token)
        key_ops += ko
        value_ops += vo

    migrated, migration_ops = migrate(relation)
    return {
        "n": n,
        "remint": remint,
        "persistent_cells_single_orientation": n,
        "migration_ops": migration_ops,
        "key_block_ops": key_ops,
        "value_block_ops": value_ops,
        "key_exact": key_exact,
        "value_exact": value_exact,
        "key_checks": key_checks,
        "value_checks": value_checks,
        "migration_exact": migrated == inv,
    }


def crossover_from_observation(obs: Mapping[str, int]) -> dict:
    advantage = obs["key_block_ops"] - obs["value_block_ops"]
    assert advantage > 0
    q = Fraction(obs["migration_ops"], advantage)
    first = q.numerator // q.denominator + 1
    return {
        "advantage_per_block": advantage,
        "continuous_crossover": frac_json(q),
        "first_strict_migration_horizon": first,
        "m2_stay_key": 2 * obs["key_block_ops"],
        "m2_migrate_value": obs["migration_ops"] + 2 * obs["value_block_ops"],
        "m3_stay_key": 3 * obs["key_block_ops"],
        "m3_migrate_value": obs["migration_ops"] + 3 * obs["value_block_ops"],
    }


def compare_observation_to_frozen(obs: Mapping[str, int], n: int, frozen=None) -> bool:
    pred = FROZEN_HOLDOUT[n] if frozen is None else frozen
    for coordinate in COORDINATES:
        if obs[coordinate] != pred[coordinate]:
            return False
    cross = crossover_from_observation(obs)
    if cross["continuous_crossover"] != frac_json(pred["continuous_crossover"]):
        return False
    if cross["first_strict_migration_horizon"] != pred["first_strict_migration_horizon"]:
        return False
    for field in ("m2_stay_key", "m2_migrate_value", "m3_stay_key", "m3_migrate_value"):
        if cross[field] != pred[field]:
            return False
    return True


def build_results() -> dict:
    sample_meta, bits = unpack_sample()
    full = hoeffding_boundary(bits, 16384, Fraction(1, 64))
    small = hoeffding_boundary(bits, 64, Fraction(1, 4))

    full_plo = Fraction(full["p_interval"]["lo"]["numerator"], full["p_interval"]["lo"]["denominator"])
    full_phi = Fraction(full["p_interval"]["hi"]["numerator"], full["p_interval"]["hi"]["denominator"])
    full_qlo = Fraction(full["q_interval"]["lo"]["numerator"], full["q_interval"]["lo"]["denominator"])
    full_qhi = Fraction(full["q_interval"]["hi"]["numerator"], full["q_interval"]["hi"]["denominator"])

    train = load_training()
    fits = fit_training(train)

    holdouts = {}
    holdout_assertions = {}
    for n in (17, 31):
        base = measure_holdout(n, False)
        remint = measure_holdout(n, True)
        cross = crossover_from_observation(base)
        pred = FROZEN_HOLDOUT[n]
        hostile = dict(pred)
        hostile["key_block_ops"] = pred["key_block_ops"] + 1
        holdouts[str(n)] = {
            "frozen_prediction": {
                **{k: v for k, v in pred.items() if k not in ("continuous_crossover",)},
                "continuous_crossover": frac_json(pred["continuous_crossover"]),
            },
            "observed": base,
            "observed_crossover": cross,
            "remint_observed": remint,
            "zero_tolerance_match": compare_observation_to_frozen(base, n),
            "remint_counts_match": all(base[c] == remint[c] for c in COORDINATES),
            "remint_exact": all(remint[x] for x in ("key_exact", "value_exact", "migration_exact")),
            "hostile_altered_prediction_detected": not compare_observation_to_frozen(base, n, hostile),
        }
        holdout_assertions[n] = (
            holdouts[str(n)]["zero_tolerance_match"]
            and holdouts[str(n)]["remint_counts_match"]
            and holdouts[str(n)]["remint_exact"]
            and holdouts[str(n)]["hostile_altered_prediction_detected"]
            and base["key_checks"] == pred["distinct_obligations"]
            and base["value_checks"] == pred["distinct_obligations"]
        )

    sample_sha_ok = sample_meta["packed_sha256"] == hashlib.sha256(bytes.fromhex(sample_meta["packed_bits_hex"])).hexdigest()
    full_contains_p = full_plo <= TRUE_P <= full_phi
    full_contains_q = full_qlo <= TRUE_Q <= full_qhi
    full_inside_3_4 = Fraction(3) < full_qlo <= full_qhi < Fraction(4)
    small_localizes = small["q_interval"]["lo"] is not None and small["q_interval"]["hi"] is not None
    if small_localizes:
        small_qlo = Fraction(small["q_interval"]["lo"]["numerator"], small["q_interval"]["lo"]["denominator"])
        small_qhi = Fraction(small["q_interval"]["hi"]["numerator"], small["q_interval"]["hi"]["denominator"])
        small_inside_3_4 = Fraction(3) < small_qlo <= small_qhi < Fraction(4)
    else:
        small_inside_3_4 = False

    assertions = {
        "U1_full_sample_contains_true_p": full_contains_p,
        "U2_boundary_interval_contains_true_32_over_9": full_contains_q,
        "U3_full_boundary_interval_strictly_inside_3_4": full_inside_3_4,
        "U4_full_interval_localizes_integer_switch_Q4": full["possible_first_strict_integer_switches"] == [4],
        "U5_hoeffding_failure_bound_lt_0_001": full["failure_bound_lt_0_001"] and small["failure_bound_lt_0_001"],
        "U6_small_sample_does_not_localize_to_3_4": not small_inside_3_4,
        "U7_raw_sample_custody": sample_sha_ok and len(bits) == 16384 and sum(bits) == sample_meta["ones_count"],
        "X1_training_restricted_to_2_3_4_5": train["training_sizes"] == [2, 3, 4, 5],
        "X2_affine_fits_validate_and_match_second_freeze": all(
            fits[c]["zero_validation_residual"] and fits[c]["matches_second_freeze"] for c in COORDINATES
        ),
        "X3_second_stage_authority_registered": STAGE2_FREEZE == "0a153e972dd920f61f394ce117d5dfa189ad964f",
        "X4_n17_zero_tolerance_match": holdout_assertions[17],
        "X5_n31_zero_tolerance_match": holdout_assertions[31],
        "X6_n17_crossover_matches": holdouts["17"]["observed_crossover"]["first_strict_migration_horizon"] == 3,
        "X7_n31_crossover_matches": holdouts["31"]["observed_crossover"]["first_strict_migration_horizon"] == 3,
        "X8_all_heldout_distinct_queries_exact": all(
            holdouts[str(n)]["observed"][x]
            for n in (17, 31) for x in ("key_exact", "value_exact", "migration_exact")
        ),
        "X9_remints_preserve_counts_exactness_and_winner": all(
            holdouts[str(n)]["remint_counts_match"] and holdouts[str(n)]["remint_exact"]
            and crossover_from_observation(holdouts[str(n)]["remint_observed"])["first_strict_migration_horizon"] == 3
            for n in (17, 31)
        ),
        "X10_hostile_prediction_mutation_fails_closed": all(
            holdouts[str(n)]["hostile_altered_prediction_detected"] for n in (17, 31)
        ),
    }

    return {
        "authority": {
            "stage1_freeze_commit": STAGE1_FREEZE,
            "stage2_freeze_commit": STAGE2_FREEZE,
            "training_receipt_sha256": TRAIN_SHA,
            "claim_ceiling": [
                "FINITE_PROSPECTIVE_PHASE_BOUNDARY_CONFIDENCE_INTERVAL",
                "FINITE_PROSPECTIVE_OUT_OF_SCALE_PHASE_LAW_EXTRAPOLATION",
                "PARENT_OWNED_CONCENTRATION_INDEXING_AMORTIZATION",
                "NO_REAL_WORLD_COVERAGE_UNIVERSAL_SCALING_OR_REAL_SCALE_CLAIM",
            ],
        },
        "uncertainty": {
            "sample_custody": {
                "n": sample_meta["n"],
                "ones_count": sample_meta["ones_count"],
                "first_64_ones_count": sample_meta["first_64_ones_count"],
                "packed_sha256": sample_meta["packed_sha256"],
            },
            "true_p": frac_json(TRUE_P),
            "true_continuous_boundary": frac_json(TRUE_Q),
            "full_sample": full,
            "small_sample_negative_control": small,
        },
        "extrapolation": {
            "training_sizes": train["training_sizes"],
            "training_rows": train["rows"],
            "fits": fits,
            "holdouts": holdouts,
        },
        "assertions": assertions,
        "all_frozen_predictions_pass": all(assertions.values()),
    }


def main() -> None:
    result = build_results()
    out = ROOT / "RESULT_V5.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_frozen_predictions_pass": result["all_frozen_predictions_pass"],
        "sample_ones": result["uncertainty"]["sample_custody"]["ones_count"],
        "full_q_interval": result["uncertainty"]["full_sample"]["q_interval_decimal"],
        "small_q_interval": result["uncertainty"]["small_sample_negative_control"]["q_interval_decimal"],
        "n17_match": result["extrapolation"]["holdouts"]["17"]["zero_tolerance_match"],
        "n31_match": result["extrapolation"]["holdouts"]["31"]["zero_tolerance_match"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
