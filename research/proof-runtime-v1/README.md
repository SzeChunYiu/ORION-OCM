# Mechanical proof execution inside OCM

This is the bounded F0 integration successor to the commissioned
[native proposer](../mechanical-proof-v1/README.md). It connects the same finite
mechanical constructor to actual OCM solve, its checker callback, atomic object
admission and persistent evidence revision. It contains no neural learner,
embedding model, language model or neural acquisition path.

The native proposer and Lean checker retain their commissioned isolated processes.
OCM orchestration and the issuer journal run in trusted host Python. This is not
a qualification of an isolated whole-OCM process or arbitrary third-party plugins.

Current implementation status and measured native results are recorded separately
in [QUALIFICATION.md](QUALIFICATION.md). Mocked controls establish protocol
behavior; only a source-bound native receipt can establish actual execution.

## What executes

1. Store the exact F0 descriptor in an instruction-backed KSO procedure. Create
   an unresolved goal with UNKNOWN warrant.
2. Call `OCMRuntime.solve` with a task-local `SolveOperatorIndex`. Its backend
   reads the descriptor from the actual KSO snapshot and invokes the closed worker.
3. The actual solve checker invokes a separate fresh fixed-target Lean check.
   PASS requires a matching session-issued check, not a caller-supplied flag.
4. After ANSWER, verify the exact returned proposal, candidate, task, environment,
   source snapshot and raw artifacts. Prepare a fixed issuer admission plan.
5. Admit checked-run and derived evidence. Admit the run anchor, proof and claim
   together through one `OBJECT_BATCH_ADMITTED_V1` event. Commit their exact event
   identities in the separate issuer journal.
6. Replay ordinary OCM events and verify issuer/artifact custody before reporting
   authenticated formal support. Rebind host callbacks explicitly for new solving.

## Read next

- [Support and recovery contract](CONTRACT.md)
- [Qualification and costs](QUALIFICATION.md)
- [Corpus inventory boundary](../proof-corpus-v1/README.md)

## Operation

Run tests and native qualification on Linux laptop billy, not the Mac.
The portable controls mock native boundaries and need only pytest and OCM source:

```sh
PYTHONPATH=src python -B -m pytest research/proof-runtime-v1 \
  --ignore=research/proof-runtime-v1/records -q
```

The full engineering environment is declared in `requirements-engineering.txt`.
It includes the symbolic dependencies required by existing text integration tests;
installing all historical language/generation donor requirements is unnecessary.

The fixed descriptor permits the original registered signatures, their Eq-only
subset and reduced search limits. It refuses changed goals or constant meanings.
No FLT route, theorem-specific auxiliary decomposition or learned method is added.

Finite application closure and ordinary checked persistence remain conventional
parents. This slice supplies no evidence of useful learning, FLT reconstruction,
active-subspace scaling, LLM parity, cost superiority or OCM novelty.
