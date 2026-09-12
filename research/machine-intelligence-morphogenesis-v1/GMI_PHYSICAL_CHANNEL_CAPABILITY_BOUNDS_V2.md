# GMI Physical Channel Capability Bounds v2

Status: **PHYSICAL/NONCLASSICAL NECESSITY BOUNDS / R10**

Date: 2026-09-12.

Physical intelligence claims need information-transfer bounds as well as operation counts.

## PC-1 — noisy classical channel semantic-bit ceiling

For an AWGN channel of bandwidth `B` with signal-to-noise ratio `SNR`, Shannon capacity is
\[
C=B\log_2(1+\mathrm{SNR})
\]
bits per unit time under the registered channel model.

If a protected obligation requires at least `I_req` reliable semantic bits to cross that physical interface within time `T`, a necessary condition is
\[
BT\log_2(1+\mathrm{SNR})\ge I_{req},
\]
hence
\[
\boxed{
\mathrm{SNR}
\ge
2^{I_{req}/(BT)}-1.
}
\]

No downstream algorithm can recover distinctions that never cross the physical channel reliably.

## PC-2 — quantum readout ceiling

For an ensemble encoded in `m` qubits with average state `rho`, the Holevo information
\[
\chi=S(\rho)-\sum_xp_xS(\rho_x)
\]
upper-bounds the accessible classical mutual information from one measurement. Since `S(rho)<=m` bits,
\[
I_{\text{accessible}}\le m
\]
for an ordinary `m`-qubit message ensemble absent additional registered resources.

This blocks the invalid inference:

```text
2^m amplitudes
=> 2^m freely readable classical semantic values.
```

Any quantum-domain advantage must survive state preparation, coherent evolution, repeated sampling, error correction and output extraction.

## PC-3 — repeated-read reliability burden

If one physical read succeeds with probability `q>1/2`, majority voting over `r` independent reads has error bounded by
\[
\exp(-2r(q-1/2)^2)
\]
by Hoeffding, so achieving error `delta` is guaranteed by
\[
r\ge
\frac{\log(1/\delta)}
{2(q-1/2)^2}.
\]

Thus analog/quantum/molecular speed claims must charge reliability repetitions or an equivalent error-correction mechanism.

## GMI consequence

A physical domain comparison must register:

```text
semantic bits/distortion required at interfaces
bandwidth / parallel channels
noise / precision
preparation/transduction
coherence or settling time
repetition/error correction
readout
energy
manufacture/maintenance when in scope
```

## Claim ceiling

These are parent information-theoretic necessity bounds. They do not establish classical, analog, molecular or quantum superiority on any workload.
