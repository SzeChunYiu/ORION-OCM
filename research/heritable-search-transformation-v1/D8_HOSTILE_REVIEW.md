# D8 — Fresh-Context Hostile Review of the HST Capsule (V1)

- **review_id**: D8_HOSTILE_REVIEW_V1
- **reviewed branch head**: `58145bc0cab5e474622a5babec7a3789dc540761` (origin/centre/registry-integration-round2)
- **reviewer**: fresh-context hostile reviewer, work package D8 (issue #233); no allegiance to producing lanes
- **machine record**: `D8_HOSTILE_REVIEW_V1.json` (this file is its human summary)

## VERDICT: PASS_WITH_FINDINGS

7/7 checks PASS (0 FAIL, 0 UNCHECKABLE). No finding invalidates any row's
status; the census (12 PROVED / 3 FINITE_CERTIFIED / 2 PARENT_SUFFICIENT /
1 BOUND_DERIVED, 18 total, 0 OPEN) recomputes exactly. Two MED findings are
evidence-text/integration defects, not theorem defects.

## Findings

| # | sev | check | where | gap (verified against artifact text) | fix |
|---|-----|-------|-------|--------------------------------------|-----|
| 1 | MED | C1 | HST-T11 evidence.witness (registry + REGISTRY_PATCH_B) | Registry quotes "h=7: 21 vs 21.5 reject; h=8: 24 vs 24 boundary; h=9: 27 vs 26.5 promote" (3-op-slot accounting) but the cited receipt `exact/T11_MODULE_PROMOTION_V1.json` gives 14 vs 14.5 / 16 vs 16 / 18 vs 17.5 (2-op-slot unpromoted, `t11_module_v1.py` line 58). Threshold H*=8, net=1/2, flip-at-h=9 and h=8 tie identical under both accountings — status NOT invalidated; the registry misquotes its own receipt. | AMEND_3: re-quote receipt numbers or extend the frozen suite definition |
| 2 | MED | C1 | HST-T01/T03/T05/T06/T07/T18 | REGISTRY_PATCH_A fills `counterexample_when_assumption_removed` (a row_schema field) for all 6 lane-A rows; the integrated registry carries it for none of them (only T12–T17 have it). Drop undocumented in AMEND_1's change_scope. Content survives in `hostiles/W_T*.json` + exact_checker prose; check_core replays every witness — no status invalidated. | AMEND_3 field-fill restoring the six pointers verbatim from patch A |
| 3 | LOW | C2 | FREEZE_HST_V1 AMEND_1 patches_sha256 | 16-hex truncated prefixes (vs AMEND_2's full sha256) weaken chain binding to 2^64. Values DO match current patch files. | record full 64-char sha256 in future amendments |
| 4 | LOW | C6 | HST-T01 row field `secondary` | Undefined field ("HST-T01 P2(hostile)") absent from row_schema; byte-identical at the frozen commit 553cadd — freeze-intact leftover, not a lane edit. | document or remove in next declared amendment |
| 5 | LOW | C7 | exact/check_t12_v1.py, check_t13_v1.py | cwd-dependent cert output paths: exit 1 (FileNotFoundError) unless run from package root; check_t17 derives paths from `__file__` and is location-independent. Content unaffected (exit 0 from root; counts recomputed). | derive cert paths from `__file__` |

No HIGH findings. No-alarm cases (checked clean, recorded to prevent re-litigation):
run-manifest host `billy`/py3.8.10 is not this Mac mini (runners-off-Mac rule
respected as far as the repo can show); T09's vocabulary extension is documented
in evidence, not smuggled into the status field; bridge hooks all
protocol-shaped; frozen statements byte-identical across all three registry
states (18/18 rows, field-by-field).

## Per-check one-liners

- **C1 evidence existence + match — PASS.** All cited paths exist (find over
  proofs/ bounds/ exact/ hostiles/); all 7 claimed md5s match; all 4 RUN_ALL
  manifest sha256s match committed receipts; every cited md anchor exists; 15
  rows deep-read (spec minimum 8), incl. all 3 FINITE_CERTIFIED receipts and
  both PARENT_SUFFICIENT rows. Hand-verified: T02 Wald identity 80.25=321/4 and
  reach-vs-cost 47.06→66.89; T05 lifecycles 30/33, 16/31; T04 Kraft sums=1,
  ratio 32=2^5; T08 VoI=1/4<0.3; T12 counts 288/1114; T13 66=9+57, 120 total.
  Findings 1–2 above.
- **C2 sha-chain integrity — PASS.** Every checkable link recomputed with
  hashlib and matches: current registry = AMEND_2's registry_sha256_after;
  patch B sha256; AMEND_1 prefixes. All 5 historical links recovered by
  enumerating every commit touching the files (FREEZE@553cadd → cd454886…,
  FREEZE@76ec1cc → 7e383e5e…, REGISTRY@76ec1cc → e5e2b814…) — none
  UNCHECKABLE. Frozen statements untouched across all three states. Finding 3.
- **C3 hostile genuineness — PASS.** Per-row inventory: all 6 lane-A rows have
  machine-replayed W-witnesses that revive exactly the forbidden claim if
  removed (e.g. W-T01 M>0 reversal m 3→5; W-T06 false locality with R moving
  5→6); T12's k-bit counter attacks the #221 generalization directly; T13's
  hostile is the certified two-continuation construction itself; T14/T15/T16
  carry non-vacuous escape enumerations; T17 has the machine-certified tamper
  witness. FINITE_CERTIFIED hostiles are exact separations (T10: Ev 1/18 vs
  6/17). No PROVED row missing or vacuous.
- **C4 claim-ceiling discipline — PASS.** T02/T10/T11 each carry at_scope
  (FW1 named) + claim_ceiling with explicit "P2 finite exact != general"
  language, repeated in the receipts' scope_statement. T04 "no new mathematics
  claimed"; T08 "Blackwell owns the dominance theorem". LITERATURE_LEDGER OWNS
  entries consistent. T09 honestly reports VACUOUS AT ZOO SCOPE (0.6242 vs bar
  0.2245) rather than laundering it. No row asserts beyond its ceiling.
- **C5 bridge consistency — PASS.** 18/18 bridge statuses == registry (0
  mismatches); coverage 145:4, 151:4, 217:4, 221:6; all hooks
  measurement-protocol shaped with FW1-only status labeled; no FW1-finite
  result presented as general; registry_ref shas resolve.
- **C6 vocabulary + census — PASS.** All 18 statuses in the 6-value vocabulary;
  AMEND_2 census matches head registry exactly; AMEND_1 census matches registry
  at 76ec1cc exactly. Finding 4.
- **C7 reproducibility spot-run — PASS.** Pure stdlib; on this host
  (/usr/bin/python3 3.9.6): run_all_v1.py exit 0 (0.014s, 4 receipts +
  manifest); check_core exit 0 ALL CHECKS PASSED matching the committed laptop
  log verdict-for-verdict; check_t12 exit 0 (288 maps); check_t13 exit 0;
  check_t17 exit 0 WITNESS_CERTIFIED; bounds/check_bound_v1.py exit 0 incl.
  part (d) reproducing the registry's exact vacuity numbers (0.6242, m*=104,
  564). Regenerated receipts byte-identical modulo host/runtime stamps; tree
  restored clean afterward. Finding 5.

## Method notes

Every absence claim was checked with `find` (not a single empty grep); every
git decision used `/usr/bin/git` (bypassing the token-filter proxy); every
historical hash was recomputed from git-blob bytes, not read from the ledger
and trusted. Checker re-runs that rewrote committed receipts were reverted
with `/usr/bin/git checkout --`; the reviewed tree is byte-identical to the
reviewed head except for the two NEW files this review adds.
