import PartialContextV15
namespace ContextMapsV17
open PartialContextV15
universe u v w x
structure OrderMap {W : Type v} {Z : Type w} (r : PreorderSpec W) (s : PreorderSpec Z) where
  fn : W → Z
  monotone : ∀ {a b}, r.le a b → s.le (fn a) (fn b)

def identity {W : Type v} (r : PreorderSpec W) : OrderMap r r := ⟨id, fun h => h⟩
def compose {W : Type v} {Z : Type w} {Y : Type x}
    {r : PreorderSpec W} {s : PreorderSpec Z} {t : PreorderSpec Y}
    (g : OrderMap s t) (f : OrderMap r s) : OrderMap r t :=
  ⟨fun a => g.fn (f.fn a), fun h => g.monotone (f.monotone h)⟩

theorem map_ext {W : Type v} {Z : Type w} {r : PreorderSpec W} {s : PreorderSpec Z}
    (f g : OrderMap r s) (h : f.fn = g.fn) : f=g := by
  cases f
  cases g
  cases h
  rfl

theorem compose_identity {W : Type v} {Z : Type w} {r : PreorderSpec W} {s : PreorderSpec Z}
    (f : OrderMap r s) : compose (identity s) f = f ∧ compose f (identity r) = f :=
  ⟨map_ext _ _ rfl, map_ext _ _ rfl⟩

theorem compose_assoc {A : Type u} {B : Type v} {C : Type w} {D : Type x}
    {r : PreorderSpec A} {s : PreorderSpec B} {t : PreorderSpec C} {z : PreorderSpec D}
    (f : OrderMap r s) (g : OrderMap s t) (h : OrderMap t z) :
    compose h (compose g f) = compose (compose h g) f := map_ext _ _ rfl

def outcomeMap {W : Type v} {Z : Type w} (f : W → Z) : Outcome W → Outcome Z
  | .illegal => .illegal | .undefined => .undefined | .value w => .value (f w)

def postcompose {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (s : PreorderSpec Z) (f : W → Z) : Context H Z where
  defined := k.defined
  eval h := f (k.eval h)
  order := s

theorem post_defined {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (s : PreorderSpec Z) (f : W → Z) :
    (postcompose k s f).defined = k.defined := rfl

theorem post_value {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (s : PreorderSpec Z) (f : W → Z) (h : {h // k.defined h}) :
    (postcompose k s f).eval h = f (k.eval h) := rfl

theorem post_identity {H : Type u} {W : Type v} (k : Context H W) :
    postcompose k k.order id = k := by cases k; rfl

theorem post_comp {H : Type u} {W : Type v} {Z : Type w} {Y : Type x}
    (k : Context H W) (s : PreorderSpec Z) (t : PreorderSpec Y) (f : W → Z) (g : Z → Y) :
    postcompose (postcompose k s f) t g = postcompose k t (fun a => g (f a)) := rfl

theorem post_observe {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (s : PreorderSpec Z) (f : W → Z) (h : H) :
    observe P (postcompose k s f) h = outcomeMap f (observe P k h) := by
  classical
  by_cases hp : P h
  · by_cases he : k.defined h
    · rw [observe_value P k h hp he, observe_value P (postcompose k s f) h hp he]
      rfl
    · rw [observe_undefined P k h hp he, observe_undefined P (postcompose k s f) h hp he]
      rfl
  · rw [observe_illegal P k h hp, observe_illegal P (postcompose k s f) h hp]
    rfl

theorem post_comparison {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (s : PreorderSpec Z) (f : OrderMap k.order s)
    (a b : Active P k) (h : (activeOrder P k).le a b) :
    (activeOrder P (postcompose k s f.fn)).le a b := f.monotone h

theorem post_comparison_iff {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (s : PreorderSpec Z) (f : OrderMap k.order s)
    (reflect : ∀ a b, s.le (f.fn a) (f.fn b) → k.order.le a b)
    (a b : Active P k) :
    (activeOrder P (postcompose k s f.fn)).le a b ↔ (activeOrder P k).le a b :=
  ⟨reflect _ _, f.monotone⟩

def dualOrder {W : Type v} (r : PreorderSpec W) : PreorderSpec W where
  le a b := r.le b a
  refl := r.refl
  trans h k := r.trans k h

def dual {H : Type u} {W : Type v} (k : Context H W) : Context H W :=
  ⟨k.defined, k.eval, dualOrder k.order⟩

theorem dual_defined {H : Type u} {W : Type v} (k : Context H W) :
    (dual k).defined = k.defined := rfl
theorem dual_value {H : Type u} {W : Type v} (k : Context H W) (h : {h // k.defined h}) :
    (dual k).eval h = k.eval h := rfl
theorem dual_comparison {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W)
    (a b : Active P k) :
    (activeOrder P (dual k)).le a b ↔ (activeOrder P k).le b a := Iff.rfl
theorem dual_twice {H : Type u} {W : Type v} (k : Context H W) :
    dual (dual k) = k := by cases k; rfl
theorem dual_observe {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : H) :
    observe P (dual k) h = observe P k h := rfl
theorem identity_apply {W : Type v} (r : PreorderSpec W) (a : W) :
    (identity r).fn a = a := rfl
theorem compose_apply {W : Type v} {Z : Type w} {Y : Type x}
    {r : PreorderSpec W} {s : PreorderSpec Z} {t : PreorderSpec Y}
    (g : OrderMap s t) (f : OrderMap r s) (a : W) :
    (compose g f).fn a = g.fn (f.fn a) := rfl
theorem post_order {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (s : PreorderSpec Z) (f : W → Z) :
    (postcompose k s f).order = s := rfl
end ContextMapsV17
