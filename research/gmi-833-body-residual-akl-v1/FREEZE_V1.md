# FREEZE_V1 — `gmi-833-body-residual-akl-v1`

Committed and pushed **before any implementation, executor, test, scanner,
census, receipt or measurement of this package exists**. `git log --reverse`
over this directory must return this commit first, carrying only `FREEZE_V1.md`
and `FREEZE_ROWS_V1.json`. `check_freeze_order_v1.py` re-derives that from the
repository in CI, with a negative control so a path typo cannot make it
vacuously green (the #976 `POST_HOC_SUSPECT` failure class).

- **`source_main`** = `5e57d4292266bccf435136e1f7d72caa32e920a0`
  (`ci(#833): freeze-order gates must survive their own publication (#1032)`).
- **Claim ceiling** =
  `GMI_833_BODY_RESIDUAL_AKL_DISPOSITION_AT_REGISTERED_FINITE_SCOPE`.
- **Issue body fetch** pinned in `FREEZE_ROWS_V1.json` by sha256
  `d5cd0248ea2f7121d6ad52b0e0a07e832969134add95681ca36c1a6a85261fbd`
  (27,554 bytes).

## 1. The exact rows this tranche may reconcile

Three, and only three. Their verbatim text, anchors and per-row sha256 are
pinned in `FREEZE_ROWS_V1.json` and are not restated here, because one of them
contains a term the repo-wide terminology gate blocks in markdown:

| id | anchor | `old_sha256` |
|---|---|---|
| `ROW_A` | `# A. Scientific constitution and claim discipline` | `3d4f2380704b36e2…` |
| `ROW_K` | `# K. Capability theory upgrade` | `5d5fab932657bef2…` |
| `ROW_L` | `# L. Development, morphogenesis, and evolvability` | `1b2c04dda31bc3c0…` |

**No neighboring row is earned here.** In particular the three open rows of
section M (`ROW_M1`, `ROW_M2`, `ROW_M3` in `FREEZE_ROWS_V1.json`) are owned by
issue #926 and PR #927; #927 is a **draft**, which is that lane's explicit
not-ready signal. This package does not close them, does not cite #927's
evidence, and does not touch its files. No row outside sections A, K and L is
in scope at all.

This package **never edits the issue body**. Its only issue-facing artifact is
`ISSUE_833_RECONCILIATION_BODY_RESIDUAL_V1.json`.

## 2. Pre-registered dispositions and decision rules

The point of registering these before implementation is that each row's
**closure test is fixed now**, so a result cannot be re-read into a closure
afterwards. For each row the rule is stated as a biconditional, and the
expectation of this lane is recorded beside it.

### 2.1 `ROW_A` — governing verb `Replace`

The row is a **corpus-mutating** row over one named audited term, written
`ROW_A_TERM` throughout this package and stored verbatim only in JSON
(`FREEZE_ROWS_V1.json`, `RESULT_V1.json`), never in markdown, so that this
package does not itself add sites to the debt it measures.

Three scopes are registered now, and all three will be reported:

- `S1` — every `*.md` and `*.tex` file tracked at `source_main`, repo-wide.
- `S2` — every `*.md` under `research/`, repo-wide.
- `S3` — the **flagship** set of `ABH-2`: every `*.md` under `research/` plus
  repo-root `*.md`, **minus** the four declared authority/migration packages
  `gmi-833-tranche-ab-ac-lit`, `gmi-833-ab-terminology-harness-v1`,
  `gmi-833-terminology-migration-v1`, `gmi-833-checklist-mirror-v1`, and minus
  this package. `S3` is the governing scope.

**Decision rule.** `ROW_A` closes **iff** the `S3` residual is `0`.
Rationale for the exclusion: the row's own clause *preserving exact legacy
mappings* makes the crosswalk's occurrences of the audited term **required to
remain**. Counting them would be a false positive, and a checker that cries
wolf on its first real run gets switched off.

**Registered expectation:** the `S3` residual is not `0`, so the row does not
close. If the measurement contradicts this, the measurement wins.

**What is additionally measured, and why it is not a closure argument.**
`RA-3` counts how many residual-bearing files are pinned by content hash in at
least one frozen manifest or ledger elsewhere in the repository. This is
evidence about *who can repair the residual*, not about whether it exists. It
is forbidden from being read as a reason the row is closed, complete, or
unowned.

**Phrase scope, stated now rather than discovered later.** The row says
*paper-facing theory*. This repository has no `papers/` directory and no
artifact defines that phrase. This package **does not invent a definition**; it
reports under `S1`, `S2`, `S3` and says the phrase is undefined. Narrowing the
row to a self-chosen subset would be closing a row by narrowing its meaning.

### 2.2 `ROW_K` — attack the bridge, not the predictor

Parents: `gmi-833-capability-predictor-v1` (#1012, owns `F`) and
`gmi-833-capability-predictor-evaluation-v1` (owns `KE-1`…`KE-7`, `KE-3`,
`KE-3D` and the three real populations `SIGMA_REAL`, `SIGMA_REAL2`,
`SIGMA_REAL3`). **`F` is not modified, re-derived or re-fitted here.** No
training is performed here and no receipt under `REAL_RUNS*/` is read as an
input to any registration decision.

`FREEZE_V3_ADDENDUM.md` §6 of the parent pre-registered, before the V3 outcomes
existed, that a **fourth registration law fitted to the V1/V2/V3
counterexamples is tuning to outcomes**. That terminal is honoured: this
package proposes **no fourth law**. The object under test is instead the
*bridge itself*, treated as a set-valued map.

**Definitions, registered now.**

- A **bridge** `B` assigns to each registered machine `m` a non-empty set
  `B(m)` of admissible solved-bit values. The induced world set is the product
  over machines. `B` is **truthful by construction** on a population iff, for
  every machine, every outcome the training protocol can produce lies in
  `B(m)` — which requires `B` to assert nothing it has not proven.
- The **maximally conservative** bridge `CB-MAX` takes `B(m)` = all 8 values.
- The **protocol-conservative** bridge `CB-PROTO` additionally excludes a
  solved bit for a head the protocol leaves untrained. `CB-PROTO(m)` is a
  subset of `CB-MAX(m)`, so `CB-PROTO` yields a **weakly larger** census; it is
  registered as the lane's most favourable conservative bridge and is the one
  the decision rule is evaluated on.
- An emission is **world-invariant** at an input iff `F` emits a point there
  for every world in the induced product, and the point is the same value.
- An emission is **non-degenerate** iff its value is a strictly positive
  rational. `0` and `UNSATISFIED` are degenerate — the parent's own standard,
  which is how the parent found its `FREEZE_V4` power defect.
- The **resolution curve** `N(k)` is the non-degenerate world-invariant census
  when the first `k` machines of the registered rank order are collapsed to the
  parent's V3 fitted law and the remaining `32 - k` keep `CB-PROTO`.

**Decision rule.** `ROW_K` closes **iff** the `CB-PROTO` census
`N(0)` is at least 1 non-degenerate world-invariant point emission on at least
one of `SIGMA_REAL`, `SIGMA_REAL2`, `SIGMA_REAL3`.

- `N(0) >= 1` → the row closes on a bridge whose truthfulness is a theorem
  rather than a measured fraction, and `FREEZE_V2` of this package will be
  authored to register the prospective real-system test before it is run.
- `N(0) = 0` → the row **stays open**, and the census plus the resolution curve
  is the evidence. The obstruction is then reported as **structural at this
  scope** and earned by proof, not as "not attempted".

**Registered expectation:** `N(0) = 0`, and `N(k) = 0` for every `k < 32`
under contract `E_full`. If either is contradicted, the measurement wins.

**`BR-3`, registered now.** `KE-3` (`F` wrong on 0 of 161,632 pairs) is
conditioned on *truthfully-registered* worlds. Registration truthfulness held
on `19 + 28 + 26 = 73` of `3 x 32 = 96` real systems, and membership in the
conditioning event is decided **by the measured outcome**. A statistic
conditioned on an outcome-selected event is not a test of the predictor on real
trained systems. `BR-3` states exactly this and **claims no defect in `F`**:
`F`'s soundness on the worlds it was given is not in question here.

### 2.3 `ROW_L` — futurity is custody

Parents: `gmi-833-real-developmental-validation-v1` (which recorded the row as
open because "futurity cannot be manufactured in-session") and
`gmi-833-developmental-reuse-v1`.

**Criterion `FFA-1`**, registered now. A candidate task family `C` is an
admissible genuinely-future family for a frozen prediction `P` iff **all four**
hold:

1. **Dated.** `C` has a publication or authorship timestamp `T(C)` that is
   verifiable from the artifact itself or from an attestation independent of
   this programme.
2. **Posterior.** `T(C)` is strictly later than the committer timestamp of the
   commit that froze `P`.
3. **Exogenous.** `C` was not authored, generated, parameterized or selected by
   this programme, and is not reachable as a blob in this repository at the
   freeze commit.
4. **Independently attested.** The evidence for clauses 1 and 2 does not
   originate from an artifact this programme controls.

**Decision rule.** `ROW_L` closes **iff** at least one candidate family passes
all four clauses of `FFA-1` and an evolvability prediction frozen before `T(C)`
is then scored against it.

**Registered expectation:** every candidate reachable in this session fails
clause 2 or clause 3, so the count of admissible candidates is `0` and the row
stays open. **Redefining "future" to mean "out-of-sample" is forbidden** — an
out-of-sample family this lane authors or pins from a repo blob is past, and
`FFA-1` clause 3 exists precisely to refuse it.

The checker must be validated in both directions before any verdict is
reported: **recall** on a planted candidate that genuinely satisfies all four
clauses, and the **no-alarm** case on candidates that genuinely fail. A
criterion that admits nothing is worthless unless it is shown to admit
something.

## 3. Named results this package may assert

`RA-1`, `RA-2`, `RA-3` (row A); `BR-1`, `BR-2`, `BR-3` (row K); `FC-1`, `FC-2`
(row L). Each will carry scope, quantifiers, assumptions, falsifiers, strongest
parents and forbidden extrapolations in
`BODY_RESIDUAL_AKL_THEOREMS_V1.md`. No other identifier may appear in the
receipt.

- `RA-1` residual counts under `S1`/`S2`/`S3`, exact integers.
- `RA-2` the required-to-remain count inside the excluded authority packages.
- `RA-3` how many residual-bearing files are content-hash pinned elsewhere.
- `BR-1` the **bridge dichotomy**: on these populations a non-degenerate
  world-invariant point emission requires the bridge to resolve the solved-set
  of every surviving admissible machine exactly — there is no partially
  conservative middle ground.
- `BR-2` the measured census `N(0)` and the resolution curve `N(k)`.
- `BR-3` the conditioning statement above.
- `FC-1` the criterion `FFA-1` and its two-directional validation.
- `FC-2` the measured count of admissible candidates reachable in-session.

## 4. Falsifiers

- `RA-1`: a residual-bearing file inside `S3` that the scanner reports clean; a
  file outside `S3`'s stated definition counted inside it; a count that differs
  between the two routes.
- `RA-2`: an occurrence counted as required-to-remain that lies outside the four
  declared authority/migration packages.
- `RA-3`: a file reported as pinned whose claimed pinning manifest does not
  contain its hash; a file reported unpinned that a manifest does pin.
- `BR-1`: an input, a population and a bridge strictly coarser than full
  resolution at which `F` emits a non-degenerate world-invariant point.
- `BR-2`: any disagreement between the structural route and the black-box route
  on any input; a census of `0` on a bridge for which the positive control also
  returns `0` (which would prove the counter cannot count).
- `BR-3`: a demonstration that the conditioning event is decided without
  reference to the measured outcome.
- `FC-1`: a planted admissible candidate the checker rejects; a candidate that
  fails a clause and is admitted.
- `FC-2`: any in-session candidate that passes all four clauses (which would
  close the row).

## 5. Two routes, hostiles, nulls

Every computational claim is carried by **two materially independent routes**.
Route B (`oracle_route_b_v1.py`) imports nothing from this package's executor.

- Row A, route A: the parent gate's compiled pattern, applied over the registered
  scopes. Route B: an independently written line scanner with its own tokenizer
  that never imports the parent gate.
- Row K, route A: the structural characterization — the survivor set is
  world-independent, so the admissible image is computed directly from the
  bridge. Route B: black-box — install concrete worlds on the registration
  surface, run `F` end to end, and require the observed emissions to be
  consistent with route A's per-input admissible image on every input.
- Row L, route A: the criterion evaluated clause by clause. Route B: an
  independently written evaluator over the same candidate list.

**Hostiles.** Each must be shown to actually move the quantity it perturbs; a
hostile that cannot move its own quantity is a test of nothing, and this
programme has been bitten by that twice. Registered now:

| id | planted defect | quantity it must move |
|---|---|---|
| `HA1` | drop the plural branch from the scanner pattern | `S3` residual falls |
| `HA2` | silently drop a package from the `S3` walk | `S3` file census falls |
| `HA3` | claim a residual-bearing file is clean | route disagreement appears |
| `HA4` | assert a hash pin that no manifest contains | `RA-3` verifier refuses |
| `HB1` | collapse the bridge to the parent's V3 fitted law (**positive control**) | census must rise far above `0` |
| `HB2` | widen the bridge to every world including untrained heads | census must not rise |
| `HB3` | count `0` and `UNSATISFIED` as non-degenerate | census must rise |
| `HB4` | perturb one machine's admissible set away from truthfulness | route-B consistency check must fail |
| `HC1` | a candidate dated after the freeze but authored in-session | clause 3 must reject |
| `HC2` | a candidate with an unattested date | clause 4 must reject |

**Nulls.** Row A: a control term absent from the corpus must score `0`, and a
control term that must match (a common English word) must score far above `0`,
so a `0` is never read off a broken scanner. Row K: `NULL_UNIFORM`, a bridge
drawn uniformly at random per machine, over 200 seeds — the true `CB-PROTO`
census must be greater than or equal to every randomized census, and the
positive control `HB1` must beat both. Row L: a randomized candidate list must
be admitted at rate `0`.

## 6. Forbidden promotions

`ROW_A_CLOSED_BY_MEASUREMENT`, `TERMINOLOGY_MIGRATION_COMPLETE`,
`RESIDUAL_IS_UNOWNED`, `PAPER_FACING_SCOPE_DEFINED_HERE`,
`PREDICTOR_TESTED_ON_REAL_TRAINED_SYSTEMS`, `F_IS_DEFECTIVE`,
`KE_3_INVALIDATED`, `FOURTH_REGISTRATION_LAW`, `BRIDGE_REPAIRED`,
`CAPABILITY_PREDICTION_IMPOSSIBLE_IN_GENERAL`,
`FUTURE_TASK_FAMILY_CONSTRUCTED`, `EVOLVABILITY_PREDICTED_PROSPECTIVELY`,
`OUT_OF_SAMPLE_EQUALS_FUTURE`, `SECTION_A_COMPLETE`, `SECTION_K_COMPLETE`,
`SECTION_L_COMPLETE`, `SECTION_M_ANY_ROW_EARNED`, `PR_927_EVIDENCE_CITED`,
`CHECKLIST_CLOSURE_IMPLIES_COMPLETENESS`.

## 7. What is not claimed

Nothing here is a claim about whether any GMI theorem is true. Nothing here
re-derives, re-fits or repairs `F`, the registration law, the crosswalk, the
banned-term list, or any evolvability result. Every parent owns its own result
and is cited as owner in `PARENT_OWNERSHIP_V1.md`; the residual contribution of
this tranche is the **disposition** of three rows under rules fixed in advance,
and the exact evidence that supports each disposition.
