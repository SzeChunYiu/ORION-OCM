import PermissionSetsV22
namespace PermissionIncidenceV22
open PermissionSetsV22
universe u v
variable {H : Type u} {Q : Type v}
def Cap (W : H→Prop) (R : H→Family Q) (S : Family Q) :=
  ∃h, W h ∧ Sub (R h) S
def Blocks (W : H→Prop) (R : H→Family Q) (S B : Family Q) :=
  ¬Cap W R (diff S B)
def Hits (W : H→Prop) (R : H→Family Q) (S B : Family Q) :=
  ∀h, W h → Sub (R h) S → ∃q, R h q ∧ B q
def Private (W : H→Prop) (R : H→Family Q) (S B : Family Q) :=
  ∀b, B b → ∃h, W h ∧ Sub (R h) S ∧ ∀q, (R h q ∧ B q) ↔ q=b
theorem cap_mono (W : H→Prop) (R : H→Family Q) (S T : Family Q)
    (h : Sub S T) : Cap W R S → Cap W R T := by
  rintro ⟨w,hw,hr⟩
  exact ⟨w,hw,sub_trans hr h⟩
theorem blocks_iff_hits (W : H→Prop) (R : H→Family Q) (S B : Family Q) :
    Blocks W R S B ↔ Hits W R S B := by
  classical
  constructor
  · intro hb h hw hs
    apply Classical.byContradiction
    intro hn
    apply hb
    refine ⟨h,hw,fun q hq => ⟨hs q hq,?_⟩⟩
    intro hB
    exact hn ⟨q,hq,hB⟩
  · intro hh hc
    obtain ⟨h,hw,hs⟩ := hc
    obtain ⟨q,hq,hB⟩ := hh h hw (fun q hq => (hs q hq).1)
    exact (hs q hq).2 hB
theorem blocks_mono (W : H→Prop) (R : H→Family Q) (S B C : Family Q)
    (h : Sub B C) : Blocks W R S B → Blocks W R S C := by
  intro hb
  apply (blocks_iff_hits W R S C).mpr
  intro w hw hs
  obtain ⟨q,hq,hbq⟩ := (blocks_iff_hits W R S B).mp hb w hw hs
  exact ⟨q,hq,h q hbq⟩
theorem empty_family (R : H→Family Q) (S : Family Q) :
    ¬Cap (fun _ => False) R S := by rintro ⟨h,hh,_⟩; exact hh
theorem empty_support (W : H→Prop) (R : H→Family Q) (h : H)
    (hw : W h) (hr : R h=empty) (S : Family Q) : Cap W R S := by
  refine ⟨h,hw,?_⟩
  rw [hr]
  exact fun _ hh => False.elim hh
theorem available_restrict (W : H→Prop) (R : H→Family Q) (U S : Family Q)
    (h : Sub S U) :
    Cap (fun x => W x ∧ Sub (R x) U) R S ↔ Cap W R S := by
  constructor
  · rintro ⟨x,hx,hs⟩; exact ⟨x,hx.1,hs⟩
  · rintro ⟨x,hx,hs⟩; exact ⟨x,⟨hx,sub_trans hs h⟩,hs⟩
def Upper (F : Family Q→Prop) (D : Family Q) := ∃B, F B ∧ Sub B D
theorem minimal_upper (F : Family Q→Prop) (D : Family Q) :
    Minimal (Upper F) D ↔ Minimal F D := by
  constructor
  · rintro ⟨⟨B,hB,hBD⟩,hm⟩
    have he := hm B hBD ⟨B,hB,sub_refl B⟩
    subst B
    exact ⟨hB,fun C hC hF => hm C hC ⟨C,hF,sub_refl C⟩⟩
  · rintro ⟨hD,hm⟩
    refine ⟨⟨D,hD,sub_refl D⟩,?_⟩
    rintro C hCD ⟨B,hB,hBC⟩
    have he := hm B (sub_trans hBC hCD) hB
    subst B
    exact sub_antisymm hCD hBC
theorem cofinal_supports (W V : H→Prop) (R : H→Family Q)
    (hsub : ∀h,V h→W h)
    (hcover : ∀h,W h→∃g,V g∧Sub (R g) (R h)) (S : Family Q) :
    Cap W R S ↔ Cap V R S := by
  constructor
  · rintro ⟨h,hw,hs⟩
    obtain ⟨g,hg,hgh⟩ := hcover h hw
    exact ⟨g,hg,sub_trans hgh hs⟩
  · rintro ⟨h,hv,hs⟩; exact ⟨h,hsub h hv,hs⟩
end PermissionIncidenceV22
