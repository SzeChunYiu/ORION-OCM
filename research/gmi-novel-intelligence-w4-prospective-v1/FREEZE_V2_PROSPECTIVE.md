# W4 prospective replication freeze V2 (REV-L47-NOVEL-INTELLIGENCE-W4)

Custody statement: this freeze document (with `FREEZE_V2_PROSPECTIVE.json`) is
committed to this branch BEFORE any replication outcome, executor, test, or
receipt of the package `gmi-novel-intelligence-w4-prospective-v1` exists in
git. The package CI verifies the add-order mechanically and fails otherwise.

## Why this freeze exists (recorded defect, not erased)

The corpus passes v2 L47 pass (PR #976) adjudicated the parent package
`gmi-novel-intelligence-w4-v1` POST_HOC_SUSPECT (CONFIRMED, double-verified,
independently re-verified on this branch): `RESULT_V1.json`
("all_w4_boxes_green") first added at commit `08c4d206`
2026-09-15T16:54:44+02:00; `FREEZE_V1.md` first added at `7ce73e5d`
2026-09-15T18:23:27+02:00 (89 min later); the result commit is a true
ancestor of the freeze commit. Mitigating, recorded: the freeze SEED literal
+ sha256 pre-existed inside the WIP executor at `08c4d206` (lines 29-30), so
seed custody was prospective; the freeze DOCUMENT was not.

That commit-order defect is PERMANENT. What this package re-earns, per the
registered revival lever (REV-L47-NOVEL-INTELLIGENCE-W4), is prospective-ness
of the CONTENT: the family-member search is re-run from the SAME pre-existing
frozen seed under this NEW freeze, committed before the replication outcomes.
Original commit-order gap remains on the parent package's record forever.

## Seeds

Inherited (pre-existing, prospective since 08c4d206):

```text
sha256("GMI-NOVEL-INTELLIGENCE-W4-V1/RQM-FAMILY-RECURRENCE")
  = 57ddb8d1195e0eba61e0527828882bce1f9e0da24a4474ef3a69b7c6c71789c9
```

New prospective seed for this replication (executor recomputes and refuses to
run on mismatch):

```text
sha256("GMI-NOVEL-INTELLIGENCE-W4-PROSPECTIVE-V2/REPLICATION-2026-09-16")
  = 971e3ed3fec5568a588ff475badd1be77a0533bf6a99d0f9a2a99da5138f3110
```

## Hypothesis (original claim strength, assumption set held fixed)

Everything the original package claimed, re-earned under demonstrable
custody. The upstream V6 machine (P fixed to registered q_P, cost
C = |range(P)| + |range(R)|, architecture macros forbidden) applies
unchanged. On the registered family F(k), k in {2,3,4}:

```text
max_m(k) = k          C*(k) = 2 + k          flat_table_cost(k) = k + 3
material gap vs flat = 1                     needs_residual = true
pure predictor under q_P fails               fixed-budget B=3 is NOT the family law
  k=2: B overprovisions (does not track max_m)
  k=3: B locally matches at B only
  k=4: B fails exact recovery
remint (history reverse + label cycle) preserves law and recovery on all members
upstream compose gate: V6 six boxes green, W2/W3 true, W4 false, phase-hole refused
```

Held-out fresh ecology (original registration, k=5 not in family):
max_m=5, C*=7, flat=8, zero-residual impossible, fixed-budget B=3 fails,
pure predictor fails.

## NEW prospective content (genuinely blind: never measured anywhere)

1. Extended held-out H = {k : 5 < k <= K_max} with K_max derived from the
   registered exhaustive-search budget 2^30 tuple-visits: the first-valid
   residual assignment in `find_matching_residuals` enumerates
   ~(K-1)*K^K tuples for F(K); K=9 gives 8*9^9 ~ 3.14e9 > 2^30, K=8 gives
   7*8^8 ~ 1.18e8 <= 2^30, so **K_max = 8**. For every k in {6,7,8}:
   max_m=k, C*=2+k, flat=k+3, pure predictor fails, fixed-budget B=3 fails
   exact recovery. Per-assay wall-clock abort budget 3600 s; exceeding it is
   recorded as ASSAY_TIMEOUT (a charging fact; the analytic independent route
   still covers the prediction).
2. Negative control family G(k), k in {2..8}: q_p = (0,)^k + (1,)^k,
   q_o = (i%2 for i in 0..k-1) + (2 + (i%2) for i in 0..k-1). Predicted law
   is CONSTANT in k: max_m=2, C*=4, flat=5, pure predictor fails,
   fixed-budget B=3 SUCCEEDS (2 <= 3). If the instrument reported max_m=k on
   G(k), the measurement is broken and the replication REFUTES at the
   measurement stage.
3. Independent route (no V6/W4 import): direct fiber-multiplicity count for
   max_m, first-occurrence canonical construction for C*, distinct-label
   count for flat, pigeonhole bound for fixed-budget, and a brute-force
   tightness witness enumerating all residual assignments over alphabet
   m-1 (rule: witness run where (m-1)^(2k) <= 2^20, i.e. k in {2,3,4,5})
   confirming NO exact decoder exists below m. Exact agreement with the V6
   route required on every shared quantity, k in {2..8} for both F and G.
4. Determinism and custody protocol: the executor emits a
   deterministic-content-only receipt; two runs on one host and one run on a
   second host must produce byte-identical receipts (sha256-pinned). Runtime
   and host facts are charged in separate RUNTIME_V1 records.

## Decision rule (stated before any run)

CONFIRMED (suspicion cleared, claim stands at original strength with this
receipt as its new strongest evidence) iff ALL of:

- D1 replication: re-run of the original campaign shows all_w4_boxes_green
  and equals the parent RESULT_V1.json on every semantic field
  (structured comparison, no field differs);
- D2 registered predictions: every F/fresh/extended prediction above matches
  measured values exactly;
- D3 negative control: G(k) shows the registered constant law (max_m=2,
  C*=4, flat=5, fixed-budget succeeds) for every k in {2..8};
- D4 independent route agrees exactly with the V6 route everywhere;
- D5 determinism: same-host rerun and cross-host receipts byte-identical.

Any failure REFUTES at a named stage (measurement / family-law /
custody-protocol) and triggers the revival chain (attribute one stage ->
lever -> retest at original strength); terminal only with a structural proof.

## Non-claims (inherited verbatim, unchanged)

```text
NEW_DOMAIN / J4
NEW_FORM_OF_INTELLIGENCE_PROVEN
atlas phase-hole occupancy
P4 surviving-unseen-domain (J4 gate)
```

The extended held-out set {6,7,8} and negative control are CORROBORATING
EVIDENCE for the claim at its registered scope F(k), k in {2,3,4}; they do
NOT widen the claim to k in {2..8}. Widening the registered family would
require a new freeze. Honest scope note: predictions for F({2,3,4}) and k=5
restate the parent registration (its outcomes are public in-repo, so those
legs are re-earnings under custody, not blind tests); the genuinely blind
surface is the extended held-out {6,7,8}, the negative control, the
independent route, and the determinism protocol.

## Claim ceilings on confirm (unchanged from the parent package)

```text
W4_RESIDUAL_QUOTIENT_STRUCTURAL_DOMAIN_AT_REGISTERED_FINITE_FAMILY_SCOPE
NOVEL_INTEL_LADDER_W2_W3_W4_GREEN_AT_EXACT_RQM_FAMILY_SCOPE
```
