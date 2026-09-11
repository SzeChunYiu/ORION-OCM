# GMI Mechanism Necessity / Information Theorems v1

Status: **FORMAL THEORY HARDENING — MOST MATHEMATICS PARENT/Elementary; GMI INTERPRETATION ONLY**

Status date: 2026-09-12.

Refs:

- `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`
- `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`
- `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`
- `GMI_MECHANISM_WITNESS_REGISTRY_V1.md`
- `GMI_MORPHOLOGY_SELECTION_NO_GO_V1.md`

Purpose:

> Replace some architecture heuristics with implementation-neutral necessity statements and explicit non-identifiability theorems. The goal is not to prove VLC globally optimal. The goal is to identify what *any* exact realization must preserve or pay when a registered obligation contains particular future distinctions.

These results are intentionally finite/exact unless stated otherwise.

---

# 1. Setup

Let a fixed registered obligation `Omega` induce semantic developmental quotient

\[
S_\Omega.
\]

Any exact realization must preserve every distinction in `S_Omega` by `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`.

The important observation for the present document is:

> mechanisms such as rollback, historical persistence and authority/serving separation become necessary only when the protected future continuation class makes their missing information semantically relevant.

Therefore the strongest GMI claims should derive mechanism pressure from *future distinguishability*, not from architecture labels.

---

# 2. GMI-MN1 — exact rejectable-update recoverability theorem

## Statement

Let `S` be a finite set of incumbent semantic states at the registered scope.

Fix one candidate-producing update transformation

\[
T:S\to C.
\]

Suppose:

1. the update may be rejected after `T(s)` is produced;
2. on rejection the obligation requires exact restoration/continued serving of incumbent state `s`;
3. no external oracle may re-supply lost information for free;
4. after candidate production the realization retains candidate state `T(s)` plus auxiliary retained rollback/staging information `R(s)`.

Then exact rejection recovery requires the map

\[
F:S\to C\times\mathcal R,
\qquad
F(s)=(T(s),R(s))
\]

to be injective.

## Proof

Assume `F` is not injective. Then there exist `s_1 != s_2` such that

\[
T(s_1)=T(s_2)
\]

and

\[
R(s_1)=R(s_2).
\]

After candidate production, the recovery mechanism receives exactly the same retained information for both incumbents.

A deterministic exact recovery procedure therefore cannot output both distinct states correctly. A randomized recovery procedure cannot guarantee exact restoration of both states either because its conditional input state is identical.

Contradiction.

Therefore `F` must be injective.

QED.

## Corollary MN1-a — worst-case rollback information lower bound

For each candidate image `c`, the auxiliary retained information must distinguish every member of the fiber

\[
T^{-1}(c).
\]

Therefore

\[
|\mathcal R|
\ge
\max_c |T^{-1}(c)|
\]

for a fixed-width code space, and the required worst-case auxiliary bits satisfy

\[
\boxed{
B_{rollback}
\ge
\left\lceil
\log_2
\max_c |T^{-1}(c)|
\right\rceil.
}
\]

This bound is relative to information not already preserved in `T(s)` or another legally retained state component.

## Corollary MN1-b — average coding form

Under a prospectively frozen distribution over incumbent states, any uniquely decodable/prefix-free exact auxiliary code has expected length bounded below by the corresponding conditional information requirement, up to standard coding constants:

\[
E[L(R)]
\gtrsim
H(S_{old}\mid T(S_{old})).
\]

Parent status: elementary lossless coding/injective-recovery logic.

## GMI consequence

The theory should predict:

```text
old-state information must remain available until rejection is impossible
```

not:

```text
there must be two full physical copies.
```

Shadow copies, copy-on-write, logs, checkpoints, reversible deltas and persistent roots are different realization responses to the same semantic information obligation.

This is the formal core of mechanism A4.

---

# 3. GMI-MN2 — developmental side-information theorem for serving compilation

## Statement

Let

\[
K:S_\Omega\to C_{serve}
\]

be a serving compiler/materialization.

Suppose the exact realization retains serving state `K(s)` plus auxiliary persistent developmental state `A(s)` from which all protected future developmental distinctions must remain realizable.

Then the combined map

\[
s\mapsto(K(s),A(s))
\]

must be injective over `S_Omega`.

## Proof

If distinct quotient states `s_1 != s_2` map to the same pair `(K,A)`, then the realization aliases a distinction that `S_Omega` guarantees is separated by some legal future continuation.

This violates exact adequacy by `GMI-SQ5`.

QED.

## Corollary MN2-a — side-information lower bound

For fixed serving representation `K`, persistent developmental side information must distinguish each fiber of `K`:

\[
|\mathcal A|
\ge
\max_c |K^{-1}(c)|,
\]

hence fixed-width side information requires at least

\[
\boxed{
B_{dev-side}
\ge
\left\lceil
\log_2
\max_c |K^{-1}(c)|
\right\rceil
}
\]

bits beyond what the serving code preserves, under the same finite exact qualifications.

## Interpretation

This is a stronger and cleaner form of VLC P2.

Authority/serving separation is not universally required.

It becomes necessary in the information sense when:

```text
1. the serving representation intentionally merges developmental quotient states;
2. those merged distinctions remain relevant to legal future development;
3. reacquisition from an external source is unavailable or charged.
```

If `K` is itself injective on `S_Omega`, no separate developmental side state is forced by this theorem.

If the obligation weakens so future development no longer distinguishes the states, the lower bound can disappear.

Parent status: direct consequence of semantic sufficiency and elementary coding.

---

# 4. GMI-MN3 — historical lineage quotient theorem

Historical persistence should be derived from the obligation, not from update rate.

## Setup

Let `H` be a finite set of legal developmental histories up to present time.

After the present time, let the registered continuation alphabet include historical/as-of/branch/provenance queries whenever the obligation requires them.

Define

\[
h_1\sim_{lin}h_2
\]

iff every legal future continuation containing current and historical queries yields the same protected semantic trace from histories `h_1` and `h_2`.

Define the historical-lineage quotient

\[
L_\Omega=H/\sim_{lin}.
\]

## Statement

Any exact realization of the obligation after those histories must preserve at least the distinctions in `L_Omega`.

Thus any exact finite discrete realization state `Z` satisfies

\[
|Z|
\ge
|L_\Omega|
\]

with an information lower bound

\[
\boxed{
B_{lineage}
\ge
\lceil\log_2|L_\Omega|\rceil
}
\]

under the same exact/discrete assumptions.

## Proof

This is `GMI-SQ1/SQ2` applied to developmental histories when historical queries are part of the legal future continuation class.

QED.

## Important consequence

`beta_lin` in `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md` is best interpreted as a **structured measurable projection of lineage distinctions already induced by Omega**, not as a new ontological primitive independent of semantic state.

Likewise `Delta_Q`, `Delta_U`, `chi_V`, etc. are structured projections/functionals of the obligation used because the complete quotient is often too large to serve directly as a predictive signature.

This resolves a potential redundancy problem:

```text
semantic quotient = canonical obligation-relative distinction object;
Xi coordinates     = compact measurable projections proposed to predict realization economics/mechanism pressure.
```

They are not competing definitions of cognition.

---

# 5. GMI-MN4 — drift does not identify persistence demand

## Statement

No predictor using update/invalidation rate `nu` alone can determine whether historical-state persistence A5 is semantically required over all obligations.

## Construction

Take two obligations with identical current semantics, update process and update rate `nu`.

### Obligation E — ephemeral

After each admitted update, only the latest semantic state may ever be queried. Old states may be destroyed immediately.

### Obligation P — persistent

After each admitted update, a legal future query may request any previous admitted semantic state exactly.

The environment update process can be identical in E and P, hence `nu` is identical.

An in-place destructive realization that preserves only the latest state can be semantically admissible in E.

The same realization is not admissible in P whenever two histories with different old states induce different legal historical-query answers.

Therefore identical `nu` admits opposite A5 necessity.

QED.

Terminal if a theory predicts A5 from `nu` alone:

```text
DRIFT_IS_NOT_VERSION_DEMAND
```

---

# 6. GMI-MN5 — query/update geometry overcompression no-go

The old scalar locality idea can be insufficient even at fixed semantic complexity.

## Statement

There exist two obligations with:

```text
same semantic state complexity sigma;
same update consequence geometry Delta_U;
same update rate/reuse/resource context;
```

but different query/composition geometry `Delta_Q` such that preferred factor granularity reverses in a fixed candidate portfolio.

## Exact construction

Consider two semantic factors `A,B` and two exact candidate realizations.

### Fine realization F

```text
local one-factor query cost       = 1
joint two-factor query cost       = 3
local one-factor update cost      = 1
```

The joint cost includes cross-factor composition.

### Coarse realization G

```text
any query cost                    = 1.5
local one-factor update cost      = 2
```

Fix identical build cost for simplicity and identical local one-factor update process in both worlds.

Thus semantic state set, `sigma` and `Delta_U` are matched.

### World Q-local

All serving queries ask only one factor.

For any positive query count and update count:

```text
F serves cheaper (1 < 1.5)
F updates cheaper (1 < 2)
```

so F dominates G on these two work coordinates.

### World Q-global

All serving queries ask both factors.

F serving cost is `3`, G serving cost is `1.5`.

Let query count be `H` and update count be `U`.

Ignoring equal build terms:

\[
C_F=3H+U,
\qquad
C_G=1.5H+2U.
\]

G is cheaper whenever

\[
1.5H>U.
\]

Choose, for example, `H=100,U=10`.

Then

```text
Q-local -> F preferred/dominant on work;
Q-global -> G lower scalar work under the frozen unit valuation.
```

The only changed obligation feature is query/composition workload geometry.

Therefore a signature that collapses query and update locality into one scalar cannot be universally sufficient even for this finite candidate class.

QED.

Terminal:

```text
DEPENDENCY_SIGNATURE_OVERCOMPRESSED
```

---

# 7. GMI-MN6 — present-signature-only response no-go under path dependence

## Statement

Suppose morphology `M` has two legal developmental histories `h_1,h_2` that produce:

```text
same present obligation-side signature Xi_obl(t);
same present exogenous context P(t);
different reachable internal realization states z_1 != z_2;
```

and there exists a legal future continuation `w` for which protected outcome/resource distributions differ:

\[
\mathcal L(Y,B\mid z_1,w)
\ne
\mathcal L(Y,B\mid z_2,w).
\]

Then no response function of present exogenous variables alone,

\[
r_M(\Xi_{obl}(t),P(t)),
\]

can exactly predict both cases.

## Proof

Both histories present identical arguments to `r_M`, so `r_M` must output the same prediction for both.

But by assumption the correct future distributions differ.

Contradiction.

QED.

## Consequence

A correct response model must do one of:

```text
include relevant realization/developmental state;
include a sufficient history summary;
condition on a reset/fixed-history protocol;
accept approximation error and state its scope.
```

This is the formal reason `R_M(Xi)` should be treated as shorthand rather than a universal memoryless law.

Continual-learning plasticity loss supplies a real parent phenomenon showing why history-sensitive response is scientifically plausible, but the theorem itself is elementary.

Terminal when the hostile is observed:

```text
STATIC_RESPONSE_INSUFFICIENT__HISTORY_REQUIRED
```

---

# 8. GMI-MN7 — mechanism encoding non-identifiability

A theory that predicts literal implementation encodings instead of semantics is not architecture-neutral.

## Definition

For registered mechanism `A_k`, define implementation equivalence

\[
M\equiv_{A_k}M'
\]

when the two realizations satisfy the same registered semantic witness contract for `A_k` over all protected mechanism probes, even if their internal data structures/source code differ.

Example A4-equivalent implementations may include:

```text
full shadow state
copy-on-write
undo log
persistent root swap
transactional private workspace
```

provided each preserves incumbent semantics until admission and exactly recovers on rejection.

## Architecture-neutrality requirement

A demand-to-mechanism prediction is implementation invariant only if its mechanism conclusion is constant over `equiv_Ak` classes, while the resource-response model may distinguish costs inside the class.

If a predictor calls only one encoding “the mechanism,” it has not identified the mechanism-level law.

Terminal:

```text
IMPLEMENTATION_LABEL_NOT_MECHANISM_LAW
```

This is a theory contract/definition, not a mathematical impossibility theorem.

---

# 9. GMI-MN8 — mechanism lower bounds are obligation-relative

The preceding lower bounds can disappear when the obligation changes.

Examples:

```text
remove rejectability/rollback requirement
-> MN1 no longer forces recoverability of incumbent state;

remove future developmental distinctions merged by K
-> MN2 side-information bound shrinks;

remove historical/as-of queries
-> lineage quotient can collapse;

make query geometry local
-> fine factorization serving penalty can disappear.
```

Therefore GMI should prefer statements of the form:

> Under obligation class `O*` and registered response/resource assumptions, every exact realization must preserve/pay `L(O*)`; candidate mechanism family `A` is one way to meet that requirement with response profile `R_A`.

Avoid:

> intelligent systems intrinsically need mechanism A.

The first is testable and scoped; the second silently universalizes the obligation.

---

# 10. From lower bound to frontier pressure

A semantic/information lower bound does not by itself prove one concrete mechanism is Pareto-optimal.

The reasoning chain must remain:

\[
\text{obligation distinction}
\Rightarrow
\text{necessary information/behavior}
\Rightarrow
\text{implementation equivalence class of mechanisms}
\Rightarrow
\text{morphology-specific response/cost}
\Rightarrow
\text{registered frontier}.
\]

For example, MN1 proves recoverability information is necessary for exact rejectable updates.

It does **not** prove:

```text
shadow copy is cheapest;
copy-on-write is best;
versioning beats recomputation at every horizon;
A4 must appear when failed candidates are impossible;
```

Those are realization/frontier questions governed by `R_M`, `P`, reuse and verifier dynamics.

This distinction is crucial for keeping theorem strength separate from engineering preference.

---

# 11. Immediate empirical theorem hostiles

Issue #419 E1-E3 should instantiate at least one exact/controlled test for each theorem boundary.

```text
MN1: vary candidate transform information loss and verify rollback storage/work lower-bound behavior;
MN2: vary serving compression that merges developmental states and measure necessary persistent side state/reacquisition;
MN3/MN4: matched nu with historical-query contract on/off;
MN5: matched Delta_U with local vs global Delta_Q;
MN6: matched present Xi/P after different developmental orders;
MN7: multiple implementation-equivalent A4/A5 encodings.
```

These tests are more informative than asking only whether a composite VLC implementation wins.

---

# 12. Claim ladder enabled by these theorems

After theorem statement alone:

```text
MECHANISM_INFORMATION_NECESSITY_SPECIFIED_AT_FINITE_EXACT_SCOPE
```

After controlled experiments validate the measurements and predicted boundaries:

```text
MECHANISM_PRESSURE_SUPPORTED_AT_CONTROLLED_SCOPE
```

After family-held-out mechanism invariance:

```text
CROSS_PARADIGM_MECHANISM_LAW_SUPPORTED_AT_SCOPE
```

Only after neutral recovery and parent reduction:

```text
THEORY_PREDICTED_DISTINCT_REALIZATION_CANDIDATE_SUPPORTED_AT_SCOPE
```

No theorem here establishes a new form of machine intelligence.

---

# 13. Parent/literature ownership

The mathematical ingredients are deliberately parent-owned.

- Semantic quotient/minimal-state logic: automata minimization, sufficient state, predictive-state/bisimulation traditions.
- Lossless recoverability/injective coding: elementary information theory/coding.
- Persistence: Driscoll, Sarnak, Sleator & Tarjan distinguish access to old versions from ephemeral update.
- Optimistic validation: Kung & Robinson provide a parent pattern for private/optimistic work plus validation without implying indefinite historical persistence.
- Distributed lineage: Parker et al. and version-vector traditions show that divergent update history/order is structurally richer than a scalar update count/rate.
- Incremental change propagation: self-adjusting computation is a direct parent for dependency-tracked local recomputation.
- Continual-learning path dependence/plasticity: modern continual-learning results make memoryless response assumptions empirically suspect.

GMI contribution here is the obligation-relative integration and the explicit separation of semantic necessity from realization economics.

---

# 14. Current terminal

```text
GMI_MECHANISM_NECESSITY_THEOREMS_SPECIFIED_V1
EMPIRICAL_MECHANISM_BOUNDARY_VALIDATION_PENDING
```
