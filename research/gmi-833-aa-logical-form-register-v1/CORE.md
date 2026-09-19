# CORE — `gmi-833-aa-logical-form-register-v1`

**Issue #833, section AA. Rows AA16, AA17, AA18, AA20, AA22.** Claim ceiling
`LOGICAL_FORM_REGISTER_AND_REVIEW_QUEUE_V1`.

The census registration pass found 13 AA rows undecidable because **no
register carries the statement's logical form**. This package adds that
register — a quantifier prefix, a small implicational matrix with atom
relation classes, necessary/sufficient roles and a scope — on the census's
own named-result population, plus a **warrant** column read from bytes
outside the statement, and runs the five rows' discriminators as metadata
predicates over the two columns. Every predicate emits a review queue, never
a verdict.

## Coverage (the first thing to read)

| | count |
|---|---|
| population (frozen rule, census enumeration) | **391** = 346 heading + 45 bold-led; 266 mention lines listed, not registered |
| registered by the frozen grammar (R1–R9) | **271** |
| registered by hand (seed 833, 40 drawn, 2 refused with reasons) | **38** |
| `FORM_UNAVAILABLE` | **82** (79 `NO_GRAMMAR_RULE`, 1 empty, 2 hand-refused) |
| **coverage** | **`309/391`** — nothing is claimed past it |
| warrant column | 115 proof blocks; 20 hand warrants (seed 834) + 3 AA16-applicable (1 refused `NO_WARRANT_BYTES`) |

## Rows (exact, over the registered set)

| row | applicable | evaluable | queue | hostiles | own null (reach/200) |
|---|---|---|---|---|---|
| AA16 quantifier order | 5 | 4 | **0** | swap 4/4, warrant flip 4/4 | 0 |
| AA17 converse/inverse | 95 | 11 | **0** | converse 11/11, inverse 11/11 | 0 |
| AA18 necessity/sufficiency | 57 | 10 | **1** (`DL-3`, real-data recall 1/1) | iff-promotion 12/12, role swap 12/12 | 0 |
| AA20 optimality vs run search | 34 | 31 | **0** | evidence flip 31/31, atom flip 2/2 | 25 (not beaten, disclosed) |
| AA22 correlation/causal | 5 | 5 | **0** | evidence flip 5/5 | 72 (not beaten, disclosed) |

Pooled null: true agreement **60**, shuffled max **38**, mean `6633/200`,
**0/200** reach. No-alarm: **57** hand-verified clean objects, **0** alarms.
Loosening (warrant conjunct dropped, measured only): 5/95/57/34/5 queued vs
the true 0/0/1/0/0. Two routes — route B a regex-free scanner importing
nothing from A — agree on **391/391** forms and every queue by set equality.

## What the validation found and discarded

A first-sentence lexical alignment of the proof with the statement's sides
raised **6/6 false converse alarms** on real proofs (AM-1, ER-2, KF-16.1,
NR-3, TC-1, ID-2); a naive proof-first quantifier cue called KF-4 a swap; a
label-anchored hand warrant made the swap hostiles vacuous (0/15, 0/16);
`requires <MATH> bits` parsed as a necessity. Each is repaired and disclosed
in `FREEZE_AMENDMENT_01.md`, committed before the receipt.

## Not earned here

AA23, AA28, AA29, AA30, AA32, AA34, AA35, AA36 need **experiment metadata**
(identifiability, equivariance outcome, objective form, search budget,
ecology sample, leakage ledger, sample size, latent structure) that a
logical-form register does not carry; the lever is an experiment-ledger
register beside this one.

## Reproduce

```sh
python3 -I -B  research/gmi-833-aa-logical-form-register-v1/logical_form_register_v1.py
python3 -I -B  research/gmi-833-aa-logical-form-register-v1/independent_form_oracle_v1.py
python3 -I -B  research/gmi-833-aa-logical-form-register-v1/test_logical_form_register_v1.py
python3 -I -O -B research/gmi-833-aa-logical-form-register-v1/test_logical_form_register_v1.py
python3 -I -B  research/gmi-833-aa-logical-form-register-v1/check_receipt_v1.py
```

Stdlib only; Python 3.8+; every quantity an `int` or exact `Fraction`. Route
A re-reads the 114 pinned blobs through `git cat-file`, rewrites
`STATEMENT_SNAPSHOT_V1.json`, `LOGICAL_FORM_REGISTER_V1.json` and
`QUEUES_V1.json` byte-identically (CI asserts a clean diff) and degrades to
`BLOBS_UNREACHABLE` — never a pass — when git is absent.

## Files

| file | what |
|---|---|
| `FREEZE_V1.md` | pre-implementation freeze, committed alone first: population rule, grammar, warrant, discriminators, hostiles, null, closure rule |
| `FREEZE_AMENDMENT_01.md` | disclosed refinements found on real data, committed before the receipt |
| `AA_LOGICAL_FORM_REGISTER_THEOREMS_V1.md` | LF-1..LF-7 with all ledgers |
| `logical_form_register_v1.py` / `independent_form_oracle_v1.py` | routes A / B |
| `test_logical_form_register_v1.py` | 30 tests, both modes |
| `check_receipt_v1.py` | builds / verifies `RESULT_V1.json` by equality |
| `STATEMENT_SNAPSHOT_V1.json` | statement / proof / falsifier bytes per object, blob-pinned |
| `LOGICAL_FORM_REGISTER_V1.json` | the register: form + warrant per object |
| `QUEUES_V1.json` | the five review queues with evaluable / applicable sets |
| `HAND_REGISTER_V1.json` | 40 hand forms + 21 hand warrants with reader verdicts |
| `MANIFEST_V1.json`, `ISSUE_833_RECONCILIATION_LOGICAL_FORM_V1.json` | pins; five reconciliation lines |
