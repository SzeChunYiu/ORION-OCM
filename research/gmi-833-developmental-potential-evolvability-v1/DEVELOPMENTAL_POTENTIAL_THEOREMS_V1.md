# Developmental potential, quantitative evolvability, and capital separation — v1

**Issue:** #908, child of #833 Section L  
**Freeze:** `FREEZE_V1.md` at commit `f7e3e07edd07a0edafbcb62d50f038cea6e11667`  
**Claim ceiling:** `GMI_833_FINITE_DEVELOPMENTAL_POTENTIAL_EVOLVABILITY_AND_CAPITAL_SEPARATION_AT_REGISTERED_SCOPE`

## 1. Registered objects

Fix an architecture-name-free external capability contract `c`, a finite
developmental carrier `X`, current state `x0`, finite directed development
relation `Delta`, exact nonnegative vector edge costs, development law `D`, and
coordinatewise budget `B`. Let `s_c(x)` be the protected capability score of
state `x`. This is a finite registered microscope under the #833 foundation;
it is not a universal model of development.

Separately fix a finite descendant carrier `Z`, an exact proposal kernel `Q`
on `Z`, and a registered useful-descendant set `U subseteq Z`. Proposal mass,
stored solutions, current capability, and reachable capability are kept as
different typed objects.

## 2. DP-1 — current capability is not developmental potential

Let `Reach_D(x0,B)` be states reachable on a finite path whose summed raw cost
vector is coordinatewise at most `B`. Define

`C_now = s_c(x0)`,

`C_pot(B) = max { s_c(x) : x in Reach_D(x0,B) }`,

`H_dev(B) = C_pot(B) - C_now`.

The empty-reachability ambiguity cannot arise because the length-zero path
makes `x0` reachable at every nonnegative budget. `C_now` is a present score;
`C_pot` is a budget/development-law-relative reachable envelope; `H_dev` is
headroom. None is an architecture label or intrinsic universal intelligence.

### Theorem DP-1A — budget monotonicity

If `B <= B'` coordinatewise, then

`Reach_D(x0,B) subseteq Reach_D(x0,B')`

and hence `C_pot(B) <= C_pot(B')`.

**Proof.** Every path whose nonnegative summed vector is at most `B` is also at
most `B'`. Maximization over the larger reachable set cannot decrease. `□`

### Theorem DP-1B — current capability does not identify potential

There exist states with high current capability and zero headroom, and states
with lower current capability and positive headroom. The executable crossed
witnesses use a singleton score-5 state, whose headroom is zero, and a score-1
state reaching score 5 within budget, whose headroom is 4. Therefore no
function of current score alone identifies registered potential across
development graphs.

The executor retains every nondominated path-cost vector at each state; it does
not collapse raw resources to an unregistered scalar.

## 3. EV-1 — quantitative finite evolvability

Following the already merged HST/#779 parent, define useful-descendant
evolvability at the registered target set by

`Ev_Q(U) = Q(U) = sum_{z in U} Q(z)`.

This is the probability mass a fixed proposal law assigns to a specified
useful set. It is not current capability, improvement magnitude, universal
adaptability, or evidence of open-ended evolution.

### Theorem EV-1A — iid first-hit burden

Under iid proposals from fixed `Q`, if `p=Ev_Q(U)>0` and `T` is the one-indexed
first proposal in `U`, then

`P(T=k)=(1-p)^(k-1)p` and `E[T]=1/p`.

**Proof.** `P(T>k)=(1-p)^k`. The tail-sum formula yields
`E[T]=sum_{k>=0}(1-p)^k=1/p`. `□`

If `p=0`, success has probability zero at every finite draw and no finite
expectation exists. The exact terminal is
`UNREACHABLE_ZERO_USEFUL_MASS`, never zero, a clipped number, or infinity
serialized as a floating-point value.

## 4. HIST-1 — when history improves discovery

Compare baseline kernel `Q0` with a history-conditioned kernel `QH` on the same
carrier and useful set. Require `U` to be disjoint from the explicit stored
solution set, so direct recall cannot masquerade as search improvement. Let a
proposal have exact raw burden vector `r>0`, let history-policy use have
overhead vector `h>=0`, and let preregistered nonnegative prices `pi` give
positive proposal price

`c=pi dot r > 0`, `a=pi dot h >= 0`.

Write `p0=Q0(U)` and `pH=QH(U)`.

### Theorem HIST-1A — positive-mass iff

When `p0,pH>0`, history strictly lowers expected priced discovery burden iff

`a + c/pH < c/p0`.

**Proof.** EV-1A gives expected proposal counts `1/p0` and `1/pH`.
Multiplying by per-proposal price and charging history overhead gives exactly
the two sides. Strict improvement is their strict comparison. `□`

This shows why `pH>p0` alone is insufficient when policy overhead is charged.
Equality is a tie, not an improvement. If `p0=0<pH`, history changes an
unreachable target to finite expected discovery. If `pH=0<p0`, history harms.
If both are zero, both remain unreachable.

The result is conditional on fixed iid kernels and registered prices. Proposal
count is not silently relabeled wall-clock, energy, or total lifecycle burden.

## 5. CAPITAL-1 — solution capital and search-policy capital

Define **solution capital at `U`** as an explicit stored solution lying in `U`
and therefore available for direct reuse. Define **search-policy capital at a
held-out `U`** as a changed proposal law that strictly lowers charged expected
discovery burden under HIST-1 while `U` is absent from stored solutions.

### Theorem CAPITAL-1A — discriminating interventions

1. If a solution in `U` is stored but `QH=Q0`, direct reuse can help current
   solving while the proposal law is unchanged. This is solution capital and
   not evidence of search-policy improvement.
2. If `U` is absent from storage and a changed `QH` satisfies HIST-1A, the
   improvement cannot be direct stored-answer reuse. It is search-policy
   capital at the registered held-out set.

**Proof.** In case 1 the defining intervention for policy capital—changed
charged discovery law—is absent. In case 2 the defining mediator for solution
capital—a stored member of `U`—is absent, while the discovery-burden comparison
is strict. `□`

If stored solutions intersect `U`, the policy assay reports
`CONTAMINATED_BY_STORED_SOLUTION` rather than trying to assign the observed
benefit to both mechanisms. This preserves the existing repository finding:
K1-style solution/search assistance may be supported at a registered assay
while empirical second-order K2 remains `NOT_ESTABLISHED`.

## 6. Exact replay

The executable exhaustively verifies:

- 1,512 budgeted developmental-potential cases;
- 105 exact proposal-kernel/useful-set first-hit cases;
- 300 history/overhead discovery comparisons; and
- 24 target/storage capital-separation cases.

Hostiles cover non-normalized kernels, out-of-carrier useful sets, zero mass,
stored-target leakage, unmatched carriers, omitted/negative/misaligned resource
charges, float/Boolean inputs, graph edges outside the carrier, and parent
mutation. Normal and optimized execution must emit the same receipt bytes.

## 7. Parent subtraction and boundary

Finite reachability/shortest paths, maxima over nested feasible sets, probability
mass, the geometric distribution, and solution reuse versus meta-search are
parent mathematics. The scoped contribution is their typed integration with the
upgraded #833 capability/development/resource objects and an exact separation
test that cannot turn the standing empirical K2 negative into a positive.

Allowed terminal:

`GMI_833_FINITE_DEVELOPMENTAL_POTENTIAL_EVOLVABILITY_AND_CAPITAL_SEPARATION_AT_REGISTERED_SCOPE`

Forbidden from this tranche alone: universal or open-ended evolvability,
history-always-helps, physical-runtime inference, empirical K2 closure, future
task prediction, recursive primitive invention, or complete GMI.

