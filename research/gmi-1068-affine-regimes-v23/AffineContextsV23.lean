import AffineIntervalsV23
import PartialPostcontextV20
import ContextMapsV17
namespace AffineContextsV23
open ScalarV12 AffineArithmeticV23 PartialContextV15 PartialPostcontextV20 FrontierOrderV20
universe u v
variable {I : Type u} {α : Type v} [Scalar α]
def score (a b : I→α) (t : α) (i : I) := affine (a i) (b i) t
def active (P E : I→Prop) (i : I) := P i ∧ E i
def valueOrder : PreorderSpec (I×α) where
  le x y := y.2≤x.2
  refl _ := Scalar.le_refl _
  trans h g := Scalar.le_trans g h
def context (E : I→Prop) (a b : I→α) (t : α) : Context I (I×α) where
  defined := E
  eval i := (i.val,score a b t i.val)
  order := valueOrder
def codedOrder (a b : I→α) (t : α) : PreorderSpec I where
  le i j := score a b t j≤score a b t i
  refl _ := Scalar.le_refl _
  trans h g := Scalar.le_trans g h
def codedContext (E : I→Prop) (a b : I→α) (t : α) : Context I I where
  defined := E
  eval i := i.val
  order := codedOrder a b t
def decode (a b : I→α) (t : α) (i : I) := (i,score a b t i)
def Image {W : Type v} (P : I→Prop) (k : Context I W) :=
  Attained P k (fun _ => True)
def Winner (P E : I→Prop) (a b : I→α) (t : α) (i : I) :=
  active P E i ∧ ∀j,active P E j→score a b t i≤score a b t j
theorem pair_attained (P E : I→Prop) (a b : I→α) (t : α) (i : I) (v : α) :
    Image P (context E a b t) (i,v) ↔ active P E i ∧ score a b t i=v := by
  constructor
  · rintro ⟨j,_,hp,he,hv⟩
    have hij : j=i := congrArg Prod.fst hv
    subst j
    exact ⟨⟨hp,he⟩,congrArg Prod.snd hv⟩
  · rintro ⟨⟨hp,he⟩,hv⟩
    exact ⟨i,True.intro,hp,he,by simp only [context,hv]⟩
theorem coded_attained (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    Image P (codedContext E a b t) i ↔ active P E i := by
  constructor
  · rintro ⟨j,_,hp,he,hji⟩
    change j=i at hji
    subst j
    exact ⟨hp,he⟩
  · rintro ⟨hp,he⟩; exact ⟨i,True.intro,hp,he,rfl⟩
theorem maximal_pair (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    Maximal valueOrder (Image P (context E a b t)) (decode a b t i) ↔
      Winner P E a b t i := by
  constructor
  · rintro ⟨hi,hm⟩
    refine ⟨((pair_attained P E a b t i _).mp hi).1,?_⟩
    intro j hj
    rcases Scalar.le_total (score a b t j) (score a b t i) with hji|hij
    · exact hm (decode a b t j) ((pair_attained P E a b t j _).mpr ⟨hj,rfl⟩) hji
    · exact hij
  · rintro ⟨hi,hm⟩
    refine ⟨(pair_attained P E a b t i _).mpr ⟨hi,rfl⟩,?_⟩
    rintro ⟨j,v⟩ hj _
    obtain ⟨hja,hv⟩ := (pair_attained P E a b t j v).mp hj
    change score a b t i≤v
    rw [← hv]
    exact hm j hja
theorem maximal_identity_projection (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    (∃v,Maximal valueOrder (Image P (context E a b t)) (i,v)) ↔
      Winner P E a b t i := by
  constructor
  · rintro ⟨v,hv⟩
    have he := ((pair_attained P E a b t i v).mp hv.1).2
    rw [← he] at hv
    exact (maximal_pair P E a b t i).mp hv
  · intro h
    exact ⟨score a b t i,(maximal_pair P E a b t i).mpr h⟩
theorem maximal_code (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    Maximal (codedOrder a b t) (Image P (codedContext E a b t)) i ↔
      Winner P E a b t i := by
  constructor
  · rintro ⟨hi,hm⟩
    refine ⟨(coded_attained P E a b t i).mp hi,?_⟩
    intro j hj
    rcases Scalar.le_total (score a b t j) (score a b t i) with hji|hij
    · exact hm j ((coded_attained P E a b t j).mpr hj) hji
    · exact hij
  · rintro ⟨hi,hm⟩
    exact ⟨(coded_attained P E a b t i).mpr hi,
      fun j hj _ => hm j ((coded_attained P E a b t j).mp hj)⟩
theorem tied_winner (P E : I→Prop) (a b : I→α) (t : α) (i j : I)
    (hi : Winner P E a b t i) (hj : active P E j)
    (he : score a b t i=score a b t j) : Winner P E a b t j := by
  refine ⟨hj,?_⟩
  intro k hk
  rw [← he]
  exact hi.2 k hk
end AffineContextsV23
