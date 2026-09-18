# AG1 / AG8 named results

Scope: the 32 registered #833 objects listed in `FOUNDATION_DEPENDENCY_DAG_V1.json`, placed on the
ten-layer stack `F0..F9` exactly as issue #833 comment `5693520829` section AG1 states it. All
quantities are exact integers or `fractions.Fraction`.

---

## AG1-1 — every arrow is typed, witnessed, and never points up a layer

**Statement.** The registry carries 37 arrows over 32 nodes. Every arrow's kind lies in the closed
vocabulary `{DERIVATION, FREE_CONSTRUCTION, INTERPRETATION_MODEL, COMPILATION, DEVELOPMENT,
SELECTION, MUTUAL_INTERPRETATION}` (0 unknown kinds); every arrow carries a witness naming a merged
package and a field that is actually present in that package's `RESULT_V1.json` (0 missing fields,
0 unresolved packages); and **no** arrow points up a layer (0 monotonicity violations). The 7
same-layer refinement arrows are declared `intra_layer: true` (0 undeclared), so an intra-layer
refinement can never be mistaken for a foundation-descent arrow. Kind histogram: `DERIVATION 20`,
`DEVELOPMENT 5`, `INTERPRETATION_MODEL 4`, `SELECTION 4`, `MUTUAL_INTERPRETATION 2`,
`COMPILATION 1`, `FREE_CONSTRUCTION 1`.

**Quantifiers.** For all 37 arrows.

**Assumptions.** An arrow `{from, to, kind}` reads "`from` is obtained from `to` by `kind`".
Witness verification is presence-of-field plus pinned blob sha, not re-derivation of the parent's
mathematics.

**Falsifiers.** An untyped or witnessless arrow; a witness field absent from the cited receipt; any
upward arrow; a silent same-layer arrow.

**Strongest parents.** Dependency-graph and provenance practice; the interface-keyed
`GMI_THEORY_DEPENDENCY_DAG.json` of `gmi-833-ai0-convergence-spine-v1`, which this registry does
**not** replace — AI0 remains authoritative for `GEN/DEV/REQ/REL/CAP/SEL/EVID` ownership and every
AG1 node cites its AI0 node where one exists.

**Forbidden extrapolations.** `LAYER_ASSIGNMENT_IS_ONTOLOGY`,
`DAG_ACYCLICITY_PROVES_FOUNDATIONAL_PRIORITY`.

---

## AG1-2 — every layer `F0..F9` is occupied by a named, pinned #833 object

**Statement.** All ten layers are non-empty, with node counts
`F0 6, F1 4, F2 6, F3 2, F4 2, F5 3, F6 3, F7 2, F8 2, F9 2`. Every node names the merged package
that owns it; **21** distinct packages are pinned by path and git blob sha at `source_main`
`91c6d287`, with 0 pin violations.

**Quantifiers.** For all ten layers and all 32 nodes.

**Assumptions.** "Registered #833 object" means an object owned by a package merged to `main` at
`source_main`. The registry is a census of those, not of all mathematics.

**Falsifiers.** An empty layer; a node whose owning package is absent; a pin mismatch.

**Forbidden extrapolations.** `F0_IS_UNIQUE`; the registry does not claim `F0` exhausts possible
foundations — `gmi-833-aj12-foundation-substrate-relativity-v1` owns that boundary and two of the
six `F0` nodes are joined by a `MUTUAL_INTERPRETATION` pair precisely because neither is privileged.

---

## AG1-3 — `G0` sits at `F4`, not at the bottom (demotion earned, not asserted)

**Statement.** `GRM_G0` is assigned layer `F4` (free syntax / term algebra), is generated from
`SIG_G0` at `F3` by a `FREE_CONSTRUCTION` arrow, and is connected by a directed path of
derived-from arrows down to an `F0` node — verified by DFS (route A) and independently by boolean
transitive closure over the adjacency matrix (route B). Its realization `MDL_G0_LOWERED` at `F5` is
obtained from `GRM_G0` by `COMPILATION` and from `PRS_AJ5_ROLE_BASIS` by `INTERPRETATION_MODEL`.
0 demotion violations.

**Quantifiers.** For the single node `GRM_G0`.

**Assumptions.** The demotion is licensed by merged evidence, not by relabelling: AJ5 lowers all
five registered `G0` opcodes onto the operational role basis (`READ/EMIT/INC/DECJZ` `DERIVED`,
`HALT` `PRESENTATION_ONLY`) over 484 executions with 0 mismatches, and AG2 exhibits `G0` as the free
term algebra over `Sigma_G0` (11 `Instr` terms, 121 `Prog` terms).

**Falsifiers.** `GRM_G0` at `F0/F1/F2`; no path from `GRM_G0` to any `F0` node.

**Strongest parents.** `gmi-833-aj5-g0-lowering-v1` (lowering), `gmi-833-g0-register-core-v1`
(registered semantics), Minsky 1967 (the instruction set).

**Forbidden extrapolations.** `G0_IRREDUCIBILITY_DISPROVED_IN_GENERAL` — the demotion is a
statement about layer placement at the registered scope, not a proof that no instruction basis is
irreducible.

---

## AG1-4 — declared primitives name their lower layer; apparent bottoms expose their assumptions

**Statement.** Every node marked `primitive` names an `introduced_from_layer` strictly below its own
(0 violations). Every apparent bottom node — the 5 nodes with no outgoing derived-from arrow —
carries a non-empty metatheoretic assumption list, and every assumption is tagged with one of the
five AJ12 classes `{MATHEMATICAL_FOUNDATION, LOGIC/METATHEORY, PHYSICAL_SUBSTRATE_LAW,
RESOURCE_MODEL, VALUE/REQUIREMENT_INPUT}` (0 untagged). Cycles over derived-from arrows: **0**, by
DFS colour-marking and independently by Kahn in-degree peeling (32 of 32 nodes removed).
`MUTUAL_INTERPRETATION` arrows are required to be symmetric and same-layer (0 violations), so an
equivalence can never be smuggled in as a derivation.

**Open provenance, declared not hidden.** One node — `GRM_G0_EXTENSIONS_UNADJUDICATED` at `F4`,
covering the registered stochastic, local-graph, channel/tool and governed-self-change operator
families — carries `lowering_status: UNKNOWN`. It names `F2` as the layer it is introduced from and
exposes its assumptions, but no merged package has yet assigned it an AG5 status. This is the
residual that section AG5 rows on stochastic update, communication/tool calls and governed
self-change still ask for, and the registry displays it rather than papering over it.

**Falsifiers.** A primitive without provenance; a bottom node with no assumptions; any cycle; an
asymmetric or cross-layer `MUTUAL_INTERPRETATION`.

**Forbidden extrapolations.** `ABSOLUTE_BOTTOM_LAYER_PROVEN`.

---

## AG1-5 — the first layer at which a matched pair diverges is `F6`, not the grammar layer

**Statement.** For the registered matched pair (same substrate, same operational theory, same
presentation, same grammar, same machine organization; differing only in developmental context),
the first layer at which the two systems differ is **`F6` — DEVELOPMENTAL DYNAMICS**. Computed by
linear scan (route A) and independently by integer bitmask lowest-set-bit (route B). The capability
values at divergence are exactly `1/2` for the frozen system and `0` for the one-edit system (best
achievable identity-task error), and these agree with the pinned
`gmi-833-aj6-hst-layer-map-v1` receipt, which reports `current_organization_same: true`,
`frozen_future_best_identity_error: 0.5`, `one_edit_future_best_identity_error: 0.0` over
**51** same-current-capability-different-future pairs.

**Consequence for AG0/AG7.** Two systems identical through `F5` — including identical grammar at
`F4` — can differ in developmental capability. No predicate evaluated at or below `F4` can
therefore separate them. This is the layer-indexed form of the AJ8 result that finite universality
is not sufficient for intelligence.

**Quantifiers.** For the registered pair; existence, not universality.

**Assumptions.** The capability coordinate is the registered identity task at AJ6's scope; the pair
is one of AJ6's 51. The `F0`-`F5` identity of the pair is **registered from AJ6's receipt** -- it
rests on AJ6's `current_organization_same: true` together with this package's layer assignment. It
is not independently re-verified layer by layer here, and the claim must not be read as such.

**Falsifiers.** A divergence at any layer below `F6` for a pair declared identical through `F5`; a
mismatch with AJ6's pinned values.

**Strongest parents.** `gmi-833-aj6-hst-layer-map-v1` and #233 HST/HSG own the developmental
dynamics; `gmi-833-aj8-intelligence-boundary-v1` owns the fixed-vs-developmental boundary. AG1-5
contributes only the layer index.

**Forbidden extrapolations.** No definition of intelligence is frozen here;
`CURRENT_CAPABILITY_IDENTIFIES_DEVELOPMENTAL_CAPABILITY` remains forbidden by AJ8.

---

## AG8 — the descent protocol, as eight machine-checked obligations

`AG8_DESCENT_OBLIGATIONS_V1.json` registers AG8's eight steps with `direction: DOWNWARD`, each
carrying (a) an upward counterpart and (b) a discharge reference. The upward counterparts are real
and resolvable, not invented: AA's `OPEN_GAP` / `GMI_GAP_GRAPH` and AD's recursive research loop
(issue #833 comment `5684607872`), and the HSG Atomic/Reflexive Generalization Closure protocol
registered as parent row `HSG_AGP` in
`research/gmi-833-af-barrier-context-v1/GMI_BARRIER_PARENT_LEDGER_V1.json`, pinned to
`research/heritable-search-geometry-v1/HSG_FREEZE_V1.json` and `HSG_ATOM_TABLE_V1.json`. The checker
verifies all 8 steps present with distinct indices, every upward counterpart resolving, every
discharge non-empty, and every pinned HSG artifact existing on disk (0 obligation violations).
AA/AD close gaps **upward** from a claim to its descendants; AG8 closes them **downward** from an
object to what it is built from. The two are counterparts, not duplicates.
