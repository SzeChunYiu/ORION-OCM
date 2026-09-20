import Std
namespace LTSCoalgebraV27
universe u v w x
abbrev LTS (S : Type u) (A : Type v) := S → A → S → Prop
def successors {S : Type u} {A : Type v} (r : LTS S A) : S → (A×S) → Prop :=
  fun s p => r s p.1 p.2
def relationOf {S : Type u} {A : Type v} (a : S → (A×S) → Prop) : LTS S A :=
  fun s l t => a s (l,t)
theorem relation_successors {S : Type u} {A : Type v} (r : LTS S A) :
    relationOf (successors r)=r := rfl
theorem successors_relation {S : Type u} {A : Type v} (a : S → (A×S) → Prop) :
    successors (relationOf a)=a := rfl
def powerMap {S : Type u} {T : Type w} {A : Type v} (f : S → T)
    (p : (A×S) → Prop) : (A×T) → Prop :=
  fun q => ∃ s, p (q.1,s) ∧ f s=q.2
theorem power_id {S : Type u} {A : Type v} (p : (A×S) → Prop) :
    powerMap id p=p := by
  funext q; apply propext
  constructor
  · rintro ⟨s,h,e⟩; change s=q.2 at e; simpa only [e] using h
  · intro h; exact ⟨q.2,h,rfl⟩
theorem power_comp {S : Type u} {T : Type w} {U : Type x} {A : Type v}
    (f : S → T) (g : T → U) (p : (A×S) → Prop) :
    powerMap (g ∘ f) p=powerMap g (powerMap f p) := by
  funext q; apply propext
  constructor
  · rintro ⟨s,h,e⟩; exact ⟨f s,⟨s,h,rfl⟩,e⟩
  · rintro ⟨t,⟨s,h,e⟩,e'⟩; exact ⟨s,h,by simpa only [Function.comp_apply,e] using e'⟩
def Forward {S : Type u} {T : Type w} {A : Type v}
    (r : LTS S A) (q : LTS T A) (f : S → T) :=
  ∀ s a t, r s a t → q (f s) a (f t)
def Back {S : Type u} {T : Type w} {A : Type v}
    (r : LTS S A) (q : LTS T A) (f : S → T) :=
  ∀ s a t, q (f s) a t → ∃ u, r s a u ∧ f u=t
def HomEquation {S : Type u} {T : Type w} {A : Type v}
    (r : LTS S A) (q : LTS T A) (f : S → T) :=
  ∀ s, powerMap f (successors r s)=successors q (f s)
theorem hom_iff {S : Type u} {T : Type w} {A : Type v}
    (r : LTS S A) (q : LTS T A) (f : S → T) :
    HomEquation r q f ↔ Forward r q f ∧ Back r q f := by
  constructor
  · intro h; constructor
    · intro s a t hr
      have hh : powerMap f (successors r s) (a,f t) := ⟨t,hr,rfl⟩
      rw [h s] at hh
      exact hh
    · intro s a t hq
      have hh : powerMap f (successors r s) (a,t) := (h s).symm ▸ hq
      exact hh
  · rintro ⟨hf,hb⟩ s
    funext p; apply propext
    constructor
    · rintro ⟨t,hr,e⟩
      change q (f s) p.1 p.2
      rw [← e]
      exact hf s p.1 t hr
    · intro hq; exact hb s p.1 p.2 hq
def Bisimulation {S : Type u} {T : Type w} {A : Type v}
    (r : LTS S A) (q : LTS T A) (b : S → T → Prop) :=
  ∀ s t, b s t →
    (∀ a s', r s a s' → ∃ t', q t a t' ∧ b s' t') ∧
    (∀ a t', q t a t' → ∃ s', r s a s' ∧ b s' t')
theorem graph_bisimulation {S : Type u} {T : Type w} {A : Type v}
    (r : LTS S A) (q : LTS T A) (f : S → T) :
    Bisimulation r q (fun s t => f s=t) ↔ HomEquation r q f := by
  rw [hom_iff]
  constructor
  · intro h; constructor
    · intro s a t hr
      obtain ⟨u,hq,he⟩ := (h s (f s) rfl).1 a t hr
      exact he.symm ▸ hq
    · intro s a t hq; exact (h s (f s) rfl).2 a t hq
  · rintro ⟨hf,hb⟩ s t ht
    subst t
    exact ⟨fun a s' h => ⟨f s',hf s a s' h,rfl⟩,hb s⟩
end LTSCoalgebraV27
