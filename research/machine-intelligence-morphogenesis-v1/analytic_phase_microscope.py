#!/usr/bin/env python3
"""Tiny exact/calculable phase-boundary calibration for two morphology families.

This is lifecycle economics, not a GMI novelty claim. It calibrates the idea that
morphology frontier membership can reverse as reuse horizon and revision burden
change.
"""

from dataclasses import dataclass
from fractions import Fraction
import json


@dataclass(frozen=True)
class LinearLifecycle:
    build: Fraction
    per_use: Fraction
    per_revision: Fraction

    def cost(self, horizon: int, revisions: int) -> Fraction:
        return self.build + self.per_use * horizon + self.per_revision * revisions


def crossover_horizon(a: LinearLifecycle, b: LinearLifecycle, revisions: int):
    """Solve C_a(H,r) = C_b(H,r); return None if parallel/no finite crossing."""
    delta_per_use = a.per_use - b.per_use
    fixed = (a.build - b.build) + (a.per_revision - b.per_revision) * revisions
    if delta_per_use == 0:
        return None
    return -fixed / delta_per_use


def run() -> dict:
    # Illustrative neural-like amortizer versus explicit/search-heavy form.
    # Values are registered toy coordinates, not measured empirical constants.
    parametric = LinearLifecycle(Fraction(100), Fraction(1), Fraction(20))
    explicit = LinearLifecycle(Fraction(10), Fraction(5), Fraction(2))

    rows = []
    for r in (0, 1, 2, 5, 10):
        h_star = crossover_horizon(parametric, explicit, r)
        assert h_star is not None
        # Here: 90 - 4H + 18r = 0 -> H* = 22.5 + 4.5r.
        expected = Fraction(45 + 9 * r, 2)
        assert h_star == expected
        below = max(0, int(h_star) - 1)
        above = int(h_star) + 2
        rows.append(
            {
                "revisions": r,
                "crossover_horizon": str(h_star),
                "parametric_wins_below": parametric.cost(below, r) < explicit.cost(below, r),
                "parametric_wins_above": parametric.cost(above, r) < explicit.cost(above, r),
                "costs_below": {
                    "H": below,
                    "parametric": str(parametric.cost(below, r)),
                    "explicit": str(explicit.cost(below, r)),
                },
                "costs_above": {
                    "H": above,
                    "parametric": str(parametric.cost(above, r)),
                    "explicit": str(explicit.cost(above, r)),
                },
            }
        )
        assert not rows[-1]["parametric_wins_below"]
        assert rows[-1]["parametric_wins_above"]

    return {
        "terminal": "LINEAR_LIFECYCLE_PHASE_BOUNDARY_CALIBRATED",
        "model": "C_m(H,r)=build_m + H*use_m + r*revision_m",
        "parametric_toy": {"build": "100", "use": "1", "revision": "20"},
        "explicit_toy": {"build": "10", "use": "5", "revision": "2"},
        "boundary": "H*(r)=45/2 + (9/2)r",
        "rows": rows,
        "interpretation": (
            "With high upfront cost but lower per-use cost, the parametric toy wins "
            "only after a reuse-horizon crossover. Higher revision burden shifts the "
            "crossover outward because this toy assigns higher revision cost to it."
        ),
        "claim_boundary": (
            "Arithmetic lifecycle-economics calibration only. Parameters are toy values; "
            "this does not establish an empirical neural-vs-symbolic phase law."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
