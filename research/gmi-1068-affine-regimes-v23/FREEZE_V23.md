# V23 preregistration: actual affine context regimes

Control plane #1068; historical programme #833.
Parent: 9d5254cd621f83266ef7be5565c9bb55f1bd7e68 (V22, #1118).
This freeze precedes all V23 implementation, experiments and outcome files.
Coverage counts below are planning algebra, not observations.

## W1 — actual contexts, decoding and all winner identities

Fix candidate identities I, admission P, evaluator domain E and coefficients
a_i,b_i. Active means P AND E; score_t(i)=a_i+b_i*t.
Construct actual V15 Context with defined domain E and value (i,score_t(i))
in common I times scalar. The fixed preorder reverses scalar cost order
and ignores identity. Bind actual observation tags and evaluator fields.
Use actual V20 attained image and full maximal set: its identity projection
equals every active minimizing identity, retaining all ties and aliases.
For infinite I do not assert a winner exists; for a complete finite roster
derive finite existence when the active roster is nonempty.

Construct a coded V15 Context with value code i and order induced by score_t.
Define dec_t(i)=(i,score_t(i)); prove injectivity, order reflection, actual
V17 postcomposition equality and decoded attained/maximal image equality.
Python codes are indices of unique external labels with explicit decoder.
A code may decode to different scalar values at different parameters.
Cross-context winner comparison uses fixed IDs; numeric comparison uses
the common decoded space. Preserve illegal/undefined tags and E-true/P-false
ambient evaluation. Neither an implicit quotient nor a tie breaker is allowed.

## W2 — whole-interval endpoint laws under primitive ordered-ring laws

Reuse actual V12 Scalar primitive ordered commutative ring and Int instance.
Derive affine difference and slope-sign monotonicity/antitonicity.
For lo<=hi and every t in the closed interval, weak pairwise endpoint
dominance implies weak dominance throughout; strict at both endpoints
implies strict throughout. Necessity follows because endpoints belong.
This direct whole-interval proof needs no division or density:
a nonnegative difference slope compares to lo, otherwise compare to hi.
Derive universal weak winners = intersection of endpoint winner-ID sets.
Derive the same unique winner everywhere iff it strictly beats every OTHER
active identity at both endpoints. Singleton weak intersection is insufficient.
Bind active membership and empty/singleton/zero-width cases explicitly.

Also prove actual affine endpoint-interpolation identity and dominance
for (1-s)*lo+s*hi when0<=s<=1. Do not infer normalized interpolation
covers every ordered-ring interval; Int lo0,hi2,t1 is a counterexample.
Optional strengthening within this freeze: from an explicit checked affine
equality at c derive difference factorization slope*(t-c) and order behavior
on either side. Do not assume root existence or sign constancy as an axiom.

## W3 — exact rational diagram and independent interval certificates

For finite active affine roster over Q and lo<=hi, construct sorted distinct
boundaries: endpoints plus every nonparallel active-pair equality root in range.
Parallel unequal lines have no root; identical lines tie everywhere.
At each boundary retain ALL argmin IDs. At every adjacent nonempty open cell
retain its midpoint and full winner-ID set. Empty active roster is valid.
Paper prove pairwise order is constant in a root-free open cell; winner IDs
are constant there. Numeric values themselves generally still vary.
The boundary/cell sample union equals all possible winners in the interval;
the intersection equals universal weak winners and endpoint intersection.
For a finite nonempty active roster, singleton possible-winner union implies
one unique winner throughout. No probability distribution on parameters is used.
All-pair roots may refine the true envelope: a crossing need not change winners.
The pair-root count is bounded by n*(n-1)/2 in explicit roster size,
not in the size of a compact graph that may encode many paths.

General rational root existence, ordering and sample completeness have explicit
paper proofs and exact Fraction evidence. V12 ordered rings alone cannot
supply them; the actual Int instance does not prove a rational/real field model.
No new field interface may assume the desired root/envelope theorem.

Independently solve each active candidate's entire weak-winning interval:
intersect lo<=t<=hi with (b_i-b_j)*t<=a_j-a_i for every active j.
Zero slope either imposes no constraint or makes the interval empty;
positive slope supplies an upper bound, negative slope a lower bound.
Retain closed singleton intervals. Prove the update invariant on paper.
The oracle must not import production scores, roots, samples or argmin.
Verify full diagram coverage and each open cell's WHOLE membership:
every candidate's feasible interval contains the whole open cell or is
disjoint from it; partial overlap fails even if the midpoint label agrees.
For the promised all-pair refinement, every interior boundary needs an
active nonparallel equality witness and no open cell may conceal a pair root.

## Eligible unchanged original requirement and historical parents

Only GMI2-R3-008, "derive phase/frontier change", may close at its declared
FORMAL_OR_FINITE scope. This is an actual affine context-family regime
derivation, not a theorem for every nonlinear family or a physical transition.
Preserve every other original field, including V22's R3-007 and earlier atoms.
R3-009 still requires exact full legacy transports; whole R3 remains stale.
If this one original scope earns closure:29 fulfilled/193 unresolved;
two unchanged qualified replacements separately leave191 active unresolved.

Import the original R3 actual scalar_winner fixture and preserve the switch
and tie at lambda=3/2. Preserve its value-image versus history distinction.
On valid nonempty fully-active inputs compare the actual old affine_argmin,
pairwise_crossings,phase_cells,critical_samples,possible_winners,
uncertainty_terminal and endpoint_strict_dominance functions.
Old phase_cells deliberately omits boundary records; compare them separately.
Old empty affine roster behavior differs from the new valid-empty diagram;
document and test the contracts rather than silently redefining the parent.
This partial parent comparison does not retire every legacy foundation symbol.

## Independent finite calibration and hostile controls

A: nine line types (a,b) in{-1,0,1} squared, ordered rosters size0..3
with distinct positional IDs and repeated lines allowed:820 rosters.
All six closed intervals with endpoints in{-1,0,1},lo<=hi:4920 cases.
B: sizes0..2 with independent four(P,E) flag pairs per line:1333 context
families,7998 interval cases. These strata overlap; do not sum as distinct models.
Measure boundaries, cells, whole-cell comparisons, decoded observations,
target IDs, empty families and all legacy helper comparisons in actual loops.
Check relabelling and shared positive affine score transformations on declared
named controls. No coefficient grid is promoted to arbitrary exact arithmetic.
Add fractional controls and a separately identified larger seeded review sample.

Controls: endpoint union misses an interior winner; open-cell-only misses
an isolated tied winner at1/3; lines0,t tie at0 despite singleton universal
weak intersection. Duplicate IDs are invalid but distinct IDs/equal lines valid.
Cover parallel/identical/simultaneous/nonwinning roots, no active candidates,
inactive or undefined low score, equal endpoints and parameter-dependent codecs.
Changing P/E invalidates fixed-domain conclusions; nonlinear interior dips
invalidate affine endpoint export. Restore or explicitly enrich the context
family rather than relabeling these as violations of the conditioned theorem.
An Int pair can reverse without an integral equality root: no false field claim.
Missing roots/cells, wrong inequality sign, dropped ties and misplaced roots
must fail independent full-interval certification, including nonwinning roots.

Strict new inputs reject floats/bools as exact rationals, duplicate labels,
malformed flags/dimensions, reversed intervals, and invalid unused coefficients.
Validate complete input before empty or inactive early returns.
Valid empty diagrams, invalid input and unavailable sources remain distinct.

## Proof and publication discipline

Pinned Lean4.19.0, isolated SOURCE plus exact typed AUDIT and axiom scan.
Bind actual constructors, scalar operations, codecs and maximal/winner predicates.
Source-valid mutations compile SOURCE then fail exact AUDIT: all sources empty,
endpoint theorem leaf, decoder/maximal bridge leaf and universal-winner leaf.
Independent normal/-O receipts must match bytes. Exact measured coverage guards,
real no-alarm, custody/missing-source/path-escape, coupled scope and top-level
metadata mutations are required. Preserve strict V22 successor provenance guards.
Every science/review file is receipt-bound. Publish/merge only after exact-head CI.
Modular files<=200lines; raw receipts may exceed. No novelty or complete GMI claim.

## Primary assimilation

CGAL official 2D Envelopes manual, Introduction/Envelope Diagram/exact-rational
labelled example: https://doc.cgal.org/latest/Envelope_2/index.html
Use all inducing IDs at vertices/overlap cells. Our all-pair refinement is not
CGAL's optimized divide-and-conquer algorithm and imports no speed claim.
Boyd/Vandenberghe, Convex Optimization §§2.2.1/2.2.4/2.3.1:
https://stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
Winning intervals are one-dimensional intersections of weak affine halfspaces.
The old affine schema owns the sample parent; V12/V15/V17/V20 own reused laws.
Restricted-slope parametric shortest-path bounds do not apply to arbitrary
explicit affine rosters or prove compact-graph envelope efficiency.

## Immutable input SHA256 bindings
- `research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json` `4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574`
- `research/gmi-1068-r3-contextual-attainability-v1/FREEZE_V1.md` `e9f25acb58dc24f2bda8ae6dfeab4e78660f3e1ffc664638b74b76d7f5557209`
- `research/gmi-1068-r3-contextual-attainability-v1/THEORY_V1.md` `6298fda4b6a2f4feb63c98f103c69ffea2602ec86e58fbbfb7dcad06c4aa8c9a`
- `research/gmi-1068-r3-contextual-attainability-v1/check_r3.py` `7862cbb10877bb80a21182b53fac6253e8707fcf76620552fbe5e9a0d4effcd4`
- `research/gmi-833-morphology-selection-schema-v1/morphology_selection_schema_v1.py` `7d664a5d0f3fa0ea8a2e0b6692597825c05143404cd7101cf1f47615e789571e`
- `research/gmi-833-morphology-selection-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md` `9a2b180819885107d01cc571ad673f6767e6f3eec3c1fe01d859b8d0a312f2b7`
- `research/gmi-1068-partial-context-v15/PartialContextV15.lean` `332dcfb63304d5668800ea21f09795c2d92267989291ffe35d9e38ea2db0edf5`
- `research/gmi-1068-partial-context-v15/context_v15.py` `75c62203c8ae61ddce1081f9deaf463dfce6965bb160086a8e21adfe787fcd2f`
- `research/gmi-1068-context-specializations-v17/ContextMapsV17.lean` `90d7a5a77e4ed59569276d4e38a41602292df91a096229eb62cd55e0c4b58730`
- `research/gmi-1068-scalarization-v12/ScalarLawsV12.lean` `fc6a14981c710647135e2354616db6170fa7c5e483c61ca3a0e9f58de8887f1e`
- `research/gmi-1068-scalarization-v12/FiniteSumsV12.lean` `efaad21772778c70ab2bfea3aedcf26841f9895da104111ba299e9edd7117638`
- `research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean` `ec4a10f31365a2e304dd12b599e7c0ac83e3996c31e3a6b6f7307252e8d24bf4`
- `research/gmi-1068-frontier-simulation-v20/GuardedMapsV20.lean` `343d1cdd1897b854c57d6885cdaf46daca70dd405a4248485780d63c3fabf176`
- `research/gmi-1068-frontier-simulation-v20/PartialPostcontextV20.lean` `909ed050209b15d797138a30231eca9b12393618052c73607788725a9bc7e8f8`
- `research/gmi-1068-frontier-simulation-v20/core_v20.py` `3f1cc388ddf559b5ae7eb45ff6f20e27affbf7ba4285fb9287039e02c35d3ac3`
- `research/gmi-1068-permission-barriers-v22/RESULT_V22.json` `d4d5fe7489c978f9c001365271107fefc3ac2d2df82aeb135becff7b30e89b5f`
- `research/gmi-1068-recursive-audit-v22/SCOPE_SNAPSHOT_V22.json` `289a91f8485dcc8e754f45afe9ed26791a17ba93c4ebe26194bcdbcedf8a039c`
- `research/gmi-1068-recursive-audit-v22/CURRENT_ACCOUNTING_V22.json` `934665d4d5f0ca0b44bc1c4a41f67db87eabe48aeaff84e3787ec072c0a9129c`
- `research/gmi-1068-corrected-targets-v16/RESULT_V16.json` `18bea5c6f85b4fcc91c40c53cbf63df59c38d70e9e839efc4585f6640497ad1a`
- `research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json` `e1cc2d2dbc10171407577889f75ac531c30cf09eab224fc3823f3931c5048618`
- `research/gmi-1068-amendment-governance-v16/RESULT_V16.json` `ed491fab2cd0b69fb4ee845b82e349c79ff0d70f0dbc1d312ee0755645437de4`
