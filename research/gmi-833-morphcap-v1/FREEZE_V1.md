# GMI #833 morphology/capability freeze v1

**Parent:** #833 Section C  
**Child:** #848  
**Source main:** `4f2466d2dabad316249a2fe86c6a819e43eb8b10`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the target definitions, theorem statements, exact witnesses, hostiles, and claim ceiling before implementation/tests/results/reconciliation exist on this branch.

## Registered scope object

A finite registered scientific scope `Omega` declares:

- external action/input labels and protected output labels;
- permitted interventions;
- verifier/admissibility semantics;
- lifecycle resource coordinates;
- registered developmental transitions/reachability relation;
- capability contracts built from external tasks/ecologies, outcomes, budgets and thresholds.

No architecture-family label is part of the scientific object.

## MORPH-1 — mechanism signature and morphology equivalence

A realization's reduced mechanism signature at `Omega` is the finite relational structure consisting of:

1. its reachable protected-state quotient;
2. initial-state marker;
3. labeled transition and output relations;
4. registered intervention-response labels;
5. raw lifecycle resource vector under the registered experiment;
6. registered developmental/reachability relation.

Define `M approx_Omega N` iff there exists a bijection between their reduced state sets preserving every registered component above.

Target theorem: `approx_Omega` is an equivalence relation. State/syntax renaming cannot change the class. Protected behavior equality alone is not sufficient when resource/intervention/developmental coordinates differ.

Frozen exact witnesses:

- `M_A` and `M_RENAMED`: two-state realizations related by a pure state renaming; must be equivalent.
- `M_RESOURCE_TWIN`: same protected transitions/outputs as `M_A` but one resource coordinate differs; behavior equal but morphology inequivalent.
- `M_INTERVENTION_TWIN`: same ordinary behavior/resources but a registered intervention response differs; morphology inequivalent.

## SPECIES-1 — machine species

Define legacy `machine species` at scope `Omega` as the quotient class `[M]_(approx_Omega)`. Paper-facing preferred term: `computational-mechanism equivalence class` unless an explicitly biological analogy is intended.

No claim of a universal biological taxonomy or unique architecture ontology is permitted.

## CAP-1 — architecture-independent capability object

A capability contract is externally defined by:

`c = (task/ecology measure, protected utility or acceptance functional, verifier/admissibility rule, resource budget vector, threshold)`.

For realization `M`, the capability value is computed only from protected outcomes and resource records under `c`. The capability region `Cap_Omega(M)` is the set of registered contracts satisfied by `M`.

Target theorem: if `M approx_Omega N` and a capability contract is measurable entirely from components preserved by the mechanism isomorphism, then the two realizations have identical value and satisfaction status for that contract; hence identical registered capability regions.

## CAP-2 — ceiling and impossibility region

Let `A_Omega` be an externally defined admissible class of realizations, not a named architecture family. For capability functional `C_c`, define

`C*_c(Omega) = sup { C_c(M) : M in A_Omega and M satisfies the registered resource/admissibility contract }`.

At finite registered scope this supremum is a maximum when the feasible set is nonempty.

Define the impossibility region as registered contracts whose threshold is strictly above the ceiling, plus resource/admissibility regimes with no feasible successful realization.

Target monotonicity:

- enlarging the admissible realization class cannot lower the ceiling;
- relaxing resource budgets cannot lower the ceiling;
- raising the required threshold cannot turn an impossible contract into a possible one.

## CAP-3 — architecture-independent information ceiling

Frozen hostile: two equiprobable latent worlds `w0,w1` produce the same pre-action observation. Success requires action `0` in `w0` and action `1` in `w1`. Any randomized policy chooses action `1` with probability `p`; exact expected success is

`(1/2)(1-p) + (1/2)p = 1/2`.

Therefore every threshold greater than `1/2` is impossible for this information contract regardless of internal architecture.

Positive twin: reveal the world before action; policy `a=w` attains success `1`.

P2 control: enumerate every rational `p=k/32` for `k=0..32`; all hidden-world policies must score exactly `1/2`. For the revealed twin enumerate all pairs `(p0,p1)` on the same grid and require a maximum of `1`.

## Frozen falsifiers

This tranche fails if:

- state-renaming changes the mechanism class;
- resource/intervention mismatches are ignored;
- morphology equivalence fails reflexivity, symmetry or transitivity in finite hostile checks;
- capability code branches on architecture-family names;
- morphology-equivalent witnesses receive different registered capability regions;
- budget/class relaxation lowers an exact finite ceiling;
- any hidden-world randomized policy exceeds `1/2` in CAP-3;
- the revealed-information positive twin fails to attain `1`;
- these definitions are promoted to a universal ontology or to a re-proof of all historical capability bounds.

## Claim ceiling

`GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions:

- `UNIVERSAL_MORPHOLOGY_ONTOLOGY`
- `ALL_MACHINE_SPECIES_CLASSIFIED`
- `ALL_CAPABILITY_CEILINGS_REPROVED`
- `REAL_WORLD_CAPABILITY_CEILING`
- `UNIVERSAL_INTELLIGENCE_MEASURE`
- `COMPLETE_GMI`

No Section-K capability re-audit, real-system validation, or architecture selection is claimed.