import FiniteWinnersV23
import RootCertificatesV23
namespace AffineControlsV23
open ScalarV12 AffineArithmeticV23 AffineContextsV23 AffineWinnersV23
def zeroIntercept (_i : Bool) : Int := 0
def splitSlope (i : Bool) : Int := if i then 1 else 0
theorem int_affine_binding (a b t : Int) : affine a b t=a+b*t := rfl
theorem integral_interpolation_gap :
    ¬∃s : Int,0≤s ∧ s≤1 ∧ lerp s 0 2=1 := by
  simp only [lerp,Int.mul_zero,Int.zero_add]
  omega
theorem integral_root_gap :
    0<affine (1 : Int) (-2) 0 ∧ affine (1 : Int) (-2) 1<0 ∧
      ¬∃t : Int,affine (1 : Int) (-2) t=0 := by
  simp only [affine]
  omega
theorem weak_intersection_singleton (i : Bool) :
    (Winner (fun _ => True) (fun _ => True) zeroIntercept splitSlope 0 i ∧
      Winner (fun _ => True) (fun _ => True) zeroIntercept splitSlope 1 i) ↔ i=false := by
  cases i <;> simp [Winner,active,score,affine,zeroIntercept,splitSlope]
theorem tie_at_zero :
    Winner (fun _ => True) (fun _ => True) zeroIntercept splitSlope 0 false ∧
    Winner (fun _ => True) (fun _ => True) zeroIntercept splitSlope 0 true ∧
    (false : Bool)≠true := by
  simp [Winner,active,score,affine,zeroIntercept,splitSlope]
theorem not_unique_at_zero :
    ¬UniqueWinner (fun _ => True) (fun _ => True) zeroIntercept splitSlope 0 false := by
  intro h
  have he := h.2 true tie_at_zero.2.1
  cases he
theorem parameter_dependent_decode :
    decode zeroIntercept splitSlope 0 true≠decode zeroIntercept splitSlope 1 true := by
  simp [decode,score,affine,zeroIntercept,splitSlope]
def nonlinear (t : Int) := (t-1)*(t-1)
theorem nonlinear_endpoint_failure :
    1≤nonlinear 0 ∧ 1≤nonlinear 2 ∧ ¬1≤nonlinear 1 := by decide
theorem zero_intercept_binding (i : Bool) : zeroIntercept i=0 := rfl
theorem split_slope_binding (i : Bool) : splitSlope i=(if i then 1 else 0) := rfl
theorem nonlinear_binding (t : Int) : nonlinear t=(t-1)*(t-1) := rfl
end AffineControlsV23
