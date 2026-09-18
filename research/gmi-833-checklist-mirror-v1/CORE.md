# gmi-833-checklist-mirror-v1

Custody mirror, evidence ledger and mandatory safe-write path for the #833 checklist of record.

**This package closes no scientific row.** It repairs the instrument the programme uses to record
closure.

## The measured defect

The #833 issue body is the only checklist of record and a GitHub issue body has **no server-side
edit history** — a write replaces the previous body irrecoverably. Two hazards were measured
against the live body (sha256 `9d7b0219f370fce6…`, 64,031 characters):

- **D1 — already truncated.** The body's final characters are `- [` followed by blank lines: a
  checkbox token that does not form a row. At least one stated row is absent from the checklist.
  The content could not be recovered from the repository tree, the issue's 31 comments, or local
  session transcripts. **This package records the loss and refuses to reconstruct it by
  inference.**
- **D2 — 1,505 characters from the ceiling.** GitHub's limit is 65,536. The 167 closed rows carry
  57,550 characters of inline evidence (mean 344, max 1,054). At that rate the remaining headroom
  admits **5 further closures** against **92 rows still open**. The checklist could not reach
  closure in that form; D1 is the most likely already-realised consequence.

## The remedy

| | before | after |
| --- | --- | --- |
| body characters | 64,031 | 24,035 |
| headroom | 1,505 | 41,501 |
| closures admitted at the mean annotation rate | 5 | 150 |

Compaction moves each closed row's full evidence into `EVIDENCE_LEDGER_V1.json`, keyed by
`sha256(section \x00 row text)`, and leaves the row's source refs, package name and a `L:<12 hex>`
ledger key in the body. **No row text and no disposition ever changes.**

## Files

- `ISSUE_833_BODY_MIRROR.md` — byte-exact snapshot of the live body, committed to git, which does
  have history. This is the recovery source that did not exist.
- `EVIDENCE_LEDGER_V1.json` — all 259 rows (167 closed / 92 open) with section, stated text,
  disposition and full evidence text.
- `checklist_core_v1.py` — exact parser, row keys, signature invariant, ledger builder.
- `issue_body_safe_write_v1.py` — **the mandatory write path.**
- `compact_body_v1.py` — the loss-forbidding compaction.
- `test_checklist_mirror_v1.py` — 21 cases, 10 of them hostiles that must be detected.

## Why a count assertion is not enough

A pre/post checked-count assertion is derived from the caller's own stale snapshot. It passes
while a concurrent lane's edit is silently erased. The safe writer instead re-fetches the live
body immediately before writing, applies the declared replacements to *that* fetch, and refuses
unless **every changed line is one the caller declared**. Its hostiles cover the stale-`old`,
wrong-section, ambiguous-`old`, undeclared-collateral-edit, row-text-rewrite, row-un-checking and
over-limit cases.

## Writing a closure

```bash
python3 -I -B research/gmi-833-checklist-mirror-v1/issue_body_safe_write_v1.py \
    research/<pkg>/ISSUE_833_RECONCILIATION_<NAME>_V1.json           # dry run
python3 -I -B research/gmi-833-checklist-mirror-v1/issue_body_safe_write_v1.py \
    research/<pkg>/ISSUE_833_RECONCILIATION_<NAME>_V1.json --apply
```

New closures should be written in pointer form from the start — refs, package, `L:<key>` — with
the full evidence in the package's own `RESULT_V1.json`, so headroom is never consumed again.

## Reproduce

```bash
python3 -I -B  research/gmi-833-checklist-mirror-v1/test_checklist_mirror_v1.py -v
python3 -I -O -B research/gmi-833-checklist-mirror-v1/test_checklist_mirror_v1.py -v
```

Claim ceiling: `GMI_833_CHECKLIST_CUSTODY_MIRROR_AND_SAFE_WRITE_PROTOCOL_AT_OBSERVED_BODY_STATE`.
