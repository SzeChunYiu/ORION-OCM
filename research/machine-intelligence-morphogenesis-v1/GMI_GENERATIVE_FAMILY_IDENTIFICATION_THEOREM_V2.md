# GMI Generative-Family Identification Theorem v2

Status: **DEVELOPMENT LOWER BOUND / R5**

Date: 2026-09-12.

Likelihood equivalence alone cannot select a generative morphology. A second missing coordinate is the information required to learn which target distribution is present.

Let hidden target index
\[
\Theta\in\{1,\ldots,K\}
\]
choose a target distribution `P_Theta`. A development set `D=X_1,...,X_n` is sampled conditionally iid from `P_Theta`.

Suppose the registered quality requirement is strong enough that any admissible learned generator uniquely identifies the corresponding target-family cell up to error probability `delta`. For example, pairwise target distributions may be separated more than twice the admitted output-law tolerance.

## GF-1 — Fano development lower bound

For uniform `Theta`, any development procedure with target-identification error at most `delta` obeys

\[
I(\Theta;D)
\ge
(1-\delta)\log_2 K - h_2(\delta).
\]

Under conditional iid sampling,
\[
I(\Theta;D)
\le
n\, I_{\max}
\]
for any registered upper bound `I_max` on information about `Theta` per observation. Hence

\[
\boxed{
n
\ge
\frac{(1-\delta)\log_2 K-h_2(\delta)}
{I_{\max}}.
}
\]

This is a family-independent **development information lower bound**.

## GF-2 — lifecycle selector implication

For each realization family `R`, a meaningful burden curve
\[
C_R^*(\epsilon)
\]
must include at least:

```text
target-family identification / data information burden
representation burden
optimization/development burden
sampling/decoding steps
quality verification
serve latency/parallelism
update burden under target drift
```

The earlier likelihood-only no-go plus GF-1 means two exact families can tie semantically while having different acquisition burdens.

## Negative twins

- If target index is supplied for free, the identification lower bound disappears.
- If target family cells are not separated at the admitted distortion, full identification is unnecessary.
- If one sample contains many bits about `Theta`, the sample lower bound can be small.
- This theorem does not rank AR/diffusion/flow/latent architectures by itself.

## Claim ceiling

This closes an information-theoretic acquisition lower bound, not practical high-dimensional generative-family response curves.
