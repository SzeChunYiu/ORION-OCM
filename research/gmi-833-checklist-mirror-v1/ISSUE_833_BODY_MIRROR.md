# GMI Ultimate Theory Review & Architecture-Prior-Free Derivation Programme

> **Evidence pointers.** A closed row ends with its source refs, package name and a ledger key `L:<12 hex>`. The full evidence text for every row is held byte-exact in [research/gmi-833-checklist-mirror-v1/EVIDENCE_LEDGER_V1.json](research/gmi-833-checklist-mirror-v1/EVIDENCE_LEDGER_V1.json) under that key, together with the row's stated text and section. Row texts are never rewritten here; see `research/gmi-833-checklist-mirror-v1/FREEZE_V1.md` for the invariants and the measured defect this replaces.

## Purpose

Issue #602 reached **731/731 checklist closure**, but that means every identified question has some package-scoped evidence; it does **not** mean GMI is ontologically complete or ready for a flagship general-theory claim.

This issue starts the next phase: **audit the entire scientific corpus from first principles, repair/upgrade the mathematics, remove architecture priors, derive known machine-intelligence forms from a neutral substrate, prospectively predict unknown forms, and raise the evidence standard to top-tier journal level.**

The programme must distinguish:

```text
expressible != admissible != derivable != reachable != selected != recovered != predicted != replicated != real-scale validated
```

No checkbox is earned by prose, naming, analogy, or representability alone.

---

# A. Scientific constitution and claim discipline

- [x] Define the exact flagship scientific question in one sentence. — ✅ #837 `gmi-833-foundation-v1` L:50af993017de
- [x] Define the weakest defensible GMI core claim. — ✅ #837 L:e34a654b27d4
- [x] Define the strongest eventual GMI claim. — ✅ #837 L:ad5569751f7d
- [x] Define explicit forbidden claims at each evidence level. — ✅ #837 L:a6e576c9c95d
- [ ] Replace ambiguous uses of `obligation` in paper-facing theory with academically grounded terminology (`task`, `behavioral specification`, `requirement`, etc.) while preserving exact legacy mappings.
- [x] Define `behavioral specification` formally and prove its relation to existing obligation objects. — ✅ #837 L:bd24ce79e055
- [x] Define architecture-prior-free derivation formally. — ✅ #837 L:d7efb3a87ea8
- [x] Prove why literally assumption-free/prior-free derivation is impossible or ill-posed. — ✅ #837 L:ce339d836b8f
- [x] Define what counts as an architectural prior, representation prior, operator prior, search prior, ecological prior, and evaluation prior. — ✅ #837 L:bec1b56f9f59
- [x] Create a prior-disclosure schema for every derivation experiment. — ✅ #837 L:21e02394560d
- [x] Define evidence levels for every GMI claim. — ✅ #837 L:e891c65db096
- [x] Define a maturity ladder, e.g. M0 concept → M1 theorem → M2 exact witness → M3 architecture-prior-free recovery → M4 frozen held-out prediction → M5 independent replication → M6 real-scale prospective validation. — ✅ #837 L:6c6363294b42
- [x] Re-score every major existing GMI result on the maturity ladder. — ✅ #938 #948 `gmi-833-maturity-rescore-v2-v1` L:424102dc88f0
- [x] Require every result to state scope, quantifiers, assumptions, falsifiers, strongest parents, and forbidden extrapolations. — ✅ #972 #975 `gmi-833-claim-discipline-v1` L:b59a341e8d0b (refreshed to the v2 state: `REGISTRATIONS_V2.json` registers 235 claim-bearing objects / 1,175 field slots with **0 REGISTERED_GAP**, superseding the v1 figures of 234 / 1,162 / 8 that this row carried; v2 pins `v1_baseline` by sha256 `b6bd7503…` so the supersession is traceable, and the frozen baseline's assertion A7 already cites the v2 state)
- [x] Establish an explicit rule that checklist closure never implies ontological completeness. — ✅ #837 L:126fe2a50bb9

# B. Full corpus scientific audit

- [x] Inventory every GMI theorem, lemma, proposition, definition, algorithm, experiment, receipt, and claimed law on `main`. — ✅ #948 `gmi-833-corpus-census-v1` L:1695636fd640
- [x] Build a machine-readable theorem dependency graph. — ✅ #949 `gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json` L:f589a9b2351d
- [x] Identify circular dependencies. — ✅ #949 `gmi-833-depgraph-adjudication-v1/CYCLE_REPORT_V1.json` L:d366c5a17667
- [x] Identify duplicated results under different terminology. — ✅ #976 #949 `gmi-833-corpus-passes-v2-v1/detector_l42_v1.py` L:46e7501b834b
- [x] Identify claims whose theorem names are stronger than their actual quantifiers. — ✅ #949 #939 #939 `OVERSTRONG_ADJUDICATION_V1.json` L:236b793cd0fd
- [x] Identify proofs that rely on finite enumeration where an analytic proof is possible. — ✅ #976 #939 L:cf99efbeb44a
- [x] Identify analytic claims supported only by computation. — ✅ #976 L:70607e64bd3f
- [x] Identify computational claims with no independent implementation. — ✅ #976 L:4a215e514e6e
- [x] Identify assumptions introduced after observing outcomes. — ✅ #976 L:9a75991eb651
- [x] Identify search grammars that encode the target morphology. — ✅ `gmi-833-grammar-morphology-encoding-v1` GME-1/GME-2/GME-5/GME-6: the structural/cost route #976's L48-SCREEN and the A2 signature extension both declared out of lexical reach was built and run — name-blind target-exclusivity (deleting a production set changes the declared target's minimum description cost and NO other class's), exact integers. Over 13 corpus grammar instances from 4 merged packages (11 with a verbatim-cited declared target): **7 encode their declared target, 0 ENCODES_UNDISCLOSED**, split because for some the audited package's own classifier reads the production symbol — **2 COST_MEASURED** (#897's grown library is the only finite gap: unfolding `{m1,m2}` raises mu(REUSE_POSITIVE) 2→5 over 181 target presentations and moves selection to UNRELATED_CONTROL; `cross_grammar_routing_B` qualifies on an indicator margin of 1) and **5 PRODUCTION_IS_CLASS_INDICATOR** at margin 0 (`shared`×2, `not_s`, `rows`, `leaves`) where the morphology taxonomy IS the grammar's vocabulary. 0 corpus grammars came out NEUTRAL. Lexical route over 158 packages / 1,923 blocks: 37 hits, all 37 adjudicated with written reasons, 0 CONFIRMED (PARENT_LITERATURE_ATLAS 19 / AUDIT_RECORD_ECHO 10 / SUBSTRING_COLLISION 5 / PROSE_NEGATION 3) — the two routes overlap on nothing, i.e. every encoding in this corpus wears a neutral production name. Detector power proven before any finding was emitted: #891's GA/GB re-found (ALPHA→BETA at w=(1,1), equal coverage), 11/11 planted shortcuts caught in real corpus grammars, 0 alarms on the clean control, 7/7 hostiles detected, 204 randomized isometry controls with 0 spurious changes, and field-for-field executor↔independent-oracle agreement. 4 instances SCREENED_NOT_ADJUDICATED (3 NO_PRODUCTION_STRUCTURE, 1 NUMERIC_PARAMETER_SPACE) + 2 NO_DECLARED_TARGET are screened, not cleared; #891's boundary is cited EARNED-BY-COUNTEREXAMPLE and reproduced (55 remints, 3 reversals), never overturned; INSTANCE-AJ9-NOSMUGGLING-SCOPE carried forward open.
- [x] Identify cost models that structurally force the claimed winner. — ✅ #976 #891 L:1a3d757bf1b5
- [x] Identify hidden architecture macros or privileged operators. — ✅ #976 L:0c4deccb1c56
- [x] Identify hidden independence/iid/stationarity assumptions. — ✅ #976 L:fbf345767611
- [x] Identify hidden finite-horizon assumptions. — ✅ #976 L:ffd5c1509877
- [x] Identify claims that fail under alternative but reasonable resource accounting. — ✅ #976 #891 L:acae9297a267
- [x] Identify claims sensitive to arbitrary encoding choices. — ✅ #976 #863 #875 L:e22a58325b32
- [x] Identify claims sensitive to search algorithm rather than scientific structure. — ✅ #976 #863 L:600c3dcc2d41
- [x] Identify claims that are only rediscoveries of parent mathematics. — ✅ #976 L:aebb7d048eb1
- [x] Produce a RED / AMBER / GREEN audit table for the entire corpus. — ✅ #949 `AUDIT_V1.json` L:a82aa4c429dc
- [x] Downgrade or retract any unsupported overclaim. — ✅ #976 #949 L:79a4e1737315
- [x] Freeze an audited `GMI_THEORY_BASELINE_V1` before further upgrades. — ✅ #977 #845 #939 `c4def870` L:7bf2e02df895

# C. Mathematical foundation rebuild

- [x] State the minimal mathematical objects required by GMI. — ✅ #837 L:dbcf4522f1a0
- [x] Formalize machine state carriers without architecture names. — ✅ #837 `X` L:e4a713003e19
- [x] Formalize observations, actions, outputs, transformations, update channels, communication, verification, and resources. — ✅ #837 `Q,U,Chi,rho` L:1b003ac2ef8b
- [x] Formalize behavioral specifications independently of implementation. — ✅ #837 `B=(I,Acc)` L:6bed59929399
- [x] Formalize behavioral equivalence / specification equivalence. — ✅ #837 L:ef3884a25beb
- [x] Define minimal sufficient state and quotient constructions. — ✅ #837 #516 L:513b5c6eb389
- [x] Relate GMI equivalence formally to Myhill–Nerode equivalence where applicable. — ✅ #846 `gmi-833-parent-equivalence-v1` L:ed7da4176826
- [x] Relate it to bisimulation/state abstraction where applicable. — ✅ #846 L:bf11543c13ac
- [x] Relate it to sufficient statistics and predictive-state representations where applicable. — ✅ #846 L:7502942ceae0
- [x] Prove exactly where those parents do and do not subsume GMI. — ✅ #846 L:8a90f5196602
- [x] Formalize developmental history as a mathematical object. — ✅ #837 L:179c0cb30eab
- [x] Formalize developmental/search dynamics. — ✅ #837 `Delta` L:06a49fb5ed81
- [x] Formalize reachability under a developmental law. — ✅ #837 `Reach_Delta(M0,B)` L:a78b21884676
- [x] Formalize morphology equivalence and machine-species equivalence. — ✅ #848 `gmi-833-morphcap-v1` L:b4123c20e04e
- [x] Formalize capability as an architecture-independent object. — ✅ #848 L:548e875fc5aa
- [x] Formalize capability ceilings and impossibility regions. — ✅ #848 L:090c8673d18f
- [x] Formalize lifecycle resource vectors rather than a single scalar cost. — ✅ #837 #805 L:8f8a01d1cdf4
- [x] Prove when scalarization preserves Pareto order and when it does not. — ✅ #837 L:b272cb42208b
- [x] Formalize uncertainty sets/confidence objects throughout GMI. — ✅ #851 `gmi-833-global-uncertainty-v1` L:3b33bd7811e4
- [x] Prove composition rules for uncertainty at the general claimed scope. — ✅ #851 #757 #759 `1-alpha-sum beta` L:c98b583353b3
- [x] Define abstention / non-identifiability semantics globally. — ✅ #851 `UNKNOWN` L:97de8a2b2fb8
- [x] Produce a compact axiom/definition set from which the rest of GMI can be derived. — ✅ #854 `gmi-833-axiom-core-v1` L:be4d8c9ed112
- [x] Prove consistency/non-contradiction of the registered finite core where decidable. — ✅ #854 L:2f6ff2c4c5dd
- [x] Separate universal theorems from finite-scope theorems in the notation itself. — ✅ #837 `forall[D]` L:d2bd8e1c269a

# D. Architecture-prior taxonomy and no-smuggling standard

- [x] Define P0: named architecture supplied. — ✅ #837 L:0dcaf0d10f63
- [x] Define P1: architecture-specific property vector supplied. — ✅ #837 L:f5daa24889e9
- [x] Define P2: representation/operator family supplied. — ✅ #837 L:085840aa24a8
- [x] Define P3: only generic computational primitives supplied. — ✅ #837 L:2af4dea947e5
- [x] Define P4: grammar can create/compress new primitives recursively. — ✅ #837 L:9bf6f071c422
- [x] Decide which levels may legitimately support `derive` language. — ✅ #837 L:961ccd4c2ca1
- [x] Require flagship known-form claims to reach at least P3 unless formally justified otherwise. — ✅ #837 L:7c32c1ca5396
- [x] Require unseen-form claims to reach P3/P4. — ✅ #837 L:c5b5e939122b
- [x] Build an automated architecture-name/macros leakage detector. — ✅ #855 `gmi-833-no-smuggling-audit-v1` L:a47e067ec559
- [x] Build a semantic leakage audit: detect architecture-specific operators disguised under neutral names. — ✅ #855 `mix` L:9cc2e341b24e
- [x] Build a cost-prior audit. — ✅ #855 L:3490455cfd04
- [x] Build a search-prior audit. — ✅ #855 `SEARCH_PRIOR_SENSITIVE` L:b9ba0c263076
- [x] Build an evaluation-prior audit. — ✅ #855 `EVALUATION_PRIOR_SENSITIVE` L:b20a068c9290
- [x] Build an ecology-selection-bias audit. — ✅ #855 L:9155899e1c08
- [x] Require matched grammar twins that remove the predicted mechanism without changing irrelevant search capacity. — ✅ #863 `gmi-833-robustness-controls-v1` L:2116a111725e
- [x] Require alternate encodings of the same semantics. — ✅ #863 `ENCODING_SENSITIVE` L:cbd5600c8ecf
- [x] Require alternate search algorithms. — ✅ #863 `SEARCH_ALGORITHM_SENSITIVE` L:12b00fa28a50
- [x] Require alternate resource scalarizations / Pareto analysis. — ✅ #863 `(1,4)` L:f9f2f694e1bd

# E. Universal architecture-neutral machine grammar

- [x] Define a minimal architecture-neutral grammar `G0`. — ✅ #868 `gmi-833-g0-register-core-v1` L:7eea23c81b68
- [x] Justify every primitive in `G0` from computation/interaction requirements rather than known architectures. — ✅ #868 `READ/EMIT/INC/DECJZ/HALT` L:ff2cd992e262
- [x] Prove which known computational models `G0` can express. — ✅ #868 `INC/DECJZ/HALT` L:1091db5fbbdc
- [x] Quantify description-length bias induced by `G0`. — ✅ #875 `gmi-833-g0-grammar-bias-v1` L:179daf4d7e79
- [x] Quantify reachability bias induced by `G0`. — ✅ #875 `0:1, 1:15, 2:110` L:c593c87e545a
- [x] Construct multiple semantically equivalent grammars with different syntax. — ✅ #875 `GA/GB` L:67ab6d8338bf
- [x] Test whether morphology conclusions survive grammar reminting. — ✅ #875 `GA/GB` L:aa6e72e92d20
- [x] Add typed state carriers without naming neural/symbolic/probabilistic families. — ✅ #868 L:0fead43da9d8
- [x] Add generic local/global operators. — ✅ #882 `gmi-833-g0-local-graph-ops-v1` L:494bfb4342c3
- [x] Add composition. — ✅ #868 L:f29163c6f8d9
- [x] Add recurrence. — ✅ #868 L:84e4307560f3
- [x] Add addressable storage/retrieval. — ✅ #868 L:647c964a8b2b
- [x] Add stochastic state and update operators. — ✅ #885 #851 `gmi-833-g0-stochastic-update-v1` L:7d3d55910907
- [x] Add graph/local interaction operators. — ✅ #882 L:5bbacfb1026f
- [x] Add communication/multi-agent operators. — ✅ #887 `gmi-833-g0-interaction-channels-v1` L:c3e86f607a76
- [x] Add external tool/environment calls. — ✅ #887 `EXTERNAL_DATA` L:9c94735c654a
- [x] Add self-modification/development operators. — ✅ #889 `gmi-833-g0-governed-self-change-v1` L:85959a78d158
- [x] Add verifier-gated adoption operators. — ✅ #889 `VERIFIER_V1` L:4a0eab027f42
- [x] Add resource-metered execution. — ✅ #868 `(program_instructions, steps, register_reads, register_writes, input_reads, output_writes)` L:78983a33a1bc
- [x] Adjudicate whether the grammar privileges a known family under the registered cost model. — ✅ #891 `gmi-833-g0-cost-privilege-v1` L:f28f4e4c6ff9
- [x] Define grammar expansion `G_t -> G_{t+1}` from discovered reusable abstractions. — ✅ #897 `gmi-833-g0-grammar-growth-v1` L:24705770e467
- [x] Implement recursive library formation / primitive invention. — ✅ #897 `m1 -> a b` L:b6990027e92e
- [x] Test whether newly invented primitives reduce future discovery cost on unseen tasks. — ✅ #897 `K_total=6` L:e594377d753f

# F. Intelligence-space generator

- [x] Formalize the candidate machine space `M(G0, B)` under finite budget `B`. — ✅ #966 #956 `G0-fin-v1` L:ab2bb373d042
- [x] Define semantic equivalence classes so implementation duplicates collapse. — ✅ #966 #956 L:be1c2a3b317e
- [x] Define morphology/species descriptors independent of architecture names. — ✅ #966 #956 L:69d09fe699e0
- [x] Implement exact enumeration for small budgets. — ✅ #966 #956 L:24f831883e2f
- [x] Implement scalable sampling for large budgets. — ✅ #1003 #1002 `M(G0-fin-v1,(64,32))` L:aabb7f1eba82
- [x] Generate at least 10^6 architecture-neutral candidates. — ✅ #1007 #1006 `G0-fin-v1` L:f9d74c2c9911
- [ ] Scale to at least 10^8 candidates or justify an equivalent effective coverage method.
- [x] Measure duplicate/equivalence collapse rate. — ✅ #984 #983 `(2,2)` L:c49f8366eb1e
- [x] Measure reachable fraction under each developmental/search law. — ✅ #1001 #1000 #966 `(2,2)` L:eb9d280a6d63
- [x] Measure Pareto-front density. — ✅ #996 #994 `(1,1): 2/4=1/2` L:a6600138899c
- [x] Cluster candidates only after generation/evaluation. — ✅ #999 #998 #966 `15/2` L:b84b68d62924
- [x] Blindly map recovered clusters to known architecture families after the fact. — ✅ #999 #998 L:b90e9e980726
- [x] Maintain an `UNKNOWN` cluster class; do not force every candidate into a known taxonomy. — ✅ #999 #998 `UNKNOWN` L:50edb3e8eed2
- [x] Develop novelty metrics that are not mere syntactic distance. — ✅ #984 #983 `(1,1)` L:63156d2864a3
- [x] Develop semantic/resource/developmental morphology distance. — ✅ #984 #983 `9/100` L:4c788b97266d
- [x] Validate clustering stability under grammar remints and metric perturbations. — ✅ #999 #998 #984 `9/100` L:0aa0dff20181

# G. Ecology/specification generator

- [x] Define an architecture-neutral generator of behavioral specifications. — ✅ #959 #957 L:0c9ce10be2ea
- [x] Define systematic environment/ecology families. — ✅ #959 #957 L:d0d302d3137c
- [x] Vary observability. — ✅ #959 #957 L:fb8f66ae02f0
- [x] Vary recurrence. — ✅ #959 #957 L:101db150c6fe
- [x] Vary uncertainty/noise. — ✅ #959 #957 L:4ab655a68f87
- [x] Vary causal ambiguity/intervention access. — ✅ #959 #957 L:ebfca663dc7b
- [x] Vary compositional structure. — ✅ #959 #957 L:ba0344942e8c
- [x] Vary spatial/locality structure. — ✅ #959 #957 L:59265b5e1308
- [x] Vary symmetry/equivariance. — ✅ #959 #957 L:ea1d00c25a5e
- [x] Vary communication topology. — ✅ #959 #957 L:ce82ff6c8a09
- [x] Vary multi-agent competition/cooperation. — ✅ #959 #957 L:e77d6b56619a
- [x] Vary verification availability/cost. — ✅ #959 #957 L:0d3304ccdafd
- [x] Vary memory price. — ✅ #959 #957 L:d6baacce0540
- [x] Vary compute price. — ✅ #959 #957 L:29729d1ab13c
- [x] Vary communication price. — ✅ #959 #957 L:9e298757e049
- [x] Vary energy price. — ✅ #959 #957 L:31a33f9e64f2
- [x] Vary developmental horizon. — ✅ #959 #957 L:dc46c7cdb463
- [x] Vary nonstationarity/drift. — ✅ #959 #957 L:318dcae0cbca
- [x] Vary embodiment/sensor-action constraints. — ✅ #959 #957 L:d82a83026660
- [x] Construct matched positive/negative ecology twins. — ✅ #959 #957 L:3c115ccf842d
- [x] Construct ecology families not designed around known architectures. — ✅ #959 #957 L:493b2ae8bcbd
- [x] Sample enough ecology space to avoid hand-picked niche bias. — ✅ #985 #982 L:338b488bcd44
- [x] Quantify ecology sampling bias and uncertainty. — ✅ #985 #982 L:02b19636b172

# H. Prior-free derivation of known machine-intelligence families

For every family below, require: property prediction from specification/ecology; P3/P4 grammar; no family macros; neutral recovery; negative twin; lower bound where possible; resource crossover; held-out frozen prediction; remint; independent search; real-scale test.

- [x] Finite-state/automata intelligence. — ✅ gmi-833-h-real-scale-classical-v1 RSC-1 RSC-2 RSC-3 RSC-4 RSC-5: one unchanged neutral grammar (12614 candidate pairs, digest da32872d3659) blind-selected the persistent-state program MUL(ARG,PARAM) | ADD(NEG(STEP(STATE)),S) on 466750/155583 fit/held-out real rows of the sha256-bound Debian lexicon, whose exact held-out decision-error count 17557 beats the blind-selected stateless program's 17584, with the order-randomised null at 0/200 and all eleven gates at SIGMA_H01.
- [ ] Linear regression / linear classifiers.
- [ ] GLMs.
- [ ] Basis/kernel methods.
- [ ] Nearest-neighbor / exemplar memory.
- [ ] Associative memory.
- [ ] Retrieval-augmented systems.
- [ ] Decision trees/rule systems.
- [ ] Symbolic logic systems.
- [ ] Program synthesis/program induction.
- [ ] Library-learning/program-reuse systems.
- [ ] Search/frontier algorithms.
- [ ] Planning systems.
- [ ] Dynamic programming/control.
- [ ] Model-free RL-like learning.
- [ ] Model-based RL-like learning.
- [ ] Bayesian inference/belief-state systems.
- [ ] Probabilistic graphical models.
- [ ] Particle/population inference.
- [ ] Feed-forward neural networks.
- [ ] Backprop/reverse-mode credit assignment.
- [ ] CNN/equivariant local-weight-sharing systems.
- [ ] RNNs.
- [ ] LSTM/GRU-like gating.
- [ ] Attention mechanisms.
- [ ] Transformer-like dynamic routing/composition.
- [ ] Graph neural/message-passing systems.
- [ ] State-space models.
- [ ] Mixture-of-experts/routing systems.
- [ ] Autoregressive generative systems.
- [ ] Latent-variable generative systems.
- [ ] Flow-like transport systems.
- [ ] Diffusion/iterative-refinement systems.
- [ ] Energy-based systems.
- [ ] Evolutionary/population search.
- [ ] Cellular/local-field computation.
- [ ] Distributed/collective intelligence.
- [ ] Tool-using/solver-routing intelligence.
- [ ] Neuro-symbolic/statistical-symbolic hybrids.
- [ ] Continual-learning systems.
- [ ] Meta-learning systems.
- [ ] Self-modifying/morphogenetic systems.
- [ ] Multi-agent emergent communication systems.
- [x] Verify that the same neutral grammar can recover several families without per-family redesign. — ✅ #931 #937 #951 `BIAS_LEDGER_V1.json` L:7e31b8fd301b
- [x] Quantify which families cannot be recovered and why. — ✅ #987 #986 `B=3` L:e812505e0dbe

# I. Learning-law derivation without algorithm priors

- [x] Define the space of admissible update laws architecture-neutrally. — ✅ gmi-833-update-law-space-v1 IL-1.1/IL-1.2/IL-1.3/IL-1.4/IL-1.5: update laws over the #837 realization contract are admissibility-decidable in ≤1134 exact rational operations per law per grade and closed under rational mixture (686/686) and composition (49/49) with a two-sided monoid on kernels (two-sidedness rests on the AX-3-derived quiet-step clause, disclosed post-freeze deviation D1; disabling it flips exactly 1 of 774 certificate leaf fields — `monoid_identity_ok` — leaving left identity only and every other IL-1/2/3/4 field invariant), while the one-step grade is not closed and worst-case charge is only subassociative (both EARNED-BY-COUNTEREXAMPLE, 5 vs 8); name-freedom certified over 21,420 tokens with 0 unmatched denylist hits, A2 clean, and 14/14 verdicts remint-invariant, both routes agreeing on the whole census.
- [x] Derive conditions favoring local trial-and-error updates. — ✅ gmi-833-update-law-space-v1 IL-2a/IL-2: every verified-selection evaluative-only law costs exactly (d+1)/(m+1) probes under the successor-relabeling orbit (an unconditional equality over the family, worst case d−m+1), so evaluative-only strictly dominates exactly when the price ratio exceeds rho* = mean_i (d_i+1)/(m_i+1) — 2047 such verdicts over 3450 registered cases, two routes agreeing 21/21 on the probe table and 3450/3450 on the grid, nulls 0/200.
- [x] Derive conditions favoring directional/gradient information. — ✅ gmi-833-update-law-space-v1 IL-3/IL-3b/IL-23: the matched converse holds strictly below the same rho*, and the two conditions partition the registered price/ecology space exactly (75 paths × 46 ratios = 3450 cases, 0 partition failures, 2047/1331/72 split, crossover surface price_sel = rho*·price_pt), with direction informationally worthless exactly at full improving density (rho* = 1 on 19/75 paths) and unbounded as improvement thins (max 7/2), the per-instance boundary EARNED-BY-COUNTEREXAMPLE.
- [x] Derive reverse-mode credit assignment from graph/resource structure rather than naming backprop. — ✅ gmi-833-update-law-space-v1 IL-4a/IL-4b/IL-4c/IL-4e: reverse accumulation needs exactly p sweeps and forward exactly n, necessary as well as sufficient (verified n=2..6, p=2..4), so 1 vs n at p=1; it wins exactly below the retention-price threshold sigma* = (n−p)E/(N−w) (21/2, 55/4, 32 on the registered graphs, tie at sigma*) and loses at EVERY price when p>n; and the order is RECOVERED by exhaustive census over all interior elimination orders with no algorithm name in the space or objective — argmin reverse-topological in every registered p=1 graph, flipping to topological at n=1,p=4, and a MIXED order on skip_waist_n2_p2 (7 vs 10 and 10) as the earned boundary.
- [x] Derive conditions favoring Bayesian update behavior. — ✅ gmi-833-update-law-regimes-v1 UL-2: the external signature “successor distribution is the exact conditional of the registered prior” strictly dominates its point-summary comparator exactly when p_carry/lam < beta* = alpha_gain/((M−1)T) — 1/16, 0, −1/32, 1/48, 3/16, 3/16 on the six registered environments — because the extra charge of carrying the full weighting is exactly p_carry(M−1)T and its value is exactly lam·alpha_gain; the matched converse is UNCONDITIONAL: alpha_gain ≤ 0 makes beta* ≤ 0 unsatisfiable over Q_{>0}, verified with 0 violations over 2187 registered prices on each of the two environments where it fires (posterior already concentrated, and target outside the registered candidate set), both routes agreeing on every value.
- [x] Derive conditions favoring memory/exemplar update. — ✅ gmi-833-update-law-regimes-v1 UL-3: an instance no registered query retrieves is strictly wasteful (same emitted predictor, strictly lower charge at every positive price), so the minimal-charge stored-instance law retains exactly the retrieved set of size mu, and the crossover against the compression law is the exact rational chi* = 147/8, 109/6, 221/3, 163/4, 163/4 on the five usable environments; the trichotomy is exhaustive and exclusive on the parent's own 46-ratio grid with 0 failures in 230 cases (that grid tops out at 12 and so does not straddle chi*, which the anchored probes at chi*/2, chi* and 2·chi* do by construction), the regime is WITNESSED at explicit registered prices on all five, and route B locates every chi* by outward scan and bracket without ever consulting the closed form.
- [x] Derive conditions favoring rule induction. — ✅ gmi-833-update-law-regimes-v1 UL-4, EARNED-BY-COUNTEREXAMPLE with the boundary mapped and the adjacent scoped positive exhibited: production compression pays exactly when (cover−Dmin)(p_carry·T + p_test·nq) > p_test·disc + p_build·Dmin, i.e. exactly below the discovery-charge bound disc* — 10 on D1 (at most 5/2 productions searchable), 20 on D2 (at most 10/3), and exactly 0 on D4, D5 and D6, where no discovery charge at all makes it win. At the registered 72-production space disc = 144–432 exceeds every one of these bounds, the p_build crossover is negative on all five usable environments (−137/2, −102, −108, −155/4, −155/4), three carry an unconditional coordinatewise DOMINATED_EVERYWHERE certificate, and the regime is WITNESSED on NO environment at any registered price on either grid. The condition favouring rule induction is therefore a bound on the size of the space the rules are discovered in, the bound is exact, and the registered space exceeds it everywhere — a mapped boundary, not a witnessed positive.
- [x] Derive conditions favoring program/library learning. — ✅ gmi-833-update-law-regimes-v1 UL-5, closed BY RECONCILIATION TO #897 `gmi-833-g0-grammar-growth-v1`, which owns grammar growth, recursive library formation, primitive invention and the held-out reuse benefit and whose results are NOT re-derived here: the residual is the update-law-space placement, where the re-invocation refinement of a description-emitting law is favoured exactly when Hocc·Delta > Kdef — #897's THR-1 lifecycle threshold restated in this tranche's price coordinates — and the refinement bites where it holds, cutting the constructed length from Dmin = 4 to 3 on D1 and from 4 to 1 on D5 and D6 while leaving D2 and D4 unmoved; sign agreement with #897 is checked in the receipt and LIBRARY_INVENTION_RESULT_IS_NOVEL_HERE is a forbidden promotion.
- [x] Derive conditions favoring evolutionary/population search. — ✅ gmi-833-update-law-regimes-v1 UL-6: carrying a multiset of at least two candidates and selecting over it strictly dominates the single incumbent exactly when p_branch/lam < pistar* = (Vglob−Vloc)/((Bmin−1)·Tsteps), equal to 1 on the five multimodal registered environments and WITNESSED at explicit prices on three of them; the matched converse is UNCONDITIONAL — a unimodal score landscape sends every registered start to the same terminal, so Vglob−Vloc = 0, pistar* = 0, and by UL-9 every breadth≥ 2 law emits the same predictor as its breadth-1 counterpart and is strictly dearer at every positive price, verified on the registered unimodal environment and again on the held-out one as frozen prediction HO-P3.
- [x] Derive conditions favoring meta-learning. — ✅ gmi-833-update-law-regimes-v1 UL-7: a step rule indexed by a parameter carried across episodes repays its charge exactly when p_meta/p_test < tau* = r·T·(K−k0)/(|H'|·K) with registered relatedness r = M−|H'| — 12/5, 18/5, 18/5, 6/5, 6/5 at r = 4 and exactly 0 at r = 0 — and the falsifier the row demands is delivered UNCONDITIONALLY: at r = 0 the indexed rule is behaviourally IDENTICAL to the base rule, verified pointwise at all 32 registered (episode, instance) inputs with 0 mismatches by both routes, while costing p_meta·|H'|·K = 36·p_meta more, so the regime is vacuous exactly when relatedness vanishes.
- [x] Derive conditions favoring self-modification. — ✅ gmi-833-update-law-regimes-v1 UL-1/UL-8: because the parent's admissibility is a POINTWISE conjunction, the admissible law space is closed under arbitrary pointwise selection (strengthening IL-1.2's mixture closure and absorbing history-dependent switching), so a law that changes its own admissible successor set is extensionally a fixed member of the class and pays a strictly positive mutation charge on top — the conditions favouring it inside any pointwise-selection-closed class are EMPTY, certified by s* = 0 on all six environments and strictly dearer than its comparator at all 2187 registered prices on every one, vacuous in the non-redundant grammar everywhere, with hostile HR-09 planting the opposite claim and refused; the matched positive is EARNED-BY-COUNTEREXAMPLE from the parent's own IL-1.3, since the ONE_STEP grade is NOT composition-closed and a law confined to it reaches a realization (r2) that no fixed law of that class can, so p_mut/lam < s* is satisfiable exactly when the comparison class fails closure — a condition on the class, not on the ecology or the price. Demarcated from #848/#874: this is cost and reachability inside the law space, not governance.
- [x] Prove no-free-lunch boundaries: no universal best update law without ecological assumptions. — ✅ #870 `gmi-833-update-law-nfl-v1` L:b74dd3b70549
- [x] Build a prospective learning-law selector. — ✅ gmi-833-update-law-regimes-v1 UL-11: a total deterministic function from the registered (ecology invariants, channel, price) triple to a regime or one of three typed abstentions (ABSTAIN_UNDERDETERMINED, ABSTAIN_ILL_TYPED, ABSTAIN_TIE), whose decision table is committed in FREEZE_V1.md at 6e42ccd2 BEFORE any census commit so that git order proves the prospectivity; soundness — when it selects, that law attains the strict minimum charge among the seven registered representatives and over their whole rational mixture hull (the hull extension is the parent's IL-1.2) — holds with 0 soundness violations and 0 mixture-hull violations over the frozen 2187-price grid and the anchored set on all six environments, totality verified case by case, and hostiles HR-13 (a dropped abstention), HR-10 (a tie absorbed into a regime cell) and HR-02 (a float price) all refused.
- [x] Recover selected learning laws under neutral search. — ✅ gmi-833-update-law-regimes-v1 UL-12: exhaustive enumeration of the frozen structural tuple grammar, filtered by UL-9 to the non-redundant laws, with no family token in any coordinate, in the objective or in the tie rule — the objective is exactly the charge ⟨a(g,E), pi⟩ and the signature of the argmin is computed only AFTER the search — returns the selector's regime with 0 disagreements on all six environments, on both the frozen grid and the anchored crossover set, under both routes; against 200 randomised regime assignments the true selector scores 131/131 while the best null scores 33 and 0/200 nulls reach it, a second null of foreign crossover thresholds scores 0/200 against a true threshold that locates the crossover on 5/5 usable environments, and the blindness screen catches 10/10 planted mechanism-named identifiers with 0/10 false alarms.
- [x] Test held-out crossover boundaries. — ✅ gmi-833-update-law-regimes-v1 UL-13: four predictions frozen in FREEZE_V1.md before any outcome, evaluated on six held-out environments built over a different instance set and a structurally different candidate table and used in no derivation — HO-P1 HIT on 10/10 checks (every defined closed-form threshold equals, exactly, the crossover located independently by rational bisection on the charges alone), HO-P3 HIT (both unconditional converses hold on held-out), HO-P4 HIT as stated with no convention change (the held-out set does produce DOMINATED_EVERYWHERE certificates); HO-P2 MISSED as stated with 260 mismatches, and the miss is reported with 260/260 attributed to a SINGLE stage — the frozen selector ranks canonical representatives, a canonical representative can itself be redundant, and a search over non-redundant laws can never return it — leaving 0 unattributed, with the revival select_v2 (rank the charge-minimal non-redundant law of each class, strictly more sound by UL-9) delivered and scoring 794 agreements and 0 disagreements, disclosed as post-freeze deviation D8 beside the frozen selector's unchanged numbers.
- [ ] Test on realistic learning systems.

# J. General morphology-selection theory

- [x] Upgrade the finite relation from `(S,E,R,V,H,D) -> M` into a formal selection theorem/schema. — ✅ #893 #874 `gmi-833-morphology-selection-schema-v1` L:d1c3235d3894
- [x] State sufficient conditions for unique morphology selection. — ✅ #893 L:d9c84e1c2e29
- [x] State conditions for Pareto sets / coexistence rather than unique winners. — ✅ #893 `(1,4),(4,1),(2,2)` L:b8e381b415e0
- [x] Derive phase boundaries analytically where possible. — ✅ #893 `theta_ij=(a_j-a_i)/(b_i-b_j)` L:03ea86f04478
- [x] Quantify uncertainty on phase boundaries. — ✅ #893 `ROBUST_UNIQUE` L:1b2ba70eea9a
- [x] Derive when history changes the selected morphology. — ✅ #895 `gmi-833-history-switching-hysteresis-v1` L:704650a63965
- [x] Derive when migration/switching erases history dependence. — ✅ #895 `K(h,m)=u(h)+v(m)` L:6aa3ea14f505
- [x] Derive when search law changes observed morphology. — ✅ #879 `gmi-833-search-law-morphology-change-v1` L:965c00fc89ad
- [x] Separate optimal morphology from reachable morphology. — ✅ #874 `gmi-833-global-vs-reachable-morphology-v1` L:c2eb8afd55c4
- [x] Derive morphology under finite search budgets. — ✅ #877 `gmi-833-finite-search-budget-morphology-v1` L:62e3c54d58a3
- [x] Derive coexistence/niche partitioning laws. — ✅ #892 L:42bdd6898f7d
- [x] Derive morphology transitions under resource repricing. — ✅ #892 `v_i-v_j=p·(r_i-r_j)` L:30856ef3f1c4
- [x] Prospectively predict at least 20 held-out morphology transitions. — ✅ #901 `gmi-833-heldout-20-transitions-v1` L:df37d5a3ab3e
- [x] Replicate transitions with independent search procedures. — ✅ #901 `FULL_ENUMERATION` L:5131d67035f5
- [x] Validate at least 5 transitions on real systems. — ✅ #903 #901 `gmi-833-real-transition-receipts-v1` L:448a0a6bd697

# K. Capability theory upgrade

- [x] Re-audit all existing capability definitions for architecture independence. — ✅ #921 #918 L:c9262b444b4b
- [x] Re-prove all 11 capability ceilings under the upgraded foundation. — ✅ #921 #918 L:6d69ec61704b
- [x] Generalize ceilings beyond toy finite spaces where possible. — ✅ #921 #918 L:7ded65415915
- [x] Derive capability lower bounds as well as ceilings. — ✅ #907 #906 `NO_FEASIBLE_REALIZATION` L:0d1c1f94ccd3
- [x] Derive capability interactions/synergies. — ✅ #907 #906 `s11-s10-s01+s00` L:42734d9498a6
- [x] Derive capability interference under shared budgets. — ✅ #907 #906 `M` L:bca5875882fc
- [x] Derive failure modes prospectively. — ✅ gmi-833-capability-predictor-v1 KP-2A/KP-2B/KP-2C/KP-2D: a ten-mode taxonomy derived from the registered cut ladder (expressivity, resource, reachability, search budget, evidence) plus the two typed non-answers was frozen in TAXONOMY_V1.md at commit f09288d9 before any executor existed, and partitions all 51,840 registered inputs with 0 overlaps, 0 gaps and 0 unique-binding-cut violations; every mode is non-empty (information ceiling 5,400, expressivity 216, resource 5,976, reachability 2,442, search budget 2,004, observed shortfall 1,410, aliasing 3,529, none 623, inconsistent 30,240, plus 144 cannot-check in the semantics sub-census). Order dependence is earned by counterexample: 6,347/8,640 inputs change attribution across all 120 cut orders, 488 of them with a unique individually-binding lever. Mode assignment agrees across two materially independent routes on every input; the order census is single-route and bounds a declared limitation rather than supporting a claim. This derives and freezes the taxonomy; it does not predict failure of any evaluated system.
- [x] Build `C_hat = F(M,E,R,H,D,U)` capability predictor. — ✅ gmi-833-capability-predictor-v1 KP-1A/KP-1B/KP-1C: `F` is an exact, total, deterministic function of the six registered objects on a frozen 51,840-input grid over 32 registered realizations — 10,640 points, 10,960 abstentions, 30,240 inconsistent, 0 exceptions — with 0 soundness violations, because a point is emitted iff the contract image `q_(E,R)[C]` is a singleton (ABSTAIN-1) and `R` scores infeasible candidates `UNSATISFIED` inside the image instead of deleting them from the survivor set; all 10,960 abstentions exhibit two survivors with different verdicts, so abstention is forced. The NULL_MARGINAL control emits 51,840 points with 51,840 soundness violations, and head to head on the 10,640 inputs where `F` emits a point it is unsound on 10,640 of 10,640 against `F`'s 0. Two materially independent routes agree on all 51,840 inputs for disposition, identified set, failure mode and composed budget.
- [x] Attach uncertainty/calibration to every capability prediction. — ✅ gmi-833-capability-predictor-v1 KP-3A/KP-3B/KP-3C: all 51,840 emissions leave through a single `emit` site proved sole by an `ast` call-graph audit (0 bare returns, 1 construction site) and every one carries a #851 U-1 typed object; 0 feasible sets carry a coverage number, and every confidence emission carries the U-2B dependence-safe budget `1-alpha-37/1000` (913/1000 and 863/1000) while the independence product 9152473869/10000000000 is refused as strictly larger; the emitted budget is confirmed by a second, independently parameterised route on all 51,840 inputs (0 disagreements). Coverage is exact at finite scope: the emitted object contains the true capability in 100,800/100,800 (input, consistent-world) pairs. Empirical calibration error is not measured here.
- [x] Require abstention where capability is not identifiable. — ✅ #916 #913 L:e8c384ad66cb
- [x] Test predictor on held-out synthetic machine species. — ✅ gmi-833-capability-predictor-evaluation-v1 KE-1: two held-out synthetic species, `SIGMA_SYN` (64 modular head machines) and the power-revival population `SIGMA_SYN2` (128 machines with a new head-2 gate), each disjoint from the parent's `SIGMA_1` and from every other registered population by the separating coordinate `rho[3]` with 0 descriptor collisions on all 28 pairwise comparisons, were run through the UNMODIFIED parent `F` on frozen grids of 51840 inputs each whose complete prediction streams were bound by sha256 before any outcome oracle existed (commits e46003d5 and f60377bd); against externally evaluated capability obtained by RUNNING every machine over the whole protected battery, `F` is wrong on **0 of 45800 and 0 of 25216 (input, consistent-world) pairs**, and on `SIGMA_SYN2` **3872 of its 7200 point emissions are non-degenerate** — taking the capability values 4/11, 5/11 and 9/11 over 13472 pairs — which matters because on `SIGMA_SYN` every identified value was degenerate (`UNSATISFIED` or 0), a power defect of the instrument that this tranche found prediction-side and fixed with a finer registered observation rather than reporting as a positive; every non-degenerate emission therefore comes from `SIGMA_SYN2`, whose custody is the weaker of the two strata and is labelled as such — its predictions were committed at f60377bd before its outcomes were computed, but the external evaluator already existed at 50451f23, exactly as `FREEZE_V4_POWER_ADDENDUM.md` section 4 discloses and CI re-derives; the closed-form capability law agrees with brute-force simulation on 64/64 and 128/128 machines, abstention among answerable inputs is `1801/2568` so silence is never scored as success, and route B reproduces both frozen streams' sha256 byte-exactly without importing `F` or this package.
- [x] Test predictor on held-out known architectures. — ✅ gmi-833-capability-predictor-evaluation-v1 KE-2: two held-out populations drawn from four named mechanism families (`FF` window, `REC` recurrent accumulator, `CTR` saturating counter, `STK` bounded stack) — `SIGMA_ARCH` (128 machines) and `SIGMA_ARCH2` (176, adding the parameters FF 3, REC 6 and CTR 3) — are disjoint from every other registered population, and `F` is wrong on **0 of 121920 and 0 of 24912 (input, consistent-world) pairs**, with **2400 of `SIGMA_ARCH2`'s 9488 point emissions non-degenerate** (4/13, 7/13, 11/13) over 5408 pairs — so, as on the synthetic row, every non-degenerate emission comes from the V4 population, frozen at f60377bd before its outcomes were computed but scored by an evaluator that already existed, the weaker custody stratum disclosed in `FREEZE_V4_POWER_ADDENDUM.md` section 4; the closed-form law — derived from the claim that a saturating counter with cap at least the word length tracks the ones-count exactly while a bounded window or a stack height does not — agrees with brute-force simulation on 128/128 and 176/176 machines; and the family NAME is blind structurally, not by convention: no realization record contains any string, an `ast` reference audit over the encoder and all five mask builders finds no path to the label list (negative control: a planted `ARCH_LABELS[0]` encoder is flagged), rebuilding the universe under all 24 permutations of the family names reproduces it exactly, and `k` is strictly coarser than family identity since `REC` and `CTR` share `k=1`.
- [ ] Test predictor on real trained systems.
- [x] Predict qualitative failure before evaluation. — ✅ gmi-833-capability-predictor-evaluation-v1 KE-4: the binding mode of the parent's ten-mode KP-2 taxonomy was emitted for every one of 7×51840 registered inputs and bound by sha256 in the freeze commit before any outcome oracle existed, together with a per-case KP-2D order class fixed at the same moment (`SIGMA_SYN` 8577 order-free / 8311 conjunctive / 3656 no-crossing; `SIGMA_ARCH` 10586 / 12470 / 3776), and the externally attributed mode — recomputed from measured capabilities by the independent evaluator — is reported as a confusion matrix stratified by that class and never pooled, since scoring a conjunctive case as a miss would measure the ambiguity KP-2D already proved; on the truthfully-registered universes agreement is exact but co-extensive with registration truthfulness by an algebraic identity, so the substantive evidence is the 14594 off-diagonal attributions on the real-system universes where registration fails, which is the measured cost of a bridge failure rather than of the taxonomy.
- [x] Predict quantitative resource/capability curves before evaluation. — ✅ gmi-833-capability-predictor-evaluation-v1 KE-5: 672 swept points — 8 registered curve cases × 4 thresholds × 7 held-out universes, each sweeping the resource coordinate `R.budget` across all three registered budgets — had their predicted disposition, point and identified set frozen in `FROZEN_PREDICTIONS_V1/V2/V3.json` before any outcome oracle existed; the replay reproduces every frozen curve point with **0 mismatches**, and of the 92 swept points where `F` emits a point the externally evaluated capability agrees exactly on **76**, reported as per-point exact agreement with no fitted summary and no error norm.
- [x] Measure calibration error. — ✅ gmi-833-capability-predictor-evaluation-v1 KE-6: the parent proved exact finite coverage with all registered relations assumed good and explicitly did not claim empirical calibration; this measures exact coverage under the registered fault law in which the typed-uncertainty source and each of the four registered relations `M`,`D`,`B`,`H` fails at exactly its rate (`alpha`,1/100,1/200,1/500,1/50), enumerating all 32 fault patterns with exact rational weights — against the U-2B bounds `913/1000` and `863/1000` the minimum empirical coverage over 5184 and 7680 emissions is `1191567620413/1224000000000` and `2380730729/2448000000` with **0 violations** and **0 point-emission violations** (minima `1191567620413/1224000000000`, `2380730729/2448000000` over 1312 and 2412 point emissions), every figure reported beside its abstention rate (`121/162`, `439/640`) so that silence cannot masquerade as calibration, FeasibleSet emissions excluded rather than scored 1 because U-1a carries no probability premise, and the hostile that inflates every `beta` twenty-fold does produce violations.
- [x] Measure out-of-distribution failure. — ✅ gmi-833-capability-predictor-evaluation-v1 KE-7: out-of-distribution is defined structurally — a world is out-of-universe iff its realization is not a member of the installed universe, and only the three cuts that are properties of the world can exclude it — giving `SIGMA_OOD`, 272 worlds built by relaxing each generator coordinate of `SIGMA_SYN` one at a time (head, modulus, register); the two strata are reported side by side and never merged: in-universe, soundness was actively attacked over **45800 (input, world) pairs with 0 violations**, while out-of-universe, across 20544 probed inputs and 859008 (input, OOD-world) pairs, 705732 lie inside the emitted identified set and 44172 point emissions are wrong — and per KP-1D that is the parent's declared registration boundary restated, attributable to registration and not a soundness failure of `F`.

# L. Development, morphogenesis, and evolvability

- [x] Formalize developmental potential separately from current capability. — ✅ #909 #908 L:2a33e8326125
- [x] Define evolvability quantitatively. — ✅ #909 #908 `Ev_Q(U)=Q(U)` L:3089c8667c66
- [x] Derive conditions under which history improves future discovery rather than merely storing solutions. — ✅ #909 #908 `p0,pH` L:cb9a01a27d49
- [x] Distinguish solution capital from search-policy improvement. — ✅ #909 #908 L:e40317c0ab97
- [x] Derive representation changes that reduce future search cost. — ✅ #833 `gmi-833-developmental-reuse-v1` REP-1/REP-1b/REP-2/REP-3: exact rank-free bracket `Φ(n',ℓ1) ≤ Φ(n,ℓ0−1)` ⇒ reduction, `Φ(n',ℓ1−1) ≥ Φ(n,ℓ0)` ⇒ increase, decided without running the search; 702-cell census 359/167/176 with 0 disjointness and 0 monotonicity violations, refined five-way to 359/3/172/1/167 by the second route with 0 conflicts; portfolio form `ΔNet = −Saving(T⁺) + Tax(T⁰) + K_total` reproduces #897 HLD-1 exactly (50,052→1,307, K=6, net −48,739; control 538→1,710, +1,178; combined Saving 48,745, Tax 1,172, ΔNet −47,567) and rejects the solution-capital library REP-1 accepts (−36,890 alone vs +18,139 on the distribution); boundary EARNED-BY-COUNTEREXAMPLE at `cccccabcccc` where an actually-used macro shortens ℓ 11→10 yet burden rises 265,152→1,048,831 rank-free (Φ(4,9)+1 = 349,525 > 265,719 = Φ(3,11)).
- [ ] Derive operator invention.
- [ ] Derive library formation.
- [ ] Derive developmental phase transitions.
- [ ] Derive path dependence and hysteresis.
- [ ] Derive conditions for escaping local developmental traps.
- [x] Compare mutation, local search, GP/CGP, evolutionary, gradient, NAS-like, and meta-search dynamics. — ✅ #833 `gmi-833-developmental-reuse-v1` SD-1/SD-2/SD-3: all 8 registered dynamics × 3 ecologies × 200 registered targets in ONE charged frame (same space |X|=3^8=6561, same targets, 1 unit per objective evaluation with repeats charged, same budget 6561, same frozen-LCG seed), charging verified by an independent audit counter and the three objective-blind dynamics (MUT, NAS, RAND) confirmed byte-identical across ecologies; no dynamic is best in every ecology and none is worst in every ecology (OPAQUE best ENUM 200/200 at the exact bound (|X|+1)/2 = 3281, GRADED best GRAD 200/200 in 3,075 total evaluations, DECEPTIVE best ENUM 200/200 while GRAD collapses to 12/200); the ordering is DERIVED — enumeration is exactly optimal in expectation under opacity, coordinate descent hits in exactly 1+ℓ(n−1) under separable grading (separation floor 28×/193×/1,405× at ℓ=6/8/10, verified exhaustively over every start point at ℓ∈{6,8}), and under deception LS/GRAD can reach the target only by a restart accident of window exactly 17/6561 and 3/6561 (26/26 and 12/12 measured hits explained; route B's exhaustive sweep finds precisely the predicted 3-element hitting set); OPAQUE query sequences are provably target-independent for all 9 census rows, non-vacuously compared; NAS's sign was predicted by REP-2 for all 4 pool libraries before running (+37,133 ×3, +188,758) and it hits 12/200 in every ecology; META's coverage-dilution identity gives its ENUM arm exactly |X|/3 = 2,187 (106/200 vs ENUM 200/200).
- [ ] Prove/measure reachability mass for predicted morphologies.
- [x] Test whether P4 recursive grammar growth discovers mechanisms absent from `G0`. — ✅ #833 `gmi-833-developmental-reuse-v1` NOV-1/NOV-2: under the expressibility reading the answer is a PROVEN IMPOSSIBILITY — for every acyclic grown library and every t, `{Expand(p) : p over A_t} = Σ⁺` exactly, so growth adds zero expressive power (checked on 3 libraries against all 1,092 words of length ≤ 6, with 3 cyclic hostiles returning `RECURSIVE_LIBRARY_CYCLE` unchanged); under the only surviving reading — not reachable within the registered budget — the answer is YES and simultaneously NO: with `L = {m1→ab, m2→m1m1}`, `ADDED`/`REMOVED` are 3/4 at B=10, 23/45 at B=100, 1/698 at B=1,000, 0/343 at B=5,000, 0/0 at B=20,000, so growth is an exactly-characterised budget-relative TRADE decided by REP-1 with B interposed, never a monotone gain.
- [ ] Predict evolvability on genuinely future task families.
- [ ] Validate developmental predictions on continual-learning systems.

# M. Cognitive-function derivation upgrade

- [x] Re-audit memory differentiation under the upgraded foundation. — ✅ #919 #917 L:ec7e7b80c919
- [x] Re-audit attention as resource-rational selective processing. — ✅ #919 #917 L:251b17032a41
- [x] Re-audit concept formation/abstraction. — ✅ #919 #917 L:59219d35bc3c
- [ ] Re-audit hierarchical skills/chunking.
- [ ] Re-audit planning and stopping.
- [ ] Re-audit causal cognition/intervention/counterfactuals.
- [x] Re-audit metacognition and value of computation. — ✅ gmi-833-cognitive-reaudit-social-v1 VOC-1/VOC-2/NONID-1: a further deliberation step is worth its exact charge iff its exact expected improvement strictly exceeds the step price, and a fixed-schedule twin carrying no internal estimate reproduces the allocation trace iff allocation is a deterministic function of the registered observable instance label, so trace evidence alone cannot identify metacognitive machinery; 8,748 deliberation scopes, 26,244 two-route VOC cases (2,484 exact ties where a non-strict rule is detected) and an exhaustive 125-schedule aliasing search returning 1 twin for the deterministic allocator and 0 for the latent-draw counterexample all pass with 0 two-route mismatches.
- [x] Re-audit social cognition/theory of mind. — ✅ gmi-833-cognitive-reaudit-social-v1 SOC-1: a policy conditioned on the other agent's hidden state strictly outscores every policy measurable in that agent's observed action history iff the observed-action channel is not sufficient for the payoff-relevant partition on the positive-probability support, so theory of mind is an exact property of the ecology-plus-channel pair and not of the machine; across 19,263 exact ecologies 3,996 separate (largest exact gap 1, false-belief witness gap exactly 1) while 15,267 are matched exactly by a pure behaviour-reader, with 0 two-route mismatches.
- [x] Re-audit communication. — ✅ gmi-833-cognitive-reaudit-social-v1 COM-1/COM-2/COM-3/COM-4: a charged channel strictly pays iff its exact refinement value exceeds its exact price, with the receiver's differential action proved equivalent to strictly positive refinement value rather than assumed as a second premise; across 93,075 exact instances 6,904 strictly pay, 13,915 are free but useless, 16,596 valuable but unaffordable, 15,895 sit exactly at the threshold, and 20,950 are aliased by shared observation at zero channel charge, with 0 two-route mismatches.
- [x] Re-audit imitation and teaching. — ✅ gmi-833-cognitive-reaudit-social-v1 TCH-1/TCH-2/TCH-3/NONID-4: imitation and teaching are logically independent (all four cells realizable over 1,080 exact instances -- 75 imitation-only, 375 teaching, 525 failed teaching, 105 neither) and teaching is jointly worth its cost iff n*(L_ctrl-L_demo) > D; erasing the demonstrator charge from the lifecycle vector inflates the worthwhile set from 352 to 450, so 98 verdicts are free-labour artifacts, and a pre/post detector fires 200/200 on causally inert demonstrations where the control-arm detector fires 0/200 at 200/200 recall.
- [x] Re-audit cultural accumulation. — ✅ gmi-833-cognitive-reaudit-social-v1 CUL-1/CUL-2/CUL-3/NONID-5: a population ratchets iff (1-phi)*a_n < g with exact ceiling a* = g/(1-phi) never crossed, yet the capability trajectory never identifies transmission because an independently re-deriving zero-transmission population reproduces all 270 registered trajectories exactly; the charged lifecycle vector separates them by exactly (r-t)*phi*a_n and fails identically when t = r = k, with 1,530 of 7,290 cost regimes indistinguishable, 5,760 strictly separated, and 0 mismatches over 2,160 ratchet-step and 58,320 cost-separation cases.
- [


