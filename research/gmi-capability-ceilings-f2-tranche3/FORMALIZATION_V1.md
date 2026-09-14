# #602 F2 tranche 3 — planning, search, and verification ceilings

This unit closes three bounded **capability-ceiling** rows, not a full capability predictor. Evidence class is **P1 formal + P2 exact finite witness** and the claim ceiling is **G2**.

## Expert review split

The formal-methods review checks quantifiers and tightness; the resource-accounting review checks exactly what is metered; the adversarial review removes one load-bearing assumption at a time and requires the claimed ceiling either to survive or to be explicitly withdrawn.

## Parent subtraction

These are not novelty claims. The planning result is the elementary branching-factor cost of uninformed exhaustive tree search; standard search analyses give exponential frontier growth in branching factor and depth. The search result is deterministic decision-tree/query counting for an unstructured membership oracle. The verification result is finite acceptance sampling: under sampling without replacement the miss event is hypergeometric, the standard finite-lot quality-control model.

The GMI residual is to bind those parents to the registered F2 capability coordinates, resource channels, negative twins, and falsifiers without silently importing heuristics, structure or defect-location information.

## F2-P — planning resource -> reachable complete horizon

Let `T_{b,h}` be the full rooted `b`-ary tree through depth `h`, with root depth zero. Every node through depth `h` may contain the sole obligation-changing event. A planner receives no pruning certificate, heuristic oracle, transposition merging or dominance rule. One unit of planning resource inspects one node.

Define

```text
N(b,h) = sum_{d=0}^h b^d
       = h+1                              if b=1
       = (b^(h+1)-1)/(b-1)                if b>1.
```

### Theorem F2-P [P1]

A planner that guarantees complete coverage through depth `h` in this scope needs at least `N(b,h)` node inspections, and `N(b,h)` inspections suffice.

**Proof.** If fewer than `N(b,h)` nodes are inspected, at least one node `u` is uninspected. Construct two registered worlds identical on every inspected node: in the first no node is decisive; in the second `u` is the sole decisive node. The planner has the same transcript in both worlds and therefore cannot certify complete coverage in both. Hence every node must be inspected. Conversely, breadth-first (or any exhaustive) enumeration inspects every node using exactly `N(b,h)` inspections. QED.

Thus a node budget `R` permits complete horizon only when `N(b,h) <= R`. For `b>1`, this is equivalent to

```text
h <= floor(log_b(R(b-1)+1)) - 1,
```

with the integer maximum implemented without floating-point logarithms.

**Nearest counterexample when an assumption is removed.** If a sound pruning oracle proves one whole branch irrelevant, inspecting every node is no longer necessary. That does not refute the theorem; it changes the information/resource interface.

## F2-S — search budget -> reachable verified-solution class

Let `C={1,...,N}` be an unstructured candidate class. Exactly one candidate may be valid. Querying candidate `i` returns its exact validity bit; checking one candidate gives no information about any other candidate. A deterministic search may issue at most `Q` distinct queries.

### Theorem F2-S [P1]

Worst-case zero-error discovery of the unique valid candidate requires `Q >= N`, and this is tight.

**Proof.** Suppose `Q<N`. After the search finishes there is an unqueried candidate `j`. An adversary chooses the valid instance to be exactly `j`, while every queried candidate is invalid. This transcript is consistent with all observations, so the search has not found the valid candidate. Hence `Q>=N` is necessary. Querying every candidate is sufficient. QED.

The theorem is intentionally *unstructured*. A sorted/monotone candidate family, a generative proof system, a learned heuristic with a registered guarantee, or a side channel can reduce query complexity; those are additional structure and must be charged separately.

## F2-V — verification budget -> false-adoption floor

A candidate has `M` obligation coordinates, exactly `r` of which are defective. Under the registered distributional model, the defect set is uniform over the `C(M,r)` possible `r`-subsets. The verifier checks `q` distinct coordinates without replacement, has no defect-location side information, detects every checked defect perfectly, and adopts iff all checked coordinates pass.

### Theorem F2-V1 [P1]

The false-adoption probability is exactly

```text
P_FA(q;M,r) = C(M-q,r) / C(M,r),
```

with numerator zero when `M-q<r`.

**Proof.** There are `C(M,r)` equiprobable defect sets. False adoption occurs exactly when all `r` defective coordinates lie among the `M-q` unchecked coordinates. There are `C(M-q,r)` such sets. Divide. QED.

For one defect,

```text
P_FA = (M-q)/M.
```

Consequently, for a registered admissible false-adoption threshold `alpha`, the minimum check budget is the least `q` with the hypergeometric ratio at most `alpha`. The executable witness computes that integer exactly with rational arithmetic.

### Theorem F2-V2 — distribution-free zero-FA boundary [P1]

Against an adversarial single defect, any deterministic verifier that checks `q<M` coordinates and accepts when checked coordinates pass cannot guarantee zero false adoption.

**Proof.** At least one coordinate is unchecked. Place the only defect there. All checked coordinates pass and the invalid candidate is adopted. Full `q=M` coverage is sufficient. QED.

This separates a distributional *probability floor* from a worst-case *zero-error impossibility* instead of mixing them.

## Exact witnesses

`capability_ceilings_tranche3_v1.py` and its test suite pin:

- binary planning tree: 14 inspections stop at complete horizon 2, while 15 exactly reaches horizon 3;
- unstructured search: four queries cannot guarantee a hidden valid member among five candidates;
- verification: `M=10,r=1,q=8` gives exact `P_FA=1/5`; `M=6,r=2,q=2` gives `2/5`, reproduced by exhaustive enumeration of every defect pair;
- full verification gives zero false adoption, and adversarial zero-FA is rejected below full coverage.

## Claim boundary

These results do **not** claim that real planners must exhaust full trees, that learned search cannot beat unstructured enumeration, or that real verification defects are uniformly located. They provide exact ceilings after those assumptions are prospectively registered. Planning/search heuristics, dependent verification failures, learned verifier errors and adaptive test creation remain separate statistical/empirical problems.
