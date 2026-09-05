# Heterogeneous Lifetime Benchmark V0 — frozen topology, unbound protected instances

Status: **design-frozen V0 / protected-instance binding blocked by N3 and N5**.

This is one lifetime, not a bag of reset benchmarks. A principal arm keeps one runtime identity and its allowed persistent state through every phase. Reset behavior exists only as an ablation.

## Task-family graph

Every concrete task instance will bind to one of these edge types before protected outcomes are read.

- `RELATED`: a registered reusable method/operator/substructure should help.
- `UNRELATED`: no transfer benefit is predicted.
- `ADAPTER_REQUIRED`: invariant structure is reusable but a target-specific adapter must be acquired.
- `HARMFUL_LOOKALIKE`: surface/semantic similarity exists but reuse should be refused or specialized.
- `SUPPORT_DEPENDENT`: competence depends on a support item scheduled for later revocation.
- `ALTERNATE_SUPPORTED`: one support is removed but another registered minimal support remains.
- `DRIFTED`: previously valid method/source becomes stale under a versioned environment change.

The benchmark must contain every type. A task order containing only `RELATED` edges is invalid.

## Phases and prerequisites

| Phase | Source milestone | Required event |
|---|---|---|
| L1 | N1/N2 | acquire open-vocabulary lexemes/constructions; related and harmful-lookalike construction pairs |
| L2 | N3 | persistent open-domain source-backed dialogue; source withdrawal and alternate support |
| M1 | N4 | learn/reuse proof operators or proof skeletons under exact verification |
| M2 | N5 | related/unrelated exact math problem families and method transfer |
| X | cross-family | compose at least two previously acquired operators in a new task |
| R | revision | revoke/correct an earlier support and inspect exact dependency cone/restoration |
| D | drift | change one policy/API/convention and measure stale use + adaptation |

N6 is not required for the core lifetime-scaling claim; no open-problem success can be a dependency of the result.

## Orders

The confirmatory suite uses 24 independent lifetime units: four frozen seeds/instance sets within each of six order strata.

1. related-first;
2. unrelated-first;
3. interleaved related/unrelated;
4. reverse-domain order;
5. harmful-transfer-trap early;
6. revocation/drift early.

The same 24 task-stream identities are executed by all matched arms. Order is not tuned per arm.

## Growth scales

For H2, each lifetime contains fixed-target probes at persistent-state scales approximately `1x`, `3x`, `10x`, `30x`. Growth items must be outcome-neutral distractor/relevant-state additions whose identities and relation to the target query are frozen by construction. The actual `N` reached is reported; a run is not relabeled to a nicer scale after the fact.

## Required information manifest per task

Each node binds:

- task/generator/version/hash;
- train/dev/protected role;
- visible source/evidence ids;
- labels/annotations/meaning graphs;
- lessons/demonstrations/interactions;
- tool/verifier/network permissions;
- persistent state inherited at entry;
- declared reusable parent operators available at entry;
- threshold/grader;
- resource limits.

## Revocation worlds

At least one support graph per lifetime is oracle-known and contains:

- a single-support dependent chain;
- a branch with alternate minimal support;
- a large unrelated region;
- restoration/relearning path.

The exact expected changed set is hidden from the mechanism arm but committed before execution.

## Current binding gate

The graph/order/scales above are frozen now. Concrete protected hashes **cannot** be honestly frozen because N3 and N5 are currently locked in roadmap #42. Until those mechanisms and their protected generators exist, the benchmark terminal is:

`CANNOT_CHECK_PROTECTED_TASK_BINDING_N3_N5_LOCKED`

Historical M12 V4 streams remain historical calibration. They are not silently relabeled as this benchmark.
