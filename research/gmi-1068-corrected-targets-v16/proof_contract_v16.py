"""Exact typed replay of new proofs and immutable mathematical dependencies."""
SOURCE_PATHS = (
    "research/gmi-1068-typed-foundation-v11/TypedPathsV11.lean",
    "research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean",
    "research/gmi-1068-foundation-repair-v5/AdmissibilityV5.lean",
    "research/gmi-1068-scalarization-v12/ScalarLawsV12.lean",
    "research/gmi-1068-scalarization-v12/FiniteSumsV12.lean",
    "research/gmi-1068-corrected-targets-v16/HistoryAdmissionV16.lean",
    "research/gmi-1068-corrected-targets-v16/GroupLawsV16.lean",
    "research/gmi-1068-corrected-targets-v16/CompositionContextV16.lean",
    "research/gmi-1068-corrected-targets-v16/LinearBasisV16.lean",
    "research/gmi-1068-corrected-targets-v16/PositiveAggregationV16.lean",
)
SOURCE_NAMES = tuple(path.rsplit("/", 1)[1] for path in SOURCE_PATHS)
ENTRIES = (
    ("GroupLawsV16.category_comp", """(m : Law) (a b : Label) : (GroupLawsV16.category m).comp (a:=()) (b:=()) (c:=()) (a : (GroupLawsV16.category m).Hom () ()) (b : (GroupLawsV16.category m).Hom () ()) = m.comp a b := category_comp m a b"""),
    ("GroupLawsV16.category_id", """(m : Law) : (GroupLawsV16.category m).id () = Label.zero := category_id m"""),
    ("HistoryAdmissionV16.admitted_single", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) {a b : V} (e : G a b) : Admitted @P (TypedPathsV11.Path.single e) ↔ P e := admitted_single @P e"""),
    ("HistoryAdmissionV16.admitted_iff_lift", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) {a b : V} (p : TypedPathsV11.Path G a b) : Admitted @P p ↔ ∃ q : TypedPathsV11.Path (Edges @P) a b, erase @P q = p := admitted_iff_lift @P p"""),
    ("HistoryAdmissionV16.forget_restore", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) {a b : V} (p : Raw @P a b) : forget @P (restore @P p) = p := forget_restore @P p"""),
    ("HistoryAdmissionV16.restore_forget", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) {a b : V} (p : TypedPathsV11.Path (Edges @P) a b) : restore @P (forget @P p) = p := restore_forget @P p"""),
    ("HistoryAdmissionV16.forget_empty", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) (a : V) : forget @P (.nil a) = empty @P a := forget_empty @P a"""),
    ("HistoryAdmissionV16.restore_empty", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) (a : V) : restore @P (empty @P a) = .nil a := restore_empty @P a"""),
    ("HistoryAdmissionV16.forget_concat", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) {a b c : V} (p : TypedPathsV11.Path (Edges @P) a b) (q : TypedPathsV11.Path (Edges @P) b c) : forget @P (TypedPathsV11.Path.append p q) = concat @P (forget @P p) (forget @P q) := forget_concat @P p q"""),
    ("HistoryAdmissionV16.restore_concat", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) {a b c : V} (p : Raw @P a b) (q : Raw @P b c) : restore @P (concat @P p q) = TypedPathsV11.Path.append (restore @P p) (restore @P q) := restore_concat @P p q"""),
    ("HistoryAdmissionV16.decode_admission", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) {a b : V} (e : G a b) : decode (Admitted @P) e ↔ P e := decode_admission @P e"""),
    ("HistoryAdmissionV16.domain_eq_iff_admission_eq", """{V : Type u} {G : V → V → Type v} (P : {a b : V} → G a b → Prop) (Q : {a b : V} → G a b → Prop) : (∀ {a b} (p : TypedPathsV11.Path G a b), Admitted @P p ↔ Admitted @Q p) ↔ (∀ {a b} (e : G a b), P e ↔ Q e) := domain_eq_iff_admission_eq @P @Q"""),
    ("GroupLawsV16.c4_is_modulo", """(a b : Label) : number (c4mul a b) = (number a + number b) % 4 := c4_is_modulo a b"""),
    ("GroupLawsV16.v4_is_xor", """(a b : Label) : number (v4mul a b) = Nat.xor (number a) (number b) := v4_is_xor a b"""),
    ("GroupLawsV16.c4_assoc", """(a b c : Label) : c4.comp (c4.comp a b) c = c4.comp a (c4.comp b c) := c4_assoc a b c"""),
    ("GroupLawsV16.c4_units", """(a : Label) : c4.comp .zero a = a ∧ c4.comp a .zero = a := c4_units a"""),
    ("GroupLawsV16.c4_parity_comp", """(a b : Label) : parity (c4.comp a b) = Bool.xor (parity a) (parity b) := c4_parity_comp a b"""),
    ("GroupLawsV16.v4_assoc", """(a b c : Label) : v4.comp (v4.comp a b) c = v4.comp a (v4.comp b c) := v4_assoc a b c"""),
    ("GroupLawsV16.v4_units", """(a : Label) : v4.comp .zero a = a ∧ v4.comp a .zero = a := v4_units a"""),
    ("GroupLawsV16.v4_parity_comp", """(a b : Label) : parity (v4.comp a b) = Bool.xor (parity a) (parity b) := v4_parity_comp a b"""),
    ("GroupLawsV16.category", """(m : Law) : TypedPathsV11.Category Unit := GroupLawsV16.category m"""),
    ("GroupLawsV16.actual_products", """: c4.comp .one .one = .two ∧ v4.comp .one .one = .zero := actual_products"""),
    ("CompositionContextV16.fold_parity", """(m : Law) (h : ∀ a b, parity (m.comp a b) = Bool.xor (parity a) (parity b)) (w : List Label) : parity (product m w) = rawParity w := fold_parity m h w"""),
    ("CompositionContextV16.all_word_context_eq", """(w : List Label) : parity (product c4 w) = parity (product v4 w) := all_word_context_eq w"""),
    ("CompositionContextV16.full_context_eq", """: context c4 = context v4 := full_context_eq"""),
    ("CompositionContextV16.context_nonconstant", """(m : Law) : (context m).value [] trivial ≠ (context m).value [.one] trivial := context_nonconstant m"""),
    ("RecoverabilityV9.no_recovery_of_collision", """{M : Type u} {P : Type v} {O : Type w} {p : M → P} {o : M → O} (m n : M) (hp : p m=p n) (ho : o m≠o n) : ¬ RecoverabilityV9.Recoverable p o := RecoverabilityV9.no_recovery_of_collision m n hp ho"""),
    ("CompositionContextV16.composition_not_recoverable", """: ¬ RecoverabilityV9.Recoverable context Law.comp := composition_not_recoverable"""),
    ("CompositionContextV16.kernel_witness", """: evaluationKernel c4 [.one,.one] [.two] ∧ ¬ evaluationKernel v4 [.one,.one] [.two] := kernel_witness"""),
    ("CompositionContextV16.evaluation_kernels_different", """: evaluationKernel c4 ≠ evaluationKernel v4 := evaluation_kernels_different"""),
    ("LinearBasisV16.linear_zero", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} {F : (Fin n → α) → α} (h : IsLinear F) : F (fun _ => 0) = 0 := linear_zero h"""),
    ("LinearBasisV16.basis_expansion", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} (x : Fin n → α) : (fun j => ScalarV12.sum (fun i => x i * basis i j)) = x := basis_expansion x"""),
    ("LinearBasisV16.linear_basis_representation", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} {F : (Fin n → α) → α} (h : IsLinear F) (x : Fin n → α) : F x = ScalarV12.dot (weights F) x := linear_basis_representation h x"""),
    ("LinearBasisV16.representation_unique", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} {F : (Fin n → α) → α} (w : Fin n → α) (h : ∀ x, F x = ScalarV12.dot w x) : w = weights F := representation_unique w h"""),
    ("LinearBasisV16.dot_linear", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} (w : Fin n → α) : IsLinear (ScalarV12.dot w) := dot_linear w"""),
    ("LinearBasisV16.unique_linear_representation", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} {F : (Fin n → α) → α} (h : IsLinear F) : ∃ w, (∀ x, F x = ScalarV12.dot w x) ∧ ∀ v, (∀ x, F x = ScalarV12.dot v x) → v=w := unique_linear_representation h"""),
    ("PositiveAggregationV16.monotone_iff_nonnegative", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} {F : (Fin n → α) → α} (h : IsLinear F) : PositiveAggregationV16.Monotone F ↔ ScalarV12.Nonnegative (weights F) := monotone_iff_nonnegative h"""),
    ("PositiveAggregationV16.normalized_iff_sum_one", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} {F : (Fin n → α) → α} (h : IsLinear F) : F (fun _ => 1) = 1 ↔ ScalarV12.sum (weights F) = 1 := normalized_iff_sum_one h"""),
    ("PositiveAggregationV16.probability_coefficients", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} (w : Fin n → α) (hp : ScalarV12.Nonnegative w) (hn : ScalarV12.sum w = 1) : IsLinear (ScalarV12.dot w) ∧ PositiveAggregationV16.Monotone (ScalarV12.dot w) ∧ ScalarV12.dot w (fun _ => 1) = 1 := probability_coefficients w hp hn"""),
    ("PositiveAggregationV16.probability_representation_iff", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} (F : (Fin n → α) → α) : (IsLinear F ∧ PositiveAggregationV16.Monotone F ∧ F (fun _ => 1) = 1) ↔ ∃ w : Fin n → α, ScalarV12.Nonnegative w ∧ ScalarV12.sum w = 1 ∧ ∀ x, F x = ScalarV12.dot w x := probability_representation_iff F"""),
    ("PositiveAggregationV16.probability_representation_unique", """{α : Type u} [ScalarV12.Scalar α] {n : Nat} (F : (Fin n → α) → α) (h : IsLinear F ∧ PositiveAggregationV16.Monotone F ∧ F (fun _ => 1) = 1) : ∃ w : Fin n → α, (ScalarV12.Nonnegative w ∧ ScalarV12.sum w = 1 ∧ ∀ x, F x = ScalarV12.dot w x) ∧ ∀ v : Fin n → α, (∀ x, F x = ScalarV12.dot v x) → v=w := probability_representation_unique F h"""),
    ("PositiveAggregationV16.zero_dimension_not_normalized", """{α : Type u} [ScalarV12.Scalar α] (F : (Fin 0 → α) → α) (h : IsLinear F) : F (fun _ => 1) ≠ 1 := zero_dimension_not_normalized F h"""),
    ("PositiveAggregationV16.int_projection_consistency", """: IsLinear intProjection ∧ PositiveAggregationV16.Monotone intProjection ∧ intProjection (fun _ => 1) = 1 := int_projection_consistency"""),
    ("FoundationV5.aggregator_rank_reversal", """: FoundationV5.worst (2,0) < FoundationV5.worst (1,1) ∧ FoundationV5.best (1,1) < FoundationV5.best (2,0) := FoundationV5.aggregator_rank_reversal"""),
    ("FoundationV5.min_not_additive", """: ¬ ∀ a b c d : Nat, min (a+c) (b+d) = min a b + min c d := FoundationV5.min_not_additive"""),
    ("FoundationV5.max_not_additive", """: ¬ ∀ a b c d : Nat, max (a+c) (b+d) = max a b + max c d := FoundationV5.max_not_additive"""),
)


def audit_source():
    header = "".join(f"import {name[:-5]}\n" for name in SOURCE_NAMES)
    header += ("open HistoryAdmissionV16 GroupLawsV16 CompositionContextV16\n"
               "open LinearBasisV16 PositiveAggregationV16\nuniverse u v w\n")
    return header + "\n".join(
        f"def registered_{i} {statement}\n#print axioms registered_{i}\n"
        for i, (_, statement) in enumerate(ENTRIES)
    )
