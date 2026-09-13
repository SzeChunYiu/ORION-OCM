# Grand GMI Planning Semantic-Resolution Claims V1

Status date: 2026-09-12. Uses `PSR-*` identifiers independently of the concurrently advancing master ledger.

| ID | Claim | Status | Scope |
|---|---|---|---|
| PSR-1 | With a unique hidden candidate partitioned into semantic classes of sizes `n_i`, equality-verifier-only identification of the class requires exactly `N-max_i n_i` worst-case deterministic queries. | THEOREM + 1,360 EXACT MINIMAX CHECKS | finite exact verifier channel |
| PSR-2 | In a full `b`-ary depth-`d` unique-goal tree, if only the first `q` plan symbols are required, exact leaf-verifier query complexity is `b^d-b^(d-q)`. | THEOREM + EXACT CELLS | black-box unique-goal tree |
| PSR-3 | Plan output information and planning transformation cost can separate exponentially: binary depth 10 first-action obligation is one bit but needs 512 leaf-verifier calls. | EXACT COROLLARY | PSR-2 channel |
| PSR-4 | A goal-respecting right-congruent state quotient preserves finite-horizon reachability and successful first-action sets exactly under quotient dynamic programming. | THEOREM + 340 EXACT CHECKS | finite deterministic known transition system |
| PSR-5 | Raw planning histories may be quotient-null: the binary modular witness has 4,096 depth-12 histories / 8,191 raw tree nodes but two sufficient process states. | EXACT WITNESS | modular deterministic system |

Aggregate terminal: `GRAND_GMI_PLANNING_RESOLUTION_TRANCHE_ALL_GREEN`.

The verifier exponential is not asserted outside its declared information interface; informative internal feedback, heuristics, models, noisy/multiple goals or other channels require a new derivation.