import FixedEncodersV29
namespace EncoderControlsV29
def source (m : Bool) (_ : Unit) : Option Bool := some m
def target (_ : Bool) (_ : Unit) : Option Bool := some false
def varying (m b : Bool) : Bool := Bool.xor b m
def code (_ : Bool) : Unit := ()
theorem varying_square (m : Bool) (q : Unit) :
    target m q = (source m q).map (varying m) := by cases m <;> rfl
theorem varying_inverse (m b : Bool) : varying m (varying m b) = b := by
  cases m <;> cases b <;> rfl
theorem target_recoverable : RecoverabilityV9.Recoverable code target :=
  ⟨fun _ _ => some false,fun _ => rfl⟩
theorem source_not_recoverable : ¬RecoverabilityV9.Recoverable code source := by
  apply RecoverabilityV9.no_recovery_of_collision false true rfl
  intro h
  have hh := congrFun h ()
  cases hh
theorem retained_model_repair : RecoverabilityV9.Recoverable (fun m : Bool => m) source :=
  ⟨fun m _ => some m.val,fun _ => rfl⟩
theorem retained_encoder_repair : RecoverabilityV9.Recoverable varying source :=
  ⟨fun e _ => some (e.val false),fun m => by cases m <;> rfl⟩
theorem erased_encoder_recovery : RecoverabilityV9.Recoverable code
    (fun m => FixedEncodersV29.encode (fun _ : Bool => false) (source m)) :=
  ⟨fun _ _ => some false,fun _ => rfl⟩
def omitted (m q : Bool) : Option Bool := if q then some m else some false
theorem omitted_pullback : RecoverabilityV9.Recoverable code
    (FixedEncodersV29.pullback omitted (fun _ : Unit => false)) :=
  ⟨fun _ _ => some false,fun _ => rfl⟩
theorem omitted_full_failure : ¬RecoverabilityV9.Recoverable code omitted := by
  apply RecoverabilityV9.no_recovery_of_collision false true rfl
  intro h
  have hh := congrFun h true
  cases hh
theorem fixed_none (j : Bool → Bool) : (none : Option Bool).map j = none := rfl
end EncoderControlsV29
