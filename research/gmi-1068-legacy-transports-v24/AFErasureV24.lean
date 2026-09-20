import ProfileContextsV24
namespace AFErasureV24
open ProfileContextsV24
universe u
def erase {M E A : Type u} (label : E → A) (h : M × List E) : M × List A :=
  (h.1,h.2.map label)
def consumed {A Q : Type u} (initial : Q) (tags : A → Q → Prop)
    (word : List A) (q : Q) := q=initial ∨ ∃ a, a∈word ∧ tags a q
noncomputable def present {A Q : Type u} (initial : Q) (tags : A → Q → Prop)
    (word : List A) (q : Q) : Bool := by
  classical
  exact decide (consumed initial tags word q)
noncomputable def oldProfile {M A C Q : Type u} (cap : M → C)
    (initial external oracle : Q) (tags : A → Q → Prop) (h : M × List A) :
    Profile C (Nat × Bool × Bool) (Q → Prop) M (List A) :=
  ⟨cap h.1,(h.2.length,present initial tags h.2 external,present initial tags h.2 oracle),
   consumed initial tags h.2,h.1,h.2⟩
noncomputable def fullProjection {M E A C Q : Type u} (label : E → A)
    (cap : M → C) (initial external oracle : Q) (tags : A → Q → Prop)
    (h : M × List E) := oldProfile cap initial external oracle tags (erase label h)
theorem erase_binding {M E A : Type u} (label : E → A) (h : M × List E) :
    erase label h=(h.1,h.2.map label) := rfl
theorem consumed_nil {A Q : Type u} (initial : Q) (tags : A → Q → Prop) (q : Q) :
    consumed initial tags [] q ↔ q=initial := by simp [consumed]
theorem consumed_cons {A Q : Type u} (initial : Q) (tags : A → Q → Prop)
    (a : A) (word : List A) (q : Q) :
    consumed initial tags (a::word) q ↔ tags a q ∨ consumed initial tags word q := by
  simp only [consumed,List.mem_cons]
  constructor
  · rintro (hi | ⟨b,hb,ht⟩)
    · exact Or.inr (Or.inl hi)
    · rcases hb with he | hm
      · exact Or.inl (he ▸ ht)
      · exact Or.inr (Or.inr ⟨b,hm,ht⟩)
  · rintro (ht | hi | ⟨b,hm,ht⟩)
    · exact Or.inr ⟨a,Or.inl rfl,ht⟩
    · exact Or.inl hi
    · exact Or.inr ⟨b,Or.inr hm,ht⟩
theorem presence_binding {A Q : Type u} (initial : Q) (tags : A → Q → Prop)
    (word : List A) (q : Q) : present initial tags word q=true ↔ consumed initial tags word q := by
  classical
  simp [present]
theorem repeated_presence {A Q : Type u} (initial : Q) (tags : A → Q → Prop)
    (a : A) (q : Q) : present initial tags [a,a] q=present initial tags [a] q := by
  classical
  simp [present,consumed]
theorem profile_binding {M A C Q : Type u} (cap : M → C)
    (initial external oracle : Q) (tags : A → Q → Prop) (h : M × List A) :
    oldProfile cap initial external oracle tags h =
    ⟨cap h.1,(h.2.length,present initial tags h.2 external,present initial tags h.2 oracle),
      consumed initial tags h.2,h.1,h.2⟩ := rfl
theorem projection_binding {M E A C Q : Type u} (label : E → A)
    (cap : M → C) (initial external oracle : Q) (tags : A → Q → Prop)
    (h : M × List E) :
    fullProjection label cap initial external oracle tags h =
    oldProfile cap initial external oracle tags (erase label h) := rfl
theorem erasure_collision :
    erase (fun _ : Bool => ()) ((),[false]) = erase (fun _ : Bool => ()) ((),[true]) ∧
    ((),[false]) ≠ ((),[true]) := by decide
end AFErasureV24
