# CORE — gmi-833-capability-interaction-partition-v1

**START HERE.** This package CORRECTS a GREEN mainline object.

## What it corrects

`CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1` (Theorem CI-U + Corollary CI-A4) in
`research/gmi-capability-interactions-unified-v1/`. Prior disposition: GREEN on mainline,
confirmed OVERSTRONG by the #939 verdict table, revived under the #976 L58 revival chain.

Section 1.2 defines four interaction types by **burden** relations; Corollary CI-A4 assigns
those names from **channel-set overlap alone**, never computing a burden. On the real
27-capability A4 contract (351 unordered pairs):

| defect | count |
|---|---|
| **DEF-1** shipped label FALSE by Section 1.2's own defining condition | **56 / 351** |
| **DEF-2** pairs satisfying more than one Section 1.2 label (taxonomy does not partition) | **287 / 351** |
| **DEF-3** `verify_no_interference()` is vacuous (no `"interfering"` return path exists) | — |

Lemmas A, B, C and CE-1/CE-2 are **sound and untouched**. The defect is in the
naming/classification layer only.

## The repair

| id | result |
|---|---|
| **CIP-1** | exact partition on the `(max, joint, sum)` lattice: `INDEPENDENT` (`J = s`), `REDUNDANT` (`J = m` and `m < s`), `PARTIAL_SHARING` (`m < J < s`), `INTERFERING` (`J > s`) — mutually exclusive and jointly exhaustive on the region fixed by (N) non-negativity and (M) `J >= m`, degenerate `m = s` case proved explicitly |
| **CIP-1a** | `SAVING = {J < s} = REDUNDANT ⊔ PARTIAL_SHARING` — the original `Synergistic` class survives as a named aggregate; nothing is deleted |
| **CIP-2** | corrected 351-pair census + complete per-pair delta |
| **CIP-2b** | under union accounting `INTERFERING` is provably EMPTY (replaces the vacuous check) |
| **CIP-3** | exact correspondence on `INDEPENDENT`, exact divergence on the 56 non-nested partial-overlap pairs — EARNED-BY-COUNTEREXAMPLE |
| **CIP-4** | `mu` pinned to counting measure (strict positivity), with the counterexample showing Lemma B's `iff nested` fails without it |

## Corrected census

| class | pairs | shipped | |
|---|---:|---|---:|
| `INDEPENDENT` | 8 | `independent` | 8 |
| `REDUNDANT` | 287 | `synergistic` | 161 |
| `PARTIAL_SHARING` | 56 | `redundant` | 182 |
| `INTERFERING` | 0 | `interfering` | 0 |

**217 of 351 labels change.** Full delta: `DELTA_TABLE_V1.md`; all 351 rows:
`RESULT_V1.json`.

## Issue rows

**This tranche closes NO #833 checkbox.** There is deliberately no
`ISSUE_833_RECONCILIATION_*.json`; the receipt is `CORRECTION_NOTICE_V1.json`.
See `FREEZE_V1.md`: *"No neighbouring row is earned here."*

## Reproduce (exact commands)

```bash
cd research/gmi-833-capability-interaction-partition-v1

# ROUTE A — the classifier, partition checks, hostiles, controls, null
python3 -I -B partition_witness_v1.py

# ROUTE B + ROUTE C — independent enumeration oracle and closed-form count
python3 -I -B partition_oracle_v1.py

# controls (45), including pair-by-pair route agreement
python3 -I -B  test_partition_v1.py -v
python3 -I -O -B test_partition_v1.py -v

# regenerate RESULT_V1.json / DELTA_TABLE_V1.md / CORRECTION_NOTICE_V1.json
python3 -I -B emit_receipts_v1.py
```

Stdlib only; exact `int` / `fractions.Fraction` arithmetic; no floats in any claim.

## Files

| file | purpose |
|---|---|
| `FREEZE_V1.md` | pre-registration, committed BEFORE any implementation commit |
| `CAPABILITY_INTERACTION_PARTITION_THEOREMS_V1.md` | CIP-1…CIP-4 with proofs, scope, falsifiers, forbidden extrapolations |
| `PARENT_OWNERSHIP_V1.md` | parent disclosure (4 Crossref-resolved DOIs) + named residual |
| `partition_witness_v1.py` | ROUTE A executor |
| `partition_oracle_v1.py` | ROUTE B (independent enumeration) + ROUTE C (closed form) |
| `test_partition_v1.py` | 45 controls |
| `emit_receipts_v1.py` | generates the three receipts (nothing hand-transcribed) |
| `RESULT_V1.json` | machine-readable receipt, all 351 per-pair rows |
| `DELTA_TABLE_V1.md` | generated delta table, every changed pair named |
| `CORRECTION_NOTICE_V1.json` | the correction receipt (schema `GMI_CORRECTION_NOTICE_V1`) |
| `MANIFEST_V1.json` | parent pins, source_main, freeze_commit, forbidden promotions |

## Claim ceiling

**G2**. Bounded formal framework with explicit falsifiers. Not raised by this tranche.
