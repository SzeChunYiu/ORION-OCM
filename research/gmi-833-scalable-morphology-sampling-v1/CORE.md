# GMI #833-F scalable morphology probability sampling

This package implements the proof-first sampling design frozen in #1002 and
draft PR #1003. It samples the finite candidate population
`M(G0-fin-v1,B)` from #966 without enumerating or materializing that
population.

For budget `B=(N,R)`, the population is a disjoint union of `NR` strata. A
candidate with `n` labels and `r` registers is encoded as `n` base-`q(n,r)`
instruction digits, where `q(n,r)=1+3rn+rn^2`. Exact prefix sums plus this
mixed-radix code give a global rank/unrank bijection.

Two probability designs are exposed:

- global SRSWOR by Floyd's algorithm: exactly `k` ideal draw-oracle calls,
  `O(k)` working storage, and expected `O(k log k)` work here including sorted
  output; ideal inclusion is `k/M`, pair inclusion is
  `k(k-1)/(M(M-1))`, and the HT weight is `M/k`;
- positive stratified SRSWOR: one draw is reserved for every `(n,r)` stratum
  and the remainder is allocated by exact Hamilton largest remainders, with
  inclusion `m_h/H_h` and HT weight `H_h/m_h`.

At the registered large budget `(64,32)`, the population has 329 decimal
digits (1093 bits) across 2048 strata. Six boundary/interior ranks round-trip,
and a 4096-candidate stratified replay contains 4096 unique valid candidates
and represents every stratum. The population is never enumerated.

Probability results belong to the ideal independent-uniform draw design. The
counter-hash adapter provides deterministic replay only; it is not claimed to
be physical randomness. Global candidate-uniformity is syntactic within the
registered grammar, not semantic-uniformity. Stratification changes inclusion
probabilities and therefore exposes exact HT weights rather than hiding that
choice.

Claim ceiling:
`GMI_833_SCALABLE_LARGE_BUDGET_PROBABILITY_SAMPLING_DESIGN_AT_REGISTERED_G0_SCOPE`.

The adjacent 10^6-generation and 10^8/effective-coverage rows remain open.
This is not a #220/#221 HPC/QD execution, an unbounded sampler, a unique or
unbiased grammar, known-family recovery, or a complete GMI result.

## Reproduce

```bash
python3 -I -B research/gmi-833-scalable-morphology-sampling-v1/test_scalable_morphology_sampling_v1.py -v
python3 -I -O -B research/gmi-833-scalable-morphology-sampling-v1/test_scalable_morphology_sampling_v1.py -v
python3 -I -B research/gmi-833-scalable-morphology-sampling-v1/scalable_morphology_sampling_v1.py
```
