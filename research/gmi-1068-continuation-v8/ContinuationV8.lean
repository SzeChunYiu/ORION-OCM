import Std
namespace ContinuationV8
universe u v w x y
inductive Response (O : Type w) (E : Type x) where
  | done : O → Response O E
  | illegal : O → Response O E
  | step : O → E → Response O E → Response O E
  deriving DecidableEq

structure Machine (S : Type u) (A : Type v) (O : Type w) (E : Type x) where
  obs : S → O
  next : S → A → Option (E × S)

def run (m : Machine S A O E) (s : S) : List A → Response O E
  | [] => .done (m.obs s)
  | a :: w => match m.next s a with
    | none => .illegal (m.obs s)
    | some (e,t) => .step (m.obs s) e (run m t w)

def Equivalent (m : Machine S A O E) (s t : S) : Prop :=
  ∀ w, run m s w = run m t w

def behaviorSetoid (m : Machine S A O E) : Setoid S where
  r := Equivalent m
  iseqv := ⟨fun _ _ => rfl, fun h w => (h w).symm,
    fun h g w => (h w).trans (g w)⟩

theorem observations_equal {m : Machine S A O E} (h : Equivalent m s t) :
    m.obs s = m.obs t := by
  have h0 := h []
  simpa [run] using h0

theorem transition_congruence {m : Machine S A O E}
    (h : Equivalent m s t) (a : A) :
    match m.next s a, m.next t a with
    | none, none => True
    | some (e,u), some (f,v) => e = f ∧ Equivalent m u v
    | _, _ => False := by
  have h1 := h [a]
  cases hs : m.next s a with
  | none =>
    cases ht : m.next t a with
    | none => trivial
    | some p => cases p; simp [run, hs, ht] at h1
  | some p =>
    rcases p with ⟨e,u⟩
    cases ht : m.next t a with
    | none => simp [run, hs, ht] at h1
    | some p =>
      rcases p with ⟨f,v⟩
      simp only [hs, ht]
      constructor
      · have hh : m.obs s = m.obs t ∧ e = f ∧ m.obs u = m.obs v := by
          simpa [run, hs, ht] using h1
        exact hh.2.1
      · intro w
        exact (Response.step.inj (by
          simpa [run, hs, ht] using h (a :: w))).2.2

abbrev Behavior (m : Machine S A O E) := Quotient (behaviorSetoid m)
def project (m : Machine S A O E) (s : S) : Behavior m := Quotient.mk _ s
def mappedNext (m : Machine S A O E) (s : S) (a : A) :
    Option (E × Behavior m) :=
  (m.next s a).map (fun p => (p.1, project m p.2))

theorem mappedNext_equal {m : Machine S A O E}
    (h : Equivalent m s t) (a : A) : mappedNext m s a = mappedNext m t a := by
  have hc := transition_congruence h a
  cases hs : m.next s a with
  | none =>
    cases ht : m.next t a with
    | none => simp [mappedNext, hs, ht]
    | some p => simp [hs, ht] at hc
  | some p =>
    rcases p with ⟨e,u⟩
    cases ht : m.next t a with
    | none => simp [hs, ht] at hc
    | some p =>
      rcases p with ⟨f,v⟩
      simp only [hs, ht] at hc
      have he := hc.1
      have hq : project m u = project m v := Quotient.sound hc.2
      simp [mappedNext, hs, ht, he, hq]

def quotientMachine (m : Machine S A O E) : Machine (Behavior m) A O E where
  obs := Quotient.lift m.obs (fun _ _ h => observations_equal h)
  next q a := Quotient.lift (fun s => mappedNext m s a)
    (fun _ _ h => mappedNext_equal h a) q

theorem quotient_obs (m : Machine S A O E) (s : S) :
    (quotientMachine m).obs (project m s) = m.obs s := rfl

theorem quotient_next (m : Machine S A O E) (s : S) (a : A) :
    (quotientMachine m).next (project m s) a = mappedNext m s a := rfl

theorem quotient_response_preserved (m : Machine S A O E) (s : S) (w : List A) :
    run (quotientMachine m) (project m s) w = run m s w := by
  induction w generalizing s with
  | nil => rfl
  | cons a w ih =>
    simp only [run, quotient_obs, quotient_next]
    cases hs : m.next s a with
    | none =>
      simp [mappedNext, hs, run]
    | some p =>
      rcases p with ⟨e,t⟩
      simp [mappedNext, hs, ih]

def Sufficient (m : Machine S A O E) (z : S → Z) : Prop :=
  ∃ decode : Z → List A → Response O E, ∀ s w, decode (z s) w = run m s w

theorem sufficient_separates {m : Machine S A O E} {z : S → Z}
    (hz : Sufficient m z) (he : z s = z t) : Equivalent m s t := by
  rcases hz with ⟨decode, hd⟩
  intro w
  rw [← hd s w, he, hd t w]

def Attained (z : S → Z) := {v : Z // ∃ s, z s = v}
def attained (z : S → Z) (s : S) : Attained z := ⟨z s, s, rfl⟩
noncomputable def factor (m : Machine S A O E) (z : S → Z) :
    Attained z → Behavior m :=
  fun v => project m (Classical.choose v.property)

theorem factor_commutes {m : Machine S A O E} {z : S → Z}
    (hz : Sufficient m z) (s : S) :
    factor m z (attained z s) = project m s := by
  apply Quotient.sound
  apply sufficient_separates hz
  exact Classical.choose_spec (attained z s).property

theorem factor_unique {m : Machine S A O E} {z : S → Z}
    (hz : Sufficient m z) (f : Attained z → Behavior m)
    (hf : ∀ s, f (attained z s) = project m s) : f = factor m z := by
  funext v
  rcases v.property with ⟨s, hs⟩
  have hv : attained z s = v := Subtype.ext hs
  rw [← hv, hf s, factor_commutes hz s]

theorem factor_surjective {m : Machine S A O E} {z : S → Z}
    (hz : Sufficient m z) : ∀ q, ∃ v, factor m z v = q := by
  intro q
  induction q using Quotient.inductionOn with
  | _ s => exact ⟨attained z s, factor_commutes hz s⟩

def budgetMachine (m : Machine S A O E) (cost : E → Nat) :
    Machine (S × Nat) A O E where
  obs p := m.obs p.1
  next p a := match m.next p.1 a with
    | none => none
    | some (e,t) =>
      if cost e ≤ p.2 then some (e,(t,p.2-cost e)) else none

theorem budget_lifting {m : Machine S A O E} (cost : E → Nat)
    {s t : S} (h : Equivalent m s t) (b : Nat) (w : List A) :
    run (budgetMachine m cost) (s,b) w = run (budgetMachine m cost) (t,b) w := by
  induction w generalizing s t b with
  | nil => simp [run, budgetMachine, observations_equal h]
  | cons a w ih =>
    have ho := observations_equal h
    have hc := transition_congruence h a
    cases hs : m.next s a with
    | none =>
      cases ht : m.next t a with
      | none => simp [run, budgetMachine, hs, ht, ho]
      | some p => simp [hs, ht] at hc
    | some p =>
      rcases p with ⟨e,u⟩
      cases ht : m.next t a with
      | none => simp [hs, ht] at hc
      | some p =>
        rcases p with ⟨f,v⟩
        simp only [hs, ht] at hc
        rcases hc with ⟨he, huv⟩
        subst f
        by_cases hb : cost e ≤ b
        · simpa [run, budgetMachine, hs, ht, hb, ho] using
            congrArg (Response.step (m.obs t) e) (ih huv (b-cost e))
        · simp [run, budgetMachine, hs, ht, hb, ho]

end ContinuationV8
