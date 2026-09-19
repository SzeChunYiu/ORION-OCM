# AG3 — the presentation-equivalence strength order (START HERE)

The AG3 row asks for presentation equivalence to be defined at several strengths. Witnesses
for three of the four named strengths were already merged; none of them ordered the strengths,
and one strength had no witness at all. This tranche defines all four over one registered
finite universe, computes the order between them, and certifies every inclusion and every
non-inclusion with an explicit pair.

## Headline numbers (exact integer/set arithmetic throughout; no float enters any claim)

| quantity | value |
|---|---|
| presentations in the registered universe | `2,548` |
| comparable pairs | `1,621,802` |
| related pairs — `L1` renaming / `L2` term / `L3*(1)` compiler / `L4` model | `1,762` · `29,470` · `297,166` · `297,358` |
| classes — `L1` / `L2` / `L3*(1)` / `L4` | `1,152` · `219` · `107` · `91` |
| the order | `L1 < L2 < L4`, `L1 < L3*(1) < L4`, **`L2` and `L3*(1)` incomparable** |
| generated sublattice | `5` elements, `1` of them new; **not a chain** |
| `k*`, least overhead at which term equivalence sits inside compiler equivalence | `2` |
| ladder saturation | `L3*(2) = L3*(3) = L3*(5) = L4` on this universe |
| pairs the raw compiler clause relates across **different** presented objects | `367,372` |
| `L3` certificates re-verified independently | `591,084`, `0` invalid |
| `L1` / `L2` pairs whose presented objects differ | `0` / `0` |

## The three things worth knowing

**The four strengths are not a chain.** Definitional/term equivalence and compiler equivalence
at overhead `1` are incomparable: `W-OVERHEAD` is term-equivalent and does not compile within
overhead `1`, while `W-STATESPACE` compiles within overhead `1` across a change of state space
where no term equivalence can exist. So "at strength `s` or above" is not a well-formed
qualifier for a presentation-invariance claim until the branch is named.

**Bounded mutual simulation is not semantics preservation.** Read on its own, the compiler
clause relates `367,372` pairs that present different objects; the minimal counterexample has
two states and programs `(empty, empty)` against `(empty, f1)`. Semantics preservation has to
be stated over the presented object, and the level published here is the compiler clause
intersected with model equivalence, as the freeze's section 1 required before any run.

**Fixed overhead is a tolerance, not an equivalence.** Composing two compilers of overhead `k`
costs `k^2`. An explicit non-transitive triple at `k = 1` is published. Only the transitive
closure has a place in a lattice, and every order statement is made about the closure.

## The strength with no witness

Of the four, definitional/term equivalence was the one no merged package witnessed. It is
**constructed** here, not shown impossible: `W-RENAME` adds `pred` as a symbol for the
`succ`-term `succ succ`, changing the presentation and nothing about the presented object. Its
exact level is `L2`: certified in `L2`, certified out of `L1`.

## Evidence

- **2 materially independent routes.** Route B imports neither route A nor any parent module.
  It packs state maps as base-`n` integers, decides `L1` and `L2` pairwise by explicit search
  over bijections rather than by a canonical form, decides model equivalence by Moore
  minimization and canonical renumbering rather than by a table of behaviours, and takes
  compile lengths from one BFS distance map rather than layered realizability sets. **Every
  published quantity agrees; 0 disagreements.**
- **6 hostiles, all detected, each with a control proving the perturbation moves its
  quantity**: `L1` without program translation (`1,762 -> 142,786` related pairs, `101,776`
  object violations), `L1` without observation preservation (`1,762 -> 2,250`, `372`), `L2`
  without the external-action condition (`29,470 -> 219,618`, `168,900`), `L3` without the
  reachability restriction (the `L2`/`L3` separator is lost), `L3` with the overhead bound
  removed (the incomparability is destroyed), and the raw clause with a non-observation-
  preserving encoding (`0 -> 8,912` pairs gained, `3,082` certificates rejected).
- **One perturbation is recorded as INAPPLICABLE and is not shipped as a hostile**: dropping
  injectivity from the encoding gains `0` pairs inside a model-equivalence class at this scope,
  so it would be a test of nothing.
- **Nulls.** `0 / 200` random level assignments and `0 / 200` randomized interpretation tables
  reproduce the certified witness placement.
- **No-alarm case asserted.** On the true configuration every detector is silent: `0` object
  violations, `0` invalid certificates, every strict inclusion certified, every
  incomparability certified in both directions.

## What is withdrawn rather than restated

The freeze allowed for a pair sitting in `L4` and in no registered `L3(k)`. The executor
searched the universe and found none, so the strictness claim `L3*(5) < L4` is **withdrawn**
and the equality `L3*(2) = L4` is published in its place. Whether the parent's factor `5` is
strict on a universe with longer programs is open.

## Reproduce

```
python3 -I -B  research/gmi-833-ag3-presentation-equivalence-v1/ag3_presentation_equivalence_v1.py
python3 -I -B  research/gmi-833-ag3-presentation-equivalence-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-ag3-presentation-equivalence-v1/test_ag3_v1.py
```

Route A takes about 2 min 40 s, route B about 50 s, the tests under 30 s. Stdlib only.

## Files

`FREEZE_V1.md` (committed before any code, commit `cc4444ff`) ·
`AG3_LATTICE_THEOREMS_V1.md` (`AG3L-1` … `AG3L-5`) · `PARENT_LEDGER.md` ·
`RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` · `MANIFEST_V1.json`.
