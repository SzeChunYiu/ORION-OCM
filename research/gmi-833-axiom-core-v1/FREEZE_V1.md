# GMI #833 compact finite axiom core — freeze v1

**Child issue:** #854  
**Parent:** #833 Section C  
**Frozen from main:** `1c07f45654aea522ab0f3d7cf51a84442473e523`  
**Claim ceiling:** `GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`

This is the pre-implementation scientific custody record. Model checker, finite witness, mutation hostiles, expected receipt, reconciliation spec and workflow must postdate this freeze.

## Exact target rows

This tranche may reconcile only:

1. `Produce a compact axiom/definition set from which the rest of GMI can be derived.`
2. `Prove consistency/non-contradiction of the registered finite core where decidable.`

The second row is interpreted narrowly as **finite satisfiability/non-contradiction of the registered finite core**: an explicit finite structure satisfies all registered object-level axioms simultaneously. It is not an absolute consistency proof for GMI, first-order logic, ZFC, or future extensions.

## Strongest merged parents — frozen by exact result blob

- foundation/constitution: `research/gmi-833-foundation-v1/RESULT_V1.json` — blob `c0c574c4ec6e237d5fdafa694eac131399625a70`;
- parent-equivalence boundaries: `research/gmi-833-parent-equivalence-v1/RESULT_V1.json` — blob `7f6ee1c2d6e3e1bc24e66b192abffcc2d0a23ed3`;
- morphology/capability: `research/gmi-833-morphcap-v1/RESULT_V1.json` — blob `bdc5c3cd42e312d8c7af52f7ba84220631a25f8a`;
- typed uncertainty/abstention: `research/gmi-833-global-uncertainty-v1/RESULT_V1.json` — blob `9ab16cf59087214e093ace3b18c6d08fc79ab871`.

Any path/blob drift is RED.

## Category correction: object theory vs metatheory

The provisional eight-item issue sketch mixed mathematical objects with scientific governance. This freeze corrects that.

### Object-level axioms — independent finite structure constraints

#### AX-1 — External behavioral specification
A registered behavioral specification has a nonempty finite instance set, a finite legal protected trace set for every instance, and a nonempty accepted subset for every instance. Acceptance is external to implementation state names.

#### AX-2 — Registered realization closure
A registered finite realization has nonempty finite state, action and output carriers; a registered initial state belongs to the state carrier; and every declared execution/update transition is total and closed on its declared finite domain/codomain. Architecture/family names are not semantic fields.

#### AX-3 — Lifecycle resource admissibility
Every registered lifecycle event/resource vector has exactly the declared resource coordinates and every coordinate is a nonnegative rational. Finite path cost is coordinatewise addition. Scalarization is not primitive scientific truth.

#### AX-4 — Developmental closure
A registered developmental relation is a relation over the registered realization/version carrier only. Developmental reachability is the finite reflexive-transitive closure restricted by AX-3 resource budgets. Reachability is therefore derived and remains distinct from mere membership/expressibility.

#### AX-5 — External capability admissibility
A capability contract is a protected task/verifier/resource functional over registered external behavior/resources. Any registered achieved score lies within the contract's declared score domain and cannot exceed a registered upper ceiling; a threshold above the ceiling defines an impossibility region. Capability is not an architecture label.

#### AX-6 — Typed uncertainty admissibility
Every set-valued uncertainty object has candidates contained in its registered domain. Confidence failure budgets lie in `[0,1]`; a positive-coverage confidence object may not have an empty candidate set. Predictive laws are normalized finite probability laws. Query disposition is derived from the registered candidate-set image: empty -> inconsistency, singleton image -> identified, multiple image -> cannot identify; absent required semantics -> cannot check.

### Derived definitions/theorems — not independent axioms

#### DEF-1 — Protected response equivalence
Equality of the complete registered protected-response profile defines an equivalence relation. Reflexivity/symmetry/transitivity and the quotient are theorems of equality, not extra axioms. Myhill–Nerode/bisimulation/PSR specializations remain parent-owned.

#### DEF-2 — Morphology/mechanism equivalence
Registered mechanism-structure isomorphism is a defined equivalence relation over AX-2/AX-3/AX-4 structure. Its equivalence properties are derived and parent-owned by the morphcap tranche.

#### DEF-3 — Reachability
`Reach_Delta(M0,B)` is derived from AX-3 + AX-4 as budget-bounded finite path closure; no separate reachability axiom is needed.

#### DEF-4 — Capability ceiling/impossibility region
The ceiling is a supremum/maximum over the declared finite admissible class; impossibility thresholds are derived comparisons against that ceiling.

#### DEF-5 — Query identification/abstention
Identification is the image of a query over the surviving AX-6 candidate set. The terminal vocabulary is derived from cardinality/availability, not independently axiomatized.

### Metatheory/governance rules — not object-level axioms

#### META-1 — Scope discipline
Each theorem/result carries an explicit domain/evidence tag (`forall[D]`, `forall_fin[U]`, `heldout[F]`, `sample[P,n]` or equivalent). Finite/sample/held-out evidence may not be silently promoted to unrestricted universal scope.

#### META-2 — Parent/claim ceiling discipline
A result records strongest parents, assumptions, falsifiers and forbidden extrapolations. Parent mathematics is subtracted; new claims cannot exceed demonstrated scope/evidence without new proof/evidence.

These two rules govern scientific claims about models; they are not propositions inside the finite machine model itself.

## Finite satisfiability witness requirements

Construct one explicit finite model `M_core` satisfying AX-1…AX-6 simultaneously with at least:

- two instances and finite protected trace/acceptance sets;
- at least three internal states and two actions;
- total closed update/execution tables;
- a nontrivial protected-response quotient (at least two but fewer classes than histories/states represented);
- a nonempty developmental relation and a bounded reachable set;
- at least two nonnegative rational resource coordinates;
- at least two external capability contracts, including one threshold strictly above a registered ceiling;
- a feasible set, confidence set, predictive law and a query that must abstain (`CANNOT_IDENTIFY`), plus an identified control;
- explicit finite scope tags.

A concrete satisfying model establishes only: the finite registered axiom conjunction is satisfiable/non-contradictory relative to the ordinary semantics implemented by the checker.

## Decidable hostile mutation obligations

Each mutation must return the exact violated axiom IDs, not a generic false oracle:

1. negative resource coordinate -> AX-3;
2. non-total or out-of-carrier realization transition -> AX-2;
3. developmental edge outside carrier -> AX-4;
4. achieved capability above registered ceiling -> AX-5;
5. confidence candidate outside domain -> AX-6;
6. empty positive-coverage confidence set -> AX-6;
7. malformed/non-normalized predictive law -> AX-6;
8. empty accepted trace set for an instance -> AX-1;
9. finite-to-universal scope promotion -> META-1 (metatheory, not object-model inconsistency);
10. claim above parent/evidence ceiling -> META-2 (metatheory, not object-model inconsistency).

The checker must keep object inconsistency and governance invalidity machine-distinct.

## Compactness / redundancy obligations

- Build an acyclic dependency DAG separating six object axioms, five derived definitions, and two metarules.
- Every derived definition must depend only on earlier axioms/definitions and must not be counted as an independent consistency assumption.
- For each AX-1…AX-6, provide a finite mutation that violates that axiom while leaving all other object axioms satisfied where possible. This is a bounded **independence witness at the registered finite semantics**, not a universal independence theorem.
- If an alleged axiom cannot obtain such a separating witness and is derivable in the registered semantics, demote it to a definition/theorem before closure.

## Model-theory claim boundary

The finite-model argument uses ordinary satisfaction semantics: a structure is a model of a theory when it satisfies all registered sentences/predicates. One explicit finite model proves satisfiability of this finite conjunction. It does not prove consistency of the ambient metatheory or all future extensions.

## Forbidden promotions

This tranche alone cannot support:

- `GMI_ABSOLUTELY_CONSISTENT`
- `ZFC_CONSISTENCY_PROVED`
- `ALL_FUTURE_GMI_EXTENSIONS_CONSISTENT`
- `ONTOLOGICAL_COMPLETENESS`
- `ALL_GMI_DERIVED_FROM_SIX_AXIOMS_UNIVERSALLY`
- `COMPLETE_GMI`
