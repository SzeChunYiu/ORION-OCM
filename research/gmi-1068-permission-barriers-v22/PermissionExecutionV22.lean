import PermissionMachineV22
namespace PermissionExecutionV22
open ContinuationV8 BudgetResidualV21 PermissionSetsV22 PermissionMachineV22
universe u v w x y
variable {S : Type u} {A : Type v} {O : Type w} {E : Type x} {Q : Type y}
theorem gated_success (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s t : S) (word : List A) :
    endpoint (gated m req enabled) s word=some t ↔
      ∃R, support m req s word=some (t,R) ∧ Sub R enabled := by
  classical
  induction word generalizing s t with
  | nil => simp [endpoint,support,PermissionSetsV22.Sub,empty,and_assoc]
  | cons a word ih =>
    cases hn : m.next s a with
    | none => simp [endpoint,gated,support,hn]
    | some p =>
      rcases p with ⟨e,z⟩
      by_cases hr : Sub (req s a) enabled
      · simp only [endpoint,gated,hn,Option.some_bind,if_pos hr]
        change endpoint (gated m req enabled) z word=some t ↔ _
        rw [ih]
        cases hs : support m req z word with
        | none => simp [support,hn,hs]
        | some p =>
          rcases p with ⟨v,R⟩
          simp [support,hn,hs,union_sub,hr,and_assoc]
      · simp only [endpoint,gated,hn,Option.some_bind,if_neg hr,Option.none_bind]
        cases hs : support m req z word with
        | none => simp [support,hn,hs]
        | some p =>
          rcases p with ⟨v,R⟩
          simp [support,hn,hs,union_sub,hr,and_assoc]
theorem full_successful_response (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s t : S) (word : List A)
    (h : endpoint (gated m req enabled) s word=some t) :
    run (gated m req enabled) s word=run m s word := by
  classical
  induction word generalizing s with
  | nil => rfl
  | cons a word ih =>
    cases hn : m.next s a with
    | none => simp [endpoint,gated,hn] at h
    | some p =>
      rcases p with ⟨e,z⟩
      by_cases hr : Sub (req s a) enabled
      · have hg := gated_present m req enabled s z a e hn hr
        simp only [endpoint,hg,Option.some_bind] at h
        simp only [run,hg,hn,gated_obs]
        exact congrArg (Response.step (m.obs s) e) (ih z h)
      · simp [endpoint,gated,hn,hr] at h
theorem success_mono (m : Machine S A O E) (req : S→A→Family Q)
    (lo hi : Family Q) (hsub : Sub lo hi) (s t : S) (word : List A)
    (h : endpoint (gated m req lo) s word=some t) :
    endpoint (gated m req hi) s word=some t := by
  obtain ⟨R,hR,hlo⟩ := (gated_success m req lo s t word).mp h
  exact (gated_success m req hi s t word).mpr ⟨R,hR,sub_trans hlo hsub⟩
theorem all_permissions (m : Machine S A O E) (req : S→A→Family Q)
    (s t : S) (word : List A) :
    endpoint (gated m req (fun _ => True)) s word=some t ↔
      endpoint m s word=some t := by
  rw [gated_success,endpoint_support m req]
  simp [PermissionSetsV22.Sub]
theorem successful_base (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s t : S) (word : List A)
    (h : endpoint (gated m req enabled) s word=some t) :
    endpoint m s word=some t := by
  obtain ⟨R,hR,_⟩ := (gated_success m req enabled s t word).mp h
  exact (endpoint_support m req s t word).mpr ⟨R,hR⟩
end PermissionExecutionV22
