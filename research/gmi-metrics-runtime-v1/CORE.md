# Metrics runtime V1

Formal resource-coordinate framework for measuring and pricing all
computational burden dimensions of a morphological architecture.

- [Metrics runtime theorem](METRICS_RUNTIME_THEOREM_V1.md)
- [Implementation](metrics_runtime_v1.py)
- [Controls](test_metrics_runtime_v1.py)
- [Coordinate contract](CONTRACT_V1.json)

Registers 11 coordinates (7 burden + 4 intelligence-development) under
a frozen price vector. Abstract wall-clock, memory and energy counters
are formalized but carry no platform dependencies.

The budget-flip falsifier identifies regimes where increasing budget
reverses the optimal morphological strategy, and negative budgets are
formally undefined.
