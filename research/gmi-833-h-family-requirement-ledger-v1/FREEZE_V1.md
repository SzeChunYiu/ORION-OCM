# gmi-833-h-family-requirement-ledger-v1 — FREEZE V1

Written and committed BEFORE any implementation, executor, ledger, result or oracle
file of this package. The git add-order of this file versus every other file in this
package is itself part of the receipt.

## 1. Custody pins

- `source_main` = `364f29f1b39557a863ce891529927cec8dadfd6f`
- Issue: `https://github.com/SzeChunYiu/ORION-OCM/issues/833`
- Issue body sha256 as read at freeze time: `48835323695d42f3e21d6f73d0eb535fe8b4b20262924ae5cc5611ee4c4e3240`
- `SECTION_H_MIRROR_V1.md` sha256: `d2e7ca35facc7d8abbfc8135433068454e0f635d2a8ecf55c632be8e62ae21de`
  (verbatim Section H, committed in this same freeze commit, 2193 bytes)

## 2. Claim ceiling

```text
PER_ROW_PER_REQUIREMENT_REQUIREMENT_STATUS_LEDGER_FOR_THE_43_OPEN_SECTION_H_NAMED_FAMILY_ROWS__NO_ROW_CLOSED__NO_CELL_EARNS_A_FAMILY
```

This package is a **ledger of what is already earned and what is missing**. It earns no
family gate, recovers no family, and closes no checkbox.

## 3. Rows this tranche may reconcile

**NONE.** This tranche closes zero #833 checkboxes and produces **no**
`ISSUE_833_RECONCILIATION_*.json` artifact, by explicit instruction. Deliverable item 9 of
the standard closure standard is deliberately absent and its absence is not a defect: a
later auditor must read this clause before filing it as one.

**No neighboring row is earned here.**

The 43 rows this ledger *describes* (and does not close) are exactly the 43 unchecked rows
of Section H, verbatim, in body order, mirrored in `SECTION_H_MIRROR_V1.md`. The two
already-checked Section H rows (`Verify that the same neutral grammar can recover several
families without per-family redesign.` and `Quantify which families cannot be recovered and
why.`) are out of scope and are not re-adjudicated.

## 4. The eleven requirements (frozen enumeration)

From the Section H preamble sentence, in source order:

| id | requirement |
|---|---|
| `R01` | property prediction from specification/ecology |
| `R02` | P3/P4 grammar |
| `R03` | no family macros |
| `R04` | neutral recovery |
| `R05` | negative twin |
| `R06` | lower bound where possible |
| `R07` | resource crossover |
| `R08` | held-out frozen prediction |
| `R09` | remint |
| `R10` | independent search |
| `R11` | real-scale test |

Eleven coordinates, matching PR #997 `FGS-1` ("the source sentence has eleven coordinates").
The corpus's own ten-gate ledger
(`research/gmi-833-h-neutral-four-family-v1/FAMILY_GATE_LEDGER_V1.json`) collapses `R02` and
`R03` into one gate `p3_p4_lower_grammar_without_named_macros`. This freeze **splits them
back into two cells** and requires each to carry a distinct evidence citation; where only
one citation exists, at most one of the two cells may be non-`MISSING`.

## 5. Scope is a per-cell field (FGS-2)

PR #997 `FGS-2` (scope-gluing no-go) holds that certificates proved at scopes `sigma_j`
cannot be composed into eligibility at a target scope `sigma*` absent a registered transport
theorem. A scope is `sigma = (family row, grammar, ecology, budget, freeze, protected
interface)`.

Therefore **every non-`MISSING` cell of this ledger carries the id of the single scope at
which it holds**, and a row's met-count is reported **per scope**. A pooled, scope-blind
met-count may be reported only when it is explicitly labelled
`NON_GLUABLE_UNDER_FGS2`. Frozen scope ids:

- `SIGMA_4F` — `research/gmi-833-h-neutral-four-family-v1`: carrier `{0,1,2}`, arithmetic
  modulo 3, `FiniteLowerProcessGrammarV1` grammar digest
  `465ee803c25b5a2c5d92ec559eb44fbdd0d19cf0feb76ad7c27591a08541d1e6`, max weighted serve
  cost 4, obligations frozen at commit `32566daa72ae723783a70638d5488533d70c8b86`.
- `SIGMA_CENSUS` — `research/gmi-833-h-obstruction-census-v1`: interface `{0,1}^8`, leaves
  `0,1,x0,x1,x2,x3`, operators `NOT`/`XOR`/`AND`, node budget `B=3`, observation ecology the
  8 points where `x0,x1,x2` vary and `x3..x7=0`, freeze commit
  `d2cbd897890e67a2866552b4df50b7583a2f3ceb`.
- `SIGMA_K` — `research/gmi-833-aj9a..aj9h` per-family declared finite task/primitive-basis
  scopes. **No primary artifact binds any `SIGMA_K` family to any named Section H row.**
  Every `SIGMA_K` cell is therefore `SCREENED_NOT_ADJUDICATED` by construction and may never
  be promoted.

## 6. Cell status enum (frozen) and the adjudication rule

Exactly one status per (row, requirement, scope) cell:

- `MET` — a primary artifact establishes the requirement **for the named family itself**,
  i.e. the evaluated object of the artifact is the historical family named by the row, not a
  finite proxy for it. Requires a `path:line` citation.
- `MET_AT_NARROWER_SCOPE` — a primary artifact establishes the requirement, but its
  evaluated object is narrower than the row implies (a registered finite obligation, a
  hallmark contract, an authored post-hoc evaluation prior, or a bounded budget). Requires a
  `path:line` citation **and** an exact `scope_gap` string.
- `MISSING_BUILDABLE` — not established; nothing cited in the corpus structurally prevents
  it. Requires a named `build` string.
- `MISSING_STRUCTURAL` — not establishable; requires a citation to the proof or
  counterexample that makes it so.
- `NOT_APPLICABLE` — permitted for `R06` only, and only with a proof, per `FGS-1`: "The
  lower-bound coordinate also accepts `NOT_APPLICABLE_PROVED`; an unsupported claim that no
  lower bound is possible is not accepted." Every use must carry that proof citation.
- `SCREENED_NOT_ADJUDICATED` — screened, but no primary artifact adjudicates it. Counted and
  reported separately; **never** folded into any `MISSING_*` count.

**Row-binding rule (frozen).** An artifact row string binds to a Section H row iff, after
`casefold()` and stripping a single trailing `.` and surrounding whitespace from both, the
strings are equal; or iff a registry in the artifact's own package maps a machine id to the
row text verbatim. No other binding is admitted. A binding failure yields
`SCREENED_NOT_ADJUDICATED`, never a guess.

**Non-promotion rule (frozen).** `R11` (real-scale test) is **`MISSING_BUILDABLE`, never
`MISSING_STRUCTURAL`**. `FGS-3` proves that finite evidence does not *entail* real-scale
behaviour; its own text adds that "a scaling law, structural invariant, continuity
assumption, or direct real-scale test can add the missing premise; the theorem does not say
that transfer is impossible." Filing `R11` structural would be an over-read and the checker
must reject it. Likewise `FGS-4` blocks family identity inference *from operational
equivalence alone* and expressly "does not block a scoped post-hoc family mapping when
additional structural observables and the evaluation prior are disclosed"; it is recorded as
a `structural_constraint` on method, never as a `MISSING_STRUCTURAL` cell.

## 7. Two materially independent routes (frozen)

- **Route A (row-first).** Entry point `SECTION_H_MIRROR_V1.md`. Enumerates the 43 rows in
  body order from the issue text, binds each row into the artifacts by the *text* binding
  rule above, and assigns cells from `ADJUDICATION_RULES_V1.json`.
- **Route B (artifact-first).** Entry point the artifacts' own JSON. Enumerates assertions
  from `FROZEN_FAMILY_REGISTRY_V1.json` (by machine id `H01..H43` and ordinal position) and
  `FAMILY_GATE_LEDGER_V1.json` (by ordinal position in `family_gate_ledger.family_rows`), and
  derives cell statuses from each artifact's **own status strings** with an independently
  written mapping. Route B does not import Route A and does not read
  `ADJUDICATION_RULES_V1.json`.

Routes are reconciled cell by cell. Disagreements are reported **before** resolution.

## 8. Prediction frozen before implementation

Stated now, before any executor exists, so that the outcome is falsifiable:

- `P1` — `CLOSABLE_NOW` count is **0**, because no row can carry a non-`MISSING` `R11` cell.
- `P2` — `MISSING_STRUCTURAL` count is **0** across all 473 (row, requirement) pairs.
- `P3` — `MET` (unqualified) count is **0**: no corpus artifact evaluates a named historical
  family as its object.
- `P4` — the residual's single dominant requirement is `R11`, missing at **43/43** rows.
- `P5` — `R10` (independent search) is **not** in the residual: it is met at narrower scope
  at `SIGMA_CENSUS` for all 43 rows via the source-separated oracle, and at `SIGMA_4F` for 4
  rows. This contradicts the common expectation that the residual concentrates in
  `real-scale test` *and* `independent search`; `M5` (independent **replication**) is the
  zero-instance tier, and independent **search** is a different coordinate.

A prediction that fails is recorded as failed, verbatim, and the ledger reports the observed
value.

## 9. Hostiles the checker must detect, and the null

Hostiles (each a deliberately broken ledger variant; all must be REJECTED):

1. `HOSTILE_CLOSABLE_NOW` — a row with all 11 cells met.
2. `HOSTILE_SCOPE_GLUE` — an 11/11 bundle assembled from `SIGMA_4F` and `SIGMA_CENSUS` cells.
3. `HOSTILE_K_PROMOTION` — a `SIGMA_K` cell promoted above `SCREENED_NOT_ADJUDICATED`.
4. `HOSTILE_ROW_DRIFT` — one row text altered by a single character.
5. `HOSTILE_UNQUALIFIED_MET` — any `MET` cell (forbidden by §6 rule `P3`).
6. `HOSTILE_FGS3_OVERREAD` — `R11` filed `MISSING_STRUCTURAL` citing `FGS-3`.
7. `HOSTILE_ROW_DROP` — 42 rows instead of 43.
8. `HOSTILE_NA_WITHOUT_PROOF` — `NOT_APPLICABLE` on `R06` with no proof citation.

Null: 200 randomized control ledgers (uniform random status per cell, fixed seed, exact
integer RNG) must all be REJECTED. The true ledger must be ACCEPTED. Target `0/200`.

## 10. Extractor validation before any finding is reported

Before any count in this package is believed, the extractor must reproduce, cell for cell,
four rows read by hand from the primary artifacts at freeze time:

- `H01` `Finite-state/automata intelligence.` — `SIGMA_4F`: nine gates
  `SUPPORTED_*`, `real_scale_test` `OPEN`; `SIGMA_CENSUS`: `IDENTIFIABILITY_OBSTRUCTION`,
  contract `UNEXCITED_CONTEXT`.
- `H02` `Linear regression / linear classifiers.` — `SIGMA_4F` present; `SIGMA_CENSUS`:
  `RECOVERED_CONTROL`, contract `PAIR_PARITY`.
- `H20` `Feed-forward neural networks.` — **no** `SIGMA_4F` evidence (no-alarm case);
  `SIGMA_CENSUS`: `RECOVERED_CONTROL`, contract `PAIR_PARITY`.
- `H25` `Attention mechanisms.` — **no** `SIGMA_4F` evidence (no-alarm case);
  `SIGMA_CENSUS`: `IDENTIFIABILITY_OBSTRUCTION`, contract `UNEXCITED_CONTEXT`.

Recall on planted positives AND the no-alarm case are both asserted by the test.

## 11. Arithmetic and environment

Integers only; no floating point anywhere in this package. Executors run as
`python3 -I -B`, tests as `python3 -I -O -B`, stdlib only, Python 3.8 compatible. The
CI workflow uses `runs-on: ubuntu-latest` (this repository has no self-hosted runners).

## 12. Forbidden promotions

```text
NAMED_FAMILY_ROW_CLOSED
ANY_SECTION_H_CHECKBOX_CLOSED
NAMED_FAMILY_RECOVERED
FINITE_EVIDENCE_IMPLIES_REAL_SCALE
INDEPENDENT_TEAM_REPLICATION
REAL_SCALE_VALIDATION
K_FAMILY_IS_A_NAMED_ROW
CROSS_SCOPE_GATE_COMPOSITION
SECTION_H_UNIFORMLY_IMPOSSIBLE
```

The last is as much a defect as the first: `FGS-4` permits scoped, prior-disclosed post-hoc
family mapping, and #931–#937/#951 and #999/#998 `MAP-1` already perform it. A ledger that
reported Section H as uniformly blocked would be wrong.

## 13. PR #997 is not touched

`research/gmi-833-h-family-gate-soundness-v1` and branch
`codex/833-h-family-gate-soundness-v1` are owned by another lane. This package reads PR
#997's theorem text as a citation only, at blob-pinned commit
`4abe5c4fd7a03b40082ef48ced6499a39b816e4f`, and writes nothing into that package or branch.
