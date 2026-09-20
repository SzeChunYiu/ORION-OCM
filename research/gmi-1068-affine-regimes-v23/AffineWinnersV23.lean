import AffineDecodersV23
namespace AffineWinnersV23
open ScalarV12 AffineArithmeticV23 AffineIntervalsV23 AffineContextsV23
universe u v
variable {I : Type u} {α : Type v} [Scalar α]
def UniqueWinner (P E : I→Prop) (a b : I→α) (t : α) (i : I) :=
  Winner P E a b t i ∧ ∀j,Winner P E a b t j→j=i
def StrictWinner (P E : I→Prop) (a b : I→α) (t : α) (i : I) :=
  active P E i ∧ ∀j,active P E j→j≠i→score a b t i<score a b t j
theorem unique_iff_strict (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    UniqueWinner P E a b t i ↔ StrictWinner P E a b t i := by
  classical
  constructor
  · rintro ⟨hi,hu⟩
    refine ⟨hi.1,?_⟩
    intro j hj hji
    apply (Scalar.lt_iff _ _).mpr
    refine ⟨hi.2 j hj,?_⟩
    intro he
    exact hji (hu j (tied_winner P E a b t i j hi hj he))
  · rintro ⟨hi,hs⟩
    have hw : Winner P E a b t i := by
      refine ⟨hi,?_⟩
      intro j hj
      by_cases he : j=i
      · subst j; exact Scalar.le_refl _
      · exact le_of_lt (hs j hj he)
    refine ⟨hw,?_⟩
    intro j hj
    apply Classical.byContradiction
    intro he
    exact not_le_of_lt (hs j hj.1 he) (hj.2 i hi)
theorem universal_winner (P E : I→Prop) (a b : I→α) (lo hi : α)
    (h : lo≤hi) (i : I) :
    (∀t,lo≤t→t≤hi→Winner P E a b t i) ↔
      Winner P E a b lo i ∧ Winner P E a b hi i := by
  constructor
  · intro ht
    exact ⟨ht lo (Scalar.le_refl _) h,ht hi h (Scalar.le_refl _)⟩
  · rintro ⟨hl,hh⟩ t hlt hth
    refine ⟨hl.1,?_⟩
    intro j hj
    exact interval_le (a i) (b i) (a j) (b j) lo hi t hlt hth
      (hl.2 j hj) (hh.2 j hj)
theorem universal_strict (P E : I→Prop) (a b : I→α) (lo hi : α)
    (h : lo≤hi) (i : I) :
    (∀t,lo≤t→t≤hi→StrictWinner P E a b t i) ↔
      StrictWinner P E a b lo i ∧ StrictWinner P E a b hi i := by
  constructor
  · intro ht
    exact ⟨ht lo (Scalar.le_refl _) h,ht hi h (Scalar.le_refl _)⟩
  · rintro ⟨hl,hh⟩ t hlt hth
    refine ⟨hl.1,?_⟩
    intro j hj hji
    exact interval_lt (a i) (b i) (a j) (b j) lo hi t hlt hth
      (hl.2 j hj hji) (hh.2 j hj hji)
theorem universal_unique (P E : I→Prop) (a b : I→α) (lo hi : α)
    (h : lo≤hi) (i : I) :
    (∀t,lo≤t→t≤hi→UniqueWinner P E a b t i) ↔
      StrictWinner P E a b lo i ∧ StrictWinner P E a b hi i := by
  simp only [unique_iff_strict]
  exact universal_strict P E a b lo hi h i
theorem universal_unique_explicit (P E : I→Prop) (a b : I→α) (lo hi : α)
    (h : lo≤hi) (i : I) :
    (∀t,lo≤t→t≤hi→UniqueWinner P E a b t i) ↔
      active P E i ∧ ∀j,active P E j→j≠i→
        score a b lo i<score a b lo j ∧ score a b hi i<score a b hi j := by
  rw [universal_unique P E a b lo hi h i]
  constructor
  · rintro ⟨hl,hh⟩
    exact ⟨hl.1,fun j hj hji => ⟨hl.2 j hj hji,hh.2 j hj hji⟩⟩
  · rintro ⟨ha,hs⟩
    exact ⟨⟨ha,fun j hj hji => (hs j hj hji).1⟩,
      ⟨ha,fun j hj hji => (hs j hj hji).2⟩⟩
theorem no_active_no_winner (P E : I→Prop) (a b : I→α) (t : α)
    (h : ¬∃i,active P E i) : ¬∃i,Winner P E a b t i := by
  rintro ⟨i,hi⟩
  exact h ⟨i,hi.1⟩
theorem singleton_active_unique (P E : I→Prop) (a b : I→α) (t : α) (i : I)
    (hi : active P E i) (h : ∀j,active P E j→j=i) : UniqueWinner P E a b t i := by
  apply (unique_iff_strict P E a b t i).mpr
  exact ⟨hi,fun j hj hji => False.elim (hji (h j hj))⟩
theorem zero_width (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    (∀s,t≤s→s≤t→Winner P E a b s i) ↔ Winner P E a b t i := by
  rw [universal_winner P E a b t t (Scalar.le_refl _) i]
  exact ⟨And.left,fun h => ⟨h,h⟩⟩
end AffineWinnersV23
