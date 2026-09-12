# Known-form recursive derivation register v2

Date: 2026-09-12. Additive to the V1 zero-prior and known-form gap ledgers; base `f211f99a9aaefcfcca05850e1930885701358bcc`. Related issues: #431, #432, #433, #435. Corrigendum: `GMI_RECURSIVE_CLOSURE_CORRIGENDUM_V1.md`.

## Status and dependency contract

This register contains 24 requested family groups, each with 13 required atoms. It is a conditional derivation and blocking-experiment register, NOT 24 completed derivations. No family-wide K4, K5 or K6 promotion is made here. It does not certify that every claim in every other repository file has been audited.

`[P]` means reduction to an exact scoped parent/proof under the stated assumptions, NOT an architecture selection result. `[E]` means only the named executed finite subcase. `[O]` means OPEN-BLOCKING with the frozen closure test below. A registered experiment is not an executed experiment.

For each family F, atom IDs are F.01 through F.13 in the order shown. Dependencies: .02 -> .01 and finite-state/parent bound; .03 -> .01 and legal primitives; .04 -> the family generator and measurement contract; .05 -> .02/.03/.04 and C1; .06 -> C2; .07 -> .01/.04 and the frozen paired generator; .08 -> C3; .09 -> .05/.06/.08; .10 -> .02/.03/.07/.08/.09 and C4; .11 -> .10 and C5; .12 -> .11 and C6. Atom .13 is an experimental decision rule, not evidence that its conditions passed. Every empirical dependency terminates in C1-C6 or the explicitly named family test, not in an asserted universal law.

Common exact roots: RC-04 semantic distinguishability at a specified causal cut; RC-08 matched-quality lifecycle inequality; KF-1..13 in `GMI_KNOWN_FORM_DERIVATION_THEOREMS_V1.md`; KF-14..22 in V2. Their finite precision, admissibility and restricted-comparator assumptions are mandatory. Existence of a representation is never treated as a proof of its acquisition or generalization.

Additional kernel root: in a fixed Hilbert function space with objective depending on finitely many evaluation values and a strictly increasing function of the norm, project any candidate onto the span of the corresponding kernel sections. Orthogonal residuals vanish at the evaluation points and only increase the norm; hence an optimum, when it exists, lies in that span. This is the representer-theorem parent, not a learned-kernel or architecture-uniqueness theorem. Parent: Schölkopf, Herbrich and Smola (2001), *A Generalized Representer Theorem*.

## Frozen common closure tests C1-C6 — not executed

**C1, complete meter.** Record acquisition/labels, pretrained state, rejected search candidates, development, updates, query compute, bytes read/written, communication, verification, precision, external tools and human author effort separately. For synthetic microscopes use exact primitive counters. Before real runs require an independent meter to reproduce every counter on 32 adversarial tiny traces, including failed proposals, retries, cache misses and rollback. Any omitted positive cost invalidates a frontier comparison, rather than silently assigning zero.

**C2, strongest parents.** For every family include the listed competitors plus a general low-level program and the best shared representation admitted by the same information contract. Enumerate the tiny scope where possible. In larger scopes allocate the same full development/tuning budget per arm and publish all failed trials. No execute-all portfolio may stand in for an optimally shared dense parent. Failure to bound parent adequacy yields INCONCLUSIVE_PARENT_SET, not a GMI victory.

**C3, pre-outcome measurement.** Descriptor extraction may read only the registered development split or charged specification oracle. It cannot read protected labels, final trained weights, achieved loss, search winners, architecture labels or world IDs. Freeze extractor, estimator, uncertainty intervals and predictions before protected generation. Compare against descriptor-ablation, standard statistical/description-length and resource-cost predictors. RC-07 requires retaining descriptor collisions and set-valued uncertainty; it does not authorize looking up the protected cost label.

**C4, neutral rediscovery.** The initial grammar contains finite-width constants, scalar arithmetic/Boolean operators, comparison, branch, indexed load/store, explicit random-bit sampling and bounded loops. It has no convolution, attention, recurrent gate, tree learner, solver, expert, retriever or adapter macro. Every compound operator expands to charged primitives. Register three independently implemented encodings of the same admitted candidate semantics (expression/graph, register program, bytecode), with sharing and state costs normalized before comparing them. Start with widths 1,2,4,8 and program caps 4,8,12; allow at most 1,000,000 scored candidates per cell. Verify representation and search calibration using matched-description control tasks. A search limit is INCONCLUSIVE_SEARCH unless an exhaustive bound or independent positive-control recovery supports attributing failure to the theory. These choices are a frozen pilot scope, not evidence of adequacy for large architectures.

**C5, held-family prediction.** For each family-specific structural axis below, use 32 development worlds, 16 validation worlds and 32 protected worlds from the excluded structural subfamily, with five development seeds and all three encodings. An independent author must commit the protected generator and concealed seed commitment after predictions freeze; this prerequisite is currently OPEN, so no protected results exist. Freeze a frontier choice and 90% cost/risk interval per cell. Pilot acceptance requires zero exact-semantic violations where exactness is required; otherwise the predeclared risk limit; at least 29/32 protected costs in the frozen intervals; and mean normalized cost regret <=0.10 against the metered parent envelope. All failures are retained. This is a registered acceptance rule, not a claim that 32 worlds establish a universal law.

**C6, real transfer.** Before any real test, pin workload snapshot, license, partition, metrics, quality threshold, hardware/compiler versions, budgets and all parent implementations. Select 32 untouched episodes or tasks along the named real axis. Repeat C1-C5 information/metering rules, matched risk and bootstrap uncertainty over independent tasks. No source acquisition or real transfer was performed in this tranche. Missing workload snapshots are explicit entry blockers; registering a target class does not fabricate a frozen dataset.

Universal failure rules: any counterexample falsifies the corresponding exact theorem at its assumptions; a protected prediction miss is preserved against the frozen version; failed representation/search calibration blocks attribution; a name, template or protected-outcome leak invalidates zero-prior evidence. A successor may change only the failed atom and must use a fresh protected generator. Unknown-species claims stay gated.

## F01 — regression and generalized linear models

1. [P] State: for squared-error linear responses retain `X'X,X'y,y'y` during development and coefficients for serving (KF-1). For a canonical GLM retain its likelihood-relevant design information and `X'y`, with fixed link, family and dispersion; linear sufficient statistics alone do not cover arbitrary links.
2. [P] Lower bound: distinct restricted coefficient maps require distinguishable states on separating queries (RC-04). A finite b-bit grid of d identifiable coefficients needs db bits; no bound on arbitrary-precision real coordinates follows.
3. [P] Construction: solve the known linear objective and evaluate scalar multiply/add; evaluate the specified GLM link through primitives. Existence/conditioning/precision and GLM optimization must be checked, not assumed.
4. [O] Variables: design rank, conditioning, signal/noise, link misspecification, coefficient precision and stable reuse; their joint predictive sufficiency is F01/C3.
5. [P] Law: direct dense linear statistics cost O(nd^2) arithmetic, state O(d^2), serving O(d); add solve and precision costs. GLM fitting has a separate optimization bill.
6. [O] Parents: explicit memory, fixed-feature/kernel expansion, polynomial or nonlinear shared map, trees and symbolic rules; C2.
7. [O] Twin: replace the shared linear law by independent volatile key labels, or misspecify the link while holding sample count and noise fixed.
8. [O] Descriptor: development-only singular spectrum and link-residual diagnostic, with uncertainty and charged measurement; C3.
9. [O] Crossover: predict total shared-fit burden versus memory at matched risk using RC-08; model adequacy and sample burden remain unknown terms.
10. [O] F01/C4: finite grids d=1..4, rank-deficient and full-rank designs, linear/Bernoulli-link outcomes; rediscover compressed evaluation, not a named regression instruction.
11. [O] F01/C5: exclude oblique versus coordinate-aligned designs and one link family before fitting the predictor.
12. [O] F01/C6: pin an untouched tabular sensor-prediction workload; no such workload has been run here.
13. [O] Kill: an adequate cheaper parent outside the predicted interval, incorrect GLM sufficiency, or uncharged solve/precision work invalidates the corresponding claim.

## F02 — kernels and fixed-basis systems

1. [P] State: evaluation-equivalent function component in the span of observed kernel sections under the fixed-space/norm-penalty assumptions above.
2. [P] Lower: RC-04 applies to distinct function evaluations; rank of the evaluation map bounds independent identifiable directions, not a universal required number of support examples.
3. [P] Construction: weighted section expansion; orthogonal projection proves existence at a minimizer. The similarity function itself is not derived by this argument.
4. [O] Variables: Gram spectrum, effective dimension, feature evaluation cost, regularity mismatch, approximation tolerance and sample size.
5. [P] Law: m retained sections cost O(m) section calls per query plus weights/storage; dense Gram storage is O(n^2) for that implementation, not a lower bound on every kernel implementation.
6. [O] Parents: explicit finite features, low-rank approximations, nearest exemplars, learned features and direct programs.
7. [O] Twin: destroy similarity-label alignment or make a small explicit feature map sufficient.
8. [O] Descriptor: development-only spectral tail, local label smoothness and charged feature-cost probes; C3.
9. [O] Crossover: saved fit/generalization burden must exceed section evaluation, storage and approximation loss; no universal kernel selector is closed.
10. [O] F02/C4: finite positive-semidefinite Gram families with ranks 1..8 and controlled tails; compose scalar weighted similarities without kernel macros.
11. [O] F02/C5: hold out a spectral-tail class and remint feature coordinates.
12. [O] F02/C6: pin a small-data scientific regression workload and acquisition budget.
13. [O] Kill: norm/projection assumptions fail, learned geometry cost is omitted, or a stronger explicit-feature parent dominates the frozen prediction.

## F03 — exemplar and indexed memory

1. [P] State: exact current key-value map, plus provenance/version information only when demanded by future queries.
2. [P] Lower: N independent q-ary values have q^N distinguishable maps, hence ceil(N log2 q) fixed bits (KF-2); metric assumptions restrict this class.
3. [P] Construction: table with explicit key/address representation, indexed read and local write; approximate neighboring retrieval requires an independently justified metric.
4. [O] Variables: independent record count, metric dimension, volatility, retention/lineage, query skew and index-maintenance burden.
5. [P] Law: N payloads plus index storage; charge every lookup, insertion, deletion and rebuilding action. Constant lookup is only a specified addressing-model assumption.
6. [O] Parents: compressed coefficients, perfect or hashed tables, tries, sorted search and learned indexes with identical authority guarantees.
7. [O] Twin: values generated by a stable low-dimensional function with high reuse.
8. [O] Descriptor: development-only conditional label entropy, locality and revision hazard; unknown entropy cannot be replaced by outcome compression.
9. [O] Crossover: RC-08 with measured indexing and shared-model update costs; compression/metric estimation stays open.
10. [O] F03/C4: N=2,4,8 records, q=2,4,8, independent versus law-generated revisions; rediscover explicit retained cells and reads.
11. [O] F03/C5: hold out clustered versus uniform queries and a metric remint.
12. [O] F03/C6: pin a changing factual record workload with exact source/version checking.
13. [O] Kill: aliases, provenance loss, an unpriced index or a cheaper admissible compression outside the prediction.

## F04 — Bayesian belief and graphical systems

1. [P] State: posterior over latent hypotheses for every future expected-utility decision, assuming the latent model and likelihood are correct (KF-3/4).
2. [P] Lower: distinct posteriors are separated by some utility problem. On an m-state denominator-D probability grid, all admitted distinct posterior vectors require distinct codes; restricted utilities may need less state.
3. [P] Construction: finite likelihood multiplication and normalization; sparse factors only when the asserted conditional independences are valid.
4. [O] Variables: hypothesis count, posterior precision, graphical width, evidence quality, intervention availability and model mismatch.
5. [P] Law: explicit enumeration stores O(m) masses and charges likelihood calls; factor elimination complexity depends on induced factors, not merely graph edge count.
6. [O] Parents: point estimates under restricted loss, exact enumeration, factored elimination, approximate particles and compiled decision rules.
7. [O] Twin: fully observed deterministic states, or misspecified conditional independence.
8. [O] Descriptor: calibration and conditional-independence tests on development data; latent identifiability remains a separate blocker.
9. [O] Crossover: uncertainty-sensitive decision benefit must outweigh inference/precision/learning cost under the actual utility family.
10. [O] F04/C4: 2..8 finite hypotheses, rational likelihoods and varied separating utilities; rediscover normalized uncertainty state.
11. [O] F04/C5: exclude a graph topology and an evidence channel before predictor fitting.
12. [O] F04/C6: pin a partially observed diagnostic or control workload with ground-truth latent audits.
13. [O] Kill: posterior aliasing under separating utilities, miscalibration beyond the frozen risk bound, or hidden likelihood/model acquisition.

## F05 — trees and additive boosting

1. [P] State: cell/predicate and leaf values when the target is constant on a specified recursive partition; additive residual state when a target decomposes into specified weak functions.
2. [P] Lower: L reachable distinct leaf outputs require L terminal outputs in that leaf-output language (KF-14), not in every programming language.
3. [P] Construction: recursive tests implement the partition; summing known residual components telescopes (KF-15). This does not prove greedy split or weak-learner discovery.
4. [O] Variables: predicate language, boundary sparsity, depth, leaf count, weak-learner edge and residual noise.
5. [P] Law: depth counts tests per query; an additive portfolio pays the sum of active component work and all fitting rounds.
6. [O] Parents: oblique predicates, rules/decision diagrams, smooth shared maps, kernels and direct small programs.
7. [O] Twin: globally linear law for partitioning; noise-only or inaccessible residuals for boosting.
8. [O] Descriptor: development-only partition complexity and out-of-sample weak-learner edge; count the probing learner's cost.
9. [O] Crossover: reduction in protected approximation error versus extra tests/rounds and acquisition burden remains F05/C3.
10. [O] F05/C4: 2..8 cells, axis-aligned and oblique boundaries, 1..4 additive components; grammar includes predicates and scalar addition, no tree/boost macro.
11. [O] F05/C5: hold out predicate orientation and nonadditive interaction subfamilies.
12. [O] F05/C6: pin a discontinuous tabular decision workload with drift.
13. [O] Kill: infer greedy accessibility from a telescoping identity, reuse protected split quality, or omit the strong oblique/shared parent.

## F06 — symbolic and constraint systems

1. [P] State: the distinctions between legal constraint/rule theories that can change future admissibility answers, not a required historical syntax (RC-04).
2. [P] Lower: distinguishable future query responses bound state bits. SAT decision alone does not require retaining every satisfying assignment; no generic exponential solver lower bound is asserted.
3. [P] Construction: finite rule execution or enumerate assignments and check constraints; existence is exact but may be expensive.
4. [O] Variables: variable/domain count, constraint width, induced width, reusable rule length, proof size and noise.
5. [P] Law: exhaustive finite search gives a constructive exponential upper bound; propagation, caching and compilation need separately counted work.
6. [O] Parents: strong SAT/SMT/CSP solvers, algebraic elimination, decision diagrams, dynamic programming and neural proposals with exact checks.
7. [O] Twin: noisy observations without a short stable exact rule, or constraints with easy algebraic elimination.
8. [O] Descriptor: development-only rule compression and constraint graph statistics, with failed induction/solver probes charged.
9. [O] Crossover: reusable compiled rules versus query-specific search depends on acquisition and invalidation, not exactness alone.
10. [O] F06/C4: Boolean constraints on 2..8 variables including parity and CNF twins; compose tests/branches, no SAT or rewrite-system macro.
11. [O] F06/C5: exclude parity versus clause-based structure and semantic variable remints.
12. [O] F06/C6: pin code typechecking or proof-obligation tasks with exact certificates.
13. [O] Kill: semantic rule collisions, omitted induction cost or success only against a deliberately weak solver.

## F07 — search and planning

1. [P] State: query-conditioned unresolved alternatives and enough path/cost information to preserve registered decisions; a literal search tree is not universally necessary.
2. [P] Lower: an unrestricted Boolean candidate oracle with possible all-negative outcome needs N checks in the worst case to decide whether any of N candidates succeeds; stronger structure can invalidate that adversary.
3. [P] Construction: exhaustive frontier enumeration is finite; admissible pruning requires certified bounds and correct duplicate handling.
4. [O] Variables: branching, depth, heuristic informativeness, duplicate rate, goal volatility, reuse and verifier cost.
5. [P] Law: sum actual expansions/evaluations and retained frontier bytes; compare compilation with KF-12/RC-08 at matched quality.
6. [O] Parents: dynamic programming, symbolic/algebraic solution, memoization, learned heuristic, direct policy and complete search.
7. [O] Twin: repeated identical queries with cheap compilation, or an uninformative/biased heuristic.
8. [O] Descriptor: charged development-only heuristic calibration and overlap statistics; protected winning path unavailable.
9. [O] Crossover: heuristic value and reusable compilation cost are unknown terms, not settled by an expansion-count identity.
10. [O] F07/C4: finite graphs with 4..32 states and controlled repeated subproblems; recover priority/frontier or cache operations from primitives.
11. [O] F07/C5: exclude a graph topology and heuristic-error mechanism.
12. [O] F07/C6: pin code repair or logistics instances with exact solution checking.
13. [O] Kill: inadmissible pruning, omitted failed branches, or a frozen search-value prediction outside its interval.

## F08 — recurrent and linear state-space systems

1. [P] State: future-response history quotient (KF-5/RC-04); for finite-order linear time-invariant input-output laws, linear predictive state is a realization candidate.
2. [P] Lower: quotient class count in finite deterministic systems; Hankel rank lower-bounds linear realization dimension. Finite-rank shift-consistent Hankel data admit a minimal linear realization under the realization-theory assumptions of KF-18.
3. [P] Construction: quotient transition table or factored controllable/observable linear recurrence. Nonlinear/noisy order estimation is not solved.
4. [O] Variables: state order, observability, stability, precision, nonlinear drift and history-query requirement.
5. [P] Law: a dense d-state update uses O(d^2) arithmetic per step; structured scans may lower this under separately proved structure.
6. [O] Parents: full-history replay, predictive-state methods, nonlinear recurrence, retrieval and parallel sequence processing.
7. [O] Twin: memoryless mapping, or exact late history queries that exceed retained sufficient state.
8. [O] Descriptor: development-only Hankel singular spectrum and continuation collision tests, with finite-data uncertainty.
9. [O] Crossover: recurrence versus replay/all-pairs methods must include estimation, numerical stability and error accumulation.
10. [O] F08/C4: automata with 2..8 states and rational LTI systems of order 1..4; infer updateable state without a recurrence macro.
11. [O] F08/C5: exclude nonlinear transitions and changed observation maps.
12. [O] F08/C6: pin long sensor streams with state/order and drift audits.
13. [O] Kill: future-distinguishable histories collide or the claimed linear-order model silently absorbs nonlinear errors.

## F09 — convolution and equivariance

1. [P] State: tied operator coefficients when obligations commute with a specified group action; cyclic linear shifts yield circulant maps (KF-6).
2. [P] Lower: n independently chosen cyclic convolution coefficients require n distinguishable coefficient degrees on separating inputs; additional locality restricts this to k coefficients.
3. [P] Construction: the i-th matrix column is the i-th shifted first column; local multiply/add loops implement the corresponding filter.
4. [O] Variables: exact/approximate symmetry defect, locality radius, channels, boundary conditions and precision.
5. [P] Law: a specified width-k single-channel local filter uses O(nk) operations and k parameters; this is not a universal nonlinear-CNN lower bound.
6. [O] Parents: dense/locally connected operators, spectral transforms, group-equivariant alternatives and coordinate-conditioned shared programs.
7. [O] Twin: independently vary coefficients by location while holding marginal input statistics fixed.
8. [O] Descriptor: development-only commuting residuals and locality interventions; empirical symmetry estimates can be wrong.
9. [O] Crossover: saved sharing burden versus bias from broken symmetry needs an approximate-symmetry degradation law.
10. [O] F09/C4: cyclic sizes 3..8, locality 1..3 and controlled symmetry breaking; no convolution macro.
11. [O] F09/C5: hold out a group action or boundary condition and a symmetry-defect pattern.
12. [O] F09/C6: pin spatial sensing/image tasks with controlled transformations and exact metadata.
13. [O] Kill: equivariance is assumed rather than tested, or a nonlinear architecture claim is inferred from a linear theorem.

## F10 — graph-local message passing

1. [P] State: local information sufficient for the registered graph query; permutation-respecting local targets may admit shared neighborhood computation, not every invariant target does.
2. [P] Lower: T local synchronous rounds see only radius-T information (KF-16); identical local neighborhoods with different target outputs defeat that scope.
3. [P] Construction: primitive edge reads and shared updates when the target has the specified local compositional decomposition. Arbitrary multiset aggregation can lose distinctions.
4. [O] Variables: required radius, graph cuts, node precision, degree, aggregation injectivity and long-range demand.
5. [P] Law: count traversed edges times rounds and message size; oversquashing requires a separate information-through-cuts analysis.
6. [O] Parents: global algorithms, higher-order representations, positional information, graph rewrites and sparse/dense nonlocal routing.
7. [O] Twin: distant/global distinguishing property with locally identical neighborhoods.
8. [O] Descriptor: development-only intervention radius and bottleneck probes; node labels or protected outputs cannot leak the answer.
9. [O] Crossover: local round/communication saving versus aggregation error and global-routing cost is unclosed.
10. [O] F10/C4: graphs with 4..12 vertices, local additive targets and hostile globally different twins; explicit neighbor loads only.
11. [O] F10/C5: hold out graph topology, cut width and diameter regimes.
12. [O] F10/C6: pin relational code/dependency or molecular tasks with controlled graph splits.
13. [O] Kill: an isomorphic local collision is claimed solved without extra information, or global parents are omitted.

## F11 — selective recurrent gating, including RNN/LSTM properties

1. [E] State: current retained bit for the exact retain/overwrite obligation; RC-04 proves sufficiency and necessity at this cut.
2. [E] Lower: two retained values require one bit; all 16 unconditional affine Boolean updates fail exact selective retention.
3. [E] Construction: primitive XOR/AND formula; 2,730 finite histories passed. Other nonlinear recurrences remain legal competitors.
4. [O] Variables: write sparsity, retention horizon, state dimension, feedback quality, noise and precision.
5. [E] Law: RC-06 supplies exact internal formula costs and repricing; learning, recurrent stability and physical storage are not covered.
6. [O] Parents: simple nonlinear recurrence, explicit memory, finite-state transducer, indexed write and history replay.
7. [E] Twin: always retain or always overwrite needs zero internal operators with preloaded wires; real lifecycle charges remain.
8. [O] Descriptor: observed write/retain requirement and counterfactual continuation tests, not a named gate label.
9. [O] Crossover: the finite price law is closed; gate-versus-simpler-recurrence learning and serving frontiers remain untested.
10. [E/O] F11/C4: finite Boolean selector synthesis executed; multi-bit, noisy, learnable gates and independently implemented encodings remain OPEN.
11. [O] F11/C5: exclude a control-source and write-timing process before fitting response laws.
12. [O] F11/C6: pin event-driven long-memory streams with sparse updates.
13. [O] Kill: label the Boolean primitive an LSTM derivation, fail a retained-state continuation, or omit state/gradient development costs.

## F12 — dynamic routing and Transformer properties

1. [P] State: payload plus query/key/order distinctions sufficient at the actual information cut; order-sensitive obligations cannot use only a permutation-invariant bag.
2. [P] Lower: late-query record distinguishability (RC-04); KF-7 union-edge bound applies only to the explicit edge-evaluation model, not compressed algorithms in general.
3. [P/E] Construction: indexed or content-conditioned selection is feasible; the three-input selector is synthesized. Softmax, multihead structure, positional encoding and full Transformers are not uniquely derived.
4. [O] Variables: dependency variability, density, discovery cost, sequence length, ordering and precision.
5. [P] Law: router cost plus selected interactions must beat the best fixed/compressed alternative; charge key construction and retained cache.
6. [O] Parents: indexed lookup, recurrent sufficient state, state-space recurrence, fixed sparse graph, dense shared program and retrieval.
7. [O] Twin: fixed dependencies or early-known query; content routing loses the corresponding opportunity.
8. [O] Descriptor: charged development-only dependency/cut probes; RC-07 shows low-order geometry alone may alias priced costs.
9. [O] Crossover: routing-error and dependency-discovery response law remains GKF-05, despite exact selector repricing.
10. [O] F12/C4: 2..8 payload slots, early/late queries, fixed/content selectors and order-sensitive twins; no attention or softmax macro.
11. [O] F12/C5: hold out dependency-generating rules and query-arrival timing combinations.
12. [O] F12/C6: pin long code/document tasks with query-locality and cache accounting.
13. [O] Kill: claim an unrestricted lower bound from edge counting, or infer full-family recovery from one selector.

## F13 — sparse attention and sparse interaction

1. [P] State: target-relevant edge pattern and associated values only if its omissions preserve the obligation; discovering the pattern is part of development/execution.
2. [P] Lower: m required explicit interactions impose m interaction evaluations in that registered model; compressed algebraic alternatives can evade this model.
3. [P] Construction: explicit index generation and edge loops; exact only with a correct complete pattern.
4. [O] Variables: edge density, pattern entropy, discovery complexity, omission sensitivity and memory-layout overhead.
5. [P] Law: `pattern_discovery + sparse_interactions + indexing` versus dense work (KF-19); sparsity alone is insufficient.
6. [O] Parents: dense fused operations, structured transforms, recurrence, block sparsity and exact indexing.
7. [O] Twin: dense dependencies or a sparse pattern as expensive to find as dense evaluation.
8. [O] Descriptor: development-only perturbation and dependency tests, including misses and their uncertainty.
9. [O] Crossover: saved interactions must exceed discovery/layout/error burden on the actual substrate.
10. [O] F13/C4: 4..16 slots with local, random and implicit sparse dependencies; no sparse-attention macro.
11. [O] F13/C5: exclude a pattern-generation algorithm, not just new random edge masks.
12. [O] F13/C6: pin long-context or graph tasks with measured memory traffic.
13. [O] Kill: omission violates risk, implicit pattern discovery is free, or dense fused parents are absent.

## F14 — conditional experts and mixture-of-experts properties

1. [P] State: enough information to distinguish demanded modes and compute their target functions; expert modules are one possible realization, not a semantic necessity.
2. [O] Lower: a separation from the BEST shared dense program is missing; execute-all comparison KF-8 does not supply it.
3. [P] Construction: primitive router plus specialized computations when mode membership and component functions are available; their learning costs remain due.
4. [O] Variables: function overlap, heterogeneity, activation sparsity, routing error, communication and maintenance.
5. [P] Law: `router + sum p_j cost_j + communication`, plus all parameter and update storage; only a conditional upper bound.
6. [O] Parents: optimally shared dense model, low-rank factorization, conditional program, execute-all and local table.
7. [O] Twin: identical mode functions, shared low-dimensional basis, or dominant communication price.
8. [O] Descriptor: held-development estimates of cross-mode function overlap and routing uncertainty; avoid hindsight specialization scores.
9. [O] Crossover: dense-versus-conditional separation requires charged construction and error, not counting inactive parameters.
10. [O] F14/C4: 2..4 modes with controllable shared and independent truth-table components; branch/load/arithmetic only.
11. [O] F14/C5: exclude an overlap-generating rule and mode-frequency skew.
12. [O] F14/C6: pin heterogeneous code or language tasks and cross-device traffic.
13. [O] Kill: no advantage over the best shared parent, hidden communication, or routing learned from protected mode labels.

## F15 — external residual memory and retrieval augmentation

1. [P] State: distinguish target outcomes still aliased by a reusable predictor, plus authoritative source/version data demanded by the constitution (KF-10).
2. [P] Lower: residual alphabet at least `max_p multiplicity(p)`; conditional entropy is an average coding bound under explicit coding assumptions, not a latency bound.
3. [P] Construction: residual code/table plus exact predictor-class decoder; approximate retrieval is a separate error-bearing implementation.
4. [O] Variables: conditional residual multiplicity, volatility, provenance, update locality, reuse and retrieval price.
5. [P] Law: stable core plus residual acquisition/store/query/update costs versus full or local core rewrite, under matched authority guarantees.
6. [O] Parents: direct database, cache, model editing, full retraining, low-rank adaptation and symbolic authority store.
7. [O] Twin: target quotient already determined by the predictor, or stable compact residual law.
8. [O] Descriptor: development-only predictor-target collision probes and source-change rates; protected semantic labels unavailable.
9. [O] Crossover: GKF-08 residual estimator and G2-15 authority-loss calibration remain open.
10. [O] F15/C4: finite predictor/target partition pairs and mutable records; explicit reads/writes, no retriever macro.
11. [O] F15/C5: exclude a residual-generation and provenance-conflict mechanism.
12. [O] F15/C6: pin a versioned factual/scientific source corpus with exact citations.
13. [O] Kill: a retrieval answer has wrong authority/version, residual collisions persist, or external storage/acquisition is unpriced.

## F16 — adapters and low-rank updates

1. [P] State: target residual linear map relative to a fixed reusable map; nonlinear target residuals depend on the chosen representation and layer.
2. [P] Lower: a width-r factor product has rank <=r, so exact rank-r0 residual needs r>=r0 (KF-9).
3. [P] Construction: rank factorization supplies B and A at r0; dimensions and permitted precision must be registered.
4. [O] Variables: residual spectrum, input covariance, layer sensitivity, nonlinear coupling and update reuse.
5. [P] Law: rank-r factors store r(d_in+d_out) scalars and evaluate via two products; include core cost and search for the factors.
6. [O] Parents: full residual matrix, sparse/local editing, explicit residual memory, shared subspace and full retraining.
7. [O] Twin: full-rank slowly decaying residual or representation change invalidating the frozen core.
8. [O] Descriptor: development-only residual spectral estimates and uncertainty; post-fit adapter rank is not pre-outcome evidence.
9. [O] Crossover: representation-specific approximation error versus factor development and serving cost remains open for nonlinear models.
10. [O] F16/C4: rational matrices sizes 2..8 and ranks 0..4; derive shared intermediate scalar computations without an adapter macro.
11. [O] F16/C5: exclude singular-vector alignment and nonlinear perturbation families.
12. [O] F16/C6: pin real task adaptation with identical base, data and precision budgets.
13. [O] Kill: extend an exact linear rank theorem to nonlinear risk without a reduction, or exclude stronger sparse/local parents.

## F17 — ensembles

1. [P] State: multiple error-bearing predictions and their aggregation sufficient for the specified loss; multiplicity is not necessary when one predictor dominates.
2. [P] Lower/limit: common error and bias cannot be removed by averaging. Under unbiased equal-variance equicorrelated errors, covariance algebra gives KF-11; the covariance must be positive semidefinite.
3. [P] Construction: arithmetic mean via scalar sums/division; other losses require a separate decision rule.
4. [O] Variables: error covariance, shared bias, development dependence, member costs and risk asymmetry.
5. [P] Law: variance `sigma^2[rho+(1-rho)/m]` under those assumptions, plus summed development/serve burden.
6. [O] Parents: best single predictor, shared multi-output computation, distillation, weighted covariance-aware combination and selective routing.
7. [O] Twin: perfectly correlated errors or shared systematic bias.
8. [O] Descriptor: development/validation cross-fitted covariance estimate with uncertainty; no protected-error covariance.
9. [O] Crossover: protected risk reduction must exceed total member and aggregation costs; covariance-shift response remains open.
10. [O] F17/C4: finite joint-error tables with m=2..4 and controlled covariance, synthesis from primitive outputs and sums.
11. [O] F17/C5: hold out an error-dependence and bias mechanism.
12. [O] F17/C6: pin multi-model predictions on an untouched real task split.
13. [O] Kill: biased/nonexchangeable errors are substituted into the wrong formula or shared training burden is hidden.

## F18 — verifier-gated systems

1. [P] State: proposal, verifier-relevant evidence and authoritative state separated until admission; provenance and rollback state depend on the constitution.
2. [P] Lower: merging histories needing different acceptance decisions loses admissibility information (RC-04); no verifier competence is assumed from its name.
3. [P] Construction: propose, check and conditionally commit. An exact sound verifier gives no invalid admissions (KF-22), assuming no bypass.
4. [O] Variables: false-accept/false-reject rates, proposal validity, costs, loss asymmetry, verification locality and reuse.
5. [P] Law: for one proposal, expected false-adoption loss equals P(invalid)*P(accept|invalid)*loss under fixed loss, plus checking and rejection costs; adaptive selection changes these probabilities.
6. [O] Parents: direct reliable solver, safe abstention, human/exact checker, proposal-only and full recomputation.
7. [O] Twin: negligible false-adoption loss, perfect proposal or prohibitively expensive verification.
8. [O] Descriptor: held-development generator/checker cross-tests, especially correlated and adaptive failures.
9. [O] Crossover: calibrated hazard reduction must pay for checking, rollback and rejected work; G2-09/10 open.
10. [O] F18/C4: finite proposal/checker confusion tables and authoritative update traces; no verify/admit macro.
11. [O] F18/C5: exclude a generator error mechanism and adaptive attack family.
12. [O] F18/C6: pin code/proof verification tasks with exact certificates and bounded execution.
13. [O] Kill: any invalid admitted update under an exact-soundness claim, checker bypass, or uncharged rejected work.

## F19 — tools and heterogeneous composition

1. [P] State: tool-relevant input distinctions, admissibility, intermediate results and authority contracts; multiple tools are needed only when no cheaper admitted one supplies equivalent information.
2. [P] Lower: if a tool reveals an address needed by a second tool and no single-call transcript determines the answer, RC-04 forbids exact one-call solutions under that oracle contract.
3. [P] Construction: typed sequential calls plus explicit result transport; single-tool argmin KF-21 assumes losses/costs are already known.
4. [O] Variables: complementary information, intermediate type/size, call risk, latency, authority and reuse.
5. [P] Law: sum call, transport, verification and failure/retry burdens along the executed dependency graph.
6. [O] Parents: strongest single solver, local implementation, cached composite, compiled pipeline and dynamic planner.
7. [O] Twin: one tool already supplies all required information or the intermediate dependency disappears.
8. [O] Descriptor: pre-call capability/error contracts estimated on development tasks; not actual protected tool outcomes.
9. [O] Crossover: routing versus multi-step composition needs a predictive value-of-information and failure law.
10. [O] F19/C4: two finite oracles with early/late address dependence and 2..8 values; raw calls are priced, routing macros prohibited.
11. [O] F19/C5: exclude a tool-complementarity graph and error correlation pattern.
12. [O] F19/C6: pin code/math workflows with sandboxed tool traces.
13. [O] Kill: a cheaper single-tool parent exists, result authority is lost or hidden retries dominate.

## F20 — continual learning and retention

1. [P] State: current sufficient law plus distinctions needed by future retained-task or historical-version queries; retention tolerance and lineage are separate obligations.
2. [P] Lower: N independent q-ary current records require N log2 q bits; demanding K independent complete historical versions raises the distinguishable payload count to q^(NK). This does not require any specific replay architecture.
3. [P] Construction: exact versioned table/replay history is an upper bound; modular rewrite or constrained updates require proven noninterference or checked retention.
4. [O] Variables: update overlap, task similarity, forgetting tolerance, historical query demand, plasticity, storage and drift.
5. [P] Law: charge acquisition, replay, local/global update, retained history and verification; latest-state versus lineage costs are not interchangeable.
6. [O] Parents: replay, regularization, expansion, modular update, exact memory, full retraining and stable shared representation.
7. [O] Twin: stationary short-horizon task, or no retained/history obligation; separately vary high lineage with low current retention.
8. [O] Descriptor: development-only update cones, task interference probes and explicit retention/lineage contracts.
9. [O] Crossover: GKF-12 plasticity/interference and storage-versus-recompute response laws remain open.
10. [O] F20/C4: independent/local/shared record updates over 2..8 keys with factorial current retention and historical queries.
11. [O] F20/C5: hold out an overlap/drift mechanism, not merely new update seeds.
12. [O] F20/C6: pin changing code/factual tasks with immutable historical evaluation snapshots.
13. [O] Kill: retained obligations fail, lineage is confused with current accuracy or update/replay work is omitted.

## F21 — generative systems

1. [P] State: sufficient conditional distribution/sampler state for the demanded joint law and conditioning interface; sample appearance alone does not identify distributional adequacy.
2. [P] Lower: distinct finite distributions requiring different probability answers must remain distinguishable; fresh sample randomness and retained distribution description are separate resources.
3. [P] Construction: chain-rule conditionals realize a finite joint distribution (KF-13), or categorical enumeration provides a finite upper bound. This does not select autoregression over diffusion, flows, latent or adversarial generators.
4. [O] Variables: conditional entropy structure, multimodality, dimension, smoothness, precision, sample latency and likelihood/conditioning requirements.
5. [P] Law: count actual sequential conditionals, transformation/denoising steps and random bits; equal quality must be distributionally measured.
6. [O] Parents: autoregressive, diffusion/score, flow, latent-variable, adversarial and exact finite samplers under matched training/data budgets.
7. [O] Twin: independent or simply transformable coordinates; alternatively hard multimodal conditional dependencies.
8. [O] Descriptor: development-only factorization and score/transport regularity probes with charged extraction; protected density unavailable to the predictor.
9. [O] Crossover: GKF-10 remains open; a universal representation or a denoising identity is not a zero-prior family selector.
10. [O] F21/C4: finite joint laws on up to 256 states with conditionally independent, low-rank and entangled factors; random bits plus primitive transitions, no sampler-family macro.
11. [O] F21/C5: hold out a factorization class; require KL<=0.01 nats where exact reference probabilities exist, plus the common cost tests.
12. [O] F21/C6: pin small real density/conditional-generation tasks with agreed likelihood and quality metrics before running.
13. [O] Kill: cheaper matched-distribution parent dominates, mode coverage fails, or sample-quality metrics replace the registered obligation post hoc.

## F22 — test-time search and reasoning allocation

1. [P] State: unresolved candidate alternatives, verifier evidence and reusable intermediate results sufficient for the current query; natural-language scratchpad is not a necessary representation.
2. [P] Lower: the oracle-search bound in F07 applies only without exploitable structure; correlated candidates can defeat independent-sampling predictions.
3. [P] Construction: repeated generation/checking or bounded frontier search; exact checker semantics are separately required.
4. [O] Variables: branching, depth, candidate dependence, success probability, verifier power, deadline and train-time alternative cost.
5. [P] Law: independent candidate success probability is `1-(1-p)^n`; the independence and stable-p assumptions are indispensable. Charge every branch and check.
6. [O] Parents: more train-time development, compiled solution, memoization, exact solver, retrieval and single-pass prediction.
7. [O] Twin: perfectly correlated candidate errors or reusable queries that amortize compilation.
8. [O] Descriptor: development-only candidate hazard/correlation and verifier calibration, not observed protected success curves.
9. [O] Crossover: incremental checked success must exceed inference price and the best train-time/reuse alternative; GKF-13 open.
10. [O] F22/C4: finite candidate spaces with independent/shared-latent errors and depth 1..4; explicit branching and checking.
11. [O] F22/C5: hold out a dependence/heuristic error mechanism.
12. [O] F22/C6: pin untouched code/math problems with exact solution verification and deadlines.
13. [O] Kill: independent-sampling law fails on the registered dependent scope, protected budgets are retuned or uncounted branches buy the gain.

## F23 — model-based control

1. [P] State: transition/reward or belief information sufficient for registered counterfactual decisions under the known Markov/partial-observation contract.
2. [P] Lower: models inducing different optimal decisions for admitted goals must be distinguished; mere one-goal trajectory prediction need not identify all counterfactuals.
3. [P] Construction: finite dynamic programming/planning with an exact known transition law; approximate learned models require explicit error propagation and exploration assumptions.
4. [O] Variables: model error, goal variation, horizon, observability, exploration, dynamics drift and reuse.
5. [P] Law: model acquisition/update plus planning and execution; KF-20 only compares matched-quality planning and compiled policies.
6. [O] Parents: direct policy/value learning, exact control, cached planning, robust control and hybrid residual models.
7. [O] Twin: stable one-goal high reuse, or biased model whose planning error outweighs reuse value.
8. [O] Descriptor: development-only intervention coverage and calibrated transition/reward uncertainty; off-policy gaps explicit.
9. [O] Crossover: model-error versus planning-value and exploration burden remains GKF-11, not settled by amortization.
10. [O] F23/C4: tabular MDPs with 2..8 states and 2..4 actions, goal/dynamics interventions and incomplete observations; primitive transition simulation only.
11. [O] F23/C5: exclude a dynamics/goal-shift family and an observation alias mechanism.
12. [O] F23/C6: pin safe simulated-control episodes with logged actions, rewards, resets and risk limits.
13. [O] Kill: model error breaks matched quality, unavailable counterfactual data are assumed or exploration/reset costs disappear.

## F24 — model-free policy and value control

1. [P] State: action/value distinctions sufficient for the fixed decision objective; a direct policy need not reconstruct every environmental transition.
2. [P] Lower: if all |A|^|S| deterministic policies are admitted and queried on separating states, exact policy storage needs ceil(|S| log2 |A|) bits; structured policy classes can compress.
3. [P] Construction: direct table or coefficient/program policy plus legal feedback-based development; sample-efficient learning is not supplied by representability.
4. [O] Variables: policy complexity, reward/feedback coverage, horizon, exploration, goal stability and reuse.
5. [P] Law: development plus cheap repeated policy serving; charge all exploration, failed trajectories and shift-induced relearning.
6. [O] Parents: model-based planner, exact controller, policy compilation/distillation, tabular and shared feature/value implementations.
7. [O] Twin: frequent goal/dynamics changes or inadequate action feedback where a reusable accurate model has value.
8. [O] Descriptor: development-only policy sensitivity and coverage estimates, not protected return or hindsight fitted value residual.
9. [O] Crossover: KF-20/RC-08 supplies only the matched-quality accounting boundary; policy learning burden and transfer remain open.
10. [O] F24/C4: same finite control worlds and information prices as F23; primitive state-to-action computation without policy/value macros.
11. [O] F24/C5: hold out reward-shaping, exploration or transition structure, not just trajectories.
12. [O] F24/C6: the same pinned safe-control workloads as F23 with equal reset/action budgets.
13. [O] Kill: direct policy misses risk/quality, exploitation of uncharged feedback or a matched planner dominates the frozen crossover.

## Terminal discipline and next discrimination

Every family above has a named sufficient-state question, bound, construction, native variables, resource law, strong-parent set, negative twin, descriptor, crossover, neutral trial, held-family trial, real-transfer entry and kill rule. That is registration, not achievement. C1-C6 and all family [O] rows remain blockers. The new finite evidence applies to subcases of F08/F11/F12, not to all known architectures or learning mechanisms.

The highest-value next experiment is a cost-complete, family-held crossover tournament on early/late query timing, reusable-law versus independent-record structure, update locality and retention/lineage. Before protected generation, require GMI to issue numeric predictions that differ from a predeclared ordinary description-length/cost-model predictor; otherwise the trial cannot distinguish the explanations. The generic synthesis parent receives identical primitives and legal data. Primary pilot endpoint: mean normalized cost regret under matched exact semantics/risk, with a predeclared 0.10 practical improvement target and a task-clustered 95% confidence interval excluding zero for the paired improvement. A wide interval is inconclusive, not confirmation. The estimator and independently authored protected generator are missing entry artifacts; they are explicit blocking gaps, not completed work.

Both programme-wide requested terminal strings remain FALSE. Strong unknown-species claims remain gated; ordinary classical realizations remain in one H4 super-domain unless the separate H0-H3 resource-separation programme succeeds.
