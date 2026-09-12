# GMI — the depth-gated kingdom question, executed (V1)

Status: **EXECUTED EXACT DECISION AT SCOPE — NO KINGDOM IS CLAIMED.** Issue #422 (Track B).
Record: `RV-377-065` in `REVIVAL_LEDGER_DK1.jsonl` (frozen before the run, scored clause by clause after it).
Receipt: `microscopes/results/STAGE_DK_V1_DEPTH_GATED.json`,
`receipt_sha256 = 86a427444265798a6da28f4dbbe5a351f89631cb31f23febc93aa05c2fe86b2e`.
Microscope: `gmi_microscope/dk_depth.py`.
Companions: `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` (GMI-DA1, GMI-DA2, GMI-DA3, §9),
`GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 (amended by this record, gap DG-3),
`GMI_GAP_LEDGER_EXECUTED_V1.md` (DG-2, DG-3, DG-5, G8), `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` (DC1).

---

## 1. The question, stated so it can be decided

GMI-DA2 proved the lazy/eager duality for the binding carrier: the algebraic realization (store a codebook of `R` roles
and `F` fillers, compose a bound structure on demand) and the materializing exemplar store (store the composites) are
exactly developmentally equal and differ only in a description/serve trade with a reuse crossover `H*`. GMI-DA3 claimed
the one escape left on the depth axis: at structure depth `d`,

```
H*(d) = [ (R^d·F − (R+F))·bits + R^d·F·D·d ] / (d·D)   ~   R^d / d,
```

unbounded in `d`, so the bounded reduction exists at every **fixed** depth and no single reuse horizon amortizes it over
a family of **unbounded** depth. That has stood as a remark. The executable form is:

> is there a structure depth `d*` at which the binding carrier occupies a frontier cell that a **parent-maximal**
> exemplar-store opponent cannot occupy at **any** reuse horizon on a grid that extends past every crossover reported?

Protocol rule 19 (gap DG-5) makes "parent-maximal" the load-bearing word, and it is the word that decided the outcome.

## 2. What was executed

`E_rolefill(R = 4, F = 8, k = 3)` at structure depths `d = 1 … 6`, hypervector widths `D = 64` (three record seeds) and
`D = 128` (one): **48 cells**, six rows each, **96 frontier decisions**. Registered universe throughout: `TOTAL_BITS 8`,
`FRAC_BITS 4`, basis `B0`, `θ = 0.85`, `C = desc + H·exec_q + r·(upd_e + ver_e) + (r/4)·rev_e` with `r = 0`. Two declared
price vectors: `reduced` (charged ops, materialization charged) and `native` (one op per hypervector operation,
materialization **unpriced** — the reading most favourable to the opponent, used deliberately so the negative verdict is
conservative). Every frontier comparison is exact rational arithmetic; the only rounded quantity is `capability`, and
admissibility is decided on the exact rational `correct/total`.

Two declared binding laws over the same record structures:

| law | BIND | distinct path vectors at depths 1…6 (measured) |
|---|---|---|
| `XOR` | bitwise XOR — the law `RV-377-044` actually executed | **4, 7, 8, 8, 8, 8** |
| `PERM` | XOR with the role at path position `i` protected by `ρ^i`, the PERMUTE primitive already in DC1's declared native basis | **4, 16, 64, 256, 1024, 4096** |

Four opponents, constructed adversarially rather than conveniently: `STORE_MAT` (RV-377-044's materializing store at
depth `d`), `STORE_PATH` (materialize the `R^d` **path** vectors only, serve with one XOR plus the cleanup),
`STORE_DEDUP` (one bundle per **distinct** path vector, class recovered by a declared key program, cheapest
representative materialized) and `STORE_SEEN`; plus the negative twin `VSA_NOBIND`. The verdict is taken against
`PARENT_BEST`, their pointwise-minimum lifecycle.

**Gap DG-2 is closed for this receipt by construction.** Every cell's analytic crossovers are computed *first* in exact
rationals; the grid is then built to bracket each one and to reach `4×` the largest. `max(grid) ≥ 2·max(crossover)` in
**96 of 96** decisions, asserted rather than inspected.

## 3. The executed decision

```
NO_DEPTH_GATED_KINGDOM_AT_EXECUTED_DEPTHS__PARENT_MAXIMAL_OPPONENT_OCCUPIES_EVERY_CELL_TO_DEPTH_6
```

`d*` is **null**. In **62 of the 62** decisions with a non-empty admissible set a parent row occupies at least one reuse
horizon of the extended grid; in **0 of 96** does the binding carrier occupy a horizon while no parent occupies any. The
remaining 34 decisions have an empty admissible set — nothing occupies them, the carrier included.

Three numbers carry the result.

**(a) Exact developmental equality at every executed depth.** In all 48 cells the carrier and all three materializing
parents return bit-identical answers on every evaluation query; the negative twin never does. The reduction is an
identity of the two laws — `Hamming(cue ⊕ P, f) = Hamming(cue, P ⊕ f)` — not a measurement, so depth cannot break it.

**(b) Under `PERM` the crossover is unbounded, and the carrier still never excludes the opponent.** The parent-maximal
reduced-price crossover at `D = 64` is exactly

| `d` | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| `H*(d)` | `109/2` = 54.5 | `91/4` = 22.75 | `647/8` = 80.875 | `1213/4` = 303.25 | `18679/16` = 1167.4375 | `91127/20` = 4556.35 |

identical at all three record seeds, with consecutive ratios 0.4174, 3.5549, 3.7496, 3.8498, **3.9029** — rising strictly
towards `R = 4` and never reaching it, so `H*(d) ~ R^d/(d−1)` is unbounded. The depth-1 value 54.5 reproduces
`RV-377-044`'s executed `H*` exactly. The ratio *drops* at depth 2 because `STORE_PATH`, an opponent `RV-377-044` did not
construct, first bites there. But at every depth the opponent occupies the frontier for every `H ≥ H*(d)`, and `H*(d)` is
finite and well inside the grid. **An unbounded crossover is not an unoccupied cell.**

**(c) Under `XOR` there is no escape at all.** The XOR path code is commutative and involutive, so a path composes to the
parity of its role multiset and its image is bounded by `2^R` **however deep the family goes**. The parent-maximal store
is therefore 2309, 4038, 4615, 4616, 4617, 4618 bits at depths 1…6 (`D = 64`) against a carrier description of 864 bits
at every depth: overhead factor `≤ 5.3449`, **constant in depth**. A single bounded reduction covers the whole
unbounded-depth `XOR` family. The same collapse destroys the obligation itself: ambiguous evaluation queries are
strictly positive in all 16 `XOR` cells of depth `≥ 3`, and the carrier is inadmissible in 16 of the 24.

## 4. The correction this forces on GMI-DA3

GMI-DA3's formula is the crossover against an opponent that materializes `R^d·F` bindings, and that opponent is
parent-maximal **only when the binding operator's path code is injective**. For the XOR operator it overstates the
parent-maximal store by `R^d / |image|` = 1, 16/7, 8, 32, 128, 512 at depths 1…6, and at the one depth-2 cell where the
comparison is measurable (`D = 128`, where the row is admissible) it overstates the crossover by `189.625 / 28.75 =
6.5957`. `RV-377-044`'s published depth-2 description ratio of **10.667 is corrected to 56/12 = 4.6667** stored vectors
per carrier vector against the parent-maximal opponent.

GMI-DA3 is not withdrawn: its unbounded `H*(d)` is *executed* here for the permutation-protected code against the
strongest opponent we could build. It is **relativized to a named binding operator**.

## 5. A second executed fact: depth 1 cannot decide anything

At depth 1 the path-materializing opponent **is** the carrier — 864 bits of description, 1095 charged ops per query and
bit-identical answers. The carrier is never the sole frontier occupant in any depth-1 cell under either price. Any
experiment that argues for a binding carrier at depth 1 is arguing against itself.

## 6. Remint

Under the declared nuisance relabelling of role and filler names (with the matching relabelling of the codebook), in all
three remint cells every charged coordinate of every row, admissibility, the carrier-versus-parent answer equality and
the entire frontier decision are **identical**. Capability is identical except in the one remint cell that contains a
tied cleanup, where it moves by exactly one query and moves **identically in the carrier and in all three materializing
parents** — the declared tie-break is the smallest filler index, so a tie is decided by a name. In the morphology IR all
three genotypes are remint-canonical at three remint seeds with pairwise distinct fingerprints, and the carrier and the
path-materializing parent have **equal mechanism vectors**: they differ only in a state-width parameter, which is the
whole content of GMI-DA2.

**The separation does not survive remint, because there is no separation to survive.** What survives remint is the
reduction.

## 7. Claim levels and ceilings

| statement | claim level | ceiling |
|---|---|---|
| the binding carrier and the three materializing opponents are exactly developmentally equal at depths 1–6 in both laws | `PROVED_AT_SCOPE` | an algebraic identity of the two laws, executed on 48 cells; it is not a claim about any trained system |
| no depth-gated kingdom at executed depths: the parent-maximal opponent occupies every cell with a non-empty frontier | `REDUCED_TO_PARENT(D2)` at the executed scope, `EMPIRICALLY_SUPPORTED_AT_TIER_EXACT_SCOPE` for the frontier statement | an **occupancy** result over **four constructed opponents**, depths ≤ 6, one obligation family, one codebook, two widths, three record seeds. It is not a lower bound over all opponents — that remains gap **G8** |
| `H*(d) ~ R^d/(d−1)` is unbounded for a path-injective binding operator | `PROVED_AT_SCOPE` (closed form, executed to depth 6 against the parent-maximal opponent) | the constant depends on the opponent; the strongest opponent built here lowers it by a factor of about 4 against GMI-DA3's |
| the XOR family admits **one** bounded reduction with overhead `≤ 5.3449` uniformly in depth | `PROVED_AT_SCOPE` | `R = 4`, `F = 8`, `D ∈ {64, 128}`; the bound is `2^R·F` vectors and scales with `R`, not with depth |
| GMI-DA3 as written (an `R^d·F` opponent at every operator) | `FALSIFIED_AND_REPLACED` for the XOR operator; restated under a named operator otherwise | see §4 |
| criterion 3 needs a depth bound, a named binding operator and a reuse-horizon bound | gap **DG-3** `CLOSED` (§14 amended) | the amendment is a statement about this programme's own criterion |

**Claim ceiling for the whole document.** Everything here is exact charged replay inside one registered universe over
one synthetic obligation family. No statement is evidence about a trained neural network, and a negative kingdom verdict
is defeasible by exactly one thing: a carrier that beats all four opponents on a registered cell. It is not defeasible by
a weaker parent.

## 8. What would still have to happen for a kingdom

By GMI-DA1 a new kingdom needs a carrier that is **not** a bounded composition of the primitive alphabet, which means
enlarging the alphabet (gap G10). This record removes the depth axis as a route: depth changes the **price** of the
reduction, never its existence, and it changes the price only for an operator whose path code is injective. The live
mechanism named in `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` §9 — certification of impossibility — remains the one that has to
be beaten, and G8 (lower bounds rather than occupancy) remains the gap that any positive verdict would have to close.
