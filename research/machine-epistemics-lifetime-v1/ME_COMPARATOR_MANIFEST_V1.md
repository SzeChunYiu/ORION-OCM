# Strongest-parent manifest for ORION-OCM #50

Status: **registered comparator contract**. Concrete model/version hashes are bound only when the corresponding N1–N5 study unlocks and freezes its data.

## Why the historical parent is insufficient for #50

`src/ocm/comparators/matched_parent.py` is useful for the earlier language study, but its own contract deliberately removes warrant intervals, reopening, version spaces and the commitment gate. It also lacks a retrieval index, a learned executable skill library, and post-deployment adaptation. That makes it a mechanism ablation, not the strongest faithful comparator for the new lifetime-scaling thesis.

For #50, withholding the closest known parent mechanism would turn an architectural difference into a foregone conclusion.

## Comparator families

| ID | Family | Powers required | Scientific role |
|---|---|---|---|
| P0 | reset/static parent | same task information/tools; reset or no persistent post-deployment competence | lower-bound/fresh-start control only |
| P1 | indexed retrieval / RAG | same persistent documents/memory; strong ANN/indexed retrieval; index build/storage/maintenance counted | strongest parent for sparse query scaling |
| P2 | structured persistent memory agent | dynamic memory extraction/linking/consolidation and long-term retrieval | memory-organization parent |
| P3 | executable skill-library agent | persistent executable skills, composition/retrieval, later-task reuse | strongest parent for amortized acquisition/reuse |
| P4 | continual-adaptation parent | in-context memory plus the strongest feasible adapters/fine-tuning/replay/update route under matched information and update budget | strongest parent for post-deployment acquisition |
| P5 | truth/reason-maintenance parent | explicit justifications/dependencies, alternate support and exact retract/reinstate behavior | strongest parent for H3/H4 locality/revocation |
| P6 | composite whole-system parent | P1–P5 capabilities combined where compatible, same tools/verifiers/memory permissions | primary causal parent for the joint thesis |
| R0 | current frontier/open reference | best available system at execution time, possibly unmatched pretraining | absolute product reference; never causal matched evidence |

## Parent literature that must be subtracted

This list is not a novelty claim; it is a minimum reviewer attack surface.

- **Truth Maintenance / ATMS**: Doyle/de Kleer line, including de Kleer's *Exploiting Locality in a TMS* (AAAI 1990) and general ATMS labeling. Local dependency-directed revision is therefore not new merely because OCM implements it.
- **Indexed sparse retrieval**: HNSW and modern ANN/RAG systems show that query work need not scale with the full stored corpus. Sparse retrieval alone cannot be the ORION residual.
- **Executable lifelong skills**: Voyager (Wang et al., 2023; arXiv:2305.16291) keeps an ever-growing executable skill library and reuses compositional skills without parameter fine-tuning.
- **Structured long-term agent memory**: A-MEM (Xu et al., 2025; arXiv:2502.12110) dynamically links/evolves structured memories; Mem0 (Chhikara et al., 2025; arXiv:2504.19413) evaluates scalable long-term and graph memory against RAG/full-context families.
- **LLM lifelong learning**: Zheng et al. (2024; arXiv:2406.06391) surveys both internal continual adaptation and external retrieval/tool routes. #50 must not define "static LLM" so narrowly that these parents are excluded.

At execution time refresh the literature/model versions and add any stronger intervening parent.

## Parity matrix

Every causal comparison must bind these coordinates before outcome access:

- task/source/lesson identities;
- annotations and aligned semantics;
- demonstrations/interactions;
- persistent memory capacity and allowed lifetime;
- tools and network access;
- verifier/checker access;
- test-time search/planning budget;
- post-deployment update permission;
- preprocessing/index construction;
- storage/index size;
- training/update/query compute;
- human instructional burden.

If a power OCM uses is denied to the parent, that power is the experimental difference and the claim is narrowed accordingly. If a credible strongest parent cannot be implemented, the corresponding residual is `CANNOT_CHECK_MATCHED_PARENT`.

## Current synthetic calibration

`calibration.py` implements exact toy versions of P0, P1/P3/P5 concepts to test the *measurement harness*. It intentionally finds:

- H1 amortized acquisition: OCM toy = skill-library parent → `PARENT_SUFFICIENT` in isolation;
- H2 sparse query: indexed parent is also sub-global → `PARENT_SUFFICIENT` in isolation;
- H3/H4 exact local revision: exact reason-maintenance parent can match → `PARENT_SUFFICIENT` in isolation.

This is the desired skeptical result: the remaining scientific question is whether the **joint persistent epistemically governed lifecycle** creates a measurable residual under one matched task ecology.
