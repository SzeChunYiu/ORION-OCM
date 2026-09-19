# FREEZE_V1 — gmi-833-mtg-naturality-tiers-v1

Parent issue: SzeChunYiu/ORION-OCM#833. Programme comment: `5687604615` (headings are `###`).
`source_main`: `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`. Live comment sha256 at fetch: `bb5e9e8bb7b2a8f5e89d499d581ac7c63863a016bee5d371293eb1cf9c8ff5bb` (8570 chars, 61 open rows, 0 checked).
Row texts are pinned byte-exact in `research/gmi-833-mtg-map-v1/MTG_ROWS_V1.json`; the rows quoted below are copied from that file unchanged.
Parent receipts are pinned by path + git blob sha in `PARENT_PINS_V1.json` (sha256 `55ebb7194110592703643e759fc44e57e27d7afba394189a9a92c418ed532cb3`); prose in this package names parents by alias only.

## Claim ceiling

`GMI_833_MTG_APPROXIMATE_AND_STOCHASTIC_NATURALITY_TIERS_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions: `OPTIMIZER_EQUIVALENCE_PROVED`, `REAL_LEARNING_DYNAMICS_VALIDATED`, `BAYESIAN_OR_LATENT_UNCERTAINTY_CLAIMED`, `UNIVERSAL_HYSTERESIS`, `CONTINUOUS_STATE_NATURALITY_PROVED`, `COMPLETE_GMI`.

## Rows this package may reconcile

Under the anchor quoted verbatim below:

> ### MTG-3 — Developmental naturality

- [ ] Define exact and approximate developmental commuting squares.
- [ ] Distinguish static compiler, learning-compatible transform, and full developmental-equivalence transform.
- [ ] Track path dependence/hysteresis rather than erasing it through final-output equivalence.
- [ ] Extend to stochastic update kernels with calibrated uncertainty rather than deterministic overclaim.

## Frozen objects

Finite deterministic developmental systems `M=(X,E,Phi,lambda)`, `N=(Y,E,Psi,mu)` sharing the experience alphabet `E`, as in parent P02, plus a registered exact metric `d_Y` on `Y` (the discrete metric unless a rational distance table is registered). For a total state map `T:X->Y` define the **naturality defect** `eps(T)=max_{x,e} d_Y(T(Phi(x,e)), Psi(T(x),e))`. The **exact square** holds iff `eps(T)=0`; the **approximate square at level `a`** holds iff `eps(T)<=a`.

Finite stochastic systems replace `Phi` by an exact row-stochastic kernel `K_M(x,e) in Delta(X)` (parent P24 owns the kernel object). For `T` define the **stochastic defect** `tv(T)=max_{x,e} TV(T_* K_M(x,e), K_N(T(x),e))` with `TV` the exact half-L1 distance and `T_*` the push-forward.

## Frozen theorem targets

- `NAT-1` — approximate squares: `eps` is exact and total; for the discrete metric every map is 1-Lipschitz, hence `eps(U o T) <= eps(T) + eps(U)`; for `eps=0` the parent's exact square and trajectory preservation are recovered. Checked on every composable pair of the fixture.
- `NAT-2` — three tiers, defined and separated: `STATIC` (labels preserved), `LEARNING_COMPATIBLE(a)` (labels preserved and `eps<=a` for the registered `a>0`), `FULL_DEVELOPMENTAL_EQUIVALENCE` (labels preserved, `eps=0`, `T` bijective and `T^-1` also exactly natural). Inclusions `FULL ⊂ EXACT ⊂ LC(a) ⊂ STATIC` are proved and every inclusion is **strict** by an exact witness; the complete tier census over all `|Y|^{|X|}` maps of the fixture is reported.
- `NAT-3` — path dependence is tracked, not erased: for the registered word set the tracker reports the per-prefix vector of state mismatches `T(Phi*(x,w)) != Psi*(T(x),w)` alongside final-output agreement `lambda(Phi*(x,w)) = mu(Psi*(T(x),w))`. Hostile: a pair with final-output agreement on **every** registered word but a non-commuting trajectory; a final-output-only check reports `0` and the tracker reports a positive mismatch count. A two-order hysteresis witness (`ab` vs `ba` reaching different states with equal outputs) is recorded exactly.
- `NAT-4` — stochastic kernels: `tv` is exact; push-forward is 1-Lipschitz in `TV`, hence `tv(U o T) <= tv(T) + tv(U)`; deterministic kernels specialize `tv` to `eps` under the discrete metric; the reported object is the exact interval `[0, tv(T)]`, never a point claim. Hostile (deterministic overclaim): the argmax-projected deterministic systems commute exactly (`eps=0`) while the true kernels have `tv>0`; a checker that projects to the mode passes and the exact checker refuses. Null: 200 seeded random exact kernels `K_N` must yield `0/200` with `tv=0`.

Two materially independent routes: route A (executor) computes `eps`/`tv` by direct definition with dictionary push-forward; route B (oracle, importing nothing from route A) computes the same quantities by explicit trajectory enumeration and matrix-form kernel products indexed by integers.

## Frozen boundary

No claim about continuous state spaces, real optimizers, learning-rate or normalization invariance, epistemic/latent uncertainty (P24's `UNC-BND` boundary is inherited), or universal hysteresis.

## Order discipline

This freeze is committed **before** any executor, oracle, test, receipt, theorem note or workflow of this package exists. The freeze commit contains only `FREEZE_V1.md` and the pin/row JSON files named above. `git log` over this package must show this file in a commit strictly earlier than every implementation commit; the CI custody step checks that no post-freeze artifact exists at the freeze commit and degrades to a distinct `UNREACHABLE` state if the commit is not in the checkout, never to a pass.

## No neighboring row is earned here.

Only the rows quoted above may be reconciled by this package. Every other row of comment `5687604615`, every row of the #833 body, and every row of the other #833 comments remain untouched by this tranche.
