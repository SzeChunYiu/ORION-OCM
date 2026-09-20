import PermissionIncidenceV22
namespace PermissionMinimalityV22
open PermissionSetsV22 PermissionIncidenceV22
universe u v
variable {H : Type u} {Q : Type v}
theorem minimal_blocker (W : H→Prop) (R : H→Family Q) (S B : Family Q) :
    Minimal (Blocks W R S) B ↔ Blocks W R S B ∧ Private W R S B := by
  classical
  constructor
  · rintro ⟨hb,hm⟩
    refine ⟨hb,?_⟩
    intro b hBb
    let C := diff B (single b)
    have hCB : Sub C B := fun _ h => h.1
    have hnb : ¬Blocks W R S C := by
      intro hc
      have he := hm C hCB hc
      have hCb : C b := he ▸ hBb
      exact hCb.2 rfl
    have hc : Cap W R (diff S C) := Classical.byContradiction hnb
    obtain ⟨h,hw,hs⟩ := hc
    have hRS : Sub (R h) S := fun q hq => (hs q hq).1
    obtain ⟨q,hq,hBq⟩ := (blocks_iff_hits W R S B).mp hb h hw hRS
    have hqb : q=b := by
      apply Classical.byContradiction
      intro hn
      exact (hs q hq).2 ⟨hBq,hn⟩
    subst q
    refine ⟨h,hw,hRS,?_⟩
    intro q
    constructor
    · rintro ⟨hr,hB⟩
      apply Classical.byContradiction
      intro hn
      exact (hs q hr).2 ⟨hB,hn⟩
    · intro he; subst q; exact ⟨hq,hBq⟩
  · rintro ⟨hb,hp⟩
    refine ⟨hb,?_⟩
    intro C hCB hc
    apply sub_antisymm hCB
    intro b hBb
    obtain ⟨h,hw,hs,hprivate⟩ := hp b hBb
    obtain ⟨q,hq,hCq⟩ := (blocks_iff_hits W R S C).mp hc h hw hs
    have he := (hprivate q).mp ⟨hq,hCB q hCq⟩
    exact he ▸ hCq
theorem private_empty (W : H→Prop) (R : H→Family Q) (S : Family Q) :
    Private W R S empty := by intro b hb; exact False.elim hb
theorem minimal_empty_blocker (W : H→Prop) (R : H→Family Q) (S : Family Q) :
    Minimal (Blocks W R S) empty ↔ Blocks W R S empty := by
  rw [minimal_blocker]
  exact ⟨And.left,fun h => ⟨h,private_empty W R S⟩⟩
def DeficitFamily (W : H→Prop) (R : H→Family Q) (U S0 D : Family Q) :=
  ∃h, W h ∧ Sub (R h) U ∧ D=diff (R h) S0
def Enabling (W : H→Prop) (R : H→Family Q) (U S0 D : Family Q) :=
  Sub D (diff U S0) ∧ Cap W R (union S0 D)
theorem deficit_admissible (W : H→Prop) (R : H→Family Q) (U S0 D : Family Q)
    (h : DeficitFamily W R U S0 D) : Sub D (diff U S0) := by
  obtain ⟨w,_,hu,rfl⟩ := h
  exact fun q hq => ⟨hu q hq.1,hq.2⟩
theorem enabling_deficits (W : H→Prop) (R : H→Family Q) (U S0 D : Family Q)
    (hS : Sub S0 U) (hD : Sub D (diff U S0)) :
    Cap W R (union S0 D) ↔ Upper (DeficitFamily W R U S0) D := by
  constructor
  · rintro ⟨h,hw,hr⟩
    have hu : Sub (R h) U := by
      intro q hq
      rcases hr q hq with hs|hd
      · exact hS q hs
      · exact (hD q hd).1
    exact ⟨diff (R h) S0,⟨h,hw,hu,rfl⟩,(diff_sub_union _ _ _).mpr hr⟩
  · rintro ⟨B,⟨h,hw,_,he⟩,hB⟩
    subst B
    exact ⟨h,hw,(diff_sub_union _ _ _).mp hB⟩
theorem minimal_enabling (W : H→Prop) (R : H→Family Q) (U S0 D : Family Q)
    (hS : Sub S0 U) :
    Minimal (Enabling W R U S0) D ↔ Minimal (DeficitFamily W R U S0) D := by
  have upper_enable : ∀B, Sub B (diff U S0) →
      (Enabling W R U S0 B ↔ Upper (DeficitFamily W R U S0) B) := by
    intro B hB
    exact ⟨fun h => (enabling_deficits W R U S0 B hS hB).mp h.2,
      fun h => ⟨hB,(enabling_deficits W R U S0 B hS hB).mpr h⟩⟩
  constructor
  · rintro ⟨hD,hm⟩
    apply (minimal_upper _ D).mp
    refine ⟨(upper_enable D hD.1).mp hD,?_⟩
    intro C hCD hC
    have hc := sub_trans hCD hD.1
    exact hm C hCD ((upper_enable C hc).mpr hC)
  · intro hD
    have hd := deficit_admissible W R U S0 D hD.1
    obtain ⟨hu,hm⟩ := (minimal_upper _ D).mpr hD
    refine ⟨(upper_enable D hd).mpr hu,?_⟩
    intro C hCD hC
    exact hm C hCD ((upper_enable C hC.1).mp hC)
end PermissionMinimalityV22
