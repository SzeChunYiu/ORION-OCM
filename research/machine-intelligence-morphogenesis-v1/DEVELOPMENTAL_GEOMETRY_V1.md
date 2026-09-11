# Developmental geometry v1 — a stronger cross-paradigm object

Status: **candidate unifying formalism; parent-heavy and non-final**.

## Motivation

Once neural, symbolic and programmatic systems are sufficiently expressive, representability often stops being the important difference.

The developmental difference is instead closer to:

```text
which candidate computations have high prior/proposal mass?
which changes are local/cheap?
what feedback can move the system where?
what structure is preserved or destroyed by an update?
what resource must be paid to reach useful future cognition?
```

This motivates characterizing an intelligence morphology by its **developmental geometry**, not only its execution syntax.

## Candidate object

For morphology `M`, define provisionally

\[
\mathcal G_M=(\mathcal H_M,\pi_M,K_M,c_M,V_M),
\]

where:

- `H_M` — legal cognitive/hypothesis/configuration states;
- `pi_M` — prior/proposal/search mass over states/constructions before new evidence;
- `K_M(h' | h,e)` — developmental update/proposal kernel after experience/evidence `e`;
- `c_M(h,h',e)` — raw resource vector for making/considering the transition;
- `V_M` — verification/evidence interface used to evaluate candidate states/actions.

For deterministic learners, `K` is a delta kernel. For search systems it may describe proposal + selection. For explicit program synthesis it can be induced by grammar/search order.

## Induced developmental distance

Under a frozen scalar price vector `w` only when justified, define a path cost

\[
d_M(h_0,h_1)
=\inf_{p:h_0\to h_1}\sum_{(a\to b)\in p} w\cdot c_M(a,b).
\]

Without a price vector retain the Pareto set of path resource vectors.

This gives a precise sense in which two expressively equivalent morphologies can place the same useful computation at very different developmental distance.

## Known morphology interpretations

### Neural / gradient-based

```text
H     parameterized networks / activations / architecture state
pi    initialization + pretraining-induced parameter distribution
K     gradient/optimizer/meta-learned update
c     forward/backward compute, data, optimizer state, communication
geometry often locally smooth in parameter coordinates but highly representation-dependent
```

### Symbolic / production

```text
H     rule bases / symbolic working states
pi    supplied rule vocabulary + chunking/induction bias
K     rule addition/deletion/chunking/rewrite/unification-driven update
c     match/search/agenda/revision costs
```

### Programmatic / synthesis

```text
H     programs/libraries
pi    grammar / prefix-code / library-induced proposal distribution
K     edit/mutation/synthesis/library-learning search
c     candidate generation, execution, verification, library maintenance
```

### Probabilistic

```text
H     distributions / generative programs / latent models
pi    prior
K     conditioning/posterior/inference update or proposal kernel
c     inference/sampling/normalization/approximation cost
```

### OCM-like explicit developmental cognition

```text
H     field + cognitive assets + applicability/control state
pi    retrieval/search ordering induced by history and library
K     verified admission/revision/composition/representation updates
c     search, checker calls, acquisition, storage, maintenance, revision
```

The history-induced search-prior evidence in #323 is naturally a measured change in `pi/K`, not merely a larger memory.

## Parent ownership warning

Nearly every component is parent-owned in some field:

- inductive bias / hypothesis classes;
- Bayesian priors/posteriors;
- PAC/PAC-Bayes;
- meta-learning;
- optimization geometry;
- Markov kernels;
- program-search priors;
- algorithm selection;
- rational metareasoning.

Track B cannot claim `developmental geometry` as novel merely by naming the tuple.

The candidate residual is whether one such cross-paradigm object supports **quantitative bounded compilers and prospective morphology phase predictions** across materially different families.

## Stronger morphology equivalence

Two morphologies should only be called developmentally equivalent if a compiler approximately preserves not just final functions but the developmental geometry:

```text
useful states map to useful states
proposal/update probabilities or ranks are boundedly related
transition resource vectors are bounded
verification semantics are preserved
retention/revision behavior is preserved
```

This is much stronger than Turing equivalence.

## Developmental capital becomes geometry change

Experience creates `K1` search capital when it changes the future geometry so useful new states become easier to reach:

\[
d_{M,t+1}(h, h^*) < d_{M,t}(h,h^*)
\]

or increases useful proposal mass/rank before target success.

`K2` developmental capital changes the process that produces such geometry improvements.

This connects Track B directly to the existing HST developmental state/proposal-distribution framing.

## Morphology phase law in geometry terms

An ecology favors a morphology when its regularities align with that morphology's developmental geometry sufficiently well to overcome build/update/maintenance costs.

Informally:

```text
useful target regularities lie close/high-mass under geometry G_M
AND
lifetime savings exceed development + maintenance
```

Different ecologies can therefore favor different geometries even when all systems are universal in principle.

## New Track-B question

The strongest next formal question becomes:

> Can we define measurable invariants of developmental geometry that predict, before outcome/search, which morphology family will have lower verified acquisition burden on a registered ecology?

Candidate invariants might involve:

```text
useful-descendant proposal mass
local smoothness / neighborhood usefulness
factorization/coupling
credit-assignment depth
library/representation compression
update locality
verification locality
plasticity under accumulated state
```

These must be parent-subtracted individually.

## Current terminal

```text
DEVELOPMENTAL_GEOMETRY_CANDIDATE_FORMALISM
NOT_NOVEL_BY_DEFINITION
PROSPECTIVE_CROSS_PARADIGM_PREDICTION_REQUIRED
```