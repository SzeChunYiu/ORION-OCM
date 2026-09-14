# Discrete relations, rewrite emitters, and the symbolic/parametric line (B14)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/symbolic_rewrite_witness.py`.
Receipt: `microscopes/results/STAGE_SYMBOLIC_REWRITE_V1.json`.
Executed on `laptop-billy`, exit 0, byte-identical stdout across repeats;
witness and receipt md5 independently reproduced before this document was
written. 60 assertions; a deliberately mutated method is caught immediately.

## When explicit relational state is forced

A census over **all 512** binary relations on 3 objects, by two independent
methods — an exhaustive search over all 27 scalar assignments, and a structural
test (asymmetry / transitivity / negative-transitivity):

| carried by a scalar | needing explicit relational state |
|---:|---:|
| **13** | **499** |

The two methods agree on all 512, asserted as set equality. So the question is
decided twice, independently.

The matched twin controls both density and CSR-1's distinction count:

| relation | pairs | distinct rows | scalar |
|---|---:|---:|---|
| linear `0>1>2` | 3 | 3 | `(2,1,0)` |
| cyclic `0>1>2>0` | 3 | 3 | **none** — transitivity fails |

Identical in size and in distinctions; separated only by structure.

On a concrete rewrite system `{b→a anywhere}` over `{a,b}³`:

| relation | pairs | scalar |
|---|---:|---|
| derivability `x →⁺ y` | 19 | **none**, certificate: negative transitivity at `(abb, baa, aab)` |
| potential `|x|_b > |y|_b` | 22 | verified `h = (0,1,1,4,1,4,4,7)` |

> The two relations disagree on only **3 of 64** ordered pairs — and a scalar
> that agrees on 61 of 64 still cannot answer the question.

*The potential is scalar-representable **by construction**, so verifying it
confirms the verifier rather than establishing anything about rewrite systems.
The load-bearing results here are the 13/512 census and derivability's exhibited
certificate.*

## The emitter, not the operator

Minimum instructions for exact coverage of `{a,b}³`, by BFS, proved minimal:

| obligation | const | copy | substitute |
|---|---:|---:|---:|
| identity | 8 | **1** | **1** |
| set slot1 to `b` | 4 | — | **1** |
| `slot3 := ¬slot1` | 4 | — | **2** |
| flip every slot | 8 | — | 8 |

Copy-only expresses 1 of 7 obligations at any size; `const` degenerates to a
full table on 3 of 7.

**This does not close the box as written.** The box asks to derive *rule/rewrite
operators from generic transformations*. What is shown is narrower: **given
pattern-matching selectors, only the slot-carrying emitter reaches sub-`|D|`
instruction counts when the output tracks the input.** The *selector* — matching
a pattern over `{a,b,*}` — is shared by all three repertoires compared and is
**assumed, not derived**. Closing it properly needs a comparison across selector
families (positional pinning, equality constraints, arbitrary subsets).

## Compositional reuse is about closure, not compression

| family (k=3 each) | d=1 | d=2 | d=3 | d=4 | d=5 | d=6 |
|---|---:|---:|---:|---:|---:|---:|
| composing `{rotate, set-slot1-b, swap12}` | 3 | 11 | 22 | 31 | **34** | 34 |
| collapsing `{const-aaa, -bbb, -aba}` | 3 | 3 | 3 | 3 | 3 | 3 |

Priced under PVR-3 at depth 3:

| family | \|M₃\| | generator cells | table cells | break-even `r` |
|---|---:|---:|---:|---:|
| composing | 22 | 18 | 528 | **255** |
| collapsing | 3 | 18 | 72 | **27** |

Same `k`, same cell prices, same per-query work — **only the closure differs**.
The gate asserts the composing family's break-even *strictly exceeds* the
collapsing one, which is what isolates composition from the per-map compression
both families enjoy.

## Symbolic versus parametric

At `L=4` (`|D|=16`):

| obligation | instrs | symbolic | parametric | cheaper |
|---|---:|---:|---:|---|
| set slot1 to `b` (pointwise) | 1 | **8** | 16 | symbolic |
| `slot_last := slot1` (copyable) | 1 | **8** | 20 | symbolic |
| `slot_last := ¬slot1` (not copyable) | 2 | **16** | 20 | symbolic |
| flip every slot (affine) | 16 | 128 | **20** | **parametric** |
| leftmost `ab→ba` (context-sensitive) | 5 | **40** | 54 | symbolic |

> The two machines fail on **orthogonal** things: substitution cannot negate a
> slot, and coefficients cannot select on context.

**The copyability twin is the dial.** Same dependence — output slot fixed by
input slot 1 — costs 1 instruction copyable and 2 not, at both lengths. So the
axis is not *how many inputs the output depends on*; it is **how much of that
dependence the emitter cannot copy**.

*The split is exhibited at `L=4`. At `L=3` the not-copyable row is an exact
**tie**, so at that length the result is directional only.*

### Exactness

For leftmost `ab→ba` at `L=4`:

| machine | instructions | cells |
|---|---:|---:|
| unordered sound cover | 5 | 40 |
| **ordered default + exceptions** | **4** | **32** |
| exact parametric | — | 54 |

> Ordering is worth exactly **8 cells**, because a default may be *wrong* where
> an earlier instruction catches it — so it need not be sound on its own
> selector.

Tolerating error, with all 1296 defaults enumerated:

| errors | fraction | cells | vs exact |
|---:|---|---:|---:|
| 0 | 0 | 32 | +0 |
| **1** | **1/16** | **24** | **−8** |
| 4 | 1/4 | 16 | −16 |

The saving is real at **1/16** of the domain, not only at degenerate error
fractions.

## Neutral recovery

Seven obligations produce **seven distinct** measured fingerprints
`(instructions, wildcards, copies, moved-copies)`. The gate is on those measured
tuples, never on label strings:

| obligation | instrs | wild | copy | moved | reads as |
|---|---:|---:|---:|---:|---|
| identity | 1 | 3 | 3 | 0 | a bare copy |
| constant `aaa` | 1 | 3 | 0 | 0 | a constant |
| set slot1 to `b` | 1 | 3 | 2 | 0 | **a production system** |
| flip every slot | 8 | 0 | 0 | 0 | **a lookup table** |
| leftmost `ab→ba` | 2 | 4 | 4 | 2 | **a production system** |

Both degenerate ends are reached and an intermediate shape exists. Every
returned machine is executed on every input it claims to cover.

**Evidence the search is a search**: a hand-derived 4-instruction cover for
leftmost `ab→ba` at `L=3` was beaten by the BFS, which found **2** and proved it
minimal. The arithmetic scramble is defined by modular arithmetic on the string
index — never written as a selector or emitter — so there is no handed answer to
echo.

## Failures found and fixed

- A first symbolic/parametric ladder had **no parametric winner** — symbolic won
  all 8 rows and the gate aborted. Genuine vacuity: only obligations the rule
  language is good at had been chosen. Fixed by adding negation.
- A twin matcher silently paired a case **with itself**: `"copyable)"` is a
  substring of `"not copyable)"`. It would have passed on `2 == 2`; caught only
  because the assert direction was strict.
- A default search truncated to the best 40 of 1296 would have made the
  tolerance curve silently non-minimal. Removed; all 1296 now enumerated.
- `int(r[1])` parses one character, so at `L>9` slot `#10` would read as slot 1
  and return a **wrong answer without crashing**. Fixed in all four places;
  output byte-identical, so no reported number changes.
- An ordered-vs-unordered "contradiction" (4 against 5) that tripped an assert
  was not a bug — an ordered machine is strictly more expressive. It became a
  result.

## Scope

Binary alphabet, `L ≤ 4`. Selectors are positional patterns with wildcards;
emitters are slot-wise letter-or-copy. Cost is one cell per stored atom, with a
wildcard charged the same as a constant — making wildcards free would only
strengthen the symbolic side, so the reported crossover is **conservative
against it**. Parametric cost charges the whole monomial basis up to the minimal
degree per output slot, the same convention as
`GMI_LINEAR_FAMILY_DERIVATION_V1.md`.

**Falsifier.** Exhibit a relation outside the 13 that a scalar carries; or a
context-sensitive obligation cheaper parametrically at `L=4`; or a selector
family under which the copy emitter is not required for sub-`|D|` coverage.
