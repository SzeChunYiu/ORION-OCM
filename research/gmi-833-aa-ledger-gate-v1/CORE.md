# CORE — `gmi-833-aa-ledger-gate-v1`

**Issue #833, section AA. Five rows: AA02–AA06.**
Claim ceiling `RATCHETED_LEDGER_EMISSION_GATE_V1`.

The four theorem ledgers and the five experiment ledgers were requirements that
nothing enforced and nothing measured. This package makes them decidable,
measures the corpus, and stops the debt growing.

## What it establishes (exact numbers)

| result | statement | number |
|---|---|---|
| LG-1 | corpus state at `source_main`, disclosed not discharged | **0 of 2345** named results in **329** theorem artifacts emit all four ledgers — assumptions **31**, dependency **0**, falsifier **93**, strongest parent **59**; conservative subset **1015/2345**; **6** unparsed artifacts in their own category; **42** vendored copies carrying **310** results |
| LG-2 | exact predicate, two independent parsers, decoy rejected | agreement by **set equality** over **2315** `path::result` keys (route B uses no regex at all); the prose decoy emits **0** and is failed by the gate |
| LG-3 | the gate is blocking and **proven able to fail** | clean fixture exit **0**/0 violations; new-result, regression and decoy fixtures all exit **1**; live repo exit **0** with **17** new results seen and debt unchanged at **2345** |
| LG-4 | AA06's artifact class exists now | **0** experiment ledgers on `main` → **2** authored here, recall **2/2**, all **5** ledgers each; planted theorem recall **9/9** |
| LG-5 | the vocabulary was read off the rows | **9/9** canonical labels occur in their own row text; **0/200** random row bindings satisfy all nine (max **7**, mean **79/25**) |

## The plan item this refuted

The #833 batching plan recorded the two most recent theorem notes on `main` as
"already emitting all four ledgers, so the gate has planted positives". They do
not. `AA_GAP_OBJECT_THEOREMS_V1.md` emits assumptions on 2 of 5 results and a
dependency ledger on none; `AB_TERMINOLOGY_THEOREMS_V1.md` emits assumptions on
1 of 3 and a dependency ledger on none. **Zero** results on `main` are
compliant, so the planted positives had to be authored here — and were declared
as planted in the freeze before they were written.

## Requirement clause vs corpus-state clause

A `Require` row is discharged by a decidable predicate, a blocking gate that
enforces it on everything the repository grows, and the measured corpus state
disclosed as a residual. The debt is **2345** and it is not repaid here. What
changes is that it can now only fall.

## Measurement scope is not enforcement scope

The census counts by the declared over-approximating predicate — right for the
debt number, since it can only overstate. **Enforcement** and the monotone
ratchet bind the conservative `identified` subset (**1015** non-compliant at
baseline). Without that split the gate would fail any lane whose new theorem
note uses `##` for section headings, which is precisely how a gate gets switched
off. Two fixtures hold it: a note with `## Scope` + `## Claim ceiling` + one
compliant `## XY-1` passes; the same note with `## XY-1` non-compliant fails.
Building that fixture is what exposed `claim` and `result` as bad result-word
triggers, and they were removed.

## The failure that made the predecessor gate vacuous

The terminology gate this ratchet pattern comes from ran its checks under
`|| true`. This one is exercised against three deliberately broken fixtures
inside the test module on every CI run, so its ability to fail is re-proved,
not asserted.

## Reproduce

```sh
python3 -I -B  research/gmi-833-aa-ledger-gate-v1/ledger_gate_v1.py
python3 -I -B  research/gmi-833-aa-ledger-gate-v1/ledger_gate_v1.py --null
python3 -I -B  research/gmi-833-aa-ledger-gate-v1/ledger_gate_v1.py --gate
python3 -I -B  research/gmi-833-aa-ledger-gate-v1/independent_ledger_oracle_v1.py
python3 -I -B  research/gmi-833-aa-ledger-gate-v1/test_ledger_gate_v1.py
python3 -I -O -B research/gmi-833-aa-ledger-gate-v1/test_ledger_gate_v1.py
python3 -I -B  research/gmi-833-aa-ledger-gate-v1/check_receipt_v1.py
```

Stdlib only; every reported quantity is an `int` or an exact `Fraction`. 69 checks, both modes.
