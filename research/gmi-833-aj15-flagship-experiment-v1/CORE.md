# CORE — `gmi-833-aj15-flagship-experiment-v1`

**The AJ chain's flagship experiment, executed once, end to end, under rules frozen before any
evidence existed.** Registry hidden, regime predictions frozen, `UNKNOWN` channel live,
post-hoc adjudication only after the blind outcome, a larger non-enumerated universe searched
by two independent implementations with a live honest-failure terminal, AJ13/AJ14 applied at
the end. Outcome: `CONFIRMED` on both routes; `FULL_GMI` **not** earned.

Claim ceiling `AJ15_FLAGSHIP_END_TO_END_EXECUTED_WITH_FAMILY_REGISTRY_HIDDEN_AT_REGISTERED_FINITE_B1_AND_B2_SCOPES`
(strictly under the AJ9 aggregate ceiling and `FGS-4`). `source_main f1e150ea`, freeze
`793e3548` (freeze first; `check_freeze_order_v1.py` re-derives it with a negative control).

## Headline numbers

| facet | result | number |
|---|---|---|
| B1 bounded, every candidate enumerated | `FX-1` | 260 presentations, 148 classes, digest `09a99f29…` reproduced by both routes |
| regimes where the persistent-state organization is predicted absent | `FX-1` | `identity` 0/29, `not` 0/29, `const0` 0/29 exact solvers with a reachable-state-dependent output; K02 fingerprint 0/29 each post hoc |
| regimes where it is predicted present | `FX-1` | `delay1` 1/1, `toggle` 1/1; K02 fingerprint 1/1 each |
| UNKNOWN channel | `FX-2` | 88 solvers match no registered fingerprint; 88/88 parent-reduced; no novel form claimed |
| B2 (16,777,216 presentations, not enumerated), S1 vs S2 | `FX-3` | `identity` 23 evals / 1 class, `delay1` 53 / 2, `delay2` 273 / 4 — all `RECOVERED` and certified on all words; `delay3` `NOT_RECOVERED_AT_SCOPE` on both routes (300,000 evals, 135 restarts; 8 residual classes > 4 states) |
| hostiles and nulls | `FX-4` | 8/8 hostiles applicable and detected; N1 111/200; N2 exact chance 1/10 · 1/8 = 1/80; N3 0/200 |
| AJ13 / AJ14 at the end | `FX-5` | stopping rule 6/6; badges 1–4 earned, 5 and 6 not; both routes agree; AJ11/AJ13/AJ14 receipts re-derived |
| custody | `FX-6` | registry read only post hoc; blind-source audit 0 violations, 8/8 planted recall, control 27+2+4 hits; universe built 51 min before the registry freeze |

## What each AJ15 row gets

Each row is a facet of the one run, not a package of its own: R1 ← `FX-1`; R2 ← `FX-1`/`FX-6`;
R3 ← `FX-3`; R4 ← `FX-1`; R5 ← `FX-3` (scoped: independent implementations, not independent
teams); R6 ← `FX-2`; R7 ← `FX-4`.

## Why the zeros are trustworthy

`N1` shows the state-dependence test fires on 111 of 200 random tables, so 0/29 is a property
of the memoryless regimes. `H2` shows the fingerprint's reachable-state clause is load-bearing
(dropping it passes 12 of the 29 `identity` solvers). `H5` shows the evaluation window is
load-bearing (words ≤ 1 admit 65 "solvers" of `delay1`, 64 rejected). The source-audit zero is
searched, not empty: the same scanner finds 33 hits where the vocabulary is allowed and 8/8
planted positives.

## Reproduce

```bash
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/check_freeze_order_v1.py .
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/aj15_flagship_v1.py --out /tmp/a/BLIND_OUTCOME_V1.json
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/independent_oracle_v1.py --blind /tmp/a/BLIND_OUTCOME_V1.json --out /tmp/a/ORACLE_RESULT_V1.json
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/posthoc_adjudicate_v1.py --blind /tmp/a/BLIND_OUTCOME_V1.json --out /tmp/a/POSTHOC_RESULT_V1.json
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/apply_aj13_aj14_v1.py --out /tmp/a/LADDER_RESULT_V1.json
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/independent_ladder_oracle_v1.py --out /tmp/a/LADDER_ORACLE_RESULT_V1.json
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/check_receipt_v1.py --live /tmp/a
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/build_result_v1.py --check
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/test_aj15_flagship_v1.py
python3 -I -O -B research/gmi-833-aj15-flagship-experiment-v1/test_aj15_flagship_v1.py
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/build_reconciliation_v1.py --check
python3 -I -B research/gmi-833-aj15-flagship-experiment-v1/ra1_citation_audit_v1.py
```

Stdlib only; exact integers and `Fraction`; no float in any receipt. Route A takes about two
minutes (the `delay3` budget is exhausted honestly); everything else is seconds. Computed on
laptop-billy (python 3.8.10); CI re-derives every receipt on ubuntu-latest. **This package
never edits any comment or the issue body**; `ISSUE_833_COMMENT_RECONCILIATION_V1.json` is its
only issue-facing artifact and is applied by the orchestrator.

## Files

`FREEZE_V1.md` + `FREEZE_ROWS_V1.json` (committed first) · `SEARCH_CONFIG_V1.json` ·
`aj15_flagship_v1.py` (route A, blind) · `independent_oracle_v1.py` (route B, blind) ·
`posthoc_adjudicate_v1.py` · `apply_aj13_aj14_v1.py` · `independent_ladder_oracle_v1.py` ·
receipts `BLIND_OUTCOME_V1.json`, `ORACLE_RESULT_V1.json`, `POSTHOC_RESULT_V1.json`,
`LADDER_RESULT_V1.json`, `LADDER_ORACLE_RESULT_V1.json`, `RESULT_V1.json` · `MANIFEST_V1.json` ·
`AJ15_THEOREMS_V1.md` (`FX-1` … `FX-6`) · `PARENT_OWNERSHIP_V1.md` · `test_aj15_flagship_v1.py` ·
`check_freeze_order_v1.py` · `check_receipt_v1.py` · `ra1_citation_audit_v1.py` ·
`build_reconciliation_v1.py` · `ISSUE_833_COMMENT_RECONCILIATION_V1.json` ·
`comment_fetches/5693954852.txt` (the byte-exact comment fetch pinned in `FREEZE_ROWS_V1.json`; `.txt` so the
repo-wide markdown terminology gate does not scan quoted issue text) · `RA1_AUDIT_RESULT_V1.json`.
