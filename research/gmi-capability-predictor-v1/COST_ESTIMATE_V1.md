# Cost Estimate V1 — completing 602 F4 (next steps)

**Status:** `ESTIMATE` · honest, pre-outcome · no held-family data touched.
**Scope:** Completing 11 F4 boxes from current G1 design to G6 prospective + real-regime.

## Current sunk cost (this folder, G1)

| item | cost |
|---|---|
| Design + validation (Mac-only, 8-field enum + 27-row interface + freeze rule) | 0 GPU-h, ~2 eng-days, pure enumeration at scope `n≤6` |
| Files in this unit | 9 files, ~35 KB |

## Next-step campaigns

### Phase A — G3: fit `Cap` on development worlds only (no held-family data) — CHEAPEST after G1

| step | what happens | compute | why cheap |
|---|---|---|---|
| A1 | Enumerate `Gen_n(B)` at `n=6..8` across development ecologies (finite `D_tau,O,A,F,V`) and record `Phi_E=(Q,R,D,S)` + `C27` success/resource per A4 row | CPU only; exact Fractions; Tiny-world size `2^d` with `d≤6`, `|Gen_n|~10^3-10^4`; runs on `billy-laptop`/`billy-old` | No held families; enumeration is the microscope |
| A2 | Fit `P_c` distributions (per-row histograms + calibrated abstention thresholds for the 4 gates) by cross-validation *within* development worlds | CPU; counts + Fractions | No outcome leakage — provenance already frozen |
| A3 | Freeze `Cap_v1` artifact: descriptor/predictor digests + `prediction_time` + per-family remint commitments (`outcome_seal_hash=null`) | hash + timestamp | Structural |
| A4 | Validate honesty: ensure no held-family `E` identity enters `A1/A2` (remint audit) | structural check | Anti-story rule |

**Cost A:** < 1 GPU-h; CPU-hours on laptop/old dominated by `Gen_n` enumeration (parallel by `n`). Eng: ~3 days (fit + calibration + receipt).

### Phase B — G6 held-family prospective (per-family remint, prospective only) — MODERATE

For each held family `f ∈ {B4-neural, B5-equivariant, B11-memory, B19-continual, + synthesis/learning-law families}`:

| per-family campaign | what happens | compute |
|---|---|---|
| B.f.1 | Derive remint bijection on `E_f` (preserve `O,A,F,V,p,b,H,Delta` by pullback) + open seal commitment | structural |
| B.f.2 | Emit `P_c`/`Q_c` for all 27 rows with `abstain_c` gates evaluated; write `PREDICTION_RECEIPT_f.json` with `prediction_time < outcome_open` | CPU |
| B.f.3 | Unseal held-family outcomes (execute held ecologies on `⟦M⟧` at scope, meter `success_metric` + `resource_metric` per A4 row) | same enumeration cost as A1 per family |
| B.f.4 | Score: proper loss on `P_c` vs observed `success_metric` (per F1 scoring on 27 rows, or per-row proper loss); calibration of abstention; resource `Q_c` vs metered | CPU |

**Cost B (per family):** same order as A1 per family (~minutes–tens of minutes CPU at `n≤6`). For ~6 families in this tranche: < 2 GPU-h total, CPU-bound. Branching factor is the number of families, not model scale.

**F4 boxes closed by A+B:**
- F4-2 (fit only from development worlds) — by A
- F4-3 (freeze held-family predictions) — by A3 + B.f.2/bijection checks
- F4-4/F4-5/F4-6 (strengths/weaknesses, failure modes, transfer) — by B (prospective scoring)
- F4-10 (abstention calibration) — by B calibration curve (G1 gate already)
- F4-7/F4-8/F4-9 REPRICING/ABLATION/DRIFT at tiny-world — can be folded into B's per-family `E` variants (repriced `p`, lesioned `native_operators` field, `Delta`-perturbed `E→E'`) at same CPU cost; no extra GPU.

**Eng B:** ~1 week for 6 families (receipts + scoring + lesion/drift variants reused from `gmi-derived-lesion-v1` and `gmi-developmental-taxonomy-v1` worlds).

### Phase C — Real-regime replication (G6+ transfer) — EXPENSIVE, queued last

| task | scope | why expensive |
|---|---|---|
| Code tasks (HumanEval/MBPP-style with tool/oracle channel) | API/code-execution runs, real token/latency metering | GPU + human review of tool boundary charging (GG58) |
| Math/proof (Lean), factual/science, multimodal/control | model calls + verifier `V` latency/false-adoption cost | GPU + verifier cost accounting |
| Scaling-law comparison: tiny → real sign/order preservation | requires both tiny and real points on same `(D,E,R,H)` | cross-regime, not just larger `n` |

**Cost C:** 10–50 GPU-h depending on model scale + verifier; eng weeks. MUST NOT start before A+B green — tiny-world G6 is the gate (see `/tmp/602_new.md` §T Real-scale transfer: "Only after exact/predictive microscopes"). Doing C before B would spend GPU on a predictor whose tiny-world `F-DESC-COLLISION`/`F-ABSTENTION-VIOLATION` may already falsify it.

## Ordering rationale (highest-cost last)

1. G1 design (this folder) — `~0` compute, closes F4-1 + F4-10 structurally.
2. A (G3 fit) + B (G6 tiny-world held-family, per-family remint, prospective) — CPU-bound, closes 8/11 F4 boxes; cheapest falsifiers F1/F2/F3 live here.
3. C (real-regime) — only after A+B, because real-regime success without tiny-world prospectivity is not G6.

## Triggered Falsifiers by phase

- **F1 `F-DESC-COLLISION`** can fire already at A1 (descriptor incomplete → redesign `DESCRIPTOR_V1.md` values before any held prediction).
- **F2 `F-ABSTENTION-VIOLATION`** can fire at B.f.2 (overconfident distribution where gate says abstain).
- **F3 `F-FREEZE-VIOLATION`** can fire at any B.f.2 receipt audit; also gates C.

## Summary

- To close **structural** F4 (F4-1, F4-10, half of F4-3): **0 GPU-h** — already filed in this G1 unit.
- To close **tiny-world G6** (remaining F4-2..F4-9): **< 3 GPU-h-equivalent CPU** on `billy-laptop`/`billy-old`/`LUNARC` (no-network math), ~1–2 eng-weeks.
- To close **real-regime** F4-11: **10–50 GPU-h + verifier cost**, queued until tiny-world G6 receipt is green.

No `LUNARC → exchange` network path is needed (operator hard ban on crypto-platform connects); all enumeration is no-network math with generic instrument labels if any market-adjacent task enters later.
