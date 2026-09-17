# CORE — gmi-833-g0-grammar-growth-v2 (#897 follow-up / #833 Section E8)

**What this package proves (exact, machine-checked):** the three gaps left by
the merged v1 package (`SCIENTIFIC_LEDGER_V1.json`) are closed at registered
scope: (1) depth-3 generational formation exists (two corpus shapes, m3 built
literally over m2) but **saturates at depth 3 under the frozen INV-1 rule** —
with the dominance mechanism proved (T7: `gain(u c u) − gain(u) = P·n − b − 1`)
and the ceiling shown rule-attributable (ADM-ALT diagnostic: depth 7/9 on the
same corpora); held-out burden reduction **compounds tier-conditionally**;
(2) **neither compression nor utility-gated admission dominates** — compression
regresses vs primitive search when corpus compressibility diverges from
held-out reuse (trap3: `+43897`, greedy 'abc' destroys the reusable 'ab' mass),
the utility gate forfeits deep macros under shallow validation (c3: loses by
14,939; deep-V tie); (3) the v1 headline **survives the EXEC-B execution-cost
metric** (H+ net −395,484 at ρ=1 vs count −48,739; break-even ρ†=164) while
its rank-1 null claim is cost-fragile (19/200 exec-nulls beat the recursive
library; flat `abab` executes cheaper than recursive `m2`).

**Headline integers (κ=1, all charged):** c3 tiers T1
`1712→732→1296→2098`, T2 `1.97e9→…→4130→7652`, T3
`3.15e16→1.22e11→20616→1350`; aggregate net −3.15e16; H− `429→1911`
monotone regression; 0/200 nulls better on c3/c4/c5 (rank 1); trap1
0/200 beat utility vs 52/200 beat compression; economics f* = 19/50/115,
κ* = 1/4/4, S_0 per depth 23→102→240/518.

**Read in order:** `FREEZE_V2.md` (commits `65df05af`/`74d0a24e`, before all
implementation) → `THEOREMS_V2.md` (T7–T10) → `RESULT_V2.json` (receipt,
terminal `GMI_833_E8_TRANCHE2_GREEN_AT_REGISTERED_SCOPE`) →
`SCIENTIFIC_LEDGER_V2.json` (gap closures + two new recorded gaps) →
`RECEIPTS_RUN_LOG.md` (hosts/commands/hashes).

**Reproduce (stock CPython ≥3.8, stdlib only; CI reruns both modes):**

```bash
python -I -B  test_g0_grammar_growth_v2.py -v   # 30+ tests: hostiles, oracle agreement, receipt validation
python -I -B  g0_grammar_growth_v2.py           # stdout must equal RESULT_V2.json bytes
python -I -B  independent_oracle_v2.py          # stdout must equal ORACLE_RESULT_V2.json bytes
```

**Claim ceiling (from FREEZE_V2.md):**
`GMI_833_E8_TRANCHE2_DEPTH3_FORMATION__TIER_CONDITIONAL_COMPOUNDING__ADMISSION_RULE_ECONOMICS__EXEC_COST_ROBUST_AT_REGISTERED_SCOPE`.
Conditional registered-scope results only; the forbidden-promotion list
(v1's verbatim + `DEPTH_4_PLUS_FORMED`, `UNIVERSAL_DEPTH_GROWTH`,
`COMPRESSION_GATE_DOMINATES`, `UTILITY_GATE_DOMINATES`,
`EXEC_INVARIANT_ALL_RHO`) is enforced by CI.
