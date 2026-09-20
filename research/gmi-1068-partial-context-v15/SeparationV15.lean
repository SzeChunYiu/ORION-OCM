import PartialContextV15
import RecoverabilityV9
namespace PartialContextV15
universe u v w x
def Strict {W : Type v} (r : PreorderSpec W) (a b : W) := r.le a b ∧ ¬r.le b a
noncomputable def preferLow {A : Type u} {W : Type v} (a : A) (lo hi : W) (z : A) : W := by
  classical
  exact if z=a then lo else hi
noncomputable def preferHigh {A : Type u} {W : Type v} (a : A) (lo hi : W) (z : A) : W := by
  classical
  exact if z=a then hi else lo
theorem opposite_strict {A : Type u} {W : Type v} (r : PreorderSpec W)
    (a b : A) (hne : a≠b) (lo hi : W) (hs : Strict r lo hi) :
    Strict r (preferLow a lo hi a) (preferLow a lo hi b) ∧
    Strict r (preferHigh a lo hi b) (preferHigh a lo hi a) := by
  simpa [preferLow,preferHigh,Ne.symm hne] using And.intro hs hs
theorem orders_different {A : Type u} {W : Type v} (r : PreorderSpec W)
    (a b : A) (hne : a≠b) (lo hi : W) (hs : Strict r lo hi) :
    (fun x y => r.le (preferLow a lo hi x) (preferLow a lo hi y)) ≠
    (fun x y => r.le (preferHigh a lo hi x) (preferHigh a lo hi y)) := by
  intro h
  have hp := opposite_strict r a b hne lo hi hs
  have he := congrFun (congrFun h a) b
  exact hp.2.2 (he ▸ hp.1.1)

def Models {A : Type u} {W : Type v} (Allowed : (A → W) → Prop) :=
  {f : A → W // Allowed f}
def processObs {A : Type u} {W : Type v} {Proc : Type w}
    {Allowed : (A → W) → Prop} (C : Proc) (_ : Models Allowed) : Proc := C
def evaluatorObs {A : Type u} {W : Type v}
    {Allowed : (A → W) → Prop} (m : Models Allowed) : A → W := m.val
def orderingObs {A : Type u} {W : Type v}
    {Allowed : (A → W) → Prop} (r : PreorderSpec W) (m : Models Allowed) : A → A → Prop :=
  fun x y => r.le (m.val x) (m.val y)

theorem fixed_process {A : Type u} {W : Type v} {Proc : Type w}
    {Allowed : (A → W) → Prop} (C : Proc) (m n : Models Allowed) :
    processObs C m=processObs C n := rfl
theorem fixed_nonrecovery {A : Type u} {W : Type v} {Proc : Type w}
    (C : Proc) (r : PreorderSpec W) (a b : A) (hne : a≠b)
    (lo hi : W) (hs : Strict r lo hi) (Allowed : (A → W) → Prop)
    (hl : Allowed (preferLow a lo hi)) (hh : Allowed (preferHigh a lo hi)) :
    ¬ RecoverabilityV9.Recoverable (processObs (Allowed:=Allowed) C) (orderingObs r) := by
  apply RecoverabilityV9.no_recovery_of_collision
    (p:=processObs C) (o:=orderingObs r)
    (⟨preferLow a lo hi,hl⟩ : Models Allowed) (⟨preferHigh a lo hi,hh⟩ : Models Allowed) rfl
  exact orders_different r a b hne lo hi hs

theorem constant_no_strict {W : Type v} (r : PreorderSpec W) (w : W) :
    ¬ Strict r w w := fun h => h.2 h.1
theorem collapsed_no_strict {A : Type u} {X : Type x} {W : Type v}
    (r : PreorderSpec W) (obs : A → X) (f : X → W) (a b : A) (h : obs a=obs b) :
    ¬ Strict r (f (obs a)) (f (obs b)) := by
  rw [h]
  exact constant_no_strict r _
theorem admitted_nonrecovery {H : Type u} {W : Type v} {Proc : Type w}
    (C : Proc) (admitted : Proc → H → Prop) (D : RelativeDomain (admitted C))
    (r : PreorderSpec W) (a b : D.Carrier) (hne : a≠b)
    (lo hi : W) (hs : Strict r lo hi) (Allowed : (D.Carrier → W) → Prop)
    (hl : Allowed (preferLow a lo hi)) (hh : Allowed (preferHigh a lo hi)) :
    ¬ RecoverabilityV9.Recoverable (processObs (Allowed:=Allowed) C) (orderingObs r) :=
  fixed_nonrecovery C r a b hne lo hi hs Allowed hl hh
end PartialContextV15
