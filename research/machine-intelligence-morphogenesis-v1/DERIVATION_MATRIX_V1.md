# Known-Morphology Derivation Matrix v1

This is a work map, not evidence that any candidate basis is general.

A derivation must preserve **developmental semantics**, not only current computation, and must not invoke an opaque primitive equivalent to the target architecture.

| Target morphology | Parent object that gets first refusal | B0 local transducers | B1 compositional learner | B2 rewritable program graph | B3 stochastic generative kernel | Decisive unresolved question |
|---|---|---|---|---|---|---|
| finite-state / automata | automata/state machines | natural | possible | natural | degenerate deterministic case | can state/update compile with bounded overhead? |
| feedforward/recurrent neural | neural nets; categorical DL; Backprop-as-Functor | natural if weighted aggregation/nonlinearity compile from low primitives | strongest natural parent | possible but risk of interpreter emulation | possible but risks treating weights as generic latent variables | can NN + learning law be derived without a `NEURON`/gradient macro and with competitive bounded overhead? |
| production / symbolic rule | Soar/production systems/rewrite systems | possible via local match/fire dynamics | possible but may require discrete non-differentiable update | strongest natural parent | possible but likely unnatural | can condition/action matching and chunk/rule update arise from same low primitives? |
| programmatic / synthesis | lambda/program machines, GP, DreamCoder, Stitch, CEGIS | possible but likely interpreter-heavy | possible through parameterized programs but risks black-box maps | strongest natural parent | Church-like stochastic-program route | does a neutral basis explain program/library structure rather than merely simulate an interpreter? |
| probabilistic / Bayesian | Church, Bayesian inference, BPL | possible with explicit stochastic transition or pseudo-random construction | possible with probabilistic learners | possible if random choice/inference compiles | strongest natural parent | is stochasticity fundamental at bounded cost or a derived morphology? |
| learned optimizer / meta-learner | MAML, learned optimizers, meta-RL | natural as update dynamics | strongest natural parent | programmatic optimizer possible | probabilistic/meta-inference possible | which basis makes update-law learning simplest without baking optimizer semantics in? |
| self-organising/developmental | NCA, HyperNEAT, developmental systems | strongest natural parent | possible | graph grammar/program development | stochastic generative development | can global morphology emerge from local rules with a predictive ecology law? |
| OCM-like explicit epistemic | #93/#145/current OCM | possible explicit units/relations | possible as composed learners but likely awkward | strong candidate via typed program/state graph | possible but explicit warrant may be expensive | are warrant/provenance/revision structures ecology-selected morphology features rather than fundamental atoms? |
| hybrid statistical + exact | neuro-symbolic, tool agents, mixed systems | natural heterogeneous graph | natural composition if semantics rich enough | explicit donor/module composition | probabilistic programs + deterministic modules | is hybrid genuinely non-equivalent to parent product after full cost accounting? |

## What counts as success per row

### D0

Target computation is expressible. This is almost scientifically worthless by itself.

### D1

A compiler is explicit, semantics-preserving at registered scope, and bounded on description/execution/update resources.

### D2

The target-specific architecture macro is removed; search/development from a neutral grammar recovers the morphology under frozen budget.

### D3

Before search, ecology/resource/verification conditions predict the morphology class/frontier and the result reproduces on disjoint ecologies.

## Required parent attacks

- **Neural expert:** show B0/B1 simply restate known neural/categorical machinery.
- **Programming-languages expert:** show B2 is just a universal interpreter and therefore not explanatory.
- **Probabilistic-programming expert:** show B3 already follows from Church/universal stochastic programs.
- **Cognitive-architecture expert:** show symbolic/OCM derivations are merely productions/blackboards under new names.
- **Learning-theory expert:** show any claimed learnability phase law is already a standard sample-complexity/inductive-bias result.

Track B only earns a residual after those reductions are attempted.