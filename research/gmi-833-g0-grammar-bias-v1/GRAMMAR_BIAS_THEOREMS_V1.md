# G0 finite grammar-bias theorems v1

## Expert review lanes

- **Formal methods / semantics:** checks that the semantic quotient is exactly the frozen protected execution signature and that every remint condition is extensional and machine-checkable.
- **Program synthesis / representation bias:** checks that grammar restrictions and presentation multiplicities are treated as inductive/search bias rather than as neutral ontology.
- **Algorithmic information / coding:** checks the boundary between finite grammar-relative code length and classical additive-constant invariance results.
- **Hostile verification:** attacks bijection, semantic, length, edge, start-set, counting, and shortest-path assumptions with independent implementations.

## BIAS-1 — finite description bias

For finite `P`, decidable `sigma:P→M`, and integer `ell`, each class has exact

`L_G(m)=min ell(p)`, `N_G(B,m)`, and `Q_G(B,m)`.

On the frozen G0 slice, all 126 presentations are enumerated exactly once. They form 18 protected semantic classes. Four classes have `L_G=1`; fourteen first occur at `L_G=2`. Multiplicity is highly nonuniform: the class-size histogram is

`1×10, 2×2, 3×1, 4×1, 14×1, 15×1, 23×1, 53×1`.

This is a finite grammar-relative counting fact, not a universal prior.

## BIAS-2 — finite reachability bias

For a finite unit-edge search graph and nonempty starts, shortest-path distance is decidable. `d_G`, `A_G`, and `R_G` follow by finite minimization/counting.

Two independent algorithms are required: BFS and monotone wave expansion. A third oracle uses an independently constructed graph plus Floyd–Warshall.

Frozen result: the 126 presentations occur at distances `0:1, 1:15, 2:110`; class-minimum distances are `0:1, 1:3, 2:14`. All presentations are reachable by radius 2. This does **not** mean all search algorithms reach classes equally quickly, only that the registered mutation graph has these exact distances.

## REMINT-1 — isometric semantic grammar remints preserve registered bias

Let `phi:P→P'` be a bijection preserving, pointwise, semantic class and description length, and preserving directed edges and the start set exactly. Then `phi` bijects every defining set for `L,N,Q,A`; graph isomorphism transports every start-rooted path length-for-length, hence preserves `d` and `R`. Any selector depending only on preserved external semantic data and these statistics is invariant/equivariant.

The executable certificate checks all `4!=24` surface-node permutations of a four-presentation fixture: all 24 certify and all preserve every registered statistic and selection.

## REMINT-2 — same semantic image is insufficient

The frozen `GA/GB` pair has identical semantic image `{ROOT,A,B}` but swapped code lengths/search geometry:

- `GA`: `(L,d)(A)=(1,1)`, `(L,d)(B)=(2,2)`;
- `GB`: `(L,d)(A)=(2,2)`, `(L,d)(B)=(1,1)`.

For candidate set `{A,B}`, the registered diagnostic selector changes from `A` to `B`. The obvious semantic-name correspondence fails the isometric-remint gate because lengths (and geometry) are not preserved.

Thus:

`same semantics != same description bias != same reachability bias != same grammar-relative selection`.

## KOL-BOUND — finite/non-asymptotic boundary

Classical invariance results for universal description systems allow description-system-dependent additive constants. They do not imply equality of finite `L_G`, bounded syntax masses `Q_G`, or mutation distances `d_G`. This capsule does not claim a new Kolmogorov-complexity theorem.

## Falsifiers

The claim is RED if any registered presentation is omitted/duplicated, BFS disagrees with wave/Floyd–Warshall, a certified remint changes a protected statistic, a malformed remint is accepted, or the same-semantics hostile fails to change the registered grammar-relative selection.
