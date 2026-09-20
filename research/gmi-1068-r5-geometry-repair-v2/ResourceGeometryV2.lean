/- R5 successor: actual witness-based implications, with natural costs.
   Not a formalization of the real-infimum or infinite-Pareto prose extensions. -/
namespace ResourceGeometryV2

universe u v
variable {Obj : Type u} (Hom : Obj → Obj → Type v)
variable (cost : {a b : Obj} → Hom a b → Nat)

def IsMinimum {a b : Obj} (f : Hom a b) : Prop :=
  ∀ g : Hom a b, cost f ≤ cost g

theorem minimum_identity {a : Obj}
    (id : Hom a a) (zero : cost id = 0)
    (f : Hom a a) (minimum : IsMinimum Hom cost f) :
    cost f = 0 := by
  have bound : cost f ≤ cost id := minimum id
  rw [zero] at bound
  exact Nat.le_zero.mp bound

theorem minimum_triangle
    (comp : {a b c : Obj} → Hom a b → Hom b c → Hom a c)
    (subadd : ∀ {a b c : Obj} (f : Hom a b) (g : Hom b c),
      cost (comp f g) ≤ cost f + cost g)
    {a b c : Obj} (f : Hom a b) (g : Hom b c) (h : Hom a c)
    (minimum : IsMinimum Hom cost h) :
    cost h ≤ cost f + cost g := by
  exact Nat.le_trans (minimum (comp f g)) (subadd f g)

-- Replacing f,g by their minimizing witnesses specializes to d(a,c)≤d(a,b)+d(b,c).
-- The conclusion is absent from all hypotheses.

def Minimal {X : Type u} (le : X → X → Prop) (p : X) : Prop :=
  ∀ q, le q p → le p q

theorem minimal_transport
    {X : Type u} {Y : Type v}
    (leX : X → X → Prop) (leY : Y → Y → Prop)
    (f : X → Y) (g : Y → X)
    (rightInverse : ∀ y, f (g y) = y)
    (orderIff : ∀ x z, leY (f x) (f z) ↔ leX x z)
    (p : X) : Minimal leX p ↔ Minimal leY (f p) := by
  constructor
  · intro hp y hyp
    have hqp : leX (g y) p := by
      apply (orderIff (g y) p).mp
      simpa only [rightInverse] using hyp
    have hpq := hp (g y) hqp
    have image := (orderIff p (g y)).mpr hpq
    simpa only [rightInverse] using image
  · intro hp q hqp
    exact (orderIff p q).mp (hp (f q) ((orderIff q p).mpr hqp))

#print axioms minimum_identity
#print axioms minimum_triangle
#print axioms minimal_transport
end ResourceGeometryV2
