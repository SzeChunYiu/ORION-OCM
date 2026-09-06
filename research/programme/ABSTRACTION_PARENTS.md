# Additional parents for the representation programme

[Core programme](CORE.md) · [main parent matrix](PARENTS.md).

The atlas and local-execution work should also absorb the established theory of abstract interpretation and counterexample-guided refinement. These are mechanisms to reuse, not merely related vocabulary.

## Completeness is relative to semantic operations

Giacobazzi, Ranzato and Scozzari's [Making Abstract Interpretations Complete, JACM 2000](https://www.sci.unich.it/~scozzari/paper/JACM00.pdf) distinguishes sound approximation from completeness for specified operations and fixed points. It constructs complete domain extensions or restrictions under stated assumptions, and identifies cases where the desired least extension need not exist.

OCM application: bind each sufficiency certificate to the actual operation/query family, abstraction and concrete semantics. When a new operator is learned, recheck completeness against that operator. A statement that compression is "good enough for current operators" is not, by itself, a new theoretical contribution.

A useful new experiment would combine a specific incremental certificate-maintenance algorithm with evidence revision and an expanding operator library, then compare it with an equally equipped abstract-interpretation parent. Prove the declared interface and assumptions before claiming a general certificate theorem. This is a proposed OCM mapping, not a claim established by the cited paper.

## Refinement should answer an observed precision failure

The [original counterexample-guided abstraction refinement work](https://www.cs.cmu.edu/~emc/papers/Technical%20Reports/Counterexample-guided%20Abstraction%20Refinement.pdf) is a direct parent for checking an abstraction, detecting a spurious counterexample and refining it. OCM should preserve the distinction between an actual counterexample and failure caused by an insufficient representation.

For OCM, the measurable question is whether evidence- and operator-aware certificate reuse reduces complete future work compared with a faithful refinement parent. Renaming a familiar refinement loop or adding an epistemic label is not enough.

## Explicit synthesis diagnostic interface

The current worker parses a command and then invokes it. This separation is exposed by the [cvc5 InputParser interface](https://cvc5.github.io/docs/latest/api/cpp/classes/inputparser.html). The diagnostic records those intervals without changing solver options. The installed version and exact source bytes remain the authority for the actual experiment; current documentation is an interface reference.

Do not infer an internal search/reconstruction cause from a single unfinished `check-synth` invocation. Any subsequent solver-option or grammar change is a new, separately registered intervention and must be applied to the matched parent where appropriate.
