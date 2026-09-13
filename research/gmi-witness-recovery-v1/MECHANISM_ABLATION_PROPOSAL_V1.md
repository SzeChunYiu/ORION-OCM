# Proposed mechanism ablation — prepared, not executed

Question: does this recovered graph need learned DENSE coefficients, or does
the descriptor identify a fixed-width key channel within a memory mechanism?
This is warranted by the actual pruned witness, not by the label alone.

The original pinned VM supplies the matched parent. DENSE emits a list of
parameter-name strings (vm.py:162). INSERT forms key bits using
getattr(value,"v",0)>0 (vm.py:300--303), so the witness's width-one DENSE output
yields key (0,) regardless of its numeric cell value. Feedback populates
EVIDENCE from the actual x,y directly (vm.py:367--374). This graph has no
GRAD, LINEAR or AFFINE node. These are source-derived facts, not a completed
intervention result or a claim of causal necessity.

MECHANISM_ABLATION_CANDIDATES_V1.json retains three constructed graphs.
The frozen typechecker accepted every graph; no ecology evaluation was run.

| Arm | Change | Purpose |
|---|---|---|
| Original | Exact saved pruned graph | Clean matched baseline |
| Zero vector | Replace dense0 with INPUT(width1) -> NONLIN(NEG) -> NONLIN(ReLU); reroute its two outgoing edges | Same one-bit zero key, no DENSE cells |
| Variable key | Same replacement graph, final NONLIN changed from ReLU to NEG | Same width and node/edge structure, input-dependent one-bit key |

Frozen INPUT emits nonnegative bit values. Therefore ReLU(-x)=0, while
-(-x)=x. Every replacement edge remains VEC-typed. This uses admitted
primitives and fully connected input ports, without relying on malformed
operands or a newly invented literal primitive.
The two replacement graphs differ in one NONLIN parameter. Their operation
types differ, so actual resource ledgers must be compared; cost equality is
not assumed. The replacement adds two nodes relative to the original while
removing its dense cell. Charge that change explicitly.

Smallest informative run: evaluate the three fixed pruned graphs under the
same six historical controls and five probe ecologies, 33 direct ecology
calls total. No search, no additional pruning, no threshold change, and no
parameter fitting. Validate the cloned baseline fingerprint before executing.
Retain complete served traces, capabilities, cell/store/update ledgers and
all measured resource coordinates. Treat exceptions as failures, never as
distinct probe answers. Keep all outputs, including contradictory outcomes.

If the zero-vector arm matches every declared served trace and remains
admissible while eliminating DENSE, coefficient learning is unnecessary for
this witness's behavior at that tested scope. If the variable-key arm changes
responses, the constant key channel is a candidate explanation. If it also
matches, inspect which outgoing channel is causally used before claiming a
role. A failed zero-vector replacement calls for locating the differing
runtime representation, ordering, or resource effect before changing a claim.
None of these outcomes is promised by this unexecuted proposal.
