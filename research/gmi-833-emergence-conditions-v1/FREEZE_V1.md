# FREEZE — `gmi-833-emergence-conditions-v1`

Committed **before** any executor, oracle, test, receipt or workflow file of this package.
Nothing below may be edited after the first implementation commit; a later correction must
arrive as a new file that cites this one.

## Custody

| field | value |
|---|---|
| `source_main` | `50f833cc4bc3cadcefd44eca14fa58f73f815587` |
| issue | `SzeChunYiu/ORION-OCM#833` |
| sections | AG7 (one row), AH3 (one row) |
| comments | `5693520829` (AG7), `5693590252` (AH3) |
| claim ceiling | `EMERGENCE_BY_PRICE_CONDITION_DERIVED_AND_THIRTEEN_BOUNDARIES_TESTED_AT_REGISTERED_FINITE_SCOPE` |

## The exact rows this tranche may reconcile

Byte-exact. No other row of any section is in scope.

Anchor `### AG7 — Intelligence should emerge above common non-intelligent substrate`:

```
- [ ] Test candidate boundaries: adaptation, history-sensitive development, acquisition of reusable distinctions/operators, metareasoning, endogenous experiment/search selection, and capability-frontier expansion.
```

Anchor `### AH3 — “MI atoms” must satisfy stronger criteria than Turing universality`:

```
- [ ] Test whether candidate atoms support emergence of memory, routing, search, probabilistic state, symbolic rewriting, learning laws and self-modification without those appearing as primitive macros.
```

**No neighboring row is earned here.** In particular this tranche does not touch AG7's four
already-checked rows, AH3's already-checked row, AG6 rows 34-36 and 38, AG8 row 48, AH4 rows
63-66, or any other row of any section.

**Known structural conflict, recorded rather than resolved.** The repo-wide AB terminology
ratchet bans the bare word that appears in the AG7 row quoted above. The #833 closure standard
requires this freeze to quote the row byte-exactly, and a freeze may not be edited after the
fact. The quotation therefore stands and the ratchet will register a new site in this file.
That is a conflict between two live contracts, not a defect in either, and it is recorded in
`KNOWN_CONFLICT_V1.json` rather than papered over by paraphrase or by a post-hoc freeze edit.
Every other file of this package uses this package's own predicate names and is clean.

## 1. The substrate, fixed before any run

`B0` is a bounded machine whose operation names are drawn from generic computation and name
none of the thirteen target behaviours. Two value cells `c0`, `c1` over `V = {0,1,2}`; an input
stream; an output list; a program counter.

```text
OBS0 / OBS1      read the next input symbol into c0 / c1 (underflow -> stall, no write)
INC0 / INC1      c := (c + 1) mod 3
DEC0 / DEC1      c := (c - 1) mod 3
CPY01 / CPY10    copy one cell into the other
EMIT0 / EMIT1    append a cell to the output
SKZ0 / SKZ1      if the cell is zero, skip the next instruction
BNZ0 / BNZ1      if the cell is not zero, jump to instruction 0
HLT              stop
```

Fifteen operations. A program is a tuple of at most `L` operations, executed from index `0`
under a step budget `S`; running off the end halts. No operation reads or writes the program
itself, so `B0` has an immutable instruction store by construction; no operation is stochastic.

Two declared extensions, each introduced ONLY as the revival substrate for a behaviour that
`B0` structurally cannot host, and each adding exactly one generic operation:

- `B0R` = `B0` + `RND0` (write an entropy-stream symbol into `c0`). The entropy stream is an
  externally registered input, not an internal architecture.
- `B0W` = `B0` + `WRT` (write `c0` into the instruction store at the index held in `c1`,
  re-encoding it as the operation with that index in the fixed operation list). The store
  becomes ordinary addressable state; nothing is called self-modification.

## 2. Prices, fixed before any run

`price(op) = 1` for every operation except `HLT`, which is `0`, and `OBS0`/`OBS1`/`RND0`, whose
price is the declared parameter `p_obs`. Cost of a program is **dynamic**: the sum of the prices
of the operations actually executed, taken as the **maximum over the task instances** of the
family (a worst-case accounting, so no instance distribution has to be invented). Ties in cost
are broken by nothing: a tie means the behaviour is not forced.

`p_obs = 1` is the registered default. The `p_obs` sweep `{1, 2, 3, 4, 5, 6}` is run for every
experiment so that the price at which a verdict flips is reported rather than assumed.

## 3. The emergence condition, stated before any run

Let `M` be an **extensional predicate**: a function of a program's registered observable trace
only — the sequence of observation, emission, branch-outcome and halt events, with the cell
values they carried. A predicate may not read the program text. This is the formalization of
the AH3 row's "without those appearing as primitive macros": a predicate that could read the
text could be satisfied by naming.

For a substrate `B`, prices `p`, a task family `T` with an exact requirement `R`, and a length
bound `L`:

```text
Sol       = { programs of B of length <= L that satisfy R on every instance of T }
cost(P)   = max over instances of the sum of prices of the executed operations
c*_M      = min { cost(P) : P in Sol,  M holds of P }          (+infinity if none)
c*_notM   = min { cost(P) : P in Sol,  M fails of P }          (+infinity if none)
Delta     = c*_notM - c*_M
```

**`EC-1`.** `M` is **forced** by `(B, p, T, L)` exactly when every minimum-cost member of `Sol`
satisfies `M`, which holds exactly when `Delta > 0`.

**`EC-2`.** `Delta` is a property of `(B, p, T)` alone and involves no naming: it is the
difference between the cheapest program that resolves the family's instance distinction and the
cheapest program that covers the family without resolving it.

**`EC-3`.** Under a flat accounting — every member of `Sol` assigned the same cost — the
minimum-cost set is all of `Sol`, so `M` is forced only if `c*_notM` is infinite. Any behaviour
whose emergence disappears under flat pricing was produced by the accounting, not by the
vocabulary. This is the control every positive verdict must pass.

**Verdict vocabulary** (fixed here; no verdict may be invented later):

- `EMERGES_BY_PRICE` — `c*_M` and `c*_notM` both finite and `Delta > 0`.
- `FORCED_BY_REQUIREMENT` — `c*_M` finite, `c*_notM` infinite: no conforming program avoids the
  behaviour at all, so price is not what decides it.
- `DOES_NOT_EMERGE` — `c*_M` finite and `Delta <= 0`.
- `NOT_EXPRESSIBLE` — `c*_M` infinite: the substrate cannot host the behaviour at this scope.
  A `NOT_EXPRESSIBLE` verdict on `B0` obliges a revival run on the declared extension for that
  behaviour, and the revival verdict is published beside it.

## 4. The thirteen behaviours, defined extensionally before any run

Six from the AG7 row, seven from the AH3 row. Each is a predicate on the trace.

| id | from | predicate on the registered trace |
|---|---|---|
| `ADAPTATION` | AG7 | two instances whose observation sequences differ produce different emission sequences |
| `HISTORY_SENSITIVE_DEVELOPMENT` | AG7 | an emission differs across two instances because of an observation made at least two events earlier, with at least one intervening event |
| `REUSABLE_OPERATOR_ACQUISITION` | AG7 | one contiguous block of at least two trace events occurs at two disjoint positions of the same trace, and deleting either occurrence breaks the requirement |
| `METAREASONING` | AG7 | a branch event whose two outcomes lead to executed suffixes of different cost, and the cheaper suffix is taken exactly on the instances where it still meets the requirement |
| `ENDOGENOUS_EXPERIMENT_CHOICE` | AG7 | an observation event whose observed value is never emitted, and whose value changes the remainder of the trace |
| `CAPABILITY_FRONTIER_EXPANSION` | AG7 | the set of family instances met from the state reached after some prefix strictly contains the set met from the initial state |
| `MEMORY` | AH3 | a value observed at event `t` determines an emission at event `t' > t` with at least one observation event strictly between them |
| `ROUTING` | AH3 | a branch event both of whose outcomes occur across the family and whose two arms emit different sequences |
| `SEARCH` | AH3 | a repeated test-then-revise cycle -- at least two branch events on the same cell separated by a write to that cell -- whose repetition count differs across instances |
| `PROBABILISTIC_STATE` | AH3 | the emission sequence on one fixed instance is not constant across runs |
| `SYMBOLIC_REWRITING` | AH3 | the emission sequence is the image of the observation sequence under one position-independent map applied at two or more positions |
| `LEARNING_LAWS` | AH3 | within a single run over a presented sequence of instances, the cost spent on the `k`-th instance is strictly below the cost spent on the first, and stays below for every later instance |
| `SELF_MODIFICATION` | AH3 | an operation of the program is altered during the run and the altered operation is afterwards executed |

`METAREASONING` and `ENDOGENOUS_EXPERIMENT_CHOICE` are the two the structural map records as
having no coverage anywhere in the merged corpus; they are the ones this package is built
around, and the other eleven are run through the same engine so that neither row is closed on
partial coverage.

## 5. The task families, fixed before any run

Each behaviour gets one registered family; each family states its instances, its requirement,
its length bound `L` and its step budget `S`. Instances are input words over `{0,1,2}`.

| behaviour | instances | requirement | `L` | `S` |
|---|---|---|---|---|
| `ADAPTATION` | `(0,)`, `(1,)` | emit the observed symbol | 4 | 12 |
| `HISTORY_SENSITIVE_DEVELOPMENT` | `(0,0)`, `(1,0)` | emit the FIRST symbol after both are observed | 5 | 16 |
| `REUSABLE_OPERATOR_ACQUISITION` | `(1,1)` | emit `2` then `2` | 5 | 16 |
| `METAREASONING` | `(0,0)`, `(1,0)` | emit `0` on the first instance and `2` on the second | 5 | 16 |
| `ENDOGENOUS_EXPERIMENT_CHOICE` | `(0,1)`, `(1,1)` | emit `1` on the first instance and `2` on the second, never emitting the first symbol | 5 | 16 |
| `CAPABILITY_FRONTIER_EXPANSION` | `(0,)`, `(1,)` | emit the observed symbol | 4 | 12 |
| `MEMORY` | `(1,0)`, `(2,0)` | emit the first symbol after the second has been observed | 5 | 16 |
| `ROUTING` | `(0,)`, `(1,)` | emit `0` once on the first instance and `1` twice on the second | 5 | 16 |
| `SEARCH` | `(1,)`, `(2,)` | emit `0` after decrementing the observed value to zero | 5 | 16 |
| `PROBABILISTIC_STATE` | `()` | the emission is not constant across runs | 3 | 8 |
| `SYMBOLIC_REWRITING` | `(1,1)`, `(2,2)` | emit each observed symbol incremented once, in order | 5 | 16 |
| `LEARNING_LAWS` | `(1,1,1)` | emit `0` three times, with strictly falling per-instance cost | 5 | 20 |
| `SELF_MODIFICATION` | `(1,)` | emit `1` after an instruction has been changed and re-executed | 5 | 16 |

The enumeration is exhaustive over every program of length `1..L`; no sampling and no search
heuristic is used anywhere.

## 6. The gates, fixed before any run

`status: GREEN` requires **all** of:

1. every one of the thirteen behaviours carries a verdict from the section-3 vocabulary, with
   `c*_M`, `c*_notM` and `Delta` published as exact integers or `null` for infinity;
2. the substrate neutrality check passes: no operation name and no operation's semantics is any
   of the thirteen behaviours, checked by a name-collision detector over the behaviour ids and
   their component words;
3. every predicate is extensional: a detector re-evaluates every predicate on the trace alone,
   with the program text withheld, and must return the same verdict on every program tested;
4. every `EMERGES_BY_PRICE` verdict survives its flat-pricing control, meaning the behaviour is
   NOT forced under flat pricing; a positive that survives flat pricing is republished as
   `FORCED_BY_REQUIREMENT`;
5. every `NOT_EXPRESSIBLE` verdict on `B0` is paired with a revival run on the declared
   extension and with a discharged proof requirement: an exhaustive statement that no program of
   `B0` up to `L` satisfies the predicate;
6. route A and route B agree on every published quantity, route B importing nothing from route A;
7. every declared hostile is detected, each paired with a control proving the perturbation moves
   the quantity it claims to move; a perturbation that cannot move its quantity is recorded as
   inapplicable and is NOT counted as a hostile;
8. the null reproduces the verdict vector in `0` of its live draws;
9. the no-alarm case is asserted: on the unperturbed configuration every detector is silent.

Any failure publishes `status: RED` with the failing gate named. A red result is a result.

## 7. Falsifiers, fixed before any run

- If `METAREASONING` or `ENDOGENOUS_EXPERIMENT_CHOICE` comes out `DOES_NOT_EMERGE` at every
  price in the sweep, the price account is not what produces them at this scope and the
  headline claim is withdrawn, not restated at a narrower scope.
- If any `EMERGES_BY_PRICE` verdict persists under flat pricing, `EC-3` is false as stated and
  the whole emergence-by-price reading is void.
- If a predicate's verdict changes when the program text is withheld, that predicate is not
  extensional and is withdrawn: it was naming the behaviour, which is exactly what the AH3 row
  forbids.
- If the substrate neutrality check finds an operation whose semantics is one of the thirteen
  behaviours, the substrate is not neutral and every verdict over it is void.
- If a randomized price vector reproduces the verdict vector, the prices are not identifying and
  the emergence claim is withdrawn.
- If a `NOT_EXPRESSIBLE` verdict is contradicted by any program found in the exhaustive
  enumeration, the enumeration was not exhaustive and every number is void.

## 8. Forbidden promotions

`INTELLIGENCE_DEFINED`, `UNIVERSAL_INTELLIGENCE_DEFINITION_PROVED`, `EMERGENCE_EXPLAINED`,
`METAREASONING_IS_INTELLIGENCE`, `THESE_THIRTEEN_ARE_THE_MI_ATOMS`,
`PRICE_ACCOUNT_IS_UNIVERSAL`, `SELF_IMPROVEMENT_PROVED`, `RECURSIVE_SELF_IMPROVEMENT_PROVED`,
`AUTONOMOUS_SELF_AUTHORITY`, `UNIVERSAL_COMPUTATION_IS_INTELLIGENCE`,
`EMERGENCE_LAW_HOLDS_AT_SCALE`, `COMPLETE_GMI`.

This package does not promote the AG7 lane into a definition of intelligence, and the AH3
criteria list is not claimed satisfied. Only the two rows above are reconciled, and only at the
registered finite scope.

## 9. What is not claimed novel

Bounded-rational and resource-bounded reasoning, the value of computation and the metalevel
control of computation (Good, Horvitz, Russell and Wefald), the value of information and
sequential experiment design (Blackwell, Lindley, Chernoff), minimum-description-length and
cost-sensitive model choice, register machines and their instruction decomposition (Minsky),
program enumeration over a bounded instruction alphabet, and the observation that a resource
constraint can make a conditional strategy cheaper than an unconditional one, are all parent
mathematics. They are pinned in `PARENT_LEDGER.md`. The residual contribution of this tranche is
the exact, exhaustive, two-route computation of `Delta` for thirteen behaviours over one
registered neutral substrate, the flat-pricing control that separates accounting from
vocabulary, and the extensionality detector that makes "not a primitive macro" a checkable
property rather than a promise.
