# Issue #982 / #833 Section G registered-ecology sampling freeze v1

Frozen parent: Issue #833. Dependency: Issue #957 / PR #959. Frozen
dependency head:
`bd61471056cc904b03e70f05e6b64c4445e25b07`.

The live Issue #833 body used to identify the target rows has SHA-256
`d5fb641d9af6fe71b054361a32df486763e9497a17dcd946f63ce832518f790b`.
The child Issue #982 scope body has SHA-256
`bbf484ae0a771c7551ddd43f313f65b5b7d8e6db1d50b9b4b28132415209acbf`.

## Exact closure target

This tranche targets exactly the final two unchecked Section G rows:

1. `Sample enough ecology space to avoid hand-picked niche bias.`
2. `Quantify ecology sampling bias and uncertainty.`

No other Issue #833 row may be changed by this tranche.

## Frozen population and scope

The population is exactly the registered binary product from PR #959,

`E = product_(j=0)^16 {0,1}`, with `N = 2^17 = 131072`.

The rank is the dependency's mixed-radix rank in frozen axis order. A census is
valid only if the iterator visits every integer rank in `[0,N)` exactly once and
an independent arithmetic product also equals `N`.

This finite population is the whole claim domain. No inference is made to an
unregistered, infinite, natural, deployed, or real-world ecology universe.

## Frozen census obligation

The primary anti-niche certificate is an exact full census, not an extrapolation
from a favorable subset. For every registered rank, the implementation must
construct and semantically validate its ecology and behavioral specification.
It must compute the frozen diagnostic outcomes below for all `N` ranks.

Because the inclusion indicator is one for every population member, every total
registered-population quantity computed by the census has exactly zero selection
bias and zero sampling uncertainty. This conclusion is limited to `E`.

## Frozen diagnostic outcomes

Write `x_j(e)` for the binary index of axis `j` in frozen order. The executable
audit must use exactly these bounded, architecture-neutral diagnostics:

1. `axis_load(e) = (sum_j x_j(e))/17`;
2. `rare_niche(e) = product_(j in {0,3,7,12,16}) x_j(e)`;
3. `global_parity(e) = (sum_j x_j(e)) mod 2`;
4. `cross_pair(e) = x_2(e) x_11(e)`.

They audit the sampling machinery; they are not performance scores, architecture
rankings, or claims about nature. Their census means and all calculations must
use exact rational arithmetic.

## Frozen prospective probability design

After this freeze is committed, and before any outcome is evaluated, draw one
ordered sample of size `n = 4096` by partial Fisher--Yates sampling:

For `i = 0,...,n-1`, obtain an independent integer `u_i` uniformly from
`{0,...,N-i-1}` using Python `secrets.randbelow(N-i)`. Set `j=i+u_i`, emit the
population member currently at virtual-array position `j`, and swap virtual
positions `i` and `j`. Record every `u_i`, the emitted ranks, time, Python
version, source description, and hashes in an immutable draw receipt. No redraw
is permitted. A failed gate is a red result.

The draw code receives no outcome vector or outcome callback. Git history must
show this freeze before the draw receipt and the draw receipt before result
generation. The receipt is an operational provenance statement about system
entropy, not a cryptographic proof that the host entropy source was ideal.

Conditional on the frozen design assumption that the `u_i` are independent and
uniform on their stated carriers, every ordered sample has probability
`1/(N)_n`, every unordered `n`-subset has probability `1/binom(N,n)`, and the
first- and second-order inclusion probabilities are

`pi_i = n/N` and `pi_ij = n(n-1)/(N(N-1))` for `i != j`.

## Frozen estimands and uncertainty

For any frozen bounded outcome vector `y=(y_0,...,y_(N-1))` with values in
`[0,1]`, define

`mu = (1/N) sum_i y_i` and `mu_hat = (1/n) sum_(i in S) y_i`.

The equal-probability Horvitz--Thompson estimator simplifies to `mu_hat`. Under
the design above it is exactly design-unbiased for every fixed `y`:

`E_S[mu_hat] = mu`.

With

`S_y^2 = (1/(N-1)) sum_i (y_i-mu)^2`,

its exact design variance is

`Var_S(mu_hat) = (1-n/N) S_y^2/n`.

With sample variance

`s_y^2 = (1/(n-1)) sum_(i in S) (y_i-mu_hat)^2`,

`(1-n/N)s_y^2/n` is an unbiased estimator of that design variance. The package
must report, as exact fractions, the census mean, sample estimate, signed and
absolute realized sampling error, exact design variance, and sample variance
estimate for every frozen diagnostic. It must keep zero design bias distinct
from a nonzero realized sampling error.

## Frozen coverage and bias diagnostics

The unalterable prospective sample must pass all of the following:

- exactly 4096 distinct in-range ranks;
- every axis level represented at least 1600 times;
- every two-axis cell represented at least 700 times for all 136 axis pairs;
- total-variation distance between the sample and census Hamming-weight
  distributions no more than `1/20`;
- at least 64 sampled members of the frozen five-axis rare niche;
- exact equality between the sample mean and Horvitz--Thompson form;
- valid exact first- and second-order inclusion probabilities.

The audit must also construct deterministic hand-picked hostile panels (all-zero
prefix, low-Hamming-weight niche, and outcome-selected top ranks), quantify their
error against the census, and prove that at least one frozen diagnostic exposes
each panel. These hostiles show why coverage or favorable-looking point estimates
alone do not establish probability-sample validity.

## Frozen falsifiers and claim boundary

The result is red if the dependency population changes; census ranks are missing
or duplicated; any ecology/specification fails semantic validation; the draw
depends on outcomes; the realized draw is altered or redrawn; any coverage gate
fails; Boolean values pass as integer ranks or outcomes; exact and independently
computed arithmetic disagree; finite-population correction is omitted; design
bias is confused with realized error; normal and optimized runs differ; or
reconciliation targets anything beyond the two frozen rows.

No claim is made about unknown outcomes outside `E`, empirical
representativeness, external validity, model-family discovery, or universal
adequacy of a 4096-member sample. Within `E`, the exhaustive census is the
unconditional anti-niche result; the prospective sample supplies a replayable
design-based uncertainty audit and does not replace that census.

Allowed terminal only after proof, exact replay, and package validation:

`GMI_833_REGISTERED_ECOLOGY_CENSUS_AND_SAMPLING_UNCERTAINTY_PROVED`
