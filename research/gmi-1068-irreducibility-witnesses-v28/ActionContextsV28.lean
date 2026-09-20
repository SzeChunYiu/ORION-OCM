import OriginalBindingsV28
import TypedPathsV11
import PartialContextV15
import RecoverabilityV9
namespace ActionContextsV28
open TypedPathsV11 PartialContextV15 RecoverabilityV9
def Graph (_ _ : Unit) := Action
abbrev History := Path Graph () ()
def category : Category Unit := Path.category Graph
def terminal : Category Unit where
  Hom _ _ := Unit
  id _ := ()
  comp _ _ := ()
  assoc _ _ _ := rfl
  left_id f := by cases f; rfl
  right_id f := by cases f; rfl
def generator {a b : Unit} (f : Graph a b) : terminal.Hom a b := processStep a f
theorem generator_original {a b : Unit} (f : Graph a b) :
    generator f = processStep a f := rfl
def interpret {a b : Unit} (p : Path Graph a b) : terminal.Hom a b :=
  eval terminal id (fun f => generator f) p
theorem interpret_single {a b : Unit} (f : Graph a b) :
    interpret (Path.single f) = processStep a f := eval_single terminal id _ f
def length : {a b : Unit} → Path Graph a b → Nat
  | _,_,.nil _ => 0
  | _,_,.cons _ p => length p + 1
def head : {a b : Unit} → Path Graph a b → Action
  | _,_,.nil _ => .a0
  | _,_,.cons a _ => a
def single (a : Action) : History := Path.single a
def h0 : History := single .a0
def h1 : History := single .a1
def empty : History := .nil ()
def double : History := .cons (b:=()) .a0 (.cons (b:=()) .a1 (.nil ()))
theorem histories_distinct : h0 ≠ h1 := by
  intro h
  have hh := congrArg (fun p : History => head p) h
  cases hh
theorem single_not_empty (a : Action) : single a ≠ empty := by
  intro h
  have hh := congrArg (fun p : History => length p) h
  cases hh
def natOrder : PreorderSpec Nat := ⟨Nat.le,Nat.le_refl,fun h h' => Nat.le_trans h h'⟩
def rewards (m : Bool) := if m then ctx1 else ctx0
def context (m : Bool) : Context History Nat where
  defined p := length p = 1
  eval p := rewards m (head p.val)
  order := natOrder
def admitted (_ : History) : Prop := True
def process (_ : Bool) := category
def value (m : Bool) (a : Action) : Nat := (context m).eval ⟨single a,rfl⟩
def orderView (m : Bool) (p q : History) : Prop :=
  ∃ hp : (context m).defined p, ∃ hq : (context m).defined q,
    (context m).order.le ((context m).eval ⟨p,hp⟩) ((context m).eval ⟨q,hq⟩)
theorem same_process : process false = process true := rfl
theorem same_domain : (context false).defined = (context true).defined := rfl
theorem value_original (m : Bool) (a : Action) :
    value m a = if m then ctx1 a else ctx0 a := by cases m <;> rfl
theorem rankings : value false .a1 < value false .a0 ∧ value true .a0 < value true .a1 := by decide
theorem contexts_differ : context false ≠ context true := by
  intro h
  have hh := congrArg (fun k : Context History Nat => observe admitted k h0) h
  change observe admitted (context false) h0 = observe admitted (context true) h0 at hh
  rw [observe_value _ _ _ trivial rfl,observe_value _ _ _ trivial rfl] at hh
  change (Outcome.value (1 : Nat)) = Outcome.value 0 at hh
  cases hh
theorem order_differ : orderView false ≠ orderView true := by
  intro h
  have hh := congrFun (congrFun h h0) h1
  have ht : orderView true h0 h1 := ⟨rfl,rfl,Nat.zero_le 1⟩
  have hf : orderView false h0 h1 := hh.symm ▸ ht
  rcases hf with ⟨_,_,bad⟩
  exact Nat.not_succ_le_zero 0 bad
theorem process_no_context : ¬ Recoverable process context :=
  no_recovery_of_collision false true same_process contexts_differ
theorem process_no_order : ¬ Recoverable process orderView :=
  no_recovery_of_collision false true same_process order_differ
theorem single_value (m : Bool) (a : Action) :
    observe admitted (context m) (single a) = .value (value m a) :=
  observe_value _ _ _ trivial rfl
theorem empty_undefined (m : Bool) : observe admitted (context m) empty = .undefined :=
  observe_undefined _ _ _ trivial (by change (0 : Nat) ≠ 1; decide)
theorem double_undefined (m : Bool) : observe admitted (context m) double = .undefined :=
  observe_undefined _ _ _ trivial (by change (2 : Nat) ≠ 1; decide)
end ActionContextsV28
