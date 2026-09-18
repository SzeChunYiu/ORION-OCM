# AG6 — named results

Scope token for every result below: `MEALY_2x2` on `W` (all `{0,1}`-words of length `0..3`),
3840 tasks, exactly as frozen in `FREEZE_V1.md` (commit `243ec345`, before any implementation
file existed).

Throughout, **registered universality** of a basis means: the basis realizes every one of the 256
machines on every one of the 15 words. It is a finite, scope-bounded property. It is **not** Turing
universality, and nothing here is evidence for Turing universality of any basis. Turing
universality of combinatory logic belongs to Schönfinkel and Curry, of elementary cellular automata
to Cook, of counter machines to Minsky; see `PARENT_LEDGER.md`.

---

## AG6B-1 — a combinatory / rewrite basis at the registered scope

**Statement.** Let `CMB` be the rewrite system with generators `S` and `K`, one binary application
former, and exactly the two rules `S x y z -> x z (y z)` and `K x y -> x`. For every machine
`m` in `MEALY_2x2` there is a closed `S`,`K` term `T_m`, produced from a lambda specification by
Curry-optimized bracket abstraction, such that for every `w` in `W` the frozen decoding procedure
applied to `T_m <w>` returns exactly `out_m(w)`.

**Evidence.** 3840/3840 exact matches, 0 mismatches, 0 budget exhaustions. Maximum contractions on
any single task `403`; total `1,107,456`. Term sizes `249..297` nodes under the optimized
abstraction, `147,821..171,149` under the naive one.

**Quantifiers.** For all 256 machines, for all 15 words. Not: for all words, not: for all
transducers, not: for all computable functions.

**Assumptions.** The encoding convention is part of the basis package: words are Church fold-lists
over Church booleans, and the output is read by the frozen `PAIRIFY`/`NILP` probe sequence. A
different convention is a different basis package and may charge differently.

**Falsifiers.** One `(m, w)` pair whose decode differs from `out_m(w)`; a decode that returns
neither `K` nor `K (S K K)` for a bit position; a task that exhausts the 200,000-contraction budget.

**Strongest parents.** Schönfinkel 1924; Curry 1930; Turner 1979 for abstraction optimization;
Church and Rosser 1936 for confluence.

**Forbidden extrapolations.** `COMBINATORY_BASIS_TURING_UNIVERSAL_PROVED_HERE`,
`UNIVERSAL_SIMPLICITER`.

---

## AG6B-2 — a cellular / local basis at the registered scope

**Statement.** Let `CEL` be the one-dimensional synchronous cellular automaton with a finite cell
alphabet and a single radius-1 local rule `d : Sigma^3 -> Sigma`. For every machine `m` in
`MEALY_2x2` there is such a rule `d_m`, together with the frozen initial-configuration convention,
whose terminal configuration carries exactly `out_m(w)` on the output track, for every `w` in `W`.

**Evidence.** 3840/3840 exact matches, 0 mismatches, 0 cap hits; at most `4` synchronous sweeps per
task; total sweeps `12,544`. Alphabets `10..18` symbols, each the least set containing the initial
cells of all 15 runs and closed under `d_m`; closure violations `0` on the probed machines.

**Locality is measured, not assumed.** Over `Sigma^3` for machine 0: varying the left window
coordinate changes the result on `640 / 4500` pairs; varying the right coordinate changes it on
`0 / 4500`. A `POINTWISE` control rule that ignores both neighbours scores `0 / 4500` on the left
coordinate and fails `12` of the 15 words. This is the same contrast AG5 measured for
`NEIGHBOR_UPDATE` (680/756) against `POINTWISE` and `GLOBAL_BROADCAST` (0/756), re-run for this
rule. The rule is therefore **one-sided**: radius 1, with a measured dependence on two of the three
window coordinates.

**Quantifiers.** For all 256 machines, for all 15 words, on the declared tape layout.

**Falsifiers.** A task whose output track differs from `out_m(w)`; a live head after the sweep cap;
a reachable cell value outside `Sigma_m`; a locality violation on the factorization checker.

**Strongest parents.** von Neumann 1966; Codd 1968; Smith 1971; Margolus 1984; Cook 2004;
Hedlund 1969 for the characterization of cellular automata as exactly the shift-commuting
continuous maps. Inside this corpus, `gmi-833-ag5-extension-lowering-v1` owns the measured
structure-dependence of `NEIGHBOR_UPDATE`.

**Forbidden extrapolations.** `CELLULAR_BASIS_TURING_UNIVERSAL_PROVED_HERE`.

---

## AG6B-3 — the three bases compared on one charged frame (overhead)

**Statement.** On the identical 3840-task set, with **one step** defined as one application of that
basis's own one-step relation, the attained per-semantic-unit bounds are

| basis | `max steps / (|w| + 1)` | class | declared-range bound | class |
|---|---|---|---|---|
| `REG` | `11/2` (machine 80, word `111`, 22 steps) | `ATTAINED` | `10/1` | `VACUOUS` |
| `CMB` | `403/4` (machine 160, word `000`, 403 steps) | `ATTAINED` | `200000/1` | `VACUOUS` |
| `CEL` | `1/1` (machine 0, empty word) | `ATTAINED` | `4/1` | `VACUOUS` |

Cross-basis: `max CMB/REG = 397/16`, `max CEL/REG = 1/4`, totals
`CMB/REG = 8652/457`, `CMB/CEL = 618/7`, `REG/CEL = 457/98`.

**The vacuity classification is the point.** Each row states both a bound that a witness attains and
the bound implied by the quantity's own declared range. The second is `VACUOUS` in every row even
though a tightness-by-attainment test cannot see that, because attainment only detects vacuity for
lower bounds. Every bound published by this package carries its class.

**Assumptions.** A step is basis-relative in wall-clock terms. No claim is made that one `CMB`
contraction and one `CEL` sweep cost the same. `CROSS_BASIS_COST_UNIT_COMMENSURABLE` is forbidden.

**Falsifiers.** A task exceeding its attained bound; a bound whose class is wrong under the
classifier; a task hitting a budget cap.

---

## AG6B-4 — description bias is basis-relative, and at this scope not compiler-relative

**Statement.** Rank the 256 machines by compiled artifact size within each basis. Over the
`32,640` unordered pairs:

| comparison | concordant | discordant | tied in first only | tied in second only | tied in both | `tau_a` |
|---|---|---|---|---|---|---|
| `REG` vs `CMB` | 17,491 | 2,332 | 6,510 | 3,985 | 2,322 | `5053/10880` |
| `REG` vs `CEL` | 11,164 | 4,404 | 3,976 | 8,240 | 4,856 | `169/816` |
| `CMB` vs `CEL` | 10,591 | 5,934 | 3,019 | 9,808 | 3,288 | `4657/32640` |
| `CMB` optimized vs `CMB` naive | 26,333 | **0** | 0 | 0 | 6,307 | `1549/1920` |

**Reading.** Every cross-basis comparison has a strictly positive discordant count, so the
disagreement is genuine and not an artefact of ties. The two bracket-abstraction algorithms — naive
and Curry-optimized, differing by roughly a factor of 580 in absolute size (`249..297` against
`147,821..171,149`) — produce **zero** discordant pairs, so the cross-basis conclusion does not
depend on which abstraction algorithm is charged.

**A sharper form of the same fact.** `REG`'s artifact size takes only 5 distinct values and is a
closed form `40 + 3 * popcount(delta)`: it is completely blind to the output table. `CMB`'s size
takes 9 values and responds to every one of the 8 table bits, because the Church booleans `T = K`
and `F = K (S K K)` have sizes 1 and 5. `CEL`'s size takes 6 values, spans `1930..14418`, and is
driven by reachable-alphabet diversity. Three bases, three different notions of which machine is
simple.

**On the step coordinate**, `CEL` is constant at `49` for all 256 machines, so all `26,880`
`CEL`-untied pairs vanish and `tau_a` against `CEL` is `0/1` with `tau_restricted` undefined. The
cellular basis's time cost carries no information about which machine it is running.

**Falsifiers.** A cross-basis comparison with zero discordant pairs; a nonzero discordant count
between the two abstraction algorithms; a size that violates the `REG` closed form.

**Forbidden extrapolations.** `BASIS_INDEPENDENT_DESCRIPTION_SIZE`.

---

## AG6B-5 — reachability geometry separates the three bases

**Statement.** On the pre-registered probes (machines `0, 85, 170, 255`, word `010`), over the
corridor of the deterministic run together with every one-step successor of every corridor
configuration under the basis's *full* one-step relation:

| basis | corridor | max out-degree | branching configurations | terminal |
|---|---|---|---|---|
| `REG` | 18 | 1 | 0 | 1 |
| `CEL` | 5 | 1 | 0 | 1 |
| `CMB` | 345 / 347 / 349 / 351 | **217** | 342 / 344 / 346 / 348 | 1 |

**Confluence.** For `CMB`, every branching configuration has all of its one-step successors sharing
one normal form: `342/342`, `344/344`, `346/346`, `348/348` across the four probes, with `0`
divergent. Since all successors share a normal form, every pair of them joins; this is the
registered-scope instance of Church–Rosser, consumed from the parent rather than proved here.

**Bounded reachable set.** From the probe start under the full relation the reachable set exceeds
the node cap of `50,000` in every probe. That figure is published as
`LOWER_BOUND_ONLY`, not as an exact count.

**Reading.** The register and cellular bases are path-shaped: one successor, no choice, no
confluence question to ask. The combinatory basis is a lattice: up to 217 redexes at once, hundreds
of branch points, and a confluence obligation that the register and cellular bases never incur.
This is a geometric difference, not a cost difference, and it survives any resource normalization
because it does not mention resources.

**Falsifiers.** A branching configuration with two successors of different normal forms; an
out-degree above 1 in `REG` or `CEL`; a corridor that reaches its cap.

---

## AG6B-6 — developmental search burden, and the obstruction to its uniform-enumeration reading

**Statement, part 1 (the obstruction, proved).** The uniform-enumeration reading of search burden —
enumerate artifacts in canonical size order until one realizes the target — is not executable
across all three bases. The cellular rule space over the largest registered alphabet has exactly
`18 ** (18 ** 3) = 18 ** 5832` rules, a number with `7322` decimal digits. No bounded enumeration
reaches a realizing rule. This tranche does **not** repair that by declaring a restricted rule
schema: choosing a restriction in order to make the fourth comparison measurable would narrow the
row to close it, and the restriction would dominate the answer.

**Statement, part 2 (what is measured instead).** The one-edit local-search landscape, frozen before
measurement. An artifact is a list of typed slots with finite domains; one edit replaces one slot's
value. On the pre-registered subsample `S16` (machine indices `0, 16, ..., 240`):

| basis | neighbourhood | preserving | preserving fraction | viable | viable fraction |
|---|---|---|---|---|---|
| `REG` | 4,496 | 1,480 | `185/562` | 1,552 | `97/281` |
| `CMB` | 2,288 | 350 | `175/1144` | 373 | `373/2288` |
| `CEL` | 290,228 | 286,893 | `286893/290228` | 286,893 | `286893/290228` |

`CEL`'s preserving count uses the exact fact that an edit to a rule entry never queried by any of
the 15 runs cannot change any run; the shortcut was validated by brute force on 200 sampled unused
entries with `0` failures.

**Neutral mutation, three slots at once, 200 draws from machine 0** (reported, not gated):
`CMB` 7 still realize machine 0 and 10 realize some machine; `REG` 29 and 32; `CEL` 185 and 185.

**Reading.** The three landscapes differ by two orders of magnitude in neutral-mutation density.
The register basis is moderately robust, the combinatory basis is the most brittle per slot, and
the cellular basis is almost entirely inert because its artifact is dominated by rule entries the
registered runs never reach. "One edit" is basis-relative; that is the declared description bias,
not a hidden assumption.

**Falsifiers.** A preserving edit to an unused cellular entry; a neighbourhood count that includes
the identity edit; a `viable` artifact whose behaviour is not in the registered behaviour index.

**Forbidden extrapolations.** `SEARCH_BURDEN_BASIS_INDEPENDENT`,
`UNIFORM_ENUMERATION_SEARCH_BURDEN_MEASURED`.

---

## AG6B-7 — the capability/resource frontier law does **not** survive across the three bases

**Statement.** Let `Q(m)` be the frozen three-task capability battery (`IDENTITY`, `COMPLEMENT`,
`CONST0` over `W`; integer in `[0,45]`, observed `7..23`, 17 distinct values), and let `C(m)` be the
charged artifact size in a basis. Take the law object of
`research/machine-intelligence-morphogenesis-v1/PHASE_LAW_V1.md`: the Pareto-undominated set over
`(Q, C)`. Then the three bases give **three different frontiers**:

| basis | frontier | size |
|---|---|---|
| `REG` | `{0, 1, 2, 3}` | 4 |
| `CMB` | `{3, 7, 11, 15}` | 4 |
| `CEL` | `{0,1,2,3,16,17,18,19,32,33,34,35,48,49,50,51}` | 16 |

Pairwise: `REG` vs `CMB` intersection 1, symmetric difference 6; `REG` vs `CEL` intersection 4,
symmetric difference 12; `CMB` vs `CEL` intersection 1, symmetric difference 18. Verdict:
`LAW_DOES_NOT_SURVIVE`.

**Why the verdict is attributable to the basis and not to the accounting.** The frontier depends on
`C` only through the within-basis ordering of `C`. It is therefore invariant under every strictly
increasing map applied **uniformly to all 256 machines of one basis** — the class that contains unit
changes, affine rescalings, division by a basis constant and monotone reparametrizations. This was
checked executably for `x -> 7x`, `x -> x + 1000` and `x -> x^2`: the frontier is unchanged in all
three bases under all three. So no uniform resource normalization can make the three frontiers
agree.

**Scope of the invariance — stated, because the stronger reading is false.** The invariance class is
*uniform* strictly increasing maps. It does **not** include machine-dependent reweighting. A
reweighting by `C_i * (1 + (i mod 7))` moves the `REG` frontier from 4 elements to 1; that is a
registered hostile, and `PARETO_FRONTIER_INVARIANT_UNDER_ARBITRARY_RESOURCE_NORMALIZATION` is a
forbidden promotion.

**Vacuity and degeneracy guards, applied before the verdict is read.** No frontier is of size 1 or
256. On the size coordinate all three cost vectors are non-constant (5, 9 and 6 distinct values), so
the comparison is marked `decisive`. On the step coordinate the cellular cost is constant across all
256 machines, so its frontier degenerates to `argmax Q`; that coordinate is marked
`DEGENERATE_CONSTANT_COST` and **does not carry the verdict**, even though it happens to give the
same `LAW_DOES_NOT_SURVIVE` reading with frontiers 16, 16 and 28.

**What this does and does not say.** `Q` transfers across the bases exactly, because realization is
exact: the same machine has the same capability in all three. What fails to transfer is the
*frontier*, that is, which machines are worth building. Universality is common to the three bases
and carries no information about that; the description bias of the basis does. This is the AG6
thesis — universality is a lower-bound null — in its quantified form, and it is a negative about
transfer, not about the bases.

**Falsifiers.** Two bases with equal frontiers on the size coordinate; a frontier that moves under a
uniform strictly increasing normalization; a frontier of size 1 or 256; a cost coordinate that is
constant and still used for the verdict.

**Strongest parents.** `PHASE_LAW_V1.md` owns the frontier law's shape;
`gmi-833-aj12-foundation-substrate-relativity-v1` owns the formalization-style relativity reading.

**Forbidden extrapolations.** `MI_LAW_PROVED_BASIS_INVARIANT`, and equally its negation stated
beyond this scope: this is one law object, one capability battery, one registered semantic class.

---

## Two materially independent routes

Route B (`independent_oracle_v1.py`) imports nothing from route A and nothing from any parent
module. It evaluates the **source lambda term directly** by capture-avoiding substitution under
normal order and compares de Bruijn normal forms, so bracket abstraction and the `S`/`K` machine are
both bypassed; it runs the cellular automaton as an explicit rule table applied as a block map over
shifted sequences with a worklist alphabet closure; it re-derives the register program from the
declared specification with an integer-coded dispatch interpreter; it counts Kendall's five
quantities by a Fenwick sweep plus value-multiplicity arithmetic instead of the pair loop; and it
computes the Pareto frontier by sort-and-sweep instead of the domination loop.

**Agreement set, all exact and all agreeing:** realized machines 256/256/256; 3840 tasks; 148
distinct behaviours on `W`; size ranges for all three bases; `REG` and `CEL` step ranges;
capability range and distinct-value count; all five Kendall counts for all three cross-basis
comparisons; all three size-coordinate Pareto frontiers and their pairwise symmetric differences;
`REG` corridor 18, `CEL` corridor 5, `CMB` corridor 345, `CMB` max out-degree 217 and confluence
342/342.

**Declared out of the agreement set:** the `CMB` step counts. A contraction count is a property of a
reduction strategy and a term representation; route B counts beta-steps on lambda terms, which is a
different quantity. This follows AJ5 and AG5, where charged instruction counts are likewise excluded
from transfer.

## Hostiles and nulls

13 hostiles, each detected and each paired with a clean control that is silent: transposed `S`
contraction (90 induced mismatches against 0), bracket abstraction emitting `S` with exchanged
arguments, a decoder probing with `K` instead of `K I`, a planted radius-2 dependence in the
cellular update (504 locality violations against 0), a pointwise control rule, a cellular alphabet
trimmed out of closure (9 violations against 0), `DECJZ` without its decrement, swapped `EMIT`
operands, Kendall with concordant and discordant exchanged, Pareto with reflexive domination,
the vacuity classifier fed the declared range maximum, the identity edit counted as an edit, and
machine-dependent reweighting of the cost.

One further perturbation — the unsound eta rule `abs(x, M x) = M` without the side condition — was
found **inert on this term family**: it compiles to a byte-identical term for all 256 machines,
because `M x` with `x` free in `M` never occurs here. It is therefore recorded as an excluded
perturbation that cannot move the quantity it perturbs, and is **not** counted among the hostiles.

Nulls, randomized-semantics in AG2's style: all `119` non-identity permutations of the five
register opcode roles (exhaustive), all `11` non-identity variants of the two combinatory
contraction rules (exhaustive), and `200` random non-identity relabelings of the cellular alphabet
reproduce the full 3840-task census `0` times.

No-alarm case on the true configuration: realization mismatches 0, cap hits 0, closure violations 0,
locality violations 0, undetected hostiles 0, nulls reproducing the census 0. 9 of 9 gates pass;
98 of 98 tests pass in both normal and `-O` mode.
