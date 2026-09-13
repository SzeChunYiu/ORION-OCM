# Zero-cost computation: proper values and constructive stopping

## Register and parents

Use the finite deterministic register of
[VOC](../gmi-value-of-computation-v1/VALUE_OF_COMPUTATION_THEOREM_V1.md):
finite nonempty S, finitely many cognitive edges s→t of rational charge e≥0,
and finitely many certified terminal actions per state of rational charge c≥0.
The state contains everything relevant to future transitions, legal actions,
adequacy and charges. Policies may use history. A serving episode takes finitely
many edges and then a terminal action; nonserving/infinite runs are infeasible,
with value +∞. Minima of empty sets are +∞. This is a supplied model, not a
learned law or action-verification mechanism.

[Bertsekas (2020), §§I–II](https://arxiv.org/html/1711.10129v2) distinguishes
proper-policy values from unrestricted accumulated-cost values. We use that
mechanism in the finite deterministic case; his infinite-state stochastic
hypotheses are not silently imported. [Sedgewick–Wayne, §4.4](https://algs4.cs.princeton.edu/44sp/)
supplies the established shortest-path and cycle-removal parent. The added
choice is an exact lexicographic progress certificate in this VOC interface.
This is an adaptation/application, not a claim of new graph theory.

## ZCS-1 — attained proper value and the greatest Bellman solution

Let V contain exactly those states with a finite path to a terminal action.
Let J(s) be the infimum cost of serving policies from s, with J=+∞ outside V.
Then J is finite and attained on V, satisfies

    J(s)=min({c: terminal at s} ∪ {e+J(t): edge s→t}),

and is the greatest solution of this equation in [0,+∞]^S.
A cost-minimizing path can be chosen with at most |V|−1 cognitive edges.

**Proof.** Every serving path stays inside V. Removing a repeated-state
segment preserves its suffix and cannot increase cost. After all cycles are
removed the path has at most |V|−1 edges. There are finitely many such paths
and terminal choices, so their minimum is attained. First-action decomposition
proves Bellman's equation on V. Outside V there is no terminal and every
successor is outside V, so both sides equal +∞. For any other nonnegative
extended solution W, Bellman's inequalities along a finite serving path give
W(s)≤its total cost. Hence W≤J on V; outside V the inequality is automatic.
Thus J is the greatest solution. This does not assert uniqueness. ∎

For a terminal cost1 and zero-cost self-loop, every j∈[0,1] solves the scalar
equation. The serving value is J=1. Initializing ordinary iteration at zero
can return the nonserving value0; a finite Bellman residual alone is inadequate.
Nonnegative value-domain restriction is part of this statement.

## ZCS-2 — a stationary optimal selector without positive edge prices

For s∈V let L(s) be the smallest number of cognitive edges among serving paths
with cost exactly J(s). Then 0≤L(s)≤|V|−1 and the pair (J,L) satisfies the
lexicographic equation

    (J(s),L(s)) = min_lex({(c,0): terminal at s}
                        ∪ {(e+J(t),1+L(t)): edge s→t, t∈V}).

Choose any action attaining this pair minimum. A terminal action serves;
an edge satisfies J(s)=e+J(t) and L(s)=1+L(t). Consequently every selected
edge strictly decreases L. The stationary selector serves from every s∈V
in exactly L(s) cognitive edges, at total cost J(s).

**Proof.** Minimum edge count exists among the finite cost-optimal simple
paths. An optimal suffix must first minimize cost, then length: substituting
a cheaper suffix would contradict J; substituting an equal-cost shorter suffix
would contradict L. Conversely every displayed action/suffix is a serving
candidate. This proves the paired equation. The integer descent proves
termination and telescoping cost proves optimality. A repeated zero-cost cycle
can be removed to shorten a cost-optimal path, so the length bound follows. ∎

This supplies a concrete progress mechanism, rather than requiring every edge
to have a positive price. Arbitrary scalar-greedy tie choices can still loop.
If immediate stopping and continuation have equal optimal cost, the paired
rule stops because 0<1+L(t). An equal-cost continuation may still be a valid
optimal serving policy; the rule chooses the shortest such policy.
Zero-cost cycles with no path to a terminal stay infeasible.

## ZCS-3 — exact finite construction, costs and boundaries

Initialize each state with its least terminal pair (c,0), or infinity.
For k=1,…,|S|−1, synchronously retain each old pair and compare every edge's
(e+J_{k−1}(t),1+L_{k−1}(t)). Induction gives the least pair over serving paths
with at most k edges. By ZCS-1/2 the final table is (J,L). Construct each
stationary action from the paired equation, never from scalar J alone.
The rank is synthesized from the graph; no externally supplied horizon or
positive epsilon is necessary.

For S states, E edges and T terminal actions, this implementation uses
O(S(E+S)+T) exact arithmetic/comparison operations and O(S) auxiliary labels
in addition to the retained graph and returned policy. It scans all edges
in each of S−1 passes even if the table stabilizes earlier. This is an operation
bound, not constant-time rational arithmetic, a measured runtime, or free
synthesis. Labels add at most S input rational charges; with B-bit input
numerators/denominators, a direct common-denominator bound is O(SB+log S) bits
per rational label. Input, program, synthesis workspace, verification and
execution must be charged in the actual substrate before an economic claim.
A policy table stores one indexed action per viable state plus the declared
infeasible outcome; storing the whole value/rank table is optional at runtime.

Nonnegativity matters: a charge−1 self-loop and terminal0 permit arbitrarily
negative serving costs and no optimum. Finiteness matters: a zero-cost chain
with terminal costs 1/(n+1) has serving infimum0 at its root but no attaining
finite path. These are boundary countermodels, not in-scope failures.
A stochastic geometric-success process may have a proper finite-expectation
policy with unbounded realized duration; the deterministic edge-count theorem
does not apply. The unchanged VOC stochastic witness records that distinction.

## Evidence

Independent controls enumerate actual stationary policies, following their
edges until a terminal or a repeated state. Their complete serving outcomes
are compared to the constructed cost-and-length table. They also run the
returned selector from every state, including zero-cost cycles, ties, absent
terminals and trapped regions. Scalar-greedy looping and negative/unbounded
boundary witnesses prevent a false upgrade from a Bellman equation to serving.
Finite checks challenge this construction; the proofs carry its universal
finite-register quantifiers. No campaign or general physical claim is made.
