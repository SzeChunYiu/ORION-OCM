# FLT KSO v1 — prerequisite microscope, not a full FLT solver

Owners: #38 / #62; instrumentation #115. **#46 remains LOCKED.**
Base: `d53d0082bfdada811a565253f3e18680f91e878a`.
Registration: issue #62, comment 5562223172, before implementation/outcomes.
Historical `research/proof-replay-v1/` is not edited or repinned.

## Executable scope

`native.py` is a bounded symbolic equality-path constructor using hypothesis
references, reflexivity, symmetry and transitivity. It emits an inspectable AST,
per-edge events, canonical endpoint states and full cold adjacency-index counts.
It does not read files, call a model, or receive proof text. The exact same
constructor outside OCM is the conventional construction-sufficiency parent.
This is deliberately not a novel or superior proof-search algorithm.

`bridge.py` stores an OPEN obligation as a `goal` in the actual `OCMRuntime`,
retrieves the statement from that field, uses the existing `SolveOperatorIndex`
and canonical `runtime.solve`, checks the candidate, records the exact attempt
through the existing evidence/event ledger, persists and reloads that runtime.
The LIVE goal warrants only the existence of the request, **not its truth**.
Its mathematical truth profile is the existing partial/UNKNOWN warrant.

The current general admission gate refuses a claim with no exhibited warrant.
We do not bypass that gate, fabricate an axiom or create a separate truth store.
**Theorem admission is deliberately disabled in this tranche.** Canonical
commitment here is a checked candidate-program output, not admission of a
mathematical theorem/support cone. `new_theorems_admitted = 0`. Arbitrary checked
proof admission, conjunctive/alternative proof support and support withdrawal
remain next qualification boundaries, not completed features.

`kernel.py` accepts only this closed AST, renders the source itself and checks
it with a fresh extracted Lean 4.33.1 release. Both original and copied archive
must match the release's published SHA-256 and byte size. It clears inherited
search/tool paths, uses a fresh source directory, records process outputs/exits,
kills the process group on timeout, and requires an empty axiom list. Arbitrary
Lean source, `sorry`, injected axioms and `native_decide` are not in the grammar.
The pinned full Mathlib environment is recorded but **not prepared**; R1 uses
only Lean's standard library. Unavailable/mismatched tools fail closed.

`REGISTRY.json` fixes one R1 task, grammar, budget and criterion before execution.
`run.py` executes the unchanged R0 control first, then the actual OCM arm and
matched equality-constructor parent; every invocation requires a fresh output
path and binds the exact Git head/tree and all tranche source bytes. A positive
R1 terminal establishes only construction and kernel checking of this statement.
It establishes no useful acquisition, general theorem solving or FLT result.

## Evaluator inventory and sealing boundary

`graph.py` extracts cited wrapper-module dependencies from solution imports,
checks wrapper/solution pairing, coverage, unresolved references and acyclicity.
A lexer handles nested comments, quoted material and balanced multiline theorem
headers. Unsupported forms are refusals. Extracted **textual signatures are not
elaborated types**: wrapper prefixes include environment-altering attributes and
imports, so deleting a proof body does not establish a safe challenge.

`audit.py` binds a clean evaluator checkout to the frozen Anthropic commit and
records whole-corpus work, exact source/proof/signature hashes and a private DAG
inventory. No proof text or original topology enters a public solver package.
`seal.py` can currently publish only the closed equality fragment, with no Lean
imports. General Anthropic signature export refuses with
`CANNOT_CHECK_ELABORATED_TYPE_AND_DEFINITION_CLOSURE`. It must not be advertised
as a completed R2/R3 challenge constructor.

An actual bubblewrap namespace probe tries to read a known-existing private
file while requiring a public-file positive control. Missing/restricted sandbox
support is CANNOT_CHECK. Even a successful probe proves only that probe scope:
**no R2/R3 solver process is implemented or certified by it**. No `html/` is
mounted or copied into the public package. The evaluator checkout is acquired
only after the R1 mechanism run in the engineering workflow.

## Run

```sh
PYTHONPATH=src python -m unittest discover -s research/flt-kso-v1 -p 'test_*.py' -v
PYTHONPATH=src python research/flt-kso-v1/run.py \
  --control-archive /absolute/path/lean-4.19.0-linux.tar.zst \
  --archive /absolute/path/lean-4.33.1-linux.tar.zst --out /new/output/directory
PYTHONPATH=src python research/flt-kso-v1/audit.py \
  --source /clean/frozen/anthropic/checkout --out /new/evaluator/output
```

No scientific row is written over an old row. CI artifacts bind execution to
source, but are not automatically an authenticated external adoption warrant.
Current-head full engineering tests and M1–M12 receipt checks are still required
before merging; any source drift requires a new qualification.

## Explicit missing gates

R2/R3 execution, intermediate generation, proof-method/schema learning,
causal reuse after a fresh-process restart, removal ablation, failure-memory
utility, distractor scaling, strong general-DAG parent subtraction, component
proofs and R6/R7/R8 are **NOT EXECUTED**. Restarting the existing runtime is not
learned-method reuse. Whole-field canonical navigation remains visible; `k`
and `k/N` are unknown, not fabricated as sparse. CPU/RSS/energy and complete
OS-level IO are unmeasured where not explicitly captured. The inherited
`ResourceVector` and operator-index work are retained alongside scoped new
constructor counters; checker-call counts are distinct from generic runtime
verification counters.
