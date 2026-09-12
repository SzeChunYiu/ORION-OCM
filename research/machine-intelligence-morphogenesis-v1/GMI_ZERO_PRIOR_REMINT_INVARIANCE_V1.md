# GMI Zero-Prior Remint Invariance v1

Status: **EXECUTABLE EXACT SUCCESSOR / K4-STYLE PROPERTY CALIBRATION — NOT REAL-FAMILY CLOSURE**

Status date: 2026-09-12.

Purpose:

> Strengthen the exact zero-prior rediscovery microscope by requiring structural predictions to survive semantics-preserving remints rather than succeeding only in one canonical encoding.

A property is not considered robustly rediscovered if the winner changes merely because variable names, coordinate labels, state labels, edge labels or basis coordinates are renamed while the underlying registered semantic structure is preserved.

---

# 1. Coefficient state versus indexed cells under affine remint

Work over `F_5` on five query coordinates.

Canonical positive target:

\[
f(x)=2x+1.
\]

Canonical negative twin:

```text
[0,0,0,0,1]
```

Apply every invertible affine input remint

\[
x'=ax+b,
\qquad a\ne0,
\]

and every invertible affine output remint

\[
y'=cy+d,
\qquad c\ne0.
\]

The transformed positive target remains degree 1; the transformed negative twin remains degree 4.

Under the same frozen state/serve prices as the predecessor microscope, prediction is invariant:

```text
positive -> compact coefficient program
negative twin -> indexed cells
```

There are `4*5*4*5=400` remints per target.

---

# 2. Recurrent state under input/output label remint

Canonical positive task: cumulative parity.

Canonical negative twin: output current input bit.

Apply all binary input-label flips and output-label flips. The semantic automaton is conjugated/reminted, but minimal state cardinality remains:

```text
parity family -> 2 states
memoryless family -> 1 state
```

This checks that recurrence is detected from history dependence rather than from canonical bit labels.

---

# 3. Dynamic routing under input/edge permutations

Canonical positive dependency family:

```text
input 0 -> edge 0
input 1 -> edge 1
input 2 -> edge 2
```

Canonical negative twin: every input requires the same edge.

Apply every permutation of input labels and every permutation of edge labels.

The routing-opportunity variable

\[
|\cup_xE_x|-\mathbb E|E_x|
\]

is invariant under the remint, so predicted winners remain:

```text
positive -> input-conditioned edges
negative twin -> fixed edges
```

---

# 4. Symmetry tying under coordinate conjugation

Canonical positive target is a cyclic-translation-equivariant `4x4` binary operator.

Apply every permutation `p` of coordinates and conjugate both:

```text
the target operator
the registered cyclic group action
```

by the same remint.

The target remains invariant under the reminted group action and has four ordered-pair orbits/independent tied parameters.

A one-entry symmetry-breaking negative twin is reminted identically and remains non-equivariant.

Prediction remains:

```text
positive -> orbit/group tying
negative twin -> free matrix
```

This is stronger than testing only the canonical circulant matrix representation.

---

# 5. Low-rank residual under row/column coordinate remint

Canonical positive residual has GF(2) rank 1. Negative twin has rank 4.

Apply every row permutation and column permutation. Rank is invariant, so the frozen factor/full-state burden comparison remains:

```text
rank 1 -> rank factorization
rank 4 -> full matrix
```

---

# 6. Acceptance rule

A property passes this successor only if:

1. the semantic remint preserves the registered obligation;
2. the hidden structural coordinate is mathematically invariant/equivariant under the remint;
3. exhaustive remints at the registered finite scope preserve the predicted positive winner;
4. matched negative twins preserve the predicted flip;
5. no remint identifier is given to the selection rule as a shortcut.

Terminal:

`ZERO_PRIOR_EXACT_REMINT_INVARIANCE_GREEN`

---

# 7. Claim ceiling

This is still a small exact grammar with hand-registered primitive families and remint groups. It strengthens mechanism evidence but does not establish broad K4 closure for real machine-learning families.

A stronger successor must widen the primitive grammar and hold out whole realization families/search encodings, not merely remint coordinates inside known primitive classes.
