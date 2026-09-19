# R1 — minimal typed sequential process core

## Result

Relative to the universal GMI requirements that survive the #833 audit, the weakest common process structure needed here is an ordinary typed category C_S:

- objects A,B,... are interface/configuration types;
- Hom(A,B) is the substrate-admitted process set from A to B;
- id_A is no-change;
- composition is typed sequential composition;
- identity and associativity laws make histories independent of arbitrary bracketing and admit empty/no-change histories.

Admissibility is represented extensionally: a physically/computationally forbidden process is absent from Hom. This removes the separate AJ1 Adm_S predicate from the universal core. A richer theory may add an explicit predicate if it needs to reason about a larger mathematical ambient category versus a physical subcategory, but that is derived presentation structure.

## Removal witnesses

1. TYPE: erase source/target typing and illegal boundary joins become expressible; the registered ill-typed hostile composes 0->1 with 0->1.
2. MORPHISM/PROCESS: erase processes and there is no transformation/interaction content.
3. COMPOSITION: erase composition and no multi-step history can be formed.
4. IDENTITY: erase id and zero-change/empty continuation cannot be represented internally.
5. ASSOCIATIVITY: without associativity, the outcome of a three-step history can depend on parse bracketing; the finite mutant in check_r1.py gives an explicit one-object counterexample.
6. IDENTITY LAWS: without left/right unit laws, inserting a no-change process can alter the process.

These establish requirement-relative irreducibility, not unique metaphysical ontology.

## Structures removed from the universal minimum

- Tensor/parallel composition: important and often natural, but no R1 universal GMI theorem requires an independent parallel operator. A substrate with parallel composition may enrich C_S monoidally.
- Symmetry/braiding: even less universal; ordered process systems need not support swaps as free processes.
- Probability/stochasticity: deterministic process categories already support the universal process/context construction. Stochastic kernels are an optional enrichment/instance.
- Nondeterministic choice: likewise optional.
- Higher cells/supermaps: useful for transformations between processes, but reflective/program-transforming processes can be represented as first-order morphisms when process descriptions are objects. Whether higher categorical structure buys stronger invariance is deferred to R5.
- External admissibility predicate: removed from the minimal signature by making Hom substrate-relative.

## Parent ownership

Category/process-theoretic composition is parent mathematics. R1 claims only the GMI-specific subtraction/minimality result at the registered requirements: the earlier AJ1 monoidal frame is stronger than required for the ultimate common core.

## Claim ceiling

GRAND_GMI_V2_R1_TYPED_SEQUENTIAL_PROCESS_CORE_MINIMAL_RELATIVE_TO_REGISTERED_REQUIREMENTS
