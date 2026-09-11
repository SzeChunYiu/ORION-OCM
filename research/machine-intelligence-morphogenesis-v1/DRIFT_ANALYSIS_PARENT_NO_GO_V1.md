# Drift-analysis parent no-go v1

Status: **parent subtraction for developmental geometry.**

## Claim attacked

A tempting generalization is:

> Define a scalar developmental potential/distance to a target, measure expected progress per learning/search step, and derive expected cost/time to verified competence.

This is powerful, but it is not new.

## Parent theory

Drift analysis studies exactly this pattern for stochastic search processes:

```text
choose a potential X_t measuring distance/progress
bound expected local change (drift)
-> derive first-hitting/optimization-time bounds
```

Additive, multiplicative and variable drift theorems provide mature conditions and hitting-time bounds. The literature is central in theoretical evolutionary-algorithm analysis and applies to more general random processes.

A particularly strong parent observation is that, for a time-homogeneous Markov chain with finite expected hitting times, the expected remaining hitting time itself can serve as a potential with exact one-step drift properties. Therefore inventing a perfect scalar "distance to solution" after knowing the full process can be tautological.

## Consequence for Track B

The following do **not** constitute a novel cross-paradigm intelligence theory:

```text
potential to target
+ expected progress per update
+ first-hitting-time bound
```

or

```text
eta = development progress / cost
```

by themselves.

Valid parent terminal:

```text
DRIFT_ANALYSIS_PARENT_SUFFICIENT_FOR_HITTING_TIME_FROM_GIVEN_POTENTIAL
```

## Stronger residual

The nontrivial Track-B question is:

> Can a useful low-dimensional potential/drift signature be predicted from morphology structure, update law and legal history **before** solving the fresh target, and can the same construction retain meaning across different morphology paradigms?

This is different from choosing a target-specific potential after full transition knowledge.

## Resource-weighted extension

For transition resource vector `r_t`, a scalar cost requires a prospectively frozen price/utility mapping. A per-cost drift can be defined only after that choice.

Track B should prefer raw vector reporting and use scalar drift only for registered experiments with a declared price vector.

## Morphology comparison

For two morphologies `M1,M2`, a useful general theory would need to predict from structure/history quantities analogous to:

```text
initial potential / target surprisal
expected progress/drift under legal updates
variance / tail risk
per-step resource cost
retention/plasticity under repeated updates
```

and correctly predict a frontier crossing on held-out ecologies.

If the potential or drift is estimated only from the same protected outcome trajectories being explained, the result is descriptive, not predictive.

## Parent anchors

- Doerr & Neumann et al., survey of evolutionary-algorithm theory: drift analysis as a principal runtime-analysis tool.
- Kötzing & Krejca, *First-Hitting Times Under Additive Drift*.
- Doerr, Johannsen & Winzen, *Multiplicative Drift Analysis*.
- He & Yao's expected-time/potential results and related drift-analysis literature.

## Revised live residual

After SSP/metareasoning + information theory + drift subtraction, the central object is no longer "developmental geometry exists".

It is:

\[
\boxed{
\text{morphology structure/history}
\to
\text{predictive compact potential/proposal/update signature}
\to
\text{held-out developmental burden/frontier}
}
\]

with cross-paradigm transfer and causal intervention.

This is exactly the bar in `STRUCTURE_TO_GEOMETRY_PROGRAMME_V1.md`.