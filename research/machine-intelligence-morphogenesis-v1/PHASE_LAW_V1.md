# Morphology Phase-Law Programme v1

The strongest Track-B claim should not be “basis B can build architecture X.” It should be a **prospective conditional law** predicting which morphology occupies the capability/resource/development frontier as the ecology changes.

This document freezes the mathematical shape of that programme, not final parameter values or confirmatory predictions.

## 1. Lifecycle objective

For morphology `M` under ecology `E` define a raw resource vector over a registered lifetime:

\[
\mathbf C(M,E,H)=
\mathbf C_{construct}
+\mathbf C_{acquire}
+\sum_{t=1}^{H}\mathbf C_{use,t}
+\mathbf C_{verify}
+\mathbf C_{maint}
+\mathbf C_{revise}
+\mathbf C_{recover}.
\]

Capability/quality is a separate vector `Q(M,E,H)`.

The primary object is a Pareto frontier. A scalar objective

\[
J_{\mathbf p}=\mathbf p\cdot\mathbf C - \lambda Q
\]

is allowed only when price/utility vector `p` and capability treatment are frozen prospectively.

## 2. Morphology frontier

\[
Frontier(B,E,H)
=
\operatorname{Pareto}\{\Phi_E(M): M\in Reach(B,E,H)\}.
\]

A morphology phase boundary exists only when a registered change in ecology/resource parameter changes the nondominated equivalence class(es), not merely when one seed's winning source code changes.

## 3. Arithmetic break-even parent

Many putative “morphology laws” may reduce to ordinary amortisation.

For two matched-capability morphologies A and B with constant per-use difference at a frozen regime:

\[
H^*=
\frac{C_{build,B}-C_{build,A}}
{(c_{use,A}-c_{use,B})-(c_{maint,B}-c_{maint,A})}
\]

when the denominator is positive.

This arithmetic is parent-owned. Track B novelty cannot be “one architecture pays after enough uses.” The higher question is whether the theory predicts **which structural representation/update law changes those terms** as ecology coordinates change, and whether those predictions transfer to unseen ecologies.

## 4. Provisional phase hypotheses — exploratory only

These are intentionally hypotheses to derive, falsify or delete.

### PH-N: amortized parametric regime

Candidate conditions:

```text
high data volume
smooth/statistical regularity
large reuse horizon
high tolerance for approximate internal representation
low/moderate revision pressure
low per-inference latency budget
```

Candidate prediction: parametric/neural-like morphology becomes nondominated because high construction/training cost is amortized by cheap repeated inference/generalization.

**Strong parents:** statistical learning theory, neural scaling, amortized inference.

### PH-S: explicit compositional regime

Candidate conditions:

```text
sparse exact structure
strong compositionality
strong exact verifier
low tolerance for semantic error
reusable symbolic substructure
meaningful local revision
```

Candidate prediction: programmatic/symbolic morphology gains because exact reusable operations and verification dominate dense approximate amortization.

**Strong parents:** program synthesis, theorem proving, production systems, library learning.

### PH-P: uncertainty-dominant regime

Candidate conditions:

```text
partial observability
small data
expensive observations
uncertain latent causes
value of information matters
```

Candidate prediction: explicit probabilistic/belief-state morphology or equivalent inference machinery becomes nondominated.

**Strong parents:** Bayesian decision theory, POMDPs, active learning, probabilistic programming.

### PH-H: mixed-regime hybrid

Candidate conditions:

```text
large noisy perception / semantic input
+
exact compositional decisions or formal verification
+
heterogeneous tools
```

Candidate prediction: a hybrid morphology may dominate pure forms.

**Critical hostile:** strongest ordinary parent product may already explain the frontier (`PARENT_PRODUCT_SUFFICIENT`).

### PH-D: high-drift / high-revision regime

Candidate conditions:

```text
frequent regime changes
support revocation
short reuse horizon
high retraining/rebuild cost
```

Candidate prediction: morphology preference shifts toward cheap local adaptation/revision, potentially away from systems whose competence is expensive to update globally.

**Critical hostile:** modern continual learning/adapters/caches may remove the alleged explicit-system advantage.

## 5. Required derivation before confirmatory tests

No phase hypothesis above becomes an E3 prediction until it has:

- an explicit cost/development model;
- at least one parent theorem/mechanism explaining its expected direction;
- a nontrivial competing prediction;
- a phase variable measurable without architecture labels;
- a predicted transition interval/direction;
- a parent-favoring control;
- a resource-price sensitivity analysis frozen in advance.

## 6. Search-independent validation

Where possible, test phase laws first on **hand-instantiated strong parent morphologies** before relying on architecture search.

For example:

```text
known strong neural learner
vs strong program/library learner
vs strong probabilistic learner
vs strongest practical hybrid
```

under deliberately parameterized ecologies.

If no frontier transition is observed among strong known parents, launching a giant neutral morphology search is low-value.

## 7. Blind-recovery gate

After a phase law is calibrated but before claiming morphogenesis:

1. freeze basis and construction grammar;
2. remove architecture-family labels/macros;
3. freeze ecology and predicted morphology class;
4. run at least two search encodings/algorithms;
5. classify outputs using the pre-frozen bounded equivalence contract;
6. use a disjoint ecology family for confirmatory recovery.

Positive terminal:

`PROSPECTIVE_MORPHOLOGY_PHASE_PREDICTION_SUPPORTED_AT_SCOPE`

Important negatives:

```text
NO_FRONTIER_TRANSITION
ECOLOGY_COORDINATES_DO_NOT_PREDICT_FRONTIER
SEARCH_ENCODING_DETERMINES_MORPHOLOGY
PARENT_PRODUCT_SUFFICIENT
PRICE_VECTOR_ARTIFACT
NON_IDENTIFIABLE_AT_CURRENT_RESOLUTION
```

## 8. Upward claim ladder for Track B

```text
B0  finite basis/equivalence machinery calibrated
B1  known morphologies have bounded developmental compilations
B2  architecture-specific structure can be acquired from neutral basis
B3  one morphology transition predicted prospectively
B4  phase law replicates on disjoint ecology/implementation
B5  same law spans >=3 known morphology families
B6  new non-equivalent morphology predicted/discovered with new frontier region
B7  architecture-independent generative principle of machine intelligence supported
```

No rung is earned by vocabulary alone.