# Search-stage amendment to `FREEZE_V1_ECOLOGY_ADDENDUM.md` A8 step 3

Registered **before any held-out or contiguous-tail slice has been read, before
any arm has been fitted at scale, and before any prediction of `FREEZE_V1.md`
Section 8 has been resolved.** No outcome exists at the time of this commit.

## What was observed

A machinery smoke run of A8 step 3 on the `E_H03` **search** slice only
(`n_screen = 300` rows, no held-out or tail row read) showed that the frozen
two-scalar screen — one `BIAS` and one value shared by every `PARAM_i` — ranks
candidates by how well a *single shared* coefficient fits all coordinates. The
top of that ranking was populated by `RECIP`-headed candidates; the canonical
`MUL(ARG,PARAM) | ADD(S,BIAS)` candidate cannot be represented at all by a
shared coefficient when the design's coordinates carry different scales, which
`E_H02`, `E_H03` and `E_H04` all do by construction.

## Single-stage attribution

The defect is in the **screen stage** and only there. Enumeration, quotient,
classification, fitting, cost model, evaluation and the frozen predictions are
untouched. The screen was intended as a cheap pre-filter; as frozen it is not
merely cheap, it is **structurally unable to score a per-coordinate parameter
vector**, so it can eliminate exactly the structures Section 8 predicts and
would have produced a search artefact rather than a result.

## The lever

A8 step 3 is replaced by: **screen every enumerated pair with the same generic
fitting routine used in step 4, at reduced rows and reduced sweeps** —
`n_screen = 600` rows of the search slice, generic fit (least squares when the
prediction is affine in the parameters, else coordinate descent with 2 sweeps),
ranked by the same loss, keeping the best `KEEP = 40`.

This removes a representational restriction; it adds no family information, no
target-specific candidate, and no per-scope constant. It is applied identically
and blind at all four scopes. Steps 1, 2, 4 and 5 of A8 are unchanged, as is
every threshold, prediction, falsifier and forbidden promotion.

## What this amendment does not do

It does not change any ecology, any slice, any response, any comparison arm,
any cost model, any claim ceiling, or any prediction. It reads no held-out data.
It is not a response to an outcome, because no outcome exists yet.
