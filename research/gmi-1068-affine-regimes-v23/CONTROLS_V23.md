# V23 — scope controls and revival paths

These are mathematical falsifiers and preregistered test targets. Observed execution
belongs to REVIEW_V23.md and RESULT_V23.json, not this list of intended checks.

## W4.1 — endpoint and midpoint shortcuts fail

A=t, B=1-t, C=2/5 on [0,1] have endpoint winners A,B, while C is uniquely best
for 2/5<t<3/5. Thus endpoint UNION misses possible winners. Revive by complete
root/cell subdivision or full half-line feasible intervals. Endpoint INTERSECTION
remains exactly the universal weak winners; the quantifiers differ.

With A=t-1/3, B=-t+1/3, C=0 on [0,1], C wins only at t=1/3, where all three tie.
Off that point one of A,B is negative. Keeping only open-cell winners drops C.
Revive by retaining full boundary records, including closed singleton intervals.

Lines A=0, B=t on [0,1] have universal weak intersection {A}, but tie at0.
So singleton universal intersection is not robust uniqueness. Revive by strict
endpoint inequalities or singleton possible-winner union with finite existence.
For A=0, B=2+t, C=2-t on [-1,1], B/C cross at0 but A alone always wins.
A pair root is not necessarily a change of frontier identities.

## W4.2 — identities, domains and codecs

Two distinct IDs with equal affine coefficients are permanent aliases, both kept
when optimal. Duplicate external IDs instead destroy the one-to-one coding contract
and are rejected. Do not repair ties by imposing an arbitrary label order.

An undefined or inadmissible low-scoring candidate is not a winner. E and P must
remain separate even when public observation of an ambient defined value is illegal.
Changing admission only at an interior point can create a winner invisible at both
endpoints. This violates the fixed-family premise; its repair is a separately
registered piecewise domain with new boundaries, not rejection of W2.

A code can have score0 at t=0 and score1 at t=1 while retaining its identity.
Its decoding makes these different contextual values explicit. Comparing bare codes
as scalar values loses this distinction. Likewise injective decoding alone does not
ensure order reflection; the actual declared score preorder must be checked.

## W4.3 — arithmetic and structural boundaries

A nonlinear competitor (t-1/2)^2-1/8 is positive at endpoints0,1 and negative at1/2.
Against score0, endpoint domination fails inside. Revive by a suitable nonlinear
root/sign method and fresh hypotheses; affine completeness makes no such claim.
Over Int, lines0 and2*t-1 reverse order between0 and1 but have no integral root.
The direct endpoint theorem survives; integer root subdivision does not recover
the rational diagram. Use an actual ordered field for W3, not a named field axiom.

Zero-width intervals have one boundary and no open cells. Empty active sets have
no winners; they are valid new diagrams. Validate malformed unused coefficients
and flags before returning this empty answer. No input error is converted to emptiness.
No probability prior, thermodynamic limit or statistical significance is present.

For every fixed c>0 and affine g, transformed scores c*f_i(t)+g(t) preserve all
pair comparisons and winners by cancelling g and dividing by positive c (or order
cancellation). ID relabelling preserves results via the bijection. Candidate-specific
shifts need not preserve anything: adding2 only to the initially better score0
makes it worse than score1. These are clean invariance and falsification controls.

## W4.4 — actual historical behavior and test authority

The old affine API sorts ALL tied IDs. Its phase_cells returns open cells only;
critical_samples adds boundaries, and possible_winners takes their sample union.
uncertainty_terminal calls a singleton union ROBUST_UNIQUE. None is an expectation,
minimax selector, or a theorem for parameter-dependent availability.
On nonempty valid fully-active inputs compare these actual functions and the old
endpoint_strict_dominance result. Preserve exceptions for empty affine_argmin and
its callers. A degenerate empty phase_cells may return no cells without calling
argmin; that historical behavior is not a new scientific defect.

Primary calibration consists of the separate frozen 4920 roster/interval and7998
context/interval strata. They overlap; no summed distinct-model claim is permitted.
The larger 64-case seeded review sample is supplementary. Only executed loops earn
coverage counts; normal/-O equality and source-valid proof mutations are distinct
checks from hash custody. Source-unavailable outcomes are not scientific passes.
