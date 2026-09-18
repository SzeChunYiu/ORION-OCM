# GMI #833 Section AE1 — exploitable-structure separation lattice: prospective freeze v1

Source `main`: `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`.

This freeze is committed **before** any executor, oracle, test, fixture, receipt
or reconciliation file of this package exists in the tree. The add-order of the
blobs is the custody evidence.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE1 — Define \`exploitable structure\` without handwaving`

1. `- [ ] Define task-relative exploitable structure formally; do not equate it with low entropy, nonuniform marginals, low manifold dimension, or compressibility alone.`
2. `- [ ] Separate marginal nonuniformity from dependence.`
3. `- [ ] Separate statistical dependence from predictive dependence.`
4. `- [ ] Separate predictive dependence from causal/control relevance.`
5. `- [ ] Separate existence of structure from accessibility to a resource-bounded learner.`
6. `- [ ] Separate finite-sample discoverability from asymptotic learnability.`
7. `- [ ] Define an architecture-independent \`structure available to agent A under resource budget R\` object or prove why no single scalar can do this.`
8. `- [ ] Construct minimal counterexamples for every false equivalence above.`

**No neighboring row is earned here.** In particular this tranche does not earn
any AE2, AE3, AE4, AE5, AE6, AE7, AE10, AE13, AE14, AE15, AE16 or AE17 row, and
does not earn any row of the #833 issue body.

## Frozen registered objects

A **registered world** is the tuple
`W = (X, Y, P, A, U)` where `X`, `Y`, `A` are finite ordered label sets, `P` is a
joint probability mass function on `X x Y` with every value an exact
`fractions.Fraction`, and `U : A x Y -> Fraction` is a utility. Every
probability in every registered world is rational; no float may appear in any
claim, receipt or test assertion.

A **registered causal world** additionally fixes a structural causal model over
a fixed finite DAG on the registered variables with rational mechanism tables,
so that both `P(y | x)` and `P(y | do(x))` are exactly computable.

A **budget** `R` is an element of a finite lattice frozen here:
`R = (junta_arity k, decision_tree_depth d, training_sample_count m)`, ordered
componentwise. The **rule class** `H_R` is the set of functions `X -> Y` that
are `k`-juntas of the registered coordinate decomposition of `X` *and* are
computable by a decision tree of depth at most `d` over those coordinates.
`H_R` is architecture-independent: it is defined by the coordinates a rule may
read and the branching depth it may use, never by a network, layer or parameter
count.

## Frozen predicates (all exactly rational)

- `MARG_NONUNIF(W)`: the `X`-marginal of `P` is not uniform.
- `DEP(W)`: there exist `x, y` with `P(x,y) != P_X(x) * P_Y(y)`.
- `PRED(W)`: `acc_obs(W) > acc_base(W)` where
  `acc_obs = sum_x max_y P(x,y)` and `acc_base = max_y P_Y(y)`.
- `CTRL(W)`: `sup_{policy: X -> A} E[U] > sup_{a in A} E[U(a, Y)]`.
- `CAUSAL(W)`: for the registered causal world, there exist `x, x'` with
  `P(y | do(x)) != P(y | do(x'))` for some `y`.
- `ACC(W, R)`: `max_{h in H_R} acc(h) > acc_base(W)`.
- `DISC(W, m)`: the Bayes-optimal learner over the registered hypothesis family,
  given `m` i.i.d. labelled draws, attains expected test accuracy strictly
  greater than `acc_base(W)`.
- `LEARN(W)`: `PRED(W)` (asymptotic learnability of the Bayes rule).

## Required evidence and falsifiers

- An exact separation table over a registered finite witness roster giving, for
  every frozen predicate, its exact truth value on every witness.
- For each of the five false equivalences named in rows 2-6, a witness world
  realizing the separating truth-value pattern, with all quantities exact.
- A **minimality** certificate for every witness: an exhaustive search over all
  strictly smaller alphabet shapes `(|X|,|Y|)` under the product order, across a
  registered finite probability grid (all joints whose probabilities are
  multiples of `1/D` for a frozen denominator `D`), reporting that no witness
  exists there; plus an analytic impossibility argument where one exists.
  Minimality is claimed only at this registered grid and shape order, never as
  minimality over all real-valued joints.
- Row 7 must be closed on **both** disjuncts: (a) an explicit order-reversal
  counterexample refuting every *budget-independent* scalar `sigma(W)` that is
  claimed to determine available structure, with the quantifier stated
  explicitly; and (b) the positive construction of the resource-conditioned
  achievable-accuracy profile object, proved well-defined and monotone on the
  frozen budget lattice.
- Two materially independent routes for every computational claim. Route A is
  the analytic/closed-form computation. Route B is an independently written
  oracle that imports nothing from the route-A module and recomputes each
  quantity by brute-force enumeration over the rule/function space.
- Hostiles: each deliberately broken variant must first be shown to actually
  move the quantity it perturbs (`perturbed != true`), and only then must the
  checker be shown to flag it. A hostile that cannot move its quantity is a
  package defect, not a pass.
- A null: randomized control worlds drawn from a registered exact-rational
  sampler must fail the separation the true witnesses pass, at a reported rate,
  and the no-alarm case must be asserted on the known-clean witnesses.
- Deterministic byte-identical `RESULT_V1.json` under `python3 -I -B` and
  `python3 -I -O -B`.

## Claim ceiling

`GMI_833_AE1_TASK_RELATIVE_EXPLOITABLE_STRUCTURE_SEPARATED_ON_REGISTERED_FINITE_WITNESS_ROSTER`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`,
`MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`,
`WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`,
`THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`,
`COMPLETE_GMI`, `UNIVERSAL_STRUCTURE_MEASURE`,
`MINIMALITY_OVER_ALL_REAL_VALUED_JOINTS`, `ARCHITECTURE_SELECTION_LAW`,
`GMI_MORPHOLOGY_PREDICTION`.

Nothing here is claimed novel against the parent literature. The parent-owned
mathematics (Shannon independence, Bayes decision theory, Pearl's do-calculus,
juntas and decision-tree lower bounds, PAC/statistical learning) is disclosed
in the package's parent-ownership section; the residual contribution is the
exact finite separation lattice with minimality certificates and the
budget-indexed profile object, not the underlying theorems.
