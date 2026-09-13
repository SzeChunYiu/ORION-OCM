# Typed delegation cost — DCR-1–4

This is a finite cost-semantics application and correction of PR563 at
`d9e4a190b2d2fda9000483291262f6d658a0891f`, not a new resource-analysis theorem.
[Parents and accounting](PARENTS_AND_COSTS_V1.md) give the immediate prior work.
[Raw bindings](RAW_BINDINGS_V1.json) preserve the source, protocol, full receipt
and independently executed countercontrols. Their bytes are historical.

## Interface and authority

A program is a finite immutable register of source strings, typed constant
bindings and declared transparent adapter bindings. Each source defines only
`f(x)`: one unannotated argument, assignments, then one final return. There
are no decorators, defaults, closures, imports, control flow or mutation.
The admitted expressions are integer/Boolean/tuple constants and locals,
tuple construction/unpacking/subscription, the explicitly enumerated integer
arithmetic/bit operations, unary operators, one comparison, and named unary
calls. The implemented opcode list, not all Python syntax, is authoritative.

All values have exact type int, bool or recursively such tuples. Subclasses
and arbitrary objects are refused before invoking their methods. Subscription
requires an exact tuple and an exact integer valid index. Arithmetic requires
exact int/bool operands. Native calls are ONLY standard int on exact int/bool,
and standard sum on an exact tuple of exact int/bool values. Neither input
can trigger a Python conversion, iterator or numeric-method override.

Other calls resolve to registered source functions or a declared zero-prefix,
keyword-free `functools.partial` of one such function. Arbitrary callable
objects, partial subclasses, bound arguments, methods and opaque extensions
are outside this register. The native oracle constructs precisely that adapter
from the bound source function; this is not adapter recognition by a label
supplied on an arbitrary object. Recursion and depth beyond eight frames are
refused. Source functions and standard builtins cannot be rebound during a run.

Each successful run emits an ordered trace: one `py:OPNAME` event per modeled
nonspecialized opcode, excluding RESUME/CACHE; an extra native obligation for
int/sum, including its argument; and an extra adapter obligation before the
partial's fully expanded descendant trace. A native obligation does not
replace any descendant opcode or inner int obligation. No obligation is an
estimate of native internal work. Stack/type/dispatch errors yield refusal,
not a cheap successful score. Finite machine exhaustion is not a certificate.

## DCR-1. Exact execution and typed Python closure

Assume the stated CPython3.12 opcode layout, an unmutated register, no external
monitor callbacks altering execution, and successful evaluation at each step.
The typed evaluator returns the same value as native execution. Its Python
projection is the complete sequence of admitted Python opcodes, including
source descendants reached through the registered partial adapter.

Proof: induct on the finite call expansion, then on instructions in each
straight-line frame. LOAD/STORE and exact tuple operations preserve matching
stacks and locals. Numeric operations use the same exact builtin types, so
no implicit Python special method can intervene. Each admitted native call
has its explicit type contract and no Python callback. A direct source call
uses the induction hypothesis. The partial has no bound prefix/keywords and
calls its bound source with the same argument, so that hypothesis applies
unchanged; its native adapter remains a separate obligation. RETURN therefore
agrees. The per-frame bytecode sequence is straight-line; recursion is rejected.
The trace accounts for each executed admitted instruction once. Unsupported
opcodes/values are not covered by the claim.

The independent oracle executes actual compiled source functions and native
partials with INSTRUCTION monitoring installed before the first call. It
compares the complete Python event sequence and result, not only a total.
This finite check is a falsifier of implementation mistakes, not a proof of
an arbitrary Python release. Missing/empty instrumentation is UNVERIFIABLE.

## DCR-2. Preserved-trace monotonicity

Fix a nonnegative additive event cost assignment w on the declared labels.
Its units and state-uniform applicability are part of the resource model.
Let E(R) be a transformation whose complete trace retains R's ordered events
and inserts only additional charged events. Then

    C_w(E(R)) = C_w(R) + sum_{inserted e} w(e) >= C_w(R).

Proof: partition the child trace into the retained subsequence and inserted
positions, then use additivity and nonnegativity. The same argument holds
componentwise for a vector of such assignments. At least one positive added
charge is needed for strictness. Zero-cost wrappers can tie; deleting events,
changing contracts or exploiting context-dependent hardware costs invalidates
the premise. This is not a theorem about arbitrary source refactoring.

The whole-function wrapper fixture binds the exact original source and input.
DCR-1 gives its unchanged descendant trace; wrapper opcodes and the partial
obligation are inserted. Thus both direct and transparent partial calls satisfy
this positive lemma even though the legacy opaque-call count decreased.
The executable certificate checks the full ordered subsequence and records
every residual label. Consolidating four int obligations into one unknown
wrapper does not satisfy this certificate.

## DCR-3. Sound contract bounds and explicit unknowns

A supplied contract gives 0<=l_e<=u_e for every occurrence of label e over the
whole compared register/domain. Soundness for a real resource is an independent
proof obligation; a source hash or the existence of a dictionary is not that
proof. Additivity yields sum_e n_e l_e <= C <= sum_e n_e u_e. Missing bounds
mean [0,infinity), never zero. An absent upper bound prevents a certified
strict scalar win via U_candidate<L_comparator. This sufficient comparison
may abstain on a real win; no completeness claim is made for interval bounds.

The implemented exact numeric contract is the DEFINED Python-opcode count:
py events cost one and native/adapter obligations cost zero Python opcodes.
DCR-1 justifies that projection. Zero here excludes native work from this
coordinate; it does not make native execution free in a broader resource.
A native-work or physical contract is not supplied by this unit. Uniform
per-label physical bounds would require an additional state/domain proof.

## DCR-4. Repaired finite findings and original structural bound

The original written shared-sum parent has312 Python opcodes and32 native-int
obligations per eight-input sweep. A direct call and a transparent partial
both have344 Python opcodes and retain all32 int obligations; the partial
also records eight adapter obligations. It cannot win by hiding its parent.
The historical API accepted the same partial at(32,8) and a Python-coded
`__getitem__` wrapper at(32,0). The latter cannot enter this typed register;
its missing dispatch is refused without invoking the object. An exact tuple
lookup is admitted and independently checked as the no-alarm control.

STR's39/312 minimum remains valid ONLY for its two flat written source shapes
and declared opcode contract. DCR admits additional sources but transports no
minimum or complete frontier to that larger register. Legacy counts remain
diagnostics, not total work, hardware cost or a universal anti-gaming theorem.
Setup, source/adapter descriptions, acquisition, monitoring and lifetime cost
are outside the displayed per-invocation Python coordinate. They must be
charged separately before any broader machine comparison.
