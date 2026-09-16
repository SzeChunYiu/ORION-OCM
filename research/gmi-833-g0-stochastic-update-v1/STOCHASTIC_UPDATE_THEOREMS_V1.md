# Finite stochastic-update theorems v1

## Expert review lanes

- **Probability / stochastic processes:** finite Markov-kernel validity, push-forward and composition.
- **Formal semantics:** predictive randomness is distinct from confidence/latent uncertainty objects.
- **Symmetry / representation:** state-relabeling covariance.
- **Hostile verification:** exact rationality, normalization, dimensions, relabeling and latent/confidence boundary attacks.

## STOCH-1 — exact law preservation

For a finite probability distribution `mu` and row-stochastic kernel `K`, `muK` is nonnegative and sums to one:

`sum_j (muK)_j = sum_i mu_i sum_j K_ij = sum_i mu_i = 1`.

The finite registered family checks all 216 kernels against all six input distributions: 1,296 exact updates, zero failures.

## STOCH-2 — composition / sequential equality

For kernels `K1,K2`, define `K12=K1K2`. Associativity of finite sums gives

`(muK1)K2 = mu(K1K2)`.

Every one of the 216² = 46,656 ordered registered kernel pairs is composed. Equality is then checked on each of the three point-mass basis distributions, yielding 139,968 exact sequential/composed comparisons; basis equality fixes every row of the resulting matrix.

A second independently indexed multiplication path agrees on all 46,656 products.

## STOCH-3 — identity

The exact identity kernel is both left and right identity for all 216 registered kernels. Zero failures.

## STOCH-4 — deterministic specialization

A deterministic map `f:S→S` embeds as a point-mass-row kernel `DET(f)`. For all 27 maps and all three source point masses, stochastic update returns exactly the deterministic image point mass: 81/81 exact checks.

## STOCH-5 — state-relabeling covariance

For a permutation `pi`, transport distribution mass by `i→pi(i)` and transport kernel row/column indices `(i,j)→(pi(i),pi(j))`. Index substitution gives

`T_pi(muK)=T_pi(mu) T_pi(K)`.

The executable certificate checks all 216×6×6 = 7,776 registered kernel/distribution/permutation triples, zero mismatches.

Kernel composition covariance follows by the same index renaming. The exact pair census checks all 46,656 registered pairs under the generating transposition `(0 1)`, zero mismatches; the analytic proof is permutation-general.

## STOCH-6 — closure exceeds the frozen census

The six-row input census is only a finite test family. Composing a genuinely stochastic registered kernel with itself produces quarter probabilities. The operational constructor accepts the exact resulting row-stochastic law, demonstrating that composition is not artificially projected back into the six-row census.

## UNC-BND — uncertainty-kind boundary

A `KernelV1`/distribution is a predictive stochastic law. It cannot be silently coerced into a confidence-set claim or decomposed into epistemic/aleatoric latent components without the premises/latent semantics required by #851. The executable adapter returns machine-distinct `CANNOT_*` terminals for both attempted promotions.

## Resource accounting

Dense one-step update emits `(state_mass_reads,kernel_entry_reads,multiply_ops,add_ops,output_writes)=(3,9,9,6,3)`.

Dense kernel composition emits `(0,54,27,18,9)`.

These are exact implementation-resource counts at the registered 3-state scope, not asymptotic optimality claims.

## Falsifiers

Any accepted float/malformed probability object, row-normalization failure, composition/sequential mismatch, relabeling mismatch, deterministic-specialization mismatch, or fabricated confidence/latent interpretation makes the tranche RED.
