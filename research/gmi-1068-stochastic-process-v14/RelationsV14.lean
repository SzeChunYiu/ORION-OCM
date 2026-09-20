import Std
namespace StochasticV14
universe u v w x
structure TotalRel (A : Type u) (B : Type v) where
  relates : A → B → Prop
  total : ∀ a, ∃ b, relates a b
namespace TotalRel
@[ext] theorem ext {A : Type u} {B : Type v} {r s : TotalRel A B}
    (h : ∀ a b, r.relates a b ↔ s.relates a b) : r=s := by
  have he : r.relates=s.relates := funext (fun a => funext (fun b => propext (h a b)))
  cases r; cases s; cases he; rfl
def comp {A : Type u} {B : Type v} {C : Type w}
    (r : TotalRel A B) (s : TotalRel B C) : TotalRel A C where
  relates a c := ∃ b, r.relates a b ∧ s.relates b c
  total a := by
    obtain ⟨b,hb⟩ := r.total a
    obtain ⟨c,hc⟩ := s.total b
    exact ⟨c,b,hb,hc⟩
def graph {A : Type u} {B : Type v} (f : A → B) : TotalRel A B :=
  ⟨fun a b => b=f a, fun a => ⟨f a,rfl⟩⟩
def ident (A : Type u) : TotalRel A A := graph id
theorem assoc {A : Type u} {B : Type v} {C : Type w} {D : Type x}
    (r : TotalRel A B) (s : TotalRel B C) (t : TotalRel C D) :
    comp (comp r s) t=comp r (comp s t) := by
  apply ext
  intro a d
  constructor
  · rintro ⟨c,⟨b,hab,hbc⟩,hcd⟩
    exact ⟨b,hab,c,hbc,hcd⟩
  · rintro ⟨b,hab,c,hbc,hcd⟩
    exact ⟨c,⟨b,hab,hbc⟩,hcd⟩
theorem left_id {A : Type u} {B : Type v} (r : TotalRel A B) :
    comp (ident A) r=r := by
  apply ext
  intro a b
  constructor
  · rintro ⟨a',ha,hr⟩
    change a'=a at ha
    exact ha ▸ hr
  · intro h
    exact ⟨a,rfl,h⟩
theorem right_id {A : Type u} {B : Type v} (r : TotalRel A B) :
    comp r (ident B)=r := by
  apply ext
  intro a b
  constructor
  · rintro ⟨b',hr,hb⟩
    change b=b' at hb
    exact hb ▸ hr
  · intro h
    exact ⟨b,h,rfl⟩
theorem graph_comp {A : Type u} {B : Type v} {C : Type w} (f : A → B) (g : B → C) :
    comp (graph f) (graph g)=graph (g ∘ f) := by
  apply ext
  intro a c
  constructor
  · rintro ⟨b,hb,hc⟩
    change b=f a at hb
    change c=g b at hc
    change c=g (f a)
    rw [hb] at hc
    exact hc
  · intro h
    exact ⟨f a,rfl,h⟩
theorem graph_faithful {A : Type u} {B : Type v} {f g : A → B}
    (h : graph f=graph g) : f=g := by
  funext a
  have hh : (graph g).relates a (f a) := h ▸ (show (graph f).relates a (f a) from rfl)
  exact hh
theorem no_into_empty {A : Type u} (a : A) : ¬ Nonempty (TotalRel A Empty) := by
  rintro ⟨r⟩
  obtain ⟨e,_⟩ := r.total a
  exact Empty.elim e
theorem from_empty_unique {B : Type v} (r s : TotalRel Empty B) : r=s :=
  ext (fun e => Empty.elim e)
end TotalRel
end StochasticV14
