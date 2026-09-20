import PartialContextV15
namespace FrontierOrderV20
open PartialContextV15
universe u
def Down {X : Type u} (r : PreorderSpec X) (S : X → Prop) (x : X) :=
  ∃ y, S y ∧ r.le x y
def Cofinal {X : Type u} (r : PreorderSpec X) (C S : X → Prop) :=
  (∀ x, C x → S x) ∧ ∀ x, S x → ∃ y, C y ∧ r.le x y
def Maximal {X : Type u} (r : PreorderSpec X) (S : X → Prop) (x : X) :=
  S x ∧ ∀ y, S y → r.le x y → r.le y x
theorem cofinal_down {X : Type u} (r : PreorderSpec X) (C S : X → Prop)
    (h : Cofinal r C S) : ∀ x, Down r C x ↔ Down r S x := by
  intro x
  constructor
  · rintro ⟨y,hy,hxy⟩
    exact ⟨y,h.1 y hy,hxy⟩
  · rintro ⟨y,hy,hxy⟩
    obtain ⟨z,hz,hyz⟩ := h.2 y hy
    exact ⟨z,hz,r.trans hxy hyz⟩
def extend {X : Type u} (r : PreorderSpec X) [DecidableRel r.le] : X → List X → X
  | x, [] => x
  | x, a::as => extend r (if r.le x a then a else x) as
theorem extend_spec {X : Type u} (r : PreorderSpec X) [DecidableRel r.le]
    (xs : List X) (x : X) :
    r.le x (extend r x xs) ∧
    extend r x xs ∈ x::xs ∧
    ∀ z, z ∈ x::xs → r.le (extend r x xs) z → r.le z (extend r x xs) := by
  induction xs generalizing x with
  | nil =>
    simp only [extend, List.mem_cons, List.not_mem_nil, or_false]
    exact ⟨r.refl x,True.intro,fun z hz _ => hz ▸ r.refl x⟩
  | cons a as ih =>
    by_cases hxa : r.le x a
    · simp only [extend, if_pos hxa]
      obtain ⟨ha,hm,hmax⟩ := ih a
      refine ⟨r.trans hxa ha,?_,?_⟩
      · exact List.mem_cons_of_mem x hm
      · intro z hz hzle
        rcases List.mem_cons.mp hz with hzx | hz
        · subst z
          exact r.trans hxa ha
        · exact hmax z hz hzle
    · simp only [extend, if_neg hxa]
      obtain ⟨hx,hm,hmax⟩ := ih x
      refine ⟨hx,?_,?_⟩
      · rcases List.mem_cons.mp hm with he | ht
        · exact List.mem_cons.mpr (Or.inl he)
        · exact List.mem_cons.mpr (Or.inr (List.mem_cons_of_mem a ht))
      · intro z hz hzle
        rcases List.mem_cons.mp hz with he | ht
        · exact hmax z (List.mem_cons.mpr (Or.inl he)) hzle
        · rcases List.mem_cons.mp ht with he | ht
          · subst z
            exact False.elim (hxa (r.trans hx hzle))
          · exact hmax z (List.mem_cons.mpr (Or.inr ht)) hzle
def frontier {X : Type u} (r : PreorderSpec X) [DecidableRel r.le] (xs : List X) :
    List X :=
  xs.filter (fun x => xs.all (fun y => decide (r.le x y → r.le y x)))
theorem frontier_mem {X : Type u} (r : PreorderSpec X) [DecidableRel r.le]
    (xs : List X) (x : X) :
    x ∈ frontier r xs ↔ Maximal r (fun y => y ∈ xs) x := by
  simp only [frontier, List.mem_filter, List.all_eq_true, decide_eq_true_eq, Maximal]
theorem frontier_cofinal {X : Type u} (r : PreorderSpec X) [DecidableRel r.le]
    (xs : List X) :
    Cofinal r (fun x => x ∈ frontier r xs) (fun x => x ∈ xs) := by
  constructor
  · intro x hx
    exact ((frontier_mem r xs x).mp hx).1
  · intro x hx
    obtain ⟨hle,hm,hmax⟩ := extend_spec r xs x
    have hm' : extend r x xs ∈ xs := by
      rcases List.mem_cons.mp hm with he | ht
      · rw [he]; exact hx
      · exact ht
    exact ⟨extend r x xs,(frontier_mem r xs _).mpr
      ⟨hm',fun z hz => hmax z (List.mem_cons_of_mem x hz)⟩,hle⟩
theorem frontier_down {X : Type u} (r : PreorderSpec X) [DecidableRel r.le]
    (xs : List X) :
    ∀ x, Down r (fun z => z ∈ frontier r xs) x ↔ Down r (fun z => z ∈ xs) x :=
  cofinal_down r _ _ (frontier_cofinal r xs)
theorem frontier_empty {X : Type u} (r : PreorderSpec X) [DecidableRel r.le] :
    frontier r ([] : List X)=[] := rfl
end FrontierOrderV20
