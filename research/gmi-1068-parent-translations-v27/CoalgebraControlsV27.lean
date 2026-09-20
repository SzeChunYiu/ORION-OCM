import SetCoalgebraV27
namespace CoalgebraControlsV27
open SetCoalgebraV27 LTSCoalgebraV27 BracketV25
def outputNext : SetEndo where
  obj X := Bool×X
  map f p := (p.1,f p.2)
  map_id _ := rfl
  map_comp _ _ := rfl
def singleton (b : Bool) : System outputNext := ⟨Unit,fun _ => (b,())⟩
theorem singleton_distinct : singleton false≠singleton true := by
  intro h
  have hs : (fun _ : Unit => (false,()))=(fun _ : Unit => (true,())) :=
    eq_of_heq (System.mk.inj h).2
  have he := congrArg Prod.fst (congrFun hs ())
  cases he
theorem same_carrier : (singleton false).carrier=(singleton true).carrier := rfl
theorem forgotten_empty_loss :
    CategoryTreesV25.observer (category outputNext) (.seq (.empty (singleton false)) (.empty (singleton true)))=none ∧
    CategoryTreesV25.observer functions
      ((forget outputNext).tree (.seq (.empty (singleton false)) (.empty (singleton true))))=
        some (BundledCategoryV19.identity functions Unit) :=
  RawTransportV26.collapsed_empty_witness (forget outputNext) _ _ singleton_distinct same_carrier
theorem tagged_revival :
    CategoryTreesV25.observer (tagged outputNext)
      ((taggedForget outputNext).tree (.seq (.empty (singleton false)) (.empty (singleton true))))=none := by
  rw [tagged_raw_transport outputNext]
  rw [forgotten_empty_loss.1]
  rfl
def dead : LTS Unit Unit := fun _ _ _ => False
def loop : LTS Unit Unit := fun _ _ _ => True
theorem forward_not_back : Forward dead loop id ∧ ¬Back dead loop id := by
  constructor
  · intro s a t h; exact False.elim h
  · intro h; obtain ⟨t,ht,_⟩ := h () () () trivial; exact ht
theorem no_dead_hom : ¬HomEquation dead loop id := by
  intro h; exact forward_not_back.2 ((hom_iff _ _ _).mp h).2
end CoalgebraControlsV27
