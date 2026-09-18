# FREEZE — `gmi-833-aa-ledger-gate-v1` (issue #833, section AA)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, test,
receipt, theorem note, ledger or workflow file of this package exists.
`git log --reverse -- research/gmi-833-aa-ledger-gate-v1/` must show this file,
alone, first.

## 1. Source pin

- `source_main` = `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue comment under reconciliation: `5684607872`, anchor
  `### AA. Recursive loophole / logic-gap closure`
- live comment bytes at freeze: 28361 (LF only).

## 2. Claim ceiling

`RATCHETED_LEDGER_EMISSION_GATE_V1`

This package makes the four theorem-side ledgers and the five experiment-side
ledgers **machine-checkable and enforced going forward**, and measures the
corpus state exactly. It establishes nothing about the truth of any GMI
theorem, and emitting a ledger is not evidence that the ledger's contents are
correct.

## 3. Requirement clause vs corpus-state clause (declared before implementation)

Every row in scope is governed by the verb **Require**. A `Require` row is
discharged by (i) an exact, declared, machine-checkable emission predicate,
(ii) a **blocking** gate that enforces it on everything the repository grows
from here, and (iii) the measured corpus state at `source_main` disclosed as a
residual, never as discharged. This is the same audit-clause/corpus-state
split the AB tranche declared, and the same ratchet shape: a gate that fires
on work a lane did not do is a gate that gets switched off.

**The corpus-state number is a disclosure, not a claim of compliance.** If the
measured compliance is low, that is what is reported.

## 4. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Require every theorem/proof/experiment to emit an explicit assumptions ledger.
    - [ ] Require every theorem to emit a dependency ledger.
    - [ ] Require every theorem to emit a falsifier/counterexample ledger.
    - [ ] Require every theorem to emit a strongest-parent/subsumption ledger.
    - [ ] Require every experiment to emit leakage, search-space, cost-model, evaluation and sampling-bias ledgers.

**No neighboring row is earned here.** Explicitly NOT earned:

    - [ ] Define a machine-readable `OPEN_GAP` object: claim, premise, inference, unresolved assumption, possible counterexample, severity, owner, parent result, evidence needed.
    - [ ] Recurse until no new **material** gap is found under the declared scope.
    - [ ] Require independent hostile review before a gap can be marked exhausted.

and no row of AB, AC or AD. In particular AD02 (new-gap records per iteration)
is a different gate and is not earned.

## 5. The emission predicate (declared before it is run)

A **theorem artifact** is a git-tracked file under `research/` whose basename
matches `*THEOREM*.md`. A **named result** inside one is a level-2 ATX heading
(`## `) whose text is not a bare definition marker. A named result **emits a
ledger** when the ledger's own bold label appears as a block-leading
`**Label.**` run inside that result's span. Accepted labels are fixed now:

| row | ledger | accepted block labels |
|---|---|---|
| AA02 | assumptions | `Assumptions`, `Assumption` |
| AA03 | dependency | `Dependencies`, `Dependency`, `Depends on` |
| AA04 | falsifier | `Falsifiers`, `Falsifier`, `Counterexamples`, `Counterexample` |
| AA05 | strongest parent | `Strongest parents`, `Strongest parent`, `Parents`, `Parent` |

A prose sentence containing the word "assumption", "depends", "falsify" or
"parent" is **not** an emission. That decoy must be rejected, and the rejection
is a named result of this package.

An **experiment artifact** is a git-tracked file under `research/` whose
basename matches `*EXPERIMENT*LEDGER*.md`, declaring the schema line
`GMI_EXPERIMENT_LEDGER_V1`. Its five required ledgers (AA06) are the five the
row itself names: leakage, search space, cost model, evaluation, sampling bias.

Because AA03's dependency ledger and AA06's experiment ledger have, at
`source_main`, no known instance, this tranche **authors planted positives**:
fully compliant theorem notes and experiment ledgers are written here, and the
gate's recall is measured against them. They are declared as planted here, in
advance, so that no post-hoc positive can be passed off as a corpus finding.

## 6. Forbidden promotions

- `CORPUS_LEDGERS_COMPLETE`, `ALL_THEOREMS_COMPLIANT`, `LEDGER_DEBT_CLEARED` —
  the measured baseline is disclosed in `RESULT_V1.json` and is the opposite of
  these.
- `LEDGER_CONTENTS_VERIFIED` — the gate checks emission, never correctness. An
  assumptions ledger that lists the wrong assumptions passes.
- `ASSUMPTIONS_EXHAUSTED`, `ALL_FALSIFIERS_KNOWN`, `ALL_PARENTS_EXHAUSTED`.
- `RECURSION_EXHAUSTED`, `NO_MATERIAL_GAP_REMAINS`.
- `ANALYTIC_PROOF`.

## 7. Parent ownership (declared before implementation)

- `research/gmi-833-aa-gap-object-v1/` — **owns** the `OPEN_GAP` object, the
  materiality threshold, the closure-grade lattice and the `REPAIR_DELTA`
  emitter. This package adds no gap object and no grading.
- `research/gmi-833-ab-terminology-harness-v1/terminology_ratchet_v1.py`
  — **owns** the ratchet pattern (frozen baseline, owned-files scope on
  `pull_request`, strict repo-wide scope on `push`). The ratchet *shape* is
  reused and credited; the ledger predicate it carries is the residual here.
- `research/gmi-833-corpus-census-v1/` — owns the corpus census and the
  `assumptions` / `falsifiers` / `strongest_parents` / `forbidden_extrapolations`
  object fields, which are a *census extraction*, not an enforced emission.
- `research/gmi-833-aa-gap-object-v1/AA_GAP_OBJECT_THEOREMS_V1.md`
  blob `03da1a3566a6e62f8506981c7dde51ebc212cc81` and
  `research/gmi-833-ab-terminology-harness-v1/AB_TERMINOLOGY_THEOREMS_V1.md`
  blob `7d43f04ae0b078263ba3ed2070fba2bbdd773c7b` — the two most recent theorem
  notes on `main`. The #833 batching plan records these as already emitting all
  four ledgers. **That is checked here, not assumed**, and whichever way it
  falls is reported.

External parents restated, not claimed novel: the assumptions/limitations
ledger is standard scientific-reporting practice — Nosek et al.,
"Preregistration revolution", *PNAS* 115(11) 2018,
doi:10.1073/pnas.1708274114; the falsifier requirement is Popper, *The Logic of
Scientific Discovery* (1959); leakage and evaluation ledgers follow Kapoor &
Narayanan, "Leakage and the reproducibility crisis in machine-learning-based
science", *Patterns* 4(9) 2023, doi:10.1016/j.patter.2023.100804, and the
model/datasheet reporting line of Mitchell et al., "Model cards for model
reporting", FAT* 2019, doi:10.1145/3287560.3287596, and Gebru et al.,
"Datasheets for datasets", *CACM* 64(12) 2021, doi:10.1145/3458723. None of
these is claimed as this package's invention.

**Residual contribution claimed here:**
(a) an exact per-named-result emission predicate for the four theorem ledgers
    and the five experiment ledgers, with a declared decoy class (prose
    mention) that must be rejected;
(b) the first per-result measurement of ledger compliance over the whole
    `research/**` theorem corpus at `source_main`;
(c) a blocking, ratcheting CI gate that fails a pull request whose own new or
    grown theorem note omits a ledger — demonstrated to fail, not merely
    installed;
(d) `GMI_EXPERIMENT_LEDGER_V1`, the experiment-side artifact class AA06 names,
    which has no instance on `main`.

## 8. Evidence standard binding this package

Two materially independent routes for every computational claim (route B parses
by a line state machine and shares no code with route A's span extraction);
hostiles that are detected AND whose perturbed quantity is asserted to have
moved; a null the true result beats; exact arithmetic only; stdlib only;
runnable under `python3 -I -B` and `python3 -I -O -B`; Python 3.8-compatible.
The gate is proven to be able to fail: a deliberately non-compliant fixture is
run through it and its non-zero exit is recorded in the receipt.
