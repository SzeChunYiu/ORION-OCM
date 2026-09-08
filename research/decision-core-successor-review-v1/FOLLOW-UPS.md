# Small source-contract follow-ups

These are source-derived corrections queued outside the three principal findings.
They require no change to the selected mathematical parent.
No checks or examples below were executed.

## P3 — action-set equality should not depend on container order

[decision_core.py 180–183](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L180)
compares tuples of admissible actions. Two equivalent states exposed as
`("a","b")` and `("b","a")` are rejected despite having identical action sets,
contracts and transition laws. Theorem 10's condition is set equality.
Compare canonical sets of action identifiers (and validate uniqueness if needed),
or explicitly narrow the input contract to one globally canonical action order.
This is a false-negative admission problem, not unsafe merging.

## P3 — preserve iterables across all cognition steps

[decision_core.py 133–135](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L133)
permits transition iterables, but
[151](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L151) materializes them inside the budget loop.
A one-shot iterator is exhausted after its first visit; at the second step its
sum becomes zero and the function raises. Materialize transitions once before
iteration, or require and document re-iterable collections. Use the same contract
for cognitive action collections, which are also revisited at each step.

## Input admission scope — normalized signed masses are not probability kernels

The sum-to-one checks at
[153](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L153) and [206](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L206)
do not reject negative entries such as (-1,2), which sum to one. If these helpers
serve as theorem-admission checks, reject nonfinite/negative probabilities,
unknown successor states and unsupported cost domains, then check normalization
under the chosen exact/approximate policy. Alternatively document that a separate
trusted validator must establish those mathematical preconditions first.
This is an input-contract gap; theorems assuming genuine kernels are not refuted
by invalid signed inputs.

## Bounded future regression cases

On the authorized Linux lane, after implementation is requested, include F1's
finite information table in the mathematical receipt; use F2's near-equal dyadic
laws and exact equal laws for bisimulation; use F3's integer stop/action ordering;
and include two-step cognition with a generator and permuted admissible actions.
These are proposals, not a registered or executed test pass. Existing tests are
small examples, not exact-arithmetic certificates for untested numerical rows.
