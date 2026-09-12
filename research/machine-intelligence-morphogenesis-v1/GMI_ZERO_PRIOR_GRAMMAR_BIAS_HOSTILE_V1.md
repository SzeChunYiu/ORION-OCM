# GMI Zero-Prior Grammar-Bias Hostile v1

Status: **FALSIFICATION / SUCCESSOR FREEZE — PREDECESSOR K4 TOY PARTIALLY REOPENED**

Status date: 2026-09-12.

Purpose:

> Attack the exact zero-prior rediscovery microscope with a materially different expression grammar. The goal is to determine whether the alleged coefficient-vs-memory negative twin was genuinely structurally incompressible or only difficult in the hand-registered polynomial encoding.

---

# 1. Predecessor claim under attack

`GMI_ZERO_PRIOR_EXACT_REDISCOVERY_MICROSCOPE_V1.md` used the five-point target

```text
[0,0,0,0,1]
```

as a negative twin for shared polynomial coefficient state. In the polynomial-coefficient grammar its minimum interpolation degree is four, so under the registered coefficient-vs-cell price the indexed-cell realization wins.

That result remains correct **inside that grammar**.

The stronger interpretation

> this target is generally poorly compressible and therefore a valid architecture-neutral memory twin

was not established.

---

# 2. Independent expression grammar

Register a different low-level DSL over input `x in F_5`:

```text
primitive terminals:
    x
    constants 0,1,2,3,4

binary operators:
    add modulo 5
    multiply modulo 5
    equality, returning 1 for equality and 0 otherwise

cost:
    one AST node for every terminal/operator
```

No polynomial-degree primitive is present.

For every expression, only its five-output semantic vector matters. Dynamic programming over semantic vectors computes the minimum AST-node count for every function `F_5 -> F_5`.

There are exactly

\[
5^5=3125
\]

such functions, so the registered finite search is exhaustive over semantics.

---

# 3. Falsification of the predecessor negative twin

## Exact result GB-1

Under the expression grammar above,

```text
[0,0,0,0,1]
```

has a three-node realization:

```text
eq(4,x)
```

Therefore it is **more compact in this grammar than the stable affine target**

\[
2x+1 \pmod 5,
\]

whose minimum registered expression cost is five AST nodes:

```text
1 + 2*x
```

(up to commutation/equivalent syntax).

### Verdict

The predecessor negative twin is RED as a **cross-grammar incompressibility control**.

Preserve the original receipt because it remains a valid statement about the polynomial-coefficient versus indexed-cell candidate set. Do not promote it to architecture-neutral K4 evidence.

---

# 4. Exhaustive successor hostile

The semantic dynamic programme exhaustively reaches all 3125 functions under the richer DSL by AST cost 15.

A maximally difficult registered target is

```text
[4,2,4,1,1]
```

with minimum AST-node cost exactly

\[
15.
\]

One minimum expression found is

```text
1 + 3*(eq(1,x) + eq(eq(3,x),eq(4,x)))
```

where all arithmetic is modulo five and equality returns 0/1.

There is exactly one semantic function at cost 15 in this registered grammar.

This target is frozen as the successor **grammar-hard twin** for the expression DSL.

---

# 5. What the result means

It does **not** prove `[4,2,4,1,1]` is intrinsically incompressible. Another grammar could contain a primitive that makes it trivial.

That is precisely the point.

Finite-description compressibility is always relative to a description language unless one pays the compiler/grammar description cost and works with an invariance theorem up to additive compiler constants.

Therefore zero-prior coefficient-vs-memory prediction must not use a single hand-chosen labeling as evidence of architecture-neutral incompressibility.

---

# 6. Revised zero-prior compression protocol

For a serious coefficient/shared-law versus memory experiment:

1. freeze at least three materially different low-level grammars;
2. charge grammar/compiler description and search cost;
3. estimate/compute target description length under each grammar;
4. include semantic remints;
5. use target **families/distributions**, not one handpicked vector, wherever possible;
6. require the predicted shared-law/memory crossover to survive encoding changes or explicitly model encoding dependence;
7. hold out the protected grammar/search encoding when feasible.

A more architecture-neutral quantity is a registered minimum description/lifecycle burden

\[
K_{\mathcal G}(f)+B_{eval/update}(f)
\]

reported across multiple grammars `G`, rather than polynomial degree alone.

---

# 7. Theory correction

The P0 shared-law theorem remains valid:

- if the legal target family has size `M`, exact target identity requires at least `log2 M` bits;
- arbitrary independent tables require `N log2 q` bits;
- sparse residual families have exact Hamming-ball cardinality.

What failed was using one surface target and one representation class as a proxy for the unknown target-family description complexity.

Thus the corrected hidden variable is:

> **effective semantic description complexity under a registered grammar ensemble and lifecycle price**, not historical model degree.

---

# 8. Claim impact

Update the zero-prior evidence interpretation:

```text
coefficient-vs-memory toy in polynomial grammar:
    exact local GREEN retained

cross-grammar architecture-neutral coefficient/memory K4 claim:
    REOPENED / RED predecessor twin

richer-grammar successor hostile:
    FROZEN
```

Other exact toy rediscovery atoms (recurrence, routing, symmetry, rank) are not invalidated by this specific hostile, but each must receive analogous independent-encoding attacks before broad K4 status.

---

# 9. Desired successor terminal

`ZERO_PRIOR_COMPRESSION_MULTI_GRAMMAR_GREEN`

Only after the compression/memory phase prediction survives disjoint grammars, remints and charged search/compiler costs.
