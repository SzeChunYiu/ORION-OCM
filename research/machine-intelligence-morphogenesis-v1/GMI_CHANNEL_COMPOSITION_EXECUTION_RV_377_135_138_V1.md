# GMI Channel Composition Execution — RV-377-135 … RV-377-138 V1

Status: **ALL FOUR PROSPECTIVELY NAMED ATLAS CELLS FINITE-EXACT GREEN**  
Date: 2026-09-12  
Atlas predecessor: `GMI_CHANNEL_CAPABILITY_ATLAS_V1.md`

## 0. Protocol discipline

The predecessor atlas named four unoccupied channel combinations, equations, boundary reductions, attaining constructions and falsifiers before this execution tranche. This tranche does not change those equations after seeing results. It implements exact finite microscopes with `fractions.Fraction`, no RNG and no tolerance bands.

Runner: `gmi_microscope/run_gmi_operational_closure_v1.py`

Receipt: `microscopes/results/channel_compositions_v1/RECEIPT.json`

## 1. RV-377-135 — noisy development × bounded state

Microscope: Hamming(7,4), `L=8`, revealed block `r=7`, retained state `s=4`, BSC `q=1/4`.

The perfect code has exact average per-bit quantization distortion

\[
d^*(7,4)=1/8.
\]

The composed predicted revealed-bit error is

\[
q+(1-2q)d^*=1/4+(1/2)(1/8)=5/16.
\]

Full enumeration of all true revealed blocks and all BSC noise vectors gives **exactly `5/16`**. Including the one unrevealed world bit, predicted and observed capability are both **`85/128`**.

The atlas' registered Hamming(63,57) point is also checked exactly from all 64 syndrome coset leaders (`d*=1/64`); at `q=0.1` its capability evaluates to `4513/5120 = 0.8814453125`, above the truncation line `137/160 = 0.85625`.

Terminal: `NOISY_BOUNDED_STATE_COMPOSITION_FINITE_EXACT_GREEN`.

## 2. RV-377-136 — noisy development × external store

For two conditionally independent symmetric binary observations of one fair bit, with accuracies `a` and `b`, exact enumeration of observation pairs confirms Bayes accuracy

\[
\max(a,b).
\]

The runner checks 20 `(q,rho)` combinations, including anti-correlated development where the known channel model is inverted optimally.

Example `L=8,r=4,c=1/2,q=1/4,rho=1/4`: predicted and observed capability are both **`21/32`**.

Terminal: `NOISY_EXTERNAL_STORE_COMPOSITION_FINITE_EXACT_GREEN`.

## 3. RV-377-137 — structured world × verifier

World: `W=G theta` over GF(2), six public rows, latent dimension `H=3`. For every two-row revealed set `S`, each of three two-bit blocks `B`, every reachable revealed value and proposal budgets `k in {1,2,4}`, the runner computes

\[
delta_B(S)=rank(S union B)-rank(S)
\]

and exhaustively enumerates latent `theta`.

Every conditional block support is uniform over exactly `2^delta` values and the optimal exact-verifier success is

\[
\min(1,k/2^{\delta}).
\]

**540/540 conditional checks exact.**

Terminal: `STRUCTURED_WORLD_VERIFIER_COMPOSITION_FINITE_EXACT_GREEN`.

## 4. RV-377-138 — verifier × external store

For `u=1..5` unknown block bits, every coverage subset, store reliability `rho in {0,1/4,1/2,1}` and proposal budget up to eight, the runner enumerates the exact posterior over every completion and computes the mass of the `k` highest-posterior completions.

Results:

- **1,872/1,872** top-k posterior checks exact;
- **588/588** CL-6/perfect-store boundary checks exact;
- strict witness `u=4`, covered bits `{0,1}`, `rho=1/2`, `k=3`: posterior-ordered proposals succeed with `27/64`, while ignoring the store gives `3/16`.

Terminal: `VERIFIER_EXTERNAL_STORE_COMPOSITION_FINITE_EXACT_GREEN`.

## 5. Prospective-prediction disposition

All four channel cells were named in the atlas before this execution and all four survive exact execution. Therefore the programme may claim:

`PROSPECTIVE_UNOCCUPIED_CHANNEL_CLASS_PREDICTION_GREEN_AT_REGISTERED_FINITE_SCOPE = TRUE`.

The stronger statement “these mechanisms were historically unknown to humanity” is **not** asserted. Side-information/rate-distortion coding, robust retrieval and verifier-guided search already parent important pieces. The prediction being validated is the GMI atlas' pre-execution quantitative composition law.

## 6. Reproducibility

The runner, tests and receipt are committed together on the operational-closure branch/PR; the Git commit pins their exact bytes. Six unit tests pass and the runner's aggregate terminal is `GMI_FINITE_OPERATIONAL_CLOSURE_MICROSCOPES_ALL_GREEN`.
