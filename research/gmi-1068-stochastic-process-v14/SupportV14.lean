import MatricesV14
import RelationsV14
namespace StochasticV14
universe u
variable {α : Type u} [Weight α]
namespace Kernel
def support {n m : Nat} (p : Kernel α n m) : TotalRel (Fin n) (Fin m) where
  relates i j := p.value i j≠0
  total i := (sum_support (p.value i)).mp (by
    rw [p.normalized i]
    exact Weight.one_ne_zero)
theorem support_comp {n m k : Nat} (p : Kernel α n m) (q : Kernel α m k) :
    support (comp p q)=TotalRel.comp (support p) (support q) := by
  apply TotalRel.ext
  intro i z
  change (sum (fun j => p.value i j*q.value j z)≠0) ↔
    ∃ j, p.value i j≠0 ∧ q.value j z≠0
  rw [sum_support]
  constructor
  · rintro ⟨j,hj⟩
    exact ⟨j,(mul_support _ _).mp hj⟩
  · rintro ⟨j,hj⟩
    exact ⟨j,(mul_support _ _).mpr hj⟩
theorem support_embed {n m : Nat} (f : Fin n → Fin m) :
    support (embed (α:=α) f)=TotalRel.graph f := by
  apply TotalRel.ext
  intro i j
  change (if j=f i then (1:α) else 0)≠0 ↔ j=f i
  by_cases h : j=f i <;> simp [h,Weight.one_ne_zero]
theorem support_ident (n : Nat) :
    support (ident (α:=α) n)=TotalRel.ident (Fin n) := support_embed id
end Kernel
end StochasticV14
