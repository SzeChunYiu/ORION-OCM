import CategoryAdaptersV26
namespace ProcessMapsV26
open TypedPathsV11 BundledCategoryV19 BracketV25
universe u v w x
structure ProcessMap {O : Type u} {P : Type w}
    (C : Category.{u,v} O) (D : Category.{w,x} P) where
  obj : O → P
  hom : {a b : O} → C.Hom a b → D.Hom (obj a) (obj b)
  id_law : ∀ a, hom (C.id a) = D.id (obj a)
  comp_law : ∀ {a b c} (f : C.Hom a b) (g : C.Hom b c),
    hom (C.comp f g) = D.comp (hom f) (hom g)
namespace ProcessMap
variable {O : Type u} {P : Type w} {C : Category.{u,v} O} {D : Category.{w,x} P}
def bundle (F : ProcessMap C D) : Arrow C → Arrow D
  | ⟨a,b,f⟩ => ⟨F.obj a,F.obj b,F.hom f⟩
def tree (F : ProcessMap C D) := Tree.map F.obj F.bundle
def ObjectInjective (F : ProcessMap C D) := ∀ a b, F.obj a = F.obj b → a = b
def Faithful (F : ProcessMap C D) :=
  ∀ {a b} (f g : C.Hom a b), F.hom f = F.hom g → f = g
theorem bundle_identity (F : ProcessMap C D) (a : O) :
    F.bundle (identity C a) = identity D (F.obj a) := by
  simp [bundle,identity,F.id_law]
theorem product_success (F : ProcessMap C D) (x y z : Arrow C)
    (h : mul C x y = some z) : mul D (F.bundle x) (F.bundle y) = some (F.bundle z) := by
  have hd := (defined_iff C x y).mp ⟨z,h⟩
  rcases x with ⟨a,b,f⟩
  rcases y with ⟨c,d,g⟩
  dsimp at hd
  subst c
  rw [aligned] at h
  cases h
  simp [bundle,aligned,F.comp_law]
theorem product_commutes (F : ProcessMap C D) (hi : F.ObjectInjective)
    (x y : Arrow C) :
    mul D (F.bundle x) (F.bundle y) = (mul C x y).map F.bundle := by
  rcases x with ⟨a,b,f⟩
  rcases y with ⟨c,d,g⟩
  by_cases h : b = c
  · subst c
    simp [bundle,aligned,F.comp_law]
  · have hh : F.obj b ≠ F.obj c := fun e => h (hi b c e)
    simp [bundle,mul,h,hh]
theorem bundle_injective (F : ProcessMap C D) (hi : F.ObjectInjective)
    (hf : F.Faithful) (x y : Arrow C) (h : F.bundle x = F.bundle y) : x = y := by
  rcases x with ⟨a,b,f⟩
  rcases y with ⟨c,d,g⟩
  have ha := hi a c (congrArg Sigma.fst h)
  have hb := hi b d (congrArg (fun t => t.2.1) h)
  subst c
  subst d
  have h1 := eq_of_heq (Sigma.mk.inj h).2
  have h2 := eq_of_heq (Sigma.mk.inj h1).2
  have hh := hf f g h2
  cases hh
  rfl
def path (F : ProcessMap C D) {a b : O} : Path C.Hom a b → Path D.Hom (F.obj a) (F.obj b)
  | .nil a => .nil (F.obj a)
  | .cons f p => .cons (F.hom f) (F.path p)
theorem path_nil (F : ProcessMap C D) (a : O) :
    F.path (.nil a) = .nil (F.obj a) := rfl
theorem path_cons (F : ProcessMap C D) {a b c : O} (f : C.Hom a b) (p : Path C.Hom b c) :
    F.path (.cons f p) = .cons (F.hom f) (F.path p) := rfl
theorem path_append (F : ProcessMap C D) {a b c : O} (p : Path C.Hom a b) (q : Path C.Hom b c) :
    F.path (p.append q) = (F.path p).append (F.path q) := by
  induction p with
  | nil => rfl
  | cons f p ih => simp only [Path.append,path,ih]
theorem path_eval (F : ProcessMap C D) {a b : O} (p : Path C.Hom a b) :
    TypedPathsV11.eval D id (fun f => f) (F.path p) = F.hom (TypedPathsV11.eval C id (fun f => f) p) := by
  induction p with
  | nil a => exact (F.id_law a).symm
  | cons f p ih => simp only [path,TypedPathsV11.eval,ih,F.comp_law]
theorem path_tree (F : ProcessMap C D) {a b : O} (p : Path C.Hom a b) :
    CategoryTreesV25.pathTree D (F.path p) = F.tree (CategoryTreesV25.pathTree C p) := by
  induction p with
  | nil => rfl
  | cons f p ih => simp only [path,CategoryTreesV25.pathTree,tree,Tree.map,bundle] at *; rw [ih]
end ProcessMap
end ProcessMapsV26
