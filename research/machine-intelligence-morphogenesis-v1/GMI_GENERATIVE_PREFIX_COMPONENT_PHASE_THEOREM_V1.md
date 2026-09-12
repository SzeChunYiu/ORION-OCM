# GMI generative prefix/component phase theorem v1

Status: **EXACT GENERATIVE BURDEN-CURVE MICROSCOPE / T6 NARROWING**

Date: 2026-09-12.

Purpose: exhibit a family where two exact generative factorizations have identical semantic likelihood but different representation/serving burden, and derive the lifecycle phase boundary exactly.

## 1. Target family

Let `S` be a nonempty set of `K` distinct binary strings, each of length `L`. The target distribution is uniform over `S`.

Both realizations below represent the target exactly, so both achieve the same optimum semantic negative log-likelihood `H(P)=log K` per sampled string. The comparison is purely lifecycle/resource.

## 2. Realization A — component table

Store all `K` complete strings. Under the registered unit code:

\[
B_{component}=KL
\]

binary symbol-storage units.

To generate one sample, choose one of the `K` leaves uniformly and retrieve its stored string. Assign one unit of internal selection/lookup burden per generated sample; output transmission is common and excluded from the comparison.

For reuse horizon `R`,

\[
C_{component}=KL+R.
\]

## 3. Realization B — prefix-conditional tree

Build the binary trie containing exactly the prefixes of strings in `S`. Let

\[
E(S)=\left|\{\text{nonempty prefixes of strings in }S\}\right|
\]

be the number of trie edges/nodes below the root.

The trie topology plus the fact that terminal leaves are equiprobable determines every exact conditional branch probability: at a prefix, branch probability is the fraction of descendant leaves under that child. No separate real-valued probability table is needed in this finite registered code.

State burden:

\[
B_{prefix}=E(S).
\]

Generation follows one conditional branch per output position, so assign `L` units of internal sequential generation burden per sampled string:

\[
C_{prefix}=E(S)+RL.
\]

## 4. Theorem GP-1 — exact prefix-sharing state saving

Every string contributes `L` prefix incidences before merging, hence

\[
E(S)\le KL.
\]

The exact state saving of the prefix representation is

\[
\boxed{S_{prefix}=KL-E(S)}.
\]

It equals the number of duplicate prefix incidences removed by shared-prefix factoring.

## 5. Theorem GP-2 — exact lifecycle phase boundary

Prefix-conditional generation is cheaper iff

\[
E(S)+RL<KL+R,
\]

i.e.

\[
\boxed{KL-E(S)>R(L-1)}.
\]

Thus:

- more shared prefix structure favors the sequential conditional factorization;
- more repeated serving with a per-step sequential premium favors pre-materialized component state;
- both families have identical semantic likelihood, so likelihood alone cannot predict the winner.

This is a concrete registered instance of the generative burden curve `C_R^*(epsilon)` at `epsilon=0`.

## 6. Negative twins

1. **No nonroot prefix sharing:** `E(S)=KL`; there is no representation saving, so any positive sequential premium favors the component table.
2. **Heavy prefix sharing, low reuse:** trie storage can dominate lifecycle cost.
3. **High reuse/latency price:** even a strongly compressed sequential factorization can lose to pre-materialized component state.
4. **Richer latent/compositional parent:** a stronger component model may itself factor common prefixes/suffixes. The theorem compares only the two frozen realization languages and is not a universal AR-vs-latent result.

## 7. Executed exhaustive microscope

`run_gmi_generative_prefix_component_phase_v1.py` enumerates all `2^16-1=65,535` nonempty uniform target sets of four-bit strings.

Checks:

```text
exact prefix-state saving on every target set
reuse horizons R in {0,1,2,4,8}
327,675 lifecycle phase cells
zero inequality mismatches
```

At `R=0`, 65,455 target sets strictly favor prefix sharing and 80 tie. At `R=8`, only 701 favor the prefix tree while 64,810 favor component materialization.

Receipt: `GMI_GENERATIVE_PREFIX_COMPONENT_PHASE_RECEIPT_V1.json`.

## 8. Claim ceiling

This is an exact finite two-language generative burden microscope. It does not establish AR, diffusion, flow or latent superiority on real data; its role is to prove that factorization selection requires structural complexity plus serving prices even when semantic likelihood is tied.
