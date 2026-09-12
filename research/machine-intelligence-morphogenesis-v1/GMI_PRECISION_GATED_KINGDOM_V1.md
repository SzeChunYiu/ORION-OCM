# GMI — the precision-gated kingdom: is D3 a domain that exists only above an arithmetic threshold? (V1, executed)

Status: **EXECUTED EXACT AT SCOPE.** Receipt `microscopes/results/STAGE_DK_V2_PRECISION_GATED.json`
(`receipt_sha256` `096c09c47d14d1d8…`), frozen record `RV-377-066` in `REVIVAL_LEDGER_DK2.jsonl`
(FREEZE commit `a19197e`, before execution), microscope `gmi_microscope/dk_precision.py`. Issue #422.
Companions: `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` (GMI-DA1, GMI-DA4, GMI-DA5, §9),
`GMI_GAP_LEDGER_EXECUTED_V1.md` (gap G5, closed; its consequence is executed here),
`GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` (D3, §14).

---

## 1. The question, and why it had never been asked

Eleven domain candidates have been executed against matched strongest parents and **all eleven reduced**. GMI-DA1
says why: each was a bounded composition over the primitive alphabet **at a fixed arithmetic precision**. GMI-DA5
already proves that carrier admissibility is a function of the *instrument*, not only of the carrier and the
ecology — two instruments running identical charged operation sequences at different precisions can differ in
admissibility — and two carriers are known to be shut out at 8 bits and to work wide: the probabilistic carrier
(D3, `RV-377-029`/`031`) and the energy/coupling carrier (`RV-377-045`).

What was never asked is the **kingdom** question on that axis:

> Is there an ecology in which, at wide precision, the probabilistic carrier occupies frontier cells that **no
> carrier admissible at 8 bits** occupies at any reuse horizon?

If yes, D3 is a structural domain that exists only above a precision threshold, and the eleven reductions were an
artefact of the registered 8-bit universe. If no, precision is a substrate parameter and not a kingdom-maker.

**The executed answer is yes on one of the two ecologies built for it, and the threshold is 10 total bits.**

---

## 2. The executed decision

```
PRECISION_GATED_KINGDOM_ESTABLISHED_AT_SCOPE__THRESHOLD_12_BITS
```

on the declared ladder (8, 12, 16, 24, 32, unbounded), **refined by bisection to 10 total bits with 5 fractional
bits**. Thirteen frozen clauses, **13 of 13 HOLD**, including the one clause of the record that was genuinely
blind (clause 13, the variant-C replication).

The decision rests on the **ambiguous-evidence** ecology and *not* on the noisy-label one. Both are recorded.

| | `E_ambig` (ambiguous evidence) | `E_noisy` (noisy labels) |
|---|---|---|
| admissible at fx8 (the registered universe) | **nothing** — all ten rows score exactly 0.0 | `QCOUNT` at **0.863997** |
| 8-bit-representable answer would score | **0.910880** (≥ θ = 0.85) | — |
| admissible at fx12 | `BAYESM` 0.997275, `QCOUNT` 0.997275 | `BAYES`, `BAYESM`, `QCOUNT` |
| admissible at `wide` | `BAYES` 1.0, `BAYESM` 0.997275, `QCOUNT` 0.997275 | `BAYES` 1.0, `BAYESM` 0.921941, `QCOUNT` 0.949948 |
| precision-gated frontier cells at fx12 and above | **every cell of all 20 (instrument, price, description) keys**, 36–63 per key | **0** |
| verdict | **precision-gated kingdom** | **no gate: an 8-bit parent occupies every cell** |

---

## 3. The two confounds, separated (this is the load-bearing part)

A capability difference between two instruments is a **precision gate** only if the operation sequences are
identical and the descriptions are charged on the same basis. Both are enforced and both are measured.

* **Identical charged operation sequences.** Every row is written with fixed-trip-count loops and no
  data-dependent early exit. For all **20 row-cells** (10 rows × 2 ecologies) the charged op vector
  `R = (desc, exec, upd, ver, rev)`, the total charged scalar activation count and the native op vector are
  **identical across all six instruments**; the receipt asserts it per row per cell
  (`charged_op_identity.all_rows_all_cells_identical = true`), and clause 2 falsifies the run if it ever fails.
* **Same description basis.** `desc = w_scalars · 8 bits + struct_bits` for *every* instrument, with a declared
  `scaled` sensitivity column (`w_scalars ·` the instrument's own word width). The flat basis is generous to the
  wide instrument; the decision holds under both.
* **The 8-bit column really is the registered universe.** `fx8` is bit-identical to `core.Machine.op` for MUL,
  ADD, SUB and GT on all **65 536 operand pairs — 262 144 assertions** (clause 1).

---

## 4. The gate is dynamic range, not resolution

The single most important number in the receipt is **0.910880**. On `E_ambig`, a forecaster that serves at every
evaluated input the closest value on the fx8 grid (multiples of 1/16) to the exact Bayes probability `q*(x)`
scores 0.910880, comfortably above θ = 0.85. **An admissible answer is expressible at 8 bits.** No 8-bit carrier
computes one.

The mechanism: a normalized weight vector over a 32-member hypothesis class has no representable uniform value at
4 fractional bits — 1/32 is below the instrument's smallest positive value — so sum-normalization drives the whole
posterior to 0 or to 1/16 and the mixture collapses. This is the `RV-377-029`/`031` underflow, priced and raised
to an occupancy verdict.

The threshold, bisected on the fine ladder 8…16 total bits (fractional bits = ⌊b/2⌋):

| total bits | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|
| fractional bits | 4 | 4 | 5 | 5 | 6 | 6 | 7 | 7 | 8 |
| `BAYESM` on `E_ambig` | 0.0 | 0.0 | **0.954074** | 0.954074 | 0.997275 | 0.997275 | 0.997275 | 0.997275 | 0.997275 |
| `QCOUNT` on `E_ambig` | 0.0 | 0.0 | **0.997275** | 0.997275 | 0.997275 | 0.997275 | 0.997275 | 0.997275 | 0.997275 |
| `BAYES` on `E_ambig` | 0.0 | 0.0 | 0.0 | 0.0 | 0.456162 | 0.456162 | **0.080183** | 0.080183 | **0.886352** |

Two things worth stating plainly. The domain's threshold is **10 total bits / 5 fractional bits** — one bit of
mantissa past the registered universe. And **capability is non-monotone in precision** for the exact posterior:
0.456 at 12 bits, 0.080 at 14, 0.886 at 16. "More bits is better" is false for a quantized mixture.

---

## 5. The parent-maximal opponents (protocol rule 19), and what they cost the claim

The opponents were built adversarially, not conveniently, and two of them were **added or repaired during
pre-freeze calibration specifically to make them stronger** — both changes are disclosed in `RV-377-066` and each
was worth one ecology's verdict:

* the count accumulator step was changed from 1/8 to 1/16 because at 1/8 the count row's top-4 normalizing sum
  reached 12 and **clamped at 7.9375** — an accounting handicap, not a precision one. With the repair `QCOUNT`
  rises from 0.6012 to **0.863997** on `E_noisy` at fx8 and becomes admissible there, which is precisely what
  removes `E_noisy` from the kingdom claim;
* `BAYESM`, a max-renormalized top-4-pruned Bayesian row — the two standard anti-underflow devices of practical
  Bayesian computation — was added after the first calibration showed that no 8-bit Bayesian row was registered
  at all.

Without either change this document would have claimed a kingdom on *both* ecologies.

The remaining opponents fail for reasons that are **carrier** properties, not precision properties, and the
receipt says so: `PROG` (deterministic program search, serving a 0/1 label) scores exactly 0.0 in 12 of 12
(ecology, instrument) cells; `MAP` (the same evidence-weighing machinery served as a point estimate in hypothesis
space) scores 0.800443 at `wide` on `E_noisy` and 0.0 on `E_ambig`; and `COEF`, `EXEM`, `GEN`, `BASE` and
`UNIFMIX` are inadmissible in **60 of 60** row-cells. Under a strictly proper scoring rule the sub-optimality of a
point estimate is a *measured* quantity here, not a definition.

---

## 6. The uncomfortable half: the occupant is not the exact posterior

Inside the kingdom, the exact posterior does not hold the ground.

| row on `E_ambig` | desc (bits) | charged activations / query | reduced-price cells held | native-price cells held |
|---|---|---|---|---|
| `BAYES` (exact posterior over 32 hypotheses) | 544 | 96 | **0 of 42** | **1 of 49** (H = 1, r = 0) |
| `BAYESM` (max-renormalized, top-4) | 596 | 12 | shares 6 | shares 6 |
| `QCOUNT` (quantized counts, top-4) | 596 | 12 | 36 alone | 42 alone |

`BAYES` is a factor of **exactly 8** more expensive per query and only 52 bits cheaper to describe, so its
analytic reduced-price crossover is `H* = 52/84 = 0.619048` queries — below the smallest non-abstained reuse
horizon `H = 1`. (Per gap G3 the `H = 0` description corner is **abstained**, not claimed; every grid here starts
at `H = 1`.) The cells are held by the two rows that were built as *opponents*. They are themselves D3 carriers
and are themselves precision-gated on `E_ambig`, which is why the domain verdict stands and the exact-inference
verdict does not: **what is gated in is the domain, not exact inference.**

---

## 7. Grid discipline (gap DG-2) and replication

The H and r grids are extended past **twice** the analytic crossover of every pair under every price vector, and
the receipt additionally reports the exact asymptotic occupants as `H → ∞` and as `r → ∞`, so no clause here is a
grid-truncation artefact. Two further declared event sequences were executed: variant B (disclosed as calibrated
before the freeze) and **variant C, blind** — written into the committed code before the FREEZE commit and first
executed by this receipt. Both reproduce `E_ambig`: empty admissible set at fx8, exactly `{BAYESM, QCOUNT}` at
fx12, exactly `{BAYES, BAYESM, QCOUNT}` at `wide`. Every row is deterministic (no `SAMPLE` activation is executed
anywhere in this microscope) and all 40 seed-1-versus-seed-0 comparisons are equal.

---

## 8. Claims, with levels and ceilings

**Claim DK-1.** *There exists a registered ecology and a reuse region in which every frontier cell is occupied by
a carrier that is inadmissible in the registered 8-bit universe, while the charged operation sequence is held
bit-for-bit identical across instruments.*
**Level:** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY` (`RV-377-066`, 13/13 clauses).
**Ceiling:** one ecology (`E_ambig`), one declared hypothesis class of 32 members, one declared prior, three
declared event sequences, one machine seed, one basis column. It is not a claim about any real probabilistic
system, and it is not a proof over the whole non-negative `(H, r)` quadrant — the frontier is decided on an
extended grid plus exact asymptotics.

**Claim DK-2 (the threshold).** *The domain's threshold is 10 total bits with 5 fractional bits; the exact-posterior
realization's is 16; and capability is non-monotone in precision between them.*
**Level:** `PROVED_AT_SCOPE` for the executed instrument family.
**Ceiling:** the threshold is a property of this instrument family (`b` total bits, `⌊b/2⌋` fractional), this
class size (32) and this evidence length (24 events); it is not a universal bit width for probabilistic inference.

**Claim DK-3 (the negative half).** *Precision is not a kingdom-maker in general: on `E_noisy` a quantized-count
posterior reaches θ at 8 bits (0.863997) and occupies all 36 cells of every fx8 key, so that ecology has an 8-bit
parent everywhere.*
**Level:** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY`.
**Ceiling:** the margin is 0.013997 above θ — thin, and the verdict for that ecology would flip if the count row
were weakened. It was strengthened twice before the freeze precisely because of that.

**Claim DK-4 (the theory consequence).** *GMI-DA5 upgrades from admissibility to occupancy: the arithmetic
instrument is a kingdom parameter. Criterion 3 of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1` §14 must therefore name its
instrument, as it already must name its depth bound (DG-3) and its parent-maximal opponent (DG-5). This is new gap
**DG-6**, and it scopes §9b of the domain algebra: the terminal
`NO_NEW_KINGDOM_ESTABLISHED__NINE_CANDIDATES_EXECUTED_AND_ALL_NINE_REDUCED` is a statement about the 8-bit
universe, and every one of the eleven reduction verdicts inherits an instrument qualifier.*
**Level:** `PROVED_AT_SCOPE` as a statement about this programme's own criterion.
**Ceiling:** it does not re-adjudicate any of the eleven candidates. Whether any of them would survive a wide
instrument is unexecuted, and is the obvious successor experiment.

---

## 9. Honest limits of this record

`RV-377-066` is labelled a **reproduction-and-structure freeze, not a blind prediction**: every number in clauses
1–12 was computed in uncommitted dry runs before the FREEZE commit, and the record says so. Only clause 13 carries
predictive weight. The two ecologies are built so that only a carrier holding an explicit hypothesis class can
serve the obligation at all — that is a property of the ecologies, and it is why the class-free parents fail at
every precision rather than at a threshold. Charged ops are counted per scalar **activation**, not per bit, so a
wide-precision operation is charged exactly as an 8-bit one and a division is charged by a fixed macro; this is
the declared basis on which the instruments are made comparable, and it is generous to the wide instrument. The
`scaled` description column is the declared sensitivity, and the decision holds under it.

**Terminal:** `PRECISION_GATED_KINGDOM_ESTABLISHED_AT_SCOPE__THRESHOLD_12_BITS` (declared ladder; refined
threshold 10 total bits / 5 fractional bits), on one of two ecologies, with the occupancy held by the pruned and
count-based realizations of D3 rather than by exact inference.
