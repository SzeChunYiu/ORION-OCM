import PartialContextV15
namespace PermissionSetsV22
universe u
abbrev Family (Q : Type u) := Q → Prop
def Sub {Q : Type u} (R S : Family Q) := ∀ q, R q → S q
def empty {Q : Type u} : Family Q := fun _ => False
def union {Q : Type u} (R S : Family Q) : Family Q := fun q => R q ∨ S q
def diff {Q : Type u} (R S : Family Q) : Family Q := fun q => R q ∧ ¬S q
def single {Q : Type u} (q : Q) : Family Q := fun x => x=q
theorem sub_refl {Q : Type u} (R : Family Q) : Sub R R := fun _ h => h
theorem sub_trans {Q : Type u} {R S T : Family Q}
    (h : Sub R S) (g : Sub S T) : Sub R T := fun q hq => g q (h q hq)
theorem sub_antisymm {Q : Type u} {R S : Family Q}
    (h : Sub R S) (g : Sub S R) : R=S := by
  funext q
  exact propext ⟨h q,g q⟩
theorem union_sub {Q : Type u} (R S T : Family Q) :
    Sub (union R S) T ↔ Sub R T ∧ Sub S T := by
  constructor
  · intro h; exact ⟨fun q hq => h q (Or.inl hq),fun q hq => h q (Or.inr hq)⟩
  · rintro ⟨h,g⟩ q (hq|hq)
    · exact h q hq
    · exact g q hq
theorem union_empty {Q : Type u} (R : Family Q) : union empty R=R := by
  funext q; exact propext ⟨fun h => h.resolve_left id,Or.inr⟩
theorem union_assoc {Q : Type u} (R S T : Family Q) :
    union (union R S) T=union R (union S T) := by
  funext q; exact propext or_assoc
theorem union_self {Q : Type u} (R : Family Q) : union R R=R := by
  funext q; exact propext ⟨fun h => h.elim id id,Or.inl⟩
theorem diff_sub_union {Q : Type u} (R S D : Family Q) :
    Sub (diff R S) D ↔ Sub R (union S D) := by
  classical
  constructor
  · intro h q hq
    by_cases hs : S q
    · exact Or.inl hs
    · exact Or.inr (h q ⟨hq,hs⟩)
  · intro h q hq
    exact (h q hq.1).resolve_left hq.2
def Minimal {Q : Type u} (F : Family Q → Prop) (B : Family Q) :=
  F B ∧ ∀ C, Sub C B → F C → C=B
end PermissionSetsV22
