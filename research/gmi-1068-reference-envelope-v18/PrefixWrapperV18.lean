import Std
namespace PrefixWrapperV18
universe u
abbrev Program := List Bool
abbrev Machine (α : Type u) := Program → Option α
def IsPrefix (p q : Program) : Prop := ∃ r, p ++ r = q
def PrefixFree {α : Type u} (U : Machine α) : Prop :=
  ∀ p q, (∃ x, U p = some x) → (∃ y, U q = some y) → IsPrefix p q → p=q
def stripOnes : Nat → Program → Option Program
  | 0, p => some p
  | n+1, true::p => stripOnes n p
  | _+1, _ => none
def pad (L : Nat) (p : Program) := List.replicate L true ++ p
def wrapper {α : Type u} (U : Machine α) (z : α) (L : Nat) (p : Program) :=
  if p = [false] then some z else (stripOnes L p).bind U

theorem pad_binding (L : Nat) (p : Program) :
    pad L p=List.replicate L true++p := rfl
theorem wrapper_binding {α : Type u} (U : Machine α) (z : α) (L : Nat) (p : Program) :
    wrapper U z L p=(if p=[false] then some z else (stripOnes L p).bind U) := rfl

theorem strip_iff (L : Nat) (p q : Program) :
    stripOnes L p = some q ↔ p = pad L q := by
  induction L generalizing p with
  | zero => simp [stripOnes,pad]
  | succ L ih =>
    cases p with
    | nil => simp [stripOnes,pad]
    | cons b p =>
      cases b <;> simp [stripOnes,pad,List.replicate_succ,ih,pad]

theorem pad_length (L : Nat) (p : Program) : (pad L p).length=L+p.length := by
  simp [pad]
theorem pad_ne_target (L : Nat) (hL : 0<L) (p : Program) :
    pad L p ≠ [false] := by
  cases L with
  | zero => omega
  | succ L => simp [pad,List.replicate_succ]
theorem wrapper_target {α : Type u} (U : Machine α) (z : α) (L : Nat) :
    wrapper U z L [false] = some z := by simp [wrapper]
theorem wrapper_simulates {α : Type u} (U : Machine α) (z : α)
    (L : Nat) (hL : 0<L) (p : Program) :
    wrapper U z L (pad L p) = U p := by
  rw [wrapper,if_neg (pad_ne_target L hL p)]
  rw [(strip_iff L _ p).mpr rfl]
  rfl
theorem wrapper_empty {α : Type u} (U : Machine α) (z : α)
    (L : Nat) (hL : 0<L) : wrapper U z L [] = none := by
  cases L with
  | zero => omega
  | succ L => simp [wrapper,stripOnes]
theorem success_iff {α : Type u} (U : Machine α) (z y : α)
    (L : Nat) (hL : 0<L) (p : Program) :
    wrapper U z L p = some y ↔
    (p=[false] ∧ y=z) ∨ ∃ q, p=pad L q ∧ U q=some y := by
  constructor
  · intro h
    by_cases hp : p=[false]
    · subst p
      have hz : z=y := Option.some.inj (by simpa [wrapper] using h)
      exact Or.inl ⟨rfl,hz.symm⟩
    · simp only [wrapper,if_neg hp] at h
      cases hs : stripOnes L p with
      | none => simp [hs] at h
      | some q =>
        exact Or.inr ⟨q,(strip_iff L p q).mp hs,by simpa [hs] using h⟩
  · rintro (⟨rfl,rfl⟩ | ⟨q,rfl,hq⟩)
    · simp [wrapper]
    · rw [wrapper_simulates U z L hL q]
      exact hq

theorem pad_prefix_iff (L : Nat) (p q : Program) :
    IsPrefix (pad L p) (pad L q) ↔ IsPrefix p q := by
  constructor
  · rintro ⟨r,hr⟩
    exact ⟨r,by simpa [pad,List.append_assoc] using hr⟩
  · rintro ⟨r,hr⟩
    exact ⟨r,by simp [pad,List.append_assoc,hr]⟩
theorem target_not_prefix_pad (L : Nat) (hL : 0<L) (p : Program) :
    ¬ IsPrefix [false] (pad L p) := by
  cases L with
  | zero => omega
  | succ L => rintro ⟨r,hr⟩; simp [pad,List.replicate_succ] at hr
theorem pad_not_prefix_target (L : Nat) (hL : 0<L) (p : Program) :
    ¬ IsPrefix (pad L p) [false] := by
  cases L with
  | zero => omega
  | succ L => rintro ⟨r,hr⟩; simp [pad,List.replicate_succ] at hr
theorem wrapper_prefix_free {α : Type u} (U : Machine α) (z : α)
    (L : Nat) (hL : 0<L) (hU : PrefixFree U) :
    PrefixFree (wrapper U z L) := by
  rintro p q ⟨x,hx⟩ ⟨y,hy⟩ hp
  rcases (success_iff U z x L hL p).mp hx with ⟨rfl,_⟩ | ⟨a,rfl,ha⟩
  · rcases (success_iff U z y L hL q).mp hy with ⟨rfl,_⟩ | ⟨b,rfl,_⟩
    · rfl
    · exact False.elim (target_not_prefix_pad L hL b hp)
  · rcases (success_iff U z y L hL q).mp hy with ⟨rfl,_⟩ | ⟨b,rfl,hb⟩
    · exact False.elim (pad_not_prefix_target L hL a hp)
    · exact congrArg (pad L) (hU a b ⟨x,ha⟩ ⟨y,hb⟩
        ((pad_prefix_iff L a b).mp hp))
end PrefixWrapperV18
