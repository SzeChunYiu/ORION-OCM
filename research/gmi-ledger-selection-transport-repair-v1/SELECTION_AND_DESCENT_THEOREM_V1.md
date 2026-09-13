# Same-task selection and finite ordinal adequacy — LST-1–3

Status: conditional repair of PR590's learning-law and ecology interpretation.
This is an application of the [bound parents](PARENTS_AND_COSTS_V1.md), not a
new optimizer, convergence theorem or general learning-law classification.

## LST-1 — applicability precedes preference

The original seven-tag, five-label menu is a stipulated finite classifier.
Its exact 128-input census (36 empty, 50 unique, 42 tied) and six point-price
comparisons remain valid. Empty means no admitted label in that menu; it
does not establish physical infeasibility. A full contract determines a
set of minimizers, not necessarily a unique law or an executable learner.

Formal OPTIMIZATION O0 supplies the objective, derivative, update domain,
movement penalty, positive step size and local minimization decision.
O1's projection requires a nonempty closed convex set (or unconstrained
Euclidean space). O2 requires the actual mirror potential, existence and
appropriate differentiability/interiority; convergence requires further
premises. Geometry names and differentiability alone do not supply these.

For finite prior p_j>=0, sum p_j=1, and finite likelihood L_j>=0, define
Z=sum p_j L_j. If Z>0, Bayes gives q_j=p_j L_j/Z. If Z=0, this conditioning
operation is undefined; three tag bits cannot repair its zero denominator.
For positive p,L, entropy mirror descent with eta=1 and g_j=-log L_j has
exactly this same q. Indeed its normalization is sum p_j exp(-g_j)=Z.
Writing p'_j=p_j L_j/Z, the objective in a trial distribution u equals
KL(u||p')-log Z, uniquely minimized at p'. With zero likelihoods and Z>0 use the nonzero posterior support.
This is O2/O3 and the Beck–Teboulle/Bissiri parents, not a new equivalence.

For p=(1/2,1/2), L=(1,2), both updates return (1/3,2/3). Changing the cost
assigned to the two labels can select different labels for the same map.
Different implementations can still have different costs; labels do not
establish either implementation identity or scientific superiority.

## LST-2 — a constructive finite common-task contract

Fix a finite nonempty input set X and, for each x, a nonempty finite set
Gamma(x) of adequate outputs. Register a finite set I of total table
implementations f_i:X->Y, with exact output equality. Each is an executable
lookup table, not a certificate of an arbitrary supplied program's behavior.
Reject incomplete, undefined or out-of-domain tables before selection.

Check every (i,x), and retain A={i: f_i(x) in Gamma(x) for every x}.
Supply finite nonnegative complete implementation charges c_i at one
common task, lifetime, valuation and execution interface. Let s>=0 include
the whole registration, construction/evaluation of evidence, all admission
checks, selection and retained apparatus charges not already in c_i.
Each physical charge or upper bound needs its own warranted accounting.
No operation in this proof is free merely because it is called validation.

If A is nonempty, an exact scan yields argmin_(i in A) c_i, including ties;
any returned implementation is adequate and minimizes s+c_i over A.
Proof: exhaustive table checking establishes adequacy, and finite comparison
attains the minimum. Adding common s preserves all orderings. Conversely an
inadequate cheap table cannot be admitted by lowering its price. Empty A
means this registered menu has no adequate member, not that none exists.

The helper performs |I||X| adequacy checks and |A| cost visits; supplied per
check/visit charges are added to a supplied common setup charge. These are
declared abstract charges, not inferred CPU time or a complete hardware model.
It reports the complete validation burden even when A is empty. Table
materialization, acquisition and retention must be included in setup or c_i.
The helper does not audit arbitrary physical cost declarations.

An extension to all implementations needs coverage: for every adequate
outside implementation j, some retained i has c_i<=c_j at the same scope.
MSC-2 supplies that standard sufficient condition. A sample, family label,
capability tag or point-price vector does not establish it. With uncertain
costs, use the actual joint feasible worlds (EFI); exact point prices are
legitimate degenerate worlds and do not themselves need error intervals.

The six old price vectors are authored arithmetic examples. There is no
sample-access variable deriving E1's likelihood price 5 from sample scarcity,
nor a common adequate task tying all five labels to competing full learners.
Their document explicitly denies temporal preregistration. These examples
remain point-menu predictions; they are not ecological or full-family laws.

## LST-3 — when local ordinal descent supplies an adequate implementation

Let a finite nonempty directed graph (V,E) give admitted one-step moves.
Let f:V->R be exact, and A subseteq V the adequate states. An algorithm checks
all outgoing moves and takes any strictly decreasing one when one exists;
otherwise it stops. A local minimum means no strictly decreasing outgoing
move, so plateaus count as local minima under this strict rule.

Every such trajectory terminates in at most |V|-1 moves: strict descent
forbids repeating a vertex. If every local minimum is adequate, every
trajectory from every start terminates adequately. Conversely, if every
such trajectory from every start is adequate, every local minimum must be
adequate, since starting there stops immediately. Thus this is an exact
all-start adequacy criterion for this declared move rule.

For a restricted start set it suffices to check all minima reachable by
strict descent from those starts; arbitrary other minima need not qualify.
Neither version identifies a global optimizer unless adequacy itself means
global optimality. Verifying that predicate can require full enumeration
or an independent mathematical certificate.

On the bidirectional three-vertex chain, f=(2,3,0), state 0 is an inadequate
local minimum for adequacy A={2}. Its downhill trajectory stops immediately,
while complete enumeration finds the adequate global minimum at state 2.
Cheap comparison does not make this hill climb solve enumeration's task.
A constructive revival adds the admitted edge 0->2 (and charges discovering,
validating and storing it), or uses charged exhaustive enumeration. Both
restore all-start adequacy; simply asserting ordinal comparison does not.

The finite helper checks all vertices/edges, identifies local minima, and
returns a certificate or the exact bad minima. Counts are n objective reads,
n adequacy checks and m directed edge comparisons before deployment.
A trajectory separately pays its visited outgoing comparisons and moves.
These validation/acquisition costs can eliminate an apparent price advantage;
no universal efficiency claim or optimal graph construction is made.
