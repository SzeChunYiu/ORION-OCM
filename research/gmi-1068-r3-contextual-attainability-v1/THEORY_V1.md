# R3 — contextual attainability as the master derived attainable-value object

For a start configuration `x` and a context `kappa`, let `Hist_S(x)` be the substrate-admitted **finite** histories beginning at `x`. R2 permits a partial evaluator:

`nu_kappa : Hist(C_S) ->? W_kappa`.

The contextual attainability set is the image of admissible histories on the evaluator's defined domain:

`A_kappa(x) = { w in W_kappa | exists h in Hist_S(x) with nu_kappa(h) = w }`.

Undefined evaluations contribute no value. Distinct histories may map to the same value, so `A_kappa(x)` is a value image, not a history set.

For a declared restriction `B`, let `Hist_S^B(x) subset Hist_S(x)` and define `A_kappa^B(x)` by the same image construction.

## R3-1 conditional monotonicity

For any history sets `H1 subset H2`, the contextual image of `H1` is a subset of the contextual image of `H2`, after intersecting both sets with the evaluator's defined domain.

Thus attainability is monotone under **actual inclusion of admissible histories**. A numeric quantity called "budget" does not by itself establish this premise: a budget family must be registered so that larger budget really induces a nested admissible-history set.

## R3-2 order and frontier

The context supplies a preorder `<=_kappa`. Its strict part is:

`u <_kappa v  iff  (u <=_kappa v) and not (v <=_kappa u)`.

A finite frontier is the set of attainable values for which no strictly better attainable value exists. Preorder-equivalent values are not artificially ordered.

No existence of maximal elements is asserted for arbitrary infinite preorders without additional conditions such as compactness, chain conditions, well-foundedness, or an appropriate maximality theorem.

## R3-3 what is and is not derived from attainability

`A_kappa(x)` is the master **attainable-value object relative to the rest of the declared context/process structure**. The bare set alone does not determine all GMI notions.

- **Capability.** Given a context-declared success region `G subset W_kappa`, finite-history capability is `A_kappa(x) intersect G != empty`.
- **Impossibility.** Relative to a declared target `T subset W_kappa`, finite-history impossibility is `A_kappa(x) intersect T = empty`.
- **Frontier / preference shorthand.** These require the inherited context preorder. The bare attainable set does not encode which direction is better.
- **Resource response, value-borne form.** If contextual values explicitly contain a resource coordinate, a declared projection `rho : W_kappa -> R` may be applied to `A_kappa(x)`. The finite fixture declares its second coordinate to be cost and tests that exact projection.
- **Resource response, reachability-borne form.** If changing resources changes which histories are admissible, the object is instead a registered family such as `r -> A_kappa^{B_r}(x)`, and monotonicity requires a proved nesting relation on the `B_r`. R3 does not collapse these two resource semantics.
- **Barrier witness.** A baseline attainable set cannot identify a unique causal barrier. A registered one-step enabling witness is defined only relative to a declared admissibility-relaxation or intervention family `Delta`: a relaxation is enabling when the relaxed attainable set intersects the target. Minimal or causal barrier claims need an additional order, cost, or causal semantics on `Delta`.
- **Context-family regime change.** Comparing frontiers or selected optima across a family `kappa_theta` requires either a common result space/order or an explicit transport between result spaces. The finite R3 fixture proves an argmax-regime switch, including its tie boundary. It does **not** promote that switch to a thermodynamic, statistical-mechanical, or nonanalytic "phase transition" without additional topology or regularity.

These qualifications preserve the candidate two-factor foundation `G_S = (C_S, K)`: the extra ingredients above are declared inside the process/context presentation or inside explicitly registered comparison/intervention structure. They are not silently manufactured from the unlabelled attainable set.

## R3-4 finite-history boundary

The R3 attainable-value object is generated from finite histories. Therefore it does not, by itself, decide claims whose witness exists only as:

- an infinite trace;
- a limit point of longer finite traces;
- an almost-sure or asymptotic event;
- a limiting average or stationary quantity;
- a topological/measure-theoretic completion point not attained by any finite history.

Such claims require an explicit trace-completion, topology, sigma-algebra, convergence notion, or other limit semantics. A sequence of increasingly good finite outcomes is not silently identified with attainment of its limit.

## R3-5 retirement of legacy foundation symbols

`Gamma`, `Pref`, and `SEL` may remain conservative abbreviations where an old theorem explicitly supplies the required target, order, projection, or selector structure. They are removed from the universal primitive list.

No historical theorem transports automatically. Each transport must restate:
1. its original quantifiers;
2. whether its evaluator was total or partial;
3. whether it reasoned over histories or contextual values;
4. which order, resource, and success structure it assumed;
5. whether resources changed values, admissible histories, or both;
6. whether it compared distinct contexts through a legitimate common space or transport;
7. whether it made finite-horizon or infinite/asymptotic claims.

## R3-6 registered finite hostile results

The executable fixture contains:
- six finite histories;
- one evaluator-undefined history;
- two distinct histories with the same contextual value;
- four unique attainable contextual values;
- a nested two-history restriction;
- a three-point finite Pareto frontier;
- a capability threshold that is impossible under the restricted set and attainable under the full set;
- an explicitly declared cost projection, with four full-set resource levels and two restricted-set resource levels;
- three distinct one-step enabling witnesses, demonstrating non-uniqueness of a "barrier" absent further minimality semantics;
- a scalar-context family with a switch at `lambda = 3/2`, where the boundary is a tie rather than a unique winner.

Nine planted hostile interpretations are rejected. The optimized Python route is required to execute the same fail-closed checks as the normal route, and a source-separated oracle recomputes the finite results.

## Claim ceiling

`GRAND_GMI_V2_R3_CONTEXTUAL_ATTAINABILITY_MASTER_CARRIER_AT_REGISTERED_FINITE_HISTORY_SCOPE`
