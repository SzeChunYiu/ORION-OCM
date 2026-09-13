# Structural threshold repair — STR-1–5

Primary parents are [Paturi–Saks §3.1](https://cseweb.ucsd.edu/~paturi/myPapers/pubs/PaturiSaks_1990_focs.pdf),
the [CPython3.12 opcode specification](https://docs.python.org/3.12/library/dis.html)
and its [pinned expression compiler](https://github.com/python/cpython/blob/v3.12.3/Python/compile.c#L5687).
This is a correction and elementary specialization, not a new general circuit
lower bound. [Parent subtraction](../gmi-structural-threshold-repair-v1/PARENTS_AND_COSTS_V1.md)
and [historical source bindings](../gmi-structural-threshold-repair-v1/SOURCE_PARENTS_V1.json)
remain in the standalone archive unit.

## STR-1. Exact model and what the old enumeration establishes

The task is parity on all eight inputs x=(a,b,c) in {0,1}³, with exact integer
output. One hidden layer consists of integer affine thresholds; the output
is an integer affine threshold of hidden bits ONLY. No raw-input or shared
preactivation skip connections enter the output.

The registered Python source has mandatory tuple unpacking a,b,c=x and one
of two shapes. A computes each hidden threshold from its own flat linear
form over a,b,c. B computes one shared flat form s and then thresholds s.
Every hidden line assigns int(form>=threshold) to a separate local; the
return is int(flat_form_of_hidden_bits>=threshold). Coefficients and
thresholds are arbitrary integer literals admitted by the compiler. Terms
with zero coefficient are omitted; each other variable appears once.
Term order is unrestricted. Linear forms use literal coefficients, loads,
multiplication, unary signs, addition and subtraction, without delegation,
aliases, lookup, factoring, vectorization or extra shared expressions.
The standard int builtin is not rebound. All task inputs are ordinary ints.

Only candidate-frame nonspecialized opcodes, excluding RESUME and CACHE, are
counted. The exact compiler-layout contract is stated in STR-4. This includes
the int call opcode but excludes the callee's work, integer bit complexity,
description size, acquisition, timing, memory and hardware costs.

The old [-2,2] output grid does NOT cover arbitrary coefficients: at four
hidden bits it contains 986 functions and omits weights (3,2,2,1), threshold4.
Matching hidden behavior sets on two finite grids also does not prove every
cost-optimal coefficient pattern or every shared-form configuration covered.
Its finite search remains evidence for its actual bounded grammar.
The false rendering lemma is independently falsified: -a+b+c and b+c-a agree
on all eight inputs, but the former costs one more opcode in the registered
layout. Neither finding alone disproves the old numerical minimum.

## STR-2. At least three active hidden predicates

Absorb constant hidden predicates into the output threshold and ignore
zero-output-weight predicates for mathematical analysis. Let r be the
remaining nonconstant predicates with nonzero output weights.
The executed source may still contain the ignored lines; their instructions
are not subtracted from the original machine's cost.

A threshold on two Boolean inputs realizes neither pair of opposite square
corners: the positive and negative pairs have the same midpoint, contradicting
strict separation. The other fourteen functions are constants, literals,
one-corner conjunctions, and three-corner disjunctions. Therefore a network
with at most two active predicates has a positive region that is a halfspace,
an intersection of two halfspaces, or a union of two halfspaces, apart from
the trivial constants. Complements of threshold predicates may be open
halfspaces; the following argument works for both open and closed boundaries.

Any two distinct vertices of the same parity in the three-cube differ in
two coordinates. Flip one differing coordinate in each vertex: the resulting
two opposite-parity vertices have the same midpoint as the original pair.
Consequently a halfspace containing no opposite-parity vertex contains at
most ONE of the four same-parity vertices. Otherwise averaging its two
included and two excluded points contradicts its defining affine inequality.

A union of two such halfspaces cannot cover all four positive vertices.
An intersection cannot work either: complementing it gives a union of two
halfspaces that would have to cover all four negative vertices. A single
halfspace and constants also fail. Hence r>=3 for arbitrary real weights,
and therefore for arbitrary integer weights. No coefficient grid is used.

## STR-3. At least six active input incidences

Fix any raw input coordinate. If it influences at most one retained hidden
predicate, that predicate is monotone or antitone in the coordinate with a
fixed sign determined by its affine coefficient. The output threshold is
monotone or antitone in that hidden bit with its fixed output-weight sign.
Other hidden bits remain fixed when the coordinate changes.
The composition is therefore unate in that raw coordinate.

Parity has both increasing and decreasing edges in EACH raw coordinate.
Thus each raw input influences at least two retained predicates.
If d_i counts nonzero raw coefficients of active predicate i, its syntactic
support can overestimate actual dependence, which only strengthens the bound:
s=sum_i d_i>=6, with every d_i>=1. A shared form must involve all three inputs,
since omitting one would make the entire network independent of that input.

The hidden-only output premise is necessary. With a raw/shared-sum skip,
h=int(a+b+c>=2), followed by int(a+b+c-2*h>=1), computes parity with ONE
hidden predicate. This legal different architecture is retained as a control.

## STR-4. Arbitrary-coefficient lower bound and attained optimum

The declared opcode-layout contract is:

- unpack plus return0 baseline BASE=6;
- an own-form hidden line of support d>=1 adds at least 4+2d;
- a shared-form assignment of support d adds at least 2d;
- each shared-threshold line adds at least6;
- an output expression using r>=1 active hidden locals adds at least3+2r
  relative to the baseline return0.

The lower counts follow from syntax, not coefficient saturation. A flat form
using d distinct variables needs d loads and d-1 combining operations.
A hidden assignment additionally needs load-int, threshold load, comparison,
call and store. A shared assignment adds only its store. An output uses the
same five overhead operations with return in place of store, while the
baseline's single return0 instruction is removed. Coefficient multiplication,
leading negation, ignored predicates and extended operands add nonnegative
instructions. Reordering a form can remove a leading negation but cannot
remove a required load or combining operation.

The pinned CPython3.12 compiler visits both children of each binary expression
and emits its operation; name expressions emit name loads. This accounts for
the required syntax instructions in the nonspecialized 3.12 layout.
The native validator checks representative opcode lists, signed/zero/large
coefficients and extended operands. These checks detect layout incompatibility;
finite samples are NOT a proof of an arbitrary compiler or future release.
The theorem is explicitly conditional on this opcode contract.
Native version and binary identity are retained separately from its portable
receipt; a mismatch is UNVERIFIABLE, never a passed bound.

For shape A, retain only mandatory contributions from active predicates:

    C_A >= 6 + sum_i(4+2d_i) + (3+2r)
        = 9+6r+2s >=39.

For shape B the shared form needs all three raw inputs:

    C_B >= 6+6+6r+(3+2r) =15+8r >=39.

These inequalities cover every unit count and integer coefficient magnitude
inside the two shapes. For example A with r=4 costs at least45; with r>=5
it costs at least51. No claim of attaining those per-r floors is required.

The explicit B witness s=a+b+c, h_j=int(s>=j) for j=1,2,3,
return int(h_1-h_2+h_3>=1), costs39 and computes every input correctly.
Thus the entire registered class has minimum39 per call,312 per eight-input
sweep. The registered XOR source costs11 per call,88 per sweep, so it strictly
excludes that class at this coordinate. The arithmetic minimizer is inherited;
the repaired analytic coverage is independent of the flawed output grid.

## STR-5. Delegation and remaining scientific scope

The universal SN7a exclusion under expanded delegation is WITHDRAWN.
Four compared programs establish four point costs, not a class lower bound.
A C-implemented functools.partial wrapper around the explicit threshold
network has no outer __code__ yet retains a Python descendant. The candidate
return delegate(x) costs4 opcodes for either that neural implementation or
an XOR implementation, with all eight outputs correct. Both cost32 per sweep.
This exposes the accounting boundary; it does not measure or equate callee
work, full computation, physical resources or their family optima.

The 39/312 result applies to the two faithful flat-linear source shapes and
the declared layout. It does not cover skip connections, opaque delegation,
other activations, multiple layers, vectorization, other languages, arbitrary
physical machines, time/energy, or a universal neural/non-neural verdict.
The old three-runtime receipt is preserved as historical evidence. A current
native contract check does not impersonate its recorded interpreter.
