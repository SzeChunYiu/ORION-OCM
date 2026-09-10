"""OCM Form Oracle V1 — self-built residual only (#277 sec 7 + #233 D26/D27).

Everything reusable is imported from research/ocm-morphology-zoo-v1:
  search/successive_halving.py  multi-fidelity rungs (T0->T1->T2, eta=3)
  search/mome.py                per-niche Pareto archive structure
  search/novelty_viability.py   behaviour-keyed archive
  evaluation/lifetime2.py       T2 developmental lifetime + RESET control
  evaluation/t3_ecology.py      key-parameterised held-out family generator
  morphology/gs_bound.py        legality-filtered (F,O,Pi) enumeration

This package contains ONLY what has no upstream: a k-objective Pareto over a
4-vector the frozen 10-name registry cannot express, the full-lifetime burden
estimator including rejected-candidate work, the evolvability estimator, the
behaviour signature, the C-immutability hard gate and the D26/D27 harnesses.
"""
