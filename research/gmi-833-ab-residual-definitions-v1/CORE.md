# CORE — `gmi-833-ab-residual-definitions-v1`

**Issue #833, section AB. Two rows: AB08, AB25.**
Claim ceiling `DECLARED_DEFINITION_ARTIFACT_V1`.

Both are authoring rows. Nothing on `main` subtracted Rice, and no
novelty-ladder level had an operational criterion.

## What it establishes (exact numbers)

| result | statement | number |
|---|---|---|
| RD-1 | Rice's five components subtracted, each with a verdict and a named residual | **5/5** complete; **2 ABSORBED**, **3 PARTIAL**, **0 DIVERGENT**; every ABSORBED residual is literally `None` |
| RD-2 | six ladder levels, each operational | **6/6** carry criterion + falsifier + parent + demotion rule, **6/6** name a witness, criteria pairwise distinct, all demotions strictly downward, chain terminates at level **0** |
| RD-3 | every requirement read off its own row | **18/18** guard checks; **0/200** random bindings reproduce the true one (true **11/11**, max random **7**, exact mean **203/100**) |

Two independent routes agree on every quantity and every row-named list; route
B re-reads the three row strings out of `FREEZE_V1.md` rather than sharing a
constant, and uses no regular expressions. **6/6** hostiles detected, each
moving its own quantity. 90 checks, both modes.

## The AB25 antecedent, declared before anything was written

AB25 reads *"Define a novelty ladder using **those** academically interpretable
levels"* — a back-reference. The six levels are not in its own text, so a
literal-occurrence guard over AB25 is unsatisfiable. The honest move is not to
weaken the guard but to fix its resolution target in advance: `FREEZE_V1.md` §4
names the antecedent row verbatim, before any level existed. A test asserts
both directions — the six levels occur in the antecedent **and** none of them
occurs in AB25 itself, so the exception cannot be quietly widened.

## What this does not establish

No GMI claim is placed on the ladder. No claim of novelty with respect to Rice
is made — three `PARTIAL` verdicts are three places such a claim *could* live,
two of which are already owned by other packages on `main` and the third of
which is stated as a gap with no result behind it. Every citation is `CITE-TF`
and AC05 stays open.

## Reproduce

```sh
python3 -I -B  research/gmi-833-ab-residual-definitions-v1/residual_definitions_v1.py
python3 -I -B  research/gmi-833-ab-residual-definitions-v1/independent_definitions_oracle_v1.py
python3 -I -B  research/gmi-833-ab-residual-definitions-v1/test_residual_definitions_v1.py
python3 -I -O -B research/gmi-833-ab-residual-definitions-v1/test_residual_definitions_v1.py
python3 -I -B  research/gmi-833-ab-residual-definitions-v1/check_receipt_v1.py
```

Stdlib only; every reported quantity is an `int` or an exact `Fraction`.
