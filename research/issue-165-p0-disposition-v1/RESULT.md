# What this disposition recorded

Six exact controls passed (`python -m pytest -q research/issue-165-p0-disposition-v1`).
The linear parent uses `fractions.Fraction` only.

## Linear cache-admission / ski-rental (executed here)

Registered instance: rent `10`, buy `30`, hit `1`, savings `9`, `H_max = 24`.

| Quantity | Value |
|---|---|
| Known-H admit | `H >= 4` at density 1 |
| Density `1/2` break-even | `H >= 7` |
| Density `0` | never admit |
| Deterministic buy request | 4 |
| Max competitive ratio | `61/34` `<= 2` |
| Cache-admission `==` ski-rental | true on `H = 1..24` |
| ML residual | false |

Reuse density is an exact scale on remaining uses: admit iff
`rho * H * (rent - hit) > buy`. Zero density is the incumbent uncached arm.

## Nonlinear ADAPT witness (toy table, not the 142-target donor)

Semantic costs `{22,24,27,31,36}` are not affine in `H`, while inverse `10H` is.
Clairvoyant semantic already wins from `H = 3`, but the exact one-way minimax
parent on `H in {1..5}` stays inverse (`tau* = 5`, ratio `25/18`).
A forced linear fit through the first two semantic points switches at `tau = 2`
and pays `14/9`. The 2-competitive ski-rental guarantee is therefore not
imported onto a nonlinear frontier. That is the qualification
`research/metareasoning-parent-review-v1` asked for.

PR154 already supplies the stronger exact threshold / randomized switch parents
on the real donor. This capsule does not rerun that ecology.

## #71

```text
LEARNED_ROUTER_NOT_YET_AUTHORIZED
```

No `STRATEGY_SELECTION_RESIDUAL_CONFIRMED`. The only new exact parent here is
linear and sufficient for its model. Remaining G4 boxes wait on unmerged
PR154 / PR158 / PR161 / PR163 plus the unmerged compose R0 branch.

[Qualification receipt](QUALIFICATION.json). [Checkbox map](CHECKLIST.json).
