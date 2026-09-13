# Parents and source custody

The direct scientific parent is the preserved
[PR551 source diagnosis](raw/pr551-grad-audit-20260913/PR551_GRAD_DIAGNOSIS_CORRECTION_7328D5B3_V1.md)
and its [zero-input protocol](raw/pr551-grad-audit-20260913/ZERO_INPUT_ADJOINT_PROTOCOL_V1.md).
The no-outgoing-edge control establishes that a scheduled GRAD node can update
state without a dataflow edge to OUTPUT. The zero-input control then isolates
one incorrect reverse-path attribution. Neither implies a capability gain.

The mathematical parent is reverse-mode AD's multiplication chain rule and
reverse accumulation on a computational DAG, described precisely in
[Baydin et al., JMLR18(153), §3.2](https://jmlr.org/papers/volume18/17-468/17-468.pdf).
Its real-arithmetic rule explains why the adjoint of w*x toward w includes x.
That paper does not certify this VM's fixed-point rounding, clipping, threshold
or surrogate-adjoint choices. We preserve and explicitly delimit those choices.
This repair is an application of established AD, not a new AD theorem.

[Source bindings](SOURCE_BINDINGS_V1.json) identify the old main, original audit,
complete parent manifest and five-file corrected import closure. The changed
active vm.py is byte-identical to its versioned corrected-source copy. The
other four imported modules are unchanged. The active fix is exactly the
parameter-marker relocation, and focused active-runtime tests exercise it.
The full corrected import closure is a source artifact, not newly authored
monolithic code; new helpers and documents are modular.

The parent packet's31 payloads plus manifest are copied byte-for-byte. It
includes its full source/proposal excerpts, two raw controls, protocols,
execution metadata, note and hashes. Old native controls are revalidated
as deterministic source checks, not presented as new executions under their
once-only empirical identity. The new versioned receipt labels both sources
and keeps their outcomes separate.

Finite differences use exact Fraction arithmetic on native forward evaluations
with representable operands; no float tolerances can hide a mismatch. The broad
fixed-point census instead checks the declared rounded/clamped local rule.
These are different references with deliberately different claim ceilings.

A whole-unit manifest binds all corrected-source and historical files. Full
isolated replay anchors its original bytes before executing the checker and
revalidates membership afterward; a self-consistent rehashed manifest cannot
replace the initial authority. Neither this binding nor a successful replay
authenticates a host or expands the registered scientific scope.
