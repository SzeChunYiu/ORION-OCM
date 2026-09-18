# GMI #833 Section-H successor-construct freeze v1

`source_main`: `50f833cc4bc3cadcefd44eca14fa58f73f815587`.

Committed **in its own commit, before any executor, test, ecology, enumeration,
search, or result artifact of this package exists**. `git log --diff-filter=A`
order is the custody record and CI asserts it. #976 confirmed a
`POST_HOC_SUSPECT` on an 89-minute freeze/result gap; this file exists to make
that check trivial here.

## 1. The exact issue rows this tranche concerns

Section of issue #833: the `# H.` header line, recorded verbatim as the
`anchor` field of `ISSUE_833_RECONCILIATION_H3_V1.json`.

Rows, verbatim and complete, with their canonical machine ids from
`research/gmi-833-h-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json`:

```
H17  - [ ] Bayesian inference/belief-state systems.
H20  - [ ] Feed-forward neural networks.
H22  - [ ] CNN/equivariant local-weight-sharing systems.
H32  - [ ] Flow-like transport systems.
H34  - [ ] Energy-based systems.
```

**No neighboring row is earned here.** No aggregate Section-H row, no row of
any other section, and none of the other 38 named-family rows.

**This package closes no row and expects to close none.** `R11` (real-scale
test) is out of scope by construction (Section 9), so no row can reach eleven
coordinates at this package's scopes. `replacements[]` of the reconciliation
artifact is expected to be empty, and a test asserts that any non-empty
`replacements[]` is accompanied by eleven earned coordinates at one and the
same `sigma`.

## 2. The scope decision that governs this package

Five scopes, one per row: `SIGMA_D17`, `SIGMA_D20`, `SIGMA_D22`, `SIGMA_D32`,
`SIGMA_D34`. A scope is the tuple `(family row, grammar, ecology, budget,
freeze, protected interface)`.

**This package imports no gate certificate from any parent.** Composing a
coordinate earned at `SIGMA_4F`, `SIGMA_CENSUS`, `SIGMA_R02`, `SIGMA_R03` or
`SIGMA_R04` with a coordinate earned here is `CROSS_SCOPE_GATE_COMPOSITION`,
forbidden by `gmi-833-h-family-requirement-ledger-v1` `HRL-1` and proved
invalid by PR #997 `FGS-2`. A test asserts that no certificate emitted here
carries a `sigma` that is not one of this package's own five, and that the
checker reads no parent result file.

Parents supply **form only** — the eleven-coordinate ledger shape, the lower
grammar shape, the post-hoc tree-only classifier idea, the charged cost model
shape, the applicability-flag discipline. `PARENT_LEDGER.md` names them. No
parent number is counted here.

## 3. What this package builds, and why

`gmi-833-h-real-scale-revival-v1/SECTION_H_RESIDUAL_OBSTRUCTION_V1.md` named,
per row, the construct the lower grammar `G_S` lacks. It closed no checkbox and
built no construct. This package builds the five constructs, derives their
properties, and earns the coordinates the derivation reaches.

The five named missing constructs, and the generic form each takes here:

| row | named missing construct | generic construct built here |
|---|---|---|
| H17 | two accumulates over one shared index set, and their ratio | `COFOLD`: `r` co-indexed fold banks over one index set, exposing `S1..Sr` to the head; the ratio is then `MUL(S1, RECIP(S2))` in the **existing** operation set |
| H20 | a vector of accumulators feeding a second accumulate | `STAGE`: fold depth `L in {1,2}`; at `L=2`, `w` stage-1 folds produce `U_0..U_{w-1}`, folded again by `BODY2(U_j, PARAM2_j)` |
| H22 | an index map from position to parameter slot, plus a declared group action | `TIE`: a tying map `tau_p(i) = i mod p` on the index set, together with the registered cyclic shift group `C_p` acting on it |
| H32 | an invertible-composition construct and a log-volume accumulator | `COMBINER`: a fold's combining operation is a construct parameter over `{ADD, MUL}` with identities `{0, 1}`; the volume change is an **exact rational product accumulator**, never a logarithm, so no float is introduced. The invertible composition is registered separately in Section 7 and its Jacobian identity is derived, not searched |
| H34 | an argmin or partition-function operator over the response space | `REDUCE`: a reduction over the registered finite response set `Y`, `ARGMIN` or `RSUM`, with the candidate response exposed to the head as the leaf `RESP` |

`COFOLD` and `COMBINER` are one generalisation seen twice: *a fold is a triple
(combining operation, body, index set), and several folds may share one index
set*. Registering it once, generically, is strictly stronger for `R03` than
registering a normalisation operator and a volume operator separately. No
construct carries a family word, and none is reachable only by one ecology.

## 4. The grammar `G_H`, frozen before any data is built

`G_H` extends `G_S` (`gmi-833-h-real-scale-revival-v1` `FREEZE_V1.md` section
5, re-implemented here from its written specification, imported from nothing).

### 4.1 Terminals

- Fold-body level: `ARG`, `PARAM`, `C0` = 0, `C1` = 1.
- Second-stage body level: `U`, `PARAM2`, `C0`, `C1`.
- Head level: `S1`, `S2`, `BIAS`, `STATE`, `RESP`, `C0`, `C1`.

### 4.2 Compositions

Unary `NEG(a)`, `ABS(a)`, `STEP(a)` = 1 if `a > 0` else 0, `RECIP(a)` = `1/a`
if `a != 0` else 0. Binary `ADD(a,b)`, `MUL(a,b)`. All generic, arity at most
two, unchanged from `G_S`. **No operation is added.**

### 4.3 Storage

`INDEXED_PARAMETER_READ` through a tying map `tau_p(i) = i mod p`, `p` in the
registered list `(1, 2, 3, 4, 6, 12)`. `p = 12 = N` is the identity map and is
the `G_S` behaviour.

### 4.4 Temporal

`DELAY_CELL`: `STATE_{t+1} <- OUT_t`. Kept although no row of this tranche is a
stateful family; removing it would tailor the grammar to the answer.

### 4.5 Reductions

- `FOLD(op, body, index set)` with `op` in `{ADD, MUL}`, identity `0` and `1`
  respectively. `r` in `{1, 2}` banks may share the one registered index set
  `I = 0..11`.
- `REDUCE(kind, Y)` with `kind` in `{NONE, ARGMIN, RSUM}` over the registered
  finite response set `Y = (-6, -4, 0, 4, 6)`. `ARGMIN` returns the `y` in `Y`
  minimising the head value, ties broken to the **smallest** `y` in the
  registered order. `RSUM` returns the exact sum of the head value over `Y`.
  When `kind = NONE` the head may not read `RESP`.

### 4.6 Program schema

```
for k in 0..r-1:   S_k = FOLD(op_k, BODY_k, I)                       (L = 1)
or                 U_j = FOLD(op_1, BODY1, I) using PARAM2D[i][j]     (L = 2)
                   S_0 = FOLD(op_2, BODY2(U_j, PARAM2_j), J=0..w-1)
OUT_t = REDUCE(kind, Y) of HEAD(S1, S2, BIAS, STATE, RESP)
STATE_{t+1} = OUT_t
```

`L = 2` forces `r = 1`. `BODY_k` ranges over every `G_H` expression of at most
3 nodes on `{ARG, PARAM, C0, C1}`. `BODY2` ranges over every expression of at
most 3 nodes on `{U, PARAM2, C0, C1}`. `HEAD` ranges over every expression of
at most 4 nodes on `{S1, S2, BIAS, STATE, RESP, C0, C1}`.

`N = 12`, `w = 4`.

### 4.7 Registered budget and charged cost

```
cost = sum_k nodes(BODY_k) + nodes(BODY2 if L = 2) + nodes(HEAD)
     + 1 if r = 2
     + 1 if L = 2
     + 1 if tau_p is not injective
     + 1 if kind != NONE
```

The combining operation is charged **0**: `ADD` and `MUL` are equally primitive
in the composition set, and charging one of them would be a thumb on the scale
for or against one row. The registered search cap is `B_MAX = 10`. `R06` is a
statement about minimality **within the enumerated set at `B_MAX`**, never
about all programs.

### 4.8 Canonical-form rule

An `r = 2` program whose head does not depend on `S2` denotes the same function
as an `r = 1` program and is excluded from the `r = 2` stratum. An `L = 2`
program is excluded when its head does not depend on `S1`. Both rules are
generic and stated before any ecology exists.

### 4.9 Family-blindness

The generator receives no family name, no family identifier, no
family-specific candidate menu, and no response values. Enumeration is built
**before** any ecology is loaded and its digest is checked before and after
every search. Every ecology presents the **same four input channels** with the
same shapes, so channel shape carries no hint: `A[0..11]`, `P[0..11]`,
`M[0..11][0..3]`, `Q[0..3]`, each filled at every scope whether the response
uses it or not.

### 4.10 Structural classifier, priority fixed here

Reads expression trees and structural flags only; never a family label. A call
that is passed anything but trees and flags raises.

```
 1 kind != NONE and head depends on RESP                  -> RESPONSE_SPACE_SEARCH
 2 some fold combining operation is MUL                   -> MULTIPLICATIVE_ACCUMULATION
 3 r = 2, head depends on S1 and S2, and head is not
   affine in S1 or not affine in S2                       -> NORMALISED_RATIO
 4 r = 2 and head depends on S1 and S2                    -> COUPLED_FOLDS
 5 L = 2 and BODY2 is not affine in U                     -> LAYERED_NONLINEAR
 6 L = 2                                                  -> LAYERED_AFFINE
 7 tau_p is not injective                                 -> TIED_PARAMETER
 8 head depends on STATE                                  -> PERSISTENT_STATE
 9 BODY is not affine in ARG                              -> LIFTED_BASIS
10 head is not affine in S1                               -> NONLINEAR_LINK
11 otherwise                                              -> AFFINE_SCORE
```

`affine in x` means: for every fixed assignment of the other leaves from the
probe grid, the map `x -> value` has vanishing second difference on the
arithmetic sub-grid `(-2, -1, 0, 1, 2)`. `depends on x` means the value moves
when `x` moves with the others fixed. Probe grid `(-2, -1, -1/2, 0, 1/2, 1, 2)`,
unchanged from `G_S`.

## 5. The five ecologies, registered before they are built

Every scope shares `N = 12`, `w = 4`, `Y = (-6, -4, 0, 4, 6)`, 48 rows, and the
four channels of Section 4.9. Channel values come from the registered
deterministic stream

```
s_0 = 20260918 ;  s_{k+1} = (1103515245 * s_k + 12345) mod 2^31
```

drawing, in the fixed order `A`, `P`, `M`, `Q`, the integers

```
A_i = (s mod 11)            in [0, 10]
P_i = ((s mod 21) - 10), replaced by 1 when it is 0   in [-10, 10] \ {0}
M_ij = ((s mod 7) - 3)      in [-3, 3]
Q_j = ((s mod 7) - 3)       in [-3, 3]
```

No sampler, simulator or generator outside this stream is used, and no value is
drawn from any model. A row whose `sum_i A_i` is zero is rebuilt from the next
stream position; the number of rebuilds is reported.

**Two pinned rows**, registered here so that the `ARGMIN` tie-break hostile of
Section 8 is not vacuous. Search-slice row 0 and held-out-slice row 0 have
their `A` and `P` channels overridden to

```
A = (1,1,1,1,1,0,0,0,0,0,0,0)  P = (1,1,1,1,1,1,1,1,1,1,1,1)   (S = 5, a tie)
A = (1,1,0,0,0,0,0,0,0,0,0,0)  P = (-1,-1,1,1,1,1,1,1,1,1,1,1) (S = -2, a tie)
```

The midpoints of `Y` are `-5, -2, 2, 5`; both pinned rows sit on one.

### 5.1 The five response functionals

| scope | row | response `y` |
|---|---|---|
| `SIGMA_D17` | H17 | `(sum_i A_i * P_i) / (sum_i A_i)` |
| `SIGMA_D20` | H20 | `sum_{j<4} STEP(U_j) * Q_j` with `U_j = sum_i A_i * M_ij` |
| `SIGMA_D22` | H22 | `sum_i A_i * P_{i mod 3}` |
| `SIGMA_D32` | H32 | `(prod_i P_i) * (sum_i A_i)` |
| `SIGMA_D34` | H34 | `argmin_{u in Y} |(sum_i A_i * P_i) + u|`, ties to the smallest `u` |

For `SIGMA_D34` the score `S = sum_i A_i * P_i` is built from the restricted
channels `A_i in {-1,0,1}`, `P_i in {-1,0,1}` (drawn as `(s mod 3) - 1`, with
`P_i` left at `0` when it is `0`), so `S` lies in `[-12, 12]` and `Y` is a
genuine coarse quantisation of `-S`. Every other channel is drawn as in
Section 5.

### 5.2 The five matched negative controls, each moving exactly one property

| twin | scope | response `y` | the one property moved |
|---|---|---|---|
| `T17` | `SIGMA_D17` | `sum_i A_i * P_i` | normalisation removed; everything else identical |
| `T20` | `SIGMA_D20` | `sum_{j<4} U_j * Q_j` | the second stage made affine in `U`; `STEP` removed |
| `T22` | `SIGMA_D22` | `sum_i A_i * P_i` | the tying map made injective |
| `T32` | `SIGMA_D32` | `(sum_i P_i) * (sum_i A_i)` | the combining operation of one bank changed from `MUL` to `ADD` |
| `T34` | `SIGMA_D34` | `-(sum_i A_i * P_i)` | the response supplied directly instead of searched over `Y` |

**Applicability of every twin.** The predicate the twin moves must actually
flip in the recovered program. A twin that recovers the same construct as its
target **fails the run**. This is the same rule the hostiles obey.

### 5.3 Slice rule, frozen here

Row index `0..47`. `index mod 4 in {0,1}` is the **search** slice (24 rows),
the only rows the structural search may read. `index mod 4 == 2` is the
**held-out** slice (12 rows), never read before the recovered program is fixed.
`index mod 4 == 3` is the **regeneration** slice (12 rows), used only by `R09`.
The three are disjoint by construction and a test asserts it.

## 6. What the search is, and what it is not

The search is **form recovery under exact agreement**, not parameter
estimation. The ecology supplies the parameter channels; the task is to
identify the functional form. A program *matches* a slice when its output
equals the response **exactly**, in `Fraction` arithmetic, on every row of that
slice. Enumeration proceeds in ascending charged cost; the recovered program is
the cheapest match, ties broken by the registered rendering order.

**What this does not license.** Parameter estimation, fitting, statistical
inference, real provenance, real scale, any statement about data outside the
Section-5 stream, transport of these certificates to another scope,
independent-team replication, maturity `M5`, `EV4`/`EV5`, the aggregate
Section-H rows, or any other named-family row. Intra-package agreement between
two routes is not independent replication.

## 7. The invertible composition of `SIGMA_D32`, derived not searched

Registered elementary map on `Q^2`, step `i` with parameters `(s_i, c_i)`,
`s_i != 0`:

```
z1' = s_i * z1
z2' = z2 + c_i * STEP(z1')
```

Claims to be derived exactly, over the probe set, with no float:

1. Each step is a bijection of `Q^2`, with inverse `z1 = z1'/s_i`,
   `z2 = z2' - c_i * STEP(z1')`.
2. The composition of the twelve steps is a bijection; a round trip returns
   every probe point unchanged.
3. The Jacobian determinant of the composition is `prod_i s_i`, independent of
   the point, and is exactly the response functional of `SIGMA_D32`'s first
   bank. The volume accumulator is therefore a `MUL`-combining fold, which is
   the construct `COMBINER` supplies. No logarithm is taken anywhere.

## 8. Frozen predictions, with falsifiers, before any outcome exists

`R01` is discharged by the `a`-predictions, read off the ecology specification
alone. `R08` is discharged by the `c`-predictions **and** by the
discriminativeness test of Section 8.6.

For each scope both the **class name** and the **tree predicates** are frozen,
so that a name mismatch is adjudicated against the predicates rather than
being a blind failure.

### 8.1 `SIGMA_D17`
- `a` Recovered class `NORMALISED_RATIO`. Predicates: `r = 2` true; head
  depends on `S1` and on `S2` true; head affine in `S2` false; `kind = NONE`;
  every combining operation `ADD`.
- `b` No program of the `G_S` stratum (`r = 1`, `L = 1`, `tau` injective,
  `kind = NONE`, head over `G_S` leaves) matches the search slice, at any cost
  up to `B_MAX`.
- `c` Recovered charged cost `9`. The recovered program matches the held-out
  slice exactly.
- `d` Twin `T17` recovers a program with `r = 1`.

### 8.2 `SIGMA_D20`
- `a` Recovered class `LAYERED_NONLINEAR`. Predicates: `L = 2` true; `BODY2`
  affine in `U` false; `r = 1`.
- `b` No `G_S`-stratum program matches the search slice at any cost up to
  `B_MAX`.
- `c` Recovered charged cost `9`. Held-out exact match.
- `d` Twin `T20` recovers a program whose `BODY2` is affine in `U`
  (class `LAYERED_AFFINE`).

### 8.3 `SIGMA_D22`
- `a` Recovered class `TIED_PARAMETER`. Predicates: `tau_p` not injective,
  `p = 3`; `r = 1`; `L = 1`; `kind = NONE`.
- `b` No `G_S`-stratum program matches the search slice at any cost up to
  `B_MAX`.
- `c` Recovered charged cost `5`. Held-out exact match.
- `d` Twin `T22` recovers a program with `tau` injective.

### 8.4 `SIGMA_D32`
- `a` Recovered class `MULTIPLICATIVE_ACCUMULATION`. Predicates: exactly one
  bank has combining operation `MUL` and one has `ADD`; `r = 2`; head depends
  on `S1` and `S2`.
- `b` No `G_S`-stratum program matches the search slice at any cost up to
  `B_MAX`.
- `c` Recovered charged cost `6`. Held-out exact match.
- `d` Twin `T32` recovers a program in which no bank combines with `MUL`.

### 8.5 `SIGMA_D34`
- `a` Recovered class `RESPONSE_SPACE_SEARCH`. Predicates: `kind = ARGMIN`;
  head depends on `RESP` true; `r = 1`.
- `b` No `G_S`-stratum program matches the search slice at any cost up to
  `B_MAX`.
- `c` Recovered charged cost `8`. Held-out exact match.
- `d` Twin `T34` recovers a program with `kind = NONE`.

### 8.6 The null, and why it is not the vacuous one

A response-permutation null is **vacuous under an exact-agreement criterion**:
permuting the response makes the target exactly unmatchable, so "0 of 200
recover the target class" would be true by construction. That is the mirror of
the 98-of-200 coin flip a parent package shipped, and it is registered here as
refused.

The null used instead is a **base rate over the grammar itself**. For each
scope, over the whole well-formed enumeration up to the recovered cost, report
the exact integer count of programs in each structural class and the exact
count of programs that match the search slice.

- *Applicability.* The base-rate count of the recovered class must be `> 0` in
  the enumeration — a null that cannot produce the class tests nothing and
  **fails the run**. The recovered class must additionally not be the modal
  class of the enumeration at that cost, or the recovery is reported as
  `BASE_RATE_DOMINATED` and the scope's `R04` is `NOT_EARNED`.
- *The prediction.* At every scope, the exact-match count is at most `4`, and
  the base rate of the recovered class is strictly below `1/2`.

### 8.7 `R08` discriminativeness, tested not assumed

Count the programs that match the **search** slice but fail the **held-out**
slice. If that count is `0` the held-out slice discriminates nothing and
`R08` is reported `NOT_EARNED` at every scope, with the count as the reason.
The count is reported exactly whichever way it falls. No coordinate is claimed
because it was convenient.

### 8.8 Cross-scope prediction

`P00` One and the same `G_H`, unchanged between scopes — enumeration digest
identical before and after all searches, all twins, all nulls and all hostiles
— produces all five recoveries. No ecology receives a grammar extension, an
extra operation, an extra leaf, or a hand-supplied candidate.

**A prediction that fails is reported as failed and earns no coordinate.**

## 9. Coordinates: what is targeted and what is refused

| id | requirement | targeted here |
|---|---|---|
| `R01` | property prediction from specification/ecology | yes, Section 8 `a` |
| `R02` | `P3`/`P4` grammar | yes, Section 4 with exact raw and quotiented counts |
| `R03` | no family macros | yes, Section 10 audit |
| `R04` | neutral recovery | yes, Section 6 with the Section 8.6 base rate |
| `R05` | matched negative control | yes, Section 5.2 with applicability |
| `R06` | lower bound where possible | yes, minimality within the enumerated set at `B_MAX`, plus the five `G_S` non-representability exhaustions |
| `R07` | resource crossover | yes, Section 4.7 cost model, exact crossovers |
| `R08` | held-out frozen prediction | conditional on Section 8.7 |
| `R09` | independent regeneration | yes, regeneration slice |
| `R10` | independent search | yes, source-separated oracle |
| `R11` | real-scale test | **NOT EARNED, NOT ATTEMPTED, NOT ASSERTED** |

`R11` is refused because this scope has no real provenance, no fitted rows, and
no scale coordinate: it is a derivational scope. Therefore **no row of Section
H closes here**, and the eleven-coordinate conjunction is not available. Adding
this package's coordinates to a parent's is `CROSS_SCOPE_GATE_COMPOSITION` and
is forbidden.

## 10. Hostiles, each with its applicability condition

The run **fails** if a hostile is vacuous — if the quantity it perturbs does
not move. Twelve are registered.

| id | perturbation | must be detected | applicability condition |
|---|---|---|---|
| `HX01` | a macro operation named for a family is added to the grammar | macro audit fires | audit is clean on the true grammar |
| `HX02` | a family label is handed to the classifier | classifier raises | classifier accepts trees and flags only |
| `HX03` | the grammar digest input is perturbed | digest changes | digest is stable across a no-op rebuild |
| `HX04` | a held-out row is placed in the search slice | disjointness check fires | true slices are disjoint |
| `HX05` | a certificate is stamped with a foreign `sigma` | foreign-sigma check fires | true certificates pass |
| `HX06` | a float is written into a claimed quantity | float scan fires | the true result has zero floats |
| `HX07` | the `ARGMIN` tie-break is changed to the largest `y` | `SIGMA_D34` recovery breaks | at least one pinned tie row is in each of the search and held-out slices |
| `HX08` | `tau_3` is replaced by `tau_4` | `SIGMA_D22` match breaks | the ecology distinguishes `p = 3` from `p = 4` |
| `HX09` | the `MUL` combining operation is replaced by `ADD` | `SIGMA_D32` match breaks | the two combiners give different fold values on the slice |
| `HX10` | one ecology row value is perturbed | recovery or held-out match changes | the perturbed row is in a read slice |
| `HX11` | a parent gate certificate is offered to a row ledger | rejected | the ledger accepts this package's own certificates |
| `HX12` | the `G_S` stratum is extended with `COFOLD` and the `SIGMA_D17` non-representability exhaustion is re-run | the exhaustion now finds a match | the unextended exhaustion found none |

`HX12` exists because an exhaustion that finds nothing proves nothing unless it
can be made to find something.

**No-alarm case.** The true run raises no hostile. A test asserts it.

## 11. Two routes

Route A is the executor. Route B is a source-separated oracle that re-derives
every recovered program, every non-representability verdict, every crossover
and every held-out check **by a materially different enumeration scheme** —
generate-and-parse over a string grammar rather than tree tiers, with its own
independent recomputation of every ecology response in closed form. Non-import
is enforced structurally by an `ast` scan of the oracle's imports and by a
`sys.modules` assertion, not by a comment. A renamed copy of route A is
single-route and is refused.

## 12. Arithmetic rule

Every reported quantity is an `int` or a `fractions.Fraction`. **No float
appears anywhere in this package**, including inside any helper: there is no
fitting routine, so there is no rationalisation step and no float tolerance. A
scan asserts the absence of float literals in the claimed-quantity path and of
`float` in the result artifacts.

## 13. Claim ceiling

```
DERIVATIONAL_CONSTRUCT_CERTIFICATE_AT_SIGMA_D17_D20_D22_D32_D34__NO_ROW_CLOSED
```

Allowed terminal for a scope all of whose Section-8 predictions held: *the
named missing construct exists, is generic, is recovered family-blind at that
scope, and the family's functional is not in the image of `G_S` at the
registered budget on the registered slice.* Nothing about real systems,
nothing about scale, nothing about the historical family the row names beyond
that functional.

Forbidden promotions, asserted in `MANIFEST_V1.json`:

```
CROSS_SCOPE_GATE_COMPOSITION
REAL_SCALE_CLAIM
INDEPENDENT_TEAM_REPLICATION
MATURITY_M5
EV4_OR_EV5
SECTION_H_ROW_CLOSURE
AGGREGATE_SECTION_H_ROW
PARAMETER_ESTIMATION_CLAIM
UNIVERSAL_NON_REPRESENTABILITY
FRONTIER_MODEL_CLAIM
```

`UNIVERSAL_NON_REPRESENTABILITY` is listed because the `R06` results are
exhaustions at `B_MAX = 10` over `G_S`'s registered leaves and budgets. They
are not statements about all programs, all budgets, or all grammars, and must
never be restated as such.
