# GMI semantic rate-distortion theorem v1

Status: **FORMAL APPROXIMATE SEMANTIC-STATE LOWER BOUND / T3, GKF-01/08 NARROWING**

Date: 2026-09-12.

Purpose: extend exact semantic quotient/residual information bounds to obligations that permit controlled approximation.

## 1. Registered semantic target

Let `S` be the random obligation-relevant semantic state under a frozen ecology distribution. Let `Z` be a machine state available to the protected decoder/controller, and let

\[
\hat S=g(Z)
\]

be the reconstructed/acted-upon semantic state.

Let `d(S,\hat S)` be the registered semantic distortion and require

\[
E[d(S,\hat S)]\le D.
\]

## 2. Rate-distortion function

Define

\[
R_S(D)=
\inf_{P(\hat s\mid s):\ E[d(S,\hat S)]\le D}
I(S;\hat S).
\]

This is obligation/distribution/distortion specific. It is not an architecture metric.

## 3. Theorem RD-1 — state information lower bound

For any realization satisfying the distortion constraint,

\[
\boxed{I(S;Z)\ge R_S(D)}.
\]

### Proof

Because `S -> Z -> \hat S` is a Markov chain under deterministic or randomized decoding, data processing gives

\[
I(S;Z)\ge I(S;\hat S).
\]

The latter is at least the infimum defining `R_S(D)`. QED.

If `Z` has at most `M` reliably distinguishable finite states, then

\[
\log_2 M\ge H(Z)\ge I(S;Z)\ge R_S(D)/\log 2
\]

when mutual information is measured in nats in the definition above.

## 4. Exact zero-distortion limit

For identity reconstruction under zero distortion on a finite semantic alphabet,

\[
R_S(0)=H(S).
\]

Thus the theorem recovers the ordinary exact information lower bound and is compatible with the finite semantic-quotient cardinality theorem.

Worst-case exact quotient size can be stronger than entropy when the ecology distribution is nonuniform; expected and worst-case burden must remain distinct.

## 5. Conditional residual rate-distortion

Suppose a broad predictive/core state `P` is already available to both encoder and decoder. Define the conditional rate-distortion function

\[
R_{S\mid P}(D)
=
\inf I(S;Z\mid P)
\]

over admissible residual codes meeting the conditional distortion requirement.

Then any additional residual state satisfies

\[
I(S;Z\mid P)\ge R_{S\mid P}(D).
\]

At zero distortion this reduces, under the usual exact-source setting, to the conditional entropy lower bound `H(S|P)` already used by the predictive residual quotient theory.

This provides one mathematical bridge among:

```text
full rewrite / full semantic state
parameter/core compression
external residual memory
low-rank/sparse adapters
approximate lossy semantic state
```

## 6. Developmental potential consequence

If the available lifecycle state capacity under budget `B` is upper bounded by `C(B)` reliable semantic bits and

\[
C(B)<R_S(D)/\log2,
\]

then the requested distortion level is information-theoretically unreachable at that budget regardless of architecture/search quality.

This gives one necessary condition for finite critical developmental burden `B*_dev`.

## 7. Negative twins / limitations

- `R_S(D)` depends on the protected semantic distribution; a surface/world-ID code outside the registered distribution does not count.
- Low rate-distortion does not prove development can find the code or that serving/update cost is low.
- High-dimensional estimation of `R_S(D)` from finite data is itself difficult and remains assumption-indexed.
- Interactive/control obligations may require directed/control-aware information rather than a static source model.

## Claim ceiling

This closes a general information lower bound for approximate semantic state and residual coding. Practical rate-distortion estimation, constructive upper bounds and protected architecture selection remain OPEN-BLOCKING.
