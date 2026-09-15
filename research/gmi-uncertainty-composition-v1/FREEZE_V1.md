# Freeze V1 — dependency-aware uncertainty propagation through composition

Issue: #759. Parent ledger: #602 Section M, row `Propagate uncertainty through composition`.

**Pre-implementation freeze.** At this commit the scored executor, tests, formalization and result receipt for this capsule do not exist. This file fixes the mathematical contract, exact controls, expected results, claim ceiling and falsifiers before those artifacts are written.

## Claim ceiling

```text
DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE
```

No claim of universal uncertainty propagation, probabilistic capability calibration, learned dependence, real-scale calibration, or complete GMI.

## Frozen mathematical object

A finite composition contract consists of:

- a finite directed acyclic graph `G=(V,E)`;
- a nonempty exact finite domain `X_v` for every node;
- root set `R`;
- a preregistered root joint confidence set `C_R subseteq product_{r in R} X_r` with source failure budget `alpha`;
- for every non-root `v`, either a preregistered finite relation
  `Q_v subseteq (product_{p in Pa(v)} X_p) x X_v`
  with failure budget `beta_v`, or an explicit `UNKNOWN_RELATION` marker;
- frozen output nodes.

For an unknown relation the only sound registered semantics is the universal relation `(product parent domains) x X_v`, i.e. the node value is the full registered output domain.

No relation, domain, root set, output set or failure budget may be added/changed after source activation.

## Frozen theorem targets

### UC-1 global feasible-assignment coverage

Define

```text
A = {x_V : x_R in C_R and
             ((x_p)_{p in Pa(v)},x_v) in Q_v for every non-root v}.
```

For output nodes `O`, `C_O = projection_O(A)`. If

```text
P(theta_R in C_R) >= 1-alpha
P(H_v^c) <= beta_v
```

where `H_v` means the true local tuple satisfies `Q_v`, then for every finite registered DAG

```text
P(theta_O in C_O) >= 1 - alpha - sum_v beta_v
```

without independence. Exact deterministic/set-valued relations have `beta_v=0`.

### UC-2 marginal-root source bound

If only root marginal confidence sets `C_r` are registered with

```text
P(theta_r notin C_r) <= alpha_r,
```

then the Cartesian root set has simultaneous source failure at most `sum_r alpha_r` by Boole's union bound. Multiplying marginal coverages is forbidden without an independence premise.

### UC-3 local propagation is sound but can be loose

Let roots use marginal projections of `C_R` and recursively define

```text
S_v = Q_v(product_{p in Pa(v)} S_p).
```

Then the global feasible projection at each node is a subset of `S_v`. Strict containment is possible when parent sets share ancestors or other joint constraints.

### UC-4 ignorance propagation

An `UNKNOWN_RELATION` node receives the full registered node domain. Downstream uncertainty propagates from that full set. A parent value may not be copied forward as a nominal substitute.

## Frozen exact controls

All arithmetic uses exact integers/Fractions and canonical sorted finite sets.

### C1 — shared-ancestor dependency hostile

```text
x in {-1,+1}                        root
C_x = {-1,+1}
a = x                               domain {-1,+1}
b = x                               domain {-1,+1}
y = a - b                           domain {-2,0,+2}
```

Frozen result:

```text
global exact y = {0}
local Cartesian y = {-2,0,+2}
global is a strict subset of local
```

Any local result `{0}` without carrying the `a=b` dependence fails the hostile. Any global result containing ±2 is not exact global projection.

### C2 — nonlinear two-root graph with no hidden dependence loss

Roots use the full Cartesian joint set

```text
x in {-2,-1,+1,+2}
z in {-1,+1}
```

and

```text
sq = x^2
out = sq + z
```

Frozen exact output:

```text
{0,2,3,5}
```

Global and local propagation must agree on this control.

### C3 — set-valued operator

```text
u in {0,1}                           root
s in {u,u+1}                         set-valued relation
y = 2*s
```

Frozen exact output:

```text
{0,2,4}
```

### C4 — unknown relation fail-closed

```text
x = 0                                root
q in {0,1,2}                         UNKNOWN_RELATION from x
y = q + 1                            domain {1,2,3}
```

Frozen result:

```text
q uncertainty = {0,1,2}
y uncertainty = {1,2,3}
terminal includes CANNOT_IDENTIFY_UNKNOWN_RELATION
```

### C5 — marginal confidence dependence counterexample

Use 20 equiprobable atoms. Root-1 confidence fails only on atom 0; root-2 confidence fails only on atom 1.

Each marginal coverage is `19/20`. Their joint coverage is exactly `18/20 = 9/10`, while a false independence product would be `361/400`.

Frozen conclusions:

```text
actual joint = 9/10
union-bound lower = 9/10  (tight)
independence product = 361/400 != 9/10
```

### C6 — source + operator failure budget

Freeze

```text
alpha = 1/20
beta_1 = 1/100
beta_2 = 1/200
```

with pairwise-disjoint failure events on 200 equiprobable atoms. Frozen total failure is `13/200`; simultaneous-good probability and union-bound lower bound are both `187/200`. Product-of-success-probabilities must differ from `187/200`.

### C7 — affine RR-4 regression control

Reproduce the already-parent-owned affine special case:

```text
x in [1/4,3/4]
y = -2*x + 3 + e,  e in [-1/10,1/10]
```

exact interval hull `[7/5,13/5]` by corner enumeration. This is a regression/parent-subtraction control, not the new theorem.

## Frozen governance hostiles

The suite must reject or fail closed on:

1. cycles/self-cycles;
2. unknown parent names;
3. empty domains/root confidence sets;
4. out-of-domain root assignments or relation endpoints;
5. duplicate node names;
6. malformed/non-Fraction failure budgets and budgets outside `[0,1]`;
7. relation mutation after activation;
8. output/domain mutation after activation;
9. a registered non-universal relation omitting every output for some parent-domain tuple (unless explicitly declared partial with nonzero failure semantics; V1 forbids such incompleteness and requires total relation coverage over the registered parent domain);
10. multiplication of marginal confidence labels as though independence were proven.

## Proof boundaries

- The graph is finite and acyclic. Cyclic fixed-point uncertainty is outside V1.
- Relations are finite exact registered objects. Learning/estimating relations from data is outside V1.
- `beta_v` values are scientific premises/budgets, not inferred by the executor.
- Exact global feasible propagation may be exponentially expensive. V1 proves soundness, not scalable inference.
- Local Cartesian propagation is allowed as a sound over-approximation; precision loss is reported, never silently called exact.
- Continuous interval arithmetic is represented only by the finite affine regression control; general continuous range computation is outside V1.

## Parent subtraction

The underlying mathematics is standard: set images and projections, relational composition, Boole's union bound, and interval inclusion/isotony. Literature anchors include Moore/Kearfott/Cloud interval analysis, finite/set-valued reachability analysis, and imprecise-probability/Fréchet bounds for unknown dependence. Repository parents: #657/RR-4 (affine composition special case) and #748 (sequential relation-chain special case).

## Success rule

Only after the frozen theorem statements, all C1–C7 controls and all governance hostiles pass under both normal Python and `python -O`, a deterministic result receipt byte-reproduces, dedicated CI is green, and the PR merges may #759 be closed and the single #602 Section-M composition row be reconciled.
