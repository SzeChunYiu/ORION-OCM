# Foundational Questions v2 — Track B

Status: **steering questions, not conclusions**. This document turns the current Track-B sketch into explicit mathematical objects, falsifiers and work packages.

The programme now has four primary questions and one higher-order extension.

---

## Q1 — What is the minimal generating basis of machine intelligence?

Do there exist one or more small adaptive generating bases

\[
B^* = (\mathcal T,\mathcal P,\mathcal C,\mathcal U,\rho)
\]

such that materially different intelligence morphologies can be constructed and developed from them with bounded overhead?

Do **not** assume one unique atom. Valid outcomes include:

```text
ONE_MINIMAL_BASIS_AT_SCOPE
MULTIPLE_EQUIVALENT_MINIMAL_BASES
RESOURCE_IRREDUCIBLE_BASIS_ONLY
LEARNING_IRREDUCIBLE_BASIS_ONLY
NO_SMALL_CROSS_PARADIGM_BASIS
UNIVERSAL_COMPUTATION_ONLY
```

### Scientific requirements

- minimality is compensation-aware: remove a primitive, then allow the remaining basis to recompose;
- distinguish algebraic, resource, learning and epistemic irreducibility;
- quotient syntactically different bases when they mutually compile with registered bounded overhead;
- no `FUNDAMENTAL_COGNITIVE_UNIT` claim from elegance or Turing completeness;
- current OCM `u2` remains a possible morphology-level Cognitive Asset Contract, not the assumed primitive.

### Immediate tasks

- [x] exact Boolean generator calibration;
- [ ] exact developmental-equivalence witness;
- [ ] tiny adaptive-basis census;
- [ ] bounded basis-equivalence theorem/preorder;
- [ ] basis candidates must derive at least neural, symbolic, probabilistic and programmatic tiny systems without architecture-labelled macros.

---

## Q2 — What generates different forms of machine intelligence?

The central object is a **morphogenesis law**, not a hand-written list of architectures.

Provisional form:

\[
\Gamma : (B,E,R,V,H) \longrightarrow \mathcal P(\mathcal M)
\]

where:

- `B` = adaptive generating basis;
- `E` = task ecology / observation-action structure;
- `R` = resource budget and prices, including hardware realization;
- `V` = verification / feedback regime;
- `H` = developmental history;
- `M` = machine-intelligence morphology.

The output may be a distribution/frontier over morphologies rather than one deterministic architecture.

Known candidate regions include:

```text
M_neural
M_symbolic
M_probabilistic
M_programmatic
M_hybrid
M_unknown
```

The names are external labels used for evaluation, not primitives supplied to the generator.

### Four levels of derivation

```text
D0 representability       — can B simulate M?
D1 bounded compilation    — can B realize M with bounded overhead?
D2 developmental acquire  — can M emerge without its label/architecture being supplied?
D3 prospective morphogenesis — can theory predict which M will emerge before search?
```

D0 alone is nearly worthless because universal computation can trivialize it.

### Immediate tasks

- [ ] finish parent subtraction against coalgebra/dynamical-system/category formalisms;
- [ ] derive tiny neural, production, probabilistic and programmatic systems from the same basis candidate;
- [ ] prohibit architecture-labelled primitives (`NEURON`, `BACKPROP`, `PRODUCTION_RULE`, `BAYES_UPDATE`, `PROGRAM_INTERPRETER`);
- [ ] freeze morphology identity/equivalence by developmental behavior and resource profile, not source-code shape;
- [ ] prospective blind recovery before any morphology-search claim.

---

## Q3 — What limits a form of intelligence, and why does one form dominate a regime?

Track B should explain morphology success/failure through a **developmental frontier**, not slogans such as “neural is more powerful” or “symbolic is more interpretable.”

For morphology `M`, ecology `E` and complete scalarized resource budget `c` only when a price vector has been frozen, define

\[
Q_M^*(c;E)
\]

as the best verified capability reachable by the legal developmental process within cost `c`.

The local developmental productivity is then

\[
\eta_M(c;E)=\frac{\partial Q_M^*(c;E)}{\partial c}
\]

when the scalarization and differentiability assumptions are meaningful.

The default object remains a vector/Pareto frontier rather than one scalar.

### Distinct limitations

A morphology can stop improving for different reasons:

```text
REPRESENTATION_CEILING
UPDATE_LAW_CEILING
CREDIT_ASSIGNMENT_FAILURE
SEARCH_CONTROL_FAILURE
INFORMATION_LIMIT
VERIFICATION_LIMIT
PLASTICITY_LOSS
STABILITY / FORGETTING FAILURE
COMMUNICATION / TOPOLOGY BOTTLENECK
MAINTENANCE_COST_DOMINATES
HARDWARE / MEMORY-BANDWIDTH REGIME
NO_REUSE_HORIZON
```

Do not collapse these into one “intelligence ceiling.”

### Morphology phase boundary

At matched verified capability, a regime boundary between morphologies `M_i` and `M_j` occurs when their complete lifetime Pareto ordering changes. Under a prospectively frozen scalar price vector this can be written approximately as

\[
C_i(E)=C_j(E).
\]

The research goal is to predict such crossings from ecology coordinates **before** architecture search.

### Candidate ecology coordinates

```text
data volume
noise
smoothness / continuity
algorithmic/compositional structure
exactness requirement
uncertainty / partial observability
feedback density / credit assignment depth
drift / regime-change frequency
revision / revocation frequency
reuse horizon
verification strength
interaction cost
memory bandwidth / accelerator structure
```

These are hypotheses to test, not a finished phase diagram.

---

## Q4 — Can the theory predict a machine-intelligence morphology humans have not already designed?

A visually unusual graph is not a new form of intelligence.

A candidate `M?` must survive reduction against registered known families under bounded **developmental equivalence**:

\[
M_? \not\approx_{E,R,V} M_{neural},M_{symbolic},M_{probabilistic},M_{programmatic},M_{registered\ hybrids}.
\]

### Theory-first discovery protocol

Do not begin with unconstrained novelty search.

1. map known morphology frontiers on a registered ecology family;
2. identify a **phase-diagram hole** where all known families are jointly dominated by a theoretical lower bound / unmet requirement;
3. derive the properties a missing morphology would need;
4. freeze those properties and predicted regime before search;
5. run neutral search over the already-frozen basis/grammar;
6. reduce every survivor against known parent families;
7. replicate on a disjoint ecology where the same theory predicts the advantage;
8. only then use `NEW_MORPHOLOGY_CANDIDATE_AT_SCOPE`.

A candidate that is merely a known hybrid under a new graph encoding is `PARENT_PRODUCT_SUFFICIENT`.

---

## Q5 — Higher-order extension: can the morphology generator itself improve?

Only after Q1–Q4 have nontrivial support, ask whether the laws that generate and develop morphologies can themselves be developmental objects:

\[
(\Gamma_g,U_g) \rightarrow (\Gamma_{g+1},U_{g+1}).
\]

This is a stronger object than ordinary self-modification of one machine.

It asks whether prior experience makes **the generation of future intelligence forms** more efficient, predictive or general.

This connects Track B to #149/#233 governed RSI, but it is deliberately gated behind the lower-level programme.

Allowed early terminal:

```text
META_MORPHOGENESIS_NOT_YET_AUTHORIZED
```

---

# Compact Track-B roadmap

```text
B1  minimal basis / equivalent bases
 ↓
B2  cross-paradigm derivation + developmental acquisition
 ↓
B3  developmental frontier + morphology phase laws
 ↓
B4  theory-predicted missing morphology + blind recovery
 ↓
B5  meta-morphogenesis / generator improvement
```

Track A remains the real-capability programme (language, mathematics, code/tools, science). Track B explains **why forms of intelligence arise and develop**. Track-A domains later become demanding ecologies for Track-B theory, not the definition of the theory itself.
