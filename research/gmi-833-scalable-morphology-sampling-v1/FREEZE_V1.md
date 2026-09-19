# Freeze V1 — scalable morphology probability sampling

Frozen before implementation under child issue #1002.

- source main: `324614bfc95a0f923d6dbaffd0fb2cbbbc4869b0`
- parent evidence: PR #966, `research/gmi-833-finite-candidate-space-v1/`
- target: only #833 Section-F row `Implement scalable sampling for large budgets.`
- authority boundary: #220 is read-only context; #221 owns the LUNARC/HPC morphology-zoo programme

## Registered design

For exact positive budget `B=(N,R)`, strata are ordered by `(r,n)` with `r`
outermost. Stratum size is `H_(n,r)=q(n,r)^n`, where
`q(n,r)=1+3rn+rn^2`; the population is their disjoint ordered union.

The implementation will provide:

1. exact global rank/unrank by prefix sums and base-`q` instruction digits;
2. global SRSWOR using Floyd's algorithm;
3. positive stratified SRSWOR when `k >= NR` using one guaranteed draw per
   stratum and exact Hamilton largest-remainder allocation of the balance;
4. exact first- and second-order inclusion probabilities and
   Horvitz–Thompson weights;
5. exact predicate hit/miss probability formulas and explicit failure
   boundaries;
6. a deterministic entropy adapter for replay, while limiting probability
   claims to the ideal independent-uniform design.

## Registered gates

- exhaustive rank/unrank agreement with the #966 enumerator on `(1,1)`,
  `(2,1)`, `(1,2)`, `(2,2)`;
- independent exhaustive Floyd trace oracle at population 5, sample 2;
- large-budget boundary/probe round trips at `B=(64,32)` without population
  materialization;
- a 4096-draw stratified replay at `B=(64,32)`, covering all 2048 strata;
- malformed-input, oversampling, underallocation, entropy-exhaustion, and
  out-of-range hostile tests;
- normal/optimized deterministic suites and a byte-stable receipt.

## Claim ceiling and exclusions

Claim ceiling:
`GMI_833_SCALABLE_LARGE_BUDGET_PROBABILITY_SAMPLING_DESIGN_AT_REGISTERED_G0_SCOPE`.

The 10^6 and 10^8 execution rows remain open. This tranche makes no claim of
unboundedness, grammar neutrality, semantic-uniform sampling, physical entropy,
QD/open-ended search, known-family recovery, or inference outside the
registered finite grammar.
