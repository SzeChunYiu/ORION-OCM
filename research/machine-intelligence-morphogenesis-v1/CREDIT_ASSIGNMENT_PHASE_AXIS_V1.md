# Credit-assignment structure as a morphology phase axis v1

Status: **parent-derived candidate phase coordinate**, not an ORION novelty claim.

## Motivation

Different machine-intelligence morphologies often differ less in whether they can represent a solution than in **how experience assigns responsibility for error/success to internal changeable structure**.

This suggests that Track B should distinguish:

```text
representation morphology
credit-assignment morphology
update morphology
```

rather than identifying, for example, `neural = gradient` or `symbolic = no gradient`.

Parent literature already makes credit assignment a major learning problem; information-theoretic work emphasizes **information sparsity** rather than reward sparsity alone, and categorical learner/lens work formalizes backward/request channels compositionally.

---

# 1. Generic credit object

For mutable internal components `z_1 ... z_n`, experience/outcome `e`, and global evaluation signal `y`, define a credit process provisionally as

```text
C_i = Credit(z_i, trajectory, y, context)
```

where `C_i` is the information available to update component `i`.

Do not assume `C_i` is numeric. It may be:

```text
gradient / derivative
TD error / advantage
posterior likelihood contribution
counterexample / unsat core / violated constraint
causal responsibility estimate
fitness / selection survival
local control error
failure receipt / rejected obligation
human correction
```

The update then has the abstract shape:

```text
z_i' = U_i(z_i, C_i, local_context)
```

This decomposition is parent-owned in many forms. Track B uses it only to define ecology/morphology coordinates.

---

# 2. Candidate measurable coordinates

## CA-1 — credit bandwidth

How much update-relevant information reaches mutable structure per evaluation event?

Possible operationalizations:

```text
bits / nats of outcome information about local responsibility
rank/dimension of usable update signal
number/fraction of mutable components receiving nontrivial credit
```

Do not treat raw gradient dimensionality as information content without further analysis.

## CA-2 — credit locality

How local is the information required for a correct/useful update?

```text
local state only
neighborhood
module/global graph
global trajectory
counterfactual reruns
```

## CA-3 — credit delay

Distance between causative choice and usable feedback.

## CA-4 — credit dilution / information sparsity

How difficult is it to distinguish causative changes from irrelevant trajectory components?

This is directly threatened/parented by temporal-credit-assignment and information-theoretic credit literature.

## CA-5 — credit decomposability

Can a global objective/evidence signal be transformed into compatible local requests/updates for composed subsystems?

Learners/lenses/backprop are a strong parent here.

## CA-6 — credit identifiability

Can alternative internal causes be distinguished from available interventions/feedback?

## CA-7 — credit verification strength

Does the feedback merely score behavior, or identify an exact violated obligation/counterexample/proof failure?

---

# 3. Morphology examples

These are explanatory mappings, not novelty claims.

## Gradient/differentiable neural systems

```text
credit form: derivative / adjoint
potential bandwidth: high-dimensional
locality: computationally global but efficiently decomposed by chain rule/backprop
strength: highly informative when objective/model are differentiable and gradients useful
failure regimes: vanishing/exploding/poor gradients, long-horizon temporal credit, non-differentiable evaluators, distribution shift
```

## Bayesian / probabilistic systems

```text
credit form: likelihood / posterior change / message
locality: factorization-dependent
strength: explicit uncertainty/evidence semantics
cost: exact inference can be hard; approximations introduce their own regime
```

## Symbolic / formal systems

```text
credit form: failed constraint, counterexample, proof obligation, unsat core
locality: may be sharply structured but sparse/discrete
strength: exact semantic information where verifier exposes it
cost: search/abduction required to turn failure into useful repair
```

## Evolutionary / black-box search

```text
credit form: individual/population fitness and selection
locality: weak per internal component unless additional structure is supplied
strength: minimal differentiability/model assumptions
cost: potentially large sample/evaluation burden
```

## OCM-like explicit governed development

```text
credit form: typed success/failure receipts, provenance/dependency, controlled interventions
locality: potentially explicit/causal when instrumentation is complete
risk: diagnosis/search overhead can dominate; current ORION evidence does not establish universal superiority
```

---

# 4. Candidate phase hypotheses

These are **not confirmatory claims**.

### H-CA-N

When feedback admits cheap, dense, decomposable derivative-like credit across many reusable parameters, differentiable parametric morphologies should occupy a large efficient region.

### H-CA-S

When feedback is sparse but exact/structured (counterexamples, proof obligations, tests), explicit symbolic/programmatic search/repair may become more competitive, especially when local causal responsibility can be identified without dense gradient information.

### H-CA-P

When uncertainty itself is central and observations have explicit likelihood structure, probabilistic/factorized morphologies may gain an advantage if inference cost remains bounded.

### H-CA-E

When only black-box terminal evaluation is available, morphology search/evolution may be necessary but evaluation cost becomes a dominant phase variable.

### H-CA-H

Mixed ecologies may favor hybrid morphologies that transform one credit regime into another—for example learned parametric proposals followed by exact verifier feedback and explicit repair.

---

# 5. Strong parents / anti-novelty boundary

At minimum consume:

- temporal credit-assignment literature in RL;
- information-theoretic credit assignment (information sparsity);
- backprop / automatic differentiation;
- alternative neural credit-assignment schemes;
- causal responsibility / counterfactual attribution;
- CEGIS/CEGAR/unsat-core/counterexample-guided repair;
- evolutionary credit/fitness shaping;
- categorical learners/lenses/request maps.

Track B receives **no novelty credit** for identifying credit assignment as important.

The candidate Track-B residual is only:

```text
Does a measurable credit-structure coordinate improve prospective prediction of
which intelligence morphology lies on the developmental Pareto frontier?
```

---

# 6. Prospective test

For a future finite phase microscope:

1. construct matched task families with the same solution class but systematically vary feedback informativeness/decomposability;
2. hold information content and evaluation budget as tightly matched as possible;
3. compare tiny differentiable/parametric, symbolic-repair, probabilistic and black-box/evolutionary parents;
4. freeze frontier-transition predictions before protected variants;
5. measure whether `credit bandwidth/locality/identifiability` predicts frontier membership beyond generic task labels.

Negative terminal:

```text
CREDIT_STRUCTURE_ADDS_NO_PREDICTIVE_MORPHOLOGY_INFORMATION
```

Positive scoped terminal:

```text
CREDIT_STRUCTURE_PREDICTS_MORPHOLOGY_FRONTIER_AT_REGISTERED_SCOPE
```

Neither terminal establishes a universal intelligence law by itself.
