# Named results — `gmi-833-mtg-enriched-geometry-v1` (issue #833, programme comment 5687604615)

**Freeze:** `FREEZE_V1.md`, commit `fdd7255e40421db3a6de35622e6fda0a9e6f1150` (committed before every file below).
**Claim ceiling:** `GMI_833_MTG_ORDERED_MONOID_ENRICHMENT_AND_TOPOLOGY_STABILITY_AT_REGISTERED_FINITE_SCOPE`.
**Rows:** indices 23 and 24 of `research/gmi-833-mtg-map-v1/MTG_ROWS_V1.json` (MTG-4: stability under relabeling controls and resource perturbations; quantale/ordered-monoid enrichment). No neighboring row is earned here.

Every number below is read from `RESULT_V1.json` (route A) and agrees with `ORACLE_RESULT_V1.json` (route B) on all 81 shared quantities. All arithmetic is `fractions.Fraction`; floats are rejected.

## Objects

Finite Pareto antichains over `Q^2_{>=0}` with choice `A (+) B = PF(A ∪ B)`, sequential composition `A (*) B = PF({a+b})`, identity `I = {0}`, unreachable `∅` (parent `P04` owns this algebra). Dominance `A ⊑ B` ("`B` at least as good as `A`"): for every `a ∈ A` there is `b ∈ B` with `b ≤ a` coordinatewise. The registered graph has 5 nodes (`A,B,C,D,E`; `D` isolated), 6 antichain-valued edges, closure `H` by `(+,*)`, a 64-vector budget grid `{1..8}^2`, forward budget balls `B_b(M) = {N : ∃ v ∈ H(M,N), v < b}` and the topology they generate (parent `P04` `TOPO-1A`).

## ENR-1 — the algebra is a finite ordered monoid and the closure is laxly enriched in it

**Statement.** On the 20-antichain grid universe: (i) `⊑` is reflexive, transitive and antisymmetric; `∅ ⊑ B` for every `B` and `A ⊑ ∅` only for `A = ∅`; `A ⊑ I` for every `A`. (ii) `(*)` is monotone in each argument: `A ⊑ A'` implies `A (*) C ⊑ A' (*) C` and `C (*) A ⊑ C (*) A'`. (iii) `(+)` is the join for `⊑`. (iv) For every ordered node triple, `H(M,N) (*) H(N,P) ⊑ H(M,P)`, and `I ⊑ H(M,M)` for every node.

**Proof.** (i) Reflexivity is `a ≤ a`. Transitivity: `a ≥ b ≥ c` chains. Antisymmetry on antichains: `A ⊑ B` and `B ⊑ A` give, for `a ∈ A`, some `b ∈ B` with `b ≤ a` and some `a' ∈ A` with `a' ≤ b ≤ a`; an antichain has no strict domination, so `a' = a`, hence `b = a` and `A ⊆ B`; symmetrically `B ⊆ A`. The `∅` clauses are vacuity of the universal quantifier and emptiness of the existential one; `0 ≤ a` gives `A ⊑ I`. (ii) For `a + c` with `a ∈ A`, pick `a' ∈ A'` with `a' ≤ a`; then `a' + c ≤ a + c`, and some element of `PF({a'+c'})` lies below `a' + c`. (iii) `PF(A ∪ B)` is an upper bound because every element of `A` or `B` is dominated by a Pareto-minimal element of the union; it is least because every `x ∈ PF(A ∪ B)` lies in `A` or `B` and is therefore dominated by any common upper bound. (iv) Concatenating an `M→N` walk with an `N→P` walk yields an `M→P` walk, whose burden is dominated by the `M→P` frontier; the empty walk gives `0 ∈ H(M,M)`. (Nonnegative burdens make the frontier over walks equal the frontier over simple paths, which is why route B may enumerate simple paths.) ∎

**Numbers.** 20 reflexive checks; 400 dominance pairs (175 related); 8,000 transitivity triples; 400 antisymmetry pairs; 7,000 monotonicity checks; 800 upper-bound and 8,000 least-upper-bound checks; enrichment law on 125/125 triples and identity law on 5/5 nodes; 28 triples where the composite is nonempty and strictly worse than the closure (witness `A→B→C`: composite `{(1,1)}`, closure `{(0,5),(1,1),(5/2,3/4),(5,0)}`) and 8 distinct-node triples where they are equal (witness `B→A→E`, `{(9,15/2)}`).

**Assumptions.** Burdens are exact nonnegative rationals in a fixed dimension `d = 2`; antichains are finite; the closure is over finite walks of a finite graph; `⊑` is read as cost dominance ("at least as good"), so `∅` is the bottom element and `I` the top.

**Depends on.** `P04` (`DIST-1B` Pareto antichain algebra, `TOPO-1A` forward topology) for the objects; `P01` (`DIST-1A`) for the scalar projection that ENR-1 shows to be lossy; nothing from this tranche's other packages.

**Terminal.** `FINITE_ORDERED_MONOID_ENRICHMENT_VERIFIED`. A complete quantale would additionally require the four conditions recorded in the receipt (`complete_quantale_would_additionally_require`): arbitrary infinite joins of antichains, composition preserving them in each argument, the closure as a least fixpoint over infinite path families, and well-defined Pareto minima for infinite subsets of `Q^d_{>=0}`. None is claimed; `quantale_completeness_not_claimed = true`.

**Falsifiers.** Any universe pair violating (i)–(iii); any triple violating (iv); a planted closure entry that passes the enrichment check (hostile `planted_closure_entry_violating_enrichment_detected`: planting `{(6,6)}` at `A→C` produces violating triples `A→B→C`, `A→E→C`).

**Strongest parents.** Metric spaces as categories enriched in `([0,∞], ≥, +)` (Lawvere, *Rend. Sem. Mat. Fis. Milano* 43 (1973), doi:10.1007/BF02924844); quantaloid- and quantale-enriched categories (Stubbe, *Fuzzy Sets and Systems* 256 (2014), doi:10.1016/j.fss.2013.08.009; Hofmann, Seal & Tholen, *Monoidal Topology*, Cambridge 2014, doi:10.1017/CBO9781107517288); path algebras over ordered semirings and dioids (Gondran & Minoux, *Graphs, Dioids and Semirings*, Springer 2008, doi:10.1007/978-0-387-75450-5); multiobjective shortest paths and Pareto label sets (Hansen 1980, doi:10.1007/978-3-642-48782-8_9; Martins, *Eur. J. Oper. Res.* 16 (1984), doi:10.1016/0377-2217(84)90077-8); the algebra itself and the forward topology (`P04`), the scalar Lawvere distance (`P01`). **Not claimed novel:** ordered-monoid/quantale enrichment, Pareto path algebra, lax composition. **Residual:** the machine-checked statement, at registered finite scope, that GMI's vector-valued transform burden is an ordered-monoid enrichment with the scalar `d_w` an explicitly lossy projection — the row's investigation terminates in a named finite verdict with the completeness gap enumerated rather than assumed.

**Forbidden extrapolations.** `COMPLETE_QUANTALE_ENRICHMENT_PROVED`, any infinite graph, any claim that `(*)` preserves infinite joins.

## STAB-1 — relabeling stability

**Statement.** For every bijection `σ` of the node set, the closure of the relabeled graph transported back along `σ⁻¹` equals `H`, and the generated topology transported back equals the original open-set family.

**Proof.** Every construction (edge burdens, walks, `(+,*)`, balls, unions, intersections) is defined from the labelled graph structure alone and commutes with a relabeling of the node set; transporting along `σ⁻¹` inverts the relabeling. ∎

**Assumptions.** Relabelings are bijections of the registered node set; edge burdens and the budget grid are untouched by a relabeling (a relabeling that also changed burdens would be a resource perturbation, handled under STAB-2).

**Depends on.** ENR-1 (the closure object) and `P03` `GAUGE-1A` (relabeling groupoid on presentations); the null's generator is this package's own.

**Falsifiers.** Any of the 120 relabelings whose transported closure or transported open-set family differs from the original; a null draw count of closure equalities above 0; a non-bijective map accepted as a relabeling.

**Numbers.** 120/120 closure equalities, 120/120 topology equalities, open-set count invariant (18). Automorphism group of the registered graph: trivial (1 element). **Null (misaligned transport):** 200 seeded pairs `(σ, τ)` with `τ ≠ σ⁻¹` (the true law is excluded from the pool; draws from a 64-bit LCG reading only the high 31 bits) — closure equalities 0/200; topology equalities 1/200 (one wrong transport reproduces the coarser open-set family by coincidence; recorded, not hidden). The true law's 120/120 beats the null on both quantities.

**Hostile.** A non-bijective relabeling (`B ↦ A`) is refused with `NON_BIJECTIVE_RELABELING`.

**Strongest parents.** `P03` (presentation-relabeling groupoid, `GAUGE-1A`); transport of structure along isomorphisms is elementary. **Residual:** the topology, not only the closure, is checked, with an explicit null.

## STAB-2 — resource-coordinate stability (three exact statements)

**Assumptions.** Rescalings are strictly positive coordinatewise; additive perturbations are bounded by the registered `e = 1/4` per edge per coordinate and clipped at 0; the budget grid is `{1..8}^2`; scalar weights are strictly positive; the graph is the registered 5-node fixture (the counterexample in (b) uses a separate 4-node graph, recorded in the receipt).

**Depends on.** ENR-1 (closure and dominance), STAB-1 (the topology object), `P04` `TOPO-1A` (budget balls), `P01` `DIST-1A` (scalar `d_w`), `P18` `PERTURB-1` (perturbation vocabulary).

**Falsifiers.** A rescaling pair where `H_λ ≠ λ·H` or the alike-rescaled topology differs; a `STABLE_MEMBER` cell (margin `> L·e`) that flips under a registered pattern; a pattern whose membership escapes the `[H_{+e}, H_{−e}]` sandwich; the counterexample cell being classified stable by the box criterion; a finite frontier pair violating the scalar bound, or an empty frontier receiving a finite distance.

**Strongest parents.** Sensitivity of shortest-path and Pareto-frontier solutions to edge-weight perturbation (Gondran & Minoux 2008, doi:10.1007/978-0-387-75450-5; Martins 1984, doi:10.1016/0377-2217(84)90077-8); Lipschitz continuity of a minimum of finitely many linear functionals (elementary); `P04` for balls and topology; `P18` `PERTURB-1` for bounded perturbation controls. **Not claimed novel:** interval/sandwich arguments for monotone path costs. **Residual:** the exact counterexample that maps the boundary of the frozen frontier-margin rule and the proved box criterion that replaces it, both machine-checked on two routes.

### (a) Positive rescaling

**Statement.** For `λ ∈ Q^2_{>0}`, `H_λ(M,N) = λ·H(M,N)` for every pair; with budgets rescaled by the same `λ`, the generated topology is identical. With the budget grid held fixed the topology may change.

**Proof.** Coordinatewise multiplication by positive rationals is an order isomorphism of `Q^2_{>=0}` that commutes with addition, so it commutes with Minkowski sums and Pareto reduction, hence with the closure; `v < b` iff `λv < λb`, so balls and the topology are unchanged when budgets are rescaled alike. ∎

**Numbers.** 75/75 closure pairs across 3 rescalings; 3/3 identical topologies. **Fixed grid:** 2 of 3 rescalings change the topology (18 → 24 open sets, e.g. `{E}`, `{B,E}` become open under `λ = (2,1)`), the hostile `fixed_budget_grid_rescaling_changes_topology` is applicable (2 rescalings move the raw ball family) and detected. This is the exact witness the freeze asked for: the topology is a joint invariant of burdens **and** budget units.

### (b) Additive perturbation — a frozen lemma refuted and replaced (first-run negative, revived)

Registered `e = 1/4`; every edge burden is perturbed by at most `e` per coordinate (clipped at 0). Registered patterns: 73 (uniform sign patterns over coordinates plus per-edge `±e`), 71 distinct.

**Sound half of the frozen criterion (membership).** If `N ∈ B_b(M)` with a frontier witness `v < b` realised by a path of length `L` and margin `min_i(b_i − v_i) > L·e`, then membership survives every pattern. *Proof.* Each edge moves by at most `e` per coordinate, clipping only lowers, so the same path's burden `v'` satisfies `v' ≤ v + L·e·1 < b`. ∎ 612 cells are `STABLE_MEMBER`; the tightest has margin `1/2`, `L = 1`, slack `1/4` (`E→C` at budget `(1,1)`).

**Refuted half (non-membership).** The frozen rule "every frontier vector exceeds `b` by more than `L_v·e` in some coordinate ⇒ non-membership is stable" is **unsound**. *Counterexample (machine-checked on both routes).* Nodes `M,a,b,N`; edges `M→N = (10,0)`, `M→a = a→b = b→N = (41/12, 0)`; budget `b = (155/16, 1)`; `e = 1/4`. The frontier `H(M,N) = {(10,0)}` (the 3-edge path sums to `(41/4,0)` and is dominated); `10 − 155/16 = 5/16 > 1·e`, so the frozen rule classifies the cell `STABLE_NONMEMBER`. Lowering every edge by `e` brings the 3-edge path to `(19/2, 0) < b`: the cell becomes a member. **Attribution (one stage):** the frozen rule bounds only frontier vectors by *their own* path lengths; a dominated, longer path gains `L'·e` with `L' > L` and can undercut the budget. **Lever:** the box criterion — compare against the two extreme closures `H_{+e}` (all edges `+e`) and `H_{−e}` (all edges `−e`). *Soundness proof.* For any pattern `δ` with `|δ| ≤ e` entrywise, every walk's burden is coordinatewise sandwiched between its `−e` and `+e` versions (clipping is monotone), so `N ∈ B_b^{+e}(M) ⇒ N ∈ B_b^{δ}(M) ⇒ N ∈ B_b^{−e}(M)`. Hence "member and member under `+e`" and "non-member and non-member under `−e`" are each preserved by every admissible pattern. ∎ **Re-test:** the sandwich holds on 113,600 (pattern, cell) checks; 1,544 of 1,600 cells are box-stable (56 undetermined); every frozen-stable cell (612 + 925 = 1,537) is box-stable; the counterexample cell is marked `UNDETERMINED` by the box criterion (no false alarm, no false stability). On the registered graph the frozen classification happened to produce 0 flips across 109,127 stable-cell pattern checks — the refutation required the constructed graph, which is why it is recorded as an exact counterexample rather than inferred from the fixture.

**Hostile.** A uniform `+δ` with `δ = 1/2` (the best margin, exceeding the `L·e` guarantee) flips `E→C` at budget `(1,1)` from member to non-member; applicable and detected.

**Disclosure.** The freeze is not edited. `MANIFEST_V1.json` records `s6_instruction_followed: false` for the frozen non-membership rule with `audit_shape_disclosed: FROZEN_LEMMA_REFUTED_BY_COUNTEREXAMPLE_BEFORE_RECEIPT`; the boundary is labelled earned-by-counterexample and the adjacent positive (box criterion) is the delivered law.

### (c) Scalar projection

**Statement.** For positive weight vectors `w, w'` and a nonempty frontier `F`, `|d_w − d_{w'}| ≤ max_{v∈F} |(w − w')·v|`, where `d_w = min_{v∈F} w·v`; for `F = ∅` both distances are `+∞`.

**Proof.** The two minima are taken over the same finite set of values that differ pointwise by at most the bound. ∎ 51/51 finite checks over 3 weight pairs; 24/24 empty-frontier pairs stay `INF` (`D` is unreachable from and to every other node — `+∞` is preserved, never fabricated). Hostile `coordinatewise_infimum_fabrication_detected`: the coordinatewise infimum `(1,1)` of `{(1,4),(4,1)}` is not attainable and is not dominated by the frontier — detected.

## Fail-closed contract

Negative burden (`NEGATIVE_BURDEN`), dimension mismatch in composition and dominance (`DIMENSION_MISMATCH`), non-exact numbers, non-bijective relabeling, nonpositive scale or weight; a tampered receipt (one registered edge burden changed) fails closure re-verification against the recorded digest while the untampered receipt verifies. 8/8 hostiles applicable and detected.

## Boundary (frozen)

No claim about infinite graphs, complete quantales, arbitrary (unbounded) perturbations, Hausdorffness, manifold structure, or universal price vectors. Forbidden promotions: `COMPLETE_QUANTALE_ENRICHMENT_PROVED`, `UNIVERSAL_INTELLIGENCE_SPACE_TOPOLOGY_PROVED`, `TOPOLOGY_STABLE_UNDER_ARBITRARY_PERTURBATION`, `TOPOLOGY_IS_HAUSDORFF_PROVED`, `TOPOLOGY_IS_MANIFOLD_PROVED`, `COMPLETE_GMI`.

## Two routes

Route A (`enriched_geometry_v1.py`): Floyd–Warshall over `(+,*)` to a fixpoint (2 passes), topology by basis generation. Route B (`independent_oracle_v1.py`, imports nothing from route A): closure by explicit simple-path enumeration with its own dominance test, topology by explicit union closure over the subset lattice, its own LCG for the null. 81 shared quantities compared by the test module; all equal.
