# Parents, contracts and verification boundaries

The immediate methodological parent is
[Carbonneaux, Hoffmann and Shao, PLDI2015, Compositional Certified Resource Bounds](https://www.cs.cmu.edu/~janh/assets/pdf/CarbonneauxHZ15.pdf).
Its function resource specifications compose under a formal cost semantics
with soundness certificates. We apply that principle to a much smaller finite
Python interface; their C analysis and proofs do not certify this evaluator.
No novel general resource logic, inference algorithm or hardware bound is claimed.

Native source semantics follow the
[Python3.12 data model](https://docs.python.org/3.12/reference/datamodel.html#object.__getitem__),
[functools.partial contract](https://docs.python.org/3.12/library/functools.html#functools.partial)
and [instruction monitoring API](https://docs.python.org/3.12/library/sys.monitoring.html).
The opcode layout follows [dis](https://docs.python.org/3.12/library/dis.html).
The exact native contracts are standard int on exact int/bool, sum on exact
int/bool tuples, and zero-prefix partial of a bound source function. Arbitrary
objects and Python method dispatch are refused. The library contracts justify
the call semantics; they do not supply timings or non-Python resource costs.

The strongest internal parent is STR-1–5's analytic parity bound in
`research/gmi-structural-threshold-repair-v1/STRUCTURAL_THRESHOLD_ANALYTIC_CORRECTION_V1.md`.
Its written grammar prohibits the delegation at issue. DIC does not invalidate
that scoped39/312 result. The new unit does not search another neural grammar
or promote its finite register into all admissible machines.

The archived DIC pair counts visible Python opcodes and opaque call boundaries.
An unknown call's count is not its work, and one wrapper can subsume many such
calls. The archived positive no-alarm receipt and both exact counterexamples
are replayed in full before the repaired checker runs. None is overwritten.

The repaired coordinate is an ordered semantic event ledger, with the complete
admitted Python opcode projection and separate unresolved native obligations.
The full symbolic nonnegative-cost statement is conditional on the declared
additive cost model. No numerical native weights were fitted to restore an
ordering. Additional resource bounds require independently justified uniform
contracts; unknowns cause abstention. This is the positive correction to the
failed inference, not an assertion that a call-count vector measures all work.

The native oracle is deliberately independent: actual compiled functions,
actual functools.partial and CPython INSTRUCTION events. It does not call the
typed evaluator to produce its reference event sequence. Every comparison
creates fresh function code; monitoring is enabled before its first use.
A preliminary sys.settrace probe on the local3.12.13 build returned no opcode
events on first use and events on second use. We rejected that empty reference
and used the documented monitoring API, with a fresh-function no-priming guard.
That diagnostic does not rewrite an older instrument or establish a new timing
result. The Python patch/binary used for validation is recorded separately;
portable opcode-layout receipts do not impersonate historical binary identity.

All finite verification runs are on laptop billy. There is no candidate search,
training, ecology rerun, timing study or native-work measurement. The full
result includes original and repaired payloads, input outputs, event ledgers,
ordered-event digests, refinement residuals and refusal reasons. Normal and
optimized executions must agree. The manifest anchors every unit member before
and after isolated replay; a rewritten self-consistent manifest is rejected.
