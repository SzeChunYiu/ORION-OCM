import CountermodelsV19
import GroupLawsV16
namespace InformationControlsV19
open PartialUnitsV19 CountermodelsV19
def discrete (x y : Bool) : Option Bool := if x = y then some x else none
def join (x y : Bool) : Option Bool := some (x || y)
def discreteAlgebra : Algebra Bool where
  mul := discrete
  assoc := by unfold discrete; decide
  localUnits := by unfold IsUnit discrete; decide
  coherent := by unfold discrete; decide
def joinAlgebra : Algebra Bool where
  mul := join
  assoc := by unfold join; decide
  localUnits := by unfold IsUnit join; decide
  coherent := by unfold join; decide
theorem default_collision : (∀ x y, (discrete x y).getD true = (join x y).getD true) ∧
    discrete false true = none ∧ join false true = some true := by decide
theorem distinct_unit_information :
    (∀ x, IsUnit discrete x) ∧ (∀ x, IsUnit join x ↔ x = false) := by
  unfold IsUnit
  decide
def sourceMul (_ _ : Unit) : Unit := ()
def constantMap (_ : Unit) : Bool := true
theorem multiplicative_not_unital :
    (∀ x y, join (constantMap x) (constantMap y) = some (constantMap (sourceMul x y))) ∧
    ¬ IsUnit join (constantMap ()) := by
  constructor
  · intro x y; rfl
  · unfold IsUnit
    decide
def emptyAlgebra : Algebra Empty where
  mul x _ := nomatch x
  assoc x := nomatch x
  localUnits x := nomatch x
  coherent x := nomatch x
def singletonAlgebra : Algebra Unit where
  mul _ _ := some ()
  assoc _ _ _ := rfl
  localUnits x := by
    cases x
    refine ⟨(),(),?_,?_,rfl,rfl⟩ <;>
      exact ⟨rfl,fun _ _ _ => Subsingleton.elim _ _,fun _ _ _ => Subsingleton.elim _ _⟩
  coherent _ _ _ _ _ _ _ := ⟨(),rfl⟩
theorem no_empty_units : ¬ ∃ e, IsUnit emptyAlgebra.mul e := by
  rintro ⟨e,_⟩
  exact nomatch e
theorem singleton_unit : IsUnit singletonAlgebra.mul () :=
  ⟨rfl,fun _ _ _ => Subsingleton.elim _ _,fun _ _ _ => Subsingleton.elim _ _⟩
def lifted (L : GroupLawsV16.Law) (x y : GroupLawsV16.Label) :=
  some (L.comp x y)
theorem lifted_unit (L : GroupLawsV16.Law) : IsUnit (lifted L) .zero := by
  refine ⟨congrArg some (L.left_id .zero),?_,?_⟩
  · intro x y h
    change some (L.comp .zero x) = some y at h
    rw [L.left_id] at h
    exact (Option.some.inj h).symm
  · intro x y h
    change some (L.comp x .zero) = some y at h
    rw [L.right_id] at h
    exact (Option.some.inj h).symm
def liftedAlgebra (L : GroupLawsV16.Law) : Algebra GroupLawsV16.Label where
  mul := lifted L
  assoc x y z := congrArg some (L.assoc x y z)
  localUnits x := ⟨.zero,.zero,lifted_unit L,lifted_unit L,
    congrArg some (L.left_id x),congrArg some (L.right_id x)⟩
  coherent _ _ _ _ _ _ _ := ⟨_,rfl⟩
theorem lifted_unit_iff (L : GroupLawsV16.Law) (x : GroupLawsV16.Label) :
    IsUnit (lifted L) x ↔ x = .zero := by
  constructor
  · intro hx
    exact (liftedAlgebra L).units_equal hx (lifted_unit L) rfl
  · rintro rfl
    exact lifted_unit L
theorem c4_v4_same_admission_units :
    (∀ x y, (∃ z, lifted GroupLawsV16.c4 x y = some z) ∧
      (∃ z, lifted GroupLawsV16.v4 x y = some z)) ∧
    (∀ x, IsUnit (lifted GroupLawsV16.c4) x ↔ IsUnit (lifted GroupLawsV16.v4) x) := by
  exact ⟨fun _ _ => ⟨⟨_,rfl⟩,⟨_,rfl⟩⟩,
    fun x => (lifted_unit_iff _ x).trans (lifted_unit_iff _ x).symm⟩
theorem c4_v4_different_products :
    lifted GroupLawsV16.c4 .one .one = some .two ∧
    lifted GroupLawsV16.v4 .one .one = some .zero := ⟨rfl,rfl⟩
end InformationControlsV19
