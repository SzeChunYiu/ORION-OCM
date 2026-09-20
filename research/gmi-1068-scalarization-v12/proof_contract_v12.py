"""Explicit theorem-type contracts, including a concrete integer specialization."""
SOURCE_NAMES = ("ScalarLawsV12.lean", "FiniteSumsV12.lean", "ScalarizationV12.lean")
ENTRIES = (
("intScalar", """: Scalar Int := intScalar"""),
("Scalar.zero_lt_one", """{α : Type u} [Scalar α] : (0 : α) < 1 :=
 Scalar.zero_lt_one"""),
("magnitude_bounds", """{α : Type u} [Scalar α] (a : α) :
 0 ≤ magnitude a ∧ -a ≤ magnitude a := magnitude_bounds a"""),
("dot_monotone", """{α : Type u} [Scalar α] {n : Nat} {w x y : Fin n → α}
 (hw : Nonnegative w) (h : CoordLE x y) : dot w x ≤ dot w y :=
 dot_monotone hw h"""),
("dot_strict", """{α : Type u} [Scalar α] {n : Nat} {w x y : Fin n → α}
 (hw : Nonnegative w) (h : CoordLE x y)
 (k : Fin n) (hk : x k < y k) (hwk : 0 < w k) : dot w x < dot w y :=
 dot_strict hw h k hk hwk"""),
("dot_difference", """{α : Type u} [Scalar α] {n : Nat} (w x y : Fin n → α) :
 dot w (fun i => x i + -y i) = dot w x + -(dot w y) := dot_difference w x y"""),
("separator_positive", """{α : Type u} [Scalar α] {n : Nat} (d : Fin n → α)
 (k : Fin n) (h : 0 < d k) : Positive (separator d k) :=
 separator_positive d k h"""),
("separator_formula", """{α : Type u} [Scalar α] {n : Nat} (d : Fin n → α)
 (k : Fin n) : dot (separator d k) d =
 d k * ((except (fun j => magnitude (d j)) k + 1) + except d k) :=
 separator_formula d k"""),
("separator_dot_positive", """{α : Type u} [Scalar α] {n : Nat} (d : Fin n → α)
 (k : Fin n) (h : 0 < d k) : 0 < dot (separator d k) d :=
 separator_dot_positive d k h"""),
("separating_weight", """{α : Type u} [Scalar α] {n : Nat} {x y : Fin n → α}
 (h : ¬ CoordLE x y) : ∃ w, Positive w ∧ dot w y < dot w x :=
 separating_weight h"""),
("positive_family_recovers_order", """{α : Type u} [Scalar α] {n : Nat}
 (x y : Fin n → α) :
 CoordLE x y ↔ ∀ w, Positive w → dot w x ≤ dot w y :=
 positive_family_recovers_order x y"""),
("incomparable_reversal", """{α : Type u} [Scalar α] {n : Nat}
 {x y : Fin n → α} (hxy : ¬ CoordLE x y) (hyx : ¬ CoordLE y x) :
 ∃ w v, Positive w ∧ Positive v ∧ dot w x < dot w y ∧ dot v y < dot v x :=
 incomparable_reversal hxy hyx"""),
("no_total_scalar_reflection", """{X : Type u} {β : Type v} [LE β]
 (total : ∀ a b : β, a ≤ b ∨ b ≤ a) (r : X → X → Prop)
 (x y : X) (hxy : ¬ r x y) (hyx : ¬ r y x) :
 ¬ ∃ f : X → β, ∀ a b, f a ≤ f b → r a b :=
 no_total_scalar_reflection total r x y hxy hyx"""),
("coordinate_no_total_reflection", """{α : Type u} [Scalar α] {n : Nat}
 {D : (Fin n → α) → Prop} {β : Type v} [LE β]
 (total : ∀ a b : β, a ≤ b ∨ b ≤ a)
 (x y : {v : Fin n → α // D v})
 (hxy : ¬ CoordLE x.val y.val) (hyx : ¬ CoordLE y.val x.val) :
 ¬ ∃ f : {v : Fin n → α // D v} → β,
 ∀ a b, f a ≤ f b → CoordLE a.val b.val :=
 coordinate_no_total_reflection total x y hxy hyx"""),
("positive_minimizer_efficient", """{α : Type u} [Scalar α] {n : Nat}
 {D : (Fin n → α) → Prop} {w x : Fin n → α}
 (hw : Positive w) (hm : Minimizer D w x) : ParetoEfficient D x :=
 positive_minimizer_efficient hw hm"""),
("positive_family_recovers_order[α=Int]", """{n : Nat} (x y : Fin n → Int) :
 (∀ i, Int.le (x i) (y i)) ↔
 ∀ w : Fin n → Int, (∀ i, Int.lt 0 (w i)) → Int.le (dot w x) (dot w y) :=
 positive_family_recovers_order x y"""),
("dot_strict[α=Int]", """{n : Nat} {w x y : Fin n → Int}
 (hw : ∀ i, Int.le 0 (w i)) (h : ∀ i, Int.le (x i) (y i))
 (k : Fin n) (hk : Int.lt (x k) (y k)) (hwk : Int.lt 0 (w k)) :
 Int.lt (dot w x) (dot w y) :=
 dot_strict (α := Int) (w := w) (x := x) (y := y) hw h k hk hwk"""),
)


def audit_source():
    header = ("import ScalarLawsV12\nimport FiniteSumsV12\n"
              "import ScalarizationV12\nopen ScalarV12\nuniverse u v\n")
    checks = []
    for number, (target, statement) in enumerate(ENTRIES):
        declaration = "def" if target == "intScalar" else "theorem"
        checks.append(f"{declaration} registered_{number} {statement}\n"
                      f"#print axioms registered_{number}\n")
    return header + "\n".join(checks)
