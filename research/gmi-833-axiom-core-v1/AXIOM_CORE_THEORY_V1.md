# Compact finite axiom core — v1

**Issue:** #854, child of #833 Section C  
**Freeze:** `FREEZE_V1.md`  
**Claim ceiling:** `GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`

## 1. Scientific role

The purpose of this tranche is not to invent a second GMI ontology. It compresses already-merged foundation objects into the smallest registered finite spine that survives explicit independence hostiles, while keeping scientific governance outside the object theory.

The four pinned parents remain authoritative for their stronger theorems and boundaries:

- #837 foundation/constitution;
- #846 parent-equivalence boundaries;
- #848 morphology/capability;
- #851 global uncertainty/abstention.

## 2. Why the provisional eight-item sketch was reduced

The issue sketch mixed three categories:

1. assumptions needed for a mathematical machine structure;
2. definitions/theorems derivable from those assumptions;
3. rules governing what scientists may claim about evidence.

Treating all three as axioms would inflate the consistency burden and obscure category boundaries. The registered core therefore contains six object axioms, five derived definitions, and two metarules.

## 3. Six object-level axioms

### AX-1 — external behavioral specification

Every registered finite behavioral specification has a nonempty finite instance carrier. Each instance has a nonempty legal protected trace set and a nonempty accepted subset. Acceptance is external to implementation state names.

### AX-2 — registered realization closure

A finite realization has nonempty state/action/output/observation/message/intervention carriers, an initial state in its carrier, total closed registered transition/output/observation tables, total registered communication and intervention-response channels, a nonempty verifier boundary, and a registered raw resource vector family.

### AX-3 — lifecycle resource admissibility

A declared resource coordinate set is nonempty and duplicate-free. Every event/development/budget vector has exactly those coordinates and nonnegative rational values. Finite path cost is coordinatewise addition.

### AX-4 — developmental closure

The finite developmental carrier is nonempty, the initial version belongs to it, the developmental relation is nonempty, every edge stays within the carrier, and every edge has a registered resource vector.

### AX-5 — external capability admissibility

Capability contracts depend only on protected task/verifier/resource coordinates, have declared score domains, contain their achieved values and ceilings within those domains, and never register an achieved value above the ceiling. A threshold may exceed a ceiling; that is an impossibility region rather than a contradiction.

### AX-6 — typed uncertainty admissibility

The uncertainty family contains five machine-distinct tagged constructors: feasible set, confidence set, predictive law, latent predictive model, and selective prediction. Set-valued candidates are subsets of registered domains. Confidence failure budgets lie in `[0,1]`; an empty confidence set cannot claim positive guaranteed coverage. Predictive laws, latent priors, and every latent kernel have unique finite domains and normalized nonnegative probabilities. Selective risk/error and coverage certificates lie in `[0,1]`.

## 4. Derived definitions/theorems

### DEF-1 — protected response equivalence

Equality of complete registered protected-response profiles defines an equivalence relation. Profiles include registered action outputs, observations, intervention responses, resource coordinates, and developmental relations. Reflexivity, symmetry and transitivity are inherited from equality; no separate equivalence axiom is required. The executable witness has quotient

`{{s0,s1},{s2}}`,

which is nontrivial: two classes from three states.

Myhill–Nerode, deterministic bisimulation, PSR and statistical-sufficiency relationships remain owned by #846 and its parents.

### DEF-2 — morphology/mechanism equivalence

Registered structure isomorphism over realization/resource/development coordinates defines morphology equivalence; its equivalence properties remain parent-owned by #848. It is not another independent consistency assumption here.

### DEF-3 — developmental reachability

Given AX-3 resource addition and AX-4 developmental edges, `Reach_Delta(M0,B)` is the set of versions on finite paths whose cumulative vector does not exceed `B`. In the witness, budget `(compute=1,memory=1)` makes exactly `v0,v1` reachable while `v2` is outside budget.

### DEF-4 — capability ceiling and impossibility region

A finite declared admissible class has a maximum/supremum capability score. A threshold above the ceiling is impossible at that scope. The witness's `hidden_world` contract has achieved/ceiling `1/2` and threshold `3/4`.

### DEF-5 — query identification/abstention

For candidate set `C` and registered query `q`, the identified set is `q[C]`. Empty `C` is inconsistent, singleton image is `IDENTIFIED`, multiple images are `CANNOT_IDENTIFY`, and unavailable query semantics give `CANNOT_CHECK`. The witness identity query over `{0,1}` abstains while the constant query is identified as `7`.

## 5. Metatheory is kept outside the object model

### META-1 — scope discipline

Finite, sampled and held-out statements cannot be rewritten as unrestricted universal claims without a separate theorem. The hostile `forall_fin -> forall` is rejected while the underlying machine structure remains object-theoretically satisfiable.

### META-2 — parent/claim ceiling discipline

Claims inherit parent/evidence ceilings. `COMPLETE_GMI` is rejected by the governance checker while the finite machine model remains satisfiable. This machine-distinct separation prevents an evidentiary overclaim from masquerading as a mathematical contradiction.

## 6. Relative finite satisfiability result

In ordinary model-theoretic language, a structure is a model of a set of sentences when it satisfies all of them. Tarskian satisfaction/model semantics supplies the parent notion; finite model theory studies satisfaction over finite structures.

The executable `M_core` is an explicit finite structure satisfying AX-1…AX-6 simultaneously. Therefore the conjunction of these six registered predicates is satisfiable at the implemented finite semantics. This establishes a relative non-contradiction result for this finite core: no contradiction follows merely from the conjunction, because one concrete model realizes it.

This does **not** establish consistency of the metalanguage, ZFC, all future GMI extensions, or an arbitrary first-order axiom system.

## 7. General finite satisfiability is not being decided

Finite satisfiability for unrestricted sufficiently expressive first-order signatures is not generally decidable (Trakhtenbrot's theorem). This tranche avoids that prohibited extrapolation: it model-checks one explicit registered finite structure and exhaustively enumerates a fixed 128-case mutation universe. It does not claim a complete solver for arbitrary finite first-order theories.

Parent references:

- A. Tarski / R. Vaught model-theoretic satisfaction tradition; see Stanford Encyclopedia of Philosophy entries on Tarski and truth definitions.
- H.-D. Ebbinghaus and J. Flum, *Finite Model Theory*, chapters on satisfiability in the finite.
- Trakhtenbrot's finite satisfiability undecidability boundary; modern mechanized treatment includes Kirst & Larchey-Wendling, *Trakhtenbrot's Theorem in Coq*.

## 8. Bounded independence/compactness evidence

Each AX-1…AX-6 has a single-mutation witness whose validator output names that axiom alone:

- AX-1: empty accepted set;
- AX-2: missing transition table entry;
- AX-3: negative resource coordinate;
- AX-4: developmental edge outside the version carrier;
- AX-5: achieved score above its registered ceiling;
- AX-6: candidate outside domain, empty positive-coverage confidence set, and non-normalized predictive law.

These are bounded independence witnesses at the registered finite semantics, not universal logical-independence theorems.

The hostile hypercube retains the seven independent defect bits from #858 (AX-1…AX-5 plus two distinct AX-6 defects), exhaustively checking all `2^7 = 128` combinations. Exactly one case—the all-clean assignment—satisfies all six axioms, and zero cases have incorrect violation attribution.

The issue-mandated targeted audit separately locks exact attribution for negative resource, non-total transition, attained score above ceiling, confidence outside domain, empty positive-coverage confidence, illegal finite-to-universal promotion, a corrupted equivalence relation, and a developmental edge outside its carrier. Because equivalence is derived and scope discipline is governance, those two hostiles correctly report `DEF-1` and `META-1`, not fictitious object-axiom failures. Three additional audit hostiles cover a missing communication entry, non-normalized latent prior, and out-of-range selective coverage.

## 9. Dependency graph

The registered DAG is acyclic:

- six AX nodes have no definitional parents;
- DEF-1 depends on AX-1/AX-2;
- DEF-2 depends on AX-2/AX-3/AX-4;
- DEF-3 depends on AX-3/AX-4;
- DEF-4 depends on AX-5;
- DEF-5 depends on AX-6;
- META-1 is governance-only;
- META-2 depends on META-1's scope discipline.

Thus the definitions do not circularly justify the axioms they are derived from.

## 10. Falsifiers

The registered result is falsified if any of the following occurs:

- the explicit finite witness violates an object axiom;
- a single-axiom hostile causes an unrelated axiom to fail without a documented dependency;
- any of the 128 hostile combinations has incorrect violation attribution;
- any mandated or audit-targeted mutation has inexact AX/DEF/META attribution;
- the derived protected-response relation is not an equivalence;
- the dependency graph is cyclic;
- a governance hostile is misclassified as object inconsistency or vice versa;
- a pinned parent result drifts;
- normal and optimized execution differ or fail byte replay.

## 11. Claim boundary

Earned only at green CI:

`GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`.

Forbidden here:

`GMI_ABSOLUTELY_CONSISTENT`, `ZFC_CONSISTENCY_PROVED`, `ALL_FUTURE_GMI_EXTENSIONS_CONSISTENT`, `ONTOLOGICAL_COMPLETENESS`, `ALL_GMI_DERIVED_FROM_SIX_AXIOMS_UNIVERSALLY`, `COMPLETE_GMI`.
