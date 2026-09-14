# Generative factorizations, and a law that failed its held test (B17)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/generative_family_witness.py`.
Receipt: `microscopes/results/STAGE_GENERATIVE_FAMILY_V1.json`.
Derived by a parallel worker. Witness and receipt md5 **independently
reproduced** on `laptop-billy` (exit 0, 22.8 s); 58 assertions; byte-identical
across runs; **zero floating-point values in the receipt**.

## The main finding is a failure

The chain-ordering law — fitted on the 70 four-atom supports where it reads as a
clean two-way rule, **right 70 of 70** — is **wrong** on held data:

| support size | joints | correct | said sensitive, was flat |
|---:|---:|---:|---:|
| 2 | 28 | 22 | 6 |
| 3 | 56 | 32 | **24** |
| 5 | 56 | 32 | **24** |

> A rule that is perfect on the support size it was fitted on is wrong on nearly
> half the joints at two other sizes. **Filed CORRECTED, not repaired.**

Only the one-way implication survives, and it survives cleanly: full coordinate
symmetry ⟹ ordering-flat, **13 of 13** across the whole 247-joint census. The
converse fails.

The witness contains `assert _fail` — it asserts the failures **exist**, so a
future change that quietly made the law pass would trip the gate rather than
erase the correction.

## The sharp impossibility

`parity_even` — uniform on even-parity strings — is where the families visibly
stop being interchangeable:

| representation | cost |
|---|---|
| chain | **4 numbers** |
| mixture | **4 components** — one per atom, *no compression at all* |
| bijection from a full-support product base | **none exists** |

The mixture needs one component per atom because every product set inside an
even-parity support is a singleton. And no bijection whatever writes it down —
**verified against all 40 320** — because a bijection cannot create the four
zeros. Exhibited, not argued.

The base-relative caveat is kept honest and backed by a construction:
`parity_even` **is** reachable from base `(unif, unif, δ₀)` under
`x ↦ (x₁, x₂, x₁ ⊕ x₂ ⊕ x₃)`.

## Two strengths of "unreachable", deliberately never merged

| joint | status | kind |
|---|---|---|
| `and_gate` under iteration | `not ≤ 3` | **a search limit** |
| `product_biased` | `never (non-dyadic)` | **structural** — every kernel maps dyadic rationals to dyadic rationals |

A gate asserts that both kinds occur, so the weaker sense can never be reported
as the stronger one.

## What the worker weakened or flagged

Recorded because it is the useful part.

- **The specimen panel has exactly one ordering-sensitive joint** (`and_gate`).
  The general claim rests on the **247-joint census**, not the panel.
  `pair_block`'s flat gap was separately verified genuine — all six orderings
  cost 4 — rather than a dedup artefact.
- **`layers` is relative to the 1344-element affine class**, not all 40 320
  bijections. `and_gate` is *not in class* yet reachable by *some* bijection.
  Two invertible columns use different bases and the header says so.
- **Discrete flows carry no Jacobian**, so the impossibility is about the
  discrete case only — stated in the output, since it is the first thing a
  reviewer reaches for.
- **A pricing omission the worker caught in their own machine.** The local-step
  machine was charged for neither its start distribution nor its kernel class,
  so it won every cell at `stored = 1` and — having `ctx = 0, parts = 1` —
  *printed as "independent coordinates"* for `parity_even`, which the same
  witness proves is **not** a product. One omission, two visible faults. Now
  priced at `N + T`. An arbitrary tie-break (first-generated candidate) was also
  replaced by a stated criterion (fewer passes).
- **The held panel is 5 usable joints, not 6** — one duplicated `uniform` and was
  dropped by the disjointness filter; two of the five share a value multiset.

## Scope

- Three binary coordinates, eight atoms, exact `Fraction` arithmetic throughout.
- The census is 247 joints; the specimen panel and the held panel are much
  smaller and are not the basis of any general claim.
- Flow results are stated **relative to a named base**, and the document says
  which one each time.

**Falsifier.** Exhibit a joint where full coordinate symmetry fails to imply
ordering-flatness; or a bijection from a full-support product base onto a joint
with a zero atom; or a mixture representing `parity_even` in fewer than 4
components.
