# GMI Zero-Prior Exact Rediscovery Microscope v1

Status: **EXECUTABLE EXACT MICRO-SCOPE / NOT REAL-FAMILY K4 CLOSURE**

Status date: 2026-09-12.

Purpose:

> Test the zero-prior derivation operator on small exact worlds where historical family names are hidden and only low-level state/evaluation primitives plus lifecycle prices are available.

This is a calibration of the *rediscovery mechanism*, not evidence that real regression/RNN/attention/CNN/adapter families have already reached K4.

---

# 1. Constitution

The search is allowed low-level primitives, not named architecture macros.

Registered primitive alternatives include:

```text
q-ary coefficient list + Horner evaluation
indexed q-ary cells
finite deterministic state transition/output tables
fixed dependency-edge set
input-conditioned dependency-edge map
free matrix parameters
parameter tying by a supplied group action
full matrix state
matrix factorization at searched rank
```

The ecology supplies semantic targets and resource prices only.

For every positive ecology there is a matched negative twin expected to select a different primitive realization.

---

# 2. Shared coefficient state versus indexed cells

Domain: five query points over `F_5`.

Search candidates:

```text
coefficient list of degree d=0,...,4, found by exact enumeration
indexed five-cell value store
```

Lifecycle burden:

```text
state symbol price = 10
serve operation price = 1
reuse R = 20
coefficient evaluation cost = d+1 operations
indexed lookup cost = 1 operation
```

## Positive world

Target

\[
y(x)=2x+1 \pmod 5.
\]

Minimal coefficient degree is 1. Expected winner: two coefficient symbols rather than five independent cells under the frozen prices.

## Negative twin

Target values

```text
[0,0,0,0,1]
```

have minimal interpolation degree 4. State count no longer improves over cells and polynomial serving is more expensive. Expected winner: indexed cells.

The search is not told the terms regression or memory.

---

# 3. Recurrent state versus stateless response

Input alphabet is `{0,1}`. Search exhaustively enumerates deterministic Mealy machines by state count.

## Positive world

Protected output after each prefix is cumulative parity of all inputs so far.

Expected minimal exact state count: 2.

## Negative twin

Protected output is simply the current input bit.

Expected minimal exact state count: 1.

The search is not given RNN/FSM names; it enumerates transition/output tables.

---

# 4. Fixed versus input-conditioned dependency edges

Three input types have exact required edge sets.

## Positive world

```text
E_0={0}
E_1={1}
E_2={2}
```

Frozen cost:

```text
edge cost = 1
router cost = 0.5
```

Static exact realization activates union size 3. Input-conditioned realization activates one edge plus router cost 0.5. Expected winner: input-conditioned edges.

## Negative twin

All inputs require `{0}`. Static cost is 1, dynamic is 1.5. Expected winner: fixed edges.

The search is not told attention or dynamic routing.

---

# 5. Group-orbit tying versus free matrix

A binary `4x4` target linear map is given.

Search candidates:

```text
free 16-entry matrix
entries tied according to cyclic-translation conjugacy orbits
```

## Positive world

Target is exactly circulant. Expected exact tied realization uses 4 independent orbit parameters rather than 16.

## Negative twin

Flip one matrix entry to break equivariance. Tied representation becomes inadmissible; expected winner is free matrix.

The search is not told convolution/CNN.

---

# 6. Rank-factorized residual versus full matrix

Binary `4x4` residual matrices are given. Search obtains exact GF(2) rank and compares:

```text
rank-r factor state: r(m+n) field symbols
full matrix: mn field symbols
```

## Positive world

Rank-1 residual: factor state uses 8 symbols versus 16 full entries.

## Negative twin

Full-rank identity residual: naive rank-4 factor state uses 32 symbols versus 16 full entries. Expected winner: full matrix.

The search is not told LoRA/adapter.

---

# 7. Acceptance criterion

For each positive/twin pair:

1. both targets are exactly evaluated;
2. all registered primitive candidates are searched at the declared finite scope;
3. expected structural property wins in the positive ecology;
4. the negative twin flips/removes that property for the predicted reason.

Terminal:

`ZERO_PRIOR_EXACT_PROPERTY_REDISCOVERY_GREEN`

---

# 8. Claim ceiling

Passing this microscope means the zero-prior machinery can recover several known structural properties in exact finite worlds without architecture names.

It does **not** mean:

```text
real known families are K4 closed
neural training can discover the structures
large grammar search is unbiased
held-family response prediction is green
unknown-species discovery is validated
```

The next step is to enlarge the same neutral grammar and run protected leave-one-family-out recovery on real/synthetic learning regimes.
