# Definitions v1 — Track B

Status: **provisional attack surface**, not a final theory. Successful definitions migrate upward into #233; failed ones are replaced rather than defended.

## 1. Adaptive generating basis

A candidate basis is

\[
B=(\mathcal T,\mathcal P,\mathcal C,\mathcal U,\rho)
\]

where:

- `T` is a finite or recursively specified type system for values, state and ports;
- `P` is a set of primitive typed state transformations/transducers;
- `C` is a composition grammar over primitives and already-composed objects;
- `U` is the permitted family of developmental updates to mutable state, parameters, programs and/or topology;
- `rho` maps description, execution, update and maintenance events to a declared resource vector.

A primitive `p in P` is specified by a typed contract, not a prose name:

\[
p=(S_p,I_p,O_p,\delta_p)
\]

with local state `S_p`, typed input `I_p`, typed output `O_p`, and transition kernel

\[
\delta_p : S_p\times I_p \to \mathcal D(S_p\times O_p)
\]

where `D(X)` denotes deterministic or stochastic distributions over `X`. Deterministic primitives are the degenerate stochastic case.

The basis definition deliberately does **not** include warrant/provenance/OCM lifecycle fields as mandatory atom properties. Those may emerge as a morphology or be externally required by an ecology. Otherwise the basis would bake current OCM into the answer.

### 1.1 Basis equivalence is not syntax equality

Two bases may differ syntactically but be equivalent at registered scope if each can compile the other's admissible constructions and updates with bounded resource inflation. The exact relation is defined in `EQUIVALENCE_CONTRACT_V1.md`.

### 1.2 Minimality is relative

No absolute metaphysical minimum is assumed. Minimality is always stated relative to:

```text
task ecology / task class
resource envelope or price vector
verification obligations
allowed compilation overhead
```

Possible result: multiple equivalent minimal bases.

---

## 2. Machine-intelligence morphology

A morphology is a complete executable/developable organization built over some basis:

\[
M=(G,X,\Theta,\Pi,\mathcal L,\mathcal K)
\]

where:

- `G` is the typed composition/topology/program structure;
- `X` is persistent and transient machine state;
- `Theta` is mutable parametric or symbolic configuration not already represented structurally in `G`;
- `Pi` is execution/control/scheduling semantics;
- `L` is the learning/developmental update law acting on `(G,X,Theta,Pi)`;
- `K` is the externally visible I/O/action interface required by the ecology.

The separation is representational: a neural system may put most competence in `Theta`; a production system may place it in `G/X`; a probabilistic program may encode stochastic structure in `G`; an OCM-like system may place explicit methods and dependencies in `X/G`.

A morphology is **not** identified by a human architecture label. `neural`, `symbolic`, `probabilistic`, `programmatic`, and `hybrid` are hypotheses about equivalence classes under structural/developmental invariants.

### 2.1 Morphology phenotype

For experiments define an observable phenotype

\[
\Phi_E(M)= (Q,R,D,S)
\]

where under ecology `E`:

- `Q` = verified capability vector;
- `R` = complete resource vector;
- `D` = developmental response (how behavior/resources change after experience);
- `S` = registered structural observables that are not mere encoding artifacts.

A new morphology claim must survive behavioral/developmental equivalence testing; different source code or graph shape alone is insufficient.

---

## 3. Ecology

An ecology is

\[
E=(\mathcal D_\tau,\mathcal O,\mathcal A,\mathcal F,V,\mathbf p,\mathbf b,H,\Delta)
\]

where:

- `D_tau` is a task/problem distribution or finite registered family;
- `O` is the observation/information interface;
- `A` is the legal action/output interface;
- `F` is feedback available during development;
- `V` is the external verifier/evaluator for registered claims;
- `p` is a resource-price/priority vector when scalarization is needed;
- `b` is a resource-budget vector;
- `H` is horizon/reuse opportunity;
- `Delta` is the drift/regime-change process.

Ecology coordinates may include data volume, stochasticity, smoothness, compositionality, algorithmic regularity, partial observability, verification strength/cost, revision frequency, reuse horizon, communication/interaction cost and resource prices. The coordinate set is itself an empirical hypothesis and may prove insufficient.

---

## 4. Four levels of derivation

### D0 — representability

`B` represents morphology `M` if an object constructed from `B` has the required I/O behavior at the registered scope.

This is weak. Turing completeness or universal approximation may make it trivial.

### D1 — bounded developmental compilation

A compiler

\[
\kappa_{B}:M\mapsto M_B
\]

establishes D1 only if, over registered ecology `E`:

1. task behavior is preserved within tolerance `epsilon_Q`;
2. the developmental update trajectory is preserved within `epsilon_D` for the registered experiences/interventions;
3. verifier outcomes are preserved;
4. resource inflation satisfies prospectively specified bounds, e.g.

\[
R(M_B,e) \preceq \alpha\odot R(M,e)+\beta
\]

for the declared resource coordinates.

If only final input/output behavior is preserved, call it `BEHAVIORAL_COMPILATION_ONLY`.

### D2 — developmental acquisition

A morphology family `C` is developmentally acquired from basis `B` under ecology `E` when the construction/search/development process:

- starts without a direct architecture label or architecture-specific macro sufficient to instantiate `C`;
- has a prospectively frozen construction grammar and resource budget;
- reaches a member of `C` under a preregistered morphology classifier/equivalence test;
- survives controls for encoding/search bias.

D2 is a statement about discoverability, not merely expressibility.

### D3 — prospective morphogenesis

Let `Frontier(B,E)` denote the nondominated morphology classes under registered capability/resource/development coordinates.

A morphology phase law is a pre-outcome map

\[
\Gamma_B : E \to \mathcal P(\mathcal M)
\]

that predicts the morphology class(es), ordering, or transition boundaries expected on the frontier.

D3 support requires predictions to be frozen before protected morphology search/evaluation and to survive disjoint ecology draws and search-encoding controls.

---

## 5. Intelligence-specific content criterion

A candidate Track-B theory must produce at least one nontrivial statement that would not follow merely from generic universal computation, such as:

- a lower/upper bound on developmental compilation overhead between morphology classes;
- an impossibility result separating morphologies under a resource/verification constraint;
- a predicted morphology transition as an ecology coordinate varies;
- a relation between ecology structure and useful inherited representation/update law;
- a bound on acquisition/search cost for one morphology relative to another.

If all surviving statements reduce to “the basis can simulate the target,” terminal:

`UNIVERSAL_COMPUTATION_ONLY`.

---

## 6. Relationship to HST

Track B should embed in #233 by treating morphology/basis changes as changes to HST state components, especially constructive language `L`, proposal/search process `Q`, inherited structure `H` and resource allocation `R`.

A tentative correspondence is:

```text
B / morphology grammar -> HST L
morphology construction/search -> HST Q
learned morphology state -> HST H
learning/update scheduling -> HST R
registered ecology -> HST E
external evaluator -> HST V
external non-self-certifying rules -> HST C
```

This correspondence is provisional. Track B does not create a second incompatible developmental theory.