# Developmental Frontier v1

Status: **formal target + empirical programme**, not an established law.

This document hardens the question “what limits a form of intelligence, and why can one morphology dominate another?” into measurable objects.

---

## 1. Do not define intelligence as one scalar

For morphology `M`, ecology `E`, developmental history `H` and complete resource vector `b`, let

\[
Q(M,E,H,b)
\]

be the verified capability vector reachable under the legal development process.

The primary object is the nondominated set

\[
\mathcal F_M(E,H)
=
\operatorname{Pareto}\{(b,Q): Q \text{ is legally reachable by } M\}.
\]

Examples of capability coordinates:

```text
verified task success / coverage
calibration / uncertainty quality
retention
negative-transfer refusal
revision correctness
cross-family transfer
future acquisition capability
```

Examples of resource coordinates:

```text
new information / examples
training / acquisition work
inference / search work
verification work
interaction / tool calls
persistent bytes
active bytes
index / maintenance work
revision / retraining work
wall / CPU / GPU / energy
human instruction where relevant
```

No post-hoc weighted “intelligence score.”

---

## 2. Scalar developmental productivity is secondary

If and only if a price vector `lambda` and quality coordinate/utility have been prospectively fixed, define scalar lifetime cost

\[
c=\lambda^T b.
\]

Let

\[
Q_M^*(c;E,H)
\]

be the best verified quality reachable under cost `c`.

Then local developmental productivity is

\[
\eta_M(c;E,H)
=
\frac{\partial Q_M^*}{\partial c}
\]

where a derivative is meaningful. For discrete development use a finite difference:

\[
\eta_M(c_1,c_2)
=
\frac{Q_M^*(c_2)-Q_M^*(c_1)}{c_2-c_1}.
\]

This formalizes the sketch quantity `d(development)/d(cost)` without pretending development is intrinsically one-dimensional.

---

## 3. Separate four failure modes that look like a “ceiling”

### 3.1 Expressive / representation ceiling

There exists a required task distinction or transformation outside registered bounded reach:

\[
\tau \notin Reach_B(M,E,C).
\]

More search cannot solve it without representation/operator expansion.

### 3.2 Search/update inefficiency

A solution is expressible, but the current update/search law makes the expected first useful acquisition too expensive.

### 3.3 Plasticity ceiling

The system remains competent but loses ability to acquire fresh capability efficiently as history grows.

Measure on matched fresh-task families:

\[
P_t(b)=E[\Delta Q_{fresh}\mid \text{additional budget } b,H_t].
\]

`P_t` falling while representational reach remains sufficient is a plasticity problem, not an expressivity problem.

### 3.4 Stability / retention ceiling

New competence can still be acquired, but doing so destroys old competence or produces unacceptable negative transfer.

Plasticity and stability must be reported separately.

---

## 4. Morphology dominance

Morphology `M_i` Pareto-dominates `M_j` on ecology `E` at registered scope only if, for matched capability obligations, `M_i` is no worse on every registered resource/risk coordinate and strictly better on at least one.

Most likely outcome is **conditional dominance**, not one universal winner.

Under a prospectively frozen scalar price vector, a two-family phase boundary can be written as

\[
C_i(E)=C_j(E).
\]

In the vector formulation, the relevant object is where the nondominated frontier changes membership.

A phase law is therefore a mapping

\[
\Phi:E\rightarrow\operatorname{FrontierClasses}(E)
\]

or probabilistically

\[
P(M \in \text{frontier}\mid E,R,V).
\]

---

## 5. Candidate ecology axes

Every axis below has a strong parent literature and is initially a hypothesis generator, not an OCM novelty claim.

### Statistical structure

```text
sample volume
noise
smoothness / continuity
intrinsic dimension
shared latent representation across tasks
```

### Algorithmic structure

```text
compositionality
exact reusable subroutines
program length / description length
branching/search depth
availability of exact semantics
```

### Learning signal

```text
feedback density
differentiability / local credit assignment
supervision quality
delayed reward / sparse feedback
counterfactual observability
```

### Environment dynamics

```text
drift rate
regime change
revision / revocation frequency
task relatedness
harmful-transfer frequency
reuse horizon
```

### Verification / risk

```text
formal checker availability
cost of false positive
need for provenance / traceability
need for exact local correction
```

### Physical resource regime

```text
matrix-multiply throughput
memory bandwidth
random-access latency
communication cost
parallelism
accelerator availability
energy price
```

Architecture performance must be interpreted relative to physical resource prices; hardware is part of `R`, not an invisible constant.

---

## 6. Parent results that already constrain the phase theory

Track B must absorb rather than rename these results:

- **No Free Lunch:** no universal winner over unrestricted problem classes; phase laws require structured ecologies.
- **Baxter / multitask representation-learning theory:** related-task environments can make learned inductive bias / representation advantageous under explicit conditions.
- **Information Bottleneck / rate-distortion:** useful representation can be framed as preserving task-relevant information under capacity cost.
- **Resource-rational analysis / rational metareasoning:** mechanisms should be understood relative to computational costs, not only ideal output quality.
- **Neural scaling laws:** in major language-model regimes, loss follows systematic empirical scaling with model/data/compute; this is evidence for a large region where parametric neural morphology has favorable scaling, not universal optimality.
- **Compute-optimal scaling (Chinchilla):** even within one morphology, the best parameter/data allocation is resource-regime dependent.
- **Loss of plasticity in deep continual learning:** long-lived neural development can degrade without diversity-preserving mechanisms; this is a direct Track-B morphology-limit parent.
- **Specialized neural hardware:** matrix-multiply-friendly neural workloads receive large system-level acceleration; morphology comparisons that ignore hardware co-design are incomplete.

---

## 7. Provisional phase hypotheses

These are **registered hypotheses to attack**, not accepted laws.

### PH-N — parametric/neural region

Predicted to improve relative to explicit search-heavy forms when all/most are true:

```text
large repeated dataset
smooth/statistical regularity
useful shared distributed representation
dense or differentiable credit assignment
very large future inference horizon
hardware strongly rewards dense tensor computation
exact local revision is weakly weighted
```

### PH-S — symbolic/programmatic region

Predicted to improve when:

```text
exact compositional rules are short
verification is exact and important
solutions reuse discrete subroutines
local revision / provenance is frequent or valuable
search space can be pruned by structure
training data are sparse relative to rule structure
```

### PH-P — probabilistic region

Predicted to improve when:

```text
uncertainty is central
observations are costly
sample size is small/moderate
posterior information directly controls decisions/experiments
explicit calibrated uncertainty is valuable
```

### PH-H — hybrid region

Predicted where statistical amortization and exact compositional/verified operations are both material and neither pure morphology has a complete Pareto advantage.

A “hybrid” claim is only interesting if it survives reduction to an ordinary parent product.

---

## 8. Prospective phase-law protocol

1. choose 2–4 ecology axes with independent controls;
2. define several morphology families using faithful parent implementations;
3. freeze resource meters and capability constraints;
4. measure development/frontier only on development ecologies;
5. fit a phase model without protected ecologies;
6. freeze quantitative region/boundary predictions;
7. evaluate on disjoint ecologies;
8. include parent-favoring controls and regime reversals;
9. report boundary misses as theory failures;
10. only after predictive success allow neutral morphology search in unexplained regions.

Valid terminals:

```text
MORPHOLOGY_PHASE_BOUNDARY_PREDICTED_AT_SCOPE
CONDITIONAL_MORPHOLOGY_DOMINANCE_SUPPORTED
PARETO_FAMILY_NO_UNIVERSAL_WINNER
ECOLOGY_COORDINATES_DO_NOT_PREDICT_FRONTIER
HARDWARE_REGIME_DOMINATES
SEARCH_ENCODING_DOMINATES
PARENT_PRODUCT_SUFFICIENT
CANNOT_CHECK_<reason>
```
