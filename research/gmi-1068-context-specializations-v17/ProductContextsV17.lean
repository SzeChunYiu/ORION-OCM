import ContextMapsV17
namespace ProductContextsV17
open PartialContextV15
universe u v

def productOrder {n : Nat} {W : Fin n → Type v}
    (r : (i : Fin n) → PreorderSpec (W i)) : PreorderSpec ((i : Fin n) → W i) where
  le a b := ∀ i, (r i).le (a i) (b i)
  refl a i := (r i).refl (a i)
  trans h k i := (r i).trans (h i) (k i)

def shared {H : Type u} {n : Nat} {W : Fin n → Type v}
    (E : H → Prop) (r : (i : Fin n) → PreorderSpec (W i))
    (f : (i : Fin n) → {h // E h} → W i) : Context H ((i : Fin n) → W i) where
  defined := E
  eval h i := f i h
  order := productOrder r

def independent {H : Type u} {n : Nat} {W : Fin n → Type v}
    (k : (i : Fin n) → Context H (W i)) : Context H ((i : Fin n) → W i) where
  defined h := ∀ i, (k i).defined h
  eval h i := (k i).eval ⟨h.val, h.property i⟩
  order := productOrder (fun i => (k i).order)

theorem shared_defined {H : Type u} {n : Nat} {W : Fin n → Type v}
    (E : H → Prop) (r : (i : Fin n) → PreorderSpec (W i))
    (f : (i : Fin n) → {h // E h} → W i) : (shared E r f).defined = E := rfl
theorem shared_projection {H : Type u} {n : Nat} {W : Fin n → Type v}
    (E : H → Prop) (r : (i : Fin n) → PreorderSpec (W i))
    (f : (i : Fin n) → {h // E h} → W i) (h : {h // E h}) (i : Fin n) :
    (shared E r f).eval h i = f i h := rfl
theorem shared_comparison {H : Type u} {n : Nat} {W : Fin n → Type v}
    (P E : H → Prop) (r : (i : Fin n) → PreorderSpec (W i))
    (f : (i : Fin n) → {h // E h} → W i) (a b : Active P (shared E r f)) :
    (activeOrder P (shared E r f)).le a b ↔
      ∀ i, (r i).le (f i ⟨a.val,a.property.2⟩) (f i ⟨b.val,b.property.2⟩) := Iff.rfl

theorem independent_defined {H : Type u} {n : Nat} {W : Fin n → Type v}
    (k : (i : Fin n) → Context H (W i)) (h : H) :
    (independent k).defined h ↔ ∀ i, (k i).defined h := Iff.rfl
theorem independent_projection {H : Type u} {n : Nat} {W : Fin n → Type v}
    (k : (i : Fin n) → Context H (W i))
    (h : {h // (independent k).defined h}) (i : Fin n) :
    (independent k).eval h i = (k i).eval ⟨h.val,h.property i⟩ := rfl
theorem independent_comparison {H : Type u} {n : Nat} {W : Fin n → Type v}
    (P : H → Prop) (k : (i : Fin n) → Context H (W i))
    (a b : Active P (independent k)) :
    (activeOrder P (independent k)).le a b ↔ ∀ i, (k i).order.le
      ((k i).eval ⟨a.val,a.property.2 i⟩) ((k i).eval ⟨b.val,b.property.2 i⟩) := Iff.rfl

theorem shared_observe {H : Type u} {n : Nat} {W : Fin n → Type v}
    (P E : H → Prop) (r : (i : Fin n) → PreorderSpec (W i))
    (f : (i : Fin n) → {h // E h} → W i) (h : H) :
    observe P (shared E r f) h =
      (by classical exact if P h then if he : E h then
        Outcome.value (fun i => f i ⟨h,he⟩) else .undefined else .illegal) := rfl

theorem independent_observe {H : Type u} {n : Nat} {W : Fin n → Type v}
    (P : H → Prop) (k : (i : Fin n) → Context H (W i)) (h : H) :
    observe P (independent k) h =
      (by classical exact if P h then if he : ∀ i, (k i).defined h then
        Outcome.value (fun i => (k i).eval ⟨h,he i⟩) else .undefined else .illegal) := by
  classical
  simp [observe, independent]

theorem independent_has_value {H : Type u} {n : Nat} {W : Fin n → Type v}
    (P : H → Prop) (k : (i : Fin n) → Context H (W i)) (h : H) :
    (∃ v, observe P (independent k) h = .value v) ↔ P h ∧ ∀ i, (k i).defined h :=
  observe_has_value P (independent k) h

theorem independent_undefined {H : Type u} {n : Nat} {W : Fin n → Type v}
    (P : H → Prop) (k : (i : Fin n) → Context H (W i)) (h : H) :
    observe P (independent k) h = .undefined ↔ P h ∧ ¬ ∀ i, (k i).defined h := by
  classical
  by_cases hp : P h
  · by_cases he : ∀ i, (k i).defined h
    · rw [observe_value P (independent k) h hp he]
      simp [hp, he]
    · rw [observe_undefined P (independent k) h hp he]
      simp [hp, he]
  · rw [observe_illegal P (independent k) h hp]
    simp [hp]

theorem independent_empty_defined {H : Type u} {W : Fin 0 → Type v}
    (k : (i : Fin 0) → Context H (W i)) (h : H) :
    (independent k).defined h := fun i => Fin.elim0 i

theorem independent_empty_observe {H : Type u} {W : Fin 0 → Type v}
    (P : H → Prop) (k : (i : Fin 0) → Context H (W i)) (h : H) :
    observe P (independent k) h =
      (by classical exact if P h then Outcome.value (fun i => Fin.elim0 i) else .illegal) := by
  classical
  by_cases hp : P h
  · rw [observe_value P (independent k) h hp (independent_empty_defined k h)]
    simp only [hp, ↓reduceIte]
    congr 1
    funext i
    exact Fin.elim0 i
  · rw [observe_illegal P (independent k) h hp]
    simp [hp]
end ProductContextsV17
