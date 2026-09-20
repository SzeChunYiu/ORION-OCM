"""Explicit theorem statements for concrete optional-structure countermodels."""
SOURCE_NAMES = ("InterchangeV13.lean", "DiscreteMonoidalV13.lean", "LoopMonoidalV13.lean")
ENTRIES = (
("operations_coincide", """{α : Type u} (seq tensor : α → α → α) (e : α)
 (sl : ∀ a, seq e a=a) (sr : ∀ a, seq a e=a)
 (tl : ∀ a, tensor e a=a) (tr : ∀ a, tensor a e=a)
 (inter : ∀ a b c d, tensor (seq a b) (seq c d)=seq (tensor a c) (tensor b d)) (a b : α) : seq a b=tensor a b := operations_coincide seq tensor e sl sr tl tr inter a b"""),
("operations_commute", """{α : Type u} (seq tensor : α → α → α) (e : α)
 (sl : ∀ a, seq e a=a) (sr : ∀ a, seq a e=a)
 (tl : ∀ a, tensor e a=a) (tr : ∀ a, tensor a e=a)
 (inter : ∀ a b c d, tensor (seq a b) (seq c d)=seq (tensor a c) (tensor b d)) (a b : α) : seq a b=seq b a := operations_commute seq tensor e sl sr tl tr inter a b"""),
("sequence_actual", """(f g : BitProc) (b : Bool) : act (sequence f g) b=act g (act f b) := sequence_actual f g b"""),
("act_faithful", """{f g : BitProc} (h : ∀ b, act f b=act g b) : f=g := act_faithful h"""),
("sequence_assoc", """(f g h : BitProc) : sequence (sequence f g) h=sequence f (sequence g h) := sequence_assoc f g h"""),
("sequence_left", """(f : BitProc) : sequence .identity f=f := sequence_left f"""),
("sequence_right", """(f : BitProc) : sequence f .identity=f := sequence_right f"""),
("invertible_iff_identity", """(f : BitProc) : (∃ g, sequence f g=.identity ∧ sequence g f=.identity) ↔ f=.identity := invertible_iff_identity f"""),
("resets_noncommute", """: sequence .reset0 .reset1 ≠ sequence .reset1 .reset0 := resets_noncommute"""),
("weak_unitors_forced", """{tensor : BitProc → BitProc → BitProc} (h : WeakTensorData tensor) :
 h.leftUnitor=.identity ∧ h.rightUnitor=.identity := weak_unitors_forced h"""),
("tensor_units_derived", """{tensor : BitProc → BitProc → BitProc} (h : WeakTensorData tensor) :
 (∀ f, tensor .identity f=f) ∧ (∀ f, tensor f .identity=f) := tensor_units_derived h"""),
("no_any_tensor", """: ¬ ∃ tensor, Nonempty (WeakTensorData tensor) := no_any_tensor"""),
("xor_interchange", """(a b c d : Bool) : Bool.xor (Bool.xor a b) (Bool.xor c d)=
 Bool.xor (Bool.xor a c) (Bool.xor b d) := xor_interchange a b c d"""),
("discrete_assoc", """{a b c d : BitProc} (f : DiscreteHom a b) (g : DiscreteHom b c) (h : DiscreteHom c d) :
 discreteComp (discreteComp f g) h=discreteComp f (discreteComp g h) := discrete_assoc f g h"""),
("discrete_left", """{a b : BitProc} (f : DiscreteHom a b) : discreteComp (discreteId a) f=f := discrete_left f"""),
("discrete_right", """{a b : BitProc} (f : DiscreteHom a b) : discreteComp f (discreteId b)=f := discrete_right f"""),
("discrete_tensor_interchange", """{a b c d e f : BitProc} (p : DiscreteHom a b) (q : DiscreteHom b c)
 (r : DiscreteHom d e) (s : DiscreteHom e f) :
 discreteTensor (discreteComp p q) (discreteComp r s)=
 discreteComp (discreteTensor p r) (discreteTensor q s) := discrete_tensor_interchange p q r s"""),
("discreteAssociator", """(a b c : BitProc) : DiscreteHom (sequence (sequence a b) c) (sequence a (sequence b c)) := discreteAssociator a b c"""),
("discreteLeftUnitor", """(a : BitProc) : DiscreteHom (sequence .identity a) a := discreteLeftUnitor a"""),
("discreteRightUnitor", """(a : BitProc) : DiscreteHom (sequence a .identity) a := discreteRightUnitor a"""),
("discrete_coherence", """{a b : BitProc} (f g : DiscreteHom a b) : f=g := discrete_coherence f g"""),
("no_discrete_braiding", """: ¬ ∀ a b, DiscreteHom (sequence a b) (sequence b a) := no_discrete_braiding"""),
("LoopHom.comp_assoc", """{a b c d : BitProc} (f : LoopHom a b) (g : LoopHom b c) (h : LoopHom c d) :
 LoopHom.comp (LoopHom.comp f g) h=LoopHom.comp f (LoopHom.comp g h) := LoopHom.comp_assoc f g h"""),
("LoopHom.left_id", """{a b : BitProc} (f : LoopHom a b) : LoopHom.comp (LoopHom.ident a) f=f := LoopHom.left_id f"""),
("LoopHom.right_id", """{a b : BitProc} (f : LoopHom a b) : LoopHom.comp f (LoopHom.ident b)=f := LoopHom.right_id f"""),
("LoopHom.tensor_ident", """(a b : BitProc) : LoopHom.tensor (LoopHom.ident a) (LoopHom.ident b)=LoopHom.ident (sequence a b) := LoopHom.tensor_ident a b"""),
("LoopHom.tensor_interchange", """{a b c d e f : BitProc} (p : LoopHom a b) (q : LoopHom b c)
 (r : LoopHom d e) (s : LoopHom e f) :
 LoopHom.tensor (LoopHom.comp p q) (LoopHom.comp r s)=
 LoopHom.comp (LoopHom.tensor p r) (LoopHom.tensor q s) := LoopHom.tensor_interchange p q r s"""),
("LoopHom.structural_inverse", """{a b : BitProc} (h : a=b) :
 LoopHom.comp (LoopHom.structural h) (LoopHom.structural h.symm)=LoopHom.ident a ∧
 LoopHom.comp (LoopHom.structural h.symm) (LoopHom.structural h)=LoopHom.ident b := LoopHom.structural_inverse h"""),
("LoopHom.associator_natural", """{a b c d e f : BitProc} (p : LoopHom a d) (q : LoopHom b e) (r : LoopHom c f) :
 LoopHom.comp (LoopHom.tensor (LoopHom.tensor p q) r) (LoopHom.associator d e f)=
 LoopHom.comp (LoopHom.associator a b c) (LoopHom.tensor p (LoopHom.tensor q r)) := LoopHom.associator_natural p q r"""),
("LoopHom.leftUnitor_natural", """{a b : BitProc} (f : LoopHom a b) :
 LoopHom.comp (LoopHom.tensor (LoopHom.ident .identity) f) (LoopHom.leftUnitor b)=
 LoopHom.comp (LoopHom.leftUnitor a) f := LoopHom.leftUnitor_natural f"""),
("LoopHom.rightUnitor_natural", """{a b : BitProc} (f : LoopHom a b) :
 LoopHom.comp (LoopHom.tensor f (LoopHom.ident .identity)) (LoopHom.rightUnitor b)=
 LoopHom.comp (LoopHom.rightUnitor a) f := LoopHom.rightUnitor_natural f"""),
("LoopHom.pentagon", """(a b c d : BitProc) :
 LoopHom.comp (LoopHom.associator (sequence a b) c d) (LoopHom.associator a b (sequence c d))=
 LoopHom.comp (LoopHom.comp (LoopHom.tensor (LoopHom.associator a b c) (LoopHom.ident d))
 (LoopHom.associator a (sequence b c) d)) (LoopHom.tensor (LoopHom.ident a) (LoopHom.associator b c d)) := LoopHom.pentagon a b c d"""),
("LoopHom.triangle", """(a b : BitProc) :
 LoopHom.comp (LoopHom.associator a .identity b) (LoopHom.tensor (LoopHom.ident a) (LoopHom.leftUnitor b))=
 LoopHom.tensor (LoopHom.rightUnitor a) (LoopHom.ident b) := LoopHom.triangle a b"""),
("LoopHom.toggle_nonidentity", """(a : BitProc) : LoopHom.toggle a ≠ LoopHom.ident a := LoopHom.toggle_nonidentity a"""),
("LoopHom.toggle_involution", """(a : BitProc) : LoopHom.comp (LoopHom.toggle a) (LoopHom.toggle a)=LoopHom.ident a := LoopHom.toggle_involution a"""),
("LoopHom.no_braiding_component", """: ¬ Nonempty (LoopHom (sequence .reset0 .reset1) (sequence .reset1 .reset0)) := LoopHom.no_braiding_component"""),
("LoopHom.no_braiding", """: ¬ ∀ a b, Nonempty (LoopHom (sequence a b) (sequence b a)) := LoopHom.no_braiding"""),
)


def audit_source():
    header = ("import InterchangeV13\nimport DiscreteMonoidalV13\n"
              "import LoopMonoidalV13\nopen OptionalV13\nuniverse u\n")
    return header + "\n".join(
        f"theorem registered_{number} {statement}\n"
        f"#print axioms registered_{number}\n"
        for number, (_, statement) in enumerate(ENTRIES)
    )
