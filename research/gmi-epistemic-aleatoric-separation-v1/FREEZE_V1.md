# #750 freeze — exact epistemic / aleatoric separation V1

Date: 2026-09-15. Parent ledger: #602 Section M. Child issue: #750.

This file is the pre-implementation authority for the tranche. No executor, scored receipt, or hostile test for this tranche exists on this branch before this commit.

## Claim boundary

Target only:

```text
EXACT_EPISTEMIC_ALEATORIC_SEPARATION_FOR_REGISTERED_FINITE_LATENT_MODELS
```

This tranche may establish an exact finite law-of-total-variance decomposition under a preregistered latent/model semantics, a stronger non-identifiability theorem showing that the decomposition cannot be recovered from the predictive marginal alone, and a fail-closed executable contract.

It may not claim universal uncertainty decomposition, posterior correctness/calibration, empirical capability or morphology calibration, that real-world stochasticity is intrinsically irreducible, or that one scalar captures every form of epistemic uncertainty.

## Strongest parents

No novelty is claimed over the law of total variance, Bayesian posterior-predictive decomposition, or standard uncertainty taxonomy. Literature anchors:

- Hüllermeier & Waegeman (2021), *Aleatoric and epistemic uncertainty in machine learning: an introduction to concepts and methods*, Machine Learning 110:457–506, DOI 10.1007/s10994-021-05946-3;
- Kendall & Gal (2017), *What Uncertainties Do We Need in Bayesian Deep Learning for Computer Vision?*, NeurIPS 30;
- ordinary finite probability / conditional expectation identities.

The repository residual is operational: exact rational latent contracts, explicit semantics, exact counterexamples, a fail-closed no-latent terminal, and hostile controls preventing a marginal uncertainty score from being mislabeled as a unique decomposition.

## Frozen mathematical object

A `FiniteLatentModel` contains:

```text
latent labels theta in a finite nonempty set Theta
exact epistemic weights pi(theta) in Q_[0,1], summing to 1
one finite exact outcome kernel K_theta(y) in Q_[0,1] per theta, summing to 1
outcomes y in Q
```

Only positive-weight latent states contribute to the registered decomposition. All arithmetic is exact `Fraction` arithmetic.

For each positive-weight latent state define

```text
m(theta) = sum_y K_theta(y) y
v(theta) = sum_y K_theta(y) [y - m(theta)]^2.
```

Define

```text
mu     = sum_theta pi(theta) m(theta)
A      = sum_theta pi(theta) v(theta)
E_mean = sum_theta pi(theta) [m(theta)-mu]^2
T      = sum_y P_Y(y) [y-mu]^2,
```

where

```text
P_Y(y) = sum_theta pi(theta) K_theta(y).
```

`A` is named the **registered aleatoric variance component**. `E_mean` is named the **registered epistemic variance of the conditional predictive mean**. The word `registered` is load-bearing: the split is relative to the frozen latent semantics.

## Frozen theorem EA-1 — exact total-variance decomposition

For every valid finite latent model above,

```text
T = A + E_mean.
```

The proof must be given by exact finite expansion, with explicit quantifiers and no independence assumption.

Both terms are nonnegative. Therefore `0 <= A <= T` and `0 <= E_mean <= T`.

## Frozen theorem EA-2 — decomposition is not identifiable from the predictive marginal

There exist two valid latent models with exactly the same full predictive marginal distribution `P_Y` but different `(A,E_mean)`.

Use the exact frozen pair:

### PURE_ALEATORIC

```text
Theta = {q}
pi(q)=1
K_q(-1)=1/2
K_q(+1)=1/2
```

Expected:

```text
P_Y(-1)=P_Y(+1)=1/2
mu=0
T=1
A=1
E_mean=0
```

### PURE_EPISTEMIC_MEAN

```text
Theta={minus,plus}
pi(minus)=pi(plus)=1/2
K_minus(-1)=1
K_plus(+1)=1
```

Expected:

```text
P_Y(-1)=P_Y(+1)=1/2
mu=0
T=1
A=0
E_mean=1
```

Hence no function of `P_Y` alone can uniquely identify the registered `(A,E_mean)` pair over this model class. In particular, support width, confidence-interval width, predictive variance, and entropy-like summaries cannot by themselves license a unique epistemic/aleatoric attribution.

The proof document must state this as a non-identifiability theorem, not merely as an example.

## Frozen theorem EA-3 — pure and mixed edge cases

The executor must exactly reproduce:

1. point-mass latent weights plus a nondegenerate kernel => `E_mean=0` and `A>0`;
2. multiple positive latent weights plus deterministic kernels with different means => `A=0` and `E_mean>0`;
3. mixed model:

```text
pi(L)=pi(R)=1/2
K_L(-1)=K_L(0)=1/2
K_R(0)=K_R(+1)=1/2
```

Expected:

```text
m(L)=-1/2
m(R)=+1/2
A=1/4
E_mean=1/4
T=1/2
P_Y = {-1:1/4, 0:1/2, +1:1/4}.
```

## Frozen theorem EA-4 — mean-epistemic variance is not all model uncertainty

Use:

```text
pi(a)=pi(b)=1/2
K_a(0)=1
K_b(-1)=K_b(+1)=1/2.
```

Both conditional means are zero, so

```text
E_mean=0.
```

But the positive-weight conditional kernels are different. Therefore zero epistemic variance **of the conditional mean** does not imply zero epistemic/model uncertainty about the full predictive law.

The implementation must expose a non-probabilistic diagnostic

```text
positive_weight_kernels_identical : bool
```

and this control must report `false`. This diagnostic is not added to `A+E_mean`; it exists only to prevent an overgeneralized interpretation of the scalar decomposition.

## Frozen theorem EA-5 — semantic relativity / refinement law

The same observed predictive marginal may admit multiple latent refinements, as EA-2 proves. Therefore labels `aleatoric` and `epistemic` are relative to a registered conditioning/latent semantics. A refinement or coarsening of the latent variable can move variance between `A` and `E_mean` while preserving the marginal predictive law.

This tranche must not use wording such as “the uniquely true decomposition” without an independently justified latent semantics.

## Frozen fail-closed API

A marginal-only object can contain an exact finite `P_Y`, but it has no registered latent semantics. Calling decomposition on it must return exactly

```text
CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS
```

and must not fabricate `A` or `E_mean`.

A full latent model must reject:

- empty latent space;
- duplicate latent labels;
- non-`Fraction` weights/probabilities/outcomes;
- negative probabilities or probabilities above one;
- latent weights not summing exactly to one;
- empty kernels;
- kernel probabilities not summing exactly to one;
- duplicate outcomes inside a kernel representation;
- malformed labels.

Zero-weight latent states are permitted for exact registry completeness but do not influence the decomposition or the `positive_weight_kernels_identical` diagnostic.

## Frozen exact receipt controls

The deterministic receipt must contain, at minimum:

```text
PURE_ALEATORIC:     A=1, E_mean=0, T=1
PURE_EPISTEMIC:     A=0, E_mean=1, T=1
MIXED:              A=1/4, E_mean=1/4, T=1/2
SAME_MEAN_DIFFERENT_KERNELS: E_mean=0, kernels_identical=false
MARGINAL_NONIDENTIFIABILITY: same marginal=true, different decomposition=true
NO_LATENT: CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS
```

For every full latent control, direct marginal variance computed independently from `P_Y` must equal `A+E_mean` exactly.

## Frozen adversarial controls

At minimum the suite must demonstrate:

1. the EA-2 pair has byte-for-byte identical canonical marginal distributions;
2. the EA-2 pair has distinct decomposition pairs `(1,0)` and `(0,1)`;
3. an attempted marginal-only decomposition fails closed;
4. total variance identity holds for exhaustive small rational model families generated independently from the production decomposition function;
5. `A>=0`, `E_mean>=0`, and each is `<=T` on that family;
6. point-mass/nondegenerate and deterministic-kernel/uncertain-latent edge cases behave as frozen;
7. the mixed model yields exactly `(1/4,1/4,1/2)`;
8. same-mean/different-kernel control yields `E_mean=0` while kernel identity diagnostic is false;
9. zero-weight latent states do not change any decomposition value or positive-weight kernel diagnostic;
10. malformed weights/kernels/outcomes/floats are rejected;
11. relabeling latent states leaves all decomposition values and marginal law unchanged;
12. normal Python and `python -O` produce the same deterministic receipt.

## Frozen falsifiers

This tranche fails if any of the following occurs:

- any valid registered finite latent model violates `T=A+E_mean`;
- the two frozen EA-2 models produce different marginals;
- marginal-only input receives a fabricated decomposition;
- `E_mean=0` is described as proving absence of all epistemic/model uncertainty;
- a latent relabel changes the result;
- floats or non-normalized probability tables enter scored computation;
- the implementation claims data alone authenticate the chosen latent semantics;
- optimized mode changes the receipt;
- wording upgrades the result to universal uncertainty decomposition or empirical calibration.

No #602 master checkbox is changed merely because this freeze exists. Closure requires implementation, formalization, exact/adversarial tests, deterministic receipt reproduction, repository CI, merge, and scoped checklist reconciliation.