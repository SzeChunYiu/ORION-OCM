import RestrictedV26
namespace ResourceCategoryV26
open CategoryAdaptersV26 ProcessMapsV26
universe u v
variable {O : Type u} (C : TypedPathsV11.Category.{u,v} O)
    (cost : {a b : O} → C.Hom a b → Nat)
    (id0 : ∀ a, cost (C.id a) = 0)
    (add : ∀ {a b c} (f : C.Hom a b) (g : C.Hom b c), cost (C.comp f g) = cost f + cost g)
def category : TypedPathsV11.Category (O × Nat) :=
  fromProc (FoundationV5.resourceCategory (toProc C) cost id0 add)
def projection : ProcessMap (category C cost id0 add) C where
  obj := Prod.fst
  hom := Subtype.val
  id_law _ := rfl
  comp_law _ _ := rfl
theorem hom_binding (x y : O × Nat) :
    (category C cost id0 add).Hom x y = {f : C.Hom x.1 y.1 // x.2 = cost f + y.2} := rfl
theorem id_binding (x : O × Nat) :
    ((category C cost id0 add).id x).val = C.id x.1 := rfl
theorem comp_binding {x y z : O × Nat}
    (f : (category C cost id0 add).Hom x y) (g : (category C cost id0 add).Hom y z) :
    ((category C cost id0 add).comp f g).val = C.comp f.val g.val := rfl
theorem projection_object (x : O × Nat) : (projection C cost id0 add).obj x = x.1 := rfl
theorem projection_arrow {x y : O × Nat} (f : (category C cost id0 add).Hom x y) :
    (projection C cost id0 add).hom f = f.val := rfl
theorem arrow_lift_iff {a b : O} (f : C.Hom a b) (r : Nat) :
    (∃ s, ∃ g : (category C cost id0 add).Hom (a,r) (b,s), g.val = f) ↔ cost f ≤ r := by
  constructor
  · rintro ⟨s,g,hg⟩
    have h := g.property
    rw [hg] at h
    dsimp at h
    omega
  · intro h
    exact ⟨r-cost f,⟨f,by dsimp; omega⟩,rfl⟩
theorem arrow_residual {a b : O} {r s : Nat}
    (g : (category C cost id0 add).Hom (a,r) (b,s)) : s = r-cost g.val := by
  have h := g.property
  dsimp at h
  omega
def pathCost {a b : O} : TypedPathsV11.Path C.Hom a b → Nat
  | .nil _ => 0
  | .cons f p => cost f + pathCost p
theorem cost_nil (a : O) : pathCost C cost (.nil a) = 0 := rfl
theorem cost_cons {a b c : O} (f : C.Hom a b) (p : TypedPathsV11.Path C.Hom b c) :
    pathCost C cost (.cons f p) = cost f + pathCost C cost p := rfl
include id0 add in
theorem cost_eval {a b : O} (p : TypedPathsV11.Path C.Hom a b) :
    cost (TypedPathsV11.eval C id (fun f => f) p) = pathCost C cost p := by
  induction p with
  | nil a => exact id0 a
  | cons f p ih => simp only [TypedPathsV11.eval,add,pathCost,ih]
theorem successful_tree (t : BracketV25.Tree (O × Nat) (BundledCategoryV19.Arrow (category C cost id0 add)))
    (z : BundledCategoryV19.Arrow (category C cost id0 add))
    (h : CategoryTreesV25.observer (category C cost id0 add) t = some z) :
    CategoryTreesV25.observer C ((projection C cost id0 add).tree t) =
      some ((projection C cost id0 add).bundle z) :=
  RawTransportV26.success _ t z h
end ResourceCategoryV26
