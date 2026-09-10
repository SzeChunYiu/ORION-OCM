# RV-A revival chain — what is decided, what is next

Parent: [CORE.md](CORE.md).

## Iteration 1 — attribution (done, this commit)

One stage: the T2/T3 correctness-predicate asymmetry (gate leakage), proven
exactly rather than inferred. Plus the draw-invariance proof that the endpoint
carries no information from the held-out key. Receipts under `results/`.

## Iteration 2 — is the depletion owned by the gate or by the ranking?

The revival question is now sharp: can any legitimate lever raise the
**absolute** count of checker-bearing T2-viable distinct survivors?

The discriminating measurement is the checker-bearing fraction of the viable set
**under the search's own sampling measure with all ranking machinery disabled**:
draw from `lane_hetero` (the lane every R2 arm used), evaluate every draw at T2,
apply no novelty gate, no surrogate ranking, no successive halving, no dedup
promotion, and report `P(can_check | T2-viable)` against the observed 0.1556.

- Lands near 0.1556 → the **gate** owns the depletion on frozen physics. No
  allocation or ranking lever can move it; the honest terminal is a
  proven-structural negative, delivered with the composition result above.
- Lands materially higher → the **ranking/promotion** stage owns it, the lever
  has a named target, and iteration 3 applies it.

Sizing: T2 evaluation measured at 0.385 ms/genome on LUNARC `lu48`
(`results/`-adjacent probe `hpc/rva_timing.py`), so 2×10⁶ draws is ≈0.3
CPU-hours. Interval width at that n is far below the effect size being tested.

## Iteration 2b — exhaustive ceiling: RETIRED, never run

An exhaustive enumeration of `GS_BOUND_V1` (143,881,920 grammars, 20.9 CPU-hours
at measured rates) was designed to bound `|{T2-viable ∧ can_check}|`. It was
**never run and its scripts are not in this study**, deliberately: the ceiling
was only ever going to argue headroom indirectly, and iteration 3 demonstrated
headroom directly by finding 34628 distinct T3-holding phenotypes in 0.0237
CPU-hours. A raw ceiling over 1.4×10⁸ grammars is in any case a statement about
budget rather than bias, since a search evaluating ~10⁵ candidates finds a tiny
fraction of any large space by budget alone. Recorded here so the absence is
deliberate rather than an oversight.

## Lever candidate, if iteration 2 says the ranking owns it

`evaluation/descriptors.py:78` computes
`refusal_rate = correct_refusals / (correct_refusals + harmful_transfers)`.
`GATE_CORRECTNESS` forces `harmful_transfers == 0` on every survivor, so this
archive axis is identically 1.0 across the entire archive — a gate-induced dead
axis, the same defect class as the `consolidation_ratio` dead axis already
recorded for the P00C census space. That degeneracy is provable from T2 and the
gate alone, with no reference to T3, which is what makes it the one lever
justification that is not designed to the endpoint.

Before use it must be verified as gate-induced rather than constant: 1.0 for all
survivors **and** varying over non-survivors.

## Rules this lane holds itself to

- No threshold moved, no gate loosened or tightened, no re-drawn or re-selected
  T3 key, no re-split after seeing results. Raising the hold rate by admitting
  fewer candidates is selectivity, not edge, and is recorded as a defect.
- Every claimed improvement reports hold **rate**, absolute hold **count**, and
  the null together. Here the null is analytic: hypergeometric subsampling of
  the parent survivor set to the lever arm's n.
- `PARENT_SUFFICIENT` is a success terminal; a proven-structural obstruction is
  a success terminal provided the proof and an adjacent scoped positive ship
  with it.
