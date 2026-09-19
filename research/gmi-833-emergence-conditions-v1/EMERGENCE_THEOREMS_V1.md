# Named results — emergence by price, and what actually decides it

Scope for everything below: the substrate `B0` and its two declared one-operation extensions,
the thirteen extensional predicates and the thirteen task families fixed in `FREEZE_V1.md`, and
an exhaustive enumeration of every program of length `1..L` — `813,615` programs at `L = 5`,
`54,240` at `L = 4`, `3,615` at `L = 3`. `24,326` programs meet a requirement across the
thirteen families. Nothing here is asserted beyond that scope, and no definition of
intelligence is offered.

---

## `EC-1` — the emergence condition

**Statement.** For a substrate `B`, an integer price vector `p`, a task family `T` with an exact
requirement `R`, a length bound `L` and an extensional predicate `M` on the registered trace,
let `Sol` be every `B`-program of length at most `L` meeting `R` on every instance, let
`cost(P)` be the worst-case sum of prices of the operations `P` actually executes, and let
`c*_M`, `c*_notM` be the least costs over the members of `Sol` that satisfy and fail `M`. Then
`M` is **forced** — every minimum-cost member of `Sol` satisfies `M` — exactly when
`Delta = c*_notM - c*_M > 0`, where an empty minimum is `+infinity`.

Four verdicts follow and no fifth is admissible: `EMERGES_BY_PRICE` (both finite,
`Delta > 0`), `FORCED_BY_REQUIREMENT` (`c*_notM` infinite), `DOES_NOT_EMERGE`
(`Delta <= 0`), `NOT_EXPRESSIBLE` (`c*_M` infinite).

**Why `M` may not read the program.** A predicate with access to the program text can be
satisfied by naming an operation, which is precisely what the AH3 row forbids. Extensionality is
enforced, not promised: the solving programs are grouped by trace signature and the predicate
must be constant on each group. Measured across all thirteen families: `0` groups split. The
detector is validated in the other direction too — a planted predicate that reads the program's
first operation splits `4` groups at once.

**Falsifier.** A predicate whose value changes when the program text is withheld.

**Assumptions.** A finite substrate, an integer price vector, a finite task family with an exact
requirement, and a length bound. Every predicate is a function of the registered trace alone,
and cost is the worst case over the family's instances.

**Dependency.** Depends on nothing outside `FREEZE_V1.md` sections 1 to 4.

**Strongest parents.** Bounded rationality (Simon) and the value of computation (Russell and
Wefald) own the idea that a resource account shapes the procedure a bounded agent adopts. The
residual is that the condition here is decidable by exhaustive enumeration and carries an exact
integer margin.

---

## `EC-2` — the structural condition behind a forced verdict is blind-cover impossibility

**Statement.** `c*_notM = infinity` holds exactly when the substrate has no conforming program
whose registered trace is identical across the family's instances and which fails `M`. Call such
a program a **blind cover**. Measured for every `FORCED_BY_REQUIREMENT` verdict: blind covers
that fail the predicate, `0`, in every case.

This is the structural property the AG7 row was after, and it is a property of `(B, T)` alone:
the family carries a distinction the substrate cannot cover without resolving it. No operation
names the behaviour, and the price vector plays no part in the statement.

**Falsifier.** A forced verdict accompanied by a predicate-free blind cover.

**Assumptions.** The family's instances are distinguishable only through the registered trace,
and a blind cover is a conforming program whose trace is constant across them.

**Dependency.** Depends on `EC-1` for the verdict vocabulary.

**Strongest parents.** The value of information (Howard; Lindley) owns the question of when an
observation has to be made at all. The residual is the exhaustive blind-cover count behind every
forced verdict.

---

## `EC-3` — the flat-pricing control, stated and NOT exercised

**Statement.** Under an accounting that gives every member of `Sol` the same cost, the
minimum-cost set is all of `Sol`, so `M` is forced only when `c*_notM` is infinite. Any
`EMERGES_BY_PRICE` verdict that survives flat pricing was not produced by the accounting.

**Status at this scope: the control has nothing to act on.** `EMERGES_BY_PRICE` occurs `0`
times in thirteen families, so the gate that runs this control passes **vacuously** and `EC-3`
is published as stated but **not exercised**. The receipt says so in a dedicated field
(`ec3_exercised: false`) rather than letting a vacuous pass read as evidence.

**Assumptions.** Flat pricing assigns every conforming program the same cost; nothing else about
the substrate or the family changes.

**Dependency.** Depends on `EC-1` for the vocabulary and, for whether it can be exercised at
all, on `EM-4`.

**Falsifier.** An `EMERGES_BY_PRICE` verdict that survives flat pricing. At this scope there is
no such verdict to test, which is itself reported rather than passed over.

**Strongest parents.** Ablating the cost model is ordinary practice and no owner is claimed;
what is recorded here is only that the ablation has nothing to act on at this scope.

---

## `EM-4` — at this scope emergence is never by price

**Statement.** Across the thirteen registered families, the verdict histogram is

```text
FORCED_BY_REQUIREMENT   7
NOT_EXPRESSIBLE         4
DOES_NOT_EMERGE         2
EMERGES_BY_PRICE        0
```

and the zero is robust: it is unchanged under the frozen worst-case accounting and under the
summed accounting, and unchanged at every observation price in the registered sweep
`p_obs in {1,...,6}`. No behaviour in the table is price-sensitive at all. The single
perturbation of the price account that was tried — charging cost per written instruction rather
than per executed step — moved **no** verdict, and is therefore recorded as an **inapplicable
perturbation** and deliberately not shipped as a hostile.

**What decides instead.** Expressibility and the requirement. Every verdict here is settled by
whether the substrate can produce the behaviour at all and by whether the task admits a blind
cover; the resource account never breaks a tie because there is never a tie to break.

**This corrects the expected mechanism.** The hypothesis this package was built to test was
that a behaviour emerges when the accounting makes it the cheaper option. At this scope that
mechanism is empty. The reason is visible in the data and is structural: all thirteen
predicates are *difference-making* properties, and a difference-making property is either
demanded by the family's input-to-output specification — in which case no conforming program
avoids it and `Delta` is infinite rather than finite — or not needed, in which case a
behaviour-free program is strictly cheaper because `B0`'s constant initial state is available at
zero observation price. `DOES_NOT_EMERGE` carries the exact margins: `-2` for reusable-operator
acquisition and `-1` for symbolic rewriting.

**Falsifier.** A registered family over `B0` exhibiting a finite `Delta > 0`.

**Forbidden extrapolation.** `PRICE_ACCOUNT_IS_UNIVERSAL` is a registered forbidden promotion of
this package, and so is its converse: nothing here shows that price never matters at a larger
scope. It shows that it decided nothing in thirteen exhaustively enumerated finite families.

**Assumptions.** The thirteen registered families and their frozen requirements, the worst-case
accounting of section 2, and the summed accounting run beside it as a declared variant.

**Dependency.** Depends on `EC-1` for the verdicts and on `EM-6` for knowing which families'
verdicts were settled by their own requirement rather than by the substrate.

**Strongest parents.** No parent claims that price never decides; none is contradicted either.
The value-of-computation literature (Russell and Wefald; Horvitz) predicts that price can
decide, and this scope is a region where it does not.

---

## `EM-5` — the two boundaries with no prior coverage are forced, not named

**Statement.** `METAREASONING` and `ENDOGENOUS_EXPERIMENT_CHOICE` — the two boundaries the
`#833` structural map records as having no coverage anywhere in the merged corpus — both come
out `FORCED_BY_REQUIREMENT` on a substrate that names neither and whose fifteen operations
contain no behaviour word.

| | conforming programs | `c*_M` | predicate-free blind covers | programs enumerated |
|---|---|---|---|---|
| `METAREASONING` | `132` | `4` | `0` | `813,615` |
| `ENDOGENOUS_EXPERIMENT_CHOICE` | `1,648` | `3` | `0` | `813,615` |

Every one of the `132` programs that meets the metareasoning family's requirement contains a
branch whose two outcomes lead to executed suffixes of different cost, and every one of the
`1,648` that meets the experiment-choice requirement makes an observation it never emits and
whose value changes the rest of its trace.

Neither forcing is an artifact of the requirement, and that is measured rather than assumed.
The metareasoning requirement is a bare input-to-output table, so its stripped requirement *is*
its frozen requirement; the control re-runs it and returns `FORCED_BY_REQUIREMENT` with
`requirement_entails_predicate: false`, which is the statement that the table alone admits no
predicate-avoiding conforming program. The experiment-choice requirement is **not** bare —
frozen `req_endogenous` adds the clause `word[0] not in out` on top of its table — so it is
stripped to the table alone and genuinely re-searched. That search returns the same `1,648`
conforming programs and the same verdict, so the extra clause is **inert on this universe** and
cannot be what forces the predicate. The same control returns `false` for the other two
headline families, `ADAPTATION` (`882` conforming) and `ROUTING` (`154`).

**What this does and does not say.** It says the behaviour is not a primitive and was not
named: it appears in every conforming program of a neutral substrate. It does **not** say the
behaviour is intelligence, that the substrate is an MI atom, or that the result survives to
larger programs. `METAREASONING_IS_INTELLIGENCE` and `THESE_THIRTEEN_ARE_THE_MI_ATOMS` are
registered forbidden promotions.

**Falsifier.** One conforming program of length at most `5` over `B0` that meets either family's
requirement and fails the predicate.

**Assumptions.** The substrate names none of the thirteen behaviours, checked by the neutrality
detector, and neither family's requirement is what forces its predicate, checked by the
stripped-requirement control of `EM-6`: both come out `requirement_entails_predicate: false`,
metareasoning because its requirement has no clause to remove and experiment choice because
removing its one extra clause changes neither the solution set nor the verdict.

**Dependency.** Depends on `EC-2` for what a forced verdict means structurally and on `EM-6` for
the restriction to families whose requirement is a plain input-to-output specification.

**Strongest parents.** `gmi-833-aj8-intelligence-boundary-v1` owns the registered negative
controls this result must not contradict; metareasoning as a subject is owned by Russell and
Wefald, and endogenous experiment choice by the sequential-design literature (Chernoff). The
residual is the exhaustive forcing count on a neutral substrate.

---

## `EM-6` — five of the thirteen frozen requirements entail their own predicate

**Statement.** The freeze's own section-5 wording puts a behaviour clause inside the
requirement for five families. Re-running each with that clause removed shows what the clause
was doing:

| family | frozen verdict | stripped verdict | stripped `Delta` |
|---|---|---|---|
| `HISTORY_SENSITIVE_DEVELOPMENT` | `FORCED_BY_REQUIREMENT` | `DOES_NOT_EMERGE` | `-1` |
| `MEMORY` | `FORCED_BY_REQUIREMENT` | `DOES_NOT_EMERGE` | `-1` |
| `LEARNING_LAWS` | `FORCED_BY_REQUIREMENT` | `DOES_NOT_EMERGE` | `-1` |
| `PROBABILISTIC_STATE` | `NOT_EXPRESSIBLE` | `NOT_EXPRESSIBLE` | — |
| `SELF_MODIFICATION` | `NOT_EXPRESSIBLE` | `NOT_EXPRESSIBLE` | — |

For the first three the forced verdict is an artifact of the requirement, not a fact about the
substrate: with the clause removed a behaviour-free program is one unit cheaper. This is
published rather than buried, and it is why `EM-5` is stated only over families that survive
this control.

The four headline families are entered into the same control, so that surviving it is a
measurement and not an omission. `ADAPTATION`, `ROUTING` and `METAREASONING` are stated as bare
input-to-output tables, so their stripped requirement is their frozen one (`stripped_is_frozen:
true`) and the control reports that the table alone admits no predicate-avoiding program.
`ENDOGENOUS_EXPERIMENT_CHOICE` does carry an extra clause — `word[0] not in out` — and is
therefore genuinely re-searched without it; the count is unchanged at `1,648` conforming
programs, so the clause is inert on this universe. All four return
`requirement_entails_predicate: false`, which is why the count above is `5 / 13` and not more.

| control family | stripped requirement | conforming | stripped verdict | entails |
|---|---|---|---|---|
| `ADAPTATION` | frozen (no clause) | `882` | `FORCED_BY_REQUIREMENT` | `false` |
| `ROUTING` | frozen (no clause) | `154` | `FORCED_BY_REQUIREMENT` | `false` |
| `METAREASONING` | frozen (no clause) | `132` | `FORCED_BY_REQUIREMENT` | `false` |
| `ENDOGENOUS_EXPERIMENT_CHOICE` | table only, clause dropped | `1,648` | `FORCED_BY_REQUIREMENT` | `false` |

**Falsifier.** A stripped run in which one of the five behaviours above remains forced, or one
in which any of the four control families flips to `requirement_entails_predicate: true`.

**Assumptions.** A requirement entails its predicate when the full run admits no conforming
program that fails the predicate while the run with the behaviour clause removed does.

**Dependency.** Depends on `EC-1` for the verdicts; `EM-4` and `EM-5` both depend on this result
for their scope.

**Strongest parents.** None external. This is a self-audit of the freeze's own section-5
wording.

---

## `EM-7` — what `B0` cannot host, and what one generic operation restores

Four behaviours are `NOT_EXPRESSIBLE` over `B0`, each proved by the exhaustive enumeration
rather than argued:

- **`PROBABILISTIC_STATE`** — `B0` is deterministic, so no program produces two emission
  sequences on one instance: `0` conforming programs out of `3,615` enumerated. **Revival on
  `B0R`**, which adds one generic entropy-stream read: `35` conforming programs,
  `FORCED_BY_REQUIREMENT`, `c*_M = 2`.
- **`SELF_MODIFICATION`** — `B0`'s instruction store is immutable by construction: `0`
  conforming programs. **Revival on `B0W`**, which adds one generic store write: `311`
  conforming programs, `FORCED_BY_REQUIREMENT`, `c*_M = 4`.
- **`SEARCH`** — `14,478` programs meet the requirement and not one exhibits the predicate. The
  obstruction is named and is a property of the frozen substrate: `B0`'s only backward jump
  returns to instruction `0`, which re-runs the input read, so a one-symbol instance cannot
  carry a test-then-revise cycle. **Adjacent scoped measurement** (labelled
  `VARIANT_NOT_PRE_DECLARED`, and not used to close anything): with a three-symbol instance the
  behaviour becomes expressible at `c*_M = 7` while a behaviour-free program costs `3`, so the
  verdict there is `DOES_NOT_EMERGE` with `Delta = -4`.
- **`CAPABILITY_FRONTIER_EXPANSION`** — the frozen predicate compares the family instances met
  from a reached state against those met from the initial state, and membership in `Sol` already
  requires every family instance to be met from the initial state, so the predicate cannot hold
  of any member of `Sol`. The freeze's wording is followed rather than quietly repaired.
  **Adjacent scoped measurement** against a probe set strictly larger than the family
  (`{(0), (1), (2)}` against a family of `{(0), (1)}`): `0` of `882` conforming programs reach a
  state covering strictly more than the initial state, so the behaviour is absent for a second,
  independent reason and not merely by a definitional artifact.

**Falsifier.** Any program found by the enumeration that contradicts a `NOT_EXPRESSIBLE`
verdict.

**Assumptions.** Non-expressibility is asserted only where the exhaustive enumeration produced
no program satisfying the predicate; each revival adds exactly one generic operation and changes
nothing else.

**Dependency.** Depends on `EC-1` for the `NOT_EXPRESSIBLE` verdict and on `EM-6` for which of
the four verdicts were settled by their own requirement.

**Strongest parents.** Register machines and their instruction decomposition (Minsky) own the
substrate's shape; `gmi-833-aj5-g0-lowering-v1` owns the generic role basis its operation names
follow. The residual is the exhaustive impossibility proof and the one-operation recovery.

---

## Evidence carried by every result above

**Two materially independent routes.** Route B imports neither route A nor any parent module.
It rebuilds the substrate, the families and all thirteen predicates from the freeze's wording,
runs a different interpreter, enumerates by an explicit descending odometer with **no** static
prefilter, takes costs from the executed opcode stream rather than an accumulated count vector,
and finds the minima by a full sort rather than a running minimum. Verdict, margin, both minimum
costs, conforming-program count and blind-cover count agree for all thirteen behaviours and both
revivals: **0 disagreements**.

**Five hostiles, all detected, each with a control proving it moves its quantity.** A predicate
that reads the program text (`0 -> 4` split trace groups); an operation named after a target
behaviour (`0 -> 2` name collisions); an enumeration missing every cost-minimal program
(`24,326 -> 23,518` conforming programs, caught by an independently computed minimum); an
unsound static prefilter (`24,326 -> 4,014`, caught by the prefilter validator — which had
already caught a real unsound filter in this package's own first draft); and a requirement that
stops checking termination (`24,326 -> 25,980`, caught by the termination check).

**One perturbation recorded as inapplicable and deliberately not shipped.** Charging cost per
written instruction moves no verdict at this scope, so it would be a test of nothing.

**Nulls.** `0 / 200` random price vectors and `0 / 200` random trace-keyed predicates reproduce
the published verdicts, margins and both exact minimum costs.

**No-alarm case asserted.** On the true configuration every detector is silent: `0` split trace
groups, `0` name or semantics collisions, every published cost recomputing from its trace, every
prefilter check identical.
