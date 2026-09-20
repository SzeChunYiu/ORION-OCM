import TableTransportV19
import RecoverabilityV9
namespace ResponsesV19
open PartialUnitsV19 TableTransportV19
universe u v w
inductive Query (A : Type u) where
  | word : A → List A → Query A
  | empty : A → Query A
def Query.map (f : A → B) : Query A → Query B
  | .word x xs => .word (f x) (xs.map f)
  | .empty e => .empty (f e)
def run (m : A → A → Option A) (x : A) : List A → Option A
  | [] => some x
  | y :: ys => (m x y).bind (fun z => run m z ys)
theorem run_nil (m : A → A → Option A) (x : A) : run m x [] = some x := rfl
theorem run_cons (m : A → A → Option A) (x y : A) (ys : List A) :
    run m x (y :: ys) = (m x y).bind (fun z => run m z ys) := rfl
theorem query_map_word (f : A → B) (x : A) (xs : List A) :
    Query.map f (.word x xs) = .word (f x) (xs.map f) := rfl
theorem query_map_empty (f : A → B) (x : A) :
    Query.map f (.empty x) = .empty (f x) := rfl
noncomputable def response (m : A → A → Option A) : Query A → Option A := by
  classical
  exact fun q => match q with
    | .word x xs => run m x xs
    | .empty e => if IsUnit m e then some e else none
theorem word_binding (m : A → A → Option A) (x : A) (xs : List A) :
    response m (.word x xs) = run m x xs := rfl
theorem empty_binding (m : A → A → Option A) (e : A) :
    response m (.empty e) = some e ↔ IsUnit m e := by
  classical
  simp [response]
theorem empty_illegal (m : A → A → Option A) (e : A) :
    response m (.empty e) = none ↔ ¬ IsUnit m e := by
  classical
  simp [response]
theorem singleton_binding (m : A → A → Option A) (x : A) :
    response m (.word x []) = some x := rfl
theorem pair_binding (m : A → A → Option A) (x y : A) :
    response m (.word x [y]) = m x y := by
  simp [response,run]
theorem run_transport {A : Type u} {B : Type v}
    {m : A → A → Option A} {n : B → B → Option B}
    (I : TableIso m n) (x : A) (xs : List A) :
    run n (I.forward x) (xs.map I.forward) = (run m x xs).map I.forward := by
  induction xs generalizing x with
  | nil => rfl
  | cons y ys ih =>
    simp only [List.map_cons,run,I.mul]
    cases h : m x y with
    | none => rfl
    | some z => exact ih z
theorem response_transport {A : Type u} {B : Type v}
    {m : A → A → Option A} {n : B → B → Option B}
    (I : TableIso m n) (q : Query A) :
    response n (q.map I.forward) = (response m q).map I.forward := by
  classical
  cases q with
  | word x xs => exact run_transport I x xs
  | empty e =>
    simp only [Query.map,response,I.unit_iff]
    split <;> rfl
theorem responses_eq_iff_tables_eq {A : Type u} (m n : A → A → Option A) :
    response m = response n ↔ m = n := by
  constructor
  · intro h
    funext x y
    have hh := congrFun h (.word x [y])
    simpa only [pair_binding] using hh
  · intro h
    rw [h]
theorem response_recovery_iff_table_recovery {A : Type u} {M : Type v} {Z : Type w}
    (table : M → A → A → Option A) (code : M → Z) :
    RecoverabilityV9.Recoverable code (fun m => response (table m)) ↔
      RecoverabilityV9.Recoverable code table := by
  rw [RecoverabilityV9.recoverable_iff_fiber_constant,
    RecoverabilityV9.recoverable_iff_fiber_constant]
  constructor
  · intro h x y hc
    exact (responses_eq_iff_tables_eq _ _).mp (h x y hc)
  · intro h x y hc
    exact (responses_eq_iff_tables_eq _ _).mpr (h x y hc)
end ResponsesV19
