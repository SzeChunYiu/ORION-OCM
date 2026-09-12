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
precision instruments, and was the sole frontier occupant of all 48 grid cells. The surviving niche, found by a **failed
clause** of the frozen prediction, is `P = 4` under the native associative-memory price at reuse `H > 1856`.

**Status:** `PROVED_AT_SCOPE` for the executed instance (one pattern set per cell; a second set is the obvious replication).

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

**Executed decision.** `STAGE_DE_S3_SEED_CENSUS_V1.json` (`RV-377-040`): the particle carrier is admissible on 10 of 192
runs (about 5 percent), with seed-medians 0.39–0.60 and maxima up to 0.9583. `STAGE_DE_SMOOTH_V22_SYM5_S4.json`
(`RV-377-041b`, all five clauses held): on an admissible seed the same carrier is the cheapest admissible form and takes
14 of 56 frontier cells in the scan-store columns, 50 of 56 in the native-store column and **56 of 56** in the
native-stochastic, uniform and compressed-program columns.

**Status:** `PROVED_AT_SCOPE`. **Open consequence (gap G14):** the registered cost model does not yet charge the *failed
draws* of a stochastic carrier as search cost, although the biosphere burden vector requires it (`B_search`,
`B_failed_candidates`; implemented in `gmi_microscope/vm.py::lifecycle_vector` but not yet applied to the D′/E′ frontier).

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
| `p` precision | **EXECUTED then REFUTED** (`RV-377-066`, refuted by `RV-377-075`) | **no new kingdom**; the gate was a property of the *linear representation*, not of the word width — an 8-bit **log-domain** posterior built only from registered kinds scores 0.874265 where ten linear rows scored exactly 0.0 |
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
