import Foundation

/- Independently fixed obligation. It contains no proof of the target. -/
namespace F0Target

def statement : Prop :=
  forall {H A : Type} (V W : H -> Prop)
    (q : H -> A) (answer : A) (actual : H),
    W actual -> (forall h, W h -> V h) ->
    (forall h, V h -> q h = answer) -> q actual = answer

end F0Target
