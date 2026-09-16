# GMI #833 terminology migration v1 — freeze

Parent issue: #833, Section A box: "Replace ambiguous uses of `obligation` in paper-facing theory
with academically grounded terminology (`task`, `behavioral specification`, `requirement`, etc.)
while preserving exact legacy mappings."
Base main: `88d28de396a7d005c12de88b44aa258ae34dd9fc`.
Gate authority: `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py`
+ `GMI_TERMINOLOGY_CROSSWALK_V2.md` (row 2 + migration-rule table).
Status: PRE-EDIT FREEZE (this file committed before any corpus edit).

## 1. Target corpus (frozen)

Paper-facing markdown under every `research/gmi-833-*/` package — 24 packages, of which 23 carry
gate hits. Other `research/*` packages (e.g. `gmi-grand-unification-v1`, `gmi-section-e-*`,
`gmi-theory-foundations-v1`) are OUT OF SCOPE for this migration and are listed as such; they belong
to other lanes/programmes.

Pre-edit gate inventory (measured on this freeze commit, `--json` over all `research/gmi-833-*/`):

- **371 gate hits at 320 distinct file:line sites**, exit 1;
- by term: bare morphology 155, remint 97, bare selection 53, bare carrier 33,
  obligation 10, parent subtraction 9, machine species 5, negative twin 5, bare prior-free 4;
- FOUNDATION_THEOREMS_V1.md alone: 7 hits (obligation x3, bare prior-free x1, bare carrier x1,
  bare selection x2) — the Section-A box's named instance.

Note: the gate self-skips authority artifacts
(`GMI_TERMINOLOGY_CROSSWALK_V2.md`, `BANNED_PAPER_TERMS_V1.md`, `EXPERT_LITERATURE_LANES_V1.md`,
`WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md`, `GMI_TERMINOLOGY_CI_GATE_V1.py`) via `_authority_doc`;
quoted/named banned terms inside this package's own docs are likewise definitional, not live prose.

## 2. Replacement policy (per crosswalk row 2 + migration-rule table)

| gate term | policy |
|---|---|
| obligation | context-selected replacement: `task` / `behavioral specification` / `formal specification` / `requirement`; where the sentence is about the frozen governance bundle itself, name it (`claim-governance items`, `checklist obligations` → `frozen acceptance items`) and never reuse the banned word as live prose |
| bare prior-free | `architecture-prior-free` with the residual-prior ledger named, or `architecture-agnostic`/`architecture-uncommitted`; never a literal no-assumptions claim |
| bare carrier | `state carrier`/`state space`/`state representation` with the representation named (or `realization/version set`, `instance set` where that is the actual object) |
| bare selection | state which of the five kinds (algorithm/model/architecture/configuration/evolutionary) or use the sanctioned compound already registered in the line's context (`candidate selection`, `morphology selection`, `sample-selection bias` with its Heckman citation, etc.) |
| bare morphology | `computational architecture` / `model class` / `mechanism structure` per context; retained ONLY where the crosswalk's sanctioned sense applies ("structure across heterogeneous computational organizations") and the line carries that qualifier |
| remint | `presentation relabeling` / `independent regeneration` / `relabeling control` per the exact variant the line describes (bijective state-label transport = presentation relabeling; fresh random source = independent regeneration) |
| negative twin | `matched negative control` |
| parent subtraction | `strongest-parent subsumption analysis` (or `strongest-baseline comparison` where comparison is meant) |
| machine species | `computational-mechanism equivalence class`, with the legacy name preserved as a quoted object ("historically: machine species") |

Legacy mapping PRESERVATION rule: legacy object names inside math and frozen identifiers
(`Omega`, `Species_Omega`, claim-ceiling strings, schema names, receipt keys, package/file names)
STAY UNCHANGED. Each first paper-facing use gains a one-time legacy-mapping note, e.g.
"Theorem BS-1 — conservative legacy claim-governance map (historically: the obligation object
`Omega`)". The migration is PAPER-RENAME only: semantics, theorem statements, math, premise sets,
claim ceilings, and frozen identifiers are untouched.

## 3. Preservation rule (custody)

- Frozen `RESULT_V1.json` / receipt JSONs are NEVER edited, for any reason.
- `.py` executors/tests and their embedded claim strings are NEVER edited (out of gate scope anyway:
  the gate scans `.md` only).
- Package and file NAMES are internal tooling identifiers: untouched (PAPER-RENAME, not filesystem
  rename). `CORPUS_TERMINOLOGY_MIGRATED` remains a forbidden promotion — the claim ceiling of this
  package is Section-A scope only (see section 5).
- Per-package custody check: each target package's `MANIFEST_V1.json` was inspected for sha256/blob
  bindings over `.md` files — ZERO exist (manifests bind receipts only; the single `.md` blob
  citation in any freeze doc points to `research/gmi-grand-unification-v1/`, outside this corpus).
  Package tests assert on JSON receipts, never on `.md` content (`test_ab_ac.py` reads only its own
  authority artifacts). Re-verified per package at edit time; any drift discovered mid-edit halts
  that file and is recorded DEFERRED in `MIGRATION_LOG_V1.md`.

## 4. Edit discipline

- Minimal-diff, line-scoped edits only; no reflow, no reordering, no heading renumbering.
- Each edit logged in `MIGRATION_LOG_V1.md` (file, line, before → after, crosswalk rule).
- If an edit would need a semantic change (not just wording), the line is LEFT UNCHANGED and logged
  DEFERRED with the reason. Expected DEFERRED population: zero; a nonzero population is reported,
  never silently absorbed.
- Legacy names may continue to appear ONLY inside quoted/named-object constructions
  (`legacy \`machine species\``, "historically written ..."), which the gate's own design accepts
  when they are in the package's authority files — for non-authority corpus files the construction
  must avoid the literal banned token: write `legacy claim-governance object`, `historically:
  species-style label`, etc., so the gate reads clean at scope.

## 5. Claim ceiling

Earned at GREEN scope (gate exit 0 over all `research/gmi-833-*/`, tests pass, CI wired):

`TERMINOLOGY_MIGRATION_AT_GMI_833_PAPER_FACING_SCOPE`

Forbidden promotions:

- `CORPUS_TERMINOLOGY_MIGRATED` (corpus-wide = other research/* packages; still open);
- internal tooling identifiers renamed (they are not);
- any semantic/mathematical change claimed (none is made);
- `GMI_833_FOUNDATION_V1_FORMALIZED...` or any other package's ceiling.
