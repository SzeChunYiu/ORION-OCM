import CumulativeV21
namespace ResourceControlsV21
open ContinuationV8 OrderedCostsV21 WeightedExecutionV21 CumulativeV21
def intAdd : CostMonoid Int where
  order := ⟨Int.le,Int.le_refl,fun h1 h2 => Int.le_trans h1 h2⟩
  one := 0
  mul := Int.add
  assoc := Int.add_assoc
  left_id := Int.zero_add
  right_id := Int.add_zero
  mono := Int.add_le_add
instance intComparison : DecidableRel intAdd.order.le := fun a b =>
  inferInstanceAs (Decidable (a≤b))
def integerWords : Machine Unit Int Unit Int :=
  ⟨fun _ => (),fun _ c => some (c,())⟩
def maxDemand : Int → List Int → Int
  | spent, [] => spent
  | spent, c::word => max spent (maxDemand (spent+c) word)
theorem signed_prefix_demand (word : List Int) (spent capacity : Int) :
    (∃ out, cumulative intAdd integerWords id capacity () spent word=some ((),out)) ↔
      maxDemand spent word≤capacity := by
  induction word generalizing spent with
  | nil =>
    change (∃ out, (if spent≤capacity then some ((),spent) else none)=some ((),out)) ↔ spent≤capacity
    by_cases ha : spent≤capacity <;> simp [ha]
  | cons c word ih =>
    by_cases ha : spent≤capacity
    · change (∃ out, (if spent≤capacity then
          cumulative intAdd integerWords id capacity () (spent+c) word else none)=some ((),out)) ↔ _
      rw [if_pos ha,ih]
      change maxDemand (spent+c) word≤capacity ↔ max spent (maxDemand (spent+c) word)≤capacity
      omega
    · change (∃ out, (if spent≤capacity then
          cumulative intAdd integerWords id capacity () (spent+c) word else none)=some ((),out)) ↔ _
      rw [if_neg ha]
      change (∃ out, (none : Option (Unit × Int))=some ((),out)) ↔
        max spent (maxDemand (spent+c) word)≤capacity
      constructor
      · rintro ⟨_,h⟩; cases h
      · intro h; omega
theorem signed_final_countermodel :
    weighted intAdd integerWords id () [2,-2]=some ((),0) ∧
    cumulative intAdd integerWords id 1 () 0 [2,-2]=none ∧
    maxDemand 0 [2,-2]=2 ∧
    cumulative intAdd integerWords id 2 () 0 [2,-2]=some ((),0) := by decide
theorem initial_prefix_countermodel :
    cumulative intAdd integerWords id (-1) () 0 []=none ∧ maxDemand 0 []=0 := by decide
theorem peak_is_not_additive : natMax.mul 5 5=5 ∧ natAdd.mul 5 5=10 := by decide
theorem vector_incomparability :
    ¬vectorAdd.order.le (1,0) (0,1) ∧ ¬vectorAdd.order.le (0,1) (1,0) := by
  change ¬((1:Nat)≤0 ∧ 0≤1) ∧ ¬((0:Nat)≤1 ∧ 1≤0)
  decide
theorem int_operation (a b : Int) : intAdd.mul a b=a+b := rfl
theorem int_identity : intAdd.one=0 := rfl
theorem int_order (a b : Int) : intAdd.order.le a b ↔ a≤b := Iff.rfl
theorem integer_words_next (s : Unit) (c : Int) :
    integerWords.next s c=some (c,()) := rfl
theorem integer_words_observation (s : Unit) : integerWords.obs s=() := rfl
theorem demand_empty (spent : Int) : maxDemand spent []=spent := rfl
theorem demand_cons (spent c : Int) (word : List Int) :
    maxDemand spent (c::word)=max spent (maxDemand (spent+c) word) := rfl
end ResourceControlsV21
