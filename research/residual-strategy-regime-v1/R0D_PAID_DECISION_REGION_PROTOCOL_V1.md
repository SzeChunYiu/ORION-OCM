# R0D paid Decision Region Determination protocol V1

**Status:** formal protocol / direct DRD + metareasoning parent adoption / no ML.

R0D should no longer be described as an OCM-specific contest between
"singleton" and "unanimity."  The mature parent is **Decision Region
Determination (DRD)**: stop gathering information when all surviving hypotheses
are contained in at least one decision region.  The economic parent layered on
top is rational metareasoning/value of computation: even after a safe region is
known, another paid probe may be worthwhile if it enables a sufficiently cheaper
protected action.

## 1. Frozen finite model

Register before protected outcomes:

```text
H          finite hypotheses/world states
A          protected actions
G_h        safe/acceptable actions under h
R_a        {h : a in G_h}       decision region for action a
T          legal probes/tests
O_t        outcomes
cost(t)    raw resource vector / frozen scalar price coordinate as declared
obs(h,t)   exact deterministic outcome or a registered stochastic channel
V(S)       hypotheses consistent with evidence S
```

If a prior is used, freeze it.  If worst-case cost is used, do not switch to
Bayes expected cost after seeing outcomes.

## 2. Four stopping parents

### P-ID — full identification

```text
stop iff |V| = 1.
```

This is the strongest-information parent and usually performs unnecessary probes
when multiple states license the same action.

### P-ECD — disjoint decision/equivalence class

When decision regions partition `H`, stop once the version space lies entirely
inside one class.  This is the Equivalence Class Determination special case.

### P-DRD — overlapping common-action stop

```text
stop iff exists a in A : V subset R_a.
```

By Theorem 1 of `FORMAL_DECISION_CORE_V2.md`, this is exactly

```text
Gamma(V) != empty.
```

Multiple actions may cover the same surviving states; regions may overlap.

### P-PAID — action/probe Bellman parent

Let `Stop(V)` be the minimum registered protected action cost available from the
current information state.  For a finite probe budget `k`, use

```text
D_0(V) = Stop(V)

D_k(V) = min(
  Stop(V),
  min_t [ c_pred(V,t) + c_probe(t)
          + E_o D_{k-1}(V_{t,o}) ]
).
```

`c_pred` includes the cognition required to enumerate regions, determine
admissibility, maintain votes/counts, compute the Bellman lookup or otherwise
decide whether/probe what to run.  If the controller uses a precomputed table,
charge table construction/storage/update/replay over the registered lifetime.

## 3. Theorem — DRD stops no later than full identification

Assume every hypothesis is contained in at least one decision region (equivalently
`G_h` is nonempty).  Along any evidence path for which full identification is
reached at time `tau_ID`, the first DRD-feasible stopping time satisfies

```text
tau_DRD <= tau_ID.
```

### Proof

At time `tau_ID`, `V={h}` for the identified hypothesis.  By coverage there is an
action `a in G_h`, so `{h} subset R_a`.  Therefore the DRD stopping condition is
true no later than `tau_ID`.  QED.

The inequality may be strict whenever two or more surviving hypotheses share an
action region.

## 4. Theorem — fewer probes does not imply lower total cognition

There exist finite DRD problems in which `tau_DRD < tau_ID` on every path but a
DRD implementation has larger total cost because evaluating/maintaining its stop
predicate costs more than the probes it avoids.

### Construction

Suppose full identification always takes two unit-cost probes.  Suppose every
version after the first probe already lies in a valid decision region, so DRD
uses one probe.  Let computing the DRD region-intersection predicate after that
probe cost `2`, while the identification parent incurs no additional predicate
cost beyond reading the second probe.

Then:

```text
DRD cost = 1 probe + 2 predicate = 3
ID  cost = 2 probes = 2.
```

Yet DRD uses strictly fewer probes.  QED.

This is the exact formal pattern observed by DEV6/X1.

## 5. Decision-value target, not cause identity

Probe-selection information bounds should target the required protected decision
region/action class, not hidden cause identity, unless identifying the cause is
itself needed for the protected contract.

A probe that distinguishes ten causes all lying in the same region may contain
many bits about cause while having zero immediate protected decision value.

Conversely, a low-probability distinction can have high value when it changes a
high-cost protected action.  Therefore report Bayes/decision regret and raw cost,
not mutual information alone.

## 6. Misspecification hostile

DRD guarantees are relative to the declared hypothesis/decision-region model.  A
version space collapsing inside one region is not authority if the true world can
lie outside `H` and require a disjoint safe action.

Add at least one controlled out-of-class hostile when the domain permits it:

```text
same legal transcript as an in-class world
+
different protected safe-action requirement.
```

If such a pair exists, the observation/class boundary is inadequate and no
posterior confidence/region vote authorizes action without an external checker or
abstention path.

## 7. Executable comparison grid

Run all parents on the identical frozen tests/outcomes:

```text
P-ID
P-ECD where applicable
P-DRD with naive region scan
P-DRD with any proposed incremental structure, fully charged
P-PAID exact finite DP where tractable
strong simple greedy DRD parent (HEC/EC2-style only when its assumptions fit)
```

For every run report:

```text
probe count and probe resource vector;
region/predicate computation;
maintained state update cost;
peak/persistent bytes;
protected action cost;
checkpoint/replay/revision cost;
total raw resource vector;
scalar result only under prospectively frozen prices;
```

## 8. Terminals

```text
FULL_IDENTIFICATION_PARENT_SUFFICIENT_R0D
  no useful earlier decision-region stop exists at this scope

DECISION_REGION_STOPPING_USEFUL_R0D
  overlapping-region stop safely eliminates information work and remains cheaper
  after complete predicate/lifecycle accounting

DECISION_REGION_PREDICATE_COST_DOMINATES_R0D
  fewer probes survive but total cognition worsens

PAID_META_POLICY_SUFFICIENT_R0D
  exact Bellman/simple metareasoning captures the useful stop/probe frontier

OBSERVATION_OR_HYPOTHESIS_CLASS_INSUFFICIENT_R0D
  legal observations/class cannot authorize a protected action
```

None of these terminals requires a learned router.