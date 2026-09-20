# Next original scientific requirements
These are prospective targets, not earned closures. Each needs a successor
freeze, proof/evidence, independent review, exact-head green CI and merge.

## R2-006: scalarization boundaries
For arbitrary finite real vectors prove nonnegative weighted sums preserve
coordinate order; strict improvement on a positive-weight coordinate implies
strict score improvement. Prove x<=y iff every strictly positive weighted sum
orders x below y. Construct opposite positive weights for every incomparable
pair. A single scalar cannot reflect a partial order containing incomparables.

Division-free separation: if d_k>0, set S=sum_{i!=k}|d_i|,
w_k=S+1, w_i=d_k otherwise. Then w.d>=d_k>0. Reverse d for the
other ranking. The argument works over ordered commutative rings.
Any Int-only kernel proof must not be presented as a kernel proof over reals.

Controls: negative weights reverse dominance; zero weights erase improvements;
positive weighted sums miss unsupported Pareto points. For minimization,
(2,2) in {(0,3),(2,2),(3,0)} is Pareto efficient but never minimizes a
strictly positive weighted sum. Include empty dimension and ties.

Parent: [Boyd and Vandenberghe, sections4.7.4–4.7.5](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf).
R2-007's universal measure assertion remains a separate corrected target.

## R1-010: original formal-law requirement
The original R1 freeze result7 specifies universal category-law consequences
in Lean. V11 constructs these for typed paths and supplies a quotient
presentation of arbitrary lawful small categories. Independently adjudicate
this original requirement; do not silently include minimality or physical
adequacy. Recheck interpreter uniqueness and both inverse preservation laws.

## R1-004 and R1-005: optional tensor and symmetry
R1-004 candidate: one-object category of bit maps id/reset0/reset1. It is
noncommutative and has no invertible arrow except id. Hypothetical monoidal
unitors are therefore identities; naturality and interchange imply
commutativity by Eckmann–Hilton, a contradiction. Rule out all tensors on
the unchanged category, not only a selected operation. Enlargement differs.

R1-005 candidate: the discrete category on that noncommutative monoid,
with tensor given by multiplication. It is strict monoidal but admits no
braiding for that tensor, since opposite tensor objects can have no arrow.
Do not claim no alternative symmetric tensor could exist.

Parents: [Baez's Eckmann–Hilton account](https://math.ucr.edu/home/baez/week258.html)
and [Riehl, appendixE.2](https://emilyriehl.github.io/files/context.pdf).
Check unitors, naturality, interchange and actual finite laws.

## R1-008: process instances
Construct finite stochastic kernels and nonempty-valued maps; prove lawful
composition and faithful Dirac/singleton deterministic embeddings. Prove the
finite support functor and its failure to recover probability weights.
Reject negative or unnormalized rows and empty total outputs.
Parent: [Fritz, examples2.5–2.6](https://arxiv.org/html/1908.07021v8).
This is optional process structure, not an environment probability prior.

## Correct targets before closure
R1-001/007: identity notation can be eliminated while identity structure
survives; primitive counts are not presentation invariant.
R1-006: absorbing admission requires identity/composition closure.
R2-003: an evaluator's admitted-history domain reveals admission; the V9
ambient-domain repair changes that formulation and must be declared.
R2-007: general scalar aggregation need not use probability weights.
The broader synthesis, architecture recovery, real-scale predictions and
hostile fixed-point integration remain unresolved.
