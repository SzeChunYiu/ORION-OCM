import QuotientPathsV11
import ProcessMapsV26
namespace EvalKernelV29
open TypedPathsV11 ProcessMapsV26
universe u v w
variable {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b)
abbrev quotient : Category O := (kernel C id edge).category
def lower {a b : O} (p : (quotient C edge).Hom a b) : C.Hom a b :=
  Quotient.liftOn p (eval C id edge) (fun _ _ h => h)
theorem lower_class {a b : O} (p : Path G a b) :
    lower C edge ((kernel C id edge).classOf p) = eval C id edge p := rfl
theorem lower_id (a : O) :
    lower C edge ((quotient C edge).id a) = C.id a := rfl
theorem lower_comp {a b c : O} (p : (quotient C edge).Hom a b)
    (q : (quotient C edge).Hom b c) :
    lower C edge ((quotient C edge).comp p q) = C.comp (lower C edge p) (lower C edge q) := by
  induction p using Quotient.inductionOn with
  | h p =>
    induction q using Quotient.inductionOn with
    | h q => exact eval_append C id edge p q
theorem lower_injective {a b : O} (p q : (quotient C edge).Hom a b)
    (h : lower C edge p = lower C edge q) : p = q := by
  induction p using Quotient.inductionOn with
  | h p =>
    induction q using Quotient.inductionOn with
    | h q => exact Quotient.sound h
def lowerMap : ProcessMap (quotient C edge) C where
  obj := id
  hom := lower C edge
  id_law := lower_id C edge
  comp_law := lower_comp C edge
theorem lower_faithful : (lowerMap C edge).Faithful := lower_injective C edge
theorem lower_objects : (lowerMap C edge).ObjectInjective := fun _ _ h => h
def Generates : Prop := ∀ {a b : O} (f : C.Hom a b), ∃ p : Path G a b, eval C id edge p = f
noncomputable def quote (gen : Generates C edge) {a b : O} (f : C.Hom a b) :
    (quotient C edge).Hom a b := (kernel C id edge).classOf (Classical.choose (gen f))
theorem lower_quote (gen : Generates C edge) {a b : O} (f : C.Hom a b) :
    lower C edge (quote C edge gen f) = f := Classical.choose_spec (gen f)
theorem quote_lower (gen : Generates C edge) {a b : O} (p : (quotient C edge).Hom a b) :
    quote C edge gen (lower C edge p) = p :=
  lower_injective C edge _ _ (lower_quote C edge gen _)
theorem quote_id (gen : Generates C edge) (a : O) :
    quote C edge gen (C.id a) = (quotient C edge).id a := by
  apply lower_injective C edge
  rw [lower_quote, lower_id]
theorem quote_comp (gen : Generates C edge) {a b c : O} (f : C.Hom a b) (g : C.Hom b c) :
    quote C edge gen (C.comp f g) = (quotient C edge).comp (quote C edge gen f) (quote C edge gen g) := by
  apply lower_injective C edge
  rw [lower_quote, lower_comp, lower_quote, lower_quote]
noncomputable def quoteMap (gen : Generates C edge) : ProcessMap C (quotient C edge) where
  obj := id
  hom := quote C edge gen
  id_law := quote_id C edge gen
  comp_law := quote_comp C edge gen
theorem quote_faithful (gen : Generates C edge) : (quoteMap C edge gen).Faithful := by
  intro a b f g h
  change quote C edge gen f = quote C edge gen g at h
  have hh := congrArg (lower C edge) h
  simpa only [lower_quote] using hh
theorem quote_objects (gen : Generates C edge) : (quoteMap C edge gen).ObjectInjective := fun _ _ h => h
theorem generates_iff_onto :
    Generates C edge ↔ ∀ {a b : O} (f : C.Hom a b), ∃ p, lower C edge p = f := by
  constructor
  · intro gen a b f
    exact ⟨quote C edge gen f,lower_quote C edge gen f⟩
  · intro h a b f
    obtain ⟨p,hp⟩ := h f
    induction p using Quotient.inductionOn with
    | h p => exact ⟨p,hp⟩
theorem own_generates : Generates C (fun f : C.Hom _ _ => f) := eval_onto C
theorem own_quotient : quotient C (fun f : C.Hom _ _ => f) = presented C := rfl
theorem own_lower {a b : O} (p : (presented C).Hom a b) :
    lower C (fun f : C.Hom _ _ => f) p = TypedPathsV11.lower C p := rfl
theorem own_quote {a b : O} (f : C.Hom a b) :
    quote C (fun f : C.Hom _ _ => f) (own_generates C) f = TypedPathsV11.quote C f := by
  apply lower_injective C (fun f : C.Hom _ _ => f)
  rw [lower_quote,own_lower,TypedPathsV11.lower_quote]
end EvalKernelV29
