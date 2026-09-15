"""
metrics_runtime_v1.py — 11-coordinate capability measurement + budget-flip detection.

Python 3.8 safe. No network. Exact arithmetic via fractions.Fraction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# 11 Coordinates
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Coordinates:
    """Immutable 11-coordinate vector for a capability measurement.

    All coordinates are non-negative Fraction values.
    """
    wall_clock: Fraction          # T — elapsed time (seconds)
    memory_bytes: Fraction        # M — peak resident set size (bytes)
    energy_joules: Fraction       # E — estimated energy (power x time)
    description_length: Fraction  # D — Kolmogorov-complexity proxy (bits)
    update_cost: Fraction         # U — state change cost per learning step
    execution_cost: Fraction      # X — per-inference compute cost
    generalization_gap: Fraction  # G — train/test performance difference [0,1]
    retention_rate: Fraction      # R — performance after n time steps [0,1]
    plasticity: Fraction          # P — rate of adaptation to new tasks [0,1]
    stability: Fraction           # S — resistance to catastrophic forgetting [0,1]
    information_required: Fraction  # I — minimum input bits needed

    def __post_init__(self) -> None:
        """Validate non-negativity of all coordinates."""
        for name in [
            'wall_clock', 'memory_bytes', 'energy_joules', 'description_length',
            'update_cost', 'execution_cost', 'generalization_gap', 'retention_rate',
            'plasticity', 'stability', 'information_required',
        ]:
            val = getattr(self, name)
            if not isinstance(val, Fraction):
                raise TypeError(f"{name} must be Fraction, got {type(val).__name__}")
            if val < 0:
                raise ValueError(f"{name} must be non-negative, got {val}")

    @property
    def aggregate_cost(self) -> Fraction:
        """L1 aggregate cost: sum of cost-contributing coordinates.

        G contributes directly; R, P, S contribute as (1 - val) since
        lower values mean worse outcomes.
        """
        return (
            self.wall_clock
            + self.memory_bytes
            + self.energy_joules
            + self.description_length
            + self.update_cost
            + self.execution_cost
            + self.generalization_gap
            + (Fraction(1) - self.retention_rate)
            + (Fraction(1) - self.plasticity)
            + (Fraction(1) - self.stability)
            + self.information_required
        )

    def as_tuple(self) -> Tuple[Fraction, ...]:
        """Return coordinates as an ordered tuple."""
        return (
            self.wall_clock, self.memory_bytes, self.energy_joules,
            self.description_length, self.update_cost, self.execution_cost,
            self.generalization_gap, self.retention_rate, self.plasticity,
            self.stability, self.information_required,
        )

    def to_dict(self) -> Dict[str, str]:
        """Serialize to dict with string values (for JSON)."""
        return {
            'wall_clock': str(self.wall_clock),
            'memory_bytes': str(self.memory_bytes),
            'energy_joules': str(self.energy_joules),
            'description_length': str(self.description_length),
            'update_cost': str(self.update_cost),
            'execution_cost': str(self.execution_cost),
            'generalization_gap': str(self.generalization_gap),
            'retention_rate': str(self.retention_rate),
            'plasticity': str(self.plasticity),
            'stability': str(self.stability),
            'information_required': str(self.information_required),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> 'Coordinates':
        """Deserialize from dict with string values."""
        return cls(**{k: Fraction(v) for k, v in d.items()})


# ---------------------------------------------------------------------------
# Capability Runtime
# ---------------------------------------------------------------------------

@dataclass
class CapabilityRuntime:
    """A named capability with its 11-coordinate measurement."""
    name: str
    coords: Coordinates

    @classmethod
    def create(
        cls,
        name: str,
        wall_clock: float = 0.0,
        memory_bytes: float = 0.0,
        energy_joules: float = 0.0,
        description_length: float = 0.0,
        update_cost: float = 0.0,
        execution_cost: float = 0.0,
        generalization_gap: float = 0.0,
        retention_rate: float = 1.0,
        plasticity: float = 1.0,
        stability: float = 1.0,
        information_required: float = 0.0,
    ) -> 'CapabilityRuntime':
        """Convenience constructor from numeric values."""
        coords = Coordinates(
            wall_clock=Fraction(wall_clock).limit_denominator(10**9),
            memory_bytes=Fraction(memory_bytes).limit_denominator(10**9),
            energy_joules=Fraction(energy_joules).limit_denominator(10**9),
            description_length=Fraction(description_length).limit_denominator(10**9),
            update_cost=Fraction(update_cost).limit_denominator(10**9),
            execution_cost=Fraction(execution_cost).limit_denominator(10**9),
            generalization_gap=Fraction(generalization_gap).limit_denominator(10**9),
            retention_rate=Fraction(retention_rate).limit_denominator(10**9),
            plasticity=Fraction(plasticity).limit_denominator(10**9),
            stability=Fraction(stability).limit_denominator(10**9),
            information_required=Fraction(information_required).limit_denominator(10**9),
        )
        return cls(name=name, coords=coords)


# ---------------------------------------------------------------------------
# Subadditivity Check
# ---------------------------------------------------------------------------

def check_subadditivity(
    coords_a: Coordinates,
    coords_b: Coordinates,
    coords_ab: Coordinates,
) -> bool:
    """Verify Cost(A+B) <= Cost(A) + Cost(B).

    Returns True if subadditivity holds.
    """
    return coords_ab.aggregate_cost <= coords_a.aggregate_cost + coords_b.aggregate_cost


def combine_coordinates(coords_a: Coordinates, coords_b: Coordinates) -> Coordinates:
    """Combine two capabilities by taking per-coordinate max (shared resource model).

    This models the case where both capabilities share infrastructure and the
    combined cost is bounded by the larger of the two for each coordinate.
    """
    a = coords_a.as_tuple()
    b = coords_b.as_tuple()
    combined = tuple(max(x, y) for x, y in zip(a, b))
    return Coordinates(
        wall_clock=combined[0],
        memory_bytes=combined[1],
        energy_joules=combined[2],
        description_length=combined[3],
        update_cost=combined[4],
        execution_cost=combined[5],
        generalization_gap=combined[6],
        retention_rate=combined[7],
        plasticity=combined[8],
        stability=combined[9],
        information_required=combined[10],
    )


# ---------------------------------------------------------------------------
# Budget-Flip Detection
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BudgetFlip:
    """A detected budget flip: ROI goes negative at a specific budget transition."""
    capability: str
    budget_from: Fraction
    budget_to: Fraction
    roi: Fraction
    performance_from: Fraction
    performance_to: Fraction


class BudgetFlipDetector:
    """Detect budget flips across capability budget profiles.

    A budget flip occurs when increasing the budget allocated to a capability
    causes overall system performance to decrease (negative ROI).
    """

    def compute_roi(
        self,
        perf_from: Fraction,
        perf_to: Fraction,
        budget_from: Fraction,
        budget_to: Fraction,
    ) -> Fraction:
        """Compute ROI between two budget levels.

        ROI = (perf_to - perf_from) / (budget_to - budget_from)
        Returns Fraction(0) if budget levels are identical (degenerate case).
        """
        delta_budget = budget_to - budget_from
        if delta_budget == 0:
            return Fraction(0)
        return (perf_to - perf_from) / delta_budget

    def detect(
        self,
        profiles: Dict[str, List[Tuple[Fraction, Fraction]]],
    ) -> List[BudgetFlip]:
        """Detect budget flips across all capabilities.

        Args:
            profiles: Dict mapping capability name to list of
                      (budget_level, system_performance) tuples,
                      sorted by budget level ascending.

        Returns:
            List of BudgetFlip instances (empty if no flips detected).
        """
        flips: List[BudgetFlip] = []

        for cap_name, budget_perf_pairs in profiles.items():
            if len(budget_perf_pairs) < 2:
                continue

            # Sort by budget level
            sorted_pairs = sorted(budget_perf_pairs, key=lambda p: p[0])

            for i in range(len(sorted_pairs) - 1):
                b_from, p_from = sorted_pairs[i]
                b_to, p_to = sorted_pairs[i + 1]

                roi = self.compute_roi(p_from, p_to, b_from, b_to)

                if roi < 0:
                    flips.append(BudgetFlip(
                        capability=cap_name,
                        budget_from=b_from,
                        budget_to=b_to,
                        roi=roi,
                        performance_from=p_from,
                        performance_to=p_to,
                    ))

        return flips

    def detect_single(
        self,
        cap_name: str,
        budget_perf_pairs: List[Tuple[Fraction, Fraction]],
    ) -> List[BudgetFlip]:
        """Detect flips for a single capability."""
        return self.detect({cap_name: budget_perf_pairs})


# ---------------------------------------------------------------------------
# Finite World (4 capabilities, 3 budget levels)
# ---------------------------------------------------------------------------

def build_finite_world() -> Dict[str, List[Tuple[Fraction, Fraction]]]:
    """Build a finite world with 4 capabilities and 3 budget levels each.

    Returns profiles suitable for BudgetFlipDetector.detect().
    """
    return {
        'inference': [
            (Fraction(1), Fraction(80)),
            (Fraction(2), Fraction(85)),
            (Fraction(3), Fraction(82)),  # flip at level 3
        ],
        'memory_store': [
            (Fraction(1), Fraction(70)),
            (Fraction(2), Fraction(75)),
            (Fraction(3), Fraction(78)),
        ],
        'preprocessing': [
            (Fraction(1), Fraction(60)),
            (Fraction(2), Fraction(65)),
            (Fraction(3), Fraction(68)),
        ],
        'postprocessing': [
            (Fraction(1), Fraction(50)),
            (Fraction(2), Fraction(55)),
            (Fraction(3), Fraction(57)),
        ],
    }


def build_finite_world_coords() -> Dict[str, Dict[Fraction, Coordinates]]:
    """Build 4 capabilities x 3 budget levels with all 11 coordinates measured."""
    return {
        'inference': {
            Fraction(1): Coordinates(
                wall_clock=Fraction('0.5'), memory_bytes=Fraction(1048576),
                energy_joules=Fraction('0.25'), description_length=Fraction(64),
                update_cost=Fraction('0.01'), execution_cost=Fraction('0.10'),
                generalization_gap=Fraction('0.05'), retention_rate=Fraction('0.95'),
                plasticity=Fraction('0.80'), stability=Fraction('0.90'),
                information_required=Fraction(128),
            ),
            Fraction(2): Coordinates(
                wall_clock=Fraction('0.4'), memory_bytes=Fraction(2097152),
                energy_joules=Fraction('0.30'), description_length=Fraction(64),
                update_cost=Fraction('0.01'), execution_cost=Fraction('0.08'),
                generalization_gap=Fraction('0.03'), retention_rate=Fraction('0.96'),
                plasticity=Fraction('0.82'), stability=Fraction('0.91'),
                information_required=Fraction(128),
            ),
            Fraction(3): Coordinates(
                wall_clock=Fraction('0.3'), memory_bytes=Fraction(4194304),
                energy_joules=Fraction('0.40'), description_length=Fraction(64),
                update_cost=Fraction('0.01'), execution_cost=Fraction('0.06'),
                generalization_gap=Fraction('0.04'), retention_rate=Fraction('0.93'),
                plasticity=Fraction('0.78'), stability=Fraction('0.88'),
                information_required=Fraction(128),
            ),
        },
        'memory_store': {
            Fraction(1): Coordinates(
                wall_clock=Fraction('0.2'), memory_bytes=Fraction(2097152),
                energy_joules=Fraction('0.10'), description_length=Fraction(32),
                update_cost=Fraction('0.02'), execution_cost=Fraction('0.05'),
                generalization_gap=Fraction('0.10'), retention_rate=Fraction('0.90'),
                plasticity=Fraction('0.70'), stability=Fraction('0.95'),
                information_required=Fraction(64),
            ),
            Fraction(2): Coordinates(
                wall_clock=Fraction('0.2'), memory_bytes=Fraction(4194304),
                energy_joules=Fraction('0.12'), description_length=Fraction(32),
                update_cost=Fraction('0.02'), execution_cost=Fraction('0.05'),
                generalization_gap=Fraction('0.08'), retention_rate=Fraction('0.92'),
                plasticity=Fraction('0.72'), stability=Fraction('0.96'),
                information_required=Fraction(64),
            ),
            Fraction(3): Coordinates(
                wall_clock=Fraction('0.2'), memory_bytes=Fraction(6291456),
                energy_joules=Fraction('0.15'), description_length=Fraction(32),
                update_cost=Fraction('0.02'), execution_cost=Fraction('0.05'),
                generalization_gap=Fraction('0.06'), retention_rate=Fraction('0.94'),
                plasticity=Fraction('0.74'), stability=Fraction('0.97'),
                information_required=Fraction(64),
            ),
        },
        'preprocessing': {
            Fraction(1): Coordinates(
                wall_clock=Fraction('0.1'), memory_bytes=Fraction(524288),
                energy_joules=Fraction('0.05'), description_length=Fraction(16),
                update_cost=Fraction('0.005'), execution_cost=Fraction('0.03'),
                generalization_gap=Fraction('0.15'), retention_rate=Fraction('0.85'),
                plasticity=Fraction('0.90'), stability=Fraction('0.80'),
                information_required=Fraction(32),
            ),
            Fraction(2): Coordinates(
                wall_clock=Fraction('0.1'), memory_bytes=Fraction(1048576),
                energy_joules=Fraction('0.06'), description_length=Fraction(16),
                update_cost=Fraction('0.005'), execution_cost=Fraction('0.03'),
                generalization_gap=Fraction('0.12'), retention_rate=Fraction('0.87'),
                plasticity=Fraction('0.91'), stability=Fraction('0.82'),
                information_required=Fraction(32),
            ),
            Fraction(3): Coordinates(
                wall_clock=Fraction('0.1'), memory_bytes=Fraction(1572864),
                energy_joules=Fraction('0.07'), description_length=Fraction(16),
                update_cost=Fraction('0.005'), execution_cost=Fraction('0.03'),
                generalization_gap=Fraction('0.10'), retention_rate=Fraction('0.89'),
                plasticity=Fraction('0.92'), stability=Fraction('0.84'),
                information_required=Fraction(32),
            ),
        },
        'postprocessing': {
            Fraction(1): Coordinates(
                wall_clock=Fraction('0.05'), memory_bytes=Fraction(262144),
                energy_joules=Fraction('0.02'), description_length=Fraction(8),
                update_cost=Fraction('0.002'), execution_cost=Fraction('0.02'),
                generalization_gap=Fraction('0.20'), retention_rate=Fraction('0.80'),
                plasticity=Fraction('0.95'), stability=Fraction('0.75'),
                information_required=Fraction(16),
            ),
            Fraction(2): Coordinates(
                wall_clock=Fraction('0.05'), memory_bytes=Fraction(524288),
                energy_joules=Fraction('0.025'), description_length=Fraction(8),
                update_cost=Fraction('0.002'), execution_cost=Fraction('0.02'),
                generalization_gap=Fraction('0.18'), retention_rate=Fraction('0.82'),
                plasticity=Fraction('0.96'), stability=Fraction('0.77'),
                information_required=Fraction(16),
            ),
            Fraction(3): Coordinates(
                wall_clock=Fraction('0.05'), memory_bytes=Fraction(786432),
                energy_joules=Fraction('0.03'), description_length=Fraction(8),
                update_cost=Fraction('0.002'), execution_cost=Fraction('0.02'),
                generalization_gap=Fraction('0.16'), retention_rate=Fraction('0.84'),
                plasticity=Fraction('0.97'), stability=Fraction('0.79'),
                information_required=Fraction(16),
            ),
        },
    }


if __name__ == '__main__':
    # Quick demo
    cap = CapabilityRuntime.create(
        name='demo',
        wall_clock=0.5, memory_bytes=1048576, energy_joules=0.25,
        description_length=64, update_cost=0.01, execution_cost=0.10,
        generalization_gap=0.05, retention_rate=0.95, plasticity=0.80,
        stability=0.90, information_required=128,
    )
    print(f"Capability: {cap.name}")
    print(f"Aggregate cost: {cap.coords.aggregate_cost}")
    print(f"Coordinates: {cap.coords.to_dict()}")
