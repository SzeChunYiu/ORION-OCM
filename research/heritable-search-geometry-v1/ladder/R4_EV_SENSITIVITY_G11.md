# R4 — G11: metric sensitivity of Ev (evolvability)

Row: G11 (Ev, finite probability), rung R4 (cheap partial per lane plan).

## Verdict (first sentence)

PARENT_SUFFICIENT — Ev is 1-Lipschitz in total variation between proposal kernels:
`|Ev_t(x; Σ) − Ev_t(x; Σ')| ≤ ‖Q_t(·|Σ) − Q_t(·|Σ')‖_TV ≤ δ_TV(Q_t)`, which is the
Dobrushin coupling bound applied to the indicator event {Adm ∧ Useful}; the same verified
parent as R4_CONTRACTION_G09.md owns it.

## Statement and one-line proof

`Ev_t(x;Σ) = P_{x'~Q_t(·|Σ)}[Adm(x') ∧ Useful(x')]` is the probability of a fixed event
under two candidate distributions; the coupling characterization of TV gives
|P_μ(E) − P_ν(E)| ≤ ‖μ − ν‖_TV for every event E (Dobrushin 1956; verified). No further
geometry: for stronger metrics d on the candidate space, Ev gains sensitivity only through
the induced TV (data processing) — i.e. the ONLY contraction-relevant metric on proposals
is TV, Chentsov-constraint echo.

## Assumption pass (A3)

- Remove xiii-iid-computable-Q: the bound is distributional, i.i.d. never used; verdict
  unchanged.

## Cell-grid note (atom-table ladder question)

The table asks "cell grid vs Wasserstein archive geometry": as a finite specialism, Ev on
a partitioned candidate space equals Ev of the coarsened kernel (law of total
probability), and the checker verifies equality exactly on a 4-cell example — coarsening
changes the EVENT, not the Lipschitz property; recorded as NOT a geometry finding
(NOT_APPLICABLE for the grid-vs-W axis at R4 scope).
