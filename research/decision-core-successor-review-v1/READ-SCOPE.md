# Read scope and custody

Date: 2026-09-08. Independent source/design review only.
Repository: SzeChunYiu/ORION-OCM, PR154.

## Binding chain

1. Queried live PR metadata before fetching source: head
   `e7d3cd067510c3a4a69568e5f4cf95554e455eb8`, tree
   `519f2bd1001bb903dd8e9be7adf53e2d2764ebc9`.
2. The comparison from historical `9087971dd3a9847149fa8cf844cb13e84a57cacd`
   contained 62 commits and 43 files: 42 additions and one workflow modification.
   The requested four are a subset; the remaining 39 were not source-reviewed.
3. Retrieved four Git blobs through GitHub's API, verified Git blob SHA1 and
   SHA256, and wrote only this owned Linux capsule. No checkout was created.
4. Closing live PR query observed `c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd`, tree
   `05fef3d2bafe7acd6e6a89fbaf610171381b052c`, updatedAt 2026-09-08T16:10:11Z.
   The four intervening commits affect a workflow plus three additional files.
   A nontruncated recursive tree response independently binds the same four blob
   SHAs and sizes at this newer head. The reviewed content is therefore unchanged.

Raw initial metadata and comparison: [PR-METADATA.json](PR-METADATA.json).
Closing metadata, comparison and tree selection: [CLOSING-METADATA.json](CLOSING-METADATA.json).
File SHA256/Git-blob bindings: [FETCHED-SOURCES.json](FETCHED-SOURCES.json).

## Complete source reads

| Source | Lines read |
|---|---:|
| FORMAL_DECISION_CORE_V2.md | 1–754 |
| LITERATURE_SYNTHESIS_V1.md | 1–350 |
| decision_core.py | 1–242 |
| test_decision_core.py | 1–152 |

Copied source resides under `source/research/residual-strategy-regime-v1/`.
Reading a test is not a test run. By-hand counterexamples are independently
reasoned input witnesses, not observed study outcomes.

## Primary-source scope

- Previously read Hay et al. 2012 v1: definitions 1/3, theorems 4/5, Example 3,
  §6.2. [Primary PDF](https://arxiv.org/pdf/1207.5879v1).
- Previously read Bertsekas corrected 2020 v2: introduction, Eq. (7),
  propositions 2/7 and conditions, Example 1, conclusion; v1 comparison.
  [Primary PDF](https://arxiv.org/pdf/1711.10129v2).
- Previously read Lotker et al. expanded 2010: introduction, §2–3 including
  decomposition/combination proofs; §4 opening only.
  [Author PDF](https://www.eng.biu.ac.il/~rawitzd/Papers/ski.pdf).
- New bounded read of Givan–Dean–Greig author manuscript: §3.3 definition and
  Theorems 4–7, plus located appendix proof passages for Theorems 5/7.
  [Primary PDF](https://cs.brown.edu/people/tdean/publications/archive/GivanetalAIJ-03.pdf).
  Other literature-map families were not independently re-reviewed here.

## Exclusions

No experiment, study, native verifier, learner, protected corpus, CI or tests;
no imports of copied modules; no source edits, GitHub writes, comments or messages
to the other PR lane. Mac use was limited to metadata/blob transfer because the
Linux executable named gh was an unrelated CLI. Source storage and receipt writes
were on billy-laptop. No PR156/157 or root checkout/capsule was modified.

Later lifecycle, representation, coverage, convergence, parent implementation,
and CI additions are outside scope. This review does not classify the whole PR,
reproduce the frozen population, judge novelty, or approve a research result.
