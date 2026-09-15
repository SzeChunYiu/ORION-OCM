# GMI #602 B14 — selector-plus-emitter derivation

Status: **P1 formal theorem plus P2 exhaustive finite certificate**

Scope: finite obligations; exact semantics; declared selector and emitter repertoires; full selector-description burden.

Claim ceiling: `SELECTOR_PLUS_EMITTER_REWRITE_OPERATOR_DERIVED_AT_REGISTERED_SCOPE`.

## The gap being closed

The existing B14 witness derives the slot-carrying emitter while holding a positional pattern selector fixed. That proves only half of a rewrite instruction. This artifact derives the complete `(selector, emitter)` operator and compares the selector families named by #602: positional pinning, equality constraints, and arbitrary subsets.

No production-system, rewrite-system, decision-tree, or architecture label occurs in the executable candidate descriptions. Candidates are finite subsets paired with primitive emitters: constants and input-coordinate projections.

## Theorem B14-S1: sound-cover characterization

Let `D` be any finite input domain, `Y` any output set, `f:D -> Y` the protected obligation, `S` a declared selector repertoire with each selector denoting a subset of `D`, and `E` a declared emitter repertoire with each `e:D -> Y`.

Define `(s,e)` to be sound exactly when

```text
for every x in s: e(x) = f(x).
```

A finite unordered instruction set `R subset S x E` implements `f` exactly iff:

1. every instruction in `R` is sound; and
2. the selectors in `R` cover `D`.

Proof. If both clauses hold, every admitted instruction emits `f(x)` on every selected input, and coverage supplies at least one admitted instruction for every input; overlapping instructions agree because each equals `f(x)`. Conversely, an exact implementation cannot leave an input uncovered, and any instruction that emits a different value on a selected input violates exactness there. This proves both directions. The minimum instruction count is therefore exactly the minimum set cover over sound selector-emitter pairs. No rewrite operator was assumed: sound selection plus reusable emission is the operator forced by exact coverage.

For ordered/default rules, replace soundness by residual soundness after earlier selectors. The existing B14 ordered-cover result is that companion case; this artifact intentionally isolates unordered exact selection so selector-family effects cannot hide in priority semantics.

## Theorem B14-S2: representation and selection are separate

For any nonconstant binary obligation, arbitrary-subset selectors admit a two-rule realization using the positive and negative fibers with constant emitters. This is not a free universal solution: each arbitrary subset is a `|D|`-bit table. Rule count and selector-description burden are distinct resource coordinates.

Consequently, minimizing rule count alone privileges arbitrary subsets by construction. A neutral comparison must either retain the Pareto vector or apply a prospectively frozen price vector to at least:

```text
(instruction count, selector description, emitter description,
 matching/execution cost, verification cost, revision cost).
```

This is a formal anti-rigging result. Expressivity alone cannot derive the selector language.

## Exact matched twins

The executable microscope enumerates all eight three-bit inputs, all five primitive emitters (`0`, `1`, `x0`, `x1`, `x2`), all 27 positional patterns, all 11 distinct satisfiable equality/inequality conjunctions, and all 255 nonempty arbitrary subsets. Breadth-first dynamic programming exhausts every reachable coverage mask at each instruction depth and retains the least selector-description burden at that depth.

The worlds hold domain, information access, emitters, exact verifier, and search fixed. Only the obligation changes.

| obligation | positional | equality | arbitrary subset |
|---|---:|---:|---:|
| `x0 XOR x1` | 3 rules | **2 rules** | 2 rules / 16 mask bits |
| `if x0 then x1 else x2` | **2 rules** | 3 rules | 2 rules / 16 mask bits |

The reversal is the result. Equality-sensitive obligations select an equality language; position-gated obligations select positional pinning. There is no family-name-only winner. Arbitrary subsets tie the two-rule minima but pay table-sized selector descriptions, exposing why uncharged arbitrary predicates would smuggle the answer into the selector.

The negative mutation replaces XOR with projection `x0`; the same equality-family search must collapse to one global zero-atom rule. This rejects a certificate that ignores the target.

## Lifecycle law

Let rule `r=(s,e)` have acquisition, description, match, emit, verification, revision, and storage coordinates. For query distribution `mu` and horizon `q`, an exact instruction set has lifecycle vector

```text
C(R) = acquisition(R) + storage(R) + verification(R)
     + q * E_mu[matching(R,x) + emission(R,x)]
     + revision(R,H).
```

Hard budgets first remove inadmissible covers. Without fixed prices, retain the Pareto frontier. With a frozen nonnegative price vector, minimize the resulting scalar burden. The selected rewrite operator is therefore obligation- and lifecycle-relative, not a primitive architecture macro.

## Strongest-parent disposition

Exact set cover owns the finite minimization; decision lists/rule learning own cover-based induction; production/rewrite systems own selector-emitter execution; discrimination networks own efficient matching. GMI contributes no new mechanism here. Its residual is the architecture-neutral obligation/resource criterion that decides which parent selector/emitter repertoire is admissible and cheapest.

## Falsifier and boundary

Falsify this registered result by exhibiting a legal cover smaller than the exhaustive minimum, a retained rule that is unsound on one selected input, a failure of the matched-twin reversal, or a purported neutral comparison that charges structured selector descriptions but gives arbitrary subsets free masks.

The theorem covers every finite `D` at the formal level; the executable certificate covers the registered eight-input microscope. It does not establish an empirical, real-scale, or universally best selector language and makes no new-domain claim.

The following stronger claims remain forbidden:

```text
UNIVERSAL_BEST_SELECTOR_LANGUAGE
UNBOUNDED_EMPIRICAL_REWRITE_RECOVERY
NEW_SYMBOLIC_DOMAIN
```
