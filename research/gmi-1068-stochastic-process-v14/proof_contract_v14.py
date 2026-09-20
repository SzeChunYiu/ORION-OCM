"""Exact typed proof registrations for generic laws and actual rational kernels."""
SOURCE_NAMES = ("WeightSumsV14.lean", "MatricesV14.lean", "RelationsV14.lean",
                "SupportV14.lean", "RationalModelV14.lean")
ENTRIES = (
("natWeight", """: Weight Nat := natWeight"""),
("sum_support", """{α : Type u} [Weight α] {n : Nat} (f : Fin n → α) : sum f≠0 ↔ ∃ i, f i≠0 := sum_support f"""),
("mul_support", """{α : Type u} [Weight α] (a b : α) : a*b≠0 ↔ a≠0 ∧ b≠0 := mul_support a b"""),
("mcomp_assoc", """{α : Type u} [Weight α] {n m k l : Nat} (p : Matrix α n m) (q : Matrix α m k) (r : Matrix α k l) :
 mcomp (mcomp p q) r=mcomp p (mcomp q r) := mcomp_assoc p q r"""),
("comp_normalized", """{α : Type u} [Weight α] {n m k : Nat} {p : Matrix α n m} {q : Matrix α m k}
 (hp : Normalized p) (hq : Normalized q) : Normalized (mcomp p q) := comp_normalized hp hq"""),
("Kernel.assoc", """{α : Type u} [Weight α] {n m k l : Nat} (p : Kernel α n m) (q : Kernel α m k) (r : Kernel α k l) :
 Kernel.comp (Kernel.comp p q) r=Kernel.comp p (Kernel.comp q r) := Kernel.assoc p q r"""),
("Kernel.left_id", """{α : Type u} [Weight α] {n m : Nat} (p : Kernel α n m) : Kernel.comp (Kernel.ident n) p=p := Kernel.left_id p"""),
("Kernel.right_id", """{α : Type u} [Weight α] {n m : Nat} (p : Kernel α n m) : Kernel.comp p (Kernel.ident m)=p := Kernel.right_id p"""),
("Kernel.embed_comp", """{α : Type u} [Weight α] {n m k : Nat} (f : Fin n → Fin m) (g : Fin m → Fin k) :
 Kernel.comp (Kernel.embed (α:=α) f) (Kernel.embed g)=Kernel.embed (g ∘ f) := Kernel.embed_comp f g"""),
("Kernel.embed_faithful", """{α : Type u} [Weight α] {n m : Nat} {f g : Fin n → Fin m}
 (h : Kernel.embed (α:=α) f=Kernel.embed g) : f=g := Kernel.embed_faithful h"""),
("Kernel.no_into_empty", """{α : Type u} [Weight α] {n : Nat} (i : Fin n) : ¬ Nonempty (Kernel α n 0) := Kernel.no_into_empty i"""),
("Kernel.from_empty_unique", """{α : Type u} [Weight α] {m : Nat} (p q : Kernel α 0 m) : p=q := Kernel.from_empty_unique p q"""),
("TotalRel.assoc", """{A : Type u} {B : Type v} {C : Type w} {D : Type x}
 (r : TotalRel A B) (s : TotalRel B C) (t : TotalRel C D) :
 TotalRel.comp (TotalRel.comp r s) t=TotalRel.comp r (TotalRel.comp s t) := TotalRel.assoc r s t"""),
("TotalRel.left_id", """{A : Type u} {B : Type v} (r : TotalRel A B) : TotalRel.comp (TotalRel.ident A) r=r := TotalRel.left_id r"""),
("TotalRel.right_id", """{A : Type u} {B : Type v} (r : TotalRel A B) : TotalRel.comp r (TotalRel.ident B)=r := TotalRel.right_id r"""),
("TotalRel.graph_comp", """{A : Type u} {B : Type v} {C : Type w} (f : A → B) (g : B → C) :
 TotalRel.comp (TotalRel.graph f) (TotalRel.graph g)=TotalRel.graph (g ∘ f) := TotalRel.graph_comp f g"""),
("TotalRel.graph_faithful", """{A : Type u} {B : Type v} {f g : A → B} (h : TotalRel.graph f=TotalRel.graph g) : f=g := TotalRel.graph_faithful h"""),
("TotalRel.no_into_empty", """{A : Type u} (a : A) : ¬ Nonempty (TotalRel A Empty) := TotalRel.no_into_empty a"""),
("TotalRel.from_empty_unique", """{B : Type v} (r s : TotalRel Empty B) : r=s := TotalRel.from_empty_unique r s"""),
("Kernel.support_comp", """{α : Type u} [Weight α] {n m k : Nat} (p : Kernel α n m) (q : Kernel α m k) :
 Kernel.support (Kernel.comp p q)=TotalRel.comp (Kernel.support p) (Kernel.support q) := Kernel.support_comp p q"""),
("Kernel.support_embed", """{α : Type u} [Weight α] {n m : Nat} (f : Fin n → Fin m) :
 Kernel.support (Kernel.embed (α:=α) f)=TotalRel.graph f := Kernel.support_embed f"""),
("Kernel.support_ident", """{α : Type u} [Weight α] (n : Nat) :
 Kernel.support (Kernel.ident (α:=α) n)=TotalRel.ident (Fin n) := Kernel.support_ident n"""),
("RationalModel.normalized", """(f : RationalModel.Arrow) (x : Bool) :
 RationalModel.matrix f x false+RationalModel.matrix f x true=1 := RationalModel.normalized f x"""),
("RationalModel.nonnegative", """(f : RationalModel.Arrow) (x y : Bool) : (0:RationalModel.Q) ≤ RationalModel.matrix f x y := RationalModel.nonnegative f x y"""),
("RationalModel.actual_comp", """(f g : RationalModel.Arrow) (x z : Bool) :
 RationalModel.matrix (RationalModel.comp f g) x z=
 RationalModel.matrix f x false*RationalModel.matrix g false z+RationalModel.matrix f x true*RationalModel.matrix g true z := RationalModel.actual_comp f g x z"""),
("RationalModel.matrix_faithful", """{f g : RationalModel.Arrow} (h : ∀ x y, RationalModel.matrix f x y=RationalModel.matrix g x y) : f=g := RationalModel.matrix_faithful h"""),
("RationalModel.assoc", """(f g h : RationalModel.Arrow) :
 RationalModel.comp (RationalModel.comp f g) h=RationalModel.comp f (RationalModel.comp g h) := RationalModel.assoc f g h"""),
("RationalModel.left_id", """(f : RationalModel.Arrow) : RationalModel.comp .identity f=f := RationalModel.left_id f"""),
("RationalModel.right_id", """(f : RationalModel.Arrow) : RationalModel.comp f .identity=f := RationalModel.right_id f"""),
("RationalModel.encode_dirac", """(f : Bool → Bool) (x y : Bool) : RationalModel.matrix (RationalModel.encode f) x y=(if y=f x then 1 else 0) := RationalModel.encode_dirac f x y"""),
("RationalModel.encode_identity", """: RationalModel.encode id=.identity := RationalModel.encode_identity"""),
("RationalModel.encode_comp", """(f g : Bool → Bool) :
 RationalModel.comp (RationalModel.encode f) (RationalModel.encode g)=RationalModel.encode (g ∘ f) := RationalModel.encode_comp f g"""),
("RationalModel.encode_faithful", """{f g : Bool → Bool} (h : RationalModel.encode f=RationalModel.encode g) : f=g := RationalModel.encode_faithful h"""),
("RationalModel.reduced_entries", """(f : RationalModel.Arrow) (x y : Bool) :
 0 < (RationalModel.matrix f x y).den ∧
 Nat.gcd (RationalModel.matrix f x y).num.natAbs (RationalModel.matrix f x y).den=1 := RationalModel.reduced_entries f x y"""),
("RationalModel.event_probabilities", """:
 RationalModel.matrix .third false true=RationalModel.frac 1 3 ∧
 RationalModel.matrix .half false true=RationalModel.frac 1 2 ∧
 RationalModel.matrix .twoThirds false true=RationalModel.frac 2 3 := RationalModel.event_probabilities"""),
("RationalModel.half_nontrivial", """: RationalModel.matrix .half false true≠0 ∧ RationalModel.matrix .half false true≠1 := RationalModel.half_nontrivial"""),
("RationalModel.support_probability_loss", """:
 (∀ x y, RationalModel.support .third x y ↔ RationalModel.support .twoThirds x y) ∧
 RationalModel.matrix .third false true≠RationalModel.matrix .twoThirds false true := RationalModel.support_probability_loss"""),
)


def audit_source():
    header = "".join(f"import {name[:-5]}\n" for name in SOURCE_NAMES)
    header += "open StochasticV14\nuniverse u v w x\n"
    checks = []
    for number, (target, statement) in enumerate(ENTRIES):
        declaration = "def" if target == "natWeight" else "theorem"
        checks.append(f"{declaration} registered_{number} {statement}\n"
                      f"#print axioms registered_{number}\n")
    return header + "\n".join(checks)
