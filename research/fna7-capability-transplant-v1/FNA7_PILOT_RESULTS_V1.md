# FNA-7 / D8 pilot results — capability transplant, K2 failure classification

Terminal: **PARENT_SUFFICIENT_FOR_FAILURE_CLASSIFICATION__GUARDED_DECLARED_RULE_AT_PILOT_SCOPE_FNA7_V1**
(first-class SUCCESS: the #219 guarded-declared parent supplies the transplanted capability
sufficiently at pilot scope; no learned or neural machinery needed.)

Machine record: `FNA7_PILOT_RESULTS_V1.json` (freeze sha256 at run:
`adb35e198762f4ff45a8a3771ac568e9b4534a5272a117ff8e8b48fc31c80696`).

## Setup (frozen)

- World: #219 FNA-5 exact world, 2400 queries, md5 split buckets DEV 962 / EVAL 923 / DRIFT 515,
  imported read-only; drift mutation replicated exactly.
- Host harness (AMENDMENT 1): #219 A2 cost-model router fitted on DEV identification
  (identification+fit price 2,055,614 work units, common to all arms, cancels in comparisons).
  Held constant: every arm runs its own seed-identical fresh world; the EVAL failure stream is
  byte-identical across arms (single `eval_failure_qid_digest`, 93 failures = 10.1% fallback,
  matching #219's published A2 fallback rate 0.1008).
- Capability under transplant: responsibility classification of router failures into
  SELECTOR_METHOD_MISMATCH / NOISE_BOUNDARY_UNAVOIDABLE / STALE_DECLARED_MODEL (frozen order,
  latents only for ground truth). Labels for fitting arms acquired at in-world identification
  price 110,797 over 81 DEV failures; R1 pays zero acquisition by construction.
- Sufficiency (frozen before outcomes): EVAL accuracy >= incumbent − 0.03 AND whole-chain cost
  per failed query <= incumbent × 1.05 AND zero neural invocations.

## Headline (EVAL, 93 failures; true composition 79 NOISE / 14 SELECTOR / 0 STALE)

| arm | accuracy | whole-chain / failed query | neural calls |
|---|---|---|---|
| R1_GUARDED_DECLARED | 0.84946 | **142.18** | 0 |
| R2_CALIBRATED_BAYES | 0.84946 | 1333.55 | 0 |
| R3_CART_TREE | 0.81720 | 1325.29 | 0 |
| INCUMBENT_NEURAL_REF (MLP stand-in) | 0.86022 | 2281.32 | 93 |
| NO_CLASSIFIER floor | 0.0 | 1319.86 | 0 |
| ORACLE_LATENT (ceiling, never a result) | 1.0 | 1326.02 | 0 |

DRIFT (37 failures, 22 NOISE / 15 SELECTOR / 0 STALE): R1 0.5946 @ 201.27; incumbent collapses
to 0.4054 @ 4180.51 (predicts SELECTOR everywhere); R2/R3 0.5946; oracle 1.0.
Nulls: shuffle 0.84946 = majority-class rate 0.84946 (R1 is a constant predictor; the
majority rate is the honest null and R1 sits exactly on it — the stream is NOISE-dominated).

## Reading (post-outcome observations, computed in the `observed` block)

1. **Parent sufficiency is real but stream-bounded.** The A2 residual failure stream is 85%
   NOISE on EVAL: failures no cheaper applicable alternative could have passed. On such a
   stream the zero-acquisition declared-centres rule is within ε of the incumbent
   (−0.0108 accuracy) at ~16× lower whole-chain cost — hence the terminal.
2. **Even exact classification does not pay on this stream.** ORACLE continuation work is
   +5.16/failure ABOVE the scan-always floor: SELECTOR retries under declared-cost ordering
   net-lose. The capability's value at this scope is parity at zero cost, not savings.
3. **The incumbent-class arm is the worst generalizer under drift** (0.41 vs R1 0.59),
   consistent with #219's finding that learned selectors do not beat guarded rules here.
4. **STALE never occurs in the scored stream** (binding-clause gap ≤ 0.04 everywhere), so the
   refresh path is exercised structurally (tests, and by ORACLE in the pre-fix run) but not in
   the scored run; stale_flags = 0 and no refresh was billed. Declared scope limitation.

## Causal gate (#214 §5)

All 10 clauses evaluated with evidence in the json (`verdict.causal_gate_214_s5`); notable:
clause 4 margin −0.0108 accuracy / −2139.14 cost; clause 6 substitution delta 0.0 (R1's action
set equals the floor's); clause 3 consumption — EVAL retries per arm: ORACLE 14, R3 7,
incumbent 3, R1/R2 0; clause 8 — replacement arms structurally neural-free (tested).

## Amendments

- AMENDMENT 1 (pre-outcome): router switched from analytic-guarded to #219's A2 cost model;
  the analytic router's failure stream (fallback 0.0043 per #219's published results) was too
  sparse to exercise the capability. Recorded in FREEZE before any scored run.
- AMENDMENT 2 (post-outcome-access, mechanical defect fix): shared-world contamination across
  sequential arms (in-stream drift mutated later arms' DEV/EVAL) fixed by a fresh seed-identical
  world per arm; SHUFFLE_NULL augmented with majority_class_rate. No threshold, arm, terminal
  mapping, or ground-truth rule changed. The first scored run was discarded; all numbers above
  come from the corrected harness.

## Scope

Pilot scope only (one authored E1/L1 world, seeded-MLP incumbent stand-in, three classes):
the terminal licenses no deployment and no #208-scale claim. It proves
CapabilityTransplantProtocolV1 executable end-to-end — contract, incumbent arm, replacement
ladder with strongest-parent first refusal, held-constant harness, blinded legal surface,
charged acquisition, causal gate, scoped terminal — and yields the first piloted transplant
spec (K2) of the seven in `CAPABILITY_TRANSPLANT_PROTOCOL_V1.json`.
