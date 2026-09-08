# Convergence V1 — Minimum Sufficient Cognition as the common research spine

This note consolidates the presently separate ORION-OCM findings into one
research programme without claiming that the synthesis itself is novel.

## 1. The object is a decision contract, not an operator label

Let `V` be the surviving admissible models/hypotheses under legal observations,
and let `G_m(d)` be the actions that satisfy the protected decision/lifecycle
contract in context `d` if model `m` is true.

```text
Gamma(V,d) = intersection_{m in V} G_m(d).
```

When `Gamma(V,d)` is nonempty, full hidden-model identification is unnecessary.
The machine may execute a certified common action.  This subsumes exact
unanimity/common-action stopping and corrects formulations that ask for the
identity of the “best operator” when the downstream contract only needs a
coarser action class.

This immediately explains several branches:

- compose-stage R0: reordering the already-evaluated candidate set has zero
  residual work, so operator identity is the wrong target;
- DEV5/DEV6: agreement can justify stopping before singleton identification,
  but computing agreement must itself be charged;
- X1: an implied probe can be skipped, yet deciding implication can cost more
  than the probe;
- factorization/diagnosis: if legal observations do not separate required
  repair classes, no router can repair the missing channel.

## 2. Realizability is an authority gate

Agreement is only sound relative to a hypothesis language adequate for the
protected claim.  A false singleton inside a misspecified class is not truth.

Therefore confidence, entropy, score margin, or prediction unanimity may guide
search but cannot independently authorize a protected action unless the
relevant adequacy/coverage assumption is separately justified.

This makes representation expansion and routing different problems:

```text
L0  no useful candidate exists
    -> representation/discovery

L1  a candidate exists but essential demand is zero
    -> ecology/opportunity

L2  multiple safe useful alternatives exist with different current costs
    -> genuine decision/strategy opportunity

L3  alternatives are current-output equivalent but create different reusable
    state or future revision behavior
    -> lifecycle / investment decision

L4  legal observations collapse distinct worlds that require different
    protected actions
    -> observation-channel insufficiency, not routing
```

## 3. Cognition has two values: information and reusable state

The branches expose two superficially different ways cognition can pay:

```text
information value:
  buy a probe/check/deliberation to reduce uncertainty before acting

state value:
  build/retain an exact structure whose cost is amortized over later demand
```

Both obey the same economic discipline.

For any cognitive intervention `u`, publish its raw resource-vector value:

```text
Delta C(u)
  = avoided downstream work
    + future reusable-state value
    - deliberation/acquisition cost
    - maintenance/update cost
    - policy-use cost
    - lifecycle/replay/revision cost.
```

No intervention is globally “better” unless it Pareto-dominates its parent.
Otherwise the result is a price region, not a scalar victory.

This unifies:

- DEV6: incremental bookkeeping can erase the value of fewer checks;
- X1: fewer external interventions can still mean more total cognition;
- X3: carry/replay claims can change sign under corrected resource prices;
- structure learning: fewer source queries can coexist with ~3x counted
  computation;
- native proof serving: a real proof/search reduction can coexist with worse
  whole-call latency;
- semantic lifetime search: a stateful method can lose cold and win across a
  reusable lifetime.

## 4. New R0B formal object: effective reusable horizon

The semantic-search donor makes the state-value term exact.

For primary phase coordinate `r`:

```text
C_sem,r = B_r(max R(q)) + sum K_r(q)
C_inv,r = sum I_r(q).
```

A reset, drift event, revocation, grammar change, or incompatible checkpoint
starts a new epoch:

```text
C_sem,r =
  sum_e B_r(max_{q in epoch e} R(q))
  + sum K_r(q)
  + lifecycle_r.
```

The controlling variable is therefore **effective reusable horizon**, not
nominal lifetime length.

If invalidation has hazard `delta`, a useful first parent is the corresponding
geometric survival model, followed by exact finite-horizon DP when the hazard,
demand distribution, or resource prices are nonstationary.  A learned policy
is only justified if legal features predict departures from these parents well
enough to repay policy cost.

This gives a prospective cross-domain prediction:

> Persistent cognitive structure should be favored when the expected reuse
> before invalidation is high relative to build/replay cost; target-directed
> action should be favored when reuse is sparse, drift is high, or state
> reconstruction is expensive.

That prediction applies equally to semantic indices, proof-route indices,
support structures, diagnosis caches, and future exact method libraries.

## 5. Lifecycle equivalence is part of correctness

Current output equality is insufficient when a strategy changes persistent
state, support cones, traces, revocation response, or future availability.

A strategy-selection experiment must therefore freeze:

```text
current protected output
future revision/revocation behavior
authority/checker boundary
trace/audit obligations
persistent state identity
fallback behavior
resource vector
```

This is why R0A compose early-exit must prove more than answer equality, and why
#112-style alternative support is relevant even though it is not itself a
routing result.

## 6. Information lower bounds must target the required decision class

Fano-style arguments remain useful only after defining the coarsest variable
the contract truly requires.

Use:

```text
Z = required protected decision class
```

rather than automatically:

```text
Z = hidden cause identity
Z = best operator identity.
```

For adaptive probes, any per-probe information cap must be conditional:

```text
I(Z ; Y_i | history_{i-1}, chosen_probe_i) <= b.
```

This preserves the possibility that individually weak observations become
jointly informative.

## 7. Parent ladder and ML kill rule

The programme should search in this order:

```text
exact incumbent
-> common-action / exact early exit
-> analytic threshold, cache, rent-vs-buy, ski-rental parent
-> exact finite-state metareasoning DP
-> ordinary algorithm-selection rule on legal features
-> simple statistical model
-> tiny learned model only if a residual remains.
```

A learned policy is killed at a scope if any of these holds:

```text
no L2/L3 decision population exists
the required decision is not identifiable from legal observations
an exact/simple parent captures the boundary
cost-free oracle residual is too small to repay selector cost
selector advantage disappears under lifecycle-equivalent accounting
hypothesis-class adequacy is not established for protected authority
```

The scientific target is therefore not “neural routing.”  It is a theory of
**minimum sufficient cognition**: how much information and reusable structure
a machine should acquire before the next protected action, under exact
correctness, lifecycle, and resource constraints.

## 8. Immediate experimental order

R0B now has the cleanest real strategy phase boundary and should be calibrated
first.  R0A follows as an exact lifecycle-qualified local optimization.
Merged #153 supplies a later R0C proof-scheduler population once many frozen
proof families expose legal pre-outcome features.  R0D should then compare
full identification, common-action stopping, and paid-probe DP on exact finite
decision regions.

None of these steps requires ML to produce a scientific result.  A negative
residual is itself a useful result: it tells us the machine should not spend
cognition learning a decision it can already make exactly and cheaply.
