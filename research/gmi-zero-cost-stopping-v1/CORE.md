# Proper stopping with zero-cost computation

The [proof](ZERO_COST_STOPPING_THEOREM_V1.md) extends the finite deterministic
VOC interface to **nonnegative**, rather than strictly positive, edge charges.

The minimum cost among successfully terminating policies is attained. Among
cost-optimal policies, minimize the number of remaining cognitive edges.
That integer strictly decreases along the selected path, including zero-cost
edges. The resulting stationary policy terminates optimally from every viable
state; a missing serving path remains infeasible.

This is a finite shortest-path specialization of established proper-policy
and graph algorithms. It does not claim a new general metareasoning theorem.
The [model](zero_cost_stopping_v1.py) and [independent controls](test_zero_cost_stopping_v1.py)
use exact rational costs. The receipt binds the actual source and run output.
The previous [VOC repair](../gmi-value-of-computation-v1/CORE.md) remains unchanged.
Neither result establishes stochastic pathwise bounds, action certification,
unknown transition laws or measured full physical costs.
