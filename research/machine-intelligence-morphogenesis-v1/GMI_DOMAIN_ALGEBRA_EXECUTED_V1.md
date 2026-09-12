# GMI Domain Algebra — deriving the domains of machine intelligence from the normal form, with executed receipts (V1)

Status: **FORMAL DERIVATION WITH EXECUTED EXACT RECEIPTS AT SCOPE.** Every theorem below is either proved from the
definitions or decided by a named receipt in `microscopes/results/`; none is an empirical claim about real systems.
Issue #422. Companions: `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` (the D1–D9 taxonomy), `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md`
(the candidate programme), `GMI_DOMAIN_DERIVATION_COMPLETENESS_V1.md` and `GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md` (the
parallel lane's derivation and hypotheses), `GMI_THEORY_CORE_V3_EXECUTED.md` (laws L1–L7).

What this document adds: the taxonomy of domains is not a list to be curated, it is **generated** by the normal form, and
the relations between domains are **crossover laws** of the same family as the executed compile-amortization law L4. Three
of the six theorems were produced by failed clauses of frozen predictions and are marked as such.

---

## 1. Setting

A realization is `M = (Z, K, U, Γ, κ, ρ)`: sufficient developmental state `Z`, execution law `K`, update law `U`,
morphogenesis `Γ`, interface `κ`, resource semantics `ρ`. The morphology IR (`gmi_microscope/morph.py`) fixes a neutral
primitive alphabet: state kinds (`DENSE`, `TABLE`, `KVSTORE`, `PROGRAM`, `VERSIONED`, …), execution kinds (`EDGE`,
`LOOKUP`, `NEAREST`, `SCORESELECT`, `LINEAR`, `AFFINE`, `PROGEXEC`, …), update kinds (`GRAD`, `CLOSEDFORM`, `INSERT`,
`SEARCH`, `PMUTATE`, …), verification kinds (`VERIFY`, `ABSTAIN`, `ROLLBACK`), history (`EVIDENCE`) and compilation
(`MATERIALIZE`, `SHADOW`). An **ecology** `e` fixes an obligation, a development schedule and an intervention family; the
**developmental response** `R_{E,J}(M)` is the exact served trace under every registered `(e, j)` (`gmi_microscope/ecology.py`).

**Definition (bounded reduction).** `M_1 ≼_B M_2` iff there is a compiler `C` with `R_{E,J}(C(M_1)) = R_{E,J}(M_1)`,
`C(M_1)` built from `M_2`'s carrier and law, and lifecycle burden overhead bounded by a declared function `B` of the state
size. A **domain** is a class of the symmetric part of `≼_B`; a **new domain** is a class with no `≼_B` arrow into D1–D9
that additionally changes the frontier in a predicted niche and recurs under neutral search and reminting
(criteria 3–6 of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14).

---

## 2. GMI-DA1 — domain generation

**Statement.** Every realization expressible in the IR is a composition of a state kind, an execution kind and an update
kind; the domains D1–D9 of the taxonomy are exactly the `≼_B`-classes of the nine carrier/law pairs that the alphabet
admits with a single dominant state kind, and D9 (hybrid) is the class of compositions with more than one.

**Proof.** By construction of `morph.KINDS` and `morph.typecheck`: a genotype is a typed port graph whose nodes carry the
class letters `S R T U V G H C D P`; the mechanism vector `morph.mechanism_vector` counts them. Two genotypes with the same
dominant `S` kind and the same `U` kind are inter-compiled by renaming ports (bounded), which is the identity compiler; two
with different dominant `S` kinds are not, since the served state of one is not a value of the other's type. ∎

**Status:** `PROVED_AT_SCOPE` (the scope is the IR alphabet). **Receipt:** `STAGE_B0_EQUIVALENCE_METERING_V1.json`
(the equivalence harness that decides `R_{E,J}` equality; 16 implementation-equivalent rewrites merged, 5 collision pairs split).

**Consequence.** The question "how many kingdoms of machine intelligence are there?" is, at scope, the question "how many
carrier/law pairs does the primitive alphabet admit, up to bounded reduction?" — a question about the *alphabet*, not about
the history of the field. Enlarging the alphabet is therefore the only way to add a kingdom, which is why candidate domains
must be argued at the level of primitives (`DC1`–`DC9`, `N3`, `N8`, `N10`, `N11`), not at the level of architectures.

---

## 3. GMI-DA2 — lazy/eager duality (the composite-carrier theorem)

**Statement.** Let a carrier hold composite objects built by an associative, invertible binding operator `⊗` from atoms of
a codebook `A`. Then the **lazy** realization (store `A`, compute `a ⊗ b` on demand) and the **eager** realization (store
every composite `a ⊗ b` reachable in the registered query family) are exactly developmentally equivalent, and their
lifecycle costs differ only by

```
Δdesc   = (|composites| − |A|) · (bits per object)        (in the eager realization's favour: negative)
Δserve  = depth · (cost of one binding)                    (in the lazy realization's disfavour)
H*      = (Δdesc + materialization) / Δserve
```

so the eager realization wins above the reuse horizon `H*` and the lazy one below it.

**Executed decision.** `STAGE_DC_V24_DC1_VSA.json` (record `RV-377-044`). The hyperdimensional carrier (binding = XOR,
cleanup = nearest codebook item) and the materializing exemplar parent returned **identical answers in all 7 cells**; the
description ratio was exactly `R^depth · F / (R + F)` (2.667 at depth 1, 10.667 at depth 2, independent of the hypervector
width); the serve surplus was exactly `depth · D`; and all five predicted crossovers were hit to two decimals
(54.50, 53.25, 193.25, 189.62, 187.81 against 54.5, 53.25, 193.25, 189.6, 187.8).

**Status:** `PROVED_AT_SCOPE` for the executed instance; the general statement is `PARENT_THEOREM_UNDER_ASSUMPTIONS`
(it is the memoization/compilation trade-off of the caching literature, applied to an algebraic carrier).

**Consequence for the taxonomy.** DC1 (hyperdimensional / vector-symbolic) is **not** a kingdom: it is the lazy phase of
D2. The cost law says *when* the field's preference for it is right — short reuse, deep structure — and law L4 of the
theory core already governs that axis. Symmetrically, DC3 (energy landscape) is the *lossy eager* phase of D2.

---

## 4. GMI-DA3 — depth relativization of the domain criterion

**Statement.** With `R` roles and `F` fillers and structure depth `d`, the crossover of GMI-DA2 is

```
H*(d) = [ (R^d·F − (R+F))·(bits) + R^d·F·D·d ] / (d·D)   ~   R^d / d
```

which is unbounded in `d`. Hence the bounded reduction of GMI-DA2 exists at every **fixed** depth and no single reuse
horizon amortizes it over a family of **unbounded** depth: criterion 3 of the domain-novelty criterion is not a property of
a carrier alone but of a carrier **and a declared depth bound**.

**Executed decision.** `RV-377-044` clause 7 (held). **Status:** `PROVED_AT_SCOPE_UNDER_A_NAMED_BINDING_OPERATOR` —
see the correction below.

**Correction forced by `RV-377-065`** (`GMI_DEPTH_GATED_KINGDOM_V1.md`, receipt `STAGE_DK_V1_DEPTH_GATED.json`). The
formula above is the crossover against an opponent that materializes `R^d·F` bindings, and that opponent is
**parent-maximal only when the binding operator's path code is injective**. XOR binding — the law `RV-377-044` executed —
is commutative and involutive, so a path composes to the parity of its role multiset and the measured image is
`4, 7, 8, 8, 8, 8` at depths 1–6, saturating at `2^R`. Against an opponent that materializes one bundle per **distinct**
composition, the store is bounded by `2^R·F` vectors uniformly in depth (≤ 4 618 bits at `D = 64` against the carrier's
864, a constant factor 5.3449), the crossover never exceeds its depth-1 value, and **a single bounded reduction covers
the whole unbounded-depth family**. The formula overstates the parent-maximal store by `R^d/|image|` = 1, 16/7, 8, 32,
128, 512 at depths 1–6 and the crossover by 6.5957 at the one depth-2 cell where the comparison is measurable;
`RV-377-044`'s reported depth-2 description ratio of 10.667 becomes **4.667**. With the PERMUTE primitive of DC1's own
declared native basis protecting the role at path position `i`, the image is exactly `R^d` and the statement above is
executed as written to depth 6 against the strongest opponent constructed: parent-maximal `H*(d)` = 54.5, 22.75, 80.875,
303.25, 1167.4375, 4556.35 at `D = 64`, with consecutive ratios rising strictly towards `R = 4`. Even there the carrier
never excludes the opponent from the frontier: an unbounded crossover is not an unoccupied cell.

**Theory correction this forces.** `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 criterion 3 ("no bounded
semantics-preserving reduction to existing domains over the registered family") must be read with the registered family's
**structure-depth bound** stated. Without it the criterion is neither true nor false. This is now gap **DG-3**.

---

## 5. GMI-DA4 — the capacity/compression gate separation

**Statement.** A compressed carrier that stores `P` items in state of size `S` has two gates:

* the **capacity gate** `P ≤ c(S)` above which its capability fails;
* the **compression gate** `P ≥ p(S)` above which its description is smaller than the explicit store.

Its advertised advantage is reachable only if `p(S) ≤ c(S)`. When `p(S) ≫ c(S)` the carrier is dominated everywhere in
capability-feasible space, and the only surviving niche is a serve-price corner at the capacity edge.

**Executed decision.** `STAGE_DC_V25_DC3_ENERGY.json` (record `RV-377-045`). At `N = 32`: capacity gate between `P = 4`
and `P = 8` (`0.125 N` to `0.25 N`, bracketing the classical `0.138 N`); compression gate at `P* = 124 = 3.9 N`. The
separation is a factor of 31. The exemplar parent was exactly correct (1.0) at every tested pattern count under both
precision instruments, and was the sole frontier occupant of all 48 grid cells **up to the grid that was run**.
*Bound attached 2026-09-12: `RV-377-068` grades this receipt **TRUNCATED, MAJOR**. Its grid stops at `H` = 1024 while
the coupling-field row overtakes the pattern store at `H*` = 1856 exactly, in context `N32_P4_n1` under the wide
instrument at the native price — a factor of 1.812 beyond the grid. "Sole occupant of all 48 cells" is therefore a
statement about `H ≤ 1024` and not about the quadrant; the surviving niche the failed clause found is the same one,
recovered here from the receipt's own coordinates rather than from the prose that first recorded it.* The surviving niche, found by a **failed
clause** of the frozen prediction, is `P = 4` under the native associative-memory price at reuse `H > 1856`.

**Status:** `PROVED_AT_SCOPE` for the executed instance (one pattern set per cell; a second set is the obvious replication).

**Grid correction (`RV-377-068`, gap DG-2 closed).** "The sole frontier occupant of all 48 grid cells" is a statement about
`H ≤ 1024` and must be read that way (protocol rule 21). The standing audit reproduces this receipt's own frontier cell for
cell and then grades it **TRUNCATED, MAJOR**: the coupling-field row occupies zero cells of the reported grid and does
occupy cells beyond it, with the crossover recomputed independently at exactly `H* = 1856` in the `N32_P4_n1` cell under the
wide instrument at the native price. The re-run on a grid extended past that crossover changes **no cell the receipt already
reported** and adds 216 it never reported, which is where the denied occupant appears. The factor-of-31 gate separation and
every capability in the receipt are untouched: `H` enters only the cost model, never the execution.

**Consequence.** "Compressed memory" is not a kingdom-making property. The executed statement is sharper and more useful
than the usual qualitative one: *a compressed carrier earns its place only where its compression gate precedes its capacity
gate*, and for Hebbian couplings at this scale it does not, by a factor of 31.

---

## 6. GMI-DA5 — precision as a domain gate

**Statement.** Carrier admissibility is a function of the arithmetic instrument, not only of the carrier and the ecology.
Two instruments executing **identical charged operation sequences** at different precisions can differ in admissibility;
therefore every domain claim must name its instrument.

**Executed decision.** `RV-377-045` clause 1 (held): under the registered 8-bit fixed-point universe the energy carrier is
inadmissible at **every** pattern count (field sums saturate), while under the declared wide-integer instrument with the
same charged op sequence it is admissible to `P = 4`. The probabilistic carrier showed the same gate earlier
(`RV-377-029`/`031`). `gmi_microscope/dc_energy.py::Arith` implements both instruments.

**Status:** `PROVED_AT_SCOPE`. This **closes gap G5** of the theory core for these microscopes: the wide-precision
instrument is no longer a declared intention but an executed column.

**Executed consequence (`RV-377-066`, `STAGE_DK_V2_PRECISION_GATED.json`, `GMI_PRECISION_GATED_KINGDOM_V1.md`).** The kingdom question has now been asked on this axis. On a declared ambiguous-evidence ecology **no carrier of any registered kind is admissible in the 8-bit universe** — all ten rows score exactly 0.0, while the closest 8-bit-grid answer to the Bayes probability would score 0.910880 — and at **10 total bits (5 fractional)** and above, every frontier cell of all 20 (instrument, price, description-basis) keys is occupied by a probabilistic carrier and by no 8-bit-admissible one. GMI-DA5 therefore upgrades from a statement about **admissibility** to a statement about **occupancy**: the arithmetic instrument is a *kingdom* parameter, new gap **DG-6**. Two qualifications are executed alongside it: on a second, noisy-label ecology a quantized-count posterior reaches θ at 8 bits (0.863997) and occupies every cell, so precision is not a kingdom-maker in general; and inside the kingdom the occupant is the pruned or count-based realization, not exact inference (the exact posterior holds 0 of 42 reduced-price cells, crossover H* = 52/84 = 0.619048 queries). Consequently the §9b terminal below is a statement about the **8-bit** universe, and each of the eleven reduction verdicts inherits an instrument qualifier.

---

## 7. GMI-DA6 — the reliability index of a stochastic carrier

**Statement.** For a carrier whose development consumes randomness, admissibility is a **distribution over seeds**, and the
frontier is a step function of the declared reliability `q` (the fraction of seeds at or above `θ`). Frontier tables
without a declared `q` are `q = 0.5` tables.

**Executed decision.** `STAGE_DE_S3_SEED_CENSUS_V1.json` (`RV-377-040`): the particle carrier is admissible on
**9 of 192 runs (4.6875 %, `1/q` = 21.33 draws)** — the "10 of 192, about 5 percent" carried here until 2026-09-12 was an
**off-by-one**, corrected by `RV-377-067` — with seed-medians 0.39–0.60 and maxima up to 0.9583.
`STAGE_DE_SMOOTH_V22_SYM5_S4.json` (`RV-377-041b`) reported that on an admissible seed the same carrier is the cheapest
admissible form, taking 14 of 56 frontier cells in the scan-store columns, 50 of 56 in the native-store column and 56 of
56 in the native-stochastic, uniform and compressed-program columns, with **all five clauses held**.
**Every occupancy figure in that sentence is superseded by §7b, where the carrier takes 0 of 336 cells and the record
keeps 2 of its 5 clauses.**

**Status:** `PROVED_AT_SCOPE` for the reliability statement; **the cost statement above is superseded — see 7b.**

### 7b. GMI-DA6 corrected by `RV-377-067` (gap G14 closed): the cheapest admissible form was the most expensive one

Gap G14 is now executed, and it inverts the cost half of this section rather than qualifying it. Charging the failed draws
through the burden vector's own terms (`B_search`, `B_failed_candidates` from `gmi_microscope/vm.py::lifecycle_vector`),

```
C′(row, H, r) = C(row, H, r) + B_search,   B_search = (1/q − 1) · D_draw
D_draw = exec + upd + ver + rev of ONE complete run of the registered protocol
```

the particle carrier occupies **0 of 336** frontier cells — none in any of the six columns, at either declared reliability —
against the 14/56 to 56/56 reported above. `RV-377-041b` re-adjudicated clause by clause keeps **2 of its 5 clauses**, and
they are exactly the two that are not cost claims (admissibility at size 8, and the identity of the non-stochastic cells).
The charge is between **9.5 and 32 729 times** the cheapest competing row's entire registered lifecycle cost across the
336 cells, and the carrier's break-even reliability is **q\* = 0.4992–0.8426** by column against a measured 1 seed in 32.
The re-entry crossover exists but lies at H = 4.2 × 10⁷ to 1.2 × 10⁹ (reported per gap `DG-2`, whose audit instrument is now standing).

Two further corrections this forces on the text above:

* the census rate is **9 of 192 runs (4.6875 %, 1/q = 21.33 draws)**, not the "10 of 192 runs (about 5 percent)" stated in
  §7 and in `RV-377-040`: the committed census receipt's own per-cell counts are 1 + 2 + 0 + 4 + 1 + 1 = 9, and a recount
  over its 192 raw capability values agrees. The published figure is off by one run;
* the theory core's two-regime answer ("at low reliability a stochastic search form dominates because its lifecycle burden
  is the smallest of all") has the wrong sign once the lottery is paid for. The corrected statement is that **lowering the
  declared reliability moves a stochastic carrier into the admissible set and out of the cheap set at the same time**,
  which is **protocol rule 35**.

**Receipt:** `STAGE_G14_FAILED_DRAW_CHARGING_V1.json` (`RV-377-067`, 6 of 8 clauses; clauses 2 and 5 failed and kept).

---

## 8. Placement of every candidate examined so far

| candidate | carrier | verdict | receipt / status |
|---|---|---|---|
| DC1 hyperdimensional / VSA | superposed hypervector | **lazy phase of D2** (GMI-DA2, GMI-DA3) | `RV-377-044`, 6/7 clauses, `REDUCED_TO_PARENT(D2)` at fixed depth |
| DC3 energy landscape | coupling field | **lossy eager phase of D2** (GMI-DA4, GMI-DA5) | `RV-377-045`, 5/7 clauses, `REDUCED_TO_PARENT(D2)`, dominated on the grid |
| DC4 population-hereditary | multiset of candidates | **D7 × D5 with A5** | `RV-377-040`, `RV-377-041b`, `RV-377-023`, `RV-377-028`; `REDUCED_TO_PARENT` |
| DC2 self-organizing field | lattice with a shared local rule | expected **D6 + weight sharing** | `REGISTERED_FOR_EXPERIMENT` (worker branch `claude/gmi-domain-dc2-dc7-dc9`) |
| DC7 quantum cognition | amplitude vector | expected **D3 with an amplitude state** | `REGISTERED_FOR_EXPERIMENT` (same branch) |
| DC9 oscillatory / phase | phases | expected **DC1 in a different code** | `REGISTERED_FOR_EXPERIMENT` (same branch) |
| DC5 molecular, DC6 analog | molecule counts, continuous physical state | **substrate variants** (price vectors, GMI-DA5) | `REGISTERED_FOR_EXPERIMENT` |
| DC8 stigmergic | environment-written field | **D2 + D6 with a priced world step** | `REGISTERED_FOR_EXPERIMENT` |
| N3 relational-constraint / sheaf | constraint system with gluing | **reduced**: answers bit-identical to BOTH a constraint/table parent and a program-search parent; its serve law falsified out of sample (28 of 32 checks) | `REDUCED_TO_PARENT(D2 × D4/D5)`, `RV-377-050` |
| N10 event-causal / partial order | partial order of events | **reduced**: identical to both relational parents under the wide instrument; interleaving-invariant where the sequence parent is not; 8-bit instrument gates it at chain length 12 | `REDUCED_TO_PARENT(D2 × D4/D5)`, `RV-377-051/052` |
| N8 constructive / autocatalytic | closure of a construction set | **reduced**: exact serve-time equality with the memory parent in 6 of 6 cells at overhead factor 1.0; closure growth 1.7549^L; native-price crossover 45–1 499 | `REDUCED_TO_PARENT(D2 × D5)` |
| N11 invariant / obstruction | an invariant certifying impossibility | **reduced — the decisive one.** Against a naive exhaustive search the separation is real (serve `d(2m+2)`, constant in k, against `2m + 3m(2^k − 1)`, ×4.00 per 2 bits over five sizes), but against the STRONGEST parent — a dense-coefficient row computing the same annihilator by row reduction — the answers are identical in 10 of 10 cells and the advantage collapses to the constant factor `(m − d)/d` = 4, 7, 11, 15, 23 | `REDUCED_TO_PARENT(D1, annihilator/dual presentation)` |
| DC2 self-organizing field | lattice with a shared local rule | **reduced**: identical answers in exactly the 60 of 144 cells where the weight-sharing-ablated parent is capable | `REDUCED_TO_PARENT(D6 + translation-equivariant weight sharing)` |
| DC7 quantum cognition | real amplitude vector, Lüders projectors, Born readout | **reduced**: both parents reproduce the whole registered obligation exactly (capability 1.0, zero error); the carrier's value is description parsimony below `H = 32Q − 12` | `REDUCED_TO_PARENT(D3 with an amplitude state)`, `SUBSTRATE_VARIANT` |
| DC9 oscillatory / phase coding | phases in `Z_Q` | **reduced, and unified with DC1**: identical to a phase-coded exemplar store in 66 of 66 (cell, instrument) pairs, and bit-identical to DC1's hyperdimensional row in every `Q = 2` cell — **DC1 is the `Q = 2` special case of DC9** | `REDUCED_TO_PARENT(D2)`, same parent as DC1 |

---

## 9. What would actually make a new kingdom, stated operationally

From GMI-DA1 through GMI-DA6, a candidate must exhibit a carrier whose compilation into the alphabet is **not** bounded by
a declared function of the state size over the registered family. The executed results rule out the two mechanisms that
usually get proposed:

* **compression** (DC3): bounded, and gated behind capacity (GMI-DA4);
* **algebraic superposition** (DC1): bounded at fixed depth, unbounded only in structure depth (GMI-DA3) — which is a
  statement about the *family*, not the carrier.

The remaining live mechanism is **certification of impossibility**: a carrier whose native law produces a witness that a
search parent can only obtain by exhaustion. That is `N11`, and the measured quantity that decides it is the growth of the
parent's exhaustion cost against the candidate's certificate cost over instance size. If that separation is exponential and
survives remint, neutral recovery and parent-team reduction, the programme has a kingdom; if it is polynomial, it is one
more crossover law of the L4 family. Either outcome is recorded.

### 9b. The programme-level prediction, adjudicated

Section 4 of `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` froze the prediction that **no candidate survives criterion 3 at the
exact layer**. Nine candidates have now been executed against matched strongest parents — DC1, DC3, DC9, DC2, DC7 by this
lane and its workers, N3, N10, N8, N11 from the parallel lane's theory-generated hypotheses — and **all nine reduce**.
Seven of the nine exhibit *exact developmental equality* with a parent (identical answers on every registered cell), and
the two that do not (DC3, DC2) are dominated rather than distinct. The prediction held, and it held even for the case it
was least likely to survive: N11, the impossibility-certificate carrier, where the separation against a naive search
parent is genuinely exponential and collapses to a constant factor against the *strongest* parent.

Two things were learned that the prediction did not anticipate:

* **A unification.** DC9 and DC1 are the same carrier at different code radix — the hyperdimensional carrier is the
  `Q = 2` case of the phase carrier — so what looked like two candidate kingdoms is one phase of D2.
* **A criterion defect.** N11 shows that "no bounded reduction to an existing domain" is only meaningful against the
  *parent-maximal* member of that domain. Measured against a weak parent almost any carrier looks new. The
  parent-maximality clause is now `PROVED_AT_SCOPE` as a statement about this programme's own criterion.

**Current honest terminal for the domain programme:**
`NO_NEW_KINGDOM_ESTABLISHED__NINE_CANDIDATES_EXECUTED_AND_ALL_NINE_REDUCED_TO_D1_D2_D3_OR_D6__SEVEN_BY_EXACT_DEVELOPMENTAL_EQUALITY__CRITERION_3_REQUIRES_A_DECLARED_DEPTH_BOUND_AND_A_PARENT_MAXIMAL_OPPONENT`

---

## 10. GMI-DA7 — kingdom closure, and the four axes on which a kingdom can be gained

`GMI-DA1` says the domain count is a question about the alphabet. Eleven executed candidates (`DC1`, `DC2`, `DC3`, `DC7`,
`DC9`, `N3`, `N8`, `N10`, `N11`, `F4`, `F6`) then reduced to parents, eight of them by *exact developmental equality*. That
run of eleven is not eleven independent empirical facts. It is one theorem, and stating it exposes exactly where a kingdom
can still be gained.

**Definition (the closure parameters).** Bounded reduction `≼_B` of section 1 is not a single relation. It is indexed by
four declared parameters, every one of which the executed microscopes fix:

| parameter | what it is | fixed in this lane at |
|---|---|---|
| `A` | the primitive alphabet — the typed kinds of `morph.KINDS`, each with a signature and a charged cost | 34 kinds |
| `d` | the structure-depth bound of the registered task family | `d = 1` for every executed candidate except `DC1`/`DC9`, which were adjudicated at fixed `d` |
| `p` | the arithmetic instrument | 8-bit fixed point, `FRAC_BITS = 4` (with a declared `wide` column at two records) |
| `F` | the ecology family and intervention set the response `R_{E,J}` is quantified over | 5 registered ecologies × 6 interventions |

Write `K(A, d, p, F)` for the set of `≼_B`-classes of carriers expressible over `A` at depth bound `d` and precision `p`,
where `R_{E,J}` ranges over `F`.

**Statement (GMI-DA7).**

1. *Partition.* `K(A, d, p, F)` partitions the set of realizations expressible over `A` at `(d, p)`; every expressible
   machine lies in exactly one class.
2. *Closure.* A candidate carrier `C` introduces a class outside `K(A, d, p, F)` **iff** `C` is not a bounded composition
   over `A` at `(d, p)` with responses separated within `F`. Every carrier implementable in the microscope is by
   construction such a composition.
3. *Monotonicity.* `K` is monotone in all four parameters, in two opposite senses. Enlarging `A`, raising `d` or raising
   `p` enlarges the set of expressible realizations and can only **add** classes. Refining `F` — adding an ecology or an
   intervention — can only **split** existing classes, never merge them, because `R_{E,J}` equality over a larger index set
   is a stronger condition.

**Proof.** (1) is `GMI-DA1` plus the fact that `≼_B`'s symmetric part is an equivalence relation on a set. (2) is
immediate from the definition: a class outside `K` requires a carrier with no bounded compilation from any `A`-composition,
and everything the IR type-checks is such a composition. (3) For `A`, `d`, `p`: the expressible set is monotone in each and
`≼_B` restricted to the old set is unchanged, so old classes survive and new carriers land in old or new classes. For `F`:
if `R_{E,J}(M_1) = R_{E,J}(M_2)` for all `(e, j)` in `F'` ⊇ `F` then the same holds on `F`, so `F'`-equality refines
`F`-equality; classes split and never merge. ∎

**Status:** `PROVED_AT_SCOPE`. The scope is the IR alphabet, the bounded-reduction definition of section 1, and the
equivalence harness of `STAGE_B0_EQUIVALENCE_METERING_V1.json` which decides `R_{E,J}` equality.

### 10a. Corollary — why every candidate reduced, and what the eleven results actually are

Each of the eleven candidates was implemented as a type-checking genotype over `A` at `d` fixed and `p = 8`, and adjudicated
on `F`. By part 2 its reduction was **forced before it was run**. The executed records therefore do not measure whether
these carriers are kingdoms; they measure *which* parent each compiles into and at what cost, which is the useful content
and is what the receipts report. The honest terminal of the domain programme is a statement about the closure parameters,
not about substrate stories:

> No candidate expressible over the fixed alphabet at fixed depth, fixed precision and the registered ecology family can
> be a new kingdom. Eleven were executed; eleven reduced; the theorem says any twelfth of the same kind will too.

### 10b. Corollary — D1 to D9 are read off the type system

The registered domains are exactly the classes generated by the **state-type partition** of `A`, which is the derivation
the programme owed:

| state type in `A` | with update law | domain | occupancy at the registered `(p, q)` |
|---|---|---|---|
| none | — | stateless transducer | occupied |
| `VEC` (`DENSE`) | `GRAD` / `CLOSEDFORM` | **D1** coefficient / function field | occupied |
| `TAB` (`KVSTORE`, `TABLE`) | `INSERT` | **D2** exemplar / indexed memory | occupied |
| `VEC` read as a distribution | Bayes update | **D3** probabilistic | **empty at `p` = 8** (`RV-029`/`031`) |
| `PROG` | `SEARCH` | **D4/D5** symbolic program / deliberative search | occupied |
| `VEC` under an iterated map | — | **D6** dynamical / controller | no kind of its own — gap `DG-1` |
| population of `PROG` | `PMUTATE` | **D7** collective / population | **empty at `q` = 0.5** (`RV-040`/`041b`) |
| `G`-class kinds | morphogenesis | **D8** morphogenetic | occupied |
| more than one dominant state kind | any | **D9** hybrid | occupied |

Two of the nine registered domains are **empty at the registered instrument settings** and one has no primitive of its own.
That is a sharper statement of the taxonomy than "there are nine domains", and it is checkable: raise `p` and D3 should
become non-empty; raise `q` and D7 should; add a `RECUR` kind and D6 should separate from D1.

### 10c. The four escape axes, and who is executing each

Part 3 turns the negative into a search procedure. There are exactly four ways to gain a kingdom, and each is now a
registered experiment rather than a hope.

| axis | what it means | registered experiment | status |
|---|---|---|---|
| `d` — structure depth | `GMI-DA3`: the role-filler crossover `H*(d) ~ R^d/d` is unbounded in `d`, so the bounded reduction exists at every fixed depth and none amortizes over a family of unbounded depth | `RV-377-065`, module `dk_depth.py`, grid extended past the analytic crossover (also closes `DG-2`, `DG-3`) | running |
| `p` — precision | `GMI-DA5`: admissibility is a function of the arithmetic instrument; D3 is empty at 8 bits | `RV-377-066`, module `dk_precision.py`, identical charged op sequences at two instruments, threshold bisected | running |
| `F` — ecology family | part 3: refining `F` can only split classes, so any reduction certified by *exact developmental equality* is certified only against the demands actually posed | `RV-377-070`, the equality-splitting test below | this lane |
| `A` — the alphabet | a new primitive kind with its own signature and charged cost; `DG-1`'s `RECUR` is the smallest instance | registered, not yet executed | `OPEN_NONBLOCKING` |

The `F` axis is the one the programme has been least honest about, because eight of the eleven reductions were certified by
exact developmental equality — identical answers on every registered `(e, j)`. Under part 3 that is not evidence that the
carriers are the same machine. It is evidence that **`F` never asked them to differ**. The test is stated and executed in
`GMI_ECOLOGY_REFINEMENT_KINGDOM_V1.md`.

---

## 11. GMI-DA8 — the register theorem, and the correction it forces on GMI-DA1

`GMI-DA1` asserts that the nine taxonomy domains are **exactly** the `≼_B`-classes the primitive alphabet admits. The A
axis of `GMI-DA7` was executed against that assertion (`RV-377-072`, receipt `STAGE_AXIS_A_V1.json`) and it is **false in
its enumeration half**.

**Statement (GMI-DA8).** Let `C` be any carrier whose state is a single finite-precision value updated by an input-driven
transition `z ← g(z, x)` reading no target. Then `C` is exactly emulated, answer for answer, by a **one-entry store used
as a register** over the registered alphabet:

```
INSERT( tab, key, g( LOOKUP(tab, key), f(INPUT) ) )
```

Every port of that expression is a registered kind, the graph is acyclic — the feedback runs through the state-update
convention, not through an edge — and no `TARGET` is read. The emulation overhead is a **constant**: `desc_store_header +
desc_store_entry` against one declared cell, and an execution ratio that is exactly affine in `1/T`.

**Executed decision.** 3 obligations × 6 stream lengths × 6 rows × 6 price columns = 648 exact charged replays, 9 828
frontier cells.

| quantity | executed |
|---|---|
| iterated map vs register parent, bit-identical answers | **108 of 108 cells** |
| declared description, iterated map | exactly 8 bits at every `T`, every column |
| declared description, register parent | exactly 12 bits at every `T`, every column |
| description overhead | **exactly 4 bits, constant in `T`** |
| execution overhead ratio | exactly `c + k/T` per column (e.g. `6 + 0.5/T`, `1.0618 + 0.006/T`) |
| replay parent description | exactly `2 + 10·T` bits — the only row whose state grows with the horizon |
| frontier cells taken by the register parent | **0 of 9 828** |
| C2 column invariance | 108 groups, 0 violations |

**Status:** `PROVED_AT_SCOPE` at 8-bit fixed point. **Consequence for `GMI-DA1`:** its enumeration half is
`FALSIFIED_AND_REPLACED`. The alphabet admits **eight** carrier classes, not nine. D6 is not a class of its own; it is the
**read-modify-write phase of D2**, and it appeared in the taxonomy because the taxonomy was read off the literature rather
than off the type system. Gap `DG-1` is therefore closed — not by adding the primitive, but by showing the primitive adds
no class.

**A second, sharper fact the same run produced.** The *coefficient* carrier genuinely cannot express an input-driven
transition: `GRAD` is the only update kind producing a `VEC` and it requires a target. So in this alphabet "recurrent" is
a property of the **memory** carrier, not of the continuous one — which is the opposite of how the neural literature
assigns it.

### 11z. What the grid audit did to every occupancy sentence in this document

`RV-377-068` wrote the enforcement instrument gap `DG-2` had only ever described, and ran it over the whole corpus. Of 73
committed receipts carrying a frontier, **64 were graded and 9 cannot be audited from their own contents at all**. Of the
64:

| verdict | count |
|---|---|
| SAFE | 30 |
| **TRUNCATED** | **34** — every one graded MAJOR, none minor |

Worst case: a grid stopping at **1/32 082** of the crossover it implicitly denies. The auditor's positive control
recovered the original instance independently, at exactly `H* = 1856` against a grid maximum of 1024, from the receipt's
own coordinates rather than from the prose that first recorded it.

**This is a defect in more than a third of the programme's frontier claims, this document included.** `GMI-DA4`'s "sole
frontier occupant of all 48 grid cells" and every sentence of the same shape must now be read with its `H` bound
attached: *sole occupant up to the grid that was run*, not sole occupant. The 34 truncated receipts are named in the
audit receipt with their crossovers and the extensions they need.

The second defect class is worse because it is not fixable by re-running: nine receipts report a frontier without the
per-row cost coordinates that produced it, so nobody — the author included — can check their grids. That is now protocol
rule 28.

### 11a. Two defects this run found in the programme's own instrument

Both were found by **failed clauses**, and neither touches the headline, which compares only the two rows above.

* **Charging defect.** The exemplar row's serve path executed a native lookup with **no charged operation**, giving it an
  execution cost of exactly `0.0000` per event while every other row paid 3 to 65. An unmetered serve path silently wins
  every frontier cell at large reuse: at `H = 4 096` it costs 802 against the iterated map's 12 296. That is the whole of
  its 175-cell occupancy. → **protocol rule 21**: every row's serve path must be charged, and a receipt must assert that
  no admissible row has zero execution cost per query.
* **Ecology defect.** The running-maximum obligation **degenerates**: a maximum saturates, so the correct answer becomes a
  constant and the obligation stops being history-dependent. A memoryless row passes it (0.9062 at `T = 64`). → **protocol
  rule 22**: an obligation is history-dependent only where the best *constant* answer is below `θ`; every temporal ecology
  must carry a constant-answer control row, and clauses may be evaluated only on cells where that control fails.

### 11b. Scoreboard of the four axes

| axis | status | result |
|---|---|---|
| `A` alphabet | **EXECUTED** (`RV-377-072`, `RV-377-073`) | **no new kingdom**; D6 reduces to D2 at a constant 4-bit overhead (GMI-DA8) |

| `p` precision | **EXECUTED, REFUTED, then the refutation AUDITED and upheld** (`RV-377-066` → `RV-377-075` → `RV-377-076`, 9 of 11 clauses) | **no new kingdom**; the gate was a property of the *linear representation*, not of the word width. Seven independent attacks on the refuting row leave capability bit-identical. The residual is answered: **precision buys description and execution cost, not capability** — two extra bits buy back 2 508 description bits and 196 charged activations per query, and on the noisy ecology precision buys nothing at all |
| `d` structure depth | **EXECUTED** (`RV-377-065`, 7 of 12 clauses) | **no new kingdom** to depth 6; the parent-maximal opponent occupies every cell. And `GMI-DA3` itself is **falsified for the XOR code**: one bounded reduction with overhead ≤ 5.3449 covers the whole unbounded-depth family. It survives only for a *permutation-protected* code, so the theorem must name its binding operator |
| `F` ecology family | **EXECUTED** (`RV-377-070`) | **no new kingdom**; the refined family **splits 10 of 14** exact-equality certificates and 3 survive the known gates, but every reduction survives *qualified by a declared capacity bound* rather than overturned. Two candidates (DC7, and F6 against the universal parent) gain a `CANDIDATE_CLASS_SEPARATION` no known gate explains — and still fail criterion 3, the reduction existing at polynomial cost (8Q² or 6Q² against 2Q), which by §9 is one more crossover law of the L4 family |

### 11d. The kingdom question, answered on all four axes

`GMI-DA7` proves these four axes are the *only* places a kingdom can hide. All four have now been executed, and the
answer is the same on each: **no new kingdom at this scope.** That is not four independent negatives. It is the theorem
being confirmed where it could most easily have failed, and each axis returned something the theory did not have before:

* `A` gave **GMI-DA8** and cost the enumeration half of `GMI-DA1` — the alphabet admits eight carrier classes, not nine.
* `p` gave the first positive result of the programme and then took it back, and cost the claim that a gate is a property
  of a word width — it is a property of a *representation* (rule 24).
* `d` cost `GMI-DA3` its generality: the unbounded-depth crossover holds for a permutation-protected binding operator and
  **not** for the XOR code the original record executed it on.
* `F` cost every one of the eleven reductions its unqualified form: each now carries a declared **capacity bound**, and
  the reductions hold up to the parent's certified state size and not past it.

Stage B4's first open-world pre-test agrees (`RV-377-077`): of seven neutrally recovered admissible machines, **five look
novel structurally and none is novel by response** — every one emits a final served answer vector bit-identical to a
known parent's, and one reproduces a parent node for node.
| `p` precision | **EXECUTED, REFUTED, then AUDITED AND SETTLED** (`RV-377-066`, refuted by `RV-377-075`, audited and residual executed by `RV-377-076`) | **no new kingdom, and no capability purchase either — only a priced one.** The gate was a property of the *linear representation*, not of the word width: an 8-bit **log-domain** posterior built only from registered kinds scores 0.874265 where ten linear rows scored exactly 0.0. Seven attacks on that row (its table's status as a registered kind and its charge, its constants, its renormalization charge, its actual bit width, leakage, charged-op identity, its op counter) leave it admissible under **every** declared charging regime. What survives is a **cost** statement — see §11d |
| `d` depth | running (`RV-377-065`) | — |
| `F` ecology family | running (`RV-377-070`) | — |

### 11c. The precision axis, and the rule its refutation forced

`RV-377-066` was this programme's first positive: 13 of 13 clauses, a carefully controlled instrument (262 144 assertions
of bit-identity against the registered universe; identical charged operation sequences across all six instruments; a
representability control showing an admissible answer *is* expressible at 8 bits), and a threshold bisected to 10 total
bits. It was refuted within the hour by a single missing row.

The gate rested on the linear mixture's inability to concentrate 32 weights at four fractional bits. Log-domain Bayesian
updating is the textbook fix for exactly that underflow; it needs only `ADD`, `SUB`, `GT`, `SEL` and a table, all
registered kinds; and it is **more** expensive, not less — 3 104 description bits against 544–596, since the exponent
table and the log constants are both charged to `desc`.

| ecology, sequence | ten linear rows at fx8 | log-domain row at fx8 |
|---|---|---|
| ambiguous, A (the terminal's own sequence) | all exactly 0.0 | **0.874265, admissible** |
| ambiguous, B | all exactly 0.0 | 0.400545, inadmissible |
| ambiguous, C | all exactly 0.0 | **0.874265, admissible** |
| noisy, A | best 0.863997 (quantized counts) | **0.979053** |
| negative twin: log domain, no renormalization | — | exactly 0.0 everywhere |

**Protocol rule 24, from this failure.** A gate claim — precision, capacity, reliability or depth — must enumerate the
**representations of the carrier's state** that the alphabet admits, and test the strongest at the gated setting. Rule
19's parent-maximality now explicitly covers the opponent's *state encoding*, not only its carrier family. `GMI-DA5`
survives as stated — admissibility is a function of the instrument — but every executed instance must name the encoding.

The general lesson is worth more than the lost result: **a gate is a claim about a representation, not about a word
width, until every representation the alphabet admits has been tried at that width.** `RV-377-066` controlled for
everything except the one thing that mattered. It held the charged operation sequence identical across instruments, which
is the right control for comparing instruments, and it verified that the answer is representable at 8 bits, which is the
right control for representability. Neither control reaches the choice of state encoding, and that is where the gate
lived.

### 11c-audit. The refutation was itself attacked, and it survived — but its accounting did not

`RV-377-076` was commissioned to break the refuting row rather than accept it. Seven attacks; **none reverses the
verdict**, because capability is bit-identical under every attack and every re-charging regime: the log constants
recomputed by exact integer comparison with no floating point (0 wrong over 1 056 constants and 256 table entries across
8 cells), 137 326 traced values at fx8 lying in exactly `[-128, 127]` with 0 outside, the renormalization charged within
1 activation per event of the theoretical minimum, and a nonsense-ecology control leaving every answer signature
identical while the positive control moves.

It found **three things against the refuting row**, all recorded rather than absorbed:

| finding | effect |
|---|---|
| the readout division was charged only when the denominator was non-zero | the charged op sequence was **data-dependent** (3 290 043 at fx8/10/12 against 3 289 787 at fx16) — the very control the comparison rests on. Repaired: all instruments now execute 66 235 activations, capability unchanged |
| the exponent-table reads were charged on the Machine but not counted in the row's own total | understated by 12 544 and 25 088 activations, in 48 of 72 cells. Repaired |
| no table kind is native in the registered column, which realizes a store lookup as a **linear scan** | re-charged honestly, execution cost per query rises from 208 to **8 432**, a factor of 40.54. The claim ceiling said the charging was generous to this row; it was more generous than stated |

And one limitation diagnosed and deliberately **not** repaired, because repairing it changes the description cost and so
needs its own frozen prediction: the exponent table is a fixed 256 entries, so the log₂ range it covers **halves with
every two extra fractional bits** — down to −15.94 at fx8, −3.98 at fx12, only −0.996 at fx16. The row is admissible at
8, 10 and 12 bits and fails at 16 for a reason that has nothing to do with precision. None of it touches the fx8 result,
which is the whole of the claim.


---

## 12. Structural closure and statistical closure are different theorems, and only one of them is proved

The parallel lane's `GMI_DOMAIN_DISCOVERY_SATURATION_THEOREMS_V1.md` (DSAT-1/2/3, merged 2026-09-12) supplies exactly the
half this lane does not have, and reading the two together corrects an over-reach in §11d.

| | statement | status here |
|---|---|---|
| **structural closure** | `GMI-DA7`: a kingdom can be gained only by enlarging `A`, raising `d`, raising `p`, or refining `F`. There is no fifth place to look. | `PROVED_AT_SCOPE` |
| **statistical closure** | DSAT-1/2/3: *having looked and found nothing* bounds the chance of a missed domain only if a minimum discoverability `p_min > 0` is registered. `K ≤ ⌊1/p_min⌋`, and missing any of `K` domains has probability at most `K·e^{−Λ}` for cumulative cross-encoding exposure `Λ`, so `Λ ≥ ln(K/δ)` suffices. | **NOT ESTABLISHED** |

DSAT-2 is explicit that consecutive no-new-domain runs justify no stopping rule without `p_min`, because arbitrarily many
domains can hide in arbitrarily small probability mass. **That applies directly to this lane's own negatives.** The
four-axis result of §11d is a *structural* statement and stands; the stage-B4 result of `RV-377-077` — "0 of 7 recovered
machines is novel by response" — is exactly the kind of evidence DSAT-2 forbids as a stopping claim.

### 12a. What `p_min` would have to be, and what the executed data says

`Λ ≥ ln(K/δ)` with `K ≤ ⌊1/p_min⌋` and `δ = 0.05` gives the number of independent search units required:

| `p_min` | `K ≤` | `Λ ≥` | independent units `n ≥` |
|---|---|---|---|
| 0.50 | 2 | 3.689 | **8** |
| 0.33 | 3 | 4.094 | **13** |
| 0.25 | 4 | 4.382 | **18** |
| 0.167 | 6 | 4.787 | **29** |
| 0.10 | 10 | 5.298 | **53** |
| 0.05 | 20 | 5.991 | **120** |

This lane has executed **9** neutral search units (6 B1 runs over the typed IR, 2 quality-diversity runs and 1
regularized-evolution control over the expression-tree grammar). That would support a saturation claim only at
`p_min ≥ 0.5` — every material domain recovered by half of all independent search units.

**The executed data refutes that assumption outright.** Read on *atrophied* carriers (protocol rule 23), the coefficient
carrier D1 is recovered in **0 of 6** B1 runs: every genotype the raw descriptor labelled `DENSE` loses its `DENSE` node
at no capability cost. Zero successes in six trials gives **no positive lower bound on `p_min` at all** — by the rule of
three only `p_min ≤ 0.5` at 95 %, which is an upper bound, not the lower one DSAT-1 needs.

So the honest position is sharper than "no new kingdom found":

> **The structural closure is proved and the statistical closure is not even parameterized.** We know there are exactly
> four places a kingdom can hide and have looked in all four. We do not know, and cannot yet bound, how hard we looked.

### 12b. The closure experiment this forces

`p_min` cannot be estimated from zero successes. The registered closure experiment is therefore not "run more search" but
**observe the least-recoverable registered domain at least once**, then estimate `p_min` from that rate and read `n` off
the table above:

1. Recover the coefficient carrier D1 by neutral search over the typed IR, verified on the **atrophied** genotype, at
   least once. Until then `p_min` is unbounded below and no saturation arithmetic applies.
2. Diversify the encoding, not the seed. DSAT-3 is a statement about cumulative **cross-encoding** exposure `Σ_e n_e p_{i,e}`,
   and a domain hard for one grammar may be easy for another — which this lane has already measured: the expression-tree
   grammar plateaus at 0.7441 where the typed IR reaches admissibility in 6 000 evaluations. Repeated copies of one biased
   search buy far less exposure than their count suggests.
3. Register the materiality threshold explicitly, per the DSAT discipline: `p_min`, the independence definition for
   search units, `n`, `δ`, the grammar scope and the parent-reduction scope, in every saturation claim.

Gap **G15** is opened for this: *no registered `p_min`, so no saturation claim is available at any confidence.*
`OPEN_BLOCKING` for any statement of the form "the domain list is complete", and `OPEN_NONBLOCKING` for everything this
lane has actually claimed, which is structural.
### 11d. The precision axis, settled: precision buys **description and execution cost**, not capability

`RV-377-076` did two things. It **attacked** `RV-377-075` — seven named attacks, any of which would have restored the
kingdom — and it **executed the residual** the refutation left behind. Receipts
`STAGE_DK_V4_LOGDOMAIN_AUDIT_V1.json` and `STAGE_DK_V5_PRECISION_RESIDUAL_V1.json`; record `RV-377-076` in the new
ledger `REVIVAL_LEDGER_PRESIDUAL.jsonl`, **9 of 11 clauses HOLD**, clauses 2 and 9 **FAIL** and are stated in full
there and in `GMI_PRECISION_GATED_KINGDOM_V1.md` §§11a and 12.

**The refutation survives.** The sharpest attack is real and still does not land: there is **no `TABLE` or
`MATERIALIZE` kind** in the registered universe, and **none of the five registered store kinds is native in `B0`**,
which realizes a table read as a **linear scan, one `EQ` per entry**. Charged at that registered rate the log row's
`exec_q` goes **208 → 8 432** per query and its description **3 104 → 3 618** bits. Its capability does not move by
a single bit, because **charging is not in the capability functional** and `RV-377-066`'s kingdom condition is an
*admissibility* condition. Two genuine instrument defects were found in the refuting row — a data-dependent division
charge that breaks charged-op identity across instruments (3 290 043 against 3 289 787 at fx16), and an op counter
that omits its own 12 544 table reads — and neither moves a capability either.

**The residual, executed.** On the **cross-instrument** frontier — the frontier `RV-377-066` never computed, and the
one on which "is a wider instrument necessary?" is actually decidable — the 8-bit log row holds **0 of 42, 0 of 49,
0 of 294 and 0 of 899** cells, and so does **every** other fx8 row. It holds 36 of 36 cells of the fx8
*per-instrument* frontier only because it is the sole admissible row there: protocol rule 17 applied per instrument
reports an **empty field** as a victory. The 0-cell result is a **theorem**, not a grid observation: `QCOUNT@fx10`
dominates it on all three coefficients the frozen cost function has — `(596, 12, 549)` against
`(3 104, 208, 2 075.75)` reduced, `(596, 4, 112)` against `(3 104, 96, 904)` native.

So two extra bits of instrument (8 → 10 total, 4 → 5 fractional) buy, on `E_ambig`:

| | 8 bits (`LOGBAYES8`) | 10 bits (`QCOUNT`) | ratio |
|---|---|---|---|
| description, flat basis | 3 104 | 596 | **5.208054** |
| description, `scaled` basis | 3 104 | 668 | **4.646707** |
| charged activations / query, reduced price | 208 | 12 | **17.333333** |
| … at the **registered `B0`** table charge | 8 432 | 12 | **702.666667** |
| reuse coefficient ρ | 2 075.75 | 549 | **3.780965** |

**2 508 description bits and 196 charged activations per query, at every cell — not at a crossover.** And on
`E_noisy` precision buys **nothing**: `QCOUNT@fx8` holds 42 of 42, 243 of 243, 48 of 49 and 1 120 of 1 120 joint
cells. Whether the instrument buys anything is an **ecology** property; what it buys, where it buys anything, is
**description and execution cost**.

**`GMI-DA5`, final form at this scope.** The arithmetic instrument is **not** a kingdom parameter (`RV-377-075`) and
**not merely** a substrate parameter: on an ecology where the 8-bit universe can only answer in a representation that
costs 5.2× the description and 17.3× the per-query charge, it is a **description-cost parameter**. Gap `DG-6`'s
closure experiment — re-adjudicating the eleven reduced candidates under the wide instrument — is unchanged in form
but changed in kind: it is now a **cost** question, not a capability one.

**One more thing `RV-377-076` corrected in `RV-377-075`.** `RV-377-075` reported its row admissible "on two of three
declared event sequences" and registered the prediction that a fourth and fifth would split the same way. Both new
sequences are **admissible** (D 0.910859, E 0.874273), so the split is **4–1**, and the single failure is not a
property of the event sequence at all: it is **one of 256 exponent-table entries** — the unique entry decided by a
rounding **tie**, at `log₂ w = −5` exactly — on which three hypotheses of sequence B land and none of the other four
sequences does. Flipping that one entry's tie-break moves B from 0.400545 to **0.874245 and admissible** and leaves
the other nine sequence-cells **bit-identical**. Under half-down tie-breaking the split is **5–0**. → **protocol
rules 25, 26 and 27**.

---

## 13. GMI-DA9 — exactness buys intervention-robustness

Every admissibility verdict in this lane was taken under the `standard` intervention while the registry declares six.
`RV-377-085` evaluated the registered zoo on all five registered ecologies under all six, and the single-condition tables
turn out to have been reporting something weaker than they said.

| ecology | admissible under `standard` | under all six | lost |
|---|---|---|---|
| `E_smooth1` | 5 | 3 | particles, soft retrieval |
| `E_smooth3` | 5 | 3 | nearest-neighbour store, particles |
| `E_sym5` | 4 | 3 | soft retrieval |
| `E_sym3` | 6 | 4 | gradient net, particles |
| `E_parity` | 5 | 4 | soft retrieval |
| **total** | **25** | **17** | **8, i.e. 32 %** |

**Statement (GMI-DA9).** Admissibility is a property of a carrier and an **intervention family**, not of a carrier and an
ecology. On the registered family, **exactly two rows are admissible under all six interventions on all five
ecologies — `program_search` and `compiled_search`, and both are EXACT.** Every approximate carrier fails somewhere:
memory, coefficient, stochastic and attention-like alike.

**Status:** `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_CHARGED_REPLAY` over 5 ecologies × 6 interventions × the registered zoo.
**Receipt:** `STAGE_RULE36_INTERVENTION_ADMISSIBILITY_V1.json` (`RV-377-085`).

> **SECOND SCOPE CORRECTION (`RV-377-101`, gap `DG-9`).** The table's `E_sym3` row is taken on an ecology where the
> **best constant scores 0.8750 and is therefore admissible at θ = 0.85** — a machine that reads neither its input nor
> its feedback passes. Re-measured directly, the entry **survives**: all four rows admissible under all six
> interventions on `E_sym3` (`hamming_knn_k3` 0.9167, `program_search` 0.9375, `compiled_search` 0.9375,
> `soft_retrieval` 0.8854) strictly beat the constant, **4 of 4**. But margins must now be read in the instrument's
> own units — one fx unit of mean absolute error is `1/(1.5·16) = 0.041667` of capability — and two of them are
> **within one quantization step**: `soft_retrieval` at **0.250 fx units** and, outside the zoo,
> `RV-377-089b`'s `grad_h3_lr3` at **0.375 fx units**. `hamming_knn_k3` (1.000) and `program_search` (1.500) are
> clear. Under protocol rule 40 a margin below one fx unit is `WITHIN_QUANTIZATION` and may not separate mechanisms.
>
> The non-discriminating region is exactly `E_sym(k)` for `k ≤ 3` (both criteria) and `k = 4` under `all`, which
> follows in closed form: the target `(k/16)·popcount(x)` has spread growing in `k` while a constant's best error
> does not.

> **SCOPE CORRECTION (`RV-377-089b`).** The table above is a fact about the **zoo's default-parameter rows**,
> not about the carrier **classes**. The zoo contains exactly two coefficient members, `gradient_net_h2` and
> `gradient_net_h4`, both at the default `lr = 4`, and those are the two `RV-377-085` evaluated. Sweeping the
> coefficient class over 80 declared settings finds **six rows on `E_sym3` admissible under all six interventions**
> (`grad_h3_lr3` clears θ everywhere with a margin of `0.0354`), none of them in the zoo — so the row marked *lost:
> gradient net* for `E_sym3` is a default-parameter loss, not a class loss. The **headline is unharmed**: no single
> coefficient row is robust on all five ecologies, so *exactly two rows are admissible under all six interventions
> on all five ecologies, and both are exact* still stands. What narrows is the gloss below — see §15.3.

The losses are **mechanism-specific rather than uniform**, which is what makes this a separation and not a difficulty
shift — the nearest-neighbour store's capability *rises* under three of the five non-standard interventions on
`E_smooth1`:

* **coefficient** rows fail under `shuffled_events` and `half_events` — when the order or the number of gradient steps
  changes, which is what a gradient learner is sensitive to and a table is not;
* **store** rows fail under `extra_unseen_feedback` — when given feedback on inputs they will be evaluated on;
* **search** rows are exact and immune to both.

**Why this matters beyond the bookkeeping.** It is the first executed reason in this programme to prefer a deliberative
carrier that is *not about cost*. Every earlier argument for D4/D5 was a lifecycle-cost argument on a frontier; this one
says the exact carriers are the only ones whose admissibility is a property of the machine rather than of the conditions
it was measured under — **narrowed by `RV-377-089b` to: the only ones whose admissibility is machine-determined on
*every* registered ecology.** On `E_sym3` alone, once the coefficient class is swept rather than sampled at its
defaults, an **approximate** carrier's admissibility is machine-determined too.

**Consequence for the corpus.** Protocol rule 36: every admissibility verdict must name its intervention set, and a row
is "admissible" unqualified only if it passes under all of them. A verdict under one condition is reported as
"admissible under ⟨intervention⟩" and is necessary, not sufficient, for occupancy. Roughly a third of the corpus's
verdicts need that qualification, and the frontier tables built on them inherit it.

---

## 14. GMI-DA10 — a cost law is a pair of scaling functions, never an inequality between coordinates

**Status:** `PROVED_AT_SCOPE` for the `N10` microscope; the *methodological* half is protocol rule 37 and binds the
whole corpus.
**Receipt:** `STAGE_DN_V29_N10_SERVE_LAW.json` (`RV-377-053`), sha `325e600a58efa244…`, 12 cells × 2 rows × 2
instruments, 70 700 queries per row per instrument, 6.0 s.

### 14.1 The negative this replaces

`RV-377-051` observed that the `N10` candidate (a vector clock) sometimes serves more cheaply than its program-search
parent and sometimes does not. `RV-377-052` froze the closed form

> `exec_per_query(POSET) < exec_per_query(PROG_SEARCH)` **iff** `L > w`

and ran it out of sample. It **failed**, 28 of 32, refuted in the single cell `w6_L6` where `L = w` and the candidate
won anyway. `RV-377-052` then registered a *second* closed form, `L ≥ 6 ∨ w ≤ 2`, which fitted all sixteen cells then
on record, and marked it `REGISTERED_FOR_EXPERIMENT` "pending a cell at `L = 5`". That cell was never run, and the
successor id the record named was never written. The negative stood for the rest of the programme.

### 14.2 Why the replacement was not entitled to promotion

`RV-377-052`'s own `new_theory_constraint` had already said what was wrong:

> *a cost law separating a candidate from a parent must be stated as a comparison of each row's own scaling FUNCTION,
> not as an inequality between the coordinates … any inequality between `w` and `L` is an artefact of the grid on
> which it was fitted.*

`L ≥ 6 ∨ w ≤ 2` is another inequality between the coordinates, fitted to the same grid. Promoting it would have
repeated the error that produced the falsified law. `RV-377-053` therefore registered, **before the run**, the
prediction that the replacement **fails**.

### 14.3 The theorem

Read off the charged source rather than any grid:

* `Poset.query` serves through `_le`, which charges **one `GT` per clock component** and returns at the first
  componentwise excess. The clock has **one component per chain**, and there are `w` chains. Therefore

  | query truth | charged ops | range |
  |---|---|---|
  | `i` precedes `j` | `w` | exactly `w` |
  | `j` precedes `i` | `k₁ + w` | `(w, 2w]` |
  | concurrent | `k₁ + k₂` | `[2, 2w]` |

  **No `L` term appears anywhere.** `L` changes only *which queries exist and what their truths are* — the ecology's
  query mix — never the cost of serving one of them.

* `ProgSearch.query` charges **one `EQ` per DFS edge examined**, so its cost is the size of the explored edge set,
  which grows in **both** coordinates.

Both are consequently **exact functions of the dependency graph**, computable with no Machine, no charging and no free
parameter: the vector clock is the componentwise longest-path vector, and the DFS is deterministic given the
successor-list order.

### 14.4 What was measured

Grid `CELLS_R3` = widths `5, 7, 9, 16` × chain lengths `5, 7, 10`. **No width and no length here appears** in `CELLS`
(`w ∈ {1,2,4,8}`, `L ∈ {4,8,12}`) or `CELLS_R2` (`w ∈ {2,3,4,6,12}`, `L ∈ {4,6,8,12}`), so every cell is out of sample
for every law on record. Three cells were run before the freeze to size the runtime and are **disclosed as
calibration** (protocol rule 17) and excluded from the decisive count of the closed-form clauses.

| clause | content | verdict |
|---|---|---|
| C1 | no `POSET` query costs more than `2w`, at either instrument | **HOLDS** 12/12 |
| C2 | every forward-ordered query costs **exactly `w`** | **HOLDS** 12/12 |
| C3 | reverse in `(w, 2w]`, concurrent in `[2, 2w]` | **HOLDS** 12/12 |
| C4 | the distinct-forward-cost set at a width is `{w}` at **every** `L` | **HOLDS** |
| C5 | pure-graph predictors reproduce the charged count **query by query** | **HOLDS**, 141 400 / 141 400, **zero** mismatches |
| C6 | the `RV-377-052` registered closed form holds out of sample | **FAILS** — refuted at `w7_L5` (frozen as a *predicted* failure) |
| C6b | the already-falsified form `L > w`, re-tested | holds only **6 of 12** here, against 28 of 32 on its own grid |
| C7 | the boundary is a **surface**, not an inequality | **HOLDS** — 8 pairs share `sign(L − w)` with opposite verdicts, 4 share `L` with opposite verdicts |

The distinct-forward-cost set is `{5}` at width 5 for `L = 5, 7` and `10` alike, `{7}` at width 7, `{9}` at width 9,
`{16}` at width 16. The **mean** still drifts — `5.9850 / 5.7143 / 5.5237` at `w = 5` — and the per-query decomposition
shows exactly why: the concurrent-to-ordered mix moves from `422/178` at `L = 5` to `1254/1196` at `L = 10`, and
concurrent queries are the cheap ones. **The drift `RV-377-052` measured is the query mix, now confirmed by
construction rather than conjectured.**

### 14.5 The boundary, since it is now computable

At `L = 5` the verdict **splits between `w = 7` and `w = 9`** (`6.3975 < 7.0269` but `8.8187 > 8.2232`); at `L = 7` and
`L = 10` the candidate wins at all four widths; at `L = 5` the parent wins at `w = 9` and `w = 16`. That split is the
whole content of the `L = 5` row `RV-377-052` was waiting for, and it is why no inequality between `w` and `L` can
express the boundary — the crossing is where `mean explored-edge count` overtakes `mean clock-comparison count`, and
those are two different functions of the graph, not two coordinates.

### 14.6 Unplanned corroboration

The grid was built for the serve law and incidentally re-tested the **precision-gate law** on ground it had never
seen. It holds **12 of 12**: `POSET`'s `fx8` capability is strictly below its wide capability in exactly the four
cells where the counter range `L` exceeds 8 (`L = 10`: `0.9898, 0.9942, 0.9944, 0.9976` against `1.0000`) and equal to
it in all eight cells at `L = 5` and `L = 7`, while `PROG_SEARCH`, which holds no counter, is ungated everywhere.
That is a **third independent grid** for that law.

### 14.7 Consequence for the corpus — protocol rule 37

> A cost law stated as an **inequality between ecology coordinates** may not be promoted above
> `REGISTERED_FOR_EXPERIMENT`. To reach `PROVED_AT_SCOPE` it must exhibit, **for each row it compares**, a predictor of
> that row's charged cost **derived from the row's own source or state**, carrying **no parameter fitted to the
> measurement grid**, and must be adjudicated at the **finest resolution the charging supports** — per query, not per
> cell mean.

The `N10` serve law needed two falsifications to reach this form: once as `L > w`, once as `L ≥ 6 ∨ w ≤ 2`. Both were
inequalities between coordinates and both died on the first grid that was not built around them. The mechanism form
died nowhere, because it is not a fit.

**`N10`'s domain verdict is unchanged at `REDUCED_TO_PARENT`.** Nothing here reopens it; this is a cost-law record.

---

## 15. GMI-DA9 corroborated on rows it was not derived from, and the correction it forces on `G15`

**Status:** `PROVED_AT_SCOPE` for the coefficient carrier over the registered ecology family.
**Receipt:** `STAGE_B1_V31_DG7_COEFFICIENT_WITNESS.json` (`RV-377-089`), sha `a07f2109839c75f9…`, 80 declared parameter
settings × 3 ecologies, with the full six-intervention family charged on every row clearing θ under `standard`.

### 15.1 What this was supposed to be

The first **`DG-7` audit**. `RV-377-082` had swept the coefficient row's parameters, found an admissible witness on
`E_smooth1`, and written of the other two ecologies that their failure was *"a **real ceiling** rather than a missing
setting: the best of all 68 rows reaches only `0.8438` on `E_smooth3` and `0.8385` on `E_sym5`."* Those 68 rows swept
`h` over `(1, 2, 3, 4, 6, 8)` and **stopped at `h = 8`**. Under protocol rule 38 that is a class-level negative over a
truncated grid, so it was re-run to `h = 32`.

**The audit confirmed its target.** No cell of the extension clears θ on either ecology, and the best cells *outside*
the old grid are **worse** than inside it (`0.8125` and `0.7865`). The ceiling is real and is now entitled to the word.
The first `DG-7` audit upholding rather than overturning is what makes the remaining audits worth running.

### 15.2 What it actually found

The frozen clause `C5` predicted that *at most a minority* of rows admissible under the `standard` intervention would
survive all six. The observed number is **zero — on all three ecologies**.

| ecology | best row | `standard` | falls to | under |
|---|---|---|---|---|
| `E_smooth1` | `grad_h6_lr2` | 0.8906 | **0.8281** | `shuffled_events` |
| `E_smooth1` | `grad_h6_lr3` | 0.8698 | **0.7448** | `shuffled_events` |
| `E_smooth1` | `grad_h24_lr3` | 0.8594 | **0.5260** | `half_events` |
| `E_smooth3` | `grad_h6_lr2` | 0.8438 | **0.6927** | `shuffled_events` |
| `E_sym5` | `grad_h3_lr1` | 0.8385 | **0.7708** | `half_events` |

The binding interventions are exactly the two `GMI-DA9` names for this carrier class — *"coefficient rows fail under
`shuffled_events` and `half_events`, when the order or the number of gradient steps changes, which is what a gradient
learner is sensitive to and a table is not."* `GMI-DA9` was derived from 8 registered rows on `E_smooth1`; it is here
corroborated on **240 fresh rows across three ecologies** that it was not derived from.

> **On these three ecologies** the coefficient carrier `D1` has no intervention-robustly admissible witness. Every row
> that clears θ does so only because the registered protocol feeds gradient steps in one fixed order and one fixed
> number, and loses admissibility as soon as either is varied.

> ⚠️ **This paragraph originally read "anywhere in the registered ecology family", and that was wrong.** It was a
> class-level negative over **3 of the 5** registered ecologies — the same truncation defect, on the *ecology* axis,
> that rule 38 had been written about on the *parameter* axis one hour earlier. `RV-377-089b` extended the identical
> sweep to all five and found **six** coefficient rows on `E_sym3` admissible under **all six** interventions. The
> wrong sentence is kept above, struck through in substance rather than deleted, because the corpus records
> corrections against the original. §15.3 is rewritten accordingly.

### 15.3 What this actually settles — corrected by `RV-377-089b`

`RV-377-082` recorded `G15_STEP_ONE_REACHED` before rule 36 existed, and its witness holds only under the `standard`
intervention. `RV-377-089` then denied step one altogether. **Both are superseded.** Extending the same sweep from the
three ecologies `RV-377-082` happened to use to **all five registered ones** settles it the other way:

| `E_sym3` row | `standard` | **min over all six interventions** |
|---|---|---|
| `grad_h3_lr3` | 0.8906 | **0.8854** |
| `grad_h3_lr1` | 0.8594 | **0.8594** |
| `grad_h3_lr2` | 0.8906 | **0.8594** |
| `grad_h3_lr8` | 0.8698 | **0.8594** |
| `grad_h1_lr8` | 0.8542 | **0.8542** |
| `grad_h8_lr8` | 0.8542 | **0.8542** |

> **`G15` step one is reached, in the strongest available form: an intervention-robustly admissible coefficient-carrier
> witness exists on a registered ecology — six of them, at declared parameters, with margin.**

**The missing index was never the width.** All six sit *inside* `RV-377-082`'s original `h` grid (`h = 1, 3, 8`); the
wide cells `RV-377-089` added contribute none of them. What was missing was the **ecology** — `RV-377-082` measured
three of five and never touched `E_sym3`, and `RV-377-089` inherited that choice without noticing. `E_sym3`'s target
has all four coefficients equal at `3/16`, the smallest-magnitude symmetric target in the registry, which is where an
8-bit gradient learner's quantization dead zone costs least.

Consequences, restated correctly:

* `D1`'s exposure under rule-36 admissibility is **1 of 5** registered ecologies, not 0. A `B1` recovery run **on
  `E_sym3`** would be the first genuine full-family exposure trial the coefficient carrier has ever had — and is the
  registered next experiment.
* `RV-377-081`'s **0 of 6** and `RV-377-083`'s **0 of 3** remain zero-exposure results, because those runs used
  `E_smooth3` and `E_sym5`, where the ceiling *is* real and is now swept to `h = 32`. That part of `RV-377-089`
  stands.
* The answer to task #25 — *budget or encoding?* — is **neither, and the runs could not have told us either way**:
  they were held on the two ecologies where nothing robust exists to recover.
* **Protocol rule 39** (opened here): rule 38's sweep obligation applies to *every* index of a class-level negative —
  parameters, ecologies, interventions, instruments — and a terminal must name which indices were swept and which
  were held at a default.

This is the third time a positive claim has been invalidated by a rule this lane wrote itself, and the second time
inside one session. Rule 38 was written at 07:30 and falsified a claim made under it at 08:30.

### 15.4 The clause that failed, and why it is worth keeping

`C1` predicted that the `(h, LR)` ridge `RV-377-088` measured on the `smooth` layer — best width rising as rate falls,
with a single wide low-rate winner at 16 events — would **transfer** to the typed IR and lift `E_smooth3` over θ. It
does not. The capability surface over `h` on the typed IR has no trend at all (`0.6302, 0.7500, 0.6510, 0.5365,
0.5156, 0.7188, 0.5469` at `lr = 1` on `E_smooth1`).

The reason is that the two rows are **not the same parameterization under the same name**. `smooth.S4Net` initialises
`h` hidden units by cycling a fixed 24-constant list; `zoo.gradient_net` builds a `DENSE` block of width `5h` and an
`AFFINE` block of width `h` under the `morph` initialiser. `h` indexes a different family of initial conditions in
each, so a landscape feature in one says nothing about the other.

**Constraint recorded:** two rows implementing "the same mechanism" at different layers may not be read as the same
function of a shared parameter name unless their initialisers coincide. A landscape feature measured at one layer is
evidence at that layer only.

---

## 16. GMI-DA11 — a negative claim is a claim about a region of the closure lattice, and must be indexed like one

**Status:** `PROVED_AT_SCOPE` as a corollary of `GMI-DA7`; the corpus evidence is four executed instances, three of
which falsified a standing claim and one of which falsified a claim made under the rule itself.
**Protocol rules:** 37, 38, 39.

### 16.1 The observation

Three protocol rules were opened in one session, from three apparently unrelated failures:

| rule | from | the claim that died | the index left unswept |
|---|---|---|---|
| 37 | `RV-377-053` | the `N10` serve law, twice: `L > w`, then `L ≥ 6 ∨ w ≤ 2` | the **cost coordinates** — both forms were inequalities between grid axes, fitted to the grid |
| 38 | `RV-377-088` | `E_smooth2` is `NOT_OBSERVABLE`, recorded twice | the **row parameters** `h`, `LR` — the class was tested at two of 35 settings |
| 39 | `RV-377-089b` | *my own* "no coefficient witness anywhere in the registered family" | the **ecologies** — 3 of 5 were measured |

These are the same error on three different indices. In each case a claim of the form *"no X"* was recorded after
searching a proper subset of the space X ranges over, with the subset fixed by an inherited default — a class constant,
a hardcoded dict, a grid someone else chose — rather than by the claim.

### 16.2 Why `GMI-DA7` makes this a theorem and not a hygiene rule

`GMI-DA7` (§10) proves that the expressible-realization set `K(A, d, p, F)` is **monotone in all four of its declared
parameters**: refining the alphabet `A`, the structure-depth bound `d`, the arithmetic instrument `p` or the ecology
family `F` can only **split** classes, never merge them. A positive claim — *this carrier is admissible*, *this
reduction exists* — is a claim about a **point**, and monotonicity carries it upward: a witness at `(A, d, p, F)`
remains a witness at every refinement.

A negative claim is the opposite. *"No carrier of this class is admissible"* is a claim about an entire **region** of
the lattice, and monotonicity gives it no protection whatever: it is falsified by a single point anywhere in the region
it implicitly quantified over. So:

> **`GMI-DA11`.** A negative claim is a universally quantified statement over a region of `K(A, d, p, F)` and over the
> parameter family within `A`. It is entitled to exactly the region actually searched. A negative recorded without
> naming its indices claims a region it did not search, and the difference is not conservatism — it is the claim being
> **false over the unsearched part**, as three of the four executed instances demonstrate.

The asymmetry is exact and worth stating plainly: **positives are cheap to hold and negatives are expensive**, because
monotonicity is on the positive's side. Every negative in this corpus is a bounded-search result wearing a universal's
clothes unless its bounds are written down.

### 16.3 The four executed instances

* **`RV-377-053`** — the serve law died twice as a coordinate inequality and survives as a pair of scaling functions
  derived from the row source, exact in **141 400 of 141 400** query-level identities. *Rule 37.*
* **`RV-377-088`** — `E_smooth2` carried two `NOT_OBSERVABLE` terminals; sweeping `h` and `LR` overturned **both**
  (`0.8802` at 48 events against `0.8411` recorded; `0.9271` at 16 against `0.7578`). The registered constants turned
  out to be the **argmax for the first ecology the row ever faced**, carried unchanged into every later verdict.
  *Rule 38.*
* **`RV-377-089`** — the first `DG-7` audit **upheld** its target: `RV-377-082`'s ceiling on `E_smooth3` and `E_sym5`
  survives a sweep to `h = 32`. A rule that only ever overturns is not measuring anything.
* **`RV-377-089b`** — and then falsified a claim made *under rule 38, one hour after it was written*, on the axis the
  rule had not been written for. Six coefficient rows on `E_sym3` are admissible under all six interventions.
  *Rule 39.*

### 16.4 The operational form

Every negative terminal in this corpus must now carry an **index block**: for each of `A` (including the parameter
family within it), `d`, `p`, `F` and the intervention set, either the swept range or the held default, explicitly.
`DG-7` is the audit that brings the existing corpus into that form.

Two consequences already banked:

* the word **"ceiling"** is now earned only with an index block — `RV-377-082`'s was not, and survived; `RV-377-014`'s
  was not, and did not;
* the phrase **"no admissible witness"** carries a quantifier that must be written: `RV-377-089`'s cost a correction
  within the hour.

### 16.5 What this does not say

It does not say the corpus's negatives are wrong. It says their **scope** is narrower than their wording, and that the
difference is measurable — four measurements so far, two overturned, one upheld, one overturned against its own author.
The upheld case is what makes the other three informative rather than merely embarrassing.


### 16.6 Corollary — four one-axis negatives do not compose into a negative over the product

`GMI-DA7` names four axes on which a kingdom can be gained, and the programme's central negative is that none of them
yields one. The `DG-7` index audit (§5 of `GMI_DG7_INDEX_AUDIT_V1.md`) establishes what those four sweeps actually
covered:

| axis | swept | held at default |
|---|---|---|
| `A` | 7 rows × 3 obligation modes × 6 columns | `d`, `p`, `F`, intervention set |
| `d` | 48 cells, depths `d1`–`d6`, two code families | depth > 6, `p`, `F`, intervention set |
| `p` | 7 instruments `fx8`…`wide`, 13 rows | **2 ecologies only**, `A` parameters, `d` |
| `F` | 14 certified pairs × 7 deciding demands | `A` parameters, `d`, `p` |

Each is strong on its own axis and defaulted on the other three. **No cell off the diagonal of `A × d × p × F` has
been searched.** `GMI-DA7`'s monotonicity says refining any axis can only split classes; it says nothing about whether
a kingdom lives at a *combination*.

**This is not a scruple — it has already cost a witness.** `RV-377-089b`'s six intervention-robust coefficient
witnesses sit at `A`-parameter `h = 3` **×** ecology `E_sym3`. The parameter sweep ran the right parameters on the
wrong three ecologies; the ecology enumeration ran all five at the zoo's default parameters. Both were correct on
their own axis; the product contained what neither found. One executed off-diagonal miss is enough.

The theorem is untouched — it is proved, not measured. What narrows is the empirical conclusion drawn under it:

> No kingdom is gained by refining **any single axis while the other three are held at their registered defaults**.
> The joint region is unsearched.

Gap `DG-8`. Closure is a **declared low-discrepancy sample** of the off-diagonal region, sized so that a
kingdom-bearing cell of stated minimum measure is hit with stated probability, registered before the run — not an
exhaustive product sweep, which is not affordable.
