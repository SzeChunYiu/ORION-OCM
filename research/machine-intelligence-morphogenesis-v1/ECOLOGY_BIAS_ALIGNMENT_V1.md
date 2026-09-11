# Ecology–bias alignment baseline v1

Status: **parent-derived analytic baseline, not a GMI novelty claim.**

## 1. Motivation

A morphology differs from another not only by what it can compute but by which useful computations it makes easy to reach.

Let an ecology induce a distribution `P_E(h)` over useful target hypotheses/configurations. Let morphology `M` induce a normalized proposal/prior distribution `Q_M(h)` before solving the fresh target.

Under an ideal code-length / surprisal proxy,

\[
C_{search}(h\mid M)=-\log Q_M(h).
\]

Then

\[
\mathbb E_{h\sim P_E}[-\log Q_M(h)]
=H(P_E)+D_{KL}(P_E\Vert Q_M).
\]

This is standard information theory/Bayesian coding. Track B adopts it as a parent baseline.

## 2. Consequence

Within this idealized model, the ecology-dependent excess search/code burden of morphology `M` is exactly its mismatch

\[
D_{KL}(P_E\Vert Q_M).
\]

Therefore a large part of morphology dominance can be understood as:

```text
ecological regularities
↔ morphology's inductive/proposal bias
+ lifecycle cost
```

This is the formal version of the intuition that no morphology is uniformly best: a bias helps when the ecology matches it and hurts when it does not.

## 3. Add lifetime economics

For horizon `H` and build/learning cost `B_M`, define the calibration model

\[
C_M(H,E)=B_M+H\,\mathbb E_{h\sim P_E}[-\log Q_M(h)].
\]

A phase boundary between `M1` and `M2` occurs where their total costs are equal.

This combines ordinary inductive-bias/coding theory with ordinary amortization economics. Neither ingredient is novel.

## 4. Exact calibration in this capsule

Use

\[
P_p=[p/2,p/2,(1-p)/2,(1-p)/2],
\]

structured morphology

\[
Q_S=[0.4,0.4,0.1,0.1],
\]

and uniform morphology

\[
Q_U=[0.25,0.25,0.25,0.25].
\]

With structured build cost `B` and uniform build cost zero,

\[
CE_S=\ln(10)-p\ln(4),\qquad CE_U=\ln(4).
\]

Hence the exact boundary is

\[
\boxed{p^*(H,B)=\frac{\ln(2.5)+B/H}{\ln 4}}.
\]

For `B=1`:

```text
H=1    p*=1.3823   structured can never pay on p∈[0,1]
H=2    p*=1.0216   structured can never pay
H=4    p*=0.8413
H=8    p*=0.7511
H=16   p*=0.7060
H=64   p*=0.6722
H=256  p*=0.6638
```

The long-horizon limit is

\[
\lim_{H\to\infty}p^*=\frac{\ln 2.5}{\ln 4}\approx0.660964.
\]

Artifacts:

```text
alignment_phase_calibration.py
EXACT_ECOLOGY_BIAS_ALIGNMENT_V1.json
test_alignment_phase_calibration.py
```

Terminal:

```text
ECOLOGY_BIAS_ALIGNMENT_PHASE_EXACT__INFORMATION_THEORY_PARENT
```

## 5. Why this is not yet a morphology theory

The calibration **assumes** `Q_S` and `Q_U`.

That is the central missing step.

Track B must derive or estimate

```text
Q_M
K_M
resource metric c_M
plasticity/retention response
```

from the morphology's actual structure, learning rule, history and hardware/resource model.

If those objects are simply assigned by hand, the phase law is an ordinary portfolio comparison.

## 6. Stronger research question

> Given the executable structure and update law of a morphology, can we predict its induced developmental geometry sufficiently well to forecast its relative acquisition burden on a new ecology before running the full learning/search process?

This is the `structure -> developmental geometry` problem.

## 7. Relation to known paradigms

Examples of parent-specific geometry:

- **Bayesian:** `Q` is explicit prior and `K` posterior/inference update.
- **program search:** `Q` can arise from a grammar/prefix code/library/search allocation.
- **neural:** `Q/K` are implicit in initialization/pretraining, architecture, optimizer and data; optimization/implicit-bias/meta-learning theory are parents.
- **production systems:** rule ordering/utilities/indexing/chunking induce proposal and update biases.
- **OCM:** history-induced search ordering, applicability and acquired assets induce explicit proposal/search changes.

The cross-paradigm residual is a common predictive language linking these structures to measurable future burden.

## 8. Strong null

If the best Track-B result is merely

```text
pick the prior/algorithm with the lowest measured cost on each ecology
```

then algorithm-selection/resource-rational parents are sufficient.

Required stronger terminal:

```text
STRUCTURE_TO_GEOMETRY_PREDICTION_SUPPORTED_AT_SCOPE
```

before any general morphology-law claim.