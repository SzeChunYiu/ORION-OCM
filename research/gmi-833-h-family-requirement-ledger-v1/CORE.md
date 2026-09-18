# gmi-833-h-family-requirement-ledger-v1 — CORE

**What this is.** A per-row, per-requirement, scope-indexed status ledger for the **43 open
named-family rows of Issue #833 Section H** — two-thirds of everything still open in the
issue. It says, for each row and each of the eleven requirements the Section H preamble
demands, exactly what is already earned, at which scope, with a `path:line` citation, and
exactly what is missing and what would have to be built.

**It closes no #833 checkbox and emits no `ISSUE_833_RECONCILIATION_*.json`.** That absence
is deliberate and instructed; see `FREEZE_V1.md` §3. No neighboring row is earned here.

## The headline

| | |
|---|---|
| `CLOSABLE_NOW` | **0 rows** |
| `CLOSABLE_AFTER_BUILDABLE_WORK` | **43 rows** |
| `BLOCKED_STRUCTURAL` | **0 rows** |

Zero `CLOSABLE_NOW`, citable two independent ways:
`gmi-833-h-neutral-four-family-v1/RESULT_V1.json:56` (`open_gate = real_scale_test`, all four
rows `complete: false`) and `gmi-833-h-obstruction-census-v1/RESULT_V1.json:485`
(`eligible_named_family_rows = 0`).

**Zero `BLOCKED_STRUCTURAL` is the substantive finding.** `FGS-3` proves finite evidence does
not *entail* real-scale behaviour — it does not forbid *running* the test; `FGS-4` blocks
identity inference from operational equivalence *alone* and expressly permits scoped,
prior-disclosed post-hoc mapping; the census obstructions each name their own removal (raise
`B` from 3 to 5; excite the context probe; register the missing channel). Section H is not
uniformly impossible, and reporting it so would be as much a defect as closing a row.

## HRL-3 — the residual distribution

Met requirements at the single best scope covering all eleven coordinates (no `FGS-2`
gluing):

| met of 11 | rows |
|---|---|
| **10** | 4 — `H01` finite-state/automata, `H02` linear regression/classifiers, `H03` GLMs, `H04` basis/kernel |
| **8** | 5 — `H17` Bayesian, `H20` feed-forward NN, `H22` CNN, `H32` flow-like transport, `H34` energy-based |
| **7** | 34 — every remaining row |
| 0–6, 9, 11 | 0 |

Residual dominance, rows missing the requirement out of 43:
`R11` real-scale **43**, `R05` negative twin **39**, `R07` resource crossover **39**,
`R04` neutral recovery **34**, and `R01 R02 R03 R06 R08 R09 R10` **0**.

**The correction the numbers force.** `real-scale test` is indeed universal. But
`independent search` is **not** in the residual at all: it is met at narrower scope at every
row via the source-separated oracles. The zero-instance corpus tier is `M5` independent
**replication** ("no disjoint-team replication",
`gmi-833-maturity-rescore-v2-v1/MATURITY_RESCORE_V2.md:14`), which is a different coordinate.
The true second and third tiers are `negative twin` and `resource crossover`.

## HRL-2 — the two enumerations do not line up

- **43 named rows resolve to only 10 distinct census contracts** (evidence-backed, read from
  `FROZEN_FAMILY_REGISTRY_V1.json`). Census evidence is contract-specific, not row-specific:
  `H01`, `H05`, `H06`, `H11`, `H25`, `H29` all receive the same `UNEXCITED_CONTEXT` object.
- **No primary artifact binds any K-family to any named row.** Verified two ways with a
  control. The corpus's only K-to-Section-H attachment is to the *aggregate* row, at
  `gmi-833-checklist-mirror-v1/EVIDENCE_LEDGER_V1.json:1302`.
- The 35 candidate K-to-row edges in `LEDGER_V1.json` are **agent-constructed and
  unadjudicated**; all 132 `SIGMA_K` cells are `SCREENED_NOT_ADJUDICATED`, never folded into
  any missing count. **10 rows have no K candidate at all**; `H11` and `H19` have several;
  `K04` "attention" maps one-to-many onto `H25`, `H26`, `H29`, `H38` and is **not** the same
  object as the row `Attention mechanisms.`

## Reproduce

```bash
cd research/gmi-833-h-family-requirement-ledger-v1
python3 -I -B  h_family_requirement_ledger_v1.py        # writes LEDGER_V1.json + RESULT_V1.json
python3 -I -O -B test_h_family_requirement_ledger_v1.py # 29 tests
```

Stdlib only, Python 3.8 compatible, integers only (an exact LCG supplies the null; no
`random`, no float anywhere — enforced by an AST test).

## Receipts

- 649 cells: 473 at `SIGMA_CENSUS`, 44 at `SIGMA_4F`, 132 at `SIGMA_K`.
  `MET 0 | MET_AT_NARROWER_SCOPE 348 | MISSING_BUILDABLE 169 | MISSING_STRUCTURAL 0 |
  NOT_APPLICABLE 0 | SCREENED_NOT_ADJUDICATED 132`.
- **Two materially independent routes.** Route A row-first from the issue text via a rule
  table frozen before any executor; Route B artifact-first from the packages' own status
  strings, by machine id and ordinal, importing neither Route A nor the rule table. Round 1
  disagreed on **43 cells of coverage** (zero status disagreements on 606 shared cells),
  recorded verbatim in `ROUTE_RECONCILIATION_ROUND1_V1.json` **before** resolution; Round 2
  agrees on all 649.
- **Hostiles 8/8 detected**, including a fabricated `CLOSABLE_NOW` row, an `FGS-2` scope
  glue, a `SIGMA_K` promotion, an unqualified `MET`, and the `FGS-3` over-read.
- **Null 0/200**: 200 randomized control ledgers all rejected; the true ledger accepted.
- **Extractor validated on real data first**: four rows read by hand from the primary
  artifacts are reproduced cell for cell, including two **no-alarm** rows (`H20`, `H25`) that
  must produce no `SIGMA_4F` cell at all.
- **All five pre-implementation predictions held** (`P1`–`P5` of `FREEZE_V1.md` §8), including
  the `R10`-not-in-residual prediction that contradicts the common expectation.
- Bit-identical on Darwin/CPython 3.13 and laptop-billy Linux/CPython 3.8.10. This licenses
  **neither `EV4` nor `M5`**: intra-package is not independent replication.

## What this does not do

It does not recover a family, does not certify a gate, does not glue scopes, does not touch
PR #997's package or branch, and does not edit the issue body.
