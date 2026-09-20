import ProfileContextsV24
import FrontierOrderV20
import FiniteSumsV12
namespace CandidateContextsV24
open PartialContextV15 ProfileContextsV24 ImageTransportV24 FrontierOrderV20 ScalarV12
universe u v
variable {I : Type u} {α : Type v} [Scalar α] {n : Nat}
def active (viable reachable : I → Prop) (reachableOnly : Bool) (i : I) :=
  viable i ∧ (reachableOnly=true → reachable i)
def vectorOrder : PreorderSpec (I × (Fin n → α)) where
  le a b := CoordLE b.2 a.2
  refl _ _ := Scalar.le_refl _
  trans h k i := Scalar.le_trans (k i) (h i)
def context (r : I → Fin n → α) : Context I (I × (Fin n → α)) :=
  ProfileContextsV24.context (fun _ => True) vectorOrder (fun i => (i,r i))
def Pareto (P : I → Prop) (r : I → Fin n → α) (i : I) :=
  P i ∧ ∀ j, P j → CoordLE (r j) (r i) → CoordLE (r i) (r j)
def Dominates (x y : Fin n → α) := CoordLE x y ∧ ∃ k, x k < y k
theorem image_pair (P : I → Prop) (r : I → Fin n → α) (i : I) (v : Fin n → α) :
    Image P (context r) (i,v) ↔ P i ∧ r i=v := by
  simp only [context,decoded_image,true_and,Prod.mk.injEq]
  constructor
  · rintro ⟨j,hj,he,hv⟩; subst j; exact ⟨hj,hv⟩
  · rintro ⟨hp,hv⟩; exact ⟨i,hp,rfl,hv⟩
theorem maximal_pair (P : I → Prop) (r : I → Fin n → α) (i : I) :
    Maximal vectorOrder (Image P (context r)) (i,r i) ↔ Pareto P r i := by
  constructor
  · rintro ⟨hi,hm⟩
    refine ⟨((image_pair P r i _).mp hi).1,?_⟩
    intro j hj hji
    exact hm (j,r j) ((image_pair P r j _).mpr ⟨hj,rfl⟩) hji
  · rintro ⟨hi,hm⟩
    refine ⟨(image_pair P r i _).mpr ⟨hi,rfl⟩,?_⟩
    rintro ⟨j,v⟩ hj hji
    obtain ⟨hp,hv⟩ := (image_pair P r j v).mp hj
    subst v
    exact hm j hp hji
theorem maximal_ids (P : I → Prop) (r : I → Fin n → α) (i : I) :
    (∃ v, Maximal vectorOrder (Image P (context r)) (i,v)) ↔ Pareto P r i := by
  constructor
  · rintro ⟨v,hv⟩
    have he := ((image_pair P r i v).mp hv.1).2
    subst v
    exact (maximal_pair P r i).mp hv
  · intro h; exact ⟨r i,(maximal_pair P r i).mpr h⟩
theorem pareto_nondominated (P : I → Prop) (r : I → Fin n → α) (i : I) :
    Pareto P r i ↔ P i ∧ ¬∃ j, P j ∧ Dominates (r j) (r i) := by
  classical
  constructor
  · rintro ⟨hi,hm⟩
    refine ⟨hi,?_⟩
    rintro ⟨j,hj,hji,k,hk⟩
    exact not_le_of_lt hk ((hm j hj hji) k)
  · rintro ⟨hi,hn⟩
    refine ⟨hi,?_⟩
    intro j hj hji k
    by_cases h : r i k≤r j k
    · exact h
    · exact False.elim (hn ⟨j,hj,hji,k,lt_of_not_le h⟩)
theorem equal_vector_alias (P : I → Prop) (r : I → Fin n → α) (i j : I)
    (hi : Pareto P r i) (hj : P j) (he : r j=r i) : Pareto P r j := by
  refine ⟨hj,?_⟩
  intro k hk hkj
  rw [he] at hkj ⊢
  exact hi.2 k hk hkj
theorem vector_order_binding (a b : I × (Fin n → α)) :
    vectorOrder.le a b ↔ ∀ k, b.2 k≤a.2 k := Iff.rfl
theorem context_binding (r : I → Fin n → α) :
    (context r).defined=(fun _ => True) ∧
    (context r).eval=(fun h => (h.val,r h.val)) ∧
    (context r).order=vectorOrder := ⟨rfl,rfl,rfl⟩
end CandidateContextsV24
