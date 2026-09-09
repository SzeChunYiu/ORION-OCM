# R0B — exact lifetime strategy regime before learned routing

**Status:** exposed source-derived calibration / NO ML / research-only.

This tranche advances issue #152 from “there appears to be a horizon-dependent
choice” to a falsifiable exact metareasoning object.  It does **not** train or
authorize a learned router.

The branch is based on current `main@6032fa6f`, which already contains merged
PR #153.  The two strategy engines are transplanted by exact Git blob identity
from `research/epistemic-structure-discovery-20260908`:

- `SemanticSearchSession`: reusable exact semantic BFS;
- `InverseSession`: exact target-directed backwards BFS.

The donor study already established the motivating sign change: inverse search
wins cold single queries while persistent semantic search wins the 142-target
lifetime.  This tranche asks what exact state variable explains that boundary,
how drift/restart changes it, and how much residual value is left for any
selector after the strongest simple exact parent is considered.

## Formal reduction

Let `q` be a frozen exact polynomial task.  For the semantic BFS define:

```text
R(q) = transition rank at which q first enters the exact semantic index
B_r(f) = cumulative build cost on resource coordinate r after f transitions
K_r(q) = zero-transition lookup + exact verification cost once q is indexed
I_r(q) = exact inverse-search cost for q
```

For the three registered phase coordinates

```text
r in {transitions, arithmetic_additions, arithmetic_multiplications}
```

and a stable semantic state, the donor implementation gives the exact identity

```text
C_sem,r(q_1 ... q_H)
  = B_r(max_i R(q_i)) + sum_i K_r(q_i).
```

The inverse parent is additive:

```text
C_inv,r(q_1 ... q_H)
  = sum_i I_r(q_i).
```

So the reusable machine is not paying “one search per query.”  It is buying a
frontier.  Once the frontier has reached the hardest demanded rank, later
queries inside that frontier pay only lookup/check cost on these coordinates.

This yields the exact rent-versus-build inequality

```text
buy reusable search state iff

B_r(max_i R(q_i)) + lifecycle_r
<
sum_i [I_r(q_i) - K_r(q_i)].
```

The important horizon is therefore not raw query count.  It is the **effective
reusable horizon**: how much future demand arrives before the retained state is
invalidated, reset, revoked, drifted, or made stale.

With reset/drift epochs `e` the build term becomes

```text
sum_e B_r(max_{i in e} R(q_i)),
```

which makes the sign change a lifecycle property rather than a generic claim
that persistence is always good.

## Exact i.i.d. parent

For the frozen finite population of `N=142` depth-four identities, sort targets
by discovery rank.  If `Q_1 ... Q_H` are i.i.d. uniform frozen targets, then

```text
P(max R = R_j)
  = (j/N)^H - ((j-1)/N)^H.
```

Therefore the expected cost of each static exact arm is computable without a
trained selector:

```text
E[C_inv,r(H)] = H E[I_r(Q)]

E[C_sem,r(H)]
  = sum_j P(max R = R_j) B_r(R_j)
    + H E[K_r(Q)].
```

`regime_sweep.py` evaluates these equations for horizons 1..142 and reports raw
coordinates.  The exposed donor source implies a source-drift calibration
boundary of:

```text
first expected semantic win:
  transitions              H = 4
  arithmetic additions     H = 6
  arithmetic multiplications H = 9

inverse is Pareto-better on all three through H = 3
semantic is Pareto-better on all three from H = 9
H = 4..8 is a price-sensitive transition band
```

These numbers are **not a blind/protected prediction**.  They are explicit
source-derived hostiles that must remain reproducible on the frozen source.

## Upper-bounding selector value before paying for a selector

The tranche also computes a deliberately unfair, nondeployable dynamic-program
oracle.  At each query it is handed the exact target-specific values `R(q)`,
`I(q)`, `K(q)`, and the current semantic frontier before choosing inverse or
semantic execution.

For coordinate `r`, frontier `f`, and remaining horizon `h`:

```text
V_r(f, 0) = 0

V_r(f, h) =
  E_q min(
    I_r(q) + V_r(f, h-1),

    [B_r(max(f,R(q))) - B_r(f)]
      + K_r(q)
      + V_r(max(f,R(q)), h-1)
  ).
```

This oracle pays **zero** for knowing which arm is cheaper.  A real selector
must infer that decision from legal pre-outcome features and must pay feature,
inference, training, maintenance, revision, and lifecycle costs.

The source-derived calibration checks require the oracle's maximum improvement
over the best static exact arm to stay below 8% on each of the three primary
coordinates.  If that holds, it sharply limits the room available to a learned
router: even perfect free foresight can only harvest a narrow residual in this
frozen ecology.

That does not prove ML can never help.  It changes the burden of proof.  A
future learned policy must beat the exact/static/analytic parents **after**
paying its own cognition, and it cannot claim value larger than the residual
available in the legal information state.

## Lifecycle sweep

The deterministic exposed sweep uses eight frozen permutations and separately
tests:

```text
reset/drift every      1,2,4,8,16,32,64,142 queries
checkpoint/replay every 4,8,16,32,64,71 queries
```

Every run preserves exact answer checking.  Reset experiments verify the exact
epoch-frontier identity above.  Checkpoint experiments charge snapshot writes,
reads and deterministic replay.  Raw resource vectors are retained rather than
collapsed into one post-hoc “work” number.

Storage is also explicit: semantic search retains serialized state while the
inverse parent retains no cross-query index.  Divisions and integer square-root
calls remain separate inverse-only coordinates.  Consequently the study
reports Pareto/price sensitivity instead of pretending one scalar exchange
rate is canonical.

## Scientific interpretation

This is the concrete form of the broader convergence behind #152:

```text
minimum cognition worth performing before acting
=
minimum sufficient decision information
+
minimum worthwhile reusable state
```

but only when both are cheaper than the work they avoid.

The decision question and the investment question are distinct:

```text
1. Do surviving models already license a common safe action?
   If yes, stop identifying.

2. If not, is another probe/deliberation cheaper than the action/check it may avoid?

3. Independently, is reusable cognitive state worth building before it is likely
   to be invalidated?
```

A learned router is downstream of all three exact gates, not a substitute for
them.

## Claim boundary

This directory is E2/exposed research calibration.  It does not run protected
#143 evaluation, does not change production routing, does not exercise native
proof verification, and does not establish an OCM-specific scientific residual.
The donor search mechanisms are conventional exact parents.

The terminal for this tranche is intentionally:

```text
LEARNED_ROUTER_NOT_AUTHORIZED_R0B_PHASE1
```

Promotion requires, at minimum, a prospective legal-feature study showing a
residual that survives the analytic threshold/static parents and charging the
selector itself.  If the cost-free oracle residual is already too small, the
correct terminal is parent sufficiency, not “try a larger model.”

## Reproduction

From repository root:

```sh
PYTHONPATH=src:research/residual-strategy-regime-v1 \
  python -m pytest -q research/residual-strategy-regime-v1

PYTHONPATH=src:research/residual-strategy-regime-v1 \
  python research/residual-strategy-regime-v1/regime_sweep.py \
  --out /tmp/r0b-regime.json
```

The workflow runs the same portable controls on Linux and publishes the
machine-readable sweep artifact.
