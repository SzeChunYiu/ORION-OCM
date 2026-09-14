"""GMI Metrics Runtime V1 -- resource coordinate tracking and pricing.

CPython 3.8+ safe.  No network.  All counters are abstract.
"""

from time import perf_counter_ns
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 11 registered coordinates
# ---------------------------------------------------------------------------

BURDEN_COORDINATES: Tuple[str, ...] = (
    "build", "storage", "serve", "update", "verify", "history", "search",
)

DEVELOPMENT_COORDINATES: Tuple[str, ...] = (
    "capability", "plasticity", "retention", "information_required",
)

ALL_COORDINATES: Tuple[str, ...] = BURDEN_COORDINATES + DEVELOPMENT_COORDINATES

DEFAULT_PRICE_VECTOR: Dict[str, float] = {c: 1.0 for c in ALL_COORDINATES}


# ---------------------------------------------------------------------------
# ResourceCounter -- independent per-coordinate counters
# ---------------------------------------------------------------------------

class ResourceCounter:
    """Track 11 independent coordinates with a frozen price vector."""

    def __init__(
        self,
        price_vector: Optional[Dict[str, float]] = None,
    ) -> None:
        self._prices: Dict[str, float] = dict(
            price_vector or DEFAULT_PRICE_VECTOR
        )
        # Validate that all coordinates have a price
        for coord in ALL_COORDINATES:
            if coord not in self._prices:
                raise ValueError(
                    f"Price vector missing coordinate: {coord}"
                )
        # Freeze the price vector
        self._prices = dict(self._prices)
        self._counts: Dict[str, int] = {c: 0 for c in ALL_COORDINATES}

    @property
    def price_vector(self) -> Dict[str, float]:
        return dict(self._prices)

    def increment(self, coordinate: str, amount: int = 1) -> None:
        if coordinate not in ALL_COORDINATES:
            raise ValueError(f"Unknown coordinate: {coordinate}")
        if amount < 0:
            raise ValueError(
                f"Cannot decrement coordinate: {coordinate}"
            )
        self._counts[coordinate] += amount

    def get(self, coordinate: str) -> int:
        if coordinate not in ALL_COORDINATES:
            raise ValueError(f"Unknown coordinate: {coordinate}")
        return self._counts[coordinate]

    def vector(self) -> Dict[str, int]:
        return dict(self._counts)

    def scalarized_cost(self) -> float:
        """L(x) = lambda . x -- the weighted sum under frozen prices."""
        return sum(
            self._prices[c] * self._counts[c] for c in ALL_COORDINATES
        )

    def are_independent(
        self, coord_a: str, coord_b: str, delta_a: int = 1
    ) -> bool:
        """Verify that changing coord_a leaves coord_b unchanged."""
        before = self.get(coord_b)
        self.increment(coord_a, delta_a)
        after = self.get(coord_b)
        self._counts[coord_a] -= delta_a  # undo
        return before == after


# ---------------------------------------------------------------------------
# WallClock -- monotonic non-negative elapsed time
# ---------------------------------------------------------------------------

class WallClock:
    """Monotonic wall-clock using perf_counter_ns.

    Elapsed time is always non-negative by construction.
    """

    def __init__(self) -> None:
        self._start: Optional[int] = None
        self._stop: Optional[int] = None

    def start(self) -> None:
        self._start = perf_counter_ns()
        self._stop = None

    def stop(self) -> None:
        if self._start is None:
            raise RuntimeError("Clock not started")
        self._stop = perf_counter_ns()

    def elapsed_ns(self) -> int:
        if self._start is None:
            raise RuntimeError("Clock not started")
        end = self._stop if self._stop is not None else perf_counter_ns()
        delta = end - self._start
        if delta < 0:
            raise RuntimeError(
                "Negative elapsed time violates monotonicity"
            )
        return delta

    def reset(self) -> None:
        self._start = None
        self._stop = None


# ---------------------------------------------------------------------------
# MemoryTracker -- peak allocation counter
# ---------------------------------------------------------------------------

class MemoryTracker:
    """Abstract peak memory tracker via allocation counter.

    M(t) is the cumulative allocation; M_peak is the max.
    Non-decreasing by construction.
    """

    def __init__(self) -> None:
        self._allocation: int = 0
        self._peak: int = 0

    def allocate(self, units: int) -> None:
        if units < 0:
            raise ValueError("Negative allocation")
        self._allocation += units
        if self._allocation > self._peak:
            self._peak = self._allocation

    def deallocate(self, units: int) -> None:
        if units < 0:
            raise ValueError("Negative deallocation")
        if units > self._allocation:
            raise ValueError("Deallocation exceeds current allocation")
        self._allocation -= units

    @property
    def current(self) -> int:
        return self._allocation

    @property
    def peak(self) -> int:
        return self._peak

    def reset(self) -> None:
        self._allocation = 0
        self._peak = 0


# ---------------------------------------------------------------------------
# EnergyProxy -- compute x time linear model
# ---------------------------------------------------------------------------

class EnergyProxy:
    """Abstract energy: E(alpha, t) = alpha * t.

    Additive over independent workloads: E(a+b, t) = E(a,t) + E(b,t).
    """

    def __init__(self, intensity: float = 1.0) -> None:
        if intensity <= 0:
            raise ValueError("Energy intensity must be positive")
        self._intensity = intensity

    @property
    def intensity(self) -> float:
        return self._intensity

    def compute(self, compute_units: int, wall_ns: int) -> float:
        """E = alpha * compute_units * wall_ns."""
        if compute_units < 0:
            raise ValueError("Negative compute units")
        if wall_ns < 0:
            raise ValueError("Negative wall time")
        return self._intensity * compute_units * wall_ns

    def add(self, e1: float, e2: float) -> float:
        """Additive: E(a+b) = E(a) + E(b)."""
        return e1 + e2


# ---------------------------------------------------------------------------
# Budget-flip falsifier
# ---------------------------------------------------------------------------

def budget_flip_check(
    x: Dict[str, int],
    y: Dict[str, int],
    prices_b1: Dict[str, float],
    prices_b2: Dict[str, float],
) -> bool:
    """Check whether budget change flips the optimal morphology.

    Returns True if the ranking of x vs y reverses between the two
    price vectors (budget-flip detected).

    L_B1(x) = sum_j prices_b1[j] * x[j]
    L_B2(x) = sum_j prices_b2[j] * x[j]
    Flip iff sign(L_B1(x) - L_B1(y)) != sign(L_B2(x) - L_B2(y))
    """
    lx_b1 = sum(prices_b1[c] * x.get(c, 0) for c in ALL_COORDINATES)
    ly_b1 = sum(prices_b1[c] * y.get(c, 0) for c in ALL_COORDINATES)
    lx_b2 = sum(prices_b2[c] * x.get(c, 0) for c in ALL_COORDINATES)
    ly_b2 = sum(prices_b2[c] * y.get(c, 0) for c in ALL_COORDINATES)

    d1 = lx_b1 - ly_b1
    d2 = lx_b2 - ly_b2

    def _sign(v: float) -> int:
        if v > 0:
            return 1
        elif v < 0:
            return -1
        return 0

    return _sign(d1) != _sign(d2)


def reject_negative_budget(
    energy: float, memory: int
) -> Tuple[bool, Optional[str]]:
    """Reject negative energy or memory budgets.

    Returns (accepted, reason).
    """
    if energy < 0:
        return False, "Negative energy budget is undefined"
    if memory < 0:
        return False, "Negative memory budget is undefined"
    return True, None
