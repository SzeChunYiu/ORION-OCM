import Foundation

/- Authored reconstruction/composition fixture. This is not a held-out or learned proof. -/
namespace OCMProofReplay

theorem refinement_then_sound {H A : Type} (V W : H -> Prop)
    (q : H -> A) (answer : A) (actual : H)
    (member : W actual) (subset : forall h, W h -> V h)
    (agreement : forall h, V h -> q h = answer) : q actual = answer :=
  MEFoundation.agreement_sound W q answer actual member
    (MEFoundation.agreement_refinement V W q answer subset agreement)

end OCMProofReplay

#print axioms OCMProofReplay.refinement_then_sound
