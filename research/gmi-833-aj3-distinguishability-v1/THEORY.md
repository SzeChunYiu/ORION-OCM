# AJ3 — distinguishability, access and decision relevance

## Scope

AJ3 consumes AJ2's registered operational response semantics. It does not introduce a bit, entropy or information variable as an ontological atom.

For two preparations `p,q` and an admissible test family `E`, let each test produce a registered outcome law. Define the operational distinguishability magnitude

`Delta_E(p,q) = sup_{e in E} TV(P(.|p,e), P(.|q,e))`.

At the frozen binary-outcome finite scope this is simply the maximum absolute difference of outcome-1 probabilities across the registered tests.

- **exact operational equivalence:** `Delta_E=0`;
- **perfect single-test distinguishability:** `Delta_E=1`;
- **approximate distinguishability:** use the magnitude or a declared threshold, without assuming the threshold relation is an equivalence relation;
- **probabilistic discrimination:** with equal priors in the registered binary hypothesis problem, optimal single-test success is `(1+Delta_E)/2`.

## Physical, accessible and decision-relevant distinction

Three layers are kept separate.

1. `Delta_phys`: maximum over all tests admitted by the registered substrate/laws.
2. `Delta_R`: maximum over the subset executable within a declared resource budget `R`.
3. `Delta_Q` / decision value: the improvement attainable for a registered decision problem or requirement family.

Because accessible tests form a subset, `Delta_R <= Delta_phys`; enlarging the budget cannot decrease the maximum. The finite certificate checks this across all 81 registered worlds and includes a hostile where only the expensive test separates the preparations: physical distinguishability is 1 while accessible distinguishability at budget 1 is 0.

Decision relevance is not physical distinguishability. For equal-prior hypothesis classification, observation value increases by `Delta/2`. For a constant-utility requirement that does not care which hypothesis is true, the same physically distinguishable pair has zero decision gain. Thus the requirement branch is essential.

## Approximate boundary

Naive epsilon-indistinguishability `Delta<=epsilon` is generally **not transitive**. At `epsilon=1/2`, response values `0`, `1/2`, `1` satisfy `0~1/2` and `1/2~1` but not `0~1`. Therefore AJ3 forbids treating thresholded approximate indistinguishability as a quotient equivalence without an additional construction.

## Information is derived after probability semantics

Only after a prior and outcome probability model are registered may an information measure be computed. As frozen controls, an equal-prior perfect binary test yields one Shannon bit and identical laws yield zero. Those values are derived coordinates of the chosen experiment; they are not assumed as primitive ontology and no AJ3 theorem depends on Shannon units.

## Blackwell / Le Cam / decision-sufficiency connection

The decision-relevance layer is deliberately compatible with statistical experiment comparison: an experiment is useful insofar as it changes attainable risk/value for declared decision problems. Existing #833 Blackwell/Le Cam and decision-sufficiency results retain ownership of their stronger experiment-comparison theorems. AJ3 only supplies the lower operational distinction/access layer feeding those results and does not reify the quotient inside the machine.

## Parent ownership

Total variation, binary hypothesis testing, statistical decision theory, Shannon information, operational/general probabilistic distinguishability, Blackwell comparison and Le Cam deficiency are parent mathematics. The GMI residual is the explicit layer separation and executable bridge from AJ2 operational tests to resource-accessible and requirement-relative distinction.

## Claim ceiling

`AJ3_DISTINGUISHABILITY_RESOURCE_ACCESS_AND_DECISION_RELEVANCE_AT_FINITE_REGISTERED_SCOPE`

Forbidden promotions include universal approximate quotients, equality of physical/access/decision distinction, ontological-bit claims, and internal representation of the scientist-side quotient.
