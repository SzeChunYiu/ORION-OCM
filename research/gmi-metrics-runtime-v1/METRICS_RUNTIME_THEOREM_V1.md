# Metrics runtime theorem V1

## 1. Coordinate set

The following 11 coordinates form the complete cost surface for any
morphological architecture.

### Original burden coordinates (7)

| Coordinate | Symbol | Domain | Semantics |
|---|---|---|---|
| Build | b | N >= 0 | One-time cost of constructing the implementation |
| Storage | s | N >= 0 | Persistent memory footprint of the stored form |
| Serve | v | N >= 0 | Per-query cost of serving the architecture |
| Update | u | N >= 0 | Cost of modifying the stored architecture |
| Verify | k | N >= 0 | Cost of correctness verification |
| History | h | N >= 0 | Cost of maintaining provenance and version history |
| Search | r | N >= 0 | Cost of retrieving relevant stored state |

### Intelligence-development coordinates (4)

| Coordinate | Symbol | Domain | Semantics |
|---|---|---|---|
| Capability | c | N >= 0 | Raw computational capability (operations per unit) |
| Plasticity | p | N >= 0 | Cost or capacity of restructuring the architecture |
| Retention | t | N >= 0 | Capacity of persistent memory or state |
| Information-required | i | N >= 0 | Minimum information needed to perform the function |

Each coordinate is a priced resource. A coordinate vector is

    x = (b, s, v, u, k, h, r, c, p, t, i) in Z_+^11

## 2. Price vector and scalarization

A frozen price vector lambda = (lambda_b, ..., lambda_i) in R_+^11
assigns real-valued prices to each coordinate. The scalarized cost is

    L(x) = lambda . x = sum_j lambda_j * x_j

Scalarization is only valid under an explicit price vector. Without
prices, the full 11-dimensional partial order is the only safe
representation.

### Falsification criterion

Given two morphologies x and y with x <_P y (Pareto-dominated),
any positive price vector lambda must satisfy L(x) <= L(y) with
strict inequality in at least one component.

## 3. Physical counters

### 3.1 Wall-clock

The wall-clock counter is a monotonic non-negative integer using
`time.perf_counter_ns` (abstracted as a monotonic counter in this
formalization). Let T(t) be the reading at time t. Then:

    T(t2) >= T(t1) for all t2 > t1
    T(t1) >= 0

Elapsed time is Delta T = T(t_end) - T(t_start), which is
non-negative by monotonicity.

### 3.2 Memory

The memory tracker maintains a peak resident set approximation via
an abstract allocation counter M. At any point:

    M_peak = max_{tau <= t} M(tau)

M_peak is non-decreasing over time. It is an upper bound, not an
exact measurement.

### 3.3 Energy

Energy is modeled as a linear function of compute and time:

    E(alpha, t) = alpha * t

where alpha is a proportionality constant (the energy intensity)
and t is wall-clock time. This is the RAPL proxy abstraction:
real RAPL provides per-instruction energy readings; we abstract
to compute * time as a linear model.

The energy model is additive: E(a + b, t) = E(a, t) + E(b, t)
for independent computational workloads a, b.

## 4. Budget-flip falsifier

Given a budget B and two morphologies x (budget-favored) and y
(complexity-favored), define:

    F_B(x, y) = sign(L_B(x) - L_B(y))

where L_B incorporates both the cost coordinates and a budget
penalty. The budget-flip condition is:

    F_{B1}(x, y) != F_{B2}(x, y) for B1 != B2

When budget-flip occurs, increasing the budget reverses the
optimal morphological choice. This is a first-class falsifier:
any architecture that flips under budget must be documented.

### Negative-budget refusal

Negative energy budgets (E < 0) and negative memory budgets
(M < 0) are undefined in this formalism. Any input yielding a
negative budget is rejected with an explicit error, not silently
clamped.

## 5. Independence

Coordinates are formally independent: changing one coordinate
does not alter any other. This is enforced at the implementation
level by separate counters per coordinate.

## 6. Limitations

- No network, platform or OS dependency
- CPython 3.8+ safe
- Energy proxy is a linear approximation; real hardware energy
  is non-linear in frequency and voltage
- Memory tracker is abstract; no /proc/self/statm or
  GetProcessMemoryInfo
- The price vector is frozen at definition time; price drift
  is outside scope
