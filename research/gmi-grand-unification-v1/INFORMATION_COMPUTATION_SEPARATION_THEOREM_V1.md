# Grand GMI Information–Computation Separation Theorem V1

Status: **EXACT FINAL-CUT / QUERY SEPARATION; BROADER CLAIM CORRECTED**
Date: 2026-09-12; scope and joint-attainment refinement: 2026-09-13.

## 0. Exact claim and established parent

Final-cut semantic width alone does not determine deterministic query
complexity. Even on one fixed input domain, the same one-bit final-cut
requirement is compatible with every exact query complexity from 1 to n.

This does **not** prove independence of the full collections
`{Kappa_G(C,epsilon)}_C` and `{Tau_G(R,epsilon)}_R`, nor that every theory
expressed using information is incomplete. The proof compares a single final
cut, not all cuts. The previous claims of two irreducible invariant families
and the impossibility of all information-based theories exceeded that scope.

The established parent is deterministic decision-tree complexity:
[Buhrman and de Wolf, *Complexity Measures and Decision Tree Complexity:
A Survey* (2002), Sections 1 and 3.1](https://homepages.cwi.nl/~rdewolf/publ/qc/dectree.pdf).
It defines adaptive input-bit queries and minimum worst-case tree depth;
the same survey records `D(OR_n)=n`. We use that model faithfully and add an
explicit final-message interface. The classical lower bound is not a new GMI
complexity result. The joint feasibility statement below is a direct adaptation
of these query bounds and elementary distinguishability.

## 1. Register and coordinates

Fix n>=1 and input x in {0,1}^n. A deterministic local processor learns x
only through adaptive probes of individual bits. Every input is admissible;
there is no input-dependent advice, precomputed answer, stronger oracle,
or input-dependent initial state. The fixed obligation and its indices are
known to the processor and actuator.

The processor sends one final symbol to an actuator with no input side
information. The actuator must output f(x) exactly from that symbol alone.
Timing, silence, query transcripts and other side channels are unavailable
to the actuator. Local computation precedes that final transmission.

For an exact Boolean obligation define

    kappa_f = ceil(log2 |image(f)|),
    tau_f = minimum worst-case number of probes in an exact decision tree.

Here kappa is final-message alphabet width, not Shannon entropy, mutual
information, total memory or the full indexed cut spectrum. No input
probability distribution is assumed. Under a uniform input distribution,
projection and OR generally have different output entropies despite identical
final-cut width.

The query model records probes only. Transient accumulator state, probe
addresses, controller/code storage, local operations, time, energy and
communication implementation have separate resource charges when relevant.
Their feasibility is not implied by a one-bit final message or by tau.

## 2. Exact separation at fixed input size

For each 1<=k<=n, let

    f_k(x_1,...,x_n) = OR(x_1,...,x_k).

Then, in the same registered query model,

    kappa_(f_k) = 1,       tau_(f_k) = k.

**Proof.** Both outputs occur, so the final alphabet requires two distinct
symbols and one bit suffices. Querying the first k coordinates computes f_k
with at most k probes. For the lower bound, answer zero to every probe. If
any of the first k coordinates remains unqueried, both the all-zero input
and the input with a single one at that coordinate remain consistent with
the transcript, while their required outputs differ. Therefore an exact
algorithm must probe all k relevant coordinates on the all-zero input.
Probing an irrelevant coordinate cannot resolve this ambiguity. Hence the
worst-case depth is exactly k. QED.

The original easy-versus-OR comparison is k=1 versus k=n: for n>=2,
`f_easy(x)=x_1` and `f_hard(x)=OR(x_1,...,x_n)` both have final-cut width 1,
while their query complexities are 1 and n. Their ratio is unbounded as n
grows. More strongly, fixing n>=2 still gives different query requirements
at the same final-cut width and input size.

Thus neither `tau=F(kappa)` nor even `tau=F(n,kappa)` can hold for all these
obligations. This rules out sufficiency of those particular coordinates;
it does not rule out richer information descriptions or encodings.

## 3. Joint message/query feasibility is attained

Let m>=1 be an integer allowance for the final message alphabet cardinality,
and q>=0 an integer worst-case probe allowance. For obligation f_k, exact
realization under these two allowances is possible if and only if

    m >= 2   and   q >= k.

Necessity of m>=2 follows because a one-symbol message with no side channel
cannot produce two required outputs. Necessity of q>=k is the all-zero
adversary above and holds regardless of m. A larger final alphabet supplies
no information to the local processor before it computes its message.

For simultaneous sufficiency, query coordinates 1,...,k, accumulate their
OR, and then emit one of two symbols for the result. This one construction
uses k probes and two final symbols. It attains the coordinate pair jointly;
there is no inference from separate unattained minima. With only these two
allowances constrained, the feasible region is exactly the stated rectangle.

The accumulator, its updates, scheduling/address state and controller are
part of this construction, not information hidden in the final channel.
Their costs remain separate. Additional limits on them require another
feasibility analysis; this result does not establish total physical cost,
bounded-memory attainability, or universal architecture sufficiency.

## 4. Consequence for the GMI record

It is useful to record both cut requirements and legal transformation costs.
For a region R, let P_R be the registered substrate-legal processes realizing
its required input/output relation, and rho_R(T) their charged resource vectors.
One may record their feasible resource set and, when applicable, its Pareto
minimal elements as `Tau_G(R,epsilon)`. This is a modeling definition, not an
attainment theorem: Pareto minimal elements need not exist in every register.

The proposed record

    Xi_G = (S*, {Kappa_G(C,epsilon)}_C, {Tau_G(R,epsilon)}_R)

keeps semantic equivalence, indexed cut constraints and local cost information
explicit. This finite theorem motivates that bookkeeping but proves neither
that the full collections are irreducible nor that Xi_G is a complete invariant.
Upstream cuts can reveal which coordinates matter; time-indexed cuts can
also encode aspects of the acquisition process. Their equality was not proved
for the easy-versus-OR pair.

The warranted architecture lesson is precise: providing the final output
channel does not supply the probes needed to compute that output. Claims
about retrieval, proof search, thermodynamics or general intelligence require
their own registered mechanisms and bounds rather than an analogy to this pair.

## 5. Executable scope and remaining independence obligation

`grand_gmi_checks_v1.py` computes optimal deterministic decision-tree depths
for projection and OR at n=2,...,7. Projection supplies the k=1 case; the OR
cases supply k=2,...,7. These existing exact checks cover the essential query
bounds. The proof above justifies adding irrelevant input coordinates and
joint query-then-emit realization; the receipt is not a new enumeration of
every padded (n,k), physical controller, or complete cut spectrum.

A stronger independence study must first fix the substrate, admissible
architectures, causal cut index set, error regime, side information and resource
pricing. It must then match the **entire** relevant Kappa collection under a
declared correspondence and prove that a Tau coordinate/frontier differs.
An exact finite census may seek such a pair or expose a recoverability relation;
either outcome must be retained. If mutual independence is claimed, the reverse
non-determination also needs its own witness. Equality at the final cut alone
cannot discharge this obligation. No such full-spectrum witness is established
here.

A scoped successor now proves both directions for the explicitly registered
all-input-partition width and worst/average-query summaries:
[FPW-1–2](FULL_PARTITION_WIDTH_COMPUTATION_SEPARATION_V1.md). Richer Kappa/Tau
collections and response relations retain the boundaries stated above.
