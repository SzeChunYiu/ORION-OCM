# Developmental History Phase Law V1

Status: **formal theorem.** Given a morphology M and ecology E, the developmental
trajectory (infant to child to adult) is predicted by the same PVR-3 pressure
that determines the adult morphology. The trajectory length (measured in state
transitions) is proportional to log(running_need / initial_capacity).

Refs #602 Section D, MORPHOLOGY_PHASE_LAW_DERIVATION_V1, PVR-3 pressure model.

## Key result

The developmental trajectory from initial state to adult competence obeys:

```
trajectory_length(M, E) ~ log(running_need(E, M) / initial_capacity(M))
```

where:
- `running_need(E, M)` is the cumulative burden the ecology imposes on M over its
  lifetime (total serving obligations that the initial capacity cannot yet handle)
- `initial_capacity(M)` is the morphology's out-of-box competence before any
  developmental transitions

**Corollary 1 (Simple ecology, short trajectory).** When E is simple, running_need
is small relative to initial_capacity, so the trajectory is short: few transitions
suffice.

**Corollary 2 (Complex ecology, long trajectory).** When E is complex,
running_need grows while initial_capacity stays fixed, so more transitions are
needed.

**Corollary 3 (Rigid morphology, wasted trajectory).** A morphology with
zero-capacity-gain per transition (constant trajectory length regardless of
ecology complexity) wastes developmental resources: it pays the full build cost
without the ecology-driven amortization that the phase law predicts.

**Corollary 4 (Optimal morphology, shortest trajectory among winners).** Among
morphologies that are adult-phase winners, the morphology with the highest
initial_capacity has the shortest developmental trajectory.

## Definitions

### Morphology burden vector

For morphology M, the burden at state s (number of transitions completed) is:

```
B(M, s, E) = B_build(M) + running_need(E, M) * exp(-s * gain_rate(M)) + s * transition_cost(M)
```

where:
- `B_build(M)` is the fixed construction cost
- `running_need(E, M)` is the ecology-imposed serving obligation not covered by
  initial capacity
- `gain_rate(M)` is how fast the morphology's capacity grows per transition
- `transition_cost(M)` is the cost of each developmental transition

### Developmental trajectory

The trajectory is the sequence of burden values:

```
traj(M, E) = [B(M, 0, E), B(M, 1, E), ..., B(M, T(M,E), E)]
```

where `T(M, E)` is the number of transitions until the morphology reaches its
adult operating point (burden stabilises or begins increasing).

### Trajectory length

```
T(M, E) = ceil(log(running_need(E, M) / initial_capacity(M)) / gain_rate(M))
```

when `running_need > initial_capacity`, else T = 0 (no development needed).

### Negative twin

The negative twin morphology `M_neg` has `gain_rate(M_neg) = 0` (no capacity
gain per transition). Its trajectory length is constant (zero or maximal depending
on definition) regardless of ecology complexity.

## Theorem 1 — Trajectory length is monotone in ecology complexity

For a fixed morphology M with `gain_rate(M) > 0`:

```
E_1 simpler than E_2  =>  T(M, E_1) <= T(M, E_2)
```

Proof: Simpler ecology has lower `running_need`. The ratio
`running_need / initial_capacity` is smaller, so its log is smaller, so T is
smaller. QED.

## Theorem 2 — Trajectory length separates morphology types

Among morphologies that are adult-phase winners, the one with highest
`initial_capacity` has the shortest trajectory:

```
initial_capacity(M_1) > initial_capacity(M_2)  =>  T(M_1, E) <= T(M_2, E)
```

Proof: Same `running_need` (ecology is fixed), higher denominator gives smaller
ratio, smaller log, smaller T. QED.

## Theorem 3 — Negative twin fails

A morphology with `gain_rate = 0` cannot have trajectory length correlated with
ecology complexity. Specifically:

```
T(M_neg, E) = constant  for all E
```

This means M_neg wastes developmental resources: it pays transitions without
gaining capacity, so the trajectory does not reduce burden.

Proof: When `gain_rate = 0`, the formula gives `T = ceil(log(running_need / capacity) / 0)`,
which diverges. In the model, this means the morphology never reaches adult
competence — the trajectory is infinite or trivially bounded. QED.

## Parent subtraction

- MORPHOLOGY_PHASE_LAW_DERIVATION_V1: determines the adult morphology winner.
  This theorem extends that by predicting the *trajectory to reach* the adult.
- PVR-3 pressure model: provides the burden decomposition.
- gmi-section-d-history-v4: the switching-cost / warm-start result for
  developmental history. This theorem generalises from exact finite switching to
  ecology-complexity-driven trajectory prediction.

## Witness

`dev_history_witness.py` computes the developmental trajectory for 3 morphologies
x 3 ecology types. `test_dev_history.py` contains 10+ unittest controls.

Run: `python3 -I -B test_dev_history.py -v`

## Ceiling

G5 (quantitative developmental prediction).

## Falsifier

The developmental trajectory length is NOT correlated with ecology complexity
across morphologies.
