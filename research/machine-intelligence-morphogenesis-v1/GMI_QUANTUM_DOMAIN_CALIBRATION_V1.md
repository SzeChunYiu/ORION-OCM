# GMI Quantum-Domain Calibration v1

Status: **NONCLASSICAL CALIBRATION / CLAIM-BOUNDARY HARDENING — NOT A QUANTUM-INTELLIGENCE ADVANTAGE CLAIM**

Status date: 2026-09-12.

Purpose:

> Use quantum computation as the calibration case for a genuinely different primitive state/operator law, while preventing dimension, superposition or hardware novelty from being mistaken for demonstrated machine-intelligence advantage.

---

# 1. Primitive carrier and operators

An `n`-qubit pure state is a unit vector in complex Hilbert space

\[
\mathcal H=(\mathbb C^2)^{\otimes n}
\]

of dimension

\[
2^n,
\]

modulo global phase. General mixed state is density operator `rho` on this space.

Native operations include:

```text
unitary/channel evolution
entangling operations
measurement / POVMs
state preparation
```

This state/operator law is not merely another finite classical coefficient table when efficient simulation burden is the object of study.

---

# 2. Exponential state-space dimension is not exponential readable classical memory

Let classical random variable `X` be encoded as quantum ensemble

\[
\{p_x,\rho_x\}
\]

in a `d`-dimensional Hilbert space, and let a measurement produce classical outcome `Y`.

## Parent theorem QD-1 — Holevo accessible-information bound

The classical mutual information obtainable from one measurement obeys

\[
I(X;Y)\le\chi,
\]

where

\[
\chi
=
S\left(\sum_xp_x\rho_x\right)
-
\sum_xp_xS(\rho_x).
\]

Since von Neumann entropy of a `d`-dimensional state is at most `log_2 d`,

\[
\chi\le\log_2d.
\]

For `n` qubits, `d=2^n`, so one encoded ensemble has accessible classical information bounded by at most `n` bits through the Holevo quantity.

### GMI correction

The fact that a state vector has `2^n` complex amplitudes does **not** mean a measurement exposes `2^n` independently readable classical numbers.

Any capability claim must respect measurement/access semantics.

---

# 3. State preparation is part of lifecycle burden

A quantum algorithm may assume access to a state

\[
|\psi_x\rangle
\]

encoding a classical or physical input.

GMI registers state preparation as an explicit transformation with burden

\[
B_{prep}.
\]

If a purported speedup begins only after an expensive encoding that is comparable to or larger than the saved computation, the end-to-end frontier advantage can disappear.

Likewise outputs must be measured/decoded and repeated sampling may be needed for precision/reliability.

Recent quantum-machine-learning reviews continue to identify data encoding/state preparation, noise, error correction and scalability as central practical constraints; GMI treats those as mandatory lifecycle terms rather than implementation footnotes.

---

# 4. Complexity separation is not settled by syntax

Let the registered classical comparator be a probabilistic polynomial-time family and the quantum comparator be bounded-error quantum polynomial time.

The general equality/inequality

\[
BQP\stackrel{?}{=}BPP
\]

is not resolved by current complexity theory.

Therefore one must not claim a universal polynomial quantum/classical separation merely because a realization uses qubits.

Quantum-domain evidence must be task/family specific, based on one of:

```text
proved unconditional restricted-model separation
oracle/query-complexity separation
conditional complexity assumption
experimentally measured finite-resource frontier advantage
```

with the claim labelled accordingly.

---

# 5. Quantum-native input can change the comparison

If the legal input is itself a quantum state that cannot be fully classically described/observed without changing the task, forcing classical digitization can alter the obligation.

Thus GMI distinguishes:

```text
classical-data QML:
    charge state preparation/encoding from classical input

quantum-native data:
    compare legal operations directly on the quantum input, while charging measurements/copies and physical resources
```

This prevents both unfair quantum advantage (free input loading) and unfair classical advantage (requiring destructive full classical tomography when the task never grants it).

---

# 6. Measure-first versus coherent processing

A generic pipeline that immediately measures a quantum input converts it to classical data before downstream computation. This can discard quantum information relevant to the target.

Conversely, retaining coherence is only useful if the protected obligation actually depends on distinctions that the chosen early measurement loses.

The correct GMI object is again the semantic quotient:

> what distinctions in the quantum input must survive to answer the registered obligation?

A 2025 ICML result establishes task families where measure-first protocols have provable limitations even for efficiently preparable states, providing an important calibration that quantum information structure can matter before classicalization.

---

# 7. Quantum capability envelope

For quantum realization `Q`, define full burden including at least:

```text
qubit count / logical qubits
circuit depth and gate count
state preparation
data access/oracle construction
coherence/error rates
error correction or mitigation
measurement shots/readout
classical co-processing
training/search/tuning
energy/hardware occupancy when measured
```

Then compare protected semantic capability at matched legal information and burden.

No quantum advantage is admitted if the advantage disappears once these terms are included.

---

# 8. Domain status

At the level of primitive mathematical carrier/operator law, quantum computation is a clear nonclassical calibration case.

At the level relevant to GMI—**machine-intelligence capability/resource frontier**—the question remains ecology-specific.

Thus:

```text
new primitive computational law:         yes, established parent physics/computation
universal intelligence superiority:       no
universal efficient classical separation: unproved
specific useful intelligence niches:      open / task-dependent
```

---

# 9. Zero-prior prediction target

GMI should predict quantum realization only when obligation/context descriptors indicate that:

```text
quantum-native state distinctions matter
coherent/interference operations manipulate them more cheaply than admissible classical alternatives
state-preparation/readout costs do not erase the benefit
noise/error-correction burden is tolerable
strongest classical algorithms/approximations are included
```

The negative twin is a classically supplied task whose quantum encoding dominates lifecycle cost or whose relevant semantics are efficiently captured by a classical quotient.

---

# 10. Claim ceiling

This document integrates standard quantum-information claim boundaries, especially the Holevo information limit and end-to-end preparation/measurement accounting. It does not claim a new GMI-discovered quantum algorithm or practical QML superiority.
