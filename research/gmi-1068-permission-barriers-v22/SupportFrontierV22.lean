import FinitePermissionsV22
namespace SupportFrontierV22
open PartialContextV15 FrontierOrderV20 PermissionSetsV22 PermissionIncidenceV22
universe u v
variable {H : Type u} {Q : Type v}
def supportOrder (R : H→Family Q) : PreorderSpec H where
  le a b := Sub (R b) (R a)
  refl h := sub_refl (R h)
  trans h g := sub_trans g h
noncomputable def minimalHistories (R : H→Family Q) (xs : List H) : List H := by
  classical
  exact frontier (supportOrder R) xs
theorem antichain_capability (R : H→Family Q) (xs : List H) (S : Family Q) :
    Cap (fun h => h∈xs) R S ↔ Cap (fun h => h∈minimalHistories R xs) R S := by
  classical
  apply cofinal_supports
  · exact (frontier_cofinal (supportOrder R) xs).1
  · exact (frontier_cofinal (supportOrder R) xs).2
theorem antichain_blockers (R : H→Family Q) (xs : List H) (S B : Family Q) :
    Blocks (fun h => h∈xs) R S B ↔ Blocks (fun h => h∈minimalHistories R xs) R S B :=
  not_congr (antichain_capability R xs (diff S B))
theorem minimal_history_membership (R : H→Family Q) (xs : List H) (h : H) :
    h∈minimalHistories R xs ↔
      h∈xs ∧ ∀g,g∈xs→Sub (R g) (R h)→Sub (R h) (R g) := by
  classical
  exact frontier_mem (supportOrder R) xs h
end SupportFrontierV22
