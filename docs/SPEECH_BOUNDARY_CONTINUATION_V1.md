# Actual-speech boundary continuation

The previous gate checked a renderer-supplied meaning and marker while accepting arbitrary text.
The dialogue layer could even check the placeholder `Yes.` and then commit a different sentence.
Explanations bypassed this gate and trusted free-form source glosses.

The revised gate reads the actual returned text. Event clauses use the registered interpretation
grammar; world clauses use a separate relation parser that enumerates every possible delimiter
split. Quantity values and units remain part of the graph. Unregistered or ambiguous text cannot
be accepted by selecting a convenient interpretation. Source glosses no longer certify assertions.

Contextual `said so` and `said it did not` forms bind the current question, source, evidence and
polarity. Other reports require their explicit source and a parsed clause. Citation/source metadata
must be representable in the registered grammar; sentence injection is rejected. Missing semantics,
an unrelated assertion digest, a missing marker and evidence withdrawal cannot warrant a proposition.
In particular, loss of support does not warrant its negation.

The boundary rechecks support after interpretation callbacks. Runtime response paths also compare
their epistemic checkpoint across codec execution. Explanation checks run after all rendering
callbacks so a later callback cannot invalidate an earlier clause unnoticed. Unsupported codecs
and renderer exceptions produce a typed refusal. Malformed teaching commands are rejected before
durable evidence admission.

Initial root tests reproduced nine failures. Independent review then reproduced eight additional
failures: empty asserted semantics, unbound assertion digest, lost report polarity, unwarranted
denial, source-name injection, missed relation ambiguity, a default-water crash and stale support
after a decoder callback. All seventeen regressions pass. The combined speech and existing dialogue
controls passed **29 tests**; the eight independent-review cases were separately rechecked.

Two historical positive fixture assumptions were corrected in the current test: the uncertainty
sentence had omitted the very negation its metadata claimed to preserve, and a named report had
no bound speaker. The old fixture bytes remain in the previous Git revision and custody snapshot.

Scope is the registered bounded grammar and trusted host. These checks do not certify unrestricted
English, hidden dependencies, callback executable identity, arbitrary Python object isolation or
atomic commits against arbitrary concurrent external writers. Nonassertive host control messages
are a separate trusted path, not a general renderer authorization channel.
