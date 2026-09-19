# FREEZE — `gmi-833-aa-registered-fallacy-detectors-v1` (issue #833, section AA)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, oracle,
test, receipt, theorem note, hand-check or workflow file of this package
exists. `git log --reverse -- research/gmi-833-aa-registered-fallacy-detectors-v1/`
must show this file, alone, first.

## 1. Source pin

- `source_main` = `116d972f45c7b996546df201a5e5edb2438d915b` (origin/main tip at freeze time, 2026-09-19).
- Parent register under instrumentation: branch `research/833-revive-census`
  at `a0cffa47412d2b3d3bf9f799ae98672313febc73` (PR #1057, **open** at freeze). Its artifacts are pinned by
  blob sha, which a later squash merge cannot move:
  - `research/gmi-833-census-registration-pass-v1/REGISTER_DELTA_V1.json`
    blob `be84eb34ff9fa03dbeb21f33a4df4e41c2d44f70`
  - `research/gmi-833-census-registration-pass-v1/DECIDABILITY_V1.json`
    blob `b154d5c2a49902665f3e35462a7ad4ad53122651`
  - `research/gmi-833-census-registration-pass-v1/REFUSALS_V1.json`
    blob `bb8a5bc7a2ca0ed3a2fd244036a15a138cf43dd3`
  - `research/gmi-833-census-registration-pass-v1/RESULT_V1.json`
    blob `193e6677111b31d20deed34b4226092a9085f066`
- Object universe: `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json`
  blob `709159c53c6284366aaf1f05380f5fada8d81a98` (22553 objects, keyed `source_path:source_locator`).
- Ledger value authority the register copies from:
  `research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json`
  blob `66c3b7e4ef91e096f0ece2720af4645bebe75238` (235 registrations).
- Standard-setting sibling: `research/gmi-833-aa-fallacy-detectors-v1/RESULT_V1.json`
  blob `ed4045e835ea7b980bb3b04ced00132e4130e830` (AA19 / AA31 / AA37 closed on `main`).
- Issue comment `5684607872`, anchor `### AA. Recursive loophole / logic-gap closure`;
  live body at freeze: 38943 characters / 39217 UTF-8 bytes, 0 CR bytes,
  sha256 `424a4cf062f9e25b38fd89f6eb880761a43d49f8aa894f2124091c6accc9e994`,
  `updated_at` `2026-09-18T17:31:30Z`.

## 2. Claim ceiling

`VALIDATED_REVIEW_QUEUE_DETECTOR_AT_REGISTERED_SCOPE_V1`

Every detector below emits a **review queue**, never a verdict. A queued
object is a requirement to look, not a refuted claim; an unqueued object is
not thereby correct. Every detector is **total over the 22553 objects** and
**tri-state**: an object whose `assumptions` field is the string sentinel
`UNREGISTERED` receives the state `UNEVALUABLE`, never `CLEAR`; a registered
object outside the row's trigger receives `NOT_TRIGGERED`; a triggered object
whose registered ledger names the assumption class receives `CLEAR`; a
triggered object whose ledger is silent receives `QUEUED`. The detector is
exact where the register exists and says so where it does not.

## 3. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above (byte-exact; the
lines below are quotations of the issue, not this lane's prose):

- [ ] Search for hidden dependence/independence assumptions.
- [ ] Search for hidden stationarity/ergodicity assumptions.
- [ ] Search for hidden bounded-horizon assumptions.
- [ ] Search for hidden compactness/finiteness assumptions.
- [ ] Search for post-selection inference / multiple-testing problems.

These are rows AA24, AA25, AA26, AA27 and AA33 in the numbering of the parent
register's `DECIDABILITY_V1.json`. **No neighboring row is earned here.**
Explicitly NOT earned: AA16, AA17, AA18, AA20, AA22, AA23, AA28, AA29, AA30,
AA32, AA34, AA35, AA36 — the parent register classifies each
`NO_REGISTERED_DISCRIMINATOR` and this package does not reach past that
classification. AA19, AA21, AA31 and AA37 are already closed on `main` and are
not re-earned. The still-open recursion rows of section AA (the recursion terminus,
hostile review, counterexample methods, exhaustive and SMT search, property
testing, proof-assistant targets, the live gap graph, parent-closure
prevention, the final sweep) and every row of AB, AC and AD are not earned.

### Scope the wording licenses

None of the five rows carries a universal quantifier over the corpus ("every
theorem", "all claims"). Each says *search for* a hidden assumption class. The
search this package runs is total over all 22553 objects and returns one of
four states for each; it is decidable — `CLEAR` or `QUEUED` — only on the
objects whose `assumptions` ledger the parent register populated: **173** of
22553 for AA26/AA27, the **15** of those whose evidence mode is a run
experiment for AA24/AA25, and the **10** registered statistical claims for
AA33. The other **22380** objects receive `UNEVALUABLE`. A row closes **at
registered scope** with that residual named in its reconciliation line;
`CORPUS_WIDE_DETECTION` is a forbidden promotion and the residual is the
registration pass those 22380 objects still need, which is not this lane's
work and is not claimed.

## 4. The five detectors, declared before any number is read

All vocabulary matching is case-insensitive substring matching of each
declared term against each entry of the registered ledger, entry by entry (an
entry is one string of the `assumptions` list). A ledger *names the class*
when at least one entry contains at least one term. A negated form
("infinite", "unbounded", "non-compact", "non-stationary") **does** name the
class — a ledger that declares the opposite has addressed the assumption and
it is not hidden; the count of ledgers that name a class **only** through a
negated form is measured and published as a sensitivity figure, never used to
change a state. The parent register's own measurement joined entries with a
space before matching; the entry-by-entry rule is declared here as primary and
the joined variant is recomputed to show whether the two ever differ.

### AA24 — dependence / independence

Trigger: `proof_evidence_mode` in {`STATISTICAL_EXPERIMENT`,
`EMPIRICAL_EXPERIMENT`} (a run experiment, whose validity rests on a
dependence structure). Vocabulary, copied from the parent register:
`independen`, `i.i.d`, `iid`, `exchangeab`, `dependen`.

### AA25 — stationarity / ergodicity

Trigger: as AA24. Vocabulary, copied from the parent register: `stationar`,
`ergodic`, `time-invariant`, `time invariant`.

### AA26 — bounded horizon

Trigger: any registered object. Vocabulary, copied from the parent register:
`horizon`, `finite budget`, `bounded budget`, `step budget`.

### AA27 — compactness / finiteness

Trigger: any registered object. Vocabulary, copied from the parent register:
`finite`, `compact`, `bounded`, `closed set`.

### AA33 — multiple testing after a search over candidates

Trigger: `proof_evidence_mode == STATISTICAL_EXPERIMENT` **and** the object's
package family has size at least 2 among the registered statistical claims,
where the package is the second path component of `source_path`
(`research/<package>/…`) and the family is the set of registered
`STATISTICAL_EXPERIMENT` objects sharing it. A statistical claim that is one
of several from the same package is the shape in which a multiplicity problem
arises; a singleton family is `NOT_TRIGGERED`. Vocabulary, declared **here**
(the parent register declared the predicate but no vocabulary): `bonferroni`,
`holm`, `hochberg`, `benjamini`, `sidak`, `false discovery`, `fdr`,
`family-wise`, `familywise`, `family wise`, `fwer`, `multiple comparison`,
`multiple-comparison`, `multiple testing`, `multiple-testing`, `multiplicity`,
`selective inference`, `pre-registered`, `preregistered`, `pre-registration`,
`preregistration`, `holdout`, `held-out`, `held out`.

### Tier 2 — the object's own boundary ledgers contradict its silence

For every row, a `QUEUED` object is additionally marked
`BOUNDARY_NAMES_IT` when its registered `falsifiers`,
`forbidden_extrapolations` or `scope_quantifiers` list names the same class
under the same vocabulary while its `assumptions` list does not. That is the
strict sense of *hidden*: the object's own record shows the result depends on
the class and the assumptions ledger does not declare it. Tier 2 is a
sub-queue for prioritisation and is reported with its exact count; it never
removes an object from tier 1.

## 5. Predictions, fixed before the executor exists

The parent register published ledger-vocabulary **measurements** for the four
assumption rows in `DECIDABILITY_V1.json` (`measurement_not_queue`), and those
figures were read before this freeze was written. They are restated here as
the predictions this package must reproduce, and the disclosure is that they
are the parent's numbers, not this lane's discoveries:

- P1. AA24: 15 evaluable, **4** `CLEAR`, **11** `QUEUED`.
- P2. AA25: 15 evaluable, **0** `CLEAR`, **15** `QUEUED` — the real `CLEAR`
  class is empty, which is reported as the finding it is; the real no-alarm
  population for AA25 is the **158** registered objects outside the trigger.
- P3. AA26: 173 evaluable, **8** `CLEAR`, **165** `QUEUED`.
- P4. AA27: 173 evaluable, **61** `CLEAR`, **112** `QUEUED`.
- P5. AA33: 10 evaluable, **9** triggered (the one family of size 9), **1**
  `NOT_TRIGGERED`; the `CLEAR` count is not known at freeze and is predicted
  to be at most 9.
- P6. `UNEVALUABLE` = **22380** for every row; the four states partition
  22553 exactly for every row.
- P7. The entry-by-entry rule and the parent's joined-string rule give the
  same `CLEAR` counts on the real register (difference 0); if they differ, the
  difference is published and the entry-by-entry count governs.
- P8. Tier-2 counts are strictly smaller than the tier-1 queues they refine.

## 6. Hostiles (planted; each carries an `applicable` flag)

A hostile is a deliberate loosening or corruption that the checks must
detect. Each is run on the real register and asserted to **move its own
quantity**; a hostile declared applicable whose quantity does not move fails
the run, and a hostile declared inapplicable whose quantity does move also
fails the run.

- H1 — drop the trigger conjunct (AA24, AA25, AA33): every registered object
  becomes triggered; alarms on the real `NOT_TRIGGERED` population move from 0
  to a positive number. Applicable: AA24, AA25, AA33.
- H2 — empty the vocabulary: every triggered object is `QUEUED`; the `CLEAR`
  count moves to 0. Applicable: AA24, AA26, AA27, and AA33 iff its real
  `CLEAR` count is positive. **Not applicable to AA25** (P2 says its real
  `CLEAR` count is already 0); the run must confirm that non-movement.
- H3 — read the `UNREGISTERED` sentinel as an empty ledger: the 22380
  unevaluable objects flood the queue (AA26/AA27 from 165/112 to 22545/22492,
  AA24/AA25 by the run-experiment objects among them). Applicable: all five.
- H4 — corrupt one delta copy: an in-memory `assumptions` entry of one
  registered object is altered; the pointer-fidelity check against the value
  authority must report exactly one differing entry. Applicable: all.
- H5 — evidence-mode drift: the delta's `proof_evidence_mode` of one record is
  altered against the corpus; the consistency check must report exactly one
  mismatch. Applicable: AA24, AA25, AA33.
- H6 — planted positive on a real object: a real `CLEAR` object of a row has
  its naming entries removed in memory and must become `QUEUED`; planted clean:
  a real `QUEUED` object has one naming entry appended in memory and must
  become `CLEAR`. Applicable: AA24, AA26, AA27, AA33 (both directions); AA25
  planted-clean only, since it has no real `CLEAR` object to strip.
- H7 — prose as ledger (measurement, never a queue): the statement text of
  every object is scanned with the same vocabulary as if it were the ledger,
  and the resulting queue size per row is published as the inflation a
  text-grep detector would produce over the tri-state detector. Applicable:
  all five.
- H8 — family by a different key (AA33): families recounted by the
  registration's own `package` field instead of the `source_path` prefix must
  give the identical family table; a fixture that moves one object to another
  package must change the table. Applicable: AA33.

## 7. Null

Over the 173 registered objects, independently permute the
`proof_evidence_mode` column and the `assumptions` ledger column (seeded,
`seed = 8332425`, 200 trials), keeping `source_path` fixed, and re-run each
row's tier-1 predicate. Reported per row: trials reproducing the true
`QUEUED` set exactly (must be 0), the flagged-set size range, the maximum
overlap with the true set and exact `Fraction` means. Where a row's predicate
ignores one of the two columns (AA26/AA27 ignore the mode; AA25's ledger
column carries no information because its real `CLEAR` class is empty) that is
stated, and the null still has to be beaten through the column the predicate
does read.

## 8. Two routes

- Route A (`registered_fallacy_detectors_v1.py`) reads the parent register's
  copies of the ledgers (`REGISTER_DELTA_V1.json` records), joins them to the
  corpus by register key, and evaluates every predicate with entry-by-entry
  substring matching; the family key is the `source_path` prefix.
- Route B (`independent_registered_oracle_v1.py`) imports nothing from A and
  uses no regular expression. It uses the delta records only as a **pointer
  index**: every `assumptions` entry is fetched from the value authority
  `REGISTRATIONS_V2.json` at the pointer the delta carries
  (`#result_id=<rid>.fields.assumptions.content[i]`), the evidence mode is
  read from the corpus rather than the delta, the family key is the
  registration's own `package` field, and matching uses `str.casefold` and
  `str.find` per entry. Route B also reports how many delta copies differ from
  the authority (predicted 0 over every copied entry).
- Agreement: set equality by register key on every tier-1 queue and every
  tier-2 sub-queue, and equality of every tri-state count, for all five rows.

## 9. What is NOT claimed

- That a queued object is wrong. Every output is a review requirement.
- That an unqueued object is free of the fallacy; `UNEVALUABLE` is a state,
  not a clearance, and 22380 objects carry it.
- That the vocabulary is complete: a ledger can address dependence in words
  outside the list. The lists are the parent register's declared ones (AA33's
  is declared here) and a term outside them is a miss, not a false alarm.
- Anything about AA16–AA18, AA20, AA22, AA23, AA28–AA30, AA32, AA34–AA36.
- Corpus-wide detection of any of the five classes.

## 10. Forbidden promotions

- `CORPUS_WIDE_DETECTION`, `AA_FALLACY_SWEEP_COMPLETE`,
  `ALL_FALLACIES_DETECTED`, `CORPUS_FREE_OF_FALLACY`,
  `NO_HIDDEN_ASSUMPTION_REMAINS`.
- `QUEUED_CLAIM_IS_FALSE`, `UNQUEUED_CLAIM_IS_SOUND`,
  `UNEVALUABLE_MEANS_CLEAR`, `UNREGISTERED_MEANS_NONE`.
- `DETECTOR_IS_COMPLETE`, `DETECTOR_IS_SOUND`, `VOCABULARY_IS_COMPLETE`.
- `MULTIPLICITY_CORRECTED`, `INDEPENDENCE_ESTABLISHED`,
  `STATIONARITY_ESTABLISHED`, `HORIZON_BOUND_ESTABLISHED`,
  `FINITENESS_ESTABLISHED`.
- `AA_ROW_EARNED_BEYOND_REGISTERED_SCOPE`, `RECURSION_EXHAUSTED`,
  `ANALYTIC_PROOF`.

## 11. Parent ownership (declared before implementation)

- `research/gmi-833-census-registration-pass-v1/` (PR #1057) **owns** the
  populated register, the binding rules, the `UNREGISTERED` sentinel
  semantics, the per-row decidability table, the four assumption-row
  predicates and their vocabularies, and the measurements P1–P4 restate.
  Nothing about the register is claimed novel here.
- `research/gmi-833-corpus-census-v1/` **owns** the 22553-object universe and
  every field name read.
- `research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json` **owns** every
  ledger string; route B reads it as the value authority.
- `research/gmi-833-aa-fallacy-detectors-v1/` **owns** the closure standard
  for an AA fallacy row (metadata predicate, planted positives, real
  no-alarm case, published inflation of the text variant, tri-route agreement)
  and the finding that these rows were undecidable before the register was
  populated. This package applies that standard; it does not restate it.
- `research/gmi-833-aa-finite-universal-harness-v1/` owns the
  metadata-versus-text inflation instrument (H7 reuses it).
- `research/gmi-833-aa-ledger-gate-v1/` owns ledger emission as a decidable
  predicate; this package's theorem note satisfies it.

External parents restated, not claimed novel, all `CITE-TF` (entered from
field knowledge, not checked against a live source; AC05 is not earned):
de Finetti, "La prévision: ses lois logiques, ses sources subjectives",
*Ann. Inst. H. Poincaré* 7 (1937), for exchangeability as the assumption a
sample-based claim rests on; Birkhoff, "Proof of the ergodic theorem",
*PNAS* 17(12) (1931), doi:10.1073/pnas.17.2.656, for why a time average
warrants an ensemble claim only under ergodicity; Holm, "A simple
sequentially rejective multiple test procedure", *Scand. J. Statist.* 6(2)
(1979), and Benjamini & Hochberg, "Controlling the false discovery rate",
*J. R. Statist. Soc. B* 57(1) (1995), doi:10.1111/j.2517-6161.1995.tb02031.x,
for multiplicity control; Berk, Brown, Buja, Zhang & Zhao, *Ann. Statist.* 41(2) (2013),
doi:10.1214/12-AOS1077, for valid inference after a data-driven choice; Wolpert &
Macready, *IEEE TEC* 1(1) (1997), doi:10.1109/4235.585893, for why a finite
search budget is an assumption a search-derived claim carries.

**Residual contribution claimed here:** (a) five exact, total, tri-state
detectors over the registered `assumptions` ledger, one per row, each
validated with planted positives and a real no-alarm case cited by register
key; (b) the tier-2 boundary-ledger sub-queue, the strict sense of *hidden*;
(c) the published cost of every loosening on the real register — sentinel
read as empty, trigger dropped, vocabulary emptied, prose read as ledger; (d)
the pointer-fidelity check of the register's copies against their value
authority.

## 12. Evidence standard binding this package

Two materially independent routes for every computational claim; hostiles
that are detected AND whose perturbed quantity is asserted to have moved, each
with an `applicable` flag; a null the true result beats; exact arithmetic only
(`int` / `fractions.Fraction`, no float in any reported quantity); stdlib
only; runnable under `python3 -I -B` and `python3 -I -O -B`; Python
3.8-compatible (no `match`, no `X | Y` annotations). The reconciliation JSON is
produced by this lane and applied only by the orchestrator; this lane never
edits the issue or its comments.
