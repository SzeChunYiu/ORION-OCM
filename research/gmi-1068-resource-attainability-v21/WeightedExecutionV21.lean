import ContinuationV8
import OrderedCostsV21
namespace WeightedExecutionV21
open ContinuationV8 OrderedCostsV21
universe u v w x y
def weighted {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) (m : Machine S A O E) (cost : E → R) :
    S → List A → Option (S × R)
  | s, [] => some (s,r.one)
  | s, a::word => (m.next s a).bind fun (e,t) =>
      (weighted r m cost t word).map fun (z,c) => (z,r.mul (cost e) c)
theorem weighted_empty {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) (m : Machine S A O E) (cost : E → R) (s : S) :
    weighted r m cost s []=some (s,r.one) := rfl
theorem weighted_cons {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) (m : Machine S A O E) (cost : E → R)
    (s : S) (a : A) (word : List A) :
    weighted r m cost s (a::word)=(m.next s a).bind (fun (e,t) =>
      (weighted r m cost t word).map (fun (z,c) => (z,r.mul (cost e) c))) := rfl
theorem weighted_append {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) (m : Machine S A O E) (cost : E → R)
    (u v : List A) (s : S) :
    weighted r m cost s (u++v)=
      (weighted r m cost s u).bind (fun (t,c) =>
        (weighted r m cost t v).map (fun (z,d) => (z,r.mul c d))) := by
  induction u generalizing s with
  | nil => simp [weighted,r.left_id]
  | cons a u ih =>
    cases hn : m.next s a with
    | none => simp [weighted,hn]
    | some p =>
      rcases p with ⟨e,t⟩
      simp only [List.cons_append,weighted,hn,Option.some_bind]
      rw [ih]
      cases hu : weighted r m cost t u with
      | none => simp
      | some p =>
        rcases p with ⟨z,c⟩
        cases hv : weighted r m cost z v with
        | none => simp [hv]
        | some p =>
          rcases p with ⟨q,d⟩
          simp [hv,r.assoc]
theorem weighted_nonnegative {S : Type u} {A : Type v} {O : Type w}
    {E : Type x} {R : Type y} (r : CostMonoid R) (m : Machine S A O E)
    (cost : E → R) (positive : ∀ e, r.order.le r.one (cost e))
    (word : List A) (s t : S) (c : R)
    (h : weighted r m cost s word=some (t,c)) : r.order.le r.one c := by
  induction word generalizing s t c with
  | nil =>
    have he := Option.some.inj h
    cases he
    exact r.order.refl _
  | cons a word ih =>
    cases hn : m.next s a with
    | none => simp [weighted,hn] at h
    | some p =>
      rcases p with ⟨e,z⟩
      cases hw : weighted r m cost z word with
      | none => simp [weighted,hn,hw] at h
      | some p =>
        rcases p with ⟨q,d⟩
        have he : (q,r.mul (cost e) d)=(t,c) := by simpa [weighted,hn,hw] using h
        have hd := ih z q d hw
        have hg := r.mono (positive e) hd
        rw [r.left_id] at hg
        have hc : r.mul (cost e) d=c := congrArg Prod.snd he
        rw [← hc]
        exact hg
end WeightedExecutionV21
