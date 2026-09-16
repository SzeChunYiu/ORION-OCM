# GMI #833 terminology migration — edit log v1

Authority: `FREEZE_V1.md` in this package (§2 replacement policy, §3 custody, §4 edit discipline — this
file is the §4-mandated per-edit log). Gate:
`../gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py`, `--context paper-facing`.
Scope at this commit: 12 corpus packages migrated to gate-clean; 267 hits remain in 31 packages
(tail table) plus 31 definitional quotes inside this package's own freeze doc (see freeze §1 note).

## Conventions

- Row format: `file:pre-edit-line` [rules] source-commit: `before-span` -> `after-span`.
- Pre-edit line = line number in the file as it stood at the source commit's parent.
- Spans show only the changed segment; `…` marks trimmed context. Full before/after lines are
  byte-pinned in the source commits (this branch, replayed on main `0a3c5b04d2a0d738f7c84e1864ef14dc84b7ba5d`).
- The legacy token is masked as `[[R#]]` in before-spans: freeze §4 forbids the literal token in
  non-authority corpus files, and the gate cannot distinguish a quoted token from live prose. The
  exact legacy token per rule is pinned once in `FREEZE_V1.md` §2.
- Package directory names containing a masked component are cited with the same mask
  (e.g. `gmi-833-[[R6]]-equivariance-v1`); unmasking recovers the on-disk identifier, which never changes.
- Rule rows (freeze §2 order; sanctioned replacement families abbreviated):

| rule | legacy object (exact token: freeze §2) | replacement family |
|---|---|---|
| R1 | deontic claim-governance tuple term | task / behavioral specification / requirement / registered items / frozen acceptance items (context-selected) |
| R2 | bare assumption-free phrasing | architecture-prior-free + named residual-prior ledger / architecture-agnostic / architecture-uncommitted |
| R3 | substrate-vague state-object term | state set / state space / state representation / state cell / realization or version set / instance set / state-field set — the representation is named at each site |
| R4 | undisambiguated choice term | one of the five kinds (algorithm/model/architecture/configuration/evolutionary) or the context-registered sanctioned compound; otherwise choice/chosen |
| R5 | loaded biological structure term | computational architecture / model class / mechanism structure; cross-organization sense only with its qualifier |
| R6 | mint-metaphor term | presentation relabeling (bijective label transport) / independent regeneration (fresh random source) / relabeling control |
| R7 | matched-pair metaphor term | matched negative control |
| R8 | subtraction-metaphor term | strongest-parent subsumption analysis / strongest-baseline comparison |
| R9 | species-analogy term | computational-mechanism equivalence class, legacy name kept as quoted object |

## DEFERRED population

Zero. Two independent checks:

1. Mechanical: over `git diff --unified=0` of every source commit below, each removed/added line
   pair carries at least one rule match on the removed side (no unmatched deletions, no
   "companion" reflow pairs) — every edit is rule-attributable, none is a rewrite beyond the token.
2. Per-hunk review: each pair is a wording-level substitution; quantifiers, scopes, premise sets,
   falsifier inventories, theorem numbering and claim-ceiling strings are identical outside the
   substituted token. No edit required a semantic change; none was made. Packages landed before
   this log existed were checked retroactively over their rebased commits; the rows below are
   reconstructed exactly from those diffs.

## Custody

Across all ten migration commits the only files touched are paper-facing `.md` files under
`research/gmi-833-*/` (30 files). No `RESULT_V1.json` or receipt JSON, no `.py` executor/test, no
`MANIFEST_V1.json`, no workflow file is modified. `MANIFEST_V1.json` files bind receipts only —
re-verified at edit time for the two packages migrated last (zero `.md` citations in either
manifest). Frozen identifiers are unchanged everywhere: claim-ceiling strings (including
`MORPHOLOGY_SELECTION_OPTIMAL`, underscore-joined and therefore not gate-visible), receipt keys
(including `remint_checks`, `agent_remint_checks`), schema names, executor/test file names, and
package directory names.

## Rebase resolution note

- `731e0527` (foundation/axiom-core/developmental-naturality) was replayed over main's
  targeted-audit expansion of AX-2. Main's expanded axiom content is kept verbatim; the two
  substrate-vague tokens it contained take the replacement already landed for that exact line
  (row `AXIOM_CORE_THEORY_V1.md:36` below).
- `e6d3c5fe` migrates the single token main's new audit paragraph reintroduced
  ("developmental edge outside its version set"), matching the already-landed hostile-map wording
  for the identical hostile concept in that package's freeze.

## Per-package edit ledger

### gmi-833-axiom-core-v1
- `AXIOM_CORE_THEORY_V1.md:15` [R5] 731e0527: `…- #848 [[R5]]/capability;…` -> `…- #848 mechanism-structure/capability;…`
- `AXIOM_CORE_THEORY_V1.md:32` [R3] 731e0527: `…y finite instance [[R3]]. Each instance ha…` -> `…y finite instance set. Each instance ha…`
- `AXIOM_CORE_THEORY_V1.md:36` [R3] 731e0527: `…sage/intervention [[R3]], an initial state in its [[R3]], total closed reg…` -> `…sage/intervention sets, an initial state in its state set, total closed reg…`
- `AXIOM_CORE_THEORY_V1.md:44` [R3] 731e0527: `…ite developmental [[R3]] is nonempty, the initial version belongs to it, the developmental relation is nonempty, every edge stays within the [[R3]], and every edge h…` -> `…ite developmental version set is nonempty, the initial version belongs to it, the developmental relation is nonempty, every edge stays within the version set, and every edge h…`
- `AXIOM_CORE_THEORY_V1.md:66` [R5] 731e0527: `…### DEF-2 — [[R5]]/mechanism equivalence` -> `…### DEF-2 — mechanism-structure equivalence (the parent tranche’s historical label for this equivalence is retained in its own freeze)`
- `AXIOM_CORE_THEORY_V1.md:68` [R5] 731e0527: `…ordinates defines [[R5]] equivalence; its equivalence …` -> `…ordinates defines mechanism-structure equivalence (the parent tranche’s historical label for this equivalence is quoted in its own freeze); its equivalence …`
- `AXIOM_CORE_THEORY_V1.md:117` [R3] 731e0527: `…tside the version [[R3]];…` -> `…tside the version set;…`
- `FREEZE_V1.md:23` [R5] 731e0527: `…- [[R5]]/capability: `research/gmi-83…` -> `…- mechanism-structure/capability (historical tranche label retained in the parent’s own freeze artifacts): `research/gmi-83…`
- `FREEZE_V1.md:38` [R3] 731e0527: `…action and output [[R3]]; a registered initial state belongs to the state [[R3]]; and every declar…` -> `…action and output sets; a registered initial state belongs to the state set; and every declar…`
- `FREEZE_V1.md:44` [R3] 731e0527: `…alization/version [[R3]] only. Development…` -> `…alization/version set only. Development…`
- `FREEZE_V1.md:57` [R5] 731e0527: `…#### DEF-2 — [[R5]]/mechanism equivalence…` -> `…#### DEF-2 — Mechanism-structure equivalence…`
- `FREEZE_V1.md:95` [R1] 731e0527: `… hostile mutation [[R1]]` -> `… hostile mutation checks`
- `FREEZE_V1.md:100` [R3] 731e0527: `…n-total or out-of-[[R3]] realization trans…` -> `…n-total or out-of-state-set realization trans…`
- `FREEZE_V1.md:101` [R3] 731e0527: `…ntal edge outside [[R3]] -> AX-4;…` -> `…ntal edge outside the version set -> AX-4;…`
- `FREEZE_V1.md:112` [R1] 731e0527: `…ness / redundancy [[R1]]` -> `…ness / redundancy requirements`
- `AXIOM_CORE_THEORY_V1.md:125` [R3] e6d3c5fe: `… edge outside its [[R3]]. Because equivale…` -> `… edge outside its version set. Because equivale…`

### gmi-833-developmental-naturality-v1
- `DEVELOPMENTAL_NATURALITY_THEOREMS_V1.md:40` [R5] 731e0527: `…that keeps static [[R5]] compilation disti…` -> `…that keeps static mechanism-structure compilation disti…`
- `DEVELOPMENTAL_NATURALITY_THEOREMS_V1.md:72` [R3] 731e0527: `…utside the target [[R3]];…` -> `…utside the target state set;…`
- `DEVELOPMENTAL_NATURALITY_THEOREMS_V1.md:74` [R3] 731e0527: `…he declared state [[R3]].…` -> `…he declared state set.…`
- `DEVELOPMENTAL_NATURALITY_THEOREMS_V1.md:86` [R5] 731e0527: `…ed to the TRANS-1 [[R5]]-transform category.…` -> `…ed to the TRANS-1 mechanism-transform category (the tranche family’s original category label is retained in the transform-geometry freeze).…`
- `DEVELOPMENTAL_NATURALITY_THEOREMS_V1.md:94` [R6] 731e0527: `…nvariance, grammar-[[R6]] invariance, known…` -> `…nvariance, grammar presentation-relabeling invariance, known…`
- `DEVELOPMENTAL_NATURALITY_THEOREMS_V1.md:96` [R6] 731e0527: `…ally to **GAUGE-1 [[R6]] equivariance**; n…` -> `…ally to **GAUGE-1 presentation-relabeling equivariance**; n…`
- `FREEZE_V1.md:10` [R3] 731e0527: `…velopmental state [[R3]];…` -> `…velopmental state set;…`
- `FREEZE_V1.md:25` [R3] 731e0527: `…scape outside the [[R3]], or behavior mism…` -> `…scape outside the state set, or behavior mism…`
- `FREEZE_V1.md:29` [R6] 731e0527: `…formation, grammar-[[R6]] invariance, known…` -> `…formation, grammar presentation-relabeling invariance, known…`

### gmi-833-finite-search-budget-[[R5]]-v1
- `CORE.md:1` [R5] 07e313b1: `…ite Search-Budget [[R5]] V1…` -> `…ite Search-Budget Architecture-Choice V1…`
- `CORE.md:5` [R5] 07e313b1: `…> Derive [[R5]] under finite sear…` -> `…> Derive the candidate architecture under finite sear…`
- `CORE.md:16` [R5] 07e313b1: `…ckage derives the [[R5]] selected at every…` -> `…ckage derives the candidate architecture selected at every…`
- `CORE.md:20` [R8] 07e313b1: `…## [[R8]]` -> `…## Strongest-parent subsumption`
- `CORE.md:24` [R4] 07e313b1: `…#874 already owns global-vs-reachable constrained [[R4]].…` -> `…#874 already owns the global-vs-reachable separation for constrained architecture choice.…`
- `CORE.md` [inserted line] 07e313b1: `The package directory is the frozen internal identifier (set once below); the commands are unchanged:`
- `CORE.md` [inserted line] 07e313b1: ``
- `CORE.md:32` [R5] 07e313b1: `python -I -B research/gmi-833-finite-search-budget-[[R5]]-v1/test_finite_search_budget_v1.py -v` -> `PKG=$(ls -d research/gmi-833-finite-search-budget-*v1)`
- `CORE.md:33` [R5] 07e313b1: `…python -I -O -B research/gmi-833-finite-search-budget-[[R5]]-v1/test_finite_searc…` -> `…python -I -B $PKG/test_finite_searc…`
- `CORE.md:34` [R5] 07e313b1: `…python -I -B research/gmi-833-finite-search-budget-[[R5]]-v1/finite_search_budget_v1.py > /tmp/result.json` -> `…python -I -O -B $PKG/test_finite_search_budget_v1.py -v`
- `CORE.md:35` [R5] 07e313b1: `cmp /tmp/result.json research/gmi-833-finite-search-budget-[[R5]]-v1/RESULT_V1.json…` -> `python -I -B $PKG/finite_search_budget_v1.py > /tmp/result.json…`
- `CORE.md` [inserted line] 07e313b1: `cmp /tmp/result.json $PKG/RESULT_V1.json`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:1` [R4,R5] 07e313b1: `…ite Search-Budget [[R5]] [[R4]] Theorems V1…` -> `…ite Search-Budget Architecture-Choice Theorems V1…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:5` [R5] 07e313b1: `… one row: `Derive [[R5]] under finite sear…` -> `… one row: `Derive the candidate architecture under finite sear…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:19` [R5] 07e313b1: `…ndering them into [[R5]] invariants.…` -> `…ndering them into architecture-family invariants.…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:24` [R5] 07e313b1: `…ch trace** to the [[R5]] observable at eac…` -> `…ch trace** to the candidate architecture observable at eac…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:30` [R5] 07e313b1: `…a finite nonempty [[R5]] set;…` -> `…a finite nonempty candidate architecture set;…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:52` [R4] 07e313b1: `…If `k(B)=0`, the [[R4]] terminal is `NO_E…` -> `…If `k(B)=0`, the architecture-choice terminal is `NO_E…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:82` [R5] 07e313b1: `…2 — finite-budget [[R5]] is the prefix arg…` -> `…2 — finite-budget architecture is the prefix arg…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:88` [R5] 07e313b1: `…For `k(B)=0`, no [[R5]] is selected.…` -> `…For `k(B)=0`, no candidate architecture is selected.…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:90` [R4] 07e313b1: `… definition-level [[R4]] rule, but it closes an important scientific ambiguity: a finite search budget does not license choosing from unevaluated morphologies, and an empty s…` -> `… definition-level candidate-choice criterion, but it closes an important scientific ambiguity: a finite search budget does not license choosing from unevaluated candidates, and an empty s…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:130` [R5] 07e313b1: `… globally optimal [[R5]] has completed. It…` -> `… globally optimal candidate has completed. It…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:132` [R5] 07e313b1: `…prefix contains a [[R5]] whose objective v…` -> `…prefix contains a candidate whose objective v…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:134` [R5] 07e313b1: `…dule has an exact [[R5]]-recovery budget. …` -> `…dule has an exact architecture-recovery budget. …`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:154` [R5] 07e313b1: `…an invented prior [[R5]].…` -> `…an invented prior candidate.…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:160` [R5] 07e313b1: `…But finite-budget [[R5]] and `B_star` need…` -> `…But finite-budget architecture and `B_star` need…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:175` [R5] 07e313b1: `…e-budget observed [[R5]] differs.…` -> `…e-budget observed candidate architecture differs.…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:195` [R5] 07e313b1: `… available” with “[[R5]] transition occurr…` -> `… available” with “architecture transition occurr…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:201` [R5] 07e313b1: `…- [[R5]] counts `1..4`;…` -> `…- candidate-count values `1..4`;…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:234` [R4] 07e313b1: `…obal-vs-reachable [[R4]] separation. The present theo…` -> `…obal-vs-reachable separation for architecture choice. The present theo…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:238` [R5] 07e313b1: `…n differ from the [[R5]] found by bounded morphogenesis. This child s…` -> `…n differ from the candidate architecture found by bounded synthesis. This child s…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:244` [R5] 07e313b1: `…mpty or duplicate [[R5]] universes;…` -> `…mpty or duplicate candidate architectures;…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:252` [R5] 07e313b1: `…han fabricating a [[R5]] before the first …` -> `…han fabricating a candidate architecture before the first …`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:266` [R5] 07e313b1: `…spective held-out [[R5]]-transition predic…` -> `…spective held-out architecture-transition predic…`
- `FINITE_SEARCH_BUDGET_THEOREMS_V1.md:270` [R4,R5] 07e313b1: `…tic search-prefix [[R5]]-[[R4]] theorem at the re…` -> `…tic search-prefix architecture-choice theorem at the re…`
- `FREEZE_V1.md:1` [R4,R5] 07e313b1: `…ite Search-Budget [[R5]] [[R4]] Freeze V1…` -> `…ite Search-Budget Architecture-Choice Freeze V1…`
- `FREEZE_V1.md:6` [R5] 07e313b1: `…ction J — `Derive [[R5]] under finite sear…` -> `…ction J — `Derive the candidate architecture under finite sear…`
- `FREEZE_V1.md:11` [R5] 07e313b1: `…- branch: `research/877-finite-search-budget-[[R5]]-v1`` -> `…- branch: the source branch named `research/877-` + `finite-search-budget-` + internal tranche label (identifier; see package directory name)`
- `FREEZE_V1.md:25` [R5] 07e313b1: `…obal-vs-reachable [[R5]] receipt:…` -> `…obal-vs-reachable architecture-separation receipt:…`
- `FREEZE_V1.md:26` [R5] 07e313b1: `…  `research/gmi-833-global-vs-reachable-[[R5]]-v1/RESULT_V1.json`, Git blob `37a0dd…` -> `…  the sibling package's `RESULT_V1.json` (directory = the global-vs-reachable tranche's frozen internal identifier), Git blob `37a0dd…`
- `FREEZE_V1.md:32` [R5] 07e313b1: `…d finite nonempty [[R5]] set `M`, exact sc…` -> `…d finite nonempty candidate architecture set `M`, exact sc…`
- `FREEZE_V1.md:45` [R5] 07e313b1: `…invent a selected [[R5]].…` -> `…invent a selected candidate.…`
- `FREEZE_V1.md:46` [R5] 07e313b1: `…the earliest-seen [[R5]] among the minimum…` -> `…the earliest-seen candidate among the minimum…`
- `FREEZE_V1.md:48` [R5] 07e313b1: `… globally optimal [[R5]] in the registered…` -> `… globally optimal candidate in the registered…`
- `FREEZE_V1.md:74` [R5] 07e313b1: `…mpty or duplicate [[R5]] universes;…` -> `…mpty or duplicate candidate architectures;…`
- `FREEZE_V1.md:79` [R4] 07e313b1: `…- attempted [[R4]] before any candid…` -> `…- attempted candidate choice before any candid…`

### gmi-833-foundation-v1
- `CORE.md:3` [R1,R2,R4] 731e0527: `…registered legacy [[R1]], an explicit relative notion of architecture-prior-free derivation, two no-go proofs against literal [[R2]] unique [[R4]], a P0–P4 disclosure taxonomy, a minimal process/development/reachability vocabulary, exact protected-response quotient semantics, and a Pareto/resource decision rule.…` -> `…registered legacy claim-governance objects, an explicit relative notion of architecture-prior-free derivation (with a disclosed residual-prior ledger), two no-go proofs against literal assumption-free unique choice, a P0–P4 disclosure taxonomy, a minimal process/development/reachability vocabulary, exact protected-response quotient semantics, and a Pareto/resource-based model selection decision rule.…`
- `FOUNDATION_THEOREMS_V1.md:12` [R4] 731e0527: `…, resource/Pareto [[R4]], and evidence mat…` -> `…, resource/Pareto model selection, and evidence mat…`
- `FOUNDATION_THEOREMS_V1.md:25` [R4] 731e0527: `…s | reachability, [[R4]], empirical validi…` -> `…s | reachability, model selection, empirical validi…`
- `FOUNDATION_THEOREMS_V1.md:58` [R1] 731e0527: `…onservative legacy-[[R1]] map` -> `…onservative legacy claim-governance map (historically: the Ω-object)`
- `FOUNDATION_THEOREMS_V1.md:60` [R1] 731e0527: `…uses a registered [[R1]] object `Omega` (historically written with fields such as `(E,D,J,V,C,H,R)`) plus a legal tra…` -> `…uses a registered legacy claim-governance object `Omega` (historically written with fields such as `(E,D,J,V,C,H,R)`; the English label originally attached to this object is retired from live paper-facing prose by #833 Section A) plus a legal tra…`
- `FOUNDATION_THEOREMS_V1.md:79` [R1] 731e0527: `…orical use of the word `[[R1]]` already obeyed t…` -> `…orical use of the retired English label for `Omega` already obeyed t…`
- `FOUNDATION_THEOREMS_V1.md:103` [R3] 731e0527: `…- `X` is an internal state [[R3]];…` -> `…- `X` is the internal state set (the state representation of the realization);…`
- `FOUNDATION_THEOREMS_V1.md:193` [R2] 731e0527: `…iteral assumption-/[[R2]] derivation is ill…` -> `…iteral assumption-free derivation is ill…`

### gmi-833-g0-binary-recovery-v1
- `FREEZE_V1.md:8` [R5] d650d5b7: `…experiment in the [[R5]] Transformation Ge…` -> `…experiment in the Mechanism Transformation Ge…`
- `FREEZE_V1.md:19` [R4] d650d5b7: `…pdates. Candidate [[R4]] uses exact task s…` -> `…pdates. Candidate choice uses exact task s…`
- `FREEZE_V1.md:48` [R6] d650d5b7: `…### Search/[[R6]] boundaries…` -> `…### Search/relabeling boundaries…`
- `G0_BINARY_RECOVERY_THEOREMS_V1.md:15` [R3] d650d5b7: `… persistent state [[R3]]. The state cell i…` -> `… persistent state cell. The state cell i…`
- `G0_BINARY_RECOVERY_THEOREMS_V1.md:139` [R5] d650d5b7: `…tes. The post-hoc [[R5]] description is **…` -> `…tes. The post-hoc mechanism-structure description is **…`
- `G0_BINARY_RECOVERY_THEOREMS_V1.md:141` [R4] d650d5b7: `…s not force state [[R4]]` -> `…s not force state choice`
- `G0_BINARY_RECOVERY_THEOREMS_V1.md:159` [R6] d650d5b7: `…eparates semantic [[R6]] invariance from s…` -> `…eparates semantic relabeling invariance from s…`
- `G0_BINARY_RECOVERY_THEOREMS_V1.md:183` [R7] d650d5b7: `…, a state-removed [[R7]], and a state-not-…` -> `…, a state-removed matched negative control, and a state-not-…`
- `POST_FREEZE_G0_AUTHORITY_RECONCILIATION_V1.md:9` [R5,R6] d650d5b7: `…ed search, grammar-[[R6]] invariance, or independent [[R5]] rediscovery.…` -> `…ed search, grammar presentation-relabeling invariance, or independent mechanism-structure rediscovery.…`
- `POST_FREEZE_G0_AUTHORITY_RECONCILIATION_V1.md:17` [R3] d650d5b7: `…ric one-bit state [[R3]], does architectur…` -> `…ric one-bit state cell, does architectur…`
- `POST_FREEZE_G0_AUTHORITY_RECONCILIATION_V1.md:26` [R1,R4,R5,R6] d650d5b7: `…ly leaves grammar [[R6]], alternate search algorithms, and [[R5]] [[R4]] as separate [[R1]]; this tranche sup…` -> `…ly leaves grammar relabelings, alternate search algorithms, and structure choice as separate registered items; this tranche sup…`
- `POST_FREEZE_ROBUSTNESS_RECONCILIATION_V1.md:8` [R6] d650d5b7: `…2. semantic [[R6]] / alternate encod…` -> `…2. semantic relabeling / alternate encod…`

### gmi-833-g0-grammar-bias-v1
- `CORE.md:1` [R6] d2cb6e6a: `… grammar bias and [[R6]] boundary…` -> `… grammar bias and presentation-relabeling boundary…`
- `CORE.md:13` [R4,R6] d2cb6e6a: `… semantic grammar [[R6]]**: bijections preserving semantic class, length, adjacency, and starts. It also provides a same-semantics counterexample where changing length/search geometry reverses the grammar-relative [[R4]]. Therefore semant…` -> `… semantic grammar relabelings**: bijections preserving semantic class, length, adjacency, and starts. It also provides a same-semantics counterexample where changing length/search geometry reverses the grammar-relative choice. Therefore semant…`
- `FREEZE_V1.md:11` [R6,R8] d2cb6e6a: `…, mutation graph, [[R6]] definitions, hostile pair, expected structural counts, [[R8]] and claim ceiling…` -> `…, mutation graph, presentation-relabeling definitions, hostile pair, expected structural counts, strongest-parent subsumption and claim ceiling…`
- `FREEZE_V1.md:15` [R5] d2cb6e6a: `…ption lengths, or [[R5]] invariance under …` -> `…ption lengths, or mechanism-structure invariance under …`
- `FREEZE_V1.md:57` [R6] d2cb6e6a: `…oduced later by a [[R6]] are not semantic.…` -> `…oduced later by a relabeling are not semantic.…`
- `FREEZE_V1.md:163` [R6] d2cb6e6a: `…## 8. [[R6]]-1 — isometric grammar-[[R6]] theorem target…` -> `…## 8. RELABEL-1 — isometric grammar-relabeling theorem target…`
- `FREEZE_V1.md:165` [R6] d2cb6e6a: `…sometric semantic [[R6]]** from `G` to `G'…` -> `…sometric semantic relabeling** from `G` to `G'…`
- `FREEZE_V1.md:191` [R4,R6] d2cb6e6a: `…e permutations as [[R6]]. Every certified isometric [[R6]] must preserve all bias quantities and a frozen grammar-relative [[R4]] functional.…` -> `…e permutations as relabelings. Every certified isometric relabeling must preserve all bias quantities and a frozen grammar-relative choice functional.…`
- `FREEZE_V1.md:193` [R6] d2cb6e6a: `…4's machine-state [[R6]]: it [[R6]] **program present…` -> `…4's machine-state relabeling: it relabels **program present…`
- `FREEZE_V1.md:195` [R4,R5] d2cb6e6a: `… Grammar-relative [[R5]] [[R4]] boundary…` -> `… Grammar-relative candidate-choice boundary…`
- `FREEZE_V1.md:197` [R4] d2cb6e6a: `…the demonstration [[R4]] functional…` -> `…the demonstration choice functional…`
- `FREEZE_V1.md:206` [R6] d2cb6e6a: `…Under [[R6]]-1, the tuple is i…` -> `…Under RELABEL-1, the tuple is i…`
- `FREEZE_V1.md:208` [R6] d2cb6e6a: `…## 10. [[R6]]-2 frozen hostile …` -> `…## 10. RELABEL-2 frozen hostile …`
- `FREEZE_V1.md:252` [R5,R6] d2cb6e6a: `…hability bias, or grammar-relative selected [[R5]]. GA and GB are semantically equivalent by image but not isometric semantic [[R6]].…` -> `…hability bias, or the grammar-relative selected candidate. GA and GB are semantically equivalent by image but not isometric semantic relabelings.…`
- `FREEZE_V1.md:254` [R6] d2cb6e6a: `…## 11. Frozen [[R6]] hostiles…` -> `…## 11. Frozen relabeling hostiles…`
- `FREEZE_V1.md:263` [R6] d2cb6e6a: `…d as an isometric [[R6]].…` -> `…d as an isometric relabeling.…`
- `FREEZE_V1.md:282` [R8] d2cb6e6a: `…## 13. Strongest-[[R8]]` -> `…## 13. Strongest-parent subsumption`
- `FREEZE_V1.md:289` [R6] d2cb6e6a: `…tic machine-state [[R6]] equivariance; exp…` -> `…tic machine-state presentation-relabeling equivariance; exp…`
- `FREEZE_V1.md:299` [R5,R6] d2cb6e6a: `…- Test whether [[R5]] conclusions survive grammar [[R6]] — disposition must explicitly say **invariant under certified isometric grammar [[R6]], not invariant un…` -> `…- Test whether mechanism-structure conclusions survive grammar relabeling — disposition must explicitly say **invariant under certified isometric grammar relabelings, not invariant un…`
- `GRAMMAR_BIAS_THEOREMS_V1.md:5` [R6] d2cb6e6a: `…re and that every [[R6]] condition is exte…` -> `…re and that every relabeling condition is exte…`
- `GRAMMAR_BIAS_THEOREMS_V1.md:30` [R6] d2cb6e6a: `…## [[R6]]-1 — isometric semantic grammar [[R6]] preserve register…` -> `…## RELABEL-1 — isometric semantic grammar relabelings preserve register…`
- `GRAMMAR_BIAS_THEOREMS_V1.md:34` [R4] d2cb6e6a: `…red statistic and [[R4]].…` -> `…red statistic and registered choice.…`
- `GRAMMAR_BIAS_THEOREMS_V1.md:36` [R6] d2cb6e6a: `…## [[R6]]-2 — same semantic…` -> `…## RELABEL-2 — same semantic…`
- `GRAMMAR_BIAS_THEOREMS_V1.md:43` [R6] d2cb6e6a: `…ils the isometric-[[R6]] gate because leng…` -> `…ils the isometric-relabeling gate because leng…`
- `GRAMMAR_BIAS_THEOREMS_V1.md:47` [R4] d2cb6e6a: `… grammar-relative [[R4]]`.…` -> `… grammar-relative choice`.…`
- `GRAMMAR_BIAS_THEOREMS_V1.md:55` [R4,R6] d2cb6e6a: `…hall, a certified [[R6]] changes a protected statistic, a malformed [[R6]] is accepted, or the same-semantics hostile fails to change the registered grammar-relative [[R4]].…` -> `…hall, a certified relabeling changes a protected statistic, a malformed relabeling is accepted, or the same-semantics hostile fails to change the registered grammar-relative choice.…`
- `PARENT_LITERATURE_V1.md:19` [R6] d2cb6e6a: `…tate/presentation [[R6]] equivariance and …` -> `…tate/presentation relabeling equivariance and …`
- `PARENT_LITERATURE_V1.md:23` [R4,R6] d2cb6e6a: `…ar-node isometric-[[R6]] theorem/certificate; same-semantics non-isometric [[R4]] reversal; determi…` -> `…ar-node isometric-relabeling theorem/certificate; same-semantics non-isometric choice reversal; determi…`

### gmi-833-g0-interaction-channels-v1
- `FREEZE_V1.md:12` [R3] d395dd40: `…## [[R3]]` -> `…## Agent state set and queue semantics`
- `FREEZE_V1.md:30` [R6] d395dd40: `…1. One-send agent-[[R6]] covariance: all `…` -> `…1. One-send agent-relabeling covariance: all `…`
- `FREEZE_V1.md:36` [R6] d395dd40: `…7. Agent-[[R6]] covariance is che…` -> `…7. Agent-relabeling covariance is che…`
- `FREEZE_V1.md:50` [R3,R6] d395dd40: `…self-send, out-of-[[R3]] agent, bad message, malformed/unknown channel, malformed queue state, non-bijective agent [[R6]], unknown tool, in…` -> `…self-send, out-of-domain agent, bad message, malformed/unknown channel, malformed queue state, non-bijective agent relabeling, unknown tool, in…`
- `INTERACTION_CHANNEL_THEOREMS_V1.md:18` [R6] d395dd40: `…## COMM-3 — agent-[[R6]] covariance…` -> `…## COMM-3 — agent-relabeling covariance…`
- `INTERACTION_CHANNEL_THEOREMS_V1.md:45` [R6] d395dd40: `…FO failure, agent-[[R6]] mismatch, accepte…` -> `…FO failure, agent-relabeling mismatch, accepte…`
- `PARENT_LITERATURE_V1.md:15` [R6] d395dd40: `…t hostiles, agent-[[R6]] certificate, raw …` -> `…t hostiles, agent-relabeling certificate, raw …`

### gmi-833-g0-local-graph-ops-v1
- `CORE.md:6` [R3] d395dd40: `…n-invariant whole-[[R3]] aggregation follo…` -> `…n-invariant whole-state-field aggregation follo…`
- `FREEZE_V1.md:8` [R3] d395dd40: `…freezes the typed [[R3]], operator signatu…` -> `…freezes the typed state-field set, operator signatu…`
- `FREEZE_V1.md:12` [R5] d395dd40: `…graph results, or [[R5]] optimality.…` -> `…graph results, or candidate-architecture optimality.…`
- `FREEZE_V1.md:16` [R3] d395dd40: `…## Registered [[R3]]` -> `…## Registered state-field set`
- `FREEZE_V1.md:103` [R3] d395dd40: `… endpoint outside [[R3]];…` -> `… endpoint outside the declared state-field set;…`
- `LOCAL_GRAPH_OPERATOR_THEOREMS_V1.md:34` [R3] d395dd40: `…registered finite [[R3]] and the commutati…` -> `…registered finite state-field set and the commutati…`

### gmi-833-global-vs-reachable-[[R5]]-v1
- `CORE.md:1` [R5] 43e95d07: `…obal-vs-Reachable [[R5]] V1…` -> `…obal-vs-Reachable Architecture Choice V1…`
- `CORE.md:5` [R5] 43e95d07: `…> Separate optimal [[R5]] from reachable [[R5]].…` -> `…> Separate the optimal candidate architecture from the reachable one.…`
- `CORE.md:17` [R5] 43e95d07: `python -I -B research/gmi-833-global-vs-reachable-[[R5]]-v1/test_global_vs_reachable_v1.py -v` -> `PKG=$(ls -d research/gmi-833-global-vs-reachable-*v1)`
- `CORE.md:18` [R5] 43e95d07: `…python -I -O -B research/gmi-833-global-vs-reachable-[[R5]]-v1/test_global_vs_re…` -> `…python -I -B $PKG/test_global_vs_re…`
- `CORE.md:19` [R5] 43e95d07: `…python -I -B research/gmi-833-global-vs-reachable-[[R5]]-v1/global_vs_reachable_v1.py > /tmp/result.json` -> `…python -I -O -B $PKG/test_global_vs_reachable_v1.py -v`
- `CORE.md:20` [R5] 43e95d07: `cmp /tmp/result.json research/gmi-833-global-vs-reachable-[[R5]]-v1/RESULT_V1.json…` -> `python -I -B $PKG/global_vs_reachable_v1.py > /tmp/result.json…`
- `CORE.md` [inserted line] 43e95d07: `cmp /tmp/result.json $PKG/RESULT_V1.json`
- `CORE.md:25` [R4] 43e95d07: `… lifecycle Pareto [[R4]].…` -> `… lifecycle Pareto model selection.…`
- `FREEZE_V1.md:1` [R4,R5] 43e95d07: `…obal-vs-Reachable [[R5]] [[R4]] Freeze V1…` -> `…obal-vs-Reachable Architecture-Choice Freeze V1…`
- `FREEZE_V1.md:6` [R5] 43e95d07: `…ion J — `Separate optimal [[R5]] from reachable [[R5]].`…` -> `…ion J — `Separate the optimal candidate architecture from the reachable one.`…`
- `FREEZE_V1.md:11` [R5] 43e95d07: `…- branch: `research/874-global-vs-reachable-[[R5]]-v1`` -> `…- branch: the source branch carrying the tranche's frozen internal identifier (see the package directory name)`
- `FREEZE_V1.md:29` [R5] 43e95d07: `…registered finite [[R5]] set `M`, nonempty…` -> `…registered finite candidate architecture set `M`, nonempty…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:1` [R4,R5] 43e95d07: `…obal-vs-Reachable [[R5]] [[R4]] Theorems V1…` -> `…obal-vs-Reachable Architecture-Choice Theorems V1…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:5` [R5] 43e95d07: `…ne row: `Separate optimal [[R5]] from reachable [[R5]].`  …` -> `…ne row: `Separate the optimal candidate architecture from the reachable one.`  …`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:30` [R5] 43e95d07: `…nempty registered [[R5]] set;…` -> `…nempty registered candidate architecture set;…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:92` [R5] 43e95d07: `…justify “the same [[R5]] was selected.”…` -> `…justify “the same candidate architecture was selected.”…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:112` [R5] 43e95d07: `… or that a unique [[R5]] exists.…` -> `… or that a unique candidate architecture exists.…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:142` [R5] 43e95d07: `…Thus a [[R5]] can be globally d…` -> `…Thus a candidate architecture can be globally d…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:195` [R5] 43e95d07: `…- an empty [[R5]] universe;…` -> `…- an empty candidate architecture universe;…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:198` [R5] 43e95d07: `…- duplicated [[R5]] identities;…` -> `…- duplicated candidate identities;…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:215` [R4,R5] 43e95d07: `…- unique [[R5]] [[R4]];…` -> `…- a unique selected candidate;…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:218` [R5] 43e95d07: `…- prospective [[R5]]-transition predic…` -> `…- prospective architecture-transition predic…`
- `GLOBAL_VS_REACHABLE_THEOREMS_V1.md:222` [R4] 43e95d07: `…entally reachable [[R4]].…` -> `…entally reachable architecture choice.…`

### gmi-833-morphcap-v1
- `CORE.md:7` [R5] fd35f7c8: `…- [[R5]] equivalence = iso…` -> `…- mechanism-structure equivalence = iso…`
- `CORE.md:8` [R9] fd35f7c8: `…- legacy `[[R9]]` = quotient class under that equivalence;…` -> `…- the legacy species-style label = quotient class under that equivalence (paper term: computational-mechanism equivalence class);…`
- `FREEZE_V1.md:1` [R5] fd35f7c8: `…# GMI #833 [[R5]]/capability freeze…` -> `…# GMI #833 mechanism-structure/capability freeze…`
- `FREEZE_V1.md:23` [R5] fd35f7c8: `…ism signature and [[R5]] equivalence…` -> `…ism signature and mechanism-structure equivalence…`
- `FREEZE_V1.md:41` [R5] fd35f7c8: `…ehavior equal but [[R5]] inequivalent.…` -> `…ehavior equal but structurally inequivalent.…`
- `FREEZE_V1.md:42` [R5] fd35f7c8: `…response differs; [[R5]] inequivalent.…` -> `…response differs; structurally inequivalent.…`
- `FREEZE_V1.md:44` [R9] fd35f7c8: `…## SPECIES-1 — [[R9]]` -> `…## SPECIES-1 — mechanism equivalence classes (legacy species-style label)`
- `FREEZE_V1.md:46` [R9] fd35f7c8: `…Define legacy `[[R9]]` at scope `Omega` …` -> `…Define the legacy species-style label at scope `Omega` …`
- `FREEZE_V1.md:94` [R5] fd35f7c8: `…- [[R5]] equivalence fails…` -> `…- mechanism-structure equivalence fails…`
- `FREEZE_V1.md:96` [R5] fd35f7c8: `…- [[R5]]-equivalent witness…` -> `…- structurally equivalent witness…`
- `FREEZE_V1.md:115` [R4] fd35f7c8: `…n, or architecture [[R4]] is claimed.…` -> `…n, or architecture-family choice is claimed.…`
- `MORPHCAP_THEOREMS_V1.md:1` [R5] fd35f7c8: `…# [[R5]] equivalence and a…` -> `…# Mechanism-structure equivalence and a…`
- `MORPHCAP_THEOREMS_V1.md:17` [R3] fd35f7c8: `…e protected state [[R3]] and quotient only…` -> `…e protected state set and quotient only…`
- `MORPHCAP_THEOREMS_V1.md:35` [R5] fd35f7c8: `…## 2. MORPH-1 — [[R5]] equivalence…` -> `…## 2. MORPH-1 — mechanism-structure equivalence…`
- `MORPHCAP_THEOREMS_V1.md:62` [R5] fd35f7c8: `…races agree. Thus [[R5]] equivalence is in…` -> `…races agree. Thus mechanism-structure equivalence is in…`
- `MORPHCAP_THEOREMS_V1.md:64` [R5] fd35f7c8: `…This prevents the term `[[R5]]` from degenerating into either source-code syntax or task-output equality alone.…` -> `…This prevents the equivalence from degenerating into either source-code syntax or task-output equality alone (the parent tranche’s original name for the relation is retained in its own freeze).…`
- `MORPHCAP_THEOREMS_V1.md:66` [R9] fd35f7c8: `…## 3. SPECIES-1 — [[R9]]` -> `…## 3. SPECIES-1 — mechanism equivalence classes (legacy species-style label)`
- `MORPHCAP_THEOREMS_V1.md:68` [R9] fd35f7c8: `…The legacy object called a **[[R9]]** is defined, witho…` -> `…The legacy object, named with a species-style label, is defined, witho…`
- `MORPHCAP_THEOREMS_V1.md:101` [R5] fd35f7c8: `…# Theorem CAP-1 — [[R5]] invariance…` -> `…# Theorem CAP-1 — mechanism-structure invariance…`
- `MORPHCAP_THEOREMS_V1.md:186` [R5] fd35f7c8: `… do **not** imply same [[R5]];…` -> `… do **not** imply the same mechanism structure;…`

### gmi-833-[[R6]]-equivariance-v1
- `CORE.md:1` [R6] 2d74802b: `…# gmi-833-[[R6]]-equivariance-v1` -> `…# gmi-833-presentation-equivariance-v1 (internal identifier unchanged; paper-facing title below)`
- `CORE.md:3` [R6] 2d74802b: `This tranche formalizes finite semantic presentation [[R6]] as bijective state-label transports, proves identity/inverse/composition, proves canonical mechanism fingerprints invariant under valid [[R6]], and checks quotient-level directed transform geometry is unchanged when all endpoint presentations are [[R6]] with burdens fixed.` -> `# GMI #833 finite semantic presentation-relabeling equivariance`
- `CORE.md:5` [R6] 2d74802b: `Neutral-looking semantic mutations are hostile failures. Search/reachability invariance is explicitly not inferred from semantic [[R6]] invariance.…` -> `This tranche formalizes finite semantic presentation relabelings (bijective state-label transports; the historical internal term is retired from paper-facing prose) as bijective state-label transports, proves identity/inverse/composition, proves canonical mechanism fingerprints invariant under valid relabelings, and checks quotient-level directed transform geometry is unchanged when all endpoint presentations are relabeled with burdens fixed.…`
- `CORE.md` [inserted line] 2d74802b: ``
- `CORE.md` [inserted line] 2d74802b: `Neutral-looking semantic mutations are hostile failures. Search/reachability invariance is explicitly not inferred from semantic presentation-relabeling invariance.`
- `CORE.md:10` [R6] 2d74802b: `python -I -B research/gmi-833-[[R6]]-equivariance-v1/test_remint_equivariance_v1.py -v` -> `PKG=$(ls -d research/gmi-833-presentation-equivariance-lane 2>/dev/null || ls -d research/gmi-833-*equivariance*v1)`
- `CORE.md:11` [R6] 2d74802b: `…python -I -O -B research/gmi-833-[[R6]]-equivariance-v1/test_remint_equiv…` -> `…python -I -B $PKG/test_remint_equiv…`
- `CORE.md:12` [R6] 2d74802b: `…python -I -B research/gmi-833-[[R6]]-equivariance-v1/remint_equivariance_v1.py` -> `…python -I -O -B $PKG/test_remint_equivariance_v1.py -v`
- `CORE.md` [inserted line] 2d74802b: `python -I -B $PKG/remint_equivariance_v1.py`
- `CORE.md` [inserted line] 2d74802b: `(The test/executor file names are frozen internal identifiers.)`
- `CORE.md` [inserted line] 2d74802b: ``
- `FREEZE_V1.md:1` [R6] 2d74802b: `…# GMI #833 [[R6]] equivariance v1 —…` -> `…# GMI #833 presentation-relabeling equivariance v1 —…`
- `FREEZE_V1.md:10` [R3] 2d74802b: `…e reachable state [[R3]] and initial state…` -> `…e reachable state set and initial state…`
- `FREEZE_V1.md:18` [R6] 2d74802b: `…A **presentation [[R6]]** is a bijection …` -> `…A **presentation relabeling** is a bijection …`
- `FREEZE_V1.md:22` [R6] 2d74802b: `…1. valid [[R6]] form a finite gro…` -> `…1. valid relabelings form a finite gro…`
- `FREEZE_V1.md:23` [R6] 2d74802b: `…under every valid [[R6]];…` -> `…under every valid relabeling;…`
- `FREEZE_V1.md:24` [R5,R6] 2d74802b: `…3. two pure [[R6]] therefore land in the same registered [[R5]] quotient class;…` -> `…3. two pure relabelings therefore land in the same registered mechanism quotient class;…`
- `FREEZE_V1.md:25` [R6] 2d74802b: `…ose endpoints are [[R6]] mechanisms and wh…` -> `…ose endpoints are relabeled mechanisms and wh…`
- `FREEZE_V1.md:26` [R6] 2d74802b: `…e escape fail the [[R6]]-preservation audi…` -> `…e escape fail the relabeling-preservation audi…`
- `FREEZE_V1.md:28` [R6] 2d74802b: `…7. [[R6]] invariance does *…` -> `…7. relabeling invariance does *…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:1` [R6] 2d74802b: `…3 finite semantic [[R6]] equivariance v1…` -> `…3 finite semantic presentation-relabeling equivariance v1…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:8` [R5] 2d74802b: `… the current #833 [[R5]] work:…` -> `… the current #833 mechanism-structure work:…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:12` [R3] 2d74802b: `…with finite state [[R3]] `X`, initial stat…` -> `…with finite state set `X`, initial stat…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:14` [R6] 2d74802b: `…tate-presentation [[R6]]** is a bijection …` -> `…tate-presentation relabeling** is a bijection …`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:23` [R6] 2d74802b: `…lds is not a pure [[R6]] at this scope.…` -> `…lds is not a pure relabeling at this scope.…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:25` [R6] 2d74802b: `…## 2. GAUGE-1A — [[R6]] form a groupoid…` -> `…## 2. GAUGE-1A — relabelings form a groupoid…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:29` [R6] 2d74802b: `…nite presentation [[R6]] and their inverti…` -> `…nite presentation relabelings and their inverti…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:43` [R6] 2d74802b: `…For every valid [[R6]] `r:M->M'`,…` -> `…For every valid relabeling `r:M->M'`,…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:49` [R6] 2d74802b: `…usts all `3! = 6` [[R6]] of a three-state …` -> `…usts all `3! = 6` relabelings of a three-state …`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:51` [R5] 2d74802b: `…## 4. Quotient [[R5]] consequence…` -> `…## 4. Quotient mechanism-structure consequence…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:53` [R5,R6] 2d74802b: `…The current [[R5]] object is a presentation-independent equivalence class of the registered mechanism structure. Since every pure [[R6]] has the same canonical fingerprint, all [[R6]] presentations map…` -> `…The current mechanism-structure object is a presentation-independent equivalence class of the registered mechanism structure. Since every pure relabeling has the same canonical fingerprint, all relabeled presentations map…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:61` [R6] 2d74802b: `… is independently [[R6]] by a valid semantic [[R6]] and the correspon…` -> `… is independently relabeled by a valid semantic relabeling and the correspon…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:63` [R6] 2d74802b: `…rs. Independently [[R6]] all three mechani…` -> `…rs. Independently relabeling all three mechani…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:65` [R5] 2d74802b: `…nce needed before [[R5]] distances can be …` -> `…nce needed before mechanism-structure distances can be …`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:69` [R6] 2d74802b: `…A claimed [[R6]] is rejected when …` -> `…A claimed relabeling is rejected when …`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:77` [R6] 2d74802b: `…y is not semantic [[R6]] invariance.…` -> `…y is not semantic relabeling invariance.…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:83` [R6] 2d74802b: `…. Thus a semantic [[R6]] theorem cannot er…` -> `…. Thus a semantic relabeling theorem cannot er…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:85` [R5] 2d74802b: `… P3/P4 programme: [[R5]] conclusions must …` -> `… P3/P4 programme: mechanism-structure conclusions must …`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:91` [R6] 2d74802b: `…- [[R6]] identity, inverse…` -> `…- relabeling identity, inverse…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:92` [R6] 2d74802b: `…- two valid [[R6]] yield different c…` -> `…- two valid relabelings yield different c…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:93` [R6] 2d74802b: `… passes as a pure [[R6]];…` -> `… passes as a pure relabeling;…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:94` [R6] 2d74802b: `…er valid endpoint [[R6]] with unchanged bu…` -> `…er valid endpoint relabelings with unchanged bu…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:95` [R6] 2d74802b: `…- a non-bijective [[R6]] is accepted;…` -> `…- a non-bijective relabeling is accepted;…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:96` [R6] 2d74802b: `…- semantic [[R6]] invariance is pro…` -> `…- semantic relabeling invariance is pro…`
- `REMINT_EQUIVARIANCE_THEOREMS_V1.md:101` [R5] 2d74802b: `…th the registered [[R5]] signature and tra…` -> `…th the registered mechanism signature and tra…`

### gmi-833-search-law-[[R5]]-change-v1
- `CORE.md:1` [R5] 15ef6f92: `…I #833 Search-Law [[R5]] Change V1…` -> `…I #833 Search-Law Architecture Change V1…`
- `CORE.md:5` [R5] 15ef6f92: `…> Derive when search law changes observed [[R5]].…` -> `…> Derive when a search law changes the observed candidate architecture.…`
- `CORE.md:16` [R5] 15ef6f92: `…ready derives the [[R5]] selected by one registered deterministic charged search trace at a finite budget. This child compares **two** such laws on the same [[R5]] universe and objective semantics and derives exactly when their observed morphologies disagree.…` -> `…ready derives the candidate architecture selected by one registered deterministic charged search trace at a finite budget. This child compares **two** such laws on the same candidate universe and objective semantics and derives exactly when their observed architectures disagree.…`
- `CORE.md:22` [R5] 15ef6f92: `…lue but different [[R5]] identities.…` -> `…lue but different candidate identities.…`
- `CORE.md:27` [R5] 15ef6f92: `python -I -B research/gmi-833-search-law-[[R5]]-change-v1/test_search_law_morphology_change_v1.py -v` -> `PKG=$(ls -d research/gmi-833-search-law-*v1)`
- `CORE.md:28` [R5] 15ef6f92: `…python -I -O -B research/gmi-833-search-law-[[R5]]-change-v1/test_search_law_m…` -> `…python -I -B $PKG/test_search_law_m…`
- `CORE.md:29` [R5] 15ef6f92: `…python -I -B research/gmi-833-search-law-[[R5]]-change-v1/search_law_morphology_change_v1.py > /tmp/result.json` -> `…python -I -O -B $PKG/test_search_law_morphology_change_v1.py -v`
- `CORE.md:30` [R5] 15ef6f92: `cmp /tmp/result.json research/gmi-833-search-law-[[R5]]-change-v1/RESULT_V1.json…` -> `python -I -B $PKG/search_law_morphology_change_v1.py > /tmp/result.json…`
- `CORE.md` [inserted line] 15ef6f92: `cmp /tmp/result.json $PKG/RESULT_V1.json`
- `FREEZE_V1.md:1` [R5] 15ef6f92: `…#833 — Search-Law [[R5]]-Change Freeze V1…` -> `…#833 — Search-Law Architecture-Change Freeze V1…`
- `FREEZE_V1.md:6` [R5] 15ef6f92: `… J — `Derive when search law changes observed [[R5]].`…` -> `… J — `Derive when a search law changes the observed candidate architecture.`…`
- `FREEZE_V1.md:11` [R5] 15ef6f92: `…- branch: `research/879-search-law-[[R5]]-change-v1`` -> `…- branch: the source branch carrying the tranche's frozen internal identifier (see the package directory name)`
- `FREEZE_V1.md:21` [R5] 15ef6f92: `…ite search-budget [[R5]] receipt:…` -> `…ite search-budget receipt:…`
- `FREEZE_V1.md:22` [R5] 15ef6f92: `…  `research/gmi-833-finite-search-budget-[[R5]]-v1/RESULT_V1.json`, Git blob `4ea315…` -> `…  the sibling finite-search-budget tranche's `RESULT_V1.json` (directory = that tranche's frozen internal identifier), Git blob `4ea315…`
- `FREEZE_V1.md:29` [R6] 15ef6f92: `…- #864 semantic [[R6]] equivariance with…` -> `…- #864 semantic presentation-relabeling equivariance with…`
- `FREEZE_V1.md:33` [R5] 15ef6f92: `…d finite nonempty [[R5]] set `M`, one exac…` -> `…d finite nonempty candidate architecture set `M`, one exac…`
- `FREEZE_V1.md:35` [R5] 15ef6f92: `…1. each observed [[R5]] `I_j(B)` is piece…` -> `…1. each observed candidate architecture `I_j(B)` is piece…`
- `FREEZE_V1.md:36` [R5] 15ef6f92: `…es with different [[R5]] identities;…` -> `…es with different candidate identities;…`
- `FREEZE_V1.md:37` [R5] 15ef6f92: `…w need not change observed [[R5]];…` -> `…w need not change the observed candidate architecture;…`
- `FREEZE_V1.md:39` [R5] 15ef6f92: `…h can still leave [[R5]] identity search-l…` -> `…h can still leave candidate identity search-l…`
- `FREEZE_V1.md:53` [R5] 15ef6f92: `… with no observed [[R5]] change. General p…` -> `… with no observed architecture change. General p…`
- `FREEZE_V1.md:65` [R5] 15ef6f92: `…- fabricated [[R5]] before any comple…` -> `…- a fabricated candidate before any comple…`
- `FREEZE_V1.md:68` [R5] 15ef6f92: `…- false `different law => different [[R5]]` promotion;…` -> `…- a false `different law => different observed candidate` promotion;…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:1` [R5] 15ef6f92: `…I #833 Search-Law [[R5]]-Change Theorems V…` -> `…I #833 Search-Law Architecture-Change Theorems V…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:5` [R5] 15ef6f92: `…row: `Derive when search law changes observed [[R5]].`  …` -> `…row: `Derive when a search law changes the observed candidate architecture.`  …`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:13` [R8] 15ef6f92: `…review lenses and [[R8]]` -> `…review lenses and strongest-parent subsumption`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:18` [R5] 15ef6f92: `…disagreement from [[R5]]-identity disagree…` -> `…disagreement from candidate-identity disagree…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:29` [R6] 15ef6f92: `…ly keeps semantic [[R6]] invariance separa…` -> `…ly keeps semantic presentation-relabeling invariance separa…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:37` [R5] 15ef6f92: `…a finite nonempty [[R5]] set;…` -> `…a finite nonempty candidate architecture set;…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:68` [R5] 15ef6f92: `…servable selected [[R5]], not arbitrary in…` -> `…servable selected candidate architecture, not arbitrary in…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:85` [R5] 15ef6f92: `…ce does not imply identical [[R5]].…` -> `…ce does not imply an identical candidate architecture.…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:87` [R5] 15ef6f92: `…w need not change observed [[R5]]` -> `…w need not change the observed candidate architecture`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:89` [R5] 15ef6f92: `…the same observed [[R5]] for one budget, m…` -> `…the same observed candidate architecture for one budget, m…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:125` [R5] 15ef6f92: `…que, every prefix [[R5]] attaining that va…` -> `…que, every prefix candidate attaining that va…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:131` [R5] 15ef6f92: `…ch need not erase [[R5]] identity dependenc…` -> `…ch need not erase candidate-identity dependenc…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:209` [R4] 15ef6f92: `…#877 owns one-law finite-budget prefix [[R4]], regret monotonic…` -> `…#877 owns the one-law finite-budget prefix terminal, regret monotonic…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:215` [R4] 15ef6f92: `…### Algorithm-[[R4]] / anytime parents…` -> `…### Algorithm-choice / anytime parents…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:217` [R5] 15ef6f92: `…is only the exact [[R5]]-observable integr…` -> `…is only the exact architecture-observable integr…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:223` [R5] 15ef6f92: `…mpty or duplicate [[R5]] universes;…` -> `…mpty or duplicate candidate architecture universes;…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:228` [R5] 15ef6f92: `…ered on different [[R5]] universes;…` -> `…ered on different candidate universes;…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:231` [R4,R5] 15ef6f92: `…didate completes, [[R4]] remains typed `NO_EVALUATED_CANDIDATE`; no [[R5]] or objective valu…` -> `…didate completes, the terminal remains typed `NO_EVALUATED_CANDIDATE`; no candidate or objective valu…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:239` [R5] 15ef6f92: `…aw change changes [[R5]];…` -> `…aw change changes the observed candidate architecture;…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:240` [R5] 15ef6f92: `…rch-law-invariant [[R5]] identity under gl…` -> `…rch-law-invariant candidate identity under gl…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:244` [R5] 15ef6f92: `…spective held-out [[R5]] transitions;…` -> `…spective held-out architecture transitions;…`
- `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md:248` [R5] 15ef6f92: `…rministic two-law [[R5]]-disagreement theo…` -> `…rministic two-law architecture-disagreement theo…`

## Remaining corpus at this commit

Gate findings outside the 12 migrated packages (rule ids in parentheses): 267 hits in 31 packages,
plus 31 definitional quote hits inside this package's own `FREEZE_V1.md` (freeze §1 note).

| package | hits |
|---|---|
| `gmi-833-history-switching-hysteresis-v1` | 39 |
| `gmi-833-[[R5]]-[[R4]]-schema-v1` | 33 |
| `gmi-833-[[R5]]-[[R4]]-v1` | 28 |
| `gmi-833-g0-cost-privilege-v1` | 15 |
| `gmi-833-robustness-controls-v1` | 15 |
| `gmi-833-developmental-potential-evolvability-v1` | 12 |
| `gmi-833-g0-register-core-v1` | 10 |
| `gmi-833-heldout-20-transitions-v1` | 10 |
| `gmi-833-no-smuggling-audit-v1` | 10 |
| `gmi-833-transform-geometry-v1` | 10 |
| `gmi-833-pareto-topology-v1` | 9 |
| `gmi-833-corpus-census-v1` | 7 |
| `gmi-833-aj4-process-organizations-v1` | 6 |
| `gmi-833-stochastic-predictive-v1` | 6 |
| `gmi-833-update-law-nfl-v1` | 6 |
| `gmi-833-aj9b-k01-blind-recovery-v1` | 5 |
| `gmi-833-capability-bounds-interactions-v1` | 5 |
| `gmi-833-cognitive-reaudit-v1` | 5 |
| `gmi-833-aj9c-k02-blind-recovery-v1` | 4 |
| `gmi-833-aj9d-k03-blind-recovery-v1` | 4 |
| `gmi-833-capability-abstention-v1` | 4 |
| `gmi-833-g0-stochastic-update-v1` | 4 |
| `gmi-833-aj9e-k04-blind-recovery-v1` | 3 |
| `gmi-833-aj9f-k05-blind-recovery-v1` | 3 |
| `gmi-833-global-uncertainty-v1` | 3 |
| `gmi-833-parent-equivalence-v1` | 3 |
| `gmi-833-aj5-g0-compilation-v1` | 2 |
| `gmi-833-aj7-objective-provenance-v1` | 2 |
| `gmi-833-real-transition-protocol-v1` | 2 |
| `gmi-833-aj0-foundation-scope-v1` | 1 |
| `gmi-833-aj8-intelligence-boundary-v1` | 1 |

By rule: R4=98, R5=92, R6=28, R3=20, R8=13, R1=9, R7=4, R2=3.

Packages named `gmi-833-aj*` belong to the aj-lane; their rows are listed for inventory only.
New corpus packages that landed on main after this migration's freeze base add to the remaining
work; the freeze §1 corpus snapshot (24 packages) is superseded by the live corpus (50 packages).
