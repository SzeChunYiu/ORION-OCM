# Metrics Runtime v1 — CORE

Read-first index for the metrics-runtime capsule.

## What This Capsule Provides

11-coordinate measurement system for capability runtime costs: wall-clock, memory, energy, description length, update cost, execution cost, generalization gap, retention rate, plasticity, stability, and information required.

Includes budget-flip detection: identifies when investing more resources in a capability causes overall system performance to decrease (negative ROI).

## Architecture

```
CORE.md                          ← you are here
METRICS_RUNTIME_THEOREM_V1.md    ← formal theorem + proofs
metrics_runtime_v1.py            ← implementation (all 11 coords, budget-flip detector)
test_metrics_runtime_v1.py       ← 20+ tests
MANIFEST.json                    ← capsule metadata
```

## Quick Start

```python
from metrics_runtime_v1 import CapabilityRuntime, BudgetFlipDetector

# Create a capability with measured coordinates
cap = CapabilityRuntime(
    name="inference",
    wall_clock=0.5,       # seconds
    memory_bytes=1048576,  # 1 MiB
    energy_joules=0.25,
    description_length=64,
    update_cost=0.01,
    execution_cost=0.10,
    generalization_gap=0.05,
    retention_rate=0.95,
    plasticity=0.8,
    stability=0.9,
    information_required=128,
)

# Detect budget flips across capability profiles
detector = BudgetFlipDetector()
profiles = {...}  # capability -> {budget_level: coords}
flips = detector.detect(profiles)
```

## Tests

```bash
python3 -I -B research/gmi-metrics-runtime-v1/test_metrics_runtime_v1.py -v
```

## Key Invariants

1. All coordinates are non-negative
2. Subadditivity: cost(A+B) <= cost(A) + cost(B)
3. At most one budget-flip point per capability per budget range
4. Budget-flip detection catches manufactured negative-ROI cases
