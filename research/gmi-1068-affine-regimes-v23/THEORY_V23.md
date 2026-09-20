# V23 theory — whole-interval context regimes

Frozen authority: FREEZE_V23.md, commit ee52f48a6fb4c66c0a618a6ade52e730d726f663.
This file gives mathematical proofs. Exact kernel scope and finite outcomes are
separately recorded by FORMAL_SCOPE_V23.md and RESULT_V23.json.

## W1.1 — fixed comparison semantics

Fix identities I, predicates P,E and coefficients a_i,b_i in a linearly ordered
commutative ring A satisfying the V12 primitive Scalar laws. Put D={i:P(i) and E(i)}
and f_i(t)=a_i+b_i*t. Define Win(t)={i in D: every j in D has f_i(t)<=f_j(t)}.
No selector breaks ties. I may be infinite for the logical endpoint statements;
existence of a winner is not assumed for arbitrary infinite D.
CONTEXTS_V23 proves this is the identity projection of an actual contextual frontier.
Fix lo<=hi. Every quantifier over t below ranges over the entire closed interval.

## W2.1 — direct endpoint domination without division

For fixed i,j write d(t)=f_j(t)-f_i(t)=alpha+beta*t, beta=b_j-b_i.
Distributivity gives d(t)-d(u)=beta*(t-u). If beta>=0 and t>=u, multiplication
and translation compatibility give d(t)>=d(u). If beta<=0 and t>=u, they give
d(t)<=d(u), by applying the same nonnegative-product law to -beta.
Total order supplies the exhaustive cases beta>=0 or beta<=0.
If beta>=0 then d(t)>=d(lo); otherwise d(t)>=d(hi).
Thus nonnegative endpoint differences imply d(t)>=0 throughout, and positive
endpoint differences imply d(t)>0 throughout. Conversely the interval includes
both endpoints. Therefore weak (respectively strict) pairwise dominance throughout
is equivalent to weak (respectively strict) dominance at both endpoints.

This proves every ordered-ring point between lo and hi, without dividing by hi-lo
or assuming normalized interpolation covers the interval. When lo=hi the condition
reduces to its single point.

## W2.2 — universal and unique winner quantifiers

For any i, membership in every Win(t) means i in D and every active competitor
has nonnegative difference throughout. W2.1 exchanges that condition with its
two endpoint conditions. Hence intersection_t Win(t)=Win(lo) intersection Win(hi).
No finite-minimum existence assumption is needed for this equality.

An active i is the unique winner at a fixed t iff f_i(t)<f_j(t) for every active
j distinct from i. Forward: i wins, and equality would also make j a winner.
Backward: strict inequalities imply weak inequalities and exclude every other
winner. Total scalar order is used here. Apply strict W2.1 for each competitor:
i is the same unique winner throughout iff it is active and strictly beats every
other active identity at both endpoints. A singleton active family satisfies this
vacuously. An empty family has no active witness to the claimed uniqueness.
A singleton universal weak-winner intersection need not imply uniqueness; see controls.

## W2.3 — endpoint interpolation and checked-root factorization

For 0<=s<=1 put t_s=(1-s)*lo+s*hi. Ring distributivity gives
f_i(t_s)=(1-s)*f_i(lo)+s*f_i(hi).
Both coefficients are nonnegative; t_s-lo=s*(hi-lo)>=0 and
hi-t_s=(1-s)*(hi-lo)>=0 show interval membership.
Weak endpoint domination follows by summing nonnegative weighted differences.
For strict domination, if s=0 use the left difference. Otherwise s>0, so its
product with the positive right difference is positive and the left term is
nonnegative. Strict comparison follows. Direct W2.1 also proves the result.
This parametrization is not surjective in every ordered ring: over Int, lo=0,
hi=2 and t=1 admit no integral s between 0 and 1 realizing t_s=1.

If an actual equality f_i(c)=f_j(c) is given, algebra yields
f_i(t)-f_j(t)=(b_i-b_j)*(t-c). Its sign follows from the signs of the factors.
This derives behavior around an existing root; it does not assume root existence.
DIAGRAMS_V23 supplies division-based existence over Q/R as a separate theorem.

## W3 dependencies and remaining boundaries

A finite nonempty D has a minimum score: enumerate D, start with its first member,
and retain a smaller-scored member at each step. Induction proves the retained
score is no greater than every score scanned; its final identity belongs to Win(t).
All t therefore have winners for finite nonempty D. Collect all identities at
that minimum to preserve ties, rather than returning the scan witness alone.

DIAGRAMS_V23 proves complete rational diagrams and interval certificates.
All identities, P/E and coefficients stay fixed across t. This derives no preferred
parameter, prior on parameters, physical phase transition, infinite attainment,
or canonical architecture ranking. Parameter-dependent admission or nonlinear
evaluation needs a new registered family. The original common-space requirement
is met constructively, without comparing unexplained codes or changing value meaning.
