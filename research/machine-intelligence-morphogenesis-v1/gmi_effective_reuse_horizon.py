"""Exact calibration for GMI Effective Reuse Horizon Law v1.

Parent-owned geometric-survival/amortization arithmetic only.
"""

from __future__ import annotations


def effective_reuse_horizon(horizon: int, invalidation_hazard: float) -> float:
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    q = invalidation_hazard
    if not 0.0 <= q <= 1.0:
        raise ValueError("invalidation_hazard must be in [0,1]")
    if horizon == 0:
        return 0.0
    if q == 0.0:
        return float(horizon)
    return (1.0 - (1.0 - q) ** horizon) / q


def expected_net_gain(
    *,
    build_cost: float,
    maintenance_cost: float,
    per_use_saving: float,
    horizon: int,
    invalidation_hazard: float,
) -> float:
    if min(build_cost, maintenance_cost, per_use_saving) < 0:
        raise ValueError("costs/savings must be non-negative")
    eta = effective_reuse_horizon(horizon, invalidation_hazard)
    return eta * per_use_saving - build_cost - maintenance_cost


def infinite_horizon_useful_reuses(invalidation_hazard: float) -> float:
    q = invalidation_hazard
    if not 0.0 <= q <= 1.0:
        raise ValueError("invalidation_hazard must be in [0,1]")
    if q == 0.0:
        return float("inf")
    return 1.0 / q


def can_ever_pay_under_one_shot_hazard(
    *,
    build_cost: float,
    maintenance_cost: float,
    per_use_saving: float,
    invalidation_hazard: float,
) -> bool:
    if min(build_cost, maintenance_cost, per_use_saving) < 0:
        raise ValueError("costs/savings must be non-negative")
    eta_inf = infinite_horizon_useful_reuses(invalidation_hazard)
    if eta_inf == float("inf"):
        return per_use_saving > 0.0
    return eta_inf * per_use_saving > build_cost + maintenance_cost


def calibration_receipt() -> dict:
    cases = []
    for q in (0.0, 0.05, 0.2, 1.0):
        cases.append(
            {
                "H": 20,
                "q": q,
                "eta": effective_reuse_horizon(20, q),
                "net_gain_A10_M0_D1": expected_net_gain(
                    build_cost=10.0,
                    maintenance_cost=0.0,
                    per_use_saving=1.0,
                    horizon=20,
                    invalidation_hazard=q,
                ),
                "eta_infinity": infinite_horizon_useful_reuses(q),
                "ever_pays_A10_M0_D1": can_ever_pay_under_one_shot_hazard(
                    build_cost=10.0,
                    maintenance_cost=0.0,
                    per_use_saving=1.0,
                    invalidation_hazard=q,
                ),
            }
        )
    return {
        "schema": "GMIEffectiveReuseHorizonCalibrationV1",
        "cases": cases,
        "key_boundaries": {
            "q0_H20_eta": effective_reuse_horizon(20, 0.0),
            "q005_H20_eta": effective_reuse_horizon(20, 0.05),
            "q02_H20_eta": effective_reuse_horizon(20, 0.2),
            "q02_eta_infinity": infinite_horizon_useful_reuses(0.2),
            "A10_D1_q02_ever_pays": can_ever_pay_under_one_shot_hazard(
                build_cost=10.0,
                maintenance_cost=0.0,
                per_use_saving=1.0,
                invalidation_hazard=0.2,
            ),
            "A4_D1_q02_ever_pays": can_ever_pay_under_one_shot_hazard(
                build_cost=4.0,
                maintenance_cost=0.0,
                per_use_saving=1.0,
                invalidation_hazard=0.2,
            ),
        },
        "terminal": "GMI_EFFECTIVE_REUSE_HORIZON_FINITE_CALIBRATION_GREEN_V1",
        "claim_boundary": "Geometric one-shot invalidation model only; rebuild/renewal requires another parent model.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(calibration_receipt(), indent=2, sort_keys=True))
