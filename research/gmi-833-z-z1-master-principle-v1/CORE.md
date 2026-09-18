# GMI #833 Section Z / Z1 — the Marginal Value Principle and exact incompressibility

Closes **five** of the six rows of `### Z1` in issue comment `5684819296`:
rows `1`, `3`, `4`, `5` and `6`.

Row `2` is **deliberately left open** and `FREEZE_V1.md` §7 forbids this package
from touching it: it quantifies over eight named law families and no canonical
register of those families exists on `main`. Classifying only the morphology and
capability entries would be closure by narrowing.

## What it establishes

- **`IC-1`, the Marginal Value Principle**: selection thresholds are the
  supporting slopes of the lower convex envelope of the resource-error profile —
  **marginal** error masses, never error levels. Zero free theoretical constants.
- **`IC-1a`..`IC-1d`**: `lambda* = eta*p/2`, `lambda*(A) = eta*p*(1 - 1/A)`,
  `lambda* = eta*p*R0` and the three-level ladder are all the same corollary.
  Floors `1/2`, `2/3`, `3/4` re-enumerated over `16`, `729`, `65536` tables;
  `R0 = min(q, 1-q)` over `7` input laws; `135/135` ladder worlds agree with the
  envelope-vertex criterion, `0` disagreements.
- **`IC-2`, identification**: of `289` laws in each declared two-parameter family,
  exactly **one** reproduces the enumeration — `IC-1` in both cases. `Z13-P1`'s
  level-valued pair scores `27/135`.
- **`IC-3`, incompressibility**: scored on the `264` non-degenerate instances —
  `99` profile groups, `75` shared, `240` instances in a shared group (full
  population: `102` groups, `78` shared). Four named laws (`L_DEGENERACY`, `L_MDL`,
  `L_REACH`, `L_DISTINCT`) are separated with **exhibited witness pairs**; two
  (`L_THRESHOLD`, `L_ARGMIN_BUDGET`) are compressible and the same instrument
  stays silent on them.
- **`IC-4`, compression**: raw pair `(567, 0)` for `IC-1` against `(567, 5)` for
  a four-member bag of independent laws; exactly one constant in the examined
  corpus remains `ARBITRARY_UNDER_IC-1` — the `5/16` level in `Z13-P1`.
- **`IC-5`, head to head**: on the ladder, `IC-1` `135/135` against the bag's
  ladder member `27/135`; on the two-level population `eta*p/2` scores `105/297`
  and `eta*p*(1 - 1/A)` scores `153/297`.

## What it does not establish

`IC-1` is **not new mathematics** — it is Lagrangian scalarisation over a lower
convex envelope, and the parents are named in `PARENT_DISCLOSURE_V1.md`. Nothing
is claimed about memory, abstraction, attention, planning, communication or
teaching/culture laws. Nothing about non-additive costs, non-linear resource
prices, infinite candidate sets, or real systems. The two-level head-to-head cell
for `IC-1` is labelled `TAUTOLOGICAL_AT_TWO_LEVELS` in the receipt itself.

Claim ceiling:

```
GMI_833_Z1_MARGINAL_VALUE_PRINCIPLE_AND_EXACT_INCOMPRESSIBILITY_SEPARATIONS_AT_REGISTERED_FINITE_SELECTION_SCOPE
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z1-master-principle-v1/z1_master_principle_v1.py
python3 -I -B  research/gmi-833-z-z1-master-principle-v1/independent_compression_oracle_v1.py
python3 -I -B  research/gmi-833-z-z1-master-principle-v1/test_z1_master_principle_v1.py -v
python3 -I -O -B research/gmi-833-z-z1-master-principle-v1/test_z1_master_principle_v1.py -v
```

Stdlib only, exact rational arithmetic, no float in any claim. Route A about `3`
s, Route B under `1` s on one core. `17` tests.

## The instrument failed first

The first null drew `200` random affine threshold laws and reported a "perfect
null" — because the draw pool contained the true law. Scoring a null against a
pool that includes the answer measures nothing. It was replaced by an
**exhaustive** sweep of all `289` laws in each declared family, which turns the
same computation into an identification result: exactly one law fits, and it is
`IC-1`. A second instrument problem was found by inspecting the witnesses the first
run exhibited: they were drawn from the `p = 0` slice, where the profile is
`(0, 0)` and nothing is being selected at all — a separation over a degenerate
range. `FREEZE_V1_AMENDMENT_1.md`, committed before this receipt, narrows the
separation population to `E(0) > E(1)`; every witness now comes from an instance
on which `IC-1` makes a real selection. A third: the hostile that strips `eta`
from the profile key shows the key is load-bearing — without it the `102` groups
over-merge into `59` and the separation test would report spurious splits.
