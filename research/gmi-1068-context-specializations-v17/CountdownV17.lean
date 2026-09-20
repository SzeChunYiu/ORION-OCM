import ViabilityV17
namespace CountdownV17
open ViabilityV17
inductive State where
  | root
  | chain (n : Nat)
  deriving DecidableEq

def relation : State → State → Prop
  | .root, .chain _ => True
  | .chain n, .chain m => n=m+1
  | _, _ => False

def safe (_ : State) : Prop := True

theorem chain_step {n : Nat} {y : State} (h : relation (.chain n) y) :
    ∃ m, n=m+1 ∧ y=.chain m := by
  cases y with
  | root => exact False.elim h
  | chain m => exact ⟨m,h,rfl⟩

theorem root_step {y : State} (h : relation .root y) : ∃ m, y=.chain m := by
  cases y with
  | root => exact False.elim h
  | chain m => exact ⟨m,rfl⟩

theorem tail_run (g : Nat → State)
    (h : ∀ n, safe (g n) ∧ relation (g n) (g (n+1))) :
    Trajectory safe relation (g 1) :=
  ⟨fun n => g (n+1),rfl,fun n => h (n+1)⟩

theorem chain_no_trajectory (n : Nat) : ¬ Trajectory safe relation (.chain n) := by
  induction n with
  | zero =>
    rintro ⟨g,h0,hg⟩
    have h := (hg 0).2
    rw [h0] at h
    rcases chain_step h with ⟨m,hm,_⟩
    omega
  | succ n ih =>
    rintro ⟨g,h0,hg⟩
    have h := (hg 0).2
    rw [h0] at h
    rcases chain_step h with ⟨m,hm,he⟩
    have hmn : m=n := by omega
    subst m
    have ht := tail_run g hg
    rw [he] at ht
    exact ih ht

theorem root_no_trajectory : ¬ Trajectory safe relation .root := by
  rintro ⟨g,h0,hg⟩
  have h := (hg 0).2
  rw [h0] at h
  rcases root_step h with ⟨m,he⟩
  have ht := tail_run g hg
  rw [he] at ht
  exact chain_no_trajectory m ht

def finiteWalk (N n : Nat) : State := if n=0 then .root else .chain (N-n)

def FiniteRun (N : Nat) (x : State) : Prop :=
  ∃ g : Nat → State, g 0=x ∧ (∀ n, n≤N → safe (g n)) ∧
    ∀ n, n<N → relation (g n) (g (n+1))

theorem every_finite_horizon (N : Nat) : FiniteRun N .root := by
  refine ⟨finiteWalk N,rfl,(fun _ _ => trivial),?_⟩
  intro n hn
  by_cases hz : n=0
  · subst n
    trivial
  · have hs : n+1≠0 := by omega
    simp only [finiteWalk,hz,hs,↓reduceIte,relation]
    omega

theorem root_not_viable : ¬ Viable safe relation .root :=
  fun h => root_no_trajectory (viable_to_trajectory safe relation h)

theorem finite_horizons_do_not_imply_viability :
    (∀ N, FiniteRun N .root) ∧ ¬ Viable safe relation .root :=
  ⟨every_finite_horizon,root_not_viable⟩
end CountdownV17
