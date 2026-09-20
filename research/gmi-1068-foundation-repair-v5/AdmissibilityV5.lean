import Std

universe u v

namespace FoundationV5

structure ProcCategory where
  Obj : Type u
  Hom : Obj → Obj → Type v
  ident : (A : Obj) → Hom A A
  comp : {A B D : Obj} → Hom A B → Hom B D → Hom A D
  assoc : {A B D E : Obj} → (f : Hom A B) → (g : Hom B D) →
    (h : Hom D E) → comp (comp f g) h = comp f (comp g h)
  left_unit : {A B : Obj} → (f : Hom A B) → comp (ident A) f = f
  right_unit : {A B : Obj} → (f : Hom A B) → comp f (ident B) = f

def Closed (C : ProcCategory) (P : {A B : C.Obj} → C.Hom A B → Prop) : Prop :=
  (∀ A, P (C.ident A)) ∧
  (∀ {A B D} (f : C.Hom A B) (g : C.Hom B D), P f → P g → P (C.comp f g))

/-- Restricted operations must have the original underlying arrows. -/
structure RestrictedOperations (C : ProcCategory)
    (P : {A B : C.Obj} → C.Hom A B → Prop) where
  ident : (A : C.Obj) → { f : C.Hom A A // P f }
  ident_underlying : ∀ A, (ident A).val = C.ident A
  comp : {A B D : C.Obj} → {f : C.Hom A B // P f} →
    {g : C.Hom B D // P g} → {h : C.Hom A D // P h}
  comp_underlying : ∀ {A B D} (f : {f : C.Hom A B // P f})
    (g : {g : C.Hom B D // P g}), (comp f g).val = C.comp f.val g.val

theorem restricted_operations_iff_closed (C : ProcCategory)
    (P : {A B : C.Obj} → C.Hom A B → Prop) :
    Nonempty (RestrictedOperations C P) ↔ Closed C P := by
  constructor
  · rintro ⟨ops⟩
    constructor
    · intro A
      have h := (ops.ident A).property
      rw [ops.ident_underlying] at h
      exact h
    · intro A B D f g hf hg
      have h := (ops.comp ⟨f, hf⟩ ⟨g, hg⟩).property
      rw [ops.comp_underlying] at h
      exact h
  · intro h
    exact ⟨{
      ident := fun A => ⟨C.ident A, h.1 A⟩
      ident_underlying := fun _ => rfl
      comp := fun f g => ⟨C.comp f.val g.val, h.2 f.val g.val f.property g.property⟩
      comp_underlying := fun _ _ => rfl
    }⟩

def restrictedCategory (C : ProcCategory)
    (P : {A B : C.Obj} → C.Hom A B → Prop) (h : Closed C P) : ProcCategory where
  Obj := C.Obj
  Hom A B := { f : C.Hom A B // P f }
  ident A := ⟨C.ident A, h.1 A⟩
  comp f g := ⟨C.comp f.val g.val, h.2 f.val g.val f.property g.property⟩
  assoc f g k := Subtype.ext (C.assoc f.val g.val k.val)
  left_unit f := Subtype.ext (C.left_unit f.val)
  right_unit f := Subtype.ext (C.right_unit f.val)

abbrev natProcess : ProcCategory where
  Obj := Unit
  Hom _ _ := Nat
  ident _ := 0
  comp f g := f + g
  assoc := Nat.add_assoc
  left_unit := Nat.zero_add
  right_unit := Nat.add_zero

theorem bounded_admissibility_not_closed :
    ¬ Closed natProcess (fun n => n ≤ 1) := by
  intro h
  have bad := h.2 (A := ()) (B := ()) (D := ()) 1 1 (by decide) (by decide)
  change 1 + 1 ≤ 1 at bad
  exact (by decide : ¬ (1 + 1 ≤ 1)) bad

theorem positive_admissibility_missing_identity :
    ¬ Closed natProcess (fun n => 0 < n) := by
  intro h
  have bad := h.1 ()
  change 0 < 0 at bad
  exact (by decide : ¬ (0 < 0)) bad

/-- Balances are resources still available. No resource-creation morphisms exist.
    Exact additive costs are an explicit premise, not inferred from process law. -/
def resourceCategory (C : ProcCategory)
    (cost : {A B : C.Obj} → C.Hom A B → Nat)
    (cost_id : ∀ A, cost (C.ident A) = 0)
    (cost_comp : ∀ {A B D} (f : C.Hom A B) (g : C.Hom B D),
      cost (C.comp f g) = cost f + cost g) : ProcCategory where
  Obj := C.Obj × Nat
  Hom x y := { f : C.Hom x.1 y.1 // x.2 = cost f + y.2 }
  ident x := ⟨C.ident x.1, by simp [cost_id]⟩
  comp f g := ⟨C.comp f.val g.val, by
    rw [cost_comp]
    have hf := f.property
    have hg := g.property
    omega⟩
  assoc f g h := Subtype.ext (C.assoc f.val g.val h.val)
  left_unit f := Subtype.ext (C.left_unit f.val)
  right_unit f := Subtype.ext (C.right_unit f.val)

theorem resource_cost_le_balance {C : ProcCategory}
    {cost : {A B : C.Obj} → C.Hom A B → Nat}
    {A B : C.Obj} {r s : Nat} {f : C.Hom A B}
    (h : r = cost f + s) : cost f ≤ r := by omega

theorem resource_lift_exists_iff {C : ProcCategory}
    {cost : {A B : C.Obj} → C.Hom A B → Nat}
    {A B : C.Obj} (f : C.Hom A B) (r : Nat) :
    (∃ s : Nat, r = cost f + s) ↔ cost f ≤ r := by
  constructor
  · rintro ⟨s, h⟩
    omega
  · intro h
    exact ⟨r - cost f, by omega⟩

theorem positive_cost_cannot_start_empty {c s : Nat} (hc : 0 < c) :
    ¬ (0 = c + s) := by omega

def worst (p : Nat × Nat) : Nat := min p.1 p.2
def best (p : Nat × Nat) : Nat := max p.1 p.2

theorem aggregator_rank_reversal :
    worst (2, 0) < worst (1, 1) ∧ best (1, 1) < best (2, 0) := by decide

theorem min_not_additive :
    ¬ ∀ a b c d : Nat, min (a + c) (b + d) = min a b + min c d := by
  intro h
  have bad := h 1 0 0 1
  simp at bad

theorem max_not_additive :
    ¬ ∀ a b c d : Nat, max (a + c) (b + d) = max a b + max c d := by
  intro h
  have bad := h 1 0 0 1
  simp at bad

end FoundationV5
