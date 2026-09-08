# R0B Phase 2 — prospective legal-feature selector gate

**Status:** protocol freeze / no ML / research-only.

Phase 1 bounds the largest possible value of per-query strategy selection by
letting an exact DP see `R(q)`, `I(q)`, and `K(q)` for free.  Phase 2 asks the
question that must be answered before any learned router is scientifically
admissible:

> Is the remaining strategy decision predictable from information that the
> machine can legally possess before choosing an arm, after charging the
> cognition required to obtain and use that information?

This protocol deliberately separates **decision information** from **method
identity**.  The target variable is the required strategy decision class, not
which hidden program generated the target and not the identity of an allegedly
"best operator".

## 1. Protected contract

Both candidate arms remain exact parents:

- `INVERSE`: target-directed exact inverse search;
- `SEMANTIC`: persistent exact semantic search/index construction.

Strategy selection may change non-authoritative reusable search state.  It may
not change the protected answer/checker boundary.  Any promoted selector must
preserve:

```text
same exact target answer
same native/exact checker authority
same failure/fallback contract
sound reset/invalidation behavior
sound checkpoint/restore/replay behavior
no hidden production side effects
```

Persistent search-state bytes need not be identical between strategies; the
state difference is the investment being studied.  The requirement is
**lifecycle semantic equivalence**, not byte identity.

## 2. Information boundary: what a selector may know

At decision time `t`, the deployable information state is `F_t`: facts already
available before either candidate arm is run for the current target.

Allowed without special justification:

```text
current exact target coefficients (the task input itself)
current semantic-session frontier/state summaries already maintained
remaining horizon only in the explicitly KNOWN_HORIZON experiment
registered reset/checkpoint/invalidation policy
resource coordinate / ex-ante price regime fixed before evaluation
```

Potentially allowed only if their acquisition/maintenance cost is charged:

```text
derived coefficient statistics
query-overlap summaries
cache/index occupancy summaries
revision/drift estimates from past observations
learned/statistical feature transforms
```

Forbidden as deployable features:

```text
R(q) semantic discovery rank before semantic execution
I(q) realized inverse-search cost before inverse execution
K(q) realized semantic hit/check cost before semantic execution
shortest hidden primitive program
future target identities or future realized costs
future invalidation/revision events unless exogenously announced
task fingerprint used as a lookup key for a table fitted on that same target
protected-evaluation outcomes
```

The Phase-1 DP may continue to use forbidden quantities only under the explicit
label `COST_INFORMED_NONDEPLOYABLE_UPPER_BOUND`.

## 3. Frozen feature ladder for Phase 2A

The first prospective audit must proceed from weak, cheap summaries to richer
ones.  Do not jump directly to a model.

### F0 — state-only

```text
known remaining horizon (when available)
current semantic frontier
registered lifecycle regime
resource coordinate
```

### F1 — coarse task structure

Add cheap summaries of the already supplied coefficient vector:

```text
polynomial degree
number of nonzero coefficients
positive / negative / zero coefficient counts
```

### F2 — magnitude structure

Add exact deterministic summaries whose computation is separately counted:

```text
max numerator bit length
max denominator bit length
sum numerator bit lengths
sum denominator bit lengths
constant-term sign class
leading-coefficient sign class
```

### F3 — identity-saturated information upper bound

The exact coefficient tuple may be used only as an **information-sufficiency
upper bound**.  It is not a generalizing parent.  A table keyed by the exact
coefficient tuple of an evaluation target is forbidden unless that key/value
mapping was established independently of that target.

If F3 removes a collision that remains under F0–F2, the conclusion is only that
the task input contains enough information in principle.  It does not show that
a cheap prospective policy exists.

## 4. Phase 2A: decision-collision audit

For one primary resource coordinate `r`, current semantic frontier `f`, target
`q`, and remaining horizon `h`, define the Phase-1 exact action values from the
same pre-decision state:

```text
Q_inv,r(f,q,h)
  = I_r(q) + V_r(f,h-1)

Q_sem,r(f,q,h)
  = [B_r(max(f,R(q))) - B_r(f)]
    + K_r(q)
    + V_r(max(f,R(q)),h-1).
```

Define the optimal action set rather than forcing arbitrary tie-breaking:

```text
A*(f,q,h,r) = argmin_{a in {INVERSE, SEMANTIC}} Q_a,r(f,q,h).
```

For a frozen legal feature map `phi`, bucket states by:

```text
(phi(F_t), h, f, r).
```

A bucket is **exactly action-sufficient** iff the intersection of optimal action
sets in that bucket is nonempty:

```text
intersection_s A*(s) != empty.
```

A bucket is a **decision collision** iff that intersection is empty.  Such a
collision proves that no deterministic selector using only that frozen feature
schema can reproduce the full-information oracle on every state in the bucket.
A larger MLP does not repair the missing observation.

Report at least:

```text
number and probability mass of decision-collision buckets
number and probability mass of states in those buckets
INVERSE-only / SEMANTIC-only / tie mass
minimum achievable feature-conditional cost
regret versus the full-information DP oracle
feature acquisition / maintenance / policy-use cost
```

The cost-relevant quantity is the feature-conditional regret floor, not merely
classification error.

## 5. Realizable state evolution

The Phase-1 DP already uses realizable strategy state transitions:

```text
choose INVERSE  -> semantic frontier remains f
choose SEMANTIC -> frontier becomes max(f, R(q))
```

Phase 2 must preserve this rule.  Do not give a policy a shadow semantic index
that was advanced on queries where it chose inverse unless the background build
actually occurs and every build/update/storage/lifecycle cost is charged.

Counterfactual evaluation from a cloned state is allowed only for exposed
research calibration, and clone/checkpoint/restore work must be separately
reported if it is proposed as a deployable mechanism.

## 6. Phase 2B: no-ML parent ladder

Only if legal information separates useful decision regions do we compare
policies.  Evaluate in this order:

```text
P0  always inverse
P1  always semantic
P2  one fixed known-horizon break-even threshold
P3  state-aware exact threshold using frontier + remaining horizon
P4  ski-rental / doubling parent when horizon is unknown
P5  finite exact lookup/decision tree on frozen legal feature bins
P6  exact finite-state metareasoning DP where tractable
P7  ordinary statistical algorithm selection
P8  tiny learned model only after every earlier parent leaves payable residual
```

A later parent must beat the strongest earlier parent after adding its own
feature, inference, training, update, storage, checkpoint/replay, and revision
costs.  Reporting fewer inverse/semantic operations alone is insufficient.

## 7. Unknown horizon and lifecycle regimes

Known horizon is an exposed calibration aid, not a default runtime assumption.
A separate unknown-horizon lane must test online parents without access to
future demand.

At minimum sweep:

```text
stable lifetime
registered reset intervals
registered checkpoint/replay intervals
controlled invalidation hazard
demand orders with clustered and anti-clustered structural overlap
```

Do not use future target order to construct deployable features.  If a demand
model is estimated from prior observations, charge its maintenance and test it
under drift.

## 8. Resource-vector discipline

Keep raw coordinates before any scalar pricing:

```text
semantic/inverse phase counters
feature acquisition counters
selector inference counters
selector state/update counters
checkpoint bytes written/read
restore/replay work
persistent serialized bytes
peak query/search state
wall time and CPU time when runtime validation is executed
```

A policy that wins one coordinate and loses another defines a price region.  It
does not establish a globally better machine.

## 9. Terminals and ML gate

Phase 2 must end with one of the following evidence-backed states (or a narrower
explicit boundary):

```text
EXACT_POLICY_SUFFICIENT_R0B_PHASE2
  a simple/exact legal-feature parent captures the payable residual

OBSERVATION_CHANNEL_INSUFFICIENT_R0B_PHASE2
  relevant opposite decisions remain indistinguishable under the frozen legal
  observation channel; expand/justify observations before routing

RESIDUAL_ALGORITHM_SELECTION_OPPORTUNITY_R0B
  a nontrivial legal-feature residual survives exact parents and all charged
  cognition; this authorizes ordinary algorithm-selection study, not ML by itself
```

Until the third terminal is reached and a simpler statistical parent is beaten:

```text
LEARNED_ROUTER_NOT_AUTHORIZED
```

## 10. Immediate executable sequence

1. Instrument the existing DP to emit optimal action sets for exposed states;
2. implement F0/F1/F2 collision and regret-floor reports without fingerprints;
3. use F3 only as an information upper bound;
4. test known-horizon exact thresholds;
5. test an unknown-horizon ski-rental/doubling parent;
6. charge feature/policy cognition and lifecycle work;
7. only then decide whether there is any residual worth learning.

This is the shortest path from Phase 1 to a legitimate routing population.  It
can also terminate the routing lane early, which is a successful scientific
result.