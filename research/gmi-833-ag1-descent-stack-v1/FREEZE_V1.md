# FREEZE_V1 - gmi-833-ag1-descent-stack-v1

## Claim ceiling

`AG1_AG8_TYPED_F0_F9_FOUNDATION_DEPENDENCY_DAG_AND_PRIMITIVE_PROVENANCE_AT_REGISTERED_833_OBJECT_SCOPE`

Forbidden promotions: `ABSOLUTE_BOTTOM_LAYER_PROVEN`, `F0_IS_UNIQUE`, `LAYER_ASSIGNMENT_IS_ONTOLOGY`,
`DAG_ACYCLICITY_PROVES_FOUNDATIONAL_PRIORITY`, `G0_IRREDUCIBILITY_DISPROVED_IN_GENERAL`, `COMPLETE_GMI`.

## What this package is

A machine-readable `FOUNDATION_DEPENDENCY_DAG_V1` over layers `F0..F9` as stated in issue #833
comment `5693520829` section AG1, carrying:

- a **node registry**: every registered #833 object placed at exactly one layer, with the merged
  package that owns it;
- **typed arrows** drawn from a closed vocabulary
  `DERIVATION | FREE_CONSTRUCTION | INTERPRETATION_MODEL | COMPILATION | DEVELOPMENT | SELECTION | MUTUAL_INTERPRETATION`;
- a **primitive provenance table**: every node declared primitive names the lower layer it is
  introduced from;
- **metatheoretic assumption exposure** on every bottom node, tagged with the AJ12 assumption
  classes;
- **acyclicity** over all non-`MUTUAL_INTERPRETATION` edges, with `MUTUAL_INTERPRETATION` edges
  required to be symmetric and same-layer.

AI0's `GMI_THEORY_DEPENDENCY_DAG.json` is **interface-keyed** (`GEN/DEV/REQ/REL/CAP/SEL/EVID`)
and is not a layer-keyed foundation stack. This package does not replace it; the AI0 authority map
remains authoritative for interface ownership, and every AG1 node cites its AI0 node where one exists.

## Rows this package may reconcile

- comment `5693520829` / anchor `### AG1 — Canonical descent stack`
  - `- [ ] Formalize every arrow `F_i -> F_(i+1)` as derivation, free construction, interpretation/model, compilation, development or selection rather than prose.`
- comment `5693520829` / anchor `### AG1 — Canonical descent stack`
  - `- [ ] State exactly which #833 object currently lives at each layer.`
- comment `5693520829` / anchor `### AG1 — Canonical descent stack`
  - `- [ ] Demote `G0` from “bottom substrate” wording to the appropriate F3/F4 presentation layer unless lower-layer irreducibility is actually proved.`
- comment `5693520829` / anchor `### AG1 — Canonical descent stack`
  - `- [ ] Require every claimed primitive to name the lower layer from which it is introduced.`
- comment `5693520829` / anchor `### AG7 — Intelligence should emerge above common non-intelligent substrate`
  - `- [ ] Identify the first layer at which their properties diverge.`
- comment `5693520829` / anchor `### AG8 — Recursive foundation descent protocol`
  - `- [ ] Integrate this as a downward counterpart to AA/AD recursive gap closure and HSG Reflexive Generalization Closure.`
- comment `5693520829` / anchor `### AG8 — Recursive foundation descent protocol`
  - `- [ ] Build a machine-readable `FOUNDATION_DEPENDENCY_DAG` from F0 through F9.`
- comment `5693520829` / anchor `### AG8 — Recursive foundation descent protocol`
  - `- [ ] Forbid cycles in “derived from” edges unless explicitly typed as mutual interpretation/equivalence rather than derivation.`
- comment `5693520829` / anchor `### AG8 — Recursive foundation descent protocol`
  - `- [ ] Require every apparent bottom node to expose its metatheoretic assumptions.`

## Rows this package may NOT reconcile

Every AG/AH row not listed above. In particular AG1 does **not** earn AG6 rows on universal bases,
AG9 foundation-relativity rows (owned by AJ12/AJ13), or AG2 signature/free-syntax rows.

## Frozen source

- `source_main` commit: `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`
- Issue: SzeChunYiu/ORION-OCM#833
- Checklist comments in scope: `5693520829` (sections AG, AG0-AG13) and `5693590252` (sections AH, AH0-AH10).
- Row texts are pinned byte-exact in `research/gmi-833-agah-map-v1/AGAH_ROWS_V1.json` (75 open rows at freeze time: 55 in comment 5693520829, 20 in comment 5693590252).

## Order discipline

This freeze is committed **before** any executor, test, receipt or workflow of this package exists. `git log --follow` over this package must show this file in a commit strictly earlier than every implementation commit. An audit (#976) filed a POST_HOC_SUSPECT because a freeze postdated its result by 89 minutes; the ordering gate here is the direct remedy.

## No neighboring row is earned here.

Only the rows listed above may be reconciled by this package. Any other AG/AH row, any row in the #833 body sections A-M, and any row in comments Z / AA-AF / AI / AJ remain open and untouched by this tranche.
