import OrderedWeightsV27
namespace FiniteOutcomesV27
open StochasticV14 OrderedWeightsV27
inductive Shape where
  | atom (n : Nat)
  | product (a b : Shape)
def Carrier : Shape → Type
  | .atom n => Fin n
  | .product a b => Carrier a × Carrier b
universe u v
variable {α : Type u} [Weight α]
def total : (I : Shape) → (Carrier I → α) → α
  | .atom _, f => sum f
  | .product a b, f => total a (fun i => total b (fun j => f (i,j)))
theorem total_zero (I : Shape) : total I (fun _ => (0:α))=0 := by
  induction I with
  | atom n => exact sum_zero n
  | product a b ia ib => simp only [total,ib,ia]
theorem total_add (I : Shape) (f g : Carrier I → α) :
    total I (fun i => f i+g i)=total I f+total I g := by
  induction I with
  | atom n => exact sum_add f g
  | product a b ia ib => simp only [total,ib,ia]
theorem total_mul_left (I : Shape) (c : α) (f : Carrier I → α) :
    total I (fun i => c*f i)=c*total I f := by
  induction I with
  | atom n => exact sum_mul_left c f
  | product a b ia ib => simp only [total,ib,ia]
theorem total_mul_right (I : Shape) (f : Carrier I → α) (c : α) :
    total I (fun i => f i*c)=total I f*c := by
  induction I with
  | atom n => exact sum_mul_right f c
  | product a b ia ib => simp only [total,ib,ia]
theorem exchange_fin (I : Shape) {n : Nat} (f : Carrier I → Fin n → α) :
    total I (fun i => sum (f i))=sum (fun j => total I (fun i => f i j)) := by
  induction I with
  | atom m => exact sum_swap f
  | product a b ia ib =>
    change total a (fun i => total b (fun k => sum (f (i,k))))=_
    calc
      _ = total a (fun i => sum (fun j => total b (fun k => f (i,k) j))) :=
        congrArg (total a) (funext (fun i => ib (fun k j => f (i,k) j)))
      _ = _ := ia (fun i j => total b (fun k => f (i,k) j))
theorem exchange (I J : Shape) (f : Carrier I → Carrier J → α) :
    total I (fun i => total J (f i))=total J (fun j => total I (fun i => f i j)) := by
  induction J with
  | atom n => exact exchange_fin I f
  | product a b ia ib =>
    change total I (fun i => total a (fun j => total b (fun k => f i (j,k))))=_
    rw [ia]
    exact congrArg (total a) (funext (fun j => ib (fun i k => f i (j,k))))
theorem total_mono [OrderedWeight α] (I : Shape) (f g : Carrier I → α)
    (h : ∀ i,f i≤g i) : total I f≤total I g := by
  induction I with
  | atom n => exact sum_mono f g h
  | product a b ia ib => exact ia _ _ (fun i => ib _ _ (fun j => h (i,j)))
theorem term_le_total [OrderedWeight α] (I : Shape) (f : Carrier I → α) (i : Carrier I) :
    f i≤total I f := by
  induction I with
  | atom n => exact term_le_sum f i
  | product a b ia ib =>
    exact OrderedWeight.trans (ib (fun j => f (i.1,j)) i.2)
      (ia (fun j => total b (fun k => f (j,k))) i.1)
structure Encoder (I : Shape) (L : Type u) where
  code : Carrier I → L
  injective : ∀ i j, code i=code j → i=j
def Encoder.pair {I J : Shape} {L : Type u} {M : Type v}
    (a : Encoder I L) (b : Encoder J M) : Encoder (.product I J) (L×M) where
  code p := (a.code p.1,b.code p.2)
  injective _p _q h := Prod.ext (a.injective _ _ (congrArg Prod.fst h))
    (b.injective _ _ (congrArg Prod.snd h))
theorem pair_code {I J : Shape} {L : Type u} {M : Type v}
    (a : Encoder I L) (b : Encoder J M) (i : Carrier I) (j : Carrier J) :
    (a.pair b).code (i,j)=(a.code i,b.code j) := rfl
end FiniteOutcomesV27
