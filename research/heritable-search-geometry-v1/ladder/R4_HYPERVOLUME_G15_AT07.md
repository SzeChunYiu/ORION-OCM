# R4 — G15 / A_T07: hypervolume geometry under named archive metrics; capacity caveat

Rows: G15 (archive/ratchet), A_T07 (T07 elitist ratchet monotonicity, PROVED at R0 under
a frozen total order + immutable archive + unlimited capacity). Rung R4 question: under
which archive metrics is hypervolume monotone; the HST capacity caveat is load-bearing.

## Verdict (first sentence)

PARENT_SUFFICIENT for the unlimited-capacity reading — the hypervolume indicator
literature (Zitzler–Thiele 1999, IEEE TEC 3(4), the "size of the space covered" S-metric;
verified against the primary paper) together with measure monotonicity owns the statement
"HV(A ∪ {x}) ≥ HV(A) for every finite archive A and point x, under the dominance-induced
Lebesgue volume for a fixed reference point" — and LIFT_FAILS for the capacity-removed
pass: with any capacity bound and any eviction rule, HV can strictly decrease (hostile H4,
`hostiles/witnesses/hostile_hypervolume_capacity.json`).

## Exact owned statement (parent, verified)

For objectives to be maximized, reference point r, HV(A) = λ(∪_{a∈A} [r, a] ∩ objective
box) with λ Lebesgue measure. Monotonicity under inclusion is measure-monotonicity of the
union (elementary, owned by measure theory; Z–T 1999 own the indicator's definition and
its Pareto-compliance). Monotonicity in the FROZEN TOTAL ORDER (T07's actual ratchet) is
running-max monotonicity — a different functional; see R5 file for the orbit reading.

## Capacity hostile (H4)

2-D objectives (f1, f2) maximized, reference (0,0). Archive capacity 1 (the smallest
binding capacity). A_t = {(2,2)}: HV = 4. Arriving point x = (3, 1/2): Pareto-incomparable
with (2,2); an eviction rule that keeps x (frozen-scalarization w = (2,1):
score(2,2) = 6, score(3,1/2) = 13/2 — keeps x)
yields A_{t+1} = {(3,1/2)}: HV = 3/2 < 4. The ratchet in the ORDER holds (13/2 > 6);
the hypervolume FALLS. Exact-Fraction arithmetic in the witness. This is the HST
"Pareto variant must state capacity effects" caveat made minimal and machine-checked.

## Which archive metrics keep HV monotone (the named condition)

LIFT_CONDITIONAL: HV is monotone along an archive trajectory iff the eviction rule never
removes a point whose exclusive hypervolume contribution is positive at removal time
(i.e. the archive is inclusion-nested in the HV-relevant sense). OCM-checkable: track
exclusive contributions at each eviction; the witness computes them exactly. Under
capacity < Pareto-front width, no score-based eviction satisfies this for all arrivals
(H4 is a one-arrival refutation of the greedy-scalarization eviction).

## Assumption passes (A3)

- Remove ix-elitism: non-elitist archives drop HV trivially (even without capacity) —
  strictly worse; verdict FAILS a fortiori.
- Remove x-unlimited-capacity: hostile H4 (this is the pass that breaks HV monotonicity).

## Residual claimed by HSG

H4 itself and the exclusive-contribution condition; everything else is parent-owned.
