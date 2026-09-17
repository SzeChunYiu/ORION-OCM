# FREEZE_L46_TWO_ROUTE_V1 — per-package route-2 declarations

**Programme pre-registration:** PROGRAMME_V1.md (commit a27f61dbe on this
branch, before any route-2 code or execution) froze the ranking, the
conversion template, the independence criteria (#932/D-X3: >=2 differing
axes, no re-encoding), the acceptance gate G1–G5, and the effort model.
This file consolidates the per-package declarations. Timeline honesty: the
per-package difference tables were authored inside each
`independent_oracle_v1.py` header BEFORE that package's remote run; those
files and their receipts were committed together per checkpoint, so the
in-repo pre-registration authority for the *rules* is the programme freeze
above, not per-package commit order.

## Declarations (items 1–8)

| # | package | route-1 class | route-2 class (axes: representation / exploration / completeness / cost) | agreement rule |
|---|---------|---------------|--------------------------------------------------------------------------|----------------|
| 1 | gmi-formal-proof-audit-v1 | exhaustive grid sweeps, lambda point-evaluation, trace listing, closure-file validation | division-algorithm chains, kernel-partition refinement, product-form zero-factor, symmetry reduction, Floyd cycle detection, arithmetic corpus bijection | exact, fail-closed, 16 rows |
| 2 | gmi-developmental-uncertainty-transport-v1 | stateful campaign API, forward pair comprehension, running accumulators, 4-corner enumeration | inverse-relation backward scan w/ double inclusion, telescoping boundary collapse, LCM + worst-case probability-space witness, sign-directed endpoint selection, Minkowski decomposition, purity test | exact, fail-closed, 57 rows |
| 3 | gmi-capability-ceilings-v1 | candidate-space exhaustive search (2M cap), log formulas, Gaussian rank | pigeonhole injectivity + constructive witnesses, partition-lattice refinement, falling factorials, doubling search, gap-cell counting, minor-enumeration rank w/ exact determinants, recurrence + walk horizon, Pascal-recurrence binomials | exact, fail-closed, 81 rows |
| 4 | gmi-analog-semantics-closure-v1 | 162-case product enumeration of twin encoders, float expm1 | multi-affine vertex identity + non-vertex extension, algebraic interval validity, exponent arithmetic, rational series w/ sandwiched ceiling (no floats) | exact, fail-closed, 9 rows |
| 5 | gmi-uncertainty-composition-v1 | forward pair comprehension, pair-join, tuple enumeration | boolean incidence-matrix algebra (associativity identity), bitmask universe, LCM + nested witness, min==max characterization, explicit hostile spaces | exact, fail-closed, 39 rows |
| 6 | gmi-dependency-aware-uncertainty-composition-v1 | DagCampaign state machine, forward tuple flow, tuple enumeration | full-assignment CSP model enumeration, topological DP w/ hash-join, bitmask registered family, inclusion-exclusion masses, Kahn cycle detection | exact, fail-closed, 41 rows |
| 7 | gmi-structural-threshold-repair-v1 | source->opcode walker w/ linear count, flat grid loops, partial wrapper | opcode category-partition accounting, GF(2) + indicator identity, configuration search under contract prices, sign-change counting, midpoint convexity exclusion, cutpoint sweep, degree-sum-class arithmetic, 5^3-1 counting | exact, fail-closed, 50 rows (1 finding expected-then-observed) |
| 8 | gmi-learning-law-selection-v1 | 128-set enumeration, per-set subset checks, two-vector generic probe | inclusion-exclusion (two independent counts of 36), binary-uniqueness family theorem for tie-freeness, arity-partition tie analysis, adversarial price constructions, projection-hiding witness | exact, fail-closed, 23 rows |

## Gate outcomes (G1–G5 per PROGRAMME_V1.md section 3)

All 8 packages: G1 AST import audit clean (stdlib only), G2 difference
tables >=2 axes (recorded per receipt), G3 per-claim rows over the
committed receipts, G4 negative control (corrupted committed value must be
detected), G5 source_sha256 over both routes + crosscheck + claim spec +
committed receipt, run on billy-laptop (Linux, CPython 3.8.10, `-I -B`),
receipts sha256-verified on both hosts.

## Findings (disagreements registered, none adjudicated away)

- **L46-F1 (gmi-structural-threshold-repair-v1):** the ABSOLUTE BASE6
  opcode price (6) does not reproduce under route-2 raw counting on CPython
  3.8 (count 7); all base-RELATIVE prices, every other opcode total
  (39/18/17/4), and all analytic quantities agree exactly. Attribution:
  interpreter-version sensitivity of a committed absolute constant
  (route-1's own `compiled()` requires dis features absent on 3.8, so the
  price pins an interpreter >=3.11 that CI uses). Disposition: package
  verdict TWO_ROUTE_WITH_FINDINGS; follow-up (tranche 2): pin the
  interpreter in the package ops doc or restate BASE6 as a relative anchor.

## Execution custody

All route-2 executions ran on `billy-laptop` (`~/l46/...`), rsync'd from
and scp'd back to the authoring worktree with sha256 verification both
sides. Nothing executed on the authoring Mac.
