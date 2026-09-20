"""Exact typed registrations, including immutable V9 generic proof reuse."""
SOURCE_NAMES = ("RecoverabilityV9.lean", "PartialContextV15.lean",
                "QuotientOrderV15.lean", "SeparationV15.lean")
SOURCE_PATHS = ("research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean",
                "research/gmi-1068-partial-context-v15/PartialContextV15.lean",
                "research/gmi-1068-partial-context-v15/QuotientOrderV15.lean",
                "research/gmi-1068-partial-context-v15/SeparationV15.lean")
ENTRIES = (
("RecoverabilityV9.recoverable_iff_fiber_constant", """{M : Type u} {P : Type v} {O : Type w} (p : M → P) (o : M → O) :
 RecoverabilityV9.Recoverable p o ↔ RecoverabilityV9.FiberConstant p o := RecoverabilityV9.recoverable_iff_fiber_constant p o"""),
("RecoverabilityV9.no_recovery_of_collision", """{M : Type u} {P : Type v} {O : Type w} {p : M → P} {o : M → O}
 (m n : M) (hp : p m=p n) (ho : o m≠o n) :
 ¬ RecoverabilityV9.Recoverable p o := RecoverabilityV9.no_recovery_of_collision m n hp ho"""),
("restriction_admitted", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : Active P k) : P h.val := restriction_admitted P k h"""),
("restriction_value", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : Active P k) :
 restrictedEval P k h=k.eval ⟨h.val,h.property.2⟩ := restriction_value P k h"""),
("observe_illegal", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : H) (hp : ¬P h) :
 observe P k h=.illegal := observe_illegal P k h hp"""),
("observe_undefined", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : H)
 (hp : P h) (he : ¬k.defined h) : observe P k h=.undefined := observe_undefined P k h hp he"""),
("observe_value", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : H)
 (hp : P h) (he : k.defined h) : observe P k h=.value (k.eval ⟨h,he⟩) := observe_value P k h hp he"""),
("observe_has_value", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : H) :
 (∃ w, observe P k h=.value w) ↔ P h ∧ k.defined h := observe_has_value P k h"""),
("value_ne_undefined", """{W : Type v} (w : W) : Outcome.value w ≠ Outcome.undefined := value_ne_undefined w"""),
("value_ne_illegal", """{W : Type v} (w : W) : Outcome.value w ≠ Outcome.illegal := value_ne_illegal w"""),
("illegal_ne_undefined", """{W : Type v} : (Outcome.illegal : Outcome W) ≠ Outcome.undefined := illegal_ne_undefined"""),
("active_refl", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (a : Active P k) :
 (activeOrder P k).le a a := active_refl P k a"""),
("active_trans", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) {a b c : Active P k}
 (hab : (activeOrder P k).le a b) (hbc : (activeOrder P k).le b c) :
 (activeOrder P k).le a c := active_trans P k hab hbc"""),
("mutual_equivalence", """{A : Type u} (r : PreorderSpec A) : Equivalence (Mutual r) := mutual_equivalence r"""),
("comparison_invariant", """{A : Type u} (r : PreorderSpec A) {a b a' b' : A}
 (ha : Mutual r a a') (hb : Mutual r b b') : r.le a b ↔ r.le a' b' := comparison_invariant r ha hb"""),
("quotient_comparison", """{A : Type u} (r : PreorderSpec A) (a b : A) :
 quotientLE r (project r a) (project r b) ↔ r.le a b := quotient_comparison r a b"""),
("quotient_refl", """{A : Type u} (r : PreorderSpec A) (a : OrderedQuotient r) : quotientLE r a a := quotient_refl r a"""),
("quotient_trans", """{A : Type u} (r : PreorderSpec A) {a b c : OrderedQuotient r}
 (hab : quotientLE r a b) (hbc : quotientLE r b c) : quotientLE r a c := quotient_trans r hab hbc"""),
("quotient_antisymm", """{A : Type u} (r : PreorderSpec A) {a b : OrderedQuotient r}
 (hab : quotientLE r a b) (hba : quotientLE r b a) : a=b := quotient_antisymm r hab hba"""),
("project_eq_iff", """{A : Type u} (r : PreorderSpec A) (a b : A) : project r a=project r b ↔ Mutual r a b := project_eq_iff r a b"""),
("context_quotient_comparison", """{H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (a b : Active P k) :
 (contextQuotientOrder P k).le (project (activeOrder P k) a) (project (activeOrder P k) b) ↔
 k.order.le (restrictedEval P k a) (restrictedEval P k b) := context_quotient_comparison P k a b"""),
("opposite_strict", """{A : Type u} {W : Type v} (r : PreorderSpec W)
 (a b : A) (hne : a≠b) (lo hi : W) (hs : Strict r lo hi) :
 Strict r (preferLow a lo hi a) (preferLow a lo hi b) ∧
 Strict r (preferHigh a lo hi b) (preferHigh a lo hi a) := opposite_strict r a b hne lo hi hs"""),
("orders_different", """{A : Type u} {W : Type v} (r : PreorderSpec W)
 (a b : A) (hne : a≠b) (lo hi : W) (hs : Strict r lo hi) :
 (fun x y => r.le (preferLow a lo hi x) (preferLow a lo hi y)) ≠
 (fun x y => r.le (preferHigh a lo hi x) (preferHigh a lo hi y)) := orders_different r a b hne lo hi hs"""),
("fixed_process", """{A : Type u} {W : Type v} {Proc : Type w} {Allowed : (A → W) → Prop}
 (C : Proc) (m n : Models Allowed) : processObs C m=processObs C n := fixed_process C m n"""),
("fixed_nonrecovery", """{A : Type u} {W : Type v} {Proc : Type w} (C : Proc) (r : PreorderSpec W)
 (a b : A) (hne : a≠b) (lo hi : W) (hs : Strict r lo hi) (Allowed : (A → W) → Prop)
 (hl : Allowed (preferLow a lo hi)) (hh : Allowed (preferHigh a lo hi)) :
 ¬ RecoverabilityV9.Recoverable (processObs (Allowed:=Allowed) C) (orderingObs r) :=
 fixed_nonrecovery C r a b hne lo hi hs Allowed hl hh"""),
("constant_no_strict", """{W : Type v} (r : PreorderSpec W) (w : W) : ¬ Strict r w w := constant_no_strict r w"""),
("collapsed_no_strict", """{A : Type u} {X : Type x} {W : Type v} (r : PreorderSpec W)
 (obs : A → X) (f : X → W) (a b : A) (h : obs a=obs b) :
 ¬ Strict r (f (obs a)) (f (obs b)) := collapsed_no_strict r obs f a b h"""),
("admitted_nonrecovery", """{H : Type u} {W : Type v} {Proc : Type w}
 (C : Proc) (admitted : Proc → H → Prop) (D : RelativeDomain (admitted C))
 (r : PreorderSpec W) (a b : D.Carrier) (hne : a≠b) (lo hi : W) (hs : Strict r lo hi)
 (Allowed : (D.Carrier → W) → Prop) (hl : Allowed (preferLow a lo hi)) (hh : Allowed (preferHigh a lo hi)) :
 ¬ RecoverabilityV9.Recoverable (processObs (Allowed:=Allowed) C) (orderingObs r) :=
 admitted_nonrecovery C admitted D r a b hne lo hi hs Allowed hl hh"""),
)


def audit_source():
    header = "".join(f"import {name[:-5]}\n" for name in SOURCE_NAMES)
    header += "open PartialContextV15\nuniverse u v w x\n"
    return header + "\n".join(
        f"theorem registered_{number} {statement}\n"
        f"#print axioms registered_{number}\n"
        for number, (_, statement) in enumerate(ENTRIES)
    )
