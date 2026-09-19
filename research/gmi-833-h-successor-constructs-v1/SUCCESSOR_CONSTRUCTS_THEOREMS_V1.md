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

**Assumptions.** The ecology supplies both argument and parameter channels;
the task is form recovery, not parameter estimation. Exact agreement on all 24
search rows is the criterion. The `G_S` stratum is the one written out in
`FREEZE_V1_ADDENDUM.md` A5, with `ADD` as its only combining operation.

**Dependencies.** The `G_H` enumeration of `FREEZE_V1.md` section 4 and the
canonical forms of `FREEZE_V1_ADDENDUM.md` A4. No dependency on any other
named result here, and none on any parent's number.

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

**Assumptions.** The registered channels `A`, `M`, `Q` and the 48 registered
rows; `w = 4`; exact rational arithmetic. Claim (i) is an identity over those
rows, not an algebraic identity claimed for all channels.

**Dependencies.** `SC-8` for the single unchanged grammar. Claim (iii) depends
on the enumeration and the canonical forms, not on claims (i) or (ii).

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

**Assumptions.** For claim (i), `p` divides `N`. For `p` not dividing `N` the shift by
`p` does not preserve residues and the statement is not made.

**Falsifier.** An invariant-row count below 48 at any `p | N`; a zero count in
(ii); a `G_S` match; a cheaper `G_H` match; a recovered `tau` that is
injective.

**Strongest parents.** Fukushima 1980; LeCun et al. 1989; Cohen and Welling
2016. Group-equivariant weight sharing is theirs.

**Dependencies.** The registered index set `I = 0..11` and the modulus list
`(1, 2, 3, 4, 6, 12)` of `FREEZE_V1.md` section 4.3. Independent of every other
named result here.

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

**Dependencies.** The combining-operation extension of `FREEZE_V1.md` section
4.5. Claims (i) and (ii) are independent of the search; claim (iv) depends on
the enumeration and the canonical forms.

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

**Assumptions.** `Y = (-6, -4, 0, 4, 6)` with the registered order; ties broken
to the smallest `y`; the `SIGMA_D34` channels restricted to `{-1, 0, 1}` so the
score lies in `[-12, 12]`, as registered in `FREEZE_V1_ADDENDUM.md` A7.

**Dependencies.** The response-space reduction of `FREEZE_V1.md` section 4.5
and the two pinned tie rows of section 5. Independent of `SC-1` to `SC-4`.

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

**Assumptions.** The structural-class taxonomy and its priority list, fixed in
`FREEZE_V1.md` section 4.10 before any outcome existed. A base rate is a
property of that taxonomy: a coarser class inflates its own base rate, which is
what `SC-6b` records at `SIGMA_D32`.

**Dependencies.** The enumeration of `SC-8`; the recovered cost of each scope
from `SC-1` to `SC-5`, which bounds the census.

**Strongest parents.** The refused null is the response-permutation control of
`gmi-833-h-real-scale-revival-v1`, whose own parent shipped one that nested the
arm it was compared with. Permutation tests generally: Fisher, *The Design of
Experiments*, Oliver and Boyd, 1935; Good, *Permutation, Parametric and
Bootstrap Tests of Hypotheses*, Springer, 2005. The point made here is narrow:
a permutation null is informative under a loss criterion and vacuous under an
exact-agreement criterion.

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

**Assumptions.** Discriminativeness is measured among the search-slice
matchers at the recovered cost. Costs below the recovered cost have no
matchers, so that set is the whole set.

**Dependencies.** The recovered cost and match set of `SC-1` to `SC-5`.

**Strongest parents.** Held-out evaluation as a coordinate is standard; the
residual here is only the applicability test, which is the hostile-vacuity
discipline of `gmi-833-h-real-scale-revival-v1` `FREEZE_V1.md` section 9
applied to a coordinate rather than to a hostile.

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

**Assumptions.** One grammar digest computed from the frozen definition; one
enumeration built before any ecology is loaded; twelve hostiles with the
applicability conditions of `FREEZE_V1.md` section 10.

**Dependencies.** All of `SC-1` to `SC-7`. Claim (iv) additionally depends on
`HRL-1` and on PR #997 `FGS-2` for the prohibition it states, both cited and
neither counted as evidence here.

**Strongest parents.** `gmi-833-h-neutral-four-family-v1` for the one-grammar
many-families form; `gmi-833-h-family-requirement-ledger-v1` `HRL-1` for the
scope tuple. Neither supplies a number here.

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

**Assumptions.** The eleven-coordinate requirement list of issue #833 section
H, read through `gmi-833-h-family-requirement-ledger-v1`'s identifiers.

**Dependencies.** The coordinate ledger of `RESULT_V1.json` and the two-route
agreement recorded in `ISSUE_833_RECONCILIATION_H3_V1.json`.

**Falsifiers.** A row marked closed anywhere in this package; a coordinate
listed as earned whose receipt field is not `true`; a residual that omits
`R11`.

**Strongest parents.** `gmi-833-h-family-requirement-ledger-v1` owns the
per-row residual format; the residuals here are this package's own scopes and
are not that package's row verdicts.

---

# The numbers, as measured

## `SC-9` — the measured values of `SC-1` to `SC-8`

**Scope.** The run recorded in `RESULT_V1.json` and `ORACLE_RESULT_V1.json` at
grammar digest
`d7d30e46302a01415bf0508e801798ed457222c45c3a43b5c6d6acff005b6d51`.

**Statement.** The tables below are the measured values of the results above.
Every entry is an integer produced by the committed executor and reproduced by
the source-separated oracle. Nothing here is a new claim; it is the evidence
for the claims already stated.

**Assumptions.** The registered ecologies, slices, budgets and cost model, all
unchanged from the freeze. Exact `Fraction` and `int` arithmetic throughout.

**Dependencies.** `SC-1` to `SC-8`. Route A and route B each produce these
numbers independently; a test asserts their agreement.

**Falsifiers.** Any entry that the two routes do not agree on; any entry that a
fresh run does not reproduce; a grammar digest that differs before and after
the run.

**Strongest parents.** None. These are this package's own measurements.

All from `RESULT_V1.json`, grammar digest
`d7d30e46302a01415bf0508e801798ed457222c45c3a43b5c6d6acff005b6d51`, identical
before and after every search, twin, null and hostile.

### Enumeration (`R02`)

| slot | leaves | budget | raw trees | semantic classes on the registered probe grid |
|---|---|---|---|---|
| `BODY` | `ARG PARAM C0 C1` | 3 | 116 | 34 |
| `BODY2` | `U PARAM2 C0 C1` | 4 | 756 | 102 |
| `HEAD` | `S1 S2 BIAS STATE RESP C0 C1` | 4 | 1869 | 406 |
| `G_S` head | `S1 BIAS STATE C0 C1` | 4 | 1075 | — |

180 structural configurations `(L, r, ops, p, kind)`. **The search enumerates
raw trees, never semantic representatives**, so the coarser probe grid used for
the class count cannot drop a program that would have matched.

### Recovery, per scope

| scope | row | recovered class | charged cost | syntactic matches | distinct up to commutativity and bank swap | `G_S` stratum |
|---|---|---|---|---|---|---|
| `SIGMA_D17` | H17 | `NORMALISED_RATIO` | 9 | 8 | **1** | no match at cost ≤ 10, 124,700 programs examined |
| `SIGMA_D20` | H20 | `LAYERED_NONLINEAR` | 9 | 4 | **1** | no match, 124,700 examined |
| `SIGMA_D22` | H22 | `TIED_PARAMETER` (`p = 3`) | 5 | 2 | **1** | no match, 124,700 examined |
| `SIGMA_D32` | H32 | `MULTIPLICATIVE_ACCUMULATION` | 6 | 4 | **1** | no match, 124,700 examined |
| `SIGMA_D34` | H34 | `RESPONSE_SPACE_SEARCH` (`ARGMIN`) | 8 | 4 | **1** | no match, 124,700 examined |

Every `R01` prediction of `FREEZE_V1.md` section 8 held on all three counts —
class name, charged cost, and tree predicates — at all five scopes. The
recovered programs:

```
SIGMA_D17  r=2 L=1 p=12 kind=NONE ops=ADD+ADD bodies=ARG|MUL(ARG,PARAM) head=MUL(RECIP(S1),S2)
SIGMA_D20  r=1 L=2 p=12 kind=NONE ops=ADD+ADD bodies=MUL(ARG,PARAM) body2=MUL(PARAM2,STEP(U)) head=S1
SIGMA_D22  r=1 L=1 p=3  kind=NONE ops=ADD     bodies=MUL(ARG,PARAM) head=S1
SIGMA_D32  r=2 L=1 p=12 kind=NONE ops=ADD+MUL bodies=ARG|PARAM      head=MUL(S1,S2)
SIGMA_D34  r=1 L=1 p=12 kind=ARGMIN ops=ADD   bodies=MUL(ARG,PARAM) head=ABS(ADD(RESP,S1))
```

**Uniqueness.** At every scope the whole match set collapses to exactly one
program under commutativity of `ADD` and `MUL` together with exchange of the
two fold banks. The recovery is not merely cheapest, it is unique.

### Derived theorem outputs

| result | measured |
|---|---|
| `SC-2` collapse, affine second stage | identity holds on **48 of 48** rows |
| `SC-2b` separation, `STEP` second stage | identity fails on **48 of 48** rows |
| `SC-3` tied-fold shift invariance | **48 of 48** rows invariant at every `p` in `{1, 2, 3, 4, 6}` |
| `SC-3` untied fold under the same shift | changes on **47 of 48** rows |
| `SC-4` flow round trip and determinant | **180 of 180** (row, probe point) pairs exact, determinant point-independent on all 180 |
| `SC-5` response-space staircase | **5** distinct levels out of a response set of size **5** |

### The null (`SC-6`), per scope

Exact structural-class census of the whole well-formed enumeration up to each
scope's recovered cost.

| scope | enumerated total | count of the recovered class | modal class | verdict |
|---|---|---|---|---|
| `SIGMA_D17` | 6,373,776 | 46,944 | `MULTIPLICATIVE_ACCUMULATION` | `R04` earned |
| `SIGMA_D20` | 6,373,776 | 114,696 | `MULTIPLICATIVE_ACCUMULATION` | `R04` earned |
| `SIGMA_D22` | 22,124 | 1,835 | `MULTIPLICATIVE_ACCUMULATION` | `R04` earned |
| `SIGMA_D32` | 105,232 | 52,360 | `MULTIPLICATIVE_ACCUMULATION` | **`R04` NOT EARNED — `BASE_RATE_DOMINATED`** |
| `SIGMA_D34` | 1,586,992 | 183,040 | `MULTIPLICATIVE_ACCUMULATION` | `R04` earned |

The applicability condition held everywhere: every recovered class has a
strictly positive base-rate count, so the null was never vacuous.

### `SC-6b` — `SIGMA_D32` fails its own null, and why

`MULTIPLICATIVE_ACCUMULATION` is the modal class of the enumeration at every
recovered cost, because the classifier's rule 2 fires on **any** fold whose
combining operation is `MUL`, and half of all combiner assignments have one. At
`SIGMA_D32` the recovered class *is* that class, so the recovery is
`BASE_RATE_DOMINATED` and `R04` is reported **not earned** — even though the
`R01` prediction held exactly and the recovered program is unique.

**Single-stage attribution.** The classifier, not the ecology, not the grammar,
not the search. The class `MULTIPLICATIVE_ACCUMULATION` is too coarse: it
counts a program in which the `MUL`-combining fold is never read by the head.

**The lever, named and not applied here.** A finer class that requires the
`MUL`-combining bank to be one the head depends on. Applying it now would be
tuning a classifier after seeing its verdict, which is exactly the move this
programme forbids. It belongs in a successor freeze, registered before any run.

Nothing about `SIGMA_D32` is weakened by this: `SC-4` stands, the `G_S`
exhaustion stands, the twin stands, and the row's residual simply includes
`R04` as well.

### `SC-7` — held-out discriminativeness, measured

| scope | programs matching the search slice | of those, failing the held-out slice | `R08` |
|---|---|---|---|
| `SIGMA_D17` | 8 | 0 | not earned |
| `SIGMA_D20` | 4 | 0 | not earned |
| `SIGMA_D22` | 2 | 0 | not earned |
| `SIGMA_D32` | 4 | 0 | not earned |
| `SIGMA_D34` | 4 | 0 | not earned |

The recovered program reproduces every held-out row exactly at all five
scopes. That is in the receipt. It is **not** enough to earn `R08` under the
rule registered in `FREEZE_V1.md` section 8.7, because the held-out slice
separated nothing among the search-slice matchers. Under an exact-agreement
criterion at these costs, a held-out slice of 12 rows is not a discriminating
instrument, and saying so is worth more than a coordinate.

### `R07` resource crossovers, exact integers

`table_cost(m) = m + 2^m`. `serve_cost` is the charged ops-plus-storage of the
compact program at index-set size `m`.

| scope | serve cost at `N = 12` | `m*`: first `m` where the tabulated alternative costs strictly more | construct-specific |
|---|---|---|---|
| `SIGMA_D17` | 91 | 6 | — |
| `SIGMA_D20` | 267 | 8 | two-stage parameter storage `m·w + w` beats `2^m` from `m = 5` |
| `SIGMA_D22` | 54 | 5 | tied slots 3 against untied 12; untied storage exceeds tied from `m = 4` |
| `SIGMA_D32` | 66 | 5 | — |
| `SIGMA_D34` | 82 | 6 | — |

`table_cost(12) = 4108` at every scope.

**A bug route B caught.** Route A first charged an untied program a constant
`p` parameter slots at every deployment size, because it compared the tying
modulus against the varying size instead of against the registered index-set
size `N = 12`. Route B, which compares against the registered size, returned
`m* = 5` at `SIGMA_D32` where route A returned `6`. Route A is fixed and the
two now agree at all five scopes; a test asserts the agreement so the defect
cannot return silently. This is what a second route is for, and it is recorded
rather than quietly repaired.

### A registered prediction that failed, and its diagnosis

`FREEZE_V1.md` section 8.6 predicted that the exact-match count would be at
most `4` at every scope. At `SIGMA_D17` it is **8**. Reported as failed.

**Single-stage attribution.** The prediction, not the evidence. The eight
matches are the eight syntactic spellings of **one** program: `MUL` is
commutative in the body, `MUL` is commutative in the head, and the two fold
banks can be exchanged with `S1` and `S2` — `2 × 2 × 2 = 8`. Up to that
symmetry the count is `1`, which is the quantity the prediction was reaching
for and stated badly.

**The lever, named.** Register the match count up to the commutativity and
bank-exchange quotient, not the syntactic count. The quotient is now computed
and reported at every scope (`match_equivalence` in the receipt); it is a
**reporting** quantity and the search does not use it, so no program that
could have matched was removed by it.

No coordinate rests on the failed prediction. `R04`'s applicability condition
and modal rule are separate and both were evaluated as registered.

### Coordinates earned, per scope

`R10` is earned by the agreement of the two routes and is recorded in
`ISSUE_833_RECONCILIATION_H3_V1.json`, which is written after both routes have
run.

| scope | earned | not earned |
|---|---|---|
| `SIGMA_D17` | `R01 R02 R03 R04 R05 R06 R07 R09 R10` | `R08 R11` |
| `SIGMA_D20` | `R01 R02 R03 R04 R05 R06 R07 R09 R10` | `R08 R11` |
| `SIGMA_D22` | `R01 R02 R03 R04 R05 R06 R07 R09 R10` | `R08 R11` |
| `SIGMA_D32` | `R01 R02 R03 R05 R06 R07 R09 R10` | `R04 R08 R11` |
| `SIGMA_D34` | `R01 R02 R03 R04 R05 R06 R07 R09 R10` | `R08 R11` |

**No row closes.** Eleven coordinates at one `sigma` is the bar; nine is not
ten and ten is not eleven, and coordinates earned here do not compose with any
parent's.
