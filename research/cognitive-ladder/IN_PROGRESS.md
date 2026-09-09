# In-progress experiment sources — not results

The files listed below are **incomplete sources for experiments still being
written**. They have no test files and no receipts. Nothing in them may be read
as a result, and no claim anywhere in this repository rests on them.

| file | experiment | fixes negative | status |
|---|---|---|---|
| `rho.py`, `rho_arms.py` | E7 reuse-opportunity-density sweep | N7, N9 (demand side) | source incomplete |
| `support.py` | E6 support-family discovery | N4, N9 | source incomplete |
| `libdisc.py` | E5 method discovery with opportunity control | N7, N11 | source incomplete |
| *(pending)* | E8 independent factorization parents | N10 | not yet written |

Each is registered in `NEGATIVE_DISPOSITION_V1.md` with `fix_status: RUNNING`,
and each will emit a receipt under `results/` and a `test_*.py` before any
finding is claimed. Until then the negatives they target keep their existing
verdicts unchanged.

## Correction to commit 57888dc

That commit is titled "Solve N5: incremental re-index removes the maintenance
terminal" and its message describes only that fix. It also contains, without
mentioning it, a then-268-line partial `rho.py`, swept in by a directory-wide
`git add` while the file was being written. That was my error.

The N5 result is unaffected and this was checked rather than assumed:
`reindex.py`, `run_reindex.py` and `test_reindex.py` import nothing from `rho`,
and the twenty-five re-index tests plus the root-cause and disposition suites
pass with the file present or absent. History is not rewritten, because the
branch is pushed and a receipt-based programme should correct the record forward
rather than edit what it already published.
