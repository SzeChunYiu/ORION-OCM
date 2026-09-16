# T833-B2/#842 — dependency graph v2 + corpus adjudication (duplicates, overstrong, RAG)

**Parents:** #833 (Section B), #842, #839
**Census parent:** `research/gmi-833-corpus-census-v1` (frozen source `2fffb14447193cbfbed3224508a077f2d4f5d2dd`)
**Adjudication-freeze parent:** `research/gmi-833-corpus-audit-close-v1` (#939; verdict taxonomy and evidence rules)
**Claim ceiling:** `GMI_833_DEPENDENCY_GRAPH_V2_AND_TRANCHE_ADJUDICATION_AT_FROZEN_CENSUS_SCOPE`

This tranche closes the four #842-open items the #939 freeze left explicit:
the vacuous dependency graph, the vacuous cycle check, the pending semantic
DUPLICATE verdicts, and the pending semantic OVERSTRONG verdicts, and ships
the corpus master RAG table.  It does not promote any object, does not
overwrite any census disposition, and does not edit other lanes' packages.

## 1. Dependency graph V2 (the #842 core)

`DEPENDENCY_GRAPH_V2.json` (miner: `depgraph_miner_v1.py`, validation:
`test_depgraph_miner_v1.py` — 24 checks, all passing, including determinism
byte-equality and 9 known-positive/9 no-alarm assertions derived from manual
reads, not from the miner's output).  **357 cited edges** in five layers:

| layer | edges | content |
|---|---|---|
| A1 file_local | 140 | relation-token lines in claim-declaring prose docs; every edge individually reviewed twice; 45 exclusions + 2 retypes logged in `REVIEW_OVERRIDES` (post-dedup) |
| A2 pointer_rollup | 28 | EXPLICIT pointer objects inherit their target doc's A1 edges |
| A3 parent_family_anchor | 60 | `(P7P8P6P5)`-style family anchor tags on 19 claim rows |
| B external_literature | 73 | verbatim strongest-parent bullets/rows from PARENT_LEDGER.md, LITERATURE_LEDGER, PARENTS.md, STRONGEST_PARENT maps |
| C corpus_package | 56 | 833-family freeze cross-references incl. AJ9a-g/K01-06 short names, typed post-census |

**Census finding (reported as such):** the corpus states FEW id-resolvable
claim→claim dependencies.  Zero census objects shipped `strongest_parents` or
`claim_dependencies` populated; the 173 GREEN mainline EXPLICIT objects are
mostly pointer/ledger rows: 0 receive direct file-local edges and 2
inherit via pointer rollup; 86 relation-verb lines reference parents by
NAME ONLY (counted as
`named_only_mentions`, never edged).  The dependency content that does exist
lives in structured parent tables (the collision matrix's P0–P9B literature
parents, 98 edges), strongest-parent headers, family anchor tags, and the
833-family package graph — all now registered with citations.  Absence of an
edge is NOT independence.

## 2. Cycles (non-vacuous answer)

`CYCLE_REPORT_V1.json` (Tarjan SCC over every layer and the union):
**0 cycles, 0 self-loops** over 239 union nodes.  The answer is now evidence,
not vacuity: it is conservative (ambiguous parent ids are collapsed to single
nodes, which can only create cycles, and none exist) and scoped to STATED
relations.

## 3. Duplicate adjudication

`DUPLICATE_ADJUDICATION_V1.json` over the frozen populations:

- **1,652 candidate groups (7,202 objects): 1,586 DUPLICATE / 66 DISTINCT /
  0 UNCERTAIN.**  Rules stated in the artifact; verification is exact byte
  comparison per group; the 38 read-required groups were individually read
  and logged (`A5C_OVERRIDES`).  Census hash semantics verified: groups key
  on `statement.lower()`.  Content-collapse: 7,202 → 1,907 nodes.
- **857 GAP-DUPID: 154 DUPLICATE (redeclarations/pointers) / 703 DISTINCT
  (id collisions).**  Collision composition: 437 same-file restatements,
  117 same-package, 149 cross-package (the true global-id problem; fix =
  unique ids or registered aliases, cross-package first).
- Collapse counting is by CONTENT (a DUPLICATE group = one content node),
  never by name/PR; corpus total 22,553 → **17,258 content nodes**.

## 4. Overstrong adjudication + downgrade list

`OVERSTRONG_ADJUDICATION_V1.json` over all **283 GAP-FIN2UNIV** flags:
**283 PROPER / 0 OVERSTRONG / 0 UNCERTAIN** (145 individually read — all 113
claim-class rows plus 34 residuals; 138 classified by mechanical rules
validated against 30 same-class sampled reads with 0 disagreements).

Reason distribution: 87 protocol rules, 76 finite-domain-declared universals,
32 negated universals, 28 headings/labels, 21 ledger/status rows, 16
enumerated-law/grid universals, 8 parent-theorem descriptions, 6
definitional, 5 no-universal-wording, 3 receipt-carry notes, 1 open-gap
listing.

**Downgrade/retract list: EMPTY for this population** — the census detector
fired on universal WORDS without boundedness/negation parsing.  The corpus's
one confirmed OVERSTRONG instance (CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1)
sits in the GREEN mainline population and is already adjudicated + carried by
the #939 freeze (its verdict table includes the exact defect wording); this
tranche adds nothing to that list and does not re-adjudicate it.

## 5. Master RAG table

`MASTER_RAG_TABLE_V1.json` (builder `master_rag_v1.py`): 39 non-empty strata
= the census/#939 28 AMBER+RED sample strata + 11 GREEN strata (counts sum to
22,553), each annotated with duplicate-group membership and FIN2UNIV flags;
census dispositions are never overwritten.  Six corpus-instance rows:

1. **[RED/HIGH] AJ9 no-smuggling contract scope gap** — task provenance and
   primitive-basis provenance ungoverned; inherited by K04–K06 (PR audit
   comments #931–#934, findings E1/A1/C1/D1).
2. **[AMBER/MEDIUM] config→freeze separation** — 12 s/10 s/13 s commit
   ordering gaps (#931 E2): prospective-ness non-demonstrable from custody
   metadata alone.
3. **[AMBER/MEDIUM] census FIN2UNIV detector** false-positive classes (this tranche).
4. **[AMBER/MEDIUM] census DUPID collisions** — 703 id collisions with composition.
5. **[AMBER/MEDIUM] census empty dependency fields** — V1 graph vacuous; repaired by V2.
6. **[AMBER/LOW] #939 tooling uncommitted** — `audit_close_v1.py` +
   `verdicts_v1.py` referenced by FREEZE_V1.md §6 but never merged; found
   untracked in the shared worktree and restored in this PR's first commit.

## 6. Determinism, receipts, ceilings

All four generators are stdlib-only, iterate over sorted keys, and rerun
byte-identically (`RECEIPTS_V1.json` records commands, head SHA, artifact
sha256s, and counts re-read from the written files).  Forbidden: any object
promotion, any census-disposition overwrite, `GMI_CORPUS_AUDIT_CLOSE_COMPLETE`,
`GMI_THEORY_BASELINE_V1` frozen (needs the FULL corpus adjudicated — the
22,116-object un-sampled remainder stays open), any claim that PROPER verdicts
prove theorems true, or that 0 cycles proves the corpus acyclic in substance.
