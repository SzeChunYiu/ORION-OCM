# Coherent-state semantics and finite classical-reduction theorem v1

## Native semantics

For declared \(n\), Hilbert space \(\mathcal H=(\mathbb C^2)^{\otimes n}\).
The sufficient state is a density operator \(\rho\succeq0\),
\(\operatorname{tr}\rho=1\), plus any classical control register. Native
operators are completely positive trace-preserving channels
\(\rho\mapsto\sum_jK_j\rho K_j^\dagger\); unitary evolution is the special
case \(U\rho U^\dagger\). Measurement POVM \(\{M_y\}\) returns
\(p(y)=\operatorname{tr}(M_y\rho)\) with its declared post-measurement update.
The exact carrier schema is `QUANTUM_CARRIER_SCHEMA_V1.json`.

## Theorem QS-1 — classical simulation at declared scale

Fix \(n\), a finite channel/measurement description, horizon \(T\), and an
exact algebraic or bounded-precision numeric instrument. A D1/D6/D4 parent stores
the \(2^n\) complex state-vector entries (pure state) or \(4^n\) density
entries and applies the same matrix arithmetic. Induction over the circuit gives
identical states and measurement distributions at every step under exact
arithmetic; bounded arithmetic inherits an explicit error bound.

Thus every declared finite instance has a semantics-preserving classical
simulation. The burden is generally exponential in \(n\): \(2^n\) state-vector
or \(4^n\) density entries, with dense channel/unitary work priced accordingly.
Existence of this compiler does not prove polynomial equivalence over unbounded
\(n\), nor does it erase a measured quantum resource advantage.

The executable certificate uses exact rational density matrices for five
one-qubit states, X/H channels, all operation words through length four, and
Z-measurement. Across 155 trajectories it finds zero classical-compiler, trace,
or probability violations.

## Lifecycle requirements

Any quantum cognition claim must charge, separately:

- logical and physical qubits;
- state preparation depth, fidelity, and rejected attempts;
- gate count/depth/error;
- measurements, shots, destructive readout, readout error, and tomography;
- code family/distance, syndrome qubits/cycles, decoder time, and logical error;
- classical control/communication, wall time, energy, cooling/reset;
- numeric precision and simulation error.

These are formalized in `QUANTUM_LIFECYCLE_ACCOUNTING_V1.json`. A logical
circuit with free preparation, readout, or error correction is not an end-to-end
resource comparison.

## Claim ceiling

This closes semantics, lifecycle schema, and finite-scale reduction only. The
Issue #602 box requiring a capability/resource frontier unexplained by known
quantum-algorithm parents remains open: no such frontier is produced here.
