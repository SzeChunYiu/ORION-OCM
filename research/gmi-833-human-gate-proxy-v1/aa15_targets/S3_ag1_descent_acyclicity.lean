/-
  S3 — AG1-4 descent-stack acyclicity and layer monotonicity.

  Target for: AG1_THEOREMS_V1.md, results AG1-1 ("no arrow points up a layer")
  and AG1-4 ("Cycles over derived-from arrows: 0"), over the 32 nodes and 37 arrows
  of FOUNDATION_DEPENDENCY_DAG_V1.json.  Edge semantics, quoted from that file:
  "edge {from,to,kind} reads: `from` is obtained from `to` by `kind`. ...
   MUTUAL_INTERPRETATION edges must be symmetric and same-layer."

  Lean 4 core only.  No `import` line: this file is self-contained.
  Node and arrow tables are generated from the registry, node `i` = `nodeNames[i]`.

  ---------------------------------------------------------------------------
  REVIEWER'S CORRECTION (this is why the file has section 3).

  The relation over ALL 37 arrows is NOT acyclic: `FND_SET_RELATION` (0) and
  `FND_TYPED_ALGEBRAIC` (1) are joined by a symmetric MUTUAL_INTERPRETATION pair,
  which is a 2-cycle.  `cycle_over_all_37_arrows` below PROVES this (no `sorry`).
  Acyclicity holds only for the 35-arrow sub-relation that excludes
  MUTUAL_INTERPRETATION, and that is what `derivedFrom` is here.

  But AG1-4 also counts "the 5 nodes with no outgoing derived-from arrow".  Over
  the 35-arrow relation there are 7 such nodes, not 5; 5 is the count over all 37
  arrows.  So AG1-4's two numbers use two different arrow sets under one name.
  `bottom_count_equivocation` below makes that machine-checkable.
  ---------------------------------------------------------------------------
-/

namespace S3

inductive Kind
  | DERIVATION | FREE_CONSTRUCTION | INTERPRETATION_MODEL | COMPILATION
  | DEVELOPMENT | SELECTION | MUTUAL_INTERPRETATION
deriving DecidableEq, Repr

open Kind

def nodeNames : List String :=
  ["FND_SET_RELATION", "FND_TYPED_ALGEBRAIC", "MTB_GODEL_TARSKI", "PHY_SUBSTRATE_LAW", "RES_COST_MODEL", "VAL_REQUIREMENT_INPUT", "OPF_PROCESS_FRAME", "ADM_S", "OBS_S", "SUB_STANDARD_EFFECTIVE", "THR_OPERATIONAL_EQUIVALENCE", "THR_DISTINGUISHABILITY", "THR_PARENT_EQUIVALENCE_BOUNDARY", "THR_STOCHASTIC_KERNELS", "THR_TYPED_INTERACTION", "THR_LOCAL_GLOBAL_GRAPH", "PRS_AJ5_ROLE_BASIS", "SIG_G0", "GRM_G0", "GRM_G0_EXTENSIONS_UNADJUDICATED", "MDL_G0_LOWERED", "MDL_AJ4_ORGANIZATIONS", "MDL_NEGATIVE_CONTROLS", "DEV_HST_SIGMA", "DEV_GOVERNED_SELF_CHANGE", "DEV_GRAMMAR_GROWTH", "MRP_AJ11_ATLAS", "MRP_AJ9_FAMILIES", "CAP_AJ8_BOUNDARY", "CAP_PREDICTOR", "SEL_REQ_PROVENANCE", "SEL_MORPHOLOGY_PARETO"]

/-- layer index of each node: `F0` ↦ 0, …, `F9` ↦ 9. -/
def layerOf : List Nat :=
  [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 8, 8, 9, 9]

/-- the 37 registered arrows as `(from, to, kind)`. -/
def arrows : List (Nat × Nat × Kind) :=
  [(0, 1, Kind.MUTUAL_INTERPRETATION),
  (1, 0, Kind.MUTUAL_INTERPRETATION),
  (6, 0, Kind.DERIVATION),
  (6, 1, Kind.DERIVATION),
  (7, 3, Kind.DERIVATION),
  (8, 0, Kind.DERIVATION),
  (9, 3, Kind.DERIVATION),
  (10, 6, Kind.DERIVATION),
  (10, 8, Kind.DERIVATION),
  (11, 10, Kind.DERIVATION),
  (12, 10, Kind.DERIVATION),
  (13, 6, Kind.DERIVATION),
  (14, 6, Kind.DERIVATION),
  (15, 6, Kind.DERIVATION),
  (16, 6, Kind.DERIVATION),
  (16, 14, Kind.DERIVATION),
  (17, 16, Kind.DERIVATION),
  (18, 17, Kind.FREE_CONSTRUCTION),
  (20, 18, Kind.COMPILATION),
  (20, 16, Kind.INTERPRETATION_MODEL),
  (21, 6, Kind.INTERPRETATION_MODEL),
  (21, 7, Kind.INTERPRETATION_MODEL),
  (22, 21, Kind.INTERPRETATION_MODEL),
  (23, 21, Kind.DEVELOPMENT),
  (24, 20, Kind.DEVELOPMENT),
  (25, 18, Kind.DEVELOPMENT),
  (26, 21, Kind.DERIVATION),
  (26, 23, Kind.DEVELOPMENT),
  (27, 26, Kind.DERIVATION),
  (28, 26, Kind.DERIVATION),
  (28, 23, Kind.DEVELOPMENT),
  (28, 22, Kind.DERIVATION),
  (29, 28, Kind.DERIVATION),
  (30, 5, Kind.SELECTION),
  (31, 29, Kind.SELECTION),
  (31, 30, Kind.SELECTION),
  (31, 4, Kind.SELECTION)]

def lay (i : Nat) : Nat := layerOf.getD i 0

/-- all 37 arrows, kind forgotten. -/
def allArrows : List (Nat × Nat) := arrows.map (fun e => (e.1, e.2.1))

/-- the 35 foundation-descent ("derived-from") arrows: MUTUAL_INTERPRETATION excluded,
    because a declared equivalence is not a derivation (AG1-4's own words). -/
def derivedFrom : List (Nat × Nat) :=
  (arrows.filter (fun e => e.2.2 != Kind.MUTUAL_INTERPRETATION)).map (fun e => (e.1, e.2.1))

/-- a topological rank, shipped rather than postulated: produced by Kahn in-degree
    peeling of `derivedFrom` and pasted in, so `rank_decreases` is a finite check. -/
def rank : List Nat :=
  [0, 1, 3, 4, 5, 6, 9, 7, 8, 11, 14, 20, 21, 15, 16, 13, 19, 23, 25, 2, 29, 12, 18, 17, 30, 28, 22, 26, 24, 27, 10, 31]

def rk (i : Nat) : Nat := rank.getD i 0

/- ---------------- 1. census and layer monotonicity ---------------- -/

theorem node_census : nodeNames.length = 32 ∧ layerOf.length = 32 ∧ rank.length = 32 := by
  decide

theorem arrow_census : arrows.length = 37 ∧ derivedFrom.length = 35 := by
  decide

/-- AG1-1: no arrow points UP a layer (all 37 arrows). -/
theorem no_upward_arrow : ∀ e ∈ arrows, lay e.2.1 ≤ lay e.1 := by
  decide

/-- MUTUAL_INTERPRETATION arrows are same-layer and symmetric. -/
theorem mutual_symmetric_same_layer :
    ∀ e ∈ arrows, e.2.2 = Kind.MUTUAL_INTERPRETATION →
      lay e.2.1 = lay e.1 ∧ (e.2.1, e.1, Kind.MUTUAL_INTERPRETATION) ∈ arrows := by
  decide

/- ---------------- 2. acyclicity of the derived-from relation ---------------- -/

/-- non-empty directed paths over `derivedFrom`. -/
inductive Path : Nat → Nat → Prop
  | single {u v : Nat} : (u, v) ∈ derivedFrom → Path u v
  | step   {u v w : Nat} : (u, v) ∈ derivedFrom → Path v w → Path u w

/-- the shipped witness: every derived-from arrow strictly decreases `rk`. -/
theorem rank_decreases : ∀ e ∈ derivedFrom, rk e.2 < rk e.1 := by
  decide

/-- ranks strictly decrease along paths (induction on `Path`, using `rank_decreases`). -/
theorem path_rank_decreases : ∀ {u v : Nat}, Path u v → rk v < rk u := by
  sorry

/-- **S3 / AG1-4 (repaired).**  The 35-arrow derived-from relation on the 32 registered
    nodes has no cycle. -/
theorem derivedFrom_acyclic : ∀ u : Nat, ¬ Path u u := by
  sorry

/- ---------------- 3. what is NOT true, and the equivocation ---------------- -/

/-- paths over all 37 arrows. -/
inductive PathAll : Nat → Nat → Prop
  | single {u v : Nat} : (u, v) ∈ allArrows → PathAll u v
  | step   {u v w : Nat} : (u, v) ∈ allArrows → PathAll v w → PathAll u w

/-- **REFUTATION (proved, not `sorry`).**  The relation over all 37 arrows HAS a cycle,
    namely `FND_SET_RELATION -> FND_TYPED_ALGEBRAIC -> FND_SET_RELATION`.  Any statement
    of the form "the 37-arrow derived-from relation has no cycle" is false as written. -/
theorem cycle_over_all_37_arrows : ∃ u : Nat, PathAll u u :=
  ⟨0, PathAll.step (u := 0) (v := 1) (w := 0) (by decide) (PathAll.single (u := 1) (v := 0) (by decide))⟩

/-- nodes with no outgoing arrow in a given relation. -/
def sinks (rel : List (Nat × Nat)) : List Nat :=
  (List.range 32).filter (fun u => !(rel.any (fun e => e.1 == u)))

/-- **The AG1-4 arrow-set equivocation, machine-checked.**  "the 5 nodes with no outgoing
    derived-from arrow" is the count over all 37 arrows; over the 35 arrows for which
    "Cycles ... : 0" is true, the count is 7.  The two sentences use different relations. -/
theorem bottom_count_equivocation :
    (sinks allArrows).length = 5 ∧ (sinks derivedFrom).length = 7 ∧
    sinks allArrows ≠ sinks derivedFrom := by
  decide

theorem sinks_explicit :
    sinks allArrows = [2, 3, 4, 5, 19] ∧ sinks derivedFrom = [0, 1, 2, 3, 4, 5, 19] := by
  decide

end S3
