# V12 freeze: general scalarization boundaries
Control plane: #1068. Historical programme: #833.
Eligible original atom: GMI2-R2-006, "prove scalarization boundaries".
Parent implementation: de0d1eb0ba1c86d70939cf024edf1cd3f5026b17 (V11,
PR#1107 pending at freeze time). Preserve its ancestry and merge successful
main before publishing this successor. No other original atom may close.
R2 and whole-theory closure remain OPEN.

## Original target and parent ownership
Original R2 freeze target6 and CONTEXT_SCHEMA R2-3 require licensed order
information under scalarization and reversed rankings of incomparable points.
They do not require a universal weighting, full Pareto-frontier recovery or
derivation of objectives from process. Those are distinct claims.

Primary parent: Boyd–Vandenberghe, Convex Optimization, sections4.7.4–4.7.5,
printed pages178–184, https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf.
Positive weighted sums yield Pareto-efficient attained minimizers; unsupported
Pareto points need not minimize any positive weighted sum. The convex partial
converse uses nonnegative nonzero weights and is not asserted here.
Classical mathematics remains parent-owned. No empirical novelty is claimed.

## General mathematical targets
Let x,y be vectors indexed by a finite set, and L_w(x)=sum_i w_i*x_i.
Work over real numbers, with the division-free arguments generalized wherever
the explicit ordered commutative ring laws suffice.

T1. x<=y coordinatewise and nonnegative w imply L_w(x)<=L_w(y).
T2. If additionally x_k<y_k and w_k>0, strict score improvement follows.
In particular strictly positive weights preserve strict Pareto domination.
T3. x<=y iff L_w(x)<=L_w(y) for every strictly positive weight vector w.
This is an entire family of comparisons, not a distinguished scalar.
T4. Every incomparable pair admits two strictly positive weight vectors
giving opposite strict rankings, by explicit constructive separators.
T5. No single totally ordered scalar can reflect the componentwise order on
a domain containing an incomparable pair. Tie cases must be included.
T6. Any attained minimizer of a strictly positive weighted sum over any
feasible set is Pareto efficient. No convexity is required for this direction.

Registered separator: d=x-y, choose k with d_k>0. Put
S=sum_{i!=k}|d_i|, w_k=S+1, w_i=d_k for i!=k. Then
w.d=d_k*(1+S+sum_{i!=k}d_i)>=d_k>0. Reverse d for the other sign.
This symbolic construction was derived during pre-freeze primary assimilation;
successful reproduction is not an unseen empirical prediction.

## Kernel scope
Use pinned Lean4.19.0. Prefer generic finite-dimensional proofs with only
primitive ordered-ring laws assumed and an actual integer instance.
Do not assume the target scalarization, separator or recovery theorem.
A proof over Int alone cannot certify the real theorem in the kernel.
Map every theorem to its actual kernel scope; give complete real-valued
mathematical proofs for any paper-only specialization. No hidden mathlib
availability, unproved axioms, sorry/admit or vacuous zero-dimensional case.
Register exact statement types and inspect their kernel assumptions.
Include source-valid weakened/empty proof controls.

## Independent executable calibration
Exact arithmetic only. Exhaust all vector pairs in dimensions0–4 over
{-1,0,1}, positive weights over{1,2,3}, and nonnegative weights over{0,1,2}.
Check coordinate domination and dot-product inequalities independently.
For every incomparable pair independently verify both constructed positive
separators, strict opposite rankings and any normalized-weight version claimed.
Also check equal vectors, dimension0, negative coordinates and permutations.
Count actual vectors/pairs/weights/checks and require coverage; finite
calibration supplements universal proof rather than establishing quantifiers.
A second implementation must not import production order/dot/separator logic.

## Falsifiers and hostile controls
Negative weight: 0<1 scored with weight-1 reverses dominance.
Zero weight: (0,0) versus (1,0) with weights(0,1) erases strict improvement.
Positive weights: (1,0) and (0,1) reverse under opposing weights.
Unsupported frontier: in minimization over{(0,3),(2,2),(3,0)}, (2,2)
is efficient but any positive weighted-sum selection would require
2b<=a and2a<=b, impossible. Prove nonselection over all positive weights.
Reject incompatible dimensions, malformed/bool/float aliases, invalid chosen
coordinates, nonpositive advertised separators and illegal arithmetic inputs.
Reject swapped comparison, wrong sign, missing coordinate, ignored strict
improvement, constant/zero separator and coverage omission.
The no-alarm case must pass, and unavailable inputs/toolchain must be
distinguished from checked invalid results.

## Evidence and closure gate
Own modular theory/parent/formal-scope files, executable production and
independent oracle, general Lean proof files, exact proof registration,
measured normal/optimized receipts, review and successor snapshot.
Each prose/code file stays below200lines where practical; split by purpose.
Freeze precedes outcome-bearing implementation and remains byte-unchanged.
Bind all evidence hashes and exact original title/scope/witness mappings.
Preserve all222original IDs and other dispositions. Starting V11 has11closed,
211unresolved; successful sole-atom adjudication would yield12closed,
210unresolved, with R0 still the only EARNED whole round.
Merge only after all exact-head CI succeeds, using a merge commit.

No architecture recovery, learning performance, new empirical prediction,
prior-free objectives, universal preferred scalar or complete GMI is earned.
R2-003/R2-007 corrections and R1 successor targets stay separately open.
