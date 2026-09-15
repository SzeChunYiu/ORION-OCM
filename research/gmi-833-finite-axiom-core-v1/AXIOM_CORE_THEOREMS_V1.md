# Compact registered finite GMI axiom core — v1

**Issue:** #854, child of #833 Section C  
**Freeze:** `research/gmi-833-finite-axiom-core-v1/FREEZE_V1.md`  
**Claim ceiling:** `GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`

This capsule is a **foundation-core** result. It does not derive the empirical programme, neutral architecture recovery, real-scale capability laws, or every future GMI extension from five axioms. Its purpose is narrower: factor the already-merged finite mathematical foundation into a compact primitive spine plus acyclic definitions, and show that the registered finite spine has an explicit model.

The parent mathematics is standard many-sorted finite model theory, finite model checking, and definitional extension. The GMI contribution here is the repository-specific reduction ledger and fail-closed proof/claim discipline.

## 1. Signature and five primitive axioms

A registered finite core model contains finite carriers for machine states, actions, protected outputs, interventions and intervention outputs; a deterministic registered realization; developmental edges; a lifecycle resource vector; external capability contracts; typed uncertainty objects; and claim/evidence scope records.

The compact primitive basis is exactly:

### AX-1 — finite typed registration

Every required carrier is finite, nonempty and duplicate-free. Every stored transition tuple, output value, intervention tuple and developmental edge is typed in its declared carrier.

Architecture names and source identifiers are not semantic fields of this signature. If such a label is intended to be scientifically observable, it must be deliberately registered as an observation rather than silently consulted by semantics.

### AX-2 — registered realization totality

For the deterministic finite microscope, the initial state is registered; transition is total on `X × A`; protected output is total on `X`; and the registered intervention response is total on `X × J`.

This is intentionally scoped to the deterministic exact core. It is not exported to arbitrary set-valued or stochastic realizations.

### AX-3 — resource validity

A lifecycle resource vector has fixed positive dimension and exact nonnegative coordinates. Every budget compared against it has the same dimension and nonnegative exact coordinates. Feasibility is coordinatewise.

This does not authorize scalarization.

### AX-4 — typed uncertainty validity

The five uncertainty constructors remain disjoint:

`FeasibleSet`, `ConfidenceSet`, `PredictiveLaw`, `LatentPredictiveModel`, `SelectivePrediction`.

Set-valued objects remain subsets of their declared domain. Confidence failure budgets lie in `[0,1]`; predictive and latent probability laws normalize exactly and are nonnegative; latent kernels normalize for every registered latent state; selective coverage/risk certificates are explicitly typed. In the finite consistency witness, the confidence premise is interpreted against an exact finite truth law so the coverage statement itself is checkable.

### AX-5 — claim/evidence scope monotonicity

A finite support relation states which evidence-scope tags may support which claim-scope tags. Any unregistered promotion fails closed. In particular,

`FINITE_EXHAUSTIVE -> UNIVERSAL`

is forbidden, and a parent claim ceiling remains binding absent separately registered stronger evidence.

## 2. Definitional extensions, not additional axioms

`AXIOM_SPINE_V1.json` records an acyclic dependency graph. The following objects are reconstructed as definitions/theorems:

- `DEF-SPEC`: external behavioral specification (#837);
- `DEF-BEQ`: protected future-response equivalence and quotient (#837/#846);
- `DEF-REACH`: developmental/resource-bounded reachability (#837);
- `DEF-MORPH`: registered mechanism isomorphism (#848);
- `DEF-SPECIES`: quotient class under morphology equivalence (#848);
- `DEF-CAP`: external capability region, finite ceiling and impossibility (#848);
- `DEF-UQUERY`: uncertainty query image and abstention terminals (#851);
- `DEF-SCOPE`: finite theorem/result scope checking (#837 plus AX-5).

`FOUNDATION_REDUCTION_V1.json` pins the parent manifests and maps every registered foundation object in this tranche to the relevant axiom/definition node. The reduction checker rejects dangling targets, missing parent ownership, hash drift and dependency cycles.

The classification matters: for example, morphology equivalence does not need an independent ontological axiom once the registered finite mechanism signature is fixed; it is structure isomorphism on that signature. Capability ceiling is a maximum/supremum definition over a finite admissible class, not a primitive law. Query abstention is the image cardinality rule from the typed uncertainty object, not a sixth axiom.

## 3. Explicit finite model `M_core`

`FINITE_MODEL_V1.json` is a complete machine-readable model witness.

Its state carrier is

`X={s0,s1,s2}`

with actions `{stay,flip}`, protected outputs `{0,1}` and one intervention `probe`. The registered transition has:

- `stay`: each state remains in place;
- `flip`: `s0,s1 -> s2`, and `s2 -> s2`.

Protected outputs are `0,0,1` on `s0,s1,s2`. Hence `s0` and `s1` are behaviorally equivalent while `s2` is distinct, giving the nontrivial quotient

`{{s0,s1},{s2}}`.

The developmental edges are

`s0 -> s1 -> s2`

with a two-step developmental budget, so all three registered states are reachable from the initial state. The resource vector is `(2,1)`.

Two external capability contracts are registered over the finite admissible class `{M_core}`:

- `achievable`: score/ceiling `1`, threshold `1`;
- `impossible`: score/ceiling `0`, threshold `1`.

All five uncertainty constructors are present. The confidence set `{s0,s1}` has exact finite truth law `(1/2,1/2,0)` and failure budget `1/10`, hence true coverage `1 >= 9/10`. A query over feasible states `{s0,s2}` has output image `{0,1}` and therefore returns `CANNOT_IDENTIFY` rather than inventing a unique answer.

A pure state-renaming witness `s0,s1,s2 -> x,y,z` preserves the registered mechanism structure, resource vector and developmental edges, and is independently checked as morphology-equivalent.

## 4. CORE-1 — finite satisfaction is decidable [P1]

### Theorem

For a fixed finite registered candidate structure and a finite list of total decidable predicates representing AX-1..AX-5 and the registered definition certificates, satisfaction is decidable.

### Proof

Every carrier and relation table is finite. Each axiom checker performs a finite number of equality, membership, exact-rational arithmetic or finite-iteration operations. Every such operation terminates and returns a Boolean/certificate. Sequentially evaluating the finite list therefore terminates and decides whether every predicate holds. `□`

This is ordinary finite model checking; it makes no claim about decidability of arbitrary first-order theories or unrestricted program semantics.

## 5. CORE-2 — explicit-model satisfiability [P1 + P2]

### Theorem

If `M_core` satisfies AX-1..AX-5, then the registered finite axiom theory `T_core` is satisfiable.

### Proof

By definition, a theory is satisfiable when there exists a structure satisfying every axiom. `M_core` is an explicit structure. The exact checker evaluates every AX-1..AX-5 predicate to true on that structure. Hence `M_core` is a model of `T_core`, so `T_core` is satisfiable. `□`

The independent oracle `independent_core_oracle_v1.py` reads only the serialized finite model and rechecks carrier typing/totality, resources, uncertainty coverage, scope support, the behavioral quotient and capability certificates by a separate code path.

## 6. CORE-3 — relative non-contradiction / syntactic consistency [P1]

### Theorem

Relative to the ordinary soundness theorem for the declared classical many-sorted proof semantics: if `M_core` is a model of `T_core`, then no sound proof calculus for that semantics derives a contradiction from `T_core`.

### Proof

Assume for contradiction that a sound calculus derives `⊥` from `T_core`. Soundness states that every model of the premises satisfies every derivable conclusion. Since `M_core |= T_core`, soundness would imply `M_core |= ⊥`. But falsehood has no satisfying interpretation. Contradiction. Therefore no contradiction is derivable in a sound calculus. `□`

This is **relative** syntactic consistency via model existence. It is not an absolute metamathematical consistency proof, not a proof of ZFC consistency, and says nothing about arbitrary future axioms added to GMI.

## 7. CORE-4 — acyclic definitional reconstruction [P1 + machine graph check]

### Theorem

Let `G` be the frozen finite dependency graph whose roots are AX-1..AX-5. If `G` is acyclic, every definition/theorem node has only registered dependencies, and every row in the foundation-reduction ledger targets a node reachable from the primitive roots, then the listed merged foundation objects are definitional/theorem extensions of the compact spine rather than additional independent axioms.

### Proof

A finite DAG has a topological ordering. Evaluate nodes in that order. Every non-root node is defined/proved only after its dependencies exist. Inductively, each node is therefore an extension of the root structure, not an independent root assumption. Since every reduction row points to one such reachable node, each listed foundation object has a finite derivation path from the five roots. `□`

The machine validator rejects duplicate IDs, dangling dependencies, cycles, definitions with no axiom ancestor, unknown reduction targets and parent-manifest hash drift.

## 8. CORE-5 — bounded semantic irredundancy [P2 boundary theorem]

For each AX-i the package supplies one finite mutation that satisfies the other four axiom predicates while failing AX-i alone:

- AX-1: developmental edge leaves the registered carrier;
- AX-2: one transition table entry is missing;
- AX-3: one resource coordinate is negative;
- AX-4: a confidence set contains an out-of-domain value;
- AX-5: `FINITE_EXHAUSTIVE` evidence is promoted to `UNIVERSAL`.

Therefore no AX-i is redundant **with respect to the registered checker semantics and these four other predicates**: removing AX-i admits at least one countermodel rejected by the full core.

This is a bounded semantic irredundancy witness. It is not advertised as logical independence in every possible formal language/model class.

## 9. Definition/certificate hostiles

The package distinguishes primitive-axiom failures from derived-definition failures:

- empty confidence set plus a registered positive-coverage premise -> AX-4 `COVERAGE_PREMISE_FALSE`;
- declared capability ceiling below the actually attained value -> `DEF-CAP:CERTIFICATE` failure;
- malformed claimed behavioral equivalence -> `DEF-BEQ:CERTIFICATE_MISMATCH`;
- dependency cycle -> axiom-spine validation failure.

This prevents a bad derived certificate from being misreported as evidence that a new primitive axiom is needed.

## 10. Complete bounded census [P2]

A separate small-model enumerator varies a two-state / one-action structure over:

- each of two transition entries in `{state0,state1,missing}`;
- each of two output entries in `{0,1,missing}`;
- two resource coordinates in `{-1,0,1}`;
- every subset of four typed developmental edges plus an optional out-of-carrier hostile edge.

Total candidates:

`3^2 * 3^2 * 3^2 * 2^5 = 23,328`.

Exactly

`2^2 * 2^2 * 2^2 * 2^4 = 1,024`

satisfy AX-1/AX-2/AX-3 on this frozen family. The census is a finite reconstruction/control, not the proof of CORE-2 or CORE-3.

## 11. Parent subtraction

The mathematical facts used here are parent-owned:

- many-sorted first-order/finite model semantics: model existence implies satisfiability;
- soundness: a satisfiable axiom set cannot derive falsehood in a sound calculus;
- finite model checking: finite total predicates are decidable;
- DAG/topological-order semantics: acyclic definitions can be expanded in dependency order.

The residual contribution is repository governance: finding a smaller registered basis for the already merged #833 foundation, pinning exact parent ownership, supplying explicit countermodels for retained primitive predicates, and making stronger claim promotion fail closed.

## 12. Claim boundary

Allowed if CI verifies the frozen package:

`GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`

Forbidden from this tranche alone:

- `GMI_ABSOLUTELY_CONSISTENT`
- `ZFC_CONSISTENCY_PROVED`
- `ALL_FUTURE_GMI_EXTENSIONS_CONSISTENT`
- `ONTOLOGICAL_COMPLETENESS`
- `ALL_GMI_DERIVED_FROM_FIVE_AXIOMS_UNIVERSALLY`
- `ALL_EMPIRICAL_GMI_RESULTS_DERIVED`
- `COMPLETE_GMI`
