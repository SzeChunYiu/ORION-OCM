import PartialContextV15
namespace PartialContextV15
universe u v
def Mutual {A : Type u} (r : PreorderSpec A) (a b : A) := r.le a b ∧ r.le b a
def mutualSetoid {A : Type u} (r : PreorderSpec A) : Setoid A where
  r := Mutual r
  iseqv := ⟨fun a => ⟨r.refl a,r.refl a⟩, And.symm,
    fun hab hbc => ⟨r.trans hab.1 hbc.1,r.trans hbc.2 hab.2⟩⟩
theorem mutual_equivalence {A : Type u} (r : PreorderSpec A) :
    Equivalence (Mutual r) := (mutualSetoid r).iseqv
theorem comparison_invariant {A : Type u} (r : PreorderSpec A) {a b a' b' : A}
    (ha : Mutual r a a') (hb : Mutual r b b') :
    r.le a b ↔ r.le a' b' :=
  ⟨fun h => r.trans ha.2 (r.trans h hb.1),
   fun h => r.trans ha.1 (r.trans h hb.2)⟩
def OrderedQuotient {A : Type u} (r : PreorderSpec A) := Quotient (mutualSetoid r)
def project {A : Type u} (r : PreorderSpec A) (a : A) : OrderedQuotient r :=
  Quotient.mk (mutualSetoid r) a
def quotientLE {A : Type u} (r : PreorderSpec A) (a b : OrderedQuotient r) : Prop :=
  Quotient.liftOn₂ a b r.le (fun _ _ _ _ ha hb => propext (comparison_invariant r ha hb))
theorem quotient_comparison {A : Type u} (r : PreorderSpec A) (a b : A) :
    quotientLE r (project r a) (project r b) ↔ r.le a b := Iff.rfl
theorem quotient_refl {A : Type u} (r : PreorderSpec A) (a : OrderedQuotient r) :
    quotientLE r a a := Quotient.inductionOn a (fun x => r.refl x)
theorem quotient_trans {A : Type u} (r : PreorderSpec A)
    {a b c : OrderedQuotient r} (hab : quotientLE r a b) (hbc : quotientLE r b c) :
    quotientLE r a c := by
  induction a using Quotient.inductionOn with | h a =>
  induction b using Quotient.inductionOn with | h b =>
  induction c using Quotient.inductionOn with | h c =>
  exact r.trans hab hbc
theorem quotient_antisymm {A : Type u} (r : PreorderSpec A)
    {a b : OrderedQuotient r} (hab : quotientLE r a b) (hba : quotientLE r b a) : a=b := by
  induction a using Quotient.inductionOn with | h a =>
  induction b using Quotient.inductionOn with | h b =>
  exact Quotient.sound ⟨hab,hba⟩
def quotientOrder {A : Type u} (r : PreorderSpec A) : PosetSpec (OrderedQuotient r) where
  le := quotientLE r
  refl := quotient_refl r
  trans := quotient_trans r
  antisymm := quotient_antisymm r
theorem project_eq_iff {A : Type u} (r : PreorderSpec A) (a b : A) :
    project r a=project r b ↔ Mutual r a b := by
  constructor
  · intro h
    exact Quotient.exact h
  · intro h
    apply Quotient.sound
    exact h

def contextQuotient {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) :=
  OrderedQuotient (activeOrder P k)
def contextQuotientOrder {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) : PosetSpec (contextQuotient P k) :=
  quotientOrder (activeOrder P k)
theorem context_quotient_comparison {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (a b : Active P k) :
    (contextQuotientOrder P k).le (project (activeOrder P k) a) (project (activeOrder P k) b) ↔
    k.order.le (restrictedEval P k a) (restrictedEval P k b) := Iff.rfl
end PartialContextV15
