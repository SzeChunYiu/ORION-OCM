# Z13 — the repaired negative ecology, frozen for a LATER lane

## THIS IS NOT A CLOSURE

This artifact closes no row and appears in no `replacements[]` entry. It exists
because `Z13-P1`'s matched negative ecology was refuted (`ZP-5`) and the repair
was derived **after** seeing the enumeration. A repair scored by the lane that
derived it is the `POST_HOC_SUSPECT` pattern audit #976 filed, so the repair is
frozen here and left to a separate lane — exactly the discipline the lane that
wrote `Z13-P1` used on this lane.

## The repaired statement `Z13-P2`

Under the declared cost `C = eta*sum_m p_m*r_m + lambda*b`, resource level `k`
occupies a non-empty niche **iff** it is a vertex of the lower convex envelope of
`(k, E(k))`, i.e. iff the second difference of the profile is strictly positive:

```
E(k-1) - 2*E(k) + E(k+1) > 0.
```

For the three-mode `L = 4` universe this is

```
eta * ( p1 * 1/2  -  p2 * 1/8 ) > 0        i.e.        4*p1 > p2.
```

Predictions a later lane must score, none of them adjudicated here:

- `Z13-P2a` the one-bit niche is empty exactly on `4*p1 <= p2`, and non-empty
  exactly on `4*p1 > p2`, at every `eta`;
- `Z13-P2b` `p2 = 0` with `p1 > 0` is where the niche is **widest** at fixed
  `p1`, width `eta*p1/2`;
- `Z13-P2c` the same second-difference criterion, applied to a budget ladder the
  present universe does not contain (`b = 3`, four modes, or `L = 5`), predicts
  which intermediate levels survive there — this is the part that is genuinely
  out of sample and the part worth a later lane's time.

## How a later lane must adjudicate it

Enumerate the extended ladder independently, compute the profile and its second
differences exactly, and score `Z13-P2a`-`Z13-P2c` without reusing this
package's executor. Publish the verdict either way.

Forbidden promotions:

```
Z13_P2_ADJUDICATED_BY_ITS_OWN_LANE
REPAIRED_ECOLOGY_COUNTED_AS_PROSPECTIVE_CONFIRMATION
Z13_ROW10_CLOSED_BY_THIS_ARTIFACT
```
