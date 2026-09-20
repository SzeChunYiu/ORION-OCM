import FrontierOrderV20
namespace GuardedMapsV20
open PartialContextV15 FrontierOrderV20
universe u v w
def Image {X : Type u} {Y : Type v} (F : X → Option Y) (S : X → Prop) (y : Y) :=
  ∃ x, S x ∧ F x=some y
def Guarded {X : Type u} {Y : Type v} (r : PreorderSpec X) (s : PreorderSpec Y)
    (F : X → Option Y) :=
  ∀ x x', r.le x x' → ∀ y, F x=some y → ∃ y', F x'=some y' ∧ s.le y y'
theorem image_cofinal {X : Type u} {Y : Type v}
    (r : PreorderSpec X) (s : PreorderSpec Y) (F : X → Option Y)
    (hf : Guarded r s F) (C S : X → Prop) (hc : Cofinal r C S) :
    Cofinal s (Image F C) (Image F S) := by
  constructor
  · rintro y ⟨x,hx,hf⟩
    exact ⟨x,hc.1 x hx,hf⟩
  · rintro y ⟨x,hx,hfx⟩
    obtain ⟨x',hx',hxx'⟩ := hc.2 x hx
    obtain ⟨y',hfy',hyy'⟩ := hf x x' hxx' y hfx
    exact ⟨y',⟨x',hx',hfy'⟩,hyy'⟩
theorem image_down {X : Type u} {Y : Type v}
    (r : PreorderSpec X) (s : PreorderSpec Y) (F : X → Option Y)
    (hf : Guarded r s F) (C S : X → Prop) (hc : Cofinal r C S) :
    ∀ y, Down s (Image F C) y ↔ Down s (Image F S) y :=
  cofinal_down s _ _ (image_cofinal r s F hf C S hc)
def FinitePreserves {X : Type u} {Y : Type v}
    (r : PreorderSpec X) (s : PreorderSpec Y) (F : X → Option Y) :=
  ∀ (xs cs : List X),
    Cofinal r (fun x => x ∈ cs) (fun x => x ∈ xs) →
    ∀ y, Down s (Image F (fun x => x ∈ cs)) y ↔
      Down s (Image F (fun x => x ∈ xs)) y
theorem guarded_iff_finite_preserves {X : Type u} {Y : Type v}
    (r : PreorderSpec X) (s : PreorderSpec Y) (F : X → Option Y) :
    Guarded r s F ↔ FinitePreserves r s F := by
  constructor
  · intro hf xs cs hc
    exact image_down r s F hf _ _ hc
  · intro hp x x' hxx' y hfy
    have hc : Cofinal r (fun z => z ∈ [x']) (fun z => z ∈ [x,x']) := by
      constructor
      · intro z hz
        simp only [List.mem_cons,List.not_mem_nil,or_false] at hz ⊢
        exact Or.inr hz
      · intro z hz
        simp only [List.mem_cons,List.not_mem_nil,or_false] at hz
        refine ⟨x',by simp,?_⟩
        rcases hz with hz | hz
        · subst z; exact hxx'
        · subst z; exact r.refl x'
    have hd : Down s (Image F (fun z => z ∈ [x,x'])) y :=
      ⟨y,⟨x,by simp,hfy⟩,s.refl y⟩
    obtain ⟨y',⟨z,hz,hfz⟩,hyy'⟩ := (hp [x,x'] [x'] hc y).mpr hd
    have he : z=x' := by simpa using hz
    subst z
    exact ⟨y',hfz,hyy'⟩
def compose {X : Type u} {Y : Type v} {Z : Type w}
    (G : Y → Option Z) (F : X → Option Y) (x : X) := (F x).bind G
theorem guarded_compose {X : Type u} {Y : Type v} {Z : Type w}
    (r : PreorderSpec X) (s : PreorderSpec Y) (t : PreorderSpec Z)
    (F : X → Option Y) (G : Y → Option Z)
    (hf : Guarded r s F) (hg : Guarded s t G) :
    Guarded r t (compose G F) := by
  intro x x' hxx' z hz
  cases he : F x with
  | none => simp [compose,he] at hz
  | some y =>
    have hgz : G y=some z := by simpa [compose,he] using hz
    obtain ⟨y',hfy',hyy'⟩ := hf x x' hxx' y he
    obtain ⟨z',hgz',hzz'⟩ := hg y y' hyy' z hgz
    exact ⟨z',by simp [compose,hfy',hgz'],hzz'⟩
def Upward {Y : Type v} (s : PreorderSpec Y) (G : Y → Prop) :=
  ∀ y z, s.le y z → G y → G z
theorem cofinal_goals {Y : Type v} (s : PreorderSpec Y) (C S : Y → Prop)
    (hc : Cofinal s C S) (G : Y → Prop) (hg : Upward s G) :
    (∃ y, C y ∧ G y) ↔ (∃ y, S y ∧ G y) := by
  constructor
  · rintro ⟨y,hy,hgy⟩
    exact ⟨y,hc.1 y hy,hgy⟩
  · rintro ⟨y,hy,hgy⟩
    obtain ⟨z,hz,hyz⟩ := hc.2 y hy
    exact ⟨z,hz,hg y z hyz hgy⟩
theorem down_iff_upward_goals {Y : Type v} (s : PreorderSpec Y)
    (C S : Y → Prop) :
    (∀ y, Down s C y ↔ Down s S y) ↔
    (∀ G, Upward s G → ((∃ y, C y ∧ G y) ↔ (∃ y, S y ∧ G y))) := by
  constructor
  · intro hd G hg
    constructor
    · rintro ⟨y,hy,hgy⟩
      obtain ⟨z,hz,hyz⟩ := (hd y).mp ⟨y,hy,s.refl y⟩
      exact ⟨z,hz,hg y z hyz hgy⟩
    · rintro ⟨y,hy,hgy⟩
      obtain ⟨z,hz,hyz⟩ := (hd y).mpr ⟨y,hy,s.refl y⟩
      exact ⟨z,hz,hg y z hyz hgy⟩
  · intro hg y
    exact hg (fun z => s.le y z) (fun _ _ h1 h2 => s.trans h2 h1)
end GuardedMapsV20
