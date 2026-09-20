# V23 independent scientific and executable review

Reviewer authored the paper proofs and reviewed independently authored production,
oracle and tests. This is independent implementation review, not a second independent
paper authorship claim. Formal proof review is in FORMAL_REVIEW_V23.md.

## Actual code inspected

Read core_v23.py, contexts_v23.py and regimes_v23.py in full, plus immutable
V15/V20 interface use. Construction validates all coefficients and flags before
an empty/inactive result; exact Fraction values exclude int/bool/float aliases.
Actual winner_ids calls V20 attained/maximal on an actual V15 Context. It does not
replace that bridge with a same-named direct selector. Reverse score orientation,
all equivalent IDs, P/E separation and zero-width/empty cases are consistent.

Encoded validates a generic code/context/decoder structure. Only at(family,t)
binds it to that particular affine family and parameter. The independent codec
check tests that stronger relationship against original input rows. A uniformly
shifted decoder can remain structurally valid yet fails that family-specific check;
this distinction is intentional, not an unchecked assertion of the constructor.

Root generation uses active nonparallel pairs, exact division, inclusive endpoints,
and deduplicated sorted boundaries. Every boundary and adjacent midpoint retains
all winner IDs. Possible is union; universal is intersection. The finite nonempty
case makes singleton possible union the correct robust-unique criterion.
No production defect was found in the reviewed scope.

## Independent oracle and registered tests inspected

Read oracle_v23.py and all diagram/context/control/hostile/custody/coverage tests.
The oracle independently intersects signed weak half-lines, including contradictory
zero slopes and singleton intervals. It imports no production scoring/root/argmin.
It verifies entire open-cell coverage by each feasible interval, boundary membership,
all boundary/cell adjacency, and pairwise endpoint-sign products to reject concealed
nonwinning roots. Spurious interior boundaries require real equality witnesses.
These checks are stronger than agreement at finitely many chosen sample points.

Primary loops enumerate the actual 820 rosters/4920 intervals and1333 P/E families/
7998 intervals; actual loop counters cover decoded observations and every pair order.
They do not simply assert the planning counts. Historical helper comparisons call
actual imported functions and preserve their valid-input/empty-case contracts.
The original scalar fixture replay projects h3/h4 identities back to one old value.
Its tie at3/2 has three winning histories and two winning contextual values.
Named controls test interior-only and isolated tied winners, duplicate-line aliases,
nonwinning crossings, wrong robustness quantifiers, nonlinear and changed-domain
boundaries, exact relabelling and shared positive-affine transformations.
Real valid diagram/codec baselines precede corruptions of their actual fields.

## Supplementary larger seeded review — observed

Ran /tmp/gmi-v23-independent-probe.py on billy-laptop with Python3.12, normal and -O.
Both completed PASS and emitted identical output bytes with SHA256
c680d69364092ea0c8973d64ff0302590e53cac50e5c449aae08a9c6a025ccbf.
Generator: Random(20260920),64 cases, n=randint(4,8); each coefficient is
Fraction(randint(-7,7),randint(1,5)); independent P/E use getrandbits(1).
Two endpoints use the same rational generator and are sorted. IDs are distinct.
This is supplemental review evidence, not an exhaustive or primary-receipt count.

Actual checks:
- 64 larger families;140 boundary records;76 open cells.
- 838 boundary memberships;456 whole-cell memberships;99 pair-cell root checks.
- 216 independent literal all-ID winner checks and216 full codec checks.
- 1294 individual decoded observations compared with literal P/E/score semantics.
- 64 common positive-affine score invariances and64 bijective-ID invariances.
- 126 actual certificate corruptions rejected;64 family-binding decoder mutations
  rejected despite retaining valid generic encoding;11 malformed inputs rejected.

The sample additionally probes every independently recovered feasible-interval
endpoint, so its literal point checks are not restricted to production-chosen samples.
The semantic oracle remains the whole-interval certificate, not this point sample.

## Driver, authority and custody review

Read check_regimes_v23.py, custody_v23.py, coverage_v23.py and their actual guards.
The driver requires the named theory/reviews, replays the exact kernel audit, loads
the seven mandatory test modules and checks exact measured counts before a receipt.
It binds every local science file and exact original title, lists explicit scope
boundaries, keeps overall_closure OPEN and scientific_truth_certified false.
Unavailable inputs use a separate CANNOT_CHECK outcome from checked-invalid data.

Custody verifies the committed freeze and ancestry, confirms only the freeze existed
at preregistration, checks every pinned input and dereferences inherited receipt
inventories. It checks current bytes, not receipt names alone. Coupled old source/
receipt edits remain blocked by the committed inherited receipt hash. Actual tests
include parent source mutations, path escape, missing source and no-alarm overlays.
Immutable V16 carry records the two qualified identities without promoting original
atoms or reusing old accounting totals as current. Fresh successor counts must be
derived from the current preserved original records; no automatic later-ledger scan.

Canonical primary normal/-O outcomes and actual typed inventory belong to
RESULT_V23.json. This review does not fabricate results for an integrated driver
that had not run at the time of these supplemental checks. No novelty, universal
nonlinear method, preferred parameter, physical phase transition or full GMI claim.

Read the actual successor CORE.md and RECONCILIATION_V23.md: only R3-008 eligible,
29/193 originals with2 qualified separately giving191 active unresolved; R0 alone
whole-round earned, R3 stale, R3-009 unresolved. Wording agrees with this evidence.
