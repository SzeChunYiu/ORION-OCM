# Grand GMI Claim Ledger V7 — physical resource bridge

Status date: 2026-09-12. Additive to V1–V6.

| ID | Claim | Status | Scope |
|---|---|---|---|
| GG37 | An exact semantic cut requiring `m` mutually distinguishable messages requires at least `m` reliably distinguishable protected physical carrier states; a binary carrier therefore needs at least `ceil(log2 m)` logical bits. | THEOREM | exact protected cut |
| GG38 | A GMI semantic/transformation necessity becomes a physical resource lower bound only through a valid declared substrate lower-bound map/resource monotone. | THEOREM | declared substrate physics |
| GG39 | Standard Landauer reset cost applies conditionally to an actual declared physical reset under its thermodynamic assumptions, not merely to semantic quotienting. | CONDITIONAL BRIDGE | conventional symmetric/equiprobable reset or appropriate generalized law |
| GG40 | Response-equivalent machines can have different logical irreversibility schedules and physical resource vectors; semantic compression does not determine dissipation. | THEOREM + EXACT WITNESS | protected behavior equivalence |
| GG41 | In a finite cyclic implementation, retained history that makes an operation injective must eventually be uncomputed, exported, retained in counted storage, or physically reset. | BOOKKEEPING THEOREM | declared finite cyclic boundary |

## Exact hostile evidence

- `m=1..64`: 64/64 exact binary capacity minima satisfy `2^b >= m` and `2^(b-1) < m` when `b>0`.
- all 278 set partitions of physical microstate sets of sizes 1..6: semantic response classes never exceed physical microstates.
- parity witness: direct 4-to-2 map has two preimages per semantic output and discards exactly one logical bit for uniform inputs; reversible `(x,y,0)->(x,y,x xor y)` preserves four full logical states while producing the same protected parity output.
- standard power-of-two reset bookkeeping `m=1,2,...,64` gives exact symbolic Landauer multipliers `0..6` times `k_B T ln 2` under the declared ideal assumptions.
- identical protected semantic output is exhibited with different immediate memory/reset accounting.

Aggregate terminal:

`GRAND_GMI_PHYSICAL_RESOURCE_BRIDGE_TRANCHE_ALL_GREEN`.

## Parent boundary

Landauer, Bennett, Sagawa and stochastic thermodynamics supply the thermodynamic parent laws. Grand GMI's contribution is the typed bridge from obligation-derived semantic necessities to substrate-specific physical-resource constraints. No universal joules-per-bit or joules-per-inference constant is claimed.