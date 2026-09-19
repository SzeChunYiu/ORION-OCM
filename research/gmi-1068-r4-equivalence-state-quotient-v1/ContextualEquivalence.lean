universe u v w

def OpEq {H : Type u} {T : Type v} {O : Type w}
    (resp : H → T → O) (h₁ h₂ : H) : Prop :=
  ∀ t, resp h₁ t = resp h₂ t

theorem opEq_refl {H : Type u} {T : Type v} {O : Type w}
    (resp : H → T → O) (h : H) : OpEq resp h h := by
  intro t
  rfl

theorem opEq_symm {H : Type u} {T : Type v} {O : Type w}
    {resp : H → T → O} {h₁ h₂ : H}
    (h : OpEq resp h₁ h₂) : OpEq resp h₂ h₁ := by
  intro t
  exact Eq.symm (h t)

theorem opEq_trans {H : Type u} {T : Type v} {O : Type w}
    {resp : H → T → O} {h₁ h₂ h₃ : H}
    (h12 : OpEq resp h₁ h₂) (h23 : OpEq resp h₂ h₃) :
    OpEq resp h₁ h₃ := by
  intro t
  exact Eq.trans (h12 t) (h23 t)

theorem separating_test_forces_rep_difference
    {H : Type u} {R : Type v} {O : Type w}
    (rep : H → R) (decode : R → O) (obs : H → O)
    (correct : ∀ h, decode (rep h) = obs h)
    {h₁ h₂ : H} (sep : obs h₁ ≠ obs h₂) :
    rep h₁ ≠ rep h₂ := by
  intro same
  apply sep
  calc
    obs h₁ = decode (rep h₁) := Eq.symm (correct h₁)
    _ = decode (rep h₂) := by rw [same]
    _ = obs h₂ := correct h₂
