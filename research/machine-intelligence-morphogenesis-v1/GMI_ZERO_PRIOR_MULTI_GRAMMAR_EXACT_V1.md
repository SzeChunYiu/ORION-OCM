# GMI Zero-Prior Multi-Grammar Exact Comparison v1

Status: **EXECUTABLE EXACT SUCCESSOR / FINITE MULTI-GRAMMAR COMPRESSION CALIBRATION**

Status date: 2026-09-12.

Purpose:

> Replace the falsified single-grammar coefficient/memory negative twin with an exact finite comparison across several preregistered description languages under one frozen binary accounting scheme.

---

# 1. Target universe

Registered exact target family:

\[
\mathcal F=\{f:F_5\to F_5\},
\qquad
|\mathcal F|=5^5=3125.
\]

Every target is one five-symbol output vector.

---

# 2. Frozen description portfolio

A two-bit grammar tag selects one of three encodings (one tag value remains unused/reserved).

## G1 — explicit table

Each of five outputs is stored in a fixed three-bit symbol code.

Target code length:

\[
C_{table}=2+5\cdot3=17\text{ bits}.
\]

## G2 — polynomial coefficients over `F_5`

Every function `F_5->F_5` has a unique polynomial representative of degree at most four.

Encode:

```text
2-bit grammar tag
3-bit coefficient-count field k in {1,...,5}
k coefficients, 3 bits each
```

For minimum degree `d=k-1`,

\[
C_{poly}(d)=2+3+3(d+1)=8+3d.
\]

Therefore costs by degree are:

```text
d=0 -> 8 bits
d=1 -> 11 bits
d=2 -> 14 bits
d=3 -> 17 bits
d=4 -> 20 bits
```

## G3 — generic expression DSL

Terminals:

```text
x, 0,1,2,3,4
```

Binary operators:

```text
add mod 5
multiply mod 5
equality -> {0,1}
```

Use prefix notation; arities make the tree uniquely parseable. Nine token types fit in fixed four-bit token codes.

For minimum AST node count `s`,

\[
C_{expr}(s)=2+4s.
\]

The earlier exhaustive grammar hostile established the semantic minimum-node histogram:

```text
s=1:   6 functions
s=3:  13 functions
s=5:  72 functions
s=7: 237 functions
s=9: 791 functions
s=11:1438 functions
s=13:567 functions
s=15:1 function
```

---

# 3. Exact portfolio description length

Define

\[
C^*(f)=\min\{C_{table}(f),C_{poly}(f),C_{expr}(f)\}.
\]

## Theorem MGX-1 — exact multi-grammar cost distribution

Across all 3125 exact target functions, the minimum registered costs are:

```text
6 bits:     6 functions
11 bits:   19 functions
14 bits:  105 functions
17 bits: 2995 functions
```

No target has a minimum registered cost of 8, 20 or larger because another grammar dominates at those costs.

### Explanation

- The six one-node expression functions (five constants plus identity `x`) cost six bits.
- The remaining 19 exact degree-one affine functions are cheapest in the polynomial grammar at 11 bits.
- The 100 degree-two polynomial functions cost at most 14 bits.
- Five degree-four equality-indicator functions `eq(x,c)` are also 14-bit expressions and are the important cross-grammar correction missed by polynomial degree alone.
- The remaining 2995 functions admit no saving relative to the fixed 17-bit table under this portfolio. Degree-three polynomial functions tie the table; almost all degree-four functions are strictly table-cheapest.

The counts sum to 3125.

---

# 4. Exact random-label consequence

Let protected target be uniformly random over all independent labelings in `F_5^5`.

Then under the frozen three-grammar portfolio:

\[
P(C^*(F)<17)
=
\frac{130}{3125}
=0.0416.
\]

Therefore

\[
\boxed{P(C^*(F)=17)=\frac{2995}{3125}=0.9584.}
\]

So 95.84% of uniformly random exact labelings obtain **no per-target description saving** relative to the explicit fixed table under this registered grammar portfolio.

This is a finite exact counterpart to the multi-grammar counting theorem.

---

# 5. Strict table winners versus ties

Degree-three polynomial targets have

\[
C_{poly}=C_{table}=17.
\]

There are 500 degree-three functions.

Among degree-four functions, exactly five equality-indicator functions are compressed by the expression grammar to 14 bits. Therefore:

```text
strict table winners: 2495
table/poly ties:        500
compressed by some shared grammar: 130
```

Thus the statement “95.84% obtain no code-length saving” is stronger and cleaner than claiming the table is uniquely optimal in every one of those cases.

---

# 6. Positive and negative family interpretation

## Structured positive family

Affine functions

\[
f(x)=ax+b
\]

occupy a tiny low-description subset and are compressed by polynomial/expression structure.

## Architecture-neutral finite negative family

Uniform independent labels are overwhelmingly not compressed by the frozen grammar portfolio.

This is the correct style of negative control: a **distribution/family** whose high description complexity is quantified prospectively, not a visually irregular handpicked target.

---

# 7. Compiler and grammar accounting

The per-target comparison above assumes all three interpreters/grammars are frozen reusable infrastructure and therefore only a two-bit selector is charged per target.

For a different experimental constitution, grammar/compiler description and search burden must be charged explicitly or amortized over a declared horizon.

A target-specific operator introduced after protected data is seen is contamination and invalidates the result.

---

# 8. What this closes

The predecessor cross-grammar twin failure is repaired at this finite registered scope:

```text
single polynomial grammar negative twin:
    insufficient / predecessor RED

one richer DSL hostile:
    predecessor falsified

three-grammar exhaustive portfolio:
    exact full-universe comparison

random independent-label negative family:
    95.84% no description saving in the registered portfolio
```

---

# 9. What remains open

This does **not** establish language-independent Kolmogorov complexity.

Still required for serious K4 compression/memory closure:

```text
larger target spaces
additional disjoint grammars/search encodings
grammar/compiler/search burden at scale
approximate/lossy compression
learning rather than exact semantic enumeration
protected held-out grammar/family generators
```

---

# 10. Terminal

Finite exact successor terminal:

`ZERO_PRIOR_COMPRESSION_MULTI_GRAMMAR_EXACT_GREEN`

This is deliberately narrower than broad real-family K4 closure.
