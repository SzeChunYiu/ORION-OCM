import SubEventsV27
import FiniteOutcomesV27
namespace EventTestsV27
open StochasticV14 OrderedWeightsV27 SubEventsV27 FiniteOutcomesV27
universe u v w
variable {α : Type u} [Weight α]
def aggregate {I : Shape} {n m : Nat} (p : Carrier I → Matrix α n m) : Matrix α n m :=
  fun x y => total I (fun i => p i x y)
theorem aggregate_product {I J : Shape} {n m k : Nat}
    (p : Carrier I → Matrix α n m) (q : Carrier J → Matrix α m k) :
    aggregate (I:=.product I J) (fun ij => mcomp (p ij.1) (q ij.2))=
      mcomp (aggregate p) (aggregate q) := by
  funext x z
  change total I (fun i => total J (fun j => sum (fun y => p i x y*q j y z)))=_
  calc
    _ = total I (fun i => sum (fun y => total J (fun j => p i x y*q j y z))) :=
      congrArg (total I) (funext (fun i => exchange_fin J (fun j y => p i x y*q j y z)))
    _ = sum (fun y => total I (fun i => total J (fun j => p i x y*q j y z))) :=
      exchange_fin I _
    _ = sum (fun y => total I (fun i => p i x y) * total J (fun j => q j y z)) := by
      apply congrArg sum; funext y
      simp only [total_mul_left,total_mul_right]
    _ = _ := rfl
structure Test (α : Type u) [Weight α] (I : Shape) (n m : Nat) where
  value : Carrier I → Matrix α n m
  normalized : ∀ x,total I (fun i => sum (value i x))=1
namespace Test
theorem aggregate_normalized {I : Shape} {n m : Nat} (p : Test α I n m) :
    Normalized (aggregate p.value) := by
  intro x
  change sum (fun y => total I (fun i => p.value i x y))=1
  rw [← exchange_fin]
  exact p.normalized x
def comp {I J : Shape} {n m k : Nat} (p : Test α I n m) (q : Test α J m k) :
    Test α (.product I J) n k where
  value ij := mcomp (p.value ij.1) (q.value ij.2)
  normalized x := by
    rw [exchange_fin]
    change sum (aggregate (I:=.product I J) (fun ij => mcomp (p.value ij.1) (q.value ij.2)) x)=1
    rw [aggregate_product]
    exact comp_normalized p.aggregate_normalized q.aggregate_normalized x
theorem comp_value {I J : Shape} {n m k : Nat} (p : Test α I n m) (q : Test α J m k)
    (i : Carrier I) (j : Carrier J) (x : Fin n) (z : Fin k) :
    (comp p q).value (i,j) x z=sum (fun y => p.value i x y*q.value j y z) := rfl
theorem comp_aggregate {I J : Shape} {n m k : Nat} (p : Test α I n m) (q : Test α J m k) :
    aggregate (comp p q).value=mcomp (aggregate p.value) (aggregate q.value) :=
  aggregate_product _ _
def component [OrderedWeight α] {I : Shape} {n m : Nat} (p : Test α I n m)
    (i : Carrier I) : Event α n m where
  value := p.value i
  bounded x := by
    have h := term_le_total I (fun j => sum (p.value j x)) i
    rw [p.normalized] at h
    exact h
def channel {n m : Nat} (p : Kernel α n m) : Test α (.atom 1) n m where
  value _ := p.value
  normalized x := by
    change sum (p.value x)+0=1
    rw [add_zero,p.normalized]
theorem no_empty_outcomes {n m : Nat} (x : Fin n) : ¬ Nonempty (Test α (.atom 0) n m) := by
  rintro ⟨p⟩
  have h := p.normalized x
  exact Weight.one_ne_zero h.symm
def empty_input (I : Shape) (m : Nat) : Test α I 0 m where
  value _ x := Fin.elim0 x
  normalized x := Fin.elim0 x
end Test
structure LabeledTest (α : Type u) [Weight α] (I : Shape) (L : Type v) (n m : Nat) where
  test : Test α I n m
  encoder : Encoder I L
def LabeledTest.comp {I J : Shape} {L : Type v} {M : Type w} {n m k : Nat}
    (p : LabeledTest α I L n m) (q : LabeledTest α J M m k) :
    LabeledTest α (.product I J) (L×M) n k :=
  ⟨p.test.comp q.test,p.encoder.pair q.encoder⟩
theorem paired_labels {I J : Shape} {L : Type v} {M : Type w} {n m k : Nat}
    (p : LabeledTest α I L n m) (q : LabeledTest α J M m k)
    (i : Carrier I) (j : Carrier J) :
    (p.comp q).encoder.code (i,j)=(p.encoder.code i,q.encoder.code j) := rfl
end EventTestsV27
