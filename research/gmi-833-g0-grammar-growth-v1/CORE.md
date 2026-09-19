# CORE — gmi-833-g0-grammar-growth-v1 (#897 / #833 Section E8)

**What this package proves (exact, machine-checked):** conservative grammar
growth `G_t -> G_{t+1}` with cycle rejection; deterministic charged primitive
invention forming the recursive library `m1 -> a b`, `m2 -> m1 m1`; and a
strict charged held-out discovery-burden reduction on unseen reuse-positive
targets with a preserved negative control and a 200-seed random-admission null.

**Headline (all integers, `κ=1`):** H+ burdens 50,052 -> 1,307 with `K_total=6`
(net −48,739); H− control net +1,178 (regression preserved); `H_eff·Δ > K`
exact (8>3, 13>3, aggregate 21>6); 0/200 nulls better; κ-ablation {0..8}
derives κ=1.

**Read in order:** `FREEZE_V1.md` (formalism, frozen before implementation,
commit `10f0ef37`) → `GRAMMAR_GROWTH_THEOREMS_V1.md` (proofs T1–T6) →
`RESULT_V1.json` (receipt) → `RECEIPTS_RUN_LOG.md` (hosts/commands/seeds) →
`PARENT_LITERATURE_V1.md`, `REUSE_AUDIT_V1.md`, `SCIENTIFIC_LEDGER_V1.json`.

**Reproduce (stock CPython ≥3.8, stdlib only; CI reruns both modes):**

```bash
python -I -B  test_g0_grammar_growth_v1.py -v   # 35 tests incl. hostile battery + oracle agreement
python -I -B  g0_grammar_growth_v1.py           # stdout must equal RESULT_V1.json bytes
python -I -B  independent_oracle_v1.py          # stdout must equal ORACLE_RESULT_V1.json bytes
```

**Claim ceiling (from #897, verbatim):**
`GMI_FINITE_CONSERVATIVE_RECURSIVE_LIBRARY_GROWTH_AND_HELDOUT_REUSE_BENEFIT_AT_REGISTERED_SCOPE`.
Conditional finite transfer only; the forbidden-promotion list in
`MANIFEST_V1.json` is enforced by CI.
