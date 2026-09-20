import AdmissibilityV5
import CategoryTreesV25
namespace CategoryAdaptersV26
universe u v
def toProc {O : Type u} (C : TypedPathsV11.Category.{u,v} O) : FoundationV5.ProcCategory where
  Obj := O
  Hom := C.Hom
  ident := C.id
  comp := C.comp
  assoc := C.assoc
  left_unit := C.left_id
  right_unit := C.right_id
def fromProc (C : FoundationV5.ProcCategory.{u,v}) : TypedPathsV11.Category C.Obj where
  Hom := C.Hom
  id := C.ident
  comp := C.comp
  assoc := C.assoc
  left_id := C.left_unit
  right_id := C.right_unit
theorem from_to {O : Type u} (C : TypedPathsV11.Category.{u,v} O) :
    fromProc (toProc C) = C := rfl
theorem to_from (C : FoundationV5.ProcCategory.{u,v}) :
    toProc (fromProc C) = C := rfl
theorem to_obj {O : Type u} (C : TypedPathsV11.Category.{u,v} O) :
    (toProc C).Obj = O := rfl
theorem to_hom {O : Type u} (C : TypedPathsV11.Category.{u,v} O) :
    (toProc C).Hom = C.Hom := rfl
theorem to_id {O : Type u} (C : TypedPathsV11.Category.{u,v} O) (a : O) :
    (toProc C).ident a = C.id a := rfl
theorem to_comp {O : Type u} (C : TypedPathsV11.Category.{u,v} O)
    {a b c : O} (f : C.Hom a b) (g : C.Hom b c) :
    (toProc C).comp f g = C.comp f g := rfl
theorem from_hom (C : FoundationV5.ProcCategory.{u,v}) : (fromProc C).Hom = C.Hom := rfl
theorem from_id (C : FoundationV5.ProcCategory.{u,v}) (a : C.Obj) :
    (fromProc C).id a = C.ident a := rfl
theorem from_comp (C : FoundationV5.ProcCategory.{u,v})
    {a b c : C.Obj} (f : C.Hom a b) (g : C.Hom b c) :
    (fromProc C).comp f g = C.comp f g := rfl
end CategoryAdaptersV26
