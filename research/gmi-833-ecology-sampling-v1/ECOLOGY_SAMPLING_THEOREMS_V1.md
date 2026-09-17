# Registered finite-population sampling theorems v1

## 1. Population and census

Let `E={0,1}^17` in the frozen axis order and let `N=|E|=2^17`.
Mixed-radix rank maps a bit tuple `x` to

`r(x)=sum_(j=0)^16 x_j 2^(16-j)`.

This is injective because binary expansion is unique, and its image is the
integer interval `[0,N)`. The executable census independently compares iterator
order, dependency mixed-radix rank, a direct binary rank, inverse rank, arithmetic
product, recursive product, unique occupancy, and the complete interval.

**Theorem G-S1 (registered-census closure).** If every member of `E` is included
once, the census estimator of every total function `y:E->[0,1]` equals its
finite-population value. Its selection bias and sampling variance are zero.

**Proof.** Every inclusion indicator is identically one. Thus the observed sum
is `sum_(e in E)y(e)`, not a random sub-sum. Equality is pointwise and has no
sampling distribution. QED.

This theorem is exhaustive only for the registered product `E`.

## 2. Prospective SRSWOR construction

For steps `i=0,...,n-1`, partial Fisher--Yates chooses a position uniformly from
the `N-i` remaining positions, emits its member, and swaps it into the consumed
position. Here `n=4096`.

**Theorem G-S2 (uniform ordered draw).** Conditional on independent uniform
offsets on the registered carriers, each ordered tuple of `n` distinct population
members has probability

`product_(i=0)^(n-1) 1/(N-i) = 1/(N)_n`.

**Proof.** At step `i`, exactly `N-i` members remain and the offset chooses each
with probability `1/(N-i)`, independently of prior choices conditional on the
remaining virtual array. Multiplication gives the result. QED.

Every unordered subset has `n!` orderings, so its probability is
`n!/(N)_n=1/binom(N,n)`. Therefore

`pi_i=n/N`, and `pi_ij=n(n-1)/(N(N-1))` for `i != j`.

The committed receipt is one prospective operational realization. Its statement
that `secrets.randbelow` used host entropy is provenance, not a cryptographic
proof of ideal entropy.

## 3. Design-unbiased finite-population mean

Let `I_i` be the sample inclusion indicator and

`mu=(1/N)sum_i y_i`.

The Horvitz--Thompson mean is

`mu_HT=(1/N)sum_i I_i y_i/pi_i`.

**Theorem G-S3 (unbiasedness).** For every fixed bounded vector `y`,
`E_S[mu_HT]=mu`. With constant `pi_i=n/N`, `mu_HT` equals the ordinary sample
mean.

**Proof.** Linearity gives

`E_S[mu_HT]=(1/N)sum_i E[I_i]y_i/pi_i=(1/N)sum_i y_i=mu`.

Substitution of `pi_i=n/N` gives `(1/n)sum_(i in S)y_i`. QED.

Zero design bias does not imply that the error of one realized sample is zero;
the package reports that signed realized error separately.

## 4. Exact variance and its estimator

Define

`S_y^2=(1/(N-1))sum_i(y_i-mu)^2`.

Under SRSWOR,

`Var_S(mu_hat)=(1-n/N)S_y^2/n`.

To derive it, center `z_i=y_i-mu`, so `sum_i z_i=0`, expand the variance of
`(1/n)sum_i I_i z_i`, substitute the two inclusion probabilities, and use
`sum_(i != j)z_i z_j=-sum_i z_i^2`. Simplification gives the displayed formula.

For sample variance

`s_y^2=(1/(n-1))sum_(i in S)(y_i-mu_hat)^2`,

the standard pairwise-difference identity

`sum_(i in S)(y_i-mu_hat)^2=(1/n)sum_(i<j in S)(y_i-y_j)^2`

and constant pair inclusion probability imply `E_S[s_y^2]=S_y^2`. Hence
`(1-n/N)s_y^2/n` is an unbiased estimator of the exact design variance.

The executable independent oracle enumerates all ten samples of size two from a
five-member population and verifies unbiasedness and both variance identities
without invoking the production formula as its enumerated reference.

## 5. Frozen diagnostics and analytic checks

For independent uniform coordinates, symmetry gives

- `E[axis_load]=1/2`;
- `E[rare_niche]=2^-5=1/32`;
- `E[global_parity]=1/2` by the parity-flipping bijection;
- `E[cross_pair]=1/4`.

The exact census agrees with these analytic values. These outcomes test the
sampling machinery only; they are not model performance or architecture scores.

## 6. Coverage is not probability selection

The preregistered axis, pair-cell, Hamming, and rare-niche thresholds diagnose
the realized draw. They cannot show that selection was outcome-independent.
Accordingly, deterministic prefix, low-Hamming, and outcome-selected panels are
audited separately and exposed by census comparisons. Conversely, probability
selection does not guarantee capture of every arbitrarily rare subset. The full
census, not the 4,096-member sample, supplies unconditional registered-product
anti-niche coverage.

## 7. Scope

No probability measure connecting `E` to an unregistered universe is supplied.
Therefore none of the census, bias, error, or uncertainty conclusions licenses
external-universe representativeness, empirical transfer, or claims about
natural/deployed ecologies.

