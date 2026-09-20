import CumulativeV21
namespace BudgetResidualV21
open ContinuationV8 OrderedCostsV21 WeightedExecutionV21 CumulativeV21
universe u v w x
def endpoint {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) : S → List A → Option S
  | s, [] => some s
  | s, a::word => (m.next s a).bind fun (_,t) => endpoint m t word
def budgetEndpoint {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (s : S) (b : Nat) (word : List A) :=
  endpoint (budgetMachine m cost) (s,b) word
theorem endpoint_append {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (u v : List A) (s : S) :
    endpoint m s (u++v)=(endpoint m s u).bind (fun t => endpoint m t v) := by
  induction u generalizing s with
  | nil => rfl
  | cons a u ih =>
    cases hn : m.next s a with
    | none => simp [endpoint,hn]
    | some p => cases p; simp [endpoint,hn,ih]
theorem residual_iff {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (word : List A)
    (s t : S) (b remaining : Nat) :
    budgetEndpoint m cost s b word=some (t,remaining) ↔
      ∃ c, weighted natAdd m cost s word=some (t,c) ∧ c≤b ∧ remaining=b-c := by
  induction word generalizing s t b remaining with
  | nil =>
    simp only [budgetEndpoint,endpoint,weighted,Option.some.injEq,Prod.mk.injEq]
    constructor
    · rintro ⟨hst,hr⟩
      exact ⟨0,⟨hst,rfl⟩,Nat.zero_le b,by omega⟩
    · rintro ⟨c,⟨hst,hc⟩,_,hr⟩
      change 0=c at hc
      exact ⟨hst,by omega⟩
  | cons a word ih =>
    cases hn : m.next s a with
    | none => simp [budgetEndpoint,endpoint,budgetMachine,weighted,hn]
    | some p =>
      rcases p with ⟨e,z⟩
      by_cases hb : cost e≤b
      · change ((budgetMachine m cost).next (s,b) a).bind
          (fun (_,q) => endpoint (budgetMachine m cost) q word)=some (t,remaining) ↔ _
        simp only [budgetMachine,hn,if_pos hb,Option.some_bind]
        change budgetEndpoint m cost z (b-cost e) word=some (t,remaining) ↔ _
        rw [ih]
        constructor
        · rintro ⟨d,hd,hdb,hr⟩
          refine ⟨cost e+d,by simpa [weighted,hn,hd,natAdd],by omega,by omega⟩
        · rintro ⟨c,hc,hcb,hr⟩
          cases hd : weighted natAdd m cost z word with
          | none => simp [weighted,hn,hd] at hc
          | some p =>
            rcases p with ⟨q,d⟩
            have he : (q,cost e+d)=(t,c) := by
              simp only [weighted,hn,Option.some_bind,hd,Option.map_some] at hc
              exact Option.some.inj hc
            have hqt : q=t := congrArg Prod.fst he
            have hdc : cost e+d=c := congrArg Prod.snd he
            subst q
            exact ⟨d,rfl,by omega,by omega⟩
      · simp only [budgetEndpoint,endpoint,budgetMachine,hn,if_neg hb,Option.some_bind,
          Option.none_bind]
        constructor
        · intro h; cases h
        · rintro ⟨c,hc,hcb,_⟩
          cases hd : weighted natAdd m cost z word with
          | none => simp [weighted,hn,hd] at hc
          | some p =>
            rcases p with ⟨q,d⟩
            have he : (q,cost e+d)=(t,c) := by
              simp only [weighted,hn,Option.some_bind,hd,Option.map_some] at hc
              exact Option.some.inj hc
            have hdc : cost e+d=c := congrArg Prod.snd he
            exact False.elim (hb (by omega))
theorem budget_append {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (s : S) (b : Nat) (u v : List A) :
    budgetEndpoint m cost s b (u++v)=
      (budgetEndpoint m cost s b u).bind (fun (t,r) => budgetEndpoint m cost t r v) :=
  endpoint_append (budgetMachine m cost) u v (s,b)
theorem larger_budget {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (s t : S) (word : List A)
    (lo hi r : Nat) (hle : lo≤hi)
    (hs : budgetEndpoint m cost s lo word=some (t,r)) :
    ∃ c, weighted natAdd m cost s word=some (t,c) ∧ c≤lo ∧ r=lo-c ∧
      budgetEndpoint m cost s hi word=some (t,hi-c) := by
  obtain ⟨c,hc,hcl,hr⟩ := (residual_iff m cost word s t lo r).mp hs
  exact ⟨c,hc,hcl,hr,(residual_iff m cost word s t hi (hi-c)).mpr
    ⟨c,hc,Nat.le_trans hcl hle,rfl⟩⟩
instance natComparison : DecidableRel natAdd.order.le := fun a b => inferInstanceAs (Decidable (a≤b))
theorem cumulative_nat {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (s t : S) (word : List A) (b c : Nat) :
    cumulative natAdd m cost b s 0 word=some (t,c) ↔
      weighted natAdd m cost s word=some (t,c) ∧ c≤b := by
  rw [prefix_iff_final natAdd m cost (fun e => Nat.zero_le (cost e))]
  change (∃ d, weighted natAdd m cost s word=some (t,d) ∧ 0+d≤b ∧ c=0+d) ↔ _
  simp only [Nat.zero_add]
  constructor
  · rintro ⟨d,hd,hdb,hcd⟩
    subst d
    exact ⟨hd,hdb⟩
  · rintro ⟨hc,hcb⟩
    exact ⟨c,hc,hcb,rfl⟩
theorem cumulative_residual {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (s t : S) (word : List A) (b r : Nat) :
    budgetEndpoint m cost s b word=some (t,r) ↔
      ∃ c, cumulative natAdd m cost b s 0 word=some (t,c) ∧ r=b-c := by
  simp only [residual_iff,cumulative_nat,and_assoc]
end BudgetResidualV21
