# Native parameter adjoint correction — NAR-1–3

This repairs one source-level parameter attribution error. It is not a new
learning mechanism, a capability result or a neural-family verdict.
The immediate parent is the [complete pinned PR551 audit](raw/pr551-grad-audit-20260913/PR551_GRAD_DIAGNOSIS_CORRECTION_7328D5B3_V1.md),
including its once-only positive and zero-input controls. All31 payloads and
the original manifest are preserved. Subsequent finite validation is recorded
separately; no historical campaign or measurement is overwritten.

## NAR-1. Bug and minimal positive repair

The original [vm.py](raw/pr551-grad-audit-20260913/raw/gmi_microscope/vm.py)
at `7328d5b3b0a5111fd43c3e277679faf0edeee1bb` is byte-identical to active
main `ef6de91af6f6ce692e0f8bd9725f8ad4f4435e9d` (SHA256
`ef6dba6b1b418b6750650b0518c817432c098efb746afeae9dea0ace6bdfe932`).
Its `_dot` constructs p=w*x with tape parents (w,x),(x,w), but attaches
`("param",name)` to p. `_backprop` adds the adjoint of a tagged node directly
to that parameter. Thus it returns the product adjoint instead of multiplying
by the input before attributing the result to the weight.

The frozen six-node native control has x=0, target_fx16, weight_fx8 and lr_fx1.
Its output is0 for EVERY weight, so its parameter sensitivity is exactly0,
including in the discrete/clipped forward VM. The old tape instead attributes
−16 and writes8→9. The diagnosis therefore does not rely on differentiating a
quantizer or choosing a surrogate at a boundary.

The correction puts the existing parameter marker on the weight leaf w and
removes it from p. The existing multiplication edge now performs the required
input scaling before parameter accumulation. No forward arithmetic, state
initialization, update ordering, learning rate, basis or ledger rule changes.
The corrected runtime has a new source identity; its current results are not
substituted into the old raw records.

## NAR-2. Exact scope: registered ordered clamped pullback

The fixed scale is S=16 and representable integers are[-128,127]. Write
clip(z)=min(127,max(−128,z)) and q(a,b)=clip(floor((ab+8)/16)).
The existing annotated tape implements the following local pullback convention:
for an edge with derivative label d, add q(current_adjoint,d) to its parent's
adjoint with clipping after each addition, in the registered reverse traversal
order. Parameter occurrences are accumulated by their declared cell name,
again clipping each addition. This convention is kept unchanged.

For p=q(w,x), the annotated derivative toward w is x and toward x is w.
With the corrected leaf tag, the weight contribution is q(g_p,x). The old
tag contributed g_p instead. For a zero input, q(g_p,0)=0 exactly. For x=S,
q(g_p,S)=g_p, recovering the old positive no-alarm case. These equalities hold
for every representable adjoint, including either sign and saturation limits.

A parameter may occur in multiple products. Each read creates its own weight
leaf, whose scaled contribution is accumulated under the common cell name.
A shared intermediate Val first receives all downstream contributions in
reverse traversal order before propagating through its own incoming edges.
This is the existing reverse-accumulation dependency discipline, not a separate
path-sum approximation. The tests cover tied cells, a shared intermediate and
two composed linear products.

Bias handling remains valid for this convention. A bias's local derivative
is S and q(g,S)=g. The existing bias marker on the result of its addition
therefore records the same contribution as the bias leaf's identity edge.
Both `_dot`'s optional bias and AFFINE's explicit bias path are checked.
No assertion of order-independent saturated accumulation is made: the tied
three-occurrence control explicitly preserves the reverse clamping order.

For a smooth unquantized real arithmetic graph, reverse AD's chain rule is the
mature parent. The registered integer pullback agrees, after scaling, where
all forward values, local derivatives, products, accumulated adjoints and
error seeds are exactly representable and no clipping/rounding changes them.
This statement concerns that underlying real graph. It does not make the
rounded fixed-point program differentiable. The45 central-difference controls
use a quadratic loss on exactly representable unsaturated linear products;
central differences are exact for these degree-two functions.

Outside those conditions the VM uses its declared rounded/clamped surrogate
adjoints. A retained boundary control has identical saturated forward outputs
at w−1,w,w+1 but nonzero registered pullback. This explicitly rejects a claim
that the correction computes literal derivatives of quantization/clipping.
Existing ReLU-at-zero and other surrogate choices are not changed or certified
by this repair. No global convergence, descent or differentiability follows.

## NAR-3. Verified outcomes and resource boundary

Both B0's explicit-ADJ route and B1's native-ADJ route retain weight8 at zero
input after the fix. At x=1,target0 they retain the original8→7 state/response
change, despite GRAD having no outgoing graph edge: update nodes have side
effects and are scheduled independently of dataflow output consumption.
AFFINE still changes its bias16→15 at x=0 while leaving the unrelated weight8.

The new finite certificate checks2197 scalar fixed-point combinations,
45 exact-polynomial finite differences,27 tied-parameter combinations, shared
and composed paths, identity biases and saturation/order boundaries. It retains
complete before/after Val tapes, Machine tapes, cells, authored ledgers and
outputs for the versioned native controls. The original full state/ledger
and zero-input tape reproduce their retained source records.

Keeping ledger code unchanged does NOT mean equal realized charges. At zero
input the correct zero gradient skips the existing learning-rate multiply and
write: B0 update charge changes13→10; B1 changes9→8. The nonzero no-alarm
control preserves its full state/ledger. No new operation weight is fitted,
and no claim that the authored ledger measures host work is introduced.

This unit does not rerun any B6 search, learner probe or campaign. The existing
16-event historical zoo regression and six other source-sensitive historical
fixtures are pinned to the original VM. Their goldens are unchanged; they do
not evaluate a corrected-runtime campaign.
It does not infer what a corrected search would discover, remove all native
learning limitations, or establish a broader family frontier. The old proposal,
archive and finite-prefix/cost/causal-ranking qualifications remain historical
source-scoped evidence. A new runtime requires fresh provenance for any later
experiment that chooses to use it.
