# GMI Cross-Paradigm Realization Normal Form v1

Status: **FORMAL SYNTHESIS / SPECIALIZATION CONTRACT — NOT A UNIVERSAL NOVELTY CLAIM**

Refs: #233, #377, `GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md`, `GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_V1.md`.

## 1. Purpose

The semantic quotient theorem identifies what distinctions a machine must preserve for a fixed registered cognitive obligation.

This document asks the next question:

> What common mathematical structure must neural, symbolic, probabilistic, programmatic, memory/skill and OCM-like systems instantiate if they are all realizations of the same general machine-intelligence theory?

The answer must be stronger than “they are all programs”, but weaker than pretending they use the same internal representation.

---

# 2. Registered obligation

Use the existing GMI obligation

\[
\Omega=(\mathcal E,D,J,V,C,H,\mathcal R).
\]

Let

\[
S_\Omega
\]

be the semantic developmental quotient induced by future protected consequence under the registered legal development/intervention class.

`S_Omega` is implementation independent at the registered scope.

---

# 3. Realization normal form

A morphology realization of `Omega` is represented as

\[
\mathfrak M_\Omega
=
(Z,\kappa,Q,U,\Gamma,\rho),
\]

with external `V,C,D,J` retained in the obligation rather than internalized as self-certifying machine state.

## `Z` — realization state

All internal state legally available to future cognition, including where applicable:

```text
parameters
optimizer state
facts/rules
posterior state
program/library state
episodic/semantic memory
indexes/caches
controller state
OCM F/O/Pi mutable state
```

A hidden external side channel used by cognition belongs in `Z` or the external tool contract; it cannot disappear from accounting.

## `kappa : Z -> S_Omega` — semantic interpretation

`kappa` says which obligation-relevant semantic developmental state an internal realization state implements.

It may be many-to-one.

Multiple parameter vectors/program states/database arrangements may realize the same semantic state.

If no sound `kappa` can be defined at the claimed scope, the system has not established semantic correspondence for that obligation.

## `Q` — execution/proposal kernel

Given current realization state, task/observation context and legal tools, `Q` generates or selects cognition/action candidates.

Examples:

```text
neural forward policy/predictive distribution
production conflict resolution / agenda
Bayesian posterior predictive decision
program/library search or procedure invocation
retrieval + skill selection
OCM operator proposal/execution
```

`Q` is not automatically epistemic authority.

## `U` — within-morphology developmental update

`U` changes `Z` using legal experience/evidence while the morphology family/structural language is held fixed at the registered level.

Examples:

```text
SGD / Adam / optimizer step
posterior conditioning
rule/chunk/schema learning
library induction / program update
memory insertion/consolidation
OCM field/operator/applicability update
```

## `Gamma` — morphology/structural change

`Gamma` changes the realization structure itself, such as:

```text
network topology/architecture
representation/factorization
operator language
module boundaries
memory organization
program grammar
field organization
```

`Gamma = identity` is allowed.

Do not call an ordinary parameter update a morphology change merely because parameters changed.

## `rho` — resource semantics / meter

`rho` maps execution/development/morphogenesis to the registered raw resource vector.

It must include hidden preprocessing, training, storage/indexing and maintenance where the claim requires lifetime economics.

---

# 4. Commuting semantic condition

For exact deterministic scope, let

```text
T_M(z,a,e) -> (z', o)
```

be a legal realization transition under action/intervention/input `a` and evidence `e`.

Let

```text
T_S(s,a,e) -> (s', o_sem)
```

be the corresponding semantic-quotient transition/output required by the obligation.

Exact semantic adequacy requires, on the reachable registered set,

\[
\kappa(z')=s'
\]

and protected output correspondence

\[
o \equiv_\Omega o_{sem}
\]

whenever

\[
\kappa(z)=s.
\]

Equivalently, the realization transition must commute with the semantic interpretation:

```text
        T_M
Z  ------------> Z
|                 |
kappa              kappa
|                 |
v                 v
S_Omega ---------> S_Omega
        T_S
```

up to the registered output/correspondence relation.

This is a state-realization/homomorphism condition, not an architecture claim.

---

# 5. Learning must commute too when development is protected

If the obligation includes future learning/development, the semantic transition includes learning effects.

Then the update law `U` must preserve the correct future developmental state, not merely current answer behavior.

This is why two machines can be behaviorally equivalent now but developmentally inequivalent.

A fixed inference function with different optimizer/replay/plasticity state may map to the same present answer but a different semantic developmental quotient state if future learning outcomes are protected.

---

# 6. Neural/differentiable specialization

A neural learner may instantiate:

```text
Z      = parameters theta + optimizer state + declared persistent memory
kappa  = induced obligation-relevant predictive/control/developmental state
Q      = forward model / policy / proposal distribution
U      = SGD / Adam / meta-learned update / continual-learning update
Gamma  = identity for fixed architecture, or NAS/growth/pruning/topology change
rho    = training + inference + memory + accelerator + maintenance resources
```

For supervised gradient learning, `Backprop as Functor` and categorical learner/lens work are direct algebraic parents for compositional update structure.

GMI does not claim novelty for representing gradient learning as a composable learner.

Important:

- weights are a realization state, not automatically the semantic quotient;
- different weights can induce the same protected behavior;
- optimizer state can matter developmentally even when current predictions match;
- pretraining is part of prior/developmental history, not free constitution.

---

# 7. Symbolic / production specialization

A symbolic/production realization may instantiate:

```text
Z      = facts, productions, agenda/control state, indexes, learned chunks
kappa  = obligation-relevant symbolic/epistemic developmental state
Q      = matching, agenda selection, rule execution, symbolic search
U      = chunking, rule induction, truth-maintenance/revision, utility updates
Gamma  = new representation/rule language/module/control organization
rho    = matching/search/index/update/storage/verification resources
```

Soar/ACT-R/production/TMS families are parent realizations, not OCM novelty.

---

# 8. Probabilistic specialization

A Bayesian/probabilistic realization may instantiate:

```text
Z      = posterior/belief state, sufficient statistics, latent-model state, hyperparameters
kappa  = obligation-relevant predictive/decision state
Q      = posterior predictive / expected-utility or sampling-based decision kernel
U      = conditioning / filtering / variational or approximate posterior update
Gamma  = model-class/factorization/structure change
rho    = inference, sampling, message-passing, storage and update resources
```

For exact predictive obligations, minimal sufficient/predictive-state parents receive first refusal.

Posterior state is not self-certifying truth; external evidence/verification semantics remain governed by the obligation.

---

# 9. Programmatic / library-learning specialization

A programmatic realization may instantiate:

```text
Z      = current program(s), library/macros, synthesis/search state, learned grammar
kappa  = obligation-relevant executable developmental state
Q      = program search, composition, rewrite, procedure selection
U      = library induction, CEGIS update, grammar/search-bias update
Gamma  = language/grammar/operator/module expansion
rho    = synthesis/search/execution/checking/library-maintenance resources
```

OOPS/PowerPlay/DreamCoder/Stitch/CEGIS/program synthesis are parent families.

---

# 10. Memory / skill realization

A memory-heavy realization may instantiate:

```text
Z      = episodic traces, summaries, retrieval index, skills/procedures, applicability metadata
kappa  = obligation-relevant remembered developmental state
Q      = retrieval/ranking + skill/procedure serving
U      = memory insertion, consolidation, skill extraction, applicability update
Gamma  = memory/index/schema organization change
rho    = build/storage/index/query/update/verification resources
```

RAG, case-based reasoning, skill libraries and continual-skill agents are parent families.

---

# 11. OCM-like governed specialization

Current OCM may instantiate:

```text
Z      = F + O + Pi mutable state, active workspace where persistent, method/failure/provenance state
kappa  = registered epistemic/developmental semantic state
Q      = operator retrieval/proposal/execution + executive choice
U      = governed admission, learning, revision, consolidation, applicability/value updates
Gamma  = governed representation/operator/factorization/control change
rho    = complete OCM resource ledger
```

`C` remains external and is not included in the self-certifying mutable realization state.

This mapping does not privilege OCM. It places OCM beside other morphologies in the same theory.

---

# 12. Cross-paradigm invariants

The following meanings must remain fixed across families:

```text
semantic state        = future consequence class under Omega
realization state     = implementation state used to realize it
Q                     = candidate/action generation/selection mechanism
U                     = within-family developmental update
Gamma                 = structural/morphology change
rho                   = raw resource semantics
V/C                    = external verification/constitutional authority
```

A family fails the normal form only if one of these distinctions cannot be represented without changing its meaning.

---

# 13. What this normal form does NOT prove

It does not prove:

```text
all morphologies are equally good
one morphology can efficiently simulate every other
there is a unique universal architecture
there is a low-dimensional phase law
neural networks are derivable as the inevitable optimum
OCM is more general than parent architectures
```

It supplies a common comparison language.

---

# 14. Expressive-completeness trap

A sufficiently general state-transition formalism can encode essentially arbitrary computation.

Therefore merely embedding all known families in `(Z,kappa,Q,U,Gamma,rho)` is not evidence of a theory of intelligence.

The normal form earns scientific value only if it supports at least one of:

```text
nontrivial semantic minimality / impossibility theorem
prospective cross-paradigm resource prediction
morphology phase prediction
cross-domain developmental law
useful new realization discovery
```

Otherwise terminal:

```text
GENERAL_ADAPTIVE_STATE_MACHINE_REDESCRIPTION_ONLY
```

---

# 15. Relation to the demand signature

`Xi(Omega)` describes what the obligation demands.

The realization normal form describes what a morphology supplies.

The open empirical hypothesis is whether a compact, architecture-neutral relation

\[
\mathcal R(\Xi(\Omega),\mathfrak M)
\]

can prospectively predict near-frontier realization behavior across paradigms beyond family-native parents.

This is where GMI can move beyond a common vocabulary.

---

# 16. Next exact work

Create a tiny cross-paradigm realization atlas in which multiple implementations realize the **same** exact semantic quotient but use materially different update/state organization.

Required hostiles:

```text
semantic aliasing
current-answer-only equivalence
hidden side-channel state
resource-free preprocessing
family label leakage
```

The atlas is calibration only; it must not call toy encodings neural/symbolic novelty.

---

# 17. Current terminal

```text
GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_SPECIFIED_V1
```

Claim ceiling:

> The studied machine-intelligence families can be described using one semantic-state / realization / execution / development / morphogenesis / resource factorization. This is a synthesis contract, not yet a cross-paradigm predictive law.
