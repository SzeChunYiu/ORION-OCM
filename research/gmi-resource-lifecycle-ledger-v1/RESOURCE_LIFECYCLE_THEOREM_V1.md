# Resource and lifecycle accounting theorem v1

## Contract

An admissible comparison reports the fourteen-coordinate nonnegative vector in
`RESOURCE_LIFECYCLE_LEDGER_V1.json`.  Each charge has a lifecycle stage and an
evidence identifier.  Omitted coordinates, negative charges, Boolean values,
unregistered stages and unsupported scalar totals fail closed.  Zero is an
observed claim with the coordinate-specific meaning in the ledger, not a
missing value.

The stage partition makes build/acquisition, development, serving, revision,
maintenance and search boundaries explicit.  Summing the stage totals is
identically equal to summing the event trace, so work cannot disappear when a
report changes lifecycle granularity.  Failed proposals remain separate from
the work needed to generate and verify them; both are charged.

## Order theorem

For complete resource vectors `a,b` write `a <_P b` when every coordinate of
`a` is no larger and at least one is smaller.  For every strictly positive
price vector `w`, `a <_P b` implies `w·a < w·b`.  This follows by summing
nonpositive coordinate differences, at least one of which is strictly
negative after multiplication by a positive price.

No price-free total order exists for incomparable vectors.  If `a` is cheaper
on coordinate `i` and `b` is cheaper on coordinate `j`, sufficiently increasing
the positive price of `i` favors `a`, while sufficiently increasing the price
of `j` favors `b`.  Therefore an unfrozen scalar score silently chooses a
scientific conclusion.  The implementation refuses scalarization unless the
complete strictly-positive price vector and registration identifier are
declared pre-outcome.  Otherwise it returns the Pareto frontier.

The executable certificate exhausts all 27 vectors in `{0,1,2}^3`: 351
unordered pairs, including 189 dominance pairs.  All dominance relations are
preserved by three extreme positive price vectors; all 162 incomparable pairs
are explicitly shown to reverse order under those prices.

## Scope and open measurements

This closes the typed definition of fourteen lifecycle costs and the two
decision rules.  It does not assert retrospective coverage of every experiment.
Physical CPU/GPU/wall/IO metering remains open pending a portable measurement
and coverage bridge.  Energy remains open because no calibrated source is
available here; operation counts are not relabeled as joules.

Strongest parents: multidimensional cost accounting, amortized analysis and
multi-objective/Pareto optimization.  GMI adds no residual mathematical claim.

Falsifier: an accepted incomplete/negative vector, a stage total that differs
from the event total, a Pareto dominance reversed by positive frozen prices,
or scalarization accepted without a complete prospectively registered price
vector.
