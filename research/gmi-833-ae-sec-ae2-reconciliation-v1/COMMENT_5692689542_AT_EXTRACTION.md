## AE — Structured-World / Information-Theoretic Foundations: recursive gap programme

This addendum is mandatory. It asks whether GMI can derive, delimit, and experimentally discriminate the `structured world -> compression/prediction/control -> architecture` story rather than merely paraphrase it. Parent mathematics must remain parent-owned.

### Expert lanes
1. **Information theory / statistical learning** — entropy, mutual information, sufficient statistics, information bottleneck, rate-distortion, predictive information.
2. **Algorithmic information / MDL** — Kolmogorov complexity, computability limits, MDL/universal coding, structure functions.
3. **Dynamical systems / computational mechanics** — predictive equivalence, causal states, entropy rate, excess entropy, statistical complexity.
4. **Control / decision theory** — rate-distortion control, bounded rationality, value of information, POMDP/belief-state sufficiency.
5. **Statistical physics / thermodynamics** — physical information-processing costs, Landauer-type bounds, nonequilibrium maintenance; strict Shannon-vs-thermodynamic entropy separation.
6. **Representation learning / geometry** — manifold hypothesis, latent-variable models, intrinsic dimension, symmetry/equivariance, compositional structure.
7. **Hostile theory review** — iid noise, biased-but-unstructured sources, chaotic systems, pseudorandom/computationally hard structure, nonstationarity, causal aliasing, lossy compression that destroys control-relevant information.

### AE1 — Define `exploitable structure` without handwaving
- [x] Define task-relative exploitable structure formally; do not equate it with low entropy, nonuniform marginals, low manifold dimension, or compressibility alone. — ✅ `gmi-833-ae-ae1-structure-separation-v1` D-AE1/AE1-1..AE1-6: exploitable structure is defined as the achievability gap `U(W,T,R) = max_{h in H_R} score(h) − blind score` over a budget-indexed rule class naming coordinates and branching depth, never an architecture; exact witnesses separate it from each named surrogate — nonuniform marginal `(3/4,1/4)` with L1 dependence exactly `0`, L1 dependence `1/5` with Bayes gain exactly `0`, and full-information accuracy `1` with exactly `1/2` attainable at budget `(k,d)=(2,2)`.
- [x] Separate marginal nonuniformity from dependence. — ✅ `gmi-833-ae-ae1-structure-separation-v1` AE1-1: `W_IND_SKEW` has `X`-marginal `(3/4,1/4)` and is exactly a product measure (L1 dependence `0`), while `W_DEP_UNIFMARG` has uniform marginals on both coordinates and is maximally dependent; over the exhaustive denominator-8 grid the minimal shapes are `(2,1)` and `(2,2)` respectively.
- [x] Separate statistical dependence from predictive dependence. — ✅ `gmi-833-ae-ae1-structure-separation-v1` AE1-2: `W_DEP_NOPRED` = `[[9/20,1/20],[7/20,3/20]]` has L1 dependence `1/5 > 0` yet `acc_obs = acc_base = 4/5`, a Bayes gain of exactly `0`; the converse holds strictly — across all 16 shapes of the exhaustive denominator-8 grid, `0` admit a predictive world that is independent.
- [x] Separate predictive dependence from causal/control relevance. — ✅ `gmi-833-ae-ae1-structure-separation-v1` AE1-3/AE1-4: `W_PRED_NOCTRL` has Bayes gain `1/2` but control gain exactly `0` under a utility that is *not* constant in `Y`, while `W_CTRL_NOPRED` has Bayes gain exactly `0` and control gain `1/4`; and in the confounded model `Z→X`, `Z→Y` the observational gain is `3/20` while `P(y|do(x))` is `1/2` for both `x`, an interventional gain of exactly `0`.
- [x] Separate existence of structure from accessibility to a resource-bounded learner. — ✅ `gmi-833-ae-ae1-structure-separation-v1` AE1-5: `W_PARITY3` has base rate `1/2` and full-information accuracy exactly `1`, yet every rule admissible at `(k,d)=(2,2)` attains exactly `1/2` and so does every rule at `(3,2)` — reading all three coordinates does not help at depth two; only the single top budget `(3,3)` reaches `1`.
- [x] Separate finite-sample discoverability from asymptotic learnability. — ✅ `gmi-833-ae-ae1-structure-separation-v1` AE1-6: on the 8-secret `GF(2)^3` parity family the Bayes-optimal learner attains expected test accuracy `9/16`, `79/128`, `723/1024`, `6715/8192` at `m = 0,1,2,3` against an asymptotic optimum of `1`; at `m=0` this equals the secret-marginalised base rate `9/16` exactly, and even at `m=3` it is `6715/8192 < 1` because three uniform draws span `GF(2)^3` with probability only `21/64`.
- [x] Define an architecture-independent `structure available to agent A under resource budget R` object or prove why no single scalar can do this. — ✅ `gmi-833-ae-ae1-structure-separation-v1` AE1-5: both disjuncts. No *budget-independent* scalar works — `W_PARITY3` scores `1/2` vs `W_NOISY_DICT`'s `3/4` at budget `k1_d1` and `1` vs `3/4` at `k3_d3`, and the three named candidates are refuted individually (full-information gain `1/2` vs `1/4`, L1 dependence `1` vs `1/2`, chi-squared `1` vs `1/4`). The positive object is the architecture-independent profile `S(W): R ↦ max_{h∈H_R} acc(h,W)`, monotone with `0` violations over the 16-cell lattice and bounded by the full-information optimum with `0` violations.
- [x] Construct minimal counterexamples for every false equivalence above. — ✅ `gmi-833-ae-ae1-structure-separation-v1` AE1-8: every separation in rows 2-6 carries an exhaustive minimality certificate. Distributional (rows 2-3): all 16 shapes up to `4×4` on the denominator-8 grid — minimal shape `(2,1)` for nonuniform-without-dependence, `(2,2)` for dependence-without-prediction, and `0` shapes admitting prediction without dependence. Control (row 4): all shapes `(|X|,|Y|,|A|)` up to `(3,3,2)` over denominator-6 joints and every 0/1 utility, 45,748 cases — minimal `(2,2,2)` for prediction-without-control and `(2,3,2)` for control-without-prediction, both matching the shipped witnesses, once single-action worlds are excluded as vacuous. Causal (row 4): minimal `(|Z|,|X|,|Y|) = (2,2,2)`, matching the shipped confounded triple. Accessibility (row 5) and finite-sample (row 6) are reported **against** the shipped witnesses: two coordinates already suffice for the plain accessibility gap and one coordinate for the zero-sample gap, so `W_PARITY3` and the 3-coordinate family are declared non-minimal in the receipt — `W_PARITY3` is minimal for the strictly stronger pattern in which every coordinate is reachable within the depth budget and the rule is still at the base rate, which is what the AE1-5 claim rests on. Route B independently verifies existence at every claimed minimum and absence at every strictly smaller shape.

### AE2 — Information-theoretic learnability boundary
- [x] Prove a no-predictive-information boundary: if the registered future target is independent of all allowed history/observations, no learner can improve prediction beyond the Bayes/base-rate optimum. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-1: proved for every loss and every rule — by independence, `E[L(h(X),Y)] = Σ_x P_X(x) Σ_a h(a|x) Σ_y P_Y(y)L(a,y) ≥ min_a E[L(a,Y)]`, attained by the constant rule, with randomized rules covered by convexity; verified exactly on i.i.d. Bernoulli(3/10) sources whose observation is the whole history at lengths 1 and 2 (4 and 16 deterministic rules enumerated in full), where the improvement is exactly `0` under all three registered losses.
- [x] Generalize from exact independence to bounded predictive information and derive performance bounds where possible. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-2: with `D = Σ|P(x,y) − P_X(x)P_Y(y)|`, `gain ≤ D/2` — verified on **670,396** exhaustive grid cases with **0** violations and **15,328** attaining equality, tight witness `gain = 1/2`, `D = 1`; chaining the parent-owned Csiszár–Kullback–Pinsker inequality `I(X;Y) ≥ D²/2` gives the performance bound `2·gain² ≤ I(X;Y)` in nats, asserted only in exact rational form.
- [x] Distinguish mutual information from usable/accessible information under computational/resource constraints. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-4: on `Y = x_0⊕x_1⊕x_2` the learner sees all of `x` and `I(X;Y) = 1` bit exactly, yet the best decision tree attains exactly the base rate `1/2` at depths 0, 1 and 2 and only reaches `1` at depth 3; the dictator `Y = x_0` carries exactly the same one bit and is decoded perfectly at depth 1.
- [x] Construct a source with high mutual information but computationally inaccessible dependence and show why Shannon information alone does not guarantee practical intelligence. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-4: the source is `Y = x_0⊕x_1⊕x_2` with full observation of `x`, `I(X;Y) = 1` bit (maximal for a binary target) and exactly base-rate accuracy `1/2` for every decoder of branching depth below 3; the separation is **unconditional** — it rests on the machine-checked fact that for all `7` proper coordinate subsets `(x_S, y)` is exactly uniform (`0` violations), not on any cryptographic hardness assumption.
- [x] Construct low-entropy/nonuniform but temporally independent controls. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-5 `LOWENT_IID`: i.i.d. Bernoulli(1/10) — marginal `(9/10, 1/10)` is nonuniform while the pair `(X_{t−1}, X_t)` is exactly a product measure, so L1 dependence, mutual information and predictive gain are all exactly `0`.
- [x] Construct high-entropy but strongly predictable structured controls. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-5 `HIGHENT_CYCLIC`: `X_t = X_{t−1} + 1 (mod 4)` with `X` uniform on `Z_4` — marginal entropy is `2` bits exactly, the maximum on four letters, while `acc_base = 1/4`, `acc_obs = 1` and the predictive gain is `3/4`.
- [x] Add nonstationary/drifting sources where historical dependence ceases to be useful. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-5 `DRIFT_INVERT`: phases `Y = X` then `Y = 1 − X`, equiprobable — each phase carries `1` bit, the pooled joint is **exactly** independent (L1 dependence `0`), and the phase-1 rule scores `1` in phase 1 and exactly `0` in phase 2 against a base rate of `1/2`, so historical dependence becomes harmful rather than merely useless.
- [x] Add chaotic deterministic systems where microscopic predictability is horizon-limited. — ✅ `gmi-833-ae-ae2-predictive-boundary-v1` PIB-5 `CHAOS_DOUBLING`: `x_{t+1} = 2x_t (mod 1)` on `8`-bit dyadic states with the top `4` bits observed, all `256` states enumerated — the next symbol is determined with certainty for exactly `4` steps and the Bayes accuracy is exactly `1/2` from step `4` onward.

### AE3 — Compression is not automatically learning
- [ ] Formalize at least three notions separately: lossless description compression, task-relevant lossy compression, and model/generalization compression.
- [ ] Prove/construct cases where data compresses but the compressed representation is useless for the target task.
- [ ] Prove/construct cases where a useful predictor is not the shortest description under the chosen coding language.
- [ ] Distinguish memorization/compression from out-of-sample generalization.
- [ ] Relate GMI precisely to MDL/Bayesian coding/PAC-Bayes/compression bounds where applicable; subtract parent-owned theorems.
- [ ] State Kolmogorov-complexity uncomputability boundaries explicitly; forbid claims that GMI computes the true shortest program in general.
- [ ] Define computable surrogates and quantify their representation-language dependence.
- [ ] Test whether GMI predictions survive multiple coding languages/universal-machine remints up to the actually justified invariance boundary.

### AE4 — Information Bottleneck / relevant-information boundary
- [ ] Formalize the task-relevant representation problem using established Information Bottleneck / rate-distortion terminology where applicable.
- [ ] Determine when a GMI minimal behavioral/predictive state is equivalent to, refines, or is incomparable with an IB-optimal representation.
- [ ] Prove smallest counterexamples preventing unqualified identification.
- [ ] Distinguish `retain information about Y` from `retain information required for action/control under utility U`.
- [ ] Derive conditions under which forgetting task-irrelevant information is optimal under resource constraints.
- [ ] Derive conditions under which apparently irrelevant information must be retained because of future task uncertainty, transfer, revision, causal intervention, or verifier needs.
- [ ] Quantify representation-capacity vs predictive/control distortion frontiers.
- [ ] Add held-out crossover predictions as memory/compute/precision prices change.

### AE5 — Predictive-state / causal-state unification audit
- [ ] Relate GMI predictive equivalence to computational-mechanics causal states / epsilon-machines at the exact applicable scope.
- [ ] Compare GMI minimal sufficient predictive state with statistical complexity and predictive information/excess entropy.
- [ ] Determine whether existing GMI state-complexity results are already parent-owned by causal-state/minimal-predictor theory.
- [ ] Construct processes where predictive-state cardinality, linear predictive rank, entropy of causal state, and description length disagree.
- [ ] Determine which quantity, if any, predicts morphology/resource cost under GMI.
- [ ] Extend beyond finite horizon only with explicit measurable/infinite-horizon assumptions; otherwise preserve OPEN gaps.

### AE6 — Manifold hypothesis and geometric structure
- [ ] Replace loose `data lie on a manifold` language with a hierarchy: low intrinsic dimension, union/stratification of manifolds, sparse/compositional latent structure, symmetry/orbit structure, graph/topological structure, and non-geometric algorithmic structure.
- [ ] Construct learnable distributions that violate a smooth-manifold assumption.
- [ ] Construct low-dimensional manifolds that are statistically/causally useless for the target task.
- [ ] Derive when locality/smoothness should favor local/shared operators.
- [ ] Derive when symmetry/equivariance should favor parameter sharing.
- [ ] Derive when compositional latent factors should favor modular/hierarchical representations.
- [ ] Derive when manifold assumptions fail and another morphology should be selected.
- [ ] Prospectively test intrinsic-structure -> morphology transitions on synthetic and real datasets.

### AE7 — From prediction to control
- [ ] Prove that prediction alone is insufficient for general intelligence by constructing same-predictive/different-control-relevance examples.
- [ ] Formalize control-relevant sufficient state / action equivalence under a utility or behavioral specification.
- [ ] Relate to POMDP belief states, sufficient information states, rate-distortion control and bounded rationality; subtract parent mathematics.
- [ ] Derive value-of-information conditions for when sensing/remembering/computing additional information is worth its resource cost.
- [ ] Derive when an agent should compress observations more aggressively because actions are insensitive to distinctions.
- [ ] Derive when control requires preserving distinctions that pure prediction would discard.
- [ ] Prospectively predict policy/representation transitions under changing information-processing prices.

### AE8 — `Compression + Prediction + Control` master-principle test
- [ ] Formalize candidate CPC principle(s) without choosing weights post hoc.
- [ ] Determine whether CPC is a theorem, variational principle, decomposition, heuristic, or merely descriptive slogan.
- [ ] Search for a minimal objective that reproduces multiple existing GMI laws as corollaries.
- [ ] Prove which GMI phenomena cannot be reduced to CPC without additional terms (verification, development, communication, history, uncertainty, etc.).
- [ ] Compare CPC against alternative master principles: MDL, rate-distortion, bounded rationality, predictive information, free-energy/active-inference formulations, control-as-inference, algorithm selection and resource-rational computation.
- [ ] Construct preregistered worlds where these principles make different predictions.
- [ ] Preserve observational equivalence where no discriminating experiment exists.
- [ ] Do not call CPC the GMI master law unless it beats the bag-of-laws baseline and survives parent discrimination.

### AE9 — Learning as representation restructuring
- [ ] Define measurable representation-change quantities during learning that do not depend on neural architecture names.
- [ ] For neural systems, measure representational geometry, effective rank/dimension, clustering, linear separability, invariances, circuit/path usage and information flow across training.
- [ ] Distinguish smooth quantitative improvement from genuine qualitative computational transition.
- [ ] Re-audit `emergence` terminology: thresholded metric artifact vs phase-like internal reorganization vs grokking-like delayed generalization.
- [ ] Freeze prospective markers of a representation transition before observing the capability transition.
- [ ] Test whether internal transition markers predict new capability onset better than parameter count/training loss alone.
- [ ] Compare neural transition results with non-neural systems to test whether the law is architecture-general.

### AE10 — Resource-bounded usable information
- [x] Define `usable information` relative to allowed computation, memory, communication, precision, time and energy budgets. — ✅ `gmi-833-ae-ae10-usable-information-v1` D-AE10: `U(W,T,R)` = best expected score over the rules admissible at budget `R`, minus the best blind score — exact rational, task-relative, defined by the rule class and never by an architecture; the frozen lattice is `(junta arity k, tree depth d, sample budget m, precision p, communication bits c)` with `128` decoder-side cells, and time and energy are **declared but not instantiated**, recorded as a checked receipt field rather than passed off as measured.
- [x] Show exact examples where Shannon mutual information is identical but achievable task performance differs because decoding/search cost differs. — ✅ `gmi-833-ae-ae10-usable-information-v1` USE-3: at the identical budget `k3_d2_p3_c2` — where junta arity and precision are unrestricted so only the decoder's branching depth binds — `W_PARITY3` and `W_DICTATOR` both have `Y` determined by `X` with a uniform `Y`-marginal — so `I(X;Y) = 1` bit **exactly** for both — yet `U = 0` versus `U = 1/2`, a difference of `1/2` attributable to decoder branching cost alone; on the search axis a **single fixed** world (`Y = ⟨s,x⟩`, `s` uniform over the 7 nonzero secrets) holds information identical by identity while accuracy moves `5/8 → 43/64 → 383/512 → 3463/4096` as the sample budget goes `0→3`.
- [x] Derive monotonicity/bounds as resource budgets relax. — ✅ `gmi-833-ae-ae10-usable-information-v1` USE-1/USE-2: `U` is monotone on the frozen lattice — **9,000** ordered budget pairs across 3 worlds with **0** violations, with the rule-class inclusion premise itself checked rather than assumed — and is bounded above by the full-information gap with **0** violations, equality attained at the lattice top for every registered world.
- [x] Relate to computationally constrained information measures / bounded rationality literature rather than inventing duplicate terminology. — ✅ `gmi-833-ae-ae10-usable-information-v1` USE-5: a machine-readable crosswalk in the receipt maps `U` onto predictive V-information (Xu et al., ICLR 2020, arXiv:2002.10689) as an instance with `V = H_R` and 0-1 loss, the budget lattice onto bounded rationality and resource-rational analysis (Simon 1955, doi:10.2307/1884852; Lieder & Griffiths 2020, doi:10.1017/S0140525X1900061X), the exists-but-not-extractable phenomenon onto HILL pseudoentropy (Håstad et al. 1999, doi:10.1137/S0097539793244708) and the ceiling onto the data-processing/rate-distortion bound (Cover & Thomas 2006) — all four entries carry citations and no duplicate term is introduced without one.
- [ ] Determine whether GMI morphology selection is better predicted by raw information, usable information, or a vector of resource-conditioned sufficient statistics.
- [x] Add adversarial cryptographic/pseudorandom-style fixtures only at a mathematically defensible scope to separate information existence from feasible extraction. — ✅ `gmi-833-ae-ae10-usable-information-v1` USE-4: the fixture is `Y = x_0⊕x_1⊕x_2`, for which all `7` proper coordinate subsets give an exactly uniform `(x_S, y)` (**0** violations), so `U = 0` at junta arity 2 and `1/2` at arity 3; the separation is **unconditional** — the receipt records `cryptographic_assumption_used: false` and `is_a_complexity_class_separation: false`, so no hardness conjecture is smuggled in.

### AE11 — Thermodynamics and physical information processing
- [ ] Keep Shannon entropy, algorithmic complexity, statistical-mechanical entropy and thermodynamic entropy formally distinct.
- [ ] Define exactly which GMI resource claims are logical/computational and which are physical/energetic.
- [ ] Audit Landauer-style lower bounds and their assumptions; do not infer whole-system energy from bit erasure alone.
- [ ] Model nonequilibrium maintenance only where a physical system boundary/dynamics are registered.
- [ ] Compare logical irreversibility with physical dissipation at the correct scope.
- [ ] Measure actual energy on real hardware for selected GMI morphology transitions.
- [ ] Test whether information-theoretic savings predict physical energy savings; preserve negative results if hardware overhead dominates.
- [ ] For biological claims, separate energetic maintenance of life from cognitive information processing.

### AE12 — Free-energy / active-inference strongest-parent audit
- [ ] Audit Free Energy Principle / active inference as a strongest-parent candidate for perception-learning-action unification.
- [ ] State exact assumptions needed for any claimed equivalence with Bayesian inference/predictive coding/control.
- [ ] Include published technical counterexamples/criticisms; do not inherit universal FEP claims uncritically.
- [ ] Construct finite discriminating tasks where GMI/CPC, rate-distortion control and an active-inference formulation differ.
- [ ] Compare predictive and control behavior prospectively.
- [ ] If GMI is reducible to an established FEP/active-inference formulation at a scope, mark parent sufficiency rather than novelty.

### AE13 — Causality and intervention
- [ ] Prove that observational compression/prediction does not generally identify causal structure.
- [ ] Construct observationally equivalent worlds with different intervention consequences.
- [ ] Define when interventions are required for the behavioral specification.
- [ ] Derive the value of intervention under resource cost.
- [ ] Distinguish predictive state from causal/control state.
- [ ] Relate to causal-state, causal-representation-learning and causal-inference parents precisely.
- [ ] Test whether causal structure changes selected morphology relative to observational prediction alone.

### AE14 — Generalization, analogy, reasoning: do not collapse them by rhetoric
- [ ] Give architecture-independent operational definitions of memorization, interpolation, extrapolation, systematic generalization, analogy, planning/inference and reasoning.
- [ ] Determine which are reducible to prediction under a registered specification and which require additional search/composition/control machinery.
- [ ] Construct matched tasks where predictive accuracy is equal but reasoning/compositional capability differs.
- [ ] Construct matched tasks where compression is equal but transfer differs.
- [ ] Test whether GMI predicts which additional computational mechanisms are required.
- [ ] Forbid the blanket claim that memory/generalization/analogy/reasoning are `the same mechanism at different scales` unless a formal reduction theorem is earned.

### AE15 — World-model necessity boundary
- [ ] Define `world model` operationally and distinguish explicit generative model, predictive state, value representation, reactive policy and cached skill.
- [ ] Construct tasks solvable optimally without an explicit world model.
- [ ] Construct tasks where a model is provably necessary under the registered interface/resource assumptions.
- [ ] Derive model-based vs model-free/retrieval/reactive phase boundaries.
- [ ] Test whether latent variables recovered by a model correspond to identifiable world factors or merely predictive coordinates.
- [ ] Forbid claims that successful intelligence necessarily reconstructs human-interpretable latent variables.

### AE16 — Real-world empirical programme
- [ ] Choose real datasets/tasks spanning vision, language, sequential control and one scientific/biological domain.
- [ ] Estimate relevant structure measures without using protected outcomes to choose them.
- [ ] Freeze GMI predictions linking structure/resource regime to representation/morphology/capability.
- [ ] Compare against strong architecture-selection and information-theoretic baselines.
- [ ] Include deliberately structure-destroyed controls preserving marginal statistics where possible.
- [ ] Include structure-preserving recodings/remints.
- [ ] Test predicted crossovers as data, compute, memory, precision and energy budgets vary.
- [ ] Report failures and non-identifiability rather than post-hoc redefining `structure`.

### AE17 — Recursive loophole extraction for this addendum
- [ ] Every AE theorem/result emits assumptions, strongest parents, counterexamples, falsifiers, prior disclosures and unresolved descendants into the #833 gap graph.
- [ ] Every proposed scalar `structure/intelligence/information` measure must be attacked with at least two non-isomorphic counterexample families.
- [ ] Every positive unification claim must include a nearest negative theorem/counterexample.
- [ ] Every finite theorem must retain explicit finite/sample/horizon tags.
- [ ] Every architecture-selection claim must pass #833 D controls: matched negative twin, semantic remint, alternate search and Pareto/resource sensitivity.
- [ ] Every parent-overlap finding updates the terminology/subsumption ledger.
- [ ] Reopen any green AE row if a material descendant gap is discovered.

### AE closure rule

This addendum is **not** closed by showing that structured data are compressible or that mutual information is nonzero. A strong terminal requires a chain of the form:

`registered world/task structure -> architecture-independent sufficient/predictive/control requirements -> resource-conditioned representation/morphology prediction -> frozen recovery/selection -> held-out validation -> real-system test`

with parent subtraction and explicit counterexamples at every arrow.

Forbidden promotions from AE alone: `INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`, `MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`, `WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`, `THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`.
