import PartialUnitsV19
set_option synthInstance.maxSize 4096
set_option maxRecDepth 4096
namespace CountermodelsV19
open PartialUnitsV19
theorem exists_empty_fin (p : Fin 0 → Prop) : (∃ x, p x) ↔ False :=
  ⟨fun ⟨x,_⟩ => Fin.elim0 x, False.elim⟩
def StrongAssoc (m : A → A → Option A) : Prop :=
  ∀ x y z, (m x y).bind (fun u => m u z) = (m y z).bind (fun v => m x v)
def Local (m : A → A → Option A) : Prop :=
  ∀ x, ∃ e f, IsUnit m e ∧ IsUnit m f ∧ m e x = some x ∧ m x f = some x
def Coherent (m : A → A → Option A) : Prop :=
  ∀ x y z u v, m x y = some u → m y z = some v → ∃ w, m u z = some w
def WeakAssoc (m : A → A → Option A) : Prop :=
  ∀ x y z u v, (m x y).bind (fun a => m a z) = some u →
    (m y z).bind (fun b => m x b) = some v → u = v
def incoherent : Bool → Bool → Option Bool
  | true,true => none
  | x,y => some (x || y)
theorem coherence_isolated : StrongAssoc incoherent ∧ Local incoherent ∧ ¬ Coherent incoherent := by
  unfold StrongAssoc Local Coherent IsUnit
  decide
def nonassoc (x y : Fin 3) : Fin 3 :=
  if x = 0 then y else if y = 0 then x else
  if x = 1 ∧ y = 1 then 2 else if x = 2 ∧ y = 2 then 2 else 0
theorem nonassoc_units :
    (∀ x, nonassoc 0 x = x) ∧ (∀ x, nonassoc x 0 = x) := by decide
theorem associativity_isolated :
    Local (fun x y => some (nonassoc x y)) ∧
    Coherent (fun x y => some (nonassoc x y)) ∧
    ¬ StrongAssoc (fun x y => some (nonassoc x y)) := by
  unfold StrongAssoc Local Coherent IsUnit
  simp only [Fin.exists_fin_two,Fin.exists_fin_one,Fin.exists_fin_succ,exists_empty_fin,or_false]
  decide
theorem nonassoc_witness :
    nonassoc (nonassoc 1 1) 2 = 2 ∧ nonassoc 1 (nonassoc 1 2) = 1 := by decide
theorem two_point_unital_associative (m : A → A → A) (e a : A)
    (cover : ∀ x, x = e ∨ x = a)
    (hl : ∀ x, m e x = x) (hr : ∀ x, m x e = x) :
    ∀ x y z, m (m x y) z = m x (m y z) := by
  intro x y z
  rcases cover x with hx | hx <;> rcases cover y with hy | hy <;>
    rcases cover z with hz | hz <;> rw [hx,hy,hz] <;> try simp only [hl,hr]
  rcases cover (m a a) with h | h <;> rw [h] <;> simp only [hl,hr]
theorem fin_small_unital_associative {n : Nat} (hn : n ≤ 2)
    (m : Fin n → Fin n → Fin n) (e : Fin n)
    (hl : ∀ x, m e x = x) (hr : ∀ x, m x e = x) :
    ∀ x y z, m (m x y) z = m x (m y z) := by
  have casesn : n = 0 ∨ n = 1 ∨ n = 2 := by omega
  rcases casesn with rfl | rfl | rfl
  · exact Fin.elim0 e
  · intro x y z
    exact Subsingleton.elim _ _
  · have cover : ∀ e x : Fin 2, x = e ∨ x = (if e = 0 then 1 else 0) := by decide
    exact two_point_unital_associative m e _ (cover e) hl hr
theorem nonassoc_minimum_size {n : Nat} (m : Fin n → Fin n → Fin n) (e : Fin n)
    (hl : ∀ x, m e x = x) (hr : ∀ x, m x e = x)
    (hf : ∃ x y z, m (m x y) z ≠ m x (m y z)) : 3 ≤ n := by
  have hnot : ¬ n ≤ 2 := by
    intro hn
    rcases hf with ⟨x,y,z,h⟩
    exact h (fin_small_unital_associative hn m e hl hr x y z)
  omega
def leftProjection (x _ : Bool) : Bool := x
def rightProjection (_ y : Bool) : Bool := y
theorem projection_controls :
    (∀ x y z, leftProjection (leftProjection x y) z = leftProjection x (leftProjection y z)) ∧
    (∀ x, leftProjection x false = x) ∧ ¬ (∀ x, leftProjection false x = x) ∧
    (∀ x y z, rightProjection (rightProjection x y) z = rightProjection x (rightProjection y z)) ∧
    (∀ x, rightProjection false x = x) ∧ ¬ (∀ x, rightProjection x false = x) := by decide
theorem projections_have_no_opposite_unit :
    (∀ e, ¬ ∀ x, leftProjection e x = x) ∧
    (∀ e, ¬ ∀ x, rightProjection x e = x) := by decide
def weakOnly (x y : Fin 3) : Option (Fin 3) :=
  if x = 0 ∧ y = 0 then some 0 else
  if x = 1 ∧ y = 1 then some 1 else
  if (x = 0 ∧ y = 2) ∨ (x = 1 ∧ y = 2) ∨
    (x = 2 ∧ y = 0) ∨ (x = 2 ∧ y = 2) then some 2 else none
theorem strong_definedness_isolated :
    WeakAssoc weakOnly ∧ Local weakOnly ∧ Coherent weakOnly ∧ ¬ StrongAssoc weakOnly := by
  unfold WeakAssoc StrongAssoc Local Coherent IsUnit
  simp only [Fin.exists_fin_two,Fin.exists_fin_one,Fin.exists_fin_succ,exists_empty_fin,or_false]
  decide
theorem weak_only_witness :
    (weakOnly 0 1).bind (fun x => weakOnly x 2) = none ∧
    (weakOnly 1 2).bind (fun x => weakOnly 0 x) = some 2 := by decide
end CountermodelsV19
