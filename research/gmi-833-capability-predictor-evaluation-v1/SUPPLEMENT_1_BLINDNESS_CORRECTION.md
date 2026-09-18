# SUPPLEMENT 1 — correction to BLINDNESS_V1 section 2

`BLINDNESS_V1.md` is left exactly as frozen. This supplement records a claim in
it that the implementation does not support, and what replaces it.

## The overstated claim

BLINDNESS_V1 section 2 asserted that an `ast` audit would show
`arch_descriptor` "contains **no string literal equal to any family name**".
That is false. The shipped encoder reads

```python
rho[0] = param + (1 if mech in ("CTR", "STK") else 0)
rho[3] = 3 + (1 if mech in ("REC", "CTR") else 0)
dev    = param + popcount(h) + w + ARCH_K[mech]
```

so three family strings do appear in it. Asserting otherwise would have been a
checker that passes by looking in the wrong place — exactly the failure class
this corpus is supposed to refuse. The claim is withdrawn, not narrowed away:
the property it was meant to establish is established below by a stronger test.

## What is actually true, and how it is checked

The mechanism tag is not a *label* attached to a machine from outside; it is the
machine's own transition function — which simulator the realization *is*. The
property that matters for the held-out known-architecture row is that the
family's **name** carries no information, and that is checked three ways:

1. **The realization record carries no tag at all.** `ARCH_RAW[i]` is
   `(param, w, h, k, rho, dev, obs)` — every field an integer or a tuple of
   integers. `test_the_realization_record_carries_no_mechanism_tag` asserts no
   string appears anywhere in any record. `F` sees only these records.
2. **No predictor path reads `ARCH_LABELS`.** An `ast` reference audit over
   `arch_descriptor`, `make_spec`, `cap_table`, `install_universe` and all five
   mask builders finds zero references to `ARCH_LABELS`, `labels`, `family` or
   `label`. Its negative control is a planted encoder that reads
   `ARCH_LABELS[0]`, which the audit flags.
3. **Renaming the four families changes nothing.** The descriptor is a function
   of a structural record `{r0_extra, r3_extra, k, params}`, with the family
   string only a key into it.  `test_family_renaming_leaves_the_universe_identical`
   rebuilds the whole 128-realization universe under all **24** permutations of
   `("FF","REC","CTR","STK")` and requires the result to equal `ARCH_RAW`
   exactly, every time. This is the substantive blindness result.

Additionally, `k` is provably not a recoding of the family: `REC` and `CTR` both
map to `k = 1`, so the expressivity class is a strictly coarser quantity than the
family identity.

## What is still not claimed

`F` is not blind to *structure* — it demonstrably infers an expressivity class
from `rho`, `dev` and `obs`, and that is the point of a capability predictor.
The claim is only that the held-out known-architecture result is not a lookup
keyed on a family name.
