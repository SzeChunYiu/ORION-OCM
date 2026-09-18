# CORE — gmi-833-g0-exec-rank-revival-v1 (#897 follow-up / #833 Section E9)

**What this package proves (exact, machine-checked):** the v1 rank-1 null
claim, cost-fragile under EXEC-B (19/200 exec-nulls beat the recursive library
on v1ref at ρ=1), is **restored to rank-1 under BOTH accountings on every
battery corpus** by the nesting-ladder witness — the exec-argimal rung of the
invented library's flat/nested body choices. On v1ref the witness is the flat
pair {ab, abab} (cb=0, eb=0; ties are exactly the 19 identity draws;
**break-even ρ† = 314 vs the recursive library's 164**). On c3/c4/c5 the
recursive INV-1 library was already rank-1 under both (0/0) and its flat rung
strictly exec-dominates it while staying 0/0 (strict margins on c4/c5 — the
W·c·W bodies are not drawable). On trap1/trap3 the #978 compression trap is
exec-symmetric (52/49, 33/33 nulls beat INV-1) and the both-metric argmin
({ab,abab}, {ab}) is exhibited with break-evens 53 and 41 (vs 5 and 1).

**The three ladder rungs landed:** rung 1 (recursive optimal under both)
closed NEGATIVE earned-by-counterexample — the exec-argmin is flat on every
corpus (T-E5); rung 2 (single joint charge rule) closed NEGATIVE
earned-by-construction for the frozen five-charge class (T-E4: the greedy
first admission is forced under every Φ and the rewrite then destroys the
witness mass); rung 3 (structural frontier) DELIVERED: the frontier IS the
nesting ladder with the **exact affine exchange law**
`Net_exec(flat,ρ) − Net_exec(nested,ρ) = −ρ·ΔD·V + ΔK` (37/37 pairs exact at
ρ ∈ {1,2,4}; per-visit dispatch decomposition T-E1; exec-MDL invention is
degenerate — T-E3 — so the ladder refinement, not re-invention, is the
correct instrument).

**Headline integers:** v1ref inv −48,739/−395,484 (cb0/eb19), witness
−48,737/−396,644 (cb0/eb0), space count-argmin = recursive −48,739,
exec-argmin = flat −396,644; c3 argmin −31,501,345,179,969,635 (closure
chain, INV-1 within 356); trap1 argmin {ab,abab} −21,537/−144,023 (both
metrics); trap3 {ab} −17,348/−117,867.

**Read in order:** `FREEZE_E1.md` (commits `79651e48`/`a2bf8d26`, before all
implementation) → `THEOREMS_E1.md` (T-E1..T-E5) → `RESULT_E1.json`
(terminal `GMI_833_E9_EXEC_RANK_REVIVAL_GREEN_AT_REGISTERED_SCOPE`, 16
checks, 7 hostiles) → `SCIENTIFIC_LEDGER_V2.json:revival_records` (closes
GAP-T2-2) → `../gmi-833-claim-discipline-v1/REGISTRATIONS_E9_APPEND.json`
(METRIC_RELATIVE_RANK1 forbidden-extrapolation note) →
`../gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V2.json:e9_note`
(the note's post-correction home; the V1 file is frozen at its bound bytes)
→ `RECEIPTS_RUN_LOG.md`.

**Reproduce (stock CPython ≥3.8, stdlib only; CI reruns both modes):**

```bash
python -I -B  test_exec_rank_revival_v1.py -v    # 44 tests
python -I -B  exec_rank_revival_v1.py            # stdout == RESULT_E1.json
python -I -B  independent_oracle_v1.py           # stdout == ORACLE_RESULT_E1.json (19 checks, slow-engine cross-verification)
```

**Claim ceiling (from FREEZE_E1.md):**
`GMI_833_E9_EXEC_RANK_REVIVAL__BOTH_METRIC_RANK1_WITNESS_BY_NESTING_LADDER__EXACT_AFFINE_EXCHANGE_LAW__STRUCTURE_CLASSIFICATION_AT_REGISTERED_SCOPE`.
Ensemble-relative rank statements with exact tie census; optimality only
over the frozen spaces (full on v1ref/traps; top-T closure on c3;
NFAM-chain-only on c4/c5). Forbidden (in addition to v1/v2 lists):
`RECURSIVE_LIBRARY_EXEC_OPTIMAL`, `SINGLE_JOINT_CHARGE_ACHIEVES_BOTH_METRIC_RANK1`,
`UNIFORM_IN_RHO_RANK1`, `CLOSURE_ARGMIN_ON_C4_C5`, `NESTING_LADDER_COMPLETE_BEYOND_BATTERY`.
