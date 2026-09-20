import ProcessMapsV26
import RelationsV14
namespace RelParentV27
open TypedPathsV11 ProcessMapsV26 StochasticV14
universe u v w x
abbrev Rel (A : Type u) (B : Type v) := A → B → Prop
def ident (A : Type u) : Rel A A := fun a b => b=a
def comp {A : Type u} {B : Type v} {C : Type w} (r : Rel A B) (s : Rel B C) :
    Rel A C := fun a c => ∃ b, r a b ∧ s b c
theorem assoc {A : Type u} {B : Type v} {C : Type w} {D : Type x}
    (r : Rel A B) (s : Rel B C) (t : Rel C D) : comp (comp r s) t=comp r (comp s t) := by
  funext a d; apply propext
  constructor
  · rintro ⟨c,⟨b,hab,hbc⟩,hcd⟩; exact ⟨b,hab,c,hbc,hcd⟩
  · rintro ⟨b,hab,c,hbc,hcd⟩; exact ⟨c,⟨b,hab,hbc⟩,hcd⟩
theorem left_id {A : Type u} {B : Type v} (r : Rel A B) : comp (ident A) r=r := by
  funext a b; apply propext
  constructor
  · rintro ⟨a',ha,h⟩; exact ha ▸ h
  · intro h; exact ⟨a,rfl,h⟩
theorem right_id {A : Type u} {B : Type v} (r : Rel A B) : comp r (ident B)=r := by
  funext a b; apply propext
  constructor
  · rintro ⟨b',h,hb⟩; exact hb ▸ h
  · intro h; exact ⟨b,h,rfl⟩
def category : Category (Type u) where
  Hom := Rel
  id := ident
  comp := comp
  assoc := assoc
  left_id := left_id
  right_id := right_id
def totalCategory : Category (Type u) where
  Hom := TotalRel
  id := TotalRel.ident
  comp := TotalRel.comp
  assoc := TotalRel.assoc
  left_id := TotalRel.left_id
  right_id := TotalRel.right_id
def inclusion : ProcessMap totalCategory.{u} category.{u} where
  obj := id
  hom := TotalRel.relates
  id_law _ := rfl
  comp_law _ _ := rfl
theorem inclusion_faithful : inclusion.{u}.Faithful := by
  intro a b f g h
  apply TotalRel.ext
  intro x y
  exact Iff.of_eq (congrFun (congrFun h x) y)
def empty {A : Type u} {B : Type v} : Rel A B := fun _ _ => False
theorem empty_not_total {A : Type u} {B : Type v} (a : A) :
    ¬ ∃ r : TotalRel A B, r.relates=empty := by
  rintro ⟨r,h⟩
  obtain ⟨b,hb⟩ := r.total a
  have : empty a b := h ▸ hb
  exact this
theorem empty_into_empty : ∃ r : category.Hom Unit Empty, ∀ a b, ¬r a b :=
  ⟨empty,fun _ _ h => h⟩
end RelParentV27
