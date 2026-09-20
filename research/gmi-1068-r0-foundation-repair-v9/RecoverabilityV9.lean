import Std
namespace RecoverabilityV9

def Image (p : M → P) := {v : P // ∃ m, p m = v}
def encoded (p : M → P) (m : M) : Image p := ⟨p m, m, rfl⟩
def Recoverable (p : M → P) (o : M → O) : Prop :=
  ∃ d : Image p → O, ∀ m, d (encoded p m) = o m
def FiberConstant (p : M → P) (o : M → O) : Prop :=
  ∀ m n, p m = p n → o m = o n

theorem recoverable_iff_fiber_constant (p : M → P) (o : M → O) :
    Recoverable p o ↔ FiberConstant p o := by
  constructor
  · rintro ⟨d, hd⟩ m n h
    have he : encoded p m = encoded p n := Subtype.ext h
    rw [← hd m, he, hd n]
  · intro hf
    refine ⟨fun v => o (Classical.choose v.property), ?_⟩
    intro m
    exact hf _ _ (Classical.choose_spec (encoded p m).property)

theorem recovery_unique {p : M → P} {o : M → O}
    (d e : Image p → O)
    (hd : ∀ m, d (encoded p m) = o m)
    (he : ∀ m, e (encoded p m) = o m) : d = e := by
  funext v
  rcases v.property with ⟨m, hm⟩
  have hv : encoded p m = v := Subtype.ext hm
  rw [← hv, hd m, he m]

theorem no_recovery_of_collision {p : M → P} {o : M → O}
    (m n : M) (hp : p m = p n) (ho : o m ≠ o n) :
    ¬ Recoverable p o := by
  intro h
  exact ho ((recoverable_iff_fiber_constant p o).mp h m n hp)

/-- These weaker hypotheses hold for commuting bijective re-encodings. -/
theorem fiber_transport (p : M → P) (o : M → O)
    (p' : N → Q) (o' : N → V) (em : M → N) (ep : P → Q) (eo : O → V)
    (hm : ∀ n, ∃ m, em m = n)
    (hp : ∀ x y, ep x = ep y → x = y)
    (ho : ∀ x y, eo x = eo y → x = y)
    (cp : ∀ m, p' (em m) = ep (p m))
    (co : ∀ m, o' (em m) = eo (o m)) :
    FiberConstant p o ↔ FiberConstant p' o' := by
  constructor
  · intro hf n n' hn
    rcases hm n with ⟨m, rfl⟩
    rcases hm n' with ⟨m', rfl⟩
    rw [co, co]
    apply congrArg eo
    apply hf
    apply hp
    rw [← cp, ← cp]
    exact hn
  · intro hf m m' hh
    apply ho
    rw [← co, ← co]
    apply hf
    rw [cp, cp, hh]

theorem recovery_transport (p : M → P) (o : M → O)
    (p' : N → Q) (o' : N → V) (em : M → N) (ep : P → Q) (eo : O → V)
    (hm : ∀ n, ∃ m, em m = n)
    (hp : ∀ x y, ep x = ep y → x = y)
    (ho : ∀ x y, eo x = eo y → x = y)
    (cp : ∀ m, p' (em m) = ep (p m))
    (co : ∀ m, o' (em m) = eo (o m)) :
    Recoverable p o ↔ Recoverable p' o' := by
  rw [recoverable_iff_fiber_constant, recoverable_iff_fiber_constant]
  exact fiber_transport p o p' o' em ep eo hm hp ho cp co

def UnitFor (mul : A → A → A) (e : A) : Prop :=
  (∀ x, mul e x = x) ∧ (∀ x, mul x e = x)

theorem unit_unique {mul : A → A → A} {e f : A}
    (he : UnitFor mul e) (hf : UnitFor mul f) : e = f := by
  exact (hf.2 e).symm.trans (he.1 f)

theorem unique_unit_expansion {mul : A → A → A}
    (h : ∃ e, UnitFor mul e) :
    ∃ e, UnitFor mul e ∧ ∀ f, UnitFor mul f → f = e := by
  rcases h with ⟨e, he⟩
  exact ⟨e, he, fun _ hf => unit_unique hf he⟩

def constantMul (_ _ : Bool) : Bool := false
theorem constant_associative (a b c : Bool) :
    constantMul (constantMul a b) c = constantMul a (constantMul b c) := rfl
theorem constant_has_no_unit : ¬ ∃ e, UnitFor constantMul e := by
  rintro ⟨e, he⟩
  have h := he.1 true
  cases h

inductive Arrow where
  | i0 | i1 | a | b
  deriving DecidableEq, BEq
def source : Arrow → Bool
  | .i1 => true
  | _ => false
def target : Arrow → Bool
  | .i0 => false
  | _ => true
def Typed : Bool → List Arrow → Prop
  | _, [] => True
  | s, f :: fs => source f = s ∧ Typed (target f) fs
def History := {p : Bool × List Arrow // Typed p.1 p.2}
def aHistory : History := ⟨(false,[.a]), by trivial⟩
def bHistory : History := ⟨(false,[.b]), by trivial⟩
def isIdentity : Arrow → Bool
  | .i0 | .i1 => true
  | _ => false
def admission (full : Bool) (h : History) : Bool :=
  full || h.val.2.all isIdentity
def evaluation (preferA : Bool) (h : History) : Bool :=
  h.val.2.any (fun f => if preferA then f == .a else f == .b)
def process (m : Bool × Bool) : History → Bool := admission m.1
def objective (m : Bool × Bool) : History → Bool := evaluation m.2

theorem process_does_not_recover_context : ¬ Recoverable process objective := by
  apply no_recovery_of_collision (true,true) (true,false) rfl
  intro h
  have hh := congrFun h aHistory
  cases hh

theorem context_does_not_recover_admission : ¬ Recoverable objective process := by
  apply no_recovery_of_collision (false,true) (true,true) rfl
  intro h
  have hh := congrFun h aHistory
  cases hh

theorem actual_ranking_reversal :
    evaluation true aHistory = true ∧ evaluation true bHistory = false ∧
    evaluation false aHistory = false ∧ evaluation false bHistory = true := by
  decide

theorem actual_admission_difference :
    admission false aHistory = false ∧ admission true aHistory = true := by
  decide

theorem identity_list_no_a (fs : List Arrow) (h : fs.all isIdentity = true) :
    fs.any (fun f => f == Arrow.a) = false := by
  induction fs with
  | nil => rfl
  | cons f fs ih =>
    cases f <;> simp_all [isIdentity] <;> rfl

theorem identities_only_no_success (h : History) (ha : admission false h = true) :
    evaluation true h = false := by
  apply identity_list_no_a
  simpa [admission] using ha

theorem full_process_success :
    ∃ h : History, admission true h = true ∧ evaluation true h = true := by
  exact ⟨aHistory, rfl, rfl⟩

end RecoverabilityV9
