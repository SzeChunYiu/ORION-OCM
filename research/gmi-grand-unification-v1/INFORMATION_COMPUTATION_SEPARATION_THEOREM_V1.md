# Grand GMI Information–Computation Separation Theorem V1

Status: **EXACT FINITE SEPARATION THEOREM**  
Date: 2026-09-12

## 0. Claim

A theory of intelligence based only on information, entropy, mutual information, channel capacity, memory size or communication width cannot be complete.

Two obligations can require exactly the same semantic information across a downstream cut while requiring arbitrarily different local computation before that cut.

Therefore Grand GMI needs at least two irreducible families of invariants:

1. a **semantic cut spectrum** — what distinctions must cross each causal cut;
2. a **transformation-complexity spectrum** — what physical/computational work is required locally to produce those distinctions.

## 1. Definitions

Let a local processor receive input `x in {0,1}^n` and send a final answer bit to an actuator.

For an exact Boolean obligation `f`, define the final-cut semantic width

`kappa_f = ceil(log2 |image(f)|)`.

Define `tau_f` in this theorem to be deterministic decision-tree query complexity: the smallest worst-case number of input-bit probes required to compute `f` exactly.

These are deliberately simple exact coordinates. The Grand GMI generalization replaces `tau` by a resource-vector Pareto frontier over the substrate's legal local transformations.

## 2. Separation family

For every `n >= 2`, define

`f_easy(x_1,...,x_n) = x_1`

and

`f_hard(x_1,...,x_n) = OR(x_1,...,x_n)`.

Both have image `{0,1}`. Therefore

`kappa_easy = kappa_hard = 1 bit`.

But

`tau_easy = 1`

while

`tau_hard = n`.

### Proof

`f_easy` is computed by probing `x_1`, so `tau_easy <= 1`; a nonconstant Boolean function requires at least one probe, so equality holds.

For OR, probing all `n` bits is sufficient. For necessity, consider an adversary answering `0` to every query. Until every bit has been queried, an unqueried bit could be `1`; therefore both the all-zero input and an input with a single unqueried `1` remain consistent but require different outputs. No exact deterministic algorithm can stop. Hence worst-case depth is at least `n`, and `tau_hard=n`. QED.

The ratio `tau_hard/tau_easy=n` is unbounded even though the final semantic cut requirement is identical.

## 3. Consequence

There is no function `F` of final-cut information alone such that

`transformation complexity = F(final-cut information)`

for all finite obligations.

Thus a universal GMI invariant cannot be one scalar 'amount of information'.

## 4. Transformation-complexity spectrum

For a region `R` of a causal process network, let `P_R` be the set of substrate-legal local processes that realize the required semantic relation from the region's incoming semantic classes to its outgoing classes. Let `rho_R(T)` be a vector of physical/computational resources such as time, energy, memory traffic, circuit depth, queries, communication, precision and irreversible erasures.

Define

`Tau_G(R,epsilon) = Pareto{ rho_R(T) : T in P_R and task error <= epsilon }`.

Grand GMI's task invariant is therefore not just a state quotient or cut width. At minimum it contains

`Xi_G = (S*, {Kappa_G(C,epsilon)}_C, {Tau_G(R,epsilon)}_R)`.

`S*` says which histories are semantically distinct; `Kappa` says which distinctions must cross which cuts; `Tau` says how difficult it is to transform available distinctions into required ones.

## 5. Why this matters for machine-intelligence morphology

The separation explains phenomena that information-only theories conflate:

- a model can possess all task-relevant facts but lack enough inference-time compute to derive the answer;
- a verifier can collapse semantic uncertainty while search cost remains dominant;
- retrieval can supply the right information while reasoning over retrieved items remains hard;
- two memories of equal bit capacity can support different capability because their access/transform costs differ;
- thermodynamically low-information operations can still be computationally hard to realize efficiently.

Recent quantum thermodynamics gives a physical analogue: Zhao, Zhang and Preskill (2026) show that information-theoretically optimal erasure work can be separated from efficient attainability under computational hardness assumptions. This is supporting parent evidence, not a proof of the GMI theorem above.

## 6. Architecture interpretation

A machine architecture is a factorization of the global obligation into local transformations connected by cuts.

Its morphology must therefore solve a joint embedding problem:

- provision enough distinguishability at every relevant cut (`Kappa`);
- provision enough local transform resources in every region (`Tau`);
- obey physical feasibility and global resource budgets.

This is the first reason Grand GMI can distinguish architectures with equal memory or equal communication but radically different compute topology.

## 7. Executable hostile check

`grand_gmi_checks_v1.py` exactly computes deterministic decision-tree depth for the two function families for `n=2...7`. It obtains `1` for `f_easy` and `n` for OR while both final cuts remain one bit.

The mathematical proof is for every finite `n`; the executable witness guards the implementation and statement against accidental weakening.
