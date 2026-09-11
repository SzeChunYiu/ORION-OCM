# Morphogenesis Law v1

Status: **provisional formalization / attack surface**.

The handwritten Track-B sketch separates two questions that must remain distinct:

```text
What form of intelligence exists?
How does that form learn once it exists?
```

This document reserves separate objects for those questions.

---

## 1. Morphogenesis versus development

Let `B` be a candidate adaptive generating basis, `E` an ecology, `R` a resource regime, `V` a verification/feedback regime, and `H` inherited developmental/search history.

A morphogenesis operator is provisionally

\[
\Gamma(B,E,R,V,H) \Rightarrow \mu_{\mathcal M}
\]

where `mu_M` is a distribution, archive or Pareto set over candidate morphologies rather than necessarily one deterministic machine.

Once a morphology `M_t` is instantiated, its within-form development is

\[
M_{t+1}=U(M_t,e_t;E,R,V).
\]

`Gamma` and `U` may interact, but they are not identified by definition.

Examples:

```text
fixed neural architecture + SGD:
  Gamma mostly hand-supplied architecture selection
  U = parameter update

NEAT:
  Gamma includes topology/weight evolutionary search
  U may include inherited within-lifetime learning if enabled

AutoML-Zero:
  Gamma searches executable learning algorithms from primitive operations
  U is whichever learned algorithm candidate induces

OCM today:
  much of Gamma is human architecture design
  U includes explicit state/method/controller development
```

This decomposition prevents us from calling ordinary parameter learning “morphogenesis” or ordinary NAS “general intelligence theory.”

---

## 2. What information is allowed into Gamma?

To avoid baking the answer into the generator, `Gamma` receives ecology properties and experience, not target architecture labels.

Allowed:

```text
task samples / generators
feedback/checker interface
resource prices / budgets
observed failures
verified prior history
primitive/basis grammar
```

Forbidden in a blind morphogenesis study:

```text
"build a neural network"
"use Bayesian update"
"add production rule"
architecture class label as fitness feature
protected target winner identity
hand-coded morphology descriptor that directly names the desired family
```

Architecture labels may be applied **afterward** by independent reduction/classification.

---

## 3. Generator quality is not final-task score only

A morphology generator can be evaluated on:

```text
first admissible morphology burden
frontier quality at fixed search cost
diversity of non-equivalent frontiers
prediction calibration
regret versus best registered morphology family
robustness to ecology change
search encoding sensitivity
fraction of generated candidates reducible to known parents
```

This gives a scientific object above “the optimizer found something good.”

---

## 4. Phase-law factorization hypothesis

One possible decomposition is

\[
\Gamma = Search \circ Prior_B \circ Pressure(E,R,V,H)
\]

where:

- `Pressure` maps ecology/resource/verification structure to abstract design pressures;
- `Prior_B` maps pressures into a proposal distribution expressible by the basis;
- `Search` allocates finite evaluation to candidate morphologies.

This is only a hypothesis, but it gives falsifiable subproblems.

### Candidate pressure coordinates

```text
need for distributed statistical compression
need for exact compositionality
need for calibrated uncertainty
need for local revision
need for continual plasticity
need for long inference reuse
need for cheap communication / parallelism
need for strong provenance / external verification
```

A serious phase law predicts changes in these pressures and the resulting morphology frontier before search.

---

## 5. Generator non-uniqueness

Different `Gamma` procedures may induce the same morphology distribution/frontier under registered ecologies.

Therefore Track B should define generator equivalence separately from basis/morphology equivalence.

Candidate relation:

\[
\Gamma_1 \approx_{\mathcal E,R,V,\epsilon} \Gamma_2
\]

when, across a registered ecology family and equal search budgets, their distributions over developmental-equivalence classes and frontier quality are within tolerance.

This prevents implementation details of search from masquerading as a theory of intelligence forms.

---

## 6. Known parent ownership

Major pieces of `Gamma` are already parent-owned:

```text
NEAT / HyperNEAT          topology/encoding evolution
NAS / DARTS               architecture optimization
AutoML-Zero               learning-algorithm search from primitive ops
Genetic Programming       program morphology search
MAP-Elites / QD           archive diverse high-performing forms
Novelty Search            divergent search / stepping stones
POET                      coupled environment-solution evolution
PowerPlay                 solver/task co-development
```

Track-B novelty cannot be `Gamma = evolutionary search` or `Gamma = NAS`.

The possible residual is the **theory linking ecology/resource/verification structure to morphology pressures/frontiers**, plus cross-paradigm recovery from a shared low-level basis.

---

## 7. Immediate tests

### G-0 finite generator identity

On the Stage-C exact grammar, enumerate all morphologies; compare two search procedures to exact census truth. This calibrates generator regret without scientific novelty.

### G-1 blind known-form recovery

Freeze a basis and ecology, hide architecture labels, run a neutral search. Afterward reduce survivors against known tiny neural/symbolic/probabilistic/programmatic target classes.

### G-2 phase reversal

Construct two ecologies with prospectively opposite pressure predictions and test whether frontier membership reverses.

### G-3 generator transfer

Use the same `Gamma` on a held-out ecology coordinate not used to design the generator.

No large-scale search until these finite tests are interpretable.

---

## 8. Long-run extension

Only later allow `Gamma` itself to become developmental state:

\[
\Gamma_{g+1}=G(\Gamma_g,\text{verified morphology-search history}).
\]

This is governed by `META_MORPHOGENESIS_V1.md` and remains unauthorized today.
