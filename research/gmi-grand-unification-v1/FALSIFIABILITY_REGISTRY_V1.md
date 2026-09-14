# Universal falsifiability registry — every GGU principle's triple (checklist item 38)

Status: **REGISTRY + MACHINE-CHECKED COVERAGE. Admissibility scope throughout.**
Date: 2026-09-14. This file closes the item-38 gap: "no registry giving *every*
principle its falsifier + competing parent + load-bearing assumption triple."

Coverage: all 50 `*THEOREM_V1.md` files in `research/gmi-grand-unification-v1/`
plus the 6 GGU-adjacent units this lane owns or touches (CAU-1–4, CAU-5, TOM-1–3,
ARC-1–4, ARC-5, JRC-1–4). 56/56 rows present. Each row names: the principle's
load-bearing assumption (the premise whose failure breaks the result, not a
background condition), the competing parent with first refusal (what already
explains it, or would own it if the proof failed), and a concrete falsifier
(an observation/computation that would refute the claim as stated).

How to read "status": THEOREM rows carry exact finite witnesses; BOUNDARY rows
state proven obstructions; the registry does not upgrade any row's own status.

## A. Semantic information and cuts (GG1–GG9, GG29–GG32)

| principle | load-bearing assumption | competing parent (first refusal) | falsifier |
|---|---|---|---|
| SC-1 exact cut = conflict-chromatic number (`SEMANTIC_CUT_THEOREM_V1`) | finite registered one-way interface `c(X)`, `d(Z,Y)`; complete-message counting | Shannon zero-error / graph coloring (Körner–Orlitsky function computation) | an adequate protocol using fewer symbols than `χ(H)` on a registered interface |
| GG2 pairwise insufficiency | the triple-conflict hypergraph instance is correctly enumerated | hypergraph coloring theory | a pairwise-coloring achieving 2 messages on the stated triple |
| GG26 distributed one-way cut (`COMPOSITIONAL_DISTRIBUTED_GMI`) | one-way factorization at the registered boundary; feedback re-registered | Roughgarden INDEX separation (communication complexity) | a one-way protocol beating `χ(H)` with the complete message counted |
| GG29 causal semantic nullity (`CAUSAL_SEMANTIC_VIABILITY`) | admitted-intervention set and continuation family are completely declared | Pearl SCM intervention semantics; LMT complete-view lemma | a `z` with no admitted-intervention effect anywhere, yet some GMI capability statement requiring it |
| GG30 semantic data processing | garbling is a stochastic map applied to the side channel only | Shannon data processing inequality | one of the 36 enumerated channel/garbling pairs violating monotonicity (receipt-bound) |
| GG31 viability lift | constitution predicate `V` is declared in the boundary | viability/autopoiesis literature (Maturana–Varela); homeostatic regulation | a system satisfying `V` whose trajectory law provably needs machinery outside the master tuple |
| GG32 obligation non-identifiability | opposite constitutions on identical dynamics are admitted boundaries | Hume's is-ought gap; obligation-deletion countermodel | deriving the optimal action from the transition law alone with no constitution premise |

## B. Composition and coordination (GG25–GG28, JRC)

| principle | load-bearing assumption | competing parent (first refusal) | falsifier |
|---|---|---|---|
| GG25 team centralization (`COMPOSITIONAL_DISTRIBUTED_GMI`) | finite synchronous team; product-state compilation is admitted | distributed-systems product construction (standard) | a finite synchronous team with no trace-equivalent centralized realization |
| GG27 product tensorization | genuine independence: product ecology/state/obligation AND product-only machines | probability product measures; game-theory independent subgames | independent problems whose attainable set is not the Cartesian product |
| GG28 exact-function specialization | exact-function obligations (singletons) | Körner–Orlitsky / exact-function compression | distinct output pairs decoded from one message symbol |
| GAC-5 founded composition (corrected) | well-founded dependency bases / initialized invariants | well-founded induction (standard) | a composed claim whose discharged interfaces trace to an uninitialized invariant |
| JRC-1 coverage optimum (`gmi-joint-relational-composition-v1`) | supplied finite relation; no side information; deterministic codecs admitted | set-cover optimality (standard) | an adequate codec with fewer symbols than `τ(H)` |
| JRC-3/JRC-4 shared-message savings | joint encoder sees both inputs; full Cartesian domain | — (positive construction, parents intact) | local relations whose joint optimum the coverage proof miscounts (re-run the checker) |

## C. Causality and acquisition (CAU, GG12 acquisition family)

| principle | load-bearing assumption | competing parent (first refusal) | falsifier |
|---|---|---|---|
| CAU-1 indistinguishability obstruction | declared compatible model class; complete-view learner typing | Pearl identification vs estimation split; LMT complete-view lemma | a fixed learner separating W1's worlds from the identical stream |
| CAU-2 fiber constancy = identification | nonempty fiber `C(P)`; declared class | Pearl §2–3 identification theory; faithfulness qualification | a target constant on no fiber yet identified, or identified off-fiber |
| CAU-3 supported adjustment / randomization | back-door criterion + positive support; surgical replacement validity | Pearl back-door criterion; RCT randomization theory | a supported adjustment disagreeing with surgical evaluation (re-run W2) |
| CAU-5a no-universal-sign separator (this lane) | finite binary SCM interface (CAU-1–4) | — (separator pair is new; SCM semantics Pearl's) | miscount in W4a/W4b tables (re-run `test_causal_rungs_v1.py`) |
| CAU-5b discovery boundary (this lane) | learner sees observational law only | Gold/Pitt–Warmuth passive-intractability; Angluin query-learning | an obs-law-only map separating W1's worlds |
| CAU-5c rung-3 strictness (this lane) | uniform root law; response-table scope | Balke–Pearl bounds shape (cited, not re-derived) | miscount in W5A/W5B rung laws or PN values (re-run) |
| Task-directed / controlled acquisition (GG12 family) | obligation-relevant uncertainty is measurable; probe costs declared | Blackwell value of information; optimal stopping | a probe whose measured obligation-relevant reduction contradicts the booked value net of cost |

## D. Strategy and social cognition (GG-S1–GG-S8, TOM-1–3)

| principle | load-bearing assumption | competing parent (first refusal) | falsifier |
|---|---|---|---|
| GG-S2 Nash = simultaneous local satisfaction | declared scalar loss game + strategy class | Nash (1950) existence; game-theory textbooks | a profile satisfying all local obligations that is not Nash, or vice versa |
| GG-S3 strategic refinement | opponent strategies are admitted probes | GG41 semantic refinement (same theorem, larger probe family) | a refinement check failing in the 196,608 census (receipt-bound) |
| GG-S4 one-way strategic cuts | classical deterministic one-way interface | SC-1 (same bound, inter-agent interface) | a one-way inter-agent protocol beating the cut bound |
| GG-S5 finite strategic frontier computable | finite registers + effective evaluation + decidable comparisons | finite-game enumeration (standard); halting-boundary for reals | a finite rational register whose frontier the enumeration miscounts |
| GG-S6 no universal ecology-robust equilibrium | opposite dominant-action ecologies admitted | prior-free no-universal-optimum boundary (same programme) | a joint action that is an exact equilibrium in both stated ecologies |
| TOM-1 opponent-model forcing (this lane) | copycat/contrarian response functions; deterministic policies | level-k / cognitive hierarchy (Stahl; Camerer–Ho–Chong) | a fixed policy scoring 2 against both opponents (re-run) |
| TOM-2 belief closure depth (this lane) | `{0..5}` beauty game; ties-down best reply | Nagel beauty contest; iterative reasoning literature | a ladder miscount (`beauty_ladder() != [5,3,2,1,1,1]`) or `BR(1) != 1` |
| TOM-3 reliability probe value (this lane) | declared team optimum `(C,C)`; stag-hunt loss matrix | Skyrms stag hunt; Blackwell probe pricing | a probe-value miscount (re-run) or a regret-only selector separating the two Nash profiles |

## E. Development, reachability, morphology

| principle | load-bearing assumption | competing parent (first refusal) | falsifier |
|---|---|---|---|
| DU-1 admissibility ≠ reachability (`DEVELOPMENTAL_UNDERDETERMINATION`) | two development laws sharing all static facts | developmental-systems underdetermination literature | the two stated laws reaching identical frontiers under the same seed |
| Developmental taxonomy five types (`DEVELOPMENTAL_TAXONOMY_THEOREM_V1`, this lane, sibling `gmi-developmental-taxonomy-v1`) | g-preserving transitions classified by which of `s/r/K/L/M` moves; `g` orthogonal; `n=3` product fixture | `DEVELOPMENT_TIMESCALE_SEPARATION` + `DEVELOPMENTAL_STATE_FACTORIZATION` parents own the split/fixture | a g-preserving log entry firing zero or two of the five predicates under the stated attribute rules (re-run `test_taxonomy_v1.py`) |
| Reachability selection (`DEVELOPMENTAL_REACHABILITY_SELECTION`) | declared development law + seed distribution | evolutionary reachability / evo-devo constraints | a morphology in `Reach` never reached, or outside `Reach` reached, under the declared law |
| Morphology phase law (`MORPHOLOGY_PHASE_LAW_DERIVATION` + soundness) | declared ecology contract + basis identity | phase-transition physics (analogy only — mechanism, not parent) | a frozen ecology/basis cell whose outcome contradicts the derived boundary (re-run the cell) |
| Niche-frequency law (`gmi-niche-frequency-repair-v1`, joint-event form) | exact grid + joint-event statement | — (repair is new; marginal-vs-conditional error owned) | a grid cell miscount or a joint event outside the stated law |
| Family-phase / neural–nonneural selection | registered family definitions + envelope protocol | universal approximation (resource-blind — P9A); depth separation (Telgarsky) | a family outside its phase boundary winning inside it under the frozen protocol |

## F. Statistics, validity, computation

| principle | load-bearing assumption | competing parent (first refusal) | falsifier |
|---|---|---|---|
| FMT finite-data transfer | fixed-N sufficient-state contract; common-policy premise | Weissman finite-alphabet concentration; simulation-lemma coupling | a row outside the simultaneous TV event with the transfer applied anyway |
| ARC-1–4 adaptive rows | fixed finite register; predictable selection; conditional fixed row laws | Howard et al. 2021 (time-uniform); FC-T7 error spending | a registered row violating its `αw/[n(n+1)]` certificate (re-run) |
| ARC-5a bounded creation (this lane) | predeclared potential register + finite budget; `Σw ≤ 1` | ARC-1 (same union argument, larger finite set) | a potential row violating its own certificate (re-run) |
| ARC-5b(ii) unbounded-creation obstruction (this lane) | each created row needs positive budget for a non-vacuous certificate | countable additivity of probability (the union bound itself) | a fixed-`α` scheme covering unbounded unbudgeted creations non-vacuously |
| Finite quantum cover | declared finite cover + error contract | quantum information parents (as cited in-unit) | a cover element outside its error contract |
| Delegation / terminal-cost / native-adjoint repairs | per-unit declared contracts (see in-unit OPERATIONS) | — (scoped repairs, parents in-unit) | a receipt hash mismatch on re-run (custody failure, not a theory failure) |

## G. Reflection, recursion, resources, physics

| principle | load-bearing assumption | competing parent (first refusal) | falsifier |
|---|---|---|---|
| GR1–GR2 reflective quotient (`REFLECTIVE_SELF_REFERENCE`) | self-probe family declared; diagonal impossibility premise | Gödel/Tarski diagonal literature (analogy, typed); introspection literature | an exact self-prediction succeeding under an admitted inverting intervention |
| Recursive morphogenesis lift | state-level-indexed construction; lifted obligation = future capability profile | meta-learning / AutoML / evolution literature (each level's mechanics) | a claimed lift level with no registered state-level distinction |
| Bounded-controller resource charging | `desc/exec/upd/ver/rev` cost registration; no free cognition | bounded rationality (Simon); resource-rational cognition (Lieder–Griffiths) | a cognitive operation with zero booked cost somewhere in the burden vector |
| Physical-resource bridge / realization / lifting | declared physical process + resource contract | physics of computation (Landauer et al., as cited) | a compiled realization violating its resource contract on re-execution |

## Registry maintenance rule

Every new theorem file added to `research/gmi-grand-unification-v1/` (or any
GGU-adjacent unit) must add its triple row here before its PR merges: one
load-bearing assumption, one competing parent with first refusal, one concrete
falsifier. A row whose falsifier is "re-run the checker" must name the file.
The `check_registry_v1.py` checker enforces: (i) every `*THEOREM_V1.md` in the
GGU dir has a row; (ii) every row names all three columns non-trivially;
(iii) every cited witness file exists.

## H. Per-theorem triple index (machine-checked)

Each row names the exact theorem file so `check_registry_v1.py` verifies coverage. Shorthand IDs in sections A-G resolve to these rows.

| file | shorthand | load-bearing assumption | competing parent | falsifier |
|---|---|---|---|---|
| `ACTIVE_CLOSED_LOOP_INTELLIGENCE_THEOREM_V1.md` | ACL | ACL-2b conditional whole-policy scope | POMDP belief-state control; active-experiment design | a passive predictor matching the closed-loop policy with no sensor-controller state |
| `APPROXIMATE_SEMANTIC_GEOMETRY_THEOREM_V1.md` | approx geometry | declared response metric/covers + tolerance | rate-distortion theory | an epsilon-quotient merging obligation-distinct states while claimed exact |
| `BOUNDED_CONTROLLER_RESOURCE_THEOREM_V1.md` | BCR | finite deterministic synthesis; legal finite termination | Meuleau et al. UAI99 policy graphs; Hu-De Giacomo bounded synthesis | a finite controller synthesis the search misses inside the declared bound |
| `CERTIFIED_REUSE_INVALIDATION_THEOREM_V1.md` | CRI | certificate validity window; no reuse after expiry | PVR-3 stable-validity reuse | certified reuse succeeding after invalidation with no renewal |
| `CAUSAL_SEMANTIC_VIABILITY_THEOREM_V1.md` | GG29-GG32 | admitted interventions + declared constitution; common-decoder semantics | Pearl SCM interventions; viability/autopoiesis literature | an obligation-null physical detail some capability statement requires, or opposite constitutions agreeing on one dynamics |
| `DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM_V1.md` | reachability selection | declared development law + seed distribution | evolutionary reachability / evo-devo constraints | a morphology in Reach never reached, or outside Reach reached, under the declared law |
| `DEVELOPMENTAL_UNDERDETERMINATION_THEOREM_V1.md` | DU-1 | two development laws sharing all static facts | developmental-systems underdetermination literature | the two stated laws reaching identical frontiers under the same seed |
| `COMPOSITIONAL_DISTRIBUTED_GMI_THEOREM_V1.md` | GG25-GG28 | finite synchronous team; one-way factorization at the cut; product-only machines for GG27 | distributed-systems product construction; Roughgarden INDEX; Shannon zero-error | a finite team with no trace-equivalent centralization, or independent problems whose attainable set is not the product |
| `SEMANTIC_CUT_THEOREM_V1.md` | SC-1 | finite registered one-way interface; complete-message counting | Shannon zero-error / Koerner-Orlitsky function computation | an adequate protocol using fewer symbols than chi(H) on a registered interface |
| `COMPOSITIONAL_LANGUAGE_MORPHOLOGY_THEOREM_V1.md` | compositional-vs-holistic phase law | product meaning space + recombination witnesses | compositional distributional semantics; iterated learning | a holistic code beating the compositional bound inside the product regime |
| `CONTINUAL_SEMANTIC_RETENTION_THEOREM_V1.md` | retention needs N_t joint states | zero-error exact retention; no side information | EWC / continual-learning literature (mechanisms, not the bound) | exact retention with fewer than N_t joint states and no side channel |
| `CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md` | lift boundary | epsilon/enclosure certificates; no Boolean-to-continuous leap | computable analysis; order-theoretic optimization | a finite example claimed to establish the continuous transfer without the certificate |
| `CONTINUOUS_REALIZATION_BRIDGE_THEOREM_V1.md` | approx bridge | universal approximation is not necessity/efficiency/trainability | universal approximation theorems (Cybenko/Hornik) | a continuous map with no neural realization inside the declared error |
| `CONTROLLED_ACQUISITION_INFORMATION_STATE_THEOREM_V1.md` | CAIS | candidate set + physical/control state tracked jointly | POMDP / active-experiment parents (acknowledged) | a state-changing experiment correctly handled by candidate-set-only recurrence |
| `CONTROLLED_RELATIONAL_ACQUISITION_THEOREM_V1.md` | CRA | finite deterministic constructive synthesis scope | TDA-1 fixed-world testing (narrower, intact) | a finite controlled synthesis instance the construction fails inside its scope |
| `EMPIRICAL_FRONTIER_IDENTIFICATION_THEOREM_V1.md` | EFI | vector Pareto verdicts need set-valued resource evidence | Hladik possible/necessary efficiency | a family verdict drawn from scalar point estimates surviving all compatible vectors |
| `EMPIRICAL_RESOURCE_IDENTIFICATION_THEOREM_V1.md` | resource sets | verdict must survive every compatible resource vector | measurement-uncertainty / robust selection | a verdict that collapses under some resource vector inside the certified set |
| `EPISTEMIC_ACQUISITION_THEOREM_V1.md` | EA | eta_Omega is the protected response quotient, not action cost | TDA-1-3 relational acquisition law | an experiment count below the booked bound identifying the quotient |
| `FAMILY_FRONTIER_PHASE_THEOREM_V1.md` | FP | repaired FP-3/5/6 hypotheses (soundness correction) | phase-transition physics (analogy only) | a frozen cell contradicting the repaired boundary (re-run the cell) |
| `FINITE_DATA_MODEL_TRANSFER_THEOREM_V1.md` | FMT | fixed-N sufficient-state contract | Weissman finite-alphabet concentration | transfer applied outside the sufficient-state contract |
| `FIXED_UNKNOWN_MODEL_ACQUISITION_THEOREM_V1.md` | UMA | finite known-hypothesis scope; rectangularity per Iyengar | Duff 2001 Bayes-adaptive POMDP; Iyengar robust DP | a non-rectangular kernel where the robust recursion is applied anyway |
| `FORMAL_REASONING_PROOF_SEARCH_THEOREM_V1.md` | proof-search reduction | proof system is declared; no manufactured soundness | proof-complexity / automated reasoning literature | an accepted certificate from an unsound checker counted as a proof |
| `GENERALIZATION_ECOLOGY_INFERENCE_THEOREM_V1.md` | generalization bridge | deployment distribution D declared separately from samples | PAC / statistical learning theory | a deployment failure outside every bound the certificate allows |
| `GENERALIZATION_IDENTIFIABILITY_RADIUS_THEOREM_V1.md` | GIR | infimum identity + attainment gate | identifiability theory (as cited in-unit) | a radius prediction succeeding where the gate says UNDECIDED |
| `INFORMATION_COMPUTATION_SEPARATION_THEOREM_V1.md` | cut/query separation | single final-cut width vs query complexity 1..n | query complexity (decision-tree) literature | a 1-bit final-cut family with query complexity outside 1..n |
| `INTRAFAMILY_ARCHITECTURE_REFINEMENT_THEOREM_V1.md` | intra-family refinement | named-family boundary; property forced across the frontier | architecture-property literature (conv/recurrent/attention ablations) | a property claimed derived that some frontier optimum lacks |
| `LABELLED_PARTITION_QUERY_RECONSTRUCTION_THEOREM_V1.md` | LQR | coordinate-query scope (not general-test hardness) | Hyafil-Rivest decision trees; Ambainis-de Wolf queries | a query optimum the labelled-partition construction misses in-scope |
| `MEASURABLE_CONTINUOUS_GMI_THEOREM_V1.md` | measurable sector | measurability declared; existence needs regularity | measure-theoretic probability; computable analysis | an optimal realization claimed existent with no regularity premise |
| `MORPHOLOGY_SELECTION_THEOREM_V1.md` | derivation criterion | derived means forced across the relevant optimum/frontier set | realization compilation (coexistence, not derivation) | a morphology called derived while some frontier optimum lacks the property |
| `NEURAL_NONNEURAL_FAMILY_SELECTION_THEOREM_V1.md` | family frontier law | family-conditioned frontiers compared in a declared substrate model | universal approximation (resource-blind); Telgarsky depth separation | a family verdict flipping under no change to the declared substrate model |
| `NN_NONNN_DERIVATION_CERTIFICATE_AND_BOUNDARY_THEOREM_V1.md` | derivation certificate | certificate scope; irreducible empirical boundary stated | piece-parents keep refusal per piece (synthesis object) | a derivation claim beyond the certificate without the missing physical facts |
| `NONNEURAL_CONSTRUCTIVE_DERIVATION_THEOREM_V1.md` | non-neural compiler | finite semantic transducer to table/circuit/SLP | circuit-synthesis / automata theory | a finite quotient with no realizing circuit inside the stated size |
| `PHYSICAL_RESOURCE_BRIDGE_THEOREM_V1.md` | substrate bridge | substrate laws supplied; no manufactured physics | Landauer / physics of computation (as cited) | a resource verdict contradicting the supplied substrate law |
| `PLANNING_SEMANTIC_RESOLUTION_THEOREM_V1.md` | resolution ladder | possibility/next-action/prefix/trajectory levels distinguished | classical/AI planning complexity literature | a plan claimed adequate at a resolution the ladder says is insufficient |
| `PROBABILISTIC_CONTROLLED_ACQUISITION_THEOREM_V1.md` | PCA | known stochastic kernel; fairness is not deadline/cost | Cimatti et al. strong vs cyclic planning; Bertsekas-Tsitsiklis SSP | an expected-cost claim drawn from fairness alone |
| `PROOF_SEARCH_VERIFICATION_REUSE_THEOREM_V1.md` | PVR | stable validity assumed; scoped finite checks | proof-search / verification-reuse literature | reuse after certificate expiry, or a PVR-3 miscount (re-run) |
| `QUANTUM_PROCESS_INSTANTIATION_THEOREM_V1.md` | quantum instantiation | finite-dimensional quantum process theory as P | quantum information theory (as cited in-unit) | a quantum-instantiated claim violating the declared POVM/intervention contract |
| `REALIZATION_COMPILATION_THEOREM_V1.md` | compilation law | operational morphology to realization-type boundary | ReLU compilation / circuit compilation | an operational morphology with no realization of some admitted type in-scope |
| `RECURSIVE_MORPHOGENESIS_THEOREM_V1.md` | recursive lift | state-level-indexed lift; lifted obligation is future capability | meta-learning / AutoML / evolution (per-level mechanics) | a lift level with no registered state-level distinction |
| `REFLECTIVE_SELF_REFERENCE_THEOREM_V1.md` | GR | self-probe family declared; diagonal boundary | Goedel/Tarski diagonal (analogy, typed) | exact self-prediction succeeding under an admitted inverting intervention |
| `RELATIONAL_QUERY_RECONSTRUCTION_THEOREM_V1.md` | RQR | adequate-output (not full-response) scope; TDA composed | Javdani et al. 2014 overlapping regions | a candidate set inside no R_a with an adequate output claimed |
| `ROBUST_DECISION_PRECISION_THEOREM_V1.md` | score precision | explicit score domain; sharp finite witnesses | decision theory under uncertainty | an adequate decision with coarser scores than the bound allows |
| `SEMANTIC_STATE_REFINEMENT_THEOREM_V1.md` | refinement monotonicity | enlarging care gives refinement; canonical surjection | quotient/bisimulation theory | a probe-enlargement that coarsens the semantic quotient |
| `SHARED_DEPENDENCY_MEMORY_REUSE_THEOREM_V1.md` | SMR | registered configuration/renewal synthesis; charged recomputation | Hong-Kung pebbling; Checkmate rematerialization | a reuse schedule exceeding the booked memory with all charges paid |
| `STRATEGIC_MULTIAGENT_THEOREM_V1.md` | GG-S | declared game + strategy class; GG-S rows in CLAIM_LEDGER_STRATEGIC_V1 | Nash 1950; finite-game theory | a GG-S row miscount (re-run grand_gmi_strategic_checks_v1.py) |
| `STRUCTURAL_NEURAL_BOUND_THEOREM_V1.md` | STR | declared opcode-layout contract; one code grammar | threshold-circuit complexity | a faithful flat-linear construction below 39 opcodes/call in-contract |
| `SUBSTRATE_LIFTING_THEOREM_V1.md` | lifting | semantic core survives realization change when behavior survives | multiple realizability; compilation proofs | a realization change preserving all protected behavior that breaks a semantic claim |
| `SYMMETRY_TO_MORPHOLOGY_THEOREM_V1.md` | equivariance | G-invariance of obligation + coordinates; averaging hypotheses | equivariant learning theory | a G-invariant problem whose frontier optimum breaks the derived equivariance |
| `TASK_DIRECTED_ACQUISITION_THEOREM_V1.md` | TDA | worlds/tests/outcomes registered; tests leave world fixed | optimal test design; active learning | a successful action costing less than the booked experiment/retention tradeoff |
| `UNCOMPUTABILITY_BOUNDARY_THEOREM_V1.md` | no-go | unrestricted Turing-complete instances; unbounded horizon | halting problem (reduction) | a total computable exact-capability procedure for the unrestricted class |
