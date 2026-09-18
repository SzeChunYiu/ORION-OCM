# FREEZE — `gmi-833-aa-finite-universal-harness-v1` (issue #833, section AA)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, test,
receipt, theorem note or workflow file of this package exists.
`git log --reverse -- research/gmi-833-aa-finite-universal-harness-v1/` must
show this file, alone, first.

## 1. Source pin

- `source_main` = `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue comment under reconciliation: `5684607872`, anchor
  `### AA. Recursive loophole / logic-gap closure`
- live comment bytes at freeze: 28361 (LF only).

## 2. Claim ceiling

`REGISTERED_DETECTOR_VALIDATED_V1`

This package **validates an existing detector**. It does not detect anything
new and it does not establish that any flagged claim is actually wrong. It
establishes, by exact recount over a pinned corpus, that the
finite-scope-to-universal (`FIN2UNIV`) predicate registered on `main` is
faithfully implemented, has measurable recall on planted positives, raises no
alarm on declared-clean inputs, and that the registered gap population it
produced is exactly what the predicate licenses.

## 3. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Search for finite-scope-to-universal extrapolation.

**No neighboring row is earned here.** In particular AA16, AA17, AA18, AA19,
AA20, AA22–AA37 name *different* fallacies and are NOT earned by validating
this one detector; AA12 (bounded exhaustive counterexample search) and AA13
(SAT/model checking) are NOT earned; and no row of AB, AC or AD is earned.

## 4. What will be measured (declared before the numbers are read)

Route A reads the frozen `GMI_GAP_GRAPH_V1.json` and reports, for the
`GAP-FIN2UNIV-*` population: the number of gap records, the number of distinct
gap ids, the number of distinct `claim_id`s, and the multiset of the six
non-identifying columns. Route B never opens the gap graph: it re-derives the
predicate from `CORPUS_INDEX_V1.json`'s `scientific_objects` and reconstructs
each gap id from the declared `sha256(object_id)[:12]` rule. The two routes are
compared by set equality, not by count equality.

Validation, also declared here and before the numbers are read:

- **recall** — planted positive objects, each carrying the exact
  `quantifier_class` / `proof_evidence_mode` combination the predicate names,
  must all be flagged;
- **no-alarm** — declared-clean objects must produce **zero** alarms. The
  clean classes are fixed now: `UNIVERSAL` with an analytic or mechanized
  evidence mode, and any non-`UNIVERSAL` quantifier class with a finite
  evidence mode. A single alarm on either class fails the package;
- **null** — randomized reassignment of the two predicate fields across the
  real object population, 200 trials under a pinned seed, must not reproduce
  the true flagged set.

Whatever these numbers turn out to be is what is reported. No threshold on the
gap count is declared here, because the count is the thing being measured.

## 5. Forbidden promotions

- `FIN2UNIV_CLAIMS_ARE_FALSE` — a flag is a *review obligation*, not a refuted
  claim. The predicate fires on metadata (declared quantifier class + declared
  evidence mode), never on the mathematics.
- `ALL_FALLACIES_DETECTED`, `AA_FALLACY_SWEEP_COMPLETE` — one of the 22 named
  fallacy searches is instrumented here.
- `CORPUS_FREE_OF_OVEREXTRAPOLATION`, `NO_UNIVERSAL_OVERCLAIM_REMAINS`.
- `DETECTOR_IS_COMPLETE` — recall is measured against planted positives of the
  declared shape only; the predicate's own definition is the scope boundary and
  a differently-worded overextrapolation is outside it.
- `ANALYTIC_PROOF`.

## 6. Parent ownership (declared before implementation)

- `research/gmi-833-corpus-census-v1/corpus_census_v1.py`
  blob `e35f1ae92ea9d140675e01750252dca0a36d2b6e` — **owns** the `FIN2UNIV`
  predicate and the `make_gap` emission. Not claimed novel here.
- `research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json`
  blob `61006b756721c748f8dcc797c755abd25cc42956` — owns the gap population.
- `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json`
  blob `709159c53c6284366aaf1f05380f5fada8d81a98` — owns the object corpus.
- `research/gmi-833-aa-gap-object-v1/` — owns the `OPEN_GAP` schema, the
  materiality threshold and the closure-grade lattice over this same
  population. This package adds no grading.

External parents restated, not claimed novel: Hales, "Formal proof", *Notices
of the AMS* 55(11) 2008 (the computer-assisted-checking / analytic-proof line
this predicate encodes); Rice, "The algorithm selection problem", *Advances in
Computers* 15 (1976), doi:10.1016/S0065-2458(08)60520-3 (cited by the parent
crosswalk for the surrounding terminology, not for this predicate).

**Residual contribution claimed here:**
(a) a materially independent re-derivation of the registered `FIN2UNIV`
    population from the object corpus, including the gap-id reconstruction
    rule, agreeing by set equality rather than by count;
(b) the first recall / no-alarm / null validation of that detector — the
    census registered its output but never tested it;
(c) whatever integrity defects the recount exposes in the registered
    population, disclosed rather than absorbed.

## 7. Evidence standard binding this package

Two materially independent routes for every computational claim; hostiles that
are detected AND whose perturbed quantity is asserted to have moved; a null the
true result beats; exact arithmetic only (`int` / `fractions.Fraction`, no
float in any reported quantity); stdlib only; runnable under `python3 -I -B`
and `python3 -I -O -B`; Python 3.8-compatible (`from __future__ import
annotations`).
