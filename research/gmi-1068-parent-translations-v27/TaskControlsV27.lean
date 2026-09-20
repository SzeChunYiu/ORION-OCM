import RegularTasksV27
namespace TaskControlsV27
open StochasticV14 TaskInterfacesV27
def full : Interface Bool := fun _ => True
def swap (x : Carrier full) : Carrier full := ⟨!x.val,trivial⟩
def swapTask : (category Bool).Hom full full := TotalRel.graph swap
def idTask : (category Bool).Hom full full := TotalRel.ident (Carrier full)
def Possible (t : (category Bool).Hom full full) := t=idTask
theorem swap_twice : swapTask.comp swapTask=idTask := by
  rw [show swapTask=TotalRel.graph swap from rfl,TotalRel.graph_comp]
  have h : swap ∘ swap=id := by
    funext x; apply Subtype.ext
    exact Bool.not_not x.val
  rw [h]
  rfl
theorem swap_impossible : ¬Possible swapTask := by
  intro h
  have hf : swap=id := TotalRel.graph_faithful h
  have hh := congrArg Subtype.val (congrFun hf ⟨false,trivial⟩)
  cases hh
theorem possible_closed (p q : (category Bool).Hom full full)
    (hp : Possible p) (hq : Possible q) : Possible (p.comp q) := by
  change p=idTask at hp; change q=idTask at hq
  subst p; subst q
  exact TotalRel.left_id _
theorem possible_composite_not_factors :
    Possible (swapTask.comp swapTask) ∧ ¬Possible swapTask :=
  ⟨swap_twice,swap_impossible⟩
def candidate (f : Bool → Bool) := ¬(f false=true ∧ f true=true)
theorem candidate_not_closed :
    candidate id ∧ candidate Bool.not ∧ candidate (fun _ => false) ∧
      ¬candidate (Bool.not ∘ (fun _ => false)) := by
  unfold candidate
  decide
end TaskControlsV27
