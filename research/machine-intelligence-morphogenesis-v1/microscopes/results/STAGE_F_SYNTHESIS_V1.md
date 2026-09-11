# Stage F — blind recovery at tiny scope: synthesis across the three registered runs

| run | budget | ecology | frozen criterion | outcome | falsifier triggered? |
|---|---|---|---|---|---|
| V1 (frozen) | 3 000 random + 40 hill steps | E_bind (4 inputs) | F1: ≥ 0.5 of winners use the store with ≤ 2 writes/event | 6 winners at θ=1.0: 3 numeric-sparse (cells used as memory, 0–1 writes/event), 1 numeric-dense, 2 hybrid; 0 store-local | no (winners are not dense-numeric as a class) — but criterion fails |
| V1 (frozen) | same | E_smooth (16 inputs, 8 seen) | F2: ≥ 0.5 of winners numeric-dense (no store, ≥ 3 cells) | no winner reaches θ=0.85 (best 0.833) | undecidable |
| RUN2 (declared, 4×) | 12 000 + 160 | E_bind | F1 | 12 winners: 5 numeric-sparse, 4 store-local, 3 hybrid | criterion fails (0.33) |
| RUN2 (declared, 4×) | same | E_smooth | F2 | 1 winner (0.854): numeric-sparse, non-store | direction consistent (numeric, non-store); density criterion fails |
| RUN3 (declared F′) | 6 000 + 80 | E_bind16 (16 inputs, all seen) | F′: ≥ 0.5 of winners store/cell-local (≤ 2 writes/event); falsifier = dense numeric winners | 9 winners at θ=1.0: 9/9 store-based, 0/9 dense-numeric; 2/9 within the write threshold, 7/9 also write scratch cells | **falsifier not triggered**; criterion fails on incidental writes |

## What survives

- The **type axis** behaved as the ecology-axis theory predicts in every run: discrete exact
  binding ecologies were solved by memory forms (cells or store), never by a dense-numeric class as
  a majority; the smooth-generalization ecology's only winner was numeric and non-store.
- The **frozen criteria were the wrong instruments**: store-primitive use is not a morphology
  coordinate when cells can act as a store (V1/RUN2), and raw write counts include dead scratch
  writes (RUN3). Both defects are recorded as revival records (RV-377-006/007/008) with the
  corrected instrument (dead-write elimination; locality on output-relevant writes) frozen for
  the next run — not applied retroactively.
- **No blind-recovery credit is claimed.** Per #377 §13/§23 the outcome is a *bounded failure* with
  the instrument defect identified, one seed, one search family, one basis column. B5 stays not
  earned.

## What this says about the ultimate question

At this scope a label-free search over one neutral grammar reliably finds *memory-form* solutions
to exact discrete binding and *numeric-form* solutions to smooth targets — the direction the
parent-anchored axes predict — but the signature observables must be computed on canonicalized
(dead-code-free) candidates before they can classify what search finds. That canonicalization
requirement was already in Codex's Stage C-v1 protocol; Stage F re-derived it the hard way.
