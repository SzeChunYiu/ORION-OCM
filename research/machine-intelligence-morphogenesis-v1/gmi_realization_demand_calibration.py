"""Exact DS-E0 calibration for selected realization-demand coordinates.

The task is an exact finite parity obligation over `r` relevant binary inputs.
Two semantically exact realizations are compared:

1. MATERIALIZED_TABLE
   - construct all 2**r input/output rows;
   - query in one counted lookup;
   - after a registered rule-version change, rebuild all rows.

2. COMPOSITIONAL_PARITY
   - construct an r-input parity composition;
   - query with r counted primitive reads/combines;
   - a local registered rule-version update costs one counted local update.

The formulas are intentionally simple and parent-owned. They calibrate only:

* semantic equivalence held fixed;
* semantic size/representation pressure via r;
* reuse horizon H;
* drift/update count U;
* complete build + serve + update accounting.

No machine-intelligence novelty follows from this toy.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemandWorld:
    relevant_bits: int
    query_horizon: int
    rule_updates: int

    def __post_init__(self) -> None:
        if self.relevant_bits < 1:
            raise ValueError("relevant_bits must be >= 1")
        if self.query_horizon < 0 or self.rule_updates < 0:
            raise ValueError("query_horizon and rule_updates must be non-negative")


@dataclass(frozen=True)
class CostReceipt:
    morphology: str
    build: int
    serve: int
    update: int

    @property
    def total(self) -> int:
        return self.build + self.serve + self.update


def materialized_table(world: DemandWorld) -> CostReceipt:
    rows = 2 ** world.relevant_bits
    return CostReceipt(
        morphology="MATERIALIZED_TABLE",
        build=rows,
        serve=world.query_horizon,
        update=world.rule_updates * rows,
    )


def compositional_parity(world: DemandWorld) -> CostReceipt:
    return CostReceipt(
        morphology="COMPOSITIONAL_PARITY",
        build=world.relevant_bits,
        serve=world.query_horizon * world.relevant_bits,
        update=world.rule_updates,
    )


def winner(world: DemandWorld) -> tuple[str, ...]:
    receipts = (materialized_table(world), compositional_parity(world))
    best = min(r.total for r in receipts)
    return tuple(sorted(r.morphology for r in receipts if r.total == best))


def horizon_crossover(relevant_bits: int, rule_updates: int) -> float | None:
    """Solve table total == compositional total as a real-valued H.

    Table:
        2^r + H + U 2^r
    Compositional:
        r + Hr + U

    Therefore for r > 1:
        H* = ((1+U)2^r - r - U) / (r - 1)
    """

    if relevant_bits < 1 or rule_updates < 0:
        raise ValueError("invalid world coordinates")
    if relevant_bits == 1:
        return None
    numerator = (1 + rule_updates) * (2 ** relevant_bits) - relevant_bits - rule_updates
    return numerator / (relevant_bits - 1)


def calibration_receipt() -> dict:
    # r=4, no drift: crossover is exactly H*=4.
    no_drift_short = DemandWorld(relevant_bits=4, query_horizon=2, rule_updates=0)
    no_drift_long = DemandWorld(relevant_bits=4, query_horizon=8, rule_updates=0)

    # r=4, U=2: drift pushes table crossover to H*=14.
    drift_mid = DemandWorld(relevant_bits=4, query_horizon=8, rule_updates=2)
    drift_long = DemandWorld(relevant_bits=4, query_horizon=20, rule_updates=2)

    cases = {
        "no_drift_short": no_drift_short,
        "no_drift_long": no_drift_long,
        "drift_mid": drift_mid,
        "drift_long": drift_long,
    }

    rows = {}
    for name, world in cases.items():
        table = materialized_table(world)
        comp = compositional_parity(world)
        rows[name] = {
            "world": {
                "relevant_bits": world.relevant_bits,
                "query_horizon": world.query_horizon,
                "rule_updates": world.rule_updates,
            },
            "MATERIALIZED_TABLE": {
                "build": table.build,
                "serve": table.serve,
                "update": table.update,
                "total": table.total,
            },
            "COMPOSITIONAL_PARITY": {
                "build": comp.build,
                "serve": comp.serve,
                "update": comp.update,
                "total": comp.total,
            },
            "winner": winner(world),
        }

    return {
        "schema": "GMIRealizationDemandCalibrationReceiptV1",
        "semantic_obligation": "exact parity over r relevant binary inputs",
        "semantically_exact_realizations": [
            "MATERIALIZED_TABLE",
            "COMPOSITIONAL_PARITY",
        ],
        "demand_coordinates_exercised": [
            "sigma/relevant semantic input dimension",
            "eta/effective reuse horizon",
            "nu/rule-update drift count",
        ],
        "r4_no_drift_crossover": horizon_crossover(4, 0),
        "r4_u2_crossover": horizon_crossover(4, 2),
        "cases": rows,
        "terminal": "REALIZATION_DEMAND_SIGNATURE_SUPPORTED_AT_FINITE_CALIBRATION_SCOPE",
        "claim_boundary": (
            "Exact authored calibration only. The phase law follows elementary "
            "materialization/amortization arithmetic and is parent-owned."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(calibration_receipt(), indent=2, sort_keys=True))
