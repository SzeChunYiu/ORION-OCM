# Stage C-v1 parent mapping — exact finite-state/adaptive-table sufficiency

## Result

For the executed Stage C-v1 structured two-cell subproblem, every candidate morphology has an exact canonical representation as an ordinary finite adaptive state machine / lookup table.

Therefore the structured local-unit semantics are **not a new class of adaptive computation** at this scope.

Primary terminal:

```text
PARENT_STATE_MACHINE_SUFFICIENT_FOR_STAGE_C1_SEMANTICS__LOCAL_STRUCTURE_REMAINS_RESOURCE_BIAS
```

This is an upward result: stop searching for novelty in the low-level state-transition object and move the scientific question to representation/resource/developmental morphology selection.

---

# 1. Exact compilation

A Stage C-v1 morphology has two Boolean state cells:

```text
S = {0,1}^2
```

external input:

```text
x in {0,1}
```

and, on labelled development events:

```text
l in {0,1}
```

Its structured local update rules induce a deterministic whole-machine transition:

\[
T_M : S \times X \times L \to S
\]

and its output expression induces:

\[
O_M : S \times X \to Y.
\]

Construct the exact parent `P2` table by enumerating every row:

```text
for each (s0,s1,x,l): store T_M(s0,s1,x,l)
for each (s0,s1,x):   store O_M(s0,s1,x)
```

This compilation preserves **every** finite history, state trajectory and output because the parent table implements exactly the same transition and output maps.

No approximation is involved.

---

# 2. Exact direct-table size at this registered scope

Transition table:

```text
|S| * |X| * |L| = 4 * 2 * 2 = 16 rows
```

Each row stores two next-state bits:

```text
32 transition bits
```

Output table:

```text
|S| * |X| = 4 * 2 = 8 rows
```

with one output bit per row:

```text
8 output bits
```

So a raw uncompressed direct representation requires:

```text
40 behavior/update bits
```

before metadata/identity overhead.

The structured grammar can encode many of its reachable machines more compactly than this direct table. That is a **representation/resource result**, not a new semantics result.

---

# 3. The reverse direction does not hold under the shallow structured bound

An arbitrary P2 adaptive lookup table ranges over a much larger transition/output family than the depth-1 structured grammar.

The structured CROSS_CELL full arm reaches only:

```text
294 exact developmental classes
```

under the registered history horizon.

Therefore:

```text
structured grammar ⊂ exact adaptive-table parent
```

at this scope.

The structured grammar is an **inductive/compression bias over a parent formalism**, not a more general computational ontology.

---

# 4. Why local structure can still matter

Parent semantic sufficiency does not imply resource equivalence.

The executed census shows:

```text
LOCAL_ONLY developmental reach = 95 classes
CROSS_CELL developmental reach = 294 classes
```

and:

```text
{AND,XOR} and {NOT,AND,XOR} have equal registered reach
but NOT lowers mean minimum compilation cost.
```

Thus local topology/primitive structure can matter through:

```text
description length
compositional depth
update locality
communication work
search bias
acquisition cost
revision cost
```

These are precisely the coordinates on which a morphology/phase theory should operate.

---

# 5. Consequence for the “fundamental cognitive unit” question

Stage C-v1 does **not** justify a new ORION-specific primitive.

The strongest current disposition is:

```text
finite/open adaptive state-machine / learner / lens / cybernetic-process parents
receive first right of refusal as the low-level substrate.
```

The fundamental scientific question moves upward from:

> What new state-transition atom did ORION invent?

into:

> Given a common adaptive-process substrate, which representation, topology, credit mechanism, update law and memory organization becomes developmentally/resource optimal under an ecology?

This is the Track-B morphogenesis/phase-law question.

---

# 6. What could reopen a new-basis claim?

Only a concrete registered residual such as:

```text
parent formalism cannot preserve required developmental semantics;
parent compilation has unavoidable material asymptotic/resource overhead;
composition law loses a required interaction/update property;
stochastic/open-ended topology semantics cannot be represented without changing the parent class;
verification/governance requirement is truly substrate-level rather than morphology-level.
```

A new name or tuple is insufficient.

Until such a residual is witnessed:

```text
DO NOT INVENT A NEW FUNDAMENTAL UNIT FORMALISM.
```
