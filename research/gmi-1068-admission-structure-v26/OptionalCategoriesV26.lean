import ProcessMapsV26
import InterchangeV13
import LoopMonoidalV13
import SupportV14
import RationalModelV14
namespace OptionalCategoriesV26
open TypedPathsV11 ProcessMapsV26
def resetCategory : Category Unit where
  Hom _ _ := OptionalV13.BitProc
  id _ := .identity
  comp := OptionalV13.sequence
  assoc := OptionalV13.sequence_assoc
  left_id := OptionalV13.sequence_left
  right_id := OptionalV13.sequence_right
def loopCategory : Category OptionalV13.BitProc where
  Hom := OptionalV13.LoopHom
  id := OptionalV13.LoopHom.ident
  comp := OptionalV13.LoopHom.comp
  assoc := OptionalV13.LoopHom.comp_assoc
  left_id := OptionalV13.LoopHom.left_id
  right_id := OptionalV13.LoopHom.right_id
def functions : Category Nat where
  Hom n m := Fin n → Fin m
  id _ := id
  comp f g := fun x => g (f x)
  assoc _ _ _ := rfl
  left_id _ := rfl
  right_id _ := rfl
def kernels (α : Type u) [StochasticV14.Weight α] : Category Nat where
  Hom := StochasticV14.Kernel α
  id := StochasticV14.Kernel.ident
  comp := StochasticV14.Kernel.comp
  assoc := StochasticV14.Kernel.assoc
  left_id := StochasticV14.Kernel.left_id
  right_id := StochasticV14.Kernel.right_id
def relations : Category Nat where
  Hom n m := StochasticV14.TotalRel (Fin n) (Fin m)
  id n := StochasticV14.TotalRel.ident (Fin n)
  comp := StochasticV14.TotalRel.comp
  assoc := StochasticV14.TotalRel.assoc
  left_id := StochasticV14.TotalRel.left_id
  right_id := StochasticV14.TotalRel.right_id
def dirac (α : Type u) [StochasticV14.Weight α] : ProcessMap functions (kernels α) where
  obj := id
  hom := StochasticV14.Kernel.embed
  id_law _ := rfl
  comp_law f g := (StochasticV14.Kernel.embed_comp f g).symm
def graph : ProcessMap functions relations where
  obj := id
  hom := StochasticV14.TotalRel.graph
  id_law _ := rfl
  comp_law f g := (StochasticV14.TotalRel.graph_comp f g).symm
def support (α : Type u) [StochasticV14.Weight α] : ProcessMap (kernels α) relations where
  obj := id
  hom := StochasticV14.Kernel.support
  id_law := StochasticV14.Kernel.support_ident
  comp_law := StochasticV14.Kernel.support_comp
theorem dirac_faithful (α : Type u) [StochasticV14.Weight α] : (dirac α).Faithful :=
  fun _ _ h => StochasticV14.Kernel.embed_faithful h
theorem graph_faithful : graph.Faithful :=
  fun _ _ h => StochasticV14.TotalRel.graph_faithful h
def rational : Category Unit where
  Hom _ _ := StochasticV14.RationalModel.Arrow
  id _ := .identity
  comp := StochasticV14.RationalModel.comp
  assoc := StochasticV14.RationalModel.assoc
  left_id := StochasticV14.RationalModel.left_id
  right_id := StochasticV14.RationalModel.right_id
theorem reset_id (a : Unit) : resetCategory.id a = OptionalV13.BitProc.identity := rfl
theorem reset_comp (f g : OptionalV13.BitProc) :
    resetCategory.comp (a:=()) (b:=()) (c:=()) f g = OptionalV13.sequence f g := rfl
theorem loop_id (a : OptionalV13.BitProc) : loopCategory.id a = OptionalV13.LoopHom.ident a := rfl
theorem loop_comp {a b c : OptionalV13.BitProc} (f : OptionalV13.LoopHom a b)
    (g : OptionalV13.LoopHom b c) : loopCategory.comp f g = OptionalV13.LoopHom.comp f g := rfl
theorem function_id (n : Nat) : functions.id n = id := rfl
theorem function_comp {n m k : Nat} (f : Fin n → Fin m) (g : Fin m → Fin k) :
    functions.comp f g = fun x => g (f x) := rfl
theorem kernel_id (α : Type u) [StochasticV14.Weight α] (n : Nat) :
    (kernels α).id n = StochasticV14.Kernel.ident n := rfl
theorem kernel_comp (α : Type u) [StochasticV14.Weight α] {n m k : Nat}
    (f : StochasticV14.Kernel α n m) (g : StochasticV14.Kernel α m k) :
    (kernels α).comp f g = StochasticV14.Kernel.comp f g := rfl
theorem relation_id (n : Nat) : relations.id n = StochasticV14.TotalRel.ident (Fin n) := rfl
theorem relation_comp {n m k : Nat} (f : StochasticV14.TotalRel (Fin n) (Fin m))
    (g : StochasticV14.TotalRel (Fin m) (Fin k)) :
    relations.comp f g = StochasticV14.TotalRel.comp f g := rfl
theorem rational_id : rational.id () = StochasticV14.RationalModel.Arrow.identity := rfl
theorem rational_comp (f g : StochasticV14.RationalModel.Arrow) :
    rational.comp (a:=()) (b:=()) (c:=()) f g = StochasticV14.RationalModel.comp f g := rfl
end OptionalCategoriesV26
