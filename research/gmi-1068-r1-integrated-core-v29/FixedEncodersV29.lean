import RecoverabilityV9
namespace FixedEncodersV29
universe u v w x y z
theorem option_map_injective {A : Type u} {B : Type v} (j : A → B)
    (hj : ∀ a b, j a = j b → a = b) (a b : Option A)
    (h : a.map j = b.map j) : a = b := by
  cases a with
  | none => cases b <;> simp_all
  | some a =>
    cases b with
    | none => simp at h
    | some b => exact congrArg some (hj a b (Option.some.inj h))
def pullback {M : Type u} {Q : Type v} {R : Type w} {B : Type x}
    (target : M → R → Option B) (i : Q → R) : M → Q → Option B := fun m q => target m (i q)
def encode {Q : Type u} {A : Type v} {B : Type w} (j : A → B)
    (f : Q → Option A) : Q → Option B := fun q => (f q).map j
theorem encode_injective {Q : Type u} {A : Type v} {B : Type w} (j : A → B)
    (hj : ∀ a b, j a = j b → a = b) (f g : Q → Option A)
    (h : encode j f = encode j g) : f = g := by
  funext q
  exact option_map_injective j hj (f q) (g q) (congrFun h q)
theorem recovery_iff {M : Type u} {Z : Type v} {Q : Type w} {R : Type x}
    {A : Type y} {B : Type z} (code : M → Z)
    (source : M → Q → Option A) (target : M → R → Option B)
    (i : Q → R) (j : A → B) (hj : ∀ a b, j a = j b → a = b)
    (square : ∀ m q, target m (i q) = (source m q).map j) :
    RecoverabilityV9.Recoverable code source ↔
      RecoverabilityV9.Recoverable code (pullback target i) :=
  RecoverabilityV9.recovery_transport code source code (pullback target i)
    id id (encode j) (fun m => ⟨m,rfl⟩) (fun _ _ h => h)
    (encode_injective j hj) (fun _ => rfl) (fun m => funext (square m))
end FixedEncodersV29
