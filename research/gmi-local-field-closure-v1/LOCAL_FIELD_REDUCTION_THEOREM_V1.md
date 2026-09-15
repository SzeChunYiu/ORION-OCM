# Local-field/cellular reduction theorem and interventions v1

## Carrier and local-radius microscope

For a finite directed, port-labelled graph `G=(V,E)` and alphabet `A`, a
radius-one cellular carrier is

`F(G,f)(x)_v = f(x_v, x_left(v), x_right(v))`.

The committed DC2 microscope instantiates `A={0,1}` on rings of length
`L in {8,16,32,64}`, executes three synchronous steps, searches all 256
elementary rules, and compares a shared 8-bit rule with independent 8-bit
rules at every site.  It contains 144 ecology cells and four rows per cell.

## Exact lesion/regeneration intervention

Take the all-one fixed point and lesion exactly one site to zero.  Elementary
rule 232 is three-bit majority: the lesioned site sees `101` and returns to
one, while every other site retains a majority of ones.  Thus every one of the
`L` possible single-site lesions regenerates in one synchronous step for each
tested `L in {4,8,16,32}`.  The matched rule-204 (identity) control repairs
zero lesions, so recovery is caused by the update law rather than by the target
or lesion generator.  This is a bounded single-site regeneration result, not a
claim about arbitrary lesions, biological regeneration, or neutral recovery.

## Exact topology intervention

Hold rule 90, the initial configuration, site labels, update schedule, and
zero boundary convention fixed; change only a path into a ring.  Rule 90 is
`left XOR right`.  The two outcomes differ exactly when either endpoint is
one: closing the path supplies the missing endpoint values across the new
edge.  Therefore `3*2^(L-2)` of all `2^L` inputs are topology-sensitive and
the fraction is exactly `3/4`.  Exhaustive enumeration verifies the formula
for `L in {4,8,12}` and also exhibits `0001` at `L=4` as a concrete witness.

## Scaling law

The DC2 receipt measures, for every cell, `desc(FIELD)=8` and
`desc(FIELD_NONLOCAL)=8L`; the description ratio is exactly `L`.  One
three-step rollout costs `33L` charged scalar operations for either row, while
the declared native count is `3L` site updates.  Identification needs one
trajectory for the shared row in 15/16 `(L,rule)` groups and two in the other;
the unshared row needs 8--128 on the registered grid.  These are exact finite
linear description/execution laws and grid-resolved sample observations, not
an asymptotic universality claim.

## Parent reductions

1. **D6 dynamical system.** `F(G,f)` is a deterministic map on the finite
   global state space `A^V`; iterating a local field is literally iterating a
   D6 transition map.  Compilation preserves every trajectory exactly.
2. **D7 distributed system.** Put one process at each vertex.  In a round each
   process sends its current symbol over each incident port, applies `f` after
   receiving neighbour symbols, and synchronously commits.  Induction on
   rounds gives the same state at every vertex.  Communication is `2|E|`
   symbols per round for the directed send implementation.
3. **GNN/NCA parents.** The update is directly an NCA layer.  It is also a
   message-passing layer with port-labelled messages, an ordered aggregation
   tuple, and update `f`; sharing `f` over vertices gives equivariance under
   port-preserving relabellings.  Unlabelled commutative aggregation would not
   realize every left/right-asymmetric elementary rule, so the port condition
   is part of the reduction rather than hidden overhead.

The reductions are bounded and answer-preserving.  Consequently these
experiments support cellular locality and perturbation sensitivity but do not
establish a new primitive beyond D6/D7/NCA/message passing.

## Claim ceiling

`BOUNDED_BINARY_RADIUS_ONE_FIELD; SINGLE_SITE_REPAIR; PATH_VS_RING;
EXACT_PARENT_REDUCTION`.  No blind family-hidden search was run, so neutral
recovery remains open.
