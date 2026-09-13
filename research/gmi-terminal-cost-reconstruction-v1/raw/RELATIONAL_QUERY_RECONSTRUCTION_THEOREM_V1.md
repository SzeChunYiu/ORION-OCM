# Relational adequate outputs reconstruct query profiles — RQR-1–4

Date: 2026-09-13. Scope resolution for Q10, with exact finite checks.

## 1. Strongest parents and subtraction

[Javdani et al. (2014), §2–3](https://proceedings.mlr.press/v33/javdani14.pdf)
already allow overlapping successful decision regions and require all surviving
hypotheses to lie in one such region. Their hyperedge construction captures
higher-order incompatibility; their greedy guarantees are not imported here.
The exact mapping is R_a={x:a in A(x)}: a common adequate output exists iff
the current candidate set lies inside R_a for some a.

The repository's [TDA-1–3](TASK_DIRECTED_ACQUISITION_THEOREM_V1.md)
already supplies this stopping law and exact adaptive acquisition. [LQR-1–4](LABELLED_PARTITION_QUERY_RECONSTRUCTION_THEOREM_V1.md)
supplies labelled-cube profile preservation and joint optimization.
**The positive reconstruction below is an immediate corollary of those
mechanisms, not a new decision-tree complexity theorem.** Its remaining GMI
use is specifying the relational invariant precisely, and identifying a
structural regime where pairwise information becomes sufficient.

[Ambainis and de Wolf (2000), §2](https://homepages.cwi.nl/~rdewolf/publ/qc/avq.pdf)
supplies the classical expected-query convention with correctness on all inputs,
including zero-mass inputs. [Kothari et al. (2015), §1–2](https://drops.dagstuhl.de/storage/00lipics/lipics-vol040-approx-random2015/LIPIcs.APPROX-RANDOM.2015.915/LIPIcs.APPROX-RANDOM.2015.915.pdf)
distinguishes arbitrary subcube partitions from actual query trees.
We reconstruct trees, not unrestricted compatible covers.

## 2. Fixed register

Fix n>=0, labelled X={0,1}^n, and nonempty finite output alphabet Z of size k.
Supply the entire indexed relation A(x) subseteq Z. Empty rows are allowed
only to expose infeasibility; ordinary adequate tasks have all rows nonempty.
The only input access is a deterministic exact coordinate query i, costing
a supplied finite nonnegative rational c_i and leaving x and A unchanged.
All inputs are admitted. There is no input-dependent advice or initial signal.
Policies are finite deterministic query trees and must emit an element of
A(x) on every input. Expected work uses a supplied rational distribution mu;
zero mass does not remove an input's success obligation.

Query work v_T(x) is the sum of query charges on input x's executed path.
Output choice/emission, controller execution, storage and compilation are
excluded from this coordinate and are not reconstructed as physical costs.
An admitted output dictionary is needed to emit actual labels.

For a partial assignment p in {*,0,1}^n, let C(p) be its nonempty subcube and

    I_A(p) = intersection_(x in C(p)) A(x),
    Gamma_A(p) = 1 iff I_A(p) is nonempty.

Gamma retains feasibility of every reachable stopping cell. It does not
retain which outputs succeed. It is semantically coarser than the full relation,
but its 3^n-entry table need not occupy fewer bits than a dense relation table.

## 3. RQR-1 — profile reconstruction from stopping cells

If Gamma_A=Gamma_B on the same labelled cube and query/cost interface, the
complete sets of attainable pointwise query-work vectors coincide. Therefore
all joint images of those vectors under common cost functionals coincide.

**Proof.** Every reachable leaf of a finite query tree is associated with the
subcube fixed by its transcript, even if it repeats coordinates. A tree shape
admits adequate A-labels exactly when Gamma_A is true at every reachable leaf.
Equal Gamma permits a B-output at each of those same leaves; queries, branches
and each input's work remain unchanged. Unreachable leaves may take arbitrary
labels because Z is nonempty. Reversing A and B proves equality of profile sets.
This is equality of attainable profiles, not a bijection of output-labelled
policies or reconstruction of output identities. QED.

Thus the full indexed action family is sufficient. Gamma alone supplies
adequate query shapes; constructive output labels additionally require I_A(p)
or a separately supplied valid leaf-output dictionary.

## 4. RQR-2 — finite constructive joint optimization

Let F(p) be the complete set of no-repeat remaining-work vectors on C(p).
Include its zero vector when Gamma_A(p)=1, and for every unfixed coordinate i
include all vectors formed from a child pair u in F(p,i=0), v in F(p,i=1):

    w(x) = c_i + u(x) when x_i=0, and c_i + v(x) when x_i=1.

Take the union of these possibilities, including query options at stopping
cells. If no option exists, F(p) is empty. Each stored vector keeps its tree;
stopping chooses a common output. Induction on the unfixed coordinates proves
that this grammar includes exactly every no-repeat tree's cost vector.

A repeated query has its answer fixed by the prior transcript; replace it by
the reached child. This preserves adequacy and never increases work because
charges are nonnegative. Hence every finite adequate tree is pointwise
dominated by one represented at F(*). Removing dominated vectors from this
finite set gives the exact frontier for all finite trees, and decides joint
finite upper bounds for monotone query-cost objectives. Gratuitous positive
queries matter to the full no-repeat set but not its Pareto frontier.
The unrestricted wasteful profile set may be infinite; this finite algorithm
claims exact optimization and downward feasibility, not finite enumeration of it.

For mean/worst constraints inspect one shared vector:

    (sum_x mu(x) v(x), max_x v(x)).

Separate minima need not be jointly attainable. If any A(x) is empty there
is no adequate tree; otherwise querying all n bits constructs one. Zero-cost
queries and n=0 are included. Infinity is an impossibility sentinel, never a
resource allowance. No randomization or probability-one relaxation is admitted.

## 5. RQR-3 — what pairwise summaries miss, and a positive repair

With unit queries, use the same four inputs and output alphabet {a,b,c,d}:

| x (ordinary binary display) | A_R(x) | A_S(x) |
|---|---|---|
| 00 | {a,b} | {a,b} |
| 01 | {b,c} | {a,c} |
| 10 | {a,c,d} | {a,b,d} |
| 11 | {a,b} | {a,b} |

Both have the complete pair-compatibility graph, the same action-set equality
partition ({00,11},{01},{10}), row sizes (2,2,3,2), and used output alphabet.
S admits constant a and zero work. R has empty intersection already on
{00,01,10}, so no zero-query tree exists. Querying the low bit permits a on
{00,10} and b on {01,11}. Thus R's exact mean/worst optimum is (1,1), while
S's is (0,0), under every prior. This refutes reconstruction from all those
cheaper summaries combined. The displayed incompatible triple witnesses that
the root-cell intersection is empty. Gamma records this root-cell failure;
Gamma plus a supplied leaf-output dictionary constructs the one-query remedy.

**Interval repair.** If every adequate set is a nonempty interval [l_x,u_x]
on one common finite ordered output alphabet, pairwise compatibility suffices
on every subcube. Let L=max l_x and U=min u_x over a subcube. The intervals
attaining L and U intersect if all pairs do, so L<=U and L is a common output.
The converse is immediate. Thus the labelled pair graph determines Gamma and
all query profiles within this interval register. The endpoints/dictionary
are still needed for actual output construction. This is the elementary
one-dimensional Helly property, not a property of arbitrary output sets.

More generally, with k outputs any empty intersection has a witness of at most
k inputs: choose, for each output a, one input excluding a. The bound is sharp
for unrestricted set families: A_j=Z minus {j} for j=1,...,k has compatible
every (k-1)-subfamily and incompatible full family. Duplicate rows embed this
witness in a cube of at least k inputs. This elementary arity bound and the
DRD parent's sharper structural bounds do not make pairwise tests universal.

## 6. RQR-4 — genuine ambiguity with incompatible joint minima

Take LQR's weighted selector f(x)=x_1 if x_2=0, otherwise x_0, costs (1,2,3),
mu(111)=8/15 and all other masses 1/15. Set A(x)={f(x),z_x}, where every z_x
is a distinct private output and none equals 0 or 1. Every input has two
acceptable outputs. A nonsingleton cell has a common output exactly when f
is constant there; singleton cells always permit stopping. Hence Gamma is
identical to the exact-function task, and its full query profile set agrees.

LQR's exhaustive first-query proof transfers without alteration. The exact
joint frontier remains {(19/5,6),(64/15,5)}. No tree meets (19/5,5); relaxing
either coordinate to the corresponding frontier point constructs a solution.
Selecting the private output z_x in advance would instead require identifying
all three bits, charging 6 on every input. Optimizing adequate action is
therefore distinct from arbitrary representative-output identification.

## 7. Representation, development and finite evidence

The supplied relation is not learned for free: a dense table uses Nk membership
bits, N=2^n, plus alphabet/header encodings. Gamma uses 3^n Boolean entries;
a selector dictionary can require further label payloads. Acquiring or proving
any input row is an additional cost. None follows from query-profile equality.

The implementation counts 3^n states, 6^n mask-membership tests, 2n3^n pattern
bit visits, and 4^n relation-row reads/bitset intersections. Bitset operations
have k-bit operands. It considers n3^(n-1) first-query choices for n>=1,
zero for n=0; Cartesian profile combinations and vector entries are counted
separately. These counts expose development work; exact-arithmetic bit costs,
allocation, program/model representation and output/controller costs remain
additional charges, not silently covered physical costs. An output-dependent
terminal charge already defeats Gamma as an invariant of total cost.

The [receipt](GRAND_GMI_RELATIONAL_QUERY_RECEIPT_V1.json) compares all profiles with an
independent syntax oracle: 4,168 relations on cubes n=0,1,2 with three outputs,
including empty rows; 1,296 interval relations; 512 weighted/zero-cost controls;
and the eight-input ambiguous selector. The oracle executes every no-repeat
shape before checking a relation, then searches actual output labels at each
leaf. It includes unnecessary queries and validates emitted synthesis labels.
This closes the stated relational Q10 implication, not changed interfaces,
arbitrary internal cuts, empirical semantics or unrestricted physical spectra.
