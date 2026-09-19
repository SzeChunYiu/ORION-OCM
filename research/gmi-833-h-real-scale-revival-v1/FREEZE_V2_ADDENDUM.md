# V2 addendum to FREEZE_V1.md — the revival set, committed before the re-test

`source_main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`.
First-run receipts being diagnosed: `REAL_RUNS_V1/`, committed in
`research(#833): executor, oracle, tests and the first real-scale run`.

`FREEZE_V1.md` section 8 says, in advance, what happens when a registered
prediction fails: the row is diagnosed to a **single stage**, **one** revival
with the matching lever is attempted, and the revival is re-tested against a
**newly frozen prediction set recorded in a `FREEZE_V*_ADDENDUM.md` committed
before that re-test** — never against the set that revealed the problem. This
file is that record. It is committed before any V2 receipt exists and CI
asserts that order.

## 1. What the first run settled, and is not re-opened

At `SIGMA_R02` every registered prediction held and is **not re-frozen here**:

- `P2a` the family-blind search chose `MUL(ARG,PARAM) | ADD(BIAS,S)`, class
  `AFFINE_SCORE`;
- `P2c` held-out exact squared error 14,612,998 parts per billion of the best
  constant arm's, and 20,089 held-out decision errors against the majority-sign
  arm's 40,324, over 87,747 held-out rows;
- `P2d` all 200 response-permutation controls landed inside the registered
  applicability band — observed ratio range 0.99043 to 1.00658 of the constant
  arm — and 0 of 200 beat the chosen arm, which sits strictly below the band;
- `P2e` `m* = 5`, program total 29 against the tabulated alternative's 37, with
  24 against 20 at `m* - 1`;
- `P3b` `P3c` `P3e`, which concern the two fitted GLM arms and not the search:
  the log-link arm was strictly closer on 22,278 of 37,948 held-out rows and
  emitted 0 negative predicted means, against the identity-link arm's 15,670
  and 779, with 0 ties; the ecology's exact fit-slice variance-to-mean ratio is
  75.756 with minimum response 1 over 189,745 rows.

`P3b` is the criterion `gmi-833-h-real-scale-classical-v1` failed, carried over
unchanged, and it held. Nothing in this addendum touches it.

## 2. The two failures, each attributed to one stage

**`SIGMA_R03` — `P3a` failed; stage: the recovery criterion.**
The family-blind search chose `MUL(ARG,PARAM) | ADD(BIAS,S)`, class
`AFFINE_SCORE`, where `NONLINEAR_LINK` was registered. The search ranks by
squared error alone. On this ecology the affine score attains a lower squared
error than any non-affine head `G_S` offers — and it does so while emitting 779
negative predicted means on a response whose registered support is the positive
integers. The criterion never charges for leaving the response support, so it
cannot distinguish a link. That is the same fact the fitted arms report from the
other side: the link's advantage on a count response is admissibility. The
search was simply not told that admissibility is part of well-posedness.
The `R09` regeneration at this scope returned `NONLINEAR_LINK` while the main
search returned `AFFINE_SCORE`, which is the same defect showing as instability.

**`SIGMA_R04` — `P4a` failed; stage: the ecology-grammar interface.**
The family-blind search chose `MUL(ARG,PARAM) | ADD(BIAS,S)`, class
`AFFINE_SCORE`, where `LIFTED_BASIS` was registered. `F04`'s response counts
frames with `x_i >= 0`. The only per-input indicator `G_S` contains is
`STEP(a) = 1 if a > 0 else 0`, which is **strict**. `D2` is digital audio and
contains 65,023 exactly-zero frames out of 614,266, 10.585 per cent. The two
counts therefore differ on 119,860 of 614,233 rows, by 3.386 counts out of 32
on average and by as much as 32. The registered response was consequently not
additive in any per-input transform `G_S` can express, so the ecology did not
pose the question the row asks. This is a defect in the response this package
registered, not a finding about basis methods.

## 3. The two levers, one per failure, and nothing else

**Lever for `SIGMA_R03` — a generic support-admissibility rule.**
Each ecology's registered response support is part of its specification, which
`R01` already licenses the derivation to read. A candidate program is
**support-admissible** at a scope iff, on the **fit slice only**, it emits no
prediction on the forbidden side of a one-sided registered support. The
family-blind search ranks support-admissible candidates ahead of inadmissible
ones; within each group the order is unchanged — squared error, then node
count, then rendering. Both orderings are reported.

The rule is stated once and applied identically at all three scopes. Where the
registered support is two-sided it imposes nothing and is inert by
construction, which is the case at `SIGMA_R02`. It carries no family name, no
family identifier and no distributional assumption: it is the requirement that
a program's range lie inside the range the ecology declares.

**Lever for `SIGMA_R04` — align the response with the operator, not the
operator with the response.**
The new response at `SIGMA_R04B` counts strictly positive frames,
`#{ i in [t, t+31] : x_i > 0 }`. `G_S` is **not** modified: adding a
non-strict indicator would break `P00`, would tailor the grammar to the answer,
and would invalidate `SIGMA_R02`, whose result is already on the record.

## 4. The V2 scopes

| id | family row | ecology | change from V1 |
|---|---|---|---|
| `SIGMA_R02` | Linear regression / linear classifiers. | `F02` unchanged | none but the admissibility rule, which is inert here |
| `SIGMA_R03B` | GLMs. | `F03` unchanged | the search's ranking rule only |
| `SIGMA_R04B` | Basis/kernel methods. | `F04b`: response `#{ i in [t, t+31] : x_i > 0 }`; design `(x_{t+1}, ..., x_{t+32})` unchanged | the response only |

Data sources, digests, slice rule, grammar, classifier priority, arithmetic
rule, real-scale definition, claim ceiling and forbidden promotions are all
unchanged from `FREEZE_V1.md`.

## 5. The newly frozen predictions

**`SIGMA_R02`, re-run under the admissibility rule.**
- `Q2h` The rule is **inert** here: zero enumerated candidates are demoted, and
  the chosen program is `MUL(ARG,PARAM) | ADD(BIAS,S)`, byte-identical to the
  first run's. A different chosen program at this scope falsifies the claim that
  the rule is generic rather than fitted to one scope.
- `Q2a` `Q2c` `Q2d` `Q2e` are the V1 predictions, re-evaluated on the V2 run.

**`SIGMA_R03B`.**
- `Q3g` **The rule is non-vacuous here**, and this is checked before the class
  is read: at least one and not all of the enumerated candidates are demoted on
  the fit slice. Both counts are reported exactly. **If the rule demotes none,
  or demotes all, the run fails** — a filter that cannot separate tests nothing,
  exactly as a hostile that cannot fire tests nothing.
- `Q3a` The family-blind, support-admissible search chooses a `HEAD` that is
  not affine in `S` while `BODY` stays affine in `ARG`; the post-hoc class is
  `NONLINEAR_LINK`.
- `Q3i` The `R09` regeneration on the disjoint slices recovers the **same**
  class. A different class fails the gate, as it did in V1.
- `Q3b` `Q3c` `Q3e` carried over verbatim from `FREEZE_V1.md` section 8 and
  re-evaluated on the V2 run.
- `Q3d` On the `F02` control ecology the same search does not choose
  `NONLINEAR_LINK`.
- `Q3f` An exact index-set size `m*` exists and is reported.

**`SIGMA_R04B`.**
- `Q4a` The family-blind search chooses `LIFTED_BASIS`: `BODY` applies a
  non-affine transform to `ARG`.
- `Q4b` Held-out exact squared error of the lifted arm is strictly lower than
  that of the affine arm fitted on the same real design at the same scale.
- `Q4c` Held-out exact squared error of the lifted arm is strictly **positive**:
  one summand of the response is outside the design, so the response is not
  exactly attainable and the gate cannot be won by an identity.
- `Q4d` An exact landmark count `q*` exists at which the charged cost of the
  landmark arm first exceeds the compact lifted program's; `q*`, both costs and
  both held-out exact squared errors are reported.
- `Q4e` On the `F02` control ecology the search does not choose `LIFTED_BASIS`.
- `Q4f` The `R09` regeneration recovers the same class.

**Across scopes.** `Q00` The grammar digest is unchanged, and equal to the
digest the first run recorded. Any change to `G_S` between V1 and V2 voids
everything above.

## 6. The stopping rule, stated before the outcome

This is the **one** revival `FREEZE_V1.md` section 8 permits per failure. If
`Q3a` fails again, the GLM row is reported open with the second attribution and
is **not** attempted a third time in this package. If `Q4a` fails again, the
basis/kernel row is reported open the same way. A prediction that fails is
reported as failed and closes no row, and neither `RESULT_V1.json` nor
`ISSUE_833_RECONCILIATION_H2_V1.json` may carry a closure for a row whose
prediction failed.

`ECOLOGY_ITERATION_UNTIL_POSITIVE` and `POST_HOC_FALSIFIER_REPLACEMENT` remain
in `forbidden_promotions`, and the `REAL_RUNS_V1/` receipts stay committed so
that the first outcome cannot be quietly replaced by the second.
