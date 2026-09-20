import EncoderControlsV29
import PresentationControlsV29
namespace ControlBindingsV29
theorem source (m : Bool) (q : Unit) : EncoderControlsV29.source m q = some m := rfl
theorem target (m : Bool) (q : Unit) : EncoderControlsV29.target m q = some false := rfl
theorem varying (m b : Bool) : EncoderControlsV29.varying m b = Bool.xor b m := rfl
theorem code (m : Bool) : EncoderControlsV29.code m = () := rfl
theorem varying_bijective (m : Bool) :
    (∀ a b, EncoderControlsV29.varying m a = EncoderControlsV29.varying m b → a = b) ∧
    (∀ b, ∃ a, EncoderControlsV29.varying m a = b) := by
  constructor
  · intro a b h
    have hh := congrArg (EncoderControlsV29.varying m) h
    simpa only [EncoderControlsV29.varying_inverse] using hh
  · intro b
    exact ⟨EncoderControlsV29.varying m b,EncoderControlsV29.varying_inverse m b⟩
theorem omitted (m q : Bool) :
    EncoderControlsV29.omitted m q = if q then some m else some false := rfl
theorem no_edges (a b : Unit) : PresentationControlsV29.noEdges a b = Empty := rfl
theorem label (a : Fin 6) :
    (PresentationControlsV29.label a).val = if a.val < 2 then a.val else a.val+1 := by
  simp only [PresentationControlsV29.label]
  split <;> rfl
theorem object_decoder :
    PresentationControlsV29.objectDecoder 0 = 2 ∧
    PresentationControlsV29.objectDecoder 1 = 0 ∧
    PresentationControlsV29.objectDecoder 2 = 1 := ⟨rfl,rfl,rfl⟩
theorem local_identity :
    PresentationControlsV29.localIdentity 0 = 0 ∧
    PresentationControlsV29.localIdentity 1 = 3 ∧
    PresentationControlsV29.localIdentity 2 = 5 := ⟨rfl,rfl,rfl⟩
theorem named_identity (n : Fin 3) :
    PresentationControlsV29.namedIdentity n =
      PresentationControlsV29.label (PresentationControlsV29.localIdentity
        (PresentationControlsV29.objectDecoder n)) := rfl
end ControlBindingsV29
