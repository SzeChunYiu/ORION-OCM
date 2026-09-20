import Std
import Std.Internal.Rat
namespace StochasticV14.RationalModel
abbrev Q := Std.Internal.Rat
def frac (n : Int) (d : Nat) : Q := Std.Internal.mkRat n d
inductive Arrow where
  | identity | Arrow.flip | zero | third | half | twoThirds | one
  deriving DecidableEq, Repr
open Arrow
def parameter : Arrow → Q
  | third => frac 1 3
  | half => frac 1 2
  | twoThirds => frac 2 3
  | one => 1
  | _ => 0
def matrix (f : Arrow) (x y : Bool) : Q :=
  match f with
  | identity => if y=x then 1 else 0
  | Arrow.flip => if y=(!x) then 1 else 0
  | f => if y then parameter f else 1-parameter f
def afterFlip : Arrow → Arrow
  | identity => Arrow.flip | Arrow.flip => identity | zero => one | one => zero
  | third => twoThirds | twoThirds => third | half => half
def comp (f g : Arrow) : Arrow :=
  match g with
  | identity => f
  | Arrow.flip => afterFlip f
  | g => g
set_option maxRecDepth 10000
set_option maxHeartbeats 2000000

theorem normalized (f : Arrow) (x : Bool) :
    matrix f x false+matrix f x true=1 := by
  cases f <;> cases x <;> decide
theorem nonnegative (f : Arrow) (x y : Bool) : (0:Q) ≤ matrix f x y := by
  cases f <;> cases x <;> cases y <;> decide
theorem actual_comp (f g : Arrow) (x z : Bool) :
    matrix (comp f g) x z =
      matrix f x false*matrix g false z+matrix f x true*matrix g true z := by
  cases f <;> cases g <;> cases x <;> cases z <;> decide

theorem entries_injective (f g : Arrow) :
    (matrix f false true=matrix g false true ∧
     matrix f true true=matrix g true true) → f=g := by
  cases f <;> cases g <;> decide
theorem matrix_faithful {f g : Arrow} (h : ∀ x y, matrix f x y=matrix g x y) : f=g :=
  entries_injective f g ⟨h false true,h true true⟩
theorem assoc (f g h : Arrow) : comp (comp f g) h=comp f (comp g h) := by
  cases f <;> cases g <;> cases h <;> decide
theorem left_id (f : Arrow) : comp identity f=f := by cases f <;> rfl
theorem right_id (f : Arrow) : comp f identity=f := rfl

def encode (f : Bool → Bool) : Arrow :=
  if f false then (if f true then one else Arrow.flip)
  else (if f true then identity else zero)
theorem encode_dirac (f : Bool → Bool) (x y : Bool) :
    matrix (encode f) x y=(if y=f x then 1 else 0) := by
  cases h0 : f false <;> cases h1 : f true <;> cases x <;> cases y <;>
    simp [encode,matrix,parameter,h0,h1] <;> decide
theorem encode_identity : encode id=identity := rfl
theorem encode_comp (f g : Bool → Bool) :
    comp (encode f) (encode g)=encode (g ∘ f) := by
  cases h0 : f false <;> cases h1 : f true <;>
    cases h2 : g false <;> cases h3 : g true <;>
    simp [encode,Function.comp_def,h0,h1,h2,h3,comp,afterFlip]
theorem encode_faithful {f g : Bool → Bool} (h : encode f=encode g) : f=g := by
  cases h0 : f false <;> cases h1 : f true <;>
    cases h2 : g false <;> cases h3 : g true <;>
    simp [encode,h0,h1,h2,h3] at h
  all_goals
    funext x
    cases x <;> simp_all
def support (f : Arrow) (x y : Bool) : Prop := matrix f x y≠0
theorem reduced_entries (f : Arrow) (x y : Bool) :
    0 < (matrix f x y).den ∧ Nat.gcd (matrix f x y).num.natAbs (matrix f x y).den=1 := by
  cases f <;> cases x <;> cases y <;> decide
theorem event_probabilities :
    matrix third false true=frac 1 3 ∧ matrix half false true=frac 1 2 ∧
    matrix twoThirds false true=frac 2 3 := ⟨rfl,rfl,rfl⟩
theorem half_nontrivial :
    matrix half false true≠0 ∧ matrix half false true≠1 := by decide
theorem support_probability_loss :
    (∀ x y, support third x y ↔ support twoThirds x y) ∧
    matrix third false true≠matrix twoThirds false true := by
  constructor
  · intro x y
    unfold support
    cases x <;> cases y <;> decide
  · decide
end StochasticV14.RationalModel
