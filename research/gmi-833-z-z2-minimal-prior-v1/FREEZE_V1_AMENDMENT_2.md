# Z2 freeze amendment 2 — the learnability instrument was dominated by
# determined cases, and `H7c` is refuted

Committed **before** any receipt, result file or reconciliation of this package
is committed. It records a defect found by running the first draft of Route A
whose output was discarded and never committed, and it records one hypothesis
the enumeration refutes. `source_main`, the claim ceiling and the five
reconcilable rows are unchanged; no neighboring row is earned here.

## 1. The defect: `A_syn`, `A_sem` and every null sat at the same place

`FREEZE_V1.md` §3 scores a learner over **all** `36 x 65552` (problem, target)
pairs. On the first run every learner landed in a band of width under one
percent around `54511/73746`, all `200` null features cleared `1/2`, and `47` of
them matched the best registered feature exactly. `H5` and `H6` both came out
false.

The cause is not the universe and not the features. It is the denominator. For
most (problem, target) pairs the observation set already **determines** the
held-out bit: the version space bucket contains only one held-out value, so
every learner — preference-free, majority, feature-biased, random — is correct
for free. Those pairs carry no information about bias and they are the majority
of the denominator, so they compress every learner toward the same number and
make the null inert in exactly the way `research/gmi-833-z-z5-critical-phenomena-v1`
was caught being inert: the comparison never touched the quantity at issue.

This is the same failure class as the Z7 `C4` tautology. A measurement that
cannot come out differently for a biased and an unbiased learner is not
evidence that bias is unnecessary; it is evidence that the measurement was
taken in the wrong place.

## 2. The repair: measure on the undetermined subpopulation, and use a
## preference-only learner

Two changes, both fixed here before any repaired number is produced.

**(a) The scored subpopulation.** The reported learnability quantities are
computed on the **undetermined** (problem, target) pairs — those whose version
space bucket contains both held-out values. The determined count and the
undetermined count are both published, so the restriction is visible rather
than implicit. On this subpopulation a learner with no preference whatsoever
scores exactly `1/2`, not by convention but because the bucket contains both
answers and nothing in the learner's input distinguishes them.

**(b) A preference-only learner `L_f_pure`.** `FREEZE_V1.md` §2's 1-bit
features were previously applied on top of a counting majority, which is not a
1-bit commitment — counting `65552` hypotheses uniformly is a full measure, not
a bit. `L_f_pure(f)` instead restricts the version space to `{c : f(c) = 0}`
and predicts only if that restriction is **unanimous** on the held-out moment;
otherwise it abstains and is credited exactly `1/2`. That is what one bit of
structural preference, and nothing else, can buy.

The bias ladder reported by the repaired executor is therefore

```
L_free    0 bits, no reference measure   -- exactly 1/2 on the undetermined set
L_f_pure  1 bit of structural preference -- one row per registered feature
L_syn     a uniform measure over the 65552 syntactic candidates
L_sem     a uniform measure over the K semantic classes
```

and the amended hypotheses are

| id | statement | falsifier |
|---|---|---|
| `H5'` | `A_syn` and `A_sem` are compared on the undetermined subpopulation and the number of buckets on which they issue different predictions is published; the hypothesis is that this count is non-zero | the count is `0` |
| `H6'` | on the undetermined subpopulation some registered feature gives `L_f_pure` accuracy `> 1/2` and some gives `< 1/2` | one direction is empty |
| `H10` | on the undetermined subpopulation the `200`-feature null `N2` does **not** place a majority of random features at or above the best registered feature | a majority does |

`H5` and `H6` as written in `FREEZE_V1.md` stand as recorded, and their verdicts
on the full population are published unchanged rather than deleted.

## 3. `H7c` is refuted

`H7c` predicted that at least one of `g_rename`, `g_state`, `g_out` moves the
minimum of `J` or the winning property class on the registered grid — the
expectation being that the global output complement `g_out`, which does not
preserve the task targets, would be the non-admissible generator.

It does not. The universe is closed under output complement, so the **multiset**
of `(e_now, e_delay)` is carried to itself, and `J` is a function of that
multiset alone; the minimum and the winner are therefore fixed. All three
generators leave every aggregate quantity fixed, and the separation the P3/P4
standard needs comes instead from `H7d` (canonical-order first-hit moves under
renaming) and `H7e` (per-candidate class membership moves under the state
relabeling).

The refutation is published, not repaired, and the row-4 statement is weakened
accordingly: the registered generators do not exhibit a non-admissible
re-encoding at this scope, so the standard is stated as *what is invariant*, and
the existence of an inadmissible re-encoding is left explicitly unproven.

## 4. Nothing else changes

The universe, the objective, the semantic definition, the specification
vocabulary, `N1`, `N3`, `N4`, the hostiles and the forbidden promotions stand as
written.
