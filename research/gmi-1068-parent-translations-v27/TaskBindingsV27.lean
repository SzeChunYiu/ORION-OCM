import RegularTasksV27
namespace TaskBindingsV27
open TaskInterfacesV27 StochasticV14
universe u
variable {X : Type u}
theorem task_hom (I J : Interface X) :
    (category X).Hom I J=TotalRel (Carrier I) (Carrier J) := rfl
theorem task_id (I : Interface X) : (category X).id I=TotalRel.ident (Carrier I) := rfl
theorem task_comp {I J K : Interface X} (p : (category X).Hom I J) (q : (category X).Hom J K) :
    (category X).comp p q=p.comp q := rfl
theorem decode_value {I J : Interface X} (p : (category X).Hom I J) (x y : X) :
    decode p x y ↔ ∃hx:I x,∃hy:J y,p.relates ⟨x,hx⟩ ⟨y,hy⟩ := Iff.rfl
theorem domain (r : RelParentV27.Rel X X) (x : X) : Dom r x ↔ ∃y,r x y := Iff.rfl
theorem range (r : RelParentV27.Rel X X) (y : X) : Ran r y ↔ ∃x,r x y := Iff.rfl
theorem canonical_value (r : RelParentV27.Rel X X) (x : Carrier (Dom r)) (y : Carrier (Ran r)) :
    (canonical r).relates x y ↔ r x.val y.val := Iff.rfl
theorem bridge_value {I J : Interface X} (h : ∀x,I x→J x) (x : Carrier I) (y : Carrier J) :
    (bridge h).relates x y ↔ y=inclusion h x := Iff.rfl
theorem regular (r s : RelParentV27.Rel X X) :
    RegularTasksV27.Regular r s ↔ ∀y,Ran r y→Dom s y := Iff.rfl
theorem regular_task (r s : RelParentV27.Rel X X) (h : RegularTasksV27.Regular r s) :
    RegularTasksV27.regularTask r s h=(canonical r |>.comp (bridge h) |>.comp (canonical s)) := rfl
theorem source_R (x y : Fin 5) : RegularTasksV27.R x y ↔ x=0 ∧ y=1 := Iff.rfl
theorem source_S (x y : Fin 5) : RegularTasksV27.S x y ↔ (x=1 ∧ y=2) ∨ (x=3 ∧ y=4) := Iff.rfl
theorem source_T (x y : Fin 5) : RegularTasksV27.T x y ↔ x=2 ∧ y=2 := Iff.rfl
end TaskBindingsV27
