# Primary parents and scope subtraction

[Paturi and Saks, On Threshold Circuits for Parity (FOCS1990), §2 and §3.1,
Lemmas1–2](https://cseweb.ucsd.edu/~paturi/myPapers/pubs/PaturiSaks_1990_focs.pdf)
supply the mature threshold-circuit framework and connect parity, input
outdegree and hidden hyperplanes. Their asymptotic edge lower bound has
weight assumptions. We do not transplant it into a three-input opcode bound.
The finite midpoint and unate-incidence proofs here are explicit elementary
specializations; no new general circuit lower bound is claimed.

[Uchizawa, Takimoto and Nishizeki, Size–energy tradeoffs for unate circuits
computing symmetric Boolean functions (2011)](https://doi.org/10.1016/j.tcs.2010.11.022)
treat threshold gates as unate gates and distinguish gate count from energy.
Only that mechanism and distinction are used here; no energy theorem is
inferred from candidate-frame opcode counts.

[CPython3.12 dis documentation](https://docs.python.org/3.12/library/dis.html)
defines disassembly, nonspecialized/adaptive views and cache handling, and
explicitly warns that bytecode changes across releases.
[The pinned v3.12.3 compiler](https://github.com/python/cpython/blob/v3.12.3/Python/compile.c#L5687)
visits both binary-expression operands then emits the binary operation;
[its name branch](https://github.com/python/cpython/blob/v3.12.3/Python/compile.c#L5817)
uses name-load/store compilation. These parents support the flat-syntax
instruction accounting. The theorem states the exact layout as a premise,
and executable guards reject a native layout that disagrees.

The historical #557 theorem/checker/receipt/test/ledger are archived unchanged
and bound by SOURCE_PARENTS_V1.json. The omission and rendering controls were
first checked directly against that exact source before the repair.
The executable replacement uses an independent finite output-grid enumeration;
it does not rerun the old expensive whole-grammar search.

The constructive result is an attained scalar optimum for a declared
rendering class. Its shape restriction is a scope choice, not a discovered
definition of all neural implementations. It covers unbounded coefficient
magnitudes and unit counts by inequalities, not by bounded saturation.
The old output-grid observations are not promoted to complete coverage.

A normal and optimized portable receipt reports the contract and complete
finite evidence without an interpreter-version field. This is explicit:
native validation separately binds full version, executable bytes and output.
No raw historical receipt is projected, overwritten or made current by
omitting fields. The portable receipt never attests a historical host.

Each reported opcode is an abstract emitted instruction in the candidate
frame. Integer arithmetic bit complexity, C and Python callee work, source
description, synthesis, acquisition, reset, memory, time, energy and hardware
are separate costs. No ecology measurement or runtime timing experiment is
run. Exact evaluation of the eight Boolean inputs checks semantics only.

[The pinned partial implementation](https://github.com/python/cpython/blob/v3.12.3/Modules/_functoolsmodule.c#L195)
forwards into its stored callable. An outer object without __code__ therefore
does not establish that its descendants contain no Python computation.
