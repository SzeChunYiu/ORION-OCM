# GMI theory map — corrected TM-1–8

**Synthesis ledger; NO NOVELTY CLAIM.** Parent results keep their original
hypotheses. The links below identify what has been derived, rather than
treating a choice of objective or representation as a discovery.
Primary sources P1–P8 are mapped in [the parent register](PARENT_MECHANISMS_V1.md).

## TM-1. Bayesian inference

**Inherited:** conditional probability, finite Bayesian filtering and
loss-plus-relative-entropy updating (P1).
**GMI instance:** [formal O3](../gmi-formal-derivation-v1/OPTIMIZATION.md)
derives Bayes' rule from log likelihood plus KL; [REAL3](../gmi-formal-derivation-v1/REALIZATIONS.md)
derives the supplied-model belief update.
**Premises:** declared prior, likelihood/observation law, available information
and nonzero normalizer. Zero-probability observations need a separate convention.
The master's ecology class need not carry a probability prior; that does not
make every admitted GMI construction prior-free. Robust and Bayesian criteria
are different declared decision problems.
**Not established:** correct priors/models from the core, cheap belief storage,
or superiority to Bayesian decision theory.

## TM-2. Information theory

**Inherited:** zero-error distinguishability, channel simulation and explicit
assistance classes (P2), alongside ordinary probabilistic information theory.
**GMI instance:** [semantic cuts](../gmi-grand-unification-v1/SEMANTIC_CUT_THEOREM_V1.md)
use adequate-message covers; [approximate geometry](../gmi-grand-unification-v1/APPROXIMATE_SEMANTIC_GEOMETRY_THEOREM_V1.md)
and probabilistic acquisition admit error/probability contracts.
**Premises:** fixed observation/decoder interface, task obligations, error
criterion and declared classical/quantum/shared-resource access.
A positive mutual information does not imply exact one-shot identification;
this is an inherited zero-error boundary, not a rejection of entropy.
[Finite quantum cover](../gmi-finite-quantum-cover-v1/CORE.md) keeps its specific
unassisted dimension/message comparison. It is not a total physical-cost result.
**Not established:** a new Shannon capacity theorem or a universal
classical/quantum ordering.

## TM-3. Statistical learning and online prediction

**Inherited:** bounded-loss concentration, simultaneous model selection,
Occam/PAC reasoning and expert-advice regret (P3).
**GMI instance:** [L1–L4](../gmi-formal-derivation-v1/LEARNING.md)
derive finite/countable risk bounds, conditional consistency and Hedge;
[repaired LMT](../gmi-recursive-theory-closure-v1/FORMAL_LEARNING_MEMORY_THEORY_V1.md)
keeps fixed-class and complete-view premises.
**Premises:** fixed evaluation loss and model universe for the IID theorem,
pre-data masses, supplied costs, and appropriate feedback for online regret.
Time-uniform coverage licenses a later member/sample-size choice within that
universe; it does not license arbitrary class selection on the same sample.
[Adaptive inference](../gmi-formal-derivation-v1/ADAPTIVE.md) supplies different
conditional-law premises for adaptive queries and births.
**Not established:** universal risk improvement, class-free learning,
or statistical consistency paying for acquisition automatically.

## TM-4. Description length and PAC-Bayes

**Inherited:** countable weighted union bounds and prefix-code penalties;
PAC-Bayes additionally controls distributions over hypotheses (P4).
**GMI instance:** L2 already proves, simultaneously for all admitted h and n,
a radius containing log(1/p_h). Prefix-free lengths permit p_h=2^-L(h).
Thus the original “only informal / no specialization” description is stale.
**Premises:** fixed countable measurable executables, masses chosen before
evaluation data with sum at most one, and IID bounded losses.
**Boundary:** this particular proof is a code-weighted Occam/PAC certificate.
It does not supply the general data-selected-posterior KL(Q||P) guarantee
of Seeger's theorem or a theorem optimizing an MDL objective.
A PAC-Bayes prior is not required to equal the world's data-generating law.
**Not established:** shortest program implies cheapest execution, computable
universal model search, or empirical superiority of a compression selector.

## TM-5. Reinforcement learning and stochastic control

**Inherited:** Bellman decomposition, belief-state control, simulation bounds
and proper-policy distinctions (P5).
**GMI instances:** [PCA](../gmi-grand-unification-v1/PROBABILISTIC_CONTROLLED_ACQUISITION_THEOREM_V1.md)
and [UMA](../gmi-grand-unification-v1/FIXED_UNKNOWN_MODEL_ACQUISITION_THEOREM_V1.md)
solve declared finite policy problems. [FMT](../gmi-grand-unification-v1/FINITE_DATA_MODEL_TRANSFER_THEOREM_V1.md)
combines row confidence and policy transfer. [CMP5](../gmi-formal-derivation-v1/COMPOSITION.md)
also supplies conditional infinite-path and discounted-value bounds.
**Premises:** sufficient common state/history, specified known or covered model
class, policy interface, objective and resource semantics. Expected, robust,
pathwise and discounted guarantees are distinct. Fixed unknown models are not
automatically equivalent to an adversary changing models each step.
Vector constraints and charged computation are supported formulations, not
properties unavailable to classical control or metareasoning.
**Not established:** unrestricted online/physical control, learned support,
or sure safety from a small uniform one-step model error.

## TM-6. Causal inference

**Inherited:** SCMs, interventions, model-class identification, graphical
adjustment and the identification/estimation distinction (P6).
**GMI instance:** [corrected CAU-1–4](../gmi-causal-identifiability-v1/CAUSAL_IDENTIFIABILITY_BOUNDARY_THEOREM_V1.md)
uses compatible-model fibers, complete-view indistinguishability, supported
back-door adjustment and surgical randomization.
**Premises:** declared compatible model class and observation/intervention
interface; graph-based claims retain their causal, support and faithfulness
conditions where required. A target is identified when constant on the
nonempty observational fiber, even if the whole model is not identified.
An already identifying premise need not be purchased by a new experiment.
Charge the acquisition and computation actually used; money cannot discharge
an unavailable intervention or an unwarranted causal premise.
**Not established:** exact finite-sample causal recovery, arbitrary graph
discovery, or attribution of an empirical campaign's failures.

## TM-7. Active learning, experimental design and metareasoning

**Inherited:** decision-region determination and nonmyopic value of
information/computation (P7). Those parents already model task-directed tests
and the cost of computation.
**GMI instance:** [TDA](../gmi-grand-unification-v1/TASK_DIRECTED_ACQUISITION_THEOREM_V1.md)
allows a common adequate output instead of demanding full identification.
[Corrected VOC](../gmi-value-of-computation-v1/VALUE_OF_COMPUTATION_THEOREM_V1.md)
gives finite deterministic serving-policy and stopping results.
**Premises:** TDA's fixed-world test register differs from state-changing
control. The two constructive selectors in that VOC version use a
decreasing rank or positive cognitive prices on the viable domain. At a viable state, with immediate cost A and charged
continuation Q, Q<A forces continuation, A<Q forces stopping, and
A=Q<infinity allows both. If both values are infinite, report infeasibility.
“Continue iff Q<A” uses the declared stop-on-ties selector.
**Not established:** nonmyopic optimization from a myopic score, a deterministic
path-length bound for stochastic trials, or free synthesis/probing apparatus.

## TM-8. Neural and non-neural computation

**Inherited:** approximation and finite machine realization (P8).
**GMI instance:** [REAL1–2](../gmi-formal-derivation-v1/REALIZATIONS.md)
construct symbolic and neural finite realizations;
[O1–O4](../gmi-formal-derivation-v1/OPTIMIZATION.md) derive known optimizer and
reverse-mode mechanisms only after adding geometry/differentiability premises.
[ARCH1–5](../gmi-formal-derivation-v1/ARCHITECTURE.md) separates realizability,
attainment and selection. These constructions do not change OCM's
non-neural cognition policy; neural realizations are mathematical comparators.
**Premises:** exact finite encodings or the chosen approximation theorem's
domain/activation assumptions; precision, storage, synthesis and execution
must be accounted for separately.
**Not established:** that representability selects a family, uniquely derives
Transformer syntax, or supplies measured neural/non-neural superiority.

## Selection and the remaining work

`REPRESENTABLE` and `SELECTED` are distinct.
A static comparison needs an admitted feasible class and a resource/objective
order. Global optimality needs warranted comparator coverage and attainment
(or an explicitly approximate claim); it need not enumerate every program.
A developmental claim additionally restricts candidates by reachability.
See [MSC](../gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md).

This map adds no empirical evidence. Remaining work concerns the supplied
state/support and causal contracts, effective acquisition/synthesis, complete
relevant costs and matched held-out transfer. A finite witness or inherited
proof must not be relabeled general intelligence.
