# GMI #833 Section I — admissible update-law space and credit-assignment regimes

**Freeze:** `FREEZE_V1.md`, commit `5c5c36e4` (pre-implementation).
**Parent ownership:** `PARENT_OWNERSHIP_V1.md` — read it first. Every result
below is stated after subtracting what the parents own.
**Claim ceiling:**
`GMI_833_SECTION_I_UPDATE_LAW_SPACE_AND_CREDIT_ASSIGNMENT_REGIMES_AT_REGISTERED_FINITE_SCOPE`
**Evidence level:** EV1 (deductive, explicit premises and falsifiers) plus EV2
(exact finite certificates over declared universes). Not EV3, EV4 or EV5.
**Domain tags:** `forall[D]` marks a deductive statement over a declared
mathematical domain; `forall_fin[U]` marks complete enumeration of a finite
registered universe. No `forall_fin` result below may be rewritten as `forall`.

---

## 0. Why this section exists

The direct parent (#870) proved that under uniform completion every update law
scores identically, and that for any two predictively distinct laws there exist
ecologies preferring each. Its corollary is that a useful preference between
update laws **requires stated ecological, informational and resource
assumptions**. It did not say which assumptions buy which law.

This tranche answers exactly that, and answers it by derivation: it defines the
space those laws live in without naming any of them, then locates the exact
boundaries in the declared price and ecology parameters at which the preference
flips. The word for a mechanism is never the input; the crossing point is the
output.

---

## 1. IL-1 — the admissible update-law space

### 1.1 Registered objects

Let the registered finite scope be `S = (R, HIST, coords, Delta, ext, Bgrid)`:
`R` a finite nonempty set of realizations of the #837 contract
`(X, x0, Q, U, Chi, rho)`; `HIST` finite registered interaction histories;
`coords` a nonempty duplicate-free tuple of resource coordinate names (AX-3);
`Delta : R x HIST -> P(R)` the declared development law (AX-4); `DeltaStar` its
reflexive-transitive closure over all histories; `ext : HIST x R -> HIST` the
registered total history-extension map; `Bgrid` a finite set of budget vectors
in `Q_{>=0}^coords`.

An **update law** is a total map `L : R x HIST x Q_{>=0}^coords -> Dist(R) x Q_{>=0}^coords`,
written `L(r,h,b) = (dist, charge)`, with `Dist(R)` the exact-rational
normalized distributions on `R`. Totality off the budget grid is what makes
composition well defined at residual budgets; the grid is only where the
certificate is evaluated.

**Admissibility `Adm_k(L)`**, for grade `k in {ONE_STEP, CLOSURE}`:

- **A1 exact totality** — defined everywhere; every probability an exact
  rational; nonnegative; summing to one.
- **A2 charge well-formedness** — exactly the coordinates `coords`, all values
  exact rationals `>= 0`.
- **A3 worst-case budget clause** — either `charge <= b` coordinatewise, or
  `charge = 0` and `dist = delta_r`. On insufficient residual budget an
  admissible law is the identity at zero charge. Budget feasibility is charged
  WORST CASE over the support; expected charge is reported by IL-2/IL-3 and is
  never a budget guarantee (see `H14`).
- **A4 development closure** — `supp(dist) subset Succ_k(r,h)`, with
  `Succ_ONE_STEP(r,h) = {r} u Delta(r,h)` and `Succ_CLOSURE(r,h) = DeltaStar(r)`.

Write `A_1` and `A_star` for the two spaces; `A_1 subset A_star`.

Nothing in A1-A4 mentions an architecture, a family, an optimizer, a
representation, or an algorithm. Section 1.6 verifies that mechanically rather
than asserting it.

### 1.2 IL-1.1 — decidability with an exact operation bound

**Statement** `forall_fin[S]`. `Adm_k` is decided by a terminating finite
procedure performing at most
`|R| * |HIST| * |Bgrid| * (|R| + 2|coords| + 1)` exact rational operations per
law per grade.

**Proof.** The predicate is a finite conjunction over the `|R| * |HIST| *
|Bgrid|` presented triples. At each triple: normalization and support
membership cost at most `|R| + 1` operations; charge well-formedness and
nonnegativity cost `|coords|`; the budget comparison costs `|coords|`. Summing
gives the bound. Each atomic test compares exact rationals and terminates. QED.

**Certificate.** At the registered scope (`|R|=9`, `|HIST|=3`, `|Bgrid|=3`,
`|coords|=2`) the bound is **1134** operations per law per grade. The executor
performs **6810** operations to decide all 7 registered laws at both grades,
against an aggregate allowance of `1134 * 7 * 2 = 15876`. All 7 laws are
`ADMISSIBLE` at both grades with 0 findings.

### 1.3 IL-1.2 — closure under rational convex mixture (both grades)

**Statement** `forall[lambda in [0,1] cap Q]`. If `L1, L2 in A_k` then
`lambda L1 + (1-lambda) L2 in A_k`, with mixture charge
`lambda c1 + (1-lambda) c2`.

**Proof.** Normalization is affine, so the mixed distribution sums to one and is
nonnegative. The support of the mixture is contained in the union of the two
supports, and `Succ_k(r,h)` is a set, so containment is preserved. For the
charge: each `c_i` is either `<= b` or `= 0 <= b`, so the convex combination is
`<= b` coordinatewise; and when both stages are the zero-charge identity the
mixture is the zero-charge identity. Exactness is preserved because `Q` is a
field. QED.

**Certificate** `forall_fin`. **686** mixture cases (7 x 7 laws, the rational
grid `lambda in {0, 1/6, ..., 1}`, both grades), **0 failures**.

### 1.4 IL-1.3 — composition closure, and its exact failure at ONE_STEP

Composition `(L2 o L1)(r,h,b)`: run `L1`, take the residual budget `b - c1`,
run `L2` from each reachable realization, mix by `d1`, and charge
`c1 + max_{r1 in supp(d1)} c2^{r1}` (coordinatewise max, i.e. worst case).

**Statement (positive)** `forall[S]`. `A_star` is closed under composition.

**Proof.** Support: `supp(d) subset DeltaStar(DeltaStar(r)) = DeltaStar(r)` by
transitivity of the closure. Charge: `c1 <= b` (or `c1 = 0`), and each
`c2^{r1} <= b - c1` (or `= 0`) by A3 at the residual budget, so
`c1 + max c2 <= b`. Normalization: `sum_{r1} d1(r1) * sum_t d2^{r1}(t) = 1`. QED.

**Certificate** `forall_fin`. **49** composition cases (7 x 7), **0 failures**
at the CLOSURE grade.

**Statement (negative, EARNED-BY-COUNTEREXAMPLE)** `A_1` is NOT closed under
composition.

**Counterexample.** With `Delta(r0, h0) = {r1}` and `Delta(r1, ext(h0,r1)) = {r2}`,
both single-step laws are `ONE_STEP`-admissible, yet the composite places all
mass at `r2` from `(r0, h0)`, where `Succ_ONE_STEP(r0,h0) = {r0, r1}`. The
checker returns `INADMISSIBLE` with finding
`A4_SUPPORT_OUTSIDE_DEVELOPMENT` at `('r0','h0',(9,9))` and target `r2`, while
the same composite is `ADMISSIBLE` at the CLOSURE grade because
`DeltaStar(r0) = {r0,r1,r2,ra,rb,ru,rv,rz}`.

This is not a defect of the definition; it is the precise content of the
distinction between a one-step development law and developmental reachability
that #837 draws, made operational on update laws.

### 1.5 IL-1.4 — a two-sided monoid on kernels, with only subassociative charging

**Statement (positive, unconditional)** `forall[S]`. `(A_star, o)` has the
zero-charge no-op as a **two-sided** identity, and the distribution component
of composition is exactly associative.

The two-sided half needs one clause, and that clause is derived rather than
stipulated. Composition presents the second stage with the extended history
`ext(h, r1)`, EXCEPT after a stage that consumed no resource and changed
nothing, which does not advance the history. This is forced by AX-3: finite path
cost is coordinatewise addition, so a zero-charge step contributes nothing to
the developmental record and cannot register an interaction. Without the clause
the no-op is a left identity only — a conditional result. With it, derived from
an already-registered axiom, the monoid is unconditional.

**Certificate.** `monoid_identity_ok = true` on every registered triple;
`kernel_associativity_exact = true`; the identity law is `ADMISSIBLE`.

**Statement (negative, EARNED-BY-COUNTEREXAMPLE)** The worst-case charge is
only SUBassociative under re-bracketing:

    charge((L3 o L2) o L1) <= charge(L3 o (L2 o L1))   coordinatewise,

and strict inequality is attainable.

**Proof of the inequality.** The left bracketing takes one maximum over pairs,
`max_{r1}(c2^{r1} + max_{r2} c3^{r2})`; the right takes two independent maxima,
`max_{r1} c2^{r1} + max_{r2} c3^{r2}`. Since `max_i (x_i + y_i) <= max_i x_i +
max_i y_i`, the left is bounded by the right. QED.

**Strictness witness.** A stage splitting `r0` into `{ra, rb}` at zero charge;
a second stage charging `3` at `ra` and `0` at `rb`; a third charging `0` at the
successor of `ra` and `5` at the successor of `rb`. The left bracketing charges
`max(3+0, 0+5) = 5`; the right charges `max(3,0) + max(0,5) = 8`. Receipt:
realization `r0`, history `h1`, budget `(9,9)`, coordinate `c_alpha`,
**5 versus 8**.

Consequence, and it is the scientifically load-bearing part: **worst-case
resource accounting over a composed update law is not an associative operation.**
A budget certificate computed by nesting the later stages inward is tight; one
computed by summing independent stage maxima is merely sound. Both are
admissible at the same budget, so no claim is lost — but a package that reports
the loose number as *the* cost of a composed law is over-reporting, and this
counterexample says by how much.

### 1.6 IL-1.5 — the name-freedom certificate

Three independent screens, none of which is claimed to prove semantic
neutrality in general.

**(a) A1 lexical.** Every `NAME`, `STRING` and `COMMENT` token of every Python
source file in the package, plus every whitespace-delimited token of every
prose file, normalized by camel-case splitting, punctuation stripping and
lower-casing, checked against a denylist of **26** entries
(`BANNED_MI_PRIMITIVES`, the no-smuggling audit's registered entries, and ten
Section-I additions). The executor screens the seven `.py` and `.md` files; the
test suite screens the four `.json` files, which do not exist when the executor
runs.

The screen is **occurrence-level, not file-level**. Only two files are skipped
whole, and both hold the screened vocabulary by construction: the denylist
itself and the hostile fixtures. Every other file is screened in full,
including this theorem note and the parent-ownership file — the two documents
most able to hide a name. Where a hit is legitimate, `DENYLIST_V1.json` names
the exact `(file, denylist entry)` pair together with a reason, and the screen
fails on any hit that no allowance covers AND on any allowance that is never
exercised, so a stale allowance is itself a failure.

A stricter rule sits on top: the two route files, the test file, `CORE.md` and
both generated receipts are declared **absolutely clean**. They must have zero
hits and no allowance may name them. Prose and governance files may carry
justified occurrences; the definitions, the routes and the receipts may not.
The verdict is `CLEAN_AT_REGISTERED_AUDIT_SCOPE`: every hit declared at
occurrence level, zero unmatched, zero stale, zero violations of the absolutely-
clean rule. The exact token and hit counts and the receipt digests are recorded
in `MANIFEST_V1.json` rather than here, because this file is itself inside the
screened population and quoting its own token count would make the number
self-referential.

The screen was validated on real data before being trusted. On its first run
against this package it flagged one genuine hit — a comment in the executor
containing a denylisted term. That hit was real, the comment was repaired, and
the screen's recall is separately evidenced by **10/10** planted hostile
identifiers caught with **0/10** false alarms on structurally similar clean
identifiers (`H11`).

**(b) A2 semantic.** All **5** search-visible primitives introduced here carry
the full **11-field** signature and are checked against **4** registered target
fingerprints. Verdict `CLEAN_AT_REGISTERED_AUDIT_SCOPE`, 0 findings. A lexically
clean but semantically smuggled primitive would be caught here; A1 alone is
one-sided by its own contract.

**(c) Opaque-token remint.** All **14** scope symbols renamed injectively to
`t0, t1, ...`; all **14** verdict pairs invariant under the induced relabeling.
A remint that mutates a semantic field rather than relabeling is rejected
(`H12`: a development edge deleted under the guise of renaming flips
`ADMISSIBLE` to `INADMISSIBLE`).

**Scope boundary.** No hit is not proof of neutrality. Only the registered
finite fingerprint library is checked; undiscovered semantic priors remain
possible. This is the parent contract's own boundary and is inherited unchanged.

---

## 2. IL-2 and IL-3 — the acquisition-cost crossover

### 2.1 Registered objects

A finite **ecology** `E = (C, succ, V, acc)`: finite configurations `C`, an
ordered successor tuple `succ(s)` with `d(s) = |succ(s)|`, an exact rational
score `V : C -> Q` derived from the registered acceptance predicate, and
accepting configurations `acc`. Write `Imp(s) = {s' in succ(s) : V(s') > V(s)}`
and `m(s) = |Imp(s)|`.

Two declared channels, both objects of the contract's channel component `Chi`:

- **`pt`** returns the exact `V` value at one queried configuration; unit price
  `price_pt in Q_{>0}`.
- **`sel`** returns SOME element of `Imp(s)`, uniformly among `Imp(s)`, or the
  abstention token when `m(s) = 0`; unit price `price_sel in Q_{>0}`.

`sel` is deliberately weakened from "the best successor" to "an improving
successor". A channel returning the maximizer would hand over strictly more than
direction at no extra charge, would make the two law families follow different
paths, and would itself be the shape of atomic primitive the A2 screen exists to
reject. With the weakened channel both families induce the same path law up to
relabeling, so the ONLY difference between them is the cost of acquiring the
next improving step. That is the mechanism under study.

A **verified-selection `pt`-only law** at `s` is any law that may query `V`
through `pt` and outputs a successor only from the set it has verified
improving. Laws that output unverified successors are OUT OF SCOPE of IL-2a by
name: they trade cost against failure probability, which is a different
comparison and needs its own theorem.

### 2.2 IL-2a — the orbit-average probe count, an equality over the whole family

**Statement (UNCONDITIONAL)** `forall[d >= 1, 1 <= m <= d]`. Averaged over the
`Sym(d)` orbit of the successor labeling — equivalently over the `C(d,m)`
equally-weighted placements of `Imp(s)` — EVERY verified-selection `pt`-only law
at `s`, with any probe-order rule, adaptive or not, has expected probe count
exactly

    rho_local(d,m) = (d+1)/(m+1),

and worst-case probe count exactly `d - m + 1`. A `sel` law needs exactly one
query.

**Proof.** Three steps.

*(i) Repeats are strictly wasteful.* The channel is deterministic in the value
it returns, so a second query at an already-queried successor returns a known
value and cannot change the law's information state while still being charged.
Any law with a repeat is strictly dominated by the law that deletes it.

*(ii) No order rule changes the expectation.* A returned value can of course
differ between two non-improving successors, so adaptivity is not vacuous in
general. What makes it worthless HERE is the orbit measure: conditional on the
queried prefix being entirely non-improving, the unqueried positions are
**exchangeable** under the uniform measure on the `C(d,m)` placements. Any rule
for choosing the next index — fixed, randomized, or adapting on the values
already seen — therefore faces the same conditional probability of success at
its next probe, so `E[T]` is identical for every rule. (Route B checks this
computationally rather than taking it on trust: it evaluates the placement
average separately for each of the `d!` fixed orders and finds all of them
equal, for every one of the 21 registered `(d,m)` pairs.)

*(iii) The expected first-marked position.* Fix any permutation. Under the orbit
average the marked set is uniform over the `C(d,m)` placements, so

    E[T] = sum_{t>=1} P(T >= t) = sum_{t=1}^{d-m+1} C(d-t+1, m)/C(d,m)
         = C(d+1, m+1)/C(d,m) = (d+1)/(m+1),

using the hockey-stick identity `sum_{j=m}^{d} C(j,m) = C(d+1,m+1)`. The worst
case places all `d-m` non-improving successors first. QED.

Because the value does not depend on the law, this is an **equality over the
family**, not a bound on one representative. That is what upgrades IL-2 and IL-3
from a comparison of two chosen laws to a dominance statement.

**Certificate (two routes, `forall_fin`).** All **21** pairs `(d,m)` with
`1 <= m <= d <= 6`. Route A evaluates the closed form. Route B never uses it: it
enumerates every placement and every one of the `d!` probe orders and averages
with exact `Fraction` arithmetic. The tables agree on **21/21** for the expected
count and **21/21** for the worst case. Route B additionally confirms that the
per-order averages are all equal within each `(d,m)` — the computational face of
step (ii) — and exhibits, for `(3,1)`, `(4,2)` and `(5,1)`, that inserting one
repeat strictly raises the expected count, the computational face of step (i).

### 2.3 IL-2 and IL-3 — the crossover

For a registered improving path `P = (s_0, ..., s_n)` with `s_n in acc` and
`s_{i+1} in Imp(s_i)`:

    Cost_pt(P)  = price_pt  * sum_{i<n} (d(s_i)+1)/(m(s_i)+1)
    Cost_sel(P) = price_sel * n
    rho_star(P) = (1/n) * sum_{i<n} (d(s_i)+1)/(m(s_i)+1)

and with `ratio = price_sel / price_pt`:

| condition | verdict |
|---|---|
| `ratio > rho_star(P)` | **IL-2**: the evaluative-only law strictly dominates |
| `ratio < rho_star(P)` | **IL-3**: the directional law strictly dominates |
| `ratio = rho_star(P)` | exact tie, the boundary |

**Proof.** Immediate from IL-2a summed along the path, since both sides are
exact rationals and `price_pt > 0`. QED.

**Every directional law, not just the endpoint.** The comparison above is
between the two pure families, but the row asks about every law that requires
directional information. That is discharged by IL-1.2: the admissible space is
closed under rational convex mixture and the mixture charge is the convex
combination of the stage charges. Any law that buys direction at some steps and
probes at others is exactly such a mixture, so its cost lies in the closed
interval between `Cost_pt(P)` and `Cost_sel(P)` and is a monotone function of
the mixing weight. Above `rho_star` the evaluative endpoint is the strict
minimum of that interval, so no mixture — hence no law that uses the directional
channel at all — can match it; below `rho_star` the same argument runs the other
way. The two theorems are therefore statements about the whole family, not about
two representatives.

`rho_star(P)` is the **mean reciprocal improving density along the path**: the
exact number of point-value probes that one directional query saves. This is the
mechanism the section asks for, and it is derived, not posited: the cost of
acquiring direction from the evaluative channel is `(d+1)/(m+1)` probes by
IL-2a, and the value of direction is precisely the probes it removes.

### 2.4 IL-3b — where direction is informationally worthless, unconditionally

**Statement** `forall[d >= 1]`. If `m(s_i) = d(s_i)` at every step, then
`rho_star(P) = 1` exactly, so the directional channel is preferred only if its
raw price is strictly lower. It carries zero informational value.

Conversely `rho_star` grows without bound as improvement becomes sparse:
`m = 1` gives `rho_star = (d+1)/2`, unbounded in `d`.

**Certificate.** **19** of the 75 registered paths have `rho_star = 1` exactly,
and all of them are exactly the full-improving-density paths. The registered
maximum is `rho_star = 7/2` at `uniform_d6_m1_n1`. Verified for `d = 1..6` that
`rho_star((d,d)^3) = 1` and that `rho_star((6,1)) = 7/2`, `rho_star((2,1)) = 3/2`.

### 2.5 IL-23 — the exact trichotomy, no gap and no overlap

**Statement** `forall[registered (E,P,price_pt,price_sel) with prices in Q_{>0}]`.
Exactly one of the three verdicts holds.

**Proof.** `Cost_pt` and `Cost_sel` are exact rationals; trichotomy of the
rational order is exhaustive and exclusive. QED.

**Certificate (two routes, `forall_fin`).** **75** registered paths (63 uniform
ladders over `d in {1..6}`, `1 <= m <= d`, `n in {1,2,3}`, plus 12 mixed ladders
whose `(d_i, m_i)` vary so that `rho_star` is a genuine mean and not a constant)
crossed with the pre-committed price-ratio grid of **46** reduced fractions
`a/b`, `1 <= a <= 12`, `1 <= b <= 6`: **3450 cases**.

- Route A and Route B agree on **3450/3450** verdicts and on all 75 `rho_star`
  values. Route B derives every verdict from its enumerated probe table and
  never from the closed form.
- Verdict split: **2047** evaluative-only, **1331** directional, **72** exact
  ties.
- **0 partition failures**: in every one of the 3450 cases exactly one of
  `<`, `>`, `=` held.
- The anchored probe, at `rho_star/2`, `rho_star` and `2*rho_star` for every
  path, produced all three verdicts on all 75 paths.

### 2.6 The per-instance boundary — EARNED-BY-COUNTEREXAMPLE

IL-2a is stated over the relabeling orbit and is unconditional there. The
per-instance corollary is not, and the counterexample that maps the boundary is
delivered rather than gestured at.

**Counterexample.** At `d = 6, m = 1`, the orbit value is `rho_local = 7/2`. A
law that pins the probe order to successor index 0 pays exactly **1** probe on
the single instance where index 0 is the improving successor, strictly beating
`7/2`.

**Why this does not weaken IL-2a.** Averaged over `Sym(6)`, that same pinned law
returns to **7/2** exactly — recomputed by explicit enumeration over all `C(6,1)`
placements. The advantage is not information; it is a bet on a labeling. By the
direct parent NFL-I3 (#870), a law preferred on one point-mass ecology is
dispreferred on the constructed reversal, and by PF-2 (#837) a deterministic
unique choice under complete renaming symmetry is impossible without breaking
the symmetry through a representation, order or tie rule. Dropping equivariance
therefore re-imports exactly the ecological prior the parent proved cannot be
free. The boundary is real, it is mapped, and the adjacent scoped positive — the
orbit equality — is the stronger statement.

---

## 3. IL-4 — credit assignment from graph and resource structure

`PARENT_OWNERSHIP_V1.md` must be read before this section. The cheap-gradient
principle, the adjoint recursion, the elimination view and the NP-completeness
of optimal accumulation are all parent-owned. Nothing here claims them. The name
of the connectionist algorithm appears nowhere in this section, in no identifier,
in no search space and in no objective.

### 3.1 Registered objects

A finite **computation graph** `G` with `n` source nodes, `N` internal nodes
listed in a topological order, `E` edges each carrying an exact rational local
partial, and `p` designated output nodes that are sinks. The Jacobian
`J in Q^{p x n}` is the path sum (Bauer; Baur-Strassen).

Declared cost model, all exact rationals:

- `sweep_price` — one elementary multiply-accumulate on one edge during one
  linearization sweep. One sweep in either direction costs exactly `E` of them.
- `retention_price` — retaining one intermediate slot.
- `w` — the peak number of live INTERNAL values under the registered
  topological evaluation order, a value being live from its production step to
  its last consumption step inclusive, with designated outputs live to the end.
  `w` is computed exactly by both routes and reported in the receipt, so
  `sigma*` is reproducible and does not rest on an uncomputed invariant. Source
  values are retained identically by both directions and are therefore excluded
  from both sides of the comparison.
- The adjoint direction retains all `N` internal values, so its incremental
  retention over the primal working set is `N - w >= 0`. The tangent direction
  interleaves with the primal and charges incremental retention `0`.

### 3.2 IL-4a — sweep counts: sufficiency AND necessity

**Statement** `forall[G]`. One tangent sweep seeded by `v in Q^n` yields `Jv`;
one adjoint sweep seeded by `u in Q^p` yields `u^T J`; each costs exactly `E`
multiply-accumulates. `n` tangent sweeps suffice and `p` adjoint sweeps suffice.
**Fewer than `n` tangent sweeps do not determine `J`, and fewer than `p` adjoint
sweeps do not determine `J`.**

**Proof of sufficiency.** Seeding with the standard bases gives the columns,
respectively the rows, of `J`. The cost is `E` because each sweep performs one
multiply-accumulate per edge.

**Proof of necessity (constructive).** Take the star graph with `n` sources each
joined to a single output by one edge with partial `a_i`, so `J = (a_1,...,a_n)`.
A tangent sweep seeded by `v` reveals only `sum_i a_i v_i`, one linear
constraint. After `k < n` sweeps the consistent assignments form an affine set
of dimension at least `n - k >= 1`, so there are two DISTINCT graphs of the same
shape agreeing on every observed sweep and differing in `J`. Symmetrically for
the adjoint direction on the graph with one source and `p` outputs. QED.

Hence at `p = 1` the adjoint direction uses exactly **1** sweep where the
tangent direction uses exactly **n**: an exact sweep-count ratio of `n`, and `n`
is not merely sufficient but necessary.

**Certificate.** Necessity established at `n = 2,3,4,5,6` (all observed sweeps
agree, Jacobians differ) and at `p = 2,3,4`. Across the registered family, e.g.
`deep_chain_n6` needs **6** tangent sweeps against **1** adjoint sweep at
`E = 11`; `fan_out_p4` needs **1** against **4** at `E = 6`.

### 3.3 IL-4b — the exact retention-price threshold

    C_tangent = n * E * sweep_price
    C_adjoint = p * E * sweep_price + (N - w) * retention_price
    sigma     = retention_price / sweep_price

**Statement** `forall[G with n > p and N > w]`.

    sigma_star = (n - p) * E / (N - w)

is an exact rational in graph invariants, and

    sigma <  sigma_star  <=>  the adjoint direction is strictly cheaper
    sigma >  sigma_star  <=>  the tangent direction is strictly cheaper
    sigma == sigma_star  <=>  exact tie.

**Proof.** The adjoint is cheaper exactly when
`(n-p) E sweep_price > (N-w) retention_price`; divide by
`sweep_price (N-w) > 0`. QED.

`sigma_star` IS the retention-versus-recomputation boundary: the retention price,
measured in sweep operations, at which keeping the whole record stops paying and
recomputation becomes the cheaper policy. Beyond it the adjoint direction loses
even though it uses strictly fewer sweeps.

**Certificate.** `source_chain_n4`: `sigma_star = 21/2`. `deep_chain_n6`:
`sigma_star = 55/4`. `fan_in_n5`: `sigma_star = 32`. For each, the executor
returns `ADJOINT_STRICTLY_CHEAPER` at `sigma_star/2`, `EXACT_TIE_AT_BOUNDARY` at
`sigma_star` and `TANGENT_STRICTLY_CHEAPER` at `2 sigma_star`. Both routes agree
on `w`, on the regime tag and on `sigma_star` for all 7 registered graphs.

### 3.4 IL-4c — the converse regime, unconditional

**Statement** `forall[G]`.

- If `p > n`, then `(n-p) < 0 <= (N-w) sigma` for every `sigma >= 0`, so the
  tangent direction is strictly cheaper at EVERY price. No retention price
  rescues the adjoint direction.
- If `p = n` and `N > w`, the tangent direction is strictly cheaper for every
  `sigma > 0` and ties at `sigma = 0`.
- If `N = w`, there is nothing extra to retain and the adjoint direction is
  cheaper whenever `n > p`, at every price.

**Certificate.** `fan_out_p4` (`n=1, p=4`) returns `TANGENT_STRICTLY_CHEAPER` at
`sigma = 0`, `1` and `10^6`. `square_n3_p3` and `bridge_n3_p3` (`n = p = 3`)
return `TANGENT_WINS_FOR_EVERY_POSITIVE_PRICE`.

Taken with IL-4b this is the precise sense in which the adjoint advantage is
**conditional on the regime**: few outputs, many inputs, and storable
intermediates. Remove any one of the three and it goes away, exactly and
computably.

### 3.5 IL-4d — cheap-sensitivity consistency, PARENT MATHEMATICS

With `p = 1`, maximum in-degree `a` (so `E <= aN`), and primal price
`eval_price` per node,

    C_adjoint / C_primal <= (a * sweep_price + retention_price) / eval_price,

a constant INDEPENDENT of `n`.

**This is the cheap-gradient principle and it belongs to Griewank and Walther
(2008), standing on Linnainmaa (1970, 1976) and Speelpenning (1980).** It is
re-derived here only to check that the declared cost model does not contradict
the parent bound; had it contradicted it, the model would have been wrong. It is
not a residual contribution and no novelty is claimed for it.

**Certificate.** At unit prices: `source_chain_n4` ratio `9/4` against bound `5`;
`deep_chain_n6` ratio `5/2` against bound `7`; `fan_in_n5` ratio `9/4` against
bound `4`. All within the parent bound, all independent of `n`.

### 3.6 IL-4e — the order is RECOVERED, not inserted

This is where the section's actual demand is met. The search space contains no
algorithm name; the objective contains no algorithm name; the winner is whatever
exhaustive search returns.

**The neutral space.** Every order in which the interior non-output vertices of
the linearized graph may be eliminated. Eliminating `v` costs
`indeg(v) * outdeg(v)` multiply-accumulates and installs the complete bipartite
fill-in between its predecessors and successors (parent: Griewank and Walther,
Ch. 9). Under the parent identification, the topological elimination order is
the tangent direction and the reverse-topological order is the adjoint
direction — but neither is privileged in the search, and nothing in the
enumeration or the cost function knows which order is which.

**Pre-committed reporting rule** (freeze section 3.3): report the argmin
whatever it is, per registered graph family, with exact costs, and no post-hoc
redefinition of the space, the cost model or the family.

**What the census found** (`forall_fin`, both routes agreeing on every field):

| graph | n | p | orders | topological | reverse-topological | minimum | argmin |
|---|---|---|---|---|---|---|---|
| `source_chain_n4` | 4 | 1 | 6 | 12 | **6** | 6 | reverse-topological |
| `deep_chain_n6` | 6 | 1 | 120 | 30 | **10** | 10 | reverse-topological |
| `fan_in_n5` | 5 | 1 | 6 | 10 | **7** | 7 | reverse-topological |
| `square_n3_p3` | 3 | 3 | 6 | 13 | **12** | 12 | reverse-topological |
| `bridge_n3_p3` | 3 | 3 | 2 | 12 | 12 | 12 | both, tied |
| `fan_out_p4` | 1 | 4 | 2 | **5** | 7 | 5 | topological |
| `skip_waist_n2_p2` | 2 | 2 | 6 | 10 | 10 | **7** | MIXED ONLY |

Every order in every graph reproduces the same Jacobian, cross-checked against
the Route B path sum.

**The result.** In every registered graph with one output and many inputs the
argmin IS the reverse-topological elimination order, and in the graph with one
input and many outputs the argmin flips to the topological order. **The
direction of accumulation is recovered from the output-to-input ratio and the
graph structure by exhaustive search over an unnamed space.** Nothing was
inserted: no name entered the space, the objective, or the tie rule.

**The earned boundary (pre-committed, and it landed).** On `skip_waist_n2_p2`,
a graph with a skip edge across a narrow waist, a MIXED order strictly beats
both pure orders: **7 against 10 and 10**, with the argmin
`(v1, v0, v2)` — neither topological nor reverse-topological. The general
problem is NP-complete (Naumann 2008), so this is the expected regime and not a
surprise; the freeze pre-committed to reporting it. Its consequence is stated
plainly: **the reverse order is optimal in the registered few-outputs regime, and
is NOT optimal in general.** That is a sharper and more defensible claim than
the one a friendlier census would have licensed, and it is the reason the
registered family deliberately includes a graph where the pure orders lose.

---

## 4. Two routes, hostiles, nulls

**Two routes.** Route A is the executor; Route B is an independently written
oracle that imports nothing from Route A and shares no helper module with it
(rational helpers are duplicated inline). Route B recomputes IL-1 by literal
tuple enumeration and fixed-point closure, IL-2/IL-3 by exhaustive enumeration
over every placement and every probe order, and IL-4 Jacobians by explicit
directed-path enumeration with sweep and elimination costs by literal
simulation.

The registered objects are transcribed independently in both files, and the
transcriptions are cross-checked before any agreement figure is reported: a
scope fingerprint built from each route's own declaration must match, and so
must the graph set, every graph, the path set and the price grid. A drift there
would make every agreement number meaningless, so it is checked rather than
assumed.

Agreement: the IL-1 closure census (**686** mixtures and **49** compositions,
zero failures, the `A4` one-step clause, and the two-sided monoid) is
recomputed by the oracle from explicit grid tables and an independently written
admissibility predicate; **3450/3450** IL-2/IL-3 verdicts; **21/21**
probe-count entries; and every IL-4 field on all 7 graphs.

**Hostiles, all DETECTED** (`H1`-`H14`): non-normalized distribution; float
probability; float price refused; support escaping the development closure;
negative charge; undeclared charge coordinate; the `A_1`-composition-closure
claim refuted; the off-by-one threshold `d/m` separated from `(d+1)/(m+1)` on
the registered paths; a gapped trichotomy that silently absorbs ties; the
adjoint-wins-at-`p>n` claim refuted at three prices; sweep-count necessity
dropped; 10/10 planted smuggled identifiers caught with 0/10 false alarms; a
remint that mutates a semantic field rather than relabeling; the budget clause
dropped; and expected charge substituted for the worst-case budget guarantee
(expected `3/2 <= 2` while a realizable branch costs `3 > 2`).

**Nulls.**
- **200/200** shuffled thresholds drawn from a different registered path fail to
  locate the exact tie of the target path: **0/200 hits**. The true threshold
  locates the tie on **75/75** paths.
- **200** randomized interior elimination orders on the chain and fan-in
  families: **0/200** strictly beat the reverse-topological order.
- That null is shown NOT to be vacuous: on `skip_waist_n2_p2` a mixed order does
  strictly beat it, so the control is capable of firing and does not simply
  lack power.

**Determinism.** `RESULT_V1.json` is byte-identical under `python3 -I -B` and
`python3 -I -O -B`; the digest is recorded in `MANIFEST_V1.json`. No claim is
gated by a bare `assert`, which `-O` would erase. Total checks in the suite:
**236**, all green.

---

## 5. Scope, quantifiers, assumptions, falsifiers, forbidden extrapolations

**Scope.** Finite registered universes throughout. `forall[D]` results are
deductive over their declared domain; `forall_fin[U]` results are complete
enumerations of the registered universe and may not be rewritten as unrestricted
universals. Evidence EV1 and EV2; maturity M1-M2. Nothing here is held out,
replicated, or validated at real scale.

**Assumptions carried.** Exact rational prices and probabilities; the declared
channel semantics; the declared cost model with its explicit storage schedule;
the successor-relabeling orbit for IL-2a; the registered ecology, path, price
and graph families. IL-2a excludes laws that output unverified successors, by
name. IL-4 charges a unit-cost elementary-operation model in which scalar bit
lengths, precision and graph storage are not further resolved — the same caveat
the in-corpus prior art O4 already records.

**Falsifiers.**
- A verified-selection `pt`-only law whose orbit-average probe count differs
  from `(d+1)/(m+1)`, or whose worst case differs from `d-m+1`.
- A registered case where more than one or fewer than one of the three IL-23
  verdicts holds.
- An admissible pair in `A_star` whose composite or mixture is inadmissible.
- A registered graph where `k < n` tangent sweeps do determine `J`.
- A registered graph where the adjoint direction is cheaper at `p > n`.
- A registered graph where `sigma_star` computed from the receipt's `n, p, E, N,
  w` disagrees with the executor's verdict trichotomy.
- A denylist hit in a non-exempt file, or a verdict that moves under an opaque-
  token remint.
- Route A and Route B disagreeing on any registered case.

**Strongest parents.** See `PARENT_OWNERSHIP_V1.md`. In one line: Linnainmaa,
Speelpenning and Griewank-Walther own reverse accumulation and the cheap-gradient
principle; Naumann owns the NP-completeness; Bauer and Baur-Strassen own the
path sum; Rumelhart-Hinton-Williams own the named algorithm; Wolpert-Macready
and Mitchell own why selection needs assumptions; #837 owns the realization
contract; #870 owns the no-free-lunch boundary this section answers; O4 and
LLS-3 are the closest in-corpus prior art and are disclosed, not cited as
authority.

**Forbidden extrapolations (binding).** `UNIVERSAL_BEST_UPDATE_LAW`,
`ALL_UPDATE_LAWS_ENUMERATED`, `ARCHITECTURE_PRIOR_FREE_IN_ABSOLUTE_SENSE`,
`NEUTRALITY_PROVEN_SEMANTICALLY_COMPLETE`, `CHEAP_GRADIENT_PRINCIPLE_IS_NOVEL_HERE`,
`OPTIMAL_JACOBIAN_ACCUMULATION_SOLVED`, `REVERSE_ORDER_GLOBALLY_OPTIMAL`,
`NAMED_ALGORITHM_DERIVED_AS_NECESSARY`, `CONTINUOUS_OR_INFINITE_SCOPE`,
`REAL_SYSTEM_VALIDATION`, `P3_RECOVERY_COMPLETE`, `SECTION_I_COMPLETE`,
`COMPLETE_GMI`, `ONTOLOGICAL_COMPLETENESS`.

In particular this tranche closes four of the eleven Section I rows. The rows on
Bayesian update behavior, memory-based update, rule induction, program learning,
population search, meta-learning and self-modification remain open and are not
touched.
