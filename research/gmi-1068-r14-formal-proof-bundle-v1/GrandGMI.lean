universe u v w

/- F01: minimal typed sequential process core -/
structure ProcCat where
  Obj : Type u
  Hom : Obj → Obj → Type v
  id : (A : Obj) → Hom A A
  comp : {A B C : Obj} → Hom A B → Hom B C → Hom A C
  assoc :
    {A B C D : Obj} →
    (f : Hom A B) → (g : Hom B C) → (h : Hom C D) →
    comp (comp f g) h = comp f (comp g h)
  id_left :
    {A B : Obj} → (f : Hom A B) →
    comp (id A) f = f
  id_right :
    {A B : Obj} → (f : Hom A B) →
    comp f (id B) = f

namespace GrandGMI

variable {C : ProcCat}

theorem F01_history_bracketing
    {A B C₁ D : C.Obj}
    (f : C.Hom A B) (g : C.Hom B C₁) (h : C.Hom C₁ D) :
    C.comp (C.comp f g) h = C.comp f (C.comp g h) :=
  C.assoc f g h

theorem F01_prepend_identity
    {A B : C.Obj} (f : C.Hom A B) :
    C.comp (C.id A) f = f := C.id_left f

theorem F01_append_identity
    {A B : C.Obj} (f : C.Hom A B) :
    C.comp f (C.id B) = f := C.id_right f

/- F02: process/context finite separating model -/
inductive Action where
  | a0
  | a1
deriving DecidableEq

def procStep (_ : Unit) (_ : Action) : Unit := ()

def ctx0 : Action → Nat
  | .a0 => 1
  | .a1 => 0

def ctx1 : Action → Nat
  | .a0 => 0
  | .a1 => 1

theorem F02_contexts_differ_on_same_process : ctx0 ≠ ctx1 := by
  intro h
  have h0 := congrFun h Action.a0
  simp [ctx0, ctx1] at h0

def reach0 (a b : Bool) : Prop := a = b
def reach1 (a b : Bool) : Prop := a = b ∨ (a = false ∧ b = true)

theorem F02_processes_differ_under_same_state_value :
    (¬ reach0 false true) ∧ reach1 false true := by
  constructor
  · simp [reach0]
  · simp [reach1]

/- F03: contextual attainability monotonicity -/
def Attain {H : Type u} {W : Type v}
    (Reach : H → Prop) (nu : H → W) (val : W) : Prop :=
  ∃ h, Reach h ∧ nu h = val

theorem F03_attain_mono {H : Type u} {W : Type v}
    {R₁ R₂ : H → Prop} {nu : H → W}
    (hsub : ∀ h, R₁ h → R₂ h) :
    ∀ val, Attain R₁ nu val → Attain R₂ nu val := by
  intro val hv
  rcases hv with ⟨h, hr, heq⟩
  exact ⟨h, hsub h hr, heq⟩

/- F04: contextual equivalence is an equivalence relation -/
def OpEq {H : Type u} {T : Type v} {O : Type w}
    (resp : H → T → O) (h₁ h₂ : H) : Prop :=
  ∀ t, resp h₁ t = resp h₂ t

theorem F04_refl {H : Type u} {T : Type v} {O : Type w}
    (resp : H → T → O) (h : H) : OpEq resp h h := by
  intro t
  rfl

theorem F04_symm {H : Type u} {T : Type v} {O : Type w}
    {resp : H → T → O} {h₁ h₂ : H}
    (h : OpEq resp h₁ h₂) : OpEq resp h₂ h₁ := by
  intro t
  exact Eq.symm (h t)

theorem F04_trans {H : Type u} {T : Type v} {O : Type w}
    {resp : H → T → O} {h₁ h₂ h₃ : H}
    (h12 : OpEq resp h₁ h₂) (h23 : OpEq resp h₂ h₃) :
    OpEq resp h₁ h₃ := by
  intro t
  exact Eq.trans (h12 t) (h23 t)

/- F05: a correct representation cannot merge separated histories -/
theorem F05_separation_lower_bound
    {H : Type u} {R : Type v} {O : Type w}
    (rep : H → R) (decode : R → O) (obs : H → O)
    (correct : ∀ h, decode (rep h) = obs h)
    {h₁ h₂ : H} (sep : obs h₁ ≠ obs h₂) :
    rep h₁ ≠ rep h₂ := by
  intro same
  apply sep
  calc
    obs h₁ = decode (rep h₁) := Eq.symm (correct h₁)
    _ = decode (rep h₂) := by rw [same]
    _ = obs h₂ := correct h₂

/- F06: directed reachability need not be symmetric -/
inductive Node where | A | B deriving DecidableEq

def oneWay : Node → Node → Prop
  | .A, .A => True
  | .B, .B => True
  | .A, .B => True
  | .B, .A => False

theorem F06_asymmetry : oneWay .A .B ∧ ¬ oneWay .B .A := by
  constructor <;> simp [oneWay]

/- F07: finite/constructible discovery follows from fair coverage -/
def FairCoverage {P : Type u} (enumerate : Nat → P) : Prop :=
  ∀ p, ∃ n, enumerate n = p

theorem F07_fair_eventually_visits {P : Type u}
    (enumerate : Nat → P) (hfair : FairCoverage enumerate) (p : P) :
    ∃ n, enumerate n = p :=
  hfair p

/- F08: no equal positive natural weight can have all prefix masses bounded -/
theorem F08_no_uniform_positive_bounded_prefix
    (p B : Nat) (hp : 0 < p)
    (hbound : ∀ n : Nat, n * p ≤ B) : False := by
  have hp1 : 1 ≤ p := hp
  have hmul : (B + 1) * 1 ≤ (B + 1) * p :=
    Nat.mul_le_mul_left (B + 1) hp1
  have hlow : B + 1 ≤ (B + 1) * p := by
    simpa using hmul
  have hhigh : (B + 1) * p ≤ B := hbound (B + 1)
  have hbad : B + 1 ≤ B := le_trans hlow hhigh
  exact (Nat.not_succ_le_self B) (by simpa using hbad)

/- F09: registered abstraction crossover D=4,L=3,c=1 -/
theorem F09_not_beneficial_at_two : ¬ (4 + 2 * 1 < 2 * 3) := by decide
theorem F09_beneficial_at_three : 4 + 3 * 1 < 3 * 3 := by decide

/- F10: evidence-conditioned adaptive rule on hidden ID/NOT tasks -/
inductive HiddenTask where
  | id
  | not
deriving DecidableEq

inductive Bit where
  | z
  | o
deriving DecidableEq

def flip : Bit → Bit
  | .z => .o
  | .o => .z

def trainLabel : HiddenTask → Bit
  | .id => .z
  | .not => .o

def queryTruth : HiddenTask → Bit
  | .id => .o
  | .not => .z

def adaptive (train : Bit) : Bit := flip train

theorem F10_adaptive_solves_both (t : HiddenTask) :
    adaptive (trainLabel t) = queryTruth t := by
  cases t <;> rfl

/- F11: any finite pair of executable self-modifiers closes under composition -/
def composeFn {A B C : Type} (f : A → B) (g : B → C) : A → C :=
  fun x => g (f x)

theorem F11_reflective_finite_composition {P : Type u}
    (m1 m2 : P → P) :
    ∃ m : P → P, ∀ p, m p = m2 (m1 p) := by
  exact ⟨composeFn m1 m2, by intro p; rfl⟩

/- F12: XOR response violates the affine rectangle identity -/
def xorVal : Bool → Bool → Nat
  | false, false => 0
  | false, true => 1
  | true, false => 1
  | true, true => 0

theorem F12_xor_breaks_affine_rectangle :
    xorVal false false + xorVal true true ≠
    xorVal false true + xorVal true false := by
  decide

end GrandGMI
