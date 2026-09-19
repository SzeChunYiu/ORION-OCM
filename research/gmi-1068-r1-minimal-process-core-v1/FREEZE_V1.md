# Grand Unified GMI V2 — R1 minimal process core freeze

Issue: #1068
Round: R1
Source main: ac8aa6ff7db1068ec227855e3162e9ab2d246431

This is the freeze-only first commit. No R1 theorem result, executable checker, hostile result, or Lean proof existed on this branch when this file was committed.

## Hypothesis under attack

The universal process-side structure required by Grand GMI may reduce to an ordinary typed category:

- object/interface types;
- typed process sets Hom(A,B);
- identity processes;
- typed sequential composition;
- associativity and identity laws.

The following are NOT assumed universal primitives unless R1 finds a loss witness forcing them:
- parallel/monoidal tensor;
- symmetry/braiding;
- stochastic kernels/probability;
- nondeterministic choice;
- higher cells/supermaps;
- an external admissibility predicate separate from membership in Hom.

## Required R1 results

1. State the minimal category core precisely.
2. Give a removal/loss witness for each retained component.
3. Give finite nontrivial models and hostile mutations.
4. Exhibit valid GMI-relevant process models without tensor/stochastic/higher-cell structure, blocking promotion of those enrichments to universal primitives.
5. Show substrate-relative admissibility can be represented by choosing which morphisms belong to Hom.
6. Record strongest-parent ownership; category/process mathematics is not GMI novelty.
7. Mechanize the universal category-law consequences in Lean.
8. Run exact finite calibration and independent checks.

## Claim ceiling

GRAND_GMI_V2_R1_TYPED_SEQUENTIAL_PROCESS_CORE_MINIMAL_RELATIVE_TO_REGISTERED_REQUIREMENTS

## Forbidden promotions

- UNIQUE_ABSOLUTE_PROCESS_ONTOLOGY
- MONOIDAL_TENSOR_UNIVERSALLY_REQUIRED
- STOCHASTICITY_UNIVERSALLY_REQUIRED
- HIGHER_CELLS_UNIVERSALLY_REQUIRED
- PROCESS_CONTEXT_FIXED_POINT_PROVED
- FULL_GMI
