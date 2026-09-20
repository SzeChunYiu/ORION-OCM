import CumulativeV21
namespace PathPositiveV21
open ContinuationV8 OrderedCostsV21 WeightedExecutionV21 CumulativeV21
universe u v w x y
def Nonnegative {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) (m : Machine S A O E) (cost : E → R) : S → List A → Prop
  | _, [] => True
  | s, a::word => ∀ e t, m.next s a=some (e,t) →
      r.order.le r.one (cost e) ∧ Nonnegative r m cost t word
theorem nonnegative_of_global {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) (m : Machine S A O E) (cost : E → R)
    (positive : ∀ e, r.order.le r.one (cost e)) (word : List A) (s : S) :
    Nonnegative r m cost s word := by
  induction word generalizing s with
  | nil => trivial
  | cons a word ih => exact fun e t _ => ⟨positive e,ih t⟩
theorem weighted_path_nonnegative {S : Type u} {A : Type v} {O : Type w}
    {E : Type x} {R : Type y} (r : CostMonoid R) (m : Machine S A O E)
    (cost : E → R)
    (word : List A) (s t : S) (c : R)
    (positive : Nonnegative r m cost s word)
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
        have hd := ih z q d (positive e z hn).2 hw
        have hg := r.mono (positive e z hn).1 hd
        rw [r.left_id] at hg
        have hc : r.mul (cost e) d=c := congrArg Prod.snd he
        rw [← hc]
        exact hg
theorem prefix_path_iff_final {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) [DecidableRel r.order.le]
    (m : Machine S A O E) (cost : E → R)
    (word : List A) (s t : S) (spent capacity out : R)
    (positive : Nonnegative r m cost s word) :
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
        rw [ih z t (r.mul spent (cost e)) out (positive e z hn).2]
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
        have hc := weighted_path_nonnegative r m cost (act::word) s t c positive hw
        exact False.elim (ha (r.order.trans (grow r spent c hc) hb))
end PathPositiveV21
