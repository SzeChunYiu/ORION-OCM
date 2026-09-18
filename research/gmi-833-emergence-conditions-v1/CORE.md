# Emergence by price — and what actually decides it (START HERE)

Two `#833` rows ask whether a list of capabilities can be shown to **emerge** from a substrate
rather than being named as primitives. This tranche builds one neutral substrate, defines all
thirteen capabilities as predicates on the observable trace, enumerates every program
exhaustively, and decides each one.

The headline is a corrected expectation. The mechanism this package was built to test — that a
resource account makes the behaviour the cheaper option — is **empty at this scope**. What
decides instead is whether the substrate can express the behaviour at all and whether the task
admits a cover that avoids it.

## Headline numbers (exact integer arithmetic throughout; no float enters any claim)

| quantity | value |
|---|---|
| programs enumerated per family at `L = 5` | `813,615` |
| programs meeting a requirement, all thirteen families | `24,326` |
| verdict histogram | `FORCED_BY_REQUIREMENT` 7 · `NOT_EXPRESSIBLE` 4 · `DOES_NOT_EMERGE` 2 · **`EMERGES_BY_PRICE` 0** |
| price-sensitive behaviours, over the sweep `p_obs in {1..6}` and both accountings | `0` |
| `METAREASONING` | forced: `132 / 132` conforming programs, `c*_M = 4`, `0` blind covers |
| `ENDOGENOUS_EXPERIMENT_CHOICE` | forced: `1,648 / 1,648`, `c*_M = 3`, `0` blind covers |
| `DOES_NOT_EMERGE` margins | reusable-operator acquisition `-2`, symbolic rewriting `-1` |
| frozen requirements that entail their own predicate | `5 / 13`, disclosed with their stripped verdicts |
| trace groups whose predicate value splits (extensionality) | `0` |
| route A / route B disagreements | `0` |

## The four things worth knowing

**The two boundaries nobody had covered are forced, not named.** `METAREASONING` and
`ENDOGENOUS_EXPERIMENT_CHOICE` are the two the `#833` structural map records as having no
coverage anywhere in the merged corpus. On a substrate whose fifteen operations contain no
behaviour word, every single conforming program exhibits them, and no blind cover exists. That
is emergence in its strongest form: not cheaper, unavoidable.

**Price decides nothing here.** `EMERGES_BY_PRICE` occurs zero times, unchanged under the
frozen worst-case accounting, under a summed accounting, and at every observation price in the
sweep. The reason is structural: all thirteen predicates are difference-making properties, and
such a property is either demanded by the family's input-to-output specification — in which
case no conforming program avoids it and the margin is infinite rather than finite — or not
needed, in which case a behaviour-free program is strictly cheaper because the substrate's
constant initial state is free. Because of this, `EC-3`, the flat-pricing control, has nothing
to act on: its gate passes **vacuously** and the receipt says so in `ec3_exercised: false`.

**Five of the thirteen frozen requirements contain their own answer.** The freeze's own wording
puts a behaviour clause inside the requirement for `HISTORY_SENSITIVE_DEVELOPMENT`, `MEMORY`,
`LEARNING_LAWS`, `PROBABILISTIC_STATE` and `SELF_MODIFICATION`. Re-running each with the clause
removed flips the first three to `DOES_NOT_EMERGE` at a margin of `-1`. This is published, and
it is why the headline is stated only over the four families whose requirement is a plain
input-to-output specification.

**"Not a primitive macro" is checked, not promised.** Every predicate is a function of the
registered trace alone. The solving programs are grouped by trace signature and the predicate
must be constant on each group: `0` split groups across all thirteen. A planted predicate that
reads the program's first operation splits `4` groups immediately.

## What the substrate cannot host, and what one operation restores

`PROBABILISTIC_STATE` (`0` conforming programs — the substrate is deterministic) and
`SELF_MODIFICATION` (`0` — the instruction store is immutable) are recovered on the two
extensions declared in the freeze, each adding exactly one generic operation: `35` and `311`
conforming programs, both `FORCED_BY_REQUIREMENT`. `SEARCH` is `NOT_EXPRESSIBLE` with a named
obstruction — the only backward jump returns to instruction `0`, which re-runs the input read,
so a one-symbol instance cannot carry a test-then-revise cycle — and becomes expressible at
`c*_M = 7` once the instance is three symbols long. `CAPABILITY_FRONTIER_EXPANSION`'s frozen
predicate cannot hold of any member of its own solution set; the freeze's wording is followed
rather than repaired, and a probe set larger than the family gives the behaviour a second,
independent negative at `0 / 882`.

## Evidence

- **2 materially independent routes**, route B importing neither route A nor any parent: a
  different interpreter, a descending odometer enumeration with no static prefilter, costs from
  the executed opcode stream, minima by full sort. **0 disagreements** on verdict, margin, both
  minimum costs, conforming-program count and blind-cover count, for all thirteen behaviours
  and both revivals.
- **5 hostiles, all detected, each with a control proving it moves its quantity**: a predicate
  reading the program text (`0 -> 4` split groups); an operation named after a behaviour
  (`0 -> 2` collisions); an enumeration missing every cost-minimal program
  (`24,326 -> 23,518`); an unsound static prefilter (`24,326 -> 4,014`); a requirement that
  stops checking termination (`24,326 -> 25,980`).
- **One perturbation recorded as INAPPLICABLE and not shipped**: charging cost per written
  instruction moves no verdict at this scope, so it would be a test of nothing.
- **The prefilter validator earned its place before any hostile ran**: it caught a genuinely
  unsound filter in this package's own first draft.
- **Nulls.** `0 / 200` random price vectors and `0 / 200` random trace-keyed predicates
  reproduce the published verdicts, margins and both exact minimum costs.
- **No-alarm case asserted** on the true configuration.

## A known conflict, recorded rather than resolved

`FREEZE_V1.md` quotes the AG7 row byte-exactly, as the closure standard requires. That row
contains a term the repo-wide AB terminology ratchet bans in new markdown. Paraphrasing would
break custody and editing a freeze after the fact is the very defect class an earlier audit had
to correct. The quotation stands; the conflict is recorded in `KNOWN_CONFLICT_V1.json` with the
fix that belongs to the AB lane, not to this one. Every other file here is clean.

## Reproduce

```
python3 -I -B  research/gmi-833-emergence-conditions-v1/emergence_conditions_v1.py
python3 -I -B  research/gmi-833-emergence-conditions-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-emergence-conditions-v1/test_emergence_v1.py
```

Route A takes about 1 min 15 s, route B about 36 s, the tests under 30 s. Stdlib only.

## Files

`FREEZE_V1.md` (committed before any code, commit `967500f8`) ·
`EMERGENCE_THEOREMS_V1.md` (`EC-1` … `EM-7`) · `PARENT_LEDGER.md` · `KNOWN_CONFLICT_V1.json` ·
`RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` · `MANIFEST_V1.json`.
