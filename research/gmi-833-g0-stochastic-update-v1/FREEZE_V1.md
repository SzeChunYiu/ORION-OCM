# GMI #833 E4 — exact finite stochastic update freeze v1

**Parent:** #833 Section E  
**Child:** #885  
**Source main:** `43102437ebcbf6f818bb58b45470beffaf865029`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the finite carrier, exact rational probability constructors, operational update/composition semantics, exhaustive census, symmetry target, resource accounting, hostile cases, parent boundary and claim ceiling before executor/tests/results/reconciliation/workflow.

## Scientific boundary

This tranche adds only an operational finite stochastic-state/update primitive to the architecture-uncommitted G0 programme. It does not re-derive predictive-state/rank results from #857, uncertainty/confidence semantics from #851, Bayesian inference, latent identification, probabilistic programming, infinite-horizon theory, or general measurable kernels.

Parent mathematics remains parent-owned: finite-state Markov chains, row-stochastic matrices/Markov kernels, matrix multiplication, distribution push-forward and state relabeling.

## Registered carrier and exact types

State carrier:

`S=(s0,s1,s2)`.

All probability values are Python `Fraction` objects. Floats are rejected, even when numerically equal to an admissible rational.

### DistributionV1

Exact tuple `mu=(mu0,mu1,mu2)` such that:

- each entry is `Fraction`;
- each entry is nonnegative;
- `sum(mu)=1`.

### KernelV1

Exact 3x3 tuple of `Fraction` rows `K[i][j]` such that every row is a valid `DistributionV1`.

Interpretation is operational predictive randomness:

`K[i][j] = P(X_{t+1}=sj | X_t=si)`.

It is not a confidence set, posterior over models, or latent decomposition.

## Operational semantics

### STOCHASTIC_UPDATE

`mu' = mu K`, i.e.

`mu'_j = sum_i mu_i K[i][j]`.

Target: any valid `mu,K` produce a valid distribution exactly.

### COMPOSE

`K12 = K1 K2`, i.e.

`K12[i][j] = sum_k K1[i][k] K2[k][j]`.

Target: `update(update(mu,K1),K2) = update(mu,compose(K1,K2))` exactly.

### IDENTITY

`I[i][j]=1` iff `i=j` else 0. Target: left/right composition identity.

### DET

For deterministic map `f:S->S`, `DET(f)[i]` is the point mass at `f(si)`. Target: updating a point mass at `si` yields exactly the point mass at `f(si)`.

## Frozen finite family

Registered row family contains exactly six distributions with entries in `{0,1/2,1}` and sum 1:

- `(1,0,0)`, `(0,1,0)`, `(0,0,1)`;
- `(1/2,1/2,0)`, `(1/2,0,1/2)`, `(0,1/2,1/2)`.

A registered kernel chooses one of these six rows independently for each of three source states, yielding exactly:

`6^3 = 216` kernels.

## Exact certificate targets

1. **Law preservation:** all `216 * 6 = 1,296` registered kernel/distribution updates produce valid exact distributions.
2. **State-relabeling covariance:** all `216 * 6 * 6 = 7,776` kernel/distribution/permutation triples satisfy transported-update equality.
3. **Composition census:** all `216^2 = 46,656` ordered kernel pairs are composed; every product is row-stochastic exactly.
4. **Sequential/composed equality:** for every ordered kernel pair, check the three point-mass basis distributions. This gives `46,656 * 3 = 139,968` exact sequential/composed comparisons; equality on the basis rows certifies the full 3x3 kernel product.
5. **Identity:** all 216 kernels satisfy `IK=KI=K`.
6. **Deterministic specialization:** all `3^3=27` deterministic maps satisfy exact point-mass map semantics on all three source states: 81 checks.

## State relabeling

For any permutation `pi` of the three state labels:

- transport a distribution by moving mass from `i` to `pi(i)`;
- transport a kernel by moving row/column `(i,j)` to `(pi(i),pi(j))`.

Target:

`T_pi(update(mu,K)) = update(T_pi(mu), T_pi(K))`.

Composition covariance must also hold:

`T_pi(compose(K1,K2)) = compose(T_pi(K1),T_pi(K2))`.

The executable certificate checks one-step covariance exhaustively over the registered 7,776 triples and composition covariance on the complete 46,656 pair family for a fixed generating transposition plus an independent oracle; the analytic index-renaming argument covers every permutation.

## Raw resource vector

Operational calls emit raw resources; validation cost is recorded separately in tests, not hidden inside the update claim.

`STOCHASTIC_UPDATE`:

`(state_mass_reads, kernel_entry_reads, multiply_ops, add_ops, output_writes) = (3,9,9,6,3)`.

`COMPOSE`:

`(state_mass_reads, kernel_entry_reads, multiply_ops, add_ops, output_writes) = (0,54,27,18,9)`.

These correspond to direct dense 3x3 arithmetic and are independently recounted.

## Positive controls

Required exact fixtures:

- point mass under identity;
- absorbing kernel;
- deterministic three-cycle;
- equal two-way mixture;
- genuinely stochastic kernel with at least one non-point row;
- two-step composition creating quarter probabilities, proving the operational domain is not artificially restricted to the six-row census after composition.

## Fail-closed hostiles

Reject:

- floats anywhere in distribution/kernel probability fields;
- negative probability;
- distribution sum not 1;
- kernel row sum not 1;
- wrong distribution length;
- wrong kernel dimensions;
- non-`Fraction` exact-looking integers in probability fields unless explicitly constructed as `Fraction`;
- non-bijective state relabeling;
- source/destination state outside the registered carrier;
- attempts to coerce this predictive law into a `ConfidenceSet`/latent decomposition without registered latent semantics.

The last boundary is represented as a machine-distinct refusal terminal in the executable adapter, consuming #851 semantics rather than inventing a decomposition.

## Claim ceiling

`GMI_FINITE_EXACT_STOCHASTIC_UPDATE_OPERATOR_AT_REGISTERED_SCOPE`

Forbidden promotions:

- `GENERAL_MEASURABLE_MARKOV_KERNEL`
- `INFINITE_HORIZON_STOCHASTIC_THEORY`
- `FINITE_SAMPLE_IDENTIFICATION`
- `BAYESIAN_INFERENCE_DERIVED`
- `PROBABILISTIC_PROGRAMMING_DERIVED`
- `LATENT_CAUSAL_IDENTIFICATION`
- `STOCHASTIC_MORPHOLOGY_OPTIMAL`
- `COMPLETE_GMI`

## Reconciliation boundary

Only after exact-head PR CI is green may this child reconcile:

- `Add stochastic state and update operators.`

All other Section-E rows remain open.
