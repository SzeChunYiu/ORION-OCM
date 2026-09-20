import CategoryTreesV25
import RoundtripResponsesV19
namespace TreeTransportV25
open BracketV25 TableTransportV19
universe u v w x
theorem eval_transport {A : Type u} {B : Type v} {O : Type w} {P : Type x}
    {m : A → A → Option A} {n : B → B → Option B} (i : TableIso m n)
    (fo : O → P) (e : O → A) (f : P → B)
    (he : ∀ o, f (fo o) = i.forward (e o)) (t : Tree O A) :
    eval n some (fun p => some (f p)) (t.map fo i.forward) =
    (eval m some (fun o => some (e o)) t).map i.forward := by
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
      | some b => exact i.mul a b
open BundledCategoryV19 CategoryRoundtripV19 RoundtripResponsesV19
variable {O : Type u} (C : TypedPathsV11.Category.{u,v} O)
theorem forward_identity (o : O) :
    identity (Rebuilt C) (objectForward C o) = categoryForward C (identity C o) := by
  apply ArrowRoundtripV19.unpack_injective
  rfl
theorem backward_identity (o : (BundledCategoryV19.algebra C).Unit) :
    identity C (objectBackward C o) = categoryBackward C (identity (Rebuilt C) o) := by
  have h := object_forward_backward C o
  have hh := congrArg (fun x => (x : (BundledCategoryV19.algebra C).Unit).val) h
  exact hh
theorem forward_response (t : Tree O (Arrow C)) :
    CategoryTreesV25.observer (Rebuilt C)
      (t.map (objectForward C) (categoryForward C)) =
    (CategoryTreesV25.observer C t).map (categoryForward C) :=
  eval_transport (categoryIso C) (objectForward C) (identity C)
    (identity (Rebuilt C)) (forward_identity C) t
theorem backward_response (t : Tree (BundledCategoryV19.algebra C).Unit (Arrow (Rebuilt C))) :
    CategoryTreesV25.observer C
      (t.map (objectBackward C) (categoryBackward C)) =
    (CategoryTreesV25.observer (Rebuilt C) t).map (categoryBackward C) :=
  eval_transport (categoryIso C).symm (objectBackward C) (identity (Rebuilt C))
    (identity C) (backward_identity C) t
theorem backward_forward_tree (t : Tree O (Arrow C)) :
    (t.map (objectForward C) (categoryForward C)).map
      (objectBackward C) (categoryBackward C) = t :=
  map_map _ _ _ _ (object_backward_forward C) (category_backward_forward C) t
theorem forward_backward_tree (t : Tree (BundledCategoryV19.algebra C).Unit (Arrow (Rebuilt C))) :
    (t.map (objectBackward C) (categoryBackward C)).map
      (objectForward C) (categoryForward C) = t :=
  map_map _ _ _ _ (object_forward_backward C) (category_forward_backward C) t
end TreeTransportV25
