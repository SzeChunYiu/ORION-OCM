import AffineContextsV23
namespace AffineDecodersV23
open ScalarV12 PartialContextV15 FrontierOrderV20 ContextMapsV17 AffineContextsV23
universe u v
variable {I : Type u} {α : Type v} [Scalar α]
theorem decode_injective (a b : I→α) (t : α) (i j : I)
    (h : decode a b t i=decode a b t j) : i=j := congrArg Prod.fst h
theorem decode_order (a b : I→α) (t : α) (i j : I) :
    valueOrder.le (decode a b t i) (decode a b t j) ↔
      (codedOrder a b t).le i j := Iff.rfl
theorem actual_postcompose (E : I→Prop) (a b : I→α) (t : α) :
    postcompose (codedContext E a b t) valueOrder (decode a b t)=context E a b t := rfl
theorem decoded_image (P E : I→Prop) (a b : I→α) (t : α) (w : I×α) :
    (∃i,Image P (codedContext E a b t) i ∧ decode a b t i=w) ↔
      Image P (context E a b t) w := by
  rcases w with ⟨j,v⟩
  constructor
  · rintro ⟨i,hi,he⟩
    have hij : i=j := congrArg Prod.fst he
    subst i
    exact (pair_attained P E a b t j v).mpr
      ⟨(coded_attained P E a b t j).mp hi,congrArg Prod.snd he⟩
  · intro h
    obtain ⟨hj,he⟩ := (pair_attained P E a b t j v).mp h
    exact ⟨j,(coded_attained P E a b t j).mpr hj,by simp only [decode,he]⟩
theorem decoded_maximal (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    Maximal (codedOrder a b t) (Image P (codedContext E a b t)) i ↔
      Maximal valueOrder (Image P (context E a b t)) (decode a b t i) := by
  rw [maximal_code,maximal_pair]
theorem decoded_maximal_image (P E : I→Prop) (a b : I→α) (t : α) (w : I×α) :
    (∃i,Maximal (codedOrder a b t) (Image P (codedContext E a b t)) i ∧
      decode a b t i=w) ↔ Maximal valueOrder (Image P (context E a b t)) w := by
  constructor
  · rintro ⟨i,hi,rfl⟩; exact (decoded_maximal P E a b t i).mp hi
  · intro h
    obtain ⟨i,_,he⟩ := (decoded_image P E a b t w).mpr h.1
    refine ⟨i,?_,he⟩
    rw [← he] at h
    exact (decoded_maximal P E a b t i).mpr h
theorem decoded_observe (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    observe P (context E a b t) i=
      outcomeMap (decode a b t) (observe P (codedContext E a b t) i) :=
  post_observe P (codedContext E a b t) valueOrder (decode a b t) i
end AffineDecodersV23
