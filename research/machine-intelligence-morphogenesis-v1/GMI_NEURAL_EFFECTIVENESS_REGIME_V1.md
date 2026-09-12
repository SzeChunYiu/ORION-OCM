# GMI Neural Effectiveness Regime v1

Status: **PROSPECTIVE MECHANISM-LEVEL HYPOTHESIS — NOT A UNIVERSAL NEURAL OPTIMALITY CLAIM**

Refs: `GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md`, `GMI_NEURAL_PREDICTION_TO_INTELLIGENCE_THEOREMS_V1.md`, `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`, `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`.

## 0. Purpose

The neural derivation explains the causal mechanisms by which neural systems can be effective.

This document adds the missing prospective step:

> **Which measurable ecology/context properties should activate each neural advantage, and which interventions should remove it?**

A theory that only says "deep networks are expressive, optimize well, generalize and scale" after seeing success is too weak.

The neural-effectiveness claim is therefore decomposed into independent mechanism-response laws.

---

# 1. Neural effectiveness is a frontier statement

For obligation `O`, development protocol `D`, context/resource prices `P`, and candidate family set `M_avail`, let

\[
\mathcal F(O,D,P,\mathcal M_{avail})
\]

be the protected capability/resource Pareto frontier.

A neural family `N` is "good" only in the comparative sense that some developed neural realization lies on or near this frontier.

The theory does **not** define neural quality by:

```text
parameter count;
training loss;
benchmark score without burden;
architectural popularity;
biological analogy.
```

---

# 2. Ecology/context descriptors used only as mechanism probes

The canonical obligation signature remains `Xi_obl^(1)` and the separate exogenous context `P`.

For neural mechanism testing, define additional prospectively measured **probe descriptors**. These are not claimed as a new universal sufficient signature.

## 2.1 `c_comp` — compositional structure

Measures whether the target computation/distribution factorizes into reusable low-arity or hierarchical submaps.

Possible estimators:

```text
known synthetic composition graph;
minimal circuit/treewidth proxy;
conditional-dependence factorization;
intervention-defined subproblem reuse;
description-length gap between compositional and flat models.
```

## 2.2 `s_share` — repeated/shared transformation structure

Measures whether the same local transformation is useful across positions, locations, examples or tasks.

Examples:

```text
translation equivariance in images;
repeated token-processing rules;
exchangeable/set structure;
repeated motifs/subroutines;
shared latent factors across tasks.
```

## 2.3 `d_eff` — effective predictive/task dimension

Measures the number/complexity of degrees of freedom needed to explain protected variation, not raw input dimension.

Possible proxies include:

```text
spectral/effective rank;
latent dimension under registered generative worlds;
manifold dimension;
rate-distortion or approximation curves;
minimum description length under neutral model classes.
```

## 2.4 `q_smooth` — local regularity / interpolability

Measures whether nearby or representation-near states tend to have related protected outputs/predictive laws.

This can support distributed approximation/interpolation.

## 2.5 `i_pred` — predictive overlap with target semantics

Measures how much target semantic state is determined by the pretraining predictive quotient.

Ideal exact form:

\[
q_O=g\circ q_{pred}.
\]

Approximate forms use a registered transfer modulus or residual target information after conditioning on predictive state.

## 2.6 `f_dense` — feedback density and gradient usability

Derived from the external feedback contract `gamma_F` plus a morphology response measurement.

Measures how often development receives informative differentiable or otherwise gradient-compatible constraints per unit data/interaction.

## 2.7 `r_reuse` — reuse before invalidation

Equivalent in spirit to `rho_use`: expected number of protected serving uses/tasks that can reuse a trained representation before major invalidation/retraining.

## 2.8 `x_exact` — exactness / authority burden

Measures how much of the obligation is governed by hard exact/provenance/branching/verifier constraints rather than approximate statistical loss.

This is not one scalar in canonical GMI; for this probe it summarizes the fraction/severity of hard obligations.

## 2.9 `u_local` — update locality / interference sensitivity

Measures how often updates should change a small semantic region while leaving the rest fixed under strict retention.

Related to `Delta_U`, `lambda_R`, drift and local verification.

## 2.10 `p_tensor` — substrate advantage for neural primitives

A context-side descriptor derived from `P`, comparing price/latency/energy of dense tensor operations and communication against alternative primitives.

---

# 3. NE-R1 — depth advantage tracks compositional structure

## Hypothesis

Holding semantic tolerance, data access, optimizer effort and substrate accounting matched, the burden advantage of deeper over shallower neural realizations should increase with `c_comp`.

Schematic response:

\[
\Delta B_{depth}
=
B_{shallow}-B_{deep}
\]

with

\[
\frac{\partial\Delta B_{depth}}{\partial c_{comp}}>0
\]

inside the registered regime.

This is not asserted globally or monotonically outside scope.

## Positive worlds

```text
hierarchical compositions;
reusable local subfunctions;
structured sequence programs;
multiscale perception.
```

## Negative twin

Destroy/re-randomize the composition while preserving input dimension, label entropy and sample count.

Predicted result:

```text
depth-specific parameter/sample advantage shrinks.
```

Parent support: depth-separation and compositional approximation theory.

---

# 4. NE-R2 — parameter sharing advantage tracks repeated transformation structure

Let

\[
\Delta B_{share}
=
B_{unshared}-B_{shared}.
\]

Prospective prediction:

\[
\Delta B_{share}
\]

increases with `s_share` under matched expressivity/search budget.

Negative twin:

```text
assign unrelated local laws to positions while preserving marginal difficulty.
```

Predicted result:

```text
weight-sharing/sample-efficiency advantage decreases or reverses.
```

This applies to convolutional, recurrent, attention-based and other shared parameterizations where the same learned transformation is reused.

---

# 5. NE-R3 — representation-learning advantage tracks latent compression/reuse

Define protected representation advantage

\[
\Delta B_{repr}
=
B(best\ downstream\ from\ raw\ observations)
-
B(best\ downstream\ from\ learned\ representation).
\]

Prediction:

`Delta B_repr` is large when:

```text
raw dimension is high;
effective target/predictive dimension is much lower;
multiple outputs/tasks depend on shared latent factors;
representation can suppress nuisance variation without merging protected distinctions.
```

Hostile:

```text
one independent label bit per raw feature / no reusable latent factor.
```

Prediction: reusable representation advantage collapses.

---

# 6. NE-R4 — predictive pretraining transfer tracks quotient overlap

Let `R_pred` be an exact or approximate predictive representation from a development stream.

Define target residual after predictive state

\[
I_{res}(O\mid S_{pred})
\]

using a registered information/description/residual-prediction measure.

Prediction:

```text
smaller residual target information
=> lower downstream sample/compute burden after pretraining.
```

Exact endpoint:

\[
I_{res}=0
\]

when

\[
q_O=g\circ q_{pred}.
\]

Negative twins:

```text
causal intervention distinction absent from passive data;
provenance distinction with identical text statistics;
historical lineage distinction absent from serving stream;
new task label statistically independent of predictive state.
```

Prediction:

```text
pretraining transfer drops until new information is supplied.
```

This is the strongest GMI explanation of why foundation-model pretraining transfers unevenly across tasks.

---

# 7. NE-R5 — gradient-development advantage tracks feedback density and alignment

Let `g_N(gamma_F)` measure how much protected improvement the neural update extracts from the external feedback contract.

Prediction:

Neural gradient development is favored when:

```text
many examples/positions provide loss constraints;
loss is differentiable through most of the realization;
gradient direction correlates with protected semantic improvement;
feedback is frequent enough to overcome noise;
shared parameters allow one signal to improve many future cases.
```

Two independent interventions are required:

### Density intervention

Reduce number of informative constraints while preserving target family.

Prediction: training burden rises.

### Alignment intervention

Keep gradients dense but rotate/misalign the proxy objective relative to protected semantics.

Prediction:

```text
optimization remains computationally easy;
protected adequacy degrades.
```

This separates cheap credit assignment from correct objective choice.

---

# 8. NE-R6 — overparameterization advantage is primarily a reachability response

Let `m` be implementation parameterization scale with target semantic class held fixed.

Prediction:

There may exist a regime in which increasing `m`:

```text
reduces optimization time/failure probability;
improves robustness to initialization;
changes effective implicit bias;
```

before resource/storage/serving costs dominate.

The theory predicts a nontrivial frontier, not monotone goodness with parameter count.

Hostile:

Compare models matched for achieved function/protected risk but different redundant parameterization.

Any remaining advantage must appear in development/search robustness or substrate efficiency, not be credited as additional semantic intelligence.

---

# 9. NE-R7 — amortization advantage tracks reuse before invalidation

For neural `N` and alternative `A`, define

\[
\Delta C_0=C_{train}^N-C_{build}^A
\]

and per-use saving

\[
\Delta c=c_{query}^A-c_{query}^N.
\]

If `Delta c > 0`, neural lifecycle advantage activates after

\[
r_{reuse}
>
\frac{\Delta C_0}{\Delta c}.
\]

Prediction:

```text
same learned system
+ same per-query quality
+ sharply lower reuse horizon
=> neural frontier advantage should shrink or reverse.
```

This is especially important for large pretraining systems whose development cost is enormous but whose state is reused billions of times or across many tasks.

---

# 10. NE-R8 — tensor-substrate advantage is exogenous and reversible

Define

\[
p_{tensor}
=
\frac{cost(registered\ alternative\ primitive\ bundle)}
     {cost(neural\ tensor\ primitive\ bundle)}
\]

under matched semantic work.

Prediction:

As `p_tensor` increases, tensor-heavy neural realizations gain frontier advantage; as it decreases, the advantage can shrink.

This must be tested by resource repricing/simulation or alternative hardware, not inferred from present GPU economics.

Consequently:

```text
neural success today
!=
substrate-independent proof of neural optimality.
```

---

# 11. NE-R9 — strict exactness and lineage reduce pure-neural dominance

As `x_exact` increases, plain approximate neural serving should increasingly require composition with exact mechanisms.

Examples:

```text
proof checker;
transaction/version store;
source/provenance ledger;
exact arithmetic kernel;
constraint solver;
certified deletion/replay mechanism.
```

Prediction:

```text
hybrid frontier occupancy increases with exactness/authority burden.
```

This is a positive morphology prediction, not merely a limitation statement.

---

# 12. NE-R10 — local revision + strict retention favors modular/versioned augmentation

As update locality `u_local` and retention/lineage demand rise, globally entangled monolithic weight updates face increasing interference and revalidation burden.

Prediction:

Plain monolithic neural realization loses frontier share to mechanisms adding some combination of:

```text
replay;
parameter isolation/adapters;
modularity;
sparse routing;
external memory;
versioned checkpoints;
local compilation;
retrieval;
exact persistent state.
```

This connects neural theory directly back to the wider GMI mechanism lattice and VLC programme.

---

# 13. NE-R11 — scale headroom tracks unresolved reusable structure

Let protected loss decompose across modes/features ordered by difficulty or frequency.

Scaling remains productive while additional data/model/compute can resolve obligation-relevant modes not already captured and the marginal semantic gain exceeds marginal burden.

Operationally define scale headroom

\[
H_{scale}(r)
=-\frac{dR_{protected}}{d\log r}
\]

for resource coordinate `r` over a registered interval.

Prediction:

`H_scale` is large when:

```text
many unresolved predictive/semantic modes remain;
training data contains evidence about them;
architecture can represent them;
optimization can reach them;
protected evaluation rewards them.
```

It falls when any bottleneck saturates.

This converts "bigger is better" into a measurable response condition.

---

# 14. NE-R12 — neural-friendly regime conjunction

A broad neural system is predicted to be especially frontier-competitive when the ecology/context jointly has:

```text
high c_comp      reusable hierarchical/compositional structure
high s_share     repeated transformations/symmetries
moderate/low d_eff relative to raw observation complexity
high q_smooth    useful regularity/interpolation
high i_pred      pretraining predictive state overlaps target semantics
high f_dense     abundant aligned learning signal
high r_reuse     large amortization horizon
moderate x_exact approximate semantics or cheap exact external checks
moderate u_local global/batch updates acceptable or modular augmentations available
high p_tensor    dense tensor compute relatively cheap
```

The hypothesis is conjunctive and mechanism-factorized.

A neural system may still succeed when one descriptor is unfavorable, but the theory predicts which compensating mechanism must carry the burden.

Example:

```text
high exactness
+ high neural predictive value
=> neural proposal engine + exact verifier hybrid,
not plain neural authority.
```

---

# 15. Why natural-language and perception tasks often land near this regime

This section is a hypothesis to be measured, not assumed.

Many real perception/language domains appear to contain:

```text
massive repeated local/global regularities;
shared latent causes across examples;
hierarchical composition;
large raw observations with lower-dimensional/task-relevant structure;
enormous passive/self-supervised data streams;
many repeated future queries/tasks;
substantial tolerance for approximate probabilistic prediction before final verification;
hardware that makes tensor primitives extremely cheap.
```

If those measurements hold, the theory predicts neural competitiveness without invoking a neuron-specific essence of intelligence.

The same theory predicts weaker dominance in domains where these properties are absent.

---

# 16. Modern language-model prediction

For autoregressive language modeling, the strongest proposed causal chain is:

```text
large textual/code/multimodal stream
-> dense next-step supervision
-> predictive quotient pressure
-> preservation of latent distinctions affecting continuations
-> shared deep representation
-> attention-based context routing
-> broad downstream projections from predictive state
-> enormous cross-task/query reuse
-> accelerator-efficient serving/training
```

The chain breaks where target distinctions are not in the passive predictive quotient or where exact authority/lineage is required.

This predicts the practical value of:

```text
retrieval;
tool use;
execution;
verifiers;
interactive environment data;
post-training with action/feedback;
external memory/versioning.
```

as mechanisms that add missing state or exactness rather than as ad hoc patches.

---

# 17. Required matched experiments

Each response law must be tested by an intervention that changes the hypothesized cause while preserving obvious confounders.

| Law | Primary intervention | Protected outcome |
|---|---|---|
| NE-R1 | compositional structure | deep-vs-shallow burden gap |
| NE-R2 | repeated/shared law | shared-vs-unshared burden gap |
| NE-R3 | latent factor reuse | representation downstream burden |
| NE-R4 | predictive-target quotient overlap | transfer sample/compute burden |
| NE-R5 | feedback density/alignment | optimization vs protected risk |
| NE-R6 | redundant parameterization | reachability/optimization robustness |
| NE-R7 | reuse horizon | lifecycle frontier crossover |
| NE-R8 | tensor primitive prices | frontier membership |
| NE-R9 | exactness/authority burden | hybrid vs pure-neural frontier share |
| NE-R10 | local update + retention | interference/revalidation burden |
| NE-R11 | unresolved structure / scale | protected marginal return to scale |

Family-held-out and implementation-equivalent comparisons are required where feasible.

---

# 18. Kill conditions

The proposed neural explanation must narrow or fail if protected experiments show any of the following robustly:

```text
DEPTH_ADVANTAGE_INVARIANT_TO_COMPOSITION_STRUCTURE
SHARING_ADVANTAGE_WITHOUT_SHARED_STRUCTURE
PREDICTIVE_TRANSFER_INDEPENDENT_OF_TARGET_QUOTIENT_OVERLAP
AMORTIZATION_ADVANTAGE_INDEPENDENT_OF_REUSE_HORIZON
NEURAL_FRONTIER_INVARIANT_TO_TENSOR_RESOURCE_PRICES
PURE_NEURAL_DOMINANCE_INVARIANT_TO_EXACTNESS_LINEAGE_BURDEN
LOCAL_UPDATE_RETENTION_DOES_NOT_CHANGE_INTERFERENCE_OR_ARCHITECTURE_PRESSURE
SCALE_IMPROVEMENT_PERSISTS_WITH_NO_ADDITIONAL_TARGET_INFORMATION_OR_RESOLUTION
```

A single failed law need not kill all neural theory; it kills the corresponding mechanism explanation.

---

# 19. Stronger final explanation

The final GMI answer to "why can neural networks be so good?" is now prospective:

> Neural networks become unusually competitive when the obligation contains large amounts of reusable, compositional, statistically regular structure that can be captured by a flexible distributed function approximator; when the development stream supplies dense feedback aligned with protected semantics; when repeated serving/tasks amortize the development cost; and when the substrate makes the resulting tensor computation cheap. Depth, sharing, attention, overparameterization, pretraining and scale are not independent magic ingredients: each is predicted to help only when its corresponding ecology/resource condition is present.

This explanation also predicts the reversal regimes and the need for hybrid mechanisms.

That is the required standard for calling the account a theory rather than an after-the-fact description.
