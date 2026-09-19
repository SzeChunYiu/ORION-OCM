universe u v

def Attain {H : Type u} {W : Type v}
    (Reach : H → Prop) (nu : H → W) (w : W) : Prop :=
  ∃ h, Reach h ∧ nu h = w

theorem attain_mono {H : Type u} {W : Type v}
    {R₁ R₂ : H → Prop} {nu : H → W}
    (hsub : ∀ h, R₁ h → R₂ h) :
    ∀ w, Attain R₁ nu w → Attain R₂ nu w := by
  intro w hw
  rcases hw with ⟨h, hr, hv⟩
  exact ⟨h, hsub h hr, hv⟩

def Maximal {W : Type u}
    (le : W → W → Prop) (A : W → Prop) (w : W) : Prop :=
  A w ∧ ∀ v, A v → le w v → le v w

theorem maximal_is_attainable {W : Type u}
    {le : W → W → Prop} {A : W → Prop} {w : W}
    (h : Maximal le A w) : A w := h.1

def TargetPossible {W : Type u} (A T : W → Prop) : Prop :=
  ∃ w, A w ∧ T w

theorem impossible_means_no_target {W : Type u}
    {A T : W → Prop}
    (h : ¬ TargetPossible A T) :
    ∀ w, A w → ¬ T w := by
  intro w ha ht
  exact h ⟨w, ha, ht⟩
