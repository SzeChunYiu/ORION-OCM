# GMI #833 E2 — finite grammar bias and remint boundary

This capsule measures representation/search bias on one frozen 126-presentation slice of merged `G0-reg-v1`.

It separates three statements that must not be conflated:

1. **semantic coverage** — which protected behaviors the grammar can present;
2. **description bias** — how many/short presentations each semantic class receives;
3. **reachability bias** — how the frozen mutation graph places those presentations relative to the registered start.

The exact result is conditional on the frozen semantic test set `(),(0,),(1,)`, step budget 6, instruction-count length, and mutation graph in `FREEZE_V1.md`.

The capsule proves an invariance theorem only for **isometric semantic grammar remints**: bijections preserving semantic class, length, adjacency, and starts. It also provides a same-semantics counterexample where changing length/search geometry reverses the grammar-relative selection. Therefore semantic equivalence alone is not a representation/search-neutrality theorem.

Claim ceiling:

`GMI_FINITE_GRAMMAR_BIAS_AND_REMINT_BOUNDARY_AT_REGISTERED_G0_SCOPE`
