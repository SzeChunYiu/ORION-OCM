# GMI #833 parent-equivalence freeze v1

**Parent:** #833 Section C  
**Child:** #846  
**Source main:** `2fffb14447193cbfbed3224508a077f2d4f5d2dd`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the target statements, finite witnesses, hostile boundaries, and claim ceiling **before** the executor, tests, result receipt, reconciliation spec, or CI workflow exist on this branch.

## Frozen theorem targets

### MN-1 — deterministic language specialization

For a reachable deterministic total finite transition system with alphabet `Sigma` and binary acceptance output, define state future-response equivalence

`p ~ q  iff  for every w in Sigma*, acceptance(delta*(p,w)) = acceptance(delta*(q,w))`.

Target: `~` is a right congruence; access histories reaching equivalent states are exactly Myhill–Nerode equivalent for the recognized language; quotient cardinality is the minimum reachable DFA state count.

Frozen finite witness: a reachable 4-state binary-alphabet DFA with exactly three future-response classes, one class containing two distinct reachable states.

### BI-1 — deterministic bisimulation boundary

For deterministic total labeled transition systems where the registered observation includes the state/output label, target equality:

`exact future-response equivalence = greatest output-respecting strong bisimulation`.

Frozen finite certificate: exhaust every 3-state, 2-action, binary-output deterministic total system (`2^3 * 3^(3*2) = 5,832` machines) and compare two independently implemented partitions.

Frozen hostile: nondeterministic systems do **not** inherit the equality. Use the standard branching counterexample in which `p -a-> p_b,p_c` and `q -a-> q_bc`, with `p_b -b-> t`, `p_c -c-> t`, and `q_bc` having both `b` and `c` transitions. The finite trace sets agree (`epsilon,a,ab,ac`) while strong bisimulation fails.

### PS-1 — predictive-sufficiency quotient

Let `H` be a finite registered history set and `T_all` the full registered future-test set. Each history `h` has an exact predictive-law vector `P_h` over all tests. Define

`h ~pred h' iff P_h = P_h'`.

Target: the quotient statistic `[h]` is exact predictive-sufficient; every exact predictive-sufficient statistic `S` satisfies `S(h)=S(h') => h ~pred h'`, hence every fiber of `S` lies inside one quotient class. Therefore the quotient has minimum cardinality among exact predictive-sufficient statistics, up to relabeling, at the registered finite exact scope.

Frozen witness: three histories with two predictive classes, including two histories with identical full predictive law.

### PSR-1 — predictive-state-coordinate boundary

Target: a vector of test predictions represents the predictive quotient injectively **iff** the chosen tests separate every pair of predictive-equivalence classes. An incomplete test set may merge histories that differ on an unrepresented test.

Frozen witness: two histories agree on a one-step test with probability `1/2`, but differ on a two-step test (`1/2` versus `1/4`).

### SUF-1 — classical/predictive sufficiency incomparability

Freeze two finite counterexamples.

1. **Predictive sufficient, not parameter sufficient.** Parameter `theta in {0,1}`; observed history `Y=theta` deterministically; future `Z` is a fair bit independent of `theta`. Constant statistic is sufficient for predicting `Z` but not sufficient for `theta` from `Y`.
2. **Parameter sufficient, not predictive sufficient.** Parameter `theta in {0,1}`; history `H=(Y,S)` with `Y=theta` and independent fair `S`; statistic `T(H)=Y` is sufficient for `theta`, but future `Z=S`, so `T` merges histories with different future laws.

### SUB-1 — strongest-parent map

The result must classify the relation between the #833 behavioral/predictive equivalence objects and these parents as one of `EXACT_SPECIALIZATION`, `STRICT_BOUNDARY`, or `INCOMPARABLE`, with explicit assumptions and nearest counterexamples:

- Myhill–Nerode / DFA minimization;
- deterministic output-respecting bisimulation / state abstraction;
- classical sufficient statistics;
- predictive state representations.

## Frozen literature anchors

Use parent terminology rather than new names where semantics coincide:

- Myhill–Nerode theorem / DFA state equivalence and minimization.
- Strong bisimulation and state abstraction/homomorphism literature.
- Fisher–Neyman/statistical sufficiency and minimal sufficient statistics.
- Predictive state representations: state as predictions of tests; completeness depends on a sufficient/core set of tests.

The mathematics owned by these parents must be explicitly subtracted from any GMI residual.

## Frozen falsifiers

The tranche fails if any of the following occurs:

- the 5,832-machine deterministic census finds a disagreement between future-response and bisimulation partitions;
- the nondeterministic hostile is accidentally classified bisimilar or has unequal registered trace sets;
- a purported predictive-sufficient statistic merges two distinct full predictive-law vectors;
- an incomplete PSR test set is called injective/minimal despite merging distinct predictive classes;
- either SUF-1 implication counterexample fails;
- finite/exact results are promoted to unrestricted stochastic-process minimality;
- trace equivalence is promoted to universal strong bisimulation;
- classical parameter sufficiency is identified with predictive sufficiency without assumptions.

## Claim ceiling

`GMI_PARENT_EQUIVALENCE_BOUNDARIES_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions from this tranche alone:

- `ALL_GMI_EQUIVALENCE_IS_MYHILL_NERODE`
- `TRACE_EQUIVALENCE_EQUALS_BISIMULATION_UNIVERSALLY`
- `CLASSICAL_SUFFICIENCY_EQUALS_PREDICTIVE_SUFFICIENCY`
- `ALL_PSRS_ARE_MINIMAL`
- `UNIVERSAL_STOCHASTIC_MINIMALITY`
- `COMPLETE_GMI`

No result on #844 terminology, #845 corpus census, G0 grammar, morphology selection, capability prediction, independent replication, or real-scale validation is claimed.