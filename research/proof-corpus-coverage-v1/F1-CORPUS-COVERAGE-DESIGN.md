# F1 real-corpus coverage — prospective design

2026-09-07. Read first; operational details are in
[EXECUTION](F1-CORPUS-COVERAGE-EXECUTION.md), source metadata in
[READINESS](F1-CORPUS-READINESS.md). No rows have been selected, built, exported,
replayed or scored by this design task. This is a bounded next experiment after
the current authored 47-control environment evidence is integrated.

## Question and claim boundary

Can the qualified parent-format bridge transport, reconstruct and kernel-check
four mechanically assigned declarations from the registered real corpus,
including their original exposed reference support, within a declared resource
envelope? The experiment measures semantic **coverage**, not proof search,
missing-proof reconstruction, learning, transfer, FLT achievement or novelty.

The reference solution is explicitly available to the evaluator. Its declaration
and proof dependencies may enter the fresh checking environment and must appear
in the receipt. Passing cannot establish that OCM discovered that solution.
The original target wrapper declaration is excluded; its independently registered
type and ordered universes remain the checking obligation. A candidate that uses
the exposed original solution is an honest reference-replay baseline.

This refines READINESS's shorthand about keeping reference solutions out of the
checker: original source/compiled modules stay outside, but this coverage arm
deliberately permits registered, freshly checked reference-support declarations.
No resulting packet is qualified as a masked learner task.

## Population and prospective assignment

Freeze the entire population of **29,511** wrapper/solution pairs at corpus commit
`aa2d8b34692b16c70f699536de0d8e75b9a3e9ef`, tree
`8bb1c43c8f26f1c127591dddeffdead2b5094eb7`.
Inventory directory on billy-laptop:
`/home/billy/orion-director-work/20260907/proof-corpus-inventory-revival-20260907T010338Z/`.

Bind raw inventory bytes, not only their internal summaries:

| File | SHA256 |
|---|---|
| CORPUS_SOURCE.json | `de911c6ef05adb9df9017d7aedd21bcfeb7376e99348af46fa4b17b14e2cd3dd` |
| GRAPH.json | `f74f7391cd36b631641c7a8207d949f49e0e42459a8ca94f87852e91b4cc82a4` |
| SOLUTIONS.json | `dcde5c01c7f256a344d0f58f4e2d932dca2997bd28851caccb83ba648b01c9bb` |

Use all GRAPH.nodes keys, verifying exact pair identities against the source
inventory before dispatch. A key maps to `Theorems/Thm_<key>.lean` and
`P2M/Sol/S_<key>.lean`; their source hashes must agree with the retained graph.
The existing 106,853-edge graph is lexical, not a semantic dependency certificate.

Ordering is fixed now, before compiling or observing semantic outcomes:

```text
prefix = UTF8("ocm.f1.semantic-coverage.v1") || 0x00
d(key) = SHA256(prefix || ASCII(corpus_commit) || 0x00 || UTF8(key))
order = ascending (digest bytes, UTF8(key))
assigned = order[0:4]
```

No IDs or hashes for this ordering are computed in this document task. The
registration implementation must bind the complete ordered list, four assigned
IDs, source hashes, ordering code and this design before execution. Do not rank
by statement/proof length, imports, topic, prior success or estimated difficulty.
No failed row is replaced. Build scheduling may follow dependencies; it cannot
change assignment. Retain all 29,511 entries and a continuation cursor of 4.
Later batches require new prospective records; they never overwrite these four.

## Four complete row records

Each assigned row declares acquisition, build, target association, export,
prepare/replay and reference checking before any dispatch. Record failures at the
first failing stage and every dependent stage as NOT_RUN with its cause. Shared
initialization failure still produces four assigned row records and preserves the
population. Count actual reached checks separately from the four-row denominator.

Record the wrapper and reference solution IDs/hashes, original declaration names,
proof-expression identity, direct and transitive dependencies, prepared membership,
exclusions with paths, reached axioms, packet sizes, process evidence and costs.
Keep original reference support distinguishable from prerequisite theorem support.
Compile success, successful parsing and PREPARED are not KERNEL_PASS.

## Generic semantic entry

1. Build each assigned wrapper module from the exact original source and locked
   dependencies. Retain actual compiler setup/import/plugin metadata. The lexical
   graph is only a scheduling aid; elaborated dependencies are authoritative.
2. A separate evaluator adapter associates the registered wrapper record with its
   exact elaborated theorem using declaration identity and source association.
   Qualify namespace/renaming/ambiguous-association controls first. Do not guess a
   constant from its leaf name or pretty-printed type. Refuse unresolvable matches.
3. Independently capture and bind its target type and ordered universe parameters
   before prepare reads a source packet; retain that original goal packet. Bind
   the exact original reference proof Expr independently as the coverage candidate.
4. Export complete parent-format support from the evaluator environment. Include
   type/value/opaque/projection/literal dependencies and full inductive/recursor
   families. Register allowed support roots and forbid the original wrapper target.
   Never thin imports, replace proofs, erase tactics or alter source to make a row fit.
5. Use the qualified prepare and fresh checker through their separate input
   profiles. The checker receives only the permitted packet, registered goal,
   registration, independent primitives and expression-only candidate; no full
   corpus, compiled target modules, Lean elaborator or reference source mounts.
6. Verify exact target/universes, normalized declaration identities, regenerated
   family membership and actual transitive axiom closure under the existing
   environment contract. Retain parent-normalization and raw-byte identities.

The independently pinned assumption registry permits only `propext`,
`Classical.choice`, and `Quot.sound`, with exact Lean 4.33.1 headers and primitive
identities. Report the reached subset. `sorryAx`, unregistered assumptions,
unsafe/partial declarations and unchecked native shortcuts receive no exception.
An unsupported form is CANNOT_CHECK, not silently omitted or a false theorem.
The current authored controls do not yet establish real-corpus adapter coverage.

## Information and no-neural boundaries

The corpus README identifies its Lean source as upstream AI-produced, on human
Lean/Mathlib infrastructure. Preserve that provenance and source identity. These
proofs are evaluator reference givens, not OCM-acquired structures; their upstream
acquisition cost is unknown and excluded only with an explicit statement.

Acquisition may fetch pinned source/tooling. Compilation, elaboration and export
must then run with outbound network disabled, no credentials or host sockets,
and a separately qualified build/import/dispatch profile. Source tactics and
`run_cmd` can execute code: a lockfile and a successful offline build alone do not
prove neural-free computation. Review actual executable/plugin/import closure,
refuse neural evaluation and undeclared dispatch, and retain denial controls.
LeanSearchClient's presence is recorded, never relabelled as proof of absence or
permission to call a model. No fallback to online retrieval/teacher is allowed.

The generic kernel checker retains its narrower source-free profile. Neither
profile qualifies the whole OCM host as neural-free. No learner runs in this arm.
Future reconstruction needs a separate qualified masking transformation removing
reference solution roots, registered direct/equivalent aliases and dependent
helpers/artifacts, retaining the target obligation and exposing no private route.
Do not claim a decision procedure excluding every logically equivalent theorem.

## Interpretation and continuation

Report each row and the full denominator even if zero checks are reached.
Distinguish acquisition/build/export limitations from kernel rejection and
resource refusal. Four passes establish four exposed coverage cases, not a
population success rate or a performance speedup. Diagnose a failing stage before
a separately frozen revival; keep its original failure and any repeat cost.
Only a later masked proposer experiment can address proof reconstruction, and
only matched post-experience arms can address learned methods or lifetime benefit.
