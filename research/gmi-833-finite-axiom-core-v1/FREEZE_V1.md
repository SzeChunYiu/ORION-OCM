# GMI #833 finite axiom core — pre-implementation freeze v1

**Issue:** #854, child of #833 Section C  
**Source `main`:** `1c07f45654aea522ab0f3d7cf51a84442473e523`  
**Status:** pre-implementation theorem/evidence freeze  
**Target claim ceiling:** `GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`

This freeze targets exactly the final two open Section-C foundation rows:

- `Produce a compact axiom/definition set from which the rest of GMI can be derived.`
- `Prove consistency/non-contradiction of the registered finite core where decidable.`

Here “the rest” is restricted to the **registered mathematical foundation objects already merged under #833**, not the empirical, real-scale, grammar-recovery, capability-revalidation, or complete-programme claims.

## Frozen parent authorities

This child composes rather than replaces:

- #837 `research/gmi-833-foundation-v1/MANIFEST_V1.json`, blob `deb8ec3ef57887790a874e01656c0cb598b2c908`;
- #846 `research/gmi-833-parent-equivalence-v1/MANIFEST_V1.json`, blob `e3aa9f88e085478586c2c53a4f1d0a2546bb90e8`;
- #848 `research/gmi-833-morphcap-v1/MANIFEST_V1.json`, blob `58b80724ef8651f3e476fdddddf2fe3a703fd5c2`;
- #851 `research/gmi-833-global-uncertainty-v1/MANIFEST_V1.json`, blob `01114b6e67c727575cfcff267d88eacd13274486`.

The current source SHA already contains the successful #851 uncertainty merge and #855 no-smuggling reconciliation. No dependency placeholder remains for uncertainty.

## Compact spine decision

The provisional eight rows in #854 are **not** frozen as eight independent axioms. The scientific target is a smaller basis: five independent finite-core axioms plus definitions/theorems that reconstruct the previously merged foundation objects.

### AX-1 — finite typed registration

Every registered carrier/domain is finite and nonempty where its constructor requires nonemptiness. Every registered element, relation tuple and version/development endpoint lies in its declared carrier. Architecture/source-code/family labels are outside the semantic signature unless explicitly registered as protected observations.

### AX-2 — registered realization totality

For a registered deterministic finite realization microscope, the initial state is registered; the action transition is total on `X × A`; protected output is total on `X`; and each registered intervention channel is total on its declared `X × J` interface. This axiom is scoped to the deterministic finite core model, not arbitrary stochastic/set-valued realizations.

### AX-3 — resource validity

Lifecycle resource vectors have a fixed positive coordinate dimension and exact nonnegative coordinates. Budgets compared to a resource vector have the same dimension; feasibility is coordinatewise. Scalarization is not part of this core axiom.

### AX-4 — typed uncertainty validity

Uncertainty constructors are disjoint tags. Feasible/confidence sets are subsets of their declared domains; confidence failure budgets lie in `[0,1]`; predictive/latent probability vectors are exact normalized nonnegative laws; latent kernels are normalized; selective-prediction certificates are explicitly tagged rather than coerced into confidence objects. In the explicit finite consistency witness, a confidence premise is interpreted against a registered finite truth law so a positive-coverage claim on the empty set can be checked rather than treated as uninterpreted prose.

### AX-5 — claim/evidence scope monotonicity

A finite explicit support relation declares which evidence/scope tags may support which claim tags. Claims outside that relation fail closed. In particular, a finite model/exhaustive certificate cannot be promoted to `UNIVERSAL`; parent claim ceilings also remain upper bounds unless new evidence is registered.

## Frozen definitional extensions

The following are **definitions/theorems, not extra independent axioms**, unless implementation discovers a genuine missing premise:

1. `DEF-SPEC`: external behavioral specification / protected acceptance object (#837).
2. `DEF-BEQ`: protected future-response/behavioral equivalence and exact quotient (#837/#846).
3. `DEF-REACH`: developmental relation and resource-bounded reachability (#837).
4. `DEF-MORPH` / `DEF-SPECIES`: registered mechanism isomorphism and quotient class (#848).
5. `DEF-CAP`: external capability value/region, finite admissible-class ceiling and impossibility region (#848).
6. `DEF-UQUERY`: query image, `IDENTIFIED`, `CANNOT_IDENTIFY`, `CANNOT_CHECK`, inconsistency and `UNKNOWN` semantics (#851).
7. `DEF-SCOPE`: theorem/result scope tags and parent-ceiling checks (#837 plus this spine's AX-5).

The implementation must ship a machine-readable acyclic dependency graph from AX-1..AX-5 to these definitions. A cycle is a failure, not silently collapsed.

## Frozen finite model witness

Construct an explicit `M_core` satisfying all five axioms simultaneously and exercising every major definition. It must include at least:

- three registered states with a nontrivial two-class behavioral quotient;
- nonempty finite action/output/intervention carriers and total deterministic registered channels;
- a nonempty typed developmental relation and a resource-bounded reachable set;
- a nonnegative two-or-more-coordinate resource vector;
- an achievable external capability contract and an impossible registered capability threshold/certificate over a declared finite admissible class;
- all five uncertainty tags (`FeasibleSet`, `ConfidenceSet`, `PredictiveLaw`, `LatentPredictiveModel`, `SelectivePrediction`), with exact rational probabilities where applicable;
- a non-identifying query that yields explicit abstention;
- scope metadata in which a finite satisfiability witness remains finite/existential and is not promoted to universal theory consistency.

## Frozen theorems

### CORE-1 — finite satisfaction is decidable

For a fixed finite candidate structure and a finite list of total decidable axiom/definition predicates, whether the structure satisfies the registered finite core is decidable by finite evaluation.

### CORE-2 — explicit-model satisfiability

If the frozen `M_core` evaluates true on every registered core axiom, then the registered finite axiom set is satisfiable. This is semantic model existence, not a claim about every future GMI extension.

### CORE-3 — relative syntactic consistency

Relative to the ordinary soundness theorem of the declared classical finite/many-sorted proof semantics: if `M_core` is a model of the axiom set, the axiom set cannot derive a contradiction in any sound proof calculus. This is a standard model-theoretic consequence, not a proof of ZFC consistency.

### CORE-4 — acyclic definitional reconstruction

If the frozen axiom/definition dependency graph is acyclic and every previously merged foundation object named in the reduction ledger is reachable from AX-1..AX-5 by definition/theorem edges, the compact spine reconstructs that registered foundation surface without adding those objects as independent axioms.

### CORE-5 — bounded irredundancy witnesses

For each AX-1..AX-5, exhibit a finite countermodel that satisfies the other four registered axiom predicates but violates that axiom alone. This establishes semantic irredundancy **on the registered finite checker semantics**; it is not advertised as unrestricted logical independence in all models.

## Frozen bounded enumeration

Enumerate a complete small candidate family with two states, one action and binary outputs. Vary:

- each transition/output entry over registered values plus a missing marker;
- two resource coordinates over `{-1,0,1}`;
- typed developmental edges plus one possible out-of-carrier hostile edge;

while keeping the external specification/uncertainty/scope fixtures fixed. The executor must count the full candidate family and all satisfying models exactly. Enumeration is a P2 corroborating certificate; CORE-2/CORE-3 are analytic/model-theoretic statements.

## Frozen hostiles

Each must return the specific violated axiom/definition rather than generic `False`:

- developmental edge outside the state carrier -> AX-1;
- missing registered transition -> AX-2;
- negative resource coordinate -> AX-3;
- confidence set outside its domain -> AX-4;
- empty confidence set with a registered positive-coverage premise under a finite truth law -> AX-4;
- finite/exhaustive evidence promoted to a universal claim -> AX-5;
- declared capability ceiling below an actually attained capability -> `DEF-CAP` certificate failure;
- malformed claimed behavioral-equivalence relation (e.g. non-reflexive) -> `DEF-BEQ` certificate failure;
- dependency cycle -> core dependency-graph failure.

Mutation of one independent axiom must not accidentally violate another independent axiom in its dedicated CORE-5 witness.

## Parent subtraction / strongest theory

The consistency step is standard many-sorted finite model theory/model checking: one concrete model proves satisfiability; soundness yields relative non-derivability of contradiction. Finite enumeration/model checking owns decidability at the bounded scope. GMI novelty is not claimed for these facts.

## Reconciliation boundary

Only after:

1. this exact freeze predates implementation/results;
2. analytic theorem note is committed;
3. exact normal and `python -O` tests/receipt are deterministic;
4. bounded enumeration and every hostile are green;
5. parent manifest hashes are rechecked against current `main`;
6. the existing #833 reconciler dry-runs exact replacements;

may the merge workflow update exactly the two targeted Section-C rows.

## Claim ceiling / forbidden promotions

Allowed only if every gate succeeds:

`GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`

Forbidden from this tranche alone:

- `GMI_ABSOLUTELY_CONSISTENT`
- `ZFC_CONSISTENCY_PROVED`
- `ALL_FUTURE_GMI_EXTENSIONS_CONSISTENT`
- `ONTOLOGICAL_COMPLETENESS`
- `ALL_GMI_DERIVED_FROM_FIVE_AXIOMS_UNIVERSALLY`
- `ALL_EMPIRICAL_GMI_RESULTS_DERIVED`
- `COMPLETE_GMI`
