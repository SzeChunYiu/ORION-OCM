# Z2 freeze amendment 3 — amendment 2 mis-attributed the inertness, and `H6'`
# gets a revival lever

Committed **before** any receipt, result file or reconciliation of this package
is committed, and before the extended feature alphabet below has been scored.
`source_main`, the claim ceiling and the five reconcilable rows are unchanged;
no neighboring row is earned here.

## 1. Correction to amendment 2

Amendment 2 wrote: *"For most (problem, target) pairs the observation set
already determines the held-out bit"*. That attribution is **wrong**, and it
was wrong at the moment it was written, because the quantity had not been
measured. The repaired executor publishes it: determined pairs are
`3151/16388` of the population, about `19.2` percent, not a majority.

The real mechanism is the one the repair happens to fix anyway. The
full-population feature learner restricted the version space and then took a
**counting majority** over whatever survived. The restriction almost never
changed that majority, so all `208` features — the `8` registered ones and the
`200` nulls — inherited `L_syn`'s score and the spread collapsed. It is the
counting step, not the denominator, that made the instrument inert; removing
the counting step (the preference-only learner `L_f_pure`) is what separates
them, and the undetermined restriction is what makes `1/2` the honest baseline.

Recording this rather than editing amendment 2 is the point: a checker whose
*explanation* is unvalidated is the same defect class as a checker whose output
is unvalidated.

## 2. `H6'` is refuted on the registered alphabet, and gets a revival lever

On the repaired instrument the best registered 1-bit preference beats chance
strictly, but **no** registered feature and **none** of the `200` null features
falls below `1/2`: the "bias can hurt" half of `H6'` has no witness in the
frozen alphabet. Under the standing discipline a one-pass negative is not a
terminal, so the alphabet is extended with a lever aimed at exactly that half,
declared here before it is scored.

`FREEZE_V1.md` §2 is extended with four semantic-rarity features, which are
functions of the candidate alone and never of the held-out moment:

```
B9  the candidate's semantic class is a singleton
B10 the candidate's semantic class is one of maximum size
B11 the candidate's semantic class is larger than the median class size
B12 the candidate's semantic class is smaller than the median class size
```

The hypothesis behind the lever, stated before it runs: `L_syn` scores well
above chance, so preferring **rare** semantic classes should anti-correlate with
the answer the bulk of the version space carries, and `B9`/`B12` are the
candidates for a sub-chance 1-bit preference.

## 3. Exhaustive 1- and 2-literal sweep over `V12`

So that the `H6'` verdict is not an artifact of a hand-picked alphabet, the
executor additionally scores **every** specification over the amendment-1
vocabulary `V12` that uses one or two literals: `24` single-literal features and
`264` two-literal features, `288` in total, each used as the preferred set of a
preference-only learner. The reported quantity is the minimum and maximum
undetermined accuracy over that exhaustive sweep.

Amended hypotheses:

| id | statement | falsifier |
|---|---|---|
| `H6''` | some 1-bit preference in the extended alphabet or the exhaustive `V12` sweep gives undetermined accuracy `< 1/2` | the minimum over all of them is `>= 1/2` |
| `H11` | the best registered or swept 1-bit preference is strictly above `1/2` and strictly above all `200` null features | it is matched or beaten by a null |

If `H6''` is refuted with the lever applied and the sweep exhausted, the
published terminal is the boundary statement *no one-bit structural preference
definable over the registered vocabulary is worse than chance at this scope*,
earned by exhaustion over `288 + 12 + 200` features, and the forbidden
promotion `BIAS_CANNOT_HURT_IN_GENERAL` is added to §11.

## 4. Added forbidden promotion

```
BIAS_CANNOT_HURT_IN_GENERAL
REFERENCE_MEASURE_CHOICE_IS_ALWAYS_DECISION_IRRELEVANT
```

The second is added because the repaired run makes `L_syn` and `L_sem` agree on
every bucket; that is a fact about this universe and this prediction family, and
must not be promoted into a general claim that the choice of reference measure
never matters.
