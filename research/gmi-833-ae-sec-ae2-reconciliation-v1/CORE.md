# gmi-833-ae-sec-ae2-reconciliation-v1

The section-level deliverable of lane `sec-ae2`: the orchestrator's input for
issue **#833**, comment **5692689542** (Section AE).

- `ISSUE_833_COMMENT_RECONCILIATION_V1.json` — schema
  `GMI_ISSUE_COMMENT_RECONCILIATION_V1`, `comment_id` `5692689542` on **every**
  entry, `17` replacements and `84` `not_closed` entries, together covering all
  `101` rows that were still unchecked at extraction, each exactly once.
- `COMMENT_5692689542_AT_EXTRACTION.md` — the comment body as fetched
  immediately before the file was finalized, md5
  `1ea73d330f495af36b4ba42c02801de7`. Committing it makes every `old` string
  byte-checkable offline and in CI.
- `verify_section_reconciliation_v1.py` — the checker.

**This lane does not edit the issue.** All issue-body writes are the
orchestrator's.

## What is closed

| package | rows | subsections |
|---|---:|---|
| `gmi-833-ae-morphology-sweep-v1` | 4 | AE5 r5, AE6 r7, AE10 r5, AE13 r7 (all Tier 2) |
| `gmi-833-ae-ae3-compression-learning-v1` | 8 | AE3 entire |
| `gmi-833-ae-ae5-causal-state-audit-v1` | 5 | AE5 rows 1-4 and 6 |

`21` were already checked by the prior lane, so applying this file leaves the
section at **38 of 122**.

## What stays open, and why

| tier | rows | reason recorded |
|---|---:|---|
| 3 — instrument-blocked | **16** | `INSTRUMENT_REQUIRED` with the specific instrument named: AE16's four-domain corpus (8), AE9's training-time measurement (4), AE11's hardware energy measurement (3), AE6's real-dataset test (1). **Not marked, not narrowed to fit.** |
| 4 — AE17 ledger | **7** | `LEDGER_SWEEP_PENDING` — requirements *on* the other packages; 3 of the plan's 13 exist so far |
| 1 — finite-exact | **61** | `NOT_ATTEMPTED_IN_THIS_LANE`, with the section-map package that covers each. Recorded as not attempted, never as blocked. |

The honest ceiling for AE remains **106 of 122**; the checker refuses a file that
claims more.

## Verify

```bash
python3 -I -B research/gmi-833-ae-sec-ae2-reconciliation-v1/verify_section_reconciliation_v1.py
python3 -I -O -B research/gmi-833-ae-sec-ae2-reconciliation-v1/verify_section_reconciliation_v1.py
```

The checker asserts: the snapshot's md5 matches the declared value; replacements
and `not_closed` partition the unchecked rows exactly; every `old` occurs exactly
once in the snapshot and sits under the anchor it names; every `new` extends its
`old` verbatim and carries an evidence marker; every closed row is backed by
exactly one committed package receipt with an identical `new` line; every Tier-3
row states its instrument requirement; every untouched Tier-1 row is recorded as
*not attempted* rather than blocked; and the section total does not exceed the
ceiling.
