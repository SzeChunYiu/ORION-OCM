# Online switch theorem V1 — exact threshold parent without horizon prediction

**Status:** finite theorem + R0B parent definition / no ML / no claim beyond the frozen iid demand and horizon range.

Phase-2B0 showed that partial semantic prebuild admits multislope geometry but is
dominated by the incumbent exact static arms at every known horizon on every
primary coordinate.  The next parent should therefore preserve the two incumbents
rather than schedule dominated prebuild slopes.

Let:

```text
I(h) = expected cost of h cold/stateless inverse queries
S(h) = expected cost of h persistent target-triggered semantic queries from cold
O(h) = min(I(h), S(h))
```

on one prospectively declared scalar resource coordinate.  For the frozen iid
population these quantities are already computed exactly by `regime_sweep.py`.

## 1. Deterministic one-way threshold family

For integer threshold `tau >= 0`, define policy `P_tau`:

```text
queries 1..tau: use INVERSE, leaving semantic state cold
query tau+1 onward: use SEMANTIC persistently forever
```

If the lifetime stops at `H`, expected cost is

```text
C_tau(H) = I(H)                         if H <= tau
           I(tau) + S(H-tau)            if H > tau.
```

`tau=0` is always-semantic.  Any `tau >= H_max` is always-inverse on the bounded
experiment.

### Proof of the cost identity

If `H<=tau`, every demand uses the stateless inverse parent, so expected total is
`I(H)`.

If `H>tau`, the first `tau` queries cost `I(tau)`.  By construction they do not
advance semantic state.  At query `tau+1` the semantic arm therefore starts from
its cold state and receives `H-tau` fresh iid demands from the same frozen
distribution.  Its expected continuation cost is exactly `S(H-tau)`.  Linearity
of expectation gives the sum.  QED.

## 2. Exact bounded-horizon minimax threshold

Freeze a finite horizon set

```text
Hset = {1,...,Hmax}.
```

For every threshold define competitive ratio against the clairvoyant best static
exact arm:

```text
R(tau) = max_{H in Hset} C_tau(H) / O(H).
```

Then

```text
tau* in argmin_{tau in {0,...,Hmax}} R(tau)
```

is an exact optimal policy **within the deterministic time-only one-way-switch
family**.

### Proof

The candidate family contains exactly `Hmax+1` behaviorally distinct thresholds
on the bounded horizon set: thresholds larger than `Hmax` coincide with
`tau=Hmax`.  `R(tau)` is exactly computable for each finite candidate.  Exhaustive
minimum therefore returns the global optimum in the declared family.  QED.

This theorem does not claim optimality among arbitrary randomized, target-aware,
or multi-switch controllers.

## 3. No horizon prediction is used

The controller observes only how many queries have occurred since the effective
lifetime/reset epoch began.  It does **not** receive future stopping time, future
target identities, `R(q)`, realized arm costs, or a learned demand forecast.

The clairvoyant `O(H)` is used only as an evaluation benchmark.

## 4. Why this is stronger than a forced ski-rental reduction

Ordinary ski rental assumes a linear rent slope and fixed buy cost.  Here
`S(h)` includes the expected maximum semantic discovery frontier across `h` iid
targets and is generally nonlinear in `h`.

The exact threshold theorem above needs none of the linear-slope assumptions.  It
uses the measured/derived finite lifetime curve directly.  If it already captures
the useful unknown-horizon tradeoff, importing a more elaborate capital-investment
scheduler is unnecessary.

## 5. Resource-vector boundary

A threshold optimum is coordinate-relative.  If transitions, additions and
multiplications yield different `tau*`, there is no price-independent scalar
winner.  Report the raw vector and price regime.  A production policy requires a
prospectively declared scalarization or a Pareto/constraint objective.

## 6. Lifecycle boundary

The first experiment treats `H` as effective reuse length of one stable epoch.
With reset/revocation/invalidation, the threshold clock must restart when the
reusable semantic state is invalidated unless a stronger lifecycle model proves
otherwise.

Checkpoint/replay and threshold-controller state must be charged if this becomes
a runtime policy.

## 7. Next parent if deterministic threshold leaves residual

Only after measuring `R(tau*)` should we consider:

```text
randomized switch-time distribution (classical online-algorithm parent);
state-aware switching after semantic activation;
known stochastic stopping distribution / Bayes-optimal stopping;
legal demand-history features;
ordinary algorithm selection.
```

A learned horizon predictor is not next by default.