import PermissionIncidenceV22
namespace HistoryPermissionsV22
open PermissionSetsV22 PermissionIncidenceV22
universe u
variable {H : Type u}
noncomputable def historyRequirements (B : H→Prop) (h : H) : Family H := by
  classical
  exact if B h then empty else single h
theorem history_admission (B D : H→Prop) (h : H) :
    Sub (historyRequirements B h) D ↔ B h ∨ D h := by
  classical
  by_cases hb : B h
  · simp [historyRequirements,hb,PermissionSetsV22.Sub,empty]
  · simp only [historyRequirements,if_neg hb,hb,false_or]
    constructor
    · intro hs; exact hs h rfl
    · intro hd q hq; exact hq ▸ hd
theorem history_capability (W B D : H→Prop) :
    Cap W (historyRequirements B) D ↔ ∃h,W h ∧ (B h ∨ D h) := by
  constructor
  · rintro ⟨h,hw,hs⟩; exact ⟨h,hw,(history_admission B D h).mp hs⟩
  · rintro ⟨h,hw,hs⟩; exact ⟨h,hw,(history_admission B D h).mpr hs⟩
theorem one_history_relief (W B : H→Prop) (h : H)
    (impossible : ¬∃g,W g∧B g) :
    Cap W (historyRequirements B) (single h) ↔ W h := by
  rw [history_capability]
  constructor
  · rintro ⟨g,hw,hb|hd⟩
    · exact False.elim (impossible ⟨g,hw,hb⟩)
    · exact hd ▸ hw
  · intro hw; exact ⟨h,hw,Or.inr rfl⟩
end HistoryPermissionsV22
