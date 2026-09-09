"""GPU lane for the GRAND SEARCH (issue #221 sec 18, worker O).

Scope (zoo protocol GPU constraint):
  * search-side surrogate training (torch on A40 when present, sklearn/stdlib
    ensemble otherwise) — NEVER a component inside an OCM organism (#71)
  * batch descriptor computation over cached compiled features
  * vectorized T0 firehose for the array-expressible micro-world subset

Array-expressibility declaration (exact, no OCM semantics rewritten):
  VECTORIZED  — the whole frozen T0 exact micro-world battery
    (evaluation/lifetime.py run_lifetime: all 8 world families
    method_acq / composition / scoped_failure / repr_twin / revocation /
    probe / similarity_recall / family_variant).  T0 is a fixed-tape
    deterministic cost-accounting simulation: no data-dependent iteration,
    no learned state, no external IO — every charge is a fixed arithmetic
    expression of per-organism compiled features, so a batched tape with
    per-organism accumulation preserved is BIT-IDENTICAL to the CPU
    reference (asserted by tests/test_gs_gpu_laptops.py against
    evaluation.lifetime.run_lifetime on diverse genomes).
  NOT VECTORIZED (stay CPU, by protocol):
    - genome compilation / invariant validation (morphology/compile.py —
      structural synthesis on python objects; never reimplemented on an
      accelerator)
    - the T2 developmental lifetime (evaluation/lifetime2.py — adaptive
      per-epoch state, branchy stack)
    - T1 (not implemented anywhere in the zoo)

Python compatibility: stdlib-only code paths run on CPython 3.8 through
3.14 (laptop billy: 3.8/3.9 + numpy; billy-old: 3.14, no numpy).  numpy /
torch / sklearn are OPTIONAL accelerators detected at import.
"""
