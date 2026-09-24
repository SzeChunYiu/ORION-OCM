# Z4 named results — universality classes at registered binary-transducer scope

Scope for every result below, and never wider: the registered `65552`-candidate
binary mechanism universe, the budget ladder `bits in {0,1}` (`2` rungs) and
`L in {2,3,4}` (`3` rungs), canonical initial state `0`, exact integer error
counts. Three of the five `Z4` rows are in scope; rows 1 and 4 are deliberately
left open and the freeze forbids this package from touching them.

Claim ceiling:

```
GMI_833_Z4_RESOURCE_RESPONSE_UNIVERSALITY_CLASSES_AND_SURVIVING_DISTINCTIONS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

---

## `UC-1` — class membership defined by resource response, not by name (row 2)

**Definition (fixed before computation).** A candidate's resource-response
profile is its exact integer `(k_now, k_delay)` at each rung of the
sequence-length ladder together with a bit saying whether it sits on the exact
Pareto frontier of its own state-bit block at that rung. Two candidates share a
class iff the profile is equal. No name, index or family label enters.

**Statement.** The universe partitions into exactly **`568`** resource-response
classes. Class sizes run from `2` to `14360`; there are **`0`** singleton
classes.

**Non-degeneracy, checked before the number was used.** A class definition that
puts everything in one class, or everything in its own, measures nothing. The
largest class holds `14360` of `65552` and no class is a singleton, so the
definition is non-degenerate (`U1`). It also sits strictly between the two
trivial resolutions available: `6` registered named families `< 568 <` `21904`
behaviour classes (`U2`). The profile is invariant under candidate renaming —
verified by permuting the index space and recovering the identical partition —
while a profile keyed on the index produces `65552` classes and is flagged
(`HS1`).

**Forbidden extrapolation.** `CLASS_DEFINITION_IS_CANONICAL` — this is *a*
resource-response quotient, defined by a registered ladder, not the canonical
one.

**Assumptions.** The registered `65552`-candidate universe of
`research/gmi-833-heldout-20-transitions-v1`, replayed from canonical initial
state `0`, and the budget ladder `bits in {0,1}`, `L in {2,3,4}` of
`FREEZE_V1.md` section 1; the resource-response profile of section 2, fixed
before computation, with exact integer error counts per rung and a frontier bit
per rung as defined above. The class count `568` is a property of this ladder
and this universe, not a canonical count.

**Dependencies.** The non-degeneracy guard of `FREEZE_V1.md` section 2,
hypotheses `U1` and `U2` (section 5) and `U12` (`FREEZE_V1_AMENDMENT_1.md`); the
hostiles `HS1` and `HS5`; the `21904` behaviour classes and the generator
`g_rename` of `research/gmi-833-z-z2-minimal-prior-v1` and the six named
families of `research/gmi-833-z-z7-impossibility-v1`, which bound the `U2`
interval; the class count, size range and singleton count in `RESULT_V1.json`,
recomputed by route B in `ORACLE_RESULT_V1.json`.

**Falsifiers.** Registered in `FREEZE_V1.md` section 5: a largest class equal to
the whole universe, or every class a singleton, refutes `U1`, and a class count
outside the interval from `6` to `21904` refutes `U2`. A partition that changes
when the index space is permuted would show that a name has entered the profile
(`HS1`).

**Strongest parents.** Kadanoff (1966) and Hohenberg & Halperin (1977), who own
the idea that systems agreeing on scaling behaviour form a class independent of
microscopic detail; Pareto (1906) for the frontier bit; Nerode (1958) and Myhill
(1957) for the behavioural quotient used as the upper comparison
(`PARENT_DISCLOSURE_V1.md`). The profile is one resource-response quotient, not
the canonical one.

---

## `UC-2` — exact frontiers, and an exponent refusal with its rung count (row 3)

**Frontiers, delivered exactly.** Within each state-bit block, at every rung:

| rung | `bits = 0` frontier | distinct points | `bits = 1` frontier | distinct points |
|---|---|---:|---|---:|
| `L = 2` | `{(0, 2)}` | `3` | `{(0, 0)}` | `25` |
| `L = 3` | `{(0, 8)}` | `3` | `{(0, 0)}` | `143` |
| `L = 4` | `{(0, 24)}` | `3` | `{(0, 0)}` | `437` |

Within each registered named family at `L = 3`:

| family | members | `(k_now, k_delay)` frontier |
|---|---:|---|
| `F_STATELESS` | `16` | `{(0, 8)}` |
| `F_DEAD_TABLE` | `4096` | `{(0, 8)}` |
| `F_FROZEN_STATE` | `512` | `{(0, 8)}` |
| `F_MOORE` | `4096` | `{(8, 0)}` |
| `F_MEALY_PURE` | `61440` | `{(0, 0)}` |
| `F_IDENTITY_STATE` | `256` | `{(0, 0)}` |

`F_MOORE` and `F_MEALY_PURE` have **different** frontiers at identical state
budget (`U8`): a Moore machine cannot get below `8` immediate-channel errors
while a Mealy machine reaches `0` on both channels. This reproduces, by an
independent route and definition, the structural separation
`research/gmi-833-z-z7-impossibility-v1` reports as its `IM-5`.

**Asymptotic forms, delivered exactly.** The minimum delayed-channel error count
attainable **without** state is `(L-1) * 2^(L-1)` at every rung — `2`, `8`, `24`
against `(L-1) * 2^L` = `4`, `16`, `48` scored moments per mode, i.e. exactly
half — and the minimum attainable with one bit is `0` at every rung (`U7`).
Route B derives the first analytically from the independence of consecutive
input bits and then checks it against the enumeration; they agree at all three
rungs.

**Exponents: refused, with the rung count stated.** No exponent is reported.
The state-bit axis has `2` rungs and the sequence-length axis has `3`; a power
law fitted to two or three points is not identified. The refusal is licensed by
the row's own clause *where mathematically justified*, and the guard that issues
it is validated in both directions — it refuses at `2` and `3` rungs and
**accepts** at a synthetic `5`-rung axis (`U11`), so it is a guard and not a
constant.

**Assumptions.** The universe and ladder of `UC-1`; frontiers are exact Pareto
frontiers of `(k_now, k_delay)` within each state-bit block and each registered
named family, reported as exact integer sets. An exponent counts as
mathematically justified only on an axis with at least `4` rungs whose quantity
has no exact closed form (`FREEZE_V1.md` section 3, guard
`exponent_identifiable`); the closed forms are stated for `L in {2,3,4}` only.

**Dependencies.** Hypotheses `U7`, `U8` and `U9` (`FREEZE_V1.md` section 5) and
`U11` (`FREEZE_V1_AMENDMENT_1.md`); the frontier null `N3` and the hostiles
`HS2` and `HS4`; the six named families of
`research/gmi-833-z-z7-impossibility-v1`, whose `IM-5` separation `U8`
reproduces; route B's analytic derivation of the stateless delayed minimum in
`independent_universality_oracle_v1.py`.

**Falsifiers.** Registered in `FREEZE_V1.md` section 5: a rung where the
stateless delayed minimum differs from `(L-1) * 2^(L-1)` or the one-bit minimum
differs from `0` refutes `U7`; coinciding `F_MOORE` and `F_MEALY_PURE` frontiers
at `L = 3` refute `U8`; a rung count other than `2` and `3` refutes `U9`. A
frontier containing a dominated point (`HS2`), or a guard that fails to accept
the synthetic `5`-rung axis (`U11`), would void the delivered sets or the
refusal.

**Strongest parents.** Pareto (1906) for dominance and the efficient frontier;
Moore (1956) and Mealy (1955), who own the two forms whose frontiers differ;
`research/gmi-833-z-z7-impossibility-v1`, whose `IM-5` already reports the
Moore/Mealy structural separation; Kadanoff (1966) and Hohenberg & Halperin
(1977) for the exponent notion that is refused here (`PARENT_DISCLOSURE_V1.md`).

---

## `UC-3` — one distinction of sixteen survives quotienting (row 5)

**Criterion (fixed before computation).** A distinction is irreducible iff it
survives **both** the semantic quotient — no `48`-bit behaviour class straddles
the two sides, and each side owns at least one — **and** every registered
re-encoding generator (`g_rename`, `g_state`, `g_out`), in the sense that each
side's behaviour-class set and its attainable `(k_now, k_delay, bits)` frontier
are carried to themselves.

**Statement.** Of `16` distinctions tested — the `bits = 0` / `bits = 1` split
and the `15` pairwise separations among the six registered named families —
exactly **one** is irreducible:

```
F_DEAD_TABLE  vs  F_MOORE
  output independent of state   vs   output independent of input
```

`13` fail the semantic quotient outright, so they are **implementation details**,
not behaviours. `3` survive it, and of those `2` — `F_DEAD_TABLE vs
F_IDENTITY_STATE` and `F_IDENTITY_STATE vs F_MOORE` — fail re-encoding
invariance and are therefore **encoding artifacts**.

**Two refutations worth the space.**

- `U3` said the `bits = 0` / `bits = 1` split would be irreducible. It is not:
  it fails the semantic quotient, because a one-bit machine whose state never
  changes what it emits has exactly the behaviour of a stateless one. The
  *syntactic* possession of a state bit is an implementation detail at this
  scope; only its *effective* use is behaviour.
- `U4` said `F_MOORE vs F_MEALY_PURE` would be irreducible. It is not, for the
  same reason in the other direction: a Mealy table that happens not to consult
  the input has a Moore machine's behaviour. The **frontier** separation of
  `UC-2` is real and survives; the **membership** separation does not.

`U5`, marked `[NAIVE]` at freeze, said all fifteen family separations would be
irreducible; refuted, `1` of `16`. Its deliberate opposite `U6`, that at least
one family separation fails the semantic quotient, is confirmed with `13`.

**The criterion is not free.** `0` of `200` uniformly random bipartitions are
irreducible (`N2`) — but that null is **inert** with respect to the second
clause, because a random split across `21904` behaviour classes cannot reach it,
and that is recorded rather than glossed (`FREEZE_V1_AMENDMENT_1.md`). The null
that does test it, `N4`, draws `200` bipartitions that respect the behaviour
quotient by construction: `0` of `200` survive re-encoding invariance. And the
second clause is not decorative: the clause-1-only verdict admits `3`
distinctions where the two-clause verdict admits `1` (`U10`, hostile `HS3`).

**Forbidden extrapolation.** `IRREDUCIBILITY_BEYOND_REGISTERED_RE_ENCODINGS` —
irreducibility here is relative to three named generators, not to all
re-encodings.

**Assumptions.** The two-clause criterion of `FREEZE_V1.md` section 4, fixed
before computation: the semantic quotient is equality of `48`-bit behaviour
vectors at `L = 3`, and invariance is relative to the three registered
generators `g_rename`, `g_state` and `g_out` only. The `16` distinctions tested
are the `bits` split and the `15` pairwise separations of the six registered
named families; nothing is claimed for other distinctions or other re-encodings.

**Dependencies.** Hypotheses `U3`..`U6` (`FREEZE_V1.md` section 5) and `U10`
(`FREEZE_V1_AMENDMENT_1.md`); the nulls `N2` and `N4` and the hostile `HS3`; the
behaviour key, the `21904`-class quotient and the three generators of
`research/gmi-833-z-z2-minimal-prior-v1`, re-implemented here; the family member
sets of `research/gmi-833-z-z7-impossibility-v1`; the frontier separation of
`UC-2`, which the `U4` refutation keeps apart from membership.

**Falsifiers.** A behaviour class straddling `F_DEAD_TABLE` and `F_MOORE`, or a
registered generator that fails to carry either side's behaviour-class set or
`(k_now, k_delay, bits)` frontier to itself, would remove the single irreducible
distinction. A behaviour-respecting random split surviving re-encoding in `N4`,
or a clause-1-only verdict set equal to the two-clause set (the falsifier of
`U10`), would show that the criterion is cheap or that clause 2 does no work.

**Strongest parents.** Nerode (1958) and Myhill (1957) for the behavioural
quotient, and Birkhoff (1935) for quotients and invariance under
structure-preserving maps, of which the two-clause criterion is a narrow
instance; Moore (1956) and Mealy (1955) for the forms whose defining properties
separate (`PARENT_DISCLOSURE_V1.md`). The generators are Z2's, owned by
`research/gmi-833-z-z2-minimal-prior-v1`.

---

## What none of these results establish

Nothing about MLP, CNN or Transformer families; no claim that named
architectures collapse into broader classes in general — that is row 1 and row 4,
both deliberately left open; no universal exponent; no asymptotic law beyond
`L = 4`; and no claim that the `568`-class quotient is canonical.
