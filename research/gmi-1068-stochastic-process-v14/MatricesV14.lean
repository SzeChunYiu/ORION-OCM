import WeightSumsV14
namespace StochasticV14
universe u
variable {α : Type u} [Weight α]
abbrev Matrix (α : Type u) (n m : Nat) := Fin n → Fin m → α
def mcomp {n m k : Nat} (p : Matrix α n m) (q : Matrix α m k) : Matrix α n k :=
  fun i k => sum (fun j => p i j*q j k)
def dirac {n m : Nat} (f : Fin n → Fin m) : Matrix α n m :=
  fun i j => if j=f i then 1 else 0
def mid (n : Nat) : Matrix α n n := dirac id

theorem mcomp_assoc {n m k l : Nat}
    (p : Matrix α n m) (q : Matrix α m k) (r : Matrix α k l) :
    mcomp (mcomp p q) r=mcomp p (mcomp q r) := by
  funext i z
  simp only [mcomp, ← sum_mul_right, ← sum_mul_left, Weight.mul_assoc]
  exact sum_swap (fun y x => p i x * (q x y*r y z))
theorem dirac_left {n m k : Nat} (f : Fin n → Fin m) (p : Matrix α m k) :
    mcomp (dirac f) p=fun i z => p (f i) z := by
  funext i z
  unfold mcomp dirac
  have e : (fun j => (if j=f i then (1:α) else 0)*p j z)=
      (fun j => if j=f i then p j z else 0) := by
    funext j
    split <;> simp only [Weight.one_mul, Weight.zero_mul]
  rw [e, sum_pick]
theorem mid_left {n m : Nat} (p : Matrix α n m) : mcomp (mid n) p=p :=
  dirac_left id p
theorem mid_right {n m : Nat} (p : Matrix α n m) : mcomp p (mid m)=p := by
  funext i z
  unfold mcomp mid dirac
  simp only [id]
  have e : (fun j => p i j*(if z=j then (1:α) else 0))=
      (fun j => if j=z then p i j else 0) := by
    funext j
    by_cases h : j=z
    · simp only [h, ↓reduceIte, Weight.mul_one]
    · simp only [h, Ne.symm h, ↓reduceIte, Weight.mul_zero]
  rw [e, sum_pick]
theorem dirac_comp {n m k : Nat} (f : Fin n → Fin m) (g : Fin m → Fin k) :
    mcomp (dirac (α:=α) f) (dirac g)=dirac (g ∘ f) := dirac_left f (dirac g)
theorem dirac_faithful {n m : Nat} {f g : Fin n → Fin m}
    (h : dirac (α:=α) f=dirac g) : f=g := by
  funext i
  have he := congrFun (congrFun h i) (f i)
  apply Classical.byContradiction
  intro hn
  simp only [dirac, ↓reduceIte, hn] at he
  exact Weight.one_ne_zero he

def Normalized {n m : Nat} (p : Matrix α n m) := ∀ i, sum (p i)=1
theorem dirac_normalized {n m : Nat} (f : Fin n → Fin m) :
    Normalized (dirac (α:=α) f) := by
  intro i
  exact sum_pick (fun _ => (1:α)) (f i)
theorem comp_normalized {n m k : Nat} {p : Matrix α n m} {q : Matrix α m k}
    (hp : Normalized p) (hq : Normalized q) : Normalized (mcomp p q) := by
  change ∀ j, sum (q j)=1 at hq
  intro i
  unfold mcomp
  rw [sum_swap]
  simp only [sum_mul_left, hq, Weight.mul_one]
  exact hp i

structure Kernel (α : Type u) [Weight α] (n m : Nat) where
  value : Matrix α n m
  normalized : Normalized value
namespace Kernel
@[ext] theorem ext {n m : Nat} {p q : Kernel α n m} (h : p.value=q.value) : p=q := by
  cases p; cases q; cases h; rfl
def comp {n m k : Nat} (p : Kernel α n m) (q : Kernel α m k) : Kernel α n k :=
  ⟨mcomp p.value q.value,comp_normalized p.normalized q.normalized⟩
def embed {n m : Nat} (f : Fin n → Fin m) : Kernel α n m :=
  ⟨dirac f,dirac_normalized f⟩
def ident (n : Nat) : Kernel α n n := embed id
theorem assoc {n m k l : Nat} (p : Kernel α n m) (q : Kernel α m k) (r : Kernel α k l) :
    comp (comp p q) r=comp p (comp q r) := ext (mcomp_assoc _ _ _)
theorem left_id {n m : Nat} (p : Kernel α n m) : comp (ident n) p=p := ext (mid_left _)
theorem right_id {n m : Nat} (p : Kernel α n m) : comp p (ident m)=p := ext (mid_right _)
theorem embed_comp {n m k : Nat} (f : Fin n → Fin m) (g : Fin m → Fin k) :
    comp (embed (α:=α) f) (embed g)=embed (g ∘ f) := ext (dirac_comp f g)
theorem embed_faithful {n m : Nat} {f g : Fin n → Fin m}
    (h : embed (α:=α) f=embed g) : f=g :=
  dirac_faithful (congrArg Kernel.value h)
theorem no_into_empty {n : Nat} (i : Fin n) : ¬ Nonempty (Kernel α n 0) := by
  rintro ⟨p⟩
  have h := p.normalized i
  exact Weight.one_ne_zero h.symm
theorem from_empty_unique {m : Nat} (p q : Kernel α 0 m) : p=q := by
  apply ext
  funext i
  exact Fin.elim0 i
end Kernel
end StochasticV14
