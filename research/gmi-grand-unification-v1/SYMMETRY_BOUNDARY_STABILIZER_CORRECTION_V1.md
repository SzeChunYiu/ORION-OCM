# Symmetry must preserve access and reachability

This repairs the master declaration's automorphism arguments. It does not
change [GG20](SYMMETRY_TO_MORPHOLOGY_THEOREM_V1.md), whose averaging proof
already requires a group-stable feasible kernel class.

## Boundary-preserving static group

Use G = Aut(P, B, E, Omega, Theta, rho, epsilon), including the machine boundary
and free information B and the error contract. A registered action of G must
map every admitted feasible kernel to an admitted feasible kernel and preserve
the obligation and resource assumptions used by GG20. Merely preserving an
abstract task's input/output relation is insufficient.

For a concrete counterexample, X={0,1}^2 has the uniform prior, binary actions
and target a=x0 XOR x1. Risk is expected error, allowed at most 1/2. Every
kernel has the same constant resource vector, and the intervention family is
invariant under coordinate swap. Boundary B reveals only x0; admitted kernels
therefore depend only on x0.

K chooses a=x0. It is B-measurable and has error 1/2. Swapping input coordinates
preserves the target, prior, tolerance and constant resources, but transports
K to K' choosing a=x1, which is not B-measurable. Their equal mixture assigns

    P(a=1 | 00) = 0,       P(a=1 | 01) = 1/2.

The two inputs share the same admitted observation x0=0. Thus the mixture
violates B even though the tuple omitting B admits the swap. Restricting the
group to boundary-preserving transformations removes that invalid operation;
no new averaging principle is needed.

## Development adds a further stabilizer

For a fixed development process and resource allowance b, the reachable group
is the subgroup of the static group satisfying

    g Reach_D(b) = Reach_D(b).

Equivariance of development transitions alone is insufficient. A sufficient
condition also preserves the admitted initial-state set, resource charges
and allowance, and the state/realization projection. Transform a legal path
from an admitted initial state: equivariance gives a legal transformed path
with the same charges and an admitted initial state. This proves one inclusion;
apply the inverse transformation for the other. Initial-state and cost
preservation cannot be omitted from that argument.

For the smallest counterexample, take one input, binary actions, no correctness
restriction and the full static Bernoulli-kernel interval, with constant
resources. Swapping actions preserves this convex static class. Development
starts only at delta_0 and admits no updates. Reach_D(b)={delta_0} for every
allowance. The action-swapped delta_1 and their equal average are statically
feasible but unreachable. Restricting to the reachable-set stabilizer excludes
the swap; admitting both initial endpoints and a charged mixing operation
would be a different development contract.

Both repairs are ordinary group restriction under the existing feasibility
hypotheses. They yield no new morphology, empirical symmetry, attainable
optimizer or unrestricted development theorem.
