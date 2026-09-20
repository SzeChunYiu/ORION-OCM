import PermissionMinimalityV22
import FrontierOrderV20
namespace FinitePermissionsV22
open PartialContextV15 FrontierOrderV20 PermissionSetsV22 PermissionIncidenceV22
open PermissionMinimalityV22
universe u v
variable {Q : Type u}
def choices : List Q → List (Family Q)
  | [] => [empty]
  | a::as => choices as ++ (choices as).map (union (single a))
def members (L : List Q) : Family Q := fun q => q∈L
theorem choices_sound (L : List Q) (R : Family Q) (h : R∈choices L) :
    Sub R (members L) := by
  induction L generalizing R with
  | nil =>
    simp only [choices,List.mem_singleton] at h
    subst R
    exact fun _ h => False.elim h
  | cons a as ih =>
    simp only [choices,List.mem_append,List.mem_map] at h
    rcases h with h|⟨T,hT,rfl⟩
    · exact fun q hq => List.mem_cons_of_mem a (ih R h q hq)
    · intro q hq
      rcases hq with hqa|hTq
      · exact List.mem_cons.mpr (Or.inl hqa)
      · exact List.mem_cons_of_mem a (ih T hT q hTq)
theorem choices_complete (L : List Q) (R : Family Q) (h : Sub R (members L)) :
    R∈choices L := by
  classical
  induction L generalizing R with
  | nil =>
    have he : R=empty := by
      apply sub_antisymm
      · intro q hq; exact List.not_mem_nil (h q hq)
      · intro _ hq; exact False.elim hq
    simp [he,choices]
  | cons a as ih =>
    by_cases ha : R a
    · let T := diff R (single a)
      have ht : Sub T (members as) := by
        intro q hq
        rcases List.mem_cons.mp (h q hq.1) with hqa|hqas
        · exact False.elim (hq.2 hqa)
        · exact hqas
      have hi := ih T ht
      have he : union (single a) T=R := by
        apply sub_antisymm
        · intro q hq
          rcases hq with hqa|hTq
          · exact hqa ▸ ha
          · exact hTq.1
        · intro q hq
          by_cases hqa : q=a
          · exact Or.inl hqa
          · exact Or.inr ⟨hq,hqa⟩
      exact List.mem_append.mpr (Or.inr (List.mem_map.mpr ⟨T,hi,he⟩))
    · have ht : Sub R (members as) := by
        intro q hq
        rcases List.mem_cons.mp (h q hq) with hqa|hqas
        · exact False.elim (ha (hqa ▸ hq))
        · exact hqas
      exact List.mem_append.mpr (Or.inl (ih R ht))
def reverseInclusion : PreorderSpec (Family Q) where
  le R S := Sub S R
  refl := sub_refl
  trans h g := sub_trans g h
noncomputable def candidates (L : List Q) (F : Family Q→Prop) : List (Family Q) := by
  classical
  exact (choices L).filter fun R => decide (F R)
noncomputable def minimalMembers (L : List Q) (F : Family Q→Prop) : List (Family Q) := by
  classical
  exact frontier reverseInclusion (candidates L F)
theorem candidates_mem (L : List Q) (F : Family Q→Prop) (R : Family Q) :
    R∈candidates L F ↔ Sub R (members L) ∧ F R := by
  simp only [candidates,List.mem_filter,decide_eq_true_eq]
  exact ⟨fun h => ⟨choices_sound L R h.1,h.2⟩,
    fun h => ⟨choices_complete L R h.1,h.2⟩⟩
theorem minimal_membership (L : List Q) (F : Family Q→Prop) (R : Family Q) :
    R∈minimalMembers L F ↔ Sub R (members L) ∧ Minimal F R := by
  classical
  rw [minimalMembers,frontier_mem]
  constructor
  · rintro ⟨hr,hm⟩
    obtain ⟨hRL,hF⟩ := (candidates_mem L F R).mp hr
    refine ⟨hRL,hF,?_⟩
    intro C hCR hFC
    have hc := (candidates_mem L F C).mpr ⟨sub_trans hCR hRL,hFC⟩
    exact sub_antisymm hCR (hm C hc hCR)
  · rintro ⟨hRL,hF,hm⟩
    refine ⟨(candidates_mem L F R).mpr ⟨hRL,hF⟩,?_⟩
    intro C hC hCR
    have he := hm C hCR ((candidates_mem L F C).mp hC).2
    exact fun q hq => he ▸ hq
theorem minimal_below (L : List Q) (F : Family Q→Prop) (B : Family Q)
    (hBL : Sub B (members L)) (hF : F B) :
    ∃C, Sub C B ∧ Minimal F C := by
  classical
  have hb := (candidates_mem L F B).mpr ⟨hBL,hF⟩
  obtain ⟨C,hC,hCB⟩ := (frontier_cofinal reverseInclusion (candidates L F)).2 B hb
  exact ⟨C,hCB,((minimal_membership L F C).mp hC).2⟩
theorem finite_enabler {H : Type v} (W : H→Prop) (R : H→Family Q)
    (L : List Q) (U S0 D : Family Q)
    (hDL : Sub D (members L)) (hD : Enabling W R U S0 D) :
    ∃C, Sub C D ∧ Minimal (Enabling W R U S0) C :=
  minimal_below L _ D hDL hD
theorem finite_blocker {H : Type v} (W : H→Prop) (R : H→Family Q)
    (L : List Q) (S B : Family Q)
    (hBL : Sub B (members L)) (hB : Blocks W R S B) :
    ∃C, Sub C B ∧ Minimal (Blocks W R S) C :=
  minimal_below L _ B hBL hB
end FinitePermissionsV22
