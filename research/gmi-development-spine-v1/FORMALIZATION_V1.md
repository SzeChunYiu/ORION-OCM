# H development / adaptation / evolvability spine v1

## Objects

Let `X` be a finite set of developmental states and let `E` be directed legal transitions with nonnegative charged cost `c(e)`. A developmental path cost is the sum of its edge costs. For a future obligation with satisfying set `G subseteq X`, define

`A(x,G) = min_{path x -> g, g in G} sum c(e)`,

with `A(x,G)=infinity` when `G` is unreachable.

This is adaptation burden. Morphology-search burden is the same cost-to-go object when `G` is a prospectively registered target morphology set rather than a task-satisfying state set.

## H-C: current capability is not future learning potential

Current capability is evaluated on the current obligation set without further adaptation. For finite future obligations `G_1,...,G_n` and budget `B`, define learning potential

`L_B(x) = (1/n) * sum_i 1[A(x,G_i) <= B]`.

**Separation witness.** Two states `reset` and `learned` emit identical current outputs and therefore have equal current capability `1/2`. Their future burdens are `(5,6)` and `(1,2)` for two future obligations. At budget `B=2`,

`L_B(reset)=0` and `L_B(learned)=1`.

Therefore current capability does not identify future learning potential, even in a finite exact world.

## H-B: shortest-path burden theorem

Because all edge costs are nonnegative, Dijkstra relaxation returns the minimum charged cost from `x` to every reachable state. Taking the minimum over `G` therefore computes `A(x,G)` exactly. Unreachable targets retain infinite burden rather than being assigned an arbitrary finite penalty.

The same theorem applies to morphology-search burden when graph edges are defined to include all charged candidate-generation/evaluation work represented by a developmental transition.

## H-U: useful-descendant mass

Let `w(y)>=0` be a prospectively registered weight on useful descendant states or behavioral-equivalence classes. Define

`U_B(x) = sum_y w(y) * 1[A(x,{y}) <= B]`.

The sum is over descendant identities/classes, not paths. Therefore adding a duplicate path to an already reachable descendant leaves `U_B` unchanged. This prevents path multiplicity from masquerading as evolvability.

## H-T: transfer sign

For a reset state `x_0`, continued state `x_c`, and the same future obligation `G`, define

`T(G) = A(x_0,G) - A(x_c,G)`.

`T>0` is beneficial transfer, `T=0` neutral, and `T<0` harmful transfer. This definition makes the sign auditable against independently computed burdens and preserves reachability infinities.

## H-P: developmental path dependence

Suppose two histories produce states `x` and `x'` with identical present observable outputs. They are path-dependent at a registered future scope iff there exists a future obligation `G` such that

`A(x,G) != A(x',G)`.

The current-output equality is load-bearing: if current outputs already differ, future burden differences do not isolate hidden developmental history.

## H-I: free optional inheritance monotonicity

Let base developmental graph `D` and inherited graph `D+'` share the same registered state set. Assume every edge `(u,v,c)` in `D` remains present in `D+'` with exactly the same cost; `D+'` may add extra edges but cannot remove or reprice old ones.

Then every legal base path remains a legal inherited path at the same cost. Hence the inherited feasible path set is a superset of the base feasible path set. Taking a minimum over a superset cannot increase the minimum:

`A_{D+'}(x,G) <= A_D(x,G)`

for every start `x` and target set `G`.

For every fixed budget `B`, any descendant satisfying `A_D(x,{y}) <= B` also satisfies `A_{D+'}(x,{y}) <= B`. With nonnegative weights,

`U^{D+'}_B(x) >= U^D_B(x)`.

So genuinely free optional inheritance cannot worsen minimum adaptation/morphology burden or reduce useful-descendant mass.

### Exhaustive finite check

The test suite exhausts all `3^6 = 729` relations on the six possible directed unit-cost edges among three states, where each edge is either absent, extension-only, or present in both base and inherited graphs. Every legal optional extension preserves or improves all shortest-path distances from the registered start state.

### Scope-breaking counterexample

Base graph: one edge `s -> g` of cost `1`.

A so-called inherited system replaces it by a mandatory `s -> g` cost `3`. Burden rises from `1` to `3`, but this is **not** a counterexample to the theorem because the old cost-1 option was removed/repriced. Mandatory maintenance, shared-budget coupling, compulsory serialization, or changed transition costs are precisely the cases the theorem excludes and later H rows must model explicitly.

## Claim boundary

These are finite exact definitions and feasible-set/shortest-path proofs at **G2**. They do not establish G7 developmental prediction, empirical inheritance advantage, maintenance-cost crossover, architecture expansion/pruning, self-compilation, multi-generation open-endedness, or learned-representation/operator/search-prior benefit.
