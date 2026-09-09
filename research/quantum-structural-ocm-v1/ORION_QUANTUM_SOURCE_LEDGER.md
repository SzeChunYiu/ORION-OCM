# ORION Quantum/QG Source Ledger — issue #216 section 2 (donor recovery)

Source ledger for `[FNA-Q1]` SzeChunYiu/ORION-OCM#216. Every identity below was verified this
session by gh issue reads (full bodies + comments) and read-only `/usr/bin/git` inspection of the
local ORION checkout at pinned commits and at `origin/main = 1b6f767ea`. Machine-readable detail,
verbatim quoted terminals/numbers and comment URLs: `ORION_QUANTUM_SOURCE_LEDGER.json`.

Status key: **CLOSED+merged** = issue closed with merged material evidence bound below.
**OPEN/unmerged** = candidacy or coordination text only, no earned artifact.

## Binding table

| Donor | ORION issues | Primary bound artifacts (path @ pin → main blob) | Status |
|---|---|---|---|
| FQ-1 query-indexed abstraction | #904, #908, #911 | `QG31_QUERY_INDEXED_ABSTRACTION_RESULTS.json` (main add af7163662 → 39234e2cfd06); `MAX_R4EA_AUTHORITY_INDEXED_ROUTER_RESULTS.json` @962e9d264 → defcc04eab70; `QG22_COMPLEXITY_SEPARATION_RESULTS.json` (c756b29f8 → c15dd814cc) | CLOSED+merged |
| FQ-2 separating probes + adaptive tree | #911, #924, #933, #942, #914 | `QG32_MIN_SEPARATING_PROBES_RESULTS.json` @33bf62e54 → df0d8def4aee; `QG34_ADAPTIVE_PROBE_TREE_RESULTS.json` (welded on main → 13a1a2803; canonical via correction receipt, sealed blob 61ad64ed0); `QG34_PROTECTED_RUN_RECEIPT_2026-08-22.json` @4ff87a97a → b8476763f83d; `QG35_…`, `QG32C_…` (demoted); `QG39_SELECTION_REGRET_RESULTS.json` (2589801ac → ff3ed811c4); `MAX_R4EB0_HELDOUT_QG32_RESULTS.json` @9a9ab3a84 → 5e3d15d89d9c; retraction docs (2589801ac → e8dd0f4918b5 / 66ab32a5f9a7) | CLOSED+merged, **headline retracted** |
| FQ-3 bounded-defect localization | #886, #903 | `QG27_BULK_DEFECT_RESULTS.json` (af7163662 → e015cec136); `QG23_AUX_SUPPORT_COMPACTNESS_RESULTS.json` → 7d50e3e92e8; `QG26_NERODE_MINIMALITY_RESULTS.json` → 4a2581c35029; `QG29_DEFECT_SATURATION_RESULTS.json` → 648bb0ec6c4f | CLOSED+merged |
| FQ-4 resource responsibility | #903, #839 | `QG21_FT_CHEMISTRY_RESULTS.json` (c756b29f8 → 041045985496); `QG21_REGIME_ROBUSTNESS_RESULTS.json` (present on main); `MAX_R4E_QG_SKILL_REPLAY_RESULTS.json` @3b594a326 → 2a418b5b2673 | CLOSED+merged |
| FQ-5 anti-overcompression | #893, #904, #903 | `QG30_BULK_COARSE_GRAIN_RESULTS.json` @645fd9290 → 4de0a0a9e980; `QG15B_PREDICATE_LANGUAGE_RESULTS.json` → 6efedd0942e6; retraction pair as above | CLOSED+merged |
| FQ-6 safe equivalence/symmetry | #888, #1034 | `QG28_LOCAL_CLIFFORD_ORBIT_RESULTS.json` (af7163662 → 271349b476e); `QG34_ADAPTIVE_PROBE_TREE_RESULTS_CORRECTION_RECEIPT_V1.md` (9291bc6a7 → 2de63fe9a60b) | CLOSED+merged |
| FQ-7 RG invariant tuple + RG-F0 | #894 → #1383/#1384/#1396 | `papers/PAPER_PORTFOLIO_REFACTOR_PLAN_V1.md` (f58c1b3dc → 9c1eb53f33bc); `V1_ISSUE_DISPOSITION_LEDGER_V1.json` (9291bc6a7 → b701930a93b). **No RG result receipt exists — tuple bound to frozen issue text only** | CLOSED superseded, unexecuted; successors OPEN |
| FQ-8 census + transfer boundary | #1359, #1362, #903, #839 | `V1_QUANTUM_CENSUS_V1.json` (9291bc6a7 → 95c4af5fbaf); `ORION_QG_PROGRAMME_SCIENTIFIC_CLOSURE_RESULTS.json` (aac06e593 → 7d5d63fb6989); `EXECUTION_PACKET_V1.json` blob 23f6f15b @lane commit 5aa84b52c only (**not on main**) | #1359 CLOSED coordination; **#1362 OPEN, no artifact** |

## Per-donor summaries

**FQ-1 — query-indexed abstraction ladder.** QG-31 (issue #904, PR #905) machine-checked three
exact observation partitions over 715 TARE local-Clifford orbit types: bulk 45 / defect-spectrum
54 / indexed response 715, with the two cheap partitions *incomparable* and jointly insufficient
(explicit witness in receipt). QG-22 (PR #892) separately established the exact DP referee is
affine in n from a fixed 9-bit syndrome — and that evaluating the closed form costs O(n^6), more
than the referee it characterizes. MAX-R4E-A (#908) then demonstrated the OCM-shaped function
inside ORION on real receipts: authority-indexed routing 10/10 correct, 0 false authority, 7/7
safe compressions captured, per-query representation sizes [45, 54, 715, 715]. Transfer target:
`DecisionSufficientState`.

**FQ-2 — separating probes + adaptive tree, WITH retraction scope.** QG-32 (#911) certified a
deterministic 5-probe fixed set [18,68,101,181,139] separating all 715 identities after joint
summaries — *upper-bound only* (HiGHS time-limited; minimum stays null). QG-34 (#924) earned
D_*=3 exact minimax adaptive depth with a depth-2 infeasibility certificate. **Then the internal
adversarial referee retracted the headline** (retraction landed on main via PR #926): 85/92 and
708/715 are histogram identities; D_*=3 < F_*=4 < U_*=5 and the regret curve are reproduced by a
row-shuffle null; D_*>=3 is forced by class sizes + max arity 6; QG35/QG35b/QG36/QG39/QG32c were
demoted to internal notes. What survives: all arithmetic, U_*=5 by enumeration, and one genuine
residual (depth distribution {0:7,1:30,2:39,3:16} vs null {0:7,1:42,2:34,3:9}; budget-2 regret
2-vs-1). Transfer: probe-set construction + minimax stop-rule transfer; the separation claim
does NOT; every OCM "adaptive beats fixed" claim must carry a shuffle-equal-n null. QG-34's main
JSON is identity-welded — bind via the correction receipt (canonical: `QG34_EXACT_MINIMAX_
ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED`, digest 7c48f505…).

**FQ-3 — bounded-defect localization.** QG-27 (#886): exact optimum = additive bulk + O(1)
defect, uniform band `B_min(N)-34 <= C_DP(N) <= B_min(N)+8` for all N, constants explicitly
non-sharp; QG-29: defect potentials clip at k=6, scaling rays affine by k=43 (onset bound
universal, `K43_SHARP_FOR_REAL_TARE=false`); QG-23/QG-26 companions. Transfer: `LocalDefectSubspace`
plus the "prove saturation before extrapolating" rule for cached models on growing inputs.

**FQ-4 — resource responsibility.** QG-21 (PR #892): the support-weight objective O1 is *not
derivable* from FT accounting — physics charges T per arbitrary-angle rotation, every family
member carries exactly nine, so the T ratio between members is exactly 1 and studied geometry
moves under 1% of audited FT cost (delta_max 2 vs T backdrop 270–900). #903's S6 distills it:
"exactly solve the cheap inner problem, but do not confuse inner optimality with end-to-end
method value." MAX-R4E replay shows the positive side: certificate-aware stopping avoided
~10^7–10^8 search nodes on three real compiler families (replay-only). Transfer:
`ResourceResponsibilityMap` — already substrate-independent governance, the easiest honest lift.

**FQ-5 — anti-overcompression / missing coordinate.** QG-30 (#893): the 715→45 bulk coarse-
graining is exactly sufficient for asymptotic density yet *provably lossy* for finite defects —
54 one-active profiles, 15 splitting bulk signatures, first witness (IIIIXX, IIIIXY) sharing
bulk (2,2,2,2) with divergent K-histograms. QG-31 adds the third witness: same bulk + same
spectrum + different indexed response. The retraction contributes the falsifier discipline:
"X is not determined by Y" claims need a null because non-determination is generic. Transfer:
the `REPRESENTATION_INSUFFICIENT__MISSING_COORDINATE_FOUND` terminal and the mandatory hostile
for every OCM quotient.

**FQ-6 — safe equivalence/symmetry.** QG-28 (#888): per-qubit local-Clifford S3 quotient
4096→715 is exact *because verified* — 1,572,864 active canonicalization rows, 0 mismatches,
cost digests equal before/after; the tempting globally-coupled per-column position quotient is
explicitly vetoed (`INDEPENDENT_POSITION_RELABEL_PER_COLUMN=false`). The QG-34 correction receipt
(#1034) adds identity-layer hygiene: duplicate JSON keys silently selected an authority state;
repair = distinct named fields per layer + strict duplicate-key rejection. Transfer: every OCM
equivalence needs query-relative scope + active invariance verification + veto records; OCM
authority files need strict duplicate-key loaders.

**FQ-7 — RG-0 invariant tuple + RG-F0 (discovered).** #894 froze a 9-coordinate invariant tuple
(d_sem, kappa, a_cert, N_label, N_value, T_*, K(theta), rho_cert, lambda_crit) and an implication
matrix of six tempting-but-false implications (bounded d_sem ⇏ bounded kappa; …; local
certificate arity ⇏ cheap global optimization), with "no finite-domain observation may
self-promote to all-instance authority". Never executed; closed as superseded into the NQ lane
(#1383/#1384/#1396, OPEN). Transfer: the typing skeleton for OCM quotient claims and the
falsification matrix for any "compression implies X" OCM claim — as *design controls only*,
never as earned theorems.

**FQ-8 — census + transfer boundary (discovered).** #1359's census (56 scoped issues, merged,
with per-issue evidence verified at frozen base ef51b7b and origin/main) and its claim boundary:
quantum structure may donate quotient-state/syndrome/noncommutation/resource-monotone/tensor/
adaptive-measurement/phase-boundary/recovery mechanisms; it grants no advantage, physical
validity or novelty. #1362 (OPEN, no artifact of its own) adds contextuality as a warning
against globally sufficient scalar state. #903's Discovery V2 registration freezes the
fail-closed transfer protocol (relation-preserving correspondence, target-native validator,
donor-first refusal, matched resource contract, `quantum_scientific_authority_transfer=
FORBIDDEN`) — effectively #216's transfer rule, already frozen in ORION. Reuse verbatim.

## Surprises recorded for the sibling agents

1. **The fixed-vs-adaptive headline is retracted.** Any FQ-2 transfer must lead with the null
   model, not with 3 < 4 < 5.
2. **The most OCM-shaped donors are already classical in ORION.** MAX-R4E-A/B0 and the replay
   results are receipt-level classical research-control mechanisms; QG-21's S6 lesson is
   governance, not physics. The classical-parent map should treat these as in-family parents.
3. **Phantom census path**: `QG39_POST_NULL_RESIDUAL_RESULTS.json` is cited by the merged census
   but exists nowhere in the local object store; the residual numbers are bound via the
   retraction doc instead.
4. **Squash-merge pinning**: lane-intro SHAs cited in issue comments are rarely main ancestors;
   bindings pair lane SHA with byte-identical main blobs (checked per artifact).
