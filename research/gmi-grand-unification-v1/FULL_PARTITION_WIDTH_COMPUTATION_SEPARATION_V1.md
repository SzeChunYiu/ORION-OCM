# Full input-partition width and query-summary separation — FPW-1–2

Date: 2026-09-13. Status: exact scoped nondetermination and finite witnesses.

## 1. Parent mechanisms and precise scope

The classical query parent is [Buhrman and de Wolf (2002), Sections 1 and
3.1](https://homepages.cwi.nl/~rdewolf/publ/qc/dectree.pdf): exact deterministic
bit-query trees and their worst-case depth. [Ambainis and de Wolf (2000),
*Average-Case Quantum Query Complexity*, Section 2](https://homepages.cwi.nl/~rdewolf/publ/qc/avq.pdf)
separately defines the classical deterministic average as minimum expected
queries under a declared input distribution, while requiring correctness on
all inputs. We use those classical definitions faithfully. No quantum access,
randomized error or new query-complexity theorem is introduced here.

Fix n>=2. For **every indexed subset** S of [n], a sender knows x_S and sends
one message to a decoder knowing all of x_complement. The protocol must
compute f(x) exactly for every x in {0,1}^n. Messages are classical,
deterministic and one-way; timing and other side channels are excluded.
Local encoding/decoding work is unrestricted in this width abstraction.
Let W_f(S) be the ceiling of log2 of the minimum message alphabet cardinality.
The entire indexed width collection is W_f=(W_f(S))_(S subset [n]).

Separately, one processor learns x only by exact individual-bit probes and
must output f(x). The input is uniform and independent across bits. No
input-dependent initial state or advice supplies unqueried bits. Let D_f be
minimum worst-case probes and E_f minimum expected probes of an exact
deterministic algorithm. Q_f=(D_f,E_f) is the query summary considered here.
Non-query computation, code, controller state, output writing, memory and
physical costs are separate; neither abstraction certifies their feasibility.

These are fixed task summaries with declared interfaces, not an identification
of every causal-network cut with an input partition. They do not include full
response relations, weighted entropies or general transformation frontiers.

## 2. FPW-1 — identical entire width collection, unequal expected queries

Let f=OR_n and g=PARITY_n, with the same Boolean output alphabet. Then

    W_f(S) = W_g(S) = 0 if S is empty, and 1 otherwise;
    D_f = D_g = n;
    E_f = 2 - 2^(1-n),       E_g = n.

**All partitions, upper bound.** For empty S the decoder knows the whole
input and one message symbol suffices. For nonempty S, send respectively
OR(x_S) or parity(x_S); the decoder combines it with the corresponding
operation on its complementary bits. Two symbols suffice for every S.

**All partitions, lower bound.** Set the decoder's complementary bits to zero.
The all-zero sender input and one with a single one require different outputs,
for both functions. They cannot share one message. Hence every nonempty S
requires exactly two symbols. This proves equality at all indexed partitions,
not merely at the final output cut. It does not equate their response rows.

**Query costs.** An exact parity algorithm cannot stop with an unqueried bit:
flipping that bit preserves the transcript and changes the answer. Thus every
input requires n probes, and querying all bits attains both bounds. For OR,
the all-zero input requires n probes by the same indistinguishability argument.

For expected OR cost, repeated probes can be removed without changing the
answer or increasing cost. Along the all-zero transcript, a correct algorithm
cannot stop until n distinct bits have been queried. Under the uniform input,
the first k such adaptively chosen bits are all zero with probability 2^-k.
Thus for 0<=k<n, Pr(T>k)>=2^-k and

    E[T] = sum_(k>=0) Pr(T>k) >= sum_(k=0)^(n-1) 2^-k = 2-2^(1-n).

Querying bits sequentially and stopping at the first one attains equality.
The ratio E_g/E_f grows without bound. Therefore the full W collection,
even together with n and the shared worst-case depth, does not determine
uniform-input exact expected query complexity. Average advantage here is not
a per-input guarantee: the rare all-zero OR input still costs n.

## 3. FPW-2 — reverse nondetermination in a common output alphabet

Now use the common output alphabet A={0,1}^n. Define ID(x)=x and
RP(x)=(parity(x),...,parity(x)). Both have

    D_ID = E_ID = D_RP = E_RP = n.

Indeed, on every input any unqueried bit can be flipped to change the required
output of either function, and querying all bits suffices. This is also equality
of their pointwise optimal query counts, not just equal distributional means.
Yet their partition widths are

    W_ID(S)=|S|;
    W_RP(S)=0 for empty S, and 1 otherwise.

For ID, sending the sender's |S| bits suffices. With the complement fixed,
every one of its 2^|S| assignments requires a different output, proving necessity.
For RP, sending one subset parity bit suffices and the same zero-complement
argument requires it when S is nonempty. At S=[n], the widths differ by n-1.
Thus Q alone does not determine W. FPW-1 and FPW-2 establish mutual
nondetermination of **these declared width/query summaries**. The reverse pair
has a common output alphabet; it does not rely on charging output-writing work
as queries or assert that their output distributions agree.

## 4. Exact checker and completeness of the finite oracle

`grand_gmi_partition_width_checks_v1.py` builds actual truth tables for all four
functions at n=2,...,8. For every S it enumerates sender assignments a and
complementary assignments b and forms each response row (f(a,b))_b.
Two sender inputs can share a message exactly when these rows agree: differing
rows conflict at some decoder input, while a row label is a sufficient message.
Therefore counting distinct rows computes the exact minimum alphabet. The
oracle compares these counts for every indexed S, without substituting the
one-bit formulas into the calculation.

For query complexity it evaluates all 3^n partial assignments p. A constant
restricted truth table needs zero further queries. Otherwise every exact tree
must first query an unassigned coordinate i; its two branches give

    E(p)=min_i [1+(E(p,i=0)+E(p,i=1))/2],
    D(p)=min_i [1+max(D(p,i=0),D(p,i=1))].

Conditional unseen bits remain uniform, including after adaptive queries.
Induction on the number of unknown bits proves necessity of this exhaustive
first-query split and sufficiency by choosing minimizing child trees. Repeated
queries cannot improve either nonnegative cost. Every partial state and every
useful first-query branch is checked from truth-table outputs. The resulting
mean-optimal policy is also executed on every complete input and must return
the correct output with the reported average cost.

Tests independently enumerate complete decision-tree depth profiles for every
two-bit Boolean function, rather than selecting minima during recursion, and
brute-force message encoders for the two-bit functions and identity. Constant
functions, malformed registers, empty partitions and equal-width/unequal-row
controls prevent an indiscriminate positive verdict. The receipt records the
finite census; the mathematical proofs cover every n>=2.

## 5. Boundary inherited from the final-cut scope repair

[The earlier separation](INFORMATION_COMPUTATION_SEPARATION_THEOREM_V1.md)
left full-spectrum nondetermination open. This unit resolves it for the exact
all-input-partition **width** collection W and the explicit query summary Q.
It does not show independence of arbitrary richer Kappa/Tau collections.
OR and parity have different response relations and, under uniform inputs,
different output entropies. Dynamic cuts, shared resources, interactive
protocols, other distributions, error allowances and charged local operations
require new registered comparisons. This is a classical scoped witness, not
a claim of universal GMI completion or a new complexity-theoretic breakthrough.
