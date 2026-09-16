# GMI #833 E4 — exact finite stochastic update operator

This capsule adds one architecture-family-free finite stochastic-state/update contract to the G0 programme.

Registered objects are exact rational probability distributions and 3×3 row-stochastic transition kernels. Operations are one-step distribution push-forward, kernel composition, identity, deterministic-map specialization and state relabeling transport.

The package deliberately keeps predictive randomness distinct from confidence/epistemic uncertainty. It consumes #851’s typed uncertainty boundary and #857’s finite predictive parents rather than claiming Bayesian inference, latent identification or new Markov-chain mathematics.

All executable probability evidence is `fractions.Fraction`; floats are rejected.

Claim ceiling:

`GMI_FINITE_EXACT_STOCHASTIC_UPDATE_OPERATOR_AT_REGISTERED_SCOPE`
