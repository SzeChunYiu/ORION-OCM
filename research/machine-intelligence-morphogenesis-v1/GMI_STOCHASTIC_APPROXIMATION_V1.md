# GMI stochastic / approximate developmental-state semantics v1

Status: **F0 formal hardening**, using predictive-state / bisimulation / probability-metric parents rather than inventing a new stochastic-state theory.

---

# 1. Future semantic-trace kernel

Fix cognitive obligation/development/intervention contract `(O,D,J)`.

Let

\[
(\Omega^{sem}_{\mathcal O},\mathcal F^{sem}_{\mathcal O})
\]

be the measurable space of registered future **semantic** protected traces, including only quantities the obligation declares semantically relevant, for example:

```text
external outputs/actions
evidence/admissibility receipts
responses to registered teaching/probes
retention/plasticity/generalization observables
authority/abstention/refusal terminals
```

Do not automatically include raw private implementation changes or raw resource receipts. Those are attached to concrete morphology transitions and intelligence frontiers unless the obligation explicitly makes them semantic outputs.

For developmental situation `d` and admissible future intervention/probe programme `j`, let

\[
P^{M,D,sem}_{\mathcal O}(\cdot\mid d,j)
\]

be the induced probability measure over protected future semantic traces.

Randomness can come from the machine, environment, development protocol or evidence process.

---

# 2. Exact stochastic semantic developmental equivalence

Define

\[
d\sim^{sem}d'
\]

iff for every `j in J`:

\[
P^{M,D,sem}_{\mathcal O}(\cdot\mid d,j)
=
P^{M,D,sem}_{\mathcal O}(\cdot\mid d',j)
\]

as probability measures on the same semantic future-trace space.

Equality of measures is reflexive, symmetric and transitive, so exact stochastic semantic developmental equivalence is an equivalence relation.

**Computability warning:** exact equality can be impossible to decide for rich systems even when semantically well-defined.

---

# 3. Resource-labelled transition law

A concrete morphology also induces a joint law over semantic futures and raw resource receipts:

\[
P^{M,D,perf}_{\mathcal O}(\cdot\mid d,j)
\]

on an augmented trace space that includes `r`.

This performance/resource law is used for:

```text
resource-sensitive morphology comparison
bounded compiler equivalence
capability/resource frontier construction
lifecycle economics
```

Two situations/morphologies may be semantically equivalent while their performance/resource laws differ.

---

# 4. Approximate semantic future-law distance

Practical systems require approximation.

Choose a **registered** probability-distance/pseudometric appropriate to semantic protected traces, such as:

```text
total variation
Wasserstein / Kantorovich metric
integral probability metric over a registered test-function class
bisimulation metric
value/task-aware pseudometric
```

No one metric is universally canonical.

For a base distance `D_P` define

\[
\delta^{sem}_{\mathcal O}(d,d')
=
\sup_{j\in J}
D_P\left(
P^{sem}_{\mathcal O}(\cdot\mid d,j),
P^{sem}_{\mathcal O}(\cdot\mid d',j)
\right).
\]

If `D_P` is a pseudometric and the supremum is well-defined, `delta_sem` is also a pseudometric.

A separate `delta_perf` may be defined on resource-augmented traces when the scientific question concerns implementation equivalence.

---

# 5. Important no-go: epsilon-closeness is generally not an equivalence relation

A tempting definition is

\[
d\sim_\epsilon d'
\iff
\delta^{sem}_{\mathcal O}(d,d')\le\epsilon.
\]

This relation is reflexive and symmetric when `delta` is a pseudometric, but it need not be transitive at the same threshold.

By triangle inequality:

\[
\delta(d_1,d_3)
\le
\delta(d_1,d_2)+\delta(d_2,d_3)
\le 2\epsilon,
\]

not necessarily `<= epsilon`.

Therefore:

```text
DO NOT form an exact quotient by arbitrary epsilon-closeness.
```

Use:

- exact zero-distance quotient;
- metric/pseudometric state space;
- epsilon-cover/clustering with explicit non-transitivity;
- abstraction maps with proved error propagation;
- parent bisimulation/state-abstraction theorems.

---

# 6. Zero-distance quotient

For pseudometric `delta`, define

\[
d\equiv_0d'
\iff
\delta(d,d')=0.
\]

This is an equivalence relation. Quotienting by zero distance gives the usual separated metric construction under ordinary assumptions.

---

# 7. Protected-function formulation

Sometimes comparing the complete semantic trace distribution is unnecessary or impossible.

Let `G_O` be a prospectively registered class of bounded **semantic** protected functionals

\[
g:\Omega^{sem}_O\to\mathbb R.
\]

Define

\[
\delta_G(d,d')
=
\sup_{j\in J}
\sup_{g\in G_O}
\left|
E[g\mid d,j]-E[g\mid d',j]
\right|.
\]

Examples may measure:

```text
verified success/admissibility probability
capability coordinates
retention after teaching
probability of harmful/unauthorized action
future K1 acquisition event
```

Raw resource coordinates are normally compared separately through performance/frontier semantics, unless explicitly promoted into the protected semantic contract.

If `G_O` is too weak, states that matter for an unregistered quantity can be merged. That is expected: minimality is obligation-relative.

---

# 8. Bisimulation parent

For MDPs, bisimulation and bisimulation metrics already relate states via reward/transition similarity and can bound value differences under theorem-specific assumptions.

GMI imports those results when its developmental meta-state can be represented as a controlled Markov process:

```text
meta-state = machine configuration + sufficient accessible environment/information state
transition = cognition/development step
protected semantic signal = registered evidence/capability/authority outcomes
resource receipt = separate transition label/cost unless the parent theorem includes it
```

If budget/resource state changes legal future actions it belongs in the meta-state; raw spend remains a transition cost/receipt.

---

# 9. Predictive-state parent

Predictive State Representations use action-conditional predictions of future observations as state.

GMI adopts this philosophy by defining predictions over registered future semantic traces rather than assuming latent physical state is the primitive representation.

This is a parent specialization, not novelty.

---

# 10. Error propagation obligation

If approximate abstraction `phi(d)` is used operationally, claims about capability or burden require an explicit bridge.

For semantic capability functional `f`, a schematic theorem may require

\[
\delta^{sem}(d,d')\le\epsilon
\Longrightarrow
|f(d)-f(d')|\le L_f\epsilon.
\]

For resource burden, a separate bound on resource-labelled transition laws or implementation costs is needed. Semantic closeness alone does **not** guarantee similar compute/update cost.

---

# 11. F0 consequence

The corrected hierarchy is:

```text
semantic future-law equality
    -> true equivalence relation / quotient

zero semantic-pseudometric distance
    -> true equivalence relation / quotient

finite epsilon semantic similarity
    -> approximate relation, generally not transitive
    -> metrics/covers/error bounds

resource/performance similarity
    -> separate stronger relation / frontier comparison
```

Current terminal:

```text
GMI_STOCHASTIC_EXACT_SEMANTIC_STATE_WELL_DEFINED
SEMANTIC_AND_RESOURCE_DISTRIBUTIONS_SEPARATED
APPROXIMATE_EPSILON_QUOTIENT_FORBIDDEN_WITHOUT_EXTRA_STRUCTURE
BISIMULATION_PSR_PARENT_MACHINERY_ADOPTED
```
