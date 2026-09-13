# GMI — the precision-gated kingdom: is D3 a domain that exists only above an arithmetic threshold? (V1, executed)

> **STATUS AFTER `RV-377-075` AND `RV-377-076` — READ THIS FIRST.**
> The terminal of §2 below is **`FALSIFIED_AND_REPLACED`**. `RV-377-075` added one row this document's
> portfolio omitted — an 8-bit **log-domain** posterior, built only from registered kinds — which scores
> **0.874265** and **is admissible** at fx8 on `E_ambig`, where all ten rows of this record score exactly 0.0.
> `RV-377-076` then attacked that refutation with **seven** named attacks and **none of them reverses it**; the
> log row is admissible at fx8 under every declared table-charging regime. **The precision-gated kingdom is
> dead and this document does not claim it.** Everything in §§1–9 is preserved verbatim, including its
> clause-by-clause scoring — the thirteen clauses did hold, and they still do; what failed was the *inference
> from them*. The surviving result is a **cost** statement and is executed in §§10–13.
>
> Sections added by `RV-377-076`: **§10** the hostile audit of the refutation, **§11** the residual frontier,
> **§12** why declared sequence B failed, **§13** the amended claims.
> Added by `RV-377-077`: **§14** — the residual re-asked against a *parent-maximal* 8-bit row. It survives, but
> **2 352 of its 2 508-bit margin was padding**, and the pruned 8-bit log row is now admissible on **10 of 10**
> declared sequence-cells.
> Added by `RV-377-078`: **§15** — the residual re-asked on a *second ecology built to break it*. It survives
> that too, and the record's own hypothesis is **falsified**. `E_graded` widens the linear representation's gate
> from 10 to **12 total bits** and moves **no occupancy at all**.
> Added by `RV-377-079`: **§16** — **the residual is a small-class artefact.** Every record above used a
> 32-member class. At **K = 128** an 8-bit row **occupies 7 of 2 760 cells** and has **zero cost-coordinate
> dominators**. The positive is real, pre-registered, and needs four permissive choices at once — all four are
> in its terminal.
> Added by `RV-377-080`: **§17** — **it is not a residual, it is a line.** The cost difference is exactly
> **−2K + 376** under the *registered* price, verified to the unit at seven class sizes, and the occupancy
> appears at its root. **Two of the four permissive choices are gone.**

Status: **EXECUTED EXACT AT SCOPE** (§§1–9, terminal superseded — see the banner above).
Receipt `microscopes/results/STAGE_DK_V2_PRECISION_GATED.json`
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

**Terminal status:** `FALSIFIED_AND_REPLACED` by `RV-377-075`, audited and upheld as falsified by `RV-377-076`.
The replacement terminal is in §13.

---
---

# Part II — after the refutation (`RV-377-076`, executed)

Receipts `microscopes/results/STAGE_DK_V4_LOGDOMAIN_AUDIT_V1.json` and
`microscopes/results/STAGE_DK_V5_PRECISION_RESIDUAL_V1.json`; frozen record `RV-377-076` in the **new** ledger
file `REVIVAL_LEDGER_PRESIDUAL.jsonl` (FREEZE commit before execution; `REVIVAL_LEDGER.jsonl` untouched);
modules `gmi_microscope/dk_precision_log_audit.py` and `gmi_microscope/dk_precision_residual.py`.

## 10. The refutation, attacked — seven attempts to show the log row is cheating

`RV-377-075` is not accepted on trust. Seven named attacks were built, each of which would have restored §2 if it
had landed. **None does.** Every attack imports this record's own microscope, ecologies, event sequences, scoring
rule, θ and cost model unchanged.

| attack | what it tests | executed finding | lands? |
|---|---|---|---|
| **A1 TABLE** | is the 256-entry exponent table a registered kind, and is one `SEL` per read the registered charge? | **No, and no.** There is no `TABLE` or `MATERIALIZE` kind in the registered universe, and **none of the five registered store kinds is native in `B0`** — `core.Machine._emulate` realizes `S_LOOKUP` in this basis as a **linear scan, one `EQ` per entry**. Re-charged at that rate `exec_q` goes **208 → 8 432** per query (×40.54); under the declared indexed-emulation amendment (10 probes) it is **560**. Materializing the table under the store description basis raises `desc` **3 104 → 3 618** bits. **Capability is bit-identical under all six regimes.** | **no** |
| **A2 CONSTS** | are the log constants treated as `dk_precision.py` treats its probability constants? | **Yes.** 1 056 log constants and 256 table entries per (ecology, instrument) across 8 cells, recomputed by **exact integer comparison with no floating point anywhere** (`A.const(log₂p) = ⌊\|log₂p\|·S + ½⌋` is decided by `2^(2v−1) ≤ (1/p)^(2S) < 2^(2v+1)`). **0 wrong.** Both are exact values rounded half-up to the instrument grid and uncharged because they are description — the identical treatment. | **no** |
| **A3 MAXSUB** | one `GT` and one `SUB` per hypothesis per event? | **63** charged activations per event (31 `GT` — the minimum for a max over 32 — plus 32 `SUB`) against a declared 63–64. Undercharge of **at most 1 activation per event, 24 of 1 512**. | **no** |
| **A4 RANGE** | does every intermediate clamp to the fx8 range? Instrumented, not assumed. | **137 326** values traced at fx8 on `E_ambig`/A: raw range exactly **[−128, 127]**, **0** outside the instrument, **529** clamp events. Recorded and not softened: the row's underflow guard compares against `exp_lo = −255`, which is **not representable at fx8** — it is **inert** there, because a clamped log-weight never falls below −128, so the branch is unreachable. | **no** |
| **A5 LEAK** | does the answer reach the eval set through the same `capability` with no leakage of the truth? | **36** cells re-run against an ecology whose `qstar`, `post`, `qbar` and `var` are replaced by nonsense: **every answer signature identical**. Positive control (flat prior, which the row *is* entitled to read) **moves**. Same `capability` function object as `dk_precision`. | **no** |
| **A6 OPIDENT** | this record's own load-bearing control, applied to the refuting row | **FOUND A DEFECT.** `RV-377-075` charges its readout division **only when the denominator is non-zero**, so its charged op sequence is **data-dependent**: `LOGBAYES8` charges 3 290 043 at fx8/fx10/fx12 and **3 289 787** at fx16. That is exactly the control §3 enforces over 20 row-cells. Repairing it restores identity at all four instruments. It moves **no capability**. | **no** |
| **A7 COUNTER** | does the refuting row count its own table reads? | **FOUND A DEFECT.** `M.op("SEL")` charges the phase ledger but never increments the instrument's op counter, so the published `charged_ops_total` understates by **12 544** on the ambiguous ecology (392 queries × 32) and 25 088 on the noisy one, in **48 of 72** cells. The **phase ledger `R`, which is what the cost model reads, is identical in all 72 cells**, so no frontier moves. A reporting defect, not a pricing one. | **no** |

**The asymmetry, stated rather than used to soften anything.** A1, A3, A6 and A7 are real findings and two of them are
defects in the refuting row. **None of them can restore §2**, because §2's kingdom condition is an *admissibility*
condition — "no member of `S` is itself admissible at 8 bits" — and **charging is not in the capability
functional**. What the charging findings move is the **cost**, which is the entire residual of §11.

**Terminal of the audit:**
`RV_377_075_SURVIVES_THE_HOSTILE_AUDIT__THE_8_BIT_LOG_DOMAIN_ROW_IS_ADMISSIBLE_AT_0_874265_UNDER_EVERY_DECLARED_TABLE_CHARGING_REGIME__RV_377_066_IS_NOT_RESTORED`

---

## 11. The residual: precision buys **description and execution cost**, not capability

`RV-377-076` clauses **1–11**, scored verbatim. **9 HOLD, 2 FAIL.** Failed clauses are stated in full and are
neither deleted nor softened; where a failed clause has a correct replacement, the replacement is stated **as a
replacement** and carries its own level.

| # | clause | verdict |
|---|---|---|
| 1 | *(reproduction, disclosed)* all seven attacks fail to reverse `RV-377-075`; the numbers of §10 | **HOLDS** |
| 2 | *(analytic)* `LOGBAYES8@fx8` is dominated **coordinate-wise on all five raw coefficients** by `QCOUNT@fx10` and `BAYESM@fx10` | **FAILS** |
| 3 | *(analytic)* every pair involving `LOGBAYES8@fx8` reports a domination and an **empty** crossover; where a crossover exists the grid passes twice it | **FAILS** (first half) / **HOLDS** (second half) |
| 4 | *(blind)* on `E_ambig` the cross-instrument frontier gives `LOGBAYES8@fx8` **0 cells**, and **any** fx8 row **0 cells**, in all four keys | **HOLDS** |
| 5 | *(blind)* the fx8 admissible set on `E_ambig` is exactly `{LOGBAYES8}`, which therefore occupies **100 %** of the fx8 per-instrument frontier | **HOLDS** |
| 6 | *(blind)* **no** cell needs a wider instrument for *admissibility*; a wider instrument is strictly *cheaper* in every cross-instrument cell | **HOLDS** |
| 7 | *(analytic)* `desc` ratio 3 104/596 = **5.2081**; `exec_q` ratio 208/12 = **17.3333**; under the registered `B0` scan charge 8 432/12 = **702.6667** | **HOLDS** |
| 8 | *(analytic)* under the `scaled` basis 3 104 against **668**, ratio **4.6467**; domination and 0-cell occupancy unchanged | **HOLDS** |
| 9 | *(blind)* the split test: declared sequences D and E do not both agree with A and C | **FAILS** |
| 10 | *(blind)* at least one **concentration** variable separates the admissible ambiguous sequences from the inadmissible one, and H1's flip-count-before-revocation does **not** | **HOLDS** |
| 11 | *(blind)* `LOGBAYES8_NOMAXSUB` is exactly 0.0 at fx8 on all five ambiguous sequences, D and E included | **HOLDS** |

### 11a. Clause 2, FAILED — stated in full

The frozen clause asserted domination on all five raw coefficients `(desc, exec_q, upd_e, ver_e, rev_e)`. It is
**false**, and the frozen record's own falsifier (2) is what catches it. Under the **reduced** price and the flat
basis the set of rows dominating `LOGBAYES8@fx8` on the raw coefficients is **EMPTY**, because the log row is
*cheaper* on `upd_e`:

| row on `E_ambig`, reduced price, flat basis | `desc` | `exec_q` | `upd_e` | `ver_e` | `rev_e` | ρ = `upd_e + ver_e + rev_e/4` |
|---|---|---|---|---|---|---|
| `LOGBAYES8@fx8` | 3 104 | 208 | **95** | 1 672 | 1 235 | 2 075.75 |
| `QCOUNT@fx10` | 596 | 12 | 356 | 104 | 356 | **549** |
| `BAYESM@fx10` | 596 | 12 | 1 971 | 104 | 21 783 | 7 520.75 |
| `BAYES@fx16` | 544 | 96 | 1 648 | 776 | 21 472 | 7 792 |

The clause was also wrong to name `BAYESM@fx10`, whose ρ is **3.62×** the log row's.

**The replacement, which holds.** The frozen cost function `C = desc + H·exec_q + r·(upd_e + ver_e) + (r/4)·rev_e`
is affine in `(H, r)` with exactly **three** coefficients — `desc`, `exec_q` and `ρ` — not five. On those three,
`QCOUNT@fx10` dominates `LOGBAYES8@fx8` in **all four `E_ambig` keys and all four `E_noisy` keys**:
`(596, 12, 549)` against `(3 104, 208, 2 075.75)` under the reduced price, `(596, 4, 112)` against
`(3 104, 96, 904)` under the native price. Cost-coordinate domination is **necessary and sufficient** for
`cost_a ≤ cost_b` at every `H ≥ 0, r ≥ 0`, so the 0-cell result of clause 4 is a **theorem about the affine cost
function**, not a grid observation. **Level:** `PROVED_AT_SCOPE` for the frozen cost model.
**Ceiling:** it is a statement about *this* cost function's three coefficients; a cost model with a different
`r`-weighting would need re-deriving.

### 11b. Clause 3, FAILED in its first half — and how DG-2 is actually discharged

Not every pair is a domination: under the reduced price and the flat basis, `BAYESM@fx10` and `LOGBAYES8@fx8` have
a **positive `r`-crossover at 76/165 = 0.460606**, so the "empty crossover" half is false. The second half holds and
is what DG-2 requires: in **all eight** cross-instrument keys the `H` grid reaches **8 192** against a largest
`H`-crossover of **75.0**, and the `r` grid reaches **256** against a largest `r`-crossover of **23.25** — past
twice each, per axis, with the flags asserted in the receipt. The exact asymptotic occupants are also reported:
as `H → ∞` and as `r → ∞` the minimizers are `QCOUNT` (and `BAYESM` for `H → ∞`), and `LOGBAYES8@fx8` is in
**neither** set. So no cell of the unbounded quadrant is being hidden by a truncated grid.

### 11c. The executed residual

| `E_ambig`, sequence A | reduced / flat | reduced / scaled | native / flat | native / scaled |
|---|---|---|---|---|
| cells in the cross-instrument frontier | 42 | 294 | 49 | 899 |
| held by `LOGBAYES8@fx8` | **0** | **0** | **0** | **0** |
| held by **any** fx8 row | **0** | **0** | **0** | **0** |
| held by `QCOUNT@fx10` | 42 | 294 | 48 | 899 |
| fx8 **per-instrument** frontier, cells held by `LOGBAYES8` | 36 of 36 | 36 of 36 | 36 of 36 | 36 of 36 |

The fx8 row occupies its own instrument's frontier completely and the joint frontier not at all. That is not a
paradox: at fx8 on `E_ambig` it is the **only admissible row**, so protocol rule 17 hands it an empty field.

**The contrast that makes the residual a real quantity.** On `E_noisy` an 8-bit row *does* hold the joint
frontier — `QCOUNT@fx8` takes **42 of 42**, **243 of 243**, **48 of 49** and **1 120 of 1 120** cells of the four
keys. Whether precision buys anything at all is therefore an **ecology** property, exactly as `RV-377-066`
invariant (iv) said, and the direction of the purchase has changed from capability to cost.

**The price of eight bits, on `E_ambig`.** Two extra bits of instrument (8 → 10 total, 4 → 5 fractional) replace a
3 104-bit / 208-activation log-domain row with a 596-bit / 12-activation quantized-count row:

| ratio, `LOGBAYES8@fx8` ÷ `QCOUNT@fx10` | value |
|---|---|
| description, flat basis | **5.208054** (3 104 ÷ 596) |
| description, `scaled` basis | **4.646707** (3 104 ÷ 668) |
| charged activations per query, reduced price, `RV-377-075`'s own table charge | **17.333333** (208 ÷ 12) |
| charged activations per query, reduced price, **registered `B0`** table charge | **702.666667** (8 432 ÷ 12) |
| charged activations per query, native price | **24.0** (96 ÷ 4) |
| reuse coefficient ρ, reduced price | **3.780965** (2 075.75 ÷ 549) |

Two bits buy back **2 508 description bits** and **196 charged activations per query** — and they buy it at
**every** cell of all four keys, not at a crossover.

---

## 12. Why declared sequence B fails — and it is **not** the ecology

`RV-377-075` reported the log row admissible on sequences A and C and inadmissible on B (0.400545). Sequences
**D** and **E**, declared in the FREEZE commit of `RV-377-076` and never executed before it, are both
**admissible** — D at 0.910859 and E at 0.874273. The ambiguous split is therefore **4–1**, not 2–1, which
**falsifies `RV-377-075`'s own registered successor prediction** that further sequences would "split roughly as
A and C did against B", and which fails clause 9 of this record as written.

**The three structural hypotheses, measured.**

* **H1 — evidence before the revocation.** Does **not** separate. Flips before the revocation point: A 1, B 1,
  C 1, D 2, E 1; after: A 1, B 1, C 1, D 0, E 1. The revoked event is unflipped in all five.
* **H2 — flip position.** `first_flip_index` *does* separate on this five-point sample (B 9; A 5, C 2, D 0, E 7),
  but it is a **rank order over five points with one member in the failing class** and it names no mechanism.
* **H3 — concentration.** Four concentration variables separate **in rank order and nowhere else**. B is the
  minimum on every one of them, by margins of **10⁻⁴ to 10⁻⁵ relative**, against a capability gap of **0.473720**:

| | A | B | C | D | E |
|---|---|---|---|---|---|
| max posterior weight | 0.42914758 | **0.42912369** | 0.42914758 | 0.42916885 | 0.42915691 |
| participation ratio (effective hypotheses) | 3.85363382 | **3.85406274** | 3.85363382 | 3.85325178 | 3.85346624 |
| top-4 posterior mass | 0.85829515 | **0.85824739** | 0.85829515 | 0.85833771 | 0.85831382 |
| var `q*` | 0.06350857 | **0.06350151** | 0.06350857 | 0.06351487 | 0.06351134 |

  So clause 10 **HOLDS as written** and H3 is nonetheless **rejected as the mechanism**: a 0.02 % difference in
  concentration cannot produce a 54 % difference in capability. Stating both is the point.

**The ecology is not what differs at all.** The count of hypotheses whose exact posterior weight lies within a
factor `2^k` of the MAP weight is **identical on all five sequences**: 5 within `2³`, 6 within `2⁴`, **8 within
`2⁵`**, 8 within `2⁶`, 8 within `2⁷`.

### 12a. The mechanism, localized to **one of 256 table entries**

At fx8 the exponent table's entries are `A.const(2^(u/16))` for `u ∈ [−255, 0]`. Exactly **one** of those 256
entries is decided by a **rounding tie**: at `u = −80` the exact value is `16 · 2⁻⁵ = 0.5`, a half-integer.
`A.const`'s half-**up** rule sends it to raw **1** (= 1/16), **doubling** a weight whose true value is 1/32;
half-**down** sends it to **0**. (The tie census is exact: `S·2^(u/S)` is a half-integer only at `u = −80` for
`S = 16`.)

On sequence B, **three** hypotheses of the declared class — indices 8, 12 and 28 — land with max-normalized
log-weight **exactly −80 raw**, i.e. exactly `log₂ w = −5.000`. On A, C, D and E, **none** does. So B carries
**9** non-zero readout weights against **6**, and the three extra carry **3/38 = 7.8947 %** of the readout mass.
They are keyed on the *competing* bit, so the served vector loses the symmetry the obligation has:

| | served at fx8 |
|---|---|
| A, C, E | 0.625, 0.4375, 0.625, 0.4375, 0.4375, 0.625, 0.4375, 0.625 |
| **B** | 0.625, **0.5**, **0.6875**, **0.5**, 0.4375, 0.625, **0.5**, 0.625 |
| `q*` | 0.5891, 0.4109, 0.5891, 0.4109, 0.4109, 0.5891, 0.4109, 0.5891 |

**Proof by intervention — a scalpel, not a rewrite.** Change that **single** table entry from 1 to 0 (half-down
tie-breaking; 1 of 256 entries; arithmetic, constants, events, scoring rule and θ untouched):

| declared sequence | half-up (published) | half-down | non-zero readout weights |
|---|---|---|---|
| ambiguous A | 0.874265 ✓ | 0.874265 ✓ | 6 → 6 |
| **ambiguous B** | **0.400545 ✗** | **0.874245 ✓** | **9 → 6** |
| ambiguous C | 0.874265 ✓ | 0.874265 ✓ | 6 → 6 |
| ambiguous D | 0.910859 ✓ | 0.910859 ✓ | 6 → 6 |
| ambiguous E | 0.874273 ✓ | 0.874273 ✓ | 6 → 6 |
| noisy A | 0.979053 ✓ | 0.980446 ✓ | 9 → 8 |
| noisy B, C, D, E | 0.997887 / 0.999740 / 0.999678 / 0.999736 ✓ | identical | 4 → 4 |

**One** sequence-cell flips, and it is the only failing one. **Nothing** regresses. Ten of ten remain or become
admissible.

**The answer to the question.** The sequence-B failure **is** structural — but the structure is in the
**instrument**, not in the event sequence and not in the ecology. Log-domain updating at 8 bits suffices on this
ecology **exactly when no max-normalized log-weight lands on the exponent table's tie point**; and where that tie
point sits is a property of the table's **rounding rule**, which the log representation does not fix. `RV-377-075`
attributed the split to the event sequence; it is a one-bit rounding decision. That makes the refutation
**stronger** than `RV-377-075` claimed: under a half-down tie-break the 8-bit log row is admissible on **all five**
declared ambiguous sequences, not two of three.

---

## 13. Amended claims, with levels and ceilings

The claims of §8 are **not deleted**. They are re-levelled here, and the new ones are added.

**Claim DK-1 (§8).** *A region of the frontier held only by carriers inadmissible in the registered 8-bit universe.*
**Level: `FALSIFIED_AND_REPLACED`** by `RV-377-075`, upheld as falsified by `RV-377-076` §10. `A8(E_ambig)` is not
empty: it is `{LOGBAYES8}`. The thirteen clauses of `RV-377-066` still hold as written — its ten rows do all score
exactly 0.0 — and the inference from them to a kingdom does not.

**Claim DK-2 (§8, the threshold).** *10 total bits for the domain, 16 for the exact posterior, non-monotone between.*
**Level: `PROVED_AT_SCOPE`, unchanged, but re-scoped** — it is a threshold for the **linear** realizations of D3, not
for the domain. The log-domain realization's threshold on `E_ambig` is **8 total bits**.
**Ceiling:** as §8, plus: a threshold is now a property of the (instrument, **state encoding**) pair.

**Claim DK-3 (§8, the negative half).** *`E_noisy` has an 8-bit parent everywhere.* **Level: unchanged,
`EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY`, and strengthened:** `QCOUNT@fx8` holds 42/42, 243/243, 48/49
and 1 120/1 120 cells of the four **cross-instrument** keys, a frontier this record never computed.

**Claim DK-4 (§8, gap DG-6).** *Every domain criterion must name its arithmetic instrument.* **Level: unchanged,
`PROVED_AT_SCOPE`, and extended by protocol rule 24** — it must also name the **state encoding**.

**Claim DK-5 (new).** *`RV-377-075` is not cheating. Seven attacks — on the table's status as a registered kind and
its charge, on the treatment of the log constants, on the renormalization charge, on the row's actual bit width, on
leakage of the truth, on charged-op identity and on the op counter — leave the 8-bit log row admissible at
**0.874265** at fx8 on `E_ambig` under **every** declared charging regime. Two instrument defects were found in the
refuting row (a data-dependent division charge, an op counter that omits its own table reads) and neither moves a
capability.*
**Level:** `PROVED_AT_SCOPE` for A2 (exact integer recomputation of 8 448 constants and 2 048 table entries) and
`EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY` for A1, A3–A7.
**Ceiling:** the audit tests charging, constants, range, leakage and op identity. It does **not** re-derive the
ecologies, the scoring rule or θ, which are `RV-377-066`'s own and are imported unchanged. No charging finding can
restore a kingdom whose condition is an admissibility condition, and that limit is the audit's, not a defence.

**Claim DK-6 (new, the residual).** ***Precision buys description and execution cost, not capability, on `E_ambig`.***
*At 8 bits the only admissible row costs **3 104** description bits and **208** charged activations per query
(**8 432** at the registered `B0` table charge); two bits more of instrument buy a row costing **596** and **12** —
**5.208054×** the description flat, **4.646707×** scaled, **17.333333×** the per-query charge (**702.666667×** at the
registered charge), **3.780965×** the reuse coefficient. The wider instrument is strictly cheaper at **every** cell of
all four cross-instrument keys (42, 294, 49, 899), and **no** cell requires a wider instrument for admissibility.*
**Level:** `PROVED_AT_SCOPE` for the 0-cell occupancy (cost-coordinate domination by `QCOUNT@fx10`, which is
necessary and sufficient over the whole quadrant); `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY` for the
capabilities the admissible sets rest on.
**Ceiling:** one hypothesis class of 32, one prior, five declared event sequences, one machine seed, two ecologies,
one basis column. The ratios are ratios of *charged* quantities under a declared price and a declared description
basis; they are not a statement about any hardware. And the direction of the purchase is an **ecology** property:
on `E_noisy` precision buys **nothing**, because an 8-bit row holds the joint frontier there.

**Claim DK-7 (new, sequence B).** *The one inadmissible declared sequence fails because of **one of 256 exponent-table
entries** — the unique entry decided by a rounding tie, at `log₂ w = −5` exactly — on which three hypotheses of
sequence B land and none of the other four sequences does. Changing that single entry's tie-break from half-up to
half-down moves B from 0.400545 to 0.874245 and admissible, leaves A, C, D and E bit-identical, and regresses
nothing. The exact posterior has the same shape on all five sequences (8 hypotheses within `2⁵` of the MAP on every
one), so the failure is not a property of the ecology or of the event sequence.*
**Level:** `PROVED_AT_SCOPE` (a one-entry intervention with all else held fixed is a controlled experiment on a
deterministic system).
**Ceiling:** it is a statement about **this** exponent table at **this** instrument. It does not show that half-down
is the *right* rule — half-up is the microscope's own declared rounding — only that the sequence split is carried by
that one decision and not by the evidence.

**Claim DK-8 (new, the correction to `RV-377-075`).** *`RV-377-075`'s registered successor prediction — that further
declared sequences would split as A and C did against B — is **FALSIFIED**. D and E are both admissible, so the split
is 4–1 under the published rule and **5–0** under half-down tie-breaking. Its qualifier "on two of three declared
event sequences" understates its own result.*
**Level:** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY`.
**Ceiling:** five declared sequences on one ecology recipe; the flip schedules are declared, not sampled, so this is
not a claim about a distribution over sequences.

**Replacement terminal:**

```
PRECISION_BUYS_DESCRIPTION_AND_EXECUTION_COST_NOT_CAPABILITY__AT_SCOPE
  __ON_E_ambig_THE_8_BIT_LOG_DOMAIN_ROW_IS_ADMISSIBLE_AT_0_874265_AND_HOLDS_0_OF_42_49_294_899_CROSS_INSTRUMENT_CELLS
  __TWO_EXTRA_BITS_BUY_BACK_2508_DESCRIPTION_BITS_AND_196_CHARGED_ACTIVATIONS_PER_QUERY
  __ON_E_noisy_PRECISION_BUYS_NOTHING__AN_8_BIT_ROW_HOLDS_THE_JOINT_FRONTIER
  __9_OF_11_CLAUSES_HOLD__CLAUSES_2_AND_9_FAIL_AND_ARE_STATED_IN_FULL
```



---

## 14. The residual, re-asked against a **parent-maximal** 8-bit row (`RV-377-077`)

§11 drew a cost conclusion against the row `RV-377-075` built to answer a *capability* question. Protocol rule 19
says a verdict needs a parent-maximal **opponent**; it says nothing about the **subject**, and that was the hole.
The 8-bit log row had never been optimised, so §11's margin was measured against a strawman of itself. Receipt
`STAGE_DK_V6_LOG_MINIMAL_V1.json`, record `RV-377-077`, **7 of 8 clauses HOLD, clause 6 FAILS**.

Three things were wrong with the row's cost, all of them the auditor's to fix:

* **description padding** — `3·K = 96` declared log constants for a class with **seven** distinct likelihood
  values and **three** distinct priors, while the hypothesis → (predicate, value-pair) map is already paid for
  inside `CLASS_STRUCT_BITS`;
* **an accounting asymmetry** — `dk_precision._Mixture` materializes 32 × 16 = **512** probability constants and
  declares `w_scalars = 32`; it charges its constants to `struct`. The log row charged the same kind of constant
  to scalars. Both conventions are reported below and **neither is asserted correct**;
* **a table where a ladder would do** — the 256-entry exponent table spans `log₂` values fx8 cannot hold, zeroes
  everything below `u = −80`, and its output takes only `S + 1 = 17` distinct values. The whole map is fixed by
  **16 monotone breakpoints**: a comparison ladder of `GT` and `ADD` that uses **no store**, and is therefore
  immune to the linear-scan charge protocol rule 25 imposes on a table.

| row at fx8 on `E_ambig` | capability | `desc` | `exec_q` (`sel1`) | `exec_q` (registered `B0`) | declared scalars |
|---|---|---|---|---|---|
| `LOGBAYES8_FIXED` (§10's two defects repaired) | 0.874265 | 3 104 | 208 | 8 432 | 352 |
| `LOGMIN8` (minimal description) | 0.874265 | 2 672 | 208 | — | 298 |
| `LOGTRIM8` (+ trimmed table) | 0.874265 | 1 280 | 208 | 2 800 | 124 |
| **`LOGLAD8`** (+ store-free ladder) | 0.874265 | **752** | 1 168 | **1 168** | 58 |
| `LOGLAD8_T4` (+ top-4 readout) | 0.874265 | 804 | 188 | **188** | 62 |
| **`LOGTRIM8_T4`** | 0.874265 | 1 332 | **68** | 392 | 128 |

**The negative survives, and is now worth something.** On `E_ambig` **no 8-bit row occupies any cross-instrument
cell** — 0 of 288, 0 of 840, 0 of 817, 0 of 3 906 — and every one of the seven 8-bit rows has at least six
cost-coordinate dominators, so it is a theorem over the whole quadrant (rule 27), with the grids independently
past twice the largest crossover per axis. On `E_noisy`, `QCOUNT@fx8` still holds 515/516, 3 605/3 605, 224/224
and 612/612.

**But §11's headline numbers must be restated.** The residual is **not** 5.208054× the description and 17.333333×
the per-query charge. Those were measured against padding. The true figures, at the cheapest encoding of each:

| | `RV-377-076` said | `RV-377-077` measures |
|---|---|---|
| `desc` ratio vs `QCOUNT@fx10` | 5.208054 (3 104 ÷ 596) | **1.261745** (752 ÷ 596) |
| `exec_q` ratio vs `QCOUNT@fx10` | 17.333333 (208 ÷ 12) | **5.666667** (68 ÷ 12) |
| excess description | 2 508 bits | **156 bits** |
| excess charge per query | 196 activations | **56 activations** |

**2 352 of the 2 508-bit gap was padding, an accounting asymmetry, or a table where a ladder would do.** What is
left — 156 bits, 27 declared scalars: 8 log-likelihood constants, 3 log priors, 16 ladder breakpoints — is the
**exponent map**, and that is the whole of the precision residual at this scope. No re-encoding brings it below
`QCOUNT`'s 596, because both rows must carry the same 32-element state and the same 4 readout slots.

### 14a. Clause 6 FAILED — and the failure is the positive

The clause predicted top-M pruning would be capability-neutral at fx8, "because only six hypotheses carry a
non-zero readout weight and the top four carry the mass". **It is not neutral.** On declared sequence B — the one
sequence `RV-377-075` reported inadmissible — the four unpruned rows score 0.400545 and the **two pruned rows
score 0.874245 and are admissible**. That is exactly the value §12a's one-entry tie-break produced, by the same
mechanism: the three hypotheses sitting on the exponent table's rounding tie rank **seventh, eighth and ninth**,
so a top-4 readout drops them. (On `E_noisy`/A pruning costs capability without costing admissibility,
0.979053 → 0.949948.)

So there are now **two independent one-line interventions, sharing no code path**, that each remove the split — a
rounding tie-break, and the top-M pruning `BAYESM` and `QCOUNT` **already carry**. With it, the 8-bit log-domain
row is admissible on **all ten declared sequence-cells**: ambiguous 0.874265 / 0.874245 / 0.874265 / 0.910859 /
0.874273, noisy 0.949948 / 0.997887 / 0.999740 / 0.999678 / 0.999736. `RV-377-075`'s "two of three declared event
sequences" is **five of five**. The split was never a property of the evidence.

The clause failed in the direction that *helps* the row, which is the direction to report hardest — so it is
recorded as a failure and, separately, as the result it bought.

**Claim DK-9 (new).** *The precision residual on `E_ambig` is the **exponent map** and nothing else: 156 excess
description bits and 56 excess charged activations per query, against 2 508 and 196 as measured by `RV-377-076`
against an unoptimised row. No 8-bit row occupies a cross-instrument cell even so.*
**Level:** `PROVED_AT_SCOPE` for the 0-cell occupancy (cost-coordinate domination); `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY` for the capabilities.
**Ceiling:** the ladder's breakpoint count is `S`, so it scales with the instrument's fractional bits and is an
**8-bit-favouring encoding by construction** — stated rather than hidden, and it does not help, since the row
still holds no cell. Two description conventions are reported and neither is asserted correct.

**Claim DK-10 (new).** *`RV-377-075`'s sequence split is gone: with the top-M pruning its own linear opponents
carry, the 8-bit log row is admissible on 10 of 10 declared sequence-cells, and two independent interventions each
suffice.*
**Level:** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY`.
**Ceiling:** five declared flip schedules per ecology, one class, one prior, one seed. Not a claim about a
distribution over sequences.

→ **protocol rule 28** (parent-maximality binds the *subject* of a claim, not only its opponent) and **rule 29**
(a monotone map over a declared constant table must be reported in its **ladder** form as well as its table form).


---

## 15. The residual on a second ecology, built to break it (`RV-377-078`)

§14 reduced the residual to 156 bits and named its mechanism. A residual that small raises a fair objection: every
cell `QCOUNT` holds, it holds because on `E_ambig` and `E_noisy` a hypothesis can be reduced to its **thresholded**
prediction. `QCount.init` sets `expl[j][x] = 1 if p[x] ≥ 1/2 else 0` and counts agreements, discarding magnitude
entirely, and all four value pairs of a predicate share that threshold. So is the residual a *precision* fact, or a
fact about two ecologies that never ask for a calibrated magnitude?

**`E_graded`** removes the forgiveness: same seen set, same 32-member class, same prior, same 24 events and the same
revocation, with two declared changes — value pairs widened to (15/16, 1/16), (3/4, 1/4), (9/16, 7/16), (1/2, 1/2),
and the flip schedule thinned to **one flip in 24**. Receipt `STAGE_DK_V7_GRADED_ECOLOGY_V1.json`, record
`RV-377-078`, **3 of 7 clauses HOLD, 3 FAIL, 1 VOID**.

**The construction is disclosed, not neutral.** `E_graded` was built so that magnitude matters, hence built in a
regime where a thresholding count row must do badly. Protocol rule 19 was discharged by building two graded count
opponents **before** the verdict — `QCOUNT2`, which accumulates the declared likelihood instead of counting
agreements, and `QCOUNT2M` with max-renormalization. **Both scored exactly 0.0 at every instrument.** They are bad
opponents, that is a failed clause of this record, and it is stated here rather than left to be discovered.

### 15a. At 8 bits, only the log-domain row can answer at all

| `E_graded`, sequence A | fx8 | fx10 | fx12 | fx16 | wide |
|---|---|---|---|---|---|
| `QCOUNT` | 0.822415 | **0.735097** | **0.923404** | 0.923404 | 0.923404 |
| `BAYESM` | 0.0 | 0.658658 | **0.987568** | 0.996425 | 0.999843 |
| `BAYES` | 0.0 | 0.0 | 0.0 | **0.967456** | 1.0 |
| `QCOUNT2`, `QCOUNT2M` | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| **log-domain rows** (all six) | **0.898854** | 0.978920 | 0.999843 | — | — |

The fx8 admissible set is **exactly the log-domain rows**, and so is the fx10 set. `E_graded` therefore has a
**wider precision gate for the linear representation than `E_ambig` did — 12 total bits against 10** — while the
log-domain row is admissible at 8 on both.

### 15b. And it changes no occupancy whatsoever

**0 of 288, 0 of 840, 0 of 817, 0 of 3 906.** Every cell is held by `QCOUNT@fx12` or `BAYESM@fx12`. Every one of
the six 8-bit rows carries **at least five cost-coordinate dominators**, so this is a theorem over the whole
quadrant, and the grids independently pass twice the largest crossover in each axis.

> **This is the sharpest form of the residual so far.** Even on an ecology where the 8-bit log row is the *only*
> admissible row at 8 bits **and** at 10 bits, and where the linear rows need 12, the 8-bit row holds **no cell** —
> because two extra bits of instrument are simply cheap under a cost model that charges per scalar **activation**
> and describes every instrument on the same basis.

**Clause 4 was this record's hypothesis and it is falsified.** The residual is not an `E_ambig` property. It is a
property of the registered **cost model**, and the next lever is that model's description basis, not the ecology.

### 15c. Two of the supporting clauses were wrong, and the corrections are worth more than the clauses

* **Clause 2 FAILED.** It argued that `QCOUNT`'s thresholding is an *irrecoverable structural* loss, so no
  precision could rescue it. **Wrong.** `QCOUNT` recovers to **0.923404 at 12 bits** and is **non-monotone in
  precision** — 0.822415 at 8, **0.735097 at 10**, 0.923404 at 12. The argument ignored the **top-M ranking**,
  which reconstructs enough of what the threshold discards once the counts are fine enough to rank correctly.
  `RV-377-066` found non-monotonicity for the exact posterior and called it a property of a quantized mixture; it
  is a property of quantized **ranking**, which is more general. → **protocol rule 31**.
* **Clause 3 FAILED.** It explained `QCOUNT2`'s fx8 failure by quantization of its declared increment. **Wrong** —
  the same row scores 0.0 at `wide`, where nothing quantizes. The real defect is that a **sum** of likelihoods is
  not a **product**: the accumulator over-ranks the extreme value pair and serves ≈ 0.727 where `q*` is 0.608.
  → **protocol rule 30**: an opponent built to discharge rule 19 must be **scored against the ladder** and reported
  as weak if it fails everywhere; the existence of an opponent is not evidence that parent-maximality was met.

**A finding not predicted and not looked for.** On declared sequence **E** of `E_graded` the fx8 admissible set is
**empty** — `LOGLAD8_T4` scores exactly 0.0 — so this ecology carries a sequence-dependence that top-M pruning does
**not** repair, unlike `E_ambig` sequence B. A, B, C and D all give 0.898854/0.898855.

**Claim DK-11 (new).** *An ecology can move a capability gate by two bits and move no occupancy at all. `E_graded`
widens the linear representation's precision gate from 10 total bits to 12 and leaves every frontier cell with a
12-bit occupant. Under the registered cost model, precision is a capability parameter and a small description-cost
parameter, and an occupancy parameter on **no** executed ecology.*
**Level:** `PROVED_AT_SCOPE` for the 0-cell occupancy (cost-coordinate domination in all four keys);
`EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY` for the capabilities.
**Ceiling:** `E_graded` is a **constructed** ecology, disclosed as such, and two of the three opponents built for it
failed everywhere. Three ecologies now, one class of 32, one prior, five declared sequences each, one seed. The six
log-domain rows were executed only at fx8, fx10 and fx12, which does not touch the crux — the crux asks only whether
an **8-bit** row occupies.


### 15d. Where the margin actually is — and the next lever

The number of cost-coordinate dominators is not the verdict, but it is the margin, and it is very different under
the two description bases:

| dominators of `LOGLAD8_T4@fx8` on `E_graded` | flat | **scaled** |
|---|---|---|
| reduced price | 5 | **1** |
| native price | 10 | **2** |

Under the `scaled` basis an 8-bit row pays **8 bits per declared scalar** where a 12-bit row pays **12**. The log
row's irreducible overhead is 27 scalars (§14), and both rows carry the same `K + M` shared state, so the 8-bit row
is cheaper to describe exactly when

```
8·(K + M + 27)  <  12·(K + M)      ⟺      K + M  >  54
```

At the registered class size `K = 32`, `M = 4` that inequality **fails** by 18. It holds from `K = 51` upward. **The
class size has never been varied in this lane.** The `scaled` column was introduced by `RV-377-066` as a sensitivity
check and has agreed with the flat basis on every verdict since; it does not agree on the *margin*, and that is what
makes it the pointer. The successor experiment is therefore not another ecology — it is **class-size scaling under
the scaled basis**, where a fixed 27-scalar overhead is amortized against a state that grows with `K`.


---

## 16. The residual is a **small-class artefact** (`RV-377-079`) — the first positive on this axis

§§11, 14 and 15 established, three times and with increasing force, that **no 8-bit row occupies any
cross-instrument cell** on the ambiguous ecology. All three used the same **32-member** hypothesis class. The class
size is not one of `GMI-DA7`'s four closure parameters, which is exactly why nobody varied it — and the residual's
own mechanism, a **fixed** overhead against a **growing** state, makes it the one parameter the arithmetic says must
matter. Receipt `STAGE_DK_V8_CLASS_SCALING_V1.json`, record `RV-377-079`, **6 of 6 clauses HOLD**.

**The ladder is anchored on the registered ecology, not a lookalike.** The scaling rule puts the eight *registered*
predicates first in their registered order, then balanced truth tables; prior 4/2/2/2/1…; registered `VALS_AMBIG`.
At `n_preds = 8` it reproduces `E_ambig` **exactly**, asserted on seven identity checks — `n_hyps`,
`struct_bits = 288`, priors, likelihoods, events, `q*`, variance.

| | K = 32 | K = 64 | K = 96 | **K = 128** |
|---|---|---|---|---|
| `LOGLAD8_T4` at fx8 | 0.874265 | 0.874211 | 0.874156 | 0.874149 |
| `BAYES`, `BAYESM`, `QCOUNT`, `MAP` at fx8 | **0.0** | **0.0** | **0.0** | **0.0** |
| log `desc` excess over `QCOUNT` | **208** | **208** | **208** | **208** |
| cost-coordinate **dominators** of `LOGLAD8_T4@fx8` | 4 | 1 | 1 | **0** |
| cells held by an 8-bit row, native \| scaled | 0 of 2 760 | 0 of 2 337 | 0 of 2 700 | **7 of 2 760** |
| cells held by an 8-bit row, **flat** (either price) | 0 | 0 | 0 | **0** |

The description excess is a **measured constant, 208 bits at every class size** — the overhead really is fixed and
the state really is what grows. The **dominator count falls 4 → 1 → 1 → 0** monotonically, by the predicted
mechanism: the domination theorem that carried every negative from §11 through §15 is **broken at K = 128**.

**The positive.** At K = 128, under the native price and the `scaled` basis, `LOGLAD8_T4@fx8` occupies
**H = 1…7 at r = 0** — sole occupant of the first six, sharing H = 7 with `QCOUNT@fx10`. It is the **first executed
cell in this lane in which a row admissible in the registered 8-bit universe is the frontier occupant on the
ambiguous ecology.**

### 16a. How narrow it is — stated before it is cited, not after

The 7 cells are **0.25 %** of that key's 2 760, and they need **four permissive choices at once**. Every one was
declared in advance; **none is neutral**:

1. **K = 128** — a class **four times** the registered size;
2. **the native price** — which `RV-377-066`'s own claim ceiling calls *"declared, not measured"*, and which sets
   the log row's `exec_q` to **12, identical to `QCOUNT`'s**, erasing its entire execution disadvantage;
3. **the `scaled` basis** — a sensitivity column; under `flat` the count is **0 at every K**;
4. **r = 0** — the **zero-reuse** corner. All seven cells lie there and **none at r ≥ 1**.

Under `reduced|scaled` at the same K = 128 the count is **0**: `QCOUNT@fx10` costs 2 760 at H = 1, r = 0 against the
log row's 2 880. *A positive that needs a 4× class, an unmeasured price, a sensitivity column and zero reuse is a
positive. It is not a large one, and this document does not present it as one.*

What is **not** narrow is the dominator count: at K = 128 the row has **zero** cost-coordinate dominators under
**both** scaled prices, so under `reduced|scaled` it sits on the frontier's boundary even while holding no cell.

### 16b. The clause that was right for the wrong reason

Clause 2 computed the crossing against `QCOUNT@fx12` and its three signs are **exact** (+240, +112, −16, −144). But
`QCOUNT@fx12` **is not the binding competitor**: `QCOUNT@fx10` is admissible from K = 32 onward and, under the
scaled basis, pays **10** bits per declared scalar rather than 12. It is cheaper at every K and it is what actually
holds the corner. The frozen algebra named the wrong opponent; the true crossing is later than it predicted. Stated
here rather than letting a right answer stand on wrong reasoning.

**Claim DK-12 (new).** *The precision residual on the ambiguous ecology is a **function of hypothesis-class size**
with a computed crossing. Its mechanism is 208 fixed description bits against a state that grows as K; its
cost-coordinate dominator count falls 4, 1, 1, 0 over K = 32, 64, 96, 128; and at K = 128, under the native price
and the scaled basis, it reaches zero and an 8-bit row occupies 7 of 2 760 cells. Claims DK-6, DK-9 and DK-11 are
therefore **scoped to a 32-member class** and `FALSIFIED_AND_REPLACED` beyond it.*
**Level:** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY`; `PROVED_AT_SCOPE` for the zero-dominator statement
at K = 128, which is a property of the affine cost function.
**Ceiling:** one ecology recipe, one declared sequence, one seed, four class sizes, five instruments; the
class-scaling rule is declared, not sampled; the native price is declared, not measured; the occupancy exists under
`scaled` and not under `flat`, and only at r = 0.

→ **protocol rule 32** (a "no cell exists" verdict must name every parameter of the ecology *construction* held
fixed while it was established) and **rule 33** (when the flat and scaled bases **disagree** on a verdict, report
both terminals — a sensitivity column that changes an answer has stopped being a sensitivity column).


---

## 17. It is not a residual — it is a **line**, and its root is K = 188 (`RV-377-080`)

§16's positive needed four permissive choices. Two of them are removable by the very mechanism that produced it,
and this section removes them. Receipt `STAGE_DK_V9_SCALING_HARDENED_V1.json`, record `RV-377-080`,
**6 of 7 clauses HOLD, clause 7 FAILS**.

**The law.** Both rows carry the same `K`-element state and the same `M = 4` readout slots. The log row carries, in
addition, a **fixed 26 declared scalars** — 7 distinct log-likelihood constants, 3 distinct log priors, 16 ladder
breakpoints — measured at **exactly 208 bits across seven class sizes**. Under `scaled` an 8-bit row pays 8 bits per
declared scalar and a 10-bit row pays 10, so at `H = 1, r = 0` against `QCOUNT@fx10`:

```
reduced price (the REGISTERED one):   cost(log@fx8) − cost(QCOUNT@fx10)  =  −2K + 376      root K = 188
native  price:                                                           =  −2K + 208      root K = 104
```

These are **exact, not asymptotic**. Twelve predicted differences — four retrodicted from §16's receipt, eight
predicted here — match the executed values **to the unit**:

| K | 32 | 64 | 96 | 128 | 160 | 192 | 256 |
|---|---|---|---|---|---|---|---|
| reduced, predicted **and measured** | +312 | +248 | +184 | +120 | +56 | **−8** | **−136** |
| `desc` excess (bits) | 208 | 208 | 208 | 208 | 208 | 208 | 208 |

### 17a. The occupancy appears at the law's roots

| K | 128 | 160 | **192** | **256** |
|---|---|---|---|---|
| **reduced** \| scaled — the *registered* price | 0 | 0 | **1** | **1** |
| native \| scaled | 7 | 12 | 16 | **23** |
| largest occupied H | 7 | 15 | 23 | **39** |
| **flat**, either price | 0 | 0 | 0 | **0** |

The native-price sign flips at K = 104, which is why §16 saw nothing at K = 96 and seven cells at K = 128. The
reduced-price sign flips at K = 188 — and the first reduced-price occupancy is at **K = 192, and at no smaller K**.
The occupancy is **monotone** in K and **extends in H** (7 → 15 → 23 → 39). It is a crossing, not a corner.

> **Two of §16's four permissive choices are gone.** The positive no longer needs the **native price** — it exists
> under the registered `reduced` price from K = 192 — and it no longer rests on a **particular class size**, because
> the effect is an exact line verified at seven of them. What remains is the **`scaled` basis** and **r = 0**, and
> naming which two remain is worth more than the cell count.

### 17b. What still qualifies it, and where the next lever is

* **The `scaled` basis.** Under `flat` the count is **zero at all seven class sizes**. The two bases disagree at
  every K, so per **rule 33** neither is elected primary and both terminals stand.
* **r = 0.** Every occupied cell, at every K, under every key, lies at **zero reuse**. The occupancy extends in `H`
  and **never** in `r`, because the log row's reuse coefficient `ρ` exceeds `QCOUNT`'s at every class size — its
  verification phase re-serves the whole evaluation set every event. **That is a property of the row's serve path,
  not of precision,** and it names the next experiment.

**The boundary leads the verdict by 64 hypotheses.** `LOGLAD8_T4@fx8` reaches **zero cost-coordinate dominators** at
K = 128 under `reduced|scaled` while still holding zero cells, and takes its first cell only at K = 192. This is the
second time in this sequence of records that the dominator count moved before the cell count did.

### 17c. Clause 7 FAILED

It predicted exact replication across declared sequences. **Seeds** replicate exactly. **Sequences do not**: at
K = 256 under `native|scaled`, sequences A and C give **23** occupied cells and sequence B gives **21**. The frozen
falsifier says *"any occupancy count differing between sequences A, B and C"*, so the clause fails as written — a
frontier count over a 2 752-cell grid was too strong a thing to predict exactly. What **does** replicate across all
three sequences is the sign, the reduced-price count (1, 1, 1 at K = 256), the K = 128 native count (7, 7, 7) and
every flat zero. Reported as a failure, not rounded into agreement.

**Claim DK-13 (new).** *The precision "residual" on the ambiguous ecology is not a residual. It is an **affine
function of hypothesis-class size**, `−2K + 376` bits under the registered price and the scaled description basis,
exact at seven class sizes, with root `K = 188`; an 8-bit row occupies from `K = 192` under the registered price and
from `K = 128` under the native one. Four records measured it at `K = 32` — one point, on the positive side of its
root — and called it a residual.*
**Level:** `PROVED_AT_SCOPE` for the law and its roots (an identity in the affine cost model, verified at seven
points under two price vectors); `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY` for the occupancy counts.
**Ceiling:** the law holds under the **`scaled`** basis; under `flat` the count is zero at every executed K and no
crossing is claimed. Every occupied cell lies at **r = 0**. One ecology recipe, a declared (not sampled)
class-scaling rule, three declared sequences, two seeds, seven class sizes.

→ **protocol rule 34**: where a cost comparison is **affine in a construction parameter**, fit and report the exact
law and its root — a verdict at one value of a parameter the cost function is linear in is a statement about *that
value*, and the law is the result.
