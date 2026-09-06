# Native grammar with single invocation — prospective

**Prepared; actual native parsing, synthesis and checking are NOT_RUN.**
[LAUNCH.json](LAUNCH.json) gives the fixed capture and subsequent checker commands.

Two fresh cases, once each, in order:

1. Unchanged implicit primitive parent.
2. Exact prior native-grammar replay with only two added commands:
   `(set-option :sygus-si all)` and `(set-option :sygus-si-rcons all)`.

The commands occur after the original three setup commands and before synth-fun,
constraints and check-synth. Native nonterminal names, all productions, original
max3 specification and fixed host checker are unchanged. No helper or macro arm
is added. [PROPOSAL.json](PROPOSAL.json) binds the exact input and option delta.

[Source rationale](SOURCE-NOTE.md): the donor's existing single-invocation mode
`all` avoids its `use` restriction on explicit syntax. Strict reconstruction
`all` remains enabled; reconstruction may fail or exhaust the fixed envelope.
This tests one public interface revival, not learning or search guidance.

The prior three-route result remains separate and immutable:
implicit PASS; original explicit and exact native replay CANNOT_CHECK after
exit 124 and empty output. One native Z3 unsat occurred. Its seal and original
checks are copied under [predecessor/](predecessor/); the original full raw capture
remains at the source path named in the proposal. No internal timeout stage was
measured by that ordinary worker.

Each case keeps native 5000 ms, outer 20 s, kill grace 2 s, CPU 0, and
4 GiB address space. The unchanged supervisor watchdog is 24 s. Startup,
candidate discovery, reconstruction and native output all remain inside the
same invocation boundary. No timing-win or complete process-tree cost claim.

Nine [structural controls](CONTROL.json) qualify exact input construction,
unchanged implicit parent, and refusal of missing/duplicate/late options,
non-strict reconstruction, changed grammar, specification or native deadline.
No native parser, synthesis or Z3 check ran during preparation.

After capture seals, the unchanged caller checks both assigned rows once
against the original grammar/specification. At most two actual Z3 checks run
(5000 ms native, 10 s external); timeout/no candidate/grammar refusal can mean
fewer. PASS requires host grammar PASS and native fixed-spec unsat. Preserve
FAIL and CANNOT_CHECK separately; no candidate is not an impossibility result.
Incomplete custody must never be called successful checking.

Even a positive would qualify strict reconstruction on this exposed task.
A future macro could affect reconstruction/output cost without guiding native
candidate discovery. The successful implicit single-invocation parent must stay
available in every fair later comparison. Do not manufacture library utility by
comparing only with an explicit enumeration route. If this CLIA family remains
parent-sufficient, a later distinct-function benchmark needs an independently
justified library-sensitive bottleneck. No new benchmark is authorized here.

No repository, old evidence, runtime environment or default is changed.
The copied execution source is pinned at 7e45; runtime binaries remain external
and hash-bound with the predecessor's explicitly limited runtime coverage.
