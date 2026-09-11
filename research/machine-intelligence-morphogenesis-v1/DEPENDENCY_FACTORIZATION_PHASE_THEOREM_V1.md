# Dependency-aligned factorization phase theorem v1

Status: **elementary exact phase relation + parent reduction.**

## Model

Let `V` be a finite set of variables/subproblems. An ecology is a weighted undirected dependency graph with weights

\[
w_{ij}=P(\text{a future task requires interaction } i\leftrightarrow j),
\qquad \sum_{i<j}w_{ij}=1.
\]

A candidate morphology factorization is a partition `Pi` of `V` into modules.

Let:

- `I(Pi)` = number/cost of internal connections built inside modules;
- `cut_w(Pi)` = total ecology probability mass crossing module boundaries;
- `lambda` = price per internal connection/build obligation;
- `gamma` = extra execution/communication/reconfiguration cost when a required dependency crosses modules;
- `H` = lifetime task horizon.

Define

\[
C(\Pi)=\lambda I(\Pi)+H[1+\gamma\,cut_w(\Pi)].
\]

## Exact pairwise phase boundary

For two factorizations `Pi_1,Pi_2`, `Pi_1` beats `Pi_2` iff

\[
\lambda[I(\Pi_1)-I(\Pi_2)]
+H\gamma[cut_w(\Pi_1)-cut_w(\Pi_2)]<0.
\]

When the cut-cost difference is nonzero, the crossover horizon is

\[
\boxed{
H^*=
\frac{\lambda[I(\Pi_2)-I(\Pi_1)]}
{\gamma[cut_w(\Pi_1)-cut_w(\Pi_2)]}
}
\]

with the inequality direction determined by the denominator sign.

This explicitly separates:

```text
morphology build/maintenance pressure
vs
future dependency/communication pressure.
```

## Exact exhaustive calibration

`dependency_factorization_phase.py` enumerates all 15 set partitions of four variables.

With `lambda=1/2`, `gamma=2`:

```text
PAIR_01_23 ecology:
  H=1  -> {01}|{23}
  H=4  -> {01}|{23}
  H=16 -> {0123}

PAIR_02_13 ecology:
  H=1  -> {02}|{13}
  H=4  -> {02}|{13}
  H=16 -> {0123}

UNIFORM ecology:
  H=1  -> {0}|{1}|{2}|{3}
  H=4  -> {0123}
  H=16 -> {0123}
```

Thus the same neutral partition space exhibits exact ecology- and horizon-dependent morphology changes.

## Why this is parent-owned

The optimization objective is a graph clustering/partitioning objective with a regularization/build term. Closely related mathematics appears throughout:

- graph cuts / clustering / community detection;
- factored MDPs and graphical models;
- variable elimination/treewidth;
- module/connection-cost evolution;
- software/hardware partitioning;
- modularity and evolvability research.

The evolutionary literature is even closer mechanistically: modularly varying goals can cause modular circuits/neural networks to emerge, while connection-cost pressure can independently cause modularity and hierarchy (`MODULAR_MORPHOGENESIS_PARENT_NO_GO_V1.md`).

Therefore:

```text
ecology dependency graph + connection/resource price -> module partition
```

is not a new GMI result.

## What would be stronger

Track B would need to show that a dependency/coupling object derived **without knowing the final successful decomposition** prospectively predicts factorization and developmental burden across multiple realization paradigms, while beating:

```text
graph partitioning/treewidth parent
family-native structure predictor
algorithm selection
AutoML/modularity-evolution parent
```

A stronger law might need higher-order/temporal dependencies, update locality, verification locality and plasticity—not only pairwise interaction weights.

## Terminal

```text
PAIRWISE_DEPENDENCY_FACTORIZATION_PHASE_EXACT
GRAPH_PARTITIONING_AND_MODULAR_EVOLUTION_PARENT_SUFFICIENT_AT_THIS_SCOPE
HIGHER_ORDER_CROSS_PARADIGM_DEVELOPMENTAL_FACTORIZATION_LAW_OPEN
```
