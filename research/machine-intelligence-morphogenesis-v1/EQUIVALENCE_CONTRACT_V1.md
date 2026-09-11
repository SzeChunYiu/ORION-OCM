# Bounded Morphology Equivalence v1

A core Track-B risk is to call two syntactically different programs “different forms of intelligence” when they are merely alternate encodings of the same computation. Conversely, input/output equivalence alone can collapse systems whose **learning dynamics** are materially different.

This contract therefore separates three relations.

## 1. Behavioral preorder

For ecology `E`, tolerance `eps_Q`, and resource transformation bound `(alpha,beta)`, write

\[
M_1 \preceq^{beh}_{E,\epsilon,\alpha,\beta} M_2
\]

when there exists a registered compiler/wrapper `kappa: M1 -> M2` such that on all tasks in the finite exact scope, or with the declared statistical guarantee on sampled scope:

1. verified task outputs/capability of `kappa(M1)` match `M1` within `eps_Q`;
2. verifier/terminal semantics are preserved;
3. the declared resource vector satisfies

\[
R(\kappa(M_1),\tau) \preceq \alpha\odot R(M_1,\tau)+\beta.
\]

Symmetry gives bounded behavioral equivalence.

This relation is insufficient for Track B because two systems can compute the same current function but adapt differently after new experience.

## 2. Developmental preorder

Write

\[
M_1 \preceq^{dev}_{E,\epsilon,\alpha,\beta} M_2
\]

when a compiler preserves not only current task behavior but the registered **experience -> update -> later behavior** trajectory.

For every development sequence `h` in the exact registered set (or declared distribution):

```text
initial morphology
-> consume h_1
-> updated morphology
-> ...
-> consume h_n
```

require:

- capability vector after each registered checkpoint within `eps_Q`;
- retained/forgotten competence within `eps_D`;
- update outcomes and future task behavior within declared tolerance;
- update/resource cost bounded by `(alpha,beta)`;
- the compiler may not recompute from hidden target labels unavailable to the original morphology.

Symmetry yields developmental equivalence:

\[
M_1 \approx^{dev}_{E,...} M_2.
\]

A Track-B “morphology family” should preferably be an equivalence class or cluster under this stronger relation.

## 3. Structural relation

Structural descriptors such as topology, parameter distribution, rule count, modularity or memory organization are secondary observables. They help interpret phase transitions but do not define intelligence-form identity by themselves.

A structural difference is scientifically meaningful only if it survives at least one of:

- developmental non-equivalence;
- resource-frontier difference;
- robustness/revision/transfer difference;
- provable bounded-compilation separation.

## 4. Exact finite protocol

For tiny complete worlds:

1. enumerate every legal morphology up to the frozen grammar bound;
2. enumerate every registered input/task and developmental sequence;
3. compute phenotype exactly;
4. compute candidate compilers/wrappers from the frozen compiler class;
5. quotient morphologies by exact developmental equivalence where tractable;
6. report both syntactic count and semantic/developmental class count.

This is the preferred calibration before stochastic search.

## 5. Approximate/statistical protocol

For larger systems, the relation becomes an empirical preorder with uncertainty. Required:

- disjoint evaluation tasks;
- frozen metric/tolerance/resource coordinates;
- paired developmental interventions;
- confidence/credible bounds;
- explicit `NON_IDENTIFIABLE_AT_CURRENT_RESOLUTION` when equivalence cannot be resolved.

Never turn failure to distinguish into proof of equivalence.

## 6. Morphology novelty gate

A candidate `M*` may be called `NEW_MORPHOLOGY_CANDIDATE_AT_SCOPE` only if:

1. it is **not developmentally equivalent to any registered known parent morphology** under the strongest feasible compiler class;
2. the separation is not caused solely by an arbitrary resource price chosen after outcomes;
3. it occupies a reproducible new Pareto/developmental region on disjoint ecologies;
4. its advantage survives a reminted encoding/implementation where feasible;
5. a stronger parent family has not been omitted.

Equivalently, a candidate that is developmentally equivalent to even one registered known parent fails the novelty gate and must be classified under that parent/equivalence class.

Forbidden conclusion from this gate alone: `NEW_FORM_OF_INTELLIGENCE_PROVEN`.

## 7. Important counterexamples to construct

- same current truth table, different learning update;
- same behavior and learning, very different syntax;
- neural network compiled to an explicit program with huge overhead;
- program compiled to a neural emulator with huge training cost;
- two representations identical on training tasks but different under revision/drift;
- stochastic and deterministic systems indistinguishable only because the registered ecology never exposes uncertainty.

These are required hostiles for the later equivalence implementation.