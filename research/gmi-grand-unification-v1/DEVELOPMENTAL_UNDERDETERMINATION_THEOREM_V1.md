# Grand GMI Developmental Underdetermination Theorem V1

Status: **THEOREM / NO-GO BOUNDARY ON DERIVING DEVELOPMENT + EXACT FINITE WITNESSES**
Date: 2026-09-13

Authority for the derived-bound machinery used below:
`MORPHOLOGY_PHASE_LAW_DERIVATION_V1.md`. Retained predecessors: MS-6,
DRS-1–3, `DEVELOPMENTAL_LIFECYCLE_CORRECTION_V2.md`,
`UNCOMPUTABILITY_BOUNDARY_THEOREM_V1.md`.

## 1. Gap addressed

`RECURSIVE_GAP_AUDIT_20260913.md` lists a general neural training theorem and
modern-scale learning prediction as open, and records the resource/learning
obligations as missing measurements. MS-6 already records that the reachable
frontier differs from the static one.

What was missing is the reason those items are open. They were listed as work
not yet done. This theorem establishes the stronger and more useful statement:

> The reachable frontier is **not a function** of the data the rest of the
> package supplies. No theorem of the form "necessities imply the trained
> outcome" can exist, whatever effort is spent on it.

That converts an open task into a registered structural requirement: the
development law is an independent input, with its own semantics, and a
bounded-development verdict does not extrapolate.

## 2. DU-1 — realization data does not determine reachability

> **DU-1.** Two development laws can share the admitted realization set, the
> profile map, the family assignment and every proved necessity, and still
> yield different reachable frontiers and different verdicts.

### Proof

Exhibit the witness. States `{s0, a, b}` with profiles `10, 5, 3`, families
`NEURAL, NEURAL, NON_NEURAL`. The global best per family is
`NEURAL: 5`, `NON_NEURAL: 3`, and that data is shared by both laws. Law `D1`
admits only `s0 -> a`; law `D2` admits only `s0 -> b`. At budget `1` the
reachable frontier of `D1` has family support `{NEURAL}` and that of `D2` has
family support `{NON_NEURAL}`. All inputs except the development law are
identical, so the reachable frontier is not a function of them. QED.

### Consequence

A "general training theorem" cannot be derived from semantic, cut,
transformation, symmetry, resource or realization facts, because those facts
do not determine the object it would be about. This is not a statement about
the difficulty of analysing gradient descent. It is a statement that the
target is underdetermined until `D` is registered, which is why the primitive
tuple carries `D` as its own component.

## 3. DU-2 — the admitted update set does not determine the reachable set

> **DU-2.** Reachability depends on the schedule of admitted updates, not only
> on which updates are admitted. A registered development law must therefore
> fix its composition and admission semantics.

### Proof

Take admitted updates `double` and `add_three`, start value `1`, and the
admission cap `6` applied after each update. The schedule
`double -> add_three` gives `1 -> 2 -> 5`, admitted. The schedule
`add_three -> double` gives `1 -> 4 -> 8`, which exceeds the cap and is
rejected. The update set is identical; the reachable set is not. QED.

Non-commuting updates are the normal case for curricula, pruning and growth,
architecture edits, and any budgeted search. Registering a set of admitted
operations is therefore not a registration of a development law.

## 4. DU-3 — reachability is safe for bounds, unsafe for verdicts

> **DU-3a.** Restricting to reachable realizations never lowers a derived
> lower bound: `L_F^{reach} >= L_F`.
>
> **DU-3b.** Restricting to reachable realizations can invalidate a
> construction, so the verdict is not monotone and can invert.

### Proof

For DU-3a, `Reach` is a subset of the admitted set, and an infimum over a
subset is at least the infimum over the set. Reachability evidence therefore
behaves exactly like any other valid necessity in the sense of PL-4a, and a
robust exclusion obtained without it survives.

For DU-3b, an upper bound is a construction, and constructions are not
inherited by subsets. The witness has family `A` with realizations of cost `2`
and `9`, and family `B` with a single realization of cost `5`. Globally the
frontier support is `{A}` at cost `2`. If only the cost-`9` member of `A` and
the cost-`5` member of `B` are reachable, the reachable frontier support is
`{B}`. Both family lower bounds rose, from `2` to `9` and from `5` to `5`, yet
the verdict inverted. QED.

This asymmetry is the precise shape of the learning gap. Training evidence can
only strengthen exclusions; it can destroy the constructions on which any
selection rests. So a selection claim always depends on development evidence,
while an exclusion claim need not.

## 5. DU-4 — no finite budget certifies an unbounded-development verdict

> **DU-4.** For development laws in which each admitted update strictly
> improves the profile and changes family, the budget-`B` verdict reverses at
> budget `B + 1` for every `B` below the chain length. A bounded-development
> verdict therefore does not extrapolate to unbounded development.

### Proof

Take the chain `s0 -> s1 -> ... -> sk` with profile `10 - i` at `si` and
family alternating with the parity of `i`. At budget `B <= k` the reachable set
is `{s0, ..., sB}`, its frontier is `10 - B`, attained uniquely at `sB`, so the
family support is the parity class of `B`. Consecutive budgets have opposite
parity, so consecutive verdicts differ. The witness runs `k = 8` and checks
that all eight frontiers are `9, 8, 7, 6, 5, 4, 3, 2` and that the verdict
alternates at every step. QED.

The separate uncomputability boundary already forbids a total exact solver for
unrestricted machine spaces. DU-4 is the complementary finite statement: even
where every budgeted question is decidable, no budgeted answer licenses the
limit. A registered budget is a hypothesis with content, not a convenience.

## 6. What this closes and what it does not

Closed: the openness of the training and large-scale-learning items now has a
proof rather than a placeholder. Their target is underdetermined by the rest
of the package (DU-1); registering admitted operations is not registering a
development law (DU-2); development evidence strengthens exclusions but can
destroy selections (DU-3); and no finite budget certifies an unbounded
verdict (DU-4).

Not closed, and not closable this way:

- no learning process is analysed, measured or predicted here, at any scale;
- the witnesses are synthetic finite graphs, not gradient descent, architecture
  search, or any real curriculum;
- DU-1 does not say a training theorem is impossible **given** a registered
  `D`; it says one cannot be derived without it. Registered-`D` theorems remain
  an open and legitimate research target;
- the empirical obligations for resource maps, developmental reachability
  evidence and prospective replication are unchanged.

Terminal: `GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_GREEN_AT_FINITE_SCOPE`.

## 7. Parent mathematics and contribution boundary

The parent facts are elementary: reachability in a finite directed graph,
non-commutativity of function composition, and monotonicity of an infimum
under set inclusion. The uncomputability of unrestricted reachability is the
package's existing boundary theorem and is cited, not reproved. No novelty is
claimed for any of them. The contribution is the identification that the
registered package's open training items are underdetermined rather than
merely unproved, the bound/verdict asymmetry of DU-3, and the finite
non-extrapolation result DU-4, each with an exact witness.
