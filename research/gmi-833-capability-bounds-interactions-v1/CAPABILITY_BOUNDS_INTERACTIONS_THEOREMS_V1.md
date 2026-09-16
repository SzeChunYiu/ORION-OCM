# Capability lower bounds, synergy, and shared-budget interference — v1

**Issue:** #906, child of #833 Section K  
**Freeze:** `FREEZE_V1.md` at commit `964a77c3accbf51b64a4b2af355dec751dfeec92`  
**Claim ceiling:** `GMI_833_FINITE_CAPABILITY_BOUNDS_SYNERGY_AND_INTERFERENCE_AT_REGISTERED_SCOPE`

## 1. Scope and correction

Fix one architecture-name-free capability contract `c=(T,mu,u,V,b,tau)` in
the sense of #848, and let `s_c(M)` be its exact protected score for a feasible
realization `M`. All theorem domains below are finite, all numeric inputs are
integers or rational numbers, and budgets are registered before evaluation.

This tranche rejects a historical overclaim in
`gmi-capability-interactions-unified-v1`: equality or overlap of broad resource
channel labels does not determine the sign of an interaction. The same label
can describe reuse, additive execution, or contention. An interaction claim
therefore requires a registered joint design or a load-bearing mechanism.

## 2. BOUND-1 — two different meanings of capability lower bound

Let `F` be the finite feasible class for `c`. When `F` is nonempty, define

`L_c(F) = min_{M in F} s_c(M)` and `U_c(F) = max_{M in F} s_c(M)`.

`L_c(F)` is the **uniform class floor**: every member scores at least this much.
`U_c(F)` is the finite capability ceiling from #848. For any constructed
witness `M0 in F`, its attained score supplies a **constructive lower
certificate on the ceiling**,

`s_c(M0) <= U_c(F)`.

These meanings must not be conflated. Unless `s_c(M0) <= L_c(F)`, the witness
score is not a lower bound on every class member. In particular, a high-scoring
witness can certify a high ceiling while saying nothing positive about the
worst member.

### Theorem BOUND-1A — attainment and sandwich

For nonempty finite `F`, both extrema are attained and

`L_c(F) <= s_c(M) <= U_c(F)` for every `M in F`.

**Proof.** A nonempty finite subset of the rationals has a minimum and maximum.
Their definitions give both inequalities for every member. `□`

### Theorem BOUND-1B — class-inclusion antitonicity/monotonicity

If nonempty `A subseteq B` and the same score functional is retained, then

`L_c(B) <= L_c(A)` and `U_c(A) <= U_c(B)`.

**Proof.** Every value minimized or maximized over `A` is also present in `B`.
Adding candidates cannot increase a minimum or decrease a maximum. `□`

The directions are opposite. Treating both bounds as nondecreasing is a
falsifier. If `F` is empty, neither extremum exists; the executable contract
returns `NO_FEASIBLE_REALIZATION` with no numeric floor or ceiling.

## 3. INT-1 — registered interaction and strict joint-threshold synergy

Freeze one contract, ecology, resource budget, and score functional. Register
two binary interventions `A` and `B`, producing exact scores

`s00, s10, s01, s11`.

The mixed finite difference is

`Delta_AB = s11 - s10 - s01 + s00`.

At this registered design, `Delta_AB>0` is positive synergy, `Delta_AB=0` is
additive at the design, and `Delta_AB<0` is negative interaction. This is an
interaction contrast, not by itself a causal explanation or a universal fact
about named capabilities. If contract, ecology, budget, or score functional
changes between cells, the checker refuses the comparison.

### Theorem INT-1A — product-threshold iff

In the finite microscope, factors provide distinction capacities
`a0<=a1` and `b0<=b1`, all positive integers. Joint usable capacity is their
product and the binary capability score is

`u(a,b)=1[a*b >= N]`, with `N>0`.

Then strict positive synergy occurs if and only if

`a0*b0 < N`, `a1*b0 < N`, `a0*b1 < N`, and `a1*b1 >= N`.

**Proof.** Monotonicity of the product and threshold makes the four Boolean
scores coordinatewise monotone. If the displayed inequalities hold, the table
is `(0,0,0,1)` and `Delta_AB=1`. Conversely, among monotone Boolean four-cell
tables, a positive mixed difference is possible only for `(0,0,0,1)`: if the
baseline is one all cells are one; if exactly one single-upgrade cell is one its
joint cell is also one and the difference is zero; if both single-upgrade cells
are one the difference is nonpositive. Translating `(0,0,0,1)` through the
threshold definition gives exactly the four inequalities. `□`

Witness: `(a0,a1,b0,b1,N)=(1,2,1,2,4)` gives products `(1,2,2,4)` and
scores `(0,0,0,1)`. Lowering `N` to `2` is a matched single-upgrade twin:
single upgrades already succeed, so positive joint-only synergy disappears.
The additive table `(0,1,1,2)` is a separate zero-interaction control.

### Why overlap is insufficient

Hold the coarse resource-channel signature fixed at `{compute}`. The three
registered score tables `(0,0,0,1)`, `(0,1,1,2)`, and `(0,1,1,1)` have,
respectively, positive, zero, and negative mixed differences. Therefore the
channel signature alone does not identify the interaction sign. A reuse or
contention law must supply additional operational premises.

## 4. BUDGET-1 — exact shared-budget interference law

Let a target capability require `Q>0` units from a hard shared resource budget
`R>=0`. A second mandatory component consumes charge `M>=0` from that same
budget and contributes no benefit under the unchanged target score. The target
has `R` alone and `max(0,R-M)` after the component is imposed.

### Theorem BUDGET-1A — interference iff

The component changes the target from capable to incapable if and only if

`R >= Q` and `R-M < Q`.

**Proof.** Before addition, capability is exactly `R>=Q`. Afterwards it fails
exactly when `max(0,R-M)<Q`. Since `Q>0`, that inequality is equivalent to
`R-M<Q`, including the case `M>R`. Conjoining before-success and after-failure
gives the result. `□`

Witness: `(R,Q,M)=(2,2,1)` succeeds before and fails after. The matched
budget-restoration twin `(3,2,1)` retains two units and removes interference.

### Theorem BUDGET-1B — free-option monotonicity

Let `F_old` be the old feasible configurations. If adding a component creates
`F_new` while preserving every old configuration with the same objective value,
so `F_old subseteq F_new`, then

`max_{x in F_new} s_c(x) >= max_{x in F_old} s_c(x)`.

**Proof.** The maximization on the left ranges over a superset containing every
old value. `□`

Thus an optional component cannot harm the optimum merely by existing.
Interference needs a load-bearing coupling such as mandatory maintenance from a
hard shared budget, destructive parameter sharing, a changed constraint, or a
changed objective. The executable control rejects objective drift disguised as
free-option inclusion.

## 5. Exact replay and falsifiers

The implementation exhaustively checks:

- 340 nonempty finite score classes;
- 3,840 score-preserving class inclusions;
- all 81 four-cell tables with scores in `{0,1,2}`;
- 1,377 monotone product-threshold configurations;
- 1,210 shared-budget configurations; and
- 27 free-option extensions.

Matched hostiles reject empty-class numerics, witness/floor conflation, context
drift across cells, float or Boolean numerics, decreasing “upgrades”, negative
budget quantities, objective drift, parent mutation, and overlap-only inference.

## 6. Parent subtraction and claim boundary

Min/max order, mixed finite differences/factorial interaction contrasts,
threshold complementarity, and monotonicity of optimization over a superset are
standard parent mathematics. The contribution here is their exact integration
with the #833 external capability and resource contracts, plus the explicit
correction of the overlap-only overclaim.

Allowed:

`GMI_833_FINITE_CAPABILITY_BOUNDS_SYNERGY_AND_INTERFERENCE_AT_REGISTERED_SCOPE`

Not established:

- that all historical capability definitions or eleven ceilings pass audit;
- that overlap implies any interaction sign;
- that these microscopes classify all capability interactions;
- any learned-system or real-system effect;
- a universal scalar resource law or complete GMI theory.

