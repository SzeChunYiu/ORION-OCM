# Allocation and corpus audit

The source is ready for a separate custody release. This audit establishes the
recorded corpus lineage and allocation boundaries; it does not authorize a release.

Read [FINDINGS.md](FINDINGS.md), then the exact [draft attestation](ATTESTATION-DRAFT.json)
and [source/index lineage](LINEAGE.json). [SOURCE-METADATA.json](SOURCE-METADATA.json)
binds 27 metadata/source records; [INVENTORY.json](INVENTORY.json) records discovery scope.

The two Metamath censuses explicitly allocated no train/development/hidden split.
Their 6/6/12 counts were a feasibility screen. Earlier Lean and generated-unary
allocations are distinct and remain untouched.

The missing item is an authoritative, explicitly scoped declaration of prior
Metamath allocations across the relevant sessions. This audit cannot supply a
global completeness claim from the inspected records. No new corpus body,
dependency closure, learner or native verifier has run.
