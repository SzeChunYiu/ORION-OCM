# RV-377-108 — G15 restated under rule-36 **and rule-40** admissibility, with recomputed saturation denominators

Task #27. This record is a **negative** for GMI. It voids a positive claim this
lane made three weeks of work ago and narrows what the whole registered ecology
set can certify. Nothing here is softened.

## 1. Why the restatement was owed

`G15` step (i) — "an intervention-robustly admissible coefficient-carrier witness
exists on a registered ecology" — has been recorded as reached, un-reached, and
reached again:

```
RV-377-082  reached, one intervention (predates rule 36)
RV-377-085  UN-REACHED under the six-intervention family
RV-377-089  UN-REACHED, generalised to "nowhere in the family"
RV-377-089b REACHED -- six rows on E_sym3 clear theta under all six interventions
RV-377-100/101 that reading withdrawn -- E_sym3 non-discriminating
RV-377-102  GENUINELY REACHED on E_wit1
```

Rule 36 (name your intervention set) was applied at `RV-377-089b`. **Rule 40 (report
the best-constant control) was not**, because rule 40 did not exist yet. This record
applies it retrospectively to every registered ecology, as rule 40 requires.

## 2. The constant-control audit, verbatim

`python3 -m gmi_microscope.constant_control`, θ = 0.85, one fx unit = 1/(1.5·16)
= 0.041667 capability.

| ecology | criterion | best constant | c | θ − const | fx units | verdict |
|---|---|---|---|---|---|---|
| `E_parity` | all | 0.8333 | 8 | 0.0167 | 0.401 | **WITHIN_QUANTIZATION** |
| `E_parity` | unseen | 0.8333 | 8 | 0.0167 | 0.401 | **WITHIN_QUANTIZATION** |
| `E_smooth1` | all | 0.7917 | 8 | 0.0583 | 1.399 | DISCRIMINATING |
| `E_smooth1` | unseen | 0.8333 | 8 | 0.0167 | 0.401 | **WITHIN_QUANTIZATION** |
| `E_smooth3` | all | 0.7708 | 6 | 0.0792 | 1.901 | DISCRIMINATING |
| `E_smooth3` | unseen | 0.8125 | 4 | 0.0375 | 0.900 | **WITHIN_QUANTIZATION** |
| `E_sym3` | all | 0.9062 | 6 | −0.0562 | −1.349 | **NON_DISCRIMINATING** |
| `E_sym3` | unseen | 0.8750 | 3 | −0.0250 | −0.600 | **NON_DISCRIMINATING** |
| `E_sym5` | all | 0.8438 | 10 | 0.0062 | 0.149 | **WITHIN_QUANTIZATION** |
| `E_sym5` | unseen | 0.7917 | 5 | 0.0583 | 1.399 | DISCRIMINATING |
| `E_wit1` | all | 0.7500 | −16 | 0.1000 | 2.400 | DISCRIMINATING |
| `E_wit1` | unseen | 0.7083 | −8 | 0.1417 | 3.401 | DISCRIMINATING |

Across the full audit of **42** ecology × criterion pairs:

```
NON_DISCRIMINATING :   9  (21.4%)   best constant already clears theta
WITHIN_QUANTIZATION:   7  (16.7%)   clears by < 1 fx unit -- not a separation
DISCRIMINATING     :  26  (61.9%)
```

**38.1% of every ecology×criterion pair in the registry cannot certify anything.**

## 3. `RV-377-089b`'s G15 claim is not merely unsupported — it is inverted

The six rows `RV-377-089b` presented as intervention-robust witnesses on `E_sym3`,
against that ecology's best constant of 0.9062 (`all` criterion):

| row | min over six interventions | best constant | beats the constant? | deficit |
|---|---|---|---|---|
| `grad_h3_lr3` | 0.8854 | 0.9062 | **no** | −0.499 fx |
| `grad_h3_lr1` | 0.8594 | 0.9062 | **no** | −1.123 fx |
| `grad_h3_lr2` | 0.8594 | 0.9062 | **no** | −1.123 fx |
| `grad_h3_lr8` | 0.8594 | 0.9062 | **no** | −1.123 fx |
| `grad_h1_lr8` | 0.8542 | 0.9062 | **no** | −1.248 fx |
| `grad_h8_lr8` | 0.8542 | 0.9062 | **no** | −1.248 fx |

**Every one of the six is strictly worse than emitting the constant 6.** Not
"within quantization of" — worse, by 0.5 to 1.25 fx units. The ecology is
non-discriminating on both criteria, so clearing θ there was never evidence of
learning; and these particular rows would have failed even a direct comparison
against the null.

> **`RV-377-089b`'s `G15_STEP_ONE_REACHED` on `E_sym3` is VOID.** The claim is
> struck in substance and kept in the corpus, per the standing rule that
> corrections are recorded against the original rather than replacing it.

This is the fourth positive claim this lane has invalidated with a rule it wrote
itself, and the second G15 step-one claim to fall.

## 4. What survives

`RV-377-102`'s witness on `E_wit1` survives rule 40 cleanly:

```
coeffs [-0.5,-0.5,-0.5,-0.25], h=3, lr=1
capability 0.8646 under every one of the six registered interventions
best constant 0.7083  ->  margin 3.751 fx units
```

`E_wit1` is the only registered ecology discriminating on **both** criteria, and by
the largest margin in the registry. **G15 step (i) is reached — on `E_wit1`, and
only there.**

## 5. Recomputed saturation denominators

G15's stopping rule needs `n ≥ ln(⌊1/p_min⌋/δ)/p_min` independent cross-encoding
units, which requires a positive lower bound on `p_min`, which requires trials on
ecologies where the target **has exposure**. Recomputing the denominators under
rule 40:

| quantity | previously recorded | under rule 40 | why it moved |
|---|---|---|---|
| `D1` exposure among the 5 originally-registered ecologies | **1 of 5** (`E_sym3`) | **0 of 5** | `E_sym3` is non-discriminating on both criteria |
| `D1` exposure among all 6 registered (incl. `E_wit1`) | — | **1 of 6** | `E_wit1` only |
| usable ecology×criterion pairs | 42 assumed usable | **26 of 42** | 9 non-discriminating + 7 within quantization |
| `p(D1 | typed IR)` | "estimable for the first time" | **still undefined** | see §6 |
| `p(D2)` | 1.0 | **unchanged**, but its ecology must be re-audited under rule 40 before the value is quotable | not yet audited |
| `p(D4/D5)` | 1/3 | **unchanged**, same caveat | not yet audited |
| cross-encoding units executed | 9 | **9**, of which the `E_sym3` ones are now zero-exposure | exposure recount |

### The denominator problem is worse than a recount

`RV-377-081`'s **0 of 6** and `RV-377-083`'s **0 of 3** were already classed as
zero-exposure because they ran on `E_smooth3` and `E_sym5`. `RV-377-089b` appeared
to fix this by finding exposure on `E_sym3`. With `E_sym3` void, **every
coefficient-carrier recovery trial ever run has been a zero-exposure trial.** Zero
successes over zero-exposure trials bounds nothing, so `p_min` for `D1` has no
positive lower bound and G15's stopping rule remains inapplicable — exactly where
it was before `RV-377-089b`, with the intervening three records now known to have
added nothing.

## 6. `E_wit1` cannot repair the denominator by itself — a selection effect

`E_wit1` was not drawn from the registry; it was **constructed** by `RV-377-102`,
which enumerated all 6561 targets on the registered coefficient grid, found 4720
discriminating, and selected from the first 400 in canonical order the 200 rows
admissible under all six interventions with ≥ 1 fx unit of margin. `E_wit1` is one
of those 200.

An ecology found by searching 6561 candidates *for the property of bearing a
witness* is not an independent trial of whether a witness is discoverable. Using it
as a denominator entry conditions on the outcome. So:

> **`p(D1)` is NOT estimable.** Not "estimable for the first time", as the corpus
> currently reads. The single exposure-bearing ecology is a selected one, and a
> selected success contributes no unbiased rate.

Making `p(D1)` estimable requires trials on ecologies drawn **without reference to
whether a witness exists there** — e.g. a uniform sample from the 4720
discriminating targets, with recovery attempted on each. That experiment does not
yet exist. It is registered here as the next G15 experiment and is NOT claimed.

## 7. Terminal status

| terminal | value |
|---|---|
| `G15_STEP_ONE_REACHED` | **TRUE, at `E_wit1` only**, margin 3.751 fx units |
| `G15_STEP_TWO_REACHED` (recovery by neutral search) | **FALSE** — and now known never to have been tested at non-zero exposure |
| `P_MIN_LOWER_BOUND_EXISTS` | **FALSE** |
| `DOMAIN_LIST_COMPLETE` | **BLOCKED** — unchanged, and for a stronger reason than before |
| `KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE` | **FALSE** |
| `NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE` | **FALSE** |

## 8. New protocol rule

> **Rule 44.** A rule that adds an admissibility control applies **retrospectively
> to every terminal already recorded**, not only to terminals recorded after it.
> Rule 40 was written after `RV-377-089b` and its retrospective application voided
> that record's central claim. Any future control rule must be accompanied by a
> re-audit of the existing corpus before the next positive terminal is recorded.

## 9. Preserved without modification

The original real-transfer V1 failure, every grammar-bias falsification, every
developmental falsification, `RV-377-081`'s 0 of 6, `RV-377-083`'s 0 of 3,
`RV-377-085`'s and `RV-377-089`'s un-reached verdicts, and `RV-377-089b`'s text
(struck in substance, retained in place). No RED result was deleted, weakened or
rewritten by this record.
