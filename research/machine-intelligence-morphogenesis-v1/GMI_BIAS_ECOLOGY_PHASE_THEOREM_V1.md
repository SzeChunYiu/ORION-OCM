# GMI Bias–Ecology Phase Theorem v1

Status: **FORMAL FINITE PHASE THEOREM — ALGEBRA/NFL PARENT-OWNED**

Refs: `GMI_BIAS_RESOURCE_GEOMETRY_V1.md`, #233, #377.

## 1. Purpose

The exact multi-form concept-learning calibration produced the same ecology crossover for:

```text
symbolic threshold version-space learning
Bayesian threshold-biased learning
one-neuron perceptron learning
```

despite different internal representations and update laws.

The crossover can be derived without architecture labels.

This theorem states the general finite algebraic condition.

---

# 2. Setup

Let a finite target/concept universe be

\[
\mathcal F
\]

and let a distinguished structured subset be

\[
\mathcal T\subset\mathcal F.
\]

Define

\[
\alpha=\frac{|\mathcal T|}{|\mathcal F|},
\qquad 0<\alpha<1.
\]

Let a fixed learner/realization `M` have expected registered score

\[
a_T
\]

when targets are sampled uniformly from `T`, and

\[
a_N
\]

when targets are sampled uniformly from the complement

\[
\mathcal F\setminus\mathcal T.
\]

Let its score under the uniform distribution over the full concept universe be

\[
b.
\]

Therefore

\[
b=\alpha a_T+(1-\alpha)a_N.
\]

Now define a family of ecologies `E_p`:

```text
with probability p:
    sample uniformly from T
with probability 1-p:
    sample uniformly from F\T.
```

The expected score is

\[
s_M(p)=p a_T+(1-p)a_N.
\]

---

# 3. GMI-BRG4 — exact ecology-bias crossover

Subtract the full-universe baseline:

\[
\begin{aligned}
s_M(p)-b
&= p a_T+(1-p)a_N
 -\alpha a_T-(1-\alpha)a_N\\
&=(p-\alpha)(a_T-a_N).
\end{aligned}
\]

Therefore:

\[
\boxed{
s_M(p)-b=(p-\alpha)(a_T-a_N)
}
\]

exactly.

If

\[
a_T>a_N,
\]

then:

```text
p > alpha  -> score above full-universe baseline
p = alpha  -> score exactly at baseline
p < alpha  -> score below baseline.
```

If `a_T<a_N`, the inequalities reverse.

No architecture family appears in the theorem.

---

# 4. NFL interpretation

Under many finite supervised-learning No-Free-Lunch setups, averaging uniformly over all target functions equalizes learners' expected generalization performance.

When that parent condition gives a common baseline `b`, a learner's advantage on one structured subset must be balanced by disadvantage elsewhere.

The theorem above then turns ecological over/under-representation of that structure into a phase transition in expected advantage.

GMI does not claim novelty for this fact.

Its role is to connect parent inductive-bias theory to morphology realization:

```text
morphology / learned state
-> induced bias Q_M
-> structured subset advantage/disadvantage
-> ecology prevalence
-> expected capability phase
-> resource frontier after rho is added.
```

---

# 5. Registered fixture

In `gmi_cross_paradigm_bias_phase.py`:

```text
|F| = 32 Boolean concepts on five inputs
|T| = 6 monotone threshold concepts
alpha = 6/32 = 3/16.
```

For all registered training sizes `m=1..4`, exhaustive enumeration gives

```text
uniform full-concept score b = 1/2
```

for:

```text
EXEMPLAR_MEMORY
SYMBOLIC_THRESHOLD
BAYES_THRESHOLD_MIX
PARAMETRIC_PERCEPTRON.
```

For the three threshold-biased learners,

```text
a_T > 1/2 > a_N.
```

Hence their expected advantage crosses exactly at

\[
p=3/16.
\]

The exact per-family magnitudes differ.

---

# 6. What this theorem does and does not say

It says:

> Once a morphology/learner induces a measurable structured bias, the ecological prevalence of that structure can determine the sign of its expected advantage under the finite mixture assumptions.

It does not say:

```text
which morphology produces the bias most cheaply
which learner should be selected under real resources
how the structured subset should be discovered
how to identify T prospectively in real domains
that all ecologies are finite mixtures of one subset/complement
that modern deep networks reduce to one-neuron behavior
```

Those belong to the realization/resource/development layers.

---

# 7. Morphology implication

Different architectures can share the same *direction* of inductive bias.

Therefore:

```text
architecture family
!=
inductive-bias identity.
```

This suggests a more general Track-B object:

\[
\text{form of machine intelligence}
\approx
\text{reachable bias/update/resource geometry}
\]

rather than visible topology alone.

That statement is still a hypothesis at broad scale.

---

# 8. Developmental version

If experience changes the bias from `Q_t` to `Q_(t+1)`, define corresponding subset scores

\[
a_{T,t},a_{N,t}
\]

and phase response

\[
s_t(p).
\]

Development is useful on ecology `E_p` when the inherited change moves the expected capability/resource frontier in the correct direction after acquisition cost.

A development history can therefore be beneficial in one ecology and harmful in another without contradiction.

This is the exact finite ancestor of the programme's harmful-transfer requirement.

---

# 9. Resource correction

Capability advantage is not complete morphology dominance.

For lifetime comparison use, separately,

\[
B_M(p,H,\rho)
\]

including build/acquisition, serving, update, maintenance and verification.

A learner may have

```text
s_M(p) > s_parent(p)
```

but still be dominated in resources at matched capability.

Conversely, a slight capability loss may be acceptable only under a prospectively frozen non-inferiority contract.

---

# 10. Stronger open conjecture

The finite theorem motivates, but does not prove, a broader conjecture:

> Across materially different machine-intelligence families, useful developmental advantage is explained more directly by the alignment of induced pre-solution bias with the structured task ecology, together with complete resource economics, than by architecture labels alone.

Call this:

```text
GMI-BRG-CONJECTURE-1
```

It requires prospective real-family tests.

---

# 11. Falsifiers of the stronger conjecture

```text
BIAS_MEASURE_NOT_IDENTIFIABLE_PRE_OUTCOME
BIAS_ALIGNMENT_DOES_NOT_TRANSFER_ACROSS_FAMILIES
ARCHITECTURE_LABEL_ADDS_ESSENTIAL_PREDICTIVE_INFORMATION
FAMILY_NATIVE_PARENT_EXPLAINS_ALL_CROSSOVER
RESOURCE_COST_REVERSES_CAPABILITY_PHASE
NO_DISJOINT_REPLICATION
```

---

# 12. Terminal

Formal finite result:

```text
BIAS_ECOLOGY_CROSSOVER_THEOREM_PROVED_BY_ALGEBRA_AT_REGISTERED_FINITE_SCOPE
```

Scientific claim ceiling:

> Exact finite parent-owned phase relation linking structured inductive bias and ecology prevalence. It motivates—but does not establish—a general cross-paradigm law of machine-intelligence morphology.
