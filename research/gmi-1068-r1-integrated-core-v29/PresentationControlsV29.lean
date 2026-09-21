import EvalKernelV29
import FunctorControlsV26
namespace PresentationControlsV29
open TypedPathsV11 FunctorControlsV26
def noEdges (_ _ : Unit) := Empty
def noEdgeMap {a b : Unit} (e : noEdges a b) : bitGroup.Hom a b := nomatch e
theorem empty_path_eval {a b : Unit} (p : Path noEdges a b) :
    eval bitGroup id noEdgeMap p = false := by
  cases p with
  | nil a => rfl
  | cons e p => exact nomatch e
theorem no_generation : ¬EvalKernelV29.Generates bitGroup noEdgeMap := by
  intro h
  obtain ⟨p,hp⟩ := h (a := ()) (b := ()) true
  rw [empty_path_eval] at hp
  cases hp
theorem faithful_without_generation :
    (EvalKernelV29.lowerMap bitGroup noEdgeMap).Faithful ∧
    ¬EvalKernelV29.Generates bitGroup noEdgeMap :=
  ⟨EvalKernelV29.lower_faithful _ _,no_generation⟩
def label (a : Fin 6) : Fin 7 :=
  if h : a.val < 2 then ⟨a.val,by omega⟩ else ⟨a.val+1,by omega⟩
def objectDecoder : Fin 3 → Fin 3
  | ⟨0,_⟩ => 2
  | ⟨1,_⟩ => 0
  | ⟨2,_⟩ => 1
def localIdentity : Fin 3 → Fin 6
  | ⟨0,_⟩ => 0
  | ⟨1,_⟩ => 3
  | ⟨2,_⟩ => 5
def namedIdentity (n : Fin 3) := label (localIdentity (objectDecoder n))
theorem label_injective : ∀ a b, label a = label b → a = b := by decide
theorem absent_two : ¬∃ a, label a = 2 := by
  have h : ∀ a, label a ≠ 2 := by decide
  rintro ⟨a,ha⟩
  exact h a ha
theorem exact_image : ∀ l : Fin 7, (∃ a, label a = l) ↔ l ≠ 2 := by
  intro l
  constructor
  · rintro ⟨a,rfl⟩ h
    exact absent_two ⟨a,h⟩
  · intro h
    have cover : ∀ l : Fin 7, l ≠ 2 →
        label 0 = l ∨ label 1 = l ∨ label 2 = l ∨ label 3 = l ∨ label 4 = l ∨ label 5 = l := by decide
    rcases cover l h with h | h | h | h | h | h
    all_goals exact ⟨_,h⟩
theorem decoder_bijective :
    (∀ a b, objectDecoder a = objectDecoder b → a = b) ∧
    (∀ b, ∃ a, objectDecoder a = b) := by
  constructor
  · decide
  · intro b
    have h : ∀ b, objectDecoder 0 = b ∨ objectDecoder 1 = b ∨ objectDecoder 2 = b := by decide
    rcases h b with h | h | h
    all_goals exact ⟨_,h⟩
theorem identity_codebook :
    namedIdentity 0 = 6 ∧ namedIdentity 1 = 0 ∧ namedIdentity 2 = 4 := by decide
theorem label_codebook :
    label 0 = 0 ∧ label 1 = 1 ∧ label 2 = 3 ∧
    label 3 = 4 ∧ label 4 = 5 ∧ label 5 = 6 := by decide
end PresentationControlsV29
