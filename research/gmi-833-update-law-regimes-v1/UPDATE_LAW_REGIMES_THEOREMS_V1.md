# GMI #833 Section I — update-law regimes for seven external signatures

**Freeze:** `FREEZE_V1.md`, commit `6e42ccd2` (pre-implementation; the executor
lands in `8db1c10f` and later, and `git log` is the evidence).
**Parent ownership:** `PARENT_OWNERSHIP_V1.md` — read it first. Every result
below is stated after subtracting what the parents own.
**Deviations:** `SUPPLEMENT_1_POST_FREEZE_DEVIATIONS.md`, with the exposure of
the load-bearing one MEASURED, not asserted.
**Claim ceiling:**
`GMI_833_SECTION_I_UPDATE_LAW_REGIME_CONDITIONS_AND_PROSPECTIVE_SELECTOR_AT_REGISTERED_FINITE_SCOPE`
**Evidence level:** EV1 (deductive, explicit premises and falsifiers) plus EV2
(exact finite certificates over declared universes). Not EV3/EV4/EV5.
**Domain tags:** `forall[D]` is deductive over a declared domain; `forall_fin[U]`
is complete enumeration of a registered finite universe. **No `forall_fin`
result below may be rewritten as `forall`.**

---

## 0. What this section asks and what is answered

#870 proved that a useful preference between update laws requires stated
ecological, informational and resource assumptions. #1014 answered two of those
preferences exactly. Seven remained, each of the form *derive the conditions
favouring X*, where naming X is forbidden.

The move here is the one #1014 used: **define the signature from structure, then
find where the preference flips.** A signature is a predicate on a law's charged
trace and its emitted predictor; it never mentions an architecture, a family, an
optimizer, a representation or an algorithm. The seven algorithm names appear
in exactly one file, `PARENT_OWNERSHIP_V1.md`, and the lexical, structural and
remint screens check that mechanically rather than asserting it.

---

## 1. The registered objects

Everything lives inside the parent's `A_k`. No new space is defined.

A registered **environment** `E = (Z, H, prior, eps, target, train, Qset, retr,
RS, nbr, Vfun, starts, Fam)` is as frozen in `FREEZE_V1.md` section 2.2, with
`eps = 1/4` frozen before any run. Every derived quantity — the exact posterior,
`alpha_gain`, `mu`, `Dmin`, `disc`, the local optima, `Bmin`, `Tsteps`,
`r = M - |H'|`, and every per-law loss — is **computed** from `E` by both routes
independently. None is asserted.

The **price vector** is

```
pi = (p_test, p_carry, p_store, p_build, p_branch, p_meta, p_mut, lam) in Q_{>0}^8
```

and the total charge of a law is `C(L,E,pi) = <a(L,E), pi>` with
`a(L,E) in Z_{>=0}^8`, whose eighth coordinate is the law's exact integer loss on
the registered held-out query set. **Loss and resource are commensurated inside
the one price vector by the explicit loss price `lam`**, a choice frozen before
any run precisely so that it could not be substituted after seeing a census.

A law is presented as a **structural tuple**
`g = (carry, store, build, breadth, meta, mut)` over registered level sets, and
one accounting function maps `g` to `a(g,E)`. The seven signature
representatives are particular tuples in that space; the blind search of section
7 ranges over the whole space with the same objective.

---

## 2. UL-1 — pointwise-selection closure, and why it matters

**Statement (UNCONDITIONAL)** `forall[S]`. For any index map
`s : R x HIST x Bgrid -> I` and any family `{L_i}_{i in I} subset A_k`, the law
`L(r,h,b) := L_{s(r,h,b)}(r,h,b)` lies in `A_k`.

**Proof.** The parent's admissibility `A1`-`A4` is a finite conjunction of
conditions evaluated **at each presented triple separately**: exact totality and
normalization at `(r,h,b)`; charge well-formedness at `(r,h,b)`; the budget
clause at `(r,h,b)`; support containment in `Succ_k(r,h)`. At every triple the
output of `L` is the output of some `L_i` at that same triple, so every clause
holds. QED.

This strictly generalizes IL-1.2: rational convex mixture is the distributional
special case of pointwise selection. It is one line over the parent's own
definition and is claimed only as a strengthening of the parent's lemma. Its
consequence is section 8's headline, and — unlike composition, which runs stages
in a fixed order — it absorbs **history-dependent** switching, which is what a
law that changes its own rule actually does.

---

## 3. The seven external signatures

| id | external predicate on the trace and the emitted predictor |
|---|---|
| `SIG-W` | the carried state at every step is a normalized exact-rational weighting over `H` equal to the exact conditional of `prior` given the observed prefix, and the emitted predictor is the weighted majority |
| `SIG-X` | no candidate-indexed weight slot is carried; the emitted predictor's value at a query is a function of the stored observed instances only, through the registered retrieval map |
| `SIG-R` | the emitted predictor is a finite set of conditioned productions of total registered description length strictly below the description length of the instance set it covers, and no observed instance is retained after emission |
| `SIG-L` | `SIG-R` holds AND at least one sub-description is re-invoked at more than one invocation site, charged once per site |
| `SIG-P` | a multiset of at least two candidates is carried and the successor is a function of a selection over that multiset |
| `SIG-T` | the step rule is indexed by a parameter carried across episodes and updated between them |
| `SIG-S` | the admissible successor set the law is evaluated against changes during the episode |

Two further objects are registered as **comparators, not signatures**:
`BASE-0`, the single-best point summary (the frozen comparator of `SIG-W`), and
`NULL-0`, the single incumbent — one carried candidate, no store, no
construction.

---

## 4. UL-9 — the non-redundancy lemma, which is the shape of every converse

**Statement (UNCONDITIONAL)** `forall[E, g, pi > 0]`. If lowering a structural
coordinate of `g` to the next registered level leaves the emitted predictor
identical at every registered input, then the lowered tuple emits the same
predictor at a strictly lower charge, so `g` is strictly dominated at **every**
positive price.

**Proof.** The accounting function is monotone and strictly increasing in each
structural coordinate — a lower `carry` retains fewer slots, a lower `store`
retains fewer instances, a lower `build` constructs fewer symbols, a lower
`breadth` carries fewer members, a lower `meta` retains fewer cross-episode
slots, a lower `mut` performs no change — and the loss coordinate is unchanged by
hypothesis. Since `pi > 0`, the inner product strictly falls. QED.

This is the general form of the freeze's own wastefulness clause (section 4.2),
and it is the reason the seven converses below are not seven separate
arguments. Call a signature **vacuous on `E`** when no non-redundant law in the
registered grammar carries it. Then:

- `SIG-P` is vacuous exactly when breadth buys nothing — which is what
  unimodality means;
- `SIG-T` is vacuous exactly when the cross-episode index changes no step — which
  is what `r = 0` means;
- `SIG-S` is vacuous **always**, on every registered environment, which is
  section 8.

The certificate is exact: for each tuple the executor recomputes the emitted
predictor at the lowered level and compares it pointwise over every episode and
every registered query.

---

## 5. The seven thresholds

All values are exact rationals computed from `E`; both routes agree on every
one. `psi*` is reported through its sharp form `disc*` (section 5.3).

| env | `alpha_gain` | `beta*` | `chi*` | `pistar*` | `tau*` | `s*` |
|---|---|---|---|---|---|---|
| `D1` | 2 | 1/16 | 147/8 | 1 | 12/5 | 0 |
| `D2` | 0 | 0 | 109/6 | 1 | 18/5 | 0 |
| `D3` | -1 | -1/32 | undetermined | 1 | 0 | 0 |
| `D4` | 1 | 1/48 | 221/3 | 1 | 18/5 | 0 |
| `D5` | 3 | 3/16 | 163/4 | 1 | 6/5 | 0 |
| `D6` | 3 | 3/16 | 163/4 | **0** | 6/5 | 0 |

### 5.1 UL-2 — exact conditional weighting (`SIG-W`)

**Threshold** `forall[E]`. Against its registered comparator `BASE-0`, a law
with `SIG-W` strictly dominates exactly when

```
p_carry / lam  <  beta*(E) := alpha_gain / ((M - 1) * T)
```

where `alpha_gain` counts the registered queries on which the point summary is
wrong and the weighting right, minus those on which the weighting is wrong and
the point summary right. The extra charge of carrying the full weighting rather
than one slot is exactly `p_carry (M-1) T`; its value is exactly
`lam * alpha_gain`.

**Matched converse (UNCONDITIONAL).** If `alpha_gain <= 0` then `beta* <= 0`, the
inequality is unsatisfiable over `Q_{>0}`, and `SIG-W` is strictly dearer at
**every** positive price. Certificate: `D2` (`alpha_gain = 0`, `beta* = 0`) and
`D3` (`alpha_gain = -1`, `beta* = -1/32`), **0 violations over 2187 registered
prices each**.

**What the mechanism turns out to be.** `alpha_gain > 0` on `D1`, `D4`, `D5` —
environments where a registered stable generative structure is present and the
posterior stays spread. It is `0` on `D2`, where the posterior concentrates
before the last step, and negative on `D3`, where the target lies outside `H`.
The registered structure and the spread are therefore both necessary at
registered scope, and `D2` and `D3` were registered before any run precisely so
that this could fail.

**Falsifier.** A registered `E` with `alpha_gain <= 0` where `SIG-W` is not
strictly dearer at some positive price.

### 5.2 UL-3 — stored-instance retrieval (`SIG-X`)

**Wastefulness lemma (UNCONDITIONAL).** An instance that no registered query
retrieves may be dropped from the store with no change to the emitted predictor
and a strictly lower charge whenever `p_store > 0`. Hence the minimal-charge law
with `SIG-X` retains exactly the retrieved set, of size `mu`. (This is UL-9 at
the `store` coordinate.)

**Threshold.** With every price but `p_store` at the registered unit, `SIG-X`
strictly dominates the compression law exactly below

```
chi*(E)  =  the exact rational root of  <a_X - a_R, pi> = 0  in p_store
```

`chi* = 147/8, 109/6, 221/3, 163/4, 163/4` on `D1, D2, D4, D5, D6`. The general
form is the crossover hyperplane with exact integer normal, reported per pair in
the receipt.

**Certificate.** On the parent's own 46-ratio grid the trichotomy is exhaustive
and exclusive on every usable environment: **0 trichotomy failures**. `SIG-X` is
`WITNESSED` — it is the strict argmin of the seven at an explicit registered
price — on `D1, D2, D4, D5, D6`, and both routes agree on every `chi*`, route B
locating it by outward scan and bracket without ever consulting the closed form.

### 5.3 UL-4 — production compression (`SIG-R`), and its boundary

**Threshold.** Compression pays its discovery charge exactly when

```
(cover - Dmin) * (p_carry * T + p_test * nq)  >  p_test * disc + p_build * Dmin
```

with `disc = |RS| * T` the registered discovery charge and `Dmin` the minimum
total description length of a consistent covering subset of the registered
production space of size at most `KMAX = 3`.

**At the registered production space the condition is NOT satisfiable, and this
is delivered as a mapped boundary rather than hidden.** With `|RS| = 72`
intervals over eight instances, `disc` is `288` on `D1`/`D3`, `432` on `D2`/`D4`
and `144` on `D5`/`D6`, and the `p_build` crossover is negative on every
environment (`-137/2, -102, -108, -155/4, -155/4`): no positive construction
price makes compression win, and on `D1`, `D5` and `D6` `SIG-R` carries a
`DOMINATED_EVERYWHERE` certificate — a coordinatewise dominator, which is an
unconditional statement over all positive prices, not a grid observation.

**The adjacent scoped positive, and it is the sharper statement.** Solving the
same frozen inequality for the discovery charge gives `disc*(E)`, the largest
per-episode discovery charge at which the compression law still wins, hence the
largest production space at which the condition is satisfiable at all:
`|RS| <= disc*/T`.

| env | `disc` (registered) | `disc*` | largest satisfiable `|RS|` |
|---|---|---|---|
| `D1` | 288 | **10** | 5/2 |
| `D2` | 432 | **20** | 10/3 |
| `D4` | 432 | **0** | 0 |
| `D5` | 144 | **0** | 0 |
| `D6` | 144 | **0** | 0 |

**The condition favouring production compression is therefore a bound on the
size of the space the productions are discovered in**, and the registered
72-production space exceeds every one of these bounds — which is why the row's
answer is a threshold on `disc`, not on `p_build`. On `D4`, `D5` and `D6`
`disc* = 0`: no discovery charge at all, not even zero, makes compression win
there, because the retrieval law is cheaper for reasons independent of
discovery. That is reported, not smoothed.

**Falsifier.** A registered `E` where the compression law wins at a positive
price while `disc > disc*`, or loses while `disc < disc*`.

### 5.4 UL-5 — re-invocation (`SIG-L`), closed BY RECONCILIATION TO #897

#897 owns the invention result, the grammar growth and the held-out reuse
benefit, and this tranche re-runs none of them. What is added is the placement:
inside `A_k`, the re-invocation refinement of a description-emitting law is
favoured exactly when

```
Hocc * Delta  >  Kdef
```

— the same lifecycle inequality #897 earned as THR-1 (`H_eff * Delta > K`),
restated in this tranche's price coordinates, with `Hocc` the number of
invocation sites, `Delta` the per-site symbol saving and `Kdef` the definition
length plus maintenance. The refinement bites where the inequality holds: the
constructed length falls from `Dmin = 4` to `Dmin_L = 3` on `D1` and from `4` to
`1` on `D5` and `D6`, and does not move on `D2` and `D4`. Sign agreement with
#897's earned result is checked in the receipt.

**Demarcation, stated explicitly.** #897 owns `G_t -> G_{t+1}`, recursive library
formation, primitive invention and the held-out reuse study. This tranche owns
only the update-law-space placement of the condition. `LIBRARY_INVENTION_RESULT_IS_NOVEL_HERE`
and `GRAMMAR_GROWTH_OWNED_HERE` are forbidden promotions.

### 5.5 UL-6 — breadth selection (`SIG-P`)

**Threshold** `forall[E]`. Against the single incumbent,

```
p_branch / lam  <  pistar*(E) := (Vglob - Vloc) / ((Bmin - 1) * Tsteps)
```

where `Vloc` is the score of the terminal the single incumbent ascends to from
the registered start, `Vglob` the global registered score, and `Bmin` the
smallest registered breadth whose start set reaches it. `pistar* = 1` on the
five multimodal environments.

**Matched converse (UNCONDITIONAL).** If the registered score landscape is
unimodal, every registered start ascends to the same terminal, so `Vglob = Vloc`,
`pistar* = 0`, and — by UL-9 at the `breadth` coordinate — every breadth-`b`
tuple with `b >= 2` emits the same predictor as its breadth-1 counterpart and is
therefore strictly dearer at every positive price. Certificate: `D6`,
`pistar* = 0`, `SIG-P` **vacuous**, and the same statement verified on the
held-out unimodal environment `X6` as prediction `HO-P3`.

**Certificate of the positive side.** `SIG-P` is `WITNESSED` on `D1`, `D2` and
`D4` at explicit registered prices.

**Falsifier.** A unimodal registered `E` where some breadth-`b >= 2` law is not
strictly dearer than its breadth-1 counterpart at some positive price.

### 5.6 UL-7 — cross-episode indexing (`SIG-T`)

**Threshold** `forall[E]`. Over the registered `K`-episode family, with
relatedness `r := M - |H'|`,

```
p_meta / p_test  <  tau*(E) := r * T * (K - k0) / (|H'| * K)
```

`tau* = 12/5, 18/5, 18/5, 6/5, 6/5` on the five families with `r = 4`, and
exactly `0` on `D3`, where `r = 0`.

**Reduction falsifier (UNCONDITIONAL), and this is the row's falsifier.** When
`r = 0` the carried cross-episode parameter is the constant registered candidate
set, so the indexed step rule equals the base step rule. This is verified
**pointwise**, not inferred from equal cost: on `D3` the executor compares the
two rules' emitted bit at every one of the registered `(episode, instance)`
inputs — `K * nz = 4 * 8 = 32` inputs — and finds **0 mismatches**, while the
indexed law's charge exceeds the base law's by exactly `p_meta * |H'| * K =
p_meta * 36 > 0`. So at zero relatedness the law is behaviourally identical and
strictly dearer: `SIG-T` is vacuous. Both routes compute the reduction
independently and agree.

**Certificate of the positive side.** `SIG-T` is `WITNESSED` on `D1`, `D2` and
`D4`.

**Falsifier.** A registered family with `r = 0` where the two rules differ at any
registered input, or where the indexed law is not strictly dearer.

### 5.7 UL-8 — successor-set change (`SIG-S`): the conditions are EMPTY

This is the sharpest result in the tranche and it is deductive.

**Statement (UNCONDITIONAL)** `forall[E, pi > 0]`. Inside any comparison class
closed under pointwise selection — by UL-1, `A_k` itself is such a class — a law
that changes its own admissible successor set is **extensionally equal to a fixed
member of the class** and pays a strictly positive mutation charge on top.
Therefore it is strictly dominated at every positive price, and the set of
conditions favouring it is **EMPTY**.

**Proof.** A law satisfying the registered contract is a total map from
`(r,h,b)`; its internal mode, however it evolves, is a function of that argument.
By UL-1 the pointwise selection of admissible outputs is itself admissible, so
the self-modifying law's behaviour is realized by a fixed `L' in A_k` at charge
`a(L')`. The self-modifying law's charge is `a(L') + p_mut * (number of changes)`
with `p_mut > 0` registered. QED.

**Certificate.** `s* = 0` on **all six** registered environments — the loss of
the best fixed law in the class equals the loss of the best reachable law, so the
change buys nothing; the coefficient vector of `SIG-S` equals that of `BASE-0` in
every coordinate except `p_mut`, where it exceeds it; and `SIG-S` is strictly
dearer than its comparator at **all 2187 registered prices on every
environment**, with `SIG-S` **vacuous** in the non-redundant grammar on every
environment. Hostile `HR-09` plants the opposite claim and is refused.

**Matched positive, EARNED-BY-COUNTEREXAMPLE, from the parent's own
counterexample.** The emptiness is a statement about *pointwise-selection-closed*
classes. It fails exactly when the fixed comparison class is not closed under the
law's own iteration, and the parent exhibits such a class: IL-1.3 proves
`A_1` — the ONE_STEP grade — is **not** closed under composition, with the
witness `Delta(r0,h0) = {r1}`, `Delta(r1, ext(h0,r1)) = {r2}`, where the composite
places all mass at `r2` while `Succ_ONE_STEP(r0,h0) = {r0, r1}`. A law confined
to `A_1` that changes its successor set reaches `r2`; **no fixed `A_1` law places
any mass there.** So

```
p_mut / lam  <  s*  :=  (loss of the best fixed law of the class)
                        - (loss of the best law reachable after the change)
```

is satisfiable exactly when the change reaches a strictly better region outside
the class, and `s* > 0` requires the class to fail closure. That is the exact
condition the row asks for, and it is a condition on the **comparison class**,
not on the ecology or the price.

**Scope.** This is a cost-and-reachability statement inside `A_k`. It carries no
governance content; #848/#874 own that, and
`SELF_MODIFICATION_GOVERNANCE_SETTLED` is a forbidden promotion.

---

## 6. Joint structure

### 6.1 UL-10a — the compatibility matrix, reported AS A MATRIX

**The seven predicates do NOT separate law space.** Of the 21 unordered pairs,
**16 are COMPATIBLE** — each with an explicit consistent witness clause set — and
**5 are EXCLUSIVE**, each with the exact contradicting clause pair. In
particular `SIG-L` is **nested inside** `SIG-R` by its own definition, which is
exactly the shape (`joint = max` a strict sub-case of `joint < sum`) that made
`CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1`'s DEF-2 a false partition. The word
partition is **not** applied to this matrix, and
`SEVEN_SIGNATURES_PARTITION_LAW_SPACE` is a forbidden promotion. Hostile `HR-06`
plants the partition claim and is refused. Both routes compute the matrix
independently and agree.

### 6.2 UL-10b — the argmin-cell partition, which IS one

**Statement (UNCONDITIONAL)** `forall[pi in Q_{>0}^8]`. Fix `E` and the seven
representative coefficient vectors `a_1..a_7 in Z_{>=0}^8`. The strict cells
`Cell_i = {pi > 0 : <a_i,pi> < <a_j,pi> for all j != i}` and the tie sets
`Tie_S = {pi > 0 : argmin = S, |S| >= 2}` are pairwise disjoint and their union
is all of `Q_{>0}^8`.

**Proof.** At each `pi` the seven values are exact rationals; the argmin of a
finite nonempty set of rationals exists and is a nonempty subset, and every `pi`
falls in exactly one of the cases "argmin is a singleton `{i}`" or "argmin is a
set of size `>= 2`". Disjointness and exhaustiveness are immediate. QED.

The `21` crossover surfaces are the exact hyperplanes `<a_i - a_j, pi> = 0`,
reported with exact integer normal vectors per environment.

**Scope discipline, stated because it is easy to overclaim.** The theorem's scope
is every positive price vector; the censuses below exhibit cells and are
`forall_fin` over a registered price set. **Grid coverage is not the theorem's
scope**, and `GRID_COVERAGE_IS_PARTITION_SCOPE` is a forbidden promotion.

### 6.3 The two censuses, and what the frozen grid actually shows

The frozen uniform grid of `3^7 = 2187` price vectors lies entirely in the
**resource-dominated** regime: at `nq <= 6` the loss differences between laws are
at most single digits while the resource differences run to hundreds, and the
frozen `lam` levels `{1/4, 1, 4}` cannot close that gap. Its cell counts are
reported in the receipt for completeness and are **not** load-bearing.

The load-bearing census is the **anchored** one, built by the parent's own
IL-2/IL-3 design lifted to this space: for every pair of registered
representatives and every price coordinate, locate the exact crossover in that
coordinate and probe at half it, at it, and at twice it. The construction is
geometric — fixed by the crossover surfaces themselves — and was not chosen by
looking at an outcome. It yields 82 to 189 prices per environment.

| env | anchored prices | `SIG-W` | `SIG-X` | `SIG-R` | `SIG-L` | `SIG-P` | `SIG-T` | `SIG-S` | ties | partition failures |
|---|---|---|---|---|---|---|---|---|---|---|
| `D1` | 187 | 0 | 106 | 0 | 0 | 25 | 36 | 14 | 6 | **0** |
| `D2` | 154 | 0 | 72 | 0 | 0 | 12 | 57 | 7 | 6 | **0** |
| `D3` | 82 | — | — | — | — | — | — | — | 0 | **0** |
| `D4` | 142 | 3 | 106 | 0 | 0 | 14 | 16 | 0 | 3 | **0** |
| `D5` | 175 | 0 | 158 | 0 | 0 | 0 | 16 | 0 | 1 | **0** |
| `D6` | 189 | 0 | 170 | 0 | 0 | 0 | 18 | 0 | 1 | **0** |

`D3` is entirely `ABSTAIN_UNDERDETERMINED`: no consistent covering production set
exists there, so two of the seven coefficient vectors are undefined and the
frozen selector abstains on all 2187 prices — the typed abstention working as
specified, not a gap.

**Empty cells are reported as findings.** `SIG-R` and `SIG-L` are empty on every
environment, for the reason UL-4 gives; `SIG-R` additionally carries an
unconditional `DOMINATED_EVERYWHERE` certificate on `D1`, `D5` and `D6`, and
`SIG-L` on `D6`. Hostile `HR-11` plants a domination certificate whose dominator
is not coordinatewise and is refused.

---

## 7. UL-11 and UL-12 — the prospective selector and the blind search

### 7.1 The selector

`select(inv, vecs, pi)` is exactly the decision table frozen in `FREEZE_V1.md`
section 6, committed before any census was run. It is **total** on its declared
input type and **deterministic**, with three typed abstentions
(`ABSTAIN_UNDERDETERMINED`, `ABSTAIN_ILL_TYPED`, `ABSTAIN_TIE`) and no silent
failure.

**Soundness.** Whenever it returns `REGIME_i`, `a_i` attains the strict minimum
charge among the seven representatives **and over their whole rational mixture
hull** — the hull extension is the parent's IL-1.2, since a mixture's charge is
the convex combination of the stage charges.

**Certificate.** Over the frozen grid and the anchored set on all six
environments: **0 soundness violations and 0 mixture-hull violations**, with
totality verified case by case (every case is exactly one of a regime return or
one of the three typed abstentions). Hostile `HR-13` drops a typed abstention and
is refused; `HR-10` plants a tie absorbed into a regime cell and is refused;
`HR-02` feeds a float price and is refused at STEP 2.

### 7.2 The blind search

The neutral grammar is the frozen structural tuple space of section 7 of the
freeze, filtered by UL-9 to the **non-redundant** laws. No coordinate, no
objective term and no tie rule names a family, a signature or a mechanism; the
objective is exactly `<a(g,E), pi>`, the same charge function used everywhere
else; the signature of the argmin is computed **after** the search by applying
the section-3 predicates to the tuple's induced trace. Hostile `HR-12` plants ten
mechanism-named identifiers into the grammar's vocabulary and the screen catches
**10/10** with **0/10** false alarms on ten structurally similar clean
identifiers.

**Result on the derivation set: 0 disagreements**, on both the frozen grid and
the anchored set, on all six environments, under both routes. Where the selector
returns a regime that is vacuous on that environment, the case is classified
`VACUOUS_REGIME` and counted separately rather than scored as agreement — the
counts are in the receipt. Under `select_v2` (section 8) the derivation set
scores **0 disagreements on every environment on both grids**, with 2187/2187
agreement on the frozen grid for four of the six.

**Null.** Against 200 randomized regime assignments on the anchored prices: the
true selector scores **131/131** hits, the best null scores **33**, and **0/200**
nulls reach the true score. The null is shown non-vacuous by the fact that it
does score hits. A second null draws the crossover threshold from a different
registered environment: **0/200** locate the target environment's exact
crossover, while the true threshold locates it on **5/5** usable environments.

---

## 8. UL-13 — held-out crossover boundaries

Predictions `HO-P1` to `HO-P4` are in the freeze commit; the held-out
environments `X1`..`X6` are built over a different instance set and a
structurally different candidate table and are used in no derivation.

- **`HO-P1` HIT.** On every defined held-out threshold the closed form equals,
  exactly, the crossover located independently by rational bisection on the two
  charges, the bisection never consulting the closed form. Scoring convention
  disclosed as deviation D2.
- **`HO-P3` HIT.** Both unconditional converses hold on the held-out set: on the
  held-out environments with `alpha_gain <= 0` the weighting law is strictly
  dearer than the point summary at every one of the 2187 registered prices, and
  on the unimodal held-out environment every breadth-`>= 2` tuple is strictly
  dearer than its breadth-1 counterpart. Scoring convention disclosed as
  deviation D3.
- **`HO-P4` HIT**, as stated, with no convention change: the held-out set does
  produce `DOMINATED_EVERYWHERE` certificates, so the empty-cell finding is not
  an artefact of the derivation set.
- **`HO-P2` MISS, with 267 mismatches of which 267 are attributed and 0 are
  unattributed — and the miss is the most useful thing the held-out set did.**
  The frozen selector ranks **canonical** representatives. A canonical
  representative can itself be redundant — a wasted structural coordinate — and
  the blind search ranges only over non-redundant laws, so it can never return
  that law. The attribution is to **one stage**: the frozen selector's
  representative construction. The thresholds are not implicated (they are
  computed the same way and `HO-P1` hit) and the search is not implicated (it
  disagrees with nothing on the derivation set). The verdict is scored against
  the prediction **exactly as frozen**: every case where the frozen selector's
  regime is not what the blind search returns counts as a mismatch, including
  the 267 whose cause is the redundant-representative stage. Reclassifying them
  would have turned the verdict to HIT, and that reclassification is refused.

**Revival, delivered rather than deferred.** `select_v2` ranks the charge-minimal
**non-redundant** law of each signature class instead of the canonical
representative. Its soundness proof is unchanged, and by UL-9 it is *strictly
more* sound: ranking a redundant representative is ranking a law that is
dominated at every price. Its held-out agreement is reported in the receipt
under `heldout.HO_P2.repair_select_v2`. On the held-out set `select_v2`
scores **803 agreements and 0 disagreements**. `select_v2` is a **post-freeze
repair whose necessity was exposed by this held-out miss**, which is exactly
what a held-out test is for; it is disclosed as deviation D8, the row
`Build a prospective learning-law selector` is claimed on the FROZEN selector,
and the frozen selector's own numbers are reported unchanged beside it.

---

## 9. Scope, assumptions, falsifiers, forbidden extrapolations

**Scope.** Finite registered universes throughout. `forall[D]` results are
deductive over their declared domain; `forall_fin[U]` results are complete
enumerations of a registered finite universe and **may not be rewritten as
unrestricted universals**. Evidence EV1 and EV2, maturity M1-M2. **Nothing here
is validated on real trained systems**, and the row asking for that is left open
by name.

**Assumptions carried.** Exact rational prices, probabilities and scores; the
frozen noise rate `eps = 1/4`; the declared channel and store semantics (the
store is a prefix of the registered training sequence); the declared cost model
with loss commensurated by `lam`; the registered environment, production,
landscape and family declarations; the registered tie rules (smallest index;
an exactly split weight predicts `0`). Every dominance claim is scoped to the
seven registered representatives and their rational mixture hull — never to
`A_star`.

**Falsifiers.** Each is stated with its result above. In summary: a registered
`E` with `alpha_gain <= 0` where the weighting law is not strictly dearer; a
registered `E` where dropping a never-retrieved instance changes the emitted
predictor; a unimodal registered `E` where breadth is not strictly wasteful; a
registered family with `r = 0` where the indexed and base step rules differ at
any registered input; a registered `E` where a successor-set change is cheaper
than its comparator inside a pointwise-selection-closed class; a registered case
where more or fewer than one of the argmin cases holds; a `DOMINATED_EVERYWHERE`
certificate whose dominator is not coordinatewise; a denylist hit in a
strictly-clean file; and Route A and Route B disagreeing on any registered case.

**Strongest parents.** `PARENT_OWNERSHIP_V1.md`. In one line: #1014 owns the
law space and both of its earned crossovers; #870 owns the no-free-lunch
boundary that makes these rows well-posed; #897 owns library invention and its
lifecycle threshold; #848/#874 own governed self-change; and the literature
parents listed there own every one of the seven mechanisms.

**Forbidden promotions.** As pre-committed in `FREEZE_V1.md` section 10 and
carried verbatim into `MANIFEST_V1.json`.
