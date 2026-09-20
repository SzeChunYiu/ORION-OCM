import TaskControlsV27
import EventObservationsV27
import CoalgebraControlsV27
namespace ControlBindingsV27
theorem dead_edge (s a t : Unit) : CoalgebraControlsV27.dead s a t ↔ False := Iff.rfl
theorem loop_edge (s a t : Unit) : CoalgebraControlsV27.loop s a t ↔ True := Iff.rfl
theorem full_interface (x : Bool) : TaskControlsV27.full x ↔ True := Iff.rfl
theorem swap_value (x : TaskInterfacesV27.Carrier TaskControlsV27.full) :
    (TaskControlsV27.swap x).val= !x.val := rfl
theorem swap_relation : TaskControlsV27.swapTask=StochasticV14.TotalRel.graph TaskControlsV27.swap := rfl
theorem id_relation : TaskControlsV27.idTask=
    StochasticV14.TotalRel.ident (TaskInterfacesV27.Carrier TaskControlsV27.full) := rfl
theorem possible_value (t : (TaskInterfacesV27.category Bool).Hom TaskControlsV27.full TaskControlsV27.full) :
    TaskControlsV27.Possible t ↔ t=TaskControlsV27.idTask := Iff.rfl
theorem candidate_value (f : Bool→Bool) : TaskControlsV27.candidate f ↔ ¬(f false=true ∧ f true=true) := Iff.rfl
theorem rational_tests (b o : Bool) :
    EventObservationsV27.testWeights b o=
      (if b then (if o then StochasticV14.RationalModel.frac 2 3 else StochasticV14.RationalModel.frac 1 3)
       else StochasticV14.RationalModel.frac 1 2) := rfl
end ControlBindingsV27
