# Fixed alias-witness qualification — proposal for existing #62

PREPARED ONLY. No witness, solver, compression, normalization or test actor has executed here.
This is a finite witness qualification, not a generic search or novelty classifier.

## Assignment

Five records, in fixed order; maximum four actual Z3 probes:

1. Saved first winner (+ h1 (* (- 1) h0)) versus (- h1 h0).
   Expected UNSAT of inequality: WITNESS_EQUIVALENT.
2. Saved second winner not(h0 >= 1), with h0:Int, versus h0 <= 0.
   Expected UNSAT of inequality: WITNESS_EQUIVALENT.
3. Same first winner versus wrong orientation (- h0 h1).
   Expected SAT and returned counterexample; h0=0,h1=1 is an illustrative witness.
4. Same second winner versus shifted threshold h0 <= 1.
   Expected SAT and returned counterexample; h0=1 is an illustrative witness.
5. Reinterpret the second expression and witness with a Real parameter.
   Expected rejection against the unchanged accepted Int signature before native entry:
   UNSUPPORTED_HOST_TYPE. This is not a Real-equivalence solver probe.

All five records remain assigned; no failed record is removed.
Expected symbolic outcomes and illustrative counterexamples are grading metadata,
not constraints added to the verifier. Solver models need not equal those examples.
SAT is a successful negative control, not a passed equality.
Unknown/unavailable/timeout remains CANNOT_CHECK rather than SAT or equivalence.

## Inputs and authority

probes.json contains exact saved bodies from the two sealed adapter results, provenance
paths/hashes and two declared primitive witnesses. No new learning data or target task is used.
First source seal: c21af1fdd5383e9247b9cc2db1aaba081863ce0042cca40932da41491369db29.
Second source seal: 275012f6e1429c08bd481631ff821f20dff8e3ee02393294241cbf2f8181e5e8.
Original raw primitive_alias_assessment=NOT_RUN fields remain unchanged.
A new result can certify only these explicitly tested identities.

The existing generation_clia.equivalent expects Int-returning functions.
Boolean bodies are therefore encoded as ite(body,1,0) on both sides, an injective Bool-to-Int
encoding. Parameters/signatures stay source-bound Int; this does not widen the host grammar.
The fifth candidate deliberately violates that accepted signature to exercise refusal.
No general semantic canonicalization or exhaustive primitive-template generation is added.

## Exact mechanism and execution

The copied generation_clia, CLIA grammar/process/worker and supporting modules are unchanged.
Existing equivalent creates the negated-equality obligation. Existing clia_process invokes
the pinned Z3 5.1.0.0 worker, whose UNSAT/SAT/UNKNOWN values and model text are retained.
Existing observed-call wrapper preserves each actual request/return/exception verbatim.

Only alias_caller.py is new (101 lines), because the old caller always invokes compress.
It runs the five explicit records once and writes each input/result before continuing.
It never invokes the donor. All returned models and unexpected outcomes remain raw.
The old launcher/supervisor are byte-identical; create-only capture-v1 and timeout seal apply.

One caller process: CPU0, address space4GiB, outer60seconds plus2seconds kill grace,
supervisor watchdog64seconds. Four checks at most, each timeout_ms5000/deadline_s10.
No retry, fallback, discovery, rewrite, simplify, synthesis, persistence or later-use call.
launch.json will contain the exact command after this preparation is reviewed/frozen.

## Interpretation and stopping rule

All five expected results qualify this narrow witness/interface contract.
The first two then establish aliases of existing primitive applications under their stated types.
They do not classify every future macro or prove no reusable composite exists in the corpus.
Any unexpected outcome or unavailable native check prevents aggregate qualification.
A type refusal is evidence that the current host scope excludes that reinterpretation,
not evidence that the Real identity is true or false.
No new compression follows automatically, regardless of the outcomes.

## Costs and remaining limits

Charge imports, source binding, all dispatched checks, outputs, supervision and cleanup.
Caller self CPU/RSS and native worker observations remain separately scoped.
Total process-tree CPU/RSS, energy and whole-lifetime acquisition cost remain UNKNOWN.
The earlier acquisition/induction/normalization captures are imported provenance, not free work.
No performance, later-use, transfer, new-operator or OCM-residual claim follows.

Only file preparation, JSON serialization and hash/source inspection have occurred.
No Python module import of the new caller, harmless control suite or native execution was run.
Source/control qualification status is explicitly NOT_RUN pending the next batch.
