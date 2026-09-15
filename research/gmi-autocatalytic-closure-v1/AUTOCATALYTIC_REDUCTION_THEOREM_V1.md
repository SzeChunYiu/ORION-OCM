# Constructive/autocatalytic state and parent-reduction theorem v1

## State and collision

A finite constructor carrier is (A,C,R,H): artifact alphabet A, built set C,
typed construction rules R, and lineage/history H. BUILD applies a rule to built
reagents; CLOSE iterates BUILD to a fixed point; MEMBER queries the closure.
Products re-enter as reagents.

Two systems with seeds {01,110} have the same current membership answer for 01.
With bounded concatenation, 0111001 enters the future closure; with the rule
removed it does not. Present output agrees while future constructibility differs,
so rules belong to obligation-sufficient state.

## Parent reductions

- D8: represent artifacts as installed components. BUILD is typed component
  addition/replacement and lineage is D8 development history.
- D4/D5: a finite program enumerates rule applications; breadth-first derivation
  search with a visited set terminates on the bounded artifact universe.
- Reaction network: create one species per artifact and one catalytic reaction
  u+v -> u+v+product per rule instance. Under monotone presence semantics,
  reaction reachability and constructor closure coincide by induction on
  derivation/firing length.

These compilers preserve finite closure membership. A D2 table given the full
closure is exactly the eager candidate at serve time.

## Executed regime

The hash-verified N8 receipt covers limits 8–18: closure grows
14, 26, 47, 84, 149, 263 while the no-feedback twin stays at capability 0.375.
Eager, lazy, search, and full-table answers agree in 18/18 parent comparisons.
The predicted niche is deep constructibility under reuse: rules describe an
answer set much larger than the seeds, and construction/materialization phases
exchange frontier occupancy as compile cost is amortized.

## Claim ceiling

The result is positive for constructor-state necessity and phase prediction but
negative for novelty: bounded monotone closure reduces to D8, D4/D5, reaction
networks, and D2 materialization. Neutral recovery remains open.
