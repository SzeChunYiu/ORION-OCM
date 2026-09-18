## AG — Recursive foundation descent: pre-grammar substrate, presentation independence, and mathematical-base audit

This addendum corrects a remaining foundational ambiguity in #833. The current `G0` grammar is useful as a registered architecture-uncommitted **presentation/search language**, but a grammar is already too high a level to be called the bottom mathematical substrate. A grammar presupposes symbols/sorts, primitive operations or relations, arities, formation/composition rules and semantics. Therefore GMI must recursively descend below grammar and make every lower layer explicit before claiming a minimal basis.

This is a **foundation audit**, not a claim that a unique metaphysical bottom has been found. No checkbox below is closed by this comment.

### AG0 — Grammar is not the intelligence boundary

A grammar may generate an intelligent machine, a fixed calculator, a finite automaton, a parser, or a universal but non-adaptive cellular automaton. Conversely, a physical dynamical system need not internally represent the grammar by which a scientist describes it.

Therefore distinguish:

```text
scientist-side description/presentation
!= machine-side represented grammar
!= machine capability
!= intelligence/developmental capability
```

Required:

- [x] Construct explicit counterexamples showing `GRAMMAR_PRESENT` is not sufficient for intelligence. — ✅ `gmi-833-aj8-intelligence-boundary-v1` + `gmi-833-aj6-aj8-development-value-intelligence-v1`: a fully expressive finite universal interpreter with no task selector scores 1/2 on the registered identity task, exactly the collapsed constant baseline, while a fixed lookup table with no grammar-level distinction scores 1/1.
- [ ] Construct systems whose external formal description uses a grammar but whose mechanism contains no explicit grammar object.
- [x] Preserve the existing no-reification discipline: an external factorization/presentation must never be promoted into an internal representation claim without evidence. — ✅ `gmi-833-aj2-operational-equivalence-v1` + `gmi-833-no-smuggling-audit-v1`: QUOTIENT_REPRESENTED_INSIDE_MACHINE is a registered forbidden promotion and the semantic-rename detector flags planted reifications while staying silent on the clean fixture.
- [x] Test whether any defensible intelligence criterion can be stated at the grammar layer alone; allow `NO__GRAMMAR_IS_INTELLIGENCE_BOUNDARY` as a valid terminal. — ✅ `gmi-833-aj8-intelligence-boundary-v1` + `gmi-833-aj6-aj8-development-value-intelligence-v1`: no universal definition is frozen and the registered boundary is placed at developmental capability (history/information changing future organization), not at any grammar-layer predicate.

### AG1 — Canonical descent stack

Treat the current GMI hierarchy provisionally as:

```text
F0  MATHEMATICAL FOUNDATION / META-THEORY
    logic + foundational universe used to state mathematics

F1  SEMANTIC / PROCESS UNIVERSE
    admissible objects/state carriers and processes/relations/maps between them

F2  ALGEBRAIC / PROCESS THEORY
    operations/relations/composition/equations/transition structure abstracted
    away from one concrete syntax

F3  SIGNATURE / PRESENTATION
    sorts + generating operation/relation symbols + arities + equations/rules

F4  FREE SYNTAX / TERM ALGEBRA / GRAMMAR
    legal finite expressions generated from the presentation

F5  MACHINE REALIZATION / MODEL
    an interpretation of the theory/presentation in an actual computational substrate

F6  DEVELOPMENTAL DYNAMICS
    changes to state, parameters, representation, operators, theory/presentation,
    search law or morphology

F7  MACHINE-INTELLIGENCE MORPHOLOGY / SPECIES
    scoped equivalence classes of realized computational organization

F8  DEVELOPMENTAL CAPABILITY RESPONSE
    reachable capability/resource profile under information, time and resource conditions

F9  DATA/TASK-CONDITIONED SELECTION
    Pareto/preference frontier over reachable MI forms under a declared requirement family
```

- [x] Formalize every arrow `F_i -> F_(i+1)` as derivation, free construction, interpretation/model, compilation, development or selection rather than prose. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-1: all 37 arrows over 32 nodes are typed from the closed vocabulary {DERIVATION, FREE_CONSTRUCTION, INTERPRETATION_MODEL, COMPILATION, DEVELOPMENT, SELECTION, MUTUAL_INTERPRETATION} with a witness field that resolves in the cited merged receipt: 0 untyped, 0 witnessless, 0 missing fields, 0 arrows pointing up a layer, and all 7 same-layer refinements explicitly declared.
- [x] State exactly which #833 object currently lives at each layer. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-2: 32 registered #833 objects are placed across all ten layers (F0 6, F1 4, F2 6, F3 2, F4 2, F5 3, F6 3, F7 2, F8 2, F9 2), each naming its owning merged package, with 21 packages pinned by path and git blob sha and 0 pin violations.
- [x] Demote `G0` from “bottom substrate” wording to the appropriate F3/F4 presentation layer unless lower-layer irreducibility is actually proved. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-3: GRM_G0 is assigned F4 and generated from the F3 signature by a FREE_CONSTRUCTION arrow with a verified derived-from path down to F0 (DFS and, independently, boolean transitive closure), 0 demotion violations, licensed by AJ5's 484-execution lowering and by AG2's free term algebra of 11 instruction and 121 program terms.
- [x] Require every claimed primitive to name the lower layer from which it is introduced. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-4: every node marked primitive names an introduced_from_layer strictly below its own layer, 0 violations; the single node whose lowering is unadjudicated declares F2 and lowering_status UNKNOWN rather than hiding it.

### AG2 — Signature before grammar

Use the established universal-algebra distinction.

A many-sorted signature may be written schematically as

```text
Sigma = (Sorts, Ops, arity/type)
```

with each operation

```text
o : s1 × ... × sn -> s.
```

The term language is then generated recursively:

```text
variables/constants are terms;
if o is n-ary and t1,...,tn are well-typed terms,
then o(t1,...,tn) is a term.
```

A grammar is therefore generated **from** a signature/presentation; it is not the lowest object.

- [x] Formalize `G = FreeSyntax(Sigma)` for the registered finite GMI setting. — ✅ `gmi-833-ag2-signature-free-syntax-v1` AG2-1: the well-sorted ground terms over Sigma_G0 at depth bound 3 number 1 Reg / 2 Label / 11 Instr / 121 Prog, are closed under every well-sorted application (0 missing terms), and are the least such set: a depth-indexed recursive generator and an independent closure-to-fixed-point enumerator (2 rounds) produce identical sets.
- [x] Separate operation symbols from their interpretations. — ✅ `gmi-833-ag2-signature-free-syntax-v1` AG2-2: two interpretations of the same signature over the same generated term set assign materially different behaviour to 43 of the 121 program terms, witness prog(decjz(r0,l0,l1),emit(r0,l0)).
- [x] Separate formation rules from transition/reduction/equational rules. — ✅ `gmi-833-ag2-signature-free-syntax-v1` AG2-3: formation is total on all 121 terms while the transition relation is partial -- 11 terms yield an initial configuration with no successor -- and 120 unordered pairs share an identical operation-symbol multiset yet differ in behaviour, so formation neither implies nor determines transition.
- [x] Separate syntax equivalence from semantic equivalence. — ✅ `gmi-833-ag2-signature-free-syntax-v1` AG2-4: 121 syntactic classes collapse to 33 semantic classes under the registered observation family, a strict refinement with 0 refinement failures and exact collapse ratio 8/11, witnessed by prog(halt,decjz(r0,l0,l0)) and prog(halt,decjz(r0,l0,l1)).
- [x] Reconstruct the existing `G0` grammar from an explicit lower signature rather than taking its syntax as primitive. — ✅ `gmi-833-ag2-signature-free-syntax-v1` AG2-5: the 11 instruction terms and 121 program terms of FreeSyntax(Sigma_G0) map bijectively onto the registered G0 instruction classes and AJ5's 121 bounded programs, and 484 executions from an independently written interpreter reproduce AJ5's published terminal histogram exactly (HALTED 63, INPUT_UNDERFLOW 107, STEP_BUDGET_EXHAUSTED 314); the histogram is separately shown to saturate at step budget 6 and to be reproduced by 8 of 195 non-identity randomized opcode-role permutations, so identification rests on the full behaviour map, which 0 of those 195 reproduce.
- [ ] Audit every `G0` instruction (`READ/EMIT/INC/DECJZ/HALT`, stochastic/local/channel/self-change extensions, etc.) for whether it is a generator, derived operation, macro, semantic convenience, or resource-priced implementation primitive.

Strongest parents to absorb first: universal algebra/signatures/free algebras; term rewriting; structural operational semantics.

### AG3 — Presentation is not theory

Different signatures/generating sets can present the same or equivalent mathematical theory. GMI must therefore distinguish

```text
presentation P = (Sigma, equations/rules)
```

from the presentation-independent theory/semantic object it presents.

Candidate schematic:

```text
P = (Sigma, E)
Term(Sigma) / congruence(E)  ->  theory T
```

or, where appropriate, a Lawvere/algebraic/process-theoretic object whose definable operations are not privileged by one generating set.

- [ ] Define presentation equivalence at several strengths: syntactic renaming, definitional/term equivalence, semantics-preserving compiler equivalence with overhead, and stronger categorical/model equivalence where warranted.
- [x] Build multiple presentations of the same finite theory with materially different grammar/search geometry. — ✅ `gmi-833-g0-grammar-bias-v1`: two same-semantics non-isometric grammars give different description mass (A.L=1 vs B.L=2) while all 24 isometric remints are certified with 0 invariant failures.
- [x] Measure which GMI conclusions are presentation-invariant and which are presentation/search-bias dependent. — ✅ `gmi-833-aj5-g0-lowering-v1` + `gmi-833-g0-grammar-bias-v1`: 4 semantic invariants transfer under the lowering while 4 named quantities (description length, micro-step cost, mutation distance, search/reachability geometry) do not without the resource map.
- [x] Require flagship “fundamental primitive” claims to survive replacement of the chosen generating presentation by an equivalent one. — ✅ `gmi-833-aj5-g0-lowering-v1` + `gmi-833-g0-grammar-bias-v1`: the requirement holds only as a boundary: a semantics-preserving presentation replacement provably does NOT carry description length, micro-step cost, mutation distance or search/reachability geometry, so COMPILER_MAKES_SEARCH_BIAS_INVARIANT stays forbidden and any flagship primitive claim must be restated over the 4 surviving semantic invariants.
- [x] Parent-subtract Lawvere theories/universal algebra before claiming a new “basis-independent operation theory.” — ✅ `gmi-833-ag2-signature-free-syntax-v1` AG2-1: the parent ledger subtracts Birkhoff 1935 (doi:10.1017/S0305004100013463) for signatures/free algebras, Lawvere 1963 (doi:10.1073/pnas.50.5.869) for presentation-independent algebraic theories, Plotkin 2004 (doi:10.1016/j.jlap.2004.05.001) for formation-versus-transition and Minsky 1967 for the instruction set, and registers BASIS_INDEPENDENT_OPERATION_THEORY_CLAIMED as a forbidden promotion -- no such theory is claimed.

Important target:

```text
GMI primitive content should live as low as possible at the theory/invariant level,
not in an arbitrary favored syntax.
```

### AG4 — Process/transition semantics below named operators

The next descent question is whether even the operation signature is fundamental, or whether GMI can be expressed more invariantly through state/process relations and composition.

Candidate families to compare without choosing one in advance:

```text
A. carrier + finitary operations          (universal algebra)
B. states + labelled transition relation (LTS / operational semantics)
C. coalgebraic state-transition systems  (state-based behavior)
D. objects + morphisms + composition     (category/process theory)
E. relations/kernels rather than only deterministic functions
F. typed process interfaces + serial/parallel composition
```

- [ ] Construct exact translations among the applicable finite specializations.
- [x] Identify which objects are genuine invariants and which arise only from one formalism. — ✅ `gmi-833-aj12-foundation-substrate-relativity-v1` + `gmi-833-aj5-g0-lowering-v1`: 3 named objects survive translation between two formalization styles across 16 composition transfer checks, while 4 named quantities are recorded as formalism/presentation artifacts.
- [x] Test deterministic, nondeterministic, stochastic, interactive and concurrent cases separately. — ✅ `gmi-833-aj1-operational-process-base-v1` + `gmi-833-g0-interaction-channels-v1`: 64 deterministic and 4096 relational associativity cases, a two-output nondeterministic witness, a non-Dirac kernel K(0)=(1/2,1/2), interchange PASS for the concurrent tensor, and 24 FIFO channel checks with 0 isolation or implicit-broadcast failures.
- [x] Do not force stochastic/relational/quantum-like processes into deterministic function semantics merely for notational convenience. — ✅ `gmi-833-aj1-operational-process-base-v1` + `gmi-833-g0-stochastic-update-v1`: the base carries relational and kernel carriers natively (witnesses: two outputs from input 0; K(0)=(1/2,1/2)) and determinism appears only as a specialization, verified on 81 checks over 216 kernels with 0 failures.
- [x] Determine whether a common scoped object such as “typed process + composition” subsumes the current lower grammar semantics without architecture labels. — ✅ `gmi-833-aj5-g0-lowering-v1`: 484 executions over 121 bounded programs reproduce terminal status, protected output, final store and step count under both a functional and a relational lower presentation with 0 mismatches, using roles that name no MI family.
- [x] Permit `MULTIPLE_FOUNDATIONALLY_EQUIVALENT_PROCESS_BASES` if no unique lowest process formalism is justified. — ✅ `gmi-833-aj1-operational-process-base-v1` + `gmi-833-aj12-foundation-substrate-relativity-v1`: ABSOLUTE_PROCESS_ONTOLOGY_PROVEN is a registered forbidden terminal, minimality is stated only relative to 6 named requirements, and two formalization styles yield the same operational quotient.

### AG5 — `G0` must be derivable from lower relations/processes

The decisive test for the current grammar is not whether it is small. It is whether its operations can be reconstructed from a more primitive registered semantics.

For every current primitive `p`:

```text
lower semantic/process substrate
        -> composition/construction
        -> p
```

must receive one of:

```text
DERIVED
RESOURCE_IRREDUCIBLE_AT_SCOPE
SEMANTICALLY_IRREDUCIBLE_AT_SCOPE
PRESENTATION_ONLY
UNKNOWN
```

- [x] Derive finite `READ`/`EMIT` from typed interaction relations/channels. — ✅ `gmi-833-aj5-g0-lowering-v1`: READ and EMIT are both DERIVED from NEXT_INPUT/STORE and LOAD/APPEND_OUTPUT at <=2 lower operations each, verified over 484 executions with 0 mismatches.
- [x] Derive finite register mutation from generic state transformation where possible. — ✅ `gmi-833-aj5-g0-lowering-v1`: INC is DERIVED as LOAD;SUCC;STORE at <=3 generic lower operations with 0 lowering mismatches.
- [x] Derive branching/conditional transition from lower relational/process semantics where possible. — ✅ `gmi-833-aj5-g0-lowering-v1`: DECJZ is DERIVED as LOAD;IS_ZERO;SELECT (plus PRED_POS;STORE on the nonzero branch) at <=5 lower operations, with 0 mismatches under the relational small-step presentation.
- [x] Derive `HALT` as a terminal/absorbing/acceptance condition rather than assume a named opcode where possible. — ✅ `gmi-833-aj5-g0-lowering-v1`: HALT carries status PRESENTATION_ONLY: it is the choice of a terminal no-successor configuration in the lower semantics at <=1 lower operation, reached in 63 of 484 executions.
- [x] Derive recurrence from composition/feedback/cycles rather than a recurrence macro. — ✅ `gmi-833-aj4-process-organizations-v1`: recurrence is obtained from feedback composition rather than a recurrence macro (toggle and persistence witnesses PASS, exactly 1 unique delay-1 organization), but only when the substrate admits delay: 4 organizations are realizable without it against 260 with it, and FEEDBACK_FROM_STATIC_WIRING_WITHOUT_TEMPORAL_SUBSTRATE stays forbidden.
- [ ] Derive stochastic update from kernels/distributions rather than a named probabilistic architecture.
- [ ] Derive communication/tool calls as typed interaction composition.
- [ ] Derive governed self-change as state/process transformation plus an externally registered admission relation.
- [x] Charge any lower-to-`G0` compiler overhead explicitly. — ✅ `gmi-833-aj5-g0-lowering-v1`: overhead is charged as lower_ops <= 5*G0_steps and micro_size <= 5*|P| with a per-instruction table, observed maxima 32 lower operations and 4.0 operations per G0 step.

### AG6 — Universality is a lower-bound null, not intelligence

Very small calculi can already be computationally universal: e.g. combinatory logic has tiny bases, and Rule 110 is an elementary cellular automaton with universal computation. Therefore shrinking syntax until universality appears does **not** identify an intelligence atom.

- [ ] Reconstruct at least three radically different universal low-level bases (e.g. register/counter, combinatory/rewrite, cellular/local) at bounded executable scope.
- [ ] Compare their compilation overhead, description bias, reachability geometry and developmental search burden.
- [ ] Test whether the same higher MI morphology/capability laws survive across these bases after resource normalization.
- [x] Treat `TURING_UNIVERSAL` as expressibility evidence only. — ✅ `gmi-833-aj8-intelligence-boundary-v1` + `gmi-833-aj11-bounded-completeness-v1`: TURING_OR_FINITE_UNIVERSALITY_IS_SUFFICIENT_FOR_INTELLIGENCE is forbidden, the universal interpreter scores 1/2 at chance, and universality is recorded only as syntax-level enumerability against the Rice boundary.
- [ ] Preserve `UNIVERSAL_COMPUTATION_ONLY` whenever no intelligence-specific predictive residual remains.

### AG7 — Intelligence should emerge above common non-intelligent substrate

Do not require an “intelligence atom” if intelligent and non-intelligent systems share the same mathematical/computational substrate.

Candidate research question:

> Which additional organization/development/selection properties distinguish systems that merely compute from systems that acquire or exploit decision-relevant computational distinctions under changing requirements and bounded resources?

This is deliberately above the primitive layer.

- [x] Construct matched systems using the same F0–F5 substrate, one satisfying only fixed computation and one exhibiting registered developmental capability. — ✅ `gmi-833-aj8-intelligence-boundary-v1` + `gmi-833-aj6-hst-layer-map-v1`: on one substrate a fixed lookup reaches 1/1 with no development while a learner moves 1/2 -> 1/1 only after task information, and 51 pairs share an identical current organization with different developmental futures.
- [x] Identify the first layer at which their properties diverge. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-5: for a matched pair identical through F0-F5 (same foundation, process theory, presentation, grammar and machine organization) the first divergence layer is F6, computed by linear scan and independently by bitmask, with exact capability 1/2 frozen against 0 one-edit, agreeing with AJ6's pinned receipt over 51 such pairs.
- [ ] Test candidate boundaries: adaptation, history-sensitive development, acquisition of reusable distinctions/operators, metareasoning, endogenous experiment/search selection, and capability-frontier expansion.
- [x] Reject any criterion also satisfied by a fixed lookup table/universal interpreter without the additional intended property. — ✅ `gmi-833-aj8-intelligence-boundary-v1`: 5 registered negative controls include FIXED_LOOKUP_ID at 1/1 and UNIVERSAL_INTERPRETER_DEFAULT at 1/2, and the interpreter only reaches mean 1 when handed the correct external program, so neither can license a criterion.
- [x] Do not promote this lane into a definition of intelligence until negative controls and strongest cognitive/computation parents are saturated. — ✅ `gmi-833-aj8-intelligence-boundary-v1` + `gmi-833-aj14-establishment-criterion-v1`: UNIVERSAL_DEFINITION is NOT_FROZEN, UNIVERSAL_INTELLIGENCE_DEFINITION_PROVED is forbidden, and the establishment ladder still records unearned badges with full_gmi_supported_now false.

### AG8 — Recursive foundation descent protocol

For every allegedly foundational object `X`, execute:

```text
1. Is X merely syntax/presentation?
2. What lower object is required to define X?
3. Can X be constructed from that lower object?
4. Are there alternative lower foundations/formalisms yielding equivalent X?
5. Which GMI theorems are invariant under translation?
6. Which assumptions are truly load-bearing?
7. Remove one assumption at a time and seek the smallest counterexample.
8. Repeat on every newly exposed lower object.
```

- [x] Integrate this as a downward counterpart to AA/AD recursive gap closure and HSG Reflexive Generalization Closure. — ✅ `gmi-833-ag1-descent-stack-v1` AG8: the eight AG8 steps are registered with direction DOWNWARD, each cross-linked to a resolvable upward counterpart -- AA's OPEN_GAP/GMI_GAP_GRAPH and AD's recursive research loop in issue comment 5684607872, and the HSG Atomic/Reflexive Generalization Closure protocol pinned as parent row HSG_AGP in the AF barrier parent ledger -- with 0 obligation violations.
- [x] Build a machine-readable `FOUNDATION_DEPENDENCY_DAG` from F0 through F9. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-1: FOUNDATION_DEPENDENCY_DAG_V1.json is emitted machine-readable over F0 through F9: 32 nodes, 37 typed arrows, all ten layers populated, 21 blob-pinned parent packages and 20 violation counters all zero.
- [x] Forbid cycles in “derived from” edges unless explicitly typed as mutual interpretation/equivalence rather than derivation. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-4: 0 cycles over derived-from arrows, verified by DFS colour-marking and independently by Kahn in-degree peeling (32 of 32 nodes removed); MUTUAL_INTERPRETATION arrows are required to be symmetric and same-layer with 0 violations, and a planted pure intra-layer 2-cycle is detected without tripping any layer gate.
- [x] Require every apparent bottom node to expose its metatheoretic assumptions. — ✅ `gmi-833-ag1-descent-stack-v1` AG1-4: all 5 apparent bottom nodes carry a non-empty metatheoretic assumption list, every assumption tagged with one of the five AJ12 classes (0 untagged), and stripping one node's assumptions is detected.
- [ ] Require an independent formal-logic/foundations review of the stopping point.

### AG9 — There may be no unique “bottom of mathematics”

Do not silently identify the bottom with ZFC, category theory, type theory, or any one currently fashionable foundation. Modern mathematics admits multiple foundational frameworks, including set-theoretic, type-theoretic/univalent and categorical approaches. Moreover, sufficiently strong consistent effectively axiomatized theories are subject to Gödel-style incompleteness/self-consistency limits.

Therefore the scientifically defensible target is **foundation-explicit invariance**, not `ABSOLUTE_BOTTOM_PROVEN`.

Required comparison set, at minimum conceptually and where practical formally:

```text
SET-THEORETIC FOUNDATION       (e.g. ZFC-style)
TYPE-THEORETIC FOUNDATION      (dependent type theory / constructive variants)
CATEGORICAL/STRUCTURAL FOUNDATION where technically adequate
```

- [x] State the minimal foundational assumptions actually used by each flagship GMI theorem. — ✅ `gmi-833-aj12-foundation-substrate-relativity-v1` + `gmi-833-aj13-stopping-rule-v1` + `gmi-833-aj0-foundation-scope-v1`: five assumption classes are registered, every remaining assumption is explicitly tagged, and the flagship registry carries 9 rows with 16 exhaustive promotion cases and 0 illegal promotions accepted.
- [x] Re-express at least the compact GMI core in a second foundational framework where practical. — ✅ `gmi-833-aj12-foundation-substrate-relativity-v1`: the finite process core is expressed twice (finite-set/relation and explicit typed algebraic process style); all 16 ordered compositions agree and both give the same operational quotient {{p0,p2},{p1}}.
- [x] Distinguish theorem invariance from mere notational translation. — ✅ `gmi-833-aj12-foundation-substrate-relativity-v1`: three named objects are recorded as surviving translation while UNIQUE_TRUE_FOUNDATION_PROVED stays forbidden and metatheoretic equivalence of the two foundations is explicitly not claimed.
- [x] Record independence/undecidability/incompleteness rather than papering it over. — ✅ `gmi-833-aj12-foundation-substrate-relativity-v1` + `gmi-833-aj11-bounded-completeness-v1`: Goedel and Tarski boundaries are preserved as registered scope items and semantic equivalence is recorded as undecidable in general with the Rice boundary applying at standard scope.
- [x] Define a terminal such as `FOUNDATION_RELATIVE_CORE_STABLE_ACROSS_REGISTERED_FOUNDATIONS`. — ✅ `gmi-833-aj13-stopping-rule-v1`: the terminal FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE is registered with 6 criteria satisfied and 6 hostile cases rejected.
- [x] Forbid `ABSOLUTE_FOUNDATION_OF_ALL_MATHEMATICS_PROVEN` and `SELF_JUSTIFYING_FINAL_GMI_FOUNDATION`. — ✅ `gmi-833-aj13-stopping-rule-v1` + `gmi-833-aj12-foundation-substrate-relativity-v1` + `gmi-833-aj14-establishment-criterion-v1`: ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN, UNIQUE_TRUE_FOUNDATION_PROVED, SELF_JUSTIFYING_ALL_TRUTH_FOUNDATION and UNIQUE_ABSOLUTE_MATHEMATICAL_FOUNDATION are all registered prohibitions, and the absolute-promotion hostile is rejected.

### AG10 — Candidate mathematical spine after descent

Do **not** freeze this yet, but test whether the architecture-neutral spine can eventually be written schematically as

```text
foundation F
   ↓
semantic/process universe C
   ↓
abstract theory T
   ↓
presentation/signature P=(Sigma,E)
   ↓
free syntax / grammar G(P)
   ↓
model/realization M : T -> C
   ↓
development Delta over M and possibly P/T
   ↓
machine-intelligence equivalence/species space
   ↓
developmental capability response Gamma
   ↓
data/task/resource-conditioned Pareto/preference selection
```

The key novelty target, if any survives parent subtraction, is not “we invented syntax below grammar.” It is a **single experimentally connected theory that carries invariants from mathematical foundation/presentation through machine generation, development, capability and conditional MI selection**, while exposing exactly where presentation, search, data and resource priors enter.

### AG11 — Exact microscopes required before any new primitive claim

1. **Signature -> grammar microscope:** automatically generate the term grammar from a frozen finite signature and verify closure.
2. **Same theory / different presentation:** two or more presentations with the same finite semantics but different code/search geometry.
3. **Same syntax / different semantics:** demonstrate that grammar alone does not determine machine behavior/capability.
4. **Sub-`G0` derivation:** reconstruct every registered `G0` primitive from a lower relation/process system or return an honest irreducibility/unknown terminal.
5. **Cross-basis universality control:** register/counter vs combinatory/rewrite vs cellular/local universal bases; universality must not be misreported as intelligence.
6. **Cross-basis MI recovery:** ask whether at least several known MI morphology classes are recovered after compilation/resource normalization from more than one low-level basis.
7. **Intelligence-boundary negative:** fixed universal machine vs developmental/adaptive machine on the same low-level substrate.
8. **Foundation translation pilot:** port one nontrivial finite GMI theorem/object between two foundation/formalization styles and check semantic agreement.

### AG12 — Parent literature that receives first refusal

At minimum:

- universal algebra: signatures, term/free algebras, equational theories, Birkhoff-style results;
- Lawvere/algebraic theories and presentation-independent operations;
- term rewriting and structural operational semantics;
- labelled transition systems/process algebra;
- coalgebraic state-based systems;
- category/process theory and compositional semantics;
- lambda calculus/combinatory logic/register/Turing/cellular universality;
- set theory, type theory/univalent foundations and categorical foundations;
- Gödel incompleteness and computability/interpretability results.

No GMI novelty may consist of renaming these objects.

### AG13 — Proposed claim ceiling

Until this programme is discharged, use at most:

> `G0` is a registered architecture-uncommitted machine-generation grammar with explicit bias; it is not yet established as the lowest or unique mathematical substrate of machine intelligence.

A stronger future statement would require evidence that the higher GMI results are invariant across materially different presentations/bases and that all remaining primitive assumptions have explicit lower-layer or foundation-relative status.

The target is therefore not a mystical indivisible “intelligence atom.” The target is a recursively audited derivation chain in which **nothing is called primitive merely because the current implementation starts there**.
