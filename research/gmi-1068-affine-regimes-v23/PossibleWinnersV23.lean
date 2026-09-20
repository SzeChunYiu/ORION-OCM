import FiniteWinnersV23
namespace PossibleWinnersV23
open ScalarV12 AffineContextsV23 AffineWinnersV23 FiniteWinnersV23
universe u v
variable {I : Type u} {α : Type v} [Scalar α]
def Possible (P E : I→Prop) (a b : I→α) (lo hi : α) (i : I) :=
  ∃t,lo≤t ∧ t≤hi ∧ Winner P E a b t i
theorem possible_binding (P E : I→Prop) (a b : I→α) (lo hi : α) (i : I) :
    Possible P E a b lo hi i ↔ ∃t,lo≤t ∧ t≤hi ∧ Winner P E a b t i := Iff.rfl
theorem singleton_possible (P E : I→Prop) (a b : I→α) (lo hi : α)
    (h : lo≤hi) (xs : List I) (complete : ∀i,active P E i→i∈xs) (i : I) :
    (∀j,Possible P E a b lo hi j ↔ j=i) ↔
      ∀t,lo≤t→t≤hi→UniqueWinner P E a b t i := by
  constructor
  · intro hs
    obtain ⟨s,_,_,hw⟩ := (hs i).mpr rfl
    intro t hlt hth
    obtain ⟨j,hj⟩ := finite_winner P E a b t xs complete ⟨i,hw.1⟩
    have he := (hs j).mp ⟨t,hlt,hth,hj⟩
    subst j
    exact ⟨hj,fun k hk => (hs k).mp ⟨t,hlt,hth,hk⟩⟩
  · intro hu j
    constructor
    · rintro ⟨t,hlt,hth,hj⟩
      exact (hu t hlt hth).2 j hj
    · intro he
      subst j
      exact ⟨lo,Scalar.le_refl _,h,(hu lo (Scalar.le_refl _) h).1⟩
end PossibleWinnersV23
