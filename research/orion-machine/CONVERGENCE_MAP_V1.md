# Convergence map — every artifact as a component of the knowledge-space object (KSO)

Owner: the OCM lane (rule 2, #284 comment 5541151080). Prototype plan: **#284**. Umbrella #194 · master #197.
Operator directive (verbatim): *"we really need to converge everything so that we can really form the orion ocm."*

**Rule.** From #284's convergence comment on, a lane's output is a row in this map — the KSO
component it feeds, the milestone it unblocks, its status, its checker — or it is not accepted.
Lanes barred from `orion-machine/**` post rows on #284; the OCM lane carries them here. The map is
updated on every subsequent OCM PR. **NO NOVELTY OR BREAKTHROUGH CLAIM**: a row records what an
artifact *is* for the object, never that the object works.

Milestones (#284 §6): M0 substrate contract · M1 KSO v0 on one exact domain · M2 solve loop vs
oracle (translator-invariance gate) · M3 gap loop (channels) · M4 Jump loop · M5 codec / chat ·
M6 frontier-math pilot. Spine stage 2 = M0–M3; stage 7 = M6.

## 1. The map

| artifact / lane | KSO component | milestone | status | checker |
|---|---|---|---|---|
| `src/orion_v2/epistemic_atlas.py` — `ContextMapKind` {RESTRICTION, EMBEDDING, SCALE_CHANGE, BOUNDARY_CHANGE, REPRESENTATION_TRANSPORT, DECISION_TRANSPORT}, `GluingStatus`, `HorizonStatus`, `UnknownKind` | **edge vocabulary** (typed relations); charts = subgraphs; `HorizonStatus` / `UnknownKind` = the **obstruction-witness type** navigation must emit | M0 | exists, static (locality/gluing only; no reaction dynamic — the drift #194 names) | — (unit tests of the atlas; no navigation checker) |
| RCL profile = ATMS label (de Kleer 1986); substrate constraints S1–S7; Theorem S4 | **node label type**; the **retraction law** (label survival after assumption retraction) | M0 | proved / checked exhaustively at n = 4 (stage 1) | `revocation_complete_learning/rcl_checks_v1.py`; `reference/ocm_reference_semantics.py` |
| `ATOMIC_CLAIM_INVENTORY.json` (paper packages, v1) | **atom schema** — generalised in M0 to procedures / constraints / representations | M0 | exists in the paper packages; not yet on this repo's main under `orion-machine/` | — |
| `reference/ocm_reference_semantics.py` (S1–S7) | **executable substrate** the KSO is built on | M0 / M1 | exists | S1–S7 exhaustive, planted failures, M1–M4 |
| **Stage-1 tail: lane #200 revival** — `theory/OCM_NONRECTANGULAR_CLASS_V1.md`, `reference/ocm_nonrectangular_class_exact.py` (PR #288) | the **induced-warrant node type**: on a concept class the label of a query atom is the version-space agreement (`VSW`), i.e. the ATMS label *induced by the hypothesis class* — the form M1's nodes take when populated from an exact domain; also the reason the separation claim gates M6, not M2 | M0 (node type) / M6 (gate) | terminal `NATURAL_NONRECTANGULAR_CLASSES_EXIST__ONE_NATURAL_NONDECOMPOSABLE_INSTANCE_REGISTERED__PARENT_OWNED`; separation test `NOT_FROZEN__CONDITION_1_UNSATISFIABLE_CLASS_INDEPENDENT` | 2,048 / 648 worlds R0; 65,805-class affinity census; 78,848 ATMS-label cells; `VSW(SINGLETONS_5)` I = 1 certified two ways |
| FM10 / FM20 / ME-X1 / ME-X3 exact generators + oracles | **populated domains with ground truth** for the solve loop | M1 / M2 | exist, protected | per-suite receipts |
| **FM40** invariance / equivariance discovery (PR #283) — `fm40_suite.py::generate_split` (7 families, seed `FM40-PROTECTED-30f03eaa…`, 169 rejections published); oracle `oracle_element_closure` / cross-check `oracle_generator_blocks`; protected n = 126 | additional **oracle domain** | M1 | protected leg **agrees** with dev: `PARENT_SUFFICIENT`, G1a PASS identity 1.0000 both legs, every hard gate PASS, G2 on 108. F0 = oracle by construction (0/126 differ), so M 126/126 is an identity, not a measurement; `G1b` unfirable — the federation is a **ceiling** | protected receipt `FM40_OUTCOME_RECEIPT.md`; **M2 comparator (oracle-independent): `P5_FIXED_LESSON_TABLE` 0.579, `P4_REGIME_RESTRICTION` 0.571; ceiling control `P2_EQUIVARIANCE_SOLVER` 0.714 (partial oracle)**; stratum no parent reaches: `SURFACE_ONLY_SYMMETRY` 18/18 |
| **FM50** functoriality / commuting diagrams (PR #283) — `fm50_suite.py::generate_split` (8 families, gate `G0g`, seed `FM50-PROTECTED-bf064cdf…`); oracle `oracle_exhaustive` / `oracle_constraint_search`; n = 104 | additional **oracle domain** | M1 | protected leg **agrees** with dev: `PARENT_SUFFICIENT`, identity 1.0000 both legs, hard gates PASS, G2 on 65; M = P2 by mathematics (law fragment is a total function of the candidate) — ceiling | `FM50_OUTCOME_RECEIPT.md`; **M2 comparator (oracle-independent): `P3_DIAGRAM_CHASE` 0.567; ceiling control `P2_CATEGORY_LAW_FUNCTOR` 0.875** (also the cross-check oracle's law counter; misses exactly `FALSE_EQUIVALENCE`) |
| **FM60** obstruction / counterexample discovery (PR #283) — `fm60_suite.py::generate_split` (5 families, seed `FM60-PROTECTED-6a2d4a4f…`, 2,688 rejections published); oracle `oracle_exhaustive` (bitset algebra, 4,164 structures) / `oracle_stratified_dpll`; n = 125 | additional **oracle domain**; and a **budget-isolation data point** for the contract (below) | M1 | **protected leg disagrees with dev, reported plainly**: dev identity 1.0000 / G1a PASS on n = 15; protected **G1a FAIL at 0.992 on n = 125** — M 124/125, one `no_obstruction` abstention at `PROOF_STEP_BUDGET = 12` where P3 derives; diff −0.008, p = 1.0; route `PARENT_SUFFICIENT` by the pre-registered no-advantage branch; G2 on 100 (dev had `CANNOT_CHECK` on 9 under a mis-scoped runner binding, repaired pre-run). Off-population F0 is not the oracle (bounded-valid claim outside the rule base → abstain): M 124/125 is a measurement | `FM60_OUTCOME_RECEIPT.md`; **M2 comparator (oracle-independent): `P4_SMALL_SCOPE_BOUNDED_CHECK` 0.728; ceiling control `P2_EXHAUSTIVE_MODEL_SEARCH` 0.800** (same set algebra as the oracle's reject side; 0.00 on `no_obstruction`) |
| **E30-R13 → R14 patch-apply interface** (PRs #280, #285) — `research/experiments/e30-r14/BOUNDARY_CONTRACT_TEMPLATE_V1.md`, `src/orion_v2/anchored_edit_interface.py`, `interface_receipt`, GR0f | **boundary contract template** for the M5 codec boundary — the one typed interface in the programme that worked | M2 / M5 | contract registered in code and doc; attribution landed (152/205 non-applying R13 patches edited unshown code → ledger class `INTERFACE_ASKS_FOR_WHAT_IT_WITHHELD`); **checker staged, unmeasured** (LUNARC 2×2 calibration has no answered cell; selection rule pre-declared) | GR1 apply-failure ≤ 0.40 over 480 envelopes after GR0c/d/e/f; GR0f proven to fail on each mode and to read `COULD_NOT_CHECK` on zero receipts |
| **ME-X6 V3 `TYPING_IS_A_COVERAGE_PRIOR`** — `research/experiments/me-x6-v3/` (design `d492e2b9…`, receipt, protected results) | evidence for **atom / edge typing** (see §2.1) | M0 | **landed**, saturated: information (V1), capacity (V2), coverage (V3) all matched; M 1800/1800; V2's frozen vector 0/400 on never-exercised roles by construction; refit on completed coverage ties 1800/1800, 0 discordant in 36 cells; no V4 on this generator | V3 selftest 25/25; `tests/unit/test_me_x6_v3_role_coverage.py` (9); hard gates G0a–G0e, G8; live gate G2 (tie) |
| **H-EXT-1 gate-active regime → H-EXT-1R** — `research/experiments/h-ext1/H_EXT1_OUTCOME_RECEIPT.md`; `scripts/h_ext1r_regime_study.py`, `research/experiments/h-ext1r/H_EXT1R_REGIME_DESIGN_V1.md` | **navigation trigger** — when the label/dependence machinery runs vs when navigation *escalates* (see §2.2) | M2 / M4 | H-EXT-1 prospective: gate `G_B_PLUS_XREF` fires 170/520 (all 80 PDS1A/PDS1C, none elsewhere); GATED 0.9769 = the oracle-stratum ceiling; every discordant pair off-gate. H-EXT-1R: design + selftest 53/53 landed; dev split prepared (80 tasks, gate 80/80, control `False`); **F1 unmeasured** (channel unanswered; resumable) | regime checker: gate fires on every task + no-witness control `False` + F1 (parent ≤ 0.85 on treatment strata, else `REGIME_NOT_REALISED__PARENT_AT_CEILING_ON_WITNESSED_LATENT_TASKS`) |
| ME-X2 locus + minimum escalation | **Jump trigger / level gate** | M4 | protected: 0 false escalations vs the parent's 21; 140/140 correct `CANNOT_IDENTIFY` | ME-X2 receipt |
| v1 #558 `ExecutableRegimeWitness.v1` + 84 opaque worlds (42 + 42; 48 positive zero-error cases, 36 controls) | **Jump correspondence object** + first Jump benchmark | M4 | exists (v1); negative terminal `REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE` inherited | v1 zero-error controls |
| P-A structural donor discovery; P-B context-relative transport | **Jump sources**; cross-region navigation | M4 | closed papers; evidence usable | — |
| PRA revision-adequacy audit; PRA V2 (arm 1 running) | **revocation dynamics test bed** | M3 | V2 in flight | GP gates |
| FG80 R3 + ME-F1 R3 (deferred dispatch) | tells whether the frontier negative was an *interface* artifact → feeds the boundary contract | M2 | armed on billy-old | R3 receipts |
| SD70-V3 (campaign running) | **meta-policy = navigation-policy candidate** | M2 | running | V3 gates |
| ME-X3 Lean cross-check | **proof-assistant warranting channel** (an exact checker is not feedback; its verdicts carry warrant) | M6 | exists | 20/20 accept files |
| `FAILURE_LEDGER.md` (26 classes) + `research/orion-machine/OCM_FAILURE_LEDGER.md` (8 classes), checkers, kill-gates | **immune system** | all | exists | — |
| parent-strength audit (14 faithful parents) | **parent-subtraction table** for every component | M0 | exists | — |
| `src/orion_v2/jump.py` (`JumpLevel`, `TriggerKind`, `JumpTrigger`) + `research/frontier-jump/JUMP_RESEARCH_PROGRAMME_V0.md` §2–§3 | **Jump ladder J0–J8** and the witnessed-obstruction precondition (definition to cite; hooks M0 must leave) | M0 (hooks) / M4 | exists | — |

**Does not converge, retired as a component:** LLM-centred arm code and controller-around-LLM
designs (P-F, ME-F1, E40, E30-R13 negatives). Retained as the negatives that located the centre.

## 2. Judgement rows — evidence produced elsewhere, read as a component

### 2.1 ME-X6 V3 → what typing is in the substrate contract

The saturated result: a typed assignment declared a priori is exactly as good as an untyped
learner that has seen every declared role exercised, and no better — 0/400 on never-exercised
roles for the frozen vector *by construction*, 1800/1800 tie after refit on full coverage.
**Reading for M0:** an edge type is a **coverage prior for navigation**, not a capability. It
declares which channels count between two atoms and in which direction — the typed transition
structure of the walk — and that declaration is auditable and robust to roles never exercised.
It must **not** be modelled as information a fully-covered learner cannot recover. Consequence
written into the contract: every typed-navigation result carries a matched **untyped-walker
control trained on full role coverage** (the ME-X6 V3 construction); the expected outcome is a
tie, and a typed advantage is admissible only where a role is provably unexercised in the
comparator's coverage — which the checker must exhibit, not assume. Nothing here says typing is
"nothing": with sparse coverage it is what makes navigation well-defined at all; with full
coverage it is a re-description.

### 2.2 H-EXT-1 → when navigation escalates versus keeps walking

The frozen data: the gate fires exactly on the strata where the dependence machinery matters,
and where it fires the gated arm sits **at the oracle-stratum ceiling, tied with the strongest
parent** (170/170; 72/72 held-out); every discordant pair lives off-gate. **Reading for M2/M4:**
the witness that fires the machinery is a *run-the-label-propagation* signal, not an
*escalate* signal. Escalation to a Jump proposal is warranted only when (i) the gate fires
**and** (ii) the strongest parent is witnessed **off ceiling** on that regime — H-EXT-1R's F1
(parent ≤ 0.85 on the treatment strata) is precisely that second witness, and if F1 fails the
finding is that this witness family cannot be the trigger. Until F1 is measured, the contract's
navigation policy is: gate-active and at ceiling ⇒ **keep walking** (`PARENT_SUFFICIENT` is the
result); gate-active and parent off ceiling ⇒ emit an **obstruction witness** and hand to the
Jump ladder at the minimum sufficient level. **FM60 adds the budget clause:** its one abstention
was a `PROOF_STEP_BUDGET` cap the parent did not need — the same budget-isolation shape as
ME-F1's parent — so the navigation budget (steps, restarts, depth) is stated **per arm and
matched** in every M2 comparison.

### 2.3 E30 patch-apply fix → the shape of the M5 codec contract

The one typed interface that worked is closed under what the sender was shown: the presentation
shows every named file whole with an elision receipt; edits cross as `{path, search, replace}`
located by verbatim content exactly once; the diff is derived by the substrate from the real
file, never from sender coordinates; unlocated / ambiguous / overlapping / no-op edits are typed
rejections that void the whole proposal; interface id + byte fingerprint on every exchange.
The M5 codec contract takes the template's §6 substitution as written: the rendered subgraph is
**whole** with an elision receipt; atom references are located by **content hash, exactly once**,
never by position; the graph mutation is derived by the substrate from located atoms — the codec
never writes graph coordinates; an unlocatable reference voids the proposal (no partial
mutation); codec id + fingerprint on every exchange; **translator invariance** (#284 §1) is the
homogeneity gate across two codecs, with two atomizations of one question as the declared weaker
form if two codecs are unavailable; GR1's apply-rate becomes the fraction of codec proposals that
materialise as a warranted mutation.

## 3. M2 comparator line (inherited from §1, oracle-independent)

| domain | comparator (oracle-independent) | ceiling control (shares oracle procedure) |
|---|---|---|
| FM40 | `P5_FIXED_LESSON_TABLE` 0.579 / `P4_REGIME_RESTRICTION` 0.571 | `P2_EQUIVARIANCE_SOLVER` 0.714 |
| FM50 | `P3_DIAGRAM_CHASE` 0.567 | `P2_CATEGORY_LAW_FUNCTOR` 0.875 |
| FM60 | `P4_SMALL_SCOPE_BOUNDED_CHECK` 0.728 | `P2_EXHAUSTIVE_MODEL_SEARCH` 0.800 |

An M2 loop that reports against a ceiling as if it were a parent reproduces the
ceiling-labelled-as-parent defect the parent-strength audit found programme-wide; the ceiling is
the *check* (does the KSO lose to it anywhere), the oracle-independent arm is the *comparator*.

## 3b. The object's own rows (OCM lane, PRs #290 → #296 reland, #295)

| artifact | KSO component | milestone | status | checker |
|---|---|---|---|---|
| `theory/KSO_SUBSTRATE_CONTRACT_V1.md` Part I (§1–§23), `reference/kso_math_v1.py`, `results/KSO_M0_EXACT_RESULTS_V1.json` (#290, relanded as #296) | **the substrate contract**: warrant semiring (KS-T01), conjunctive firing (T02), substochastic navigation (T03), exact-share pruning (T04), restart contraction (T05), zero-surprise (T06), lumpability gate (T07), connectivity-or-quarantine (T08), impact cone (T09) | M0 | proved (all-size) + checked (20 / 400 / 8,000; 2/2; 1/1; 200/200; 80/80 + 1/1; 5; 1/1) | `tests/unit/test_kso_math_v1.py` (9) |
| `theory/KSO_SUBSTRATE_CONTRACT_V1.md` Part II (§24–§36), `reference/kso_m0_freeze_checks_v1.py`, `results/KSO_M0_FREEZE_RESULTS_V1.json` (#295) | the clauses this section listed absent: edge vocabulary bound to the atlas; **S1–S7 as predicates on the knowledge space** (the genome); KS-T04b retraction propagated to activation; KS-T06b two-direction hub; acquisition transaction with certificate kinds (KS-T18 feedback cannot warrant); atomisation; four-valued navigation outcome with the **obstruction witness** as a definition (KS-T19; ceiling-walker rule = H-EXT-1R; non-identifiability) binding to `jump.JumpTrigger`; compose = ⊗ (T20); extraction unique (T11a); translator invariance reduces to seed equality (T10a); **stem-cell invariant** (T17); budget clause; typing-as-coverage-prior; closed-under-shown | M0 | **frozen V1** — every clause has a planted failure, a must-differ control, a no-alarm case and a distinct `CANNOT_CHECK` | `tests/unit/test_kso_m0_freeze_v1.py` (18) |
| `theory/KSO_PARENT_SUBTRACTION_V1.md` + executable rows (#295) | **parent-subtraction table**: 17 literature rows + 8 parents *run* on one witness (spreading activation, Quillian, ACT-R, Hopfield, CBR, KG/RWR, JTMS, ATMS) | M0 | 0/8 single parents own label-gated exact-share retraction; KSO law = (JTMS gate) ∘ (spreading activation, frozen denominators) entry-wise — `PARENT_PRODUCT_OWNED` | checker F7 |
| `theory/KSO_ARCHITECTURE_V1.md` (#295) | **architecture**: C1 store · C2 solver · C3 codec · C4 channels · C5 immune system · C6 growth · C7 Jump proposer · C8 authority; dependency graph and the may-never rules (codec never writes a label; feedback never warrants; nothing modifies S1–S7; solver never writes; Jump never adopts) | M0 | record; each contract names its theorem, checker and parent | — |
| `reference/kso_m1_mex1_population_v1.py` → `results/KSO_M1_POPULATION_RECEIPT_V1.json` (#295) | **KSO v0 populated from ME-X1** (generator + oracle read-only): atoms = base atoms / evidence / families / claims / results with the oracle's support algebra as ATMS labels; typed hyperedges COMPOSITION / SUPPORT / CONSTRAINT / DEPENDENCE | M1 | **GREEN on the dev split** (50 worlds, seed `ME-X1-DEV-20260902`, byte-reproducible): 3,492 atoms / 1,629 hyperedges, 0 isolated; label ≡ oracle on 585 + 759 cells (v1 with 18 revoked + 7 censored base atoms), 0 mismatches; retraction both directions 400/400 (renormalising parent differs on 16 worlds); events replayed 50/50; hub background-zero / hub-seeded-top 50/50 (evidence-seeded hub wins by surprise 2/50, reported); S1–S7 hold on 100 spaces, digest unchanged. Protected split `NOT_RUN` | `tests/unit/test_kso_m1_mex1_population_v1.py` (9) |

## 4. What is absent (the object is not formed until these rows exist)

| component | milestone | state |
|---|---|---|
| `KSO_SUBSTRATE_CONTRACT_V1` — atom schema, edge types, label semantics, activation law, retraction law, obstruction-witness outcome, budget clause, Jump hooks, parent-subtraction table | M0 | **present, frozen V1** (§3b; #296 + #295) |
| label-gated activation with exact retraction propagation — the checker (planted retraction asserted applied; downstream activation drops exactly; no-alarm on an unrelated node; `CANNOT_CHECK` exit) | M0 | **present** (F2; M1 P3 400/400 on real worlds) |
| hub surprise-weighting checker (two directions) · dense-by-construction checker (edges > 0 at acquisition; reachable by navigation) · atomization checker (k atoms exactly; non-atomic input rejected) · navigation determinism under a committed seed | M0 | **present** (F3, F4, F5; M1 P1, P4) |
| KSO v0 populated from one exact domain (FM10 or ME-X1 generator; oracle held) | M1 | **present on the dev split** (ME-X1, §3b); protected `NOT_RUN` |
| solve loop vs oracle; translator-invariance gate | M2 | absent — design freeze + seed commitment next; comparator arm (B5 ceiling, RWR/PPR, CBR/KG, null, positive control) with the guards lane under one receipt schema |
| gap loop: instruction + demonstration as node-acquisition with edges; revocation replay | M3 | absent |
| Jump loop on v1's 84 opaque worlds | M4 | absent |
| codec at the boundary; chat | M5 | absent (template exists, §2.3) |
| frontier-math pilot | M6 | absent; gated by the stage-1 separation obstruction |

## 5. Custody

Rows carried from #284 comments 5541151080 (seed table), 5541151080-FM (FM40/50/60, PR #283)
and the interface-revival comment (E30-R14 / ME-X6 V3 / H-EXT-1R, PRs #280/#285) are quoted at
the strength their authors gave them; the FM60 dev/protected disagreement is carried as a
disagreement. No number in this file was produced by the OCM lane except the stage-1 row.

## 6. Absorption dispositions — one list for v1 + V2 (operator directive, #284 comment 5543833893)

Disposition vocabulary (the gate; the status column above stays the note): `ABSORBED_AS_CODE`
(re-implemented/imported on the substrate, parity test vs the original on its registered cases) ·
`ABSORBED_AS_CONSTRAINT` (invariant/checker with planted violation + no-alarm) ·
`ABSORBED_AS_BENCHMARK` (its problem set is a milestone's domain, oracle wired) ·
`ABSORBED_AS_PARENT` (matched comparator arm) · `NOT_TRANSFERABLE` (reason + replacement) ·
`PENDING_<milestone>` (disposition assigned, receipt due at that milestone).

| artifact | disposition | milestone | receipt / checker on the machine |
|---|---|---|---|
| `epistemic_atlas.py` `ContextMapKind` vocabulary | `ABSORBED_AS_CONSTRAINT` | M0 | F1: bound to the source enum, drift = fail, unregistered type rejected (`kso_m0_freeze_checks_v1`) |
| `epistemic_atlas.py` charts / gluing (`GluingStatus`, `HorizonStatus`, `UnknownKind`) | `PENDING_M4` (charts = subgraphs; horizon/unknown kinds = obstruction-witness vocabulary) | M4 | none yet; the four-valued outcome carries `GLOBAL_OBSTRUCTION` / `STRUCTURAL_NONIDENTIFIABILITY` today |
| RCL profile = ATMS label; S1–S7; Theorem S4 | `ABSORBED_AS_CONSTRAINT` | M0 / M1 | G1 (7/7 planted violations), G3 growth, M1 P5 on 100 populated spaces; `KS-S1…S7` |
| `ocm_reference_semantics.py` (record store S1–S7) | `NOT_TRANSFERABLE` as code (record-store object, not a hypergraph); replaced by the KSO predicates `ks_S1…S7` with the same planted violations — parity of *statements* recorded in contract §32 | M0 | G1 |
| `ATOMIC_CLAIM_INVENTORY.json` atom schema | `PENDING_M2b` (atom types generalised in contract §2; the paper-package inventory is not yet loaded) | M2b | — |
| `reference/ocm_nonrectangular_class_exact.py` (#288, VSW node type) | `PENDING_M6` (induced-warrant node type; gates M6) | M6 | #288's own checker (2,048/648 worlds, 65,805 classes) |
| ME-X1 generator + oracle | `ABSORBED_AS_BENCHMARK` | M1 / M2 | M1 receipt (50 worlds, label ≡ oracle 0 mismatches on 1,344 + 22 negative cells); M2 receipt (G1 50/50) |
| ME-X1 parents (`mex1_parents.py`, B5 federation) | `ABSORBED_AS_PARENT` (B5 = ceiling control; RWR/PPR, CBR/KG = oracle-independent comparators) | M2 | `KSO_M2_COMPARATOR_RECEIPT_V1.json` (guards lane; dry run B5 50/50, RWR 27/50, CBR 34/50, null 5/50) |
| FM10 / FM20 / ME-X3 exact generators + oracles | `PENDING_M2b` (`ABSORBED_AS_BENCHMARK` when populated; same map as ME-X1) | M2b+ | — |
| FM40 / FM50 / FM60 generators, oracles, protected legs | `PENDING_M2b` (`ABSORBED_AS_BENCHMARK`); their oracle-independent arms `ABSORBED_AS_PARENT` when run | M2b+ | §3 comparator line |
| FM suites' `F0_PARENT_FEDERATION` identity (F0 = oracle by construction) | `ABSORBED_AS_CONSTRAINT` (a comparator sharing the oracle's procedure is a ceiling, never a parent) | M2 | design §0 + receipt labels; `HANDICAPPED_COMPARATOR` guard |
| ME-X4 generator / oracle (B5 origin) | `PENDING_M2b` (`ABSORBED_AS_BENCHMARK`) — **row was missing from the map** | M2b+ | — |
| E40 ranker | `NOT_TRANSFERABLE` (controller-around-LLM ranking; the negative that located the centre) — **row was missing** | — | replaced by label-gated navigation + surprise ranking (F3) |
| E30-R13→R14 boundary contract; `anchored_edit_interface.py` | `ABSORBED_AS_CONSTRAINT` (closed-under-shown, content-hash location, codec never writes a label) | M0 / M5 | F10; **anchored-edit interface row was missing** — `PENDING_M5` as code (the M5 codec adopts its §6 substitution) |
| ME-X6 V3 typing-is-a-coverage-prior | `ABSORBED_AS_CONSTRAINT` | M0 | F9 (full-coverage tie; unexercised type named; no typed advantage claimed) |
| H-EXT-1 / H-EXT-1R witness rule | `ABSORBED_AS_CODE` (four-valued outcome; obstruction iff the ceiling walker also fails) | M0 / M2 | F6, G2-nonidentifiability; M2 outcomes FOUND 45 / GAP 5 |
| ME-X2 locus + minimum escalation | `PENDING_M4` (`ABSORBED_AS_CODE`: the level gate) | M4 | witness → `JumpTrigger.is_admissible` today (F6) |
| v1 `jump.py` J0–J8, `JumpTrigger`, `JumpProposal`, `JUMP_RESEARCH_PROGRAMME_V0` | `ABSORBED_AS_CODE` (hooks: witness binds to the trigger, admissible) / `PENDING_M4` (the loop) | M0 / M4 | F6 binding; loop `OPEN_M4` |
| v1 #558 `ExecutableRegimeWitness.v1` + 84 opaque worlds | `PENDING_M4` (`ABSORBED_AS_BENCHMARK`, first Jump benchmark) | M4 | — |
| v1 knowledge metabolism (`knowledge_metabolism.py`), `structural.py` | `NOT_TRANSFERABLE` as dynamics (static; no reaction) — replaced by §5–§6 navigation; `PENDING_M3` as acquisition vocabulary | M3 | — |
| P-A donor discovery; P-B context-relative transport | `PENDING_M4` (Jump sources) | M4 | — |
| PRA revision-adequacy audit / PRA V2 | `PENDING_M3` (revocation dynamics test bed) | M3 | M1 P3 events replay is the first instance |
| SD70-V3 meta-policy | `PENDING_M2b` (navigation-policy candidate) | M2b | — |
| ME-X3 Lean cross-check | `PENDING_M2b/M6` (EXACT_CHECKER channel; SymPy first, Lean at M6) | M2b / M6 | certificate kind exists (F4 case 6) |
| parent-strength audit (14 faithful parents) | `ABSORBED_AS_PARENT` (table) | M0 | `KSO_PARENT_SUBTRACTION_V1.md` + F7 (8 parents run) |
| `FAILURE_LEDGER.md` 28 classes + `OCM_FAILURE_LEDGER.md` 7 | `ABSORBED_AS_CONSTRAINT` for the classes with a checker on the machine (listed below); the rest stay process vocabularies | all | see class table |
| `pr_merge_gate.py` (six fields) | `ABSORBED_AS_CONSTRAINT` (C5 immune system, merge side) | all | self-test; #297 field 0 |
| LLM-centred arm code, controller-around-LLM designs (P-F, ME-F1, E40, E30-R13) | `NOT_TRANSFERABLE` — retained as the negatives that located the centre | — | — |
| #284 inventory rows not listed above: `patch_emission.py` / `APPLY_CLEAN_BY_CONSTRUCTION` → boundary contract template (`ABSORBED_AS_CONSTRAINT`, F10); PRA audit (above); 26-class ledger (above); ME-X2 (above); atlas (above); RCL (above); FM/ME generators (above); v1 #558 (above); P-A/P-B (above); parent audit (above) | — | — | — |

**Counts (this revision):** `ABSORBED_AS_CONSTRAINT` 9 · `ABSORBED_AS_CODE` 2 · `ABSORBED_AS_BENCHMARK` 1 ·
`ABSORBED_AS_PARENT` 2 · `NOT_TRANSFERABLE` 4 · `PENDING_<milestone>` 12 (M2b 6 · M3 2 · M4 5 · M5 1 · M6 1, rows
counted once at their earliest milestone). Rows added as missing: ME-X4 generator/oracle, E40 ranker,
anchored-edit interface, FM F0 identity.

### 6.1 Failure-ledger classes with a checker on the machine

| class | checker on the machine |
|---|---|
| `VACUOUS_CONTRAST` | two atomizers asserted to differ in source (M2); B5 labelled ceiling; P2 `NO_POWER` labels (M1) |
| `STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE` | power labels per check (`POWERED` / `NO_POWER__…`), M1; design §0 declares G1 by construction |
| `CHECK_THAT_RUNS_AND_CANNOT_FIRE` | every checker has a planted failure that must fire (M0 F1–F10, G1–G3; M1 P1–P5; M2 G5) |
| `NONREPRODUCIBLE_FROZEN_ARTIFACT` | receipts byte-reproducible in-process, asserted (M1, M2) |
| `HANDICAPPED_COMPARATOR` | budget clause: unmatched budgets ⇒ `CANNOT_CHECK` (F8); usage reported (M2) |
| `AUTHORITY_LAUNDERING` | KS-S1 (warrant only through a warranting certificate); KS-T18 feedback cannot warrant |
| `INTERFACE_ASKS_FOR_WHAT_IT_WITHHELD` | F10 closed-under-shown |
| `UNPINNED_SUBSTRATE_CONDITION` / `REPAIR_DOCUMENTED_NOT_LANDED` / `BINDING_OVER_UNCOMMITTED_BYTES` / `RECORDED_REPAIR_NEVER_LANDED` | self-binding test over committed bytes (receipt + freeze record); `DESIGN_DRIFT` ⇒ `CANNOT_CHECK` (M2) |
| `CENSORED_ROUTE` | distinct exit 2 everywhere; censored base atoms resolved exhaustively (M1 P2) or `DEFER_CANNOT_CHECK` (M2 COMPOSE) |
| `UNGATED_CONTROL_VERDICT` | must-differ controls consumed by `run()` (M1 parent-raised ≥ 1; M2 G5) |
| `DEGENERATE_PROBE_STATISTIC` | P4 direction (i) counted per world with the planted ranker |
| `FORECLOSED_FAILURE_MODE` | constraint-edge power via derived negative-evidence worlds (M1) |
| `NONIDENTIFIABLE` | `STRUCTURAL_NONIDENTIFIABILITY` obstruction witness (G2-nonidentifiability) |
| `IMMUTABLE_TARGET_MUTATED_BY_ITS_OWN_BINDING_TEST` | the freeze record binds every other file and never itself |

Without a checker on the machine (process vocabularies, audited by hand per PR): `COVERAGE_GAP`,
`REPO_COLLISION`, `DONOR_RECONSTRUCTION_FAILURE`, `FALSE_STRUCTURAL_ANALOGY`, `DONOR_PRODUCT_TIE`,
`V1_PARITY_RISK`, `PREMATURE_IMPLEMENTATION`, `SILENT_MODEL_SUBSTITUTION` (no LLM in the loop yet; becomes
a checker at M5), `MANDATE_EXPLORATION_COLLAPSE`, `UNGUARDED_DEPENDENT_CHECK`,
`TERMINAL_OVERSTATES_ITS_PROCEDURE`, `REGISTERED_SCOPE_DIVERGENCE`, `CHECKER_STAGED_ON_THE_WRONG_SUBSTRATE`,
`RENDERED_SURFACE_SUBSTITUTED_FOR_THE_FACT`, and OCM `DANGLING_CROSS_REFERENCE`,
`TARGET_ARCHITECTURE_PRESUPPOSED`, `PARALLELISM_CEILING_BREACHED`, `SUPERSEDED_BINDING_MISATTRIBUTED`.
