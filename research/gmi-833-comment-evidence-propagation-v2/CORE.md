# gmi-833-comment-evidence-propagation-v2

Round 2 of the evidence-propagation sweep over the **comment** checklists of issue #833.
Scope: four comments only — `5693666042` (AI0–AI7), `5693704406` (AI8),
`5693269426` (AF), `5693954852` (AJ).

**No new science. No issue write.** This package re-adjudicates the 105 rows that round 1
(`research/gmi-833-comment-evidence-propagation-v1`) left `BLOCKED_ON_OPEN_PR`, `PARTIAL`
or `NO_EVIDENCE`, against everything merged to `main` since, and emits
`ISSUE_833_COMMENT_RECONCILIATION_V1.json` (schema `GMI_ISSUE_COMMENT_RECONCILIATION_V1`)
for the orchestrator's safe-write path.

`source_main`: `0fb55057`.

## Result

104 rows adjudicated, each exactly once. (Round 1 left 105; one — AF1's `G0` microscope row —
was checked in the live comment by another lane while this round was running, so it is out of
scope and is recorded under `already_closed_upstream` rather than silently dropped.)

| comment | section | EARNED | PARTIAL | BLOCKED_ON_OPEN_PR | NO_EVIDENCE |
|---|---|---|---|---|---|
| 5693269426 | AF | 13 | 10 | 0 | 5 |
| 5693666042 | AI0–AI7 | 1 | 5 | 44 | 0 |
| 5693704406 | AI8 | 0 | 0 | 18 | 0 |
| 5693954852 | AJ | 0 | 1 | 0 | 7 |
| **total** | | **14** | **16** | **62** | **12** |

## Why the yield is 14 and not ~77

The round-2 brief's premise — that seven merged PRs would unblock most of round 1's 77
`BLOCKED_ON_OPEN_PR` rows — is wrong in three checkable ways:

1. **#946 never merged.** It owns AI1–AI8, which is 63 of the 77. Still `OPEN` with a failing
   check. Those rows stay blocked no matter what else landed.
2. **#997 (H family-gate soundness) closes nothing here.** Its own
   `research/gmi-833-h-family-gate-soundness-v1/ISSUE_833_RECONCILIATION_H_FAMILY_GATE_SOUNDNESS_V1.json`
   carries `mode: NO_MUTATION_PREVIEW`, an empty `mutations` array, and `close: false` on every
   named row; it targets issue-*body* H rows, not these four comments.
3. **#952/#953/#955 (AJ10/AJ11/AJ12) were already on `main` at round 1's base.**
   `git cat-file -e 91c6d287:research/gmi-833-aj1{0,1,2}-*` resolves, and the path diff
   `91c6d287..349c2e62` touches none of them. Round 1 already adjudicated against them.

What genuinely landed and moved rows: **#971** (AF4) and **#973** (AF5), 13 rows, one-for-one
with each package's own task list.

## Marking rule (all three required, unchanged from round 1)

1. a **named artifact on `main`** demonstrably satisfies the row's stated requirement, verified
   by opening and reading the artifact — never by filename or title similarity;
2. citable as `path#anchor` a reviewer can check in under a minute;
3. the artifact's own scope covers what the row asks — a row asking a *universal* property is
   `PARTIAL`, not done, when the package proves it at a registered finite scope.

A package's own live, on-subject self-disclaimer overrides apparent coverage. Round 2 adds the
discriminator that a *stale forward-looking* disclaimer does not: AF4's `FORMALIZATION_V1.md`
ends "AF5+ remains open" and its `OPEN_GAPS_V1.json#AF5_PLUS` says the verification tranche is
open — both written before #973 merged, so neither binds AF5's own six rows. By contrast
AF4's `AF4_PHYSICAL` gap ("no physical Church-Turing thesis is tested; **AF7 remains
authority**") is live and on-subject, so AF7 r093 stays `PARTIAL` even though `Comp(S)` now exists.

The discriminator that separates AI4 r035 (marked) from AI8.1 r052 (not marked), inside the same
sweep: **r035 asks for a record, and records stand alone; r052 asks for a constraint on a running
process, and the process it constrains does not exist on `main`.**

## Reproduce

```bash
# 1. re-derive the 104 adjudications (asserts each bulk reason lands in its own section)
python3 -I -B research/gmi-833-comment-evidence-propagation-v2/derive_adjudication_v1.py
# 2. emit against a FRESH fetch of the four comment bodies into $GMI833_FETCH/c_<id>.md
GMI833_FETCH=/tmp/claude-501/prop2/final GMI833_MAIN=0fb55057 \
  python3 -I -B research/gmi-833-comment-evidence-propagation-v2/build_reconciliation_v1.py
python3 -I -B research/gmi-833-comment-evidence-propagation-v2/validate_citations_v1.py
python3 -I -B research/gmi-833-comment-evidence-propagation-v2/calibrate_v1.py
```

- `build_reconciliation_v1.py` refuses to emit unless every `old` **and** every `anchor` is
  byte-exact and appears **exactly once** in the live comment, every open row is adjudicated
  exactly once, and each `(comment_id, anchor, old)` triple is unique across the emission.
  Rows are keyed on the exact `old` text, never a line number.
- `derive_adjudication_v1.py` asserts section-label containment on all 73 bulk-assigned
  reasons: an off-by-one in any index range would otherwise pass every downstream gate,
  since `old` and `anchor` would stay byte-exact and unique while carrying a neighbouring
  section's reason.
- `validate_citations_v1.py`: **36/36** evidence citations resolve; **5/5** planted bad
  citations are caught (missing file, bogus JSON key, two bogus markdown anchors, bogus
  ledger id).
- `calibrate_v1.py`: 11 hand-adjudicated rows re-derived mechanically, **11/11 agree**,
  **7 of them not-earned**, including the adjacent pair AI4 r035 (earned) / AI4 r030 (not) inside
  one section.

### The calibrator was wrong on its first real run — that is why it exists

Three of its eleven tests returned a **false EARNED** because `tree_hits()` scanned
`research/` including this sweep's own packages, whose reason strings quote the very tokens
being searched for (`NN-D1`, `DISCOVER_GMI`, `S_phys`). A fourth returned a **false PARTIAL**
on AF4: it required all 7 `jump_chain` levels to carry `parent_relation_to_next`, but the top
registered level correctly carries `None` because it has no successor in the registry. Both
are fixed and commented in place; no verdict changed as a result.

## Verified this round rather than restated

- `check_aj9a.py` re-run on **laptop-billy** against `main`: **exit 1**
  (`AssertionError` at line 101, `assert all(r for r in hostile_results)`). The AJ9 defect round 1
  filed is still live, so AJ9 r097 stays `PARTIAL`.
- AF4 and AF5 executors, tests and oracles re-run on **laptop-billy**: 16/16 and 20/20 tests pass,
  both `check_reconciliation_v1.py` print `GREEN` with `tasks: 7` and `tasks: 6`, and both
  `RESULT_V1.json` files reproduce exactly from the committed executors.
- AJ15 absence proved twice: `/usr/bin/find research -iname '*aj15*'` returns 0 paths (control
  `*aj14*` returns 2), and the only on-subject mention is a live disclaimer from the neighbouring
  tranche — `gmi-833-aj14-establishment-criterion-v1/OPEN_GAPS.json#remaining[AJ15]`,
  `severity: critical`, "flagship end-to-end falsification experiment remains to be executed".
- New-package delta sweep (19 packages merged since round 1's base): zero hits for `S_phys`,
  `smoothed`, `parameterized complexity`, `DEC`/`information-ratio`, `NFL`, `Blum`,
  `hypercomput`, `INTELLIGENCE_ATLAS`, `barrier_status`, against a validated control grep.
  AF6, AF7 and AF8 therefore stand exactly as round 1 left them.

## Defects found while sweeping (filed, not fixed here)

1. `research/gmi-833-aj9a-known-family-benchmark-v1/check_aj9a.py` still **exits 1 on `main`**
   (round 1's finding, re-verified today). `audit_config()`'s `walk()` never descends into list
   elements, so 4 of its own 11 hostiles — `{"ops":["dense_layer"]}`, `{"ops":["self_attention"]}`,
   `{"ops":["bayes_update"]}`, `{"ops":["genetic_algorithm"]}` — go undetected, which is exactly
   how operator lists are supplied. No CI workflow runs it and the committed `RESULT_V1.json`
   still asserts `hostile_configs_rejected: 11`, `status: GREEN`.
2. `gmi-833-af4-relative-computability-v1`: `MANIFEST_V1.json#hostile_tests` is `16` while
   `RESULT_V1.json#hostiles_required` is `12`. 16 hostile tests do exist and all pass, so this is
   a receipt-field inconsistency, not a coverage gap. No row turns on it.
3. Comment `5693269426`, AF1: `- [x] Construct exact finite \`G0\` microscopes …` is checked in the
   live comment with **no evidence suffix**, unlike every sibling row in that block — while open
   PR **#969** states in its own body that the merged #962 evidence for exactly that row was an
   overclaim (the witness was Boolean-level, not executed through the registered `G0-reg-v1`
   interpreter), that the literal converse is incompatible with the registered definition, and
   moves the row to `deferred_tasks`. Recorded under `already_closed_upstream`; someone should
   decide whether that check survives #969.

## Most tempted to mark, deliberately not marked

- **AI8.1 r052** (post-hoc morphology labels only after generation, via a separately frozen
  classifier with no causal access to search) — `aj10` enforces exactly this mechanically:
  `taxonomy_visible_to_search: false`, `capability_evaluated_before_taxonomy: true`,
  `family_labels_present: false`, a token audit proving `discover_v1.py` contains none of
  `k01`–`k11`/`unknown_morphology`, and a separate `posthoc_taxonomy_v1.py`. Held: the row is a
  constraint on a running blind derivation of *neural* structure, which does not exist on `main`;
  aj10 exercises the mechanism on a generic Boolean substrate.
- **AI5 r043** (preserve the raw Pareto frontier; do not manufacture one universal neural winner
  by arbitrary scalarization) — `aj10` preserves a two-candidate raw frontier with
  `unique_morphology_selected: false` and no frozen scalar prices. Held: the row presupposes
  AI5's morphology regime map from rows 037–042, and there is no such frontier on `main` to preserve.
- **AI8.5 r065** (forbid "GMI proves neural networks are inevitable" without an actual uniqueness
  theorem) — the closest sibling of the one AI row that *was* marked. Held because the only
  registrations on `main` are package-local and none states the row's condition:
  `NEURAL_NETWORK_DERIVED_AS_UNIQUE_OPTIMUM` is scoped "from this theorem" in
  `machine-intelligence-morphogenesis-v1`, and `NEURAL_NECESSARY` appears only inside
  `functional-neural-absorption-v1/fna4_library_synthesis/fna4.py` and `rv8-h1-horizon-v1/RV8_FREEZE.json`.
  Contrast r035, where the non-novelty assertion is corpus-scope in the corpus parent ledger.
- **AI4 r030** (derive reverse accumulation/reverse-mode AD on a finite acyclic graph) — the
  forbidden-set trap. `gmi-833-update-law-space-v1` IL-4 is the obvious citation, but its own
  `CORE.md` says "the adjoint recursion and the elimination view are parent mathematics and are
  not claimed here", and `MANIFEST_V1.json#forbidden_promotions` contains
  `NAMED_ALGORITHM_DERIVED_AS_NECESSARY` and `OPTIMAL_JACOBIAN_ACCUMULATION_SOLVED` — the row's
  meaning is exactly what that parent forbids.
- **AF7 r093** (update `S` and recompute the frontier if future physics supplies a stronger
  substrate) — half its round-1 reason is now void, since `Comp(S[A]) := deg_T(A)` exists and AF4
  demonstrates the recompute discipline. Held on the live on-subject disclaimer
  `OPEN_GAPS_V1.json#AF4_PHYSICAL`: "AF7 remains authority", plus `S_phys` having zero hits on `main`.

## Compute custody

All executors and checkers ran on **laptop-billy** (`python3` 3.8.10), never on the Mac.
Git metadata, the comment fetches and the emitter (pure stdlib, no tree walk of consequence) ran
on the Mac with `/usr/bin/git` and `gh`.
