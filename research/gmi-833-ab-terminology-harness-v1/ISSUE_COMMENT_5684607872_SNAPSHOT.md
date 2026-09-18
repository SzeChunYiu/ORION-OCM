## Addendum — recursive loophole closure + academic terminology normalization

This is a **mandatory cross-cutting gate** for the entire programme. A section is not scientifically closed merely because its current boxes are green. Every result must recursively generate and discharge its own unresolved assumptions, counterexamples, parent reductions, terminology mismatches, and stronger falsification tests until the declared claim has no known material loophole at its stated scope.

### AA. Recursive loophole / logic-gap closure

- [ ] Define a machine-readable `OPEN_GAP` object: claim, premise, inference, unresolved assumption, possible counterexample, severity, owner, parent result, evidence needed.
- [ ] Require every theorem/proof/experiment to emit an explicit assumptions ledger.
- [ ] Require every theorem to emit a dependency ledger.
- [ ] Require every theorem to emit a falsifier/counterexample ledger.
- [ ] Require every theorem to emit a strongest-parent/subsumption ledger.
- [ ] Require every experiment to emit leakage, search-space, cost-model, evaluation and sampling-bias ledgers.
- [ ] For every closed gap, automatically ask what new assumptions/gaps were introduced by the repair.
- [ ] Recurse until no new **material** gap is found under the declared scope.
- [ ] Define materiality thresholds so recursion does not terminate by arbitrary convenience.
- [ ] Require independent hostile review before a gap can be marked exhausted.
- [ ] Require at least two distinct counterexample-generation methods for flagship theorems.
- [ ] Add bounded exhaustive counterexample search whenever the finite domain permits it.
- [ ] Add SMT/SAT/model-checking counterexample search where appropriate.
- [ ] Add property-based/randomized adversarial testing where exact enumeration is impossible.
- [ ] Add proof-assistant/formal-verification targets for the flagship mathematical spine where practical.
- [ ] Search for quantifier-order mistakes (`forall/exists` swaps).
- [ ] Search for converse/inverse fallacies.
- [ ] Search for necessity-vs-sufficiency confusion.
- [ ] Search for representability-vs-reachability confusion.
- [ ] Search for optimality-vs-selection confusion.
- [ ] Search for finite-scope-to-universal extrapolation.
- [ ] Search for empirical-correlation-to-causal claims.
- [ ] Search for identifiability failures.
- [ ] Search for hidden dependence/independence assumptions.
- [ ] Search for hidden stationarity/ergodicity assumptions.
- [ ] Search for hidden bounded-horizon assumptions.
- [ ] Search for hidden compactness/finiteness assumptions.
- [ ] Search for encoding-dependent conclusions.
- [ ] Search for arbitrary unit/scalarization dependence.
- [ ] Search for search-algorithm-induced morphology artifacts.
- [ ] Search for grammar-induced morphology artifacts.
- [ ] Search for benchmark/ecology selection bias.
- [ ] Search for post-selection inference / multiple-testing problems.
- [ ] Search for data leakage/remint leakage.
- [ ] Search for underpowered negative results.
- [ ] Search for non-identifiable latent explanations.
- [ ] Search for alternative known-parent reductions after every new-form claim.
- [ ] Maintain a live `GMI_GAP_GRAPH` linking every claim to unresolved descendants.
- [ ] Define `LOCALLY_CLOSED`, `HOSTILE_CLOSED`, `REPLICATED_CLOSED`, and `REAL_SCALE_CLOSED`; never use bare `closed` scientifically.
- [ ] Prevent parent issue closure while any critical descendant gap remains unresolved.
- [ ] Run a final recursive hostile sweep before any flagship manuscript freeze.

### AB. Academic terminology and ontology normalization

Terminology must follow established literature where an established term accurately matches the object. New GMI terms are allowed only when existing terminology is demonstrably insufficient, and every new term requires a parent-term comparison and operational definition.

- [ ] Build a living `GMI_TERMINOLOGY_CROSSWALK` with: legacy GMI term, proposed paper term, academic field, canonical term(s), exact match/partial match/non-match, citations, definition, migration rule.
- [ ] Replace paper-facing `obligation` with `task`, `specification`, or `formal/behavioral specification` according to exact semantics; formal methods uses **formal specification** for a mathematical description of intended system behavior.
- [ ] Audit `morphology`; compare against **architecture**, **computational architecture**, **model class**, **representation**, **algorithm**, and **computational mechanism**. Keep `morphology` only where structure across heterogeneous computational organizations is genuinely intended.
- [ ] Audit `machine species`; compare against **algorithm/configuration class**, **model family**, **architecture family**, **behavioral phenotype**, and **equivalence class**. Treat biological language as analogy unless formally defined.
- [ ] Audit `ecology`; compare against **task distribution**, **environment**, **problem distribution**, **instance space**, and **operating regime**.
- [ ] Audit `niche`; compare against **region of instance space**, **operating regime**, **performance region**, and **domain of competence**.
- [ ] Audit `selection`; distinguish **algorithm selection**, **model selection**, **architecture search**, **hyperparameter/configuration selection**, and evolutionary selection.
- [ ] Explicitly parent-subtract Rice-style **algorithm selection**: problem space, feature space, algorithm space, performance space, selection mapping.
- [ ] Audit `phase law/phase diagram`; use only when there is a well-defined control-parameter space and qualitative regime transition; otherwise use regime map/crossover map.
- [ ] Audit `prior-free`; replace with **architecture-agnostic**, **architecture-uncommitted**, **family-agnostic search**, or explicit `architecture-prior-free` only after defining what priors remain.
- [ ] Use **inductive bias** for representational/search preferences when that is the established ML concept.
- [ ] Use **hypothesis class/search space/program space** rather than vague `possibility space` where appropriate.
- [ ] For synthesis, use **DSL / grammar / primitive set / search space / search strategy** where those are the actual objects; explicitly acknowledge that the DSL itself induces strong bias.
- [ ] Audit `neutral search`; replace with a precise description such as family-blind enumerative search, architecture-agnostic search, grammar-based synthesis, evolutionary search, etc.
- [ ] Audit `remint`; paper-facing alternatives should normally be **independent regeneration**, **re-randomization**, **relabeling control**, **fresh-instance replication**, or **independent replication**, depending on what was done.
- [ ] Audit `negative twin`; compare with **matched negative control**, **counterfactual control**, **ablation**, **placebo condition**, or **negative control**.
- [ ] Audit `parent subtraction`; paper-facing terminology should normally be **comparison to strongest baselines/parent theories**, **subsumption analysis**, **reduction**, **ablation**, or **novelty analysis**.
- [ ] Audit `carrier`; map where possible to **state representation**, **state space**, **memory substrate**, **computational substrate**, or **representation space**.
- [ ] Audit `quotient`; retain mathematical quotient where exact; otherwise use **equivalence classes**, **state abstraction**, **minimal sufficient representation/state**.
- [ ] Audit `capability ceiling`; compare with **upper bound**, **impossibility result**, **capacity bound**, **information-theoretic limit**, **sample/communication/complexity bound**.
- [ ] Audit `development`; distinguish **online learning**, **continual learning**, **meta-learning**, **self-modification**, **architecture adaptation**, **developmental learning**, and **evolution**.
- [ ] Audit `evolvability`; use the established evolutionary-computation/ALife meaning and avoid using it as a synonym for ordinary adaptability.
- [ ] Audit `open-ended`; connect explicitly to **open-ended evolution/open-endedness** literature; do not use it merely to mean a large search space.
- [ ] Audit `novel intelligence`; distinguish **novel implementation**, **novel architecture**, **novel algorithmic mechanism**, **novel model class**, **novel computational paradigm/domain**, and **novel capability profile**.
- [ ] Define a novelty ladder using those academically interpretable levels.
- [ ] Audit `unseen form`; paper-facing term should specify whether this means held-out architecture, predicted morphology, novel mechanism, or new computational class.
- [ ] Audit `cognition` terms against cognitive science rather than ML metaphors: working/episodic/semantic/procedural memory, attention, metacognition, theory of mind, etc.
- [ ] Require cognitive terms to satisfy operational criteria before claiming correspondence to human/animal constructs.
- [ ] Audit `causal` terminology against SCM/intervention/counterfactual conventions.
- [ ] Audit uncertainty terminology against aleatoric/epistemic, confidence set, credible set, calibration, identifiability, and partial identification conventions.
- [ ] Audit `verification`; distinguish formal verification, empirical validation, evaluation, testing, certification, and verifier feedback.
- [ ] Audit `proof`; never call exhaustive finite computation a mathematical proof without stating the certificate/computer-assisted status precisely.
- [ ] Audit `derive`; reserve it for a conclusion logically/mathematically obtained from stated premises; otherwise use recover, select, fit, construct, reproduce, or explain.
- [ ] Audit `predict`; require temporal/epistemic separation from the outcome; otherwise use post-hoc explanation or reconstruction.
- [ ] Audit `discover`; require that the target was not encoded/named/privileged and that novelty survives parent reduction.
- [ ] Create a banned/avoid list of internally convenient but academically misleading terms for manuscripts.
- [ ] Require terminology review as a CI/checklist gate for flagship documents.

### AC. Literature saturation / terminology authority

- [ ] Create expert literature lanes: theoretical CS/formal languages; statistical learning/information theory; optimization/algorithm selection; program synthesis; neural architectures; RL/control; Bayesian/causal inference; evolutionary computation/ALife; cognitive science/neuroscience; formal methods; philosophy of science.
- [ ] For every core GMI construct, collect canonical and modern parent literature before naming it.
- [ ] Prefer canonical field terminology when definitions coincide.
- [ ] When terminology differs across fields, state the cross-field synonyms and choose one primary paper term.
- [ ] Maintain citation-backed definitions rather than model-generated definitions.
- [ ] Record earliest/strongest known parent for each mathematical idea.
- [ ] Record whether GMI contribution is theorem, synthesis, generalization, new selection law, new empirical result, or only terminology.
- [ ] Require a `WHAT_IS_ACTUALLY_NEW.md` table that survives all literature lanes.
- [ ] Re-run literature search before manuscript freeze because terminology and neighboring work can change.

### AD. Recursive research loop

Every major claim must execute this loop:

```text
claim -> formalize -> parent-search -> derive -> counterexample-search ->
repair/downgrade -> architecture-prior audit -> independent implementation ->
frozen prediction -> replication -> real-scale test -> new-gap extraction -> repeat
```

- [ ] Implement the loop as a standard research template.
- [ ] Require each iteration to create explicit new-gap records rather than silently editing assumptions.
- [ ] Stop only at the declared evidence ceiling, never because the checklist is long.
- [ ] If a result fails, preserve the failure as evidence and update the theory.
- [ ] If a parent theory subsumes the result, absorb the parent terminology/mathematics and move the novelty claim upward.
- [ ] If multiple theories predict the same outcome, design a discriminating experiment.
- [ ] If no discriminating experiment is identifiable, mark the theories observationally indistinguishable at that scope.
- [ ] Require flagship claims to survive at least one independent hostile team/lane that did not author the original result.

### Terminology anchors found in the current literature review

- Formal methods: **formal specification** = precise mathematical description of intended system behavior; verification asks whether an implementation satisfies it.
- Algorithm selection: Rice's framework uses **problem space, feature space, algorithm space, performance space**, and a selection mapping; GMI morphology selection must explicitly distinguish itself from this parent problem.
- Program synthesis: **DSL/grammar, primitive set, search space, search strategy** are standard terms, and DSL choice itself determines expressiveness and strongly biases search/generalization.
- Open-ended search/evolution: **open-ended evolution, novelty search, quality diversity, evolvability** already have established meanings; GMI must use them consistently rather than metaphorically.

This addendum is a closure gate for #833, not optional editorial cleanup.
