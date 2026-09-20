"""Expected theorem types: changing a declaration to True cannot satisfy these."""
ENTRIES = (
("Path.append_assoc", """{V : Type u} {G : V → V → Type v} {a b c d : V}
 (p : Path G a b) (q : Path G b c) (r : Path G c d) :
 Path.append (Path.append p q) r = Path.append p (Path.append q r) :=
 Path.append_assoc p q r"""),
("Path.nil_append", """{V : Type u} {G : V → V → Type v} {a b : V}
 (p : Path G a b) : Path.append (.nil a) p = p := Path.nil_append p"""),
("Path.append_nil", """{V : Type u} {G : V → V → Type v} {a b : V}
 (p : Path G a b) : Path.append p (.nil b) = p := Path.append_nil p"""),
("eval_unique", """{V : Type u} {W : Type w} {G : V → V → Type v}
 (C : Category.{w,x} W) (obj : V → W)
 (edge : {a b : V} → G a b → C.Hom (obj a) (obj b))
 (f : {a b : V} → Path G a b → C.Hom (obj a) (obj b))
 (hnil : ∀ a, f (.nil a) = C.id (obj a))
 (happend : ∀ {a b c} (p : Path G a b) (q : Path G b c),
 f (Path.append p q) = C.comp (f p) (f q))
 (hedge : ∀ {a b} (e : G a b), f (Path.single e) = edge e)
 {a b : V} (p : Path G a b) : f p = eval C obj edge p :=
 eval_unique C obj edge f hnil happend hedge p"""),
("presentationIso", """{V : Type u} (C : Category.{u,v} V) :
 CategoryIso (presented C) C := presentationIso C"""),
("lower_quote", """{V : Type u} (C : Category.{u,v} V) {a b : V} (f : C.Hom a b) :
 lower C (quote C f) = f := lower_quote C f"""),
("quote_lower", """{V : Type u} (C : Category.{u,v} V) {a b : V}
 (p : (presented C).Hom a b) : quote C (lower C p) = p := quote_lower C p"""),
("lower_id", """{V : Type u} (C : Category.{u,v} V) (a : V) :
 lower C ((presented C).id a) = C.id a := lower_id C a"""),
("quote_id", """{V : Type u} (C : Category.{u,v} V) (a : V) :
 quote C (C.id a) = (presented C).id a := quote_id C a"""),
("lower_comp", """{V : Type u} (C : Category.{u,v} V) {a b c : V}
 (p : (presented C).Hom a b) (q : (presented C).Hom b c) :
 lower C ((presented C).comp p q) = C.comp (lower C p) (lower C q) := lower_comp C p q"""),
("quote_comp", """{V : Type u} (C : Category.{u,v} V) {a b c : V}
 (f : C.Hom a b) (g : C.Hom b c) :
 quote C (C.comp f g) = (presented C).comp (quote C f) (quote C g) := quote_comp C f g"""),
("eval_append", """{V : Type u} {W : Type w} {G : V → V → Type v}
 (C : Category.{w,x} W) (obj : V → W)
 (edge : {a b : V} → G a b → C.Hom (obj a) (obj b))
 {a b c : V} (p : Path G a b) (q : Path G b c) :
 eval C obj edge (Path.append p q) = C.comp (eval C obj edge p) (eval C obj edge q) :=
 eval_append C obj edge p q"""),
("RecoverabilityV9.process_does_not_recover_context", """:
 ¬ RecoverabilityV9.Recoverable RecoverabilityV9.process RecoverabilityV9.objective :=
 RecoverabilityV9.process_does_not_recover_context"""),
("RecoverabilityV9.actual_ranking_reversal", """:
 RecoverabilityV9.evaluation true RecoverabilityV9.aHistory = true ∧
 RecoverabilityV9.evaluation true RecoverabilityV9.bHistory = false ∧
 RecoverabilityV9.evaluation false RecoverabilityV9.aHistory = false ∧
 RecoverabilityV9.evaluation false RecoverabilityV9.bHistory = true :=
 RecoverabilityV9.actual_ranking_reversal"""),
)


def audit_source():
    header = "import QuotientPathsV11\nimport RecoverabilityV9\nopen TypedPathsV11\nuniverse u v w x\n"
    checks = []
    for number, (target, statement) in enumerate(ENTRIES):
        # presentationIso is data, so use a def for its explicitly checked type.
        declaration = "def" if target == "presentationIso" else "theorem"
        checks.append(f"{declaration} registered_{number} {statement}\n#print axioms registered_{number}\n")
    return header + "\n".join(checks)
