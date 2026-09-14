# Development-only capability predictor v1 — formalization

## Scope

This capsule addresses only the #602 F4 row **“Fit/derive capability predictor only from development worlds.”** It does not evaluate held families and does not claim G6.

The predictor sees five architecture-name-free signed margins derived from the registered morphology/ecology/resource contracts:

- `m`: retained-state capacity minus required memory distinctions,
- `p`: planning depth minus required planning horizon,
- `c`: communication distinctions minus required coordination distinctions,
- `r`: routed proposal coverage minus required proposal coverage,
- `v`: verification coverage minus required proposal coverage.

The registered development corpus is the exhaustive cube `{-1,0,1}^5`, hence 243 worlds. No family identity or held-out outcome field is present.

## Registered finite capability map

For a world `x=(m,p,c,r,v)` define

- `memory_exact(x) = 1[m >= 0]`,
- `planning_exact(x) = 1[m >= 0 and p >= 0]`,
- `coordination_exact(x) = 1[c >= 0]`,
- `verified_tool_exact(x) = 1[r >= 0 and v >= 0]`.

Each target is monotone under componentwise order.

## Theorem F4-D1 — monotone-envelope soundness

Let `D` be any finite development corpus with binary target `f` that is monotone under componentwise order. For query `q`, define:

- positive lower witness: some `(x,1) in D` with `x <= q`;
- negative upper witness: some `(y,0) in D` with `q <= y`.

Then:

1. if a positive lower witness exists, every monotone extension of `D` has `f(q)=1`;
2. if a negative upper witness exists, every monotone extension has `f(q)=0`;
3. both witness types cannot coexist in a monotone corpus;
4. if neither exists, monotonicity alone does not justify a determinate prediction, so the registered output is `CANNOT_IDENTIFY`.

### Proof

For (1), monotonicity gives `1=f(x) <= f(q)`, forcing `f(q)=1`. For (2), `f(q) <= f(y)=0`, forcing `f(q)=0`. If both existed, `x <= q <= y` would imply `1=f(x) <= f(y)=0`, contradiction. Item (4) is a claim-boundary rule: without an order witness, this predictor has no registered basis for choosing either binary value.

## Theorem F4-D2 — exact replay on the registered development cube

Training the envelope predictor on all 243 registered worlds reproduces every registered capability vector exactly.

### Proof

Every query point `q` in the registered cube occurs in the corpus. If `f(q)=1`, `q` itself is a positive lower witness. If `f(q)=0`, `q` itself is a negative upper witness. By F4-D1 the emitted value equals the registered target. Apply independently to all four targets.

## Why this is not G6

The predictor has not yet been challenged on a held family. It establishes a leakage-resistant development-only fitting/derivation protocol and an exact finite predictor at the registered development scope. Held-family prediction, resource repricing, ablation, drift and real-regime transfer remain separate gates.

## Strongest parent subtraction

This is a direct finite use of isotonic/monotone classification and partial-order concept learning. The GMI-specific residual is procedural: the predictor-visible inputs are tied to the architecture-name-free morphology/ecology/resource contracts, held-family identity/outcomes are forbidden at fitting time, and `CANNOT_IDENTIFY` is mandatory outside the identified order region. No novelty claim is made for the order-theoretic theorem itself.
