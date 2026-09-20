# Constructive synthesis repair — #1068, round F

Parent repair branch head: 881d453c0002e1af01a10010c3cad7c4b12fafb9.
Round F will merge only after round E merges and this branch reconciles main.
Historical R7/R8 receipts remain unchanged; they do not establish blind recovery.

## Disclosure before successor implementation

A read-only exploratory in-memory calculation already observed that the grammar
x | y | NAND(t,t) can cover the 16 binary Boolean truth tables. That preview is
not preregistered empirical evidence. This commit freezes successor proof,
implementation and falsification requirements before their repository creation.
The result is exact mathematics plus a finite executable certificate, not a
confirmatory generalization experiment or discovery of a new Boolean basis.

## Frozen construction and proof requirements

Use the single recursive grammar x | y | NAND(t,t), without family macros or
prewritten candidate solutions. Semantic dynamic programming may identify
expressions with the same complete binary truth table. Every retained witness
must actually execute, and its cost must be its measured AST node count.

Prove a certificate theorem: terminal lower bounds plus all composition
inequalities imply, by structural induction, a cost lower bound for every AST.
If every semantic value has a witness attaining its bound, minima are exact
over the infinite grammar. Check the complete four-input truth table for every
witness and every pairwise certificate inequality independently.

Compile to a distinct stack language with input loads and NAND. Prove semantic
preservation for any initial stack and arbitrary expressions, and equality of
AST node count with emitted instruction count. Reject invalid opcodes and
stack underflow. Check input relabeling, negative grammars, changed costs,
mutated witnesses, truncated code, premature search termination and certificate
corruption. Compare an independent cost-layer search/oracle.

State the uniform operational simulation requirements for transporting
attainability across digital algorithm families. Distinguish forward inclusion
from equality, finite progress from possible interpreter divergence, exact
from approximate operations, and representation from architecture discovery.
State a robust score-interval winner condition with all lifecycle costs included
in its premises, and UNKNOWN when a unique winner is not certified.

## Authority and evidence

Parent-owned Boolean completeness and compiler-correctness methods are credited.
Grammar, inputs, Boolean semantics, equality oracle, scalar costs and search
order are explicit assumptions. No neural system participates in cognition.
No claim of all known intelligence families, efficient general learning,
real-scale performance or assumption-free cognition is permitted.

Kernel-check feasible central statements in Lean 4.19.0. Record paper-only
results separately. Independent internal review, normal/optimized replay,
exact-head CI and pre-merge success are required. Preserve all 222 stable
requirements and stale dependencies in an additive successor. Use an
ancestry-preserving merge to retain this freeze.
