# PR563: source-pinned scientific audit

Reviewed head: `d9e4a190b2d2fda9000483291262f6d658a0891f`.
Disposition: two demonstrated failures of the proposed anti-export claim;
the original STR written-grammar minimum survives.
This is synthetic static-accounting validation, not new empirical evidence.
No repository authority or historical receipt was modified.

## 1. Positive baseline and custody

The exact pinned checker reproduced its entire frozen JSON byte-for-byte under
CPython3.12.13, normally and with `-O`; both exited0 with empty stderr.
The countercontrols also agree byte-for-byte normally and under `-O`.
The interpreter patch differs from the PR record; the complete no-alarm payload
and its native layout guard nevertheless match. No interpreter identity is
substituted into the historical record.

[Source and baseline hashes](SOURCE_AND_NO_ALARM.json),
[standalone countercontrol](countercontrols_v1.py), and
[full countercontrol payload](COUNTERCONTROLS_V1.json).
The source script checks the exact archived checker SHA before loading it.

## 2. Opaque consolidation defeats DIC-5

The [normative DIC-5 claim](https://github.com/SzeChunYiu/ORION-OCM/blob/d9e4a190b2d2fda9000483291262f6d658a0891f/research/gmi-grand-unification-v1/DELEGATION_INVARIANT_COST_PREREGISTRATION_V1.md#L55-L62)
says any export cannot dominate its parent. Its checker already admits
`functools.partial` but compares the two partial wrappers only to one another
([source](https://github.com/SzeChunYiu/ORION-OCM/blob/d9e4a190b2d2fda9000483291262f6d658a0891f/research/gmi-grand-unification-v1/grand_gmi_delegation_invariant_cost_checks_v1.py#L338-L375)).

| Admitted realization | sweep opcodes | unaccounted calls |
|---|---:|---:|
| exact written shared-sum parent |312|32|
| explicit Python call to that parent |344|32|
| call to `partial(parent)` |32|8|
| `table[x]`, Python `__getitem__` calling that parent |32|0|

All four compute all eight parity inputs. The partial's `.func` is the exact
compiled original function object. Its execution retains all original work.
One outer opaque call replaces four counted inner `int` calls per input,
so both recorded coordinates decrease. This is not a work reduction.
The explicit Python-call control correctly retains all inner counts and adds
wrapper opcodes. Python's [documented partial semantics](https://docs.python.org/3.12/library/functools.html#functools.partial)
provides the source-level explanation.

## 3. Implicit Python dispatch is accepted and uncharged

The checker [models BINARY_SUBSCR only by its stack effect](https://github.com/SzeChunYiu/ORION-OCM/blob/d9e4a190b2d2fda9000483291262f6d658a0891f/research/gmi-grand-unification-v1/grand_gmi_delegation_invariant_cost_checks_v1.py#L117-L155).
Its environment accepts a global object with Python-coded `__getitem__`.
`return table[x]` invokes that method, which invokes the exact written parent;
the result is accepted with zero callee names and zero unaccounted calls.
This defeats DIC-2's exact descendant bookkeeping and DIC-3's refusal ceiling
inside the implemented opcode grammar, without recursion or nontermination.
The [Python data model](https://docs.python.org/3.12/reference/datamodel.html#object.__getitem__)
explicitly supplies this implicit call. The same stage needs typed treatment
for arithmetic/comparison/unary/containment/unpacking dispatch; this audit
executes only the subscription counterexample, not an exhaustive census.

## 4. Scope-preserving constructive repair

Keep the old receipt historical and issue a new correction/operational version.
Retain the pair as a diagnostic of visible opcodes and call boundaries; do not
use an opaque-call count as an internal-work measure or certify anti-export
monotonicity from it. For a resource comparison, resolve the whole admitted
semantic call closure, or require independently sound resource contracts.
Unresolved work yields UNVERIFIABLE/unknown for that resource comparison.

For the smallest finite implementation, propagate exact builtin operand types
and fixed globals, reject implicit dispatch that is not certified, and recognize
only registered transparent adapters such as `partial` with bound `.func`,
arguments and semantics. Expanding a known wrapper must retain the original
inner opaque identities/contracts instead of replacing them by one cheap count.
Unknown adapters remain unverified. Merely recognizing partial cannot repair
the general opaque-consolidation theorem.

The valid positive lemma is conditional: for an additive nonnegative cost
semantics, if a registered adapter transformation retains the parent's entire
costed execution and adds wrapper events, its cost is parent cost plus a
nonnegative increment. A structural induction proves this for a finite,
acyclic, fully resolved expansion. It does not cover arbitrary refactoring,
unknown callees or deleted work by assumption. With sound cost intervals,
upper(candidate)<=lower(comparator) is a sufficient robust comparison; a
missing upper bound cannot silently become zero or a cheap call count.

The mature methodological parent is
[Carbonneaux–Hoffmann–Shao, Compositional Certified Resource Bounds, PLDI2015](https://www.cs.cmu.edu/~janh/assets/pdf/CarbonneauxHZ15.pdf):
resource contracts compose under an explicitly defined cost semantics.
Adapting that principle to a finite Python grammar is an application, not a
new general resource-analysis theorem or a claim to reuse their C proof intact.

Finally, [STR-1/4/5](https://github.com/SzeChunYiu/ORION-OCM/blob/d9e4a190b2d2fda9000483291262f6d658a0891f/research/gmi-structural-threshold-repair-v1/STRUCTURAL_THRESHOLD_ANALYTIC_CORRECTION_V1.md)
explicitly restrict the39/312 minimum to the two flat written source shapes.
DIC's expanded wrappers neither disprove that restricted result nor inherit
its class-wide bound. Correct DIC-6 and `class_bound_is_now_a_frontier` to the
actual declared class; the product frontier over all admitted wrappers is not
certified by the unchanged scalar syntactic lower-bound function.
