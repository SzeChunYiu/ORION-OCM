# GMI evidence synthesis V1 — what is proved, what is measured, what is still owed

Status date: 2026-09-12 (evening). Lead-session synthesis of the day's campaign on top of the codex lane's
theory tranches. Companion to `research/gmi-grand-unification-v1/MASTER_CLOSURE_LEDGER_V1.md` (formal
closure) and `GMI_COMPLETENESS_BOUNDARY_THEOREM_V1.md` (+ V1.3 addenda). Rows marked PENDING are lanes
still running when this file was written; they are updated by the records they cite, never by editing
this table silently.

## 1. Evidence tiers used below

| tier | meaning |
|---|---|
| THEOREM | proved in a committed document with stated scope |
| EXACT | exhaustive/exact finite microscope, deterministic, receipt committed |
| REPLICATED | the exact checker re-executed on a second host from a fresh clone, receipts byte-identical (`GMI_THEORY_TRANCHE_INDEPENDENT_HOST_REPLICATION_V1.md`) |
| DEV | development-tier experiment (frozen before run, not beacon-gated) |
| PROTECTED | beacon-gated (drand quicknet) or post-freeze protected draws, seeds bound to the freeze commit |
| REAL | real learners on real data with pre-outcome descriptors |
| EXTERNAL | numbers taken from published measurements, not measured in-programme |

## 2. Master objects → evidence

| master object (MASTER_CLOSURE_LEDGER §2) | theory | evidence | status |
|---|---|---|---|
| exact semantic state (canonical response quotient) | GG10–GG12 THEOREM | 110,592 refinement cases EXACT, REPLICATED | closed at finite scope |
| information / communication (semantic cut κ) | GG1–GG6 THEOREM; CL-1…CL-7 specialisations | 117,649 obligation families EXACT; CL-1…7 verified tight on protected draws (RV-377-123/124/130–134) | closed at registered channel scope |
| local computation (τ) | GG7–GG9 THEOREM | decision-tree separation through n=7 EXACT, REPLICATED | closed |
| learning / evolution as recursive lift | GG13–GG18 THEOREM | lifted reachability checks EXACT; **B6 developmental morphogenesis experiment RV-377-180 PENDING** (warm-start vs reset vs twin, 36 searches) | theory closed, evidence pending |
| symmetry → equivariant representative | GG19–GG21 THEOREM (convex conditions) | 3,375 checks + nonconvex counterexample EXACT, REPLICATED | closed with boundary |
| substrate lifting | GG22–GG24 THEOREM | 1,020 traces EXACT, REPLICATED | closed |
| morphology = Pareto frontier + operational fibers | FO1–FO3 THEOREM | frontier enumeration EXACT (16 policies, best 3/4); **K4 V7 PROTECTED: 0/264 named-family recovery** — fibers, not names, are the closed object | closed as fibers; names not recoverable (RV-377-121) |
| neural derivation with predicted capability | FO4–FO6 THEOREM | one-hot/ReLU compiler EXACT (192 traces) | closed at finite operational scope |
| held-family response / phase laws | K5 phase freeze V1 + revival plan V8 | **PROTECTED GREEN 8/8 lanes** (V7 six lanes; V8 two revived lanes, RV-377-170/171); REAL transfer RV-377-190/194: off-band 63/64 vs CV 53/64 | closed at registered + sklearn scale |
| prospective unoccupied channel domains | atlas §3 + FO11 | RV-377-135…138 EXACT GREEN; **RV-377-200 PROTECTED-draw realization: P0–P5 held** (ceiling attained on 2/3 seeds, store carriers, empty region empty, channel ablation) | prediction and realization closed at registered scope |
| composite / distributed | compositional layer (PR #467) | EXACT, REPLICATED | closed with coupled-goal counterexample |
| causal meaning / viability | causal-viability layer | EXACT, REPLICATED | closed |
| physical substrate constants | nonclassical end-to-end theorem | RV-377-195 EXTERNAL (Willow, HERMES): parent wins by ≥ 10¹⁰ at the registered obligation | evaluated from published constants only |
| uncomputability boundary | GG35 THEOREM | halting reduction | boundary, not gap |
| morphology / family selection (MS-1…3, GG60 end-to-end traces) | THEOREM + EXACT synthetic traces (neural / non-neural / hybrid / inversion) | **measured**: MS-2 on the charged frontier receipts — 82/309 scopes derive one family, 191 carry an (H, r) boundary, 26/51 ecologies show cross-column family inversion (`GMI_MEASURED_PROFILE_FAMILY_SELECTION_V1.md`) | closed at registered scope with measured profiles |
| realization compilation layer | THEOREM | EXACT after correction: the committed checker pinned 274 Boolean functions where the family has 276 and its receipt was not the script's output; fixed and regenerated (PR #480) | closed; replication caught the defect |

## 3. The seven-gap table, current reading

| # | gap | status now | record |
|---|---|---|---|
| 1 | true zero-prior derivation | named-family recovery RED at protected tier (structural); operational fibers closed; carrier-class rate law **PENDING** (RV-377-140); CP1 ablation: 33 kinds, 49/99 units done, 13 kinds revived under the kind-agnostic generator (RV-377-202, running) | #455, FO1–3, RV-140, RV-202 |
| 2 | blind recovery (B5) | lane B nine seeds: raw descriptor 4/9 DENSE (RV-118 B1 confirmed), atrophied reading 0/9 — coefficient class never recovered on any discriminating ecology (0/12 E_sym5, 0/3 each elsewhere); memory 9/12, program 1/12. `G15_STEP_TWO_REACHED` → REACHED_ON_RAW_DESCRIPTOR_ONLY (RV-377-141). Class-rate law CRML-1 scoring on 4 fresh ecologies in progress | RV-140/141 |
| 3 | cross-paradigm morphogenesis (B6) | theory: recursive lift GG13–18; experiment RV-377-180 **PENDING** | RV-180 |
| 4 | unknown / novel morphology (B7) | four unoccupied channel cells predicted and exact-verified (FO11); **RV-377-200 realized**: a preregistered occupied region (structureless world + half-coverage store, ceiling 0.8909) was reached by macro-free search on 2/3 seeds with store carriers, the region predicted empty stayed empty, and removing the store channel removed the capability (P0–P5 all held). B7 earned as a channel-defined form, novelty over parents not claimed | FO11, RV-200 |
| 5 | architecture-independent principle (B8) | semantic cut + substrate lifting + channel family verified; master factorization GG33 | GG1–9, GG22–24, GG33 |
| 6 | phase law / predictive dynamics | PROTECTED GREEN 8/8 + REAL off-band | K5 V7/V8, RV-190/194 |
| 7 | universality + real/physical | REAL closed at sklearn scale; physical sign from EXTERNAL constants; independent authorship closed by model proxy (IG-4/5, RV-377-160; residue: same model family) | RV-190/194/195, RV-160 |

## 4. Standing negatives and their root causes (revival law: one stage, one lever)

| negative | root cause (one stage) | lever | state |
|---|---|---|---|
| K4 property-vector prediction 0/264 | predicted object ill-posed (cross-seed agreement 0 %) | predict carrier-class rates; exact fibers | RV-140 running; FO2 closed |
| coefficient carrier 0/12 under atrophy | DENSE node dead weight on registered ecologies; reachability precision-gated | witness-bearing fresh ecologies; fx16 axis if still zero | RV-140/141 running |
| 13 kinds STRUCTURAL_TO_GENERATOR | generator hard-codes kinds by name | kind-agnostic generator, inert on full alphabet | RV-202 running |
| K5 C_FEATURE_LEARNING RED / E_CONTROL INCONCLUSIVE | frozen predictor omitted reachability / admissibility clause | corrected laws, fresh grids | GREEN at protected tier |
| real-transfer crossover cells | finite sample at the frozen bar | off-band grid by power calculation; mass-weighted term | GREEN off-band; crossovers inside band by construction |
| DG-12 degenerate obligations (axis_a, e1_cp, refine_f) | obligation constant on the scored window | V2 obligations (owed) | audited (RV-377-118D), repair queued |
| DG-13 leaky intervention / misnamed E_parity | scoring defect / dict-keys constructor | additive V2 registrations | CLOSED (RV-377-150): 3/36 store-row verdicts move; parity-separating split found |
| IG-4/IG-5 same-author meter/alphabet | no independent author | blind model-proxy authors | CLOSED via model proxy (RV-377-160, PR #482): meter agreement ≥ 99 % per axis, K4 verdicts meter-invariant, alphabet covers all five carrier classes |

## 5. What would still be owed after every PENDING row lands

Independent human authorship (closed only by model proxy), modern-scale neural evidence, in-programme
physical measurement, and any ecology outside the registered families. These are applications and
external gates in the master ledger's sense, not missing foundational categories.
