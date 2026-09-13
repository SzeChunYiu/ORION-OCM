# Reproduction, parents and cost scope

Run on laptop billy:

```sh
python -I -B test_adaptive_rows_v1.py -v
python -I -O -B test_adaptive_rows_v1.py -v
python -I -B check_adaptive_rows_v1.py
python -I -O -B check_adaptive_rows_v1.py
```

Compare each complete decoded checker payload with the retained receipt.
The grand replay also binds all packet bytes and supplies a fresh import-cache
location. Passing a status field alone does not reproduce the evidence.

The sampler oracles use exact rational Bernoulli path probabilities. The
single-row first-failure dynamic program is checked against every bitstring
on small horizons. Thirty-six two-row controls then use fixed, history-based
allocation/stopping rules, including adaptive preference for higher or lower
empirical means. Full-law normalization is asserted at every completed run.
These are finite authored checks, not independent observations or empirical
evidence that any external data source has the required conditional law.

The positive Taylor series satisfies exp(x)>=sum_(j=0)^m x^j/j! for x>=0.
Its reciprocal therefore gives an upper concentration bound. Eight terms are
an implementation choice, not a statistical optimum. Binary search returns
the smallest certified j/n; n itself is always valid because TV cannot exceed
one. The rule remains conservative as n increases. For any fixed e>0 and
degree m>=3, its positive m-th term grows as n^m while the allocated inverse
error grows as n^2, so a grid radius near e eventually passes. Thus radii tend
to zero if a row is sampled indefinitely; this does not prove infinite visits.

Confidence calculations require exact rational arithmetic and counters; their
bit complexity, model storage, transcript custody, policy synthesis and
controller implementation are additional work. Sampling costs use actual
per-row visit counts and the declared acquisition/interface charges. No timing
or memory saving is claimed. FMT policy transfer is reused through its analytic
simultaneous-TV premise; its policy census is not claimed as rerun here.

Primary sources and subtraction:

- [Howard et al., 2021, §§1–2](https://arxiv.org/pdf/1810.08240): time-uniform
  inference and optional monitoring; their sharper methods are not implemented
  or presented as an ARC invention.
- Weissman et al., HPL-2003-97R1, finite-alphabet concentration: union over the
  nonempty proper alphabet subsets. The FMT packet already states the parent
  and preserves its finite-alphabet assumptions.
- [FC-T7, §8.2 at 28bc6515](https://github.com/SzeChunYiu/ORION-OCM/blob/28bc6515/docs/spec/OCM_FOUNDATIONS_CLOSURE_V1.md):
  inherited telescoping error allocation. ARC retains visit-index conditioning
  and row semantics explicitly; it does not renew this donor's empirical gates.
- [FMT at dbf9d4f8](https://github.com/SzeChunYiu/ORION-OCM/blob/dbf9d4f863098693f490939a3aed4f397b6a0011/research/gmi-grand-unification-v1/FINITE_DATA_MODEL_TRANSFER_THEOREM_V1.md):
  inherited sharp common-policy probability/work transfer, including augmented
  known fees and the buffered comparator.

The full FMT and historical FC-T7-containing documents are preserved under
`raw/`. They are parent records, not modified ARC claims or new registrations.
