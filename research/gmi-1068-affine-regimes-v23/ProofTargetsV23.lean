import ConstructorBindingsV23
namespace ProofTargetsV23
open ScalarV12 AffineArithmeticV23 AffineIntervalsV23 PartialContextV15 FrontierOrderV20
open AffineContextsV23 AffineDecodersV23 AffineWinnersV23
universe u v
theorem endpoint_contract {α : Type v} [Scalar α] (a b c d lo hi : α) (h : lo≤hi) :
    ((∀t,lo≤t→t≤hi→affine a b t≤affine c d t) ↔
      affine a b lo≤affine c d lo∧affine a b hi≤affine c d hi) ∧
    ((∀t,lo≤t→t≤hi→affine a b t<affine c d t) ↔
      affine a b lo<affine c d lo∧affine a b hi<affine c d hi) :=
  ⟨interval_le_iff a b c d lo hi h,interval_lt_iff a b c d lo hi h⟩
theorem decoder_maximal_contract {I : Type u} {α : Type v} [Scalar α]
    (P E : I→Prop) (a b : I→α) (t : α) (w : I×α) :
    (∃i,Maximal (codedOrder a b t) (Image P (codedContext E a b t)) i∧
      decode a b t i=w) ↔ Maximal valueOrder (Image P (context E a b t)) w :=
  decoded_maximal_image P E a b t w
theorem universal_winner_contract {I : Type u} {α : Type v} [Scalar α]
    (P E : I→Prop) (a b : I→α) (lo hi : α) (h : lo≤hi) (i : I) :
    ((∀t,lo≤t→t≤hi→Winner P E a b t i) ↔
      Winner P E a b lo i∧Winner P E a b hi i) ∧
    ((∀t,lo≤t→t≤hi→UniqueWinner P E a b t i) ↔
      active P E i∧∀j,active P E j→j≠i→
        score a b lo i<score a b lo j∧score a b hi i<score a b hi j) :=
  ⟨universal_winner P E a b lo hi h i,universal_unique_explicit P E a b lo hi h i⟩
end ProofTargetsV23
