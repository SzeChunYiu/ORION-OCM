# Primary parents, implementation scope and cost ledger

## Parent subtraction before the mechanism

| Parent | What is inherited | What is specialized here |
|---|---|---|
| [Wolf, Cubitt and Pérez-García, §2.1 Theorem 1/Lemma 1 and §§2.5,2.7](https://arxiv.org/pdf/1111.5425) | Polynomial descriptions of finite-dimensional quantum objects and exact decidability via real-closed fields. | Apply that established method to the repository's finite relational interface; bound the dimension search by the sender-input count. This is a direct application, not new quantum decidability. |
| [Jovanović and de Moura, §2 and Theorem 1](https://dddejan.github.io/papers/jovanovic-ijcar2012.pdf) | A complete nonlinear-real decision procedure and algebraic satisfying assignments. | Supplies the effective decision/sample-point parent. No replacement solver is authored or executed here. |
| [Watrous, Chapter 2, Theorem 2.42 and Corollary 2.43](https://cs.uwaterloo.ca/~watrous/TQI/TQI.2.pdf) | Density states, POVMs, isometries and finite Naimark dilation. | Exhibit V_y from the exact feasibility factors and account for dimension d times the outcome count. |
| [Stahlke, Theorem 12 and function-evaluation example](https://arxiv.org/pdf/1405.5254) | Orthogonal rank for the exact-function quantum communication sector. | Retain the function lower-bound parent and its graph-specific scope; do not replace a general relation by pairwise conflicts. |
| [Repository quantum §4.4 and its boundary audit](raw/QUANTUM_PROCESS_INSTANTIATION_THEOREM_V1.md) | Full density/POVM feasibility and the existing rational 14-ray separation. | Complete ideal protocol-class coverage, pure-state support reduction and finite effective dimension selection. |

The contribution is a scoped constructive bridge and independently checked
application. No new parent decision theorem, Naimark theorem, quantum
communication separation, general lower bound or experimental advantage is
claimed. UMA, RQR and the finite-data model-transfer extension address different
interfaces and remain independent. The local source snapshot is d44c129f;
[exact parent bindings](SOURCE_PARENTS_V1.json) preserve its original files.

## Costs and exclusions

Only transmitted Hilbert dimension d, or ceil(log2 d) padded qubits, is minimized.
The canonical receiver dilation uses an outcome register of dimension |A|,
giving joint dimension d|A|; that construction need not minimize local workspace.
The algebraic preparation and readout descriptions, classical input interfaces,
selection logic, private ancillas, gate sequences, synthesis workspace and
bit-arithmetic work are not included in transmitted dimension.

The general finite search makes at most |X| calls to an inherited exact decision
procedure. This counts calls, not their time or memory. Its polynomial system
has 2d|X|+2d²|Y||A| real variables and quadratic equations. Algebraic witness
description lengths and arithmetic precision can be large. A finite exact
description is not a hardware precision or cost guarantee.

The supplied verifier operates on **real rational witness data**: a nonzero
rational ray denotes its mathematically normalized ket, and factors define
positive measurement effects. Normalization may involve algebraic square roots.
It verifies ray norms, all promised forbidden-output probabilities, completeness
and the actual stacked isometry. It is not a solver for all complex algebraic
protocols. Mixed-state controls use explicit positive rational convex mixtures,
so positivity is certified by construction; no unchecked eigenvalue tolerance
is used. Pure support selection is tested by comparing both distributions and
adequacy, since those claims differ.

The 343-task classical parent is exhaustive over encoders and decoder
compatibility at its finite scope. The independent quantum lower certificates
are specific analytic proofs, not floating infeasibility judgments. The graph
parent is finite exhaustive backtracking with a complete conflict check.

No ecology, candidate benchmark, priming, timing or hardware measurements are
part of this study. Verification work is paid by running the stated exact
checks; its throughput is not a quantum deployment comparison.

## Load-bearing conditions challenged by controls

- Normalize every transmitted state; a zero vector must not trivialize all
  forbidden-output constraints.
- Enforce measurement completeness; all-zero effects otherwise falsely certify
  every task by discarding all outcome probability.
- Preserve the owner and timing of x/y information; random-access changes when
  Alice is allowed to know Bob's later index.
- Include every promised pair and every forbidden action; incomplete coverage
  must not manufacture adequacy.
- Require zero forbidden probability exactly; tiny rational leakage is still an
  error, and nonzero-error criteria need a different theorem.
- Choose pure states inside the original mixed-state support. This can change
  allowed-output probabilities while retaining adequacy.
- Fix any shared classical seed using finite zero-error coverage. Independently
  averaging the sender states and receiver effects can destroy correlations;
  the exact binary identity control drops success from one to one half.
- Keep the full acceptable-action sets, including higher-order intersections.
- Exclude pre-shared entanglement and postselection. The classical upper bound
  remains feasible with extra assistance, but the unassisted lower comparisons
  and coverage class must not silently be reused.
