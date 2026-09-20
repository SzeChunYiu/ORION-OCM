import OptionalCategoriesV26
namespace OptionalBindingsV26
open OptionalCategoriesV26
theorem reset_hom (a b : Unit) : resetCategory.Hom a b = OptionalV13.BitProc := rfl
theorem loop_hom (a b : OptionalV13.BitProc) : loopCategory.Hom a b = OptionalV13.LoopHom a b := rfl
theorem function_hom (n m : Nat) : functions.Hom n m = (Fin n → Fin m) := rfl
theorem kernel_hom (α : Type u) [StochasticV14.Weight α] (n m : Nat) :
    (kernels α).Hom n m = StochasticV14.Kernel α n m := rfl
theorem relation_hom (n m : Nat) :
    relations.Hom n m = StochasticV14.TotalRel (Fin n) (Fin m) := rfl
theorem rational_hom (a b : Unit) : rational.Hom a b = StochasticV14.RationalModel.Arrow := rfl
theorem dirac_object (α : Type u) [StochasticV14.Weight α] (n : Nat) : (dirac α).obj n = n := rfl
theorem dirac_arrow (α : Type u) [StochasticV14.Weight α] {n m : Nat} (f : Fin n → Fin m) :
    (dirac α).hom f = StochasticV14.Kernel.embed f := rfl
theorem graph_object (n : Nat) : graph.obj n = n := rfl
theorem graph_arrow {n m : Nat} (f : Fin n → Fin m) :
    graph.hom f = StochasticV14.TotalRel.graph f := rfl
theorem support_object (α : Type u) [StochasticV14.Weight α] (n : Nat) :
    (support α).obj n = n := rfl
theorem support_arrow (α : Type u) [StochasticV14.Weight α] {n m : Nat}
    (p : StochasticV14.Kernel α n m) :
    (support α).hom p = StochasticV14.Kernel.support p := rfl
theorem dirac_entries (α : Type u) [StochasticV14.Weight α] {n m : Nat}
    (f : Fin n → Fin m) (i : Fin n) (j : Fin m) :
    ((dirac α).hom f).value i j = if j=f i then 1 else 0 := rfl
theorem graph_relation {n m : Nat} (f : Fin n → Fin m) (i : Fin n) (j : Fin m) :
    (graph.hom f).relates i j ↔ j=f i := Iff.rfl
theorem support_relation (α : Type u) [StochasticV14.Weight α] {n m : Nat}
    (p : StochasticV14.Kernel α n m) (i : Fin n) (j : Fin m) :
    ((support α).hom p).relates i j ↔ p.value i j ≠ 0 := Iff.rfl
end OptionalBindingsV26
