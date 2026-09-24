# CORE — `gmi-833-aa1-gap-graph-v1`

**Issue #839 (T833-AA1), child of #833 addendum AA/AD.** Claim ceiling
`GMI_833_RECURSIVE_GAP_GOVERNANCE_V1_AT_DECLARED_SCOPE`.

The census gap graph was a flat list: `descendants` was empty on 0 of 1140
records, so AA38 and AA40 stayed open. This package derives a gap-to-gap
descendant relation from records already committed, makes every repaired gap
record what its repair introduced, blocks promotion and parent closure on
unresolved CRITICAL descendants, adds counterexample-method slots for flagship
results, and implements the AD research loop as a template whose validator
refuses an iteration that extracts no gap.

## What it establishes (exact numbers, two routes)

| result | statement | number |
|---|---|---|
| AA1G-1 | typed graph, derived edges only | 2341 nodes / 2757 edges; `DESCENDANT` 198 = R1 46 + R2 16 + R3 136; **41/1140** records gain a gap descendant from corpus rules (census: **0/1140**), 169 under any rule; 1082 of 1174 claim nodes link to unresolved descendants |
| AA1G-2 | repaired gaps record new assumptions and descendant gaps | 154 `LOCALLY_CLOSED` (108 B1, 46 B3), predicate re-derived 154/154; 154/154 carry non-empty `new_assumptions`; 136 non-empty `new_gaps` |
| AA1G-3 | CRITICAL descendants block promotion and parent closure | 290 unresolved CRITICAL corpus gaps; **136/154** repaired gaps held at `LOCALLY_CLOSED` (6 by corpus rules alone); parent `T833-B1-AA` refused (292), `T833-AA1` refused (5) |
| AA1G-4 | five declared states, bare verdict refused | 0 real nodes above `LOCALLY_CLOSED`; 13824 + 1000 + 3072 exhaustive promotion cases, routes identical |
| AA1G-5 | two distinct counterexample methods before `HOSTILE_CLOSED` | flagship universe 9; 0 slots filled; refused **9/9**; 0/1000 cube grants without two methods |
| AA1G-6 | deterministic validation, cycles reported not collapsed | real graph 0 findings, 0 cycles; 39 planted positives fire (21/21 codes), 6 clean cases silent; 4608 digraphs match a brute-force oracle; 300 random graphs, 0 route disagreements |
| AA1G-7 | AD loop template requiring new-gap extraction | 12 steps; worked instance 2 iterations, 6 gaps, 5 paired changes; 200/200 mutations rejected |
| AA1G-8 | one machine-readable result record | 17 records valid in both routes (9 flagship built from registers with pointers, 8 package) |

Tests: 57, under `python3 -I -B` and `python3 -I -O -B`. Route B
(`independent_gap_graph_oracle_v1.py`) imports nothing from route A or from the
gap-object module.

## Reused, not re-derived

`gmi-833-aa-gap-object-v1` (OPEN_GAP, materiality AAG-3, lattice and bare-token
detector AAG-4, REPAIR_DELTA emitter AAG-5 — loaded by file path);
`gmi-833-census-registration-pass-v1` (`GAP_GRAPH_V2.json`, register delta);
`gmi-833-depgraph-adjudication-v1` (stated edges, DUPID/FIN2UNIV verdicts);
`gmi-833-aa-ledger-gate-v1` (theorem and experiment ledgers — this package adds
one experiment ledger instance); `gmi-833-aa-logical-form-register-v1`,
`gmi-833-aa-fallacy-detectors-v1`, `gmi-833-aa-finite-universal-harness-v1`
(the static claim-label hostiles, #839 item 6).

## #839 acceptance

| # | item | status | evidence |
|---|---|---|---|
| 1 | result record | earned here | AA1G-8, `RESULT_RECORDS_V1.json` |
| 2 | experiment ledger | pre-existing | `gmi-833-aa-ledger-gate-v1` LG-4 (+ `EXPERIMENT_LEDGER_GAP_GRAPH_V1.md`) |
| 3 | `GMI_GAP_GRAPH` + repaired-gap records | earned here | AA1G-1, AA1G-2 |
| 4 | materiality enforcement | earned here | AA1G-3 |
| 5 | closure states, bare verdict refused | pre-existing, enforced here | `gmi-833-aa-gap-object-v1` AAG-4; AA1G-4 |
| 6 | static claim-label hostiles | pre-existing | logical-form register (AA16–18, AA20, AA22), fallacy detectors FD-1 (AA19), finite-universal harness (AA21) |
| 7 | two counterexample-method slots | earned here | AA1G-5 |
| 8 | deterministic validation, both modes | earned here | AA1G-6 |
| 9 | AD loop template | earned here | AA1G-7 |
| 10 | reconcile earned #833 boxes | prepared, not applied | `ISSUE_833_COMMENT_RECONCILIATION_AA1_GAP_GRAPH_V1.json` |

## #833 rows

Earned (pending application after merge): **AA11, AA38, AD01, AD02**.
Not earned: **AA40** (the parent-closure gate exists and refuses, but nothing
binds it to the GitHub issue-close action — `GAP-AD-AA1-AA40-BINDING`),
**AA08** (no recursion to a fixpoint: the loop stopped at its declared ceiling
with 5 CRITICAL gaps open), **AA10** (no independent hostile lane),
**AD03** (a declared stop reason is not verified against a ceiling).

## What this does not show

The repaired gaps are `LOCALLY_CLOSED` only: their repairs introduced
assumptions that are themselves CRITICAL open gaps. Isolated records are not
leaves; they lack a stated edge. No flagship result has been searched for
counterexamples by two methods. The parent-closure verdicts say closure would
be premature; they do not stop anyone from closing an issue. The gap-object
bare-token detector counts 14 sites in `FREEZE_V1.md` (definitional quotes of
the rule and rule-membership phrasing), immutable after its commit; every
markdown file written after the freeze carries 0.

## Reproduce

```sh
python3 -I -B  research/gmi-833-aa1-gap-graph-v1/gap_graph_v1.py --check
python3 -I -B  research/gmi-833-aa1-gap-graph-v1/independent_gap_graph_oracle_v1.py
python3 -I -B  research/gmi-833-aa1-gap-graph-v1/test_gap_graph_v1.py
python3 -I -O -B research/gmi-833-aa1-gap-graph-v1/test_gap_graph_v1.py
python3 -I -B  research/gmi-833-aa1-gap-graph-v1/check_receipt_v1.py
python3 -I -B  research/gmi-833-aa1-gap-graph-v1/gap_graph_v1.py --parent-closure-gate T833-B1-AA   # exits 1
```

Stdlib only; Python 3.8-compatible; every quantity an `int`.

## Files

| file | what |
|---|---|
| `FREEZE_V1.md` | pre-implementation freeze, committed alone first |
| `GAP_GRAPH_SCHEMA_V1.json` | node/edge kinds, rules, states, finding codes, method classes, record fields |
| `AD_LOOP_TEMPLATE_V1.json` | the twelve-step AD loop template and its validator contract |
| `AD_LOOP_RECORDS_V1.json` | the worked loop for this lane; its gaps enter the graph |
| `RESULT_RECORDS_V1.json` | the package's 8 result records |
| `GMI_GAP_GRAPH_V3.json` | the built graph (byte-identical to a fresh build) |
| `gap_graph_v1.py` / `independent_gap_graph_oracle_v1.py` | routes A / B |
| `fixtures_v1.py` | planted positives, clean cases, exhaustive and randomized differentials |
| `test_gap_graph_v1.py` | 57 tests |
| `check_receipt_v1.py` | builds / verifies `RESULT_V1.json` and the reconciliation JSON |
| `AA1_GAP_GRAPH_THEOREMS_V1.md` | AA1G-1..AA1G-8 with all four ledgers |
| `EXPERIMENT_LEDGER_GAP_GRAPH_V1.md` | the five experiment ledgers |
| `ISSUE_833_COMMENT_RECONCILIATION_AA1_GAP_GRAPH_V1.json` | AA11/AA38/AD01/AD02 pending; AA40/AA08/AA10/AD03 not earned |
| `MANIFEST_V1.json` | pins and artifacts |
