import ProcessMapsV26
namespace RawTransportV26
open BracketV25 BundledCategoryV19 ProcessMapsV26
universe u v w x
theorem eval_map {A : Type u} {B : Type v} {O : Type w} {P : Type x}
    (m : A → A → Option A) (n : B → B → Option B) (j : A → B) (fo : O → P)
    (e : O → A) (f : P → B)
    (hm : ∀ a b, n (j a) (j b) = (m a b).map j)
    (he : ∀ o, f (fo o) = j (e o)) (t : Tree O A) :
    eval n some (fun p => some (f p)) (t.map fo j) =
    (eval m some (fun o => some (e o)) t).map j := by
  induction t with
  | arrow a => rfl
  | empty o => exact congrArg some (he o)
  | seq l r hl hr =>
    simp only [Tree.map,eval,hl,hr]
    cases eval m some (fun o => some (e o)) l with
    | none => rfl
    | some a =>
      cases eval m some (fun o => some (e o)) r with
      | none => rfl
      | some b => exact hm a b
variable {O : Type u} {P : Type w}
    {C : TypedPathsV11.Category.{u,v} O} {D : TypedPathsV11.Category.{w,x} P}
def ProductsCommute (F : ProcessMap C D) :=
  ∀ a b, mul D (F.bundle a) (F.bundle b) = (mul C a b).map F.bundle
def TreesCommute (F : ProcessMap C D) :=
  ∀ t, CategoryTreesV25.observer D (F.tree t) =
    (CategoryTreesV25.observer C t).map F.bundle
theorem trees_of_injective (F : ProcessMap C D) (hi : F.ObjectInjective) : TreesCommute F :=
  eval_map _ _ F.bundle F.obj (identity C) (identity D) (F.product_commutes hi)
    (fun a => (F.bundle_identity a).symm)
theorem injective_of_products (F : ProcessMap C D) (h : ProductsCommute F) :
    F.ObjectInjective := by
  intro a b hab
  by_cases e : a = b
  · exact e
  · have hh := h (identity C a) (identity C b)
    rw [F.bundle_identity,F.bundle_identity] at hh
    have hn : mul C (identity C a) (identity C b) = none := not_aligned C _ _ e
    rw [hn] at hh
    obtain ⟨z,hz⟩ := (defined_iff D (identity D (F.obj a)) (identity D (F.obj b))).mpr hab
    rw [hz] at hh
    cases hh
theorem products_of_trees (F : ProcessMap C D) (h : TreesCommute F) : ProductsCommute F := by
  intro a b
  exact h (.seq (.arrow a) (.arrow b))
theorem sharp_equivalence (F : ProcessMap C D) :
    (ProductsCommute F ↔ F.ObjectInjective) ∧ (TreesCommute F ↔ F.ObjectInjective) :=
  ⟨⟨injective_of_products F,F.product_commutes⟩,
   ⟨fun h => injective_of_products F (products_of_trees F h),trees_of_injective F⟩⟩
theorem success (F : ProcessMap C D) (t : Tree O (Arrow C)) (z : Arrow C)
    (h : CategoryTreesV25.observer C t = some z) :
    CategoryTreesV25.observer D (F.tree t) = some (F.bundle z) := by
  induction t generalizing z with
  | arrow a => cases h; rfl
  | empty a => cases h; exact congrArg some (F.bundle_identity a).symm
  | seq l r hl hr =>
    rw [CategoryTreesV25.seq] at h
    cases ha : CategoryTreesV25.observer C l with
    | none => simp [ha] at h
    | some a =>
      cases hb : CategoryTreesV25.observer C r with
      | none => simp [hb] at h
      | some b =>
        have hab : mul C a b = some z := by simpa [ha,hb] using h
        change (CategoryTreesV25.observer D (F.tree l)).bind
          (fun x => (CategoryTreesV25.observer D (F.tree r)).bind (mul D x)) = _
        rw [hl a ha,hr b hb]
        exact F.product_success a b z hab
theorem none_iff (F : ProcessMap C D) (hi : F.ObjectInjective) (t : Tree O (Arrow C)) :
    CategoryTreesV25.observer D (F.tree t) = none ↔ CategoryTreesV25.observer C t = none := by
  rw [trees_of_injective F hi]
  cases CategoryTreesV25.observer C t <;> simp
theorem output_reflection (F : ProcessMap C D) (hi : F.ObjectInjective) (hf : F.Faithful)
    (s t : Tree O (Arrow C)) :
    CategoryTreesV25.observer D (F.tree s) = CategoryTreesV25.observer D (F.tree t) ↔
    CategoryTreesV25.observer C s = CategoryTreesV25.observer C t := by
  rw [trees_of_injective F hi,trees_of_injective F hi]
  constructor
  · intro h
    cases hs : CategoryTreesV25.observer C s with
    | none =>
      cases ht : CategoryTreesV25.observer C t with
      | none => rfl
      | some b => simp [hs,ht] at h
    | some a =>
      cases ht : CategoryTreesV25.observer C t with
      | none => simp [hs,ht] at h
      | some b =>
        have he : F.bundle a = F.bundle b := by simpa [hs,ht] using h
        exact congrArg some (F.bundle_injective hi hf a b he)
  · exact congrArg (Option.map F.bundle)
theorem collapsed_empty_witness (F : ProcessMap C D) (a b : O)
    (hne : a ≠ b) (heq : F.obj a = F.obj b) :
    CategoryTreesV25.observer C (.seq (.empty a) (.empty b)) = none ∧
    CategoryTreesV25.observer D (F.tree (.seq (.empty a) (.empty b))) =
      some (identity D (F.obj a)) := by
  constructor
  · exact not_aligned C _ _ hne
  · change mul D (identity D (F.obj a)) (identity D (F.obj b)) = _
    rw [← heq]
    exact left_identity D (identity D (F.obj a))
end RawTransportV26
