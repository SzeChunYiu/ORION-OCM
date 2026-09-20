import BudgetResidualV21
namespace SuccessfulResponseV21
open ContinuationV8 OrderedCostsV21 WeightedExecutionV21 BudgetResidualV21
universe u v w x y
theorem weighted_endpoint {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) (m : Machine S A O E) (cost : E → R)
    (word : List A) (s : S) :
    (weighted r m cost s word).map Prod.fst=endpoint m s word := by
  induction word generalizing s with
  | nil => rfl
  | cons a word ih =>
    cases hn : m.next s a with
    | none => simp [weighted,endpoint,hn]
    | some p =>
      rcases p with ⟨e,t⟩
      simp only [weighted,endpoint,hn,Option.some_bind,Option.map_map]
      exact ih t
theorem weighted_success_response {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (word : List A)
    (s t : S) (c b : Nat) (hw : weighted natAdd m cost s word=some (t,c)) (hb : c≤b) :
    run (budgetMachine m cost) (s,b) word=run m s word := by
  induction word generalizing s t c b with
  | nil => rfl
  | cons a word ih =>
    cases hn : m.next s a with
    | none => simp [weighted,hn] at hw
    | some p =>
      rcases p with ⟨e,z⟩
      cases ht : weighted natAdd m cost z word with
      | none => simp [weighted,hn,ht] at hw
      | some p =>
        rcases p with ⟨q,d⟩
        have he : (q,cost e+d)=(t,c) := by
          simp only [weighted,hn,Option.some_bind,ht,Option.map_some] at hw
          exact Option.some.inj hw
        have hc : cost e+d=c := congrArg Prod.snd he
        have hefit : cost e≤b := by omega
        have hdfit : d≤b-cost e := by omega
        have hr := ih z q d (b-cost e) ht hdfit
        simpa only [run,budgetMachine,hn,if_pos hefit] using
          congrArg (Response.step (m.obs s) e) hr
theorem successful_full_response {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (word : List A)
    (s t : S) (b r : Nat) (h : budgetEndpoint m cost s b word=some (t,r)) :
    run (budgetMachine m cost) (s,b) word=run m s word := by
  obtain ⟨c,hc,hcb,_⟩ := (residual_iff m cost word s t b r).mp h
  exact weighted_success_response m cost word s t c b hc hcb
end SuccessfulResponseV21
