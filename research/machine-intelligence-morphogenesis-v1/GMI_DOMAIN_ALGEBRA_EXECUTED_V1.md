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
| N3 relational-constraint / sheaf | constraint system with gluing | under test | worker branch `claude/gmi-domain-n3-n10` |
| N10 event-causal / partial order | partial order of events | under test | same branch |
| N8 constructive / autocatalytic | closure of a construction set | under test | worker branch `claude/gmi-domain-n8-n11` |
| N11 invariant / obstruction | an invariant certifying impossibility | under test — **the most promising**: an obstruction certificate answers "no solution" in constant work where a search parent must exhaust, which is the one shape of qualitative asymptotic separation the criterion asks for | same branch |

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

**Current honest terminal for the domain programme:**
`NO_NEW_KINGDOM_ESTABLISHED__TWO_CANDIDATES_REDUCED_TO_D2_AS_LAZY_AND_EAGER_PHASES__FOUR_UNDER_TEST__CRITERION_3_SHOWN_TO_REQUIRE_A_DECLARED_DEPTH_BOUND`
