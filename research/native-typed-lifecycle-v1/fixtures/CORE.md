# Authored typed-wff fixture proposal

**Status:** exact inputs prepared; native, trace-bound and registered meaning-bridge
qualification remain pending. This is an engineer-authored interface control, with
no corpus-learning, useful acquisition, search, performance or novelty result.

[FIXTURES.json](FIXTURES.json) contains two ordered-premise tasks and their full
ordinary proof-token recipes. [TRAINING-SUFFIX.mm](TRAINING-SUFFIX.mm) declares the
corresponding scoped hypotheses and proposed proofs. It adds two `$p` declarations
and no `$a` declaration; neither proposed proof has been checked by this packet.

[ASSERTIONS.json](ASSERTIONS.json) copies five named contracts from the already
exposed, pinned ordinary catalogue. [AUTHORING.json](AUTHORING.json) binds the
inputs, generated files and [authoring source](author_typed_wff_fixtures_v1.py).
The entire existing prefix is identified, not copied or requalified here.

## Fixed proposed inputs

Both tasks have hypotheses H0: ph→ps and H1: ps→ch, in that order. The first
concludes ph→ch. The second concludes (ph∨ps)→ch. The ambient parameters are
three native wff variables ph, ps, ch, with floating labels wph, wps, wch.

The first authored route applies syl, then jca to obtain ph→(ps∧ch), then uses
simpr and syl to reach ph→ch. The second wraps that full route with jaoi and H1.
The recipes contain 20 and 25 proof labels respectively. Internal ordinary-rule
arguments include a compound wff; external parameter renaming remains atomic.
The existing syntax axiom wa supplies the compound's syntax proof. It is not new
trusted material. Native checking must still establish the exact issued statements,
scope, full proof population and unchanged trusted axiom identities.

The ordinary syl contract already directly matches the first task. Its supplied
longer route deliberately exercises reconstruction and extraction; it must never
serve as an artificially weak reference proof for a claimed learning benefit.

These routes deliberately provide a repeated proper fragment for an interface
control. The extractor must enumerate all proper fragments generically. There is
no expected candidate ID/body, theorem-name dispatch or utility-selection field.
The qualification may discover aliases only or refuse; retain those outcomes.
An alias witness is ineligible for learned-method serving under the current policy.

## Independent propositional authoring checks

[AUTHOR-TRUTH-TABLE.json](AUTHOR-TRUTH-TABLE.json) evaluates the two authored prose
meanings over all eight Boolean valuations. It does not parse native strings or
invoke the registered meaning bridge. The exact bridge signatures remain pending.

The first conclusion is false at two valuations; the second at three. A permutation
of variable names preserves that count, so these query truth functions cannot be
made equal by variable permutation. Consequently their complete joint signatures
including the query cannot be equal under that operation either. This assumes the
bridge represents the complete joint semantics; the actual bridge must establish it.

With both hypotheses true, both conclusions hold. Each premise is essential:

| Task | Removed premise | Counterexample (ph, ps, ch) | Remaining premise | Conclusion |
|---|---|---|---|---|
| ph→ch | H0 | (true, false, false) | H1 true | false |
| ph→ch | H1 | (true, true, false) | H0 true | false |
| (ph∨ps)→ch | H0 | (true, false, false) | H1 true | false |
| (ph∨ps)→ch | H1 | (false, true, false) | H0 true | false |

This is propositional checking of the authored meanings. It supplies neither
native proof authority nor evidence that mathematical warrant establishes the
meaning of arbitrary language or empirical claims.

## Use boundary

Independent fixture review and a separate, exact source/lifecycle execution gate
must precede native dispatch. Preserve this first generation. Any repair requires
a diagnosed failure and an explicit successor; do not select alternative fixtures
after observing candidate usefulness. Do not reopen a protected corpus allocation.

The future producer must obtain fresh native traces, group support through the
unchanged registered bridge, retain every supported candidate and exact alias result,
check emitted proofs, persist the declared typed projection and exit. Fresh consumers
must reconstruct from that projection and check the exact issued targets. This packet
does not implement or authorize those stages, and it supplies no learned method.
