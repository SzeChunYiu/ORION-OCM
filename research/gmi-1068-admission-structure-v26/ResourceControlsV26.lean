import ResourcePathsV26
namespace ResourceControlsV26
open CategoryAdaptersV26 ResourceCategoryV26 TypedPathsV11 BundledCategoryV19
abbrev base := fromProc FoundationV5.natProcess
def cost : {a b : Unit} → base.Hom a b → Nat := fun f => f
theorem cost_id (a : Unit) : cost (base.id a) = 0 := rfl
theorem cost_comp {a b c : Unit} (f : base.Hom a b) (g : base.Hom b c) :
    cost (base.comp f g) = cost f + cost g := rfl
abbrev lifted := category base cost cost_id cost_comp
abbrev forget := projection base cost cost_id cost_comp
def first : lifted.Hom ((),1) ((),0) := ⟨(1 : Nat),rfl⟩
def restarting : lifted.Hom ((),1) ((),0) := ⟨(1 : Nat),rfl⟩
theorem bad_join :
    mul lifted (⟨((),1),((),0),first⟩ : Arrow lifted)
      ⟨((),1),((),0),restarting⟩ = none := by
  apply not_aligned
  decide
theorem forgotten_join :
    mul base (forget.bundle (⟨((),1),((),0),first⟩ : Arrow lifted))
      (forget.bundle ⟨((),1),((),0),restarting⟩) = some ⟨(),(),(2 : Nat)⟩ := by
  exact aligned base (a:=()) (b:=()) (c:=()) (1 : Nat) (1 : Nat)
def twoSteps : Path base.Hom () () := .cons (b:=()) (1 : Nat) (.cons (b:=()) (1 : Nat) (.nil ()))
theorem two_cost : pathCost base cost twoSteps = 2 := rfl
def revived : Path lifted.Hom ((),2) ((),0) :=
  .cons (⟨(1 : Nat),rfl⟩ : lifted.Hom ((),2) ((),1))
    (.cons (⟨(1 : Nat),rfl⟩ : lifted.Hom ((),1) ((),0)) (.nil ((),0)))
theorem revival_projects : forget.path revived = twoSteps := rfl
theorem balance_one_fails :
    ¬ ∃ s, ∃ q : Path lifted.Hom ((),1) ((),s), forget.path q = twoSteps := by
  rw [ResourcePathsV26.lift_iff base cost cost_id cost_comp]
  decide
theorem balance_two_succeeds :
    ∃ q : Path lifted.Hom ((),2) ((),0), forget.path q = twoSteps :=
  ⟨revived,revival_projects⟩
end ResourceControlsV26
