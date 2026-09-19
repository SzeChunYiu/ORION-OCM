# GMI #910 finite developmental phase, hysteresis, trap, and mass theorems v1

Parent: #833 Section L. Source issue: #910. Source PR: #924. Immediate
prerequisite: PR #909.

## 1. Scope and parent subtraction

All carriers below are finite and use opaque, architecture-neutral state names.
All numeric registrations are integers or rational numbers and are evaluated
exactly. No floating-point approximation participates in a verdict.

PR #909 already owns the distinction between current capability and the maximum
capability over a coordinatewise budget-reachable developmental set. Its result
blob and claim are pinned. This tranche does not reclaim that distinction. It
asks when the reachable optimum changes along one registered budget ray.

PR #898 already owns the finite switching-cost argmin law, its symmetric
two-form band, and sufficient history-erasure controls. This tranche does not
present hysteresis as new mathematics. It imports that result into the
developmental-trajectory vocabulary required by Section L and keeps the parent
scope intact.

Finite shortest paths, graph reachability, Markov propagation, and
first-passage accounting are parent mathematics. The residual contribution is
an exact four-row contract joining those objects, complete tie handling,
hostiles, bounded exhaustive checks, and direct reconciliation.

## 2. PHASE-1 — exact budget-ray developmental transitions

Let `G=(V,E)` be a finite directed developmental graph with initial state `s`.
Every edge `e` has an exact nonnegative resource vector

`w(e) in Q_{>=0}^d`.

For a path `p`, let `W(p)` be the coordinatewise sum of its edge costs. Register
a nonzero nonnegative ray `r in Q_{>=0}^d` and define the resource budget

`B(lambda)=lambda r`, for `lambda>=0`.

For every state `v`, define its ray-entry threshold

`tau(v)=min_p max_{i:r_i>0} W_i(p)/r_i`,

where the minimum is over source-to-`v` paths satisfying
`W_i(p)=0` whenever `r_i=0`. If there is no such path, set `tau(v)=infinity`.

Only nondominated path-cost vectors need be retained. A vector dominated
coordinatewise by another source-to-state vector can never yield a smaller ray
threshold. Because edge costs are nonnegative, every reachable state has a
simple path witness: removing a cycle cannot increase any coordinate. The
finite simple-path set therefore supplies a finite minimum even when the graph
contains zero-cost cycles.

### Theorem 2.1 — exact entry threshold

State `v` is reachable under `B(lambda)` iff `tau(v)<=lambda`.

**Proof.** If `tau(v)<=lambda`, its witness path has
`W_i(p)<=tau(v)r_i<=lambda r_i` in every positive ray coordinate and zero cost
in every zero coordinate, hence is feasible. Conversely, every path feasible
under `lambda r` has `W_i(p)/r_i<=lambda` for positive coordinates and zero
demand in zero coordinates, so its threshold and therefore `tau(v)` are at
most `lambda`. QED.

Let `q:V->Q` be the externally registered score, and define the complete
reachable optimum correspondence

`Opt(lambda)=argmax { q(v) : tau(v)<=lambda }`.

### Theorem 2.2 — piecewise-constant optimum correspondence

`Opt(lambda)` is constant on every interval between consecutive distinct finite
state-entry thresholds. It can change only at an exact threshold `tau(v)`.

**Proof.** By Theorem 2.1, the reachable set is exactly the sublevel set of the
finite threshold map. No membership changes strictly between consecutive
thresholds. Since `q` is fixed, the complete argmax of that unchanged finite set
is unchanged. At a threshold, one or more states may enter; taking the full
argmax preserves all old/new score ties. QED.

The executable reports every threshold, a witnessing nondominated path-cost
vector, every entrant, the full reachable set, and the full tied argmax. It also
records thresholds where reachability changes but the optimum does not. Calling
these finite steps “phases” does not assert a thermodynamic limit or continuous
critical phenomenon.

The independent bounded oracle enumerates all simple paths instead of using the
Pareto label-setting routine. Exact agreement holds in 5,184 registered worlds
and across 11,097 threshold events.

## 3. HYST-1 — path dependence, the exact band, and erasure

For two forms `A,B`, let instantaneous base costs be `c(A),c(B)`, self-switch
cost be zero, symmetric cross-switch cost be `kappa>=0`, and

`delta=c(B)-c(A)`.

Given previous form `h`, the next-form correspondence minimizes

`c(m)+K(h,m)`

over `m in {A,B}`, preserving every tie.

For previous `A`, compare `A` with `B` by the sign of `delta+kappa`. For
previous `B`, compare them by the sign of `delta-kappa`. Hence:

- `delta < -kappa`: both histories select `B`;
- `delta = -kappa`: previous `A` ties `{A,B}`, previous `B` selects `B`;
- `-kappa < delta < kappa`: previous `A` selects `A`, previous `B` selects `B`;
- `delta = kappa`: previous `A` selects `A`, previous `B` ties `{A,B}`;
- `delta > kappa`: both histories select `A`.

The open middle interval is the exact registered switching band. At equal base
cost and positive `kappa`, the two inherited states select distinct next forms
under the same ecology. This is path dependence relative to the represented
previous-form state, not a claim that every history representation or ecology
has hysteresis.

### History-erasure controls

If `K(h,m)=u(h)+v(m)`, then `u(h)` is common to all current candidates and
cancels from the argmin. The selection correspondence is independent of `h`.
Zero switching is the special case `u=v=0`.

If a registered reset maps every old history to one canonical preselection
state `h0`, every post-reset selection equals `Sel(h0)`. The reset cost is not
silently omitted from any lifecycle objective; the identity only concerns the
post-reset selection state.

Twenty-one exact `(delta,kappa)` cases, both boundary ties, a negative-cost
hostile, origin-additive erasure, and canonical reset are replayed.

## 4. TRAP-1 — deterministic and stochastic escape

Fix an initial state `s`, nonempty target set `T`, allowed transition graph or
kernel, and a resource budget or finite horizon. A “local developmental trap”
is always relative to these registrations. Changing operators, targets, budget,
or horizon may change the verdict.

### Theorem 4.1 — deterministic escape iff a feasible path exists

Under nonnegative vector edge costs and coordinatewise budget `B`, deterministic
escape exists iff there is an allowed source-to-target path whose accumulated
cost is at most `B` coordinatewise.

**Proof.** A deterministic execution is a sequence of allowed edges, hence an
allowed path, and its charged accumulated cost must be feasible. Conversely, a
feasible allowed path directly specifies the deterministic choices that reach
its target. Nonnegative cycles can be removed, so a simple witness suffices.
QED.

The closed hostile contains a start/local cycle but no target edge. Its twin
adds exactly one budget-feasible local-to-target edge. The first is trapped and
the second has the explicit witness `start -> local -> target`.

### Theorem 4.2 — finite-horizon stochastic positive mass iff positive path

For an exact rational kernel `P`, normalized initial law `mu`, target set `T`,
and finite horizon `H`, the probability of hitting `T` by time `H` is positive
iff there exists a path of length at most `H` beginning at a state of positive
initial mass, ending in `T`, and having strictly positive transition
probability on every edge.

**Proof.** Each finite path contributes the product of its initial and edge
probabilities, all nonnegative. A positive-support target path contributes a
strictly positive summand. Conversely, a finite sum of nonnegative path
products can be positive only if at least one summand is positive, which implies
positive initial mass and positive probability on every edge. QED.

A zero-probability edge is therefore not a support path. The stochastic closed
hostile gives that edge probability zero; its twin changes only that row to add
positive target probability. Exact replay checks the iff in 18,144 bounded
kernel/initial/target/horizon cases.

## 5. MASS-1 — endpoint and cumulative first-hit reachability mass

Let `mu_t` be the full endpoint distribution. The exact finite Markov update is

`mu_{t+1}(y)=sum_x mu_t(x) P(x,y)`.

Endpoint target mass is

`e_t=sum_{y in T} mu_t(y)`.

Endpoint mass is not generally cumulative reachability mass because the kernel
may leave a target after entering it.

For first-hit accounting, remove initial target mass from the alive law. At
each step propagate only alive mass, record all mass entering `T` as new hit
mass `h_t`, and retain only the non-target remainder as the next alive law.
Then

`F_t=Pr[tau_T<=t]=sum_{j=0}^t h_j`.

### Theorem 5.1 — normalization and first-hit accounting

Every full endpoint distribution has total mass one. At every horizon,

`F_t + alive_t = 1`.

**Proof.** Row normalization makes the full Markov update mass preserving. For
the killed/alive process, propagation also preserves the current alive mass;
partitioning propagated mass into target and non-target parts gives
`alive_{t+1}+h_{t+1}=alive_t`. Induction from
`alive_0+h_0=1` yields the identity. QED.

### Theorem 5.2 — cumulative monotonicity

`F_{t+1}=F_t+h_{t+1}>=F_t` because every new-hit mass is nonnegative. QED.

### Independent oracle

The verification oracle recursively enumerates every positive-probability path
prefix. At each time it sums path products ending in `T` for endpoint mass and
path products whose first target occurrence is no later than that time for
cumulative mass. It shares validation but not the dynamic-programming
recurrence. Exact endpoint and cumulative arrays agree in all 18,144 bounded
cases.

The primary witness deliberately uses a nonabsorbing target:

- endpoint target mass: `(0, 1/2, 0)`;
- cumulative first-hit mass: `(0, 1/2, 1/2)`.

This hostile prevents substitution of endpoint occupancy for ever-hit mass.

## 6. Negative controls and custody

The package fails closed on malformed carriers, unknown endpoints/targets,
dimension mismatch, negative or inexact resources, a zero budget ray, negative
switching burden, incomplete switching domains, negative/unnormalized/inexact
Markov rows, malformed initial laws, and negative/nonintegral horizons.

The result receipt is canonical JSON with rational values serialized as exact
strings. Tests compare it byte-for-byte in normal and optimized Python modes.
Parent bytes and claims are independently recomputed at replay. The Section-L
reconciliation whitelist contains exactly four rows and directly names PR #924
and prerequisite PR #909.

## 7. Claim boundary

If every executable and documentary check is green, this package earns only:

`GMI_833_FINITE_DEVELOPMENTAL_PHASE_HYSTERESIS_TRAP_ESCAPE_AND_REACHABILITY_MASS_AT_REGISTERED_SCOPE`.

It does not earn a continuous thermodynamic phase result, universal hysteresis,
universal trap escape, a stationary/asymptotic Markov theorem, real-system
validation, or complete GMI. Independent hostile theorem review remains an
explicit open high-severity gap.
