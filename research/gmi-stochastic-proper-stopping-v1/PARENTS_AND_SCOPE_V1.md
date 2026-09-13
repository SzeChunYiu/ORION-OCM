# Parent subtraction and cost scope

## Primary sources and what is inherited

- [Bertsekas and Tsitsiklis (1991), *An Analysis of Stochastic Shortest Path
  Problems*](https://www.mit.edu/~jnt/Papers/J034-91-berts-SSP.pdf):
  finite SSP properness and positive-cost Bellman theory. Adding δ per
  nonterminal step puts our viable subproblem in this established regime.
- [Bertsekas and Yu (2016), *Stochastic Shortest Path Problems Under Weak
  Conditions*, Proposition2.1, §2.4](https://faculty.engineering.asu.edu/bertsekas/wp-content/uploads/sites/129/2020/03/SSP_Weak_Conditions.pdf):
  directly establishes proper-policy optimization through perturbation and
  finite-action stationary attainment. The proof in SPS-2 specializes that
  argument; its common-policy lexical selection makes expected steps explicit.
  This does not claim a new SSP law, nor import the paper's negative-cost scope.
- [Bertsekas (2020), *Proper Policies in Infinite-State Stochastic Shortest
  Path Problems*, §§II,V](https://arxiv.org/html/1711.10129v2):
  distinguishes proper from unrestricted total-cost values and restricts the
  comparison-function class for Bellman claims. Here finite state makes finite
  functions bounded; an extended infinite fixed point is not a valid substitute.
- [Guillot and Stauffer (2017), *The Stochastic Shortest Path Problem:
  A Polyhedral Combinatorics Perspective*](https://arxiv.org/pdf/1702.03186):
  occupation measures, flow formulations and stationary-policy reduction.
  The independent oracle enumerates rational flow vertices rather than using
  the main policy evaluator. It is deliberately a small exact implementation,
  not a claim to match mature SSP algorithms' scalability.

## Repository scope checked before building

At source base b43496c0e756d2732fbf5b553c59a6e8aad18fd0:

- Formal [AG2/AG3 and RES2](../gmi-formal-derivation-v1/AGENCY-RESOURCES.md)
  optimize finite-horizon or discounted stochastic objectives.
- [PCA-1](../gmi-grand-unification-v1/PROBABILISTIC_CONTROLLED_ACQUISITION_THEOREM_V1.md)
  supplies stationary absorption and a positive-cost optimality certificate;
  PCA-2 handles finite horizons. Its c_min>0 excludes the present zero loops.
- [ZCS](../gmi-zero-cost-stopping-v1/ZERO_COST_STOPPING_THEOREM_V1.md)
  constructs a proper optimal selector in finite deterministic nonnegative
  graphs, including zero-cost cycles.

The incremental contribution is a supplied finite rational stochastic
construction covering zero costs and partial viability, plus independent
mathematical controls. The optimum theorem is inherited from SSP, not a new
scientific principle. Existing positive-cost, deterministic and finite-horizon
statements remain valid. Parent files are bound separately and unchanged.

## Physical and computational accounting

The scalar stage charge c is supplied, not inferred from probability,
source size, dispatch counts or a finite receipt. A terminal action includes
its actual registered implementation charge. Count τ includes that final
transition; expected cognitive computations alone would subtract one from
every successfully terminated trajectory. No convention is silently mixed.

For n viable states and K=product_s |A_V(s)| stationary policies, the direct
constructor uses K support/properness checks and at most two n×n rational
linear solves per accepted policy. Gaussian elimination uses O(n³) rational
arithmetic operations per solve; bit complexity depends on input rational
encoding and intermediate sizes. Enumeration is exponential in n in general.
The retained model stores all action rows; the returned controller stores one
action index per viable state. Building, verifying and retaining that controller
are additional operations, not free consequences of knowing J.

Model acquisition, adequate terminal verification, compilation, random-number
generation, observation processing, sufficient-state construction, transition
implementation and all required resources must be charged in a real application.
A setup fee constant across choices adds to total cost. Policy-dependent setup
fees change the comparison and require a larger explicit register/objective;
the unaugmented Bellman table is not a certificate for that new objective.
Expected cost feasibility does not imply pathwise storage/time feasibility.

No unknown-kernel learning, generic POMDP solution, continuous-state synthesis,
arbitrary-language completion, all-architecture Pareto frontier or new empirical
capability follows from this exact finite interface.
