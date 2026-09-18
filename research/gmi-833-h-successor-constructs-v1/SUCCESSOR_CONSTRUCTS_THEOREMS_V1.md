# Named results `SC-1` … `SC-8`

Every result below is stated with its scope, its quantifiers, its assumptions,
its falsifier, its strongest parent and its forbidden extrapolations. Every
number is an integer or an exact `Fraction` and is reproducible from
`RESULT_V1.json`; none is restated here in a stronger form than the receipt
supports.

Shared scope material for `SC-1` … `SC-5`: the grammar `G_H` of `FREEZE_V1.md`
section 4 with digest recorded in `RESULT_V1.json`; index set `I = 0..11`;
stage width `w = 4`; response set `Y = (-6, -4, 0, 4, 6)`; the deterministic
channel stream of `FREEZE_V1.md` section 5; the search slice of 24 rows; the
charged cost model of section 4.7; the canonical forms of
`FREEZE_V1_ADDENDUM.md` A4.

Shared assumption: the search criterion is **exact agreement on every row of a
slice**, in `Fraction` arithmetic. There is no fitting and no tolerance.

Shared forbidden extrapolation, for all eight: none of these is a statement
about all programs, all budgets, all grammars, all data, or any real system.
`UNIVERSAL_NON_REPRESENTABILITY` is a forbidden promotion of every
non-representability result below.

---

## `SC-1` — `COFOLD`: normalisation is a second co-indexed fold, not a new operation

**Scope** `SIGMA_D17`, row `H17` *Bayesian inference/belief-state systems.*
Ecology response `y = (sum_i A_i P_i) / (sum_i A_i)`.

**Statement.** (i) No program of the `G_S` stratum — one `ADD`-combining fold,
`BODY` at most 3 nodes over `{ARG, PARAM, C0, C1}`, `HEAD` at most 4 nodes over
`{S1, BIAS, STATE, C0, C1}` — reproduces `y` on the search slice at any charged
cost up to `B_MAX = 10`. (ii) The cheapest `G_H` program that does has charged
cost `9`, uses two co-indexed fold banks, and is classified
`NORMALISED_RATIO` by the tree-only classifier whose priority was fixed in the
freeze. (iii) **The operation set is unchanged.** The ratio is
`MUL(S1, RECIP(S2))` in the operations `G_S` already had; what `G_S` lacked was
a second fold over the same index set, exactly as the parent obstruction
document said.

**Quantifiers.** For every program in the enumerated `G_S` stratum at
`cost <= 10`; for every program in the enumerated `G_H` set at `cost < 9`.

**Falsifier.** A `G_S`-stratum program that matches the search slice; or a
`G_H` program of charged cost below `9` that matches it; or a recovered
program whose head does not depend on both `S1` and `S2`.

**Strongest parent.** Pearl 1988: the normalising constant as a sum over the
same index set. Not claimed novel.

---

## `SC-2` — `STAGE`: depth two collapses under affinity and separates without it

**Scope** `SIGMA_D20`, row `H20` *Feed-forward neural networks.* Ecology
response `y = sum_j STEP(U_j) Q_j` with `U_j = sum_i A_i M_ij`.

**Statement.** (i) *Collapse.* For every one of the 48 registered rows,
`sum_j (sum_i A_i M_ij) Q_j = sum_i A_i (sum_j M_ij Q_j)` exactly: a two-stage
fold whose second stage is affine in `U` denotes a one-stage fold over a
re-parameterised channel. (ii) *Separation.* With the second stage non-affine
the identity fails on a strictly positive count of the same rows, reported
exactly. (iii) No `G_S`-stratum program reproduces `y` on the search slice at
cost up to `B_MAX`; the cheapest `G_H` program that does has charged cost `9`,
carries `L = 2` with a second stage **not** affine in `U`, and is classified
`LAYERED_NONLINEAR`.

**Why (i) matters.** It is what makes the `SIGMA_D20` twin a *one-property*
twin: the twin removes `STEP` and nothing else, and (i) says that is exactly
the property that separates depth two from depth one.

**Falsifier.** A row where (i) fails; a zero count in (ii); a `G_S` match; a
cheaper `G_H` match; a recovered second stage affine in `U`.

**Strongest parents.** Minsky and Papert 1969; Hornik, Stinchcombe and White
1989. The collapse is textbook and is not claimed novel; only its exact
verification on the registered rows is done here, and only so that the twin is
honest.

---

## `SC-3` — `TIE`: the tying map is a group invariance, and it is necessary here

**Scope** `SIGMA_D22`, row `H22` *CNN/equivariant local-weight-sharing
systems.* Ecology response `y = sum_i A_i P_{i mod 3}`, with the parameter
channel of full length 12 so that tying is not signalled by any channel shape.

**Statement.** (i) *Invariance.* For every `p` dividing `N = 12` and every
registered row, the tied fold `sum_i A_i P_{i mod p}` is unchanged when the
argument channel is cyclically shifted by `p`; the count of invariant rows is
`48` of `48` at every such `p`. Proof: `p | N` makes `i -> (i + p) mod N`
preserve the residue class `i mod p`, so the shift permutes the summands. (ii)
*The untied fold is not invariant*: the count of rows on which the shift by 3
changes the untied fold is strictly positive and is reported exactly. (iii) No
`G_S`-stratum program reproduces `y` at cost up to `B_MAX`; the cheapest `G_H`
program that does has charged cost `5`, carries `tau_3`, and is classified
`TIED_PARAMETER`.

**Assumption for (i).** `p` divides `N`. For `p` not dividing `N` the shift by
`p` does not preserve residues and the statement is not made.

**Falsifier.** An invariant-row count below 48 at any `p | N`; a zero count in
(ii); a `G_S` match; a cheaper `G_H` match; a recovered `tau` that is
injective.

**Strongest parents.** Fukushima 1980; LeCun et al. 1989; Cohen and Welling
2016. Group-equivariant weight sharing is theirs.

---

## `SC-4` — `COMBINER`: the volume term is a `MUL`-combining fold, exactly and without logarithms

**Scope** `SIGMA_D32`, row `H32` *Flow-like transport systems.* Ecology
response `y = (prod_i P_i) (sum_i A_i)`.

**Statement.** (i) *Bijectivity.* The registered elementary step
`z1' = s z1`, `z2' = z2 + c STEP(z1')` with `s != 0` is a bijection of `Q^2`
with the stated inverse; the twelve-step composition returns every probe point
unchanged on a round trip, on every checked (row, point) pair, count reported
exactly. (ii) *Volume.* Its Jacobian determinant is `prod_i s_i`, independent
of the point. (iii) That functional is a fold whose combining operation is
`MUL`, and it is **exact in the rationals**: no logarithm is taken, so no float
enters. (iv) No `G_S`-stratum program — whose only combining operation is
`ADD` — reproduces `y` at cost up to `B_MAX`; the cheapest `G_H` program that
does has charged cost `6`, has one `MUL`-combining and one `ADD`-combining
bank, and is classified `MULTIPLICATIVE_ACCUMULATION`.

**Assumption.** Every registered scale parameter is non-zero; the ecology
stream enforces it by construction.

**Falsifier.** A failed round trip; a point-dependent determinant; a `G_S`
match; a cheaper `G_H` match; a recovered program with no `MUL` combiner.

**Strongest parents.** Rezende and Mohamed 2015; Dinh, Sohl-Dickstein and
Bengio 2017. The triangular construction is theirs. The only move here is to
keep the volume rational.

---

## `SC-5` — `REDUCE`: a reduction over the response space reaches a staircase that forward evaluation does not

**Scope** `SIGMA_D34`, row `H34` *Energy-based systems.* Ecology response
`y = argmin_{u in Y} |S + u|`, `S = sum_i A_i P_i`, ties to the smallest `u`.

**Statement.** (i) The response takes at least three distinct values of `Y` on
the registered rows, reported exactly, so it is a genuine multi-level
quantisation of `-S` and not a degenerate endpoint rule. (ii) No `G_S`-stratum
program reproduces `y` on the search slice at cost up to `B_MAX`: a head of at
most four nodes over `{S1, BIAS, STATE, C0, C1}` evaluated forward does not
realise it. (iii) The cheapest `G_H` program that does has charged cost `8`,
carries `kind = ARGMIN` with a head that depends on `RESP`, and is classified
`RESPONSE_SPACE_SEARCH`. (iv) The tie-break is load-bearing: the registered
rows include tie rows in both the search and the held-out slice, and switching
the tie-break to the largest `u` changes the response on a strictly positive
count of them.

**Falsifier.** Fewer than three distinct levels; a `G_S` match; a cheaper
`G_H` match; a recovered `kind` of `NONE`; a zero count in (iv), which would
make the tie-break hostile vacuous and fail the run.

**Strongest parent.** LeCun et al. 2006. Inference as minimisation over the
response space is theirs.

---

## `SC-6` — the null is a base rate over the grammar, not a permuted response

**Scope** all five.

**Statement.** Under an exact-agreement criterion a response-permutation null
is **vacuous**: permuting the response makes the target exactly unmatchable, so
"0 of 200 controls recover the target class" holds by construction and carries
no information. It is the mirror image of the 98-of-200 coin flip a parent
package shipped, and it is registered in `FREEZE_V1.md` section 8.6 as refused.

The null used instead is the exact structural-class census of the whole
well-formed enumeration up to each scope's recovered cost. For every scope the
receipt reports the integer count of each class, the count of the recovered
class, the modal class, and the number of programs that match the search slice.

**Applicability, which fails the run when violated.** The recovered class must
have a strictly positive base-rate count — a null that cannot produce the class
tests nothing. When the recovered class is the modal class the recovery is
reported `BASE_RATE_DOMINATED` and that scope's `R04` is `NOT_EARNED`.

**Falsifier.** A recovered class with base-rate count zero; a recovered class
that is modal, unreported.

---

## `SC-7` — `R08` is tested for discriminativeness, not assumed

**Scope** all five.

**Statement.** The held-out slice earns a coordinate only if it discriminates.
The receipt reports, per scope, how many programs match the search slice and
how many of those fail the held-out slice. When that second count is `0` the
held-out slice separates nothing among the search-slice matchers and `R08` is
reported `NOT_EARNED` **even though the recovered program does reproduce the
held-out rows exactly**. Both facts are in the receipt.

This is the hostile-applicability discipline applied to a coordinate rather
than to a hostile. The stronger artifact is the measured count, not a claimed
coordinate.

**Falsifier.** An `R08` marked earned at a scope whose search-only-match count
is zero.

---

## `SC-8` — one grammar, five recoveries, no row closed

**Scope** all five.

**Statement.** (i) One and the same `G_H`, with an identical digest before and
after every search, twin, null and hostile, produces all five recoveries. No
ecology receives a grammar extension, an extra operation, an extra leaf or a
hand-supplied candidate. (ii) All twelve registered hostiles are detected and
**none is vacuous**: each carries an applicability condition asserted in the
receipt, and the run fails if any is unmet. (iii) The true run raises no
hostile. (iv) `R11` is not earned at any scope, so **no Section-H row closes
here**, and adding these coordinates to any parent's is
`CROSS_SCOPE_GATE_COMPOSITION`, forbidden.

**Falsifier.** A digest change; an undetected hostile; a vacuous hostile; a
hostile raised on the true run; any row marked closed; any non-empty
`replacements[]` without eleven coordinates at one `sigma`.

---

## What remains, per row

Stated exactly, so that the next lane does not have to re-derive it. Each row's
residual at this package's scope is in `RESULT_V1.json` under
`coordinates.<sigma>.not_earned`. Across all five the residual is the same
shape:

- `R11` **real-scale test** — refused here by construction. These scopes have
  no real provenance, no fitted rows and no scale coordinate. Closing any of
  the five rows requires earning all eleven at **one** real-scale scope, which
  means redoing `R01`–`R10` there too; the coordinates earned here do not
  transport.
- `R08` **held-out frozen prediction** — earned only where the held-out slice
  is shown to discriminate; see `SC-7` and the per-scope counts.
- Parameter estimation — out of scope here by design. This package recovers
  **form** from supplied parameter channels; a real-scale scope must also fit
  parameters, which reintroduces the rationalisation and control machinery this
  package deliberately does not need.
