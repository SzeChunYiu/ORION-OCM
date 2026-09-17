# Registered-ecology census and sampling core v1

This package closes exactly the final two Section G rows of Issue #833 at the
scope established by PR #959: the finite registered product of seventeen binary
external ecology axes.

The unconditional anti-niche result is the full census. All 131,072 registered
coordinate tuples are ranked, constructed in a factorized semantic form,
validated, and included exactly once. Consequently there is no selection error
or sampling uncertainty for any total computed over this registered population.

A distinct prospective audit sampled 4,096 ranks without replacement after the
protocol freeze and before result generation. Its immutable partial
Fisher--Yates transcript replays exactly. The package separates three quantities
that are often conflated: zero design bias, nonzero realized sampling error, and
design variance. It reports all three with exact rational arithmetic, including
the finite-population correction and an unbiased sample-based variance estimate.

Coverage checks include every one-axis level, every two-axis cell, the full
Hamming-weight histogram, and a frozen five-axis rare niche. Deterministic
hand-picked and outcome-selected panels are retained as hostile controls.
Passing coverage diagnostics is not treated as proof of probability selection.

The terminal is
`GMI_833_REGISTERED_ECOLOGY_CENSUS_AND_SAMPLING_UNCERTAINTY_PROVED`.
It says nothing about unregistered, infinite, natural, deployed, or real-world
ecology universes.

