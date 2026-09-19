# Z7 freeze amendment 1 — an arithmetic slip in the frozen grid size, and a
# mis-scoped aggregation

Committed **before** the receipt. `git log` must show this file added no later
than `RESULT_V1.json`.

## 1. The frozen grid has `7680` cells, not `19200`

`FREEZE_V1.md` lists the region-`R2` grid as

```
p (5) x eta (3) x lambda (4) x a_now (4) x a_delay (4) x C (4) x b (2)
```

and then states a cell count of `19200`. The product is
`5*3*4*4*4*4*2 = 7680`. The stated total was an arithmetic slip by the author.

**The grid itself is unchanged.** Every axis and every value in it is exactly as
frozen; only the derived count was wrong, and the executor computes it rather
than reading it from the freeze. The receipt reports `cells = 7680`, and the test
gates on `cells == feasible + infeasible` rather than on any number written in
prose.

This is recorded rather than silently corrected because a freeze is a committed
artifact: a number in it that the run contradicts must be visible in the record,
even when — as here — it changes no result.

## 2. `targets_infeasible_at_every_world` was aggregated across budgets

The freeze asks for *the exact set of `(a_now, a_delay)` targets that are
infeasible at every `(p, eta, lambda, C)` in the grid*. The first implementation
aggregated that set across both state budgets `b`, which makes it vacuous: a
target impossible at `b = 0` is generally reachable at `b = 1`, so the
budget-blind set is empty and the quantity reports nothing.

Since the whole subsection is about **resource-dependent** impossibility, the
aggregation is now per budget: the receipt reports
`targets_infeasible_at_every_world_by_budget`, a list of `(b, a_now, a_delay)`
triples. The budget is part of the constraint, not something to average over.

## Nothing else in the freeze changes

The claim ceiling, the rows, the hypotheses `Q1`–`Q5` with their
`[DERIVED-AT-FREEZE]` / `[UNCOMPUTED]` / `[NAIVE]` labels, the ceilings `C1`–`C6`,
the families, the null, the hostiles and the forbidden promotions are unchanged.
