# Formal Decision Core V2 — finite proofs for Minimum Sufficient Cognition

**Status:** proved finite lemmas + parent corollaries / conventional mathematics / no OCM-specific novelty claim / no ML authorization.

This note supersedes the loose "one decision quotient" wording in
`ACTION_SUFFICIENT_STATE_V1.md` wherever optimal/acceptable actions are
non-unique.  With ties, the primitive object is generally an **overlapping
family of action/decision regions** or a representation whose every fiber has a
single common admissible action.  A canonical quotient exists under stronger
uniqueness or bisimulation conditions, not in every tied decision problem.

Everything below is finite unless explicitly stated otherwise.  That keeps the
claims inspectable and gives the executable checks in `decision_core.py` a
literal mathematical target.

## 0. Basic objects

Let:

```text
X        finite set of legal world/machine states
A        finite set of protected actions/strategies
G_x      nonempty set of protected actions acceptable in state x
Q(x,a)   finite real cost of action a in state x
A*(x)    argmin_a Q(x,a)
mu(x)    probability mass, with sum_x mu(x)=1 when expected cost is used
phi:X->Z frozen prospective observation/feature map
```

For a version set `V subset X`, define

```text
Gamma(V) = intersection_{x in V} G_x.
```

When lifecycle is involved, `x` is understood to contain the retained machine
state and protected context, not only a hidden environment label.

---

## Theorem 1 — common protected action is exactly Decision Region containment

For each protected action `a`, define its decision region

```text
R_a = { x in X : a in G_x }.
```

Then, for every nonempty `V subset X`,

```text
Gamma(V) != empty
iff
there exists a in A such that V subset R_a.
```

### Proof

`=>`: choose `a in Gamma(V)`.  By definition of intersection, `a in G_x` for
every `x in V`; hence every `x in V` lies in `R_a`, so `V subset R_a`.

`<=`: if `V subset R_a`, then `a in G_x` for every `x in V`, hence `a` belongs
to their intersection and `Gamma(V) != empty`.  QED.

### Consequence

This is precisely the structural condition used by overlapping Decision Region
Determination: full hidden-state identification is unnecessary once the
surviving states are contained in one action region.

It proves **safety sufficiency only**.  It says nothing about whether that common
action is economically preferable to buying another computation.

---

## Theorem 2 — safety sufficiency does not imply economic stopping

There exists a finite decision problem with `Gamma(V) != empty` in which a paid
probe strictly lowers total expected cost.

### Construction

Let `X={0,1}` with equal prior mass.  Actions are `safe`, `a0`, `a1` and costs:

```text
Q(0,safe)=Q(1,safe)=10
Q(0,a0)=0,   Q(0,a1)=100
Q(1,a1)=0,   Q(1,a0)=100.
```

Let the protected acceptable sets include `safe` in both states, so
`Gamma({0,1})` contains `safe`.  A probe costs `1` and reveals the state
perfectly.

### Proof

Stopping with the common safe action costs `10`.  Probing and then taking the
state-specific zero-cost action costs `1`.  Therefore

```text
Gamma(V) != empty
but
optimal metareasoning chooses probe.
```

QED.

### Consequence

`Gamma(V) != empty` means *full identification is unnecessary for protected
feasibility*.  The stop rule is still value-of-computation / Bellman.

---

## Theorem 3 — exact decision sufficiency of a deterministic representation

Let `phi:X->Z`.  There exists a deterministic head `g:Z->A` satisfying

```text
g(phi(x)) in A*(x) for every x in X
```

iff every nonempty feature fiber has a common optimal action:

```text
for every z in phi(X):
intersection_{x:phi(x)=z} A*(x) != empty.
```

### Proof

**Necessity.**  Suppose `g` is optimal everywhere.  Fix a fiber `F_z`.  The
single action `g(z)` is optimal at every `x in F_z`; hence `g(z)` belongs to the
intersection of all `A*(x)` in the fiber, so the intersection is nonempty.

**Sufficiency.**  For every nonempty fiber choose one action from the stated
intersection and call it `g(z)`.  By construction this action lies in `A*(x)`
for every member of the fiber.  Hence `g(phi(x))` is optimal for every `x`.
QED.

### Why pairwise overlap is insufficient

Two different failures must not be conflated.

First, "shares an optimal action" is not a transitive relation:

```text
A*(x1)={a}
A*(x2)={a,b}
A*(x3)={b}
```

Here `x1` shares an optimum with `x2`, and `x2` with `x3`, but `x1` and `x3`
do not.

Second, even pairwise overlap throughout a group does not imply a common action
for the whole group:

```text
A*(x1)={a,b}
A*(x2)={b,c}
A*(x3)={c,a}.
```

Every pair intersects but the three-way intersection is empty.

### Corollary 3.1 — unique optimum gives a canonical action quotient

If every state has a unique optimal action `a*(x)`, then

```text
x ~ y iff a*(x)=a*(y)
```

is an equivalence relation, and any exact decision-sufficient representation
must refine its action classes.  Thus the action-label quotient is the coarsest
exact deterministic representation for the one-step decision problem.

With ties, do not claim a canonical coarsest quotient without extra structure.
Use overlapping decision regions or explicit sufficient fibers/covers.

---

## Theorem 4 — exact feature-conditional Bayes cost and regret floor

For a deterministic feature map `phi` and prior `mu`, the best deterministic
feature policy has expected cost

```text
C_phi*
 = sum_z min_a sum_{x:phi(x)=z} mu(x) Q(x,a).
```

The full-information optimum is

```text
C_full*
 = sum_x mu(x) min_a Q(x,a).
```

Therefore

```text
Regret_phi = C_phi* - C_full* >= 0.
```

### Proof

A deterministic feature policy selects one action independently for each fiber.
Expected cost is

```text
sum_z sum_{x in F_z} mu(x) Q(x,g(z)).
```

The choice of `g(z)` affects only its own fiber, so minimization separates over
fibers, giving the first formula.

For every fiber and every action `a`,

```text
sum_{x in F_z} mu(x) Q(x,a)
>=
sum_{x in F_z} mu(x) min_b Q(x,b).
```

Taking the minimum over `a` preserves the inequality; summing fibers gives
`C_phi* >= C_full*`.  QED.

### Corollary 4.1 — zero regret iff each positive-mass fiber has a common optimum

Assume `mu(x)>0` for every state under consideration.  Then

```text
Regret_phi = 0
```

iff every feature fiber has a common optimal action.

**Proof.**  The `if` direction follows by selecting that action in each fiber.
For the `only-if` direction choose a minimizing feature action `a_z`.  Write

```text
d(x,a)=Q(x,a)-min_b Q(x,b) >= 0.
```

Zero total regret implies

```text
sum_{x in F_z} mu(x)d(x,a_z)=0
```

for every fiber.  Every summand is nonnegative and every weight is positive, so
all `d(x,a_z)=0`; hence `a_z` is optimal for every state in the fiber.  QED.

### Corollary 4.2 — randomized feature policies do not improve expected cost

Let a randomized feature policy choose a distribution `pi_z(a)` in each fiber.
Its fiber cost is

```text
sum_a pi_z(a) [sum_{x in F_z} mu(x)Q(x,a)].
```

This is linear in `pi_z`; its minimum over the probability simplex is attained
at an extreme point, i.e. one deterministic action.  Hence the formula above is
already the exact optimum among randomized policies under the frozen expected
cost objective.

**Boundary:** randomization can matter for minimax/competitive objectives.  This
corollary is only for expected cost under a fixed `mu`.

### R0B interpretation

`prospective_selector.py` computes this finite quantity for the frozen cold
states.  Its `<0.08%` F2 result is therefore an exact Bayes regret floor for that
feature partition before feature/policy costs, not merely a classifier error
rate.

---

## Theorem 5 — feature collision is a model-capacity impossibility

Suppose two states `x,y` have the same legal feature value:

```text
phi(x)=phi(y)
```

and disjoint optimal action sets:

```text
A*(x) intersection A*(y)=empty.
```

Then no deterministic selector `g(phi(.))` is optimal in both states.

### Proof

Equal feature values force the selector to emit the same action at `x` and `y`.
No action is optimal in both states by the disjointness assumption.  Therefore
the emitted action is nonoptimal in at least one state.  QED.

### Safe-action strengthening

If the same condition holds for protected acceptable sets `G_x` and `G_y`, then
no randomized selector based only on `phi` can guarantee a protected action in
both states either.  To be safe with probability one in state `x`, the support
of its action distribution must be contained in `G_x`; likewise it must be
contained in `G_y`.  That would require support inside `G_x intersection G_y`,
which is empty.  QED.

This is an observation-channel limit.  A larger neural network cannot remove it.

---

## Theorem 6 — deterministic feature compression is a Blackwell garbling

Let a full observation be random variable `Y`, and let the deployable feature be

```text
Z = phi(Y)
```

for deterministic `phi`.  Then the experiment observing `Z` is a garbling of the
experiment observing `Y`.  Therefore for every decision problem, prior and loss,
the optimal Bayes risk using `Y` is no worse than the optimal Bayes risk using
`Z`.

### Proof

Define a Markov kernel

```text
K(z|y) = 1 if z=phi(y), else 0.
```

Applying `K` to the output of the `Y` experiment generates exactly the `Z`
experiment.  Any policy based on `Z` can therefore be simulated after observing
`Y` by computing `phi(Y)` and executing the same policy.  The `Y` decision maker
has every policy available to the `Z` decision maker, possibly more, so its
minimum risk cannot be larger.  QED.

### Consequence

Phase-2A is naturally read as a **decision-relative loss under garbling**.  For
one frozen prior/loss it measures a Bayes-risk gap.  A Torgersen/Le Cam relative
deficiency would take a worst case over a declared family of protected decision
problems.  That is a stronger future generalization than reporting mutual
information.

---

## Theorem 7 — mutual information and decision value can separate arbitrarily

### 7A. Arbitrarily large information with zero decision value

Let hidden state `Theta` be uniform on `N` values and observe `Y=Theta`.  Then

```text
I(Theta;Y)=log N.
```

Let the same action `a0` have zero loss in every state and all other actions have
positive loss.  Both with and without `Y`, optimal loss is zero.  Thus decision
value is zero while mutual information grows without bound as `N` grows.  QED.

### 7B. Vanishing information with fixed decision value when loss scale is free

Let `Theta in {0,1}` with `P(Theta=1)=epsilon<1/2`, observe `Y=Theta`, and use
mismatch loss `M`.  Without observation the optimal action is `0` and expected
loss is `epsilon M`; with perfect observation loss is zero.

Choose `M=1/epsilon`.  Then observation value is exactly `1`, while

```text
I(Theta;Y)=H_b(epsilon) -> 0
```

as `epsilon -> 0`.  QED.

### Boundary

The second construction uses an unbounded/scaled loss.  With a fixed bounded
loss, rare-event decision value also shrinks.  The point is not that information
theory is useless; it is that Shannon bits are not a universal substitute for
protected computational/economic value without explicit loss assumptions.

---

## Lemma 8 — adaptive probe bit bounds must be conditional

Let `Theta` be the decision-relevant target and let an adaptive procedure choose
probe `P_i` from history `H_{i-1}`, observe `Y_i`, and extend the history.  The
chain rule gives

```text
I(Theta;Y_1,...,Y_n | P_1,...,P_n as generated)
 = sum_i I(Theta;Y_i | H_{i-1},P_i)
```

under the usual representation of the adaptive transcript.

Hence if every legal probe satisfies the **conditional** bound

```text
I(Theta;Y_i | H_{i-1},P_i) <= b,
```

then the whole transcript carries at most `nb` bits about `Theta`.

A bound only on marginal `I(Theta;Y_i)` is insufficient because observations can
be individually weak or redundant/masked while becoming informative jointly.

This is the correct starting point if a Fano-style lower bound is used again.
The target should be the required decision class/region unless full identity is
itself necessary.

---

## Theorem 9 — finite paid-cognition Bellman recurrence is optimal

Let `S` be a finite metalevel state space.  In state `s` the machine may either:

- stop and pay `Stop(s)`; or
- choose cognitive action `u`, pay nonnegative `c(s,u)`, and move to `s'` with
  probability `P(s'|s,u)`.

Allow at most `k` cognitive actions before mandatory stopping.  Define

```text
V_0(s) = Stop(s)

V_k(s) = min(
  Stop(s),
  min_u [ c(s,u) + sum_s' P(s'|s,u)V_{k-1}(s') ]
).
```

Then `V_k(s)` is the minimum expected total cost achievable from `s` with at most
`k` cognitive actions.

### Proof by induction on `k`

Base `k=0`: no cognitive action is allowed, so stopping is the only legal policy
and cost is `Stop(s)`.

Inductive step: any legal policy with budget `k` either stops immediately, paying
`Stop(s)`, or chooses some first cognitive action `u`, pays `c(s,u)`, observes a
successor `s'`, and then has at most `k-1` cognitive actions left.  By the
induction hypothesis, optimal continuation cost from `s'` is `V_{k-1}(s')`.
Taking expectation and then the minimum over the first legal choice gives the
stated recurrence.  QED.

### Exact stopping rule

Stop in `(s,k)` iff

```text
Stop(s)
<=
c(s,u) + E[V_{k-1}(S')]
```

for every admissible cognitive action `u`.

### Meta-meta accounting

The theorem prices the modeled actions.  If evaluating or maintaining the
Bellman policy itself consumes resources, that computation must be:

1. included as an additional modeled resource/action; or
2. precompiled and its build/storage/update/checkpoint/replay cost charged to the
   lifecycle.

The mathematical optimum is not a free implementation.

---

## Theorem 10 — protected contract bisimulation preserves finite-horizon value

Consider a finite controlled Markov model with state set `S`, common action set
`A`, immediate protected contract/cost `c(s,a)` and transition kernel
`P(.|s,a)`.  Let `~` be an equivalence relation such that whenever `s~t`:

1. the same actions are admissible;
2. `c(s,a)=c(t,a)` for every admissible action `a` (this may be a tuple containing
   output, authority status and raw resource vector, provided comparison is
   componentwise/exact as registered);
3. for every equivalence class `B` and every action `a`,

```text
sum_{s' in B} P(s'|s,a)
=
sum_{s' in B} P(s'|t,a).
```

Then for every finite horizon, quotient-state dynamic programming yields the same
value for all states in each class, and every quotient policy lifts to a ground
policy with the same class-conditional behavior/value.

### Proof

Induct on horizon.  At horizon zero the continuation value is equal by
definition.  Assume the value is constant on every equivalence class at horizon
`h-1`.  For any action `a`, states `s~t` have equal immediate cost by condition
2.  Their expected continuation values are sums over equivalence classes; by
condition 3 they assign the same probability to each class, and by the induction
hypothesis every state in a class has the same continuation value.  Hence every
action has identical `Q_h` value at `s` and `t`; minimizing over the common
action set gives equal `V_h`, and any quotient action has identical value in both.
QED.

### Lifecycle consequence

"Same output now" checks condition 2 only for one immediate projection.  It does
not imply condition 3.  If revocation, reset, replay, support withdrawal or
retained search state can lead to different successor classes, current-answer
equivalence is insufficient for persistent-policy safety.

---

## Theorem 11 — indistinguishable misspecification can make protected safety impossible

Let two possible worlds `theta_1,theta_2` induce identical distributions over the
entire legal adaptive observation transcript for every permitted probing policy.
Suppose their final protected safe-action sets are disjoint:

```text
G_1 intersection G_2 = empty.
```

Then no policy using only those legal transcripts can guarantee a safe final
action in both worlds, even if the final policy randomizes.

### Proof

Because the transcript distributions are identical, the joint distribution of
transcript and final action generated by any fixed policy is identical under the
two worlds.  To be safe with probability one under `theta_1`, every final action
with positive probability must lie in `G_1`.  The same action distribution must,
under `theta_2`, have support inside `G_2`.  Thus its support must be contained in
`G_1 intersection G_2`, which is empty, contradiction.  QED.

### Misspecified-class corollary

If the true world lies outside hypothesis class `H` and is observationally
indistinguishable from an in-class surrogate but requires a disjoint protected
action, then posterior concentration, singleton version space, low entropy or a
large prediction margin inside `H` cannot by themselves authorize action.

Agnostic learning can target best-in-class prediction under non-realizability;
it does not prove protected class adequacy.

---

## Theorem 12 — raw resource dominance is exactly price-independent dominance

Let resource costs `c_A,c_B in R^d` and consider all nonnegative price vectors
`w>=0`.  Then

```text
c_A <= c_B componentwise
iff
w.c_A <= w.c_B for every w>=0.
```

### Proof

If componentwise dominance holds, multiplying each coordinate inequality by
nonnegative `w_i` and summing gives the scalar inequality.

Conversely, suppose componentwise dominance fails.  Then some coordinate `j`
has `c_A[j] > c_B[j]`.  Choose price vector `w=e_j`, the `j`th coordinate basis
vector.  Then `w.c_A > w.c_B`, contradicting the assumed scalar inequality for
all nonnegative prices.  QED.

### Corollary 12.1 — incomparable policies define price regimes

If `A` is cheaper in some coordinate and `B` is cheaper in another, basis-vector
prices exist that prefer each policy.  Therefore neither is generally better;
the result is a price region unless a prospectively justified price vector is
part of the experiment.

This is the exact finite discipline behind the X3 repricing warning.

---

## Lemma 13 — local method gain is not whole-machine gain

Write total costs as

```text
T_A = M_A + O_A
T_B = M_B + O_B,
```

where `M` is the method/search component and `O` all remaining machine overhead.
Assume method A is locally cheaper, `M_A < M_B`.  Then

```text
T_A < T_B
iff
M_B - M_A > O_A - O_B.
```

### Proof

Rearrange

```text
M_A + O_A < M_B + O_B.
```

QED.

This formalizes the native-proof result: fewer proof attempts or a shorter proof
method is real local evidence, but whole-machine advantage additionally requires
the saving to exceed extra runtime/compilation/coordination overhead.

---

## Lemma 14 — probe efficiency does not imply computational efficiency

No ordering of a single resource coordinate implies Pareto dominance of a
multi-resource cost vector.

### Proof by counterexample

Let algorithm A use resource vector

```text
(queries=1, other_operations=100)
```

and algorithm B use

```text
(queries=2, other_operations=1).
```

A is strictly better on queries and strictly worse on other operations.  Neither
componentwise dominates.  QED.

Hence source-query count, checker-call count, candidate count or action-attempt
count must not be reported as total cognition unless the other relevant resource
coordinates are known not to worsen.

---

## Theorem 15 — exact condition for reducing fixed-frontier R0B to multislope form

This theorem is a **conditional reduction**, not a claim that the current online
R0B process already satisfies ordinary multislope ski rental.

Assume:

1. a frozen target demand distribution `mu(q)`;
2. before each demand the investment controller chooses only a persistent
   frontier level `f`, without observing future targets;
3. reaching frontier `f` has cumulative setup cost `B(f)`, and upgrading
   `f->g` costs exactly `B(g)-B(f)` for `g>=f` on the registered coordinate;
4. once frontier `f` is fixed, every demand is answered without changing `f`,
   with target cost `C_f(q)` (for example semantic hit inside the frontier and
   exact inverse fallback outside it);
5. target draws are iid from `mu` conditional on the unknown lifetime `H`;
6. after removing dominated frontier levels, larger setup cost has weakly lower
   expected recurring cost.

Define

```text
b_f = B(f)
r_f = E_{q~mu}[C_f(q)].
```

Then for every fixed lifetime `H`, the expected cost of remaining on level `f`
is exactly

```text
b_f + H r_f,
```

and an adaptive schedule of additive frontier upgrades has the same expected
cost as the corresponding additive multislope ski-rental schedule.  Thus an
online multislope parent may be applied under these assumptions.

### Proof

Setup/upgrade costs telescope by assumption 3 to the setup cost of the final
level plus the appropriate prior levels exactly as in an additive investment
schedule.  While the controller remains at level `f`, assumption 4 makes each
demand cost `C_f(q)` without changing state.  By iid demand and linearity of
expectation, each such demand has expected cost `r_f`; hence `n` demands spent at
that level contribute `n r_f` in expectation.  Summing setup increments and
per-level demand intervals gives exactly the cost expression of an additive
multislope schedule.  QED.

### Why this is only conditional for current R0B

The existing semantic donor normally expands to a target-specific discovery rank
`R(q)`.  Its one-query cost is therefore state- and target-dependent, not a
fixed slope rate.  To use Theorem 15 we must first construct and verify a
**prebuild + no-expansion semantic hit + inverse fallback** parent (or another
fixed-frontier parent), derive its raw `C_f(q)`, and check the monotone slope
condition.  Otherwise use the more general online capital-investment / finite
state-control parent.

This is the next exact reduction audit, not an excuse to import a learned horizon
predictor.

---

## 16. Parent results we adopt rather than re-prove here

The following deep results are mature parents and are cited rather than
re-derived from first principles in this repository:

- Blackwell's full equivalence of experiment comparison and garbling under its
  regularity setting;
- Le Cam/Torgersen deficiency theory and its minimax/Bayes-risk equivalences;
- approximation/competitive guarantees of EC2/HEC/DIRECT;
- stochastic-bisimulation minimization algorithms and quantitative
  bisimulation-metric bounds;
- competitive ratios for online capital investment and multislope ski rental;
- asymptotic Bayesian posterior behavior under misspecification.

OCM work should instantiate their hypotheses carefully and test whether the
runtime satisfies those hypotheses.  Re-proving established general theorems
would add less value than proving the reduction/admission conditions that bind
them to the machine.

---

## 17. Resulting research gates

The formal core now supports a stricter sequence:

```text
G0  protected decision regions exist / authority language is adequate
G1  legal observation fibers are tested for common protected/optimal actions
G2  feature-conditional Bayes regret floor is measured
G3  lifecycle state is reduced only under contract bisimulation/information-state conditions
G4  paid-cognition Bellman / simple exact stopping parents are evaluated and charged
G5  unknown lifetime is tested against capital-investment / multislope reductions
G6  only a residual that survives those parents becomes ordinary algorithm selection
G7  a learned selector is considered only after simpler statistical parents fail
```

At every gate, a negative result is a successful terminal.

The current R0B evidence has passed only the cold known-horizon form of G1/G2.
It has **not** established nonzero-frontier sufficiency, an exact multislope
reduction, an unknown-horizon advantage, or a payable learned residual.