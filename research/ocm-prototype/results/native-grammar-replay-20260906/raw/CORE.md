# Native grammar replay — prospective

**Prepared; all actual synthesis and semantic checks are NOT_RUN.**
[LAUNCH.json](LAUNCH.json) supplies the once-only capture command and subsequent
unchanged checker command for joint root registration.

Three fresh routes, in fixed order:
1. original implicit primitive input;
2. original OCM explicit primitive input;
3. explicit replay of the exact printed native two-nonterminal grammar.

The two parents are byte-identical quoted-v2 requests. Replay changes only the
implicit synth-fun declaration by appending the printed declarations and
productions. A_Int_489 and A_Bool_491 are retained exactly; no grammar shrinking,
renaming, learned macro or outcome-dependent adjustment is allowed.

[PROPOSAL.json](PROPOSAL.json) binds the exact donor stdout-independent native
stderr and extracted grammar. [SOURCE-ORIGINS.json](SOURCE-ORIGINS.json) identifies
every unmodified worker/checker/parser/task copy from committed 7e45.
The original clia_worker and capture.py are reused; no extra tracing is enabled.

Each synthesis case retains native 5000 ms, outer 20 s plus 2 s kill grace, CPU 0 and
4 GiB address space. Existing capture watchdog is 24 s. The resource envelope applies
equally; this is not a powered timing comparison or a timing-win claim.

Nine [structural/metamorphic controls](CONTROL.json) pass: exact native grammar
and whole original spec, whitespace identity, missing/duplicate/wrong-function
grammar, changed sort, changed public constraint/deadline and explicit-parent
replacement refusal. Native parsing and grammar admissibility remain untested.

## Checker and outcomes

After complete sealed capture and source/runtime verification, process every
assigned row once with the unchanged check_outputs_v2.py and fixed clia_checker.
Its original CLIA grammar and original max3 specification remain authoritative.
At most 3 Z3 checks are possible, each 5000 ms native / 10 s external; timeout,
no-candidate or grammar refusal may use fewer. All assigned outcomes remain.

PASS requires the fixed grammar and actual native unsat result. FAIL means the
checker establishes a grammar refusal or counterexample. CANNOT_CHECK covers
timeout/no candidate/unknown/incomplete custody; it is not a no-program proof.
Incomplete capture custody cannot be relabelled as completed checking.

Donor PASS with implicit PASS would qualify one public explicit-interface
revival. Preserve the old explicit outcome even if it times out. Explicit syntax
restriction can change dispatch, so matching productions do not imply the
implicit route or cost. Learning, cognition, later use and whole-lifetime benefit
remain NOT_ESTABLISHED.

[Prior observed result](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5560143658)
supplied the grammar. That acquisition is an imported prior with its own costs.
Runtime binaries are external and hash-bound; complete OS/transitive runtime
closure is not claimed. No repo files, old packets or environments were edited.
