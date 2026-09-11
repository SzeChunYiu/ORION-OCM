# Morphogenesis decomposition v2 — closure, frontier, search

Status: **core theory refinement; non-final**.

The earlier notation

\[
\Gamma(B,E,R,V,H)\to \mathcal P(\mathcal M)
\]

was useful but overloaded. It mixed at least three scientifically different questions:

1. what morphologies are possible from the basis;
2. which possible morphologies are favorable under the ecology;
3. whether a particular search/development process can discover them.

These must be separated.

---

## 1. Generative closure — what can exist?

For basis `B` with legal composition/development grammar `C_B`, define the morphology closure

\[
\mathcal M_B = \operatorname{Closure}(B;\mathcal C_B).
\]

At finite registered scope this can sometimes be enumerated exactly. At larger scope it is a formal/reachable set.

This object answers:

> Which executable/developable organizations are expressible without adding a new primitive or architecture-specific macro?

A D0 representability claim concerns membership in `M_B`.

But universal-program parents make mere membership weak.

---

## 2. Developmental feasibility — what can be acquired at a given cost?

For morphology `M in M_B`, ecology `E`, developmental history/budget `h`, define the achievable resource/capability set

\[
\mathcal A_B(M,E)=\{(Q,\mathbf R,D):\text{reachable through legal development}\}.
\]

Here `D` includes registered developmental properties such as:

```text
retention / forgetting
plasticity
revision behavior
transfer
learning/update locality
```

This distinguishes a morphology that is representable only through an enormous handcrafted compiler from one that can be acquired efficiently from the basis.

---

## 3. Ecology frontier — what should be favored?

Define the complete morphology frontier at registered scope:

\[
\mathcal F_B(E)
=
\operatorname{Pareto}\left(
\bigcup_{M\in\mathcal M_B}\mathcal A_B(M,E)
\right).
\]

More usefully retain morphology identity:

\[
\mathcal F^{M}_B(E)
=
\{M:\exists (Q,\mathbf R,D)\text{ from }M\text{ that is nondominated}\}.
\]

This is the **search-independent** morphology phase object.

A phase transition occurs when changing a registered ecology/resource/verifier coordinate changes frontier membership/equivalence class:

\[
\mathcal F^{M}_B(E_1)\neq \mathcal F^{M}_B(E_2).
\]

This is stronger than observing that one optimizer happened to find different architectures.

---

## 4. Search / morphogenesis dynamics — what can actually be discovered?

Let `Gamma` now mean only the developmental/search dynamics over the morphology closure:

\[
\Gamma_t(M'\mid M,H,E,B)
\]

or a more general proposal/selection process.

Its realized archive after budget `C` is

\[
\mathcal A^{search}_{\Gamma,C}\subseteq\mathcal M_B.
\]

Search quality can then be evaluated against the true/exact frontier where tractable:

```text
frontier recall
regret to frontier
morphology-class coverage
cost to first frontier member
cost to predicted phase transition
```

This is where #221/#220 QD/evolution/search machinery eventually enters.

---

## 5. Four different failure modes

The decomposition prevents several common confusions.

### EXPRESSIVITY FAILURE

Target morphology not in `M_B` under the frozen grammar.

```text
BASIS_INSUFFICIENT
```

### DEVELOPMENT FAILURE

Morphology is representable but cannot be acquired/maintained under the registered developmental budget.

```text
DEVELOPMENTAL_ACQUISITION_DOMINATES
```

### ECOLOGY FAILURE

Morphology is possible/acquirable but is not on the full developmental frontier in the claimed regime.

```text
MORPHOLOGY_NOT_FAVORED_AT_SCOPE
```

### SEARCH FAILURE

Morphology is genuinely frontier-admissible but the search process fails to find it at the registered budget.

```text
MORPHOGENESIS_SEARCH_FAILURE
```

These require different scientific responses.

---

## 6. Relationship to parent fields

- computability / programming languages primarily constrain `M_B`;
- learning theory/meta-learning constrain acquisition within `A_B`;
- algorithm selection/resource rationality constrain `F_B(E)` when candidate forms are supplied;
- AutoML/NAS/evolution/QD constrain `Gamma`;
- Track B's strongest residual requires all layers to be tied together **without smuggling the target morphology labels into B or Gamma**.

---

## 7. Stronger form of the phase-law experiment

Do not merely run search in `E1` and `E2` and observe different winners.

Required order:

```text
1. freeze B and bounded morphology grammar;
2. on tiny development scopes, enumerate/estimate M_B and full frontier F_B(E);
3. derive a frontier membership/boundary prediction;
4. freeze a search algorithm Gamma that does not know the protected labels;
5. on disjoint ecologies, test whether Gamma recovers the predicted frontier classes;
6. distinguish wrong theory (frontier prediction false) from bad search (frontier true, Gamma misses it).
```

This is substantially stronger than ordinary architecture search.

---

## 8. Unknown morphology discovery becomes precise

A theory-predicted hole is now:

```text
known registered parent morphologies do not cover a predicted region of F_B(E)
```

rather than:

```text
search found a weird structure.
```

A missing-form programme can then ask whether neutral `Gamma` discovers `M*` in that region and whether `M*` is non-equivalent to all known parent families.

---

## 9. Current core notation

The Track-B theory stack should now use:

\[
\boxed{
B
\to \mathcal M_B
\to \mathcal F_B(E)
\leftarrow \Gamma
}
\]

with within-morphology development

\[
M_{t+1}=U(M_t,e_t).
\]

Informally:

```text
basis says what can exist;
ecology/resources say what is worth existing;
search says what is actually found;
learning says how a found form changes with experience.
```

This is the cleanest current answer to the original handwritten `Generator theta(...)` concept.