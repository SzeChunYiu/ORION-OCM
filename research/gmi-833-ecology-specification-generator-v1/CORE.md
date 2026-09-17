# Architecture-neutral ecology/specification generator v1

Issue #957, child of Issue #833 Section G. This package closes the frozen
computation-light generator tranche by defining a typed external ecology product,
not by sampling a few hand-picked tasks.

The registered family has seventeen binary semantic axes and therefore exactly
`2^17 = 131072` members. Each axis has:

- an opaque two-element carrier;
- a canonical external semantic payload;
- an independently evaluated probe predicate with values `false` and `true`;
- a one-coordinate matched negative/positive twin.

Every well-formed member maps to a finite behavioral contract: seventeen probe
inputs, binary responses, an exact required relation, an exact scoring rule, and
explicit price/horizon/verification terms. The construction has no
implementation-family argument. Syntax validation and semantic validation are
separate; a same-shaped but semantically inconsistent hostile is accepted by the
former and rejected by the latter.

Reproduce the exact evidence:

```bash
python3 -I -B research/gmi-833-ecology-specification-generator-v1/test_ecology_specification_generator_v1.py -v
python3 -I -O -B research/gmi-833-ecology-specification-generator-v1/test_ecology_specification_generator_v1.py -v
python3 -I -B research/gmi-833-ecology-specification-generator-v1/ecology_specification_generator_v1.py
```

The iterator count, recursive count, arithmetic product, and unique mixed-radix
rank count independently agree. A disjoint opaque-token remint preserves
token-erased semantics, specifications, exact scores, family size, and twin
isolation.

Claim ceiling:

`GMI_833_ARCHITECTURE_NEUTRAL_REGISTERED_ECOLOGY_PRODUCT_AND_TWINS_PROVED`

This proves completeness only for the registered finite product. It does not
claim sufficient or unbiased sampling of a wider ecology universe, quantify
sampling uncertainty, recover implementation families, or establish empirical
transfer.
