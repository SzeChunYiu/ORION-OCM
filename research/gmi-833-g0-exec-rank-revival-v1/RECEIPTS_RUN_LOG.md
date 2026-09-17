# E9 receipts run log

All outcome-producing computation ran off-Mac on `billy-laptop`
(CPython 3.8.10, stdlib only); the Mac was used for git/gh and file editing
only. Design probes (pre-freeze, merged v1/v2 modules only) are archived
under `design/` with their outputs; `md5` checksums of the transferred
modules were verified on both sides before any run.

## Runs

| what | host | command | result |
|------|------|---------|--------|
| design probe 1 (v1ref space) | billy-laptop | `python3 -I -B probe_execrank_v1ref.py` | `design/probe_out.json` |
| design probe 2 (battery) | billy-laptop | `python3 -I -B probe_execrank_battery.py` | `design/probe2_out.json` |
| design probe 3 (gaps: trap witnesses, affine law) | billy-laptop | `python3 -I -B probe_execrank_gaps.py` | `design/probe3_out.json` |
| fixtures generation | billy-laptop | `python3 -I -B gen_fixtures_e1.py` | `FROZEN_FIXTURES_E1.json` (sha256 `dd0c7bef…` at first freeze) |
| custody amendment | billy-laptop | `python3 -I -B design/patch_fixtures_countdisp.py` | fixtures sha256 `51adb2ab…` (superseded values retained in-file) |
| receipt | billy-laptop | `python3 -I -B exec_rank_revival_v1.py > RESULT_E1.json` | terminal GREEN; 116,427 bytes; `-O -B` byte-identical |
| oracle | billy-laptop | `python3 -I -B independent_oracle_v1.py > ORACLE_RESULT_E1.json` | all_ok; 19 checks; `-O -B` byte-identical |
| tests | billy-laptop | `python3 -I -B test_exec_rank_revival_v1.py -v` | 44 OK (≈12 s) |
| discipline append | billy-laptop + repo | `python3 -I -B assemble_e9_append.py` | `REGISTRATIONS_E9_APPEND.json`; v1 sha `b6bd7503…`, v2 sha `90a278e1…`; exactly-one-diff asserted; `-O -B` byte-identical |
| ledger + reconciliation appends | repo | `python3 -I -B design/append_ledger_and_reconciliation.py` | additive `revival_records` + `e9_note`; gap_closures untouched |

## Custody

- Freeze commit 1: `79651e4877b719b7d5575e869ad1c3c7c0018c05` (FREEZE_E1.md +
  FROZEN_FIXTURES_E1.json + design probes; precedes every implementation
  artifact).
- Custody amendment (freeze precision, pre-implementation):
  `a2bf8d26268947218fcae0f3bc4909b03bdeb62d` (Φ_countdisp macro-symbol count
  pinned; superseded probe values retained; no rule/criterion changed).
- Implementation, receipts, docs, appends and CI follow in the next commits.

## Cross-verification notes

- `RESULT_E1.json:corpora.v1ref.nulls.nets_count/nets_exec` are asserted
  equal to `v2.null_ensemble_v2`'s outputs on v1ref (machinery-reuse check,
  test `test_null_ensemble_consistent_with_v2`).
- The oracle recomputes witness/inv nets and 40-seed null sub-ensembles with
  the frozen v1/v2 engines (never the package's fast DPs) and matches the
  receipt exactly; the ρ=1 nesting-family nets on all six corpora likewise.
- Break-evens use the closed form (T-E1 affinity) with exact two-point
  verification; a 1024-step brute scan on the v1ref witness agrees (test
  `test_breakeven_closed_form_matches_bruteforce`).
