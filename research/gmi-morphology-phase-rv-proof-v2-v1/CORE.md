# Morphology Phase R/V Boundary Theorem V2 (proof strengthening): read first

Revival ticket **REV-L45-073-PROOF-STRENGTHENING** (GMI #833). Target: legacy
claim object 073 (`GMI833_V2_LEGACY_073_MORPHOLOGY_PHASE_RV_THEO`), the corpus's
single weakest-support caveat (L45 borderline caveat, VERDICT_REGISTER_V1.json).

## Diagnosis (why support was below stated strength)

The claim statement covers four components: (1) R/V-parameterized burden,
(2) 2-morphology phase condition, (3) corner regimes / phase-boundary
structure (Theorem 2 + Corollaries 1-4), (4) held-out prediction protocol.
The V1 support delivered only:

- Theorem 1: a one-line definitional rearrangement (true but vacuous at
  theorem strength).
- Theorem 2 + Corollaries 1-4: NO proofs at all; an 8x8 sweep witness + 23
  unittests stood in for the argument (computation-as-proof).
- Two asserted statements are moreover false as printed: the phase boundary
  is NOT piecewise-linear in R (it is piecewise reciprocal-affine, and the
  hinge kernel has up to 3 segments, not 2), and Corollary 2's R*(V) formula
  carries a sign error plus unstated activation-regime conditions.
- The witness implements a different burden model than the V1 doc's boxed
  definition (divisor resource kernel, no hinge, no alpha_r, plus an
  unregistered complexity-penalty x V term).

## What this package delivers

| file | what |
|---|---|
| [MORPHOLOGY_PHASE_RV_BOUNDARY_THEOREM_V2.md](MORPHOLOGY_PHASE_RV_BOUNDARY_THEOREM_V2.md) | full-rigor proofs at the claim's stated scope: kernel-regularity lemmas, boundary structure theorem (corrected), R/V-axis monotonicity + crossing uniqueness with corrected closed forms, three-morphology lower-envelope theorem with sandwich criterion, honest held-out proposition |
| [phase_rv_boundary_route2.py](phase_rv_boundary_route2.py) | independent route 2: closed-form boundary predicates only (no argmin enumeration); covers both kernels and both V1 models |
| [test_phase_rv_proof_v2.py](test_phase_rv_proof_v2.py) | unittest controls: structural properties on fixed-seed random parameter draws + exact two-route agreement vs the V1 witness |
| [RECEIPT_TWO_ROUTE_V1.json](RECEIPT_TWO_ROUTE_V1.json) | remote-run receipts (two hosts), commands, sha256s, counts |

Run: `python3 -I -B test_phase_rv_proof_v2.py -v`

The V1 8x8 sweep is DEMOTED to a declared control (regression pin of the
registered parameter point); it is no longer cited as proof support.

Terminal: `MORPHOLOGY_PHASE_RV_BOUNDARY_FULL_SUPPORT_AT_STATED_SCOPE`
