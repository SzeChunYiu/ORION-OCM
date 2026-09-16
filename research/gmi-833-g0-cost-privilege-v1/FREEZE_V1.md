# GMI #833 Section-E E7 cost-privilege freeze

**Parent:** #833 Section E  
**Child:** #891  
**Source main:** `e91ab6c799d35453addadf4101fbc9f774472d37`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the exact finite cost object, label-remint group, isometric-remint theorem, structural-bias counterexample, hostile controls, exhaustive certificate family, reconciliation wording and claim ceiling **before** any executor, tests, result receipt, manifest, reconciliation specification or dedicated workflow exists on this branch.

## 1. Scientific question and correction

The open #833 row says:

> Prove the grammar does not privilege a known family under the registered cost model.

That wording is stronger than what the already-merged G0 grammar-bias work permits. A grammar is a syntactic candidate-space restriction and therefore a representation/search bias; the registered cost cannot be called universally family-neutral merely because family names are absent.

This tranche therefore adjudicates the row into two machine-distinct statements:

1. **Narrow positive:** the registered cost is post-hoc-family-label blind and invariant under certified cost/search **isometries**.
2. **Strong boundary:** same-semantic but non-isometric grammar recodings can reverse class costs/selection, so universal grammar neutrality is false at the registered finite witness scope.

The intended row-level terminal is therefore conditional/negative, not a claim that `G0` is unbiased.

## 2. Parent subtraction

Parent mathematics is not reclaimed here:

- SyGuS/program synthesis: a grammar explicitly restricts the candidate implementation space; this is an inductive/search bias.
- machine/encoding-dependent complexity and description measures: representation must be declared rather than silently treated as invariant.
- standard multi-objective optimization: strictly positive scalarization preserves strict coordinatewise dominance, while incomparable vectors may reverse with weights.
- #875 `gmi-833-g0-grammar-bias-v1`: finite G0 description/reachability bias and exact invariance under cost/search isomorphism are parent results.
- #863 robustness controls: alternate encodings/search algorithms/scalarizations are required audit dimensions.

The residual contribution is the exact E7 cost audit: label-blindness theorem, isometry theorem on the registered cost object, explicit same-semantics/non-isometric reversal, privilege hostiles, independent machine certificate and fail-closed #833 disposition.

## 3. Frozen finite presentation object

A presentation is

```text
p = (presentation_id, semantic_class, family_label, L, d)
```

where:

- `presentation_id` is syntax/presentation identity only;
- `semantic_class` is the protected semantic-equivalence class used for scientific comparison;
- `family_label` is a **post-hoc annotation only** and may be arbitrarily permuted;
- `L in N_{>0}` is registered description/instruction length;
- `d in N_{>=0}` is registered mutation/search distance from the frozen start.

The raw primary cost vector is

```text
rho(p) = (L(p), d(p)).
```

The registered diagnostic scalar family is

```text
C_w(p) = w_L L(p) + w_d d(p)
```

for the exact strictly-positive rational weight set

```text
W = {(1,1), (2,1), (1,2), (4,1), (1,4)}.
```

Scalarization never replaces the raw vector.

For a semantic class `s`, define its presentation frontier and class minimum at weight `w`:

```text
P_s = {p : semantic_class(p)=s}
mincost_w(s) = min_{p in P_s} C_w(p).
```

Selection at weight `w` is the set of semantic classes attaining the global minimum class cost. Ties remain sets; no lexical family-label tie break is permitted.

## 4. Frozen base fixture

Three semantic classes are frozen:

```text
S = {ALPHA, BETA, GAMMA}
```

and three arbitrary post-hoc family labels:

```text
F = {F0, F1, F2}.
```

Base presentations:

```text
pA0: semantic ALPHA, family F0, rho=(1,4)
pA1: semantic ALPHA, family F0, rho=(3,2)
pB0: semantic BETA,  family F1, rho=(4,1)
pB1: semantic BETA,  family F1, rho=(2,3)
pG0: semantic GAMMA, family F2, rho=(3,3)
pG1: semantic GAMMA, family F2, rho=(5,0)
```

This fixture contains strict-dominance and Pareto-incomparability cases and enough presentations to test class minima rather than only point costs.

## 5. LABEL-1 — family-label blindness

Let `pi` be any permutation of the post-hoc family-label set `F`. Define `pi*p` by replacing only `family_label(p)` with `pi(family_label(p))`.

Target theorem:

```text
rho(pi*p) = rho(p)
C_w(pi*p) = C_w(p)
mincost_w^pi(s) = mincost_w(s)
selection_w^pi = selection_w
```

for every frozen presentation `p`, every `w in W`, every semantic class `s`, and all `3! = 6` label permutations.

This theorem is intentionally narrow: labels are irrelevant because they are not inputs to the registered cost, not because the grammar is representation-neutral.

## 6. ISO-1 — certified cost/search isometry

An isometric grammar remint on the registered finite object is a bijection `phi` on presentations satisfying all of:

1. `semantic_class(phi(p)) = semantic_class(p)`;
2. `rho(phi(p)) = rho(p)` exactly;
3. presentation adjacency/search edges are transported bijectively (where a search graph is supplied);
4. no family-label-dependent adjustment is introduced.

Then for every `w in W`, point costs, class minima, raw Pareto order and selected semantic-class sets are invariant.

The finite machine certificate must test all presentation permutations that satisfy the semantic-and-rho isometry predicate on the base fixture and reject non-bijections, semantic mutations, raw-cost mutations and search-edge mutations.

## 7. BIAS-1 — same-semantics non-isometric reversal

Freeze two grammar presentations with identical semantic coverage `{ALPHA,BETA}` but different raw coding/search geometry:

```text
Grammar GA:
  ALPHA: rho=(1,1)
  BETA : rho=(3,2)

Grammar GB:
  ALPHA: rho=(3,2)
  BETA : rho=(1,1)
```

At the unchanged registered weight `w=(1,1)`:

```text
selection_GA = {ALPHA}
selection_GB = {BETA}.
```

The grammars have the same semantic class set, but they are not raw-cost/search isometries. This is the decisive counterexample to the universal reading of the checkbox.

Required terminal:

```text
NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE
```

This negative boundary is not a defect in the audit; it is the scientifically correct disposition unless stronger structure is imposed.

## 8. DOM-1 — positive-weight dominance and price sensitivity

For raw vectors `x=(L_x,d_x)` and `y=(L_y,d_y)`:

- if `x <= y` coordinatewise and `x != y`, then `C_w(x) < C_w(y)` for every strictly positive `w`;
- if `x` and `y` are Pareto-incomparable, scalar winner may depend on `w`.

Frozen reversal witness:

```text
x=(1,4), y=(4,1)
C_(4,1)(x)=8  < 17=C_(4,1)(y)
C_(1,4)(x)=17 >  8=C_(1,4)(y).
```

The machine certificate must exhaust all pairs in the grid `{0,1,2,3,4}^2`, excluding identical pairs, and all frozen positive weights: zero strict-dominance reversals are allowed.

## 9. Privilege hostiles

The cost audit must fail closed on:

### H1 — target-family bonus / penalty

Any scalar cost of the form

```text
C'_w(p) = C_w(p) + b(family_label(p))
```

with nonconstant `b` is explicit family-label privilege and must return

```text
FAMILY_LABEL_COST_LEAK
```

rather than a valid E7 result.

### H2 — zero-cost family macro

A newly supplied presentation with a family-specific semantic macro and registered raw vector `(0,0)` must be rejected as

```text
ZERO_COST_FAMILY_MACRO
```

for this strictly-positive physical/search cost contract. No known-family macro may receive free description and reachability coordinates.

### H3 — lexical tie-breaking

If tied semantic classes are collapsed by family/presentation name ordering, return

```text
LABEL_DEPENDENT_TIE_BREAK
```

rather than a singleton selection.

### H4 — incomplete remint certificate

A remint that preserves semantics but not raw `(L,d)` or search adjacency is `NON_ISOMETRIC_REMINT`; it may be used as a bias counterexample but not as positive invariance evidence.

## 10. Exhaustive and independent machine targets

The implementation must report at least:

- all `3! = 6` family-label permutations × 5 weights × 6 presentations with exact point-cost identity;
- all class-minimum and selection identities under those permutations;
- all certified base-fixture presentation isometries discovered by independent predicate checking;
- the frozen GA/GB structural reversal;
- all raw-vector pairs on `{0,1,2,3,4}^2` × 5 weights for dominance preservation;
- the incomparable `(1,4)` vs `(4,1)` winner reversal;
- H1–H4 hostile detection.

A second implementation must independently compute the label-permutation and dominance results without calling the main audit helpers.

## 11. Parent-literature anchors

Load-bearing anchors to record in the post-freeze theorem note:

- Alur et al., *Syntax-Guided Synthesis*, FMCAD 2013: the candidate implementation set is explicitly supplied by a grammar.
- Blum, machine-independent complexity theory and the broader machine/coding-dependence boundary for resource measures.
- standard Pareto/multi-objective scalarization results.
- merged repository parents #875 and #863.

No novelty claim is made for those parent mathematical facts.

## 12. #833 reconciliation boundary

After and only after exact PR CI is GREEN, replace exactly the Section-E row

```text
- [ ] Prove the grammar does not privilege a known family under the registered cost model.
```

with a checked **adjudicated boundary** stating:

- registered cost is family-label blind and invariant under certified cost/search isometries;
- same-semantic non-isometric grammar recoding can reverse selected class;
- therefore universal no-privilege / unbiased-grammar wording is rejected rather than proved.

No other Section-E row is touched by this tranche.

## 13. Claim ceiling

```text
GMI_G0_COST_LABEL_BLINDNESS_AND_STRUCTURAL_PRIVILEGE_BOUNDARY_AT_REGISTERED_SCOPE
```

Forbidden promotions:

- `G0_UNBIASED`
- `NO_KNOWN_FAMILY_PRIVILEGED_UNIVERSALLY`
- `REPRESENTATION_INVARIANT_COST_UNIVERSALLY`
- `SEARCH_NEUTRALITY_PROVED`
- `ARCHITECTURE_PRIOR_FREE_GRAMMAR`
- `ALL_SCALARIZATIONS_AGREE`
- `COMPLETE_GMI`
