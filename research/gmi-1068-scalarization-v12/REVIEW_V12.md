# Independent scientific/API review V12

Verdict: CLEAR for the inspected mathematical statements, Python API and
independent calibration design. This is not a completed kernel, driver,
receipt, snapshot or CI review: those components were still being integrated.
The reviewer did not author the executable implementation or its oracle/tests.
The reviewer authored the theory/adjudication, so their mathematical reread
is disclosed as self-review rather than an additional independent proof audit.

## Reviewed source identity

Freeze: 3d5e7b524c05081ba28548b3d209d0c5d7e9cd18.
Package: research/gmi-1068-scalarization-v12.
The following bytes were actually inspected:

| File | SHA256 |
| --- | --- |
| scalarization_v12.py | 23f993bd30b927127939014687d9ccc739bfece26ba4c59671cb1301c1fb12bf |
| independent_oracle_v12.py | 24e79553cafa4dcdafbdd58dbce2030f0f62b32a955c543a944ad6126eea82de |
| test_scalarization_v12.py | f5bc3e35e2ec876fcd7b9571d0e7c949d66db0530cd52cc3d9eb9a1989e01313 |
| test_hostiles_v12.py | 5f979ec0d90076c714ad4d6fa5cbd439abf64d1ce51da88aa51ebcab3c55af12 |

Subsequent changes require checking which findings still apply. No historical
source, implementation, oracle or test file was changed during this review.

## Mathematical and API checks

**Assumptions.** The frozen finite-vector order/sign conventions; exact int or
Fraction entries; the primitive ordered-ring premises in THEORY_V12.
**Dependencies.** Frozen T1–T6, actual source reads and the targeted probes below.
**Falsifiers.** An accepted inexact coordinate, invalid positive witness,
incorrect domination/frontier result, or a stronger claim than its hypotheses.
**Strongest parents.** The cited Boyd–Vandenberghe scalarization results and
ordinary exact rational arithmetic; this audit introduces no new theorem.

Production validation rejects Boolean, float, complex and numeric-subclass
coordinates. It preserves exact Fraction arithmetic and validates dimensions
before pairwise comparisons. Empty vectors give zero score and equality, not
strict domination. Frontier indices preserve duplicates with equal vectors.

The registered separator excludes exactly the selected coordinate from its
absolute-difference sum. Its other entries use that coordinate's positive
gap. Every generated coordinate is positive; the sign and output orientation
match T3. Reversing weights applies the construction to each direction.

The T1/T2 calibration checks domination and strict improvement under both
positive and nonnegative families. Its strict predicate asks whether at least
one improving coordinate actually has positive weight, rather than treating
a zero-weight improvement as strict. Positive coordinates are each exercised
as separator pivots, not only the first coordinate chosen by the convenience API.

The unsupported-frontier control uses the actual points (0,3),(2,2),(3,0).
Its candidate-minus-competitor rows sum to (1,1), a positive certificate.
The general nonselection proof is in THEORY_V12; the 49 rational-weight checks
are examples and are not presented as exhausting all positive weights.
The scalar reflection control includes all three comparison outcomes,
including ties. The efficient-minimizer theorem assumes actual attainment.

## Independence and corpus meaning

**Assumptions.** The advertised finite grids and explicit measured counters.
**Dependencies.** Oracle relation/score/separator logic and the primary tests.
**Falsifiers.** Imported production logic in the oracle, checking a witness
against its own asserted value, or promotion of finite counts to universal proof.
**Strongest parents.** Independent recomputation and exact finite enumeration;
these are verification methods, not empirical intelligence comparisons.

The oracle imports no production logic. It derives order from coordinate
signs; its score accumulates integer numerator/denominator products. Its
alternative separator compensates negative differences by rational division,
whereas production uses the registered division-free construction.
Production witnesses are checked by actual positive entries and score gaps.

The primary grid has genuinely enumerated vectors, vector pairs and weight
families. Cached scalar evaluations are independently compared before use;
the pair/weight loops perform actual comparison checks rather than reporting
the Cartesian-product size without executing them. Counts of dot evaluations
and pair comparisons are separate. The full enumeration was inspected but
was NOT rerun for this review; its execution verdict belongs to the driver.

The finite-minimizer test enumerates feasible subsets, compares production
and independent frontiers, then verifies that every attained positive-weight
minimum lies in the frontier. It does not claim each frontier point is a
weighted minimum. The construction/real-valued claims still require the
separate proofs; no calibration grid establishes their universal quantifiers.

## Additional executed probes

**Assumptions.** Laptop Python3.12, deterministic seed106812; bounded review
samples supplement the frozen corpus and are not hidden in its coverage totals.
**Dependencies.** Production API and a third integer-scaling arithmetic route.
**Falsifiers.** Any failed exact equality, nonpositive separator, wrong strict
direction or mismatch in independently determined frontier indices.
**Strongest parents.** Common-denominator integer arithmetic and direct Pareto
comparison; no reference to the production/oracle dot or order helpers.

An inline laptop probe sampled 200 rational vector pairs, dimensions0–12,
numerators -20..20 and denominators1..13. Sampled score weights used
numerators -8..8 and denominators1..7. A third route scaled vector and weight
coordinates separately by denominator LCMs, evaluated an integer dot, and
scaled back. Coordinate comparisons used integer cross multiplication.
Actual successful checks were:

- 400 exact dot comparisons across 200 pairs;
- 1172 positive-coordinate separators, including both vector orientations;
- 152 incomparable-pair opposite-ranking checks;
- 200 four-point frontier checks, including duplicate vectors and the zero vector.

These probes changed no repository files and are disclosed review evidence,
not extra prospective coverage in the registered experiment receipt.
Additionally, the three hostile unittest methods and the rational-witness
method were executed on the laptop: all four passed. This did not rerun the
exhaustive primary calibration or any unavailable formal development.

## Remaining review boundary

No actionable scientific/API defect was found in the inspected bytes.
Lean was still under development; no claim is made here about its eventual
coverage, its real-number instantiation, proof registration or kernel result.
The integrated driver, missing-input classification, final receipt and
single-atom snapshot must be checked separately before closure or merge.
Only GMI2-R2-006 is eligible. The review grants no authority to R2-007,
whole R2, empirical novelty, all-family derivation or full GMI.
