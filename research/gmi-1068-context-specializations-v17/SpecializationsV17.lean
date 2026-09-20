import ProductContextsV17
namespace SpecializationsV17
open PartialContextV15 ContextMapsV17 ProductContextsV17
universe u v

def utility {H : Type u} {W : Type v} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → W) : Context H W := ⟨E,f,r⟩
theorem utility_defined {H : Type u} {W : Type v} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → W) : (utility E r f).defined = E := rfl
theorem utility_value {H : Type u} {W : Type v} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → W) (h : {h // E h}) :
    (utility E r f).eval h = f h := rfl
theorem utility_comparison {H : Type u} {W : Type v} (P E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → W) (a b : Active P (utility E r f)) :
    (activeOrder P (utility E r f)).le a b ↔
      r.le (f ⟨a.val,a.property.2⟩) (f ⟨b.val,b.property.2⟩) := Iff.rfl

def intOrder : PreorderSpec Int := ⟨(· ≤ ·), Int.le_refl, Int.le_trans⟩
def intUtility {H : Type u} (E : H → Prop) (f : {h // E h} → Int) : Context H Int :=
  utility E intOrder f
theorem int_comparison (a b : Int) : intOrder.le a b ↔ a ≤ b := Iff.rfl

def boolOrder : PreorderSpec Bool where
  le a b := a=true → b=true
  refl _ h := h
  trans h k ha := k (h ha)
def bitScore (b : Bool) : Int := if b then 1 else 0

theorem bit_order_iff (a b : Bool) : boolOrder.le a b ↔ bitScore a ≤ bitScore b := by
  cases a <;> cases b <;> simp [boolOrder, bitScore]
def bitEmbedding : OrderMap boolOrder intOrder :=
  ⟨bitScore, fun {a b} h => (bit_order_iff a b).mp h⟩

noncomputable def acceptance {H : Type u} (E : H → Prop)
    (A : {h // E h} → Prop) : Context H Bool := by
  classical
  exact utility E boolOrder (fun h => if A h then true else false)

theorem acceptance_defined {H : Type u} (E : H → Prop) (A : {h // E h} → Prop) :
    (acceptance E A).defined = E := rfl
theorem acceptance_true {H : Type u} (E : H → Prop) (A : {h // E h} → Prop)
    (h : {h // E h}) : (acceptance E A).eval h = true ↔ A h := by
  classical
  simp [acceptance, utility]
theorem acceptance_comparison {H : Type u} (P E : H → Prop) (A : {h // E h} → Prop)
    (a b : Active P (acceptance E A)) :
    (activeOrder P (acceptance E A)).le a b ↔
      (A ⟨a.val,a.property.2⟩ → A ⟨b.val,b.property.2⟩) := by
  change ((acceptance E A).eval _ = true → (acceptance E A).eval _ = true) ↔ _
  rw [acceptance_true, acceptance_true]

def vector {H : Type u} {W : Type v} {n : Nat} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) : Context H (Fin n → W) :=
  shared E (fun _ => r) (fun i h => f h i)
def cost {H : Type u} {W : Type v} {n : Nat} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) : Context H (Fin n → W) :=
  dual (vector E r f)

theorem vector_defined {H : Type u} {W : Type v} {n : Nat} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) :
    (vector E r f).defined = E := rfl
theorem vector_value {H : Type u} {W : Type v} {n : Nat} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) (h : {h // E h}) :
    (vector E r f).eval h = f h := rfl
theorem pareto_comparison {H : Type u} {W : Type v} {n : Nat} (P E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) (a b : Active P (vector E r f)) :
    (activeOrder P (vector E r f)).le a b ↔
      ∀ i, r.le (f ⟨a.val,a.property.2⟩ i) (f ⟨b.val,b.property.2⟩ i) := Iff.rfl
theorem cost_defined {H : Type u} {W : Type v} {n : Nat} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) : (cost E r f).defined = E := rfl
theorem cost_value {H : Type u} {W : Type v} {n : Nat} (E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) (h : {h // E h}) :
    (cost E r f).eval h = f h := rfl
theorem cost_comparison {H : Type u} {W : Type v} {n : Nat} (P E : H → Prop)
    (r : PreorderSpec W) (f : {h // E h} → Fin n → W) (a b : Active P (cost E r f)) :
    (activeOrder P (cost E r f)).le a b ↔
      ∀ i, r.le (f ⟨b.val,b.property.2⟩ i) (f ⟨a.val,a.property.2⟩ i) := Iff.rfl
theorem intUtility_binding {H : Type u} (E : H → Prop) (f : {h // E h} → Int) :
    intUtility E f = utility E intOrder f := rfl
theorem bit_embedding_apply (b : Bool) : bitEmbedding.fn b = bitScore b := rfl
end SpecializationsV17
