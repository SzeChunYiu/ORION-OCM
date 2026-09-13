# Physical frontier sign from published measurements (RV-377-195)

Status: **EVALUATED FROM EXTERNAL PUBLISHED MEASUREMENTS — NOT MEASURED IN THIS PROGRAMME.** Date 2026-09-12 (all
sources accessed 2026-09-12). Arithmetic: `gmi_physical_frontier_sign_rv_377_195.py` (run on billy-laptop, pure
numpy Monte Carlo + closed-form propagation), receipt
`microscopes/results/physical_frontier_rv_377_195/PHYSICAL_FRONTIER_SIGN_RV_377_195.json`.

Terminal: **`PHYSICAL_FRONTIER_SIGN_FROM_PUBLISHED_CONSTANTS__NOT_MEASURED_IN_PROGRAMME`**.

## 0. What this does and does not do

`GMI_NONCLASSICAL_END_TO_END_PHASE_THEOREM_V1.md` (NC-1..NC-3) needs preparation, noise, readout and energy
constants that only hardware supplies. `GMI_EMPIRICAL_FRONTIER_IDENTIFIABILITY_BOUNDARY_V1.md` (EF-1) says a
universal sign claim requires measuring or bounding those constants, proving invariance over their admissible
interval, or abstaining. This document takes the constants from published, citable measurements of ONE concrete
device of each kind, plugs them into NC-1's burden inequality for ONE registered obligation, and reports the
resulting sign with the interval propagated from the quoted error bars and quoted operating-mode ranges. Closure-gap
class 4 (PHYSICAL-MEASUREMENT) is thereby reclassified from "unmeasured" to "evaluated from external measurements
at one registered obligation" — and no more than that. No hardware was touched by this programme; no constant below
was fabricated; every number is quoted with its source.

## 1. The registered obligation `O_B`

Protected K5 V7, lane C_FEATURE_LEARNING, `nonlinear_signal = 0.6` (LUNARC job 3605249, beacon 32138625; receipts
`microscopes/results/k5_bh_v7/`): the FIXED_FEATURE realization is a linear readout `sign(w0 + w1 x0 + w2 x1)` on
inputs uniform in `[-1, 1]^2`, served on 1600 protected queries, admissible iff test error ≤ 0.18. Its error floor
is the linear-Bayes floor 0.0911 (protected measured 0.0907; Monte Carlo here 0.0914 with the refitted readout
`w = (−0.263, 1.000, 0.724)` after normalising `max|w_1|,|w_2| = 1`). A physical carrier serving this readout may
therefore add at most `ε_hw = 0.18 − 0.0914 = 0.0886` error per query (every hardware flip counted as an error:
conservative). The matched classical parent performs 3 INT8 multiply-accumulates per query.

## 2. Published constants (quoted verbatim, with source)

### 2.1 Classical parent — CMOS datapath energies

Horowitz, M., "1.1 Computing's energy problem (and what we can do about it)", ISSCC 2014, pp. 10–14,
DOI 10.1109/ISSCC.2014.6757323, Fig. 1.1.9 "Rough energy costs for various operations in 45nm 0.9V": 8-bit int
add **0.03 pJ**; 8-bit int multiply **0.2 pJ**; 32-bit SRAM read (8 KB) **5 pJ** (the figure is an image in the
paper; the values are those of the figure as reproduced verbatim in the ISCA 2017 tutorial "DNN Model and Hardware
Co-Design" by Sze, Chen, Yang, Emer, and in Sze et al., "Efficient Processing of Deep Neural Networks: A Tutorial
and Survey", Proc. IEEE 105(12), 2017, DOI 10.1109/JPROC.2017.2761740, which cite Horowitz for them). Horowitz text
(same paper): a general-purpose processor "has high energy overhead, 70pJ/instruction, vs. a few pJ for an
operation."

Parent burden per query: `C_P ∈ [3 × 0.23 pJ, 3 × 0.23 pJ + 3 × 70 pJ] = [0.69 pJ, 211 pJ]` (fixed-function datapath
with register-resident weights .. three instructions on a general-purpose in-order core). INT8 is exact for the
8-bit obligation: no parent precision loss.

### 2.2 Analog in-memory crossbar — IBM HERMES Project Chip

Le Gallo, M. et al., "A 64-core mixed-signal in-memory compute chip based on phase-change memory for deep neural
network inference", Nature Electronics 6, 680–693 (2023), DOI 10.1038/s41928-023-01010-1; open text arXiv:2212.02872
(CC BY 4.0). Quoted:

- energy: "A peak MVM throughput of 63.1 TOPS is achieved at an energy efficiency of 9.76 TOPS/W … for the 1-phase
  read mode, when all 64 cores are fully utilized"; "For the 4-phase read mode, the former metrics are approximately
  4 times lower"; Table I, MVM at max. utilization: Energy (µJ) **0.86** (1-phase) / **3.38** (4-phase), Peak MVM
  energy efficiency **9.76 / 2.48 TOPS/W**; "all experiments in this work were performed using the higher precision
  4-phase mode". "The reported MVM energy includes the PCM crossbar array, ADCs, and PWMs".
- precision: "Resolution of the time-encoded inputs 8 bit (1 ns/LSB)"; "ADC output bits 2 × 12 bit"; "Compared with
  an equivalent digital engine having 8-bit input/output precision and N-bit weight precision, the precision
  achieved with ODP is close to 3-bit weights. With TDP, a precision between 3-bit and 4-bit weights is achieved."
- output noise model used by the authors for hardware-aware training (quoted as the pessimistic corner, not as a
  measurement): "add additive Gaussian noise on the output of the per-tile MVM with standard deviation of 10% of the
  maximum output range".
- drift: "the conductance values drift with time t according to G(t) = G(t0)(t/t0)^−ν … Drift can partially be
  mitigated by a global drift compensation procedure". Numeric drift exponent from the companion measurement paper
  Joshi, V. et al., Nature Communications 11, 2473 (2020), DOI 10.1038/s41467-020-16108-9: "In our PCM devices,
  ν ≈ 0.06 on average"; with global drift compensation "retention of test accuracy above 92.6% over 1 day".

Derived: energy per MAC (2 ops/MAC) **0.205 pJ** (1-phase) / **0.806 pJ** (4-phase); one core executing the 3-MAC
obligation as one MVM command costs `0.86 µJ / 64 = 13.4 nJ` (1-phase) or `3.38 µJ / 64 = 52.8 nJ` (4-phase);
weight programming error std `W_max · 2^−b / √12` for `b ∈ [3, 4]`; output noise std `∈ [0, 0.10 · y_max]`.

### 2.3 Superconducting-qubit processor — Google Willow

Acharya, R. et al. (Google Quantum AI), "Quantum error correction below the surface code threshold", Nature 638,
920–926 (2025), DOI 10.1038/s41586-024-08449-y; arXiv:2408.13687. Quoted: "The qubits have a mean operating T1 of
68 µs and T2,CPMG of 89 µs"; "a cycle time of 1.1 µs"; Table S4 (72-qubit processor) component errors: CZ gates
**2.8×10⁻³**, Data qubit idle **0.9×10⁻²**, Readout **0.8×10⁻²**, SQ gates **6.2×10⁻⁴**. Google "Willow Spec Sheet"
(9 Dec 2024, quantumai.google/static/site-assets/downloads/willow-spec-sheet.pdf), Chip 1 (QEC): "Single-qubit gate
error (mean, simultaneous) **0.035% ± 0.029%**"; "Two-qubit gate error (mean, simultaneous) **0.33% ± 0.18% (CZ)**";
"Measurement error (mean, simultaneous) **0.77% ± 0.21%**"; "T1 time (mean) **68 µs ± 13 µs**"; "Error correction
cycles per second 909,000 (surface code cycle = 1.1 µs)".

Shot cost (energy): Arute, F. et al., "Quantum supremacy using a programmable superconducting processor",
Nature 574, 505–510 (2019), Supplementary Information arXiv:1910.11333, Sec. X (classical simulations), energy
consumption subsection: "our refrigerator has a direct power
consumption of ∼10 kW … chilled water cooling … can be an additional 10 kW or more … supporting electronics was
nearly 3 kW … We estimate the total average power consumption of our apparatus under worst-case conditions for
chilled water production to be 26 kW. This power does not change appreciably between idle and running states … the
energy consumed during the 200 s required to acquire 1M samples in our experiment is ∼ 5×10⁶ J (∼ 1 kWh)."
Derived: **5 J per shot** at the measured system throughput; physical floor **26 kW × 1.1 µs = 28.6 mJ per shot** if
one shot took one cycle with no control-communication overhead. (No comparable published power figure for Willow
exists; the Sycamore apparatus figure is the same laboratory's measured system.)

## 3. NC-1 evaluation on `O_B`

### 3.1 Crossbar (candidate Q1)

Precision/reliability (Monte Carlo, 400 000 inputs × 64 programming draws per corner): hardware flip rate of the
readout decision — 4-bit weights, no output noise **0.78 %**; 3-bit, no noise **2.16 %**; 4-bit + 10 % output noise
**7.64 %**; 3-bit + 10 % **7.75 %**. All four corners ≤ `ε_hw = 8.86 %`: **admissible over the whole quoted
interval**, with 1.1 pp to spare at the pessimistic corner. `ΔC_reliability = 0` (no repetition needed);
`ΔC_precision` is already inside the measured MVM energy (ADC/PWM included).

Burden: `C_Q ∈ [13.4 nJ, 52.8 nJ]` per query against `C_P ∈ [0.69 pJ, 211 pJ]`. Ratio `C_Q / C_P ∈ [64, 7.7×10⁴]`.
Native saving at `d = 3`: `S = 3 × (0.23 − 0.205..0.806) pJ ∈ [−1.7, +0.08] pJ`, i.e. zero to within the parent's
own cost; the fixed per-command encode/decode/array activation burden (13.4–52.8 nJ) is what `S` would have to
exceed. **Sign: PARENT (candidate loses) over the entire propagated interval.**

Flip variable (EF-1): the obligation's matched inner dimension `d` (the workload). The per-command crossbar burden is
amortised over `d` MACs; the parent's per-MAC cost is 0.23 pJ (register-resident weights) or 1.48 pJ (weights
fetched from SRAM, 5 pJ per 32-bit word). Crossover `d* = C_Q / c_P,MAC`: **9 100** (1-phase, SRAM-fetched parent)
… **230 000** (4-phase, register-resident parent). Obligations with `d ≳ 10⁴` MACs per query — a 256 × 40 layer —
would flip the sign in the crossbar's favour in 1-phase mode; that is the real-workload variable that no registered
GMI obligation fixes.

### 3.2 Superconducting processor (candidate Q2)

Minimal circuit for the linear-form sign on two angle-encoded inputs: 6 single-qubit gates, 2 CZ, 2 qubits idle for
one cycle, 1 readout. Per-shot hardware failure `p_fail = 6 ε_1q + 2 ε_CZ + 2 ε_idle + ε_ro`, with the spec-sheet
intervals and idle scaled by `68/(68 ± 13)`: `p_fail ∈ [2.41 %, 4.61 %]`. The single-shot readout of an
amplitude-encoded linear form is a coin with bias `|score|/(2 y_max)`; averaged over the input distribution the
single-shot decision error is **35.1–35.8 %** (`> ε_hw`), so majority voting is required. Minimal odd shot count
for flip rate ≤ 8.86 %: **79** (best-corner errors) to **87** (worst-corner); NC-2's Hoeffding sufficiency at the mean
bias gives 54 (the exact binomial is tighter). `ΔC_reliability` is therefore ×79–87 shots.

Burden: `C_Q ∈ [79 × 28.6 mJ, 87 × 5 J] = [2.26 J, 435 J]` per query against `C_P ∈ [0.69 pJ, 211 pJ]`. Ratio
`C_Q / C_P ∈ [1.1×10¹⁰, 6.3×10¹⁴]`. Native saving `S = 0`: the obligation has no quantum-native structure (its
classical cost is three multiply-accumulates). **Sign: PARENT over the entire propagated interval, by ten orders of
magnitude at the most favourable corner.**

Flip variable (EF-1): `S` itself — an obligation whose matched classical parent costs ≳ 10¹⁰–10¹⁴ pJ per query
(10¹⁰–10¹⁴ INT8 MACs, or an exponentially costly parent) while its quantum circuit stays shallow enough for the shot
bias to survive `p_fail`. No registered GMI obligation has that structure; whether any real intelligence workload
does is the unmeasured world variable EF-1 names ("real workload distribution"), and it is not settled here.

## 4. Statement of what is closed

Closure-gap class 4 moves from "unmeasured" to **"frontier sign evaluated from external published measurements at
one registered obligation, PARENT on both carriers, invariant over the quoted error bars and operating-mode
intervals"**. It does not move further: (i) the constants are the vendors'/authors' measurements on their devices,
not this programme's; (ii) the Sycamore power figure stands in for Willow's (same laboratory, different apparatus);
(iii) the obligation is the one whose classical cost is smallest of all registered obligations, so the sign is the
least surprising possible one; (iv) the identifiability boundary's flip variables (`d` for the crossbar, `S` for the
quantum processor) are named, bounded (`d* ≈ 10⁴–2×10⁵`; `S ≳ 10¹⁰–10¹⁴ pJ`), and not measured.
