import PresentedUnitsV25
import TableTransportV19
namespace ImageAlgebraV29
open PartialUnitsV19 TableTransportV19
universe u v
variable {A : Type u} {L : Type v} (j : A → L) (hj : ∀ a b, j a = j b → a = b)
def Carrier (l : L) : Prop := ∃ a, j a = l
abbrev Image := {l : L // Carrier j l}
def put (a : A) : Image j := ⟨j a,a,rfl⟩
noncomputable def get (l : Image j) : A := Classical.choose l.property
theorem put_get (l : Image j) : put j (get j l) = l :=
  Subtype.ext (Classical.choose_spec l.property)
include hj
theorem get_put (a : A) : get j (put j a) = a :=
  hj _ _ (Classical.choose_spec (put j a).property)
theorem put_injective (a b : A) (h : put j a = put j b) : a = b :=
  hj a b (congrArg Subtype.val h)
noncomputable def operation (m : A → A → Option A) (a b : Image j) : Option (Image j) :=
  (m (get j a) (get j b)).map (put j)
noncomputable def tableIso (m : A → A → Option A) : TableIso m (operation j m) where
  forward := put j
  backward := get j
  backward_forward := get_put j hj
  forward_backward := put_get j
  mul := by intro a b; simp only [operation,get_put j hj]
theorem operation_put (m : A → A → Option A) (a b : A) :
    operation j m (put j a) (put j b) = (m a b).map (put j) := (tableIso j hj m).mul a b
theorem map_put_injective (a b : Option A) (h : a.map (put j) = b.map (put j)) : a = b := by
  have hh := congrArg (Option.map (get j)) h
  simpa [Option.map_map,Function.comp_def,get_put j hj] using hh
noncomputable def algebra (P : Algebra A) : Algebra (Image j) where
  mul := operation j P.mul
  assoc := by
    intro a b c
    rw [← put_get j a,← put_get j b,← put_get j c]
    have hp := P.assoc (get j a) (get j b) (get j c)
    simpa [operation,get_put j hj,Option.bind_map,Option.map_bind,Function.comp_def] using
      congrArg (Option.map (put j)) hp
  localUnits := by
    intro x
    obtain ⟨e,f,he,hf,hl,hr⟩ := P.localUnits (get j x)
    refine ⟨put j e,put j f,(tableIso j hj P.mul).unit_forward he,
      (tableIso j hj P.mul).unit_forward hf,?_,?_⟩
    · rw [← put_get j x,operation_put j hj,hl]; rfl
    · rw [← put_get j x,operation_put j hj,hr]; rfl
  coherent := by
    intro a b c x y h k
    have h' := (tableIso j hj P.mul).symm.mul a b
    have k' := (tableIso j hj P.mul).symm.mul b c
    rw [h] at h'
    rw [k] at k'
    change P.mul (get j a) (get j b) = some (get j x) at h'
    change P.mul (get j b) (get j c) = some (get j y) at k'
    obtain ⟨z,hz⟩ := P.coherent _ _ _ _ _ h' k'
    refine ⟨put j z,?_⟩
    change (P.mul (get j x) (get j c)).map (put j) = _
    rw [hz]; rfl
noncomputable def presented (P : Algebra A) : PresentedCoreV25.Presented L where
  carrier := Carrier j
  algebra := algebra j hj P
theorem carrier_binding (P : Algebra A) (l : L) :
    (presented j hj P).carrier l ↔ ∃ a, j a = l := Iff.rfl
theorem padded_put (P : Algebra A) (a b : A) :
    PresentedCoreV25.padded (presented j hj P) (j a) (j b) = (P.mul a b).map j := by
  change PresentedCoreV25.padded (presented j hj P) (put j a).val (put j b).val = _
  rw [PresentedCoreV25.padded_present]
  change (operation j P.mul (put j a) (put j b)).map Subtype.val = _
  rw [operation_put j hj]
  simp only [Option.map_map,Function.comp_def,put]
theorem padded_absent (P : Algebra A) (l k : L) (h : ¬∃ a, j a = l) :
    PresentedCoreV25.padded (presented j hj P) l k = none :=
  PresentedCoreV25.padded_absent_left _ _ _ h
end ImageAlgebraV29
