# Independent hostile audit — #759

This review was performed after the pre-implementation freeze and after an independent reference implementation of the frozen theorem was built separately from the branch executor. It does not alter the frozen claim or expected controls.

## Review lenses

### Formal methods

Checked the quantifiers in UC-1 through UC-4, the finite-DAG acyclicity boundary, the relation-totality assumption, and the direction of every set inclusion. The load-bearing implication is:

```text
root-good AND every local-relation-good
=> true full assignment is globally feasible
=> every registered output projection contains the truth.
```

The probability statement then uses only Boole's union bound. No conditional or marginal independence is needed.

### Sequential/statistical validity

The executor treats `alpha` and `beta_v` as externally warranted failure budgets, not as estimates created by the composition code. The 20-atom and 200-atom controls correctly demonstrate that multiplying marginal success probabilities would be unjustified: the union-bound lower bound is attained while the independence product differs.

### Dependence / numerical-analysis review

The shared-ancestor hostile is the essential precision test. Global feasible assignments preserve `a=b`; node-local Cartesian propagation deliberately forgets that dependence. This is the same dependency phenomenon that motivates joint/set representations in interval and reachability analysis. Moore, Kearfott & Cloud, *Introduction to Interval Analysis* (SIAM, 2009, DOI `10.1137/1.9780898717716`) explicitly formulate range computation as the image of a set under a map; Althoff, Frehse & Girard, *Set Propagation Techniques for Reachability Analysis* (Annual Review of Control, Robotics, and Autonomous Systems 4, 2021, DOI `10.1146/annurev-control-071420-081941`) reviews guaranteed reachable-set overapproximation by iterative set propagation. No novelty over those parents is claimed.

### Hostile systems review

Checked graph/output locking, exact `Fraction` domains and budgets, totality of explicit relations, unknown-relation widening, cycle rejection, out-of-domain endpoints, and normal/optimized deterministic replay.

## Independent exhaustive census

`test_uncertainty_composition_exhaustive_v1.py` adds an independently authored finite oracle for UC-3.

It exhausts:

```text
4 deterministic Boolean maps x -> a
x 4 deterministic Boolean maps x -> b
x 16 deterministic Boolean maps (a,b) -> y
x 3 nonempty root-confidence subsets of {0,1}
= 768 complete DAG cases.
```

For every case and every node it requires

```text
global feasible projection subseteq local Cartesian propagated set.
```

A second oracle independently brute-forces the frozen shared-ancestor assignments and requires the exact joint constraint `a=b`, hence exact global `y={0}`.

This census is P2 calibration of UC-3, not a replacement for the P1 proof.

## Multi-output boundary

The executor exposes full feasible assignments, so arbitrary finite output projections are reconstructible exactly even though the convenience method `global_set(node)` is node-marginal. V1 does not claim a scalable multi-output inference API. Any downstream use that discards the full assignments and keeps only node marginals inherits the UC-3 over-enclosure boundary.

## Strongest remaining limitations

- exact global enumeration can be exponential;
- cyclic/fixed-point uncertainty is outside scope;
- continuous nonlinear range computation is outside scope except the affine parent regression;
- relation validity/failure budgets are premises rather than learned/calibrated by this capsule;
- losing dependence can destroy identifiability while remaining coverage-sound;
- this does not calibrate the separate #602 capability-prediction uncertainty row.

## Audit disposition

No theorem-breaking defect was found. The independent strengthening is the 768-case UC-3 census. Merge is authorized only if dedicated CI passes the original freeze-custody check, the complete normal and `python -O` suites, and byte-identical receipt reproduction.
