# GMI developmental complementarity theorem v3

Status: **FORMAL COMPOSITE-SPECIES INTERACTION LAW / ISSUE #435 NARROWING**

Date: 2026-09-12.

Purpose: quantify when narrow modules/domains are complements, substitutes, or jointly necessary for a species to cross a registered serious-intelligence burden threshold.

## 1. Critical burden as a module-set function

For a fixed constitution `Theta`, let

\[
B^*(S)
\]

be the critical developmental burden when modules in finite set `S` are available and optional. If modules can always be ignored, then

\[
A\subseteq B\implies B^*(B)\le B^*(A).
\]

For finite values define the marginal saving of module `i` given context `S`:

\[
\Delta_i(S)=B^*(S)-B^*(S\cup\{i\})\ge0.
\]

## 2. Theorem DC-1 — exact pair complementarity

For distinct modules `i,j` not in `S`, define

\[
I_{ij}(S)=\Delta_i(S\cup\{j\})-\Delta_i(S).
\]

Algebra gives the symmetric identity

\[
I_{ij}(S)
=
B^*(S\cup\{i\})+B^*(S\cup\{j\})
-B^*(S)-B^*(S\cup\{i,j\}).
\]

Hence `I_ij=I_ji`.

Interpretation:

```text
I_ij > 0   complementarity / increasing returns
I_ij = 0   additive-independent burden savings
I_ij < 0   substitutability / overlapping function
```

A narrow verifier, memory, planner or symbolic module can therefore have low standalone saving but high conditional saving inside the right species.

## 3. Threshold synergy when burdens may be infinite

Let available developmental budget be `B_avail` and define viability

\[
V(S)=1\{B^*(S)\le B_{avail}\}.
\]

A strong threshold complementarity witness is

\[
V(S\cup\{i\})=0,
\quad
V(S\cup\{j\})=0,
\quad
V(S\cup\{i,j\})=1.
\]

Thus neither module need be a standalone “serious intelligence” for the pair to create a viable serious species.

This formulation remains meaningful when one or more individual critical burdens are infinite.

## 4. Greedy-search theorem under diminishing returns

Define burden-saving value

\[
F(S)=B^*(\emptyset)-B^*(S)
\]

for finite baseline burden. If `F` is monotone and submodular, equivalently

\[
\Delta_i(A)\ge\Delta_i(B)
\quad\text{for }A\subseteq B,
\]

then the standard greedy algorithm that repeatedly adds the module with largest current marginal burden saving achieves at least

\[
1-1/e
\]

of the optimal `k`-module burden saving under a cardinality-`k` constraint.

## 5. Complementarity warning

Positive interaction `I_ij(S)>0` is exactly a local violation of diminishing returns for that pair/context. Strong complementary modules can therefore be invisible to one-at-a-time greedy morphology growth: each may have weak marginal value alone while the pair is decisive.

GMI biosphere search must preserve combination/co-evolution moves when measured interactions show increasing returns rather than assuming greedy module addition is adequate.

## 6. Lifecycle interaction accounting

`B*(S)` must include interface/routing/verification/communication costs. Apparent complementarity produced by leaving interface cost uncharged is invalid. Conversely, shared infrastructure can create real positive complementarity if the joint species amortizes a burden that each module would otherwise pay separately.

## 7. Required empirical calibration

For known composites (RAG-like residual memory, generator+verifier, world-model+planner, neural+symbolic, model+database/tool), measure at least the four common-budget cells

```text
S
S + i
S + j
S + i + j
```

under one semantic/risk contract. This directly estimates `I_ij(S)` and tests whether the predicted interaction survives full lifecycle metering.

## Claim ceiling

This closes the algebraic interaction/synergy object and the greedy-search condition. Real module capability curves, higher-order interactions, shared-resource nonlinearities and known-composite protected calibration remain OPEN-BLOCKING.
