# T833-B1 / AA — GMI corpus census and dependency audit freeze v1

**Parent:** #833  
**Child:** #842  
**Frozen source authority:** `2fffb14447193cbfbed3224508a077f2d4f5d2dd`  
**Claim ceiling:** `GMI_CORPUS_CENSUS_AND_DEPENDENCY_AUDIT_AT_FROZEN_MAIN_SCOPE`

This file is the pre-implementation authority. It is intentionally committed before any census implementation, generated index, audit result, dependency graph, gap graph, scorer, or #833 reconciliation artifact for this child.

## 1. Scientific question

Can the registered GMI scientific corpus present at the frozen source SHA be enumerated into a provenance-bearing claim/artifact graph that fails closed on omitted candidate material, unknown classification, duplicate identity, dangling/cyclic claim dependencies, scope/quantifier ambiguity, and proof/evidence mismatch?

This is a **corpus/provenance audit**, not a proof that the audited claims are true and not an ontological-completeness theorem.

## 2. Expert lanes and adjudication roles

1. **Formal methods / theoretical CS:** theorem/definition/proof type, quantifier and dependency discipline.
2. **Scientific methods / statistics:** experiment/receipt/evidence class, prospective-vs-retrospective custody, independent replication wording.
3. **ML / algorithm selection:** prior/search/cost/ecology/evaluation disclosures and strongest-parent links.
4. **Hostile verification:** file-universe completeness, parser fallbacks, graph integrity, mutation tests and deterministic replay.

These are review roles, not independent external replication.

## 3. Frozen corpus discovery rule

The scanner MUST derive its universe from the Git checkout, never from a hand-maintained list of successful packages.

### 3.1 Included scientific roots

A tracked path under `research/` is a **primary GMI-corpus candidate** if any path component:

- starts with `gmi-` or `gmi_` (case-insensitive), or
- equals `machine-intelligence-morphogenesis-v1`.

The scanner must also include the #833 foundation/census packages themselves when present.

### 3.2 Parent/external scientific dependencies

A primary candidate may reference a scientific artifact outside those roots (for example HST, OCM core, or a parent theorem package). Such a target is recorded as a **dependency/external-parent node** with its exact path/identifier and provenance. It is not silently promoted into the GMI-owned corpus. Missing referenced targets are RED dangling-dependency gaps.

### 3.3 File universe

Within included roots, every tracked regular file is inventoried. Each file receives exactly one file role from:

`SCIENTIFIC_TEXT`, `MACHINE_METADATA`, `EXECUTABLE_WITNESS`, `TEST_OR_HOSTILE`, `RECEIPT_OR_RESULT`, `WORKFLOW_OR_OPS`, `DATA_OR_FIXTURE`, `ANCILLARY`, `UNKNOWN`.

`UNKNOWN` is allowed only as an explicit AMBER/RED audit finding. Silent omission is forbidden.

Files excluded from scientific-object parsing (binary assets, caches, generated logs, etc.) still remain in the file census with a typed exclusion reason.

## 4. Frozen scientific-object grammar

The audit recognizes these object classes:

`AXIOM`, `DEFINITION`, `THEOREM`, `LEMMA`, `PROPOSITION`, `COROLLARY`, `LAW`, `CLAIM`, `ALGORITHM`, `EXPERIMENT`, `RECEIPT_CERTIFICATE`, `PROTOCOL`, `FALSIFIER_COUNTEREXAMPLE`, `OTHER_SCIENTIFIC_OBJECT`, `UNKNOWN`.

Candidate declarations are detected from explicit machine metadata plus conservative textual markers in Markdown/JSON/Python. At minimum the textual detector must flag theorem/lemma/proposition/definition/axiom/law/claim/proof/certificate/experiment/protocol/falsifier/counterexample terminology and common registered IDs. A candidate marker that cannot be classified becomes an explicit `UNKNOWN_SCIENTIFIC_OBJECT` gap; it must not disappear from counts.

No semantic theorem identity is inferred merely from a filename.

## 5. Stable identity and provenance

Prefer an explicit registered object ID when unique. Otherwise generate a deterministic provisional ID from frozen source path + declaration location + normalized declaration text. Generated IDs are marked `PROVISIONAL_ID` and cannot by themselves establish cross-file semantic identity.

Every object row must contain, with `UNKNOWN` where unavailable:

- `object_id`, `object_class`, `source_path`, `source_locator`;
- frozen Git blob/source identity;
- statement/title summary;
- scope and quantifier class;
- proof/evidence mode;
- evidence level and maturity level if explicitly registered;
- dependencies and strongest parents;
- assumptions;
- falsifiers/counterexamples;
- forbidden extrapolations;
- result/receipt provenance where applicable;
- unresolved gaps and audit disposition.

Absence is represented as `UNKNOWN`, not invented from context.

## 6. Scope / proof / evidence discipline

Frozen quantifier classes:

`UNIVERSAL`, `FINITE_EXACT`, `HELD_OUT`, `SAMPLED_STATISTICAL`, `EXISTENTIAL_WITNESS`, `CONDITIONAL`, `UNKNOWN`.

Frozen proof/evidence modes:

`ANALYTIC_DEDUCTIVE`, `MECHANIZED_PROOF`, `COMPUTER_ASSISTED_EXHAUSTIVE`, `FINITE_EXECUTABLE_CERTIFICATE`, `STATISTICAL_EXPERIMENT`, `EMPIRICAL_EXPERIMENT`, `PROTOCOL_ONLY`, `MIXED`, `UNKNOWN`.

Finite enumeration or executable tests may support a finite exact statement, but must not be automatically relabelled as an unrestricted analytic proof. A universal-looking claim with only bounded/exhaustive finite evidence is RED unless an analytic/mechanized universal proof artifact is explicitly linked.

ACM-style artifact functionality/reproduction and independent replication are distinct statuses; same-team deterministic replay is not `INDEPENDENT_REPLICATION`.

## 7. Dependency graph

Only **claim/theorem dependency** edges participate in the acyclicity theorem. Citation, provenance, parent-comparison, and evidence-generation edges are separately typed and may point outside the primary corpus.

Required checks:

- object IDs unique;
- every internal dependency resolves exactly once;
- no self dependency;
- registered claim-dependency graph is acyclic;
- every cycle/dangling edge produces a RED `OPEN_GAP` descendant;
- candidate aliases/duplicates are AMBER until an explicit equivalence review resolves them.

## 8. Audit dispositions

- **GREEN:** structural metadata/proof obligations for the declared registered scope are discharged and no material known gap remains for that audit row. GREEN does **not** mean the theorem is universally true or novel.
- **AMBER:** explicit unknown/manual semantic review/candidate duplicate or noncritical incomplete metadata.
- **RED:** contradiction, critical missing dependency/scope/proof obligation, cycle, overclaim, laundering, or fail-closed integrity failure.

No aggregate GREEN may hide RED descendants.

## 9. Recursive gap projection

The child must project audit failures into the #833 `OPEN_GAP` schema with at least claim/object, premise/inference, unresolved assumption, possible counterexample, severity, owner role, parent result, evidence needed, materiality, closure state and descendants.

Critical open descendants block parent scientific closure. Repairing a gap must trigger a new-gap extraction pass.

## 10. Frozen hostiles

The test suite must fail closed on at least:

1. omitted included file;
2. silently ignored unknown scientific marker;
3. duplicate stable ID;
4. dangling internal dependency;
5. dependency cycle;
6. missing/UNKNOWN scope on a claim advertised as universal;
7. receipt/result with no source/provenance link;
8. universal claim backed only by bounded finite enumeration;
9. same-team replay mislabeled as independent replication;
10. critical open descendant laundered into parent GREEN;
11. post-freeze expected-count hard-coding;
12. nondeterministic output ordering.

## 11. Determinism and execution

Normal Python and `python -O` must produce byte-identical canonical JSON for the exact frozen checkout. Counts must be derived from discovered files/objects, never hard-coded in the scorer.

## 12. Literature/parent vocabulary anchors

The implementation should reuse established distinctions rather than minting synonyms:

- formal specification describes intended behavior; verification checks conformance;
- W3C PROV-style provenance separates entities, activities/derivations and responsible agents;
- Rice-style algorithm selection separates problem, feature, algorithm and performance spaces;
- artifact functionality/reproduction/replication are not the same claim.

Literature citations support terminology only; they do not substitute for repository evidence.

## 13. Explicit non-claims / falsifiers

This child alone may not assert:

`ALL_GMI_THEOREMS_TRUE`, `ONTOLOGICAL_COMPLETENESS`, `ALL_PARENTS_EXHAUSTED`, `ALL_OVERCLAIMS_REPAIRED`, `KNOWN_FAMILY_DERIVATION_COMPLETE`, `REAL_SCALE_VALIDATION_COMPLETE`, `COMPLETE_GMI`.

The claim ceiling is falsified if the scanner can omit an included candidate without detection, if an unknown candidate is silently dropped, if graph hostiles do not fail, if output depends on file traversal order, or if the generated audit promotes finite computation into an unrestricted proof.
