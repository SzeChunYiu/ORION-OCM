import ActionContextsV28
import RawDomainsV28
namespace ContextBindingsV28
open TypedPathsV11 PartialContextV15
theorem graph (a b : Unit) : ActionContextsV28.Graph a b = Action := rfl
theorem path_hom (a b : Unit) : ActionContextsV28.category.Hom a b =
    Path ActionContextsV28.Graph a b := rfl
theorem path_identity (a : Unit) : ActionContextsV28.category.id a = Path.nil a := rfl
theorem path_composition {a b c : Unit}
    (p : ActionContextsV28.category.Hom a b) (q : ActionContextsV28.category.Hom b c) :
    ActionContextsV28.category.comp p q = Path.append p q := rfl
theorem terminal_hom (a b : Unit) : ActionContextsV28.terminal.Hom a b = Unit := rfl
theorem terminal_identity (a : Unit) : ActionContextsV28.terminal.id a = () := rfl
theorem terminal_composition {a b c : Unit}
    (p : ActionContextsV28.terminal.Hom a b) (q : ActionContextsV28.terminal.Hom b c) :
    ActionContextsV28.terminal.comp p q = () := rfl
theorem length_nil (a : Unit) : ActionContextsV28.length (Path.nil a) = 0 := rfl
theorem length_cons {a b c : Unit} (f : ActionContextsV28.Graph a b) (p : Path ActionContextsV28.Graph b c) :
    ActionContextsV28.length (Path.cons f p) = ActionContextsV28.length p + 1 := rfl
theorem head_nil (a : Unit) : ActionContextsV28.head (Path.nil a) = .a0 := rfl
theorem head_cons {a b c : Unit} (f : ActionContextsV28.Graph a b) (p : Path ActionContextsV28.Graph b c) :
    ActionContextsV28.head (Path.cons f p) = f := rfl
theorem singleton (a : Action) : ActionContextsV28.single a =
    (Path.single a : Path ActionContextsV28.Graph () ()) := rfl
theorem h_zero : ActionContextsV28.h0 = ActionContextsV28.single .a0 := rfl
theorem h_one : ActionContextsV28.h1 = ActionContextsV28.single .a1 := rfl
theorem empty_path : ActionContextsV28.empty = Path.nil () := rfl
theorem double_path : ActionContextsV28.double =
    Path.cons (b:=()) Action.a0 (Path.cons (b:=()) Action.a1 (Path.nil ())) := rfl
theorem domain (m : Bool) (p : ActionContextsV28.History) :
    (ActionContextsV28.context m).defined p ↔ ActionContextsV28.length p = 1 := Iff.rfl
theorem evaluator (m : Bool) (p : {p : ActionContextsV28.History // (ActionContextsV28.context m).defined p}) :
    (ActionContextsV28.context m).eval p =
      if m then ctx1 (ActionContextsV28.head p.val) else ctx0 (ActionContextsV28.head p.val) := by cases m <;> rfl
theorem context_order (m : Bool) (a b : Nat) : (ActionContextsV28.context m).order.le a b ↔ a ≤ b := Iff.rfl
theorem all_paths (p : ActionContextsV28.History) : ActionContextsV28.admitted p ↔ True := Iff.rfl
theorem process (m : Bool) : ActionContextsV28.process m = ActionContextsV28.category := rfl
theorem order_view (m : Bool) (p q : ActionContextsV28.History) :
    ActionContextsV28.orderView m p q ↔
      ∃ hp : (ActionContextsV28.context m).defined p, ∃ hq : (ActionContextsV28.context m).defined q,
        (ActionContextsV28.context m).order.le ((ActionContextsV28.context m).eval ⟨p,hp⟩)
          ((ActionContextsV28.context m).eval ⟨q,hq⟩) := Iff.rfl
theorem active_domain (m : Bool) (p : ActionContextsV28.History) :
    (relativeDomain ActionContextsV28.admitted (ActionContextsV28.context m)).defined p ↔
      ActionContextsV28.length p = 1 := by
  change (True ∧ ActionContextsV28.length p = 1) ↔ _
  simp
theorem interpretation {a b : Unit} (p : Path ActionContextsV28.Graph a b) :
    ActionContextsV28.interpret p =
      eval ActionContextsV28.terminal id (fun f => ActionContextsV28.generator f) p := rfl
end ContextBindingsV28
