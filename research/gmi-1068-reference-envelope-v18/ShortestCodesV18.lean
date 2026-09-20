import PrefixWrapperV18
namespace ShortestCodesV18
open PrefixWrapperV18
universe u
def IsShortest {α : Type u} (U : Machine α) (x : α) (p : Program) : Prop :=
  U p=some x ∧ ∀ q, U q=some x → p.length≤q.length
def MinimumLength {α : Type u} (U : Machine α) (x : α) (k : Nat) : Prop :=
  ∃ p, IsShortest U x p ∧ p.length=k

theorem shortest_iff {α : Type u} (U : Machine α) (x : α) (p : Program) :
    IsShortest U x p ↔ U p=some x ∧ ∀ q, U q=some x → p.length≤q.length := Iff.rfl
theorem minimum_iff {α : Type u} (U : Machine α) (x : α) (k : Nat) :
    MinimumLength U x k ↔ ∃ p, IsShortest U x p ∧ p.length=k := Iff.rfl

theorem minimum_exists {α : Type u} (U : Machine α) (x : α)
    (hp : ∃ p, U p=some x) : ∃ k, MinimumLength U x k := by
  classical
  have aux : ∀ n (p : Program), p.length=n → U p=some x →
      ∃ q, IsShortest U x q := by
    intro n
    induction n using Nat.strongRecOn with
    | ind n ih =>
      intro p hlen hs
      by_cases h : ∀ q, U q=some x → p.length≤q.length
      · exact ⟨p,hs,h⟩
      · obtain ⟨q,hq⟩ := Classical.not_forall.mp h
        have hqs : U q=some x := by
          apply Classical.byContradiction
          intro hn
          exact hq (fun hh => False.elim (hn hh))
        have hlt : q.length<p.length := by
          apply Nat.lt_of_not_ge
          intro hle
          exact hq (fun _ => hle)
        exact ih q.length (by omega) q rfl hqs
  obtain ⟨p,hp⟩ := hp
  obtain ⟨q,hq⟩ := aux p.length p rfl hp
  exact ⟨q.length,q,hq,rfl⟩
theorem minimum_unique {α : Type u} (U : Machine α) (x : α)
    {j k : Nat} (hj : MinimumLength U x j) (hk : MinimumLength U x k) : j=k := by
  obtain ⟨p,hp,rfl⟩ := hj
  obtain ⟨q,hq,rfl⟩ := hk
  exact Nat.le_antisymm (hp.2 q hq.1) (hq.2 p hp.1)
theorem target_shortest {α : Type u} (U : Machine α) (z : α)
    (L : Nat) (hL : 0<L) : IsShortest (wrapper U z L) z [false] := by
  refine ⟨wrapper_target U z L,?_⟩
  intro p hp
  cases p with
  | nil => rw [wrapper_empty U z L hL] at hp; cases hp
  | cons b p => simp
theorem target_minimum {α : Type u} (U : Machine α) (z : α)
    (L : Nat) (hL : 0<L) : MinimumLength (wrapper U z L) z 1 :=
  ⟨[false],target_shortest U z L hL,rfl⟩

theorem nontarget_success {α : Type u} (U : Machine α) (z x : α)
    (L : Nat) (hL : 0<L) (hx : x≠z) (p : Program) :
    wrapper U z L p=some x ↔ ∃ q, p=pad L q ∧ U q=some x := by
  rw [success_iff U z x L hL p]
  simp [hx]
theorem nontarget_exists {α : Type u} (U : Machine α) (z x : α)
    (L : Nat) (hL : 0<L) (hx : x≠z) :
    (∃ p, wrapper U z L p=some x) ↔ ∃ q, U q=some x := by
  constructor
  · rintro ⟨p,hp⟩
    obtain ⟨q,_,hq⟩ := (nontarget_success U z x L hL hx p).mp hp
    exact ⟨q,hq⟩
  · rintro ⟨q,hq⟩
    exact ⟨pad L q,by rw [wrapper_simulates U z L hL q]; exact hq⟩
theorem shortest_forward {α : Type u} (U : Machine α) (z x : α)
    (L : Nat) (hL : 0<L) (hx : x≠z) (p : Program) (hp : IsShortest U x p) :
    IsShortest (wrapper U z L) x (pad L p) := by
  refine ⟨by rw [wrapper_simulates U z L hL p]; exact hp.1,?_⟩
  intro q hq
  obtain ⟨r,rfl,hr⟩ := (nontarget_success U z x L hL hx q).mp hq
  simpa only [pad_length] using Nat.add_le_add_left (hp.2 r hr) L
theorem shortest_backward {α : Type u} (U : Machine α) (z x : α)
    (L : Nat) (hL : 0<L) (hx : x≠z) (q : Program)
    (hq : IsShortest (wrapper U z L) x q) :
    ∃ p, q=pad L p ∧ IsShortest U x p := by
  obtain ⟨p,rfl,hp⟩ := (nontarget_success U z x L hL hx q).mp hq.1
  refine ⟨p,rfl,hp,?_⟩
  intro r hr
  have hh := hq.2 (pad L r) (by rw [wrapper_simulates U z L hL r]; exact hr)
  simp only [pad_length] at hh
  omega
theorem nontarget_minimum_iff {α : Type u} (U : Machine α) (z x : α)
    (L : Nat) (hL : 0<L) (hx : x≠z) (k : Nat) :
    MinimumLength (wrapper U z L) x k ↔
      ∃ j, k=L+j ∧ MinimumLength U x j := by
  constructor
  · rintro ⟨q,hq,hk⟩
    obtain ⟨p,rfl,hp⟩ := shortest_backward U z x L hL hx q hq
    exact ⟨p.length,by simpa only [pad_length] using hk.symm,p,hp,rfl⟩
  · rintro ⟨j,rfl,p,hp,hj⟩
    exact ⟨pad L p,shortest_forward U z x L hL hx p hp,by rw [pad_length,hj]⟩
end ShortestCodesV18
