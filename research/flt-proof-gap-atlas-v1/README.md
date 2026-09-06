# FLT Proof Gap Atlas v1 — hermetic benchmark contract

This package supplies a **development/evaluation contract** for a formal-mathematics
instantiation of OCM's epistemic-experience programme.  It turns Anthropic's
published Fermat's Last Theorem formalization into a prospectively registrable
proof-gap benchmark without treating the published proof as the only possible
route.

It does **not** execute the protected mathematical study, establish theorem
novelty, establish an OCM advantage, unlock N4, or close the proof-route
acceptance gate.  Negative and `CANNOT_CHECK_*` terminals remain first-class
results.

## Relationship to `flt-kso-v1`

Open FLT-KSO prerequisite work in PRs #129/#130 already owns the native proof
boundary, Anthropic DAG/sanitizer work, bounded R1 construction and staged R2/R3
execution.  This Atlas package is an **evaluator/route-network contract**, not a
second proof runtime.

After one FLT-KSO substrate is qualified and lands, Atlas implementations should
consume that canonical substrate rather than copy its search, checker, KSO
admission, sealing or DAG logic.  Any integration commit must bind the exact
qualified FLT-KSO source identity.  Until then this package remains additive and
read-only with respect to those branches.

## Upstream source pin

`SOURCE_PIN_V1.json` pins:

- `anthropics/fermats-last-theorem`
  `aa2d8b34692b16c70f699536de0d8e75b9a3e9ef`;
- Lean `leanprover/lean4:v4.33.1`;
- Mathlib `v4.33.0`,
  `db584cd6d46c92f209a44c0f1c829460d327499d`;
- 1,450 definition modules, 29,511 statement modules and 29,511 proof
  modules in the upstream import closure.

The source pin is **not** yet a registered search universe.  A protected run
requires an independently generated declaration inventory and all remaining
fields below to be frozen before protected outcome access.

## Scientific question

The benchmark asks:

> Can OCM reconstruct, reroute and repair mechanically verified mathematical
> support structures under prospectively frozen information and resource
> constraints, and does accumulated verified experience make later proof
> construction cheaper or more robust?

It does not ask OCM to enumerate "all proofs of FLT".  Raw proof-term space
contains arbitrarily many cosmetic or semantically equivalent variants.

A permitted bounded claim is:

`ALL_NORMALIZED_ROUTES_WITHIN_BOUND_FOUND`

and only when the declared search is actually exhaustive and carries a bound
completeness certificate.

The terminal `ALL_FLT_PROOFS_FOUND` is forbidden by `contracts.py`.

## Frozen finite universe

Every registered challenge belongs to

\[
U = (E, L, O, B, \approx)
\]

where:

- **E — environment:** exact source commit, Lean toolchain, Mathlib identity and
  permitted checker inventory;
- **L — library:** the exact declaration inventory visible to the solver,
  source-bound by SHA-256;
- **O — operators:** a finite, explicit proof-generation/operator inventory;
- **B — budget:** named finite resource ceilings, not one post-hoc cost score;
- **≈ — normalization:** a versioned, computable route-family contract.

`validate_universe` rejects missing or non-finite declarations, duplicate
operator inventories and invalid resource ceilings.  The declaration inventory,
operator list, budgets and normalization version are all part of the frozen
identity.

Changing one of them creates a different universe and therefore a different
experiment.

## Hermetic Challenge → Submission → Checker boundary

Do **not** create a challenge by deleting text in-place from the upstream source
tree.

The upstream theorem wrappers are not a safe solver view: a theorem module can
import its corresponding `P2M/Sol/S_*.lean` module and then expose the theorem.
A solver that can read the original theorem wrapper or solution bytes therefore
has an answer channel.

Each Atlas challenge must instead synthesize an isolated challenge declaration
that preserves the exact target statement while making both of these modules
unavailable:

1. the target theorem wrapper;
2. the target original solution module.

The registered solver view must assert and the harness must independently check:

- `network_access == false`;
- `solution_bytes_present == false`;
- `theorem_wrapper_present == false`;
- exact target statement hash;
- exact visible-declaration inventory hash;
- both target modules in the forbidden-module set;
- exact registered operator identity;
- exact registered resource budget;
- exact route-normalization version.

`validate_challenge` fails closed on any mismatch.  These metadata checks do not
by themselves prove filesystem isolation; the protected harness must produce a
source-bound custody/environment receipt.

## Gap classes

The registered Atlas supports the following increasing intervention classes.

| Class | Intervention | Primary ability |
|---|---|---|
| G1 | Hide one proof body; expose target and permitted dependencies | proof completion |
| G2 | Hide original dependency choices | dependency discovery |
| G3 | Remove a connected multi-theorem region | multi-obligation repair |
| G4 | Hide original intermediate statements | lemma invention |
| G5 | Prohibit one or more dependencies from the original route | alternate-route discovery |
| G6 | Remove a bridge/cut between verified regions | bridge invention |
| G7 | Ablate a substantial major-component implementation | alternate component architecture |
| G8 | Prohibit substantial portions of the published FLT route | alternate root support DAG |

G1 is suitable for a broad leave-one-proof-out corpus.  G4–G8 require stronger
contamination, novelty and correspondence review and should not inherit a
scientific label from G1 merely because Lean accepts the final term.

## Two campaigns

### Atlas-A — leave-one-proof-out breadth

Generate one hermetic G1 challenge for each safely extractable theorem/proof
pair.  The published 29,511 statement/proof pairs define the candidate source
population, but the actual registered challenge count must be the count emitted
by the sanitizer after all exclusions and custody checks.

Each challenge ends in one registered terminal such as:

- `SOLVED`;
- `TIMEOUT`;
- `NOT_FOUND_WITHIN_REGISTERED_BUDGET`;
- a reasoned `CANNOT_CHECK` or existing more-specific `CANNOT_CHECK_*`.

Do not rewrite timeout or bounded search failure as proof impossibility.

### Atlas-B — adversarial proof-network destruction

For prospectively selected landmarks, destroy or prohibit original support and
search for another checked route.  Interventions include original-route
ablation, connected cuts, bridge deletion and progressively larger dependency
removals.

After a first route is found, a separately registered diversity phase may seek
another route subject to a minimum registered route-distance condition.  The
diversity phase consumes its own search budget.

## Proof routes are AND/OR support hyperedges

For target theorem `T`, OCM may retain independently checked routes such as

```
ProofRoute(T, π1, dependencies={A,B})
ProofRoute(T, π2, dependencies={C,D,E})
ProofRoute(T, π3, dependencies={F})
```

The warrant condition is conceptually:

\[
W(T) = \bigvee_i \left[E(π_i) \land \bigwedge_{d\in D_i} W(d)\right].
\]

A theorem remains live while at least one complete checked route survives.
Revoking support for one route must not kill unrelated surviving routes.

`validate_route` binds a route to:

- the exact challenge;
- the proof hash;
- the exact dependency-set hash;
- one registered checker identity;
- accepted checker evidence;
- a route metric vector;
- a normalization family and novelty class.

`theorem_liveness` supplies the finite development control for alternative-route
survival.  It is not a substitute for OCM's full recursive warrant engine.

## Route diversity and novelty

Cosmetic source differences are not scientific route diversity.  Route-family
classification must be prospectively versioned and can use:

- dependency-set distance;
- landmark-theorem distance;
- new intermediate-lemma count;
- proof-operator sequence distance;
- proof-DAG topology;
- proof size/checker cost;
- high-level strategy classification.

`dependency_distance` reports exact dependency Jaccard distance and explicitly
returns `semantic_novelty: NOT_ESTABLISHED`.  A large graph distance is not a
mathematical novelty certificate.

Recommended novelty ladder:

1. exact/near reconstruction;
2. retrieval of an already available theorem/proof pattern;
3. new recombination of existing dependencies;
4. alternate dependency family;
5. library-new intermediate lemma;
6. new bridge architecture;
7. candidate new mathematical strategy.

"Library-new" means absent from the prospectively frozen allowed library.
Claims of novelty to mathematics require a separate literature search and
independent mathematical review.

## Pareto proof network

Do not force route quality into one scalar.  Register minimization or
maximization direction per metric and retain a Pareto frontier over values such
as:

- dependency count;
- proof size;
- checker cost;
- search cost;
- active KSO size;
- reusable method count;
- robustness to revocation;
- measured future reuse value.

`pareto_frontier` supplies a simple minimization-only development primitive.
A protected analysis must register metric direction and any transformations
before outcome access.

## Outcome and checker evidence

`validate_outcome` does not run a checker.  It validates that an outcome is
bound to the exact challenge and registered resource names/ceilings.

`SOLVED` requires source-bound accepted checker evidence for the exact target
statement and proof.  `TIMEOUT`, bounded not-found and `CANNOT_CHECK*` cannot
carry accepted-proof evidence.

The strong enumeration terminal additionally requires:

- `search_exhaustive == true`;
- a `completeness_certificate_sha256`.

Even then the claim is only about normalized routes in the declared bounded
universe.

All validator returns set or imply that **scientific claim authority remains
external**.  Passing development contracts does not establish OCM superiority,
independent novelty, or protected-study validity.

## Required graph layers

The public citation DAG is evaluator/reference material, not automatically the
complete logical support graph.  A protected Atlas generator should separately
record at least:

1. public/source citation edges;
2. elaborated proof-term constant dependencies;
3. definition dependencies;
4. external Mathlib/upstream dependencies.

A graph cut or bridge deletion is valid only relative to the actual permitted
solver environment.  Removing an edge from the visual citation graph while
leaving an equivalent constant or upstream lemma visible is not route
destruction.

## Contamination and provenance controls

Because the FLT artifact is public, a serious generativity study must treat
retrieval and training contamination as explicit threats.

At minimum register:

- no-network solver execution;
- absence of target proof bytes and theorem wrapper;
- exact source/environment snapshot;
- visible declaration inventory;
- upstream/provenance labels;
- whether a produced route reproduces material already present in another
  accessible source;
- any identifier/randomization transformation used for contamination controls.

Randomized names do not establish absence of training contamination, and
kernel-valid output alone does not establish independent discovery.

## Reporting

Do not collapse Atlas-A into one `29511`-denominator accuracy unless exactly
29,511 sanitized challenges are successfully registered and run.

Report strata including, where available:

- mathematical component/family;
- original proof size;
- graph depth;
- visible-premise count;
- transitive dependency size;
- provenance/Mathlib overlap;
- statement complexity;
- gap class;
- registered resources.

Report at least challenge-level coverage, family-level macro summaries and
cost-to-solve distributions.  Keep checker validity, route diversity,
mathematical novelty and lifetime cognition as distinct endpoints.

The lifetime-cognition target is prospective reduction in later work, e.g.

\[
\Delta P(\text{future gap solved}\mid K_t)
\]

and/or a reduction in registered search/checking cost as the verified knowledge
state `K_t` grows.  More stored proofs without cheaper or more robust future
cognition is not sufficient evidence for amortized machine-native cognition.

## OCM task boundary

This lane supplies the missing **formal-mathematics benchmark instantiation
contract** needed by the cross-cutting epistemic-experience work and the
proof-route acceptance programme.

It deliberately does not claim these still-external steps:

- execution of an unseen prospective proof-composition study;
- demonstrated learned/reused proof methods that reduce later cost;
- protected revocation/path-destruction results;
- independent theorem-correspondence or mathematical-novelty review;
- the predecessor receipt required to unlock the N4 formal-mathematics track.

Therefore:

- issue #62 may use this lane as the concrete mathematics/Proof Gap Atlas
  instantiation and registration substrate;
- issue #38 remains the acceptance gate for executed prospective evidence;
- issue #46 remains **LOCKED** until its roadmap predecessor closes with the
  required receipt.

Do not close #38 or #46 from this package alone.

## Development replay

Run:

```sh
cd research/flt-proof-gap-atlas-v1
python test_contracts.py
```

The current development suite contains 17 controls covering:

- finite-universe validation;
- hermetic challenge identity;
- target solution/wrapper leakage;
- universe/operator drift;
- negative and `CANNOT_CHECK_CONSUMPTION` terminals;
- forbidden unbounded all-proofs claims;
- bounded-exhaustiveness certificates;
- resource overruns;
- exact route/dependency checker binding;
- alternate-route revocation survival;
- exact dependency distance without novelty inflation;
- Pareto-route selection.

These are authored development checks, not independent scientific review.

## Next executable gate

Before any protected Atlas-A run, generate and review a prospective
`FROZEN_UNIVERSE_V1.json` containing the **real declaration-inventory SHA-256**,
finite operator grammar, resource ceilings, normalization version, challenge
sanitizer identity, checker/environment identities and exclusion policy.

Do not fabricate the declaration inventory hash in advance.  `SOURCE_PIN_V1`
intentionally stops at `SOURCE_PINNED_NOT_STUDY_REGISTERED`.
