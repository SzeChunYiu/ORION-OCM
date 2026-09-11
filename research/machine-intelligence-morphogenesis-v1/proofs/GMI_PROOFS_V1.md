# GMI proofs v1 — P1 rows of `THEOREM_REGISTRY_V3.json`

Status: `DRAFT_FOR_HOSTILE_REVIEW`. Objects from `DEFINITIONS_V2_EXACT.md` (cited D2-§n).
Discipline (HST): a P1 row is a deductive consequence of the frozen definitions; it says nothing
about real systems; every row names the assumption whose removal breaks it and the finite
witness a checker must produce. No row here is "PROVED" because a script passed.

Notation. `⪯_K` affine per-coordinate bound (D2-§0). `Φ_E(x) = (Q,R,D,S)` (D2-§3.2).
`≈_{𝓔,ε,K}` phenotype equivalence (D2-§4.3). `≡_K` basis equivalence (D2-§4.5).
`K_sim(B)` self-simulation band (D2-§5.2). `𝓜_k`, `M*(E)` (D2-§4.6–4.7).

---

## §T0 — Resolution collapse (GMI-T0, P1)

**Statement.** Let `B` be any basis with finite `K_sim(B)` and let `K ⪰ K_sim(B)∘K_sim(B)`. For
every finite ecology family `𝓔`, the relation `≈_{𝓔,0,K}` on `Gen(B)` coincides with table
equality `{(x,y) : Q_E(x)=Q_E(y) ∧ D_E(x)=D_E(y) ∀E∈𝓔}`. Consequently every signature class
`𝓜_k(𝓔,0,K)` that is non-empty equals the set of all composites table-equal to some member of
it, all non-empty classes with a common table coincide, and `M*(E)` does not depend on the
signature partition.

**Proof.** (⊆) `≈` implies table equality by clauses 1–2 of D2-§4.3. (⊇) Let `x, y` be
table-equal. By D2-§5.1–5.2 there are compilers `x ↦ u_x ∈ Gen(U)` and `u ↦ Gen(B)` with
overhead `⪯_{K_sim}` each way, and likewise for `y`. Since `x` and `y` have equal `Q` and `D`
tables, the composite `y ↦ u_y ↦ (re-target to x's interface) ` is a compiler `y ↦ x'` with
`Φ(x') = Φ(x)` and `R(x') ⪯_{K_sim∘K_sim} R(y)`; symmetrically `x ↦ y'`. Hence clause 3 holds at
`K ⪰ K_sim∘K_sim`, so `x ≈ y`. For the consequence: class membership (D2-§4.6) then depends only
on tables; two classes containing table-equal members are identical; the Pareto step in
D2-§4.7 selects among table-equal composites by `R`, which is now bounded within the band for
every member, so the class set on the frontier is the single class of all frontier composites. ∎

**Assumption whose removal breaks it.** `K ⪰ K_sim∘K_sim`. At `K ≺ K_sim` the third clause is
not vacuous and classes can separate (that is the entire content regime, D2-Cor 5.4).

**Finite witness required (P2, D2/D3 microscopes).** For one registered scope: a pair `x, y`
table-equal with minimal mutual overhead outside a chosen `K ≺ K_sim` and inside `K_sim∘K_sim`
(shows the collapse is real and the sub-band regime is non-empty).

**Parent.** Invariance thesis (van Emde Boas 1990; P9A ledger) supplies finiteness of `K_sim`
for reasonable bases. The proposition itself is definitional.

---

## §T2 — Relation type of `≈` and `≡` (GMI-T2, P1)

**Statement.** (a) `≈_{𝓔,ε,K}` and `≡_K` are reflexive and symmetric for every `K`.
(b) If `x ≈_{𝓔,ε,K} y` and `y ≈_{𝓔,ε',K'} z` then `x ≈_{𝓔,ε+ε',K∘K'} z`.
(c) Hence `≈` (resp. `≡`) is an equivalence relation on `Gen(B)` (resp. on bases) whenever the
bound class is closed under `∘` and the tolerance class under `+` (e.g. `K = poly`, `ε = 0`), and
is a tolerance relation (reflexive, symmetric, not necessarily transitive) at a fixed affine
constant `K` or fixed `ε > 0`.

**Proof.** (a) Identity compiler has overhead `(1,0) ⪯ K` for any admissible `K` with
`α ≥ 1, β ≥ 0`; symmetry is built into D2-§4.3/4.5. (b) Tables: `d(Q(x),Q(z)) ≤ d(Q(x),Q(y)) +
d(Q(y),Q(z)) ≤ ε+ε'` by the triangle inequality of the registered metric (exact equality
composes trivially at `ε=0`); compilers: compose `x↦y'` with `y'↦z''`; affine bounds compose:
`R(z'') ≤ α'(αR(x)+β)+β' = (α'α)R(x) + (α'β+β')`, i.e. `⪯_{K∘K'}`. (c) immediate from (b). ∎

**Consequence for V1 registry GMI-T3 ("non-transitivity attack").** Non-transitivity at fixed
constant `K` is real and expected; the cure is not to force an equivalence but to state the
class (`K∘K`) at which transitivity is recovered, and to report class membership at both `K` and
`K∘K` (D2-§4.6).

---

## §T3 — Basis-change band lemma (GMI-T3, P1)

**Statement.** Let `B_1 ≡_K B_2` (D2-§4.5) and let `c : Gen(B_1) → Gen(B_2)` be the induced
compiler (primitive-wise substitution; overhead composes along `C`, so `R(c(x)) ⪯_{K_C} R(x)` with
`K_C` the affine bound obtained by pushing `K` through the cost algebra of the combinators —
for the V2 combinators with additive cost, `K_C = K`). Then for every `𝓔, ε` and every
signature `k`:
```text
x ∈ 𝓜_k^{B_1}(𝓔,ε,K')   ⟹   c(x) ∈ 𝓜_k^{B_2}(𝓔,ε,K∘K'∘K)
```
and the frontier sets satisfy: `k ∈ M*_{B_1}(E)` implies that some member of `𝓜_k^{B_2}` lies
within the `K_C`-band of the `B_2` frontier at the same capability threshold.

**Proof.** Membership: `x ≈ y` with `Sig_k(y)` in `B_1`; `c(x) ≈ c(y)` in `B_2` with overhead
`K∘K'∘K` (compose the three compilers: back to `B_1`, the `B_1` equivalence, forward to `B_2`);
`Sig_k` is a property of `⟦·⟧` and the feedback protocol, and `c` preserves `Q`, `D` tables and
the five observables of D2-§3.1 up to the registered canonicalization (each observable is
defined from tables and from counts of changed occurrences; primitive-wise substitution
multiplies occurrence counts by at most the `desc` factor of `K`, which moves
`update_locality` by at most a constant factor and therefore not across its registered
classes when the class boundaries are stated as growth rates), so `Sig_k(c(y))`. Frontier: a
frontier point `x` of `B_1` maps to `c(x)` with `R(c(x)) ⪯_{K_C} R(x)`; any `B_2` point dominating
`c(x)` by more than the band would map back to a `B_1` point dominating `x`, contradiction. ∎

**Consequence (encoding-robustness test; instantiates V1 hostile `H-ENCODING-BIAS` as a
number).** A phase boundary between `k, k'` on axis `a` observed under `B_1` is
*encoding-robust* iff the resource gap between the `k`- and `k'`-frontier points on each side of
`a*` exceeds the band `K_C` on the coordinate that decides dominance. If the gap is inside the
band the correct terminal is `SEARCH_ENCODING_DOMINATES` (#377 §22). This makes the encoding
hostile a computed quantity rather than a judgement.

**Assumption whose removal breaks it.** `B_1 ≡_K B_2` with additive combinator cost. If a
combinator has multiplicative cost (`loop_n`), `K_C` grows with `n` and must be computed per
scope.

---

## §T10-A — Analytic phase law from update locality (GMI-T10, analytic part, P1 under the stated cost model)

**Cost model (frozen).** For a composite `x` on ecology `E` with reuse horizon `H` and `r`
revision/feedback events, the charged lifecycle resource on a frozen price coordinate is
```text
C_E(x) = R_desc(x) + H·R_exec(x) + r·R_upd(x) + n_ver·R_ver(x) + n_rev·R_rev(x)
```
(the Codex `ANALYTIC_PHASE_MICROSCOPE_V1.json` model is the special case `n_ver = 0`, one price).

**Lemma A (locality bound).** Under `ρ` charging at least one unit of `upd` per state coordinate
written, `R_upd(x) ≥ c·loc(x)·|Θ_x|` for `loc` as in D2-§3.1: `≥ c·|Θ_x|` for
`DENSE_LINEAR`, `o(|Θ_x|)` for `SPARSE_SUBLINEAR`, `≤ c` for `LOCAL_O1`, `0` for `NONE`.
*Proof.* Writing a coordinate costs ≥ 1 unit; count the coordinates written per event. ∎

**Theorem (locality-induced boundary).** Let `x_D` have `update_locality = DENSE_LINEAR` and
`x_L` have `LOCAL_O1`, both with `Q_E ≥ θ_E`, on a coordinate where `R_exec` and `R_desc` are
registered numbers. Then on the axis `r` (revision/feedback frequency) with `H` frozen, `x_L`
dominates `x_D` for all
```text
r > r* := [ (R_desc(x_L) − R_desc(x_D)) + H·(R_exec(x_L) − R_exec(x_D)) ] / [ R_upd(x_D) − R_upd(x_L) ]
```
whenever the denominator is positive, which Lemma A guarantees for `|Θ_{x_D}|` larger than a
constant; and `x_D` dominates for `r < r*` when the numerator is positive. Symmetrically on the
axis `H` with `r` frozen.

*Proof.* `C_E(x_L) − C_E(x_D)` is affine in `r` with slope `R_upd(x_L) − R_upd(x_D) < 0` by Lemma A
and intercept the bracketed numerator; solve for the root. ∎

**What this is and is not.** The arithmetic is HST-T05 amortization (parent-owned; Codex
labels its toy the same way). The Track-B content is that the *sign of the slope is fixed by a
label-free observable* (`update_locality`), so the direction of the boundary along the
revision axis is predicted from `S(x)` **before** any cost is measured: dense-update classes
lose to local-update classes as revision frequency rises, at equal capability. That is a
prospective, falsifiable D3-shaped prediction at the analytic level (`PH-REV` in
`ECOLOGY_AXES_V2.json`), and the first registered phase prediction of Track B whose inputs are
observables rather than architecture names.

**Assumption whose removal breaks it.** (i) equal capability threshold — if `x_D` reaches a
`Q` that `x_L` cannot, the frontier is not one-dimensional and no boundary exists on `r` alone;
(ii) `ρ` charges per coordinate written — an accounting that charges a dense update as one
event (`H-HIDDEN-RESOURCE`) erases the slope; (iii) `R_exec` independent of `r` — a local-update
store whose lookup cost grows with the number of stored events (`STORE_MATCH_CYCLE` with linear
scan) adds a term `r·H·Δexec` that can reverse the boundary; the microscope must charge it.

**Finite witness required.** A tiny world with one dense-update and one local-update composite
of equal `Q`, exact `C_E` on a registered `(H, r)` grid, and the observed crossing compared with
`r*` computed from the frozen costs (Stage E in `EXACT_MICROSCOPE_V1.md`).

---

## §T11 — Identifiability (GMI-T11, P1 impossibility part + P2 positive target)

**Impossibility.** If `Φ_E(x_1) = Φ_E(x_2)` for every ecology `E` in the registered probe family
`𝓔` (including the `R` coordinate), then no classifier that receives only `(𝓔, Φ_E(·))` can
distinguish `x_1` from `x_2`; in particular a signature class is not identifiable from behaviour
alone when two signatures admit table-equal members with identical resource profiles on `𝓔`.
*Proof.* The classifier is a function of its input. ∎

**Positive target (P2).** `update_locality` is identifiable from the growth of `R_upd` along a
registered size ladder `|Θ| ∈ {n_1 < n_2 < n_3}` at fixed protocol (Lemma A), and
`feedback_dependence` from which feedback channels change `D`. `theta_type` and
`store_discipline` are identifiable only through `desc` growth with experience and through
revision-cost response (`rev`), i.e. they require probes on the `drift` axis. Consequence: a
blind-recovery protocol (#377 §13) must include a size ladder and a drift probe or accept
`MORPHOLOGY_NOT_IDENTIFIABLE_AT_SCOPE` for those coordinates.

**Assumption whose removal breaks the positive part.** A single size point (no ladder) or an
ecology with `Δ = ∅` (no drift) — then `update_locality` / `store_discipline` are not
separable by any probe.
