import ResourceControlsV26
import FunctorControlsV26
import LocallyDiscreteV26
import OptionalCategoriesV26
namespace ConstructorBindingsV26
open TypedPathsV11 ProcessMapsV26 BracketV25
universe u v w x
variable {O : Type u} {P : Type w} {C : Category.{u,v} O} {D : Category.{w,x} P}
theorem bundle_binding (F : ProcessMap C D) {a b : O} (f : C.Hom a b) :
    F.bundle ⟨a,b,f⟩ = ⟨F.obj a,F.obj b,F.hom f⟩ := rfl
theorem tree_binding (F : ProcessMap C D) : F.tree = Tree.map F.obj F.bundle := rfl
theorem object_injective_binding (F : ProcessMap C D) :
    F.ObjectInjective ↔ ∀ a b, F.obj a = F.obj b → a = b := Iff.rfl
theorem faithful_binding (F : ProcessMap C D) :
    F.Faithful ↔ ∀ {a b} (f g : C.Hom a b), F.hom f = F.hom g → f = g := Iff.rfl
theorem products_binding (F : ProcessMap C D) :
    RawTransportV26.ProductsCommute F ↔ ∀ a b,
      BundledCategoryV19.mul D (F.bundle a) (F.bundle b) =
      (BundledCategoryV19.mul C a b).map F.bundle := Iff.rfl
theorem trees_binding (F : ProcessMap C D) :
    RawTransportV26.TreesCommute F ↔ ∀ t,
      CategoryTreesV25.observer D (F.tree t) =
      (CategoryTreesV25.observer C t).map F.bundle := Iff.rfl
theorem restricted_binding (K : {a b : O} → C.Hom a b → Prop)
    (h : FoundationV5.Closed (CategoryAdaptersV26.toProc C) K) :
    RestrictedV26.category C K h =
      CategoryAdaptersV26.fromProc
        (FoundationV5.restrictedCategory (CategoryAdaptersV26.toProc C) K h) := rfl
theorem resource_binding (cost : {a b : O} → C.Hom a b → Nat)
    (id0 : ∀ a, cost (C.id a) = 0)
    (add : ∀ {a b c} (f : C.Hom a b) (g : C.Hom b c), cost (C.comp f g) = cost f + cost g) :
    ResourceCategoryV26.category C cost id0 add =
      CategoryAdaptersV26.fromProc
        (FoundationV5.resourceCategory (CategoryAdaptersV26.toProc C) cost id0 add) := rfl
theorem two_binding {a b : O} (f g : C.Hom a b) :
    LocallyDiscreteV26.Two C f g = PLift (f = g) := rfl
theorem two_id_binding {a b : O} (f : C.Hom a b) :
    (LocallyDiscreteV26.twoId C f).down = (rfl : f=f) := rfl
theorem vertical_binding {a b : O} {f g h : C.Hom a b}
    (p : LocallyDiscreteV26.Two C f g) (q : LocallyDiscreteV26.Two C g h) :
    (LocallyDiscreteV26.vertical C p q).down = p.down.trans q.down := rfl
theorem horizontal_binding {a b c : O} {f f' : C.Hom a b} {g g' : C.Hom b c}
    (p : LocallyDiscreteV26.Two C f f') (q : LocallyDiscreteV26.Two C g g') :
    (LocallyDiscreteV26.horizontal C p q).down =
      (congrArg (fun z => C.comp z g) p.down).trans (congrArg (C.comp f') q.down) := rfl
theorem local_hom_binding (a b : O) (f g : C.Hom a b) :
    (LocallyDiscreteV26.homCategory C a b).Hom f g = PLift (f=g) := rfl
theorem local_id_binding (a b : O) (f : C.Hom a b) :
    (LocallyDiscreteV26.homCategory C a b).id f = LocallyDiscreteV26.twoId C f := rfl
theorem local_comp_binding {a b : O} {f g h : C.Hom a b}
    (p : LocallyDiscreteV26.Two C f g) (q : LocallyDiscreteV26.Two C g h) :
    (LocallyDiscreteV26.homCategory C a b).comp p q = LocallyDiscreteV26.vertical C p q := rfl
theorem indiscrete_hom (A : Type u) (a b : A) : (FunctorControlsV26.indiscrete A).Hom a b = Unit := rfl
theorem collapse_object (a : Bool) : FunctorControlsV26.collapse.obj a = () := rfl
theorem collapse_arrow {a b : Bool} (f : (FunctorControlsV26.indiscrete Bool).Hom a b) :
    FunctorControlsV26.collapse.hom f = () := rfl
theorem bitgroup_hom (a b : Unit) : FunctorControlsV26.bitGroup.Hom a b = Bool := rfl
theorem bitgroup_comp (a b : Bool) :
    FunctorControlsV26.bitGroup.comp (a:=()) (b:=()) (c:=()) a b = Bool.xor a b := rfl
theorem resource_first_value : ResourceControlsV26.first.val = (1 : Nat) := rfl
theorem resource_restarting_value : ResourceControlsV26.restarting.val = (1 : Nat) := rfl
theorem resource_cost_value {a b : Unit} (n : Nat) :
    ResourceControlsV26.cost (a:=a) (b:=b) n = n := rfl
end ConstructorBindingsV26
