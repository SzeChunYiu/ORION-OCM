# FREEZE — `gmi-833-ab-residual-definitions-v1` (issue #833, section AB)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, test,
receipt, theorem note, definition artifact or workflow file of this package
exists. `git log --reverse -- research/gmi-833-ab-residual-definitions-v1/`
must show this file, alone, first.

## 1. Source pin

- `source_main` = `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue comment under reconciliation: `5684607872`, anchor
  `### AB. Academic terminology and ontology normalization`
- live comment bytes at freeze: 28361 (LF only).

## 2. Claim ceiling

`DECLARED_DEFINITION_ARTIFACT_V1`

The two rows in scope are **authoring** rows: their governing verbs are
`parent-subtract` and `Define`. They are discharged by producing the artifact
they name, with every component the row itself names, plus a checker that
verifies completeness, exactness and non-degeneracy. A definition is not an
empirical result: this package establishes that the artifacts exist, are
complete against the rows' own component lists, and are internally consistent.
It establishes nothing about whether GMI is in fact novel with respect to
Rice, and nothing about where any GMI claim sits on the ladder.

## 3. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Explicitly parent-subtract Rice-style **algorithm selection**: problem space, feature space, algorithm space, performance space, selection mapping.
    - [ ] Define a novelty ladder using those academically interpretable levels.

**No neighboring row is earned here.** Explicitly NOT earned:

    - [ ] Replace paper-facing `obligation` with `task`, `specification`, or `formal/behavioral specification` according to exact semantics; formal methods uses **formal specification** for a mathematical description of intended system behavior.

(corpus-mutating verb `Replace`; owned by `gmi-833-terminology-migration-v1`)
and no row of AA, AC or AD.

## 4. The AB25 antecedent (declared before implementation, and the reason)

The AB tranche's anti-invention guard requires every term a package demands to
occur literally in the row it is demanded of. AB25 is
`Define a novelty ladder using those academically interpretable levels.` —
a **back-reference**. The levels are not in AB25's own text. They are in the
row immediately above it, which reads, verbatim at `source_main`:

    - [x] Audit `novel intelligence`; distinguish **novel implementation**, **novel architecture**, **novel algorithmic mechanism**, **novel model class**, **novel computational paradigm/domain**, and **novel capability profile**.

That row is **AB25's declared antecedent**, fixed here in advance. The six
levels are exactly the six bolded terms of that row, extracted from its text,
and the guard is asserted against the antecedent's verbatim text. The guard is
not weakened to make AB25 pass; its resolution target is declared, once, before
any level is written. AB08 needs no such exception: its five components
(problem space, feature space, algorithm space, performance space, selection
mapping) occur literally in AB08's own text and are extracted from it.

## 5. What will be produced and checked

- `RICE_PARENT_SUBTRACTION_V1.md` — one section per Rice component, each
  stating: Rice's object, the GMI object that plays that role, the match
  verdict (`ABSORBED` / `PARTIAL` / `DIVERGENT`), what Rice already supplies,
  and the residual. A final section states what is **not** claimed novel with
  respect to Rice.
- `NOVELTY_LADDER_V1.md` — one section per level, each stating: an
  **operational criterion** (a decidable test with a named witness), a
  **falsifier**, the **parent literature** for the level, and the
  **demotion rule** — what the claim becomes when the criterion fails.
- `check_definitions_v1.py` / an independent oracle: all five Rice components
  present exactly once, each with all five fields non-empty and a verdict in
  the declared vocabulary; all six ladder levels present exactly once, in the
  declared order, each with criterion, falsifier, parent and demotion rule;
  the ladder is a strict total order whose demotion rule points strictly
  downward and terminates; no level's criterion is a restatement of another's.

## 6. Forbidden promotions

- `GMI_IS_NOVEL_WRT_RICE`, `RICE_SUBSUMED`, `PARENT_EXHAUSTED` — a subtraction
  table records what the parent already owns; it does not adjudicate novelty.
- `LADDER_APPLIED`, `CLAIM_IS_AT_LEVEL_N` — no GMI claim is placed on the
  ladder here. Placement is a separate act with its own evidence.
- `ALL_PARENTS_EXHAUSTED`, `CITATIONS_VERIFIED`, `NOVELTY_ESTABLISHED`.
- `CORPUS_TERMINOLOGY_CLEAN`, `MIGRATION_COMPLETE`.
- `ANALYTIC_PROOF`.

## 7. Parent ownership (declared before implementation)

- `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md`
  blob `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054` — **owns** crosswalk row 40
  (`novel intelligence`, which names the ladder as a sequence) and row 25
  (`selection`, which cites Rice). The crosswalk **cites** Rice; it does not
  subtract him, and it gives no level an operational criterion. That gap is
  what this package fills.
- `research/gmi-833-ab-terminology-harness-v1/AB_CROSSWALK_EXTENSION_V1.md`
  — owns the `novel implementation` extension term.
- `research/gmi-833-tranche-ab-ac-lit/WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md`
  blob `e4f1116182d16e6e74f971510b0ef883aaf16d15` — owns the six contribution
  kinds, which are a *different* axis from the novelty ladder and are not
  merged with it here.
- `research/gmi-833-parent-equivalence-v1/`, `research/parent-absorption-v1/`
  (where present on `main`) — own parent reduction as an operation.

External parents restated, not claimed novel: Rice, "The algorithm selection
problem", *Advances in Computers* 15 (1976),
doi:10.1016/S0065-2458(08)60520-3 — the four-space model and the selection
mapping are his; Smith-Miles, "Cross-disciplinary perspectives on
meta-learning for algorithm selection", *ACM Computing Surveys* 41(1) 2008,
doi:10.1145/1456650.1456656 — the modern survey of the same model;
Rice's performance-space and feature-space construction is restated, never
re-derived. Wolpert & Macready, "No free lunch theorems for optimization",
*IEEE TEC* 1(1) 1997, doi:10.1109/4235.585893. For the ladder:
Lehman & Stanley, "Exploiting open-endedness to solve problems through the
search for novelty", ALIFE XI (2008) — definitional novelty; Elsken, Metzen &
Hutter, "Neural architecture search: a survey", *JMLR* 20(55) 2019 — the
architecture level; Kuhn, *The Structure of Scientific Revolutions* (1962) —
the paradigm level as a term of art, cited for provenance and explicitly not
as a formal criterion.

**Residual contribution claimed here:**
(a) the first explicit component-by-component subtraction of Rice's algorithm
    selection from the GMI selection construct, with a per-component verdict
    and a named residual;
(b) the first operational criterion, falsifier, parent and demotion rule for
    each of the six novelty-ladder levels the AB rows name — the crosswalk
    names the levels and supplies none of these;
(c) a checker binding both artifacts to the rows' own verbatim component
    lists, with the antecedent resolution for AB25 declared in advance.

## 8. Evidence standard binding this package

Two materially independent routes for every computational claim; hostiles that
are detected AND whose perturbed quantity is asserted to have moved; a null the
true result beats; exact arithmetic only; stdlib only; runnable under
`python3 -I -B` and `python3 -I -O -B`; Python 3.8-compatible.
