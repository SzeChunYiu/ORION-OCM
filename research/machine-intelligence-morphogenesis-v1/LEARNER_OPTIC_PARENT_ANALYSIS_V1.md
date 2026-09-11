# Learner / lens / categorical-cybernetics parent analysis v1

## Why this is load-bearing for the “fundamental cognitive unit” question

Track B initially asked whether a minimal adaptive primitive might look like:

```text
local state
input -> output
experience-dependent update
composition interface
```

That structure is **not parentless**.

Several categorical-learning/cybernetics programmes already provide formal objects extremely close to this shape. Track B must absorb them before claiming a basic cognitive unit.

---

## 1. Fong–Spivak–Tuyéras learner

`Backprop as Functor` defines a compositional category of supervised learners. A learner from `A` to `B` can be represented by a tuple of the form:

```text
(P, I, U, r)
```

with:

```text
P  parameter/state space
I  implementation / forward behavior
U  parameter update from example/feedback
r  request / backward signal passed to the previous component
```

The central result is that, under the paper's assumptions, gradient descent/backprop gives a monoidal functor from parametrized functions into the category of learners.

Track-B consequence:

```text
PARAMETERS + FORWARD MAP + UPDATE + BACKWARD/REQUEST + COMPOSITION
```

cannot be claimed as an ORION fundamental-unit novelty.

It is, however, an exceptionally strong parent candidate for one equivalence class of adaptive bases.

Primary parent:

- Fong, Spivak, Tuyéras, *Backprop as Functor: A compositional perspective on supervised learning* (LICS 2019 / arXiv:1711.10455).

---

## 2. Learners as lenses / generalized dynamical systems

Subsequent work relates the learner category to parametrized lenses. `Learners' Languages` places simple lenses inside polynomial functors and interprets learners in terms of generalized Moore-machine / dynamical-system structure.

Track-B consequence:

The candidate basis family

```text
local adaptive transducer
```

is threatened simultaneously by:

```text
automata / coalgebra
lenses / optics
polynomial dynamical systems
compositional learners
```

If Stage C-v1 merely reconstructs this object with different names, use:

```text
PARENT_FORMALISM_SUFFICIENT
```

rather than a new unit claim.

Primary parent:

- Spivak, *Learners' Languages* (2021, arXiv:2103.01189).

---

## 3. Gradient-based learning already generalizes beyond ordinary neural networks

`Categorical Foundations of Gradient-Based Learning` gives categorical semantics for gradient-based learning using lenses, parametrized maps and reverse-derivative categories. The framework covers several optimizers/losses and has discrete Boolean-circuit realizations.

`Reverse Derivative Ascent` demonstrates learning parameters of Boolean circuits directly using categorical reverse-derivative structure.

Track-B consequence:

```text
gradient-like adaptation
```

is not intrinsically tied to conventional neural morphology.

Therefore one cannot define intelligence morphologies simply as:

```text
neural = gradients
symbolic = no gradients
```

Learning law and representational morphology are partly separable axes.

Parents:

- Cruttwell et al., *Categorical Foundations of Gradient-Based Learning* (ESOP 2022).
- Wilson & Zanasi, *Reverse Derivative Ascent: A Categorical Approach to Learning Boolean Circuits* (ACT 2020/2021).

---

## 4. Bayesian updating also has compositional lens structure

`Bayesian Updates Compose Optically` shows that Bayesian inversion/update for compositional causal processes can be represented using lens/optic structure, under the stated exactness/lawfulness conditions.

Track-B consequence:

A proposed common basis does not earn cross-paradigm novelty merely because both neural gradient updates and Bayesian updates can be written in one bidirectional/compositional language. Strong parent mathematics already connects Bayesian updating to optics/lenses.

Parent:

- Smithe, *Bayesian Updates Compose Optically* (2020, arXiv:2006.01631).

---

## 5. Categorical cybernetics is an even broader parent

`Towards Foundations of Categorical Cybernetics` studies compositional processes interacting bidirectionally with both environment and controller. Open learners and game-theoretic agents appear as examples.

Recent work extends this line into reinforcement-learning constructions.

Track-B consequence:

```text
open adaptive process
+ environment interaction
+ controller/optimizer interaction
+ compositionality
```

is also substantially parent-owned.

Parent family:

- Capucci, Gavranović, Hedges, Rischel, *Towards Foundations of Categorical Cybernetics* (2021).
- subsequent categorical-cybernetics RL work.

---

# 6. What this does to the fundamental-unit hypothesis

The strongest current conclusion is **not**:

```text
ORION discovered the primitive adaptive unit.
```

It is:

```text
There are existing formal equivalence-class candidates for adaptive compositional
units: learners, lenses/optics, open dynamical systems and cybernetic processes.
```

Track B should therefore test whether one of these mature formalisms is already sufficient as the lower-level substrate.

Possible outcomes:

```text
LEARNER_LENS_BASIS_PARENT_SUFFICIENT
COALGEBRAIC_ADAPTIVE_PROCESS_PARENT_SUFFICIENT
CATEGORICAL_CYBERNETICS_PARENT_SUFFICIENT
CURRENT_PARENT_FORMALISMS_MISS_<specific residual>
```

Only the final case licenses a new fundamental-basis formalism.

---

# 7. The upward residual after absorbing these parents

Even if a mature learner/lens/cybernetic object is accepted as the basic compositional adaptive substrate, it does not by itself answer:

```text
Why should neural morphology arise rather than a rule system?
Why should a probabilistic program arise rather than a deterministic program?
Which representation/topology/update-law organization is resource-optimal in a new ecology?
When should the morphology itself change?
Can a theory predict a morphology before architecture search?
Can a missing morphology be predicted from a hole in the known developmental frontier?
```

Therefore Track B's likely novel scientific level moves upward to:

```text
basic adaptive substrate (possibly parent-owned)
        ↓
constraints + ecology + resources + verification
        ↓
morphogenesis law Gamma
        ↓
intelligence morphology frontier
```

That is consistent with #373's rule: absorb the parent, then move the question upward.

---

# 8. Immediate test to add to Stage C-v1

For every proposed Stage C-v1 basis, construct an explicit mapping to at least:

```text
Fong-style Learner (P,I,U,r)
parametrized lens/optic
finite/open dynamical-system representation
```

Then classify:

```text
EXACT_PARENT_ISOMORPHISM
BOUNDED_PARENT_COMPILATION
PARENT_WITH_RESOURCE_OVERHEAD
PARENT_MISSES_REGISTERED_DEVELOPMENTAL_SEMANTIC
NON_IDENTIFIABLE
```

No fundamental-basis claim survives an exact/cheap parent equivalence.
