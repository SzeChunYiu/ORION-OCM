# Complete continuation state: read first

V8 repairs the missing operational premise between contextual attainability
and state abstraction. Control plane: [#1068](https://github.com/SzeChunYiu/ORION-OCM/issues/1068).

A state may be merged with another only if every finite continuation has the
same observed behavior, including illegal continuations, undefined evaluation,
intermediate outputs and declared resource costs. The quotient has executable
transitions. Arbitrary exactly sufficient encodings map onto it; they need not
themselves support deterministic updates.

- [General statements and proofs](THEORY_V8.md).
- [Kernel proofs](ContinuationV8.lean).
- [Finite implementation](continuation_v8.py) and [independent oracle](independent_oracle_v8.py).
- [Frozen evaluation](FREEZE_V8.md) and [exact receipt](RESULT_V8.json).
- [Parent ownership](PARENTS_V8.json); no novelty claim for classical minimization.
- [Next foundation repairs found during review](NEXT_FOUNDATION_REPAIR.md).
- [Resource-threshold prediction to test next](NEXT_RESOURCE_PREDICTION.md),
  with known parent results and explicit falsifiers; not a verified new discovery.

This covers arbitrary deterministic partial machines mathematically and finite
ones algorithmically. It does not establish stochastic or nondeterministic
bisimulation, effective infinite-state minimization, useful architecture
discovery, novel empirical predictions, or complete R0–R17 closure.
