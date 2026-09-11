# Generative Machine Intelligence — core hypothesis v1

Status: **current best synthesis after parent subtraction; falsifiable, non-final**.

## 1. What the theory should explain

A useful general theory of machine intelligence should explain at least:

1. why multiple machine-intelligence morphologies exist;
2. how those morphologies can arise from a lower-level adaptive generative substrate;
3. why different ecologies/resource regimes favor different morphologies;
4. how experience changes both a morphology and the process that generates future morphologies;
5. when accumulated structure makes later cognition/development cheaper;
6. whether the theory predicts a morphology not already supplied by human architecture labels.

It should not merely provide another universal programming language.

## 2. Current formal scaffold

The live substrate object is not one named atom but an equivalence class of adaptive generating bases:

\[
\mathfrak B=[B]_{E,R,V,\mathcal K}.
\]

A complete morphology is

\[
M=(G,X,\Theta,\Pi,\mathcal L,\mathcal K_{io}),
\]

with structure/topology `G`, state `X`, mutable configuration `Theta`, control `Pi`, learning/update law `L`, and external interface.

An ecology is

\[
E=(\mathcal T,O,A,F,V,R,H,D),
\]

covering task distribution, observations/actions, feedback, verifier, resources, horizon and drift/changes.

## 3. Two different developmental processes

### Morphogenesis

\[
\Gamma(\mathfrak B,E,H_{dev}) \to \mathcal P(\mathcal M)
\]

or more conservatively a Pareto frontier over morphology equivalence classes.

`Gamma` may be implemented by evolution, synthesis, optimization, learning, human engineering, or another search process. The scientific object is the induced developmental distribution/frontier, not the implementation name.

### Within-form development

\[
M_{t+1}=U(M_t,e_t).
\]

A neural network updated by gradient descent, a production system learning a rule, a probabilistic model conditioning on evidence, or a program learner adding a library abstraction are different specializations of `U`.

## 4. Intelligence-form identity

A morphology class is not source syntax. It is a bounded developmental equivalence class.

Two systems may be grouped when a registered compiler preserves:

```text
current verified capability
developmental response to experience
retention/plasticity behavior
resource vector within bounds
revision/drift behavior
```

Conversely, identical current outputs do not imply the same morphology.

## 5. The central predictive object

For morphology class `M` and ecology `E`, define a developmental feasible set over capability and complete resources:

\[
\mathcal A_M(E)=\{(Q,\mathbf B): \text{reachable under registered development}\}.
\]

Its nondominated boundary is the developmental frontier:

\[
\mathcal F_M(E)=\operatorname{Pareto}(\mathcal A_M(E)).
\]

A morphology phase transition occurs when changing a registered ecology/resource coordinate changes which developmental-equivalence classes are Pareto-admissible.

The flagship Track-B empirical target is therefore:

> derive a phase/frontier prediction before protected morphology search, then recover the predicted frontier transition from a shared low-level basis without supplying architecture labels.

## 6. Known forms become examples, not foundations

The theory should reproduce known morphology families as specializations:

```text
neural / differentiable
symbolic / production / rewrite
probabilistic / generative-program
programmatic / library-learning
reservoir / dynamical
vector-symbolic / HDC
spiking / neuromorphic
developmental cellular / local-rule
evolutionary / population
hybrid systems
```

Current OCM is one explicit/governed morphology hypothesis, not the definition of the substrate.

## 7. Where neural networks fit

Neural morphology is a particularly successful region characterized by some combination of:

```text
continuous/distributed mutable parameters
differentiable or otherwise effective credit assignment
high training amortization over repeated inference
representation sharing
massive hardware parallelism/co-design
```

Meta-learning, differentiable plasticity, continual learning and topology evolution make neural systems developmental too.

Track B must explain neural dominance in some regimes and predict regimes where other/hybrid morphologies become Pareto-admissible.

## 8. Strong nulls

The programme fails to establish a distinct theory if the strongest results reduce entirely to:

```text
UNIVERSAL_COMPUTATION_ONLY
ALGORITHM_SELECTION_PARENT_SUFFICIENT
RESOURCE_RATIONAL_PARENT_SUFFICIENT
AUTOML_NAS_PARENT_SUFFICIENT
PARENT_FORMALISM_SUFFICIENT
HUMAN_PORTFOLIO_DEFINES_THE_PHASES
POST_HOC_PHASE_STORY_ONLY
```

## 9. Current highest plausible novelty residual

After parent subtraction, the strongest candidate residual is:

> A resource-bounded developmental theory in which multiple known machine-intelligence morphologies arise from a shared low-level generative basis; morphology identity is defined by developmental/resource equivalence; and the theory prospectively predicts morphology-frontier transitions across task/resource/verification regimes, including a phase-diagram hole that can be filled by a blindly discovered non-parent-equivalent morphology.

This is not yet established.

## 10. Ultimate test

The theory approaches a field-level result only if all stages survive:

```text
shared basis / equivalence class
-> known-form bounded derivations
-> developmental acquisition without labels
-> prospective phase prediction
-> blind recovery on disjoint ecologies
-> parent/hybrid reduction
-> missing-form prediction
-> independent rediscovery/replication
```

Only after that should Track B revisit whether the morphology generator `Gamma` itself can improve over generations.

## Current terminal

```text
GMI_CORE_HYPOTHESIS_FORMALIZED__NOT_ESTABLISHED
NO_UNIQUE_COGNITIVE_ATOM_ESTABLISHED
PHASE_LAW_AND_CROSS_PARADIGM_DERIVATION_ARE_DECISIVE
```