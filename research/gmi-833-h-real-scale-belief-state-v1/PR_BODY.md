# Section-H real-scale measurement — row `Bayesian inference/belief-state systems.` (`SIGMA_H17R`)

New package `research/gmi-833-h-real-scale-belief-state-v1/`. Issue #833, section H.
**This PR closes no checkbox and writes no issue body.** The row stays open; the
reconciliation carries `replacements: []`.

## What the measurement delivers

A boundary, measured on a sha256-bound external source
(`/usr/share/dict/american-english` on billy-old, `9e66281f7e51`, 104,334 tokens,
776,142 descriptor-closure positions), on the registered amended ecology `F17`
(set-valued whole-word hypothesis table, evidence weight `len(w)`, two-evidence
posterior label with `T* = 8`), with the registered 7:1 slice (`n_fit` 679,124 /
`n_held` 97,018), exact integer arithmetic throughout, and two materially
independent routes.

| quantity | value |
|---|---|
| held winner, family-blind winner rule | `MEM_FALLBACK` — class `STORED_LABEL_READ_WITH_FALLBACK` |
| held errors | **1,005** (majority rule 10,099; F1 need 5,049 — F1 holds) |
| rank stage / regeneration | 6,709 vs 21,227; 17,338 and 17,200 vs 35,481 and 35,618 — same class at all four stages |
| best intended-class arm (`WEIGHTED_EVIDENCE_BELIEF`) | `WPAIR>=3_12`, **11,421** held errors |
| best raw count arm | `EXT>=4`, 65,523 (weighted beats raw — registered falsifier 2 does not fire) |
| registered weight-reassignment design null | 11,421 → 14,083 = **1.23x** against the registered 3x bar; raw count arms bit-identical |
| full-source store | reproduces the label **exactly**: 0 errors on all 97,018 held queries |
| label-shuffle null | 17,379 > 10,099 |
| store ladder | monotone 10,081 → 1,005 |
| crossover `m*` | 110,799 (`2m > V + 27`, `V` = 221,569) |
| source-order presentation control | fires (constant arm 11,128 = majority, F1 fails) |

**The boundary.** The registered label is a function of the stored completions, so
a store that holds the completions holds the label: on `F17` the family-blind
winner rule recovers the store's own posterior read, not the intended
`WEIGHTED_EVIDENCE_BELIEF`, and the registered null cannot separate them. The row
is **not recovered at this scope** and stays open.

**Adjacent scoped positive** (delivered with the boundary, and explicitly not
claimed for this row): on the 75,618 held queries whose stored table presents at
least two hypotheses, the winner rule recovers one class at all four stages and
clears F1 (917 against 8,399) — labelled with the class actually recovered,
`STORED_LABEL_READ_WITH_FALLBACK`.

## Custody (freeze-first)

Commit 1 of this branch is `FREEZE_V1.md` plus
`FREEZE_V1_SLICE_ADDENDUM_H17_V1.md` **alone**, before any executor, test, data
extraction, fit or result artifact of the package exists. CI asserts the commit
order and that the freeze survives the squash publication. The freeze registers
the design and the falsifiers; the two passages that state the delivered result
were brought into agreement with the delivered receipt at delivery time, and
`CORRECTED_CLAIM_V1.md` is the authority on which drafted claim was refuted, by
which measurement, and what replaced it.

A registered falsifier **fired** and is reported rather than buried: the
first-drafted claim that the F1 coordinate was structurally unsatisfiable at this
label is refuted by this package's own measurement (full-source optimum 0 against
a half-majority of 5,049). The ledger verdict is
`BOUNDARY_REPORTED__REGISTERED_FALSIFIER_3_FIRED`.

## Verification

- `independent_oracle_bs_v1.py` (route B) imports none of the primary executor and **agrees** on every check.
- `real_scale_belief_state_v1.py` (route A): 11/11 coordinates measured at `SIGMA_H17R`, no gate carries a foreign scope, no parent result file is read.
- 35 tests pass under both `-I -B` and `-I -O -B`.
- `ci_gates_v1.py` gates: foreign-sigma, closure-consistency (empty replacements, one attributed open row), annotation-budget (2,143-char measured limit), two-route-namespace, terminology, selftest — every gate fires on a planted positive and is silent on clean input.
- Hostiles all applicable, detected, and silent on the clean receipt (source digest, artifact path, grammar extension, tampered replay row, null seed drift, moved raw arm).

Everything above was produced on the host of record (billy-old, CPython 3.14.4)
and re-verified from the committed receipts offline.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
