import PartialContextV15
import RecoverabilityV9
namespace TaggedAdmissionV28
open PartialContextV15 RecoverabilityV9
universe u v w x
variable {H : Type u} {W : Type v}
theorem not_illegal (P : H → Prop) (k : Context H W) (h : H) :
    observe P k h ≠ .illegal ↔ P h := by
  classical
  by_cases hp : P h
  · by_cases he : k.defined h <;> simp [observe,hp,he]
  · simp [observe,hp]
theorem admission_eq (P Q : H → Prop) (k l : Context H W)
    (h : observe P k = observe Q l) : P = Q := by
  funext x
  apply propext
  rw [← not_illegal P k x,← not_illegal Q l x,h]
def decode (q : H → Outcome W) : H → Prop := fun h => q h ≠ .illegal
theorem decode_value (q : H → Outcome W) (h : H) :
    decode q h ↔ q h ≠ .illegal := Iff.rfl
theorem decode_observe (P : H → Prop) (k : Context H W) :
    decode (observe P k) = P := by
  funext h
  exact propext (not_illegal P k h)
def attainedDecoder {M : Type w} (P : M → H → Prop) (k : M → Context H W) :
    Image (fun m => observe (P m) (k m)) → (H → Prop) := fun q => decode q.val
theorem attained_binding {M : Type w} (P : M → H → Prop) (k : M → Context H W)
    (q : Image (fun m => observe (P m) (k m))) (h : H) :
    attainedDecoder P k q h ↔ q.val h ≠ .illegal := Iff.rfl
theorem attained_correct {M : Type w} (P : M → H → Prop) (k : M → Context H W) (m : M) :
    attainedDecoder P k (encoded (fun m => observe (P m) (k m)) m) = P m :=
  decode_observe (P m) (k m)
theorem admission_recoverable {M : Type w} (P : M → H → Prop) (k : M → Context H W) :
    Recoverable (fun m => observe (P m) (k m)) P :=
  ⟨attainedDecoder P k,attained_correct P k⟩
def eraseFailure : Outcome W → Option W
  | .illegal => none
  | .undefined => none
  | .value w => some w
theorem erased_failures : eraseFailure (Outcome.illegal : Outcome W) =
    eraseFailure (Outcome.undefined : Outcome W) := rfl
theorem erase_value (w : W) : eraseFailure (.value w) = some w := rfl
end TaggedAdmissionV28
