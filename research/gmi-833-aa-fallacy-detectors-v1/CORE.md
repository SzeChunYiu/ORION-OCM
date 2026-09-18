# CORE — `gmi-833-aa-fallacy-detectors-v1`

**Issue #833, section AA. Three of the 22 fallacy rows: AA19, AA31, AA37.**
Claim ceiling `VALIDATED_REVIEW_QUEUE_DETECTOR_V1`.

Each detector emits a **review queue**, never a verdict. A queued object is a
requirement to look; an unqueued object is not thereby correct.

## What it establishes (exact numbers)

| result | statement | number |
|---|---|---|
| FD-1 | **AA19** — universal claim, warranted by a search that was run | queue **60 records / 57 ids / 37 files** over **22553** objects; recall **6/6**; **0 alarms on 21548 real clean objects** (331 universal-with-analytic-warrant, 21217 non-universal); overlap with AA21's `FIN2UNIV` **1** |
| FD-2 | **AA31** — same-semantics grammar pair, exact rational divergence | the parent's whole **24**-member isometric family raises **0** alarms; its registered non-isometric pair is queued with **10** divergent cells in **2 of 3** semantic classes; `1/3` vs `333333/1000000` diverges, `2/6` vs `1/3` does not |
| FD-3 | **AA37** — new-form claim with no parent-reduction ledger | **19** trigger, **9** identified, **6** cleared, **3** queued; **2347** real non-triggering results raise nothing; this tranche's own notes are a live cleared negative (**2** trigger, **0** queued) |
| FD-4 | every text variant is measured, never used to queue | AA19 text variant **+14** (60 → 74); AA37 bare grep **236** vs tier 1's **9**, inflation **227**; **7/7** hostiles move their own quantity; null **0/200**, max overlap **2/57**, exact mean **2607/40** |

Two independent routes agree on **every queue by set equality**. Route B never
executes the grammar parent — it re-derives AA31 from the parent's **committed
receipt** — and uses no regular expression anywhere. 96 checks, both modes.

## Why these three, and why not the other 19

The rows were chosen by **available discriminator**, not by convenience. The
registered corpus turns out to populate almost nothing: `assumptions`,
`falsifiers`, `forbidden_extrapolations`, `strongest_parents` and
`claim_dependencies` are empty on **all 22553** objects, and `evidence_level`
and `maturity_level` are `UNKNOWN` on all of them. What remains is
`object_class`, `quantifier_class`, `proof_evidence_mode` and the statement
text. AA19 is decidable from the first three. AA31 is decidable from a frozen
parent's exact rational data. AA37 is decidable from the ledger predicate this
tranche installed. The other 19 fallacy rows are not decidable from anything
registered on `main`, and guessing them from prose would build the
false-positive generator this package measures rather than commits.

## The number that says what a detector is not

Every text-trigger variant is run once and published as an inflation figure.
For AA37 the bare `novel`/`new`/`first` grep triggers **233** identified results
where tier 1 triggers **8**. That is the measured cost of a loose trigger, and
it is why tier 2 never queues anything.

## Reproduce

```sh
python3 -I -B  research/gmi-833-aa-fallacy-detectors-v1/fallacy_detectors_v1.py
python3 -I -B  research/gmi-833-aa-fallacy-detectors-v1/independent_detector_oracle_v1.py
python3 -I -B  research/gmi-833-aa-fallacy-detectors-v1/test_fallacy_detectors_v1.py
python3 -I -O -B research/gmi-833-aa-fallacy-detectors-v1/test_fallacy_detectors_v1.py
python3 -I -B  research/gmi-833-aa-fallacy-detectors-v1/check_receipt_v1.py
```

Stdlib only; every reported quantity is an `int` or an exact `Fraction`, and the
test walks the whole receipt and fails on any float.
