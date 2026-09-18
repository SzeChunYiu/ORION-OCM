# AG6 — three universal low-level bases on one charged frame (START HERE)

AG6 asks for at least three radically different universal low-level bases at bounded executable
scope, a comparison of them, and a test of whether higher MI laws survive across them. Only the
register/counter basis existed on `main`. This package builds the other two and runs the comparison
and the test.

## What "universal" means here

`REGISTERED_FINITE_SCOPE_ONLY`. The registered class is `MEALY_2x2` — all 256 two-state binary
Mealy machines — on all 15 `{0,1}`-words of length `0..3`: **3840 tasks, identical for all three
bases**. A basis is registered-universal when it realizes all 256 exactly. That is not Turing
universality and is not evidence for it. The Turing universality of combinatory logic is
Schönfinkel's and Curry's, of elementary cellular automata Cook's, of counter machines Minsky's.
`COMBINATORY_BASIS_TURING_UNIVERSAL_PROVED_HERE`, `CELLULAR_BASIS_TURING_UNIVERSAL_PROVED_HERE` and
`UNIVERSAL_SIMPLICITER` are registered forbidden promotions.

## The three bases

| basis | signature | one-step relation | result |
|---|---|---|---|
| `REG` register/counter | `READ INC DECJZ EMIT HALT` | one instruction fires | 3840/3840, ≤22 steps |
| `CMB` combinatory/rewrite | generators `S`, `K`, application | `S x y z -> x z (y z)`, `K x y -> x` | 3840/3840, ≤403 contractions |
| `CEL` cellular/local | cell alphabet `Sigma`, one rule `d : Sigma^3 -> Sigma` | one synchronous radius-1 sweep | 3840/3840, ≤4 sweeps |

0 mismatches, 0 budget exhaustions anywhere. `REG` reproduces the merged parent's published census
(256 machines, 15 words, 3840 comparisons, 0 mismatches) exactly.

## Headline numbers

| quantity | value |
|---|---|
| tasks, identical across bases | `3840` |
| machines realized, `REG / CMB / CEL` | `256 / 256 / 256` |
| distinct behaviours the 256 machines induce on `W` | `148` |
| artifact size ranges | `REG 40..52` · `CMB 249..297` · `CEL 1930..14418` |
| `CMB` size under the naive abstraction instead | `147,821..171,149` |
| attained step bound per semantic unit | `REG 11/2` · `CMB 403/4` · `CEL 1/1`, all `ATTAINED` |
| the same bound read off the declared range | `VACUOUS` in all three rows |
| cross-basis step ratio, worst task | `CMB/REG = 397/16` · `CEL/REG = 1/4` |
| size-ranking discordant pairs out of 32,640 | `REG:CMB 2332` · `REG:CEL 4404` · `CMB:CEL 5934` |
| discordant pairs between the two bracket-abstraction algorithms | **`0`** |
| geometry, max out-degree | `REG 1` · `CEL 1` · `CMB 217` |
| `CMB` branching configurations whose successors share one normal form | `342/342`, `344/344`, `346/346`, `348/348` |
| one-edit preserving fraction | `REG 185/562` · `CMB 175/1144` · `CEL 286893/290228` |
| unrestricted cellular rule space | `18 ** 5832`, exactly — 7322 decimal digits |
| **capability/cost Pareto frontiers** | **`REG 4` · `CMB 4` · `CEL 16`, pairwise symmetric differences `6 / 12 / 18`** |
| verdict | **`LAW_DOES_NOT_SURVIVE`**, non-vacuous, non-degenerate |
| gates · tests · hostiles · nulls | `9/9` · `98/98` in normal and `-O` · `13/13` detected · `0` reproductions |

## The result that matters

The same capability battery `Q` transfers across the three bases exactly, because realization is
exact. What does not transfer is which machines are worth building. The Pareto-undominated set over
`(capability, charged size)` is `{0,1,2,3}` in the register basis, `{3,7,11,15}` in the combinatory
basis, and a 16-element set in the cellular basis: three bases, three different answers to "which
morphology sits on the frontier".

That verdict cannot be blamed on the accounting. The frontier depends on cost only through the
within-basis *ordering* of cost, so it is invariant under every strictly increasing normalization
applied uniformly across the 256 machines — verified executably for `x -> 7x`, `x -> x + 1000` and
`x -> x^2`, unchanged in all three bases. The invariance class stops there: machine-dependent
reweighting does move the frontier (4 elements to 1), which is a registered hostile, and the
stronger reading is a forbidden promotion.

This is AG6's own thesis in quantified form. Universality is common to all three bases and predicts
nothing about the frontier; the description bias of the basis predicts it.

## The boundary you must not drop

The row asks for four comparisons. Three — overhead, description bias, reachability geometry — are
delivered on the common frame. The fourth, developmental search burden, is delivered **only in its
one-edit local-search reading**, frozen before measurement. Its uniform-enumeration reading is
**proved not executable**: the cellular rule space over the largest registered alphabet has exactly
`18 ** 5832` members. This tranche refuses to repair that by declaring a restricted rule schema,
because a restriction chosen by the author to make the measurement possible would narrow the row in
order to close it and would then dominate the answer. The row's `not_closed` entry states this.

A second boundary: on the *step* coordinate the cellular cost is constant at 49 for all 256
machines, so its frontier degenerates to `argmax Q`. That coordinate is marked
`DEGENERATE_CONSTANT_COST` and does not carry the verdict. The size coordinate, non-degenerate in
all three bases, does.

## Evidence

- **Two materially independent routes.** Route B evaluates the **source lambda term directly** under
  normal order with capture-avoiding substitution and compares de Bruijn normal forms — bracket
  abstraction and the `S`/`K` machine are both bypassed; it runs the automaton as a rule table
  applied as a block map over shifted sequences (Curtis–Hedlund–Lyndon form); it re-derives the
  register program with an integer-coded dispatch interpreter; it counts Kendall by a Fenwick sweep
  and the frontier by sort-and-sweep. Every quantity in the agreement set agrees exactly. The `CMB`
  step counts are **declared out** of the agreement set: a contraction count is strategy- and
  representation-relative, as AJ5 and AG5 already say of charged instruction counts.
- **13 hostiles, all detected, each with a clean control.** Including a planted radius-2 dependence
  that the locality checker catches (504 violations against 0), a pointwise control rule (0/4500
  left-dependence against the true rule's 640/4500), and machine-dependent reweighting of the cost.
- **A perturbation that could not move its quantity was excluded, not counted.** The unsound eta
  rule compiles to a byte-identical term for all 256 machines here, so it is recorded as inert
  rather than reported as a hostile.
- **Nulls.** All 119 non-identity register opcode-role permutations (exhaustive), all 11
  non-identity combinatory contraction-rule variants (exhaustive) and 200 cellular alphabet
  relabelings reproduce the full census `0` times.
- **No-alarm case asserted.** Every detector silent on the true configuration.
- **Every bound classified.** `ATTAINED`, `VACUOUS`, `STRICT_UNATTAINED` or `LOWER_BOUND_ONLY`. The
  bounded reachable set (`≥ 50,000` nodes) is published as `LOWER_BOUND_ONLY`, not as a count.

## Reproduce

```
python3 -I -B  research/gmi-833-ag6-universal-bases-v1/ag6_universal_bases_v1.py
python3 -I -B  research/gmi-833-ag6-universal-bases-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-ag6-universal-bases-v1/test_ag6_universal_bases_v1.py
```

Route A about 80 s, route B about 60 s, the tests about 2 s. Stdlib only, exact integer and
`Fraction` arithmetic throughout; the test suite asserts that no float appears anywhere in the
receipt.

## Files

`FREEZE_V1.md` (commit `243ec345`, **before** the implementation commit `95347c89`) ·
`AG6_THEOREMS_V1.md` (`AG6B-1` … `AG6B-7`) · `PARENT_LEDGER.md` (verified DOIs; books marked as
having none) · `RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` ·
`MANIFEST_V1.json` · `ISSUE_833_COMMENT_RECONCILIATION_V1.json`.
