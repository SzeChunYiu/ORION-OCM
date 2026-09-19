# RESPONSES_V1 — authors' response to the five hostile-review reports (Z18 round 1)

Reports answered: `proxies/PX-Z18-THM.verdict.txt`, `PX-Z18-EXP.verdict.txt`,
`PX-Z18-LIT.verdict.txt`, `PX-Z18-STAT.verdict.txt`, `PX-Z18-COG.verdict.txt`.
Every objection a reviewer marked `material: yes` is answered below with exactly one
disposition:

- **RESOLVED** — the objection rests on a misreading or on an artifact the reviewer was not
  permitted to open; the evidence is quoted here with its repository path.
- **DOWNGRADED** — the objection is correct and the claim is weakened; the new wording is
  registered in `CLAIM_DOWNGRADES_V1.json` under the id given.
- **OPEN** — the objection is correct and cannot be discharged by a response; the repair is
  registered as a revival target (`revival` field in `CLAIM_DOWNGRADES_V1.json`) and the gate
  the reviewer named is reopened in `REOPENED_GATES_V1.json`.

"We will fix it later" is never written as RESOLVED. Every REOPEN demand in every report is
honoured in `REOPENED_GATES_V1.json` regardless of the disposition below. Non-material
objections are acknowledged in section 7 without a disposition.

The authors here are the lane, not the original package authors; where the lane checked a
number itself the check is stated.

---

## 1. Claim C1 — the state-class choice law (finite scope + real-system extension)

### Finite law (heldout-20, Z15 falsifiers)

| id | disposition | response |
|---|---|---|
| THM OBJ-1, LIT OBJ-C1-C | DOWNGRADED → `DG-C1-F1` | Correct. `F1` as frozen compares argmin classes at the two endpoints `lambda*/2`, `3lambda*/2`, so any boundary `r·lambda*` with `r ∈ (1/2, 3/2)`, `r ≠ 1` reproduces both endpoint predictions and survives. The Z15 disclosure records exactly this: "57 survivors realizing 12 distinct multipliers" for `F1` and `200/200` only for `F1PLUS-DEC`, "the revival" (`research/gmi-833-z-z15-decisive-falsifiers-v1/PARENT_DISCLOSURE_V1.md` lines 32–36). The frozen target "0/200 surviving" was not met by `F1`; it was met by the boundary-inclusive successor. The claim is restated accordingly; the unreconciled register is a revival target. |
| THM OBJ-7 | DOWNGRADED → `DG-C1-STATEMENT` | Correct. The mathematics is the exact argmin of `J = eta·E + lambda·state_bits` over the fixed 65,552-candidate universe; "which morphology a resource-bounded search will select" says more than that. New wording: "which class an exact minimiser of `J` over the registered finite universe selects". |
| THM OBJ-8, EXP OBJ-13, STAT OBJ-S6 | DOWNGRADED → `DG-C1-20CASES` | Correct. All 20 held-out cases fix `lambda_low/lambda* = 1/2`, `lambda_high/lambda* = 3/2`; the outcome depends only on that ratio, so the 20/20 and 40/40 counts are one entailed derivation instantiated across a `(p, eta)` grid, and two exact search procedures agreeing is a software cross-check. `HELDOUT_TRANSITION_FORMALIZATION_V1.md` §5 already says "not independent-team replication or real-system validation"; the success-register wording is weakened to match. |
| THM OBJ-9, LIT OBJ-C1-B | DOWNGRADED → `DG-C1-F4` | Correct. `T_b` (common rescaling of `eta` and `lambda`) is a degree-1 homogeneity of `J`; `T_a` (identifier permutation) leaves semantics fixed. Neither can fire against a correct implementation, so `F4` tests implementation invariance, not theory invariance; the planted positives establish only that the checker is not constant-False. |
| THM OBJ-10 | DOWNGRADED → `DG-C1-F3` | Correct that no sharpness or non-abstention requirement is registered. Partly a permitted-set artefact: abstention rates are disclosed beside the coverage figures — "each reported beside its abstention rate (`121/162`, `439/640`)" (`research/gmi-833-capability-predictor-evaluation-v1/CORE.md` line 45) — but a containment-only falsifier with no informativeness floor remains one a maximally wide predictor passes. `F3` is restated as containment-only. |

### Real-system extension (`gmi-833-real-transition-receipts-v1`)

| id | disposition | response |
|---|---|---|
| THM OBJ-2, EXP OBJ-5, EXP OBJ-6, STAT OBJ-S1 | OPEN → `RV-C1-BAND` | Correct. `FREEZE_V2_AMENDMENT.md` A4 derives "licensed iff `1/8 < E0 < 3/8`" from the same inequality that yields the predicted outcome; a licensed system cannot produce the wrong direction, only abstain. The upper edge `3/8` is unreachable when `err_imm ≈ 0` forces `E0 ≈ floor_del/2 ≤ 1/4`, so every exclusion is on the low side. No response fixes this; the terminal `REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE` is reopened and the repair (admission criterion independent of the outcome; two-sided threshold control) is registered. |
| THM OBJ-3 | DOWNGRADED → `DG-C1-UNLICENSED` | Correct. A4 says "predictions apply only to licensed systems"; CORE.md's "correctly predicted NOT to transition" re-imports excluded systems as confirmations. Withdrawn: unlicensed systems are out of scope, not evidence. |
| THM OBJ-4, EXP OBJ-8 | DOWNGRADED → `DG-C1-BLIND` | Correct. A3 keys `STATELESS`/`PERSISTENT_STATE` on `B == 0` / `B > 0`; in a two-candidate pool `B` is a one-to-one proxy for the family. The classifier is blind to family *names*; it is not blind to the morphology variable, which is its input by design. "Family-blind" is restated as "name-blind". |
| THM OBJ-5, THM OBJ-6, EXP OBJ-1, STAT OBJ-S2 | OPEN → `RV-C1-GRID` | Correct, and the lane verified it: `FREEZE_V1.md` line 38 writes `lambda*_s = p_s*eta_s/(2*B_s) = p_s/(8*H_s)` with `eta = 1/2`, `B_s = 4H_s`; evaluating the first expression gives `p/(16H)`, so the second equality is an algebra error, and the worked grid at line 80 ("R01: `8/(8*32) = 1/32`; `lambda_low = 1/64`, `lambda_high = 3/64`") follows the error. The receipts execute the law-correct value (`lambda_star = 1/64`, prices `1/128`, `3/128`) while the amendment calls the grid "unchanged". Because the measured `E0` (0.187–0.240) lie in `(1/8, 1/4)`, the low-endpoint prediction holds under the executed grid and fails under the numerically registered one. The outcome is grid-dependent and the prediction-of-record is self-contradictory; `lambda*` was also not re-derived when the `1/2` floor was retracted (A5). Cannot be discharged by a response. |
| EXP OBJ-2, EXP OBJ-3, STAT OBJ-S3, STAT OBJ-S4 | DOWNGRADED → `DG-C1-TIE` | Correct. On all five receipts `boundary_tie_control.winners == ["c1"]`, the `B = 0` candidate, so stateless wins strictly at `lambda*`; from A4 the true crossing is `p·E0/B ≈ 0.75–0.96·lambda*`, inside the interval the Z15 package itself proves the endpoint design is blind to. This is a failed prediction of the boundary point on real systems and is registered as such (`FP-REAL-TIE`), not as a control. The real-system claim is downgraded to direction-only within a 3× bracket. |
| EXP OBJ-4, STAT OBJ-S10 | DOWNGRADED → `DG-C1-REPRICE` | Correct that no retraining occurs between endpoints — `FREEZE_V1.md` §5 "Same trained candidates serve both lambda settings (lambda reprices only)" — so what is observed is one candidate pair repriced, not a transition in a trained population. The wording "transition" is replaced by "repricing crossover". The `resources_after` field recording the persistent candidate's `[B, params, seconds]` under `observed_after_property: STATELESS` is a receipt defect and is carried in `RV-C1-RECEIPT-FIELDS`. |
| EXP OBJ-9 | RESOLVED | R07 and R08 are registered in `research/gmi-833-real-transition-receipts-v1/FREEZE_V3_ADDENDUM.md` (lines 24–25: "R07-frankenstein | Project Gutenberg ebook #84 …", "R08-dict-words | /etc/dictionaries-common/words …"), committed at `c03eb646e` per CORE.md custody item 5. The addendum was outside the reviewer's permitted set. The separate point that the addendum postdates the V2 outcomes is answered under EXP OBJ-10. |
| EXP OBJ-10, STAT OBJ-S5 | DOWNGRADED → `DG-C1-TRANCHE` | Correct. Twelve systems were run to obtain five qualifying receipts, and the V3 tranche was "text-weighted" toward the source class V2 had shown lands in band; no stopping rule or multiplicity accounting was registered. The claim is restated with the recruitment disclosed and no error rate asserted. |
| EXP OBJ-11 | RESOLVED | The amendment's commit is pinned in `research/gmi-833-real-transition-receipts-v1/CORE.md` custody item 3: "`FREEZE_V2_AMENDMENT.md` @ `c3fbf5b11`". The receipts' `prediction_ref` string omits the hash; the pin exists in the package. Carried as a field-hygiene item in `RV-C1-RECEIPT-FIELDS`. |
| EXP OBJ-12 | DOWNGRADED → `DG-C1-REALMEANS` | Correct. The systems are a four-cell lookup MLP and a size-16/32 GRU trained a few epochs on one file's bytes with train and eval from the same file. "Real system" is restated as "torch-trained small network on a real byte source", never "deployed system". |
| EXP OBJ-14 | RESOLVED | The outcome artifact exists: `research/gmi-833-heldout-20-transitions-v1/RESULT_V1.json` (`schema: GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1`, `freeze_commit: ddb3df7a44a6a4fb47fdc362a1fa02e34b7a3a75`, `verdict: GREEN`), outside the reviewer's permitted set. Whether the 20 cases constitute independent tests is answered under THM OBJ-8. |
| STAT OBJ-S8 | RESOLVED | All twelve systems' run artifacts are committed under `research/gmi-833-real-transition-receipts-v1/REAL_RUNS/` (`R01-gutenberg-1342/` … `R12-rearleft-wav/`, including the unlicensed `R02-alsa-frontcenter/`, `R03-python38-binary/`, `R12-rearleft-wav/`). `RECEIPTS_V1.json` holds only the five counted receipts by design. |
| STAT OBJ-S9 | OPEN → `RV-C1-SEEDS` | Correct. `seed_spread_err_all = 0.0` for both candidates in all five receipts and the dispersion of `floor_del` over seeds is not reported, so the 3-sigma gates carry binomial-at-fixed-model uncertainty only. Requires a re-run with seed dispersion reported. |

## 2. Claim C2 — capability-interaction partition CIP-1 … CIP-4

| id | disposition | response |
|---|---|---|
| THM OBJ-13 | DOWNGRADED → `DG-C2-LEMMA-B` | Correct. §0 says "Lemmas A, B and C are SOUND and are not weakened here" and "the defect is confined to the naming/classification layer", while §4 (CIP-4) proves the shipped `iff` directions of Lemma B need strict positivity (P) and exhibits a measure under which "the iff nested direction fails". The correction scope is widened: the shipped Lemma B is false as an unconditional `iff`; it is true under (P), which counting measure satisfies. |
| LIT OBJ-C2-A | OPEN → `RV-C2-PARENT` | Correct. The `(max, joint, sum)` trichotomy CIP-1 performs is the object of the cooperative-game interaction index (Grabisch & Roubens 1999, doi:10.1007/s001820050125) and neither §6 nor `PARENT_OWNERSHIP_V1.md` (Nemhauser–Wolsey–Fisher, Lovász, Edmonds, Amdahl) names it. Assimilation of that parent is a supplement to the CIP package, not a response. |
| LIT OBJ-C2-B | RESOLVED (partially) | `research/gmi-833-capability-interaction-partition-v1/PARENT_OWNERSHIP_V1.md` exists and lists four Crossref-resolved DOIs (lines 29–32; line 35 "All four DOIs above were resolved against the Crossref API"). The file was outside the permitted set, so "cannot be certified" is answered; the missing interaction-index parent is a separate, open item (OBJ-C2-A). |

## 3. Claim C3 — foundation descent stack AG1 / AG8

| id | disposition | response |
|---|---|---|
| THM OBJ-17 | DOWNGRADED → `DG-C3-AG1-4` | Correct, and verified by the lane on `FOUNDATION_DEPENDENCY_DAG_V1.json`: over all 37 arrows the symmetric `MUTUAL_INTERPRETATION` pair `FND_SET_RELATION ↔ FND_TYPED_ALGEBRAIC` is a 2-cycle and there are 5 sinks; over the 35 non-`MUTUAL_INTERPRETATION` arrows there are 0 cycles and 7 sinks (the 5 plus the two F0 foundation-style nodes). AG1-4's "0 cycles" and "5 apparent bottoms" therefore quantify over different arrow sets under one name. Restated with the arrow set named in each clause. The same finding is independently proved in `aa15_targets/S3_ag1_descent_acyclicity.lean` (PX-AA15). |
| THM OBJ-18 | DOWNGRADED → `DG-C3-AUTHORED` | Correct. AG1-1/-2/-4 verify the internal well-formedness of an authored registry ("presence-of-field plus pinned blob sha, not re-derivation of the parent's mathematics"). Restated: the layer-monotonicity results are properties of the registered labelling, not of the programme's mathematics. |
| THM OBJ-19 | DOWNGRADED → `DG-C3-AG1-5` | Correct. AG1-5's consequence is stated universally while its assumptions say the F0–F5 identity "is not independently re-verified layer by layer here". Restated: at the registered matched pair, with layer identity taken from the registry. |
| THM OBJ-20 | DOWNGRADED → `DG-C3-AG8-CHECKS` | Correct. AG8's eight "machine-checked obligations" are presence, resolution, non-emptiness and file-existence checks, which cannot distinguish a discharge from a placeholder; and `check_aj13.py` audits a hand-written baseline literal and writes GREEN as a constant (also found by PX-AG8-A OBJ-1 and PX-AG8-B OBJ-1). Restated: AJ13's GREEN is the predicate's self-consistency on an authored instance, not an evaluation against the registry. The gates are reopened. |
| LIT OBJ-C3-A, OBJ-C3-B, OBJ-C3-C | OPEN → `RV-C3-LEDGER` | Correct on all three: Kahn 1962 owns topological sorting, not arrow typing; foundational pluralism and the `MUTUAL_INTERPRETATION` / `FREE_CONSTRUCTION` arrow kinds carry no citation; the READ/EMIT/INC/DECJZ/HALT repertoire's earliest parent is Shepherdson & Sturgis 1963 (doi:10.1145/321160.321170), not Minsky 1967. The ledger is a frozen artifact of another package; correction lands as a supplement there. |

## 4. Claim C4 — exact capability predictor evaluation

| id | disposition | response |
|---|---|---|
| EXP OBJ-16 | OPEN → `RV-C4-CUSTODY` | Correct as disclosed by the package itself: the pre-V4 census emitted only degenerate points and every non-degenerate emission comes from the stratum whose evaluator "already existed at 50451f23". Custody of KE-1/KE-2 is inverted for the emissions that carry the result; a response cannot restore it. |
| EXP OBJ-17 | DOWNGRADED → `DG-C4-BLIND` | Correct. `BLINDNESS_V1.md` §1 says `ARCH_LABELS` is "a third, separate sequence that no predictor path ever touches" and §3 permutes exactly that sequence, so the 24-permutation check cannot fail; the live channel `ARCH_RAW` is never permuted. Restated: labels are unused by construction; channel-level blindness is untested. |
| EXP OBJ-18, STAT OBJ-S12 | DOWNGRADED → `DG-C4-KE6` | Correct. KE-6's coverage is an exact enumeration under a stipulated fault law with betas `(1/100, 1/200, 1/500, 1/50)` of no stated empirical basis, compared to a bound built from the same betas. Restated: KE-6 verifies union-bound slack under the registered fault law; it is not empirical calibration. |
| EXP OBJ-19, STAT OBJ-S13 | DOWNGRADED → `DG-C4-KE7` | Correct. In-universe violations are excluded by construction and out-of-universe errors are pre-declared non-findings, so KE-7 has no outcome that counts against it. Restated: KE-7 reports in-universe consistency only; the OOD failure rate the row is named for is not reported. |
| EXP OBJ-20 | OPEN → `RV-C4-KE4` | Correct. No confusion-matrix result appears in the permitted artifacts and the largest stratum's mismatches are pre-excused. Requires the matrices to be produced and committed. |
| EXP OBJ-22 | OPEN → `RV-C4-SOLVED-RULE` | Correct. `REAL_MEASURED_V3.json` carries both "exact accuracy >= 99/100" and "== 1" as solved-rules with one head (GRU|32|1|2 at 124/125) between them; the recorded solved set depends on which rule is applied. Must be resolved in the outcome file, not by response. |
| EXP OBJ-23 | OPEN → `RV-C4-COUNT` | Partly a permitted-set artefact — three run directories exist (`REAL_RUNS/`, `REAL_RUNS_V2/`, `REAL_RUNS_V3/`) — but the lane did not reconcile "96 systems / 288 heads" against their contents and does not assert it here. |
| EXP OBJ-24, STAT OBJ-S17 | DOWNGRADED → `DG-C4-DENOMINATORS` | Correct. Denominators such as 161,632, 45,800, 121,920 and 24,912 are cross-products of a small number of distinct machine measurements against registered worlds, not independent trials; exact arithmetic removes rounding, not correlation. Restated with the number of distinct measurements beside each denominator. |
| STAT OBJ-S11 | OPEN → `RV-C4-POINT-COVERAGE` | Correct. `SCOPE_V1` commits to point-emission-only coverage "(the harsh test)"; only pooled coverage at 69–75% abstention is reported. Requires the point-only figure to be computed. |
| STAT OBJ-S14 | DOWNGRADED → `DG-C4-KE3` | Correct. SU-KE3's "0 of 161,632" conditions on registration truthfulness decided by comparison with the measured outcome, which held on 19/32, 28/32, 26/32 of real systems. Restated as conditional on truthful registration, with the truthfulness rates attached. |
| STAT OBJ-S15 | OPEN → `RV-C4-NULL` | Correct. `NULL_MODAL` is evaluated only where F emits a point and is arithmetically forced to miss non-degenerate values; no abstention-matched or structural-descriptor null is tested. Requires a new null run. |
| STAT OBJ-S16 | DOWNGRADED → `DG-C4-KE3D` | Correct. 28 versus 26 at n = 32 is under one binomial standard deviation, so the "optimisation threshold rather than a missing clause" diagnosis is withdrawn; KE-3D stands only as "three registered laws falsified by their own falsifiers". |

## 5. Claim C5 — theory baseline A1 … A14, §3, failed-prediction register

| id | disposition | response |
|---|---|---|
| THM OBJ-22 | DOWNGRADED → `DG-C5-LEMMA-B` | Correct; same finding as THM OBJ-13. `BASELINE_V1.md` §3 calls Lemma B's characterisation "unconditional (inclusion-exclusion)"; CIP-4 shows the `only if` directions require (P). Restated. |
| THM OBJ-23 | DOWNGRADED → `DG-C5-A5-A14` | Correct. A5 ("No unsupported overclaim remains") and A14 ("CI-U … at re-earned full strength") are contradicted by the CIP package's correction of the same GREEN object (56/351 false labels, 287/351 non-unique, a falsifier that "cannot return False"). Restated: A5 → "no overclaim was flagged by the 283-flag screen; the revived object was subsequently corrected"; A14 → "CI-U's lemmas hold under (P); Corollary CI-A4's classification is superseded by CIP-1 (217/351 labels change)". |
| THM OBJ-24 | DOWNGRADED → `DG-C5-A7` | Correct, and verified by the lane: `research/gmi-833-claim-discipline-v1/RESULT_V2.json` records `"objects": 235`, `"field_slots": 1175`, `"registered_gap_v2": 0`; A7 names five fields (scope/quantifiers, assumptions, falsifiers, strongest parents, forbidden extrapolations) and `1175 = 235 × 5`. The word "six" is a miscount in the prose; the registration is complete for five fields. Restated. |
| THM OBJ-25 | DOWNGRADED → `DG-C5-A7-FIELDS` | Correct. A7 certifies field population, and DEF-3 shows a populated falsifier field that could never fire. Restated: A7 measures registration completeness, not falsifiability. |
| STAT OBJ-S18 | DOWNGRADED → `DG-C5-FPR` | Correct. Of the six register entries, `FP-SHIFTED-BOUNDARY` is a designed control, `FP-REV-OPEN` and `FP-939-OVERSTRONG` are obligation pointers and `FP-Z12-CAL-V1` an instrument repair, leaving two discovered failures; the F1 57/200 blindness, the retracted uniform-`1/2` floor and the real-system boundary-tie discrepancy meet the register's own kind definitions and are absent. The headline is restated and the three missing negatives are registered (`FP-F1-BLIND`, `FP-FLOOR-HALF`, `FP-REAL-TIE`) in the downgrade register pending a supplement to the frozen register. |
| STAT OBJ-S19 | DOWNGRADED → `DG-C5-A5-A14` | Correct. A5 is an absence claim from 283 flags over a 22,553-object corpus with 22,116 un-sampled; no false-negative estimate exists. Covered by the A5 restatement above. |
| STAT OBJ-S20 | RESOLVED | The null family is characterised in the grammar-growth package: "0/200 equal-size random-admission nulls beat the true recursive library (empirical rank 1)" (`research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V2.json`, `new` line) and `GRAMMAR_GROWTH_THEOREMS_V1.md` line 98. The blind-set characterisation the reviewer asks for is not reported there either; that part is carried as `RV-C5-A12-NULL`. |
| LIT OBJ-C5-A, OBJ-C5-B, OBJ-C5-C | OPEN → `RV-C5-CROSSWALK` | Correct on all three (Wikipedia-mediated VERIFIED marks on rows 1, 10, 29, 32; row 48 self-citation marked EXACT; row 33's Karp-reduction citation for a methodology practice). The same defects are found independently by PX-AC05-B (rows 16, 19, 21, 23, 34, 41, 47, 48 without an externally checkable citation). AC05 stays open; the crosswalk's citation-status field is reopened. |
| LIT OBJ-C1-A | OPEN → `RV-C1-PARENT` | Correct. The Z15 parent table discloses methodology parents only; the memory-pricing parent class the programme cites at crosswalk rows 5 and 25 is absent from the law's own disclosure. Requires a supplement to the Z15 disclosure. |
| LIT OBJ-C4-A | OPEN → `RV-C4-PARENT` | Correct. The result governing the parity failure — non-SQ-learnability of parity (Kearns 1998, doi:10.1145/293347.293351) — is omitted in favour of two RNN-precision papers. Supplement to the capability-predictor disclosure. |

## 6. Claim C6 — natural-intelligence bridge

| id | disposition | response |
|---|---|---|
| COG OBJ-1 | OPEN → `RV-C6-FUNCTION` | Correct. All seven registry rows carry `phase_winner: "neural"` and no artifact states a function from `(E, R, V)` to the `C_pred` descriptor values. Without that function the profiles are not derived predictions. |
| COG OBJ-2 | OPEN → `RV-C6-HOLDOUT` | Correct. Every `D_holdout.content` is `null` and no unsealing protocol is named, so the registered falsifier cannot fire. |
| COG OBJ-3 | OPEN → `RV-C6-OPERATIONALISE` | Correct. The ordinal descriptor values are tied to no task, measure or threshold, so "contradicts on ≥2 descriptors" cannot be adjudicated. |
| COG OBJ-4 | OPEN → `RV-C6-SATURATION` | Correct. `BIOLOGICAL_BRIDGE_CONTRACT_V1.md` requires a biology-literature saturation pass before any `C_pred` is frozen and records it "Not started", yet `PREDICTIONS_REGISTRY_V1.json` freezes the corvid/rodent rows. Either branch voids `C_pred_frozen_pre_phenotype`. |
| COG OBJ-5 | DOWNGRADED → `DG-C6-NO-NEURO` | Correct. `FINAL_TARGET_NATURAL_HALF_THEOREM_V1.md` §5.3 composes with `gmi-natural-intelligence-bridge-v1`, whose §3/§6 assign cortical areas to taxa, tripping the capsule's own §7 falsifier. The composition is severed from the claim surface: C6 is restated as a functional-profile registry that asserts no neural mechanism and does not compose with §6 of the parent. |
| COG OBJ-6 | OPEN → `RV-C6-CLADES` | Correct. Single `(E, R, V)` scalars per clade with conceded internal variation and no phylogenetic control, in an ordering that reinstates a scala naturae. |
| COG OBJ-7 | DOWNGRADED → `DG-C6-PRED-NH-03` | Correct by the registry's own voiding rule: PRED-NH-03 is contradicted on `D_meta` (Foote & Crystal 2007, doi:10.1016/j.cub.2007.01.061) and `D_plan` (Miller, Botvinick & Brody, doi:10.1101/096594). PRED-NH-03 is recorded as `CONTRADICTED_ON_2_DESCRIPTORS`; the claim is restated as six rows pending and one voided. PX-Z14-COG's independent held-out comparison is recorded beside this. |

## 7. Non-material objections (acknowledged, no disposition required)

THM OBJ-11, 12, 14, 15, 16, 21, 26, 27; EXP OBJ-7, 15, 21; LIT OBJ-C1-D, C2-C, C3-D, C4-B, C5-D, C5-E, C5-F; STAT OBJ-S7; COG OBJ-8, 9. Two are corrected here for the record: THM OBJ-26 — `50,052 − 1,307 = 48,745` and the register's `−48,739` is the net after charging `K_total = 6` invention cost ("H+ burdens 50,052 -> 1,307 with `K_total=6` … (net −48,739)", `research/gmi-833-g0-grammar-growth-v1/CORE.md` lines 9–10), so the arithmetic closes once the charge is stated; LIT OBJ-C5-D/E — the Milner and Rubin bibliographic fusions are real and are carried into `RV-C5-CROSSWALK`.

## 8. Summary of dispositions

| claim | material objections | RESOLVED | DOWNGRADED | OPEN |
|---|---:|---:|---:|---:|
| C1 | 30 | 4 | 13 | 13 |
| C2 | 3 | 1 | 1 | 1 |
| C3 | 7 | 0 | 4 | 3 |
| C4 | 13 | 0 | 6 | 7 |
| C5 | 12 | 1 | 8 | 3 |
| C6 | 7 | 0 | 2 | 5 |

(Objections raised by two reviewers on the same defect are counted once per reviewer id in the
table rows above; the totals here count reviewer objection ids.) No claim's final disposition
is claimed SURVIVED by the authors: C1 carries open material objections on its real-system
extension and downgrades on its finite statement; C2–C6 carry at least one open item each.
The lane does not pre-empt the editor's disposition.
