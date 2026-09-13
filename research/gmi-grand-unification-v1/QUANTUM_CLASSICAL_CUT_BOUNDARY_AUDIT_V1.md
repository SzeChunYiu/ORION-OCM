# Grand GMI Quantum/Classical Cut Boundary Audit V1

Date: 2026-09-13  
Audit source snapshot: `5622ac45d0261e8fe0a92f4209b1bb782ce43732`  
Reconciled integration base: `2d65cb11d7f4880ff8f3a4fc41511d2f2e626814`; preserves the common-decoder correction already on main.  
Status: **SCOPED INFERENCE CORRECTION + EXACT FINITE COUNTEREXAMPLE**

## 1. Atomic gap and retained theorem

SC-1 correctly proves that the least alphabet size for its finite deterministic classical interface `c:X -> Z`, `d:Z x Y -> A` is `chi(H_C)`. The original GG37 bridge text and GG44 wording allowed this optimum to be read as a substrate-independent number of globally distinguishable messages required by every physical solution of the task.

That inference fails with quantum messages and classical downstream side information. A task may require different distinguishability tests in different side-information contexts. These tests need not be realizable as a single readout of all classical colors. The obligation remains the same; optimization over classical encodings and optimization over quantum encodings are different problems.

GG37/GG44 remain valid for a **protected identity-channel interface**: if one admissible decoder must recover any freely selected message from an `m`-symbol alphabet, the implementation has a zero-error `m`-message code. A bare quantum carrier then needs dimension at least `m`. With declared entanglement, the receiver's joint state and the assisted capacity must be used. Injective encoding alone does not imply perfect quantum distinguishability.

This audit corrects the inference from a classical task optimum to an arbitrary quantum implementation. It does not refute SC-1 or the global identity-channel capacity theorem.

## 2. Common promise and resource contract

For a finite simple graph `G=(V,E)`, the sender receives vertex `x`; the receiver receives an edge `y=(u,v)`, ordered with `u<v`, and is promised that `x` is one of its endpoints. The required output is `0` for `x=u` and `1` for `x=v`.

Both protocol classes solve exactly this same task and promise:

- the sender knows `x` but does not know `y`;
- the receiver knows `y` and receives one message;
- there is no pre-shared entanglement or further correlated side state;
- every promised input must succeed with probability one, with no abort or postselection;
- communication cost counts the classical alphabet or quantum transmitted dimension;
- local preparation and measurement are unrestricted for this dimension comparison; their time, energy and implementation precision are not claimed to be free in other resource coordinates.

The SC-1 conflict graph is exactly `G`. Each compatible set is the two endpoints of one edge, and those endpoints require different outputs. Thus the minimum classical alphabet is `chi(G)`.

## 3. Four-dimensional rational witness

Let `V13` contain the nonzero vectors in `{-1,0,1}^3`, identifying a vector with its negative and choosing the representative whose first nonzero coordinate is positive. These are the 13 rays in [Yu and Oh, equation (1)](https://arxiv.org/pdf/1109.4396). Use their lexicographic ordering:

```
0:(0,0,1)    1:(0,1,-1)   2:(0,1,0)    3:(0,1,1)
4:(1,-1,-1)  5:(1,-1,0)   6:(1,-1,1)   7:(1,0,-1)
8:(1,0,0)    9:(1,0,1)   10:(1,1,-1)  11:(1,1,0)
12:(1,1,1)
```

Join two vertices exactly when their integer dot product is zero. This graph `G13` has 24 edges and chromatic number four. The checker certifies the lower bound without numerical optimization:

1. Fix the three colors on the coordinate-axis triangle; any three-coloring can be relabeled to this choice.
2. Each pair of face diagonals orthogonal to one coordinate axis forms a triangle with that axis. The pair must use the remaining two colors, in one of two orders.
3. There are exactly `2^3=8` choices for the three pairs. In every choice, one of the four body diagonals has neighbors of all three colors, so it cannot be colored.
4. The explicit coloring `(0,0,1,1,1,1,0,2,2,0,2,2,3)` is valid and attains four colors.

Embed every vector as `(v,0)` in four dimensions and append vertex 13 with vector `(0,0,0,1)`. The resulting graph is `G=G13 join K1`, with 14 vertices and 37 edges. Its additional universal vertex needs a new color, hence `chi(G)=5` exactly.

Send the density operator

`rho_x = v_x v_x^T / (v_x dot v_x)`.

These 14 matrices have rational entries. For the side-information edge `y=(u,v)`, use the two effects `(rho_u, I_4-rho_u)`. Each is an orthogonal projector, they sum to identity, and orthogonality of the edge endpoints makes the outcome probabilities respectively `(1,0)` and `(0,1)`. All 37 contexts times two promised inputs are checked exactly.

The coordinate vectors at vertices `(0,2,8,13)` form a four-clique. Every exact quantum solution must assign mutually orthogonal supports to these four conflicting inputs. This lower-bounds dimension by four, while the displayed protocol attains it. Therefore:

| Task quantity | Exact optimum |
|---|---:|
| Classical cut alphabet | 5 symbols |
| Classical fixed-length communication | 3 bits |
| Unassisted quantum carrier dimension | 4 |
| Unassisted quantum communication | 2 qubits |

The same four coordinate states admit a single global basis readout, checked in all 16 input/output combinations. Thus the genuine four-message identity code remains valid. The task's full encoded input family does not admit global discrimination: for example `Tr(rho_0 rho_1)=1/2`. The successful edge decoders do not convert that family into a global identity code.

## 4. Correct generalization and its boundary

For a finite exact function on a declared promise relation, one unassisted quantum message has minimum dimension equal to the complex orthogonal rank of its conflict graph: adjacent inputs requiring different outputs for a common `y` must have orthogonal supports. Conversely, an orthogonal representation provides, for each `y`, mutually orthogonal spans for different outputs and hence a valid complete measurement. Mixed transmitted states do not improve this optimum: selecting one nonzero vector from each support gives the required representation. The full proof and assumptions are in [the corrected quantum theorem, §4.3](QUANTUM_PROCESS_INSTANTIATION_THEOREM_V1.md).

This specialization agrees with [Stahlke, Theorem 12 and the function-evaluation example in §IV](https://arxiv.org/pdf/1405.5254), and [de Wolf, §8.5](https://homepages.cwi.nl/~rdewolf/publ/qc/phd.pdf). Orthogonal rank here means **adjacent** vertices receive orthogonal vectors. It is not an unnamed quantum coloring-game parameter.

For general nonempty acceptable-action sets `Gamma(x,y)`, the corrected §4.4 uses density matrices and `y`-dependent POVMs with zero Born probability for every forbidden action. This preserves the full relation and its promise. No graph-only formula, efficient joint optimization algorithm, or universal quantum resource scalar is asserted. Entanglement-assisted source/channel coding has separate operational constraints, as developed by [Cubitt et al.](https://arxiv.org/pdf/1310.7120); assistance cannot silently be added to the unassisted orthogonal-rank statement.

## 5. Reproducible evidence and mutation checks

Run from this directory:

```
python grand_gmi_quantum_cut_scope_checks_v1.py
python -m unittest test_grand_gmi_quantum_cut_scope_v1.py
```

The checker emits a strict JSON receipt with terminal `GRAND_GMI_QUANTUM_CUT_SCOPE_V1_CHECKED`. [The committed receipt](GRAND_GMI_QUANTUM_CUT_SCOPE_RECEIPT_V1.json) includes the vectors, all edges, eight coloring obstructions, upper coloring, dimension witness and exact decoding counts. The test suite replays it and rejects four corrupted protocols: collapsed conflicting encodings, swapped output labels, an omitted promised context, and an incomplete measurement.

The specialized verifier proves positivity for its real projective matrices by symmetry and idempotence; it does not claim to solve arbitrary mixed-state or general relational feasibility. All decisions use integers or `Fraction` arithmetic. There is no runtime source download, floating tolerance, or appeal to a numerical optimizer.

The finite witness closes this identified transport gap after the statements are scoped correctly. It does not certify that every Grand GMI claim, every quantum task, or every unbounded process theory is closed.
