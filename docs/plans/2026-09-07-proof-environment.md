# Checked Proof Environment Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build and qualify a mechanical semantic boundary that can support actual
Lean/Mathlib proof-region reconstruction, retaining the native kernel data model.

**Architecture:** Adopt pinned lean4export/Comparator and checked Lean replay.
Add comprehensive dependency/policy checks, separately registered target data and
fresh proof checking. Python binds artifacts and enforces process/mount boundaries.

**Tech Stack:** Lean4.33.1, pinned Apache-2.0 native parents, Python3.11, existing
bubblewrap/runtime custody helpers; compute and tests on laptop billy.

## Workspace and source discipline

Own worktree: `/home/billy/orion-director-work/20260907/ocm-proof-environment`.
Base9b00cfe, branchcodex/mechanical-proof-environment-20260907. Prior native worktrees
and receipts remain immutable. Source changes stay under the new research package,
its documentation and workflow. Current core/engineering selection is unchanged.
Use `/usr/bin/git`. Independent review precedes final source-frozen commissioning.

## Task 1: native bridge and parent absorption

**Owner/files:** native lane owns `research/proof-environment-v1/parents/`,
`OCMEnvironment/{Types,Packet,Dependencies,Prepare,Check,Main}.lean`, build metadata,
and authored Lean fixture modules under `fixtures/`.

1. Fetch exact official parents: exporter15f6055e299ad5b89345e533cc2192f4cc00f659;
   Comparator3927ad383f208ae977c340a91c48ac9b497d2097. Retain source/license/manifest
   bytes and pin the local dependency, never resolve moving `master` at runtime.
2. Implement parent parser envelope and candidate Expr-table extraction. Validate
   format/toolchain and duplicate/index structure; candidate constMap must be empty.
3. Implement full type/value/opaque/family/rule dependency walking, including
   projection names and implicit literal/primitive requirements. Reject unsafe,
   partial, missing or inconsistent groups with a precise diagnostic.
4. Compute permitted closure from policy plus the target **type**, never its proof.
   A withheld root or structural dependant cannot enter allowed state. Retain paths.
5. Freshly replay the permitted map. Compare resulting identities and generated
   families; retain quotient auxiliaries for comparison even where replay regenerates.
6. Use independent target universes/type and checker-owned theorem name for direct
   `Kernel.Environment.addDeclCore`; audit all reached axioms against pinned policy.
7. Expose stable inspect/prepare/check operations with machine-readable outcomes.
   Keep source environment/private proof bytes out of the fresh checker inputs.
8. Compile and exercise the rich positive fixtures and intended negative controls.
   Preserve actual development failures; diagnose each stage before modification.

Mandatory result distinctions: accepted checked declaration/proof, rejected policy/
candidate, unsupported or incomplete environment, and infrastructure failure.
A parser or subprocess success must never become a proof verdict by itself.

## Task 2: custody, process driver and operating contract

**Owner/files:** root owns `env_inputs.py`, `env_runtime.py`, `env_prepare.py`,
`env_check.py`, `commission.py`, README/CONTRACT/PROTOCOL under the same package.

1. Bind exact parent/native/source/runtime/input bytes and declared output schema.
   Copy create-only stages and preserve independently obtained target records.
2. Reuse the existing isolation/runtime helpers with explicit source-origin checks.
   Export/build and checker profiles have distinct allowed artifacts; never mount
   original source modules, compiled fixture caches or full export into the checker.
3. Dispatch only fixed native operations; validate raw response identity and shape,
   before/after custody and cleanup. Charge preparation and complete process envelopes.
4. Expose a small operation API suitable for the later OCM adapter; do not widen F0
   silently or call these authored checks proof-search/learning results.

## Task 3: independent semantic and process qualification

**Owner/files:** reviewer supplies spec and code review; root owns
`test_environment.py`, `test_custody.py` and the source-frozen result recorder.

1. Positive tests require definitions, composition proof, polymorphism, opaque body,
   custom/mutual inductive and recursor behavior, projections/literals and cold replay.
2. Negative tests require exact type/value dependency paths, alias/helper/instance/
   opaque/inductive exclusions, same-type axiom substitution, target/universe mismatch,
   malformed/missing family, unsafe/partial and metadata/index disagreement.
3. Separately test actual checker/proposer mount profiles using harmless source/cache
   canaries, read-only custody, clean environment and bounded process cleanup.
4. Preserve each valid registered variant so a stale digest cannot fake a semantic
   rejection. Infrastructure/unsupported results cannot pass required positives.
5. Review specification compliance, then code quality. Fix and repeat relevant
   controls only for changed mechanisms or unresolved evidence.
6. Freeze actual sources/inputs/environment; execute one complete native commissioning
   with fixed denominator, exact commands, cost scope and raw evidence. Any failed
   run remains unchanged and receives a separately qualified, diagnosed successor.

## Task 4: integrate and continue the real science

Commit the concrete result with its records; push a PR. Require final-head checks,
all workflow runs and review resolution, including late jobs; guarded squash merge.
Verify live Git bytes against qualified source and retained records. Update the
modular user programme with measured scope, not an unearned F1/learning/novelty claim.

Next run a registered real-corpus semantic coverage audit, then scored masked-proof
reconstruction and explicit method acquisition/held-out transfer with strong adaptive
parents. Authored fixtures enable that experiment; they do not replace its success.
