# AB4 — positive weights reverse an incomparable pair

Let x=(1,0), y=(0,1), w=(2,1), z=(1,2).
Under coordinate order, x≤y would require 1≤0 in the first coordinate.
Likewise y≤x would require 1≤0 in the second. Hence x and y are incomparable.
Every coordinate of both w and z is strictly positive.

The actual finite sum gives w·x=2, w·y=1, z·x=1 and z·y=2.
Thus w strictly prefers x to y, while z strictly prefers y to x.
On these Nat profiles, the original score21 and score12 definitions evaluate to
exactly the same four numbers. Embedding Nat into Int preserves these equalities
and strict comparisons, so actual V12 Int dot products bind the old witnesses.

This completes premises absent from the old scalar theorem's literal type:
actual profiles, coordinate incomparability, every positive weight, and the
connection between its arithmetic expressions and the general finite sum.

## Positive converse and necessary assumptions

For finite vectors a≤b coordinatewise and nonnegative weights q,
each q_i a_i≤q_i b_i. Addition preserves order, so q·a≤q·b.
If b improves strictly in one coordinate and every q_i>0, that term improves
strictly and the others do not decrease, giving q·a<q·b.
These are classical finite scalarization laws; the actual V12 generic interface
and Int instance provide the inherited mechanism.

A zero weight can erase a strict improvement:
a=(0,0), b=(1,0), q=(0,1) gives both scores zero.
A negative weight can reverse dominance:
the same a,b with q=(-1,1) gives q·a=0>−1=q·b.
Equal profiles have equal sums under every fixed weight and cannot supply
a strict reversal. These controls prevent deletion of the required premises.

Normalization is not required for the original (2,1)/(1,2) witness.
Dividing either vector by its positive sum would preserve its ranking, but no
probability distribution or preferred prior is inferred.

## Scope and parent ownership

Boyd's primary Lecture 7 describes positive scalarization and varying its weights
to select different Pareto tradeoffs. Our coordinate order points toward larger
utility; minimization-oriented parent statements are dualized accordingly.
No convexity is needed for this two-profile arithmetic witness.
No claim that every Pareto point is selectable by a linear scalarization is made.

Actual V12 supplies stronger general ordered-ring scalarization theorems.
This round binds the old finite Nat witness to the existing Int mechanism.
It does not require a new general Real kernel instance and does not claim one.

The Python adapter accepts exact Fraction tuples and calls unchanged V12 dot and
domination functions. Its frozen calibration has four binary profiles, sixteen
ordered profile pairs and two positive weight vectors: thirty-two comparisons.
Those are finite correspondence checks, not a proof of the generic ordered-ring
theorems. The latter retain their explicit formal interface and prior authority.

Original R2-007 remains UNKNOWN. In particular this witness cannot establish
that every evaluator has a fixed linear-weight representation.
