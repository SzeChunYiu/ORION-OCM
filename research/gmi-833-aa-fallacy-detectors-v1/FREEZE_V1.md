# FREEZE — `gmi-833-aa-fallacy-detectors-v1` (issue #833, section AA)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, test,
receipt, theorem note or workflow file of this package exists.
`git log --reverse -- research/gmi-833-aa-fallacy-detectors-v1/` must show this
file, alone, first.

## 1. Source pin

- `source_main` = `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue comment under reconciliation: `5684607872`, anchor
  `### AA. Recursive loophole / logic-gap closure`
- live comment bytes at freeze: 28361 (LF only).

## 2. Claim ceiling

`VALIDATED_REVIEW_QUEUE_DETECTOR_V1`

Each detector below emits a **review queue**, never a verdict. A flagged object
is an obligation to look, not a refuted claim; an unflagged object is not
thereby correct. The three detectors are exact, finite, and validated with
recall on planted positives **and** a no-alarm case measured on real data, not
only on a constructed clean set.

## 3. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Search for representability-vs-reachability confusion.
    - [ ] Search for grammar-induced morphology artifacts.
    - [ ] Search for alternative known-parent reductions after every new-form claim.

**No neighboring row is earned here.** Explicitly NOT earned: AA16, AA17, AA18,
AA20, AA22, AA23, AA24, AA25, AA26, AA27, AA28, AA29, AA30, AA32, AA33, AA34,
AA35, AA36 — each names a **different** fallacy and needs its own planted
positives and its own no-alarm case. AA21 is already earned by
`gmi-833-aa-finite-universal-harness-v1` and is not re-earned. No row of AB, AC
or AD is earned.

## 4. The three detectors, declared before any number is read

### AA19 — representability vs reachability

A **metadata** predicate over the frozen census corpus, deliberately not a text
grep: an object is queued when its registered `quantifier_class` is `UNIVERSAL`
— a statement about everything the class can represent — while its registered
`proof_evidence_mode` is an **experiment that was run**
(`EMPIRICAL_EXPERIMENT` or `STATISTICAL_EXPERIMENT`), i.e. a search that
reached part of the space. The conjunction is the confusion the row names:
warranting a representability claim with a reachability observation.

This predicate is **disjoint by construction** from the `FIN2UNIV` predicate
already validated for AA21 (which pairs `UNIVERSAL` with a *finite certificate*
mode, not an experiment); the size of any overlap in the actual object
population will be measured and reported.

Declared-clean classes, fixed here: `UNIVERSAL` with an analytic or mechanized
warrant, and every non-`UNIVERSAL` quantifier class whatever its evidence mode.
The no-alarm case is measured over the **whole real corpus**, not a constructed
set, and a single alarm on it fails the package. A text-trigger variant is run
only to report its **inflation** over the metadata predicate — the measured
cost of a loose trigger — never as the detector.

### AA31 — grammar-induced artifacts

An **exact rational** divergence test over grammar pairs, instrumenting the
frozen result `gmi-833-g0-grammar-bias-v1`, which **owns** the underlying
finding. Two grammars with the same semantics are queued when their
per-semantic-class bias rows differ in any cell. Exact `Fraction` comparison
throughout; no float and no tolerance.

The validation set is the parent's own: its exhaustive **isometric remint**
family (a relabelling of the registered fixture's nodes) is the real no-alarm
population — an isometric relabelling changes no structure and must raise
**zero** alarms — and its registered **non-isometric same-semantics pair** is
the real positive, which must be queued with its divergent cells named. Both
counts are whatever the parent's registered construction yields.

### AA37 — parent reduction after a new-form claim

A **two-tier** instrument over the theorem-artifact corpus, using the ledger
predicate of `gmi-833-aa-ledger-gate-v1`. Tier 1 is precise: a named result is
a new-form claim when its text uses the declared novelty vocabulary — the six
novelty-ladder levels of `gmi-833-ab-residual-definitions-v1` plus the row's
own phrase `new-form` and its crosswalk siblings `unseen form` and
`novel intelligence` — and it is queued when it carries **no strongest-parent
ledger**. Tier 2, a bare `novel` / `new` grep, is run **only to report its
inflation**, never to queue anything.

The no-alarm case is real: this tranche's own theorem notes use the novelty
vocabulary and all carry a strongest-parent ledger, so they must trigger tier 1
and be **cleared**, not queued. The size of the tier-1 population is whatever
the corpus yields, and if it is small that is reported as the finding it is.

## 5. What is NOT claimed

- That a queued object is wrong. Every output is a review obligation.
- That an unqueued object is free of the fallacy. Recall is measured against
  the declared predicate's own target shape, and the text-variant inflation
  figures are published precisely to bound that blind spot.
- Any statement about the 18 other AA fallacy rows.

## 6. Forbidden promotions

- `AA_FALLACY_SWEEP_COMPLETE`, `ALL_FALLACIES_DETECTED`,
  `CORPUS_FREE_OF_FALLACY`, `NO_CONFUSION_REMAINS`.
- `QUEUED_CLAIM_IS_FALSE`, `UNQUEUED_CLAIM_IS_SOUND`.
- `DETECTOR_IS_COMPLETE`, `DETECTOR_IS_SOUND`.
- `GRAMMAR_BIAS_ELIMINATED`, `ALL_GRAMMARS_EQUIVALENT`,
  `SEARCH_REACHABILITY_INVARIANT_UNIVERSALLY`.
- `ALL_PARENTS_EXHAUSTED`, `PARENT_REDUCTION_COMPLETE`, `NOVELTY_ESTABLISHED`.
- `RECURSION_EXHAUSTED`, `ANALYTIC_PROOF`.

## 7. Parent ownership (declared before implementation)

- `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json`
  blob `709159c53c6284366aaf1f05380f5fada8d81a98` — **owns** the object corpus
  and every registered field AA19 reads. Nothing about the corpus is claimed
  novel here.
- `research/gmi-833-g0-grammar-bias-v1/` — **owns** the grammar-induced-bias
  result, the registered fixture, the isometric remint certificate and the
  non-isometric same-semantics hostile pair. AA31 instruments that result; it
  does not re-derive it and claims none of it.
- `research/gmi-833-global-vs-reachable-morphology-v1/` and
  `research/gmi-833-finite-reachability-fractions-v1/` — **own** the
  representability/reachability distinction itself and its exact fractions.
  AA19 detects claims that ignore the distinction; it does not restate it.
- `research/gmi-833-aa-finite-universal-harness-v1/` — owns the `FIN2UNIV`
  validation and the metadata-versus-text-predicate measurement reused here.
- `research/gmi-833-aa-ledger-gate-v1/` — owns the ledger emission predicate
  AA37 reads, and `research/gmi-833-ab-residual-definitions-v1/` owns the six
  novelty-ladder levels AA37's tier-1 vocabulary is drawn from.
- `research/gmi-833-parent-equivalence-v1/` — owns parent equivalence as an
  operation.

External parents restated, not claimed novel: Hutchinson, "Concluding
remarks", *Cold Spring Harbor Symposia on Quantitative Biology* 22 (1957), for
the region-of-space reading; Wolpert & Macready, "No free lunch theorems for
optimization", *IEEE TEC* 1(1) 1997, doi:10.1109/4235.585893, for why a search
result is not a statement about a whole class; Alur et al., "Syntax-guided
synthesis", FMCAD 2013, doi:10.1109/FMCAD.2013.6679385, for grammar-restricted
search; Rice, "The algorithm selection problem", *Advances in Computers* 15
(1976), doi:10.1016/S0065-2458(08)60520-3. All `CITE-TF`; AC05 is not earned.

**Residual contribution claimed here:**
(a) three exact detectors for three of the 22 named AA fallacies, each emitting
    a review queue with a declared target shape;
(b) a no-alarm case measured on **real** data for each — the whole census
    corpus for AA19, the parent's own exhaustive isometric family for AA31,
    this tranche's own compliant theorem notes for AA37;
(c) a published **inflation figure** for the text-trigger variant of each
    text-adjacent detector, which is the measured size of the gap between what
    a metadata predicate sees and what a grep sees.

## 8. Evidence standard binding this package

Two materially independent routes for every computational claim; hostiles that
are detected AND whose perturbed quantity is asserted to have moved; a null the
true result beats; exact arithmetic only (`int` / `fractions.Fraction`, no
float in any reported quantity); stdlib only; runnable under `python3 -I -B`
and `python3 -I -O -B`; Python 3.8-compatible.
