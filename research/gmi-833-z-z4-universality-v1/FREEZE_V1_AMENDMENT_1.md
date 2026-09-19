# Z4 freeze amendment 1 — two hostiles were tautologies and one null was
# trivially satisfied

Committed **before** any receipt, result file or reconciliation of this package
is committed. It records defects found by running a first draft of Route A whose
output was discarded and never committed. `source_main`, the claim ceiling and
the three reconcilable rows are unchanged; no neighboring row is earned here,
and rows 1 and 4 of `Z4` remain forbidden to this package.

## 1. `HS3` and `HS4` as frozen could not fail

`FREEZE_V1.md` §7 registered `HS3` as "an irreducibility verdict from clause 1
alone — both clauses must be recorded separately per distinction" and `HS4` as
"an exponent reported from a 2-rung ladder — rung-count guard". The first draft
implemented them as a check that both fields exist, and as the constant
`len(LADDER_L) < 4`. Neither can come out false: they are the `Z7` `C4` failure
class, an assertion over quantities that cannot violate it, and a hostile that
cannot fire is not a hostile.

**Repair, fixed here before any repaired number is used.**

- `HS3` becomes a **planted alternative verdict**: the executor computes the
  irreducibility verdict a second time using clause 1 alone, and the hostile is
  detected iff the clause-1-only verdict set differs from the two-clause verdict
  set. Both sets are published. If they coincide, clause 2 is doing no work and
  the criterion must be reported as clause 1 in disguise.
- `HS4` becomes a **validated guard function** `exponent_identifiable(rungs)`
  that refuses below `4` rungs. It is exercised twice and both outcomes are
  published: it must refuse on the registered `3`-rung sequence-length axis and
  the `2`-rung state-bit axis, and it must **accept** on a synthetic `5`-rung
  axis. A guard that only ever refuses is indistinguishable from a constant.
- `HS5` (degenerate class definition), registered but not implemented in the
  first draft, is now implemented as two planted definitions — a constant
  profile (one class) and an index-keyed profile (all singletons) — each of
  which the §2 vacuity guard must flag while staying silent on the real one.

## 2. `N2` passed for the wrong reason

`N2` draws `200` uniformly random bipartitions of the `65552` candidates and
runs them through the full two-clause test. `0` of `200` came out irreducible —
but essentially none of them can even reach clause 2, because a uniformly random
split of `65552` candidates across `21904` behaviour classes puts both sides
inside almost every class, so clause 1 rejects them immediately. The null is
therefore true but inert with respect to clause 2, which is the clause the row-5
criterion actually rests on.

**Added null `N4`, declared before it runs.** `200` random bipartitions that
**respect the behaviour quotient**: each of the `21904` behaviour classes is
assigned whole to one side or the other by a fair coin, seeds `7500..7699`. Such
a split passes clause 1 by construction, so `N4` measures exactly what fraction
of behaviour-respecting splits also survive the registered re-encoding
generators. `N2` is retained and published with the note above.

| id | statement | falsifier |
|---|---|---|
| `U10` | the clause-1-only verdict set differs from the two-clause verdict set — clause 2 rejects at least one distinction clause 1 admits | the two sets coincide |
| `U11` | `exponent_identifiable` refuses on both registered axes and accepts on the synthetic `5`-rung axis | either outcome is wrong |
| `U12` | the vacuity guard flags both planted degenerate class definitions and does not flag the registered one | any of the three verdicts is wrong |

## 3. Nothing else changes

The universe, the ladder, the resource-response profile, the two-clause
irreducibility criterion, `U1`-`U9`, `N1`, `N3`, `HS1`, `HS2` and the forbidden
promotions stand as written.
