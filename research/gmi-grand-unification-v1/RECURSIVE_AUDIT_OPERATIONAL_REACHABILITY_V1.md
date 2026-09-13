# Recursive GMI audit — finite operational reachability, 2026-09-13

Reviewed predecessor: `5622ac45d0261e8fe0a92f4209b1bb782ce43732`.

Normative repair: `../machine-intelligence-morphogenesis-v1/GMI_OPERATIONAL_COMPLETENESS_THEOREM_V1.md`, especially FOC-4 and the exact-arithmetic scope. The original finite operational capability/frontier microscope remains unchanged; this correction adds checks for claims it did not previously test.

| Stable gap ID | Independently reconstructed counterexample | Correct replacement | Verification scope |
|---|---|---|---|
| GMI-AUDIT-FOC-01 | Equally adequate machines have costs 2 and 1, but only the cost-2 machine is reachable. Filtering the global frontier gives the empty set and loses the constrained optimum. | Form the profile image of feasible reachable machines before taking Pareto. Accessible global-optimum profiles are a separate subset of this constrained frontier. Reachable fibers filter machines through the profile map. | 5,103 finite three-candidate profile/reachability cases, including 1,542 where the old filtering rule loses reachable optima. |
| GMI-AUDIT-FOC-02 | A zero-cost self-loop followed by a cost-1 exit has infinitely many distinct histories within budget 1. Finite states and finite budget do not make its history tree finite. | Traverse deduplicated state/cost-label pairs. Finite nonnegative rational edge vectors and finite component budgets yield at most `|S| product_i(floor(L B_i)+1)` such pairs. Full state must preserve future moves, output and history-sensitive obligations. | 2,187 graph/budget cases, including 651 containing zero-cost two-cycles, compared to an independently enumerated simple-path oracle for reachable states and Pareto cost labels. A 65-history prefix illustrates the analytic infinite family; it does not prove infinitude by enumeration. |
| GMI-AUDIT-FOC-03 | The uniformly computable real `x_P=2^-t` if program P halts at step t and 0 otherwise cannot have a uniform exact zero test. Even a two-machine frontier can depend on that test. | Require effective exact arithmetic and decidable required equality/order predicates, for example rational or effectively represented real-algebraic coordinates. Mere real computability permits approximation but does not certify exact ties/dominance. | Analytic reduction to halting; 1,088 exact delayed-halting interval cases and 32 same-finite-evidence pairs illustrate the boundary. Bounded simulation does not prove undecidability. |
| GMI-AUDIT-FOC-04 | Singleton protected alphabets, one-step horizon and one response kernel still permit implementations with identical responses and unbounded invisible resource burden n. Thus the trace/resource profile set can be infinite, even though its scalar Pareto minimum exists. | Explicitly register a finite effectively enumerable operational-realization domain. FOC-1 enumerates its attained profiles; FOC-3 enumerates only its registered fibers. Finite bounded cost grids restrict possible profiles but do not independently decide realizability or enumerate implementation fibers. | 65 growing finite prefixes preserve one response while increasing distinct resource profiles to 65; a finite register with 65 candidates sharing one profile shows why candidate-domain/fiber cardinality is separate. The infinite-universe counterexample is analytic. |

The state/label construction also preserves the distinction between minimizing one scalar cost and retaining a vector-cost Pareto set. Two paths costing `(1,3)` and `(3,1)` cannot be combined into a fictitious `(1,1)` path, and neither meets budget `(2,2)`. The checker verifies this directly. If lifecycle/development cost is selected, endpoint and actual cost label must remain together when the final frontier is formed.

## Correctness arguments

For reachability, finite rational edge costs have a common denominator L, so component budgets leave finitely many accumulated labels. Induction on paths proves closure completeness; nonnegative costs keep prefixes admissible. Expanding an already seen state/label cannot add new continuations, because all future-relevant information is registered in that state and label. Breadth-first closure also gives minimum steps to each pair. It enumerates pairs and witnessing paths, not all histories.

The independent graph oracle enumerates simple paths in the original state graph. Any repeated-state cycle has a nonnegative cost vector, so deleting it leaves the same endpoint at no greater cost. Consequently simple paths suffice for reachable-state existence and nondominated costs; they do not enumerate all dominated labels. Comparing those quantities to the complete finite label closure exercises two distinct algorithms.

For exact order, simulate program P for n steps. If it has halted, its encoded value is known exactly; otherwise `[0,2^-n]` contains it. Thus arbitrary precision is uniformly computable, while exact equality to zero would decide nonhalting. This is why finite machine counts alone do not guarantee a terminating exact frontier algorithm for arbitrary computable-real resource meters.

For finite enumeration, the realization domain must be an independent assumption. Finitely many response kernels do not prevent unbounded physical implementation overhead. The repaired source includes `mathcal M` in the problem tuple and makes every attainable-set/fiber quantifier relative to that finite register. A resource meter determined by a finite operational table is one sufficient instance; arbitrary invisible overhead is excluded only when the registration actually excludes it. Independently, the finite development graph has a finite terminal output image in that register.

## Validation and evidence custody

Command:

`python -m unittest discover -s research/gmi-grand-unification-v1 -p test_grand_gmi_operational_reachability_v1.py -v`

Result: **10 tests passed**. The standalone checker is `grand_gmi_operational_reachability_checks_v1.py`; its output is `GRAND_GMI_OPERATIONAL_REACHABILITY_CORRECTION_RECEIPT_V1.json`. Every numerical comparison uses exact rational arithmetic. The historical operational-closure checker and receipt are unchanged. Their older aggregate green terminal did not check these four invalid implications.

The corrected finite theorem now supplies an explicit constructive algorithm under its declared assumptions. This closes the four stated mathematical gaps at that scope. It does not establish unrestricted realization enumeration or developmental search, empirical model correctness, negative-cost termination, or computable-real exact comparison.

## Primary literature consulted

[Dijkstra, *A Note on Two Problems in Connexion with Graphs* (1959)](https://ir.cwi.nl/pub/9256/9256D.pdf) supplies the classical shortest-path context. The product-cost label closure and constrained-Pareto ordering here are proved directly under the stated hypotheses. [Turing, *On Computable Numbers, with an Application to the Entscheidungsproblem*](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) supplies the computability/undecidability parent boundary; the computable-real zero-test reduction is written explicitly above and in the normative theorem.
