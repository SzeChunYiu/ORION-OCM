universe u v w a

inductive Response (O : Type w) where
  | illegal
  | undefined
  | value (o : O)
deriving DecidableEq

def OpEq {H : Type u} {T : Type v} {O : Type w}
    (resp : H → T → Response O) (h₁ h₂ : H) : Prop :=
  ∀ t, resp h₁ t = resp h₂ t

theorem opEq_refl {H : Type u} {T : Type v} {O : Type w}
    (resp : H → T → Response O) (h : H) : OpEq resp h h := by
  intro t
  rfl

theorem opEq_symm {H : Type u} {T : Type v} {O : Type w}
    {resp : H → T → Response O} {h₁ h₂ : H}
    (h : OpEq resp h₁ h₂) : OpEq resp h₂ h₁ := by
  intro t
  exact Eq.symm (h t)

theorem opEq_trans {H : Type u} {T : Type v} {O : Type w}
    {resp : H → T → Response O} {h₁ h₂ h₃ : H}
    (h12 : OpEq resp h₁ h₂) (h23 : OpEq resp h₂ h₃) :
    OpEq resp h₁ h₃ := by
  intro t
  exact Eq.trans (h12 t) (h23 t)

/--
If extending a history by action a and then applying test t is represented
inside the registered test family by pre a t, response equivalence is a
right congruence for that extension.
-/
theorem opEq_step
    {H : Type u} {T : Type v} {O : Type w} {A : Type a}
    (resp : H → T → Response O)
    (step : H → A → H)
    (pre : A → T → T)
    (compat : ∀ h a t, resp (step h a) t = resp h (pre a t))
    {h₁ h₂ : H}
    (heq : OpEq resp h₁ h₂)
    (act : A) :
    OpEq resp (step h₁ act) (step h₂ act) := by
  intro t
  calc
    resp (step h₁ act) t = resp h₁ (pre act t) := compat h₁ act t
    _ = resp h₂ (pre act t) := heq (pre act t)
    _ = resp (step h₂ act) t := Eq.symm (compat h₂ act t)

theorem separating_test_forces_rep_difference
    {H : Type u} {T : Type v} {O : Type w} {R : Type a}
    (resp : H → T → Response O)
    (rep : H → R)
    (decode : R → T → Response O)
    (correct : ∀ h t, decode (rep h) t = resp h t)
    {h₁ h₂ : H}
    (t : T)
    (sep : resp h₁ t ≠ resp h₂ t) :
    rep h₁ ≠ rep h₂ := by
  intro same
  apply sep
  calc
    resp h₁ t = decode (rep h₁) t := Eq.symm (correct h₁ t)
    _ = decode (rep h₂) t := by rw [same]
    _ = resp h₂ t := correct h₂ t
