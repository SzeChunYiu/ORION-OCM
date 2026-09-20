import GroupLawsV16
import RecoverabilityV9
namespace CompositionContextV16
open GroupLawsV16

def product (m : Law) : List Label → Label
  | [] => .zero
  | a :: w => m.comp a (product m w)

def rawParity : List Label → Bool
  | [] => false
  | a :: w => Bool.xor (parity a) (rawParity w)

theorem fold_parity (m : Law)
    (h : ∀ a b, parity (m.comp a b) = Bool.xor (parity a) (parity b))
    (w : List Label) : parity (product m w) = rawParity w := by
  induction w with
  | nil => rfl
  | cons a w ih => simp only [product, rawParity, h, ih]

theorem all_word_context_eq (w : List Label) :
    parity (product c4 w) = parity (product v4 w) :=
  (fold_parity c4 c4_parity_comp w).trans (fold_parity v4 v4_parity_comp w).symm

def boolLE (a b : Bool) : Prop := a = false ∨ b = true

theorem boolLE_refl (a : Bool) : boolLE a a := by cases a <;> simp [boolLE]
theorem boolLE_trans {a b c : Bool} (hab : boolLE a b) (hbc : boolLE b c) :
    boolLE a c := by
  cases a <;> cases b <;> cases c <;> simp_all [boolLE]

structure FullContext where
  source : List Label → Prop
  value : (w : List Label) → source w → Option Bool
  order : Bool → Bool → Prop
  order_refl : ∀ a, order a a
  order_trans : ∀ {a b c}, order a b → order b c → order a c

def context (m : Law) : FullContext where
  source _ := True
  value w _ := some (parity (product m w))
  order := boolLE
  order_refl := boolLE_refl
  order_trans := boolLE_trans

theorem full_context_eq : context c4 = context v4 := by
  have h : (fun w : List Label => fun _ : True => some (parity (product c4 w))) =
      (fun w : List Label => fun _ : True => some (parity (product v4 w))) := by
    funext w hw
    exact congrArg some (all_word_context_eq w)
  exact congrArg (fun f => FullContext.mk (fun _ => True) f boolLE
    boolLE_refl boolLE_trans) h

theorem context_nonconstant (m : Law) :
    (context m).value [] trivial ≠ (context m).value [.one] trivial := by
  simp only [context, product, m.right_id, parity]
  decide

theorem composition_not_recoverable :
    ¬ RecoverabilityV9.Recoverable context Law.comp :=
  RecoverabilityV9.no_recovery_of_collision c4 v4 full_context_eq composition_different

def evaluationKernel (m : Law) (x y : List Label) : Prop :=
  product m x = product m y

theorem kernel_witness :
    evaluationKernel c4 [.one, .one] [.two] ∧
    ¬ evaluationKernel v4 [.one, .one] [.two] := by
  change Label.two = Label.two ∧ ¬ Label.zero = Label.two
  decide

theorem evaluation_kernels_different : evaluationKernel c4 ≠ evaluationKernel v4 := by
  intro h
  apply kernel_witness.2
  rw [← h]
  exact kernel_witness.1
end CompositionContextV16
