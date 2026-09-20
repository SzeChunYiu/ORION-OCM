import WeightedExecutionV21
namespace CumulativeV21
open ContinuationV8 OrderedCostsV21 WeightedExecutionV21
universe u v w x y
def cumulative {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) [DecidableRel r.order.le] (m : Machine S A O E) (cost : E → R)
    (capacity : R) : S → R → List A → Option (S × R)
  | s, spent, word => if r.order.le spent capacity then
      match word with
      | [] => some (s,spent)
      | a::tail => (m.next s a).bind fun (e,t) =>
          cumulative r m cost capacity t (r.mul spent (cost e)) tail
    else none
theorem cumulative_initial {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) [DecidableRel r.order.le]
    (m : Machine S A O E) (cost : E → R) (b a : R) (s : S) (word : List A)
    (ha : ¬r.order.le a b) : cumulative r m cost b s a word=none := by
  cases word <;> simp [cumulative,ha]
theorem cumulative_empty {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) [DecidableRel r.order.le]
    (m : Machine S A O E) (cost : E → R) (b a : R) (s : S) :
    cumulative r m cost b s a []=if r.order.le a b then some (s,a) else none := rfl
theorem capacity_nesting {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) [DecidableRel r.order.le]
    (m : Machine S A O E) (cost : E → R) (lo hi : R) (h : r.order.le lo hi)
    (word : List A) (s : S) (a : R) (result : S × R)
    (hs : cumulative r m cost lo s a word=some result) :
    cumulative r m cost hi s a word=some result := by
  induction word generalizing s a with
  | nil =>
    by_cases ha : r.order.le a lo
    · simpa [cumulative,ha,r.order.trans ha h] using hs
    · simp [cumulative,ha] at hs
  | cons act word ih =>
    by_cases ha : r.order.le a lo
    · cases hn : m.next s act with
      | none => simp [cumulative,ha,hn] at hs
      | some p =>
        rcases p with ⟨e,t⟩
        have ht := ih t (r.mul a (cost e)) (by simpa [cumulative,ha,hn] using hs)
        simpa [cumulative,r.order.trans ha h,hn] using ht
    · simp [cumulative,ha] at hs
theorem prefix_iff_final {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) [DecidableRel r.order.le]
    (m : Machine S A O E) (cost : E → R)
    (positive : ∀ e, r.order.le r.one (cost e))
    (word : List A) (s t : S) (spent capacity out : R) :
    cumulative r m cost capacity s spent word=some (t,out) ↔
      ∃ c, weighted r m cost s word=some (t,c) ∧
        r.order.le (r.mul spent c) capacity ∧ out=r.mul spent c := by
  induction word generalizing s t spent out with
  | nil =>
    by_cases ha : r.order.le spent capacity
    · constructor
      · intro h
        have he : (s,spent)=(t,out) := by simpa [cumulative,ha] using h
        cases he
        exact ⟨r.one,rfl,by simpa only [r.right_id] using ha,(r.right_id spent).symm⟩
      · rintro ⟨c,hc,_,hout⟩
        have he : (s,r.one)=(t,c) := Option.some.inj hc
        cases he
        rw [r.right_id] at hout
        subst out
        simp [cumulative,ha]
    · simp [cumulative,weighted,ha,r.right_id]
  | cons act word ih =>
    by_cases ha : r.order.le spent capacity
    · cases hn : m.next s act with
      | none => simp [cumulative,weighted,ha,hn]
      | some p =>
        rcases p with ⟨e,z⟩
        simp only [cumulative,if_pos ha,hn,Option.some_bind]
        rw [ih]
        constructor
        · rintro ⟨c,hw,hb,hout⟩
          refine ⟨r.mul (cost e) c,by simp [weighted,hn,hw],?_,?_⟩
          · simpa only [r.assoc] using hb
          · simpa only [r.assoc] using hout
        · rintro ⟨c,hw,hb,hout⟩
          cases ht : weighted r m cost z word with
          | none => simp [weighted,hn,ht] at hw
          | some p =>
            rcases p with ⟨q,d⟩
            have he : (q,r.mul (cost e) d)=(t,c) := by
              simpa [weighted,hn,ht] using hw
            have hqt : q=t := congrArg Prod.fst he
            have hdc : r.mul (cost e) d=c := congrArg Prod.snd he
            subst q
            subst c
            exact ⟨d,rfl,by simpa only [r.assoc] using hb,
              by simpa only [r.assoc] using hout⟩
    · rw [cumulative_initial r m cost capacity spent s (act::word) ha]
      constructor
      · intro hn; cases hn
      · rintro ⟨c,hw,hb,_⟩
        have hc := weighted_nonnegative r m cost positive (act::word) s t c hw
        exact False.elim (ha (r.order.trans (grow r spent c hc) hb))
end CumulativeV21
