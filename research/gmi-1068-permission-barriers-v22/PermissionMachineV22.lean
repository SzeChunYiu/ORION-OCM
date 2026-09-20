import BudgetResidualV21
import PermissionSetsV22
namespace PermissionMachineV22
open ContinuationV8 BudgetResidualV21 PermissionSetsV22
universe u v w x y
variable {S : Type u} {A : Type v} {O : Type w} {E : Type x} {Q : Type y}
noncomputable def gated (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) : Machine S A O E := by
  classical
  exact ⟨m.obs,fun s a => (m.next s a).bind fun p =>
    if Sub (req s a) enabled then some p else none⟩
def support (m : Machine S A O E) (req : S→A→Family Q) :
    S → List A → Option (S × Family Q)
  | s, [] => some (s,empty)
  | s, a::word => (m.next s a).bind fun (_,t) =>
      (support m req t word).map fun (z,R) => (z,union (req s a) R)
theorem gated_obs (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s : S) : (gated m req enabled).obs s=m.obs s := rfl
theorem gated_missing (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s : S) (a : A) (h : m.next s a=none) :
    (gated m req enabled).next s a=none := by simp [gated,h]
theorem gated_present (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s t : S) (a : A) (e : E)
    (h : m.next s a=some (e,t)) (hr : Sub (req s a) enabled) :
    (gated m req enabled).next s a=some (e,t) := by simp [gated,h,hr]
theorem gated_denied (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s t : S) (a : A) (e : E)
    (h : m.next s a=some (e,t)) (hr : ¬Sub (req s a) enabled) :
    (gated m req enabled).next s a=none := by simp [gated,h,hr]
theorem support_nil (m : Machine S A O E) (req : S→A→Family Q) (s : S) :
    support m req s []=some (s,empty) := rfl
theorem support_cons (m : Machine S A O E) (req : S→A→Family Q)
    (s : S) (a : A) (word : List A) :
    support m req s (a::word)=(m.next s a).bind (fun (_,t) =>
      (support m req t word).map (fun (z,R) => (z,union (req s a) R))) := rfl
theorem support_endpoint (m : Machine S A O E) (req : S→A→Family Q)
    (s : S) (word : List A) :
    (support m req s word).map Prod.fst=endpoint m s word := by
  induction word generalizing s with
  | nil => rfl
  | cons a word ih =>
    cases hn : m.next s a with
    | none => simp [support,endpoint,hn]
    | some p =>
      rcases p with ⟨e,t⟩
      simp only [support,endpoint,hn,Option.some_bind]
      rw [← ih t]
      cases support m req t word <;> rfl
theorem endpoint_support (m : Machine S A O E) (req : S→A→Family Q)
    (s t : S) (word : List A) :
    endpoint m s word=some t ↔ ∃R, support m req s word=some (t,R) := by
  rw [← support_endpoint m req s word]
  cases hs : support m req s word with
  | none => simp
  | some p =>
    rcases p with ⟨z,R⟩
    change some z=some t ↔ ∃R', some (z,R)=some (t,R')
    simp only [Option.some.injEq,Prod.mk.injEq]
    constructor
    · intro h; subst z; exact ⟨R,rfl,rfl⟩
    · rintro ⟨_,h,_⟩; exact h
theorem support_append (m : Machine S A O E) (req : S→A→Family Q)
    (s : S) (u v : List A) :
    support m req s (u++v)=(support m req s u).bind (fun (t,R) =>
      (support m req t v).map (fun (z,T) => (z,union R T))) := by
  induction u generalizing s with
  | nil =>
    simp only [List.nil_append,support,Option.some_bind]
    cases hs : support m req s v with
    | none => rfl
    | some p => rcases p with ⟨z,T⟩; simp [union_empty]
  | cons a u ih =>
    simp only [List.cons_append,support]
    cases hn : m.next s a with
    | none => simp
    | some p =>
      rcases p with ⟨e,t⟩
      simp only [Option.some_bind,ih]
      cases hu : support m req t u with
      | none => simp
      | some p =>
        rcases p with ⟨z,R⟩
        cases hv : support m req z v with
        | none => simp [hv]
        | some p => rcases p with ⟨z',T⟩; simp [hv,union_assoc]
end PermissionMachineV22
