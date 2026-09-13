# Current exposed PROGRAM qualification

This result repairs an assay prerequisite. It does not close empirical Q6.
The [protocol](PROTOCOL_V1.md) was written before its native control execution;
all observations are exposed deterministic qualification data.

## CPA-1 — Complete state at the declared checkpoint

The current VM persists a selected immutable PROGRAM tuple in vm.state. PROGRAM
and PROGEXEC read it on a fresh query, while SEARCH runs only in feedback/update.
The unchanged source provides this path; there is no new synthesis algorithm.

Checkpointing copies the entire rooted VM object graph, including Machine stores,
cells/types, RNG state, tape, cost history, Basis and grammar objects, genotype,
derived scheduling structures and aliases. Exact class/field checks refuse
unregistered objects, observers, callbacks and subclasses. Tape must be None and
event writes finalized. Encoded graph equality checks internal reference sharing;
disjoint mutable object identities check isolation. Immutable scalar/tuple sharing
is permitted. Both fields and container values/keys are inspected.

This specializes Python's existing deepcopy/memo mechanism. Its documentation
explicitly notes that functions are returned unchanged and classes can customize
copying: hence deepcopy alone is not an observer-closure isolation theorem.
See [Python copy](https://docs.python.org/3.12/library/copy.html).
The verified native classes have no custom copy hooks. This is an in-process
checkpoint under fixed verified module constants and trusted Python/library execution,
not a durable deserializer,
concurrent snapshot, host attestation or general VM checkpoint theorem.

## CPA-2 — Typed artifact intervention and exact restoration

For the exact zoo.program_search template, substitution changes only the selected
PROGRAM tuple to a member of the same finite grammar. It does not delete evidence,
revoke examples, reset RNG, replay acquisition or change the genotype. Initial,
acquired, sham and restored arms share one complete acquired starting checkpoint.
Restored/sham state is compared before serving, then complete outputs and final
encoded states/native costs are compared after all16 queries.

compiled_search is refused: MATERIALIZE builds a separate lookup table, so changing
its PROGRAM tuple alone can leave served answers unchanged through the cache.
This is a concrete alternative pathway, not proof that no compiled method can
support a differently registered state intervention.

Two fixed observations select mask1/bias0 in a pre-existing32-body XOR grammar.
Another body may fit those observations. Selection and execution of this body are
not construction of a new method, identification of the true generative law,
protected generalization, or transfer to new obligations. The zero-label experience
control preserves event inputs/count while exposing the dependence on labels;
all actual differences in native work remain in the ledgers.

## CPA-3 — Explicit current protocol and non-answer refusal

The assay admits precisely the six ordered V2 intervention names, not every key
of a mutable registry. It uses the actual current parent ecology runner and retains
every returned trace and cost ledger. A failed call is an error, never a distinct
answer; missing/abstaining final vectors remain incomplete. Any incomplete member
prevents a complete-assay terminal. The terminal is not an architecture verdict.

The parent V2 extra-feedback control uses the first four UNSEEN inputs as feedback
and scores only the final four. The runtime call observer checks actual feedback
inputs against the scored set for the existing unseen criterion. This does not
make exposed E_smooth3 a protected benchmark or justify a population estimate.
For the all-input criterion, this no-overlap claim is not offered.

## CPA-4 — Complete incurred native charges, bounded cost interpretation

A scoped observer at the parent module's actual lookup names records every write
to the native ledger coordinate map. This includes declaration, store updates,
nested primitive emulation and feedback SEARCH work. Every increment is retained
once, with before/after values; per-call intervals retain errors as well as returns.
Conservation reconstructs the entire final map from the charge sequence even when
an interruption follows an incurred write. A native no-alarm compares observer
and uninstrumented parent responses, including the full native ledger.

This is complete for writes made by the bound Machine cost implementation during
the captured call. It is not complete host Python instruction, energy, elapsed-time
or full lifecycle accounting. SEARCH loop overhead and external checkpoint,
assignment, serialization/observer work are not silently given zero physical cost.
The native source's broad header claim that everything is charged is not endorsed.
External interventions have operation counts/serialized sizes and explicitly
unmeasured host/physical cost. Copied acquisition charges are historical state,
not repeated acquisition executions; serving deltas are reported separately.
No cost advantage or lifetime improvement follows.

## CPA-5 — Historical runner disposition

The bound nn_nonnn_packet.py verdict already returns
UNRESOLVED__INCOMPLETE_EVIDENCE, but main tests only the obsolete string
UNDECIDED_FROM_CURRENT_EVIDENCE when choosing its top-level terminal.
Executing the exact archived main/verdict functions with a substituted incomplete
record reproduces the incorrect decided terminal. A complete-record control
remains complete. The successor explicitly checks complete task coverage, flags
and admitted verdict values.

The original runner remains byte-exact: RV-377-210 and the retained B6/NAR custody
packets bind it. This does not invalidate its historical complete-evidence run.
The source-preserved mismatch is a legacy defect refused by this successor,
not an unrecorded repair of the historical instrument.

## Parents and remaining gates

Actual source parents are bound in SOURCE_BINDINGS_V1.json. The evaluator, finite
grammar search, ecology protocol and charged Machine are inherited unchanged.
The instrumentation pattern is adapted from scoped patching at the lookup site,
with restoration even on failure; see
[Python mock documentation](https://docs.python.org/3.12/library/unittest.mock.html).
No scientific novelty is claimed for copying, search or fault injection.

Empirical qualification still needs separately registered evidence for acquired
method construction, protected task/language transfer, causal capability gain
against strongest matched parents, and full acquisition/lifetime advantage.
This exposed assay supplies reusable state isolation and honest error/cost handling.
