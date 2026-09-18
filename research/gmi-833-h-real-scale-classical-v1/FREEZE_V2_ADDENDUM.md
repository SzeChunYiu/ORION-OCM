# Revival addendum V2 — registered before the V2 run, after the V1 outcomes

The V1 pass ran to completion at all four scopes. Its receipts are committed
unchanged in `REAL_RUNS_V1/` and are not edited, hidden or re-labelled. Three of
the four structural predictions of `FREEZE_V1.md` Section 8 **failed**. This
addendum records the single-stage attribution for each failure, the matching
lever, and a **new** frozen prediction set to be resolved on **new** held-out
rows. It is committed before any V2 executor is run.

## 1. V1 outcomes, verbatim

| scope | predicted class | recovered class | verdict |
|---|---|---|---|
| `SIGMA_H01` | `PERSISTENT_STATE` | `AFFINE_SCORE` (`MUL(ARG,PARAM) \| S`) | **P01a failed** |
| `SIGMA_H02` | `AFFINE_SCORE` | `PERSISTENT_STATE` (`MUL(ARG,PARAM) \| ADD(S,STATE)`) | **P02a failed** |
| `SIGMA_H03` | `NONLINEAR_LINK` | `AFFINE_SCORE` (`MUL(ARG,PARAM) \| ADD(BIAS,S)`) | **P03a failed** |
| `SIGMA_H04` | `LIFTED_BASIS` | `LIFTED_BASIS` (`ABS(ARG) \| MUL(BIAS,S)`) | P04a held |

`route_b_agrees` was false at three scopes.

The V1 receipts as they stand are in `REAL_RUNS_V1/`. Two of the four scope
files are complete (`SIGMA_H02`, `SIGMA_H03`). `SIGMA_H04`'s V1 process was
killed by the operating system while materialising the degree-two design matrix
(560 features x 294,818 rows) on a host with roughly 4 GB free, and `SIGMA_H01`'s
V1 process was stopped by hand during its remint stage to free that host for the
V2 pass. Their decisive outcomes — winner expression, recovered class, held-out
and contiguous-tail numbers, remint agreement — are in the committed V1 logs
`REAL_RUNS_V1/logs_v1/` and are quoted verbatim in the table above. Nothing is
omitted, re-labelled or re-run to a different answer. The V2 executor makes the
landmark and degree-two designs blockwise and the exact evaluation streaming so
that neither stage materialises a slice-sized array again.

## 2. Attribution — one stage per failure

**`SIGMA_H01`: the head node budget.** A `G_R` expression containing three
distinct leaves needs `2n - 1 = 5` nodes. `FREEZE_V1.md` Section 5 capped `HEAD`
at 4. Therefore **no expression in the V1 head space uses `S`, `STATE` and
`BIAS` together**, and no parameterised state update — no leaky accumulator, no
decayed register, no counter with forgetting — exists in the grammar at all. The
only stateful heads available were unparameterised ones such as
`ADD(S,STEP(STATE))`. The budget structurally excluded the very class the row is
about. This is a representational restriction of the frozen grammar, exactly the
same kind of defect as the screen restriction already recorded in
`FREEZE_V1_SEARCH_AMENDMENT.md`. It is not a statement about the ecology or the
data.

**`SIGMA_H02` and `SIGMA_H04`: the ecology's presentation order.**
`E_H02` and `E_H04` present consecutive overlapping windows of one audio stream
in time order. A delay cell therefore has real temporal autocorrelation to
exploit, and at `SIGMA_H02` the search correctly preferred
`ADD(S,STATE)` — an integrator, i.e. an infinite-impulse-response linear filter.
That is a true fact about the ecology and a defect in the ecology: a row about
**regression** presupposes exchangeable observations, and a time-ordered
sliding-window presentation does not supply them. The failure is in the ecology
stage, not in the grammar, the loss, the fit or the evaluation.

**`SIGMA_H03`: the search loss.** The V1 executor searched under squared error.
Squared error **is** the identity-link criterion; minimising it can never
express a preference for a link function, so a link can never be recovered under
it. `FREEZE_V1_ECOLOGY_ADDENDUM.md` A3 had already frozen that scope's protected
interface as *closeness* — an absolute criterion — and the executor did not use
it. This is a conformance defect between the executor and the already-frozen
interface, in the loss stage alone.

**All four scopes: route B.** Route B used a weaker optimiser (random multistart
only) than route A (least squares plus coordinate descent), so a disagreement
measured optimiser strength rather than implementation independence.

## 3. Levers — one per attribution, applied uniformly and blind

- **L1** The three non-sequential ecologies `E_H02`, `E_H03`, `E_H04` are
  presented under one registered target-independent permutation
  (`grammar`-free, `run_real_scale_v2.py::registered_order`, Knuth
  multiplicative hash `2654435761`), applied **within** the first-80% region and
  **within** the contiguous-tail region separately so that the tail stays
  temporally disjoint from the fit region. Row contents, responses, index sets
  and slice sizes are unchanged; only presentation order changes, and order
  carries no information about the response. `E_H01` is **not** permuted: its
  row is about sequence.
- **L2** The search loss at each scope is that scope's already-frozen protected
  interface: decision count at `SIGMA_H01`, squared error at `SIGMA_H02` and
  `SIGMA_H04`, absolute closeness at `SIGMA_H03`.
- **L3** `HEAD_MAX_NODES` is raised from 4 to 5 at **all four scopes**, with a
  target-independent quotient keeping the heads whose denotation depends on `S`
  plus one canonical `S`-independent representative (`C0`). Head space: 8,155
  raw expressions, 712 denotation classes, 370 `S`-dependent, of which 138 read
  `STATE`. `ADD(S,MUL(STATE,BIAS))` is confirmed present. Candidate pairs rise
  from 6,324 to 12,614. Defined in `grammar_v2.py`; digest
  `digest_v2()` chains the V1 grammar digest.
- **L4** Route B is given its own least-squares path (central differences at
  step 2, solved by QR) so independence is tested on implementation. Agreement
  is recorded on the **recovered structural class**, which is what `R04` needs,
  with the stricter expression-level agreement reported alongside.

None of these is a per-scope constant, a family name, a target-specific
candidate, or a threshold change. No claim ceiling, forbidden promotion,
real-scale definition, threshold, cost model, comparison arm or falsifier is
relaxed.

## 4. New slices — the V2 predictions are resolved on rows V1 never evaluated

The slice residues **rotate**. For V2: `search = (position mod 5 == 1)`,
`held = (position mod 5 == 2)`, `fit = the remaining positions below the tail
start`, `remint_fit = (position mod 5 == 0)`,
`remint_held = (position mod 5 == 3)`, contiguous tail unchanged. V1 searched on
`mod 5 == 3` and evaluated on `mod 5 == 4`; **the V2 held-out set is disjoint
from both.** No V2 arm is fitted on any V2 held-out row.

## 5. New frozen predictions, with falsifiers

- `Q01a` at `SIGMA_H01` the blind search selects a head that reads `STATE`
  (`PERSISTENT_STATE`).
- `Q01b` on the symbol-permuted twin the search selects a head that does not.
- `Q01c` on the V2 held-out slice and on the contiguous tail the selected
  stateful program's exact decision-error count is strictly lower than the
  selected stateless program's.
- `Q01d` in 200 order-randomised controls the stateful program is not strictly
  better in any.
- `Q02a` at `SIGMA_H02` the search selects `AFFINE_SCORE` with
  `body_is_arg_times_param`, head affine in `S`, no `STATE` read.
- `Q02b` the `E_H04` twin does not select `AFFINE_SCORE`.
- `Q02c` held-out and tail exact squared error beat the best constant arm, and
  the exact sign-decision error count beats the majority-sign arm.
- `Q02d` in 200 row-permuted design controls none beats the constant arm.
- `Q02e` the exact table crossover `m*` exists and is the smallest.
- `Q03a` at `SIGMA_H03` the search selects `NONLINEAR_LINK`.
- `Q03b` the log-link arm is strictly closer than the identity-link arm on
  strictly more than half of the V2 held-out rows.
- `Q03c` the identity-link arm emits at least one negative predicted mean on the
  V2 held-out slice and the log-link arm emits none.
- `Q03d` the `E_H02` twin does not select `NONLINEAR_LINK`.
- `Q04a` at `SIGMA_H04` the search selects `LIFTED_BASIS`.
- `Q04b` held-out and tail exact squared error beat the affine arm on the same
  design.
- `Q04c` an exact landmark count `q*` exists whose charged cost exceeds the
  affine arm's while its held-out exact squared error is still lower.
- `Q04d` the `E_H02` twin does not select `LIFTED_BASIS`.
- `Q00` one unchanged `grammar_v2` digest across all four scopes.

**This is the only revival pass.** A `Q*a` that fails again is reported as a
failed row with its attribution, and that row is left open. No third pass, no
further lever, no narrowing of any row's stated meaning.
