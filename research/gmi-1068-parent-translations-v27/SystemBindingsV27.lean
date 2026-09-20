import ParentBindingsV27
import TaskInterfacesV27
namespace SystemBindingsV27
open SetCoalgebraV27 StochasticV14
universe u
theorem functions_hom (X Y : Type u) : functions.Hom X Y=(X→Y) := rfl
theorem functions_id (X : Type u) : functions.id X=id := rfl
theorem functions_comp {X Y Z : Type u} (f : X→Y) (g : Y→Z) :
    functions.comp f g=g ∘ f := rfl
theorem tagged_id (F : SetEndo.{u}) (S : System F) : (tagged F).id S=id := rfl
theorem tagged_comp {F : SetEndo.{u}} {S T U : System F}
    (f : S.carrier→T.carrier) (g : T.carrier→U.carrier) :
    (tagged F).comp f g=g ∘ f := rfl
theorem tagged_map {F : SetEndo.{u}} {S T : System F} (f : Hom F S T) :
    (taggedForget F).hom f=f.val := rfl
theorem power_obj (A X : Type u) : (power A).obj X=((A×X)→Prop) := rfl
theorem power_map {A X Y : Type u} (f : X→Y) :
    (power A).map f=LTSCoalgebraV27.powerMap (A:=A) f := rfl
theorem from_lts {A S : Type u} (r : LTSCoalgebraV27.LTS S A) :
    (fromLTS r).step=LTSCoalgebraV27.successors r := rfl
theorem output_obj (X : Type) : CoalgebraControlsV27.outputNext.obj X=(Bool×X) := rfl
theorem output_map {X Y : Type} (f : X→Y) (p : Bool×X) :
    CoalgebraControlsV27.outputNext.map f p=(p.1,f p.2) := rfl
theorem total_id (X : Type u) : RelParentV27.totalCategory.id X=TotalRel.ident X := rfl
theorem total_comp {X Y Z : Type u} (p : TotalRel X Y) (q : TotalRel Y Z) :
    RelParentV27.totalCategory.comp p q=p.comp q := rfl
theorem possible_category {X : Type u}
    (P : {I J : TaskInterfacesV27.Interface X} → (TaskInterfacesV27.category X).Hom I J → Prop)
    (closed : FoundationV5.Closed (CategoryAdaptersV26.toProc (TaskInterfacesV27.category X)) P) :
    TaskInterfacesV27.possible P closed=RestrictedV26.category (TaskInterfacesV27.category X) P closed := rfl
end SystemBindingsV27
