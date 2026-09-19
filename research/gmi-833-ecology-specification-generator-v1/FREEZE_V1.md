# Issue #957 / #833 Section G ecology/specification-generator freeze v1

Frozen parent: Issue #833. Frozen source main:
`fcbb8c08ce36b2970079ed715d5e757f28da46d2`.

The live Issue #833 body used to identify the target rows has SHA-256
`8483250b2f03400b9b18b11f1eb3c3e86176a5ce4662583bc30a8ba8c78325e7`.
The child Issue #957 scope body has SHA-256
`a90b0da4b441401ddc3d8a7d88abc82a249dd8c8088f258fc54ba42547cfac1b`.

## Exact closure target

This tranche targets exactly twenty-one unchecked Section G rows:

1. define an architecture-neutral generator of behavioral specifications;
2. define systematic environment/ecology families;
3. vary observability;
4. vary recurrence;
5. vary uncertainty/noise;
6. vary causal ambiguity/intervention access;
7. vary compositional structure;
8. vary spatial/locality structure;
9. vary symmetry/equivariance;
10. vary communication topology;
11. vary multi-agent competition/cooperation;
12. vary verification availability/cost;
13. vary memory price;
14. vary compute price;
15. vary communication price;
16. vary energy price;
17. vary developmental horizon;
18. vary nonstationarity/drift;
19. vary embodiment/sensor-action constraints;
20. construct matched positive/negative ecology twins; and
21. construct ecology families not designed around known architectures.

The two subsequent sampling-adequacy and sampling-bias rows remain open.

## Frozen registered-scope contract

The generator is a typed Cartesian product over exactly seventeen registered
finite ecology axes. Each carrier has at least two semantically distinct levels.
The generated syntax contains one registered opaque level token per axis and a
canonical semantic payload. Syntax well-formedness and semantic well-formedness
are separate predicates. A syntactically valid record with a payload that
contradicts its registered level must be rejected semantically.

Every generated ecology induces an external behavioral specification with a
finite probe-input carrier, finite response carrier, required input/response
relation, exact success score, and explicit resource limits. Generation and
scoring may use only the external ecology contract. They accept no implementation
or family label and contain none of the frozen known-family vocabulary.

For the registered finite carriers, the family iterator must enumerate every
coordinate tuple exactly once. Its cardinality must equal the independently
computed product of carrier sizes. This is finite registered-product completeness,
not completeness over all possible ecologies.

## Frozen witness and twin obligations

For each of the seventeen axes:

- two levels must differ in a load-bearing semantic quantity;
- a frozen external probe predicate must be false in the negative level and true
  in the positive level;
- a matched pair must differ only in that axis coordinate and corresponding
  canonical semantic component;
- the induced behavioral target relation must differ only on that axis probe;
- all other coordinates, semantic components, targets, and score rules must be
  byte-identical.

Opaque reminting of every carrier token by a bijection must preserve semantic
records, behavioral target relations, scores, product cardinality, and twin
isolation after token erasure. Independent arithmetic and iterator counts must
agree.

## Frozen architecture-neutrality rule

The registry, generator inputs, generated records, behavioral specifications,
scoring, and theorem statements may refer to externally observable ecology,
interaction, resource, and verification properties. They may not name, branch
on, reward, rank, or encode a known implementation/architecture family. Human
prose discussing this prohibition is not an operational field.

## Frozen claim boundary and falsifiers

The result is red if an axis is degenerate; syntax and semantics are conflated;
the family misses or duplicates a registered tuple; any matched twin changes
more than one coordinate or more than one behavioral target; a known-family name
enters generation or scoring; a remint changes token-erased semantics or scores;
normal and optimized receipts differ; or reconciliation targets anything beyond
the twenty-one frozen rows.

No claim is made about unbiased sampling, sufficient coverage of an unregistered
or infinite ecology universe, empirical representativeness, discovery of machine
architectures, real-world transfer, or a universal best ecology distribution.

Allowed terminal only after proof, exact replay, and package validation:

`GMI_833_ARCHITECTURE_NEUTRAL_REGISTERED_ECOLOGY_PRODUCT_AND_TWINS_PROVED`
