import BracketV25
namespace OptionFoldV25
open BracketV25 ResponsesV19
universe u v
attribute [local instance] Classical.propDecidable
def Strong (m : A → A → Option A) :=
  ∀ x y z, (m x y).bind (fun v => m v z)=(m y z).bind (fun v => m x v)
theorem run_append (m : A → A → Option A) (x : A) (xs ys : List A) :
    run m x (xs++ys)=(run m x xs).bind (fun v => run m v ys) := by
  induction xs generalizing x with
  | nil => rfl
  | cons y xs ih =>
    simp only [List.cons_append,run,ih]
    cases m x y <;> rfl
theorem run_product (m : A → A → Option A) (assoc : Strong m) (x y : A) (ys : List A) :
    (m x y).bind (fun z => run m z ys)=(run m y ys).bind (m x) := by
  induction ys generalizing x y with
  | nil => simp [run]
  | cons z zs ih =>
    simp only [run,Option.bind_assoc]
    have h := congrArg (fun q => q.bind (fun a => run m a zs)) (assoc x y z)
    simp only [Option.bind_assoc] at h
    rw [h]
    cases hm : m y z with
    | none => rfl
    | some a => exact ih x a
theorem fold_append (m : A → A → Option A) (assoc : Strong m) (x y : Word A) :
    fold m (append x y)=(fold m x).bind (fun a => (fold m y).bind (m a)) := by
  rcases x with ⟨x,xs⟩
  rcases y with ⟨y,ys⟩
  change run m x (xs++y::ys)=_
  rw [run_append]
  apply congrArg ((run m x xs).bind)
  funext a
  exact run_product m assoc a y ys
theorem flatten_eval {O : Type u} {A : Type v}
    (m : A → A → Option A) (assoc : Strong m) (unit : O → A) (t : Tree O A) :
    eval m some (fun o => some (unit o)) t=fold m (flatten unit t) := by
  induction t with
  | arrow _ => rfl
  | empty _ => rfl
  | seq l r hl hr =>
    simp only [eval,flatten,hl,hr,fold_append m assoc]
theorem guarded_flatten {O : Type u} {A : Type v}
    (m : A → A → Option A) (assoc : Strong m) (unit : O → A)
    (pa : A → Prop) (pe : O → Prop) (t : Tree O A) :
    eval m (fun a => if pa a then some a else none)
      (fun o => if pe o then some (unit o) else none) t =
    if Valid pa pe t then fold m (flatten unit t) else none := by
  classical
  induction t with
  | arrow a => rfl
  | empty o => rfl
  | seq l r hl hr =>
    simp only [eval,hl,hr,Valid,flatten]
    by_cases ha : Valid pa pe l <;> by_cases hb : Valid pa pe r <;>
      simp [ha,hb,fold_append m assoc]
end OptionFoldV25
