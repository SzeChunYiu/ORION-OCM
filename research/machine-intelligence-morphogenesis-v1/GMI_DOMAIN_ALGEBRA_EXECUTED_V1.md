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

**Executed decision.** `RV-377-044` clause 7 (held). **Status:** `PROVED_AT_SCOPE`.

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
