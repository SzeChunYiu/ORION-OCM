# gmi-833-ae-morphology-sweep-v1

Section AE, batching-plan item 12. Four Tier-2 rows — AE5 row 5, AE6 row 7,
AE10 row 5, AE13 row 7 — all of which ask the same question in four dialects:
**which quantity predicts the selected morphology?**

**The section map was wrong about this.** It says these rows need "no new
mathematics, only registered morphology-selection receipts pinned by blob sha".
The five morphology receipts on `main` contain no information-theoretic or
achievability quantity of any kind, so pinning them answers nothing. The
residual — declared in `FREEZE_V1.md` before any result existed — is the
**viability bridge** `active(W, tau) = { m : acc(m, W) >= tau }`, which is what
lets an exact achievability quantity reach the parent's choice correspondence.

**Harness.** `X = {0,1}^3` uniform; five architecture-name-free morphologies
with integer resource vectors `(fan_in, depth, memory_cells)`; the parent
choice correspondence (fail-closed, full argmin set, no fabricated tie-break)
under frozen prices `w_A = (1,1,1)`, `w_B = (1,3,1)` and threshold `tau = 3/4`.
Census: all `256` deterministic worlds, plus registered locality and causal
fixtures.

| result | numbers |
|---|---|
| `SWEEP-1` raw information | **4,348** conflicting pairs of **10,292** equal-information world pairs — raw `I(X;Y)` does **not** determine the selection. Equality decided exactly by `min(k, 8-k)`; no logarithm evaluated |
| `SWEEP-2` single-budget usable information | **9,576** conflicting pairs of **17,744** — AE10's `U(W,T,R0)` alone does not determine it either |
| `SWEEP-3` resource-conditioned vector | **0** conflicts; non-vacuous — `256` worlds to **11** profiles, strictly finer than either scalar; unique minimal sufficient subvector `{m0, m1, m2}` of `31` tested; at `w_B` the three counts are **3,568 / 9,576 / 0** |
| `SWEEP-4` locality boundary (AE6) | `tau = 1/2` is the exact boundary at which failure of locality displaces every local morphology; parity selects `m4_gf2_affine` for `tau in (1/2,1]`, `x0 AND x1` selects `m2_arity2_junta` for `tau in (3/4,1]` |
| `SWEEP-5` intervention (AE13) | Markov-equivalent `A→C` / `C→A`: **identical** observational joints and identical observational selection `{m1}`; under `do(A)` the selection differs — `{m1}` versus `NO_VIABLE_MORPHOLOGY` for all `tau in (1/2, 3/4]` |
| `SWEEP-6` AE5 scalars (AE5) | none predicts: `\|S\|` **8,712**, GF(2) rank **10,172**, description length **12,818**, causal-state entropy at least **2,968** (certified lower bound; no logarithm evaluated) |

**Answer, in one line.** Not raw information, and not a single usable-information
scalar — a **vector of resource-conditioned achievability statistics**, of which
three coordinates suffice at the registered threshold and price.

**Two routes.** Route A is analytic (partition-cell maxima plus the Walsh
identity `1/2 + max_a |W(a)|/2`). Route B materialises every hypothesis of every
class and scores it by direct summation, re-implements the selection rule from
the parent's written definition, and rebuilds the causal fixtures from their
structural equations; it imports nothing from Route A. They agree on all 256
profiles, all 256 selections under both prices, and all four causal fixtures.

**Hostiles.** Five, each first proved able to move the quantity it perturbs and
then proved detected: resource-vector tamper, zero price coordinate, fabricated
tie-break, observational-only intervention estimate, parent blob tamper.

**Null.** `200` shuffled selection maps never reach `0` conflicts (range
`3,533`–`3,685`) where the true profile scores `0`; `200` random positive prices
give `0` violations of the parent's `SEL-1` and leave raw information failing in
`200/200`. The no-alarm case is asserted directly.

**Row not closed here.** AE6's `Prospectively test intrinsic-structure ->
morphology transitions on synthetic and real datasets.` is Tier 3 and stays OPEN
with its instrument requirement.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-morphology-sweep-v1/test_morphology_sweep_v1.py -v
python3 -I -O -B research/gmi-833-ae-morphology-sweep-v1/test_morphology_sweep_v1.py -v
python3 -I -B research/gmi-833-ae-morphology-sweep-v1/morphology_sweep_v1.py > /tmp/sweep.json
cmp /tmp/sweep.json research/gmi-833-ae-morphology-sweep-v1/RESULT_V1.json
```

Claim ceiling:
`GMI_833_AE_MORPHOLOGY_SELECTION_PREDICTOR_COMPARISON_AT_REGISTERED_FINITE_SCOPE`.
