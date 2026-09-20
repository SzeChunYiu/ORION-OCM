# Receipt — Section-M hierarchy/planning/causal re-audit v1

Package: `research/gmi-833-cognitive-reaudit-v2-implementation-v1`.
Issue #833 Section M, rows `Re-audit hierarchical skills/chunking.`,
`Re-audit planning and stopping.`, `Re-audit causal cognition/intervention/counterfactuals.`
Freeze: `research/gmi-833-cognitive-reaudit-v2/FREEZE_V1.md`
(commit `cb6d6a590535e8660559b143cbe32308a880c482`, PR #927; frozen main
`e71ddcf8ad5e924df3d381483cdac3b3ba5307f4`).
Claim ceiling:
`GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE`.
Evidence level EV2, maturity M2. **Verdict GREEN.**

## Ledger keys (issue-body safe-write)

Section anchor: `# M. Cognitive-function derivation upgrade`; key =
`sha256(section \x00 row_text)`, 12-hex prefix (matches the evidence ledger
`research/gmi-833-checklist-mirror-v1/EVIDENCE_LEDGER_V1.json`).

| row | old | new | L: |
|---|---|---|---|
| hierarchy | `- [ ] Re-audit hierarchical skills/chunking.` | `<see ISSUE_833_RECONCILIATION_HIERARCHY_V2.json>` | `b54aa4a07f07` |
| planning | `- [ ] Re-audit planning and stopping.` | `<see ISSUE_833_RECONCILIATION_PLANNING_V2.json>` | `cae1b23a7b71` |
| causal | `- [ ] Re-audit causal cognition/intervention/counterfactuals.` | `<see ISSUE_833_RECONCILIATION_CAUSAL_V2.json>` | `363a75a09b44` |

## Result hash

`RESULT_V1.json` is the byte-exact replay receipt; both normal and optimized
executor runs and the isolated replay must reproduce it (`cmp`).  sha256:
recorded in MANIFEST_V1.json at commit time.

## Validation runs (this package, on billy-old / laptop-billy)

```text
normal   python3 -I -B  executor_v1.py        -> RESULT_V1.json (byte-identical to committed)
optimized python3 -I -O -B executor_v1.py     -> RESULT_V1.json (byte-identical to committed)
tests    python3 -I -B  test_reaudit_v1.py -v  -> N tests OK
tests    python3 -I -O -B test_reaudit_v1.py -v -> N tests OK
replay   python3 -I -B  replay_v1.py | cmp - RESULT_V1.json  -> identical
replay   python3 -I -O -B replay_v1.py | cmp - RESULT_V1.json -> identical
legacy   hierarchy/causal isolated replay == committed legacy RECEIPT (byte-exact)
reconcile python3 research/gmi-833-foundation-v1/reconcile_issue_833_v1.py --mode check --spec <each spec> -> 1 row READY_TO_APPLY each
```

## Merged artifact

PR: `<PR#>`; merge commit: `<merge-sha>`; merged to `origin/main` after the
PR head's CI reached `conclusion=success`.

## Delivered closure

- Row 1 (hierarchy): re-frame + register of the legacy repair under the
  freeze, re-parented to the upgraded foundation (`c0c574c4…`) + axiom core
  (`3366a3bc…`), byte-exact replay, hostile controls re-asserted.
- Row 2 (planning): the genuinely new result — PS-1 exact Bellman-comparison
  stopping theorem (all costs charged, exact rational, independent full-policy
  oracle) and PS-2 the registered hostile showing a merely myopic one-step EVC
  rule is not generally sufficient, plus tie-preserving control, refusals, and
  the retained 13/35 myopic scope.
- Row 3 (causal): re-frame + register of the causal-rung repair under the
  freeze, same re-parenting, byte-exact replay, causal hostiles re-asserted.

No row outside these three is touched.  Forbidden promotions
(`UNIVERSAL_HIERARCHY_DEPTH`, `GOALS_DERIVED_FROM_DYNAMICS`,
`MYOPIC_EVC_IS_UNIVERSALLY_OPTIMAL`, `OBSERVATION_IDENTIFIES_CAUSATION`,
`GENERAL_CAUSAL_DISCOVERY_SOLVED`, `EMPIRICAL_COGNITIVE_VALIDATION`,
`COMPLETE_GMI`) are preserved.
