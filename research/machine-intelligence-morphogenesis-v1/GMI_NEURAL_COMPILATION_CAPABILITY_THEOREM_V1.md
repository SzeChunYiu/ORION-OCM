# GMI Neural Compilation and Capability Theorem V1

Status: **EXACT CONSTRUCTIVE THEOREM AT FINITE OPERATIONAL SCOPE**  
Date: 2026-09-12

## 0. Question closed

This document gives a non-partial answer to two questions at the finite operational scope of `GMI_OPERATIONAL_COMPLETENESS_THEOREM_V1.md`:

1. Can a neural network be derived as a machine-intelligence realization from GMI?
2. Can GMI explain/predict the capability of that neural realization?

Answer: **YES**, by behavior-preserving compilation. This is an existence/equivalence theorem, not a claim that neural syntax is uniquely selected or parent-novel.

## 1. Finite transducer normal form

Let an operational deterministic machine have finite state set `S`, finite input alphabet `X`, next-state map

\[
\delta:S\times X\to S
\]

and finite output/action map

\[
\lambda:S\times X\to A.
\]

Encode state and input as one-hot vectors `e_s`, `e_x`.

For every pair `(i,j) in S x X`, create one ReLU hidden unit

\[
h_{ij}=\operatorname{ReLU}(e_s[i]+e_x[j]-1).
\]

Because both vectors are one-hot, exactly one hidden unit is `1` and every other hidden unit is `0`.

A linear readout then returns the exact next-state one-hot vector

\[
e_{\delta(s,x)}[k]=\sum_{(i,j):\delta(i,j)=k}h_{ij}
\]

and exact output/action one-hot vector

\[
e_{\lambda(s,x)}[a]=\sum_{(i,j):\lambda(i,j)=a}h_{ij}.
\]

The recurrent application of this block therefore reproduces the finite transducer trace exactly for every finite input history.

Width is at most `|S||X|` in this direct construction. Compression is possible but irrelevant to existence.

## 2. NC-1 — exact neural realization theorem

Every finite deterministic GMI operational machine has an exactly behavior-equivalent finite ReLU recurrent realization under the one-hot compiler above.

**Terminal:** `EVERY_FINITE_DETERMINISTIC_GMI_MACHINE_HAS_EXACT_RELU_REALIZATION = TRUE`.

The executable microscope checks all six state/input pairs of a three-state/two-input transducer and all 192 length-six traces from all starts.

## 3. NC-2 — stochastic kernel extension

For a finite stochastic operational kernel with rational probabilities, the same one-hot conjunction layer can linearly emit the exact probability vector attached to the active `(s,x)` cell. A declared categorical sampler then realizes the same stochastic kernel.

Thus behavior preservation extends from deterministic traces to exact finite trace distributions.

**Terminal:** `FINITE_RATIONAL_GMI_KERNEL_HAS_EXACT_NEURAL_PROBABILITY_REALIZATION = TRUE`.

## 4. NC-3 — intelligence preservation

GMI intelligence adequacy is morphology-neutral and determined by protected trace semantics, verifier/constitution constraints and registered resources. Therefore an exact neural compiler preserves every semantic capability coordinate that depends only on the trace distribution.

If compiler resource overhead is explicitly charged, resource coordinates transform by that known overhead rather than disappearing.

Hence:

\[
Q_{\mathcal O}(N(M))=Q_{\mathcal O}(M)
\]

for every trace-defined protected capability `Q_O`.

**Terminal:** `FINITE_GMI_INTELLIGENCE_CAPABILITY_PRESERVED_BY_EXACT_NEURAL_COMPILATION = TRUE`.

## 5. NC-4 — channel-capability consequence

CL-1 through CL-7 and the composed channel laws constrain **all** machines whose world access factors through the named channels. A compiled neural realization has the same operational channel contract as its source machine.

Therefore, whenever a finite attaining machine reaches a tight GMI channel ceiling, its exact neural compilation reaches the same semantic ceiling.

This supplies a direct chain:

```text
GMI obligation/channel contract
    -> exact class capability law
    -> finite attaining transducer
    -> exact neural compilation
    -> neural machine intelligence with the predicted capability.
```

**Terminal:** `GMI_DERIVES_NEURAL_MACHINE_WITH_PREDICTED_CAPABILITY_AT_FINITE_CHANNEL_SCOPE = TRUE`.

## 6. What the theorem does not need

It does not require gradient descent to discover the compiled weights. Training reachability is a separate developmental question. It also does not claim that ReLU networks are the only or cheapest realization.

Those distinctions are essential: **derivability/existence**, **developmental learnability**, and **frontier selection** are different theorems.

## 7. Parent subtraction

Exact neural simulation of finite automata/transducers is not claimed as GMI novelty. Classical and modern neural-automata constructions parent the representation step. GMI's contribution here is the composition with its morphology-neutral obligation semantics and channel capability laws: the same operationally derived machine-intelligence object can be compiled to neural form without changing its protected behavior.
