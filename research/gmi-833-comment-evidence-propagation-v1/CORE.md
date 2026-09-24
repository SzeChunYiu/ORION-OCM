# gmi-833-comment-evidence-propagation-v1

Evidence-propagation sweep over the **comment** checklists of issue #833.
Scope: four comments only — `5693666042` (AI0–AI7), `5693704406` (AI8),
`5693269426` (AF0–AF10), `5693954852` (AJ0–AJ16).

**No new science. No issue write.** This package only adjudicates which already-merged
artifacts on `main` satisfy which open rows, and emits
`ISSUE_833_COMMENT_RECONCILIATION_V1.json` (schema `GMI_ISSUE_COMMENT_RECONCILIATION_V1`)
for the orchestrator's safe-write path.

## Result

172 open rows adjudicated, each exactly once.

| comment | section | EARNED | PARTIAL | BLOCKED_ON_OPEN_PR | NO_EVIDENCE |
|---|---|---|---|---|---|
| 5693666042 | AI0–AI7 | 7 | 5 | 45 (#946) | 0 |
| 5693704406 | AI8 | 0 | 0 | 18 (#946) | 0 |
| 5693269426 | AF0–AF8 | 29 | 10 | 14 (#971/#973/#969) | 5 |
| 5693954852 | AJ9–AJ15 | 31 | 1 | 0 | 7 |
| **total** | | **67** | **16** | **77** | **12** |

## Marking rule (all three required)

1. a **named artifact on `main`** demonstrably satisfies the row's stated requirement,
   verified by opening and reading the artifact — never by filename or title similarity;
2. citable as `path#anchor` a reviewer can check in under a minute;
3. the artifact's own scope covers what the row asks — a row asking a *universal*
   property is `PARTIAL`, not done, when the package proves it at a registered finite scope.

A package's own self-disclaimer (`OPEN_GAPS`, `deferred_tasks`, `scientific_rows_not_earned`,
an `af_residual` that retains the question) overrides apparent coverage — applied uniformly,
including where the disclaiming artifact belongs to a different section than the row.

## Reproduce

```bash
python3 -I -B research/gmi-833-comment-evidence-propagation-v1/build_reconciliation_v1.py
python3 -I -B research/gmi-833-comment-evidence-propagation-v1/validate_citations_v1.py
python3 -I -B research/gmi-833-comment-evidence-propagation-v1/calibrate_v1.py
```

- `build_reconciliation_v1.py` refuses to emit unless every `old` **and** every `anchor` is
  byte-exact and appears **exactly once** in the live comment, and every open row is
  adjudicated exactly once.
- `validate_citations_v1.py` resolves all 120 evidence citations (120/120 resolve) and
  proves recall on 3 planted bad citations (missing file, bogus JSON key, bogus heading).
- `calibrate_v1.py` re-derives 11 hand-adjudicated rows mechanically: **11/11 agree**,
  including 4 not-earned cases.

## Defect found while sweeping (filed, not fixed here)

`research/gmi-833-aj9a-known-family-benchmark-v1/check_aj9a.py` **exits 1 on `main`**.
`audit_config()`'s `walk()` yields string values only when held directly under a dict key
and never descends into list elements, so 4 of its own 11 hostiles go undetected —
`{"ops":["dense_layer"]}`, `{"ops":["self_attention"]}`, `{"ops":["bayes_update"]}`,
`{"ops":["genetic_algorithm"]}` — which is exactly how operator lists are supplied
(`generic_ops` is list-valued in the clean config). No CI workflow runs this checker, and
the committed `RESULT_V1.json` still asserts `hostile_configs_rejected: 11`, `status: GREEN`.
This is why AJ9 row `- [ ] Remove architecture names, semantic macros, family-specific
operators/cost bonuses and evaluator leakage for every holdout.` is `PARTIAL`, not marked.

## Compute custody

All executors/checkers were run on **laptop-billy**, never on the Mac.
Git metadata (freeze ancestry, freeze-tree custody, blob pins) was read on the Mac with
`/usr/bin/git`. Where a checker's git calls could not run off-repo, the git ground truth
was established on the Mac first (each aj9b–aj9f freeze commit tree contains exactly
`FREEZE_V1.md` + `SEARCH_CONFIG_V1.json`) and the stub reproduces that verified fact.

## Most tempting to mark, deliberately not marked

- **AI3 r109 / r110** (two materially different search procedures; two materially different
  low-level presentations) — `aj9b` does exactly this for K01, which *is* the neural family,
  with 2 presentations and 2 searches. Held: AI3's protocol is a different frozen contract
  (macro denylist, matched non-neural tasks, negative controls, AutoML-Zero precedent) and
  PR #946 owns AI1–AI8.
- **AI8.2 r58** (`UNKNOWN_MORPHOLOGY` output so the machinery can return structures unlike the
  catalog) — `aj10` has an exercised UNKNOWN channel with a real occupant (T232). Held:
  mechanism similarity across a section boundary; AI8.2 asks it of `DISCOVER_GMI`, which does
  not exist on main. Blocked on #946.
- **AJ15 r257** (run end-to-end on a bounded universe where every candidate can be enumerated)
  — `aj11` enumerates all 260. Held: AJ15 is one flagship end-to-end falsification experiment;
  AJ9/AJ10/AJ11 are three separate microscopes, and no aj15 package exists.
- **AF8 r178** (`GMI_INTELLIGENCE_ATLAS_B`) — AJ11's atlas matches 4 of 6 required fields.
  Held: provenance and barrier status are absent and development is a distance scalar, not edges.
- **AF7 r165** (arbitrary-real-weight analog super-Turing) — demoted after marking: the ledger
  row cited as evidence ends `AF7 retains physical question`.
- **AJ9 r158** (no smuggling for every holdout) — per-holdout audits work and are recall-tested,
  but the frozen contract's own config auditor fails on main (see defect above).

## Remarks for the orchestrator (not actioned — no comment edits made here)

1. The AJ9–AJ13 section headings still read `— OPEN` while rows beneath them become `[x]`.
   AJ0–AJ8 carry `— ✅ PR #911`-style suffixes. The heading suffixes want updating too.
2. Already-done rows in comment `5693954852` carry no per-row evidence suffix (evidence sits on
   the heading). The `new` strings here follow the task schema instead, appending
   `— ✅ \`<package>\` <anchor>: <evidence>.` per row.
3. `aj11`, `aj13` and `aj14` carry no `FREEZE_V1.md` and no independent oracle. That is not a
   bar for *this* sweep (the criterion is artifact-satisfies-row), but it is a gap against the
   #833 closure standard and is recorded here rather than silently passed over.
