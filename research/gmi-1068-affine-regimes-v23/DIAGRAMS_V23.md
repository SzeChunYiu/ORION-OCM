# V23 — complete diagrams and independent interval certificates

## W3.1 — roots and cell constancy over an ordered field

Coefficients and interval endpoints lie in Q (the mathematics also holds in R).
The active roster D is finite; lo<=hi. For each distinct active pair write
f_i(t)-f_j(t)=alpha+beta*t. If beta=0, all points tie when alpha=0 and none do otherwise.
If beta is nonzero, division gives the unique root c=-alpha/beta. Substitution
proves equality; subtracting two putative equalities and cancelling the nonzero
factor proves uniqueness. The difference equals beta*(t-c).

Let B be sorted distinct lo,hi and all such roots in [lo,hi]. Every parameter is
a boundary or in an adjacent open cell: for a nonboundary point take the last
boundary below and first above, which exist in the finite list containing endpoints.
No pair root lies inside a cell (a,b). Each difference is identically zero, a nonzero
constant, or beta*(t-c) with c<=a or c>=b. The last factor has constant strict sign
inside. Every pairwise order/equality, and hence Win(t), is constant on the cell.
The midpoint (a+b)/2 is strictly inside because 2>0 and a<b.
Store all winner IDs there and separately at every boundary. For lo=hi only the
single boundary exists; for empty D all recorded winner sets are empty.

There are at most n*(n-1)/2 pair roots before deduplication, n the active-ID count.
Some crossings involve only nonwinning lines: this subdivision can refine the
minimal lower-envelope diagram. Boundary count is not a count of winner changes.
The bound concerns explicit rosters, not graphs implicitly encoding many paths.

## W3.2 — exact possible/universal winner summaries

Every parameter lies in a boundary or cell whose record equals its winners.
Thus union of recorded sets equals union_t Win(t), and their intersection equals
intersection_t Win(t). There is at least one sample even for lo=hi; no empty-index
intersection convention is involved. W2.2 identifies the intersection with
Win(lo) intersection Win(hi).

If D is finite nonempty and the union is {i}, finite-minimum existence ensures
each Win(t) is nonempty. Each is contained in {i}, hence each equals {i}.
Conversely Win(t)={i} everywhere makes the union {i}. No probability model enters.
Do not drop the existence premise for a generic infinite family whose infimum
can be unattained. A universal weak winner need not be unique.

## W3.3 — independent half-line feasibility

For active i its winning set is the intersection of [lo,hi] and all constraints
A_ij*t<=B_ij, where A_ij=b_i-b_j and B_ij=a_j-a_i.
Initialize [L,U]=[lo,hi] and process competitors in any order.
For A=0,B<0 return empty; for A=0,B>=0 change nothing.
For A>0 intersect with t<=B/A, replacing U by min(U,B/A).
For A<0 intersect with t>=B/A, replacing L by max(L,B/A).
These cases follow by ordered-field division, including its sign reversal.
After each step the maintained closed interval or empty marker is exactly the
initial interval intersected with all processed constraints. The invariant holds
initially and each update preserves it, so the final set is {t:i in Win(t)}.
Return empty exactly when L>U; retain L=U as a genuine point. Inactive i has empty
winning set regardless of inequalities: comparison does not replace admission.

Possible i have nonempty intervals; universal i have interval [lo,hi]. This computes
entire sets, not a grid. Its parent is one-dimensional polyhedral feasibility.
It need not reuse production roots, score helpers or argmin. Coefficients remain
common input, not a supplied answer.

## W3.4 — whole-diagram validation and all-pair refinement

Validate input and independently recover every candidate interval. Require sorted
distinct boundaries beginning at lo and ending at hi, one record per boundary,
and exactly one cell between each adjacent pair. This certifies complete coverage.
Check each boundary winner set using closed membership in the oracle intervals.

For a nonempty cell (a,b) and candidate interval [L,U], require either L<=a and
b<=U (wins throughout), or U<=a or b<=L (wins nowhere inside). Any other case is
partial overlap, invalidating the claimed constant status. This equivalence uses
a<b and Q/R density: an interval endpoint strictly inside the cell creates a
change, and each positive-length intersection has interior points. Empty oracle
intervals contribute no IDs. Compare the full resulting sets with cell labels,
and require each claimed sample strictly inside. Sample agreement alone is weaker.

Correct winners need not retain a nonwinning crossing. For the promised ALL-pair
refinement, also require each interior boundary to have an active nonparallel
equality witness; independently check every such pair has no root strictly inside
any open cell. Use its exact c=-alpha/beta, without importing production helpers.
Endpoints need no equality witness. With coverage, these checks prove all and only
required interior roots are present. Simultaneous roots give one boundary; a missing
nonwinning root cannot pass by leaving the lower envelope unchanged.

## Proof levels

Root existence, density, sorted enumeration and interval-algorithm invariants above
are paper proofs, with exact Fraction calibration separate. The V12 ordered-ring
instance alone does not mechanize field completeness. Kernel registrations cover
only their explicit types/constructors; FORMAL_SCOPE_V23.md identifies them.
CGAL owns the mature representation, not a claim this all-pair method implements
its optimized divide-and-conquer algorithm.
