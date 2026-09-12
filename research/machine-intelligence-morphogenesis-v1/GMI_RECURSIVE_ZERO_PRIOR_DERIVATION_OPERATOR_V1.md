# GMI Recursive Zero-Prior Derivation Operator v1

Status: **FOUNDATIONAL DERIVATION PROCEDURE / COMPLETENESS TARGET**

Status date: 2026-09-12.

Purpose:

> Replace architecture-by-architecture post-hoc explanation with one recursive procedure that derives candidate machine-intelligence forms from obligations, information structure and lifecycle burden. Known families are calibration targets; unknown families use the same operator unchanged.

---

# 1. Inputs

A derivation instance contains no architecture/family name. It contains only

\[
Z_0=(O,E,D,J,V,C,P,H,\mathcal G_0),
\]

where:

```text
O   protected semantic obligation
E   ecology/distribution family
D   legal development information
J   interventions/teaching actions
V   verifier/evidence rules
C   constitution/admissibility constraints
P   resource/substrate prices and budgets
H   developmental horizon/history structure
G0  low-level carrier/operator grammar
```

---

# 2. Step R1 — derive semantic distinctions

Construct or approximate the target semantic/developmental quotient

\[
q_O:h\mapsto S_O.
\]

Atomic questions:

```text
what histories/worlds must remain distinguishable?
which distinctions may be quotiented away?
which distinctions are only needed under intervention/history/provenance queries?
what approximation tolerance is legal?
```

Output:

```text
semantic state cardinality/information bounds
history dependence
causal/interventional residuals
retention/lineage requirements
```

If the quotient is unidentifiable from legal development information, open an information-acquisition/intervention gap rather than guessing an architecture.

---

# 3. Step R2 — derive state-organization lower bounds

From `S_O`, derive lower bounds on candidate state organization:

```text
memory bits / state count
predictive residual information
communication lower bound
rollback information
history/lineage state
precision/exactness
routing/dependency edges
constructor/developmental closure where applicable
```

No realization family is chosen yet.

---

# 4. Step R3 — derive reusable structure coordinates

Measure or bound structure that can lower realization burden:

\[
X=(c_{comp},s_{sym},d_{dep},v_{dep},h_{state},r_{pred},u_{local},m_{mode},e_{exact},...)
\]

where examples include:

```text
compositionality
symmetry/equivariance
locality
predictive-target overlap
state/predictive dimension
dependency density and variability
mode heterogeneity
update locality
uncertainty/latent ambiguity
exactness/verifier availability
query reuse
regime-change hazard
```

Every coordinate must be pre-outcome and bounded against hidden world-ID leakage.

---

# 5. Step R4 — generate carrier/operator candidates

Using only `G0`, generate candidate realization classes such as:

```text
shared coefficient/basis state
explicit exemplar memory
probability/belief state
symbolic/program/constraint state
search/frontier state
recurrent/dynamical state
local/shared equivariant computation
dynamic routing
conditional heterogeneous modules
external residual state
low-rank residual update
verified proposal/admission
compiled serving state
collective/distributed state
morphology-changing state
```

The grammar may combine primitives. It must not contain hidden macros named after the held-out family.

---

# 6. Step R5 — derive candidate lower and upper burden bounds

For each candidate `M`, derive

\[
LB_M(Z_0)\le \rho^*_M(Z_0)\le UB_M(Z_0)
\]

where possible.

The burden vector includes:

```text
development compute
data/labels/interventions
search/tuning
state/memory
communication
serve compute/latency
updates/maintenance
verification
human effort
precision/energy
morphology/compilation cost
failed candidates
```

Candidate families with a lower bound already dominated by another candidate's upper bound may be pruned at that cell.

---

# 7. Step R6 — solve the morphology/domain frontier

Predict the property-level frontier

\[
\mathcal F^*(Z_0)
=
\operatorname{ParetoMin}_{M\in\mathcal G_0}
\left(L_O(M),\rho(M)\right).
\]

Do not require a unique architecture. Output implementation-invariant properties:

```text
state carrier
factorization/topology
routing type
memory placement
update locality/rank
verification/authority lifecycle
search vs compilation
adaptation timescale
precision/substrate requirements
```

---

# 8. Step R7 — derive negative twins before search

For each predicted mechanism, intervene on the causal coordinate that supposedly selected it.

Examples:

```text
symmetry -> break symmetry
variable dependency -> freeze dependency graph
volatile independent facts -> replace with smooth shared law
uncertainty -> fully observe latent state
long reuse -> reduce reuse
local updates -> globalize updates
mode heterogeneity -> homogenize modes
strong verifier -> remove/deprice/reprice verifier
history demand -> remove historical queries
```

Freeze the predicted morphology change before neutral search.

---

# 9. Step R8 — neutral recovery

Run architecture-neutral search under fixed budget.

Success condition:

> recovered frontier realizations contain the frozen property vector, modulo implementation-equivalent remints.

Historical family source code need not be recovered.

---

# 10. Step R9 — known-family comparison

Only after prediction/search freeze reveal the held-out known family `F`.

Classify:

```text
MATCH
    F lies in predicted property-equivalence neighborhood.

BETTER-ALTERNATIVE
    GMI found a different realization with equal/better protected frontier; historical F is not uniquely expected.

THEORY-RED
    F is genuinely frontier on P but its key property was not predicted.

SEARCH-RED
    property was predicted but neutral search failed despite demonstrated grammar expressibility.

MEASUREMENT-RED
    required causal coordinate could not be estimated reliably from legal pre-outcome information.
```

---

# 11. Step R10 — recursive residual localization

For every RED, find the smallest failed atom.

Examples:

```text
wrong semantic quotient -> repair R1
missing lower bound -> repair R2
missing ecology coordinate -> repair R3
inadequate primitive grammar -> repair R4
wrong resource accounting -> repair R5
wrong response law -> repair R6
wrong causal hypothesis -> repair R7
search bias -> repair R8
```

Do not patch by adding the hidden family identity.

After repair, retire the old protected set and generate a fresh one.

---

# 12. Recursion fixed point

For registered known-family set `K`, define derivation closure when every `F in K` is one of:

```text
DERIVED
    property vector predicted and neutrally recovered;

REDUCED
    family is implementation-equivalent/dominated by another derived property class at the registered scope;

OUT-OF-SCOPE
    required carrier/operator/resource lies outside declared grammar/scope, explicitly recorded.
```

No `THEORY-RED`, `MEASUREMENT-RED`, or untyped gap may remain.

Quantitative closure additionally requires held-family crossover prediction for all morphology claims.

---

# 13. Why this can discover unknown forms

The same operator does not reference known architecture names. Once calibrated on known forms, applying R1-R8 to a new ecology can yield a property complex absent from the known-family library.

A candidate unknown form receives stronger status only if:

1. it was generated by R1-R7 before implementation;
2. neutral R8 search recovers it;
3. known-family/parent comparison cannot reduce it within registered burden;
4. it recurs on fresh ecologies/remints/search encodings.

Thus known-form derivability is not separate from unknown-form discovery; it is the calibration proof that the same generator works before novelty claims.

---

# 14. Immediate no-gap target

Apply the operator recursively to the registered family inventory until:

```text
linear/GLM
basis/kernel
exemplar/kNN
trees/boosting
Bayesian/graphical belief
symbolic/constraint/program
search/planning
finite/recurrent/state-space
MLP/CNN/GNN/RNN/Transformer
sparse attention/MoE
RAG/external memory
adapters/low-rank update
ensembles
verifier-gated search
model-based/model-free control
autoregressive/diffusion/flow/latent generation
continual learning
test-time search/reasoning
tool/solver systems
```

all reach derivation closure at the registered scope.

Desired terminal:

`KNOWN_FORM_RECURSIVE_ZERO_PRIOR_FIXED_POINT_GREEN`.
