# Planning Semantic-Resolution Parent Subtraction V1

Status: **PARENT BOUNDARY EXPLICIT**  
Date: 2026-09-12

## Parent-owned content

Grand GMI does not claim invention of graph/tree search, dynamic programming, verifier search, MDP state abstraction, bisimulation, homomorphisms, planning automata or black-box optimization.

Established planning/state-abstraction theory already shows that structure-preserving abstractions can preserve planning/control properties, while black-box search problems may expose exponentially large spaces.

## Grand-GMI residual

The residual contribution is the obligation-relative composition:

1. The required plan resolution defines a semantic quotient of possible successful leaves/trajectories.
2. Under an equality-only verifier channel, the exact cost of identifying that quotient is derived before choosing a search implementation.
3. For a full `b`-ary depth-`d` tree and required prefix length `q`, this gives the closed form

   `Q = b^d - b^(d-q)`.

4. The same task can move to a different complexity regime when the process boundary exposes a goal-respecting right-congruent semantic state; then exact dynamic programming operates on the quotient rather than raw histories.
5. Plan-output width and transformation/search complexity are therefore distinct Grand-GMI invariants.

The tranche's scientific content is not “search can be exponential” or “abstraction helps planning.” It is a typed law explaining **which hidden plan distinctions must be resolved for the obligation and how the available process interface changes the corresponding transformation cost**.