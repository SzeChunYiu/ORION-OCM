# CRR2 — constructive finite-class query procedure

Declare a nonempty **complete finite list** C of admitted models, an exact
population observation/intervention signature s, and a total target theta
defined on compatible candidates. Require exact finite representations with
total decidable equality for signatures and total decidable order/equality
for target values; the implementation uses rational numbers. Merely computable
real values do not supply these decision procedures. The list and evaluators are
inputs, with provenance supplied separately. This replaces a bare
set-theoretic definition with a terminating procedure at a stated scope.

1. Evaluate each candidate's full admitted signature and compare it with s.
2. Keep every exact match. No match returns INCOMPATIBLE.
3. Evaluate theta on matches. Return the minimum and maximum, together with
   model witnesses attaining each. Equal extrema return IDENTIFIED; unequal
   extrema return PARTIALLY_IDENTIFIED.

Finiteness, total evaluators and the stated total comparisons imply termination.
Exact matching and complete
enumeration make the retained set exactly C(s). A real-valued target is constant
on that finite nonempty set iff its minimum equals its maximum. Otherwise the
returned two witnesses certify ambiguity. These are necessity and sufficiency
claims for this input class, not a claim to infer C from data.

`solve_fiber` instantiates this procedure for all nine endogenous joint laws
and PN; it refuses a zero PN conditioning event. `uniform_root_models(n)`
enumerates every eight-type histogram with n equally weighted root units once,
using stars and bars. The number is choose(n+7,7). Different labelled root
permutations have the same response model and need not be repeated.

The analytic real-probability CRR1 theorem remains separate from these effective
representation premises. It is not an algorithm for equality of arbitrary
computable reals.

The executable census n=1,…,6 compares each histogram's full surgical joint
laws and PN with an independent expanded-row integer oracle. For every
nonempty defined fiber, exhaustive extrema equal CRR1's analytic bounds;
constructed lower, middle and upper models preserve the evidence. Middle
models may need a finer denominator than n; finite-class endpoints still lie
on the original grid. No enumeration completeness is inferred from sampling.

## Randomized estimator boundary

For two models with the same complete admitted decoder-view law but targets
theta0≠theta1, every estimator, including a randomized one with the same
world-independent seed law, has the same output law. Pointwise triangle
inequality gives E|Z-theta0|+E|Z-theta1|≥|theta1-theta0|, hence worst-world
expected absolute error at least half the gap. The claim remains true for
infinite expected loss. For deterministic estimates it gives the same bound.

An estimator returning the midpoint of the two **target endpoints** attains
this minimax bound on the two-world class. PR603's midpoint of q0 and q1 is
merely one blind rule; it need not attain the minimax bound. A whole finite
fiber's endpoint midpoint likewise minimizes worst-model absolute loss.

## What this closes

There is now a procedure for exact finite-class **query identification** and
an ambiguity certificate, plus a direct nonenumerative binary PN formula.
This does not close the separate demand for a general causal-structure
discovery algorithm, effective unrestricted model enumeration, finite-sample
error control or a learned model-class warrant.
