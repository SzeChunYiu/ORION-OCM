# GMI #833 maturity rescore v2 — audit table (tranche 2: legacy corpus + post-freeze arrivals)

Frozen source: `d624c617d7a7c12f28e21c59a6ccca0e75bf34c0` (origin/main tip at v2 freeze; freeze commit `f1b6ea7d`).
Rubric: `FREEZE_V2.md` (imports `gmi-833-maturity-rescore-v1/FREEZE_V1.md` unchanged). Census authority: `gmi-833-corpus-census-v1` (`2fffb144` / result `861b1ba1`); all 173 legacy source files verified byte-identical to their census blob SHA at the frozen source (zero drift).

## Score summary

| tranche | scored | M0 | M1 | M2 | M3 | M4 | UNKNOWN |
|---|---|---|---|---|---|---|---|
| legacy 173 objects (25 packages) | 173 | 48 | 30 | 72 | 0 | 22 | 1 |
| arrivals 24 packages (post-`9f90fc4e`) | 24 | 0 | 0 | 17 | 6 | 1 | 0 |
| **total** | **197** | **48** | **30** | **89** | **6** | **23** | **1** |

Evidence distribution (all rows): EV0 46, EV1 30, EV2 95, EV3 23, UNKNOWN 3. Delta: 148 MAINTAINS, 48 DOWN_GENERATING (every one individually verified — see verification protocol), 1 UNSCORED_WITH_REASON. No M5/M6: the corpus holds no EV4/EV5 evidence (no disjoint-team replication, no real-scale prospective validation) — recorded as a corpus fact, not a defect.

## Verification protocol (as frozen, executed)

- Every DOWN-generating score (48) was individually verified against the actual artifact: 38 by the adjudicator's own full read of the statement + proof/receipt (this session, cited per record in `verification_note`); 10 uniform literature-digest rows by agent per-object full read at the census locator (verbatim statement captured) + adjudicator record review + 2 adjudicator cluster reads (P9B.LEARNABILITY_UNDECIDABLE, P4.BAXTER). No mechanical downgrades.
- MAINTAINS cluster spot-verification: 34/148 = 23.0% personally re-read (frozen minimum 10%). M3/M4 awards (7) all adjudicator-read in full.
- Conservative default exercised once: `V0.2` (gmi-adaptive-row-confidence-v1) is a document preamble, not a claim statement -> UNSCORED_WITH_REASON (`SUPPORT_NOT_LOCATED`); never guessed.

## Notable adjudications

**M3 carve-out (6 arrivals).** `aj9b`-`aj9g` blind-recovery packages each evidence the P3/P4 prior-free condition: freeze precedes outcome (blob-pinned FREEZE docs for aj9b-f; commit-ordering freeze for aj9g), search-visible sources carry no family tokens (adjudicator token scan of every search file + config), family mapping post hoc only, two materially distinct searches, exact recovery. aj9g carries an explicit custody note (thinner freeze; no blob-pinned doc); its P3 condition was verified by direct inspection, not narrative. `aj9a` is PRIOR_SUPPLIED by design -> M3 forbidden (rubric rule 3), scored M2/EV2.

**M4 (23).** 22 legacy frozen-experiment rows (MIM revival ledger: kill conditions, failed clauses preserved verbatim; small-cluster freeze-seeded holdouts incl. the honestly-retained FAILED V2 N-prediction context) + `g0-grammar-growth-v1` (pre-implementation freeze, independent oracle, frozen-then-evaluated held-out burden comparison). None claims M5: intra-package procedure is not independent replication (v1 rule 2).

**Registration-gap downs (G6, 6 legacy).** DE-3, DP2-6, NC-3, SG-1, TI-2 (MIM) and AS-1, EC-2 (small) hold genuine in-doc deductive proofs with explicit premises but no registered falsifier anywhere in the package -> EV1's explicitness requirement unmet -> M0/EV0. Registration gap, not evidence gap; flagged for falsifier-registration retrofit (feeds the #833 Section-A second checkbox).

**Rubric gap G2 (2 legacy).** PHYSICAL-MEASUREMENT (RV-377-195, 400k-input Monte Carlo) and G15_STEP_TWO_REACHED (RV-377-141, post-hoc atrophied re-reading): unfrozen sampled/post-hoc evidence has no foundation EV rung -> evidence_EV UNKNOWN (typed `UNFROZEN_SAMPLED_BELOW_EV3`), M0.

**Bookkeeping downs (40).** Census GREEN claim classes include ledger digests, registry/closure-gate meta rows, parent-citation imports (e.g. HPL-2003-97R1 Weissman mirror, Krohn-Rhodes 1965 row with UNVERIFIED doi), protocol/definition rows and one reserved ID: EV0/M0 with typed reasons. The census's claim-class assignment, not the science, is what changes.

**Reclassifications found by verification (24 rows, all adjudicator-read).** GGU FALSIFIABILITY_REGISTRY/doc-status objects (the registry registers premises+falsifiers+parents; the docs hold proofs + exact witnesses) -> EV1/M1-EV2/M2; MIM `*_EXACT` closure-gate rows with executed proof outputs (one with independent second implementation in gmi-grand-unification-v1) -> EV2/M2; A2-R (exact four-number no-go witness), DT-3B (executed two-point witness) -> EV2/M2. Census proof-mode disagreed with actual support on 62 objects (table in THEOREM_SCORES_V2.json `census_proof_mode` vs `support_kind`).

**Quantifier overreach (2, crosshanded to the Section-B adjudication lane).** TT-1 (gmi-threshold-task-frontier-v1): "every Boolean task" on an exact n=3..8 receipt + by-construction remark. S0002-9947-1965-0188316-1 (MIM literature ledger): universal Krohn-Rhodes prime-decomposition asserted from a NOT_ACCESSIBLE primary with unverified DOI, secondary digest only.

**Degenerate holdout (1).** MORPHOLOGY_PHASE_RV_THEOREM_V1: the object is a MANIFEST catalog row; the package's held-out protocol is 100%-by-construction on a deterministic world (no discriminative power) -> EV0/M0 with `DEGENERATE_HELDOUT_NO_DISCRIMINATIVE_POWER`.

## Protocol gaps recorded (G1-G7)

G1 legacy objects have no per-package claim ceiling -> per-object scoring of the census claim set (FREEZE_V2 §3). G2 unfrozen sampled evidence has no EV rung -> UNKNOWN/M0 typed. G4 `M0..M5` tokens in MIM matrix/ledger/ecology files are morphology-signature row names (README.md L202, DEFINITIONS_V2_EXACT.md L94, MORPHOLOGY_ATLAS_V1.md L133, SIGNATURE_HOLE_CENSUS_V1.md L19), never maturity levels; no legacy package carries foundation-ladder maturity claims (verified by sweep). G5 census machine fields (assumptions/falsifiers/parents/forbidden) are empty for 173/173 legacy objects; prose registrations exist (e.g. GGU FALSIFIABILITY_REGISTRY, MIM 65/93 falsifier-bearing docs) and are recorded via typed markers + citations. G6 analytic-without-falsifier (above). G7 degenerate heldout (above). Delta enum addendum: `UNSCORED_WITH_REASON` labels the FREEZE_V2 §4 UNKNOWN row (no score asserted).

## Typed exclusions (listed, never silently dropped)

| package | reason |
|---|---|
| `gmi-833-corpus-audit-close-v1` | NO PRIMARY THEOREM — adjudication child, freeze-only at the v2 frozen SHA (parallel Section-B lane) |
| `gmi-833-maturity-rescore-v1` | NO PRIMARY THEOREM — tranche-1 score records (this programme's own audit object) |
| `gmi-833-terminology-migration-v1` | NO PRIMARY THEOREM — terminology authority |
| `gmi-833-corpus-census-v1` | NO PRIMARY THEOREM — corpus audit object (v1 exclusion, unchanged) |
| `gmi-833-tranche-ab-ac-lit` | NO PRIMARY THEOREM — terminology crosswalk (v1 exclusion, unchanged) |

## Claim ceiling and forbidden promotions

`GMI_MATURITY_RESCORE_V2_AT_FROZEN_MAIN_SCOPE`. Forbidden: `M3_THROUGH_UNSUPPLIED_PRIORS`, `ONTO_COMPLETENESS_IMPLIED_BY_MATURITY`, `MATURITY_PROMOTED_BY_EXISTENCE_OF_SCORE_RECORD`, `CORPUS_WIDE_MATURITY_CLOSURE`, `RESCORED_THEOREMS_REPROVEN`, `COMPLETE_GMI`, `LEGACY_GREEN_PROMOTED_BEYOND_EVIDENCE`. Scores are labels on pre-existing registered evidence; no source package was edited; retraction is owned downstream.

## Audit table — arrivals (24)

| # | package | primary anchor | M | EV | delta |
|---|---|---|---|---|---|
| 1 | `ai0-convergence-spine-v1` | AI0 canonical GMI convergence spine + 19-node authority DAG (governance/normaliz | M2 | EV2 | MAINTAINS |
| 2 | `aj0-foundation-scope-v1` | AJ0 foundation-layer registry + anti-promotion (claim-demotion) contract; explic | M2 | EV2 | MAINTAINS |
| 3 | `aj1-operational-process-base-v1` | AJ1 typed operational process frame O_S=(Obj,Proc,composition,tensor,I,id,Adm_S, | M2 | EV2 | MAINTAINS |
| 4 | `aj2-operational-equivalence-v1` | AJ2-EQ operational equivalence + AJ2-Q quotient/state reconstruction | M2 | EV2 | MAINTAINS |
| 5 | `aj3-distinguishability-v1` | AJ3 distinguishability layer separation: Delta_phys / Delta_R (resource-accessib | M2 | EV2 | MAINTAINS |
| 6 | `aj4-process-organizations-v1` | AJ4 finite process-organization space M_B(O,S) + lifecycle-stage separation (pos | M2 | EV2 | MAINTAINS |
| 7 | `aj5-g0-compilation-v1` | AJ5 G0 compilation theorem: all five G0 instruction classes lowered to micro-pro | M2 | EV2 | MAINTAINS |
| 8 | `aj5-g0-lowering-v1` | AJ5 G0 lowering to operational roles with two presentations (P-FUN functional /  | M2 | EV2 | MAINTAINS |
| 9 | `aj6-aj8-development-value-intelligence-v1` | AJ6-AJ8 layer separation on merged spine: A_t = Legal(Sigma_t) intersect Adm_S(O | M2 | EV2 | MAINTAINS |
| 10 | `aj6-hst-layer-map-v1` | AJ6 contextual-lift theorem: iota_chi(M)=Sigma; M alone does not identify develo | M2 | EV2 | MAINTAINS |
| 11 | `aj7-objective-provenance-v1` | AJ7_NO_GO: world dynamics alone do not determine a unique objective/requirement/ | M2 | EV2 | MAINTAINS |
| 12 | `aj8-intelligence-boundary-v1` | AJ8 negative-control boundary: SCOPED_CONTROL_CAPABILITY vs DEVELOPMENTAL_CAPABI | M2 | EV2 | MAINTAINS |
| 13 | `aj9a-known-family-benchmark-v1` | AJ9a frozen 11-family known-family benchmark + prospective no-smuggling holdout  | M2 | EV2 | MAINTAINS |
| 14 | `aj9b-k01-blind-recovery-v1` | AJ9b blind structural recovery of frozen family K01 (neural/feed-forward): two f | M3 | EV2 | MAINTAINS |
| 15 | `aj9c-k02-blind-recovery-v1` | AJ9c blind stateful recovery of K02 (recurrent/stateful): unique one-cell delaye | M3 | EV2 | MAINTAINS |
| 16 | `aj9d-k03-blind-recovery-v1` | AJ9d blind local/shared-transform recovery of K03: unrestricted global Boolean s | M3 | EV2 | MAINTAINS |
| 17 | `aj9e-k04-blind-recovery-v1` | AJ9e blind dynamic-routing recovery of K04 (attention/dynamic-routing) at finite | M3 | EV2 | MAINTAINS |
| 18 | `aj9f-k05-blind-recovery-v1` | AJ9f blind compositional rule/search recovery of K05 (symbolic/rewrite/search):  | M3 | EV2 | MAINTAINS |
| 19 | `aj9g-k06-blind-recovery-v1` | AJ9g blind probabilistic-update recovery of K06 (probabilistic/Bayesian) at fini | M3 | EV2 | MAINTAINS |
| 20 | `capability-abstention-v1` | ABSTAIN-1 (point prediction iff singleton capability-query image; CANNOT_IDENTIF | M2 | EV2 | MAINTAINS |
| 21 | `capability-bounds-interactions-v1` | BOUND-1 / INT-1 / BUDGET-1 (three co-equal frozen rows: floor vs ceiling-certifi | M2 | EV2 | MAINTAINS |
| 22 | `cognitive-reaudit-v1` | MEMORY-1 / ATTENTION-1 / CONCEPT-1 (+ ADOPT-1): functional differentiation witho | M2 | EV2 | MAINTAINS |
| 23 | `developmental-potential-evolvability-v1` | DP-1 / EV-1 / HIST-1 / CAPITAL-1 (potential vs current capability; useful-descen | M2 | EV2 | MAINTAINS |
| 24 | `g0-grammar-growth-v1` | GRW-1 conservative recursive grammar growth + HLD-1 charged held-out reuse benef | M4 | EV3 | MAINTAINS |

## Audit table — legacy 173 (per object; grouped by package)

### `gmi-adaptive-row-confidence-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `V0.2` | THEOREM | UNKNOWN | UNKNOWN | NONE_FOUND | UNSCOR | SUPPORT_NOT_LOCATED: census object is a document preamble paragraph, n |

### `gmi-analog-semantics-closure-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `ANALOG_SEMANTICS_THEOREM_V1` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `AS-1` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | G6_ANALYTIC_NO_FALSIFIER: support=ANALYTIC_PROOF |

### `gmi-capability-ceilings-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `F2-U` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |

### `gmi-capability-contract-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `F1-S` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |

### `gmi-capability-held-score-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `HELD_FAMILY_SCORE_V1` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |

### `gmi-capability-interactions-unified-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |

### `gmi-delegation-cost-repair-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `TYPED_DELEGATION_COST_THEOREM_V1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |

### `gmi-developmental-uncertainty-transport-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `DT-2A` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `DT-2B` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `DT-3B` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | EXISTENTIAL_NO_GO_WITH_EXECUTED_TWO_POINT_WITNESS |

### `gmi-ecology-contract-v2`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `A2-R` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | NO_GO_WITH_EXACT_WITNESS: support=ANALYTIC_PROOF |

### `gmi-experimental-validation-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `DRS-3` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |

### `gmi-extended-cognition-closure-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `EC-2` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | G6_ANALYTIC_NO_FALSIFIER: support=ANALYTIC_PROOF |

### `gmi-finite-quantum-cover-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `TQI.2` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |

### `gmi-formal-derivation-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `ADAPTIVE-EXAMPLES` | LAW | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |

### `gmi-grand-unification-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `A-G` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `ACTIVE-EXPERIMENT` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `ALL_PARENTS_KNOWN` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `AR-7` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | DOC_ANALYTIC_PREM_PLUS_REGISTRY_FALSIFIER, no per-claim exact witness |
| `ARCHITECTURE-DERIVATION` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `CA-2` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `CD-1` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `CD-2` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `CLM-5` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `D1-D8` | CLAIM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM` | LAW | M2 | EV2 | LEDGER_ENTRY | MAINTA | REGISTRY_POINTER_DOC_PROOF_WITNESS: support=LEDGER_ENTRY |
| `ERI-4` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `EXECUTED_AT_REGISTERED_FOUR_CANDIDATE_SCOPE` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `FINITE-REGRET` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `FORMAL_DERIVATION_INTEGRATION_V1` | CLAIM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `FP-4` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GEI-1` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `GG-P2` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-P3` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-P6` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-R2` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-R3` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-R5` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-R7` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-S1` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GG-S5` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GIR-3` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GMI-AUDIT-SYM-01` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GMI-AUDIT-SYM-02` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `GMI-AUDIT-SYM-03` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT: support=ANALYTIC_PROOF |
| `GMI_OPERATIONAL_COMPLETENESS_THEOREM_V1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | DOC_ANALYTIC_PREM_PLUS_REGISTRY_FALSIFIER, no per-claim exact witness |
| `GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `HPL-2003-97R1` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `NEURAL_NONNEURAL_FAMILY_SELECTION_THEOREM_V1` | LAW | M2 | EV2 | LEDGER_ENTRY | MAINTA | REGISTRY_POINTER_DOC_PROOF: support=LEDGER_ENTRY |
| `NON-NEURAL` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `PLANNING_SEMANTIC_RESOLUTION_CLAIMS_V1` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `PN-5` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `PROGRAMME_METHOD_NOVELTY` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `PRS-1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `RDP-3` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `READY_FORMAL` | THEOREM | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |
| `RM-1` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `RQR-1` | COROLLARY | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `SA-1` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `SA-4` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `SD-ERI5` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `SD-GR5` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `SET-THEORETIC` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `SR-1` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `SR-2` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `SUBSTRATE-LAW` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `S_T` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |
| `TRAINING-AND-DEVELOPMENT` | THEOREM | M2 | EV2 | ANALYTIC_PROOF_PLUS_EXACT | MAINTA | DOC_STATUS_ROW_DUAL: doc carries proof + exact finite witness + receip |
| `U_A-L_A` | THEOREM | M2 | EV2 | ANALYTIC_PROOF | MAINTA | DUAL_ANALYTIC_EXACT_STATUS: support=ANALYTIC_PROOF |

### `gmi-metacognition-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `META-1` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |

### `gmi-morphology-descriptor-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `F4-C` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |

### `gmi-morphology-phase-rv-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `MORPHOLOGY_PHASE_RV_THEOREM_V1` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | DEGENERATE_HELDOUT_NO_DISCRIMINATIVE_POWER |

### `gmi-novel-intelligence-w4-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `W4-C` | THEOREM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |

### `gmi-section-d-free-lunch-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `D-FL1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |

### `gmi-section-d-phase-winners-v2`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `EXACT_4` | CLAIM | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |

### `gmi-structural-threshold-repair-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `N_SUM_THRESHOLD3_V3` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |

### `gmi-symbolic-selector-derivation-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `UNIVERSAL_BEST_SELECTOR_LANGUAGE` | THEOREM | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |

### `gmi-threshold-task-frontier-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `TT-1` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | QUANTIFIER_EXCEEDS_EVIDENCE |

### `gmi-useful-descendant-evolvability-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `U_AND` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |

### `machine-intelligence-morphogenesis-v1`

| object | class | M | EV | support | delta | note |
|---|---|---|---|---|---|---|
| `ATTRIBUTION_KILLED` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `BR-2` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `B_T` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `CCD-1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `CI-T1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `CI-T2` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `COST-LABEL` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `CROSSOVER_CELL_WITHIN_FINITE_SAMPLE_BAND` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `DE-3` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | G6_ANALYTIC_NO_FALSIFIER: support=ANALYTIC_PROOF |
| `DISCRETE_FINITE` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `DP2-6` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | G6_ANALYTIC_NO_FALSIFIER: support=ANALYTIC_PROOF |
| `DSAT-1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `DSAT-3` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `EARNED_AT_EXACT_SCOPE` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `EG-2` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `F.01` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `FAILS_AS_FROZEN` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `FINITE_BUDGET_DEVELOPMENTAL_REACHABILITY_EXA` | THEOREM | M2 | EV2 | LEDGER_ENTRY | MAINTA | GATE_ROW_EXECUTED_PROOF: support=LEDGER_ENTRY |
| `FINITE_OPERATIONAL_CAPABILITY_SET_EXACT` | THEOREM | M2 | EV2 | LEDGER_ENTRY | MAINTA | GATE_ROW_EXECUTED_PROOF: support=LEDGER_ENTRY |
| `FINITE_OPERATIONAL_FRONTIER_EXACT` | THEOREM | M2 | EV2 | LEDGER_ENTRY | MAINTA | GATE_ROW_EXECUTED_PROOF: support=LEDGER_ENTRY |
| `FINITE_OPERATIONAL_OPTIMAL_FIBER_EXACT` | THEOREM | M2 | EV2 | LEDGER_ENTRY | MAINTA | GATE_ROW_EXECUTED_PROOF: support=LEDGER_ENTRY |
| `FINITE_REGISTERED_STOCHASTIC_CONTROL_EXACT` | THEOREM | M2 | EV2 | LEDGER_ENTRY | MAINTA | GATE_ROW_EXECUTED_PROOF: support=LEDGER_ENTRY |
| `FOC-4` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `FRAC_BITS` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `G15_STEP_TWO_REACHED` | THEOREM | M0 | UNKNOWN | EMPIRICAL_UNFROZEN | DOWN_G | G2_UNFROZEN_SAMPLED: support=EMPIRICAL_UNFROZEN |
| `GENERAL_INTELLIGENCE_THEORY_PARENT_ATLAS_V1` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `GI-2` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `GM-2` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `GMI-RT-V3R2` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `GMI_BASIN_RESTART_DEVELOPMENT_THEOREM_V1` | LAW | M1 | EV1 | LEDGER_ENTRY | MAINTA | REGISTRY_POINTER_DOC_PROOF: support=LEDGER_ENTRY |
| `GMI_EFFECTIVE_RANK_ESTIMATION_THEOREMS_V1` | CLAIM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `GMI_FINITE_PORTFOLIO_SELECTION_BOUND_V1` | THEOREM | M2 | EV2 | LEDGER_ENTRY | MAINTA | THEOREM_DOC_PLUS_EXECUTED_CALIBRATION: support=LEDGER_ENTRY |
| `GMI_JOINT_ENVELOPE_ATTAINMENT_RECEIPT_V1` | CLAIM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `GMI_K5_BH_REVIVAL_PLAN_V8` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `GMI_SPECIALIZATIONS_V1` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `HELD-OUT` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `HOPFIELD_RND` | LAW | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |
| `ITER_FROZEN` | LAW | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |
| `KF-16` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `KF-3` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `L8-OCCUPANCY` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `L8.1` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `LEARNING-SCALE` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `NC-3` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | G6_ANALYTIC_NO_FALSIFIER: support=ANALYTIC_PROOF |
| `ND-1` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `NON-FINAL` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `NS-2` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `OPEN_BLOCKING` | CLAIM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `P1.AIXI` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P4.BAXTER` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P4.MAML_UNIVERSALITY` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P7.CT_ML_SURVEY` | CLAIM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P7.GNN_DP_CORRESPONDENCE` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P9A.CHEAP_GRADIENT` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P9A.THRESHOLD_CIRCUITS` | CLAIM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P9A.UNIVERSAL_APPROXIMATION` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `P9B.LEARNABILITY_UNDECIDABLE` | LAW | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `PARENT-OWNED` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `PER_EVAL` | LAW | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `PHYSICAL-MEASUREMENT` | THEOREM | M0 | UNKNOWN | SAMPLED_STATISTICAL | DOWN_G | G2_UNFROZEN_SAMPLED: support=SAMPLED_STATISTICAL |
| `POSET_NOJOIN` | LAW | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `PREDICTION_HELD` | THEOREM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `PREDICTION_WRITING` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `PROG_SEARCH` | COROLLARY | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `QUERY_IN` | LAW | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |
| `RC-07` | THEOREM | M2 | EV2 | LEDGER_ENTRY | MAINTA | CLOSED_FORMAL_PLUS_EXHAUSTIVE_CHECKS: support=LEDGER_ENTRY |
| `RH-2` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `RV-377-009` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | LEDGER_BOOKKEEPING: support=LEDGER_ENTRY |
| `RV-377-028` | CLAIM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-046` | CLAIM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-054` | LAW | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-063` | CLAIM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-069` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-081` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `RV-377-087` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `RV-377-091` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-092` | CLAIM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-093` | PROPOSITION | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-095` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-099` | PROPOSITION | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |
| `RV-377-194` | THEOREM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `RV-377-196` | LAW | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |
| `RV-377-201` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `S0002-9947-1965-0188316-1` | THEOREM | M0 | EV0 | LEDGER_ENTRY | DOWN_G | QUANTIFIER_EXCEEDS_EVIDENCE |
| `SEARCH-T1` | THEOREM | M1 | EV1 | ANALYTIC_PROOF | MAINTA | ANALYTIC_PREM_FALS: support=ANALYTIC_PROOF |
| `SG-1` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | G6_ANALYTIC_NO_FALSIFIER: support=ANALYTIC_PROOF |
| `SKEWED_BINARY` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `STAGE_ECO_V32_ECO_AXIS` | LAW | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `TF-055` | LAW | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |
| `TI-2` | THEOREM | M0 | EV0 | ANALYTIC_PROOF | DOWN_G | G6_ANALYTIC_NO_FALSIFIER: support=ANALYTIC_PROOF |
| `UNKNOWN_MORPHOLOGY_UNEARNED` | CLAIM | M4 | EV3 | FROZEN_HELDOUT | MAINTA | FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT |
| `VEC_STATE` | LAW | M0 | EV0 | PROTOCOL_ONLY | DOWN_G | PROTOCOL_NO_RESULT: support=PROTOCOL_ONLY |
| `X-TMT9` | THEOREM | M2 | EV2 | EXACT_FINITE_CERTIFICATE | MAINTA | EXACT_FINITE: support=EXACT_FINITE_CERTIFICATE |

## Post-freeze custody note (typed POST_FREEZE_REBASE, 2026-09-16)

Main advanced by one commit between the v2 freeze and shipping (`d624c617` -> `f4d9d7d5`, PR #947 terminology migration v2). The branch was rebased; the pre-registration freeze commit `f1b6ea7d` became `94ae9786` (identical tree for this package). No new `gmi-833-*` directories appeared (inclusion lists remain mechanically complete at the ship SHA). The terminology migration touches wording in `gmi-833-*` packages only; all 173 legacy source files re-verified byte-identical to their census blob SHAs at the rebased head (scorer re-run green, counts unchanged). Scores are based on claim semantics, which wording-only migration does not change.
