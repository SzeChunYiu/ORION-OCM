import TypedPathsV11
namespace HistoryAdmissionV16
open TypedPathsV11
universe u v
variable {V : Type u} {G : V → V → Type v}
variable (P : {a b : V} → G a b → Prop)

def Admitted : {a b : V} → Path G a b → Prop
  | _, _, .nil _ => True
  | _, _, .cons e p => P e ∧ Admitted p

abbrev Edges (a b : V) := {e : G a b // P e}
abbrev Raw (a b : V) := {p : Path G a b // Admitted @P p}

def erase : {a b : V} → Path (Edges @P) a b → Path G a b
  | _, _, .nil a => .nil a
  | _, _, .cons e p => .cons e.val (erase p)

theorem erase_admitted {a b : V} (p : Path (Edges @P) a b) :
    Admitted @P (erase @P p) := by
  induction p with
  | nil => trivial
  | cons e p ih => exact ⟨e.property, ih⟩

def forget {a b : V} (p : Path (Edges @P) a b) : Raw @P a b :=
  ⟨erase @P p, erase_admitted @P p⟩

def lift : {a b : V} → (p : Path G a b) → Admitted @P p → Path (Edges @P) a b
  | _, _, .nil a, _ => .nil a
  | _, _, .cons e p, h => .cons ⟨e, h.1⟩ (lift p h.2)

def restore {a b : V} (p : Raw @P a b) : Path (Edges @P) a b :=
  lift @P p.val p.property

theorem erase_lift {a b : V} (p : Path G a b) (h : Admitted @P p) :
    erase @P (lift @P p h) = p := by
  induction p with
  | nil => rfl
  | cons e p ih => exact congrArg (Path.cons e) (ih h.2)

theorem lift_erase {a b : V} (p : Path (Edges @P) a b) :
    lift @P (erase @P p) (erase_admitted @P p) = p := by
  induction p with
  | nil => rfl
  | cons e p ih =>
    simp only [erase, lift]
    exact congrArg (Path.cons e) ih

theorem forget_restore {a b : V} (p : Raw @P a b) :
    forget @P (restore @P p) = p := Subtype.ext (erase_lift @P p.val p.property)

theorem restore_forget {a b : V} (p : Path (Edges @P) a b) :
    restore @P (forget @P p) = p := lift_erase @P p

theorem admitted_iff_lift {a b : V} (p : Path G a b) :
    Admitted @P p ↔ ∃ q : Path (Edges @P) a b, erase @P q = p := by
  constructor
  · intro h
    exact ⟨lift @P p h, erase_lift @P p h⟩
  · rintro ⟨q, rfl⟩
    exact erase_admitted @P q

theorem admitted_single {a b : V} (e : G a b) :
    Admitted @P (Path.single e) ↔ P e := by
  change (P e ∧ True) ↔ P e
  simp

def decode {a b : V} (D : {a b : V} → Path G a b → Prop) (e : G a b) :=
  D (Path.single e)

theorem decode_admission {a b : V} (e : G a b) :
    decode (Admitted @P) e ↔ P e := admitted_single @P e

theorem domain_eq_iff_admission_eq
    (Q : {a b : V} → G a b → Prop) :
    (∀ {a b} (p : Path G a b), Admitted @P p ↔ Admitted @Q p) ↔
    (∀ {a b} (e : G a b), P e ↔ Q e) := by
  constructor
  · intro h a b e
    exact (admitted_single @P e).symm.trans ((h (Path.single e)).trans (admitted_single @Q e))
  · intro h a b p
    induction p with
    | nil => exact Iff.rfl
    | cons e p ih => exact and_congr (h e) ih

theorem admitted_append {a b c : V} (p : Path G a b) (q : Path G b c) :
    Admitted @P (Path.append p q) ↔ Admitted @P p ∧ Admitted @P q := by
  induction p with
  | nil => simp [Admitted, Path.append]
  | cons e p ih =>
    change (P e ∧ Admitted @P (Path.append p q)) ↔ (P e ∧ Admitted @P p) ∧ Admitted @P q
    rw [ih, and_assoc]

def empty (a : V) : Raw @P a a := ⟨.nil a, trivial⟩
def concat {a b c : V} (p : Raw @P a b) (q : Raw @P b c) : Raw @P a c :=
  ⟨Path.append p.val q.val, (admitted_append @P p.val q.val).mpr ⟨p.property, q.property⟩⟩

theorem erase_append {a b c : V}
    (p : Path (Edges @P) a b) (q : Path (Edges @P) b c) :
    erase @P (Path.append p q) = Path.append (erase @P p) (erase @P q) := by
  induction p with
  | nil => rfl
  | cons e p ih => exact congrArg (Path.cons e.val) (ih q)

theorem forget_empty (a : V) : forget @P (.nil a) = empty @P a := rfl
theorem restore_empty (a : V) : restore @P (empty @P a) = .nil a := rfl
theorem forget_concat {a b c : V}
    (p : Path (Edges @P) a b) (q : Path (Edges @P) b c) :
    forget @P (Path.append p q) = concat @P (forget @P p) (forget @P q) :=
  Subtype.ext (erase_append @P p q)

theorem restore_concat {a b c : V} (p : Raw @P a b) (q : Raw @P b c) :
    restore @P (concat @P p q) = Path.append (restore @P p) (restore @P q) := by
  have h := forget_concat @P (restore @P p) (restore @P q)
  rw [forget_restore, forget_restore] at h
  have hh := congrArg (restore @P) h
  rw [restore_forget] at hh
  exact hh.symm
end HistoryAdmissionV16
