# Validation boundary — Section-M hierarchy/planning/causal re-audit v1

The three rows are closed at the frozen exact scope
`GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE` only
after analytic proof, hostile twins (each actually computed and caught), a
clean variant that does not alarm, exact normal + optimized replay, and
narrow reconciliation.  No empirical campaign, no native VM, no campaign
call, no finite-sample estimation.

## Reproduce (run from the repo root on a compute host, never the Mac mini)

```bash
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/replay_v1.py | cmp - research/gmi-833-cognitive-reaudit-v2-implementation-v1/RESULT_V1.json
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/replay_v1.py | cmp - research/gmi-833-cognitive-reaudit-v2-implementation-v1/RESULT_V1.json
```

Both executor modes must write a byte-identical `RESULT_V1.json`; the CI
workflow copies the committed file, runs both modes, and `cmp`s.  Stdlib
only; exact `Fraction` arithmetic; a test enforces that no float literal
exists in any package source file.

## What is actually computed

- **Planning (the genuinely new result).** PS-1 Bellman-comparison stopping
  on a finite acyclic computation graph with every cost charged; the
  registered hostile `X = f1 XOR f2` at test cost `1/8` where myopic
  one-step EVC stops (`-1/8`) while the two-step information plan has net
  value `+1/4` and the Bellman comparison continues; independent full-policy
  enumeration of all 48 policies per instance (144 across the hostile, clean
  and tie instances) matches `V*` on every instance; `k=1` clean variant does
  not alarm; `k=1/4` tie control keeps ties as sets (`{stop, t1, t2}` and
  `{a0, a1}`); missing goal/model and cyclic graphs are refused; the myopic
  META-3 rule is replayed in-process and retained only at its proved 13/35
  scope with the disagree witness `S={3,5}`.
- **Hierarchy.** The re-parented `gmi-hierarchical-chunking-repair-v1` exact
  content is replayed byte-exactly (isolated `-I -B`/`-O -B` replay equals its
  committed 45,677-byte RECEIPT) and its objects are exercised in-process:
  3060/3032/1233 complete lifecycle with first-use + descendant charges,
  greedy-longest-match failure (`abcde`: greedy 3 vs exact 2), the
  hierarchy-loses workload (retained invocation 9 vs re-derivation 2), the
  384-case policy register census vs 3,456 independent executions, and the
  1,008-case parsing census vs 3,136 complete parses.
- **Causal.** The re-parented `gmi-causal-rung-repair-v1` exact content is
  replayed byte-exactly (6,461-byte RECEIPT) and its objects are exercised
  in-process: the exhaustive n=1..6 census (8/36/120/330/792/1716 models,
  27,018 joint-law comparisons, 4,032 constructive-attainment checks),
  observation-equivalent rung pairs with different PN targets (six-original
  1/2 vs 1; two-smaller 0 vs 1), incompatible evidence refused, identified
  constant-on-fiber control (PN = 1), faithfulness-does-not-orient
  (`do(Y=1|X=1)` 3/4 vs 1/2), and undefined conditioning as a distinct
  refusal.
- **Parents.** The upgraded foundation and axiom-core receipts are
  regenerated from the imported sources and byte-compared to their committed
  (pinned) RESULTs; the foundation forbidden-promotion registry, Pareto
  certificate, prior/evidence/maturity/closure vocabularies, and the
  axiom-core finite model, hostile hypercube (128 cases, 1 satisfying), and
  dependency DAG are exercised.  All eight frozen parent blobs plus the two
  legacy receipts are re-pinned and re-checked at run time.

## Nulls beaten (no-alarm asserted, not only recall)

```
planning_clean_variant_false_alarms     0
causal_identified_control_false_alarms  0
hierarchy_exact_parser_oracle_mismatches 0 (3136 complete parses, oracle-exact)
```

## Bound

`total_registered_cases = 42,254` exact cases (144 planning policies + 63
myopic subsets + 3 planning controls + 2 refusal probes + 384 + 3,456
hierarchy register/execution cases + 1,008 + 3,136 parsing cases + 3,002
causal models + 27,018 joint-law comparisons + 4,032 attainment checks + 6
causal hosted controls).  Exact finite scopes only; no universal
generalization beyond the theorems' stated domains.
