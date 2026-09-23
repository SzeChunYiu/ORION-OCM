# GMI #833 Section-H real-scale freeze v1 — Autoregressive generative systems.

`source_main`: `bcab8e49`.

This file is committed **in its own commit, before any executor, test, data
extraction, fit, or result artifact of this package exists**. `git log
--diff-filter=A` order is the custody record and CI asserts it.

This file and its two slice addenda are **outcome-free**: they register the
scope, the sha-bound source, the ecology, the query sets, the closed readout
language, the winner rule and the controls, and they print **no arm's
performance** — no majority-rule error count, no per-arm error count, no
falsifier denominator, no delivered integer of any stage. Counts that appear
below are properties of the **frozen construction** (token counts, descriptor
counts, slice sizes, query-set sizes, alphabet width) and are re-derived by the
executor and by route B; they are not properties of any arm's behaviour.

## 1. The exact issue row this tranche may reconcile

Section of the issue: the `# H. Prior-free derivation of known
machine-intelligence families` header line of issue #833, recorded verbatim as
the `anchor` field of this package's `ISSUE_833_RECONCILIATION` document. The
row's evidence key is `L:caed52c7d53c`
(`sha256(section header \x00 row text)[:12]` over the row text alone; asserted
to be 64 characters and matched programmatically against
`research/gmi-833-checklist-mirror-v1/EVIDENCE_LEDGER_V1.json` entry 169).

Rows, verbatim and complete:

```
- [ ] Autoregressive generative systems.
```

**No neighboring row is earned here.** No row of any other section, no
aggregate Section-H row, and none of the other 40 named-family rows. In
particular this package is a **row-30 scope**: it is neither `Recurrent neural
networks.` (`H23`) nor `LSTM/GRU-like gating.` (`H24`) nor `State-space
models.` (`H28`), all of which the frozen registry gives the *same* contract —
see section 2 — and none of which is re-earned, re-claimed, or depended upon
here. The repo row id is `H30`
(`research/gmi-833-h-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json:52`).

## 2. The scope decision that governs this package, and the steer it carries

Section H requires eleven coordinates per row: property prediction from
specification/ecology (`R01`); `P3`/`P4` grammar (`R02`); no family macros
(`R03`); family-blind recovery (`R04`); a matched negative control (`R05`);
lower bound where possible (`R06`); resource crossover (`R07`); held-out frozen
prediction (`R08`); independent regeneration (`R09`); independent search
(`R10`); real-scale test (`R11`).

The finite scope of this row (R01–R10) is certified by the parents at their own
registered finite scopes, with R11 open. It is **invalid** to add a missing
certificate at a different scope and declare the conjunction: that is
`CROSS_SCOPE_GATE_COMPOSITION`, forbidden by
`gmi-833-h-family-requirement-ledger-v1` `HRL-1` and proved invalid by PR #997
`FGS-2`. A scope is the tuple (family row, grammar, ecology, budget, freeze,
protected interface); every one of those coordinates moves here.

**Therefore this package imports no gate certificate from any parent. It earns
all eleven coordinates at its own scope, self-contained.** The parents supply
form — the eleven-coordinate real-scale ledger shape, the freeze-first custody
chain, the slice-addendum architecture, the family-blind recovery procedure
with a closed pre-outcome readout language, the post-hoc structural classifier,
the constant-branch exclusion rule, the charged-cost model, the symmetric
half-split regeneration, the matched-presentation control and the
route-A/route-B checker-and-oracle shapes — and are cited as strongest parents
in `PARENT_LEDGER.md`. They supply no evidence that is counted here.

### The registered steer, and its citation

`research/gmi-833-h-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json:52`
gives this row `{"id":"H30","row":"Autoregressive generative systems.",
"contract":"HISTORY_STATE_CHANNEL","hallmark":"response dependence on generated
history"}`. **The contract is a steer, not a binding label arity** — verified
from the merged H08 package, whose `FREEZE_V1.md:50-58` records
`THRESHOLD_CONJUNCTION` as "a steer only" and whose winner is a two-test
conjunction. This package registers the steer and its citation and forces no
literal arity. The steer is load-bearing in one respect only: **the readout the
winner rule recovers must depend on history the system itself generated** — the
state of the continuation the model's own rule produces from the query — and
not on a stored input, a source fan-out, an accumulated reward or an evidence
mass. That is what separates this row from its three registry siblings on the
same channel (`H23`, `H24`, `H28`), and it is what the controls of section 10
test by measurement.

## 3. The scope, written out

| id | family row | ecology `F` | protected interface |
|---|---|---|---|
| `SIGMA_H30R` | Autoregressive generative systems. | `F30` generated-history ecology on `D` | held-out exact prototype-agreement; held-out exact sign-decision error count |

Every gate certificate emitted by this package carries its `sigma` id. The
checker fails the run if the row's eleven certificates do not all carry one and
the same `sigma` id, or if any `sigma` is foreign. The `sigma` id is the repo
row id `H30` of this family row, the convention the siblings use (`SIGMA_H05R`,
`SIGMA_H06R`, `SIGMA_H08R`, `SIGMA_H19R` for repo rows `H05`, `H06`, `H08`,
`H19`).

## 4. Real data source, bound by digest

Externally originated; none generated by this package or by any agent. Every
number in every claim traces to these bytes.

- `D` = `/usr/share/dict/american-english` on billy-old (billy-laptop-old),
  104,334 whitespace-separated tokens
  (`len(open(path).read().split())`, the exact arithmetic definition of `N`),
  in file order; sha256 digest of the file bytes
  `9e66281f7e51445eab6857488ff6e3d768afffadb7fb1adbef5e4617bee4a53b`.

Host of record: `billy-old`, Linux, CPython 3.14.4. Any digest mismatch fails
the run closed. A negative control asserts that a perturbed path or a perturbed
digest fails rather than passing vacuously.

### The ecology, registered before it is built

`F30` (`SIGMA_H30R`). Tokenise `D` into its 104,334 whitespace-separated
tokens. The **descriptor closure** is, for every token `w`, all prefixes of `w`
of length ≥ 2. The exact total is

```
T = sum(len(w) - 1 for w in words) = 776,142 descriptors
```

in source order; `237,950` of them are distinct, and the closure alphabet (the
distinct characters of the source) has width `69`.

A descriptor is **terminal** when it equals a source token — the sequence model
has reached the end of a token — and **non-terminal** otherwise. A task is a
query descriptor, and the registered query set is the **non-terminal**
descriptors: a sequence model is asked for the next step from a prefix that is
still open. This is a property of the frozen bytes alone, computed before any
fit, identical at every stage and for every arm; no position moves.

The family is **autoregressive generative systems**: the quantity that decides
the answer for a query is the **state of the continuation the model has itself
generated** from that query. The ecology makes that quantity exact and finite:

- The **stored-context table** at stored size `m` holds the descriptors at the
  first `m` positions of the registered presentation order (section 8), with
  each descriptor's stored occurrence count.
- The **model's own deterministic continuation rule of a table** is: from a
  prefix `s` that has at least one stored child descriptor (`s` + one letter),
  extend `s` by the child letter of highest **stored occurrence count**, ties
  broken to the lexicographically smallest letter; repeat. The rule is read off
  the table itself — it is a property of the frozen bytes and the store, not of
  this package.
- The **generated-history state** of a query `q` under a table is the pair
  `(steps, closed)`: `steps` counts the continuing steps the rule takes from `q`
  before the walk reaches a source token (a terminal descriptor) or the table
  has no cell for the current prefix, capped at the registered step cap
  `STEP_CAP = 6`; `closed = 1` records that the walk reached a source token.
  A walk that reaches no source token within `STEP_CAP` is recorded as
  `(STEP_CAP, 0)`.

The protected interface is held-out exact prototype-agreement and held-out
exact sign-decision error count, over the exact decisions

```
y(q) = 1 iff the FULL-SOURCE walk from q terminates within STATE_K0 = 2 steps
     = 1 iff the model's own rule, read off the complete source table,
             reaches a source token from q in at most two steps
```

evaluated on the registered query set. The label is the **state of the
model's own generated continuation**, evaluated on the complete table: a
prefix is positive exactly when the model's own rule carries it to a completed
token in at most `K0` steps. This is the property an autoregressive system
computes by running its own next-step rule on its own output, and the property
no single stored item records.

Slices, fixed here before any outcome: the descriptor list is presented under
the parents' target-independent Knuth permutation and partitioned 7:1, giving

```
n_fit = (T * 7) // 8 = 679,124  >= 100k
n_held = T - n_fit = 97,018    >= 20k
```

which clears the R11 real-scale bar (n_fit ≥ 100k / n_held ≥ 20k on a
sha256-bound external REAL source, exact arithmetic, independent oracle).

## 5. Grammar

`G_AG`: a family-blind grammar derived ONLY from the sha-bound bytes of `D`.
Descriptor closure over the token vocabulary (prefixes of length ≥ 2), the
terminal/non-terminal distinction, the stored child-extension table with its
stored occurrence counts, the generated-history walk enacted on that table, the
stored-context table (membership counts and child fan-out) and a charged-cost
model over stored-table size and scan cost. No family-level macro, no
hand-encoded autoregressive or next-step routine, no reference to any external
implementation. Section R03 asserts the grammar contains no sequence-model
macro, and R04 recovers the family from the grammar alone.

## 6. Arithmetic

Exact integer arithmetic for every reported quantity: every claimed number is
an exact integer decision count (prototype agreement, sign-decision errors,
null errors, ladder errors, charged-cost units, crossover index). No float
enters any comparison, count, loss, or claim. There is no real-valued fitting
routine whose output requires a rationalisation operator, so this package
carries no arithmetic addendum: the exact-integer form is complete in this
freeze and the slice addenda.

## 7. Budget

Registered node and index budgets for the family-blind search, stated before
any fit, identical for every arm: the descriptor-closure vocabulary index, the
stored child-extension table, the generated-history walk with its registered
step cap, the stored-context table, and the scan window are all bounded and
fixed in the executor. Resource crossover (`R07`) varies these budgets and
asserts the held-out error is monotone non-increasing in them.

## 8. Presentation, predictions, and what is frozen

The registered presentation is the parents' target-independent Knuth
multiplicative-hash lever, fixed in the slice addendum before any outcome
together with the exact 7:1 slice, the ranking sub-split, the symmetric
half-split of the fit, the closed readout language `R`, the winner rule and the
constant-branch exclusion rule. No frozen count of section 4 moves.

Held-out frozen predictions are written to the frozen-prediction record
(`R08`) before the oracle is run, exactly as in
`gmi-833-h-real-scale-classical-v1`: the fit is completed on `n_fit`, the
prediction for each held-out query is emitted to the record, and only then is
the independent oracle (Section R09) run and compared. The record is written
before the label null and before the design null.

## 9. Falsifiers

A held-out exact prototype-agreement below the registered baseline, an exact
sign-decision error count above the registered bound, a null that performs
comparably to the family on the same slice rule, a winning readout whose
structural class is not the generated-history class, a presentation or
generation-rule control that fails to fire, or any cross-scope gate
composition — any one falsifies the claim ceiling.

## 10. Controls

Matched negative control (`R05`):

1. a **shuffled-label null** with equal sample size on the identical slice rule
   must perform at chance;
2. a **design null that destroys the generated history** — the walk's
   continuation drawn at random instead of by the model's own rule, with the
   store, the query set, the length structure and the raw stored-table arms
   bit-identical — must fail to recover the family;
3. a **matched-presentation control** reading the descriptor list in source
   (identity) order instead of under the registered permutation must fail the
   registered margin, so the presentation lever is load-bearing;
4. an **alternative-generation-rule control** enacting a different
   deterministic stored rule (the lexicographically smallest stored child
   letter) must return the same **class** of readout, so the recovered class is
   a property of the ecology and not of the particular tie-break;
5. a **history-replacement control**: on the queries the store holds no cell
   for, the generated-history readout must retain its advantage while every
   readout that reads only a stored input, a stored fan-out or an external
   state probe is unchanged, so the advantage is attributable to the generated
   history and not to the query set.

The screen asserts `CLEAN` only when the no-alarm case also fires (the
checker's own controls are asserted to fire).

## 11. Claim ceiling

`REAL_SCALE_ELEVEN_GATE_DERIVATION_OF_NAMED_CLASSICAL_FAMILY_AT_REGISTERED_SCOPE`
— all eleven coordinates R01–R11 at the single registered scope `SIGMA_H30R`,
self-contained, real-scale. Forbidden promotions (mirrored from the parent
real-scale packages): `CROSS_SCOPE_GATE_COMPOSITION`,
`REGISTERED_CONTROL_SUBSTITUTION`, `POST_HOC_FALSIFIER_REPLACEMENT`,
`ECOLOGY_ITERATION_UNTIL_POSITIVE`, `INDEPENDENT_TEAM_REPLICATION`, `M5`,
`EV4`, `EV5`, `REAL_SCALE_VALIDATION_COMPLETE`, `SECTION_H_COMPLETE`,
`ALL_KNOWN_FORM_RECOVERY`, `UNIVERSAL_GRAMMAR_NEUTRALITY`,
`FRONTIER_SCALE_VALIDATION`,
`NAMED_FAMILY_ROW_CLOSED_OUTSIDE_THIS_PACKAGE`,
`FINITE_EVIDENCE_IMPLIES_REAL_SCALE`, `COMPLETE_GMI`.
