# F1 corpus readiness — metadata only

2026-09-07; inspected on billy-laptop. No checkout, clone, build, export,
proof execution, study, or scored-theorem selection was performed. No withheld
solution body or route document was opened. Existing lexical records remain
history; final environment qualification still precedes semantic coverage.

## Exact available source and inventory

- Bare source: `/home/billy/orion-director-work/20260907/proof-corpus-source-aa2d8b3.git`.
- Commit: `aa2d8b34692b16c70f699536de0d8e75b9a3e9ef`.
- Tree: `8bb1c43c8f26f1c127591dddeffdead2b5094eb7`.
- Successful lexical inventory:
  `/home/billy/orion-director-work/20260907/proof-corpus-inventory-revival-20260907T010338Z/`.
  `REPORT.json` records 29,511 wrappers, 29,511 solutions and 1,456 context files,
  all accounted; `GRAPH.json` has 29,511 nodes and 106,853 lexical import edges.
  It explicitly records semantic dependencies unverified and no kernel/solver run.
- Inventory source binding `CORPUS_SOURCE.json` SHA256:
  `de911c6ef05adb9df9017d7aedd21bcfeb7376e99348af46fa4b17b14e2cd3dd`.
- Graph file SHA256: `f74f7391cd36b631641c7a8207d949f49e0e42459a8ca94f87852e91b4cc82a4`.
  Preserve its evaluator-only boundary: retained wrapper context may contain proofs.

## Pinned build setup, read from Git blobs

`lean-toolchain` declares `leanprover/lean4:v4.33.1`.
`lakefile.lean` declares package `flt_e2e`, Mathlib
`db584cd6d46c92f209a44c0f1c829460d327499d`, libraries P2M/Definitions/Theorems
with all submodules, and default root FinalCheck. Do not invoke that global
root merely to commission one bounded semantic-coverage batch.

Registered Lean options: `autoImplicit=false`, `maxHeartbeats=4000000`,
`synthInstance.maxHeartbeats=400000`,
`backward.isDefEq.respectTransparency.types=false`.

The lockfile is version 1.2.0, `.lake/packages`, `fixedToolchain=false`.
Therefore qualify the exact executable separately and retain all resolved `rev`
values; inherited `inputRev=main/master` fields are not permission to update.

| Package | Resolved revision |
|---|---|
| mathlib | `db584cd6d46c92f209a44c0f1c829460d327499d` |
| plausible | `b7eb3304aeae834b12dda98993a37f6a41f6f0bb` |
| LeanSearchClient | `5f4d51b81cbd3f6b32b156bfad9056621a040404` |
| importGraph | `16f02aa7642864af59f1ff0e384a015994db9118` |
| proofwidgets | `4be2e3d5087eeb272cf5a8853b8f9dd025ef5957` |
| aesop | `3448c0bcc5ce01b2d1546e483ec3620e32df3d0e` |
| Qq | `92c15be17b7caf78c2ad767ec40f89052d908d81` |
| batteries | `4488d40d070b9700d4d5a6aa342f0d40c31b2a2d` |
| Cli | `6130a47896ce867c6a4a55373441e59e565bad0f` |

Exact metadata SHA256:
- `lean-toolchain`: `3aac669c7a910ec2389f4e4f921b605adf6ebf2d1e0c9b9cd0be4d33f3f5db71`.
- `lakefile.lean`: `d8ba763b04133c72e1182738f530cdd48c9b676dfb210ed551995287f319bd29`.
- `lake-manifest.json`: `435fe2ab2550e2b82c0a93fd421c96d197d6dd55bc739481e2a4a07e04b979bf`.

## Local reuse and limits

- Exact Lean 4.33.1 distribution exists at
  `/home/billy/orion-director-work/20260906/f0-development-runtime-v4/lean-4.33.1-linux/`.
  Adjacent `runtime-manifest.json` SHA:
  `93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894`.
  Its `lib/lean` contains 2,485 `.olean` files; these are release libraries, not Mathlib.
- New pinned parent exporter and generic checker development builds exist at
  `/home/billy/orion-director-work/20260907/ocm-proof-environment/research/proof-environment-v1/.lake/build/bin/`:
  `ocm_export` is evaluator tooling; `ocm_environment` is the separate checker.
  Their corpus load path and real-corpus coverage remain to be commissioned.
- Existing `/home/billy/orion-lean/mathlib4` is commit
  `4bbdccd9c5f862bf90ff12f0a9e2c8be032b9a84`, tree
  `78079b1102be3635b1c851559101191f9bb4037e`, Lean 4.14.0.
  Its build has 5,387 `.olean` files (~3.79 GB). These cannot be reused as
  Lean 4.33.1 artifacts. The required Mathlib commit is absent from this object store.
- No matching Mathlib source/cache was found in the scoped director-work tree,
  relevant ORION/OCM host trees, or conventional `.cache/mathlib*` locations.
  Search covered director-work, orion-lean, ocm-verify, orion-ci,
  orion-paper-verify, ORION-paper and rakl-lean-p1 (metadata walks only).
  This is not a global filesystem absence claim. The acquired corpus is bare;
  it has no local corpus `.lake/build` tree in that store.
- Upstream README:71–80 reports no matching prebuilt Mathlib for this toolchain,
  source compilation, ~67 GB build storage plus ~220 GB generated C, and peaks
  of 153 GB for full build / 230 GB for full comparator. These are author reports,
  not runs reproduced here. Observed laptop MemTotal is 32,520,568 kB; available
  work-volume space was 301,561,298,944 bytes. Full campaign compute is unqualified.

## Smallest honest semantic-coverage entry

1. Finish isolated environment commissioning first. Then create a separate,
   evaluator-only checkout from the verified existing corpus objects. Acquire
   exactly the nine locked package revisions and bind source/build identities;
   preserve failed acquisition/build attempts and all costs.
2. Freeze the complete lexical population and a deterministic hash ordering
   derived only from existing source IDs and a preregistered seed. Register a
   bounded initial chunk and continuation rule before semantic outcomes are known.
   Do not name a convenient theorem, filter by proof size/success, or replace a
   failed row with an easier one. This note selects no rows or scored targets.
3. Build the selected rows' required modules in dependency order, recording the
   actual transitive load/build closure. Selection order and build scheduling are
   separate. A small row batch can still require most of Mathlib. Charge cold
   Mathlib/import construction, failed modules, caching,
   parsing/export, replay, checking, storage and cleanup; retain every assigned row.
4. Use the full original environment only on the evaluator side. Register the
   intended elaborated target type and ordered universes independently of prepare;
   bind primitive/assumption headers separately. Export selected declaration
   closure through the parent format, prepare a fresh permitted packet, then
   check a retained reference proof only as a transport/replay coverage control.
   Compilation success is not fresh-environment or intended-statement certification.
5. Record PREPARED/KERNEL_PASS/REJECTED/CANNOT_CHECK at their actual stages, with
   closure size, bytes and resources. One small chunk establishes only its declared
   coverage; continue the frozen population rather than extrapolating generality.
6. Keep source, compiled target modules, reference solutions and private inventory
   out of the checker/proposer mounts. The corpus is disclosed upstream AI-authored
   reference material (README:98–101), not mechanically acquired OCM knowledge.
   LeanSearchClient in a build lockfile does not authorize a retrieval/model call.
   A future proposer needs a separately redacted task profile and no-neural closure.

Evidence commands: `/usr/bin/git --git-dir=<bare> show <pin>:<metadata>`, root
`ls-tree`, `rev-parse <pin>^{tree}`, and bounded directory/artifact metadata walks.
No `FinalCheck.lean`, PROOF-PATH, or solution proof source was opened.
