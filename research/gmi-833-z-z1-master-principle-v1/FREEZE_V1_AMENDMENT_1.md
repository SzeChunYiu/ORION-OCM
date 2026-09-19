# FREEZE_V1 amendment 1 — the separation population excludes degenerate instances

Committed **before the receipt it affects**.

`FREEZE_V1.md` §3 obliges this package to exhibit separation witnesses over "a
declared finite population" and, under `W-NONVACUITY`, to show that instances
sharing an identical profile actually exist. A first run of the executor met both
obligations but returned witness pairs drawn from the `p = 0` slice, where the
error price is zero, the profile is `E(0) = E(1) = 0`, and **nothing is being
selected at all**. A separation exhibited on an instance where the principle makes
no selection is a witness over a degenerate range — the same failure class as a
bound that is a tautology over its own range, which this section has already been
caught by once.

The separation population is therefore narrowed, before any receipt is committed,
to the **non-degenerate** instances

```
E(0) > E(1)
```

i.e. `p > 0` and `R0 > 0`. This strictly tightens the obligation: every witness
must now come from an instance on which `IC-1` makes a real, non-trivial
selection. The corollary checks (`IC-1a`..`IC-1d`), the identification test
(`IC-2`), the compression metrics and the head-to-head comparison continue to run
over the full declared population, because a degenerate instance is still a
legitimate test of a closed form.

Both the full-population and the non-degenerate non-vacuity counts are reported,
so nothing is hidden by the narrowing.

No neighboring row is earned by this amendment.
