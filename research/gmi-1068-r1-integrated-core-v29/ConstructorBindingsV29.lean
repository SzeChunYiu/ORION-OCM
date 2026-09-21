import PresentationBridgeV29
import RestrictedAmbientV29
import FixedEncodersV29
namespace ConstructorBindingsV29
open TypedPathsV11 ProcessMapsV26 BundledCategoryV19 BracketV25
universe u v w x y z
theorem quotient_hom {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) (a b : O) :
    (EvalKernelV29.quotient C edge).Hom a b = (kernel C id edge).Hom a b := rfl
theorem lower_map_obj {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) (a : O) :
    (EvalKernelV29.lowerMap C edge).obj a = a := rfl
theorem lower_map_hom {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) {a b : O}
    (f : (EvalKernelV29.quotient C edge).Hom a b) :
    (EvalKernelV29.lowerMap C edge).hom f = EvalKernelV29.lower C edge f := rfl
theorem generates {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) :
    EvalKernelV29.Generates C edge ↔ ∀ {a b : O} (f : C.Hom a b), ∃ p : Path G a b,
      eval C id edge p = f := Iff.rfl
theorem quote_map_obj {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) (gen : EvalKernelV29.Generates C edge) (a : O) :
    (EvalKernelV29.quoteMap C edge gen).obj a = a := rfl
theorem quote_map_hom {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) (gen : EvalKernelV29.Generates C edge)
    {a b : O} (f : C.Hom a b) :
    (EvalKernelV29.quoteMap C edge gen).hom f = EvalKernelV29.quote C edge gen f := rfl
theorem quote_representative {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) (gen : EvalKernelV29.Generates C edge)
    {a b : O} (f : C.Hom a b) :
    EvalKernelV29.quote C edge gen f = (kernel C id edge).classOf (Classical.choose (gen f)) := rfl
theorem put_value {A : Type u} {L : Type v} (j : A → L) (a : A) :
    (ImageAlgebraV29.put j a).val = j a := rfl
theorem image_operation {A : Type u} {L : Type v} (j : A → L)
    (m : A → A → Option A) (a b : ImageAlgebraV29.Image j) :
    ImageAlgebraV29.operation j m a b =
      (m (ImageAlgebraV29.get j a) (ImageAlgebraV29.get j b)).map (ImageAlgebraV29.put j) := rfl
theorem image_algebra_mul {A : Type u} {L : Type v} (j : A → L)
    (hj : ∀ a b, j a = j b → a = b) (P : PartialUnitsV19.Algebra A)
    (a b : ImageAlgebraV29.Image j) :
    (ImageAlgebraV29.algebra j hj P).mul a b = ImageAlgebraV29.operation j P.mul a b := rfl
theorem named_presented {O : Type u} {L : Type w} {N : Type x} (C : Category.{u,v} O)
    (j : Arrow C → L) (hj : ∀ a b, j a = j b → a = b) (q : N → O) :
    (AmbientNamedV29.named C j hj q).presented = ImageAlgebraV29.presented j hj (algebra C) := rfl
theorem named_commutes {O : Type u} {P : Type w} {C : Category.{u,v} O}
    {D : Category.{w,x} P} (F : ProcessMap C D) :
    NamedTransportV29.Commutes F ↔ ∀ t,
      NamedObserversV25.observer (CategoryTreesV25.named D) (F.tree t) =
      (NamedObserversV25.observer (CategoryTreesV25.named C) t).map F.bundle := Iff.rfl
theorem pullback {M : Type u} {Q : Type v} {R : Type w} {B : Type x}
    (target : M → R → Option B) (i : Q → R) (m : M) (q : Q) :
    FixedEncodersV29.pullback target i m q = target m (i q) := rfl
theorem encode {Q : Type u} {A : Type v} {B : Type w} (j : A → B)
    (f : Q → Option A) (q : Q) : FixedEncodersV29.encode j f q = (f q).map j := rfl
end ConstructorBindingsV29
