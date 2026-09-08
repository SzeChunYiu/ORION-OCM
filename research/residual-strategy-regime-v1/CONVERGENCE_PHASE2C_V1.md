# R0 convergence through Phase 2C — theorem graph, exact terminals, and remaining gaps

**Status:** research convergence document / no production routing change / no ML
authorization.

This document records the strongest currently defensible synthesis after the
literature-saturation, exact-parent, hostile-identifiability, unknown-lifetime,
multi-objective, and paid-information passes.  It is deliberately conservative:
results are separated into mature imported parent theory, OCM-specific
reductions/proofs, and source-derived empirical certificates.

The central conclusion is no longer merely "do not train the tiny MLP yet."  The
research question has decomposed into several distinct problems, most of which
have simpler exact parents or hard information/objective gates before ordinary
algorithm selection becomes relevant.

---

## 1. One decision state, with the objective made explicit

Use the metalevel state

```text
sigma = (V, s, d, o)
```

where

```text
V  surviving admissible world/model set or belief state
s  non-authoritative reusable computation/state
   (index, proof structure, cache, support, checkpoint, etc.)
d  protected output + lifecycle context
o  registered decision objective
   (price vector, constraints, risk criterion, Pareto/robust request)
```

Earlier notation omitted `o` only when it was fixed externally.  R0B now proves
that this omission can be substantive: different resource objectives can require
different exact strategies even when the world state and horizon are identical.

The minimal sufficient decision representation is not generally hidden-world
identity, target identity, a best-operator label, entropy, confidence, mean
horizon, or a binary long/short probability.  It is any exact quotient of
`sigma` that preserves:

```text
protected admissibility;
immediate contract-relevant value;
future successor-class law;
and the optimizer under the registered objective.
```

For finite Bayes action families a sufficient nonminimal representation is the
vector of expected action losses plus enough state to update that vector after
future legal observations.

---

## 2. Imported parent theory versus OCM work

### Mature results adopted rather than re-invented

The current research repeatedly reduces to established theory:

```text
Decision Region / Equivalence Class Determination
Blackwell comparison of experiments; Le Cam/Torgersen deficiency
rational metareasoning / value of computation
finite-horizon Bellman optimality
stochastic/contract bisimulation and information-state abstraction
online capital investment / ski-rental-style stopping
finite zero-sum minimax and LP strong duality
online algorithms with advice / untrusted advice
learning-augmented rent-or-buy
online algorithms with costly predictions
Bayesian survival/posterior stopping
multi-objective sequential decision making / coverage sets
trace/stuttering equivalence and slicing
algorithm portfolios / ATP strategy scheduling / restart theory
misspecification / agnostic prediction with independent authority boundaries
```

We do not claim novelty for these theorem families.

### OCM-specific scientific work

The reusable work is instead:

```text
1. prove that a particular OCM lane satisfies a parent theorem's assumptions;
2. expose exact counterexamples when it does not;
3. derive source-controlled cost matrices and lifecycle transitions;
4. define protected observation/authority boundaries;
5. charge cognition, state construction, policy evaluation and lifecycle work;
6. terminate learned-routing hypotheses when exact parents already suffice.
```

That is the correct place to fill gaps ourselves.

---

## 3. Formal theorem chain already established

### T1 — common protected action is safety sufficiency, not economic sufficiency

For surviving models `V`, if

```text
Gamma(V,d) = intersection_m G_m(d) != empty,
```

then full model identification is unnecessary to act safely.  It does **not**
follow that further cognition has zero value: information may reveal a cheaper
protected action.

Paid cognition therefore compares stopping with the cost of another cognitive
action rather than stopping automatically at unanimity.

### T2 — paid finite cognition obeys a Bellman recurrence

With finite metalevel state and bounded cognitive actions,

```text
V_0(s) = Stop(s)
V_k(s) = min(
  Stop(s),
  min_u c(s,u) + E[V_{k-1}(S')]
).
```

Induction on `k` proves optimality.  The implementation of this metapolicy is not
free: lookup, computation, training, storage, update, checkpoint and replay must
be included in the lifecycle account.

### T3 — observation collisions are capacity-independent impossibilities

If legal feature representation `phi` maps two states to the same feature value
but their optimal action sets are disjoint, no deterministic selector on `phi`
can be optimal in both states.  If their protected acceptable sets are disjoint,
no randomized selector can guarantee safety in both either.

For fixed-prior expected cost, the exact feature-conditional regret floor is
obtained by minimizing aggregate action loss inside each feature fiber.
Randomization cannot improve that fixed-fiber Bayes objective because the risk is
linear in the mixture.

### T4 — tied actions require overlapping decision regions, not a naive quotient

The relation "two states share some optimum" is not transitive.  Example:

```text
A*(x)={a,b}
A*(y)={b,c}
A*(z)={c,a}.
```

Every pair overlaps but all three have no common action.  Therefore tied-action
problems do not automatically admit one unique coarsest partition obtained from
pairwise overlap.  Decision Region Determination's overlapping regions are the
correct mature parent.

### T5 — deterministic feature compression is a Blackwell garbling

If `Z=phi(Y)`, every decision policy using `Z` can be simulated after observing
`Y`.  Hence full observation cannot have higher optimal Bayes risk than its
deterministic compression.  This gives the correct decision-relative language
for information loss; mutual information alone is not economic value.

### T6 — lifecycle equivalence needs successor behavior, not just current answer

Contract bisimulation preserves finite-horizon value when equivalent states have
the same admissible actions, immediate protected contract/cost, and transition
mass into every equivalence class.  Same current output checks only one
projection and is insufficient when revocation, replay, reset, support or future
retained state can differ.

This is the formal parent for R0A exact early exit.

### T7 — price-independent dominance is componentwise dominance

For nonnegative resource prices `w`,

```text
c_A <= c_B componentwise
iff
w.c_A <= w.c_B for every w>=0.
```

Therefore local gains, query-count savings, or one retrospective exchange rate
cannot establish general whole-machine improvement.

---

## 4. R0A — exact early exit, not learned reordering

The original compose-router population is not a routing opportunity: candidate
operators are already evaluated before the learned decision, so reordering
cannot avoid compose/check work.  The legitimate optimization is exact early
exit after a sufficient answer.

The mature proof obligation is now precise:

```text
removed checks must be silent under a frozen protected trace alphabet;
current output must match;
failure knowledge / trace / learning-side effects must match;
future lifecycle behavior must remain in the same contract-equivalence class.
```

Use branching/stuttering equivalence or criterion-relative slicing as the parent,
not output equality alone.

**Current R0A status:** formal parent identified; executable full trace/lifecycle
equivalence proof over the actual compose early-exit transformation remains to be
completed.  No learned reorder is justified in the meantime.

---

## 5. R0B Phase 1/2A — target-specific routing residual is tiny

Frozen population:

```text
142 exact polynomial targets
shortest primitive length = 4
semantic frontier = 256 transitions / 206 states
142 distinct discovery ranks
```

Source-derived expected static crossover:

```text
transitions                 semantic first wins at H=4
arithmetic additions        semantic first wins at H=6
arithmetic multiplications  semantic first wins at H=9
inverse Pareto-better through H=3
semantic Pareto-better from H=9
H=4..8 price-sensitive
```

The original Phase-1 cost-informed DP is an oracle only over its two original
per-query actions:

```text
inverse
target-triggered persistent semantic
```

It is not a global upper bound after adding new action families.

The Phase-2A prospective legal-feature audit gives the strongest target-routing
negative result.  With F2 magnitude features, the maximum exact
feature-conditional regret relative to the cost-informed two-arm oracle is:

```text
transitions                 0.0762783%
arithmetic additions        0.0464371%
arithmetic multiplications  0.0364070%
```

before paying feature acquisition, policy inference, training or lifecycle cost.
F3 exact task identity has zero regret, proving information sufficiency in
principle but not cheap deployable routing.

**Interpretation:** target classification ambiguity can remain while its economic
routing residual is essentially negligible.  Do not fit the MLP to this residual.

---

## 6. R0B Phase 2B0 — partial semantic prebuild is a valid reduction but a dead parent

A fixed-frontier family was constructed:

```text
prebuild semantic frontier f;
never target-expand semantic state;
answer indexed targets semantically;
fall back to exact inverse outside the frontier.
```

Under the frozen IID target distribution its Pareto-pruned setup/rate points do
satisfy a monotone multislope geometry on every primary coordinate.  Thus the
capital-investment reduction is mathematically legitimate.

However the known-horizon offline envelope gains **0%** over the incumbent best
static exact arm on every primary coordinate.  It is therefore a dominated
scientific parent.  We do not continue to a competitive multislope scheduler for
this family merely because the theorem applies.

**Terminal:** reduction supported, parent economically dominated.

---

## 7. R0B Phase 2B1/2B2 — exact online lifetime parents

For the incumbent one-way family, use inverse for `tau` demands and then switch
once to a cold persistent semantic session:

```text
C_tau(H) = I(H)                    H<=tau
           I(tau)+S(H-tau)         H>tau.
```

### Deterministic minimax, scalar coordinates

Exact exhaustive search over `H=1..142` gives:

```text
transitions                 tau=2   ratio 1.635612818
arithmetic additions        tau=4   ratio 1.503896159
arithmetic multiplications  tau=6   ratio 1.513430075
```

A single deterministic threshold robust across all three coordinates has
`tau=3` and worst ratio about `1.869814604`.

### Randomized time-only minimax

Treat horizons as rows, thresholds as columns, and competitive ratios as matrix
entries.  Against an **oblivious** horizon adversary, the exact randomized parent
is a finite zero-sum game.  Frozen primal/dual certificates are independently
recomputed in CI without importing the LP solver.

Coordinate-specific certified values:

```text
transitions                 1.368216034
arithmetic additions        1.325270314
arithmetic multiplications  1.333712604
```

One threshold distribution robust across all primary coordinates has certified
value

```text
1.559190999265383
```

versus about `1.869815` for the best single deterministic joint threshold.

This proves that private randomization materially helps the no-feature online
parent, but it still leaves a large gap to a clairvoyant static benchmark.

Randomization does **not** carry this guarantee against an adversary that first
observes the private threshold draw and then chooses the horizon.

---

## 8. R0B known-H Pareto collapse — no hidden intermediate strategy population

The all-horizon raw-vector verifier enumerates every deterministic one-way
threshold and removes dominated vectors.  The exact pattern is:

```text
H<=3    inverse only
H=4..8  inverse + semantic
H>=9    semantic only
```

No intermediate `0<tau<H` is Pareto-efficient for any `H=1..142`.

This strengthens the static crossover result: the price-sensitive band is not
hiding a third deterministic threshold strategy.  At known horizon, the exact
multi-objective coverage set has size at most two.

---

## 9. Objective uncertainty is separate from horizon uncertainty

For candidate raw vector `C` and static exact vectors `A,B`, define

```text
rho_w = (w.C)/min(w.A,w.B),  w>=0, w!=0.
```

The exact robust-price identity is

```text
sup_w rho_w
=
max_i C_i/min(A_i,B_i).
```

The upper bound follows from componentwise inequalities; the lower bound is
attained by a basis price on the worst coordinate.

Thus the coordinate-stacked minimax game is exactly the robust game over every
nonnegative linear scalarization, not merely a conservative surrogate.

### Perfect H still leaves a robust-price lower bound

Even if exact horizon `H` is revealed for free before choosing a randomized
threshold, the best price-blind policy has certified robust values:

```text
H=4  1.033708135
H=5  1.161619762
H=6  1.163222032
H=7  1.095289088
H=8  1.004075212
```

with exact ratio one outside the price-sensitive band on the frozen range.

Therefore a price-blind `1.05` claim is impossible at H=5,6,7 even with perfect
lifetime prediction.  The hardest certified point is H=6 at
`1.1632220323971705`.

This is **objective conflict**, not a prediction lower bound.

### Multi-objective parent

Under a known nonnegative linear `w`, randomization cannot improve expected scalar
cost: a mixture is a convex combination of deterministic scalar costs.  The
source-derived linear-objective coverage set is exactly:

```text
{inverse}             H<=3
{inverse, semantic}   H=4..8
{semantic}            H>=9.
```

If `w` is unknown during planning but supplied before the final choice, retain
this tiny coverage set.  If `w` is never supplied, report Pareto/coverage output
or prospectively declare a robust preference objective.

Do not ask ML to infer an unstated experiment objective.

---

## 10. R0B lifecycle advice — future identity can collapse to a decision region, but only under a fixed scalar objective

For one registered scalar coordinate, define the static decision bit

```text
Z_r(H)=0  if inverse is no worse
       1  if semantic is cheaper.
```

A perfect `Z_r` bit is sufficient to recover the two-static-arm benchmark on that
coordinate.  Full horizon identity is unnecessary for that **ex-post static
choice**.

The robust-advice game then gives an exact strong error contract required for a
1.05 bound before acquisition cost.  Current frozen certificates place the
per-horizon adversarial error allowance at approximately:

```text
transitions                 epsilon <= 3.03%
arithmetic additions        epsilon <= 2.80%
arithmetic multiplications  epsilon <= 2.45%
```

These are not ordinary average classifier accuracies.  They are robust
per-horizon error guarantees inside the declared advised-threshold family.

The advice bit is neither assumed observable nor free.  No predictor has been
trained.

---

## 11. Ex-post decision bits are not necessarily ex-ante economic belief state

For Bayes switching under a lifetime belief `P`, define

```text
L_P(tau)=E_P[C(H,tau)].
```

A calibrated probability

```text
P[semantic-static-region]
```

is not generally sufficient for minimizing `L_P`.  Source-derived theorem
counterexamples exhibit two synthetic priors with the same region probability
but disjoint optimal threshold sets.

A stronger collision now holds even for

```text
phi(P)=(E_P[H], P[semantic-static-region]).
```

For every primary coordinate there exist simple equal-weight two-point priors
with the same mean and the same region probability but disjoint Bayes-optimal
thresholds.  The executable verifier searches for the witnesses from the frozen
cost curves instead of trusting hard-coded outcomes.

Hence neither a mean-horizon regressor nor `mean + long-probability` is a general
sufficient economic representation.  A larger neural model on the same two
statistics cannot repair the lost distribution shape.

For the finite threshold family, the expected policy-loss vector

```text
ell_P(tau)=E_P[C(H,tau)]
```

is a sufficient finite parent representation.  The full posterior over `H` is
also sufficient but is not claimed minimal.

---

## 12. Paid horizon information — prediction is cognition

No operational lifetime prior or lawful forecast source is registered in the
current R0B protocol.  Synthetic priors are theorem hostiles only.

If a future prior `pi` is prospectively admitted, the no-signal Bayes parent is

```text
R_0(pi)=min_tau sum_H pi_H C_tau(H).
```

A finite signal channel `K(z|H)` has free-signal Bayes risk

```text
R_K(pi,0)
 = sum_z min_tau sum_H pi_H K(z|H) C_tau(H).
```

The signal cannot hurt when free because it can be ignored.  Perfect horizon
identity gives the gross-information upper bound.

If acquisition cost is `c`, do not necessarily query at session start.  A delayed
parent uses inverse for `d` demands and buys the signal only on paths that survive
to `d`.  The expected signal charge is therefore weighted by `P(H>d)`.

This directly instantiates the costly-prediction literature:

```text
whether to ask;
when to ask;
what to do after the answer;
and whether the value repays acquisition/maintenance cost.
```

The age/survival event `H>d` is already free information and must be included in
the baseline posterior.

**Current empirical terminal:**

```text
DEMAND_SIGNAL_SOURCE_NOT_ESTABLISHED_R0B_PHASE2C0
```

No learned lifetime predictor should be evaluated as if an operational prior
already existed.

---

## 13. R0C — proof scheduling is a portfolio problem unless a richer population survives

The native proof lane contains a real local method improvement but not a
whole-machine win under current cold overhead.  Layered/indexed scheduling is a
legitimate exact strategy population only if a much larger frozen proof family
shows distinct legally observable regimes.

Mature parents already exist:

```text
algorithm portfolios
E auto-schedule
Vampire portfolio/CASC schedules
MaLeS / BliStr-style ATP strategy selection and tuning
restart theory when its stochastic independence assumptions actually hold
```

Eventual theorem truth/falsity is not a legal pre-proof selector feature.

**Current R0C status:** parent family identified; larger prospectively frozen
proof population and complete runtime/lifecycle accounting remain prerequisites.
No learned proof scheduler is authorized by the existing small population.

---

## 14. R0D — common-action identification is Decision Region Determination with cognition cost

DEV5 already establishes the core structural fact: singleton model identification
can be unnecessary when surviving models share a protected action.  DEV6/X1 show
that computing the stopping predicate or active probe can itself cost more than
the work saved.

The correct R0D experiment is therefore not "unanimity versus singleton" in
isolation.  It is a finite paid Decision Region Determination problem comparing:

```text
full identification
singleton stopping
common protected-action stopping
paid adaptive probing
exact Bellman/DP policy
```

while charging predicate maintenance, probe cost and final action work.

**Current R0D status:** formal recurrence and DRD parent are ready; the paid
common-action experiment must be rerun on the actual source-controlled donor
before an economic terminal is claimed.

---

## 15. Misspecification remains orthogonal to all of the above

A version space can collapse to a confident singleton and still be wrong when
the protected world lies outside the hypothesis class.  If two possible worlds
are indistinguishable under every legal transcript but require disjoint safe
actions, no policy on that transcript can guarantee safety in both.

Therefore prediction, posterior confidence, low entropy, advice quality and
Bayesian optimality remain subordinate to one of:

```text
an adequacy/coverage argument for the protected class; or
an independent fail-closed checker/authority boundary.
```

This is not solved by better calibration alone.

---

## 16. What is now ruled out

The following research moves are not justified by current evidence:

```text
train target-specific MLP on F2/F3 merely because labels differ;
claim the Phase-1 two-arm DP is a global oracle after adding actions;
continue partial-frontier multislope scheduling after its 0% known-H gain;
treat lifetime prediction as the explanation for price-objective conflict;
use a binary long/short probability or mean horizon as a generally sufficient Bayes state;
credit predictions without acquisition/inference/lifecycle cost;
use current-output equality as proof of R0A lifecycle equivalence;
use proof outcome as a pre-proof selector feature;
use confidence/singleton version space as authority under misspecification;
select a favorable resource exchange rate after seeing the outcome.
```

These are negative results, not unfinished engineering preferences.

---

## 17. What remains genuinely open

The remaining high-value gaps are much narrower than the original learned-router
proposal:

```text
R0A
  prove complete protected trace/lifecycle equivalence for exact early exit.

R0B objective
  register the actual scalar/constraint/robust resource objective, or explicitly
  accept Pareto/coverage-set output.

R0B demand
  establish source custody for a real effective-lifetime process and any lawful
  pre-decision lifecycle signal; then run paid VOI against age-only exact parents.

R0B state
  extend legal-feature/state sufficiency beyond the cold-frontier audit only if a
  declared objective/demand model makes that state economically relevant.

R0C
  freeze a substantially larger proof-search population and compare exact
  portfolio parents before statistical/learned scheduling.

R0D
  execute paid DRD/common-action Bellman parents on the real donor, including
  predicate and maintenance costs.

All lanes
  preserve misspecification/fail-closed authority boundaries and whole-machine
  lifecycle accounting.
```

Only a residual that survives these exact parents becomes ordinary algorithm
selection.  Only after ordinary statistical parents fail does a tiny MLP become a
scientifically justified next parent.

---

## 18. Current convergence statement

The best current formulation of Minimum Sufficient Cognition is:

> Given the protected contract and a prospectively declared objective, retain the
> coarsest legally observable lifecycle state that preserves protected decision
> value; acquire additional information or reusable computation only when its
> complete expected protected value exceeds acquisition, execution, maintenance,
> storage, update, checkpoint/replay and failure-handling cost.

For R0B specifically, the evidence now says:

```text
target-specific cold routing residual     tiny before costs
partial prebuild strategy family          dominated
elapsed-time deterministic parent         substantial online gap
private randomized time-only parent       materially better, gap remains
perfect-H price-blind controller           still blocked by objective conflict
known-H deterministic coverage set         only inverse/semantic
binary / mean+binary lifetime summary       insufficient for Bayes switching
operational lifetime signal/prior           not yet source-established
```

Therefore the current research terminal remains **no learned router**.  The next
credible empirical advance is not more model capacity; it is a source-custodied
lifetime signal under a registered objective, or a proof that no such paid signal
is economic.
