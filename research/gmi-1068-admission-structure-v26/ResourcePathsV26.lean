import ResourceCategoryV26
namespace ResourcePathsV26
open ResourceCategoryV26 TypedPathsV11
universe u v
variable {O : Type u} (C : Category.{u,v} O)
    (cost : {a b : O} → C.Hom a b → Nat)
    (id0 : ∀ a, cost (C.id a) = 0)
    (add : ∀ {a b c} (f : C.Hom a b) (g : C.Hom b c), cost (C.comp f g) = cost f + cost g)
theorem balance {x y : O × Nat}
    (q : Path (category C cost id0 add).Hom x y) :
    x.2 = pathCost C cost ((projection C cost id0 add).path q) + y.2 := by
  induction q with
  | nil x => exact (Nat.zero_add x.2).symm
  | @cons x y z f q ih =>
    change x.2 = cost f.val + pathCost C cost ((projection C cost id0 add).path q) + z.2
    have hf := f.property
    dsimp at hf
    omega
theorem lift {a b : O} (p : Path C.Hom a b) (r : Nat) (h : pathCost C cost p ≤ r) :
    ∃ s, ∃ q : Path (category C cost id0 add).Hom (a,r) (b,s),
      (projection C cost id0 add).path q = p := by
  induction p generalizing r with
  | nil a => exact ⟨r,.nil (a,r),rfl⟩
  | @cons a b c f p ih =>
    have htail : pathCost C cost p ≤ r-cost f := by
      change cost f + pathCost C cost p ≤ r at h
      omega
    obtain ⟨s,q,hq⟩ := ih (r-cost f) htail
    have hf : r = cost f + (r-cost f) := by
      change cost f + pathCost C cost p ≤ r at h
      omega
    refine ⟨s,.cons (⟨f,hf⟩ : (category C cost id0 add).Hom (a,r) (b,r-cost f)) q,?_⟩
    change Path.cons f ((projection C cost id0 add).path q) = Path.cons f p
    rw [hq]
theorem lift_iff {a b : O} (p : Path C.Hom a b) (r : Nat) :
    (∃ s, ∃ q : Path (category C cost id0 add).Hom (a,r) (b,s),
      (projection C cost id0 add).path q = p) ↔ pathCost C cost p ≤ r := by
  constructor
  · rintro ⟨s,q,hq⟩
    have h := balance C cost id0 add q
    rw [hq] at h
    dsimp at h
    omega
  · exact lift C cost id0 add p r
theorem residual {a b : O} {r s : Nat} (p : Path C.Hom a b)
    (q : Path (category C cost id0 add).Hom (a,r) (b,s))
    (h : (projection C cost id0 add).path q = p) :
    s = r-pathCost C cost p := by
  have hb := balance C cost id0 add q
  rw [h] at hb
  dsimp at hb
  omega
theorem exact_lift {a b : O} (p : Path C.Hom a b) (r : Nat)
    (h : pathCost C cost p ≤ r) :
    ∃ q : Path (category C cost id0 add).Hom (a,r) (b,r-pathCost C cost p),
      (projection C cost id0 add).path q = p := by
  obtain ⟨s,q,hq⟩ := lift C cost id0 add p r h
  have hs := residual C cost id0 add p q hq
  subst s
  exact ⟨q,hq⟩
end ResourcePathsV26
