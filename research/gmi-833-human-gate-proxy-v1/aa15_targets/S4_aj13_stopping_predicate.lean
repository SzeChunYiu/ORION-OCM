/-
  S4 — the AJ13 recursive foundation-descent stopping predicate.

  Target for: THEORY.md ("The registered stopping predicate has six conjuncts", 1–6,
  the permitted terminal `FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE`
  and the forbidden terminal `ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN`),
  formalised at the semantics of `check_aj13.py` (`audit`, `baseline`, `run_hostiles`).

  Lean 4 core only.  No `import` line: this file is self-contained.

  ---------------------------------------------------------------------------
  Faithfulness notes (the formalisation follows the CODE, and the code is weaker
  than the prose in two places that this file makes machine-checkable):

  (a) `audit` tests `base & BANNED_MI_PRIMITIVES` — an exact, CASE-SENSITIVE match
      against 10 uppercase tokens.  THEORY.md conjunct 2 forbids "named mechanisms
      such as neuron, memory, attention, planner, world model or backpropagation".
      `case_sensitivity_gap` proves that an operational base containing the literal
      string "neuron" still satisfies the implemented predicate.
  (b) `audit` tests `set(irr.values()) != REQUIRED_OPERATIONAL_ROLES` — only the value
      set.  Nothing ties the KEYS of `aj1_irredundancy` to `operational_base`.
      `irredundancy_key_gap` proves a record whose loss witnesses are keyed by symbols
      absent from the operational base still satisfies the implemented predicate.

  Both are statements about the checker, not refutations of the AJ13 theory; they
  are recorded here so a proof effort does not silently inherit them.
  ---------------------------------------------------------------------------
-/

namespace S4

structure Assumption where
  id  : String
  tag : String
deriving DecidableEq, Repr

/-- the finite record the stopping predicate ranges over (Python `baseline()`'s shape). -/
structure AJ13Record where
  remainingAssumptions           : List Assumption
  operationalBase                : List String
  aj1Irredundancy                : List (String × String)
  presentationInvarianceEvidence : List String
  parentOwnershipRegistered      : Bool
  furtherDescentClassification   : List String
  requestedTerminal              : String
deriving DecidableEq, Repr

def allowedTags : List String :=
  ["MATHEMATICAL_FOUNDATION", "LOGIC/METATHEORY", "PHYSICAL_SUBSTRATE_LAW",
   "RESOURCE_MODEL", "VALUE/REQUIREMENT_INPUT"]

def bannedMiPrimitives : List String :=
  ["NEURON", "LAYER", "ATTENTION", "MEMORY", "PLANNER", "SEARCHER",
   "WORLD_MODEL", "BACKPROP", "TRANSFORMER", "SYMBOLIC_REASONER"]

def requiredOperationalRoles : List String :=
  ["TYPE", "SEQUENCE", "PARALLEL", "NO_CHANGE", "SUBSTRATE_ADMISSIBILITY",
   "OPERATIONAL_OBSERVATION"]

def forbiddenTerminal : String := "ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN"
def permittedTerminal : String := "FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE"

/-- kernel-reducible prefix test.  `String.startsWith` is used by the Python checker
    (`s.startswith("AJ5_")`); the core `String.startsWith` does not reduce in the Lean
    kernel, so the same function is spelled out on `String.toList` here. -/
def isPrefixChars : List Char → List Char → Bool
  | [],      _      => true
  | _ :: _,  []     => false
  | a :: as, b :: bs => a == b && isPrefixChars as bs

def startsWith (s p : String) : Bool := isPrefixChars p.toList s.toList

/-- set equality of two string lists (Python `set(...) == set(...)`). -/
def setEq (xs ys : List String) : Bool :=
  xs.all (fun x => ys.contains x) && ys.all (fun y => xs.contains y)

/-- conjunct 1 — tagged residual assumptions. -/
def taggedResiduals (x : AJ13Record) : Bool :=
  !x.remainingAssumptions.isEmpty &&
  x.remainingAssumptions.all (fun a => allowedTags.contains a.tag)

/-- conjunct 2 — no MI-specific base primitive. -/
def noMiPrimitive (x : AJ13Record) : Bool :=
  x.operationalBase.all (fun b => !bannedMiPrimitives.contains b)

/-- conjunct 3 — removal has a demonstrated boundary (AJ1 loss witnesses). -/
def removalBoundary (x : AJ13Record) : Bool :=
  setEq (x.aj1Irredundancy.map Prod.snd) requiredOperationalRoles

/-- conjunct 4 — higher results survive alternative presentations (AJ5 and AJ12). -/
def presentationInvariance (x : AJ13Record) : Bool :=
  x.presentationInvarianceEvidence.any (fun s => startsWith s "AJ5_") &&
  x.presentationInvarianceEvidence.any (fun s => startsWith s "AJ12_")

/-- conjunct 5 — strongest parents retain ownership. -/
def parentOwnership (x : AJ13Record) : Bool := x.parentOwnershipRegistered

/-- conjunct 6 — further descent changes domain. -/
def descentChangesDomain (x : AJ13Record) : Bool :=
  !x.furtherDescentClassification.isEmpty &&
  x.furtherDescentClassification.all (fun t => allowedTags.contains t) &&
  !x.furtherDescentClassification.contains "RESOURCE_MODEL"

/-- **S4 — the six-conjunct stopping predicate as a proposition over a finite record.** -/
def Stops (x : AJ13Record) : Prop :=
  taggedResiduals x = true ∧ noMiPrimitive x = true ∧ removalBoundary x = true ∧
  presentationInvariance x = true ∧ parentOwnership x = true ∧ descentChangesDomain x = true

/-- the separate seventh guard of `audit`: the absolute-bottom terminal is never requested. -/
def NoAbsolutePromotion (x : AJ13Record) : Prop := x.requestedTerminal ≠ forbiddenTerminal

/-- **S4(a) — decidability.**  The stopping predicate is decidable on every record. -/
instance stopsDecidable (x : AJ13Record) : Decidable (Stops x) := by
  unfold Stops; infer_instance

instance noAbsoluteDecidable (x : AJ13Record) : Decidable (NoAbsolutePromotion x) := by
  unfold NoAbsolutePromotion; infer_instance

/- ---------------- the registered baseline and the six hostiles ---------------- -/

def baseline : AJ13Record where
  remainingAssumptions :=
    [⟨"F", "MATHEMATICAL_FOUNDATION"⟩, ⟨"L", "LOGIC/METATHEORY"⟩,
     ⟨"S", "PHYSICAL_SUBSTRATE_LAW"⟩, ⟨"R", "RESOURCE_MODEL"⟩,
     ⟨"Q", "VALUE/REQUIREMENT_INPUT"⟩]
  operationalBase := ["Obj", "Proc", "compose", "tensor", "I", "id", "Adm_S", "Obs_S"]
  aj1Irredundancy :=
    [("Obj", "TYPE"), ("compose", "SEQUENCE"), ("tensor", "PARALLEL"),
     ("id", "NO_CHANGE"), ("Adm_S", "SUBSTRATE_ADMISSIBILITY"),
     ("Obs_S", "OPERATIONAL_OBSERVATION")]
  presentationInvarianceEvidence :=
    ["AJ5_G0_DERIVED_FROM_OPERATIONAL_LAYER_AND_PRESENTATION_INVARIANCE_AT_REGISTERED_FINITE_SCOPE",
     "AJ12_FOUNDATION_STYLE_AND_COMPUTATIONAL_SUBSTRATE_RELATIVITY_AUDITED_AT_REGISTERED_CORE_SCOPE"]
  parentOwnershipRegistered := true
  furtherDescentClassification :=
    ["LOGIC/METATHEORY", "MATHEMATICAL_FOUNDATION", "PHYSICAL_SUBSTRATE_LAW",
     "VALUE/REQUIREMENT_INPUT"]
  requestedTerminal := permittedTerminal

def hBadTag : AJ13Record :=
  { baseline with remainingAssumptions :=
      baseline.remainingAssumptions ++ [⟨"bad", "INTELLIGENCE_ATOM"⟩] }
def hMiPrimitive : AJ13Record :=
  { baseline with operationalBase := baseline.operationalBase ++ ["NEURON"] }
def hMissingLossWitness : AJ13Record :=
  { baseline with aj1Irredundancy :=
      baseline.aj1Irredundancy.filter (fun kv => kv.1 != "Obs_S") }
def hMissingCrossFoundation : AJ13Record :=
  { baseline with presentationInvarianceEvidence :=
      [baseline.presentationInvarianceEvidence.getD 0 ""] }
def hMissingParent : AJ13Record :=
  { baseline with parentOwnershipRegistered := false }
def hAbsolutePromotion : AJ13Record :=
  { baseline with requestedTerminal := forbiddenTerminal }

/- ---------------- S4(b): the registered green/hostile obligations ---------------- -/

theorem baseline_stops : Stops baseline ∧ NoAbsolutePromotion baseline := by
  decide

theorem hostile_bad_tag_rejected : ¬ Stops hBadTag := by
  decide
theorem hostile_mi_primitive_rejected : ¬ Stops hMiPrimitive := by
  decide
theorem hostile_missing_loss_witness_rejected : ¬ Stops hMissingLossWitness := by
  decide
theorem hostile_missing_cross_foundation_rejected : ¬ Stops hMissingCrossFoundation := by
  decide
theorem hostile_missing_parent_rejected : ¬ Stops hMissingParent := by
  decide
theorem hostile_absolute_promotion_rejected : ¬ NoAbsolutePromotion hAbsolutePromotion := by
  decide

/-- the truth values of the six conjuncts, in the order 1..6 of THEORY.md. -/
def profile (x : AJ13Record) : List Bool :=
  [taggedResiduals x, noMiPrimitive x, removalBoundary x,
   presentationInvariance x, parentOwnership x, descentChangesDomain x]

/-- each hostile falsifies EXACTLY the conjunct it targets and leaves the other five
    satisfied; the sixth hostile touches no conjunct at all and is caught only by the
    separate absolute-bottom guard. -/
theorem hostile_profiles :
    profile baseline                 = [true,  true,  true,  true,  true,  true] ∧
    profile hBadTag                  = [false, true,  true,  true,  true,  true] ∧
    profile hMiPrimitive             = [true,  false, true,  true,  true,  true] ∧
    profile hMissingLossWitness      = [true,  true,  false, true,  true,  true] ∧
    profile hMissingCrossFoundation  = [true,  true,  true,  false, true,  true] ∧
    profile hMissingParent           = [true,  true,  true,  true,  false, true] ∧
    profile hAbsolutePromotion       = [true,  true,  true,  true,  true,  true] := by
  decide

/- ---------------- S4(c): the two checker gaps, machine-checked ---------------- -/

/-- (a) the banned-primitive test is case-sensitive: a lowercase "neuron" passes. -/
theorem case_sensitivity_gap :
    Stops { baseline with operationalBase := baseline.operationalBase ++ ["neuron"] } := by
  decide

/-- (b) the loss-witness test looks only at the ROLE values: a record whose witnesses are
    keyed by symbols that are not in the operational base at all still passes. -/
theorem irredundancy_key_gap :
    Stops { baseline with aj1Irredundancy :=
              [("zzz1", "TYPE"), ("zzz2", "SEQUENCE"), ("zzz3", "PARALLEL"),
               ("zzz4", "NO_CHANGE"), ("zzz5", "SUBSTRATE_ADMISSIBILITY"),
               ("zzz6", "OPERATIONAL_OBSERVATION")] } := by
  decide

end S4
